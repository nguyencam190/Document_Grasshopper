"""Quét bộ tool validate của studio để dựng sẵn `adapters.yaml`.

CHỈ ĐỌC MÃ NGUỒN, không chạy gì cả:
  * Không cần Maya, không cần import module của bạn
  * Không thực thi một dòng code nào — dùng `ast` để phân tích cú pháp
  * Không đọc được logic nghiệp vụ, chỉ lấy TÊN hàm, mã lỗi và dòng mô tả đầu

Vì vậy an toàn để chạy trên máy studio, và bản tóm tắt nó xuất ra chứa rất ít
thông tin — đủ để dựng cấu hình, không đủ để lộ thuật toán.

    python -m artspec.cli scan-validators D:/pipeline/scripts
"""
from __future__ import annotations

import ast
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

# Tên hàm gợi ý đây là một validator
NAME_HINTS = ("check", "validate", "verify", "audit", "inspect", "kiem", "test_")
# Mã lỗi thường viết HOA_GẠCH_DƯỚI
CODE_RE = re.compile(r"^[A-Z][A-Z0-9]*(_[A-Z0-9]+)+$")
SKIP_DIRS = {"__pycache__", ".git", ".svn", "venv", ".venv", "node_modules", "build"}


@dataclass
class FuncInfo:
    name: str
    module: str
    lineno: int
    args: list[str] = field(default_factory=list)
    doc: str = ""
    codes: list[str] = field(default_factory=list)
    returns_list: bool = False
    decorators: list[str] = field(default_factory=list)
    calls: list[str] = field(default_factory=list)
    aggregates: list[str] = field(default_factory=list)   # gọi validator nào

    @property
    def is_aggregator(self) -> bool:
        return len(self.aggregates) >= 2

    def to_dict(self) -> dict[str, Any]:
        return {"module": self.module, "function": self.name, "line": self.lineno,
                "args": self.args, "doc": self.doc, "error_codes": self.codes,
                "returns_list": self.returns_list, "decorators": self.decorators,
                "aggregates": self.aggregates, "is_aggregator": self.is_aggregator}


def _module_name(root: Path, path: Path) -> str:
    rel = path.relative_to(root).with_suffix("")
    parts = [p for p in rel.parts if p != "__init__"]
    return ".".join(parts)


def _codes_in(node: ast.AST) -> list[str]:
    """Chuỗi HOA_GẠCH_DƯỚI xuất hiện trong hàm — nhiều khả năng là mã lỗi."""
    out: list[str] = []
    for n in ast.walk(node):
        if isinstance(n, ast.Constant) and isinstance(n.value, str):
            v = n.value.strip()
            if CODE_RE.match(v) and 3 <= len(v) <= 60:
                out.append(v)
    return sorted(dict.fromkeys(out))


def _called_names(node: ast.AST) -> list[str]:
    """Tên các hàm được gọi bên trong — để nhận ra hàm tổng hợp."""
    out: list[str] = []
    for n in ast.walk(node):
        if isinstance(n, ast.Call):
            name = _deco_name(n.func)
            if name:
                out.append(name)
    return sorted(dict.fromkeys(out))


def _returns_list(node: ast.AST) -> bool:
    for n in ast.walk(node):
        if isinstance(n, ast.Return) and isinstance(n.value, (ast.List, ast.ListComp)):
            return True
    return False


def _deco_name(d: ast.AST) -> str:
    if isinstance(d, ast.Name):
        return d.id
    if isinstance(d, ast.Attribute):
        return d.attr
    if isinstance(d, ast.Call):
        return _deco_name(d.func)
    return ""


