"""Kiểm cọ sơn hướng lưới và bước dựng lưới quad, bằng Maya GIẢ.

Kiểm chứng được: toàn bộ phần toán học — bóp dải sơn về đường tâm, tìm giao hai
nét trên mặt cong, xếp hàng/cột, nối quad, conform ra viền part; và phần logic
của cọ — lưới băm không gian, falloff, LazyMouse, gộp component, ghi undo.

KHÔNG kiểm chứng được: hành vi Maya thật (raycast viewport, đọc/ghi vertex
color, tạo mesh). Chạy `cai_dat/cai_maya_tools.py` rồi `tu_kiem()` trong Maya
thật trước khi tin.
"""
from __future__ import annotations

import sys
import types
from pathlib import Path

import numpy as np

TOOLS = Path(__file__).resolve().parent.parent / "artspec" / "maya_tools"


# ─────────────────────── Maya giả ───────────────────────

class _V3:
    def __init__(s, *a):
        vals = [float(v) for v in a[:3]] or [0.0, 0.0, 0.0]
        s.x, s.y, s.z = vals

    def __sub__(s, o):
        return _V3(s.x - o.x, s.y - o.y, s.z - o.z)

    def __add__(s, o):
        return _V3(s.x + o.x, s.y + o.y, s.z + o.z)

    def __mul__(s, k):
        return _V3(s.x * k, s.y * k, s.z * k)

    def length(s):
        return float(np.linalg.norm([s.x, s.y, s.z]))


class _ColorArray(list):
    pass


CALLS: dict[str, list] = {"setVertexColors": [], "polyColorPerVertex": []}
PTS = np.zeros((1, 3))
POLYS: list = []
SURFACE_Z = 0.0
SCALE = 0.1                      # 1 pixel = 0.1 đơn vị thế giới


class _FnMesh:
    def __init__(s, dag=None):
        pass

    def autoUniformGridParams(s):
        return None

    def getPoints(s, space):
        return [_V3(*p) for p in PTS]

    @property
    def numPolygons(s):
        return len(POLYS)

    def getPolygonVertices(s, i):
        return POLYS[i]

    def getVertexColors(s, cs=None):
        return [(0.0, 0.0, 0.0)] * len(PTS)

    def setVertexColors(s, colors, idx, *a, **k):
        CALLS["setVertexColors"].append((list(idx), [tuple(c) for c in colors]))

    def closestIntersection(s, src, vec, space, mx, both, **k):
        if abs(vec.z) < 1e-9:
            return None
        t = (SURFACE_Z - src.z) / vec.z
        if t < 0:
            return None
        return (_V3(src.x + vec.x * t, src.y + vec.y * t, SURFACE_Z), t, 0, 0, 0.0, 0.0)


def _install_fake_maya() -> None:
    maya = types.ModuleType("maya")
    cmds = types.ModuleType("maya.cmds")
    api = types.ModuleType("maya.api")
    om = types.ModuleType("maya.api.OpenMaya")
    omui = types.ModuleType("maya.api.OpenMayaUI")

    om.MPoint = om.MFloatPoint = om.MVector = om.MFloatVector = _V3
    om.MColor = lambda t: t
    om.MColorArray = _ColorArray
    om.MSpace = types.SimpleNamespace(kWorld=4, kObject=2)
    om.MFnMesh = _FnMesh
    om.MPointArray = list
    for n in ("MSelectionList", "MItMeshPolygon", "MItMeshVertex", "MItMeshEdge",
              "MFnDagNode", "MDagPath"):
        setattr(om, n, type(n, (), {}))

    # viewToWorld nhận điểm và vector làm THAM SỐ RA, không trả về chúng — Maya
    # giả phải theo đúng chữ ký này, không thì bộ kiểm bỏ lọt lỗi gọi sai.
    def view_to_world(x, y, pt, vec):
        pt.x, pt.y, pt.z = x * SCALE, y * SCALE, 10.0
        vec.x, vec.y, vec.z = 0.0, 0.0, -1.0
        return True

    omui.M3dView = types.SimpleNamespace(active3dView=lambda: types.SimpleNamespace(
        viewToWorld=view_to_world))

    cmds.exactWorldBoundingBox = lambda m: [-5, -5, -1, 5, 5, 1]
    cmds.polyColorPerVertex = lambda c, **k: CALLS["polyColorPerVertex"].append((c, k))
    cmds.undoInfo = lambda **k: None
    cmds.polyColorSet = lambda *a, **k: []
    cmds.setAttr = cmds.setToolTo = lambda *a, **k: None
    cmds.listRelatives = lambda *a, **k: ["shp"]
    cmds.draggerContext = lambda *a, **k: None

    maya.cmds, maya.api, api.OpenMaya, api.OpenMayaUI = cmds, api, om, omui
    sys.modules.update({"maya": maya, "maya.cmds": cmds, "maya.api": api,
                        "maya.api.OpenMaya": om, "maya.api.OpenMayaUI": omui})


