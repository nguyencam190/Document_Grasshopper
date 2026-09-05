"""Chạy luật trên metrics và sinh Report.

Hai nguyên tắc:
1. Lỗi của validator (luật viết sai, metrics thiếu field) hiện ra là ERROR và ghi
   rõ đó là lỗi hệ thống — không bao giờ đổ cho hoạ sĩ.
2. Waiver đã duyệt hạ FAIL xuống WARN, không xoá khỏi báo cáo — Lead vẫn nhìn thấy.
"""
from __future__ import annotations

from datetime import date
from typing import Any

from .checks import get_builtin, get_custom
from .checks.builtin import CheckError
from .model import Finding, Location, Report, Rule, STATUS_ORDER
from .registry import Registry

_SEVERITY_TO_STATUS = {"fail": "FAIL", "warn": "WARN", "info": "INFO"}


def _resolve(rule: Rule):
    ctype = rule.check.get("type")
    if not ctype:
        raise CheckError(f"{rule.id}: check thiếu 'type'")
    if ctype == "custom":
        fname = rule.check.get("function")
        if not fname:
            raise CheckError(f"{rule.id}: check.type=custom nhưng thiếu 'function'")
        fn = get_custom(fname)
        if fn is None:
            raise CheckError(f"{rule.id}: chưa đăng ký custom check '{fname}'. "
                             f"Thêm @custom_check(\"{fname}\") trong artspec/checks/")
        return fn
    fn = get_builtin(ctype)
    if fn is None:
        raise CheckError(f"{rule.id}: check.type '{ctype}' không tồn tại (xem rules/_SCHEMA.md)")
    return fn


def _is_unavailable(metric: str | None, metrics: dict[str, Any]) -> bool:
    """Reader đã khai trước là không lấy được chỉ số này?"""
    if not metric:
        return False
    declared = metrics.get("_unavailable") or []
    return any(metric == d or metric in d or d in metric for d in declared)


def _resolve_path(metrics: dict[str, Any], dotted: str) -> Any:
    cur: Any = metrics
    for part in dotted.split("."):
        if not isinstance(cur, dict) or part not in cur:
            return None
        cur = cur[part]
    return cur


def _missing_requirement(rule: Rule, metrics: dict[str, Any]) -> str | None:
    """`check.requires` liệt kê dữ liệu mà luật cần mới có nghĩa.

    Vd luật về bone bánh xe chỉ áp dụng cho file CÓ skeleton — một file body mesh
    không rig thì luật đó không liên quan, phải SKIP chứ không phải FAIL.
    """
    for dotted in rule.check.get("requires", []):
        val = _resolve_path(metrics, dotted)
        if val is None or (isinstance(val, (list, dict, str)) and len(val) == 0):
            return dotted
    return None


def run_rule(rule: Rule, metrics: dict[str, Any]) -> Finding:
    missing = _missing_requirement(rule, metrics)
    if missing:
        return Finding(rule=rule, status="SKIP",
                       note=f"Asset này không có '{missing}' nên luật không áp dụng.",
                       expected=f"chỉ áp dụng khi có '{missing}'",
                       actual="không áp dụng cho asset này")
    try:
        outcome = _resolve(rule)(rule, metrics)
    except CheckError as e:
        if _is_unavailable(getattr(e, "metric", None), metrics):
            # Không phải lỗi luật, cũng không phải lỗi hoạ sĩ: nguồn dữ liệu này
            # đơn giản là không có chỉ số đó. Nói rõ cần gì để kiểm được.
            return Finding(rule=rule, status="SKIP",
                           note=(metrics.get("_unavailable_reason")
                                 or f"Nguồn dữ liệu không có '{e.metric}'."),
                           expected=f"cần chỉ số '{e.metric}'",
                           actual=f"nguồn '{metrics.get('reader', 'metrics')}' không cung cấp")
        return Finding(rule=rule, status="ERROR", note=str(e),
                       expected="luật chạy được", actual="luật không chạy được")
    except Exception as e:  # noqa: BLE001 — một luật hỏng không được làm sập cả lượt kiểm
        return Finding(rule=rule, status="ERROR",
                       note=f"Lỗi không lường trước trong check: {type(e).__name__}: {e}",
                       expected="luật chạy được", actual="luật không chạy được")

    if outcome.status_override:
        status = outcome.status_override
    elif outcome.ok:
        status = "PASS"
    else:
        status = _SEVERITY_TO_STATUS.get(rule.severity, "FAIL")

    return Finding(rule=rule, status=status, locations=outcome.locations,
                   expected=outcome.expected, actual=outcome.actual, note=outcome.note)


