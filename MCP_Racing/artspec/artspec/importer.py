"""Chuyển bảng CSV (Art Lead điền trong Excel) thành các file luật YAML.

Mục đích: Art Lead không phải sửa YAML. Điền bảng theo mẫu, chạy một lệnh, ra
đủ file luật. Cột `check` dùng một cú pháp rút gọn học trong 2 phút:

    triangle_count <= 96000 where lod=0, platform=pc
    triangle_count within 10.24 +- 0.5 where lod=0
    name matches ^SM_[A-Z]\\w+_LOD[0-3]$
    color_space in sRGB | Linear
    ngons <= 0 ids ngon_faces
    inverted_normals is false
    manual: Decal tài trợ có bị chi tiết nào che không?
    custom: vehicle.wheel_bone_layout

Dòng nào không hiểu được thì BÁO LỖI và bỏ qua dòng đó — không đoán, vì một
luật sai âm thầm còn nguy hiểm hơn một luật thiếu.
"""
from __future__ import annotations

import csv
import re
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path
from typing import Any

COLLECTION_OF = {
    "textures": {"color_space", "width", "height", "resolution"},
    "bones": set(),
}
_DEFAULT_COLLECTION = "meshes"

_NUM = re.compile(r"^-?\d+(\.\d+)?$")


class ImportError_(Exception):
    pass


@dataclass
class Result:
    rules: list[dict[str, Any]] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)
    needs_code: list[str] = field(default_factory=list)


def _num(tok: str) -> int | float:
    return int(tok) if re.fullmatch(r"-?\d+", tok) else float(tok)


def _collection_for(metric: str) -> str:
    for coll, metrics in COLLECTION_OF.items():
        if metric in metrics:
            return coll
    return _DEFAULT_COLLECTION


def _parse_where(text: str) -> dict[str, Any]:
    out: dict[str, Any] = {}
    for part in text.split(","):
        part = part.strip()
        if not part:
            continue
        if "=" not in part:
            raise ImportError_(f"điều kiện 'where' phải dạng key=value, gặp: '{part}'")
        k, v = (x.strip() for x in part.split("=", 1))
        out[k] = _num(v) if _NUM.fullmatch(v) else v
    return out


def parse_check(expr: str) -> dict[str, Any]:
    """Dịch cú pháp rút gọn ở cột `check` thành khối YAML."""
    expr = expr.strip()
    if not expr:
        raise ImportError_("cột 'check' để trống")

    if expr.lower().startswith("manual:"):
        return {"type": "manual", "ask": expr.split(":", 1)[1].strip()}

    if expr.lower().startswith("custom:"):
        return {"type": "custom", "function": expr.split(":", 1)[1].strip(), "params": {}}

    where: dict[str, Any] = {}
    m = re.search(r"\bwhere\b(.+)$", expr, re.IGNORECASE)
    if m:
        where = _parse_where(m.group(1))
        expr = expr[:m.start()].strip()

    ids_field = None
    m = re.search(r"\bids\s+(\w+)$", expr, re.IGNORECASE)
    if m:
        ids_field = m.group(1)
        expr = expr[:m.start()].strip()

    tok = expr.split(None, 1)
    if len(tok) < 2:
        raise ImportError_(f"không hiểu biểu thức: '{expr}'")
    metric, rest = tok[0], tok[1].strip()
    applies = {"collection": _collection_for(metric)}
    if where:
        applies["where"] = where

    # inverted_normals is false
    m = re.fullmatch(r"is\s+(true|false)", rest, re.IGNORECASE)
    if m:
        return {"type": "flag", "applies_to": applies, "metric": metric,
                "equals": m.group(1).lower() == "true"}

    # name matches ^...$
    m = re.fullmatch(r"matches\s+(.+)", rest, re.IGNORECASE)
    if m:
        return {"type": "regex", "applies_to": applies, "metric": metric,
                "pattern": m.group(1).strip()}

    # color_space in sRGB | Linear
    m = re.fullmatch(r"in\s+(.+)", rest, re.IGNORECASE)
    if m:
        return {"type": "enum", "applies_to": applies, "metric": metric,
                "allowed": [x.strip() for x in m.group(1).split("|")]}

    # texel_density within 10.24 +- 0.5
    m = re.fullmatch(r"within\s+(\S+)\s*\+-\s*(\S+)", rest, re.IGNORECASE)
    if m:
        return {"type": "threshold_table", "applies_to": applies, "metric": metric,
                "op": "within",
                "table": [{**where, "value": _num(m.group(1)),
                           "tolerance": _num(m.group(2))}]}

    # ngons <= 0 ids ngon_faces  /  triangle_count <= 96000
    m = re.fullmatch(r"(<=|<|>=|>|==|!=)\s*(\S+)", rest)
    if m:
        op, raw = m.group(1), m.group(2)
        if not _NUM.fullmatch(raw):
            raise ImportError_(f"'{raw}' không phải số")
        if ids_field or metric in _MESH_DEFECT_METRICS:
            out = {"type": "mesh_defect", "applies_to": applies,
                   "count_metric": metric, "max": _num(raw)}
            if ids_field:
                out["id_metric"] = ids_field
                out["id_label"] = _label_for(ids_field)
            return out
        return {"type": "threshold", "applies_to": applies, "metric": metric,
                "op": op, "value": _num(raw)}

    raise ImportError_(f"không hiểu biểu thức: '{metric} {rest}'")


