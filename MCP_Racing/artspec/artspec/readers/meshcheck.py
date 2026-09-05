"""Phân tích sức khoẻ hình học của mesh từ dữ liệu đỉnh + mặt.

Độc lập với định dạng file: FBX, glTF, OBJ đều đưa về cùng một dạng
(vertices, polygons) rồi gọi `analyze()`.

Mỗi lỗi trả về CẢ số lượng LẪN id của mặt/cạnh/đỉnh vi phạm, để thông điệp lỗi
chỉ đúng chỗ hoạ sĩ cần mở ra sửa — báo "có 12 n-gon" mà không nói ở đâu thì
hoạ sĩ vẫn phải tự dò cả mesh.
"""
from __future__ import annotations

import math
from collections import defaultdict
from typing import Any, Iterable, Sequence

Vec3 = tuple[float, float, float]
MAX_IDS = 12          # số id tối đa liệt kê cho mỗi loại lỗi


def _edges_of(poly: Sequence[int]) -> Iterable[tuple[int, int]]:
    n = len(poly)
    for i in range(n):
        yield poly[i], poly[(i + 1) % n]


def _area(verts: Sequence[Vec3], poly: Sequence[int]) -> float:
    """Diện tích polygon bằng cách quạt tam giác từ đỉnh đầu."""
    if len(poly) < 3:
        return 0.0
    total = 0.0
    a = verts[poly[0]]
    for i in range(1, len(poly) - 1):
        b, c = verts[poly[i]], verts[poly[i + 1]]
        ux, uy, uz = b[0] - a[0], b[1] - a[1], b[2] - a[2]
        vx, vy, vz = c[0] - a[0], c[1] - a[1], c[2] - a[2]
        cx, cy, cz = uy * vz - uz * vy, uz * vx - ux * vz, ux * vy - uy * vx
        total += 0.5 * math.sqrt(cx * cx + cy * cy + cz * cz)
    return total


def _signed_volume(verts: Sequence[Vec3], polys: Sequence[Sequence[int]]) -> float:
    """Thể tích có dấu — âm nghĩa là cả khối bị lộn mặt trong ra ngoài."""
    total = 0.0
    for poly in polys:
        for i in range(1, len(poly) - 1):
            a, b, c = verts[poly[0]], verts[poly[i]], verts[poly[i + 1]]
            total += (a[0] * (b[1] * c[2] - b[2] * c[1])
                      - a[1] * (b[0] * c[2] - b[2] * c[0])
                      + a[2] * (b[0] * c[1] - b[1] * c[0])) / 6.0
    return total


def _flipped_faces(polys: Sequence[Sequence[int]],
                   edge_dirs: dict[tuple[int, int], list[tuple[int, bool]]]) -> set[int]:
    """Tìm ĐÚNG những mặt bị lật, không gắn cờ oan mặt hàng xóm.

    Hai mặt kề đi qua cạnh chung cùng chiều ⇒ một trong hai bị lật, nhưng phép
    so từng cặp không nói được mặt nào. Nên lan truyền hướng từ một mặt mốc qua
    toàn bộ khối liên thông, rồi lấy NHÓM THIỂU SỐ — vì hướng tuyệt đối là quy
    ước, còn cái sai gần như luôn là vài mặt lẻ giữa một khối đúng.
    """
    adj: dict[int, list[tuple[int, bool]]] = defaultdict(list)
    for entries in edge_dirs.values():
        if len(entries) != 2:
            continue                      # bỏ qua cạnh hở và cạnh non-manifold
        (f0, d0), (f1, d1) = entries
        consistent = d0 != d1             # ngược chiều nhau = đúng
        adj[f0].append((f1, consistent))
        adj[f1].append((f0, consistent))

    flipped: set[int] = set()
    seen: set[int] = set()
    for seed in range(len(polys)):
        if seed in seen:
            continue
        orient = {seed: False}
        stack, component = [seed], [seed]
        seen.add(seed)
        while stack:
            f = stack.pop()
            for nb, consistent in adj.get(f, ()):
                want = orient[f] if consistent else not orient[f]
                if nb not in orient:
                    orient[nb] = want
                    seen.add(nb)
                    component.append(nb)
                    stack.append(nb)
        odd = [f for f in component if orient[f]]
        flipped.update(odd if len(odd) * 2 <= len(component)
                       else [f for f in component if not orient[f]])
    return flipped


