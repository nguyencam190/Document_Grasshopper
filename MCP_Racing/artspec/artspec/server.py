"""MCP server phục vụ bộ luật và engine kiểm.

Chạy:  ARTSPEC_ROOT=/duong/dan/artspec python -m artspec.server
Mặc định transport stdio (Claude Desktop / Claude Code). Đổi sang
streamable-http khi triển khai chung cho cả team — xem README.

Server này CỐ Ý mỏng: mọi logic nằm ở engine/registry, để validator trong Maya
và MCP dùng chung một nguồn luật. Thêm luật mới không phải sửa file này.
"""
from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

from mcp.server import MCPServer

from . import engine, inbox, registry, render
from .readers import ReaderError
from .registry import Registry, RegistryError

ROOT = Path(os.environ.get("ARTSPEC_ROOT", Path(__file__).resolve().parent.parent))

mcp = MCPServer(
    "artspec",
    title="Art Spec — techspec & kiểm asset",
    version="0.1.0",
    instructions=(
        "Phục vụ techspec 3D của dự án và kiểm asset theo techspec đó.\n"
        "QUY TẮC BẮT BUỘC khi trả lời từ server này:\n"
        "1. Luôn dẫn rule_id và version kèm mọi con số. Không bao giờ nêu số mà "
        "không có rule_id.\n"
        "2. Nếu tool trả found=false hoặc danh sách rỗng, nói thẳng là không có "
        "trong techspec. TUYỆT ĐỐI không suy ra con số từ kiến thức chung về "
        "game art — sai số spec làm hoạ sĩ phải làm lại asset.\n"
        "3. Với finding status=ERROR: đó là lỗi của validator, không phải lỗi "
        "của hoạ sĩ. Bảo họ báo Art Lead, đừng bảo họ sửa asset.\n"
        "4. Khi giải thích một FAIL, dùng đúng nội dung why/how_to_fix/"
        "common_mistakes của luật, diễn đạt lại cho dễ hiểu chứ không thêm ý mới."
    ),
)

_cache: dict[str, Any] = {"reg": None, "stamp": None}


def _stamp() -> float:
    return max((p.stat().st_mtime for p in ROOT.rglob("*.yaml")), default=0.0)


def _reg() -> Registry:
    """Nạp lại registry khi có file YAML thay đổi — sửa luật không cần restart server."""
    s = _stamp()
    if _cache["reg"] is None or _cache["stamp"] != s:
        _cache["reg"] = registry.load(ROOT)
        _cache["stamp"] = s
    return _cache["reg"]


def _err(msg: str) -> dict[str, Any]:
    return {"found": False, "error": msg}


# ─────────────────────────── TOOLS ───────────────────────────

@mcp.tool()
def check_asset(metrics_json: str, stage: str | None = None) -> str:
    """Kiểm một asset theo toàn bộ luật của class nó, trả báo cáo đọc được.

    Dùng khi hoạ sĩ dán số liệu asset vào và hỏi "asset của tôi có đạt không".
    `metrics_json` là JSON do collector sinh ra (đường dẫn file hoặc nội dung JSON).
    `stage` giới hạn theo gate: G0 / G1 / G2 / G3. Bỏ trống = kiểm tất cả.

    Báo cáo đã chứa sẵn lý do và cách sửa — hãy diễn đạt lại cho dễ hiểu,
    KHÔNG thêm lời khuyên kỹ thuật ngoài nội dung luật.
    """
    raw = metrics_json.strip()
    try:
        if raw.startswith("{"):
            metrics = json.loads(raw)
        else:
            inbox.ensure_allowed(Path(raw))
            metrics = json.loads(Path(raw).read_text(encoding="utf-8"))
    except ReaderError as e:
        return str(e)
    except (json.JSONDecodeError, OSError) as e:
        return f"Không đọc được metrics: {e}"
    try:
        report = engine.run(_reg(), metrics, stage=stage)
    except (RegistryError, Exception) as e:  # noqa: BLE001
        return f"Không chạy được kiểm tra: {type(e).__name__}: {e}"
    return render.report_text(report)


