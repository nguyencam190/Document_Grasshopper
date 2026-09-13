"""Cọ sơn hướng lưới kiểu ZBrush — chạy BÊN TRONG Maya.

Hoạ sĩ dùng cọ này sơn hai họ vệt màu chỉ hướng lưới lên mặt scan, rồi
`retopo_paint.build_from_paint()` đọc các vệt đó dựng thành lưới quad.

So với Paint Vertex Color Tool sẵn có của Maya, cọ này thêm ba thứ cần cho
việc vẽ hướng lưới:

* **LazyMouse** — đầu cọ bám trễ sau con trỏ nên nét vẽ mượt dù tay run. Xử lý
  nhiễu NGAY LÚC VẼ, đỡ phải lọc nhiễu ở bước dựng lưới.
* **Đổi nhanh hai màu U/V** — `paint_flow.u()` / `paint_flow.v()`, gán phím tắt
  được, không phải mở bảng màu mỗi lần đổi hướng.
* **Bán kính theo pixel màn hình** — cọ giữ nguyên độ lớn cảm nhận khi zoom
  ra/vào, giống ZBrush; cọ theo đơn vị thế giới thì zoom ra là cọ bé tí.

Không import gì của artspec để bỏ vào Maya chạy độc lập được.

Cách dùng trong Script Editor (Python):

    import sys; sys.path.append(r"<thư mục maya_tools>")
    import paint_flow

    paint_flow.start("scan_hood")   # bật cọ, sơn màu đỏ (họ vệt dọc)
    paint_flow.v()                  # đổi sang lục (họ vệt ngang)
    paint_flow.size(60)             # bán kính 60 pixel
    paint_flow.stop()               # trả về công cụ chọn

Cần numpy (Maya 2022 trở lên có sẵn).
"""
from __future__ import annotations

import numpy as np
from maya import cmds
from maya.api import OpenMaya as om
from maya.api import OpenMayaUI as omui

CTX = "flowPaintCtx"
COLOR_SET = "flowGuide"

U_COLOR = (1.0, 0.0, 0.0)      # đỏ  — họ vệt dọc
V_COLOR = (0.0, 1.0, 0.0)      # lục — họ vệt ngang

# Đầu cọ đi được bao nhiêu phần quãng đường tới con trỏ mỗi lần nhận sự kiện.
# 1.0 = bám sát con trỏ (tắt LazyMouse); càng nhỏ càng mượt nhưng càng ì tay.
LAZY = 0.35

# Khoảng cách tối đa giữa hai dấu cọ liên tiếp, tính theo phần bán kính cọ.
# Rê chuột nhanh mà không chèn dấu ở giữa thì nét bị đứt thành các chấm rời.
SPACING = 0.25

# Số mức lượng tử hoá màu khi ghi lại nét vào undo stack của Maya. Xem _commit.
LEVELS = 12


# ───────────────────────── lưới băm không gian ─────────────────────────

class _Hash:
    """Chia không gian thành ô lập phương để tìm nhanh vertex quanh đầu cọ.

    Duyệt toàn bộ vertex mỗi dấu cọ sẽ giật tay khi mesh nặng. Băm một lần lúc
    bật cọ rồi mỗi dấu chỉ xét vài ô lân cận. Không dùng KD-tree vì Maya không
    có sẵn scipy.
    """

    def __init__(self, pts: np.ndarray, cell: float):
        self.pts = pts
        self.cell = max(cell, 1e-6)
        keys = np.floor(pts / self.cell).astype(np.int64)
        self.table: dict[tuple[int, int, int], list[int]] = {}
        for i, k in enumerate(map(tuple, keys)):
            self.table.setdefault(k, []).append(i)

    # Quá ngưỡng này thì số ô phải duyệt (span³) đắt hơn quét thẳng toàn bộ
    # vertex bằng numpy — xảy ra khi zoom xa làm cọ phủ gần hết mesh.
    MAX_SPAN = 6

    def near(self, centre: np.ndarray, radius: float) -> np.ndarray:
        """Chỉ số các vertex nằm trong bán kính `radius` quanh `centre`."""
        span = int(np.ceil(radius / self.cell))
        if span > self.MAX_SPAN:
            return np.flatnonzero(
                np.linalg.norm(self.pts - centre, axis=1) <= radius)

        c = np.floor(centre / self.cell).astype(np.int64)
        pool: list[int] = []
        for dx in range(-span, span + 1):
            for dy in range(-span, span + 1):
                for dz in range(-span, span + 1):
                    pool.extend(self.table.get(
                        (c[0] + dx, c[1] + dy, c[2] + dz), ()))
        if not pool:
            return np.empty(0, dtype=np.int64)
        idx = np.asarray(pool, dtype=np.int64)
        keep = np.linalg.norm(self.pts[idx] - centre, axis=1) <= radius
        return idx[keep]


# ───────────────────────── trạng thái cọ ─────────────────────────

