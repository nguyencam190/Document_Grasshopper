# -*- coding: utf-8 -*-
# ==========================================================================
#  FLOW PAINT - co son huong luoi, ban THU NGHIEM co giao dien
#
#  DAN VAO TAB "Python" CUA SCRIPT EDITOR - KHONG PHAI TAB "MEL".
#  Dan nham tab MEL se bao "// Error: Line 1.2: Syntax error".
#
#  File nay DOC LAP: khong can clone repo, khong can cai gi. Chi can numpy,
#  ma Maya 2022 tro len co san.
#
#  Chua co mesh de thu thi bam "Tao mesh thu" - no dung san mot mat cong.
#
#  Ghi chu: khong dung dau tieng Viet trong file nay - Script Editor cua
#  Maya hay lam hong ky tu co dau khi dan vao.
# ==========================================================================
import math
import time

import numpy as np

from maya import cmds
from maya.api import OpenMaya as om
from maya.api import OpenMayaUI as omui

WIN = "flowPaintWin"
CTX = "flowPaintCtx"
COLOR_SET = "flowGuide"

U_COLOR = (1.0, 0.0, 0.0)      # do  - ho vet doc
V_COLOR = (0.0, 1.0, 0.0)      # luc - ho vet ngang

# Do dai "soi day" keo dau co theo con tro, tinh bang pixel man hinh. Con tro
# nhuc nhich trong ban kinh nay thi dau co dung yen han - do la cach loc run
# tay. 0 = tat, dau co bam sat con tro.
LEASH = 14.0

# Lay trung binh bao nhieu vi tri gan nhat de lam muot duong di. 1 = tat.
SMOOTH = 6

# Khoang cach toi da giua hai dau co lien tiep, tinh theo phan ban kinh co.
# Re chuot nhanh ma khong chen dau o giua thi net bi dut thanh cac cham roi.
SPACING = 0.25

# Giu bao nhieu net gan nhat de lui duoc.
UNDO_DEPTH = 30

# Trong so phai tang them it nhat chung nay thi moi to lai vertex. Duoi muc do
# mat khong phan biet duoc, to lai chi ton cong.
WEIGHT_STEP = 0.02

# Cho it nhat chung nay giua hai lan ghi mesh, du keo nhanh den may.
MIN_GAP = 0.016


# ----------------------- luoi bam khong gian -----------------------

class Hash(object):
    """Chia khong gian thanh o lap phuong de tim nhanh vertex quanh dau co.

    Dung numpy va dung mot lan luc bat co. Xep vertex theo o bang lexsort roi
    ghi lai khoang chi so cua tung o - vong lap Python chi chay tren SO O
    (vai nghin) chu khong tren so vertex (co the vai trieu).
    """

    def __init__(self, pts, cell):
        self.pts = pts
        self.cell = max(cell, 1e-6)

        key = np.floor(pts / self.cell).astype(np.int64)
        self.order = np.lexsort((key[:, 2], key[:, 1], key[:, 0]))
        sorted_key = key[self.order]

        cut = np.any(np.diff(sorted_key, axis=0) != 0, axis=1)
        start = np.concatenate([[0], np.flatnonzero(cut) + 1])
        end = np.concatenate([start[1:], [len(sorted_key)]])
        self.table = {(int(k[0]), int(k[1]), int(k[2])): (int(s), int(e))
                      for k, s, e in zip(sorted_key[start], start, end)}

        self._offsets = {}

    def _cells(self, span):
        """Danh sach o lech quanh o giua, dung lai cho moi span."""
        if span not in self._offsets:
            r = range(-span, span + 1)
            self._offsets[span] = [(dx, dy, dz) for dx in r for dy in r for dz in r]
        return self._offsets[span]

    def near(self, centre, radius):
        """(chi so vertex, khoang cach) cua cac vertex trong ban kinh."""
        cell = self.cell
        span = int(math.ceil(radius / cell))
        bx = int(math.floor(centre[0] / cell))
        by = int(math.floor(centre[1] / cell))
        bz = int(math.floor(centre[2] / cell))

        chunks = []
        if (2 * span + 1) ** 3 > len(self.pts):
            # O phai duyet con nhieu hon vertex thi quet thang re hon.
            chunks.append(np.arange(len(self.pts)))
        else:
            for dx, dy, dz in self._cells(span):
                rng = self.table.get((bx + dx, by + dy, bz + dz))
                if rng is not None:
                    chunks.append(self.order[rng[0]:rng[1]])
        if not chunks:
            return None, None

        idx = chunks[0] if len(chunks) == 1 else np.concatenate(chunks)
        d = np.linalg.norm(self.pts[idx] - centre, axis=1)
        keep = d <= radius
        return idx[keep], d[keep]


