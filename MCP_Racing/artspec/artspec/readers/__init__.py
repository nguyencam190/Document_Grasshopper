"""Đọc thẳng file 3D do hoạ sĩ gửi lên — không cần mở DCC.

    from artspec.readers import read
    metrics = read("submit/SUV_A.fbx", asset_class="vehicle_exterior")

Định dạng hỗ trợ:
    .fbx            FBX nhị phân (định dạng chính vào UE5)
    .gltf / .glb    glTF 2.0
    .obj            OBJ (hạn chế — không có transform/bone)

.ma / .mb KHÔNG đọc trực tiếp: .mb là nhị phân đóng của Autodesk, .ma là script
MEL nên tự parse rất dễ sai. Dùng collectors/maya_collect.py chạy trong Maya,
hoặc yêu cầu hoạ sĩ nộp kèm FBX.

Chỉ số nào reader không lấy được thì KHÔNG đoán — nó được khai vào `_unavailable`
và engine sẽ báo SKIP thay vì FAIL. Một con số bịa nguy hiểm hơn một ô trống.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from . import fbxfile, gltf, images, obj

SUPPORTED = {".fbx": "fbx", ".gltf": "gltf", ".glb": "gltf", ".obj": "obj",
             ".json": "metrics"}
DCC_NATIVE = {".ma", ".mb", ".max", ".blend", ".c4d", ".ztl"}


class ReaderError(Exception):
    pass


def read(path: str | Path, asset_class: str | None = None,
         platform: str | None = None, asset: str | None = None) -> dict[str, Any]:
    p = Path(path)
    if not p.is_file():
        raise ReaderError(f"Không thấy file: {p}")
    ext = p.suffix.lower()

    if ext in DCC_NATIVE:
        raise ReaderError(
            f"Không đọc trực tiếp được file {ext}. Cách xử lý:\n"
            f"  1. Yêu cầu hoạ sĩ nộp kèm bản export FBX (khuyến nghị — FBX mới là "
            f"thứ thật sự đi vào UE5, và lỗi export chỉ lộ ra ở đó), hoặc\n"
            f"  2. Chạy: mayapy collectors/maya_collect.py --scene \"{p}\" "
            f"--out metrics.json --asset-class <class>")
    if ext not in SUPPORTED:
        raise ReaderError(f"Chưa hỗ trợ định dạng '{ext}'. "
                          f"Đang hỗ trợ: {', '.join(sorted(SUPPORTED))}")

    if SUPPORTED[ext] == "metrics":
        m = json.loads(p.read_text(encoding="utf-8"))
    else:
        try:
            m = {"fbx": fbxfile.to_metrics, "gltf": gltf.to_metrics,
                 "obj": obj.to_metrics}[SUPPORTED[ext]](p)
        except (fbxfile.FbxError, gltf.GltfError) as e:
            raise ReaderError(str(e)) from e
        _resolve_textures(m, p.parent)

    sidecar = p.with_suffix(".submit.json")
    if sidecar.is_file():
        m.update(json.loads(sidecar.read_text(encoding="utf-8")))

    if asset:
        m["asset"] = asset
    if platform:
        m["platform"] = platform
    if asset_class:
        m["asset_class"] = asset_class
    m.setdefault("asset_class", _guess_class(p))
    m.setdefault("platform", "pc")
    return m


def _resolve_textures(m: dict[str, Any], base: Path) -> None:
    """Tìm file ảnh cạnh model để lấy width/height thật."""
    for t in m.get("textures", []):
        rel = str(t.get("path", "")).replace("\\", "/")
        cands = [base / rel, base / Path(rel).name,
                 base / "textures" / Path(rel).name, base.parent / rel]
        for c in cands:
            if c.is_file():
                size = images.size_of(c)
                if size:
                    t["width"], t["height"] = size
                    t["resolved_path"] = str(c)
                break
    if any("width" not in t for t in m.get("textures", [])):
        m.setdefault("_unavailable", []).append("textures[].width / height")


def _guess_class(p: Path) -> str:
    """Suy asset class từ thư mục cha, để Lead không phải gõ mỗi lần.

    Quy ước: file nằm trong .../<asset_class>/... Nếu không khớp thì để trống và
    engine sẽ báo lỗi rõ ràng thay vì áp nhầm bộ luật.
    """
    known = {"vehicle_exterior", "vehicle_interior", "wheels", "environment_prop",
             "building", "vegetation", "road", "terrain"}
    for part in reversed(p.parts):
        if part.lower() in known:
            return part.lower()
    return ""