class _Brush:
    def __init__(self, mesh: str, color_set: str):
        self.mesh = mesh
        self.color_set = color_set
        self.color = np.array(U_COLOR, dtype=float)
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
        self.pts = np.array([(p.x, p.y, p.z) for p in pts], dtype=float)
        bb = cmds.exactWorldBoundingBox(mesh)
        diag = float(np.linalg.norm(np.array(bb[3:]) - np.array(bb[:3])))
        self.hash = _Hash(self.pts, cell=diag / 60.0)

        self.colors = _read_colors(self.fn, color_set, len(self.pts))
        self.before: dict[int, np.ndarray] = {}   # màu gốc trước nét đang vẽ
        self.touched: set[int] = set()
        self.tip: np.ndarray | None = None        # vị trí đầu cọ (pixel)


_B: _Brush | None = None


def _read_colors(fn: om.MFnMesh, color_set: str, count: int) -> np.ndarray:
    try:
        cols = fn.getVertexColors(color_set)
        return np.array([(c.r, c.g, c.b) for c in cols], dtype=float)
    except RuntimeError:
        return np.zeros((count, 3), dtype=float)


# ───────────────────────── một dấu cọ ─────────────────────────

def _ray(x: float, y: float):
    view = omui.M3dView.active3dView()
    src, vec = view.viewToWorld(int(x), int(y))
    return src, vec


def _world_radius(x: float, y: float, src: om.MPoint, depth: float,
                  px: float) -> float:
    """Đổi bán kính pixel màn hình sang bán kính thế giới tại độ sâu điểm chạm.

    Nhờ vậy cọ giữ nguyên độ lớn cảm nhận khi zoom, giống ZBrush.
    """
    s0, d0 = _ray(x, y)
    s1, d1 = _ray(x + px, y)
    return max(((s0 + d0 * depth) - (s1 + d1 * depth)).length(), 1e-6)


def _dab(x: float, y: float) -> None:
    """Đặt một dấu cọ tại toạ độ pixel (x, y)."""
    b = _B
    src, vec = _ray(x, y)
    hit = b.fn.closestIntersection(
        om.MFloatPoint(src.x, src.y, src.z),
        om.MFloatVector(vec.x, vec.y, vec.z),
        om.MSpace.kWorld, 1e6, False, accelParams=b.accel)
    if not hit:
        return
    centre = np.array([hit[0].x, hit[0].y, hit[0].z])
    radius = _world_radius(x, y, src, (om.MPoint(centre[0], centre[1], centre[2])
                                       - src).length(), b.radius_px)

    idx = b.hash.near(centre, radius)
    if idx.size == 0:
        return

    dist = np.linalg.norm(b.pts[idx] - centre, axis=1)
    # Falloff mượt: đậm đều ở giữa, tắt dần về mép, không cắt cứng.
    w = np.clip(1.0 - (dist / radius) ** 2, 0.0, 1.0) ** 2 * b.opacity

    for i in idx[w > 1e-4].tolist():
        if i not in b.before:
            b.before[i] = b.colors[i].copy()
    b.touched.update(idx[w > 1e-4].tolist())

    target = np.zeros(3) if b.erase else b.color
    k = w[w > 1e-4][:, None]
    sel = idx[w > 1e-4]
    b.colors[sel] = b.colors[sel] * (1 - k) + target * k

    _push(sel, b.colors[sel])


def _push(idx: np.ndarray, cols: np.ndarray) -> None:
    """Ghi màu vào mesh bằng API — nhanh, dùng cho xem trước lúc đang vẽ."""
    arr = om.MColorArray()
    for r, g, bl in cols:
        arr.append(om.MColor((float(r), float(g), float(bl))))
    _B.fn.setVertexColors(arr, [int(i) for i in idx])


# ───────────────────────── callback của draggerContext ─────────────────────────

def _press() -> None:
    b = _B
    b.before.clear()
    b.touched.clear()
    b.erase = "ctrl" in (cmds.draggerContext(CTX, q=True, modifier=True) or "")
    pos = cmds.draggerContext(CTX, q=True, anchorPoint=True)
    b.tip = np.array(pos[:2], dtype=float)
    _dab(*b.tip)


def _drag() -> None:
    b = _B
    raw = np.array(cmds.draggerContext(CTX, q=True, dragPoint=True)[:2], dtype=float)

    # LazyMouse: đầu cọ trôi dần về phía con trỏ thay vì nhảy theo tức thì.
    goal = b.tip + (raw - b.tip) * b.lazy

    # Chèn thêm dấu giữa hai vị trí nếu tay rê nhanh, tránh nét đứt thành chấm.
    # Dấu cuối luôn đặt tại `goal`: rê chậm thì quãng đường ngắn hơn một bước
    # chèn, không có dấu nào ở giữa, thiếu dòng này là nét vẽ mất hẳn.
    step = max(b.radius_px * SPACING, 1.0)
    gap = float(np.linalg.norm(goal - b.tip))
    for t in np.arange(step, gap, step) / max(gap, 1e-9):
        _dab(*(b.tip + (goal - b.tip) * t))
    _dab(*goal)
    b.tip = goal


