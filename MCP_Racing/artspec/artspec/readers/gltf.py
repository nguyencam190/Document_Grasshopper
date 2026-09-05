"""Đọc glTF / GLB. Định dạng mở, cấu trúc JSON — đọc được đầy đủ và chắc chắn."""
from __future__ import annotations

import base64
import json
import math
import re
import struct
from pathlib import Path
from urllib.parse import unquote
from typing import Any

from . import meshcheck

_LOD_RE = re.compile(r"_LOD(\d+)$", re.IGNORECASE)


class GltfError(Exception):
    pass


def _load(path: Path) -> tuple[dict[str, Any], bytes | None]:
    """Trả (tài liệu JSON, chunk nhị phân của GLB nếu có)."""
    if path.suffix.lower() == ".glb":
        data = path.read_bytes()
        if data[:4] != b"glTF":
            raise GltfError("Không phải file GLB hợp lệ.")
        doc: dict[str, Any] | None = None
        blob: bytes | None = None
        off, end = 12, len(data)
        while off + 8 <= end:
            clen, ctype = struct.unpack_from("<I4s", data, off)
            body = data[off + 8: off + 8 + clen]
            if ctype == b"JSON":
                doc = json.loads(body.decode("utf-8"))
            elif ctype.startswith(b"BIN"):
                blob = body
            off += 8 + clen + (-clen % 4)
        if doc is None:
            raise GltfError("GLB không có chunk JSON.")
        return doc, blob
    return json.loads(path.read_text(encoding="utf-8")), None


_COMP = {5120: ("b", 1), 5121: ("B", 1), 5122: ("h", 2), 5123: ("H", 2),
         5125: ("I", 4), 5126: ("f", 4)}
_NCOMP = {"SCALAR": 1, "VEC2": 2, "VEC3": 3, "VEC4": 4, "MAT4": 16}


class _Buffers:
    """Giải mã accessor của glTF thành list Python."""

    def __init__(self, doc: dict[str, Any], base: Path, blob: bytes | None):
        self.doc, self.base, self.blob = doc, base, blob
        self._cache: dict[int, bytes | None] = {}

    def _buffer(self, i: int) -> bytes | None:
        if i in self._cache:
            return self._cache[i]
        buf = self.doc.get("buffers", [])[i]
        uri = buf.get("uri")
        data: bytes | None = None
        if uri is None:
            data = self.blob                      # GLB: chunk BIN
        elif uri.startswith("data:"):
            data = base64.b64decode(uri.split(",", 1)[1])
        else:
            f = self.base / unquote(uri)
            data = f.read_bytes() if f.is_file() else None
        self._cache[i] = data
        return data

    def read(self, accessor_index: int) -> list[Any] | None:
        try:
            acc = self.doc["accessors"][accessor_index]
            if "bufferView" not in acc:
                return None                        # accessor thưa: bỏ qua
            bv = self.doc["bufferViews"][acc["bufferView"]]
            data = self._buffer(bv.get("buffer", 0))
            if data is None:
                return None
            fmt, size = _COMP[acc["componentType"]]
            n = _NCOMP[acc["type"]]
            start = bv.get("byteOffset", 0) + acc.get("byteOffset", 0)
            stride = bv.get("byteStride") or size * n
            out: list[Any] = []
            for i in range(acc["count"]):
                off = start + i * stride
                vals = struct.unpack_from("<" + fmt * n, data, off)
                out.append(vals[0] if n == 1 else vals)
            return out
        except (KeyError, IndexError, struct.error, ValueError):
            return None


def _quat_to_euler_deg(q: list[float]) -> list[float]:
    """glTF lưu xoay dạng quaternion [x,y,z,w]; luật so sánh theo euler độ."""
    x, y, z, w = q
    sinr, cosr = 2 * (w * x + y * z), 1 - 2 * (x * x + y * y)
    roll = math.atan2(sinr, cosr)
    sinp = max(-1.0, min(1.0, 2 * (w * y - z * x)))
    pitch = math.asin(sinp)
    siny, cosy = 2 * (w * z + x * y), 1 - 2 * (y * y + z * z)
    yaw = math.atan2(siny, cosy)
    return [round(math.degrees(v), 4) + 0.0 for v in (roll, pitch, yaw)]


