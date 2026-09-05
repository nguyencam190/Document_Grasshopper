"""Collector cho Maya — sinh metrics.json cho engine artspec.

    # trong Script Editor của Maya (tab Python):
    import maya_collect; maya_collect.write("D:/tmp/SUV_A.json", asset_class="vehicle_exterior")

    # hoặc headless:
    mayapy maya_collect.py --scene SUV_A.mb --out SUV_A.json --asset-class vehicle_exterior

⚠️ CHƯA CHẠY THỬ TRÊN MAYA THẬT. Viết theo maya.api.OpenMaya 2.0; hãy chạy thử
trên golden asset trước khi phát cho cả team, và đối chiếu vài con số bằng tay
(tricount đọc từ HUD, texel density đọc bằng checker map).

Quy ước cần khớp với dự án — sửa ở đây nếu khác:
  * LOD suy ra từ hậu tố tên `_LOD<n>`
  * texel density tính theo texture size của material đầu tiên gắn vào mesh;
    nếu dự án dùng nhiều size khác nhau trên một mesh thì phải sửa lại hàm này.
"""
from __future__ import annotations

import json
import math
import re

try:
    from maya import cmds
    from maya.api import OpenMaya as om
except ImportError:  # cho phép import ngoài Maya để đọc code / lint
    cmds = None
    om = None

LOD_RE = re.compile(r"_LOD(\d+)$", re.IGNORECASE)

# Dùng chung module phân tích mesh với các reader, để validator trong Maya và
# validator đọc file FBX không bao giờ cho hai kết quả khác nhau.
try:
    import sys as _sys
    from pathlib import Path as _P
    _sys.path.insert(0, str(_P(__file__).resolve().parent.parent))
    from artspec.readers import meshcheck
except ImportError:
    meshcheck = None


def _lod_of(name: str) -> int | None:
    m = LOD_RE.search(name)
    return int(m.group(1)) if m else None


def _dag(name: str):
    sel = om.MSelectionList()
    sel.add(name)
    return sel.getDagPath(0)


def _edges(dag) -> tuple[list[int], list[int]]:
    """Trả (hard_edges, uv_seam_edges) theo id cạnh.

    hard edge  = cạnh không smooth.
    uv seam    = cạnh biên UV: cạnh hở, hoặc hai mặt kề gán UV id khác nhau.
    """
    mesh = om.MFnMesh(dag)
    it = om.MItMeshEdge(dag)
    hard: list[int] = []
    seam: list[int] = []
    while not it.isDone():
        eid = it.index()
        if not it.isSmooth:
            hard.append(eid)
        faces = it.getConnectedFaces()
        v0, v1 = it.vertexId(0), it.vertexId(1)
        if len(faces) < 2:
            seam.append(eid)  # cạnh hở luôn là biên UV
        else:
            uvs = []
            for fid in faces:
                try:
                    uvs.append((mesh.getPolygonUVid(fid, _local_index(mesh, fid, v0)),
                                mesh.getPolygonUVid(fid, _local_index(mesh, fid, v1))))
                except (RuntimeError, ValueError):
                    uvs = []
                    break
            if len(uvs) == 2 and set(uvs[0]) != set(uvs[1]):
                seam.append(eid)
        it.next()
    return hard, seam


def _local_index(mesh, face_id: int, vertex_id: int) -> int:
    verts = mesh.getPolygonVertices(face_id)
    return list(verts).index(vertex_id)


def _geometry(dag) -> dict:
    """Đỉnh + mặt của mesh, để đưa qua meshcheck."""
    mesh = om.MFnMesh(dag)
    pts = mesh.getPoints(om.MSpace.kObject)
    verts = [(p.x, p.y, p.z) for p in pts]
    polys = [list(mesh.getPolygonVertices(i)) for i in range(mesh.numPolygons)]
    return {"vertices": verts, "polygons": polys}


def _texture_size_for(transform: str) -> int | None:
    """Kích thước texture của material đầu tiên gắn vào mesh (dùng để tính texel density)."""
    shapes = cmds.listRelatives(transform, shapes=True, fullPath=True) or []
    if not shapes:
        return None
    sgs = cmds.listConnections(shapes[0], type="shadingEngine") or []
    for sg in sgs:
        for f in cmds.ls(cmds.listHistory(sg), type="file") or []:
            path = cmds.getAttr(f + ".fileTextureName")
            if not path:
                continue
            try:
                w = cmds.getAttr(f + ".outSizeX")
                if w:
                    return int(w)
            except Exception:  # noqa: BLE001
                continue
    return None