def scan(root: str | Path, include_all: bool = False) -> dict[str, Any]:
    r = Path(root).resolve()
    if not r.is_dir():
        raise NotADirectoryError(f"Không thấy thư mục: {r}")

    funcs: list[FuncInfo] = []
    all_codes: dict[str, list[str]] = {}
    unreadable: list[str] = []
    n_files = 0

    for p in sorted(r.rglob("*.py")):
        if any(part in SKIP_DIRS for part in p.parts):
            continue
        n_files += 1
        try:
            tree = ast.parse(p.read_text(encoding="utf-8", errors="replace"))
        except SyntaxError as e:
            unreadable.append(f"{p.relative_to(r)}: {e.msg} (dòng {e.lineno})")
            continue

        mod = _module_name(r, p)
        for node in tree.body:
            if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                continue
            if node.name.startswith("_"):
                continue
            # Gom HẾT hàm công khai ở vòng một, lọc ở vòng hai. Hàm tổng hợp
            # (run_all, main…) thường không có chữ check/validate trong tên và
            # cũng không trả list trực tiếp (nó `return out`), nên lọc sớm sẽ
            # bỏ sót đúng cái đáng gọi nhất.
            looks_like = any(h in node.name.lower() for h in NAME_HINTS)
            doc = (ast.get_docstring(node) or "").strip().splitlines()
            info = FuncInfo(
                name=node.name, module=mod, lineno=node.lineno,
                args=[a.arg for a in node.args.args],
                doc=doc[0][:120] if doc else "",
                codes=_codes_in(node), returns_list=_returns_list(node),
                decorators=[d for d in (_deco_name(x) for x in node.decorator_list) if d])
            info.calls = _called_names(node)
            info._looks_like = looks_like          # type: ignore[attr-defined]
            funcs.append(info)
            for code in info.codes:
                all_codes.setdefault(code, []).append(f"{mod}.{node.name}")

    # Vòng hai: hàm nào gọi >= 2 validator khác thì là hàm TỔNG HỢP.
    validator_names = {f.name for f in funcs if f.codes}
    for f in funcs:
        f.aggregates = sorted(set(f.calls) & validator_names)
    # Bỏ những hàm chỉ trả list mà không có mã lỗi cũng không tổng hợp gì
    funcs = [f for f in funcs
             if f.codes or f.is_aggregator or getattr(f, "_looks_like", False)
             or include_all]

    # Hàm tổng hợp lên đầu — gọi một cái tiện hơn gọi năm cái.
    funcs.sort(key=lambda f: (not f.is_aggregator, -len(f.codes), f.module, f.name))
    return {
        "root": str(r),
        "python_files_scanned": n_files,
        "candidates": [f.to_dict() for f in funcs],
        "error_codes": {k: v for k, v in sorted(all_codes.items())},
        "unreadable": unreadable,
    }


def suggest_adapters(result: dict[str, Any], top: int = 5) -> str:
    """Dựng sẵn khối adapters.yaml từ các hàm có nhiều mã lỗi nhất."""
    rows = [c for c in result["candidates"]
            if c["error_codes"] or c.get("is_aggregator")][:top]
    if not rows:
        return ("# Chưa đoán được hàm nào. Chạy lại với --all để xem mọi hàm,\n"
                "# hoặc chỉ tôi tên hàm chính rồi tôi viết cấu hình.\n")
    aggs = [c for c in rows if c.get("is_aggregator")]
    out = ["# Dựng sẵn từ kết quả quét — kiểm lại rồi sửa cho đúng.",
           "# Đặc biệt: 'fields' đang đoán, phải đối chiếu với thứ hàm thật sự trả về.", ""]
    if aggs:
        out += [f"# GỢI Ý: {aggs[0]['module']}.{aggs[0]['function']} là hàm TỔNG HỢP "
                f"(gọi {len(aggs[0]['aggregates'])} validator).",
                "# Khai một mình nó là đủ, không cần khai từng validator riêng.", ""]
    for c in rows:
        out += [
            f"- name: {c['module'].split('.')[-1]}_{c['function']}",
            "  type: maya_batch",
            '  mayapy: "C:/Program Files/Autodesk/Maya2026/bin/mayapy.exe"',
            f"  module: {c['module']}",
            f"  function: {c['function']}",
            "  fields: {code: code, object: object, detail: message}   # ← ĐOÁN, phải sửa",
            f'  pythonpath: ["{result["root"]}"]',
            '  applies_to_ext: [".ma", ".mb"]',
            (f"  # TỔNG HỢP — gọi: {', '.join(c['aggregates'])}"
             if c.get("is_aggregator") else
             f"  # {len(c['error_codes'])} mã lỗi: " + ", ".join(c["error_codes"][:6])
             + (" …" if len(c["error_codes"]) > 6 else "")),
            "",
        ]
    return "\n".join(out)


def suggest_rule_codes(result: dict[str, Any]) -> str:
    """Danh sách mã lỗi để dán vào `external_codes` của các luật."""
    codes = result["error_codes"]
    if not codes:
        return "# Không tìm thấy mã lỗi nào.\n"
    out = [f"# {len(codes)} mã lỗi tìm được. Gắn mỗi mã vào luật tương ứng bằng",
           "# `external_codes:` trong file luật. Mã chưa gắn sẽ hiện WARN, không mất.", ""]
    for code, where in codes.items():
        out.append(f"{code:<34} # {', '.join(sorted(set(where))[:2])}")
    return "\n".join(out)
