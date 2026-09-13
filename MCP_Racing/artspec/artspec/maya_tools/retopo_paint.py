"""Dựng lưới quad từ vệt màu hoạ sĩ vẽ trên scan — chạy BÊN TRONG Maya.

Phân vai: hoạ sĩ vẽ hai họ vệt màu (dọc + ngang) chỉ hướng lưới mong muốn lên
mặt scan; module này biến các vệt đó thành lưới quad bám mặt scan.

Không import gì của artspec để bỏ vào Maya chạy độc lập được (cùng quy ước với
`adapters/maya_runner.py`).

Không tạo NURBS curve nào trong scene: mọi bước trung gian là mảng điểm numpy,
chỉ chạm vào Maya ở hai đầu — đọc màu vertex vào, ghi mesh quad ra.

Cách dùng nhanh trong Script Editor (Python) của Maya:

    import retopo_paint
    bao_cao = retopo_paint.build_from_paint(
        "scan_hood",                 # mesh đã sơn màu
        u_color=(1, 0, 0),           # đỏ  = họ vệt dọc
        v_color=(0, 1, 0),           # lục = họ vệt ngang
    )
    print(retopo_paint.report_text(bao_cao))

Cần numpy (Maya 2022 trở lên có sẵn).
"""
from __future__ import annotations

import numpy as np
from maya import cmds
from maya.api import OpenMaya as om

# Hai vertex cùng vệt được coi là liền nhau khi cách nhau dưới
# GAP_FACTOR × (khoảng cách trung bình giữa các vertex đã sơn). Trên ngưỡng đó
# coi là hai nét vẽ khác nhau. 3.0 đủ rộng để nét vẽ tay hơi đứt quãng vẫn liền,
# đủ hẹp để hai nét song song không bị dính làm một.
GAP_FACTOR = 3.0

# Số điểm resample lại cho mỗi vệt sau khi sắp thứ tự.
SAMPLES = 160

# Hai vệt được coi là có giao nhau khi khoảng cách gần nhất giữa chúng nhỏ hơn
# ngưỡng này × chiều dài đường chéo bounding box của mesh.
CROSS_TOL = 0.02


# ───────────────────────── đọc dữ liệu từ Maya ─────────────────────────

def _dag(mesh: str) -> om.MDagPath:
    sel = om.MSelectionList()
    sel.add(mesh)
    dag = sel.getDagPath(0)
    dag.extendToShape()
    return dag


def _points(fn: om.MFnMesh) -> np.ndarray:
    pts = fn.getPoints(om.MSpace.kWorld)
    return np.array([(p.x, p.y, p.z) for p in pts], dtype=float)


def read_painted(fn: om.MFnMesh, color: tuple[float, float, float],
                 color_set: str | None, tol: float) -> np.ndarray:
    """Trả về chỉ số các vertex có màu gần `color` trong sai số `tol`.

    So màu theo khoảng cách RGB. Vertex chưa sơn trả về màu mặc định nên bị
    loại tự nhiên, không cần lọc riêng.
    """
    cols = fn.getVertexColors(color_set) if color_set else fn.getVertexColors()
    rgb = np.array([(c.r, c.g, c.b) for c in cols], dtype=float)
    dist = np.linalg.norm(rgb - np.asarray(color, dtype=float), axis=1)
    return np.flatnonzero(dist <= tol)


# ───────────────────────── tách và sắp vệt ─────────────────────────

def split_strokes(pts: np.ndarray, gap: float) -> list[np.ndarray]:
    """Tách một đám điểm cùng màu thành từng nét vẽ riêng.

    Gộp theo liên thông khoảng cách: hai điểm cách nhau dưới `gap` thuộc cùng
    nét. Cần bước này vì hoạ sĩ vẽ nhiều đường song song bằng CÙNG một màu —
    nếu không tách, cả họ vệt sẽ bị coi là một đường duy nhất.
    """
    n = len(pts)
    seen = np.zeros(n, dtype=bool)
    out: list[np.ndarray] = []
    for start in range(n):
        if seen[start]:
            continue
        queue, group = [start], []
        seen[start] = True
        while queue:
            i = queue.pop()
            group.append(i)
            near = np.flatnonzero(
                (np.linalg.norm(pts - pts[i], axis=1) <= gap) & ~seen)
            seen[near] = True
            queue.extend(near.tolist())
        out.append(np.asarray(group))
    return out


