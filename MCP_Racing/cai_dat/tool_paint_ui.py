# -*- coding: utf-8 -*-
# ==========================================================================
#  FLOW PAINT - co son huong luoi, ban THU NGHIEM co giao dien
#
#  DAN VAO TAB "Python" CUA SCRIPT EDITOR - KHONG PHAI TAB "MEL".
#  Dan nham tab MEL se bao "// Error: Line 1.2: Syntax error".
#
#  File nay DOC LAP hoan toan: khong can clone repo, khong can numpy,
#  khong can cai gi. Dan vao la hien cua so cong cu.
#
#  Chua co mesh de thu thi bam "Tao mesh thu" - no dung san mot mat cong.
#
#  Ghi chu: khong dung dau tieng Viet trong file nay - Script Editor cua
#  Maya hay lam hong ky tu co dau khi dan vao.
# ==========================================================================
import math
import time

from maya import cmds
from maya.api import OpenMaya as om
from maya.api import OpenMayaUI as omui

WIN = "flowPaintWin"
CTX = "flowPaintCtx"
COLOR_SET = "flowGuide"

U_COLOR = (1.0, 0.0, 0.0)      # do  - ho vet doc
V_COLOR = (0.0, 1.0, 0.0)      # luc - ho vet ngang

# Dau co di duoc bao nhieu phan quang duong toi con tro moi lan nhan su kien.
# 1.0 = bam sat con tro (tat LazyMouse); cang nho cang muot nhung cang i tay.
LAZY = 0.35

# Khoang cach toi da giua hai dau co lien tiep, tinh theo phan ban kinh co.
# Re chuot nhanh ma khong chen dau o giua thi net bi dut thanh cac cham roi.
SPACING = 0.25

# So muc luong tu hoa mau khi ghi lai net vao undo stack. Xem commit().
LEVELS = 12

# Trong so phai tang them it nhat chung nay thi moi to lai vertex. Duoi muc do
# mat khong phan biet duoc, to lai chi ton cong.
WEIGHT_STEP = 0.02

# Mat do dich khi bam nut tao ban nhe de ve.
PROXY_TARGET = 60000


# ----------------------- luoi bam khong gian -----------------------

class Hash(object):
    """Chia khong gian thanh o lap phuong de tim nhanh vertex quanh dau co.

    Duyet toan bo vertex moi dau co se giat tay khi mesh nang. Bam mot lan luc
    bat co roi moi dau chi xet vai o lan can.
    """

    def __init__(self, pts, cell):
        self.pts = pts
        self.cell = max(cell, 1e-6)
        self.table = {}
        for i, p in enumerate(pts):
            key = (int(math.floor(p[0] / self.cell)),
                   int(math.floor(p[1] / self.cell)),
                   int(math.floor(p[2] / self.cell)))
            self.table.setdefault(key, []).append(i)

    def near(self, c, radius):
        """Tra ve [(chi so vertex, khoang cach), ...] trong ban kinh."""
        r2 = radius * radius
        out = []
        span = int(math.ceil(radius / self.cell))

        # Chi quet thang khi so O phai duyet con nhieu hon so VERTEX. Truoc day
        # dat nguong cung theo span, hoa ra sai huong: zoom xa mot chut la roi
        # vao quet thang toan bo mesh bang Python - cham hon han duyet o, vi o
        # rong chi ton mot lan tra tu dien.
        if (2 * span + 1) ** 3 > len(self.pts):
            for i, p in enumerate(self.pts):
                dx, dy, dz = p[0] - c[0], p[1] - c[1], p[2] - c[2]
                d2 = dx * dx + dy * dy + dz * dz
                if d2 <= r2:
                    out.append((i, math.sqrt(d2)))
            return out

        bx = int(math.floor(c[0] / self.cell))
        by = int(math.floor(c[1] / self.cell))
        bz = int(math.floor(c[2] / self.cell))
        for dx in range(-span, span + 1):
            for dy in range(-span, span + 1):
                for dz in range(-span, span + 1):
                    for i in self.table.get((bx + dx, by + dy, bz + dz), ()):
                        p = self.pts[i]
                        ex, ey, ez = p[0] - c[0], p[1] - c[1], p[2] - c[2]
                        d2 = ex * ex + ey * ey + ez * ez
                        if d2 <= r2:
                            out.append((i, math.sqrt(d2)))
        return out