# ----------------------- trang thai co -----------------------

class Brush(object):
    def __init__(self, mesh):
        self.mesh = mesh
        self.color = np.array(U_COLOR, dtype=float)
        self.radius_px = 40.0
        self.opacity = 1.0
        self.leash = LEASH
        self.smooth = SMOOTH
        self.erase = False

        sel = om.MSelectionList()
        sel.add(mesh)
        dag = sel.getDagPath(0)
        dag.extendToShape()
        self.dag = dag
        self.fn = om.MFnMesh(dag)
        self.accel = self.fn.autoUniformGridParams()

        pts = self.fn.getPoints(om.MSpace.kWorld)
        self.pts = np.array([(p.x, p.y, p.z) for p in pts], dtype=float)
        n = len(self.pts)

        bb = cmds.exactWorldBoundingBox(mesh)
        diag = math.sqrt(sum((bb[k + 3] - bb[k]) ** 2 for k in range(3)))
        self.hash = Hash(self.pts, diag / 60.0)

        try:
            cols = self.fn.getVertexColors(COLOR_SET)
            self.colors = np.array([(c.r, c.g, c.b) for c in cols], dtype=float)
        except RuntimeError:
            self.colors = np.zeros((n, 3), dtype=float)

        self.base = np.zeros((n, 3), dtype=float)   # mau truoc net dang ve
        self.saved = np.zeros(n, dtype=bool)        # da luu mau goc chua
        self.weight = np.zeros(n, dtype=float)      # trong so lon nhat trong net

        self.history = []          # (chi so, mau truoc net) de lui tung net
        self.pending = []          # cac chi so doi ghi len mesh
        self.tip = None            # dau soi day, bam theo con tro (pixel)
        self.paint = None          # vi tri son that, sau khi lam muot
        self.recent = []           # vai vi tri gan nhat cua dau day
        self.radius_world = None   # ban kinh co quy ra don vi the gioi
        self.dabs = 0
        self.spent = 0.0           # thoi gian tinh toan cua net, giay
        self.pushed = 0.0          # thoi gian ghi mesh cua net, giay
        self.writes = 0
        self.last_push = 0.0       # luc ghi mesh gan nhat
        self.push_cost = 0.0       # lan ghi mesh gan nhat ton bao lau

    def reset_stroke(self):
        self.saved.fill(False)
        self.weight.fill(0.0)
        self.pending = []
        self.dabs = 0
        self.spent = 0.0
        self.pushed = 0.0
        self.writes = 0
        self.push_cost = 0.0
        self.last_push = 0.0


B = None                       # con co dang bat, None neu chua bat


# ----------------------- mot dau co -----------------------

_BULK_OK = [True]      # MColorArray co nhan thang mot danh sach hay khong


def _color_array(rows):
    """MColorArray tu mang (N,4).

    Dung mot lan tu danh sach neu ban Maya nay chap nhan - nhanh hon han vong
    lap tao tung MColor mot khi net rong.
    """
    if _BULK_OK[0]:
        try:
            return om.MColorArray(rows.tolist())
        except Exception:                                     # noqa: BLE001
            _BULK_OK[0] = False
    arr = om.MColorArray()
    for r in rows.tolist():
        arr.append(om.MColor(r))
    return arr


def _ray(x, y):
    """Tia ban tu camera qua diem (x, y) tren man hinh: (goc, huong).

    viewToWorld nhan diem va vector lam THAM SO RA chu khong tra ve chung -
    goi kieu `src, vec = viewToWorld(x, y)` se bao "takes exactly 4 arguments".
    """
    view = omui.M3dView.active3dView()
    src, vec = om.MPoint(), om.MVector()
    view.viewToWorld(int(x), int(y), src, vec)
    return src, vec