def _unmapped_rule(code: str, source: str) -> Rule:
    """Luật giả cho mã lỗi chưa được khai báo trong rules/.

    KHÔNG bao giờ im lặng bỏ qua lỗi mà tool ngoài đã báo. Nó hiện ra dưới dạng
    WARN kèm hướng dẫn khai báo, để Lead biết mà bổ sung.
    """
    return Rule(
        id=f"EXT:{code}", title=f"Lỗi từ '{source}' chưa được khai báo",
        asset_class="*", category="external", tier="A", severity="warn",
        stage="G2", check={"type": "external"},
        why=(f"Tool '{source}' báo mã '{code}' nhưng chưa luật nào trong rules/ "
             f"nhận mã này, nên không có giải thích và cách sửa đi kèm."),
        how_to_fix=[f"Thêm `external_codes: [{code}]` vào luật tương ứng "
                    f"trong rules/, hoặc tạo luật mới cho mã này",
                    "Xem VIET_CHECKLIST.md nếu chưa rõ cách viết luật"],
        version=0, effective_from="1970-01-01")


def _from_external(registry: Registry, ext: Any) -> list[Finding]:
    """Gộp lỗi của các tool ngoài, ánh xạ sang luật để lấy why/how_to_fix."""
    if ext is None:
        return []
    out: list[Finding] = []

    for msg in getattr(ext, "errors", []):
        out.append(Finding(
            rule=_unmapped_rule("TOOL_ERROR", "adapter"), status="ERROR",
            note=msg, expected="tool ngoài chạy được",
            actual="tool ngoài không chạy được"))

    # Nhiều lỗi cùng mã thì gộp thành một mục, mỗi đối tượng là một dòng "Ở ĐÂU".
    groups: dict[tuple[str, str], list[Any]] = {}
    for f in getattr(ext, "findings", []):
        groups.setdefault((f.code.strip().upper(), f.source), []).append(f)

    for (code, source), items in groups.items():
        rule = registry.by_code(code)
        status = _SEVERITY_TO_STATUS.get(rule.severity, "FAIL") if rule else "WARN"
        out.append(Finding(
            rule=rule or _unmapped_rule(code, source), status=status,
            locations=[Location(i.object or "(không nêu)", i.detail) for i in items],
            expected=f"không có lỗi '{code}'",
            actual=f"{len(items)} lỗi do '{source}' báo",
            note=f"Nguồn: tool ngoài '{source}', mã '{code}'."))
    return out


def _merge_by_rule(findings: list[Finding]) -> list[Finding]:
    """Một luật chỉ hiện MỘT dòng trong báo cáo.

    Cùng một luật có thể vừa được kiểm nội bộ vừa được tool ngoài báo. Hiện cả
    hai (một PASS một FAIL) thì người đọc không biết tin cái nào. Gộp lại: lấy
    trạng thái XẤU HƠN, cộng dồn các chỗ vi phạm.
    """
    order = {s: i for i, s in enumerate(STATUS_ORDER)}
    merged: dict[str, Finding] = {}
    for f in findings:
        cur = merged.get(f.rule.id)
        if cur is None:
            merged[f.rule.id] = f
            continue
        keep, drop = ((f, cur) if order[f.status] < order[cur.status] else (cur, f))
        keep.locations = keep.locations + drop.locations
        notes = [n for n in (keep.note, drop.note) if n]
        keep.note = " · ".join(dict.fromkeys(notes))
        merged[f.rule.id] = keep
    return list(merged.values())


def run(registry: Registry, metrics: dict[str, Any], stage: str | None = None,
        today: date | None = None, external: Any = None) -> Report:
    asset = str(metrics.get("asset") or metrics.get("name") or "<không tên>")
    asset_class = str(metrics.get("asset_class") or "")
    if not asset_class:
        raise CheckError("metrics thiếu 'asset_class' — không biết áp bộ luật nào")

    rules = registry.rules_for(asset_class=asset_class, stage=stage)
    findings: list[Finding] = []
    for rule in rules:
        f = run_rule(rule, metrics)
        if f.status == "FAIL":
            w = registry.waiver_for(rule.id, asset, today=today)
            if w:
                f.status = "WARN"
                f.waiver = w
        findings.append(f)

    findings.extend(_from_external(registry, external))
    findings = _merge_by_rule(findings)

    findings.sort(key=lambda f: (STATUS_ORDER.index(f.status), f.rule.id))
    return Report(asset=asset, asset_class=asset_class, stage=stage,
                  findings=findings, source_file=str(metrics.get("source_file", "")))
