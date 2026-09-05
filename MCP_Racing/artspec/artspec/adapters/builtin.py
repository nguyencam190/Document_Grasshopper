"""Hai kiểu adapter phủ hầu hết tool validate ngoài đời.

Khai báo trong `adapters.yaml`, KHÔNG cần viết Python.
"""
from __future__ import annotations

import json
import re
import shlex
import subprocess
from pathlib import Path
from typing import Any

from . import ExternalFinding, adapter

DEFAULT_TIMEOUT = 300


def _run(spec: dict[str, Any], path: Path) -> str:
    """Chạy tool, trả stdout. `{file}` trong command được thay bằng đường dẫn."""
    cmd = spec["command"]
    if isinstance(cmd, str):
        cmd = shlex.split(cmd)
    cmd = [str(c).replace("{file}", str(path)) for c in cmd]
    proc = subprocess.run(cmd, capture_output=True, text=True,
                          timeout=spec.get("timeout", DEFAULT_TIMEOUT),
                          cwd=spec.get("cwd"))
    ok_codes = spec.get("ok_exit_codes", [0, 1])   # nhiều tool trả 1 khi có lỗi
    if proc.returncode not in ok_codes:
        raise RuntimeError(f"mã thoát {proc.returncode}: "
                           f"{(proc.stderr or proc.stdout).strip()[:200]}")
    return proc.stdout


def _dig(obj: Any, dotted: str | None) -> Any:
    if not dotted:
        return obj
    for part in dotted.split("."):
        if isinstance(obj, dict):
            obj = obj.get(part)
        else:
            return None
    return obj


@adapter("json_cli")
def json_cli(spec: dict[str, Any], path: Path) -> list[ExternalFinding]:
    """Tool in ra JSON. Kiểu dễ nối nhất.

        - name: maya_validator
          type: json_cli
          command: ["python", "tools/val.py", "--json", "{file}"]
          findings_path: issues          # chỗ chứa danh sách lỗi trong JSON
          fields:                        # tên field của tool -> tên chuẩn
            code: type
            object: node
            detail: message
    """
    raw = _run(spec, path).strip()
    if not raw:
        return []
    data = json.loads(raw)
    rows = _dig(data, spec.get("findings_path"))
    if rows is None:
        raise RuntimeError(f"không thấy '{spec.get('findings_path')}' trong JSON")
    if not isinstance(rows, list):
        raise RuntimeError("chỗ chứa lỗi phải là một danh sách")

    f = spec.get("fields", {})
    out: list[ExternalFinding] = []
    for r in rows:
        if not isinstance(r, dict):
            continue
        code = str(_dig(r, f.get("code", "code")) or "").strip()
        if not code:
            continue                     # không có mã thì không ánh xạ được
        out.append(ExternalFinding(
            source=spec["name"], code=code,
            object=str(_dig(r, f.get("object", "object")) or ""),
            detail=str(_dig(r, f.get("detail", "detail")) or ""),
            severity_hint=(str(_dig(r, f["severity"])).lower()
                           if f.get("severity") else None)))
    return out


@adapter("regex_text")
def regex_text(spec: dict[str, Any], path: Path) -> list[ExternalFinding]:
    """Tool chỉ in text cho người đọc. Bắt lỗi bằng regex.

        - name: uv_checker
          type: regex_text
          command: "uvcheck.exe {file}"
          pattern: '^(?P<code>[A-Z_]+)\\s+(?P<object>\\S+)\\s+(?P<detail>.*)$'

    Nhóm bắt buộc: `code`. Tuỳ chọn: `object`, `detail`, `severity`.

    Cách này DỄ VỠ khi tool đổi cách in. Nếu người viết tool thêm được tuỳ chọn
    `--json` thì luôn ưu tiên dùng `json_cli`.
    """
    pattern = spec.get("pattern")
    if not pattern:
        raise RuntimeError("thiếu 'pattern'")
    rx = re.compile(pattern, re.MULTILINE)
    out: list[ExternalFinding] = []
    for m in rx.finditer(_run(spec, path)):
        g = m.groupdict()
        code = (g.get("code") or "").strip()
        if not code:
            continue
        out.append(ExternalFinding(
            source=spec["name"], code=code,
            object=(g.get("object") or "").strip(),
            detail=(g.get("detail") or "").strip(),
            severity_hint=(g["severity"].lower() if g.get("severity") else None)))
    return out