@mcp.tool()
def check_file(path: str, asset_class: str | None = None,
               stage: str | None = None, platform: str | None = None) -> str:
    """Kiểm THẲNG một file 3D hoạ sĩ nộp lên — người hỏi không cần mở file.

    Dùng khi Art Lead đưa đường dẫn tới file vừa nhận (.fbx, .glb, .gltf, .obj,
    hoặc metrics .json) và hỏi "file này có đạt checklist không".

    `asset_class` bỏ trống thì suy từ tên thư mục (vd .../vehicle_exterior/...)
    hoặc từ sidecar `<tên file>.submit.json`.
    `stage` giới hạn theo gate: G0 / G1 / G2 / G3.

    File .ma/.mb sẽ bị từ chối kèm hướng dẫn — nói lại đúng hướng dẫn đó, đừng
    tự nghĩ cách khác.

    Trong báo cáo:
      FAIL  hoạ sĩ phải sửa
      SKIP  định dạng file này không chứa chỉ số đó — KHÔNG phải lỗi của hoạ sĩ,
            đừng bảo họ sửa; nói rõ cần nộp thêm gì mới kiểm được
      ERROR lỗi của validator, báo Art Lead
    """
    out = inbox.check_file(_reg(), path, asset_class=asset_class,
                           stage=stage, platform=platform)
    if out.error:
        return f"Không kiểm được {Path(path).name}:\n{out.error}"
    return render.report_text(out.report)


@mcp.tool()
def check_inbox(folder: str, stage: str | None = None) -> str:
    """Quét cả thư mục nộp bài và trả bảng tóm tắt: file nào qua, file nào không.

    Dùng khi Art Lead hỏi "sáng nay có gì cần xem" hoặc "lô này ai làm sai".
    Sau khi đọc bảng, nếu người dùng muốn biết chi tiết một file thì gọi
    check_file cho đúng file đó.
    """
    outs = inbox.check_folder(_reg(), folder, stage=stage)
    rows = inbox.summary_rows(outs)
    return render.inbox_text(rows)


@mcp.tool()
def supported_formats() -> dict[str, Any]:
    """Định dạng file nào kiểm trực tiếp được, và chỉ số nào từng định dạng thiếu."""
    return {
        "direct": {
            ".fbx": "FBX nhị phân — định dạng chính vào UE5. Không đọc được FBX ASCII.",
            ".gltf/.glb": "glTF 2.0 — đọc đầy đủ nhất.",
            ".obj": "Chỉ tricount / tên / số material. Không có transform, bone, color space.",
            ".json": "metrics do collector sinh ra — đầy đủ nhất.",
        },
        "not_direct": {
            ".ma/.mb": "Chạy collectors/maya_collect.py trong Maya, hoặc yêu cầu "
                       "hoạ sĩ nộp kèm FBX.",
        },
        "mesh_health": {
            "all_formats": ["non_manifold_edges", "boundary_edges", "flipped_faces",
                            "inverted_normals", "zero_area_faces", "duplicate_faces",
                            "invalid_index_faces"],
            "not_from_gltf": ["ngons", "quads", "tris", "duplicate_vertices"],
            "not_from_obj": ["isolated_vertices"],
            "why": "glTF luôn tam giác hoá và tách đỉnh ở UV seam; OBJ dùng kho "
                   "đỉnh toàn cục. Các chỉ số đó ở hai định dạng này không phản "
                   "ánh topology hoạ sĩ dựng nên bị báo SKIP thay vì đoán bừa.",
        },
        "note": "Chỉ số nào định dạng không có thì luật báo SKIP, không báo FAIL. "
                "Muốn kiểm đủ mọi luật thì cần metrics từ collector Maya.",
    }


@mcp.tool()
def get_rule(rule_id: str) -> dict[str, Any]:
    """Lấy nguyên văn một quy tắc theo mã (vd VEH-TRI-001).

    Dùng khi cần trích dẫn chính xác một luật. Trả found=false nếu không có —
    khi đó nói là techspec không có luật này, đừng đoán nội dung.
    """
    r = _reg().get(rule_id)
    if not r:
        near = [x.id for x in _reg().search(rule_id)][:5]
        return _err(f"Không có luật '{rule_id}' trong techspec."
                    + (f" Gần giống: {', '.join(near)}" if near else ""))
    return {"found": True, **_rule_dict(r)}


@mcp.tool()
def search_spec(query: str, asset_class: str | None = None) -> dict[str, Any]:
    """Tìm quy tắc theo từ khoá (vd "texel density", "tricount", "đặt tên bone").

    Dùng khi hoạ sĩ hỏi bằng lời chứ không biết mã luật. Danh sách rỗng nghĩa là
    techspec không quy định điều đó — nói thẳng như vậy.
    """
    hits = _reg().search(query, asset_class)
    return {"found": bool(hits), "count": len(hits),
            "results": [{"rule_id": r.id, "title": r.title, "category": r.category,
                         "severity": r.severity, "stage": r.stage,
                         "version": r.version} for r in hits[:20]]}