_MESH_DEFECT_METRICS = {
    "ngons", "non_manifold_edges", "flipped_faces", "duplicate_vertices",
    "zero_area_faces", "duplicate_faces", "isolated_vertices", "boundary_edges",
    "invalid_index_faces",
}


def _label_for(ids_field: str) -> str:
    if "edge" in ids_field:
        return "e"
    if "vert" in ids_field:
        return "v"
    return "f"


def _split_list(text: str) -> list[str]:
    """Nhiều bước / nhiều ý ngăn bằng xuống dòng hoặc dấu ' | '."""
    if not text:
        return []
    parts = re.split(r"\n|\s\|\s", text)
    return [p.strip(" -•\t") for p in parts if p.strip(" -•\t")]


REQUIRED_COLS = ("id", "title", "asset_class", "tier", "severity", "stage",
                 "check", "why", "how_to_fix")


def from_csv(path: str | Path, *, default_effective: str | None = None) -> Result:
    res = Result()
    p = Path(path)
    with open(p, encoding="utf-8-sig", newline="") as fh:
        reader = csv.DictReader(fh)
        missing = [c for c in REQUIRED_COLS if c not in (reader.fieldnames or [])]
        if missing:
            raise ImportError_(f"Bảng thiếu cột bắt buộc: {missing}")
        for n, row in enumerate(reader, start=2):
            row = {k: (v or "").strip() for k, v in row.items() if k}
            if not row.get("id") or row["id"].startswith("#"):
                continue                      # dòng trống hoặc dòng ghi chú
            try:
                res.rules.append(_row_to_rule(row, default_effective))
            except ImportError_ as e:
                res.errors.append(f"dòng {n} ({row.get('id', '?')}): {e}")
            if row.get("tier", "").upper() == "B" and not row["check"].lower().startswith("custom:"):
                res.needs_code.append(row["id"])
    return res


def _row_to_rule(row: dict[str, str], default_effective: str | None) -> dict[str, Any]:
    tier = row["tier"].strip().upper()
    if tier not in ("A", "B", "C"):
        raise ImportError_(f"tier phải là A/B/C, gặp '{row['tier']}'")
    sev = row["severity"].strip().lower()
    if sev not in ("fail", "warn", "info"):
        raise ImportError_(f"severity phải là fail/warn/info, gặp '{row['severity']}'")
    if not row.get("why"):
        raise ImportError_("thiếu cột 'why' — hoạ sĩ không hiểu lý do thì sẽ phá luật")
    if not row.get("how_to_fix"):
        raise ImportError_("thiếu cột 'how_to_fix' — báo lỗi mà không nói cách sửa là vô dụng")

    rule: dict[str, Any] = {
        "id": row["id"].strip().upper(),
        "title": row["title"],
        "asset_class": row["asset_class"],
        "category": row.get("category") or "geometry",
        "tier": tier,
        "severity": sev,
        "stage": row["stage"].strip().upper(),
        "check": parse_check(row["check"]),
        "why": row["why"],
        "how_to_fix": _split_list(row["how_to_fix"]),
        "version": int(row.get("version") or 1),
        "effective_from": row.get("effective_from") or default_effective or str(date.today()),
        "status": row.get("status") or "active",
    }
    if row.get("how_to_check"):
        rule["how_to_check"] = row["how_to_check"]
    if row.get("common_mistakes"):
        rule["common_mistakes"] = _split_list(row["common_mistakes"])
    if row.get("golden_asset"):
        rule["reference"] = {"golden_asset": row["golden_asset"],
                             "note": row.get("golden_note", "")}
    if row.get("source_url") or row.get("source_section"):
        rule["source"] = {"system": row.get("source_system") or "confluence",
                          "url": row.get("source_url", ""),
                          "section": row.get("source_section", "")}
    if row.get("requires"):
        rule["check"]["requires"] = [x.strip() for x in row["requires"].split(",") if x.strip()]
    return rule


def write_rules(rules: list[dict[str, Any]], out_dir: str | Path,
                overwrite: bool = False) -> list[Path]:
    import yaml
    d = Path(out_dir)
    d.mkdir(parents=True, exist_ok=True)
    written: list[Path] = []
    for r in rules:
        f = d / f"{r['id']}.yaml"
        if f.exists() and not overwrite:
            raise ImportError_(f"{f} đã tồn tại — dùng --overwrite nếu muốn ghi đè")
        f.write_text(yaml.dump(r, allow_unicode=True, sort_keys=False, width=88),
                     encoding="utf-8")
        written.append(f)
    return written