_install_fake_maya()
sys.path.insert(0, str(TOOLS))

import paint_flow as pf          # noqa: E402
import retopo_paint as rp        # noqa: E402

from maya import cmds            # noqa: E402


# ─────────────────────── mặt cong giả để vẽ lên ───────────────────────

SP = 0.25                        # khoảng cách vertex trên scan giả


def dome(x, z):
    return 1.2 * np.cos(x * 0.25) * np.cos(z * 0.25)


def band(fixed: float, axis: int, half: float) -> np.ndarray:
    """Dải điểm đã sơn: rộng `2*half` quanh vị trí `fixed`, chạy hết mặt."""
    pts = []
    for a in np.arange(-5, 5 + 1e-9, SP):
        for b in np.arange(fixed - half, fixed + half + 1e-9, SP):
            x, z = (b, a) if axis == 0 else (a, b)
            pts.append([x, dome(x, z), z])
    return np.array(pts)


def arc(radius: float, half: float) -> np.ndarray:
    pts = []
    for ang in np.linspace(0.15 * np.pi, 0.85 * np.pi, 60):
        for dr in np.arange(-half, half + 1e-9, SP):
            x, z = (radius + dr) * np.cos(ang), (radius + dr) * np.sin(ang)
            pts.append([x, dome(x, z), z])
    return np.array(pts)


def grid_mesh(n: int = 3):
    verts = [np.array([float(i), float(j), 0.0]) for i in range(n) for j in range(n)]
    at = lambda i, j: i * n + j                                    # noqa: E731
    faces = [(at(i, j), at(i + 1, j), at(i + 1, j + 1), at(i, j + 1))
             for i in range(n - 1) for j in range(n - 1)]
    return verts, faces


def square_loop(lo: float, hi: float, n: int) -> np.ndarray:
    t = np.linspace(0, 1, n, endpoint=False)
    up, down = lo + (hi - lo) * t, hi - (hi - lo) * t
    flo, fhi = np.full(n, lo), np.full(n, hi)
    xy = np.vstack([np.stack([up, flo], 1), np.stack([fhi, up], 1),
                    np.stack([down, fhi], 1), np.stack([flo, down], 1)])
    return np.hstack([xy, np.zeros((len(xy), 1))])


def twisted(faces) -> int:
    """Số cạnh xuất hiện hai lần CÙNG chiều — dấu hiệu mặt bị lật."""
    seen, dup = set(), 0
    for f in faces:
        for k in range(len(f)):
            e = (f[k], f[(k + 1) % len(f)])
            dup += e in seen
            seen.add(e)
    return dup


# ─────────────────────── kiểm dựng lưới ───────────────────────

# Không thể định vị đường tâm chính xác hơn một phần khoảng cách vertex, nên
# ngưỡng lấy theo chính mốc đó thay vì một con số tuỳ ý.
WOBBLE = SP * 0.3