def _params_on(poly: np.ndarray, pts: np.ndarray) -> np.ndarray:
    """Vị trí 0..1 của từng điểm khi chiếu lên đường gấp khúc HỞ `poly`."""
    a, b = poly[:-1], poly[1:]
    ab = b - a
    l2 = np.einsum("ij,ij->i", ab, ab)
    seg = np.sqrt(l2)
    cum = np.concatenate([[0.0], np.cumsum(seg)])
    total = max(float(cum[-1]), 1e-12)

    d = pts[:, None, :] - a[None, :, :]
    t = np.clip(np.einsum("ijk,jk->ij", d, ab) / np.maximum(l2, 1e-12), 0.0, 1.0)
    proj = a[None, :, :] + ab[None, :, :] * t[..., None]
    k = np.argmin(np.linalg.norm(proj - pts[:, None, :], axis=2), axis=1)
    rows = np.arange(len(pts))
    return (cum[k] + t[rows, k] * seg[k]) / total


DEGREE = 6      # bậc đa thức khớp đường tâm — đủ tả cung tròn và nét chữ S
EDGE = 2        # số nhóm ở mỗi đầu nét bị đa thức làm lệch, phải dựng lại


def _bin_average(pts: np.ndarray, key: np.ndarray, steps: int) -> np.ndarray:
    """Gom điểm theo vị trí dọc nét rồi lấy trung bình mỗi nhóm."""
    lo, hi = float(key.min()), float(key.max())
    b = np.clip(((key - lo) / max(hi - lo, 1e-12) * steps).astype(int), 0, steps - 1)
    return np.asarray([pts[b == k].mean(axis=0) for k in range(steps)
                       if np.any(b == k)])