def _hit(x, y):
    """Diem tren mesh ma con tro dang chi vao, kem do sau tu camera."""
    src, vec = _ray(x, y)
    got = B.fn.closestIntersection(
        om.MFloatPoint(src.x, src.y, src.z),
        om.MFloatVector(vec.x, vec.y, vec.z),
        om.MSpace.kWorld, 1e6, False, accelParams=B.accel)
    if not got:
        return None, 0.0
    hp = got[0]
    depth = math.sqrt((hp.x - src.x) ** 2 + (hp.y - src.y) ** 2
                      + (hp.z - src.z) ** 2)
    return np.array([hp.x, hp.y, hp.z]), depth


def _world_radius(x, y, depth, px):
    """Doi ban kinh pixel man hinh sang ban kinh the gioi tai do sau diem cham.

    Nho vay co giu nguyen do lon cam nhan khi zoom, giong ZBrush.
    """
    s0, d0 = _ray(x, y)
    s1, d1 = _ray(x + px, y)
    a = np.array([s0.x + d0.x * depth, s0.y + d0.y * depth, s0.z + d0.z * depth])
    b = np.array([s1.x + d1.x * depth, s1.y + d1.y * depth, s1.z + d1.z * depth])
    return max(float(np.linalg.norm(a - b)), 1e-6)


def dab(x, y, radius):
    """Dat mot dau co tai toa do pixel (x, y). Chua ghi len mesh."""
    centre, _ = _hit(x, y)
    if centre is None:
        return
    idx, dist = B.hash.near(centre, radius)
    if idx is None or idx.size == 0:
        return

    # Falloff muot: dam deu o giua, tat dan ve mep, khong cat cung.
    f = 1.0 - (dist / radius) ** 2
    w = np.where(f > 0.0, f * f, 0.0) * B.opacity

    # Trong MOT net, moi vertex chi giu trong so LON NHAT no tung gap, va mau
    # luon tron tu mau goc truoc net chu khong tron chong len ket qua cua dau
    # co truoc. Hai cai loi cung mot luc:
    #  - nhanh: cac dau co chong nhau rat nhieu, dau co sau phan lon cho trong
    #    so nho hon nen bo qua duoc ngay, khoi ghi lai
    #  - dep: keo cham khong con bi dam cuc lai o cho dau co don nhau
    take = w > B.weight[idx] + WEIGHT_STEP
    idx, w = idx[take], w[take]
    if idx.size == 0:
        return

    fresh = idx[~B.saved[idx]]
    if fresh.size:
        B.base[fresh] = B.colors[fresh]
        B.saved[fresh] = True

    B.weight[idx] = w
    target = np.zeros(3) if B.erase else B.color
    base = B.base[idx]
    B.colors[idx] = base + (target - base) * w[:, None]
    B.pending.append(idx)


def _push():
    """Ghi mau len mesh, CHI bang API.

    Truoc day cuoi moi net con goi them `polyColorPerVertex` de Ctrl+Z hoan
    tac duoc. Bo han vi lenh do them mot node lich su vao mesh sau MOI net:
    net sau danh de len ket qua cua net truoc (ve duong moi la duong cu bien
    mat), va mesh cu tich them node nen cang ve cang ri du da xoa lich su.
    Doi lai Ctrl+Z khong lui duoc net - dung nut 'Hoan tac net'.
    """
    if not B.pending:
        return
    idx = np.unique(np.concatenate(B.pending))
    B.pending = []

    clock = time.time()
    rows = np.empty((idx.size, 4), dtype=float)
    rows[:, :3] = B.colors[idx]
    rows[:, 3] = 1.0
    arr = _color_array(rows)
    B.fn.setVertexColors(arr, [int(i) for i in idx])

    B.push_cost = time.time() - clock
    B.pushed += B.push_cost
    B.last_push = time.time()
    B.writes += 1


# ----------------------- callback cua draggerContext -----------------------

def on_press():
    if B is None:
        return
    B.reset_stroke()
    mod = cmds.draggerContext(CTX, query=True, modifier=True) or ""
    B.erase = "ctrl" in mod or bool(cmds.checkBox(UI["erase"], query=True, value=True))
    pos = cmds.draggerContext(CTX, query=True, anchorPoint=True)
    B.tip = [float(pos[0]), float(pos[1])]
    B.recent = [list(B.tip)]
    B.paint = list(B.tip)
    B.radius_world = None
    on_drag(first=True)


