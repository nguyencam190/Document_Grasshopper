"""Check dựng sẵn cho Tier A — khai báo bằng YAML, không cần viết code."""
from __future__ import annotations

import re
from typing import Any

from ..model import CheckOutcome, Location, Rule
from . import builtin_check

_OPS = {
    "<=": lambda a, b: a <= b,
    "<": lambda a, b: a < b,
    ">=": lambda a, b: a >= b,
    ">": lambda a, b: a > b,
    "==": lambda a, b: a == b,
    "!=": lambda a, b: a != b,
}


class CheckError(Exception):
    """Luật viết sai hoặc metrics thiếu field — lỗi của hệ thống, không phải của hoạ sĩ.

    `metric` cho engine biết chỉ số nào đang thiếu, để phân biệt "reader không lấy
    được chỉ số này" (→ SKIP, bình thường) với "luật viết sai" (→ ERROR, phải sửa).
    """

    def __init__(self, message: str, metric: str | None = None):
        super().__init__(message)
        self.metric = metric


def root_scalars(metrics: dict[str, Any]) -> dict[str, Any]:
    return {k: v for k, v in metrics.items() if not isinstance(v, (list, dict))}


def context_of(metrics: dict[str, Any], item: dict[str, Any]) -> dict[str, Any]:
    """Ngữ cảnh khớp `where`: field của item + các field vô hướng ở gốc (platform, unit...)."""
    return {**root_scalars(metrics), **item}


def matches(where: dict[str, Any], ctx: dict[str, Any]) -> bool:
    return all(ctx.get(k) == v for k, v in where.items())


def items_for(rule: Rule, metrics: dict[str, Any]) -> list[dict[str, Any]]:
    applies = rule.check.get("applies_to") or {}
    coll = applies.get("collection")
    if not coll:
        raise CheckError(f"{rule.id}: check thiếu applies_to.collection")
    raw = metrics.get(coll)
    if raw is None:
        raise CheckError(f"{rule.id}: metrics không có collection '{coll}'")
    where = applies.get("where") or {}
    return [it for it in raw if matches(where, context_of(metrics, it))]


def _label(item: dict[str, Any]) -> str:
    return str(item.get("name") or item.get("id") or "<không tên>")


def _need(rule: Rule, item: dict[str, Any], metric: str) -> Any:
    if metric not in item:
        raise CheckError(
            f"{rule.id}: '{_label(item)}' thiếu metric '{metric}'. "
            f"Collector chưa xuất field này — xem collectors/README.md", metric=metric)
    return item[metric]


@builtin_check("threshold")
def threshold(rule: Rule, metrics: dict[str, Any]) -> CheckOutcome:
    c = rule.check
    metric, op, limit = c["metric"], c.get("op", "<="), c["value"]
    fn = _OPS.get(op)
    if fn is None:
        raise CheckError(f"{rule.id}: op '{op}' không hỗ trợ")
    bad: list[Location] = []
    for it in items_for(rule, metrics):
        val = _need(rule, it, metric)
        if not fn(val, limit):
            bad.append(Location(_label(it), f"{metric} = {val:,} (cho phép {op} {limit:,})"
                                if isinstance(val, (int, float)) else f"{metric} = {val}"))
    return CheckOutcome(ok=not bad, locations=bad,
                        expected=f"{metric} {op} {limit}",
                        actual=f"{len(bad)} đối tượng vi phạm" if bad else "đạt")


@builtin_check("threshold_table")
def threshold_table(rule: Rule, metrics: dict[str, Any]) -> CheckOutcome:
    """Ngưỡng đổi theo LOD / platform. Hàng nào không khớp ngữ cảnh thì bỏ qua."""
    c = rule.check
    metric, op = c["metric"], c.get("op", "<=")
    table = c["table"]
    bad: list[Location] = []
    skipped: list[str] = []
    for it in items_for(rule, metrics):
        ctx = context_of(metrics, it)
        row = next((r for r in table
                    if matches({k: v for k, v in r.items()
                                if k not in ("value", "tolerance")}, ctx)), None)
        if row is None:
            skipped.append(_label(it))
            continue
        val = _need(rule, it, metric)
        limit = row["value"]
        if op == "within":
            tol = row.get("tolerance", 0)
            if abs(val - limit) > tol:
                bad.append(Location(_label(it),
                                    f"{metric} = {val} (chuẩn {limit} ±{tol}, lệch {val - limit:+.2f})"))
        else:
            fn = _OPS.get(op)
            if fn is None:
                raise CheckError(f"{rule.id}: op '{op}' không hỗ trợ")
            if not fn(val, limit):
                over = val - limit
                bad.append(Location(_label(it),
                                    f"{metric} = {val:,} (cho phép {op} {limit:,}, vượt {over:+,})"))
    note = ""
    if skipped:
        note = ("Không có hàng ngưỡng khớp cho: " + ", ".join(skipped[:5]) +
                " — kiểm tra lại bảng `table` của luật hoặc field lod/platform trong metrics.")
    return CheckOutcome(ok=not bad, locations=bad, note=note,
                        expected=f"{metric} {op} theo bảng ngưỡng",
                        actual=f"{len(bad)} đối tượng vi phạm" if bad else "đạt")


@builtin_check("regex")
def regex(rule: Rule, metrics: dict[str, Any]) -> CheckOutcome:
    c = rule.check
    metric, pattern = c.get("metric", "name"), c["pattern"]
    rx = re.compile(pattern)
    bad = [Location(_label(it), f"{metric} = '{_need(rule, it, metric)}' không khớp mẫu")
           for it in items_for(rule, metrics)
           if not rx.fullmatch(str(_need(rule, it, metric)))]
    ok_ex = ", ".join(c.get("example_ok", [])) or pattern
    return CheckOutcome(ok=not bad, locations=bad,
                        expected=f"khớp mẫu {pattern}   (đúng: {ok_ex})",
                        actual=f"{len(bad)} đối tượng sai tên" if bad else "đạt")


@builtin_check("enum")
def enum(rule: Rule, metrics: dict[str, Any]) -> CheckOutcome:
    c = rule.check
    metric, allowed = c["metric"], list(c["allowed"])
    bad = [Location(_label(it), f"{metric} = '{_need(rule, it, metric)}'")
           for it in items_for(rule, metrics)
           if _need(rule, it, metric) not in allowed]
    return CheckOutcome(ok=not bad, locations=bad,
                        expected=f"{metric} thuộc {allowed}",
                        actual=f"{len(bad)} đối tượng sai giá trị" if bad else "đạt")


@builtin_check("manual")
def manual(rule: Rule, metrics: dict[str, Any]) -> CheckOutcome:
    """Tier C — máy không kết luận, chỉ đặt câu hỏi cho người."""
    return CheckOutcome(ok=False, status_override="MANUAL",
                        note=str(rule.check.get("ask", "")).strip(),
                        expected="cần người xác nhận", actual="chưa xác nhận")