# ----------------------- trang thai co -----------------------

class Brush(object):
    def __init__(self, mesh):
        self.mesh = mesh
        self.color = list(U_COLOR)
        self.radius_px = 40.0
        self.opacity = 1.0
        self.lazy = LAZY
        self.erase = False

        sel = om.MSelectionList()
        sel.add(mesh)
        dag = sel.getDagPath(0)
        dag.extendToShape()
        self.dag = dag
        self.fn = om.MFnMesh(dag)
        self.accel = self.fn.autoUniformGridParams()

        pts = self.fn.getPoints(om.MSpace.kWorld)
        self.pts = [(p.x, p.y, p.z) for p in pts]

        bb = cmds.exactWorldBoundingBox(mesh)
        diag = math.sqrt(sum((bb[k + 3] - bb[k]) ** 2 for k in range(3)))
        self.hash = Hash(self.pts, diag / 60.0)

        try:
            cols = self.fn.getVertexColors(COLOR_SET)
            self.colors = [[c.r, c.g, c.b] for c in cols]
        except RuntimeError:
            self.colors = [[0.0, 0.0, 0.0] for _ in self.pts]

        self.before = {}       # mau goc truoc net dang ve
        self.stroke_w = {}     # trong so lon nhat moi vertex da nhan trong net
        self.touched = set()
        self.tip = None        # vi tri dau co (pixel)
        self.radius_world = None   # ban kinh co quy ra don vi the gioi
        self.dabs = 0              # so dau co trong net dang ve
        self.spent = 0.0           # thoi gian ve net dang ve, giay


B = None                       # con co dang bat, None neu chua bat


# ----------------------- mot dau co -----------------------

def _ray(x, y):
    """Tia ban tu camera qua diem (x, y) tren man hinh: (goc, huong).

    viewToWorld nhan diem va vector lam THAM SO RA chu khong tra ve chung -
    goi kieu `src, vec = viewToWorld(x, y)` se bao "takes exactly 4 arguments".
    """
    view = omui.M3dView.active3dView()
    src, vec = om.MPoint(), om.MVector()
    view.viewToWorld(int(x), int(y), src, vec)
    return src, vec


def _world_radius(x, y, depth, px):
    """Doi ban kinh pixel man hinh sang ban kinh the gioi tai do sau diem cham.

    Nho vay co giu nguyen do lon cam nhan khi zoom, giong ZBrush.
    """
    s0, d0 = _ray(x, y)
    s1, d1 = _ray(x + px, y)
    ax, ay, az = s0.x + d0.x * depth, s0.y + d0.y * depth, s0.z + d0.z * depth
    bx, by, bz = s1.x + d1.x * depth, s1.y + d1.y * depth, s1.z + d1.z * depth
    return max(math.sqrt((ax - bx) ** 2 + (ay - by) ** 2 + (az - bz) ** 2), 1e-6)