def _steady(raw):
    """Vi tri son sau khi on dinh tay, theo dung cach ZBrush lam.

    ZBrush tach lam HAI thu khac nhau, khong phai mot:

    LazyRadius - dau co bi keo theo con tro bang mot soi day do dai co dinh.
    Con tro nhuc nhich trong ban kinh do thi dau co dung yen, chi khi con tro
    keo cang day dau co moi bi loi theo, va luon giu dung khoang cach do.

    LazySmooth - lay trung binh vai vi tri gan nhat cua dau day, bot goc canh.

    DA DO, de khoi tuong bo: so voi cach cu ("di mot phan quang duong toi con
    tro"), o CUNG mot do tre thi hai cach loc rung gan nhu ngang nhau khi keo
    nhanh; soi day chi nhinh hon khi ve cham (lech 0.63 px so voi 0.84 px o
    buoc 1 px). Cai duoc that su la do tre KHONG DOI theo toc do tay - luon
    dung bang do dai soi day - nen tay quen duoc, con cach cu thi keo cang
    nhanh tre cang nhieu (2.8 px khi cham, 15 px khi nhanh).
    """
    dx, dy = raw[0] - B.tip[0], raw[1] - B.tip[1]
    dist = math.sqrt(dx * dx + dy * dy)
    if dist > B.leash:
        k = (dist - B.leash) / dist
        B.tip = [B.tip[0] + dx * k, B.tip[1] + dy * k]

    B.recent.append(list(B.tip))
    del B.recent[:-max(int(B.smooth), 1)]
    n = float(len(B.recent))
    return [sum(p[0] for p in B.recent) / n, sum(p[1] for p in B.recent) / n]


def on_drag(first=False):
    if B is None or B.tip is None:
        return
    clock = time.time()

    if first:
        gx, gy = B.paint
    else:
        raw = cmds.draggerContext(CTX, query=True, dragPoint=True)
        gx, gy = _steady([float(raw[0]), float(raw[1])])

    # Ban kinh the gioi tinh MOT lan cho ca luot keo: no chi doi khi camera
    # hoac do sau doi, ma trong mot luot keo thi gan nhu khong.
    if B.radius_world is None:
        centre, depth = _hit(gx, gy)
        if centre is not None:
            B.radius_world = _world_radius(gx, gy, depth, B.radius_px)
    if B.radius_world is None:
        return

    # Chen them dau giua hai vi tri neu tay re nhanh, tranh net dut thanh cham.
    # Dau cuoi luon dat tai dich: re cham thi quang duong ngan hon mot buoc
    # chen, khong co dau nao o giua, thieu no la net ve mat han.
    step = max(B.radius_px * SPACING, 1.0)
    gap = math.sqrt((gx - B.paint[0]) ** 2 + (gy - B.paint[1]) ** 2)
    for k in range(1, int(gap / step) + 1):
        f = (k * step) / max(gap, 1e-9)
        dab(B.paint[0] + (gx - B.paint[0]) * f, B.paint[1] + (gy - B.paint[1]) * f,
            B.radius_world)
        B.dabs += 1
    dab(gx, gy, B.radius_world)
    B.dabs += 1
    B.paint = [gx, gy]
    B.spent += time.time() - clock

    # Ghi mesh TU DIEU TIET NHIP: cho it nhat bang thoi gian lan ghi truoc da
    # ton. Moi lan ghi la mot lan Maya nap lai mau vertex len card do hoa; mesh
    # cang nang thi cang lau. Neu cu ghi moi luot keo thi cac luot keo don lai
    # va dau co tut hau sau con tro - do la cai cam giac "ve bi cham". Cho theo
    # chi phi that giup dau co luon bam kip tay, chi la mau hien lai thua hon.
    if time.time() - B.last_push >= max(MIN_GAP, B.push_cost):
        _push()