@mcp.tool()
def get_budget(asset_class: str, lod: int | None = None,
               platform: str | None = None) -> dict[str, Any]:
    """Tra ngưỡng số cụ thể (tricount, texel density, số material...) của một class.

    Đây là câu hỏi hay gặp nhất: "xe hạng B LOD2 tối đa bao nhiêu tri?".
    Mọi con số trả về đều kèm rule_id — luôn dẫn kèm khi trả lời.
    """
    rows: list[dict[str, Any]] = []
    for r in _reg().rules_for(asset_class):
        c = r.check
        if c.get("type") == "threshold":
            rows.append({"rule_id": r.id, "metric": c["metric"], "op": c.get("op", "<="),
                         "value": c["value"], "where": c.get("applies_to", {}).get("where", {}),
                         "version": r.version, "effective_from": r.effective_from})
        elif c.get("type") == "threshold_table":
            for row in c["table"]:
                if lod is not None and row.get("lod") not in (None, lod):
                    continue
                if platform is not None and row.get("platform") not in (None, platform):
                    continue
                rows.append({"rule_id": r.id, "metric": c["metric"], "op": c.get("op", "<="),
                             **row, "version": r.version, "effective_from": r.effective_from})
    if not rows:
        return _err(f"Techspec không có ngưỡng số nào cho class '{asset_class}'"
                    + (f" ở LOD{lod}" if lod is not None else "") + ".")
    return {"found": True, "asset_class": asset_class, "budgets": rows}


@mcp.tool()
def get_checklist(asset_class: str, stage: str) -> dict[str, Any]:
    """Lấy checklist của một gate (G0 blockout / G1 model freeze / G2 tech check / G3 in-game QC).

    Dùng khi hoạ sĩ hỏi "trước khi submit tôi phải kiểm gì".
    """
    reg = _reg()
    cl = reg.checklists.get(asset_class, {})
    st = (cl.get("stages") or {}).get(stage)
    if not st:
        return _err(f"Không có checklist cho {asset_class}/{stage}. "
                    f"Các gate đang có: {sorted((cl.get('stages') or {}))}")
    auto = [{"rule_id": r.id, "title": r.title, "tier": r.tier,
             "checked_by": "máy" if r.tier in ("A", "B") else "người"}
            for r in reg.rules_for(asset_class, stage)]
    return {"found": True, "stage": stage, "title": st.get("title", ""),
            "manual_items": st.get("items", []) + st.get("extra_items", []),
            "rule_items": auto,
            "signature_required": bool(st.get("signature_required"))}


@mcp.tool()
def explain_term(term: str) -> dict[str, Any]:
    """Giải thích một thuật ngữ THEO CÁCH DỰ ÁN NÀY hiểu (vd "texel density", "hard edge").

    Ưu tiên định nghĩa này hơn kiến thức chung, vì dự án có thể quy ước khác.
    Trả found=false nghĩa là dự án chưa định nghĩa — nói rõ điều đó trước khi
    giải thích theo hiểu biết chung.
    """
    t = _reg().term(term)
    return {"found": True, **t} if t else _err(
        f"Dự án chưa định nghĩa thuật ngữ '{term}' trong glossary.")


@mcp.tool()
def list_rules(asset_class: str | None = None, stage: str | None = None) -> dict[str, Any]:
    """Liệt kê các luật đang có hiệu lực, lọc theo class và/hoặc gate."""
    rows = _reg().rules_for(asset_class, stage)
    return {"count": len(rows),
            "rules": [{"rule_id": r.id, "title": r.title, "asset_class": r.asset_class,
                       "category": r.category, "tier": r.tier, "severity": r.severity,
                       "stage": r.stage, "version": r.version} for r in rows]}


@mcp.tool()
def whats_changed_for(asset_class: str, since: str | None = None) -> dict[str, Any]:
    """Khách hàng đã đổi gì ảnh hưởng tới một loại asset, từ mốc thời gian nào tới nay.

    Dùng khi hoạ sĩ hỏi "tuần này có gì mới với xe không", "tôi nghỉ 2 tuần, đã bỏ
    lỡ gì", hoặc khi họ chuẩn bị bắt tay vào một asset mới và cần biết luật hiện
    hành đã đổi so với lần trước.

    `since` dạng YYYY-MM-DD. Bỏ trống = lấy toàn bộ lịch sử.

    Mỗi update kèm danh sách luật bị ảnh hưởng và VERSION HIỆN TẠI của luật đó —
    hãy nêu cả hai khi trả lời, và nhắc `action_required` vì đó là phần quyết
    định hoạ sĩ có phải sửa asset cũ hay không.

    Danh sách rỗng nghĩa là không có thay đổi nào — nói thẳng như vậy, đừng suy
    đoán từ nội dung các luật.
    """
    reg = _reg()
    ups = reg.updates_for(asset_class, since)
    if not ups:
        return {"found": False, "asset_class": asset_class, "since": since,
                "updates": [],
                "error": (f"Không có update nào của khách ảnh hưởng tới "
                          f"'{asset_class}'" + (f" từ {since}." if since else "."))}
    out = []
    for u in ups:
        rules = []
        for rid in u.get("affects_rules", []):
            r = reg.get(rid)
            rules.append({"rule_id": rid, "title": r.title if r else "(luật đã bị xoá)",
                          "current_version": r.version if r else None,
                          "severity": r.severity if r else None})
        out.append({"update_id": u["id"], "effective_from": u.get("effective_from"),
                    "date_received": u.get("date_received"),
                    "summary": u.get("summary_vi"), "source": u.get("source"),
                    "action_required": u.get("action_required"),
                    "status": u.get("status"), "affected_rules": rules})
    return {"found": True, "asset_class": asset_class, "since": since,
            "count": len(out), "updates": out}