def dab(x, y, radius=None, collect=None):
    """Dat mot dau co tai toa do pixel (x, y).

    `radius` tinh san mot lan cho ca luot keo (xem on_drag) de khoi goi
    viewToWorld hai lan cho moi dau co. `collect` la dict gom thay doi cua ca
    luot keo lai ghi mot the, thay vi moi dau co mot lenh ghi mesh.
    """
    if B is None:
        return
    src, vec = _ray(x, y)
    hit = B.fn.closestIntersection(
        om.MFloatPoint(src.x, src.y, src.z),
        om.MFloatVector(vec.x, vec.y, vec.z),
        om.MSpace.kWorld, 1e6, False, accelParams=B.accel)
    if not hit:
        return

    hp = hit[0]
    centre = (hp.x, hp.y, hp.z)
    if radius is None:
        depth = math.sqrt((hp.x - src.x) ** 2 + (hp.y - src.y) ** 2
                          + (hp.z - src.z) ** 2)
        radius = _world_radius(x, y, depth, B.radius_px)

    t0, t1, t2 = [0.0, 0.0, 0.0] if B.erase else B.color
    out = {} if collect is None else collect
    for i, d in B.hash.near(centre, radius):
        # Falloff muot: dam deu o giua, tat dan ve mep, khong cat cung.
        f = 1.0 - (d / radius) ** 2
        w = (f * f if f > 0.0 else 0.0) * B.opacity
        if w <= 1e-4:
            continue

        # Trong MOT net, moi vertex chi giu trong so LON NHAT no tung gap, va
        # mau luon tron tu mau goc truoc net chu khong tron chong len ket qua
        # cua dau co truoc. Hai cai loi cung mot luc:
        #  - nhanh: cac dau co chong nhau rat nhieu, dau co sau phan lon cho
        #    trong so nho hon nen bo qua duoc ngay, khoi ghi lai
        #  - dep: keo cham khong con bi dam cuc lai o cho dau co don nhau
        if w <= B.stroke_w.get(i, 0.0) + WEIGHT_STEP:
            continue
        B.stroke_w[i] = w

        if i not in B.before:
            B.before[i] = list(B.colors[i])
        base = B.before[i]
        cur = B.colors[i]
        cur[0] = base[0] + (t0 - base[0]) * w
        cur[1] = base[1] + (t1 - base[1]) * w
        cur[2] = base[2] + (t2 - base[2]) * w
        B.touched.add(i)
        out[i] = cur

    if collect is None and out:
        _push(list(out.keys()), list(out.values()))


def _push(idx, cols):
    """Ghi mau bang API - nhanh, dung de xem truoc luc dang ve."""
    arr = om.MColorArray()
    for c in cols:
        arr.append(om.MColor((float(c[0]), float(c[1]), float(c[2]))))
    B.fn.setVertexColors(arr, [int(i) for i in idx])


# ----------------------- callback cua draggerContext -----------------------

def on_press():
    if B is None:
        return
    B.before = {}
    B.stroke_w = {}
    B.touched = set()
    B.dabs = 0
    B.spent = 0.0
    mod = cmds.draggerContext(CTX, query=True, modifier=True) or ""
    B.erase = "ctrl" in mod or bool(cmds.checkBox(UI["erase"], query=True, value=True))
    pos = cmds.draggerContext(CTX, query=True, anchorPoint=True)
    B.tip = [float(pos[0]), float(pos[1])]
    B.radius_world = None
    on_drag(first=True)


def on_drag(first=False):
    if B is None or B.tip is None:
        return
    clock = time.time()

    if first:
        gx, gy = B.tip
    else:
        raw = cmds.draggerContext(CTX, query=True, dragPoint=True)
        gx = B.tip[0] + (float(raw[0]) - B.tip[0]) * B.lazy      # LazyMouse
        gy = B.tip[1] + (float(raw[1]) - B.tip[1]) * B.lazy

    # Ban kinh the gioi tinh MOT lan cho ca luot keo: no chi doi khi camera
    # hoac do sau doi, ma trong mot luot keo thi gan nhu khong. Tinh lai o moi
    # dau co ton them hai lan viewToWorld moi dau.
    if B.radius_world is None:
        src, vec = _ray(gx, gy)
        hit = B.fn.closestIntersection(
            om.MFloatPoint(src.x, src.y, src.z),
            om.MFloatVector(vec.x, vec.y, vec.z),
            om.MSpace.kWorld, 1e6, False, accelParams=B.accel)
        if hit:
            hp = hit[0]
            depth = math.sqrt((hp.x - src.x) ** 2 + (hp.y - src.y) ** 2
                              + (hp.z - src.z) ** 2)
            B.radius_world = _world_radius(gx, gy, depth, B.radius_px)

    # Chen them dau giua hai vi tri neu tay re nhanh, tranh net dut thanh cham.
    # Dau cuoi luon dat tai dich: re cham thi quang duong ngan hon mot buoc
    # chen, khong co dau nao o giua, thieu no la net ve mat han.
    changed = {}
    step = max(B.radius_px * SPACING, 1.0)
    gap = math.sqrt((gx - B.tip[0]) ** 2 + (gy - B.tip[1]) ** 2)
    for k in range(1, int(gap / step) + 1):
        f = (k * step) / max(gap, 1e-9)
        dab(B.tip[0] + (gx - B.tip[0]) * f, B.tip[1] + (gy - B.tip[1]) * f,
            B.radius_world, changed)
        B.dabs += 1
    dab(gx, gy, B.radius_world, changed)
    B.dabs += 1

    # Gom ca luot keo lai ghi MOT lan: moi lan ghi mesh la mot lan Maya nap lai
    # mau len card do hoa, goi nhieu lan trong cung mot luot keo rat ton.
    if changed:
        _push(list(changed.keys()), list(changed.values()))

    B.tip = [gx, gy]
    B.spent += time.time() - clock