def on_release():
    if B is None:
        return
    _push()
    idx = np.flatnonzero(B.saved)
    if idx.size:
        # Nho mau truoc net de con hoan tac duoc. Chi giu vai net gan nhat cho
        # do ton bo nho tren mesh nang.
        B.history.append((idx, B.base[idx].copy()))
        del B.history[:-UNDO_DEPTH]
    B.saved.fill(False)
    B.weight.fill(0.0)
    _say("Net vua ve: %d vertex | %d dau co | tinh %.0f ms | hien mau %.0f ms "
         "(%d lan). Lui mot net: nut 'Hoan tac net'."
         % (idx.size, B.dabs, B.spent * 1000.0, B.pushed * 1000.0, B.writes))


def undo_stroke():
    """Tra lai mau truoc net gan nhat.

    Phai tu lam thay vi dua vao Ctrl+Z, vi tool khong con dung
    `polyColorPerVertex` nua - xem ghi chu o dau ham `_push`.
    """
    if B is None or not B.history:
        _say("Khong con net nao de lui.")
        return
    idx, cols = B.history.pop()
    B.colors[idx] = cols
    B.pending = [idx]
    B.last_push = 0.0
    _push()
    _say("Da lui mot net (%d vertex). Con %d net lui duoc."
         % (idx.size, len(B.history)))


# ----------------------- giao dien -----------------------

UI = {}


def _say(msg):
    if UI.get("status"):
        cmds.text(UI["status"], edit=True, label=msg)
    if msg:
        print("[flow paint] %s" % msg)


def _sync():
    """Doc lai cac o chinh tren giao dien vao co dang bat."""
    if B is None:
        return
    B.radius_px = cmds.floatSliderGrp(UI["size"], query=True, value=True)
    B.opacity = cmds.floatSliderGrp(UI["opacity"], query=True, value=True)
    B.leash = cmds.floatSliderGrp(UI["leash"], query=True, value=True)
    B.smooth = cmds.intSliderGrp(UI["smooth"], query=True, value=True)
    B.radius_world = None


def _set_color(rgb):
    if B is not None:
        B.color = np.array(rgb, dtype=float)
    cmds.canvas(UI["swatch"], edit=True, rgbValue=rgb)
    cmds.colorSliderGrp(UI["custom"], edit=True, rgbValue=rgb)


def _pick_from_selection():
    sel = cmds.ls(selection=True, long=False) or []
    meshes = [s for s in sel
              if cmds.listRelatives(s, shapes=True, type="mesh", noIntermediate=True)]
    if not meshes:
        _say("Chua chon mesh nao. Chon mesh trong viewport roi bam lai.")
        return
    cmds.textFieldGrp(UI["mesh"], edit=True, text=meshes[0])
    _say("Da chon: %s" % meshes[0])


def _make_test_mesh():
    """Dung mot mat cong de thu ngay, khong can mesh co san."""
    name = cmds.polyPlane(w=10, h=10, sx=40, sy=40, name="flowPaint_thu")[0]
    sel = om.MSelectionList()
    sel.add(name)
    dag = sel.getDagPath(0)
    dag.extendToShape()
    fn = om.MFnMesh(dag)

    pts = fn.getPoints(om.MSpace.kObject)
    for i in range(len(pts)):
        p = pts[i]
        p.y = 1.2 * math.cos(p.x * 0.25) * math.cos(p.z * 0.25)
        pts[i] = p
    fn.setPoints(pts, om.MSpace.kObject)

    cmds.select(name)
    cmds.textFieldGrp(UI["mesh"], edit=True, text=name)
    _say("Da tao '%s'. Bam BAT CO roi ve thu len no." % name)


def _drop_history():
    """Xoa lich su dung hinh cua mesh dang ve.

    Con lich su thi moi lan doi mau vertex Maya phai chay lai ca chuoi node
    phia truoc, ve se ri. Xoa lich su la thao tac khong hoan lai duoc nen de
    thanh nut rieng chu khong tu lam.
    """
    mesh = cmds.textFieldGrp(UI["mesh"], query=True, text=True).strip()
    if not mesh or not cmds.objExists(mesh):
        _say("Chua co mesh de xoa lich su.")
        return
    truoc = len(cmds.listHistory(mesh) or [])
    cmds.delete(mesh, constructionHistory=True)
    _say("Da xoa lich su cua '%s' (%d node -> %d). Bat lai co de ve."
         % (mesh, truoc, len(cmds.listHistory(mesh) or [])))


