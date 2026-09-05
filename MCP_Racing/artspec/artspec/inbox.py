"""Kiểm file hoạ sĩ nộp lên — Lead không phải mở file 3D.

    from artspec import inbox
    inbox.check_file(reg, "submit/vehicle_exterior/SUV_A.fbx")
    inbox.check_folder(reg, "submit/")
"""
from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from . import adapters, engine
from .model import Report
from .readers import SUPPORTED, ReaderError, read
from .registry import Registry


def allowed_roots() -> list[Path] | None:
    """Thư mục được phép đọc, lấy từ biến môi trường ARTSPEC_FILE_ROOT.

    Không đặt = không giới hạn. Với bản chạy local (stdio) điều đó chấp nhận
    được: server chạy đúng quyền của chính người dùng, nên họ không đọc thêm
    được gì so với mở File Explorer.

    Bắt buộc đặt khi triển khai DÙNG CHUNG (Streamable HTTP) — lúc đó server
    chạy bằng một tài khoản khác và ai gọi được tool cũng đọc được file của
    tài khoản đó.
    """
    raw = os.environ.get("ARTSPEC_FILE_ROOT", "").strip()
    if not raw:
        return None
    return [Path(x).expanduser().resolve() for x in raw.split(os.pathsep) if x.strip()]


def ensure_allowed(path: Path) -> None:
    roots = allowed_roots()
    if roots is None:
        return
    target = path.expanduser().resolve()
    if not any(target == r or r in target.parents for r in roots):
        raise ReaderError(
            f"Đường dẫn nằm ngoài phạm vi cho phép: {path}\n"
            f"Chỉ đọc được trong: {', '.join(str(r) for r in roots)}\n"
            f"(giới hạn đặt bằng biến môi trường ARTSPEC_FILE_ROOT)")


@dataclass
class Outcome:
    """Một file đã nộp, cùng kết quả kiểm (hoặc lý do không kiểm được)."""
    path: Path
    report: Report | None = None
    error: str | None = None

    @property
    def verdict(self) -> str:
        if self.error:
            return "KHÔNG ĐỌC ĐƯỢC"
        return "KHÔNG QUA" if self.report.blocked else "QUA"


def check_file(reg: Registry, path: str | Path, asset_class: str | None = None,
               stage: str | None = None, platform: str | None = None) -> Outcome:
    p = Path(path)
    try:
        ensure_allowed(p)
        metrics = read(p, asset_class=asset_class, platform=platform)
        if not metrics.get("asset_class"):
            return Outcome(p, error=(
                "Không suy được asset_class từ đường dẫn. Nộp file vào thư mục tên "
                "theo class (vd submit/vehicle_exterior/), thêm sidecar "
                f"'{p.stem}.submit.json' chứa {{\"asset_class\": \"...\"}}, "
                "hoặc truyền asset_class khi gọi."))
        ext = None
        cfg = Path(reg.root) / "adapters.yaml"
        if cfg.is_file():
            ext = adapters.run_all(adapters.load_config(cfg), p)
        return Outcome(p, report=engine.run(reg, metrics, stage=stage, external=ext))
    except ReaderError as e:
        return Outcome(p, error=str(e))
    except Exception as e:  # noqa: BLE001 — một file hỏng không được làm dừng cả lô
        return Outcome(p, error=f"{type(e).__name__}: {e}")


def check_folder(reg: Registry, folder: str | Path, stage: str | None = None,
                 platform: str | None = None) -> list[Outcome]:
    root = Path(folder)
    try:
        ensure_allowed(root)
    except ReaderError as e:
        return [Outcome(root, error=str(e))]
    if not root.is_dir():
        return [Outcome(root, error=f"Không thấy thư mục: {root}")]
    files = sorted(p for p in root.rglob("*")
                   if p.is_file() and p.suffix.lower() in SUPPORTED
                   and not p.name.endswith(".submit.json"))
    return [check_file(reg, p, stage=stage, platform=platform) for p in files]


def summary_rows(outcomes: list[Outcome]) -> list[dict[str, Any]]:
    rows = []
    for o in outcomes:
        if o.error:
            rows.append({"file": o.path.name, "verdict": o.verdict,
                         "asset": "", "fail": None, "detail": o.error.splitlines()[0]})
            continue
        c = o.report.counts
        top = [f.rule.id for f in o.report.findings if f.status in ("FAIL", "ERROR")][:3]
        rows.append({
            "file": o.path.name,
            "asset": o.report.asset,
            "asset_class": o.report.asset_class,
            "verdict": o.verdict,
            "fail": c.get("FAIL", 0) + c.get("ERROR", 0),
            "warn": c.get("WARN", 0),
            "manual": c.get("MANUAL", 0),
            "skip": c.get("SKIP", 0),
            "detail": ", ".join(top),
        })
    return rows