def _release() -> None:
    _commit()


def _commit() -> None:
    """Ghi lại nét vừa vẽ theo đường đi được vào undo stack của Maya.

    Lúc đang vẽ ta ghi màu bằng API cho nhanh, nhưng API bỏ qua undo queue —
    Ctrl+Z sẽ không hoàn tác được nét vẽ. Nên khi nhả chuột: trả mesh về màu
    gốc (vẫn bằng API, không ai thấy vì Maya chưa vẽ lại màn hình), rồi áp lại
    đúng màu đó qua `polyColorPerVertex` — lệnh này có undo.

    Màu được gom về `LEVELS` mức để số lệnh gọi không phụ thuộc số vertex: vẽ
    với opacity 1 thì gần như mọi vertex nhận đúng màu cọ, chỉ tốn 1-2 lệnh.
    """
    b = _B
    if not b.touched:
        return
    idx = np.array(sorted(b.touched), dtype=np.int64)
    final = b.colors[idx].copy()

    _push(idx, np.stack([b.before[int(i)] for i in idx]))     # trả về màu gốc

    quant = np.round(final * LEVELS) / LEVELS
    cmds.undoInfo(openChunk=True, chunkName="flowPaintStroke")
    try:
        for col in np.unique(quant, axis=0):
            sel = idx[np.all(quant == col, axis=1)]
            cmds.polyColorPerVertex(_components(b.mesh, sel),
                                    rgb=[float(c) for c in col], colorDisplayOption=True)
    finally:
        cmds.undoInfo(closeChunk=True)

    b.colors[idx] = quant
    b.before.clear()
    b.touched.clear()


def _components(mesh: str, idx: np.ndarray) -> list[str]:
    """Gộp chỉ số liên tiếp thành `mesh.vtx[a:b]` cho lệnh ngắn lại."""
    out, start, prev = [], None, None
    for i in idx.tolist() + [None]:
        if prev is not None and i == prev + 1:
            prev = i
            continue
        if start is not None:
            out.append(f"{mesh}.vtx[{start}]" if start == prev
                       else f"{mesh}.vtx[{start}:{prev}]")
        start = prev = i
    return out


# ───────────────────────── điều khiển ─────────────────────────

def start(mesh: str, color_set: str = COLOR_SET) -> str:
    """Bật cọ trên `mesh`. Tự tạo color set và bật hiển thị màu nếu chưa có."""
    global _B
    shape = (cmds.listRelatives(mesh, shapes=True, noIntermediate=True) or [mesh])[0]

    if color_set not in (cmds.polyColorSet(mesh, q=True, allColorSets=True) or []):
        cmds.polyColorSet(mesh, create=True, colorSet=color_set, representation="RGB")
    cmds.polyColorSet(mesh, currentColorSet=True, colorSet=color_set)
    cmds.setAttr(f"{shape}.displayColors", 1)   # không bật thì vẽ xong không thấy gì

    _B = _Brush(mesh, color_set)

    if cmds.draggerContext(CTX, exists=True):
        cmds.deleteUI(CTX)
    cmds.draggerContext(
        CTX, pressCommand=_press, dragCommand=_drag, releaseCommand=_release,
        cursor="crossHair", space="screen")
    cmds.setToolTo(CTX)
    return (f"Cọ bật trên '{mesh}' · màu U (đỏ) · bán kính {_B.radius_px:.0f}px\n"
            "  Ctrl + kéo = xoá màu · paint_flow.v() đổi màu · paint_flow.stop() tắt")


def stop() -> None:
    """Tắt cọ, trả về công cụ chọn."""
    cmds.setToolTo("selectSuperContext")


def _brush() -> _Brush:
    if _B is None:
        raise RuntimeError("Cọ chưa bật. Gọi paint_flow.start('<tên mesh>') trước.")
    return _B


def u() -> None:
    """Đổi sang màu họ vệt dọc."""
    _brush().color = np.array(U_COLOR, dtype=float)


def v() -> None:
    """Đổi sang màu họ vệt ngang."""
    _brush().color = np.array(V_COLOR, dtype=float)


def color(rgb) -> None:
    _brush().color = np.array(rgb, dtype=float)


def size(pixels: float) -> None:
    """Bán kính cọ tính theo pixel màn hình."""
    _brush().radius_px = float(pixels)


def opacity(value: float) -> None:
    _brush().opacity = float(np.clip(value, 0.0, 1.0))


def lazy(value: float) -> None:
    """0.05 = rất mượt và ì · 1.0 = bám sát con trỏ, tắt LazyMouse."""
    _brush().lazy = float(np.clip(value, 0.05, 1.0))
