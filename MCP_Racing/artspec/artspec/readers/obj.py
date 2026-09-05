"""Đọc OBJ. Định dạng text đơn giản — nhưng KHÔNG chứa transform, bone hay
color space, nên phần lớn luật sẽ báo SKIP. Chỉ hợp để kiểm nhanh tricount,
đặt tên và số material."""
from __future__ import annotations

import re
from pathlib import Path
from typing import Any

from . import meshcheck

_LOD_RE = re.compile(r"_LOD(\d+)$", re.IGNORECASE)


def to_metrics(path: str | Path) -> dict[str, Any]:
    p = Path(path)
    meshes: list[dict[str, Any]] = []
    cur: dict[str, Any] | None = None
    has_uv = False
    all_verts: list[tuple[float, float, float]] = []

    def flush() -> None:
        if cur is None:
            return
        cur["material_slots"] = len(cur.pop("_mats"))
        cur["uv_sets"] = ["uv0"] if cur.pop("_uv") else []
        polys = cur.pop("_polys")
        # OBJ đánh số đỉnh toàn cục và mọi nhóm dùng chung kho đỉnh đó, nên chỉ
        # phân tích các đỉnh mà nhóm này thật sự tham chiếu. Hệ quả: đỉnh trùng
        # KHÔNG được mặt nào dùng sẽ không bị đếm — nhưng đó vốn là lỗi "đỉnh rời",
        # và với OBJ ta đã khai isolated_vertices là không xác định được.
        used = sorted({i for poly in polys for i in poly})
        remap = {g: l for l, g in enumerate(used)}
        local_v = [all_verts[g] for g in used if g < len(all_verts)]
        if len(local_v) == len(used) and polys:
            health = meshcheck.analyze(local_v, [[remap[i] for i in p] for p in polys])
            health.pop("isolated_vertices", None)   # OBJ dùng chỉ số đỉnh toàn cục
            health.pop("isolated_vertex_ids", None)
            cur.update(health)
        meshes.append(cur)

    for line in p.read_text(encoding="utf-8", errors="replace").splitlines():
        parts = line.split()
        if not parts:
            continue
        tag = parts[0]
        if tag in ("o", "g"):
            flush()
            name = " ".join(parts[1:]) or f"group{len(meshes)}"
            cur = {"name": name, "lod": _lod_of(name), "triangle_count": 0,
                   "_mats": set(), "_uv": False, "_polys": []}
        elif tag == "v":
            try:
                all_verts.append(tuple(float(x) for x in parts[1:4]))  # type: ignore[arg-type]
            except (ValueError, IndexError):
                pass
        elif tag == "vt":
            has_uv = True
            if cur is not None:
                cur["_uv"] = True
        elif tag == "usemtl" and cur is not None:
            cur["_mats"].add(" ".join(parts[1:]))
        elif tag == "f":
            if cur is None:
                cur = {"name": p.stem, "lod": _lod_of(p.stem), "triangle_count": 0,
                       "_mats": set(), "_uv": has_uv, "_polys": []}
            cur["triangle_count"] += max(len(parts) - 3, 0)
            idx = []
            for tok in parts[1:]:
                try:
                    i = int(tok.split("/")[0])
                except ValueError:
                    continue
                idx.append(i - 1 if i > 0 else len(all_verts) + i)   # OBJ đếm từ 1
            if len(idx) >= 3:
                cur["_polys"].append(idx)
            if "/" in line and not line.replace("f", "").strip().startswith("/"):
                cur["_uv"] = cur["_uv"] or any(
                    len(t.split("/")) > 1 and t.split("/")[1] for t in parts[1:])
    flush()

    return {
        "asset": p.stem,
        "source_file": str(p),
        "dcc": "obj",
        "reader": "obj",
        "meshes": meshes,
        "textures": [],
        "skeleton": {"bones": []},
        "_unavailable": ["isolated_vertices",
                         "meshes[].scale", "meshes[].rotation", "texel_density_px_cm",
                         "hard_edges", "uv_seam_edges", "textures[].color_space",
                         "skeleton.bones[].world_position"],
        "_unavailable_reason": (
            "OBJ không lưu transform, bone hay color space. Chỉ kiểm được tricount, "
            "tên và số material — dùng FBX hoặc collector Maya cho các luật còn lại."),
    }


def _lod_of(name: str) -> int | None:
    m = _LOD_RE.search(name)
    return int(m.group(1)) if m else None