def check_thin() -> None:
    """Bóp dải sơn về đường tâm — chỗ này từng sai nặng với nét cọ rộng."""
    for half in (0.0, 0.25, 0.5, 0.75):
        c = rp.thin(band(-3.0, 0, half), SP)
        assert abs(c[:, 0].mean() + 3.0) < 0.02, half
        assert c[:, 0].std() < WOBBLE, f"đường tâm dập dềnh ngang, bề rộng {half}"
        length = float(np.linalg.norm(np.diff(c, axis=0), axis=1).sum())
        # Nhảy sang điểm gần nhất sẽ zigzag ngang dải làm nét dài gấp mấy lần.
        assert length < 12.0, f"nét dài {length:.1f}, phải ~10"

    r = np.linalg.norm(rp.thin(arc(3.0, 0.5), SP)[:, [0, 2]], axis=1)
    assert abs(r.mean() - 3.0) < 0.05, r.mean()
    assert r.std() < WOBBLE, f"nét cong bị nắn méo, lệch chuẩn {r.std():.3f}"


def check_split_and_intersect() -> None:
    pts = np.vstack([band(v, 0, 0.25) for v in (-3.0, 0.0, 3.0)])
    groups = [g for g in rp.split_strokes(pts, rp._spacing(pts) * rp.GAP_FACTOR)
              if len(g) >= 4]
    assert len(groups) == 3, f"tách nhầm {len(groups)} nét, phải 3"

    us = [rp.resample(rp.thin(band(v, 0, 0.5), SP)) for v in (-3.0, 0.0, 3.0)]
    vs = [rp.resample(rp.thin(band(v, 2, 0.5), SP)) for v in (-3.0, 0.0, 3.0)]
    assert rp.intersect(us[0], us[1], 8 * SP) is None, "nét song song không cắt nhau"

    for i, ui in enumerate((-3.0, 0.0, 3.0)):
        for j, vj in enumerate((-3.0, 0.0, 3.0)):
            got = rp.intersect(us[i], vs[j], 8 * SP)
            assert got is not None, f"mất điểm giao ({ui}, {vj})"
            want = np.array([ui, dome(ui, vj), vj])
            assert np.linalg.norm(got[0] - want) < 0.2, np.linalg.norm(got[0] - want)


def check_grid_order() -> None:
    """Hàng/cột suy từ vị trí giao, không theo thứ tự hoạ sĩ vẽ."""
    rp.snap = lambda fn, p: np.array([p[0], dome(p[0], p[2]), p[2]])
    us = [rp.resample(rp.thin(band(v, 0, 0.25), SP)) for v in (-3.0, 0.0, 3.0)]
    vs = [rp.resample(rp.thin(band(v, 2, 0.25), SP)) for v in (-3.0, 0.0, 3.0)]
    grid, hits = rp.build_grid([us[2], us[0], us[1]], vs, object(), 8 * SP)
    assert len(hits) == 9, len(hits)
    xs = [grid[(r, 0)][0] for r in sorted({r for r, _ in grid})]
    assert xs == sorted(xs), f"xếp sai thứ tự hàng: {xs}"


def check_assemble() -> None:
    grid = {(r, c): np.array([float(r), float(c), 0.0])
            for r in range(4) for c in range(3)}
    verts, faces = rp.assemble(grid)
    assert len(faces) == 6, len(faces)
    assert twisted(faces) == 0
    for f in faces:
        q = [verts[i] for i in f]
        assert len(set(f)) == 4
        assert 0.5 * np.linalg.norm(np.cross(q[2] - q[0], q[3] - q[1])) > 1e-9

    del grid[(1, 1)]
    assert len(rp.assemble(grid)[1]) == 2, "ô thiếu góc phải bỏ, không ép quad méo"

    try:
        rp.assemble({(0, 0): np.zeros(3), (5, 5): np.ones(3)})
        raise AssertionError("phải báo lỗi khi không ô nào đủ 4 góc")
    except RuntimeError:
        pass


