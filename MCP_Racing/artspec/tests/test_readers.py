"""Kiểm reader glTF/GLB/OBJ + luồng inbox đầu-cuối.

glTF được viết tay theo spec rồi ĐỐI CHIẾU CHÉO với trimesh (một cài đặt độc
lập) để chắc chắn số tam giác không phải do tôi tự hiểu sai định dạng.
"""
from __future__ import annotations

import base64
import json
import struct
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from artspec import inbox, registry  # noqa: E402
from artspec.readers import ReaderError, gltf, obj, read  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent

# Một hình hộp: 8 đỉnh, 12 tam giác.
POS = [(-1, -1, -1), (1, -1, -1), (1, 1, -1), (-1, 1, -1),
       (-1, -1, 1), (1, -1, 1), (1, 1, 1), (-1, 1, 1)]
IDX = [0, 1, 2, 0, 2, 3, 4, 6, 5, 4, 7, 6, 0, 4, 5, 0, 5, 1,
       1, 5, 6, 1, 6, 2, 2, 6, 7, 2, 7, 3, 3, 7, 4, 3, 4, 0]


def write_gltf(path: Path, *, name: str, scale, rotation_quat) -> Path:
    pos_b = b"".join(struct.pack("<3f", *p) for p in POS)
    idx_b = struct.pack("<%dH" % len(IDX), *IDX)
    pad = (-len(pos_b)) % 4
    buf = pos_b + b"\x00" * pad + idx_b
    doc = {
        "asset": {"version": "2.0"},
        "scenes": [{"nodes": [0]}], "scene": 0,
        "nodes": [{"name": name, "mesh": 0, "scale": list(scale),
                   "rotation": list(rotation_quat)}],
        "meshes": [{"name": name, "primitives": [
            {"attributes": {"POSITION": 0, "TEXCOORD_0": 2}, "indices": 1,
             "material": 0, "mode": 4}]}],
        "materials": [{"name": "paint"}],
        "images": [{"uri": "T_Box_BC.png"}],
        "textures": [{"source": 0}],
        "accessors": [
            {"bufferView": 0, "componentType": 5126, "count": len(POS), "type": "VEC3",
             "min": [-1, -1, -1], "max": [1, 1, 1]},
            {"bufferView": 1, "componentType": 5123, "count": len(IDX), "type": "SCALAR"},
            {"bufferView": 0, "componentType": 5126, "count": len(POS), "type": "VEC3"},
        ],
        "bufferViews": [
            {"buffer": 0, "byteOffset": 0, "byteLength": len(pos_b), "target": 34962},
            {"buffer": 0, "byteOffset": len(pos_b) + pad, "byteLength": len(idx_b),
             "target": 34963},
        ],
        "buffers": [{"byteLength": len(buf),
                     "uri": "data:application/octet-stream;base64,"
                            + base64.b64encode(buf).decode()}],
    }
    path.write_text(json.dumps(doc), encoding="utf-8")
    return path