@mcp.tool()
def get_update(update_id: str) -> dict[str, Any]:
    """Chi tiết một update của khách hàng theo mã (vd CU-2026-041), kèm trích dẫn gốc.

    Dùng khi cần đối chiếu chính xác khách đã nói gì — `raw_excerpt` là nguyên
    văn, ưu tiên nó hơn phần tóm tắt khi hai bên có vẻ khác nhau.
    """
    u = _reg().update(update_id)
    return {"found": True, **u} if u else _err(
        f"Không có update '{update_id}' trong changelog.")


@mcp.tool()
def list_waivers() -> dict[str, Any]:
    """Danh sách ngoại lệ đã duyệt (asset nào được phép vi phạm luật nào, tới khi nào)."""
    ws = _reg().waivers
    return {"count": len(ws), "waivers": ws}


# ───────────────────────── RESOURCES ─────────────────────────

@mcp.resource("spec://index")
def index() -> str:
    """Bản đồ toàn bộ techspec — đọc cái này đầu tiên để biết có những gì."""
    reg = _reg()
    out = ["# Techspec index", ""]
    for ac in reg.asset_classes():
        rules = reg.rules_for(ac)
        out.append(f"## {ac} — {len(rules)} luật")
        for r in rules:
            out.append(f"- `{r.id}` (v{r.version}, {r.severity}, gate {r.stage}) {r.title}")
        out.append("")
    out += [f"Thuật ngữ: {len(reg.glossary)} · Waiver đang mở: {len(reg.waivers)}"]
    return "\n".join(out)


@mcp.resource("spec://rules/{asset_class}")
def rules_doc(asset_class: str) -> str:
    """Toàn bộ luật của một asset class, gộp thành tài liệu đọc được."""
    rules = _reg().rules_for(asset_class)
    if not rules:
        return f"Không có luật nào cho class '{asset_class}'."
    return ("\n\n" + "─" * 60 + "\n\n").join(render.rule_text(r) for r in rules)


@mcp.resource("spec://glossary")
def glossary_doc() -> str:
    """Thuật ngữ dự án."""
    return json.dumps(_reg().glossary, ensure_ascii=False, indent=2)


# ────────────────────────── PROMPTS ──────────────────────────

@mcp.prompt()
def pre_submit_review(asset_class: str, stage: str = "G2") -> str:
    """Dẫn hoạ sĩ đi qua checklist của một gate trước khi submit."""
    return (
        f"Hãy giúp tôi kiểm asset {asset_class} trước khi submit ở gate {stage}.\n"
        f"1. Gọi get_checklist('{asset_class}', '{stage}') và đọc cho tôi từng mục.\n"
        f"2. Hỏi tôi lần lượt các mục cần người tự kiểm.\n"
        f"3. Nếu tôi có file metrics, gọi check_asset để chạy phần máy kiểm được.\n"
        f"4. Tổng hợp: còn mục nào chưa đạt, và tôi phải làm gì tiếp.\n"
        f"Luôn dẫn rule_id kèm mỗi con số. Không tự nghĩ ra ngưỡng nào."
    )


def _rule_dict(r) -> dict[str, Any]:
    return {"rule_id": r.id, "title": r.title, "asset_class": r.asset_class,
            "category": r.category, "tier": r.tier, "severity": r.severity,
            "stage": r.stage, "why": r.why, "how_to_check": r.how_to_check,
            "how_to_fix": r.how_to_fix, "common_mistakes": r.common_mistakes,
            "reference": r.reference, "source": r.source, "version": r.version,
            "effective_from": r.effective_from, "check": r.check}


def main() -> None:
    mcp.run(transport=os.environ.get("ARTSPEC_TRANSPORT", "stdio"))


if __name__ == "__main__":
    main()