def on_release():
    if B is None:
        return
    clock = time.time()
    n = len(B.touched)
    commit()
    _say("Net vua ve: %d vertex | %d dau co | ve %.0f ms | ghi lai %.0f ms"
         % (n, B.dabs, B.spent * 1000.0, (time.time() - clock) * 1000.0))


def commit():
    """Ghi lai net vua ve vao undo stack cua Maya.

    Luc dang ve ta ghi mau bang API cho nhanh, nhung API bo qua undo queue -
    Ctrl+Z se khong hoan tac duoc net ve. Nen khi nha chuot: tra mesh ve mau
    goc (van bang API, khong ai thay vi Maya chua ve lai man hinh), roi ap lai
    dung mau do qua polyColorPerVertex - lenh nay co undo.

    Mau duoc gom ve LEVELS muc de so lenh goi khong phu thuoc so vertex: ve voi
    opacity 1 thi gan nhu moi vertex nhan dung mau co, chi ton 1-2 lenh.
    """
    if B is None or not B.touched:
        return
    idx = sorted(B.touched)
    final = [list(B.colors[i]) for i in idx]

    _push(idx, [B.before[i] for i in idx])              # tra ve mau goc

    groups = {}
    for i, col in zip(idx, final):
        key = tuple(round(c * LEVELS) / float(LEVELS) for c in col)
        groups.setdefault(key, []).append(i)

    cmds.undoInfo(openChunk=True, chunkName="flowPaintStroke")
    try:
        for key, verts in groups.items():
            cmds.polyColorPerVertex(_components(B.mesh, verts),
                                    rgb=[key[0], key[1], key[2]],
                                    colorDisplayOption=True)
            for i in verts:
                B.colors[i] = list(key)
    finally:
        cmds.undoInfo(closeChunk=True)

    B.before = {}
    B.stroke_w = {}
    B.touched = set()


def _components(mesh, idx):
    """Gop chi so lien tiep thanh mesh.vtx[a:b] cho lenh ngan lai."""
    out, start, prev = [], None, None
    for i in list(idx) + [None]:
        if prev is not None and i == prev + 1:
            prev = i
            continue
        if start is not None:
            out.append("%s.vtx[%d]" % (mesh, start) if start == prev
                       else "%s.vtx[%d:%d]" % (mesh, start, prev))
        start = prev = i
    return out


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
    B.lazy = cmds.floatSliderGrp(UI["lazy"], query=True, value=True)


def _set_color(rgb):
    if B is not None:
        B.color = list(rgb)
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