def _prepare(mesh):
    """Tao color set va bat hien thi mau - khong bat thi ve xong khong thay gi."""
    shape = (cmds.listRelatives(mesh, shapes=True, noIntermediate=True) or [mesh])[0]
    sets = cmds.polyColorSet(mesh, query=True, allColorSets=True) or []
    if COLOR_SET not in sets:
        cmds.polyColorSet(mesh, create=True, colorSet=COLOR_SET,
                          representation="RGB")
    cmds.polyColorSet(mesh, currentColorSet=True, colorSet=COLOR_SET)
    cmds.setAttr("%s.displayColors" % shape, 1)


def start_brush():
    global B
    mesh = cmds.textFieldGrp(UI["mesh"], query=True, text=True).strip()
    if not mesh or not cmds.objExists(mesh):
        _say("Chua co mesh. Chon mesh roi bam 'Lay tu vung chon', "
             "hoac bam 'Tao mesh thu'.")
        return
    clock = time.time()
    try:
        _prepare(mesh)
        B = Brush(mesh)
    except Exception as loi:                                  # noqa: BLE001
        import traceback
        traceback.print_exc()
        _say("Khong bat duoc co: %s: %s" % (type(loi).__name__, loi))
        return

    _sync()
    _set_color(cmds.canvas(UI["swatch"], query=True, rgbValue=True))

    if cmds.draggerContext(CTX, exists=True):
        cmds.deleteUI(CTX)
    cmds.draggerContext(CTX, pressCommand=on_press, dragCommand=on_drag,
                        releaseCommand=on_release, cursor="crossHair",
                        space="screen")
    cmds.setToolTo(CTX)

    lich_su = len(cmds.listHistory(mesh) or [])
    canh = ("" if lich_su <= 2 else
            " Mesh con %d node lich su - ve se ri, nen bam 'Xoa lich su'."
            % lich_su)
    _say("Co da bat tren '%s': %d vertex, chuan bi het %.0f ms.%s"
         % (mesh, len(B.pts), (time.time() - clock) * 1000.0, canh))


def stop_brush():
    cmds.setToolTo("selectSuperContext")
    _say("Da tat co, tro ve cong cu chon.")


def clear_colors():
    mesh = cmds.textFieldGrp(UI["mesh"], query=True, text=True).strip()
    if B is None or B.mesh != mesh:
        _say("Bat co tren mesh truoc da, roi moi xoa mau.")
        return
    idx = np.arange(len(B.pts))
    B.history.append((idx, B.colors.copy()))
    del B.history[:-UNDO_DEPTH]
    B.colors.fill(0.0)
    B.pending = [idx]
    B.last_push = 0.0
    _push()
    _say("Da xoa mau tren '%s'. Lui lai duoc bang 'Hoan tac net'." % mesh)