def check_conform() -> None:
    """Dải quad nối ra viền part, thử cả hai chiều quấn viền."""
    for src in (square_loop(-1.0, 3.0, 10), square_loop(-1.0, 3.0, 10)[::-1].copy()):
        verts, faces = grid_mesh(3)
        n0 = len(verts)
        rep = rp.conform(verts, faces, src)
        assert rep["da_conform"]
        assert len(verts) - n0 == 8 and len(faces) - 4 == 8

        cum, total, seg = rp._arc(src)
        new = np.array(verts[n0:])
        assert max(rp._closest(src, cum, total, seg, p)[2] for p in new) < 1e-9, \
            "đỉnh mới phải nằm đúng trên viền part"
        prm = rp._unwrap(np.array([rp._closest(src, cum, total, seg, p)[1]
                                   for p in new]))
        assert np.all(np.diff(prm) > -1e-9), "dải quad tự xoắn"
        assert twisted(faces) == 0, "dải mới bị lật mặt"

        loops = rp.ordered_loops(rp.boundary_edges(faces))
        assert len(loops) == 1 and len(loops[0]) == 8
        assert all(i >= n0 for i in loops[0]), "biên phải là vành ngoài mới"

    verts, faces = grid_mesh(3)
    closed = faces + [tuple(reversed(rp.ordered_loops(rp.boundary_edges(faces))[0]))]
    assert not rp.conform(verts, closed, square_loop(-1.0, 3.0, 10))["da_conform"]


def check_polygons_and_poles() -> None:
    """Hai ham doc mesh qua MFnMesh, thay cho ba lop iterator de sai chu ky."""
    global POLYS
    POLYS = [(0, 1, 2, 3), (1, 4, 5, 2)]
    assert rp.polygons(_FnMesh()) == POLYS

    # Lưới 2×2 quad: đỉnh giữa có đúng 4 cạnh, các đỉnh còn lại nằm trên biên.
    assert rp._count_poles(grid_mesh(3)[1]) == 0

    # Quạt 5 tam giác quanh một đỉnh: đỉnh giữa bậc 5 và không nằm trên biên.
    fan = [(0, 1 + k, 1 + (k + 1) % 5) for k in range(5)]
    assert rp._count_poles(fan) == 1


def check_loop_helpers() -> None:
    loop = square_loop(-1.0, 3.0, 10)
    cum, total, seg = rp._arc(loop)
    assert abs(total - 16.0) < 1e-6, total
    for p in (np.array([1.0, -3.0, 0.0]), np.array([5.0, 1.0, 0.0])):
        proj, prm, _ = rp._closest(loop, cum, total, seg, p)
        assert np.linalg.norm(rp._at(loop, cum, total, seg, prm) - proj) < 1e-9

    assert np.all(np.diff(rp._unwrap(np.array([0.9, 0.95, 0.02, 0.08]))) > 0)
    inc = rp._increasing(np.array([0.0, 0.5, 0.4, 0.4, 0.9]), 0.01)
    assert np.all(np.diff(inc) > 0)
    wide = rp._increasing(np.linspace(0, 3, 20), 0.01)
    assert wide[-1] - wide[0] <= 0.999 + 1e-9


# ─────────────────────── kiểm cọ sơn ───────────────────────

def _brush(radius_px: float = 10.0):
    global PTS
    g = np.linspace(-2, 2, 41)
    PTS = np.array([[x, y, 0.0] for x in g for y in g])

    b = pf._Brush.__new__(pf._Brush)
    b.mesh, b.color_set = "m", "cs"
    b.color = np.array([1.0, 0.0, 0.0])
    b.radius_px, b.opacity, b.lazy, b.erase = radius_px, 1.0, 0.35, False
    b.fn, b.accel, b.pts = _FnMesh(), None, PTS
    b.hash = pf._Hash(PTS, cell=0.25)
    b.colors = np.zeros((len(PTS), 3))
    b.before, b.touched, b.tip = {}, set(), None
    pf._B = b
    CALLS["setVertexColors"].clear()
    CALLS["polyColorPerVertex"].clear()
    return b


def check_hash() -> None:
    b = _brush()
    for r in (0.15, 0.4, 1.1):
        c = np.array([0.3, -0.6, 0.0])
        brute = set(np.flatnonzero(np.linalg.norm(PTS - c, axis=1) <= r).tolist())
        assert set(b.hash.near(c, r).tolist()) == brute, r
    # Bán kính lớn phải tự chuyển sang quét thẳng, không duyệt ô kiểu vét cạn.
    assert set(b.hash.near(np.zeros(3), 9.0).tolist()) == set(range(len(PTS)))