def write_png(path: Path, w: int, h: int) -> None:
    """PNG hợp lệ tối thiểu — chỉ cần header đúng để đọc kích thước."""
    def chunk(tag: bytes, data: bytes) -> bytes:
        import zlib
        return (struct.pack(">I", len(data)) + tag + data
                + struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF))
    ihdr = struct.pack(">IIBBBBB", w, h, 8, 6, 0, 0, 0)
    path.write_bytes(b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", ihdr) + chunk(b"IEND", b""))


def run(tmp: Path) -> None:
    checks: list[tuple[str, bool, str]] = []
    sub = tmp / "submit" / "vehicle_exterior"
    sub.mkdir(parents=True)

    # ── glTF: mesh xoay 90° quanh Y, scale âm ⇒ phải bị bắt lỗi transform
    q90y = (0.0, 0.7071067811865476, 0.0, 0.7071067811865476)
    g = write_gltf(sub / "SM_SuvA_Body_LOD0.gltf", name="SM_SuvA_Body_LOD0",
                   scale=(1, 1, -1), rotation_quat=q90y)
    write_png(sub / "T_Box_BC.png", 4096, 4096)

    m = gltf.to_metrics(g)
    mesh = m["meshes"][0]
    checks += [
        ("glTF: đếm tam giác", mesh["triangle_count"] == 12, str(mesh["triangle_count"])),
        ("glTF: đọc scale", mesh["scale"] == [1.0, 1.0, -1.0], str(mesh["scale"])),
        ("glTF: quaternion → euler độ", abs(mesh["rotation"][1] - 90.0) < 0.01,
         str(mesh["rotation"])),
        ("glTF: UV set", mesh["uv_sets"] == ["TEXCOORD_0"], str(mesh["uv_sets"])),
        ("glTF: suy LOD từ tên", mesh["lod"] == 0, str(mesh["lod"])),
        ("glTF: material slot", mesh["material_slots"] == 1, str(mesh["material_slots"])),
    ]

    # ── đối chiếu chéo với trimesh (cài đặt độc lập)
    try:
        import trimesh
        scene = trimesh.load(str(g), force="scene")
        tm_tris = int(sum(len(gm.faces) for gm in scene.geometry.values()))
        checks.append((f"glTF: khớp trimesh ({tm_tris} tris)",
                       tm_tris == mesh["triangle_count"],
                       f"của tôi={mesh['triangle_count']} trimesh={tm_tris}"))
    except ImportError:
        checks.append(("glTF: đối chiếu trimesh (bỏ qua, chưa cài)", True, ""))

    # ── reader dispatcher: đọc kích thước texture + suy asset_class từ thư mục
    full = read(g)
    tex = full["textures"][0]
    checks += [
        ("dispatcher: đọc kích thước PNG", (tex.get("width"), tex.get("height")) == (4096, 4096),
         str(tex)),
        ("dispatcher: suy asset_class từ thư mục",
         full["asset_class"] == "vehicle_exterior", full["asset_class"]),
    ]

    # ── sidecar ghi đè
    (sub / "SM_SuvA_Body_LOD0.submit.json").write_text(
        json.dumps({"asset": "SUV_A", "platform": "console"}), encoding="utf-8")
    checks.append(("dispatcher: sidecar ghi đè asset/platform",
                   read(g)["asset"] == "SUV_A" and read(g)["platform"] == "console", ""))

    # ── OBJ
    o = sub / "SM_SuvA_Glass_LOD0.obj"
    o.write_text("o SM_SuvA_Glass_LOD0\n"
                 "v 0 0 0\nv 1 0 0\nv 1 1 0\nv 0 1 0\n"
                 "vt 0 0\nvt 1 0\nvt 1 1\nvt 0 1\n"
                 "usemtl glass\n"
                 "f 1/1 2/2 3/3 4/4\n", encoding="utf-8")
    om = obj.to_metrics(o)
    checks += [
        ("OBJ: quad → 2 tris", om["meshes"][0]["triangle_count"] == 2,
         str(om["meshes"][0]["triangle_count"])),
        ("OBJ: khai báo không có transform",
         "meshes[].scale" in om["_unavailable"], str(om["_unavailable"])),
    ]

    # ── từ chối file DCC gốc, kèm hướng dẫn
    mb = sub / "SUV_A.mb"
    mb.write_bytes(b"\x00fake")
    try:
        read(mb)
        checks.append((".mb bị từ chối", False, "không raise"))
    except ReaderError as e:
        checks.append((".mb bị từ chối kèm 2 hướng xử lý",
                       "FBX" in str(e) and "mayapy" in str(e), ""))

    # ── đầu-cuối: Lead quét cả thư mục nộp bài
    reg = registry.load(ROOT)
    outs = inbox.check_folder(reg, tmp / "submit")
    rows = inbox.summary_rows(outs)
    by_file = {r["file"]: r for r in rows}
    gltf_row = by_file["SM_SuvA_Body_LOD0.gltf"]
    checks += [
        ("inbox: quét được cả 2 file đọc được", len(rows) == 2, str(list(by_file))),
        ("inbox: bắt lỗi transform trên glTF", gltf_row["fail"] >= 1, str(gltf_row)),
        ("inbox: có luật SKIP vì nguồn thiếu chỉ số", gltf_row["skip"] >= 1, str(gltf_row)),
        ("inbox: kết luận KHÔNG QUA", gltf_row["verdict"] == "KHÔNG QUA", gltf_row["verdict"]),
    ]
    ids = [f.rule.id for f in outs[0].report.findings if f.status == "FAIL"]
    checks.append(("inbox: đúng luật VEH-XFM-001 bị bắt", "VEH-XFM-001" in ids, str(ids)))

    fails = [c for c in checks if not c[1]]
    for name, ok, extra in checks:
        print(f"  {'✓' if ok else '✗'} {name}" + (f"   [{extra}]" if not ok and extra else ""))
    print(f"\n{len(checks) - len(fails)}/{len(checks)} pass")
    if fails:
        raise SystemExit(1)

    print("\n" + "=" * 72 + "\nBẢNG TÓM TẮT LEAD NHÌN THẤY:\n")
    from artspec import render
    print(render.inbox_text(rows))


if __name__ == "__main__":
    import tempfile
    with tempfile.TemporaryDirectory() as d:
        run(Path(d))
