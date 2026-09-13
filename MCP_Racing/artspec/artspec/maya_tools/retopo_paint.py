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


def order_stroke(pts: np.ndarray) -> np.ndarray:
    """Sắp các điểm của một nét theo thứ tự dọc theo nét.

    Bắt đầu từ đầu mút (điểm xa nhất theo trục chính PCA), sau đó liên tục nhảy
    sang điểm chưa duyệt gần nhất. PCA đơn thuần sẽ sai với nét cong (vd vòm
    bánh xe) nên chỉ dùng nó để CHỌN ĐIỂM XUẤT PHÁT, còn thứ tự thì đi theo
    láng giềng gần nhất.
    """
    if len(pts) < 3:
        return pts
    centred = pts - pts.mean(axis=0)
    axis = np.linalg.svd(centred, full_matrices=False)[2][0]
    cur = int(np.argmin(centred @ axis))

    left = np.ones(len(pts), dtype=bool)
    left[cur] = False
    order = [cur]
    while left.any():
        idx = np.flatnonzero(left)
        nxt = idx[int(np.argmin(np.linalg.norm(pts[idx] - pts[cur], axis=1)))]
        order.append(int(nxt))
        left[nxt] = False
        cur = int(nxt)
    return pts[order]


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


def build_quads(grid: dict[tuple[int, int], np.ndarray], name: str) -> str:
    """Nối các điểm lưới thành mặt quad và tạo mesh mới trong scene.

    Ô nào thiếu góc (hoạ sĩ vẽ nét ngắn không cắt hết) thì bỏ qua ô đó — thà
    hở một ô để sửa tay còn hơn ép ra quad méo.
    """
    ids: dict[tuple[int, int], int] = {}
    verts = om.MPointArray()
    for key, pos in sorted(grid.items()):
        ids[key] = len(ids)
        verts.append(om.MPoint(*pos))

    counts, connects = [], []
    for (r, c) in sorted(grid):
        corners = [(r, c), (r + 1, c), (r + 1, c + 1), (r, c + 1)]
        if all(k in ids for k in corners):
            counts.append(4)
            connects.extend(ids[k] for k in corners)

    if not counts:
        raise RuntimeError(
            "Không ô lưới nào đủ 4 góc. Thường là do các nét vẽ chưa cắt nhau "
            "thành lưới — cần vẽ đủ hai họ vệt cắt ngang nhau.")

    obj = om.MFnMesh().create(verts, counts, connects)
    return cmds.rename(om.MFnDagNode(obj).name(), name)


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

def build_from_paint(mesh: str, u_color=(1.0, 0.0, 0.0), v_color=(0.0, 1.0, 0.0),
                     color_set: str | None = None, color_tol: float = 0.25,
                     out_name: str = "retopo_grid") -> dict:
    """Đọc vệt màu trên `mesh` và dựng lưới quad bám theo hướng đã vẽ.

    `u_color` / `v_color` là màu của hai họ vệt (dọc và ngang). `color_tol` là
    sai số so màu — nới rộng nếu hoạ sĩ vẽ với brush mềm làm màu bị pha.
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
        gap = _gap(painted)
        strokes = [resample(order_stroke(painted[g]))
                   for g in split_strokes(painted, gap) if len(g) >= 4]
        families[label] = strokes

    grid, hits = build_grid(families["u"], families["v"], fn, cross_tol)
    if not grid:
        raise RuntimeError(
            f"Hai họ vệt không cắt nhau (tìm được {len(families['u'])} nét dọc, "
            f"{len(families['v'])} nét ngang). Lưới quad cần hai họ vệt CẮT "
            "NGANG nhau, không phải các nét song song cùng hướng.")

    name = build_quads(grid, out_name)
    return {"mesh": name,
            "so_net_doc": len(families["u"]), "so_net_ngang": len(families["v"]),
            "so_diem_giao": len(hits), "cham_diem": score(name, fn)}


def _gap(painted: np.ndarray) -> float:
    """Ngưỡng khoảng cách coi hai điểm là cùng một nét."""
    sample = painted[:400]
    d = np.linalg.norm(sample[:, None, :] - sample[None, :, :], axis=2)
    np.fill_diagonal(d, np.inf)
    return float(np.median(d.min(axis=1))) * GAP_FACTOR


def report_text(rep: dict) -> str:
    s = rep["cham_diem"]
    lines = [
        f"Đã dựng: {rep['mesh']}",
        f"  {rep['so_net_doc']} nét dọc × {rep['so_net_ngang']} nét ngang "
        f"→ {rep['so_diem_giao']} điểm giao → {s['so_quad']} quad",
    ]
    for key, label in (("lech_so_voi_scan", "Lệch so với scan"),
                       ("ty_le_canh", "Tỉ lệ cạnh"), ("do_venh", "Độ vênh")):
        if s[key]:
            lines.append(f"  {label}: tb {s[key]['tb']} · max {s[key]['max']}")
    lines.append(f"  Pole (đỉnh khác 4 cạnh): {s['so_pole']}")
    return "\n".join(lines)
