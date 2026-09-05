"""Đọc FBX nhị phân — không cần Maya, không cần FBX SDK, không tốn license.

Hai lớp tách bạch:
  * `parse()`  — đọc cấu trúc node của file (container). Phần này bám sát định
    dạng đã được tài liệu hoá rộng rãi và có test đi kèm (tests/test_fbx.py).
  * `to_metrics()` — dịch cây node thành metrics của artspec. Phần này phụ thuộc
    vào cách từng DCC ghi file, nên chỗ nào không chắc thì KHÔNG đoán: bỏ field
    ra khỏi metrics và khai vào `_unavailable`, để engine báo SKIP thay vì báo
    sai cho hoạ sĩ.

Chỉ hỗ trợ FBX **nhị phân** (mặc định của Maya/Max/Blender khi export).
FBX ASCII sẽ bị từ chối kèm hướng dẫn export lại.
"""
from __future__ import annotations

import struct
import zlib
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

MAGIC = b"Kaydara FBX Binary  \x00\x1a\x00"


class FbxError(Exception):
    pass


@dataclass
class Node:
    name: str
    props: list[Any] = field(default_factory=list)
    children: list["Node"] = field(default_factory=list)

    def find(self, name: str) -> "Node | None":
        return next((c for c in self.children if c.name == name), None)

    def find_all(self, name: str) -> list["Node"]:
        return [c for c in self.children if c.name == name]

    def prop(self, i: int, default: Any = None) -> Any:
        return self.props[i] if i < len(self.props) else default


class _Reader:
    def __init__(self, buf: bytes, version: int):
        self.b = buf
        self.p = 0
        self.wide = version >= 7500          # v7.5+ dùng offset 64-bit

    def u8(self) -> int:
        v = self.b[self.p]
        self.p += 1
        return v

    def u32(self) -> int:
        v = struct.unpack_from("<I", self.b, self.p)[0]
        self.p += 4
        return v

    def off(self) -> int:
        if self.wide:
            v = struct.unpack_from("<Q", self.b, self.p)[0]
            self.p += 8
            return v
        return self.u32()

    def raw(self, n: int) -> bytes:
        v = self.b[self.p:self.p + n]
        self.p += n
        return v

    def prop(self) -> Any:
        code = chr(self.u8())
        if code in "YCIFDL":
            fmt = {"Y": "<h", "C": "<?", "I": "<i", "F": "<f", "D": "<d", "L": "<q"}[code]
            size = struct.calcsize(fmt)
            v = struct.unpack_from(fmt, self.b, self.p)[0]
            self.p += size
            return v
        if code in "fdlib":
            length, encoding, comp_len = self.u32(), self.u32(), self.u32()
            data = self.raw(comp_len)
            if encoding == 1:
                data = zlib.decompress(data)
            fmt = {"f": "f", "d": "d", "l": "q", "i": "i", "b": "?"}[code]
            return list(struct.unpack("<" + fmt * length, data))
        if code in "SR":
            data = self.raw(self.u32())
            return data.decode("utf-8", "replace") if code == "S" else data
        raise FbxError(f"Property type '{code}' không hợp lệ tại offset {self.p}")

    def node(self) -> Node | None:
        end, nprops, _plen = self.off(), self.off(), self.off()
        if end == 0:
            return None                       # bản ghi rỗng = hết danh sách
        name = self.raw(self.u8()).decode("utf-8", "replace")
        n = Node(name=name, props=[self.prop() for _ in range(nprops)])
        sentinel = 25 if self.wide else 13
        while self.p < end - sentinel:
            child = self.node()
            if child is None:
                break
            n.children.append(child)
        self.p = end
        return n


def parse(path: str | Path) -> tuple[Node, int]:
    """Trả (node gốc chứa toàn bộ node cấp 1, version)."""
    data = Path(path).read_bytes()
    if not data.startswith(MAGIC):
        if b"FBXHeaderExtension" in data[:4096]:
            raise FbxError(
                "Đây là FBX ASCII. Reader chỉ đọc FBX nhị phân — export lại với "
                "tuỳ chọn Binary (mặc định của Maya/Max/Blender).")
        raise FbxError("Không phải file FBX (thiếu magic header).")
    version = struct.unpack_from("<I", data, 23)[0]
    r = _Reader(data, version)
    r.p = 27
    root = Node(name="<root>")
    while True:
        n = r.node()
        if n is None:
            break
        root.children.append(n)
        if r.p >= len(data) - 16:
            break
    return root, version


# ───────────────────── dịch sang metrics ─────────────────────

def _p70(node: Node, key: str) -> list[Any] | None:
    """Đọc một property trong khối Properties70."""
    props = node.find("Properties70")
    if not props:
        return None
    for p in props.find_all("P"):
        if p.prop(0) == key:
            return list(p.props[4:])
    return None


def _class_of(node: Node) -> str:
    """'Model::Body' -> tên; prop cuối là subclass ('Mesh', 'LimbNode'...)."""
    return str(node.prop(2, ""))


def _name_of(node: Node) -> str:
    raw = str(node.prop(1, ""))
    return raw.split("::", 1)[1] if "::" in raw else raw


