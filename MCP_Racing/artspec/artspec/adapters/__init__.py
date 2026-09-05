"""Nối NHIỀU tool validate sẵn có của studio vào một báo cáo duy nhất.

Vấn đề: studio thường đã có 5–10 tool kiểm khác nhau, mỗi cái một cách gọi và
một kiểu output. Nối từng cái vào từng chỗ sẽ không bảo trì nổi.

Cách làm: MỘT hợp đồng chung. Mỗi tool có một adapter nhỏ dịch output của nó về
cùng một dạng `ExternalFinding`. Engine gộp tất cả lại, ánh xạ sang luật trong
`rules/` để lấy `why` / `how_to_fix`, rồi in ra một báo cáo thống nhất.

    tool A ──adapter──┐
    tool B ──adapter──┼──> ExternalFinding ──> ánh xạ rule_id ──> báo cáo
    tool C ──adapter──┘                          (why, how_to_fix,
                                                  golden asset...)

Thêm một tool mới = thêm một mục trong `adapters.yaml`. Hai kiểu tool phổ biến
nhất (in JSON, in text) đã có adapter sẵn — **không phải viết Python**.
"""
from __future__ import annotations

import concurrent.futures as _cf
from collections.abc import Callable
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml


@dataclass
class ExternalFinding:
    """Một lỗi do tool ngoài báo, đã chuẩn hoá."""
    source: str                      # tên tool đã báo
    code: str                        # mã lỗi của tool đó
    object: str = ""                 # đối tượng vi phạm
    detail: str = ""                 # mô tả
    severity_hint: str | None = None # tool tự đề xuất mức (fail/warn), có thể bỏ qua


@dataclass
class AdapterResult:
    findings: list[ExternalFinding] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)   # tool nào chạy hỏng


AdapterFn = Callable[[dict[str, Any], Path], list[ExternalFinding]]
_ADAPTERS: dict[str, AdapterFn] = {}


def adapter(name: str) -> Callable[[AdapterFn], AdapterFn]:
    """Đăng ký một kiểu adapter. Dùng khi hai kiểu dựng sẵn không đủ."""
    def deco(fn: AdapterFn) -> AdapterFn:
        _ADAPTERS[name] = fn
        return fn
    return deco


def known() -> list[str]:
    return sorted(_ADAPTERS)


def load_config(path: str | Path) -> list[dict[str, Any]]:
    data = yaml.safe_load(Path(path).read_text(encoding="utf-8")) or []
    if not isinstance(data, list):
        raise ValueError(f"{path}: file adapter phải là một danh sách")
    for i, spec in enumerate(data, 1):
        for key in ("name", "type", "command"):
            if key not in spec:
                raise ValueError(f"{path}: mục {i} thiếu '{key}'")
        if spec["type"] not in _ADAPTERS:
            raise ValueError(f"{path}: '{spec['name']}' dùng type '{spec['type']}' "
                             f"chưa có. Đang có: {known()}")
    return data


def _applies(spec: dict[str, Any], path: Path) -> bool:
    exts = spec.get("applies_to_ext")
    return not exts or path.suffix.lower() in [e.lower() for e in exts]


def run_all(config: list[dict[str, Any]], path: str | Path,
            max_workers: int = 4) -> AdapterResult:
    """Chạy mọi tool phù hợp với file này, SONG SONG.

    Một tool hỏng hoặc treo không được làm sập cả lượt kiểm — nó thành một dòng
    trong `errors`, các tool còn lại vẫn chạy.
    """
    p = Path(path)
    todo = [s for s in config if s.get("enabled", True) and _applies(s, p)]
    res = AdapterResult()
    if not todo:
        return res

    def one(spec: dict[str, Any]) -> tuple[str, list[ExternalFinding] | str]:
        try:
            return spec["name"], _ADAPTERS[spec["type"]](spec, p)
        except Exception as e:  # noqa: BLE001
            return spec["name"], f"{type(e).__name__}: {e}"

    with _cf.ThreadPoolExecutor(max_workers=max_workers) as pool:
        for name, out in pool.map(one, todo):
            if isinstance(out, str):
                res.errors.append(f"tool '{name}' chạy hỏng — {out}")
            else:
                res.findings.extend(out)
    return res


from . import builtin as _b  # noqa: E402,F401  (import để chạy decorator)