def analyze(vertices: Sequence[Vec3], polygons: Sequence[Sequence[int]], *,
            weld_topology: bool = False, weld_epsilon: float = 1e-4,
            area_epsilon: float = 1e-9) -> dict[str, Any]:
    """Trả về các chỉ số sức khoẻ mesh.

    `weld_topology=True` dùng cho định dạng runtime (glTF) — nơi đỉnh đã bị tách
    sẵn ở mỗi UV seam. Không hàn lại trước khi phân tích thì mọi seam sẽ bị báo
    nhầm thành lỗ thủng.
    """
    out: dict[str, Any] = {}
    nv = len(vertices)

    # Dữ liệu hỏng không được làm sập cả lượt kiểm — tách ra thành một lỗi riêng.
    bad_faces = [i for i, poly in enumerate(polygons)
                 if any(not (0 <= v < nv) for v in poly)]
    if bad_faces:
        polygons = [p for i, p in enumerate(polygons) if i not in set(bad_faces)]
    out.update(invalid_index_faces=len(bad_faces),
               invalid_index_face_ids=bad_faces[:MAX_IDS])

    # ── hàn theo vị trí: dùng để phát hiện đỉnh trùng, và để dựng topology cho glTF
    key_of: dict[tuple[int, int, int], int] = {}
    weld_map: list[int] = [0] * nv
    inv = 1.0 / weld_epsilon
    for i, v in enumerate(vertices):
        k = (int(round(v[0] * inv)), int(round(v[1] * inv)), int(round(v[2] * inv)))
        weld_map[i] = key_of.setdefault(k, i)
    out["duplicate_vertices"] = nv - len(key_of)

    topo = [[weld_map[i] for i in p] for p in polygons] if weld_topology else polygons

    # ── thống kê mặt
    tris = quads = ngons = degenerate = 0
    ngon_faces: list[int] = []
    degenerate_faces: list[int] = []
    tri_total = 0
    for fid, poly in enumerate(polygons):
        n = len(poly)
        tri_total += max(n - 2, 0)
        if n == 3:
            tris += 1
        elif n == 4:
            quads += 1
        elif n > 4:
            ngons += 1
            if len(ngon_faces) < MAX_IDS:
                ngon_faces.append(fid)
        if n < 3 or _area(vertices, poly) < area_epsilon:
            degenerate += 1
            if len(degenerate_faces) < MAX_IDS:
                degenerate_faces.append(fid)
    out.update(triangle_count=tri_total, polygon_count=len(polygons), vertex_count=nv,
               tris=tris, quads=quads, ngons=ngons, ngon_faces=ngon_faces,
               zero_area_faces=degenerate, zero_area_face_ids=degenerate_faces)

    # ── mặt trùng nhau (cùng tập đỉnh)
    seen: dict[frozenset, int] = {}
    dup_faces: list[int] = []
    dup = 0
    for fid, poly in enumerate(topo):
        k = frozenset(poly)
        if len(k) < 3:
            continue
        if k in seen:
            dup += 1
            if len(dup_faces) < MAX_IDS:
                dup_faces.append(fid)
        else:
            seen[k] = fid
    out.update(duplicate_faces=dup, duplicate_face_ids=dup_faces)

    # ── cạnh: hở (lỗ thủng) và non-manifold
    edge_faces: dict[tuple[int, int], list[int]] = defaultdict(list)
    edge_dirs: dict[tuple[int, int], list[tuple[int, bool]]] = defaultdict(list)
    for fid, poly in enumerate(topo):
        for a, b in _edges_of(poly):
            if a == b:
                continue
            key = (a, b) if a < b else (b, a)
            edge_faces[key].append(fid)
            edge_dirs[key].append((fid, a < b))

    boundary = [e for e, f in edge_faces.items() if len(f) == 1]
    nonman = [e for e, f in edge_faces.items() if len(f) > 2]
    out.update(
        boundary_edges=len(boundary),
        boundary_edge_ids=[f"{a}-{b}" for a, b in boundary[:MAX_IDS]],
        non_manifold_edges=len(nonman),
        non_manifold_edge_ids=[f"{a}-{b}" for a, b in nonman[:MAX_IDS]],
        is_closed=not boundary and not nonman,
    )

    # ── mặt bị lật
    bad_dir_faces = _flipped_faces(topo, edge_dirs)
    out.update(flipped_faces=len(bad_dir_faces),
               flipped_face_ids=sorted(bad_dir_faces)[:MAX_IDS])

    # ── cả khối bị lộn (chỉ xác định được khi mesh kín và hướng nhất quán)
    if out["is_closed"] and not bad_dir_faces:
        out["inverted_normals"] = _signed_volume(vertices, topo) < 0
    else:
        out["inverted_normals"] = None

    # ── đỉnh rời không thuộc mặt nào
    used = {i for poly in polygons for i in poly}
    loose = [i for i in range(nv) if i not in used]
    out.update(isolated_vertices=len(loose), isolated_vertex_ids=loose[:MAX_IDS])

    return out


def unreliable_for_runtime_format() -> list[str]:
    """Chỉ số KHÔNG đáng tin khi đọc từ định dạng runtime như glTF.

    glTF luôn tam giác hoá và tách đỉnh ở mỗi UV seam, nên số n-gon, số quad và
    số đỉnh trùng ở đó không phản ánh topology mà hoạ sĩ dựng trong DCC.
    """
    return ["ngons", "quads", "tris", "duplicate_vertices"]