def _triangles(poly_index: list[int]) -> int:
    """PolygonVertexIndex: chỉ số cuối của mỗi polygon bị đảo bit (~i)."""
    tris = n = 0
    for idx in poly_index:
        n += 1
        if idx < 0:
            tris += max(n - 2, 0)
            n = 0
    return tris


def to_metrics(path: str | Path) -> dict[str, Any]:
    root, version = parse(path)
    objects = root.find("Objects")
    if objects is None:
        raise FbxError("File FBX không có khối Objects.")
    conns = root.find("Connections")

    geoms = {g.prop(0): g for g in objects.find_all("Geometry")}
    models = {m.prop(0): m for m in objects.find_all("Model")}
    mats = {m.prop(0): m for m in objects.find_all("Material")}

    # Connections dạng OO: [type, childId, parentId]
    child_to_parents: dict[Any, list[Any]] = {}
    for c in (conns.find_all("C") if conns else []):
        if c.prop(0) == "OO":
            child_to_parents.setdefault(c.prop(1), []).append(c.prop(2))

    meshes: list[dict[str, Any]] = []
    for mid, model in models.items():
        if _class_of(model) != "Mesh":
            continue
        geo = next((geoms[gid] for gid, parents in child_to_parents.items()
                    if mid in parents and gid in geoms), None)
        if geo is None:
            continue
        pvi = geo.find("PolygonVertexIndex")
        uv_layers = [str(u.find("Name").prop(0)) if u.find("Name") else f"uv{i}"
                     for i, u in enumerate(geo.find_all("LayerElementUV"))]
        scale = _p70(model, "Lcl Scaling") or [1.0, 1.0, 1.0]
        rot = _p70(model, "Lcl Rotation") or [0.0, 0.0, 0.0]
        n_mats = sum(1 for cid, parents in child_to_parents.items()
                     if mid in parents and cid in mats)
        meshes.append({
            "name": _name_of(model),
            "lod": _lod_of(_name_of(model)),
            "triangle_count": _triangles(pvi.prop(0) or []) if pvi else 0,
            "scale": [round(float(v), 6) for v in scale[:3]],
            "rotation": [round(float(v), 6) for v in rot[:3]],
            "uv_sets": uv_layers,
            "material_slots": n_mats,
            "has_custom_normals": bool(geo.find_all("LayerElementNormal")),
        })

    bones = _bones(models, child_to_parents)
    textures = _textures(objects)

    unavailable = ["texel_density_px_cm", "hard_edges", "uv_seam_edges"]
    if any(b.get("world_position") is None for b in bones):
        # Có bone cha bị xoay ⇒ không cộng dồn translation an toàn được.
        bones = [{k: v for k, v in b.items() if v is not None} for b in bones]
        unavailable.append("skeleton.bones[].world_position")
    if not any("color_space" in t for t in textures):
        unavailable.append("textures[].color_space")

    return {
        "asset": Path(path).stem,
        "source_file": str(path),
        "dcc": f"fbx-{version}",
        "reader": "fbx",
        "meshes": meshes,
        "textures": textures,
        "skeleton": {"bones": bones},
        "_unavailable": unavailable,
        "_unavailable_reason": (
            "Reader FBX không lấy được các chỉ số này. Cần collector chạy trong "
            "Maya (collectors/maya_collect.py) cho những luật dùng tới chúng."),
    }


def _bones(models: dict[Any, Node], child_to_parents: dict[Any, list[Any]]) -> list[dict[str, Any]]:
    """world_position = cộng dồn Lcl Translation theo chuỗi cha.

    CHỈ trả về khi không có bone cha nào bị xoay — nếu có, phép cộng dồn sai và
    ta để trống field thay vì trả số sai (engine sẽ báo SKIP, không báo FAIL).
    """
    out: list[dict[str, Any]] = []
    for mid, model in models.items():
        if _class_of(model) != "LimbNode":
            continue
        pos = [0.0, 0.0, 0.0]
        safe = True
        cur, guard = mid, 0
        while cur is not None and guard < 64:
            guard += 1
            node = models.get(cur)
            if node is None:
                break
            t = _p70(node, "Lcl Translation") or [0.0, 0.0, 0.0]
            pos = [pos[i] + float(t[i]) for i in range(3)]
            if cur != mid:
                r = _p70(node, "Lcl Rotation") or [0.0, 0.0, 0.0]
                if any(abs(float(v)) > 1e-6 for v in r[:3]):
                    safe = False
                    break
            cur = next((p for p in child_to_parents.get(cur, []) if p in models), None)
        out.append({"name": _name_of(model),
                    "world_position": [round(v, 4) for v in pos] if safe else None})
    return out


def _textures(objects: Node) -> list[dict[str, Any]]:
    seen: dict[str, dict[str, Any]] = {}
    for kind in ("Texture", "Video"):
        for t in objects.find_all(kind):
            rel = t.find("RelativeFilename") or t.find("FileName")
            raw = str(rel.prop(0)) if rel else _name_of(t)
            stem = Path(raw.replace("\\", "/")).stem
            if stem and stem not in seen:
                seen[stem] = {"name": stem, "path": raw}
    return list(seen.values())


import re as _re  # noqa: E402

_LOD_RE = _re.compile(r"_LOD(\d+)$", _re.IGNORECASE)


def _lod_of(name: str) -> int | None:
    m = _LOD_RE.search(name)
    return int(m.group(1)) if m else None