def _texel_density(dag, tex_size: int | None) -> float | None:
    """px/cm ≈ tex_size × sqrt(diện tích UV / diện tích thật)."""
    if not tex_size:
        return None
    it = om.MItMeshPolygon(dag)
    world_area = uv_area = 0.0
    while not it.isDone():
        world_area += it.getArea(om.MSpace.kWorld)
        try:
            uv_area += it.getUVArea()
        except RuntimeError:
            pass
        it.next()
    if world_area <= 0 or uv_area <= 0:
        return None
    return round(tex_size * math.sqrt(uv_area / world_area), 3)


def collect(asset: str | None = None, asset_class: str = "",
            platform: str = "pc") -> dict:
    if cmds is None:
        raise RuntimeError("Phải chạy trong Maya hoặc mayapy.")
    scene = cmds.file(q=True, sn=True) or ""
    meshes = []
    for shape in cmds.ls(type="mesh", noIntermediate=True, long=True):
        transform = cmds.listRelatives(shape, parent=True, fullPath=True)[0]
        short = transform.split("|")[-1]
        dag = _dag(shape)
        tri = cmds.polyEvaluate(transform, triangle=True)
        hard, seam = _edges(dag)
        tex_size = _texture_size_for(transform)
        sgs = cmds.listConnections(shape, type="shadingEngine") or []
        health = {}
        if meshcheck is not None:
            g = _geometry(dag)
            health = meshcheck.analyze(g["vertices"], g["polygons"])
        meshes.append({
            **health,
            "name": short,
            "lod": _lod_of(short),
            "triangle_count": int(tri) if isinstance(tri, int) else 0,
            "scale": [round(v, 6) for v in cmds.getAttr(transform + ".scale")[0]],
            "rotation": [round(v, 6) for v in cmds.getAttr(transform + ".rotate")[0]],
            "uv_sets": cmds.polyUVSet(transform, q=True, allUVSets=True) or [],
            "material_slots": len(set(sgs)),
            "texel_density_px_cm": _texel_density(dag, tex_size),
            "hard_edges": hard,
            "uv_seam_edges": seam,
        })

    textures = []
    for f in cmds.ls(type="file"):
        try:
            w = int(cmds.getAttr(f + ".outSizeX"))
            h = int(cmds.getAttr(f + ".outSizeY"))
        except Exception:  # noqa: BLE001
            continue
        path = cmds.getAttr(f + ".fileTextureName") or f
        name = path.replace("\\", "/").split("/")[-1].rsplit(".", 1)[0]
        cs = cmds.getAttr(f + ".colorSpace") if cmds.attributeQuery(
            "colorSpace", node=f, exists=True) else None
        textures.append({"name": name, "width": w, "height": h,
                         "color_space": _normalize_cs(cs)})

    joints = cmds.ls(type="joint", long=True)
    skeleton = {
        "bones": [{"name": j.split("|")[-1],
                   "world_position": [round(v, 4) for v in
                                      cmds.xform(j, q=True, ws=True, t=True)]}
                  for j in joints],
    }
    return {
        "asset": asset or (scene.replace("\\", "/").split("/")[-1].rsplit(".", 1)[0]
                           if scene else "<chua-luu>"),
        "asset_class": asset_class,
        "source_file": scene,
        "dcc": "maya-" + cmds.about(version=True),
        "unit": cmds.currentUnit(q=True, linear=True),
        "platform": platform,
        "meshes": meshes,
        "textures": textures,
        "skeleton": skeleton,
    }


def _normalize_cs(cs: str | None) -> str | None:
    """Gom các tên color space của Maya/OCIO về hai giá trị luật dùng."""
    if not cs:
        return None
    low = cs.lower()
    if "srgb" in low:
        return "sRGB"
    if "raw" in low or "linear" in low or "non-color" in low:
        return "Linear"
    return cs


def write(out_path: str, **kw) -> str:
    data = collect(**kw)
    with open(out_path, "w", encoding="utf-8") as fh:
        json.dump(data, fh, ensure_ascii=False, indent=2)
    return out_path


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--scene", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--asset-class", default="")
    ap.add_argument("--platform", default="pc")
    a = ap.parse_args()

    import maya.standalone
    maya.standalone.initialize(name="python")
    from maya import cmds as _c  # noqa: F811
    _c.file(a.scene, open=True, force=True)
    print(write(a.out, asset_class=a.asset_class, platform=a.platform))
    maya.standalone.uninitialize()