def _make_proxy():
    """Tao ban giam mat do de ve cho nhe tay.

    Moi luot keo la mot lan Maya nap lai mau vertex cua CA mesh len card do
    hoa, nen mesh cang nang thi co cang giat - do la gioi han cua Maya, khong
    phai cua doan Python nay. Scan hang trieu diem thi phai ve tren ban nhe.
    Vet mau ve tren ban nhe van dung de dung luoi, vi luoi bam theo hinh dang
    be mat chu khong theo tung vertex mot.
    """
    mesh = cmds.textFieldGrp(UI["mesh"], query=True, text=True).strip()
    if not mesh or not cmds.objExists(mesh):
        _say("Chua co mesh de giam mat do.")
        return
    n = cmds.polyEvaluate(mesh, vertex=True)
    if n <= PROXY_TARGET:
        _say("'%s' co %d vertex, da du nhe roi." % (mesh, n))
        return

    _say("Dang giam mat do %s (%d vertex)..." % (mesh, n))
    cmds.refresh()
    dup = cmds.duplicate(mesh, name="%s_nhe" % mesh)[0]
    cmds.polyReduce(dup, version=1, percentage=100.0 * (1.0 - float(PROXY_TARGET) / n),
                    keepBorder=True, keepQuadsWeight=0.0, constructionHistory=False)
    cmds.delete(dup, constructionHistory=True)
    cmds.setAttr("%s.visibility" % mesh, 0)
    cmds.select(dup)
    cmds.textFieldGrp(UI["mesh"], edit=True, text=dup)
    _say("Da tao '%s' (%d vertex) va an ban goc. Bam BAT CO de ve tren no."
         % (dup, cmds.polyEvaluate(dup, vertex=True)))


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
    canh = ("" if len(B.pts) <= PROXY_TARGET else
            " MESH NANG - neu co giat thi bam 'Tao ban nhe de ve'.")
    _say("Co da bat tren '%s' (%d vertex). Keo chuot trong viewport de ve.%s"
         % (mesh, len(B.pts), canh))


def stop_brush():
    cmds.setToolTo("selectSuperContext")
    _say("Da tat co, tro ve cong cu chon.")


def clear_colors():
    mesh = cmds.textFieldGrp(UI["mesh"], query=True, text=True).strip()
    if not mesh or not cmds.objExists(mesh):
        _say("Chua co mesh de xoa mau.")
        return
    count = cmds.polyEvaluate(mesh, vertex=True)
    cmds.undoInfo(openChunk=True, chunkName="flowPaintClear")
    try:
        _prepare(mesh)
        cmds.polyColorPerVertex("%s.vtx[0:%d]" % (mesh, count - 1),
                                rgb=[0.0, 0.0, 0.0], colorDisplayOption=True)
    finally:
        cmds.undoInfo(closeChunk=True)
    if B is not None and B.mesh == mesh:
        B.colors = [[0.0, 0.0, 0.0] for _ in B.pts]
    _say("Da xoa mau tren '%s'." % mesh)


def show_ui():
    if cmds.window(WIN, exists=True):
        cmds.deleteUI(WIN)
    win = cmds.window(WIN, title="Flow Paint - co son huong luoi",
                      widthHeight=(400, 470), sizeable=True)
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
    cmds.button(label="Tao ban nhe de ve (mesh nang thi co giat)", height=26,
                command=lambda *a: _make_proxy())
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
    UI["lazy"] = cmds.floatSliderGrp(
        label="Muot tay", field=True, minValue=0.05, maxValue=1.0,
        value=LAZY, precision=2, columnWidth3=(95, 55, 190),
        changeCommand=lambda *a: _sync(), dragCommand=lambda *a: _sync())
    cmds.text(label="   Muot tay: 0.05 = rat muot nhung i | 1.0 = bam sat con tro",
              align="left")
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
    cmds.button(label="Xoa het mau tren mesh", height=26,
                command=lambda *a: clear_colors())
    cmds.setParent("..")
    cmds.setParent("..")

    cmds.separator(height=6, style="in")
    UI["status"] = cmds.text(label="San sang. Chon mesh hoac bam 'Tao mesh thu'.",
                             align="left")
    cmds.text(label="Ctrl + keo = xoa mau | Ctrl+Z hoan tac tung net",
              align="left")

    cmds.showWindow(win)


show_ui()