def thin(pts: np.ndarray, spacing: float) -> np.ndarray:
    """Bóp dải điểm đã sơn về một đường tâm mảnh, theo đúng thứ tự dọc nét.

    Cọ thật sơn ra DẢI rộng nhiều vertex chứ không phải đường một điểm. Nếu chỉ
    nhảy từ điểm sang điểm gần nhất để sắp thứ tự thì đường đi zigzag ngang qua
    bề rộng dải — nét dài gấp mấy lần thực tế và điểm giao lệch hẳn.

    Làm hai nhịp:

    1. Khớp một ĐA THỨC BẬC THẤP cho từng toạ độ theo vị trí dọc trục chính PCA.
       Đa thức này chưa dùng làm kết quả — nó chỉ để biết thứ tự dọc nét, kể cả
       khi nét cong (trục PCA thẳng thì xếp sai thứ tự ở nét cong).
    2. Chiếu mọi điểm lên đường vừa khớp, gom các điểm nằm ngang nhau rồi lấy
       trung bình. Đây mới là đường tâm trả về.

    Vì sao không dùng thẳng đa thức ở nhịp 1: nó PHÌNH RA Ở HAI ĐẦU nét (sai số
    dồn hết vào biên miền khớp — bỏ hai đầu thì rất khớp). Bình quân theo nhóm
    không bị vậy, vì nhóm đầu mút đúng bằng trung bình thật của lát cắt ở đó.

    Cũng đã thử lặp bình quân-theo-nhóm nhiều vòng (principal curve) rồi bỏ: nó
    PHÂN KỲ — chỗ đường tâm phình nhẹ về một bên hút thêm điểm bên đó, bình quân
    lại kéo phình thêm; thêm bước làm mượt để ghìm thì chỉ cân bằng ở mức dập
    dềnh cỡ một khoảng cách vertex, không về không.
    """
    if len(pts) < 4:
        return pts

    centred = pts - pts.mean(axis=0)
    axis = np.linalg.svd(centred, full_matrices=False)[2][0]
    key = centred @ axis
    param = (key - key.min()) / max(float(np.ptp(key)), 1e-12)

    count = max(int(float(np.ptp(key)) / max(spacing, 1e-9)), 4)
    degree = max(2, min(DEGREE, len(pts) // 4))
    fit = [np.polynomial.Polynomial.fit(param, pts[:, k], degree) for k in range(3)]
    guide = np.stack([f(np.linspace(0.0, 1.0, count)) for f in fit], axis=1)

    centre = _bin_average(pts, _params_on(guide, pts), count)
    if len(centre) < 2:
        return guide

    # Vài nhóm ĐẦU MÚT vẫn lệch: chỗ đa thức phình ra ở đầu hút mất các điểm
    # phía ngoài dải, nên trung bình nhóm đó lệch theo (không phải do thiếu
    # điểm — số điểm vẫn xấp xỉ các nhóm khác). Bỏ hẳn chúng rồi dựng lại vị trí
    # bằng ngoại suy thẳng từ phần sạch, giữ nguyên chiều dài nét. Phải bỏ đủ
    # EDGE nhóm: ngoại suy từ nhóm kề vốn cũng đã lệch thì càng sai thêm.
    if len(centre) >= 2 * EDGE + 3:
        core = centre[EDGE:-EDGE]
        head = _extend(core, EDGE)[::-1]
        tail = _extend(core[::-1], EDGE)
        centre = np.vstack([head, core, tail[::-1]])
    return centre


def _extend(core: np.ndarray, count: int) -> np.ndarray:
    """Dựng `count` điểm nối thêm phía trước `core[0]`, cách đều như trong core.

    Lấy hướng bằng cách khớp đường thẳng qua vài điểm đầu chứ không chỉ hai
    điểm: vùng lệch ở đầu nét đôi khi lan quá `EDGE` nhóm, khớp nhiều điểm thì
    một điểm còn lệch không kéo được cả hướng đi sai.
    """
    m = min(len(core), 2 * EDGE + 1)
    t = np.arange(m)
    step = np.array([np.polyfit(t, core[:m, k], 1)[0] for k in range(3)])
    return np.array([core[0] - step * j for j in range(1, count + 1)])


def resample(pts: np.ndarray, count: int = SAMPLES) -> np.ndarray:
    """Nội suy lại nét thành `count` điểm cách đều theo chiều dài cung.

    Vừa làm mượt nhiễu tay vẽ, vừa cho hai nét cùng mật độ điểm để bước tìm
    giao ở dưới ổn định. Nội suy tuyến tính theo đoạn — không sinh curve node.
    """
    if len(pts) < 2:
        return pts
    seg = np.linalg.norm(np.diff(pts, axis=0), axis=1)
    arc = np.concatenate([[0.0], np.cumsum(seg)])
    if arc[-1] <= 0:
        return pts
    want = np.linspace(0.0, arc[-1], count)
    return np.stack([np.interp(want, arc, pts[:, k]) for k in range(3)], axis=1)


# ───────────────────────── tìm giao hai nét ─────────────────────────

def _plane_basis(pts: np.ndarray):
    """Mặt phẳng khớp nhất (PCA) cho một đám điểm: trả (gốc, e1, e2)."""
    origin = pts.mean(axis=0)
    _, _, vt = np.linalg.svd(pts - origin, full_matrices=False)
    return origin, vt[0], vt[1]


def intersect(a: np.ndarray, b: np.ndarray, tol: float):
    """Giao điểm giữa hai nét, hoặc None nếu chúng không cắt nhau.

    Làm phẳng CỤC BỘ quanh chỗ hai nét lại gần nhau nhất rồi giải giao hai đoạn
    thẳng trong 2D. Không dùng giao 3D trực tiếp vì hai nét vẽ tay trên mặt
    scan gồ ghề gần như không bao giờ cắt nhau chính xác trong không gian 3D.

    Trả (điểm 3D, t_a, t_b) với t là vị trí tương đối 0..1 dọc mỗi nét — dùng
    để xếp thứ tự các nét ở bước dựng lưới.
    """
    d = np.linalg.norm(a[:, None, :] - b[None, :, :], axis=2)
    ia, ib = np.unravel_index(int(np.argmin(d)), d.shape)
    if d[ia, ib] > tol:
        return None

    # Chỉ lấy đoạn lân cận chỗ giao để mặt phẳng khớp sát thực tế; lấy cả nét
    # thì mặt phẳng bị méo ở vùng cong mạnh.
    span = max(len(a), len(b)) // 6 + 2
    sa = slice(max(ia - span, 0), ia + span + 1)
    sb = slice(max(ib - span, 0), ib + span + 1)
    origin, e1, e2 = _plane_basis(np.vstack([a[sa], b[sb]]))

    def flat(p):
        q = p - origin
        return np.stack([q @ e1, q @ e2], axis=1)

    fa, fb = flat(a[sa]), flat(b[sb])
    hit = _segments_cross(fa, fb)
    if hit is None:
        return None
    xy, ka, kb = hit

    pt = origin + xy[0] * e1 + xy[1] * e2
    t_a = (sa.start + ka) / max(len(a) - 1, 1)
    t_b = (sb.start + kb) / max(len(b) - 1, 1)
    return pt, float(np.clip(t_a, 0, 1)), float(np.clip(t_b, 0, 1))


def _segments_cross(fa: np.ndarray, fb: np.ndarray):
    """Tìm cặp đoạn cắt nhau đầu tiên giữa hai đường gấp khúc 2D."""
    for i in range(len(fa) - 1):
        p, r = fa[i], fa[i + 1] - fa[i]
        for j in range(len(fb) - 1):
            q, s = fb[j], fb[j + 1] - fb[j]
            denom = r[0] * s[1] - r[1] * s[0]
            if abs(denom) < 1e-12:          # song song
                continue
            qp = q - p
            t = (qp[0] * s[1] - qp[1] * s[0]) / denom
            u = (qp[0] * r[1] - qp[1] * r[0]) / denom
            if 0.0 <= t <= 1.0 and 0.0 <= u <= 1.0:
                return p + t * r, i + t, j + u
    return None


def snap(fn: om.MFnMesh, pt: np.ndarray) -> np.ndarray:
    """Kéo một điểm về đúng bề mặt scan gần nhất."""
    p, _ = fn.getClosestPoint(om.MPoint(*pt), om.MSpace.kWorld)
    return np.array([p.x, p.y, p.z])


# ───────────────────────── dựng lưới ─────────────────────────

def build_grid(us: list[np.ndarray], vs: list[np.ndarray], fn: om.MFnMesh,
               tol: float):
    """Giao mọi cặp (nét dọc, nét ngang) rồi xếp thành lưới có hàng/cột.

    Thứ tự hàng/cột KHÔNG lấy theo thứ tự hoạ sĩ vẽ (vẽ lộn xộn là chuyện
    thường) mà suy từ chính vị trí giao: nét dọc nào cắt các nét ngang ở vị trí
    càng sớm dọc theo nét ngang thì xếp càng trước.
    """
    hits: dict[tuple[int, int], tuple[np.ndarray, float, float]] = {}
    for i, u in enumerate(us):
        for j, v in enumerate(vs):
            got = intersect(u, v, tol)
            if got is not None:
                hits[(i, j)] = got

    if not hits:
        return None, hits

    def mean_at(idx, axis):
        vals = [h[2 if axis == 0 else 1]
                for (i, j), h in hits.items() if (i if axis == 0 else j) == idx]
        return float(np.mean(vals)) if vals else np.inf

    u_order = sorted(range(len(us)), key=lambda i: mean_at(i, 0))
    v_order = sorted(range(len(vs)), key=lambda j: mean_at(j, 1))

    grid: dict[tuple[int, int], np.ndarray] = {}
    for r, i in enumerate(u_order):
        for c, j in enumerate(v_order):
            if (i, j) in hits:
                grid[(r, c)] = snap(fn, hits[(i, j)][0])
    return grid, hits


def assemble(grid: dict[tuple[int, int], np.ndarray]):
    """Nối các điểm lưới thành mặt quad — trả (danh sách đỉnh, danh sách mặt).

    Ô nào thiếu góc (hoạ sĩ vẽ nét ngắn không cắt hết) thì bỏ qua ô đó — thà
    hở một ô để sửa tay còn hơn ép ra quad méo.

    Chưa tạo mesh ở đây để bước conform biên còn kịp thêm dải quad vào, rồi mới
    tạo một lần — tránh phải khâu hai mesh rời lại với nhau.
    """
    ids: dict[tuple[int, int], int] = {}
    verts: list[np.ndarray] = []
    for key, pos in sorted(grid.items()):
        ids[key] = len(verts)
        verts.append(pos)

    faces: list[tuple[int, ...]] = []
    for (r, c) in sorted(grid):
        corners = [(r, c), (r + 1, c), (r + 1, c + 1), (r, c + 1)]
        if all(k in ids for k in corners):
            faces.append(tuple(ids[k] for k in corners))

    if not faces:
        raise RuntimeError(
            "Không ô lưới nào đủ 4 góc. Thường là do các nét vẽ chưa cắt nhau "
            "thành lưới — cần vẽ đủ hai họ vệt cắt ngang nhau.")
    return verts, faces


def create_mesh(verts: list[np.ndarray], faces: list[tuple[int, ...]],
                name: str) -> str:
    pts = om.MPointArray()
    for p in verts:
        pts.append(om.MPoint(float(p[0]), float(p[1]), float(p[2])))
    obj = om.MFnMesh().create(pts, [len(f) for f in faces],
                              [i for f in faces for i in f])
    return cmds.rename(om.MFnDagNode(obj).name(), name)


# ───────────────────────── conform vào biên part ─────────────────────────

def boundary_edges(faces) -> list[tuple[int, int]]:
    """Cạnh chỉ thuộc đúng một mặt — tức cạnh nằm ở rìa lưới."""
    count: dict[tuple[int, int], int] = {}
    for f in faces:
        for k in range(len(f)):
            e = (f[k], f[(k + 1) % len(f)])
            key = (min(e), max(e))
            count[key] = count.get(key, 0) + 1
    return [e for e, c in count.items() if c == 1]


def ordered_loops(edges) -> list[list[int]]:
    """Xâu các cạnh rời thành vòng có thứ tự đi vòng quanh."""
    adj: dict[int, list[int]] = {}
    for a, b in edges:
        adj.setdefault(a, []).append(b)
        adj.setdefault(b, []).append(a)

    used: set[int] = set()
    loops: list[list[int]] = []
    for seed in adj:
        if seed in used:
            continue
        loop, cur, prev = [seed], seed, None
        used.add(seed)
        while True:
            nxt = next((n for n in adj[cur] if n != prev and n not in used), None)
            if nxt is None:
                break
            loop.append(nxt)
            used.add(nxt)
            prev, cur = cur, nxt
        loops.append(loop)
    return loops


def _arc(loop: np.ndarray):
    """Chiều dài cộng dồn tới đầu mỗi đoạn của vòng kín, và tổng chu vi."""
    seg = np.linalg.norm(np.roll(loop, -1, axis=0) - loop, axis=1)
    return np.concatenate([[0.0], np.cumsum(seg)[:-1]]), float(seg.sum()), seg


def _closest(loop, cum, total, seg, p):
    """Điểm gần `p` nhất trên vòng kín, kèm vị trí 0..1 dọc theo vòng."""
    a = loop
    ab = np.roll(loop, -1, axis=0) - a
    l2 = np.einsum("ij,ij->i", ab, ab)
    t = np.clip(np.einsum("ij,ij->i", p - a, ab) / np.maximum(l2, 1e-12), 0.0, 1.0)
    proj = a + ab * t[:, None]
    k = int(np.argmin(np.linalg.norm(proj - p, axis=1)))
    return proj[k], (cum[k] + t[k] * seg[k]) / total, float(
        np.linalg.norm(proj[k] - p))


def _at(loop, cum, total, seg, param: float) -> np.ndarray:
    """Toạ độ tại vị trí `param` (0..1) dọc theo vòng kín."""
    d = (param % 1.0) * total
    k = int(np.searchsorted(cum, d, side="right") - 1)
    k = max(0, min(k, len(loop) - 1))
    nxt = loop[(k + 1) % len(loop)]
    return loop[k] + (nxt - loop[k]) * ((d - cum[k]) / max(seg[k], 1e-12))


def _unwrap(params: np.ndarray) -> np.ndarray:
    """Bỏ chỗ nhảy 0.99 → 0.01 để dãy vị trí liên tục, so sánh được."""
    out = [float(params[0])]
    for p in params[1:]:
        step = float(p) - (out[-1] % 1.0)
        out.append(out[-1] + step - round(step))
    return np.array(out)


def _increasing(u: np.ndarray, min_gap: float) -> np.ndarray:
    """Ép dãy tăng dần hẳn để dải quad không tự cắt chéo nhau.

    Hai đỉnh biên cạnh nhau có thể cùng chiếu về một chỗ trên viền (hoặc chiếu
    lộn thứ tự) — cứ để nguyên thì dải quad nối ra viền bị xoắn. Đẩy nhẹ cho
    thứ tự đúng lại, đổi lấy việc vài điểm trượt đi một chút trên viền.
    """
    out = u.astype(float).copy()
    for i in range(1, len(out)):
        out[i] = max(out[i], out[i - 1] + min_gap)
    span = out[-1] - out[0]
    if span > 0.999:                       # đã đẩy quá một vòng, co lại
        out = out[0] + (out - out[0]) * (0.999 / span)
    return out


def conform(verts: list[np.ndarray], faces: list[tuple[int, ...]],
            src_loop: np.ndarray) -> dict:
    """Nối dải quad từ vòng biên của lưới ra đúng đường viền của part.

    Lưới dựng từ điểm giao luôn dừng ở nét vẽ ngoài cùng, còn hở một vành so
    với viền part. Thay vì kéo giãn hàng ngoài cùng ra cho khít (làm méo cả
    vùng rìa), ta giữ nguyên lưới và thêm MỘT dải quad nối ra viền — đúng cách
    hoạ sĩ vá biên bằng tay.

    Đỉnh mới nằm chính xác trên viền part nên hai part cạnh nhau khâu lại được
    bằng cách merge đỉnh trùng vị trí.
    """
    loops = ordered_loops(boundary_edges(faces))
    if not loops:
        return {"da_conform": False, "ly_do": "lưới không có biên hở"}
    ring = max(loops, key=len)

    cum, total, seg = _arc(src_loop)
    if total <= 0:
        return {"da_conform": False, "ly_do": "viền part rỗng"}

    def project(order):
        got = [_closest(src_loop, cum, total, seg, verts[i]) for i in order]
        return np.array([g[1] for g in got]), np.array([g[2] for g in got])

    params, dists = project(ring)
    if _unwrap(params)[-1] < _unwrap(params)[0]:
        ring = ring[::-1]                  # lưới đi ngược chiều viền
        params, dists = project(ring)

    u = _increasing(_unwrap(params), min_gap=0.2 / max(len(ring), 1))
    new_pts = [_at(src_loop, cum, total, seg, p) for p in u]

    base = len(verts)
    verts.extend(new_pts)

    # Giữ chiều quay khớp mặt bên trong, không thì dải mới bị lật mặt.
    directed = {(f[k], f[(k + 1) % len(f)]) for f in faces for k in range(len(f))}
    n = len(ring)
    for i in range(n):
        j = (i + 1) % n
        a, b = ring[i], ring[j]
        faces.append((b, a, base + i, base + j) if (a, b) in directed
                     else (a, b, base + j, base + i))

    return {"da_conform": True, "so_dinh_bien": n,
            "khoang_cach_tb": round(float(np.mean(dists)), 4),
            "khoang_cach_max": round(float(np.max(dists)), 4)}


# ───────────────────────── chấm điểm lưới ─────────────────────────

def score(new_mesh: str, src_fn: om.MFnMesh) -> dict:
    """Đo chất lượng lưới vừa dựng để hoạ sĩ biết chỗ nào cần sửa tay.

    - lech_*      : tâm mỗi quad cách mặt scan bao xa (quad phẳng cắt góc chỗ cong)
    - ty_le_canh  : cạnh dài / cạnh ngắn của quad, càng gần 1 càng vuông vắn
    - do_venh     : góc thứ 4 lệch khỏi mặt phẳng 3 góc kia bao nhiêu
    - so_pole     : đỉnh trong lòng lưới có số cạnh khác 4 — chỗ dễ vỡ shading
    """
    fn = om.MFnMesh(_dag(new_mesh))
    pts = _points(fn)

    dev, ratio, warp = [], [], []
    it = om.MItMeshPolygon(_dag(new_mesh))
    while not it.isDone():
        idx = list(it.getVertices())
        if len(idx) == 4:
            q = pts[idx]
            centre = q.mean(axis=0)
            dev.append(float(np.linalg.norm(snap(src_fn, centre) - centre)))

            edges = np.linalg.norm(np.diff(np.vstack([q, q[:1]]), axis=0), axis=1)
            if edges.min() > 1e-9:
                ratio.append(float(edges.max() / edges.min()))

            nrm = np.cross(q[1] - q[0], q[2] - q[0])
            ln = np.linalg.norm(nrm)
            if ln > 1e-12 and edges.mean() > 1e-9:
                warp.append(float(abs((q[3] - q[0]) @ (nrm / ln)) / edges.mean()))
        it.next()

    poles = 0
    itv = om.MItMeshVertex(_dag(new_mesh))
    while not itv.isDone():
        if not itv.onBoundary() and len(itv.getConnectedEdges()) != 4:
            poles += 1
        itv.next()

    def stat(vals):
        return {"tb": round(float(np.mean(vals)), 4),
                "max": round(float(np.max(vals)), 4)} if vals else None

    return {"so_quad": len(dev), "lech_so_voi_scan": stat(dev),
            "ty_le_canh": stat(ratio), "do_venh": stat(warp), "so_pole": poles}


# ───────────────────────── điểm vào chính ─────────────────────────

def source_boundary(mesh: str, pts: np.ndarray) -> np.ndarray | None:
    """Đường viền hở của part (vòng dài nhất), theo thứ tự đi vòng quanh.

    Part tách ra từ scan luôn có viền hở tại chỗ cắt. Mesh kín (chưa tách part)
    thì không có viền nào — trả None, bỏ qua bước conform.
    """
    edges = []
    it = om.MItMeshEdge(_dag(mesh))
    while not it.isDone():
        if it.onBoundary():
            edges.append((it.vertexId(0), it.vertexId(1)))
        it.next()
    loops = ordered_loops(edges)
    return pts[max(loops, key=len)] if loops else None


def build_from_paint(mesh: str, u_color=(1.0, 0.0, 0.0), v_color=(0.0, 1.0, 0.0),
                     color_set: str | None = None, color_tol: float = 0.25,
                     out_name: str = "retopo_grid", conform_border: bool = True) -> dict:
    """Đọc vệt màu trên `mesh` và dựng lưới quad bám theo hướng đã vẽ.

    `u_color` / `v_color` là màu của hai họ vệt (dọc và ngang). `color_tol` là
    sai số so màu — nới rộng nếu hoạ sĩ vẽ với brush mềm làm màu bị pha.

    `conform_border` nối thêm một dải quad từ rìa lưới ra đúng đường viền part,
    để hai part cạnh nhau khâu lại được. Tắt đi nếu chỉ muốn phần lưới bên trong.
    """
    dag = _dag(mesh)
    fn = om.MFnMesh(dag)
    pts = _points(fn)

    bb = cmds.exactWorldBoundingBox(mesh)
    diag = float(np.linalg.norm(np.array(bb[3:]) - np.array(bb[:3])))
    cross_tol = diag * CROSS_TOL

    families = {}
    for label, col in (("u", u_color), ("v", v_color)):
        idx = read_painted(fn, col, color_set, color_tol)
        if len(idx) < 4:
            raise RuntimeError(
                f"Chỉ tìm thấy {len(idx)} vertex mang màu {col} trên '{mesh}'. "
                "Kiểm tra: đã sơn đúng color set chưa, và màu sơn có khớp tham "
                "số truyền vào không.")
        painted = pts[idx]
        spacing = _spacing(painted)
        strokes = [resample(thin(painted[g], spacing))
                   for g in split_strokes(painted, spacing * GAP_FACTOR)
                   if len(g) >= 4]
        families[label] = strokes

    grid, hits = build_grid(families["u"], families["v"], fn, cross_tol)
    if not grid:
        raise RuntimeError(
            f"Hai họ vệt không cắt nhau (tìm được {len(families['u'])} nét dọc, "
            f"{len(families['v'])} nét ngang). Lưới quad cần hai họ vệt CẮT "
            "NGANG nhau, không phải các nét song song cùng hướng.")

    verts, faces = assemble(grid)

    bien = {"da_conform": False, "ly_do": "đã tắt"}
    if conform_border:
        loop = source_boundary(mesh, pts)
        bien = (conform(verts, faces, loop) if loop is not None
                else {"da_conform": False, "ly_do": "part không có viền hở"})

    name = create_mesh(verts, faces, out_name)
    return {"mesh": name,
            "so_net_doc": len(families["u"]), "so_net_ngang": len(families["v"]),
            "so_diem_giao": len(hits), "bien": bien, "cham_diem": score(name, fn)}


def _spacing(painted: np.ndarray) -> float:
    """Khoảng cách điển hình giữa hai vertex kề nhau trong vùng đã sơn."""
    sample = painted[:400]
    d = np.linalg.norm(sample[:, None, :] - sample[None, :, :], axis=2)
    np.fill_diagonal(d, np.inf)
    return float(np.median(d.min(axis=1)))


def report_text(rep: dict) -> str:
    s = rep["cham_diem"]
    lines = [
        f"Đã dựng: {rep['mesh']}",
        f"  {rep['so_net_doc']} nét dọc × {rep['so_net_ngang']} nét ngang "
        f"→ {rep['so_diem_giao']} điểm giao → {s['so_quad']} quad",
    ]
    b = rep["bien"]
    lines.append(
        f"  Biên: nối {b['so_dinh_bien']} đỉnh ra viền part "
        f"(kéo xa tb {b['khoang_cach_tb']} · max {b['khoang_cach_max']})"
        if b["da_conform"] else f"  Biên: chưa conform — {b['ly_do']}")

    for key, label in (("lech_so_voi_scan", "Lệch so với scan"),
                       ("ty_le_canh", "Tỉ lệ cạnh"), ("do_venh", "Độ vênh")):
        if s[key]:
            lines.append(f"  {label}: tb {s[key]['tb']} · max {s[key]['max']}")
    lines.append(f"  Pole (đỉnh khác 4 cạnh): {s['so_pole']}")
    return "\n".join(lines)
