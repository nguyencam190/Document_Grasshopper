"""Định dạng thông điệp lỗi.

Một báo lỗi dùng được phải có đủ 5 phần: CÁI GÌ SAI · Ở ĐÂU · LUẬT NÀO ·
VÌ SAO · SỬA THẾ NÀO. Thiếu phần nào thì hoạ sĩ phải đi hỏi người khác, và
cả hệ thống mất tác dụng.
"""
from __future__ import annotations

from .model import Finding, Report

_ICON = {"FAIL": "❌", "ERROR": "🛠", "WARN": "⚠️", "MANUAL": "❓",
         "INFO": "ℹ️", "PASS": "✅", "SKIP": "⊘"}


def finding_text(f: Finding) -> str:
    r = f.rule
    out: list[str] = [f"{_ICON.get(f.status, '•')} {f.status} · {r.ref} — {r.title}"]

    if f.status == "ERROR":
        out += ["", "  LỖI CỦA VALIDATOR, KHÔNG PHẢI LỖI CỦA BẠN",
                f"  {f.note}", "", "  Báo Art Lead / TA — đừng sửa asset theo báo cáo này."]
        return "\n".join(out)

    if f.status == "MANUAL":
        out += ["", "  CẦN BẠN TỰ KIỂM", f"  {f.note}"]
        if r.how_to_fix:
            out += ["", "  NẾU KHÔNG ĐẠT"] + [f"    {i}. {s}" for i, s in enumerate(r.how_to_fix, 1)]
        return "\n".join(out)

    if f.status == "SKIP":
        return (f"{_ICON['SKIP']} SKIP · {r.id} — {r.title}\n"
                f"    KHÔNG KIỂM ĐƯỢC TỪ NGUỒN NÀY: {f.actual}\n"
                f"    {f.note}")

    if f.status == "PASS":
        return f"{_ICON['PASS']} PASS · {r.id} — {r.title}"

    if f.locations:
        out += ["", "  Ở ĐÂU"]
        out += [f"    • {l.object:<28} {l.detail}".rstrip() for l in f.locations]
    if f.expected:
        out += ["", f"  YÊU CẦU   {f.expected}"]
    if f.note:
        out += [f"  GHI CHÚ   {f.note}"]
    if f.waiver:
        out += ["", "  ⚖️ CÓ WAIVER ĐÃ DUYỆT — hạ từ FAIL xuống WARN",
                f"    lý do   : {f.waiver.get('reason', '')}",
                f"    duyệt   : {f.waiver.get('approved_by', '')}",
                f"    hết hạn : {f.waiver.get('expires', '')}"]
    if r.why:
        out += ["", "  VÌ SAO CÓ LUẬT NÀY", f"    {r.why.strip()}"]
    if r.how_to_fix:
        out += ["", "  SỬA THẾ NÀO"] + [f"    {i}. {s}" for i, s in enumerate(r.how_to_fix, 1)]
    if r.common_mistakes:
        out += ["", "  LỖI NÀY HAY GẶP VÌ"] + [f"    – {m}" for m in r.common_mistakes]
    if r.reference and r.reference.get("golden_asset"):
        note = r.reference.get("note", "")
        out += ["", f"  XEM MẪU ĐÚNG   golden asset {r.reference['golden_asset']}"
                    + (f" — {note}" if note else "")]
    if r.source and r.source.get("url"):
        out += [f"  CHI TIẾT LUẬT  {r.source['url']}"
                + (f"  ({r.source.get('section')})" if r.source.get("section") else "")]
    return "\n".join(out)


def report_text(report: Report, show_pass: bool = False) -> str:
    c = report.counts
    head = (f"ASSET  {report.asset}   ({report.asset_class}"
            + (f", gate {report.stage}" if report.stage else "") + ")")
    if report.source_file:
        head += f"\nFILE   {report.source_file}"
    summary = "  ".join(f"{_ICON.get(k, '')} {k} {v}" for k, v in
                        sorted(c.items(), key=lambda kv: kv[0]))
    verdict = ("⛔ KHÔNG QUA GATE — sửa hết FAIL rồi chạy lại"
               if report.blocked else "✅ QUA GATE")
    parts = ["═" * 72, head, "─" * 72, summary, verdict, "═" * 72, ""]

    shown = [f for f in report.findings
             if f.status not in ("PASS", "SKIP") or show_pass]
    skipped = [f for f in report.findings if f.status == "SKIP"]
    if skipped and not show_pass:
        parts += [f"⊘ {len(skipped)} luật không kiểm được từ nguồn này: "
                  + ", ".join(f.rule.id for f in skipped),
                  f"  {skipped[0].note}", ""]
    if not shown:
        parts.append("Không có vấn đề nào.")
    for f in shown:
        parts += [finding_text(f), "", "─" * 72, ""]
    return "\n".join(parts)


def rule_text(rule) -> str:
    out = [f"{rule.ref} — {rule.title}",
           f"class {rule.asset_class} · nhóm {rule.category} · tier {rule.tier} "
           f"· mức {rule.severity.upper()} · gate {rule.stage}", ""]
    if rule.why:
        out += ["VÌ SAO", f"  {rule.why.strip()}", ""]
    if rule.how_to_check:
        out += ["TỰ ĐO THẾ NÀO", f"  {rule.how_to_check}", ""]
    if rule.how_to_fix:
        out += ["SỬA THẾ NÀO"] + [f"  {i}. {s}" for i, s in enumerate(rule.how_to_fix, 1)] + [""]
    if rule.common_mistakes:
        out += ["HAY GẶP VÌ"] + [f"  – {m}" for m in rule.common_mistakes] + [""]
    if rule.reference:
        out += [f"MẪU ĐÚNG  golden asset {rule.reference.get('golden_asset', '')} "
                f"— {rule.reference.get('note', '')}".rstrip(), ""]
    if rule.source and rule.source.get("url"):
        out += [f"NGUỒN  {rule.source['url']} ({rule.source.get('section', '')})"]
    return "\n".join(out).rstrip()


def inbox_text(rows: list[dict]) -> str:
    """Bảng tóm tắt cho Art Lead — nhìn 5 giây biết file nào cần xem, file nào bỏ qua."""
    if not rows:
        return "Không có file nào đọc được trong thư mục."
    w = max(len(r["file"]) for r in rows) + 2
    head = f"{'FILE'.ljust(w)}{'KẾT QUẢ'.ljust(16)}{'FAIL':>5}{'WARN':>6}{'HỎI':>5}{'BỎ':>5}   LUẬT VI PHẠM"
    out = [head, "─" * (len(head) + 6)]
    for r in rows:
        if r["fail"] is None:
            out.append(f"{r['file'].ljust(w)}{'⛔ KHÔNG ĐỌC ĐƯỢC'.ljust(16)}"
                       f"{'':>21}   {r['detail']}")
            continue
        mark = "⛔ KHÔNG QUA" if r["verdict"] == "KHÔNG QUA" else "✅ QUA"
        out.append(f"{r['file'].ljust(w)}{mark.ljust(16)}{r['fail']:>5}{r.get('warn', 0):>6}"
                   f"{r.get('manual', 0):>5}{r.get('skip', 0):>5}   {r['detail']}")
    bad = sum(1 for r in rows if r["verdict"] != "QUA")
    out += ["─" * (len(head) + 6),
            f"{len(rows)} file · {bad} cần xử lý · {len(rows) - bad} qua gate"]
    return "\n".join(out)
