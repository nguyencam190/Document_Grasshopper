"""Kiểu dữ liệu dùng chung. Không chứa logic nghiệp vụ."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

# FAIL   chặn gate, không submit được
# WARN   cho qua nhưng ghi lại, Lead nhìn thấy
# MANUAL câu hỏi cho người, máy không kết luận được
# ERROR  lỗi của chính validator (luật viết sai / thiếu metric) — KHÔNG phải lỗi hoạ sĩ
STATUS_ORDER = ["FAIL", "ERROR", "WARN", "MANUAL", "INFO", "PASS", "SKIP"]


@dataclass
class Rule:
    id: str
    title: str
    asset_class: str
    category: str
    tier: str
    severity: str
    stage: str
    check: dict[str, Any]
    why: str
    how_to_fix: list[str]
    version: int
    effective_from: str
    status: str = "active"
    how_to_check: str | None = None
    common_mistakes: list[str] = field(default_factory=list)
    reference: dict[str, Any] | None = None
    source: dict[str, Any] | None = None
    changed_by_update: str | None = None
    path: str = ""

    @property
    def ref(self) -> str:
        return f"{self.id} (v{self.version}, hiệu lực {self.effective_from})"


@dataclass
class Location:
    """Chỗ cụ thể hoạ sĩ phải mở ra sửa. Thiếu cái này là báo lỗi vô dụng."""
    object: str
    detail: str = ""


@dataclass
class CheckOutcome:
    """Kết quả thô của một hàm check, trước khi áp severity và waiver."""
    ok: bool
    locations: list[Location] = field(default_factory=list)
    expected: str = ""
    actual: str = ""
    note: str = ""
    status_override: str | None = None


@dataclass
class Finding:
    rule: Rule
    status: str
    locations: list[Location] = field(default_factory=list)
    expected: str = ""
    actual: str = ""
    note: str = ""
    waiver: dict[str, Any] | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "rule_id": self.rule.id,
            "rule_title": self.rule.title,
            "rule_version": self.rule.version,
            "status": self.status,
            "category": self.rule.category,
            "tier": self.rule.tier,
            "stage": self.rule.stage,
            "expected": self.expected,
            "actual": self.actual,
            "note": self.note,
            "locations": [{"object": l.object, "detail": l.detail} for l in self.locations],
            "waiver": self.waiver,
        }


@dataclass
class Report:
    asset: str
    asset_class: str
    stage: str | None
    findings: list[Finding]
    source_file: str = ""

    @property
    def counts(self) -> dict[str, int]:
        out: dict[str, int] = {}
        for f in self.findings:
            out[f.status] = out.get(f.status, 0) + 1
        return out

    @property
    def blocked(self) -> bool:
        """True = không được qua gate."""
        return any(f.status in ("FAIL", "ERROR") for f in self.findings)

    def to_dict(self) -> dict[str, Any]:
        return {
            "asset": self.asset,
            "asset_class": self.asset_class,
            "stage": self.stage,
            "source_file": self.source_file,
            "blocked": self.blocked,
            "counts": self.counts,
            "findings": [f.to_dict() for f in self.findings],
        }