def check_dab() -> None:
    b = _brush()
    pf._dab(0.0, 0.0)
    idx, cols = CALLS["setVertexColors"][0]
    d = np.linalg.norm(PTS[idx], axis=1)
    assert d.max() <= 1.0 + 1e-9, "sơn ra ngoài bán kính cọ"
    assert np.allclose(b.colors[int(idx[np.argmin(d)])], [1, 0, 0], atol=1e-6)
    reds = np.array([c[0] for c in cols])[np.argsort(d)]
    assert np.all(np.diff(reds) <= 1e-9), "falloff phải nhạt dần ra mép"

    b.erase = True
    centre = int(idx[np.argmin(d)])
    pf._dab(0.0, 0.0)
    assert b.colors[centre][0] < 0.5, "Ctrl+kéo phải xoá màu"


def check_stroke() -> None:
    b = _brush()
    b.tip = np.array([0.0, 0.0])
    cmds.draggerContext = lambda *a, **k: ([100.0, 0.0, 0.0] if k.get("dragPoint")
                                           else "none")
    pf._drag()
    assert abs(b.tip[0] - 35.0) < 1e-6, "LazyMouse phải bám trễ sau con trỏ"

    # Rê chậm: quãng đường ngắn hơn một bước chèn dấu. Thiếu dấu cuối ở `goal`
    # thì nét vẽ mất hẳn khi vẽ chậm — đúng lỗi đã từng có.
    b.tip, b.radius_px = np.array([0.0, 0.0]), 40.0
    CALLS["setVertexColors"].clear()
    cmds.draggerContext = lambda *a, **k: ([2.0, 0.0, 0.0] if k.get("dragPoint")
                                           else "none")
    pf._drag()
    assert CALLS["setVertexColors"], "rê chậm mà không đặt dấu nào"

    b.tip, b.radius_px = np.array([0.0, 0.0]), 10.0
    CALLS["setVertexColors"].clear()
    cmds.draggerContext = lambda *a, **k: ([40.0, 0.0, 0.0] if k.get("dragPoint")
                                           else "none")
    pf._drag()
    assert len(CALLS["setVertexColors"]) >= 5, "rê nhanh phải chèn dấu ở giữa"


def check_commit() -> None:
    b = _brush()
    pf._dab(0.0, 0.0)
    n = len(b.touched)
    CALLS["setVertexColors"].clear()
    CALLS["polyColorPerVertex"].clear()
    pf._commit()

    assert len(CALLS["setVertexColors"]) == 1
    assert all(tuple(c) == (0.0, 0.0, 0.0) for c in CALLS["setVertexColors"][0][1]), \
        "phải trả mesh về màu gốc trước khi ghi lại bằng lệnh có undo"

    calls = CALLS["polyColorPerVertex"]
    assert calls, "không ghi lại qua polyColorPerVertex thì Ctrl+Z vô tác dụng"
    assert len(calls) <= pf.LEVELS + 1, "số lệnh không được phụ thuộc số vertex"

    total = 0
    for comps, _ in calls:
        for s in comps:
            inner = s[s.index("[") + 1:-1]
            total += (int(inner.split(":")[1]) - int(inner.split(":")[0]) + 1
                      if ":" in inner else 1)
    assert total == n, f"ghi {total} vertex, đã sơn {n}"


def check_components() -> None:
    assert pf._components("m", np.array([1, 2, 3, 7, 9, 10])) == \
        ["m.vtx[1:3]", "m.vtx[7]", "m.vtx[9:10]"]
    assert pf._components("m", np.array([5])) == ["m.vtx[5]"]


def check_guard() -> None:
    pf._B = None
    try:
        pf.u()
        raise AssertionError("phải báo lỗi khi cọ chưa bật")
    except RuntimeError as e:
        assert "start" in str(e)


def run_checks() -> None:
    for fn in (check_thin, check_split_and_intersect, check_grid_order,
               check_assemble, check_conform, check_polygons_and_poles,
               check_loop_helpers,
               check_hash, check_dab, check_stroke, check_commit,
               check_components, check_guard):
        fn()
        print(f"  ok  {fn.__name__[6:]}")
    print("maya_tools: tất cả OK")


if __name__ == "__main__":
    run_checks()
