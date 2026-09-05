"""Kiểm chứng reader FBX bằng file fixture tự sinh.

Test này chứng minh phần ĐỌC CONTAINER đúng (offset, property, zlib, lồng nhau)
và phần dịch semantic chạy đúng trên cấu trúc chuẩn. Nó KHÔNG thay thế được
việc chạy thử trên FBX thật do Maya export — xem README.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from fbxwriter import N, p70, prop, write  # noqa: E402

from artspec.readers import fbxfile  # noqa: E402

# Một quad (4 đỉnh ⇒ 2 tris) + một tam giác (1 tri) = 3 tris.
POLY = [0, 1, 2, -4, 0, 2, -5]   # chỉ số cuối mỗi polygon bị đảo bit
VERTS = [0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 1.0, 1.0, 0.0, 0.0, 1.0, 0.0, -1.0, 0.5, 0.0]


def build(tmp: Path) -> Path:
    objects = N("Objects", [], [
        N("Geometry", [prop(100, kind="L"), prop("Geometry::body", kind="S"),
                       prop("Mesh", kind="S")], [
            N("Vertices", [prop(VERTS, kind="d", compress=True)]),
            N("PolygonVertexIndex", [prop(POLY, kind="i", compress=True)]),
            N("LayerElementNormal", [prop(0, kind="I")]),
            N("LayerElementUV", [prop(0, kind="I")], [N("Name", [prop("map1", kind="S")])]),
        ]),
        N("Model", [prop(200, kind="L"), prop("Model::SM_SuvA_Body_LOD0", kind="S"),
                    prop("Mesh", kind="S")], [
            p70([("Lcl Scaling", [1.0, 1.0, -1.0]), ("Lcl Rotation", [0.0, 90.0, 0.0])]),
        ]),
        N("Material", [prop(300, kind="L"), prop("Material::paint", kind="S"),
                       prop("", kind="S")]),
        N("Material", [prop(301, kind="L"), prop("Material::glass", kind="S"),
                       prop("", kind="S")]),
        N("Texture", [prop(400, kind="L"), prop("Texture::diffuse", kind="S"),
                      prop("", kind="S")], [
            N("RelativeFilename", [prop("textures\\T_SuvA_BC.png", kind="S")]),
        ]),
        N("Model", [prop(500, kind="L"), prop("Model::root", kind="S"),
                    prop("LimbNode", kind="S")], [
            p70([("Lcl Translation", [0.0, 0.0, 0.0])]),
        ]),
        N("Model", [prop(501, kind="L"), prop("Model::WHL_FL", kind="S"),
                    prop("LimbNode", kind="S")], [
            p70([("Lcl Translation", [-78.0, 34.0, 132.0])]),
        ]),
    ])
    conns = N("Connections", [], [
        N("C", [prop("OO", kind="S"), prop(100, kind="L"), prop(200, kind="L")]),
        N("C", [prop("OO", kind="S"), prop(300, kind="L"), prop(200, kind="L")]),
        N("C", [prop("OO", kind="S"), prop(301, kind="L"), prop(200, kind="L")]),
        N("C", [prop("OO", kind="S"), prop(501, kind="L"), prop(500, kind="L")]),
    ])
    p = tmp / "fixture.fbx"
    write(str(p), [objects, conns])
    return p


def run(tmp: Path) -> None:
    path = build(tmp)
    checks: list[tuple[str, bool, str]] = []

    root, version = fbxfile.parse(path)
    checks.append(("version đọc đúng", version == 7400, str(version)))
    checks.append(("có Objects + Connections",
                   {c.name for c in root.children} == {"Objects", "Connections"},
                   str([c.name for c in root.children])))

    geo = root.find("Objects").find("Geometry")
    verts = geo.find("Vertices").prop(0)
    checks.append(("mảng double nén zlib giải đúng",
                   len(verts) == 15 and abs(verts[3] - 1.0) < 1e-9, str(verts[:4])))
    checks.append(("mảng int nén zlib giải đúng",
                   geo.find("PolygonVertexIndex").prop(0) == POLY, ""))

    m = fbxfile.to_metrics(path)
    mesh = m["meshes"][0]
    checks += [
        ("tên mesh bỏ tiền tố Model::", mesh["name"] == "SM_SuvA_Body_LOD0", mesh["name"]),
        ("suy ra LOD từ tên", mesh["lod"] == 0, str(mesh["lod"])),
        ("đếm tris qua chỉ số đảo bit", mesh["triangle_count"] == 3,
         str(mesh["triangle_count"])),
        ("đọc Lcl Scaling", mesh["scale"] == [1.0, 1.0, -1.0], str(mesh["scale"])),
        ("đọc Lcl Rotation", mesh["rotation"] == [0.0, 90.0, 0.0], str(mesh["rotation"])),
        ("đếm material qua Connections", mesh["material_slots"] == 2,
         str(mesh["material_slots"])),
        ("nhận UV set theo tên", mesh["uv_sets"] == ["map1"], str(mesh["uv_sets"])),
        ("nhận custom normal", mesh["has_custom_normals"] is True, ""),
        ("phân tích mesh: đếm quad", mesh["quads"] == 1, str(mesh.get("quads"))),
        ("phân tích mesh: mesh hở nên có cạnh biên",
         mesh["boundary_edges"] > 0, str(mesh.get("boundary_edges"))),
        ("phân tích mesh: không có index hỏng",
         mesh["invalid_index_faces"] == 0, str(mesh.get("invalid_index_faces"))),
        ("lấy tên texture từ RelativeFilename",
         [t["name"] for t in m["textures"]] == ["T_SuvA_BC"], str(m["textures"])),
    ]

    wheel = next(b for b in m["skeleton"]["bones"] if b["name"] == "WHL_FL")
    checks.append(("cộng dồn translation của bone",
                   wheel["world_position"] == [-78.0, 34.0, 132.0],
                   str(wheel.get("world_position"))))
    checks.append(("khai báo chỉ số không lấy được",
                   "texel_density_px_cm" in m["_unavailable"], str(m["_unavailable"])))

    # FBX ASCII phải bị từ chối rõ ràng, không được đọc bừa.
    bad = tmp / "ascii.fbx"
    bad.write_text("; FBX 7.4.0 project file\nFBXHeaderExtension:  {\n}\n")
    try:
        fbxfile.parse(bad)
        checks.append(("từ chối FBX ASCII", False, "không raise"))
    except fbxfile.FbxError as e:
        checks.append(("từ chối FBX ASCII kèm hướng dẫn", "Binary" in str(e), ""))

    fails = [c for c in checks if not c[1]]
    for name, ok, extra in checks:
        print(f"  {'✓' if ok else '✗'} {name}" + (f"   [{extra}]" if not ok and extra else ""))
    print(f"\n{len(checks) - len(fails)}/{len(checks)} pass")
    if fails:
        raise SystemExit(1)


if __name__ == "__main__":
    import tempfile
    with tempfile.TemporaryDirectory() as d:
        run(Path(d))