def show_ui():
    if cmds.window(WIN, exists=True):
        cmds.deleteUI(WIN)
    win = cmds.window(WIN, title="Flow Paint - co son huong luoi",
                      widthHeight=(400, 500), sizeable=True)
    cmds.columnLayout(adjustableColumn=True, rowSpacing=6,
                      columnAttach=("both", 8))

    cmds.frameLayout(label="1. Mesh de ve len", marginWidth=6, marginHeight=6,
                     collapsable=False)
    cmds.columnLayout(adjustableColumn=True, rowSpacing=4)
    UI["mesh"] = cmds.textFieldGrp(label="Mesh:", text="",
                                   columnWidth2=(50, 250), adjustableColumn=2)
    cmds.rowLayout(numberOfColumns=2, columnWidth2=(185, 185),
                   columnAttach=[(1, "both", 2), (2, "both", 2)])
    cmds.button(label="Lay tu vung chon", height=26,
                command=lambda *a: _pick_from_selection())
    cmds.button(label="Tao mesh thu", height=26,
                command=lambda *a: _make_test_mesh())
    cmds.setParent("..")
    cmds.button(label="Xoa lich su (mesh con lich su thi ve bi ri)", height=26,
                command=lambda *a: _drop_history())
    cmds.setParent("..")
    cmds.setParent("..")

    cmds.frameLayout(label="2. Chinh co", marginWidth=6, marginHeight=6,
                     collapsable=False)
    cmds.columnLayout(adjustableColumn=True, rowSpacing=2)
    UI["size"] = cmds.floatSliderGrp(
        label="Kich thuoc (px)", field=True, minValue=5.0, maxValue=200.0,
        fieldMinValue=1.0, fieldMaxValue=500.0, value=40.0, precision=0,
        columnWidth3=(95, 55, 190), changeCommand=lambda *a: _sync(),
        dragCommand=lambda *a: _sync())
    UI["opacity"] = cmds.floatSliderGrp(
        label="Dam nhat", field=True, minValue=0.05, maxValue=1.0,
        value=1.0, precision=2, columnWidth3=(95, 55, 190),
        changeCommand=lambda *a: _sync(), dragCommand=lambda *a: _sync())
    UI["leash"] = cmds.floatSliderGrp(
        label="Do tre (px)", field=True, minValue=0.0, maxValue=80.0,
        value=LEASH, precision=0, columnWidth3=(95, 55, 190),
        changeCommand=lambda *a: _sync(), dragCommand=lambda *a: _sync())
    UI["smooth"] = cmds.intSliderGrp(
        label="Lam muot", field=True, minValue=1, maxValue=16,
        value=SMOOTH, columnWidth3=(95, 55, 190),
        changeCommand=lambda *a: _sync(), dragCommand=lambda *a: _sync())
    cmds.text(label="   Do tre: rung tay nho hon chung nay bi triet tieu han. "
                    "0 = tat.", align="left")
    cmds.setParent("..")
    cmds.setParent("..")

    cmds.frameLayout(label="3. Mau huong luoi", marginWidth=6, marginHeight=6,
                     collapsable=False)
    cmds.columnLayout(adjustableColumn=True, rowSpacing=4)
    cmds.rowLayout(numberOfColumns=3, columnWidth3=(150, 150, 60),
                   columnAttach=[(1, "both", 2), (2, "both", 2), (3, "both", 2)])
    cmds.button(label="U - net DOC (do)", height=28,
                command=lambda *a: _set_color(U_COLOR))
    cmds.button(label="V - net NGANG (luc)", height=28,
                command=lambda *a: _set_color(V_COLOR))
    UI["swatch"] = cmds.canvas(rgbValue=U_COLOR, width=54, height=28)
    cmds.setParent("..")
    UI["custom"] = cmds.colorSliderGrp(
        label="Mau khac:", rgbValue=U_COLOR, columnWidth3=(70, 60, 180),
        changeCommand=lambda *a: _set_color(
            cmds.colorSliderGrp(UI["custom"], query=True, rgbValue=True)))
    UI["erase"] = cmds.checkBox(
        label="Che do xoa mau (hoac giu Ctrl khi keo)", value=False)
    cmds.setParent("..")
    cmds.setParent("..")

    cmds.frameLayout(label="4. Ve", marginWidth=6, marginHeight=6,
                     collapsable=False)
    cmds.columnLayout(adjustableColumn=True, rowSpacing=4)
    cmds.rowLayout(numberOfColumns=2, columnWidth2=(185, 185),
                   columnAttach=[(1, "both", 2), (2, "both", 2)])
    cmds.button(label="BAT CO", height=34, backgroundColor=(0.35, 0.55, 0.35),
                command=lambda *a: start_brush())
    cmds.button(label="TAT CO", height=34,
                command=lambda *a: stop_brush())
    cmds.setParent("..")
    cmds.rowLayout(numberOfColumns=2, columnWidth2=(185, 185),
                   columnAttach=[(1, "both", 2), (2, "both", 2)])
    cmds.button(label="Hoan tac net", height=26,
                command=lambda *a: undo_stroke())
    cmds.button(label="Xoa het mau tren mesh", height=26,
                command=lambda *a: clear_colors())
    cmds.setParent("..")
    cmds.setParent("..")
    cmds.setParent("..")

    cmds.separator(height=6, style="in")
    UI["status"] = cmds.text(label="San sang. Chon mesh hoac bam 'Tao mesh thu'.",
                             align="left")
    cmds.text(label="Ctrl + keo = xoa mau | lui net bang nut 'Hoan tac net', "
                    "KHONG phai Ctrl+Z", align="left")

    cmds.showWindow(win)


show_ui()
