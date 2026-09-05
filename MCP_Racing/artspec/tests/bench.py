"""Đo thời gian kiểm file — chạy được trên máy bạn để có số của chính máy đó.

    python tests/bench.py            # bộ chuẩn
    python tests/bench.py --big      # thêm mesh 500k tris

Sinh mesh lưới tổng hợp ở nhiều kích thước rồi bấm giờ từng công đoạn:
đọc file → phân tích hình học → chạy luật. Con số phụ thuộc CPU và ổ đĩa, nên
đừng dùng số của máy khác.
"""
from __future__ import annotations

import resource
import statistics
import sys
import tempfile
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from fbxwriter import N, p70, prop, write  # noqa: E402

from artspec import engine, registry  # noqa: E402
from artspec.readers import fbxfile, meshcheck, obj  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent

# (nhãn, số quad mỗi cạnh lưới)  →  tris = 2 * n^2
SIZES = [
    ("prop nhỏ      ~2k tris", 32),
    ("prop vừa     ~13k tris", 80),
    ("prop lớn     ~50k tris", 158),
    ("xe LOD1      ~45k tris", 150),
    ("xe LOD0     ~120k tris", 245),
]
BIG = [("mesh rất nặng ~500k tris", 500), ("high-poly    ~1M tris", 707),
       ("high-poly    ~2M tris", 1000)]


def grid(n: int) -> tuple[list, list]:
    """Lưới n×n quad — topology sạch, kín ở giữa, hở ở biên."""
    verts = [(float(x), float(y), 0.0) for y in range(n + 1) for x in range(n + 1)]
    polys = []
    for y in range(n):
        for x in range(n):
            a = y * (n + 1) + x
            polys.append([a, a + 1, a + n + 2, a + n + 1])
    return verts, polys


def write_obj(path: Path, verts, polys, name: str) -> Path:
    lines = [f"o {name}"]
    lines += [f"v {x} {y} {z}" for x, y, z in verts]
    lines.append("usemtl m")
    lines += ["f " + " ".join(str(i + 1) for i in p) for p in polys]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return path


def write_fbx(path: Path, verts, polys, name: str) -> Path:
    """FBX nhị phân tương đương — để so tốc độ đọc với OBJ text."""
    flat = [c for v in verts for c in v]
    pvi = []
    for poly in polys:
        pvi.extend(poly[:-1])
        pvi.append(-poly[-1] - 1)      # chỉ số cuối mỗi polygon bị đảo bit
    objects = N("Objects", [], [
        N("Geometry", [prop(100, kind="L"), prop("Geometry::g", kind="S"),
                       prop("Mesh", kind="S")], [
            N("Vertices", [prop(flat, kind="d", compress=True)]),
            N("PolygonVertexIndex", [prop(pvi, kind="i", compress=True)]),
            N("LayerElementNormal", [prop(0, kind="I")]),
            N("LayerElementUV", [prop(0, kind="I")], [N("Name", [prop("map1", kind="S")])]),
        ]),
        N("Model", [prop(200, kind="L"), prop(f"Model::{name}", kind="S"),
                    prop("Mesh", kind="S")],
          [p70([("Lcl Scaling", [1.0, 1.0, 1.0]), ("Lcl Rotation", [0.0, 0.0, 0.0])])]),
    ])
    conns = N("Connections", [], [
        N("C", [prop("OO", kind="S"), prop(100, kind="L"), prop(200, kind="L")])])
    write(str(path), [objects, conns])
    return path


def rss_mb() -> float:
    return resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024


def timeit(fn, repeat: int = 3) -> tuple[float, float]:
    """Trả (lần chạy ĐẦU, lần nhanh nhất).

    Lần đầu mới là con số người dùng thật sự gặp — mỗi file chỉ kiểm một lần,
    không bao giờ được "làm nóng". Lần nhanh nhất chỉ để biết trần lý thuyết.
    """
    t = time.perf_counter()
    fn()
    first = time.perf_counter() - t
    best = first
    for _ in range(repeat - 1):
        t = time.perf_counter()
        fn()
        best = min(best, time.perf_counter() - t)
    return first, best


def run(include_big: bool) -> None:
    reg = registry.load(ROOT)
    sizes = SIZES + (BIG if include_big else [])
    rows = []

    with tempfile.TemporaryDirectory() as d:
        tmp = Path(d)
        for label, n in sizes:
            verts, polys = grid(n)
            tris = len(polys) * 2
            fo = write_obj(tmp / f"m{n}.obj", verts, polys, f"SM_Bench{n}_LOD0")
            fb = write_fbx(tmp / f"m{n}.fbx", verts, polys, f"SM_Bench{n}_LOD0")
            mb_o, mb_f = fo.stat().st_size / 1e6, fb.stat().st_size / 1e6

            t_mesh, _ = timeit(lambda: meshcheck.analyze(verts, polys), 1)
            t_obj, _ = timeit(lambda: obj.to_metrics(fo), 1)
            t_fbx, t_fbx_warm = timeit(lambda: fbxfile.to_metrics(fb), 2)
            metrics = {**fbxfile.to_metrics(fb), "asset_class": "vehicle_exterior"}
            t_rules, _ = timeit(lambda: engine.run(reg, metrics), 1)
            rows.append((label, tris, mb_o, mb_f, t_obj, t_fbx, t_fbx_warm,
                         t_mesh, t_rules, rss_mb()))
            del verts, polys, metrics

    print(f"{'':26}{'tris':>10}{'FBX MB':>8} │{'OBJ':>8}{'FBX':>8}{'(warm)':>8} │"
          f"{'luật':>7}{'RAM':>9}")
    print("─" * 88)
    for label, tris, mo, mf, to_, tf, tw, tm, tru, ram in rows:
        print(f"{label:26}{tris:>10,}{mf:>8.1f} │{to_:>7.1f}s{tf:>7.1f}s{tw:>7.1f}s │"
              f"{tru:>6.3f}s{ram:>8.0f}MB")
    print("─" * 88)
    print("Cột FBX = lần chạy đầu (con số thật). (warm) = chạy lại, chỉ để tham khảo.")

    # ── ngoại suy cho các lô thực tế
    per_tri = statistics.median(tf / tris for _, tris, _, _, _, tf, _, _, _, _ in rows)
    print("\nƯỚC TÍNH CHO LÔ THẬT (ngoại suy tuyến tính theo số tam giác)\n")
    scenarios = [
        ("1 xe đầy đủ (LOD0+1+2 ≈ 180k tris)", 180_000),
        ("12 xe trên đường đua", 12 * 180_000),
        ("200 prop môi trường (~5k tris/cái)", 200 * 5_000),
        ("cả depot 2000 asset (~8k tris/cái)", 2000 * 8_000),
    ]
    for name, tris in scenarios:
        s = per_tri * tris
        unit = f"{s:.1f} giây" if s < 90 else f"{s/60:.1f} phút"
        print(f"  {name:42} {tris:>10,} tris   ≈ {unit}")

    ram_per_m = statistics.median(ram / (tris / 1e6)
                                  for _, tris, _, _, _, _, _, _, _, ram in rows if tris > 100_000)
    print(f"\nTốc độ FBX: ~{1/per_tri/1000:,.0f}k tris/giây · RAM ~{ram_per_m:,.0f} MB "
          f"mỗi triệu tris (chỉ máy này).")
    print("CẢNH BÁO: máy ảo dùng chung có thể chênh nhau 2 lần giữa các lần đo.")
    print("Chạy lại trên máy bạn, vài lần, để có số thật của máy đó.")


if __name__ == "__main__":
    run("--big" in sys.argv)
