"""Đăng ký các hàm check.

- Tier A dùng các check dựng sẵn trong builtin.py (không cần viết code).
- Tier B viết hàm riêng, đăng ký bằng @custom_check("<module>.<tên>").
"""
from __future__ import annotations

from collections.abc import Callable
from typing import Any

from ..model import CheckOutcome, Rule

CheckFn = Callable[[Rule, dict[str, Any]], CheckOutcome]

_BUILTIN: dict[str, CheckFn] = {}
_CUSTOM: dict[str, CheckFn] = {}


def builtin_check(name: str) -> Callable[[CheckFn], CheckFn]:
    def deco(fn: CheckFn) -> CheckFn:
        _BUILTIN[name] = fn
        return fn
    return deco


def custom_check(name: str) -> Callable[[CheckFn], CheckFn]:
    """Đăng ký một check đặc thù của dự án.

    Tên đăng ký chính là giá trị `check.function` trong file YAML.
    """
    def deco(fn: CheckFn) -> CheckFn:
        _CUSTOM[name] = fn
        return fn
    return deco


def get_builtin(name: str) -> CheckFn | None:
    return _BUILTIN.get(name)


def get_custom(name: str) -> CheckFn | None:
    return _CUSTOM.get(name)


def known() -> dict[str, list[str]]:
    return {"builtin": sorted(_BUILTIN), "custom": sorted(_CUSTOM)}


from . import builtin as _b  # noqa: E402,F401  (import để chạy decorator)
from . import vehicle as _v  # noqa: E402,F401
