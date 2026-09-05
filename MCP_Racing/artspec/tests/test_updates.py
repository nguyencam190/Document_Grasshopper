"""Kiểm tool whats_changed_for + changelog."""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from artspec import registry  # noqa: E402
from artspec.server import get_update, whats_changed_for  # noqa: E402


def run() -> None:
    reg = registry.load(Path(__file__).resolve().parent.parent)
    checks = [
        ("nạp được changelog", len(reg.updates) >= 2, str(len(reg.updates))),
        ("lọc theo asset_class",
         [u["id"] for u in reg.updates_for("vehicle_exterior")] == ["CU-2026-047", "CU-2026-041"],
         str([u["id"] for u in reg.updates_for("vehicle_exterior")])),
        ("class không liên quan trả rỗng", reg.updates_for("building") == [], ""),
        ("lọc theo mốc thời gian",
         [u["id"] for u in reg.updates_for(since="2026-08-20")] == ["CU-2026-047"], ""),
    ]

    r = whats_changed_for("vehicle_exterior", since="2026-08-20")
    checks += [
        ("tool trả found=true", r["found"] is True, ""),
        ("kèm version hiện tại của luật bị ảnh hưởng",
         r["updates"][0]["affected_rules"][0]["current_version"] == 1, ""),
        ("kèm action_required", "gộp material" in r["updates"][0]["action_required"], ""),
    ]

    empty = whats_changed_for("building")
    checks += [
        ("không có update thì found=false, KHÔNG bịa",
         empty["found"] is False and empty["updates"] == [], str(empty)),
        ("kèm câu giải thích rõ ràng", "Không có update" in empty["error"], ""),
        ("get_update mã sai trả found=false",
         get_update("CU-9999")["found"] is False, ""),
        ("get_update giữ nguyên văn trích dẫn",
         "raw_excerpt" in get_update("CU-2026-041"), ""),
    ]

    fails = [c for c in checks if not c[1]]
    for name, ok, extra in checks:
        print(f"  {'✓' if ok else '✗'} {name}" + (f"   [{extra}]" if not ok and extra else ""))
    print(f"\n{len(checks) - len(fails)}/{len(checks)} pass")
    if fails:
        raise SystemExit(1)


if __name__ == "__main__":
    run()
