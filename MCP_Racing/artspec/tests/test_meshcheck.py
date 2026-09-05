"""Kiểm module phân tích mesh + luật MESH-* đầu-cuối trên file OBJ thật."""
from __future__ import annotations

import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from artspec import inbox, registry  # noqa: E402
from artspec.readers import meshcheck, obj  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent

# Hộp kín 8 đỉnh, 6 quad, hướng nhất quán, pháp tuyến hướng ra ngoài.
V = [(0, 0, 0), (1, 0, 0), (1, 1, 0), (0, 1, 0),
     (0, 0, 1), (1, 0, 1), (1, 1, 1), (0, 1, 1)]
P = [[0, 3, 2, 1], [4, 5, 6, 7], [0, 1, 5, 4],
     [1, 2, 6, 5], [2, 3, 7, 6], [3, 0, 4, 7]]


def run() -> None:
    c: list[tuple[str, bool, str]] = []

    clean = meshcheck.analyze(V, P)
    c += [
        ("hộp sạch: 12 tam giác", clean["triangle_count"] == 12, str(clean["triangle_count"])),
        ("hộp sạch: 6 quad, 0 n-gon", (clean["quads"], clean["ngons"]) == (6, 0), ""),
        ("hộp sạch: kín, không cạnh biên", clean["is_closed"] and clean["boundary_edges"] == 0, ""),
        ("hộp sạch: không lỗi nào",
         all(clean[k] == 0 for k in ("non_manifold_edges", "flipped_faces", "zero_area_faces",
                                     "duplicate_faces", "duplicate_vertices",
                                     "isolated_vertices", "invalid_index_faces")), ""),
        ("hộp sạch: không bị lộn", clean["inverted_normals"] is False, ""),
    ]

    r = meshcheck.analyze(V, [list(reversed(P[0]))] + P[1:])
    c.append(("lật 1 mặt → chỉ đúng mặt đó",
              (r["flipped_faces"], r["flipped_face_ids"]) == (1, [0]),
              f"{r['flipped_faces']} {r['flipped_face_ids']}"))

    r = meshcheck.analyze(V, [list(reversed(f)) for f in P])
    c.append(("lật cả khối → inverted_normals, KHÔNG báo mặt lẻ",
              r["inverted_normals"] is True and r["flipped_faces"] == 0,
              f"inv={r['inverted_normals']} flip={r['flipped_faces']}"))

    r = meshcheck.analyze(V, P + [[0, 1, 2, 3, 4]])
    c += [("phát hiện n-gon", (r["ngons"], r["ngon_faces"]) == (1, [6]), str(r["ngons"])),
          ("n-gon chồng lên hộp → sinh cạnh non-manifold", r["non_manifold_edges"] > 0, "")]

    c.append(("hộp hở → đếm được cạnh biên",
              meshcheck.analyze(V, P[:-1])["boundary_edges"] == 4,
              str(meshcheck.analyze(V, P[:-1])["boundary_edges"])))

    r = meshcheck.analyze(V + [(0, 0, 0)], P)
    c.append(("đỉnh trùng vị trí", r["duplicate_vertices"] == 1, str(r["duplicate_vertices"])))

    # Cặp đỉnh gần nhau nhưng NẰM HAI BÊN RANH GIỚI Ô của lưới hàn.
    # Bản đầu chỉ so ô của chính điểm nên bỏ lọt các cặp này — tức bỏ lọt seam
    # chưa hàn. Giữ test để không tái phạm.
    quad = [[0, 1, 2, 3], [4, 6, 7, 5]]
    for a, b, want in ((1.0, 1.00005, 1), (1.00004, 1.00006, 1), (1.0, 1.00009, 1),
                       (1.0, 1.0, 1), (1.0, 1.0002, 0), (1.0, 1.5, 0)):
        vs = [(0, 0, 0), (a, 0, 0), (a, 1, 0), (0, 1, 0),
              (b, 0, 0), (b, 1, 0), (2, 0, 0), (2, 1, 0)]
        got = 1 if meshcheck.analyze(vs, quad)["duplicate_vertices"] else 0
        c.append((f"hàn đúng khi cách {abs(b - a):.5f} (ranh giới ô)", got == want,
                  f"mong {want} được {got}"))
    c.append(("đỉnh rời không thuộc mặt nào",
              meshcheck.analyze(V + [(9, 9, 9)], P)["isolated_vertices"] == 1, ""))

    r = meshcheck.analyze(V, P + [[0, 1, 1]])
    c.append(("mặt diện tích 0", r["zero_area_faces"] == 1, str(r["zero_area_faces"])))
    r = meshcheck.analyze(V, P + [P[0]])
    c.append(("mặt trùng nhau", r["duplicate_faces"] == 1, str(r["duplicate_faces"])))

    r = meshcheck.analyze(V, P + [[0, 1, 99]])
    c.append(("index hỏng: không crash, tách thành lỗi riêng",
              r["invalid_index_faces"] == 1 and r["triangle_count"] == 12,
              str(r["invalid_index_faces"])))

    # ── đầu-cuối: OBJ hỏng thật đi qua toàn bộ engine
    with tempfile.TemporaryDirectory() as d:
        sub = Path(d) / "submit" / "vehicle_exterior"
        sub.mkdir(parents=True)
        lines = ["o SM_Broken_Body_LOD0"]
        lines += [f"v {x} {y} {z}" for x, y, z in V]
        lines += ["v 0 0 0", "v 9 9 9"]              # đỉnh trùng vị trí + đỉnh rời
        lines.append("usemtl m")
        faces = [list(reversed(P[0]))] + P[1:]        # 1 mặt lật
        # seam chưa hàn THẬT: mặt này dùng đỉnh 8 thay vì đỉnh 0, cùng vị trí
        faces[2] = [8, 1, 5, 4]
        faces.append([0, 1, 2, 3, 4])                 # n-gon (+ non-manifold)
        lines += ["f " + " ".join(str(i + 1) for i in f) for f in faces]
        (sub / "SM_Broken_Body_LOD0.obj").write_text("\n".join(lines) + "\n", encoding="utf-8")

        reg = registry.load(ROOT)
        out = inbox.check_file(reg, sub / "SM_Broken_Body_LOD0.obj", stage="G1")
        got = {f.rule.id: f.status for f in out.report.findings}
        c += [
            ("đầu-cuối: đọc được file", out.error is None, str(out.error)),
            ("đầu-cuối: bắt n-gon", got.get("MESH-001") == "FAIL", str(got.get("MESH-001"))),
            ("đầu-cuối: bắt non-manifold", got.get("MESH-002") == "FAIL", str(got.get("MESH-002"))),
            ("đầu-cuối: bắt mặt lật", got.get("MESH-003") == "FAIL", str(got.get("MESH-003"))),
            ("đầu-cuối: đỉnh trùng ở mức WARN", got.get("MESH-005") == "WARN", str(got.get("MESH-005"))),
            ("đầu-cuối: OBJ không có đỉnh rời → SKIP, không FAIL",
             got.get("MESH-008") == "SKIP", str(got.get("MESH-008"))),
            ("đầu-cuối: kết luận KHÔNG QUA", out.report.blocked, ""),
        ]
        loc = next(f for f in out.report.findings if f.rule.id == "MESH-003").locations
        c.append(("đầu-cuối: chỉ đúng id mặt để hoạ sĩ tìm",
                  "f[0]" in loc[0].detail, loc[0].detail if loc else "không có location"))

    fails = [x for x in c if not x[1]]
    for name, ok, extra in c:
        print(f"  {'✓' if ok else '✗'} {name}" + (f"   [{extra}]" if not ok and extra else ""))
    print(f"\n{len(c) - len(fails)}/{len(c)} pass")
    if fails:
        raise SystemExit(1)


if __name__ == "__main__":
    run()
