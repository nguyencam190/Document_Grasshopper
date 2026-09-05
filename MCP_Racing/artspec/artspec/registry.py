"""Đọc rules/, checklists/, glossary/, waivers/ từ đĩa và kiểm tra tính hợp lệ.

Nguyên tắc: fail loudly. Một file luật viết sai phải báo lỗi ngay lúc load, chứ
không được im lặng bỏ qua — luật bị bỏ qua âm thầm còn nguy hiểm hơn không có luật.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from pathlib import Path
from typing import Any

import yaml

from .model import Rule

REQUIRED = ("id", "title", "asset_class", "category", "tier", "severity",
            "stage", "check", "why", "how_to_fix", "version", "effective_from")


class RegistryError(Exception):
    pass


@dataclass
class Registry:
    root: Path
    rules: dict[str, Rule] = field(default_factory=dict)
    checklists: dict[str, dict[str, Any]] = field(default_factory=dict)
    glossary: list[dict[str, Any]] = field(default_factory=list)
    waivers: list[dict[str, Any]] = field(default_factory=list)
    updates: list[dict[str, Any]] = field(default_factory=list)

    # ---- truy vấn ----

    def asset_classes(self) -> list[str]:
        return sorted({r.asset_class for r in self.rules.values()})

    def rules_for(self, asset_class: str | None = None,
                  stage: str | None = None) -> list[Rule]:
        out = [r for r in self.rules.values() if r.status == "active"]
        if asset_class:
            out = [r for r in out if r.asset_class == asset_class]
        if stage:
            out = [r for r in out if r.stage == stage]
        return sorted(out, key=lambda r: r.id)

    def get(self, rule_id: str) -> Rule | None:
        return self.rules.get(rule_id.strip().upper())

    def search(self, query: str, asset_class: str | None = None) -> list[Rule]:
        q = query.lower().strip()
        scored: list[tuple[int, Rule]] = []
        for r in self.rules_for(asset_class):
            hay = " ".join([
                r.id, r.title, r.category, r.why,
                " ".join(r.how_to_fix), " ".join(r.common_mistakes),
            ]).lower()
            if q in r.id.lower():
                scored.append((100, r))
            elif q in r.title.lower():
                scored.append((50, r))
            elif q in hay:
                scored.append((10, r))
        scored.sort(key=lambda t: (-t[0], t[1].id))
        return [r for _, r in scored]

    def term(self, name: str) -> dict[str, Any] | None:
        n = name.lower().strip()
        for t in self.glossary:
            if n == str(t.get("term", "")).lower():
                return t
            if n in [str(a).lower() for a in t.get("aliases", [])]:
                return t
        return None

    def updates_for(self, asset_class: str | None = None,
                    since: str | None = None) -> list[dict[str, Any]]:
        """Update khách hàng, mới nhất trước. Lọc theo class và mốc thời gian."""
        out = list(self.updates)
        if asset_class:
            out = [u for u in out
                   if asset_class in (u.get("affects_asset_classes") or [])]
        if since:
            cut = _as_date(since)
            out = [u for u in out
                   if _as_date(u.get("effective_from") or u.get("date_received")) >= cut]
        return sorted(out, key=lambda u: str(u.get("effective_from", "")), reverse=True)

    def update(self, update_id: str) -> dict[str, Any] | None:
        uid = update_id.strip().upper()
        return next((u for u in self.updates if str(u.get("id", "")).upper() == uid), None)

    def waiver_for(self, rule_id: str, asset: str,
                   today: date | None = None) -> dict[str, Any] | None:
        today = today or date.today()
        for w in self.waivers:
            if w.get("rule") != rule_id or w.get("asset") != asset:
                continue
            exp = w.get("expires")
            if exp and _as_date(exp) < today:
                continue  # waiver hết hạn thì tự mất tác dụng
            return w
        return None


def _as_date(v: Any) -> date:
    if isinstance(v, date):
        return v
    return date.fromisoformat(str(v))


def _load_yaml(p: Path) -> Any:
    try:
        return yaml.safe_load(p.read_text(encoding="utf-8"))
    except yaml.YAMLError as e:
        raise RegistryError(f"{p}: YAML hỏng — {e}") from e


def load(root: str | Path) -> Registry:
    root = Path(root)
    if not root.is_dir():
        raise RegistryError(f"Không thấy thư mục registry: {root}")
    reg = Registry(root=root)

    for p in sorted((root / "rules").rglob("*.yaml")):
        if p.name.startswith("_"):
            continue
        data = _load_yaml(p)
        if not isinstance(data, dict):
            raise RegistryError(f"{p}: file luật phải là một object YAML")
        missing = [k for k in REQUIRED if k not in data]
        if missing:
            raise RegistryError(f"{p}: thiếu field bắt buộc {missing} (xem rules/_SCHEMA.md)")
        if data["severity"] not in ("fail", "warn", "info"):
            raise RegistryError(f"{p}: severity phải là fail/warn/info")
        if data["tier"] not in ("A", "B", "C"):
            raise RegistryError(f"{p}: tier phải là A/B/C")
        rid = str(data["id"]).strip().upper()
        if rid in reg.rules:
            raise RegistryError(f"{p}: id {rid} trùng với {reg.rules[rid].path}")
        fix = data["how_to_fix"]
        data["how_to_fix"] = [fix] if isinstance(fix, str) else list(fix)
        data["effective_from"] = str(_as_date(data["effective_from"]))
        known = {f for f in Rule.__dataclass_fields__}
        reg.rules[rid] = Rule(path=str(p.relative_to(root)),
                              **{k: v for k, v in data.items() if k in known and k != "path"})

    for p in sorted((root / "checklists").glob("*.yaml")):
        data = _load_yaml(p) or {}
        reg.checklists[data.get("asset_class", p.stem)] = data

    gdir = root / "glossary"
    if gdir.is_dir():
        for p in sorted(gdir.glob("*.yaml")):
            reg.glossary.extend(_load_yaml(p) or [])

    cdir = root / "changelog"
    if cdir.is_dir():
        for p in sorted(cdir.glob("*.yaml")):
            data = _load_yaml(p)
            if not isinstance(data, dict) or "id" not in data:
                raise RegistryError(f"{p}: file changelog phải là object YAML có 'id'")
            for k in ("effective_from", "date_received"):
                if k in data:
                    data[k] = str(_as_date(data[k]))
            reg.updates.append(data)

    wdir = root / "waivers"
    if wdir.is_dir():
        for p in sorted(wdir.glob("*.yaml")):
            reg.waivers.extend(_load_yaml(p) or [])

    return reg
