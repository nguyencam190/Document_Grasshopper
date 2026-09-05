"""Kiểm file hoạ sĩ nộp lên — Lead không phải mở file 3D.

    from artspec import inbox
    inbox.check_file(reg, "submit/vehicle_exterior/SUV_A.fbx")
    inbox.check_folder(reg, "submit/")
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from . import engine
from .model import Report
from .readers import SUPPORTED, ReaderError, read
from .registry import Registry


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
        metrics = read(p, asset_class=asset_class, platform=platform)
        if not metrics.get("asset_class"):
            return Outcome(p, error=(
                "Không suy được asset_class từ đường dẫn. Nộp file vào thư mục tên "
                "theo class (vd submit/vehicle_exterior/), thêm sidecar "
                f"'{p.stem}.submit.json' chứa {{\"asset_class\": \"...\"}}, "
                "hoặc truyền asset_class khi gọi."))
        return Outcome(p, report=engine.run(reg, metrics, stage=stage))
    except ReaderError as e:
        return Outcome(p, error=str(e))
    except Exception as e:  # noqa: BLE001 — một file hỏng không được làm dừng cả lô
        return Outcome(p, error=f"{type(e).__name__}: {e}")


def check_folder(reg: Registry, folder: str | Path, stage: str | None = None,
                 platform: str | None = None) -> list[Outcome]:
    root = Path(folder)
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