def to_metrics(path: str | Path) -> dict[str, Any]:
    p = Path(path)
    g, blob = _load(p)
    bufs = _Buffers(g, p.parent, blob)
    accessors = g.get("accessors", [])
    gmeshes = g.get("meshes", [])
    nodes = g.get("nodes", [])

    parent_of: dict[int, int] = {}
    for i, n in enumerate(nodes):
        for c in n.get("children", []):
            parent_of[c] = i

    meshes: list[dict[str, Any]] = []
    for ni, node in enumerate(nodes):
        if "mesh" not in node:
            continue
        gm = gmeshes[node["mesh"]]
        name = node.get("name") or gm.get("name") or f"mesh{node['mesh']}"
        tris = 0
        uv_sets: set[str] = set()
        mats: set[int] = set()
        verts: list[tuple[float, float, float]] = []
        polys: list[list[int]] = []
        decoded = True
        for prim in gm.get("primitives", []):
            if prim.get("mode", 4) != 4:
                continue          # chỉ đếm TRIANGLES
            attrs = prim.get("attributes", {})
            if "indices" in prim:
                tris += accessors[prim["indices"]].get("count", 0) // 3
            elif "POSITION" in attrs:
                tris += accessors[attrs["POSITION"]].get("count", 0) // 3
            uv_sets |= {a for a in attrs if a.startswith("TEXCOORD_")}
            if "material" in prim:
                mats.add(prim["material"])

            # gom hình học của mọi primitive thành một mesh để phân tích
            pos = bufs.read(attrs["POSITION"]) if "POSITION" in attrs else None
            if pos is None:
                decoded = False
                continue
            base_i = len(verts)
            verts.extend(tuple(float(c) for c in v[:3]) for v in pos)
            idx = bufs.read(prim["indices"]) if "indices" in prim else list(range(len(pos)))
            if idx is None:
                decoded = False
                continue
            polys.extend([base_i + idx[i], base_i + idx[i + 1], base_i + idx[i + 2]]
                         for i in range(0, len(idx) - 2, 3))
        # glTF tách đỉnh ở mỗi UV seam ⇒ phải hàn theo vị trí trước khi xét topology
        health = (meshcheck.analyze(verts, polys, weld_topology=True)
                  if decoded and verts and polys else {})
        for k in meshcheck.unreliable_for_runtime_format():
            health.pop(k, None)
        entry: dict[str, Any] = {
            **health,
            "name": name,
            "lod": _lod_of(name),
            "triangle_count": tris,
            "uv_sets": sorted(uv_sets),
            "material_slots": len(mats),
            "has_custom_normals": any("NORMAL" in pr.get("attributes", {})
                                      for pr in gm.get("primitives", [])),
        }
        if "matrix" not in node:
            entry["scale"] = [round(float(v), 6) for v in node.get("scale", [1, 1, 1])]
            entry["rotation"] = _quat_to_euler_deg(node.get("rotation", [0, 0, 0, 1]))
        meshes.append(entry)

    unavailable = ["texel_density_px_cm", "hard_edges", "uv_seam_edges",
                   "textures[].color_space",
                   *meshcheck.unreliable_for_runtime_format()]
    if any("scale" not in m for m in meshes):
        unavailable.append("meshes[].scale / rotation (node dùng ma trận gộp)")

    bones: list[dict[str, Any]] = []
    joint_ids = {j for s in g.get("skins", []) for j in s.get("joints", [])}
    for ji in sorted(joint_ids):
        node = nodes[ji]
        pos = [0.0, 0.0, 0.0]
        safe = True
        cur, guard = ji, 0
        while cur is not None and guard < 64:
            guard += 1
            nd = nodes[cur]
            t = nd.get("translation", [0, 0, 0])
            pos = [pos[i] + float(t[i]) for i in range(3)]
            if cur != ji and (nd.get("rotation") or "matrix" in nd):
                safe = False
                break
            cur = parent_of.get(cur)
        b: dict[str, Any] = {"name": node.get("name") or f"joint{ji}"}
        if safe:
            b["world_position"] = [round(v, 4) for v in pos]
        bones.append(b)
    if any("world_position" not in b for b in bones):
        unavailable.append("skeleton.bones[].world_position")

    textures = []
    for img in g.get("images", []):
        uri = img.get("uri")
        if not uri or uri.startswith("data:"):
            continue
        textures.append({"name": Path(uri).stem, "path": uri})

    return {
        "asset": p.stem,
        "source_file": str(p),
        "dcc": f"gltf-{g.get('asset', {}).get('version', '?')}",
        "reader": "gltf",
        "meshes": meshes,
        "textures": textures,
        "skeleton": {"bones": bones},
        "_unavailable": unavailable,
        "_unavailable_reason": (
            "Reader glTF không lấy được các chỉ số này. Cần collector chạy trong "
            "Maya (collectors/maya_collect.py) cho những luật dùng tới chúng."),
    }


def _lod_of(name: str) -> int | None:
    m = _LOD_RE.search(name)
    return int(m.group(1)) if m else None
