"""CLI — chạy được độc lập, không cần MCP.

    python -m artspec.cli validate samples/metrics_fail.json
    python -m artspec.cli validate samples/metrics_fail.json --stage G2 --json
    python -m artspec.cli rules --asset-class vehicle_exterior
    python -m artspec.cli explain VEH-UV-002
    python -m artspec.cli checklist vehicle_exterior G1
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from . import engine, inbox, registry, render

DEFAULT_ROOT = Path(__file__).resolve().parent.parent


def _load(root: Path):
    try:
        return registry.load(root)
    except registry.RegistryError as e:
        print(f"LỖI REGISTRY: {e}", file=sys.stderr)
        raise SystemExit(2)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="artspec", description="Kiểm asset 3D theo techspec dự án")
    ap.add_argument("--root", type=Path, default=DEFAULT_ROOT, help="thư mục chứa rules/")
    sub = ap.add_subparsers(dest="cmd", required=True)

    v = sub.add_parser("validate", help="kiểm một file metrics")
    v.add_argument("metrics", type=Path)
    v.add_argument("--stage", help="chỉ chạy luật của gate này (G0/G1/G2/G3)")
    v.add_argument("--json", action="store_true", help="xuất JSON thay vì text")
    v.add_argument("--show-pass", action="store_true", help="hiện cả luật đã đạt")

    ck = sub.add_parser("check", help="kiểm thẳng một file 3D hoạ sĩ nộp (.fbx/.glb/.obj)")
    ck.add_argument("file", type=Path)
    ck.add_argument("--asset-class")
    ck.add_argument("--stage")
    ck.add_argument("--platform")
    ck.add_argument("--show-pass", action="store_true")

    ib = sub.add_parser("inbox", help="quét cả thư mục nộp bài, in bảng tóm tắt cho Lead")
    ib.add_argument("folder", type=Path)
    ib.add_argument("--stage")
    ib.add_argument("--platform")
    ib.add_argument("--json", action="store_true")

    r = sub.add_parser("rules", help="liệt kê luật")
    r.add_argument("--asset-class")
    r.add_argument("--stage")

    u = sub.add_parser("updates", help="update khách hàng ảnh hưởng tới một class")
    u.add_argument("asset_class")
    u.add_argument("--since", help="YYYY-MM-DD")

    e = sub.add_parser("explain", help="xem chi tiết một luật")
    e.add_argument("rule_id")

    c = sub.add_parser("checklist", help="in checklist của một gate")
    c.add_argument("asset_class")
    c.add_argument("stage")

    a = ap.parse_args(argv)
    reg = _load(a.root)

    if a.cmd == "validate":
        metrics = json.loads(a.metrics.read_text(encoding="utf-8"))
        metrics.setdefault("source_file", str(a.metrics))
        report = engine.run(reg, metrics, stage=a.stage)
        if a.json:
            print(json.dumps(report.to_dict(), ensure_ascii=False, indent=2))
        else:
            print(render.report_text(report, show_pass=a.show_pass))
        return 1 if report.blocked else 0

    if a.cmd == "check":
        out = inbox.check_file(reg, a.file, asset_class=a.asset_class,
                               stage=a.stage, platform=a.platform)
        if out.error:
            print(f"⛔ Không kiểm được {a.file.name}:\n{out.error}", file=sys.stderr)
            return 2
        print(render.report_text(out.report, show_pass=a.show_pass))
        return 1 if out.report.blocked else 0

    if a.cmd == "inbox":
        outs = inbox.check_folder(reg, a.folder, stage=a.stage, platform=a.platform)
        rows = inbox.summary_rows(outs)
        if a.json:
            print(json.dumps(rows, ensure_ascii=False, indent=2))
        else:
            print(render.inbox_text(rows))
        return 1 if any(r["verdict"] != "QUA" for r in rows) else 0

    if a.cmd == "rules":
        rows = reg.rules_for(a.asset_class, a.stage)
        print(f"{len(rows)} luật\n")
        for rule in rows:
            print(f"  {rule.id:<14} {rule.severity.upper():<5} tier {rule.tier}  "
                  f"{rule.stage}  {rule.title}")
        return 0

    if a.cmd == "updates":
        ups = reg.updates_for(a.asset_class, a.since)
        if not ups:
            print(f"Không có update nào ảnh hưởng tới '{a.asset_class}'"
                  + (f" từ {a.since}." if a.since else "."))
            return 0
        for up in ups:
            print(f"\n{up['id']}  ·  hiệu lực {up.get('effective_from')}  "
                  f"·  {up.get('status')}")
            print(f"  nguồn      : {up.get('source', '')}")
            print(f"  tóm tắt    : {str(up.get('summary_vi', '')).strip()}")
            print(f"  luật đổi   : {', '.join(up.get('affects_rules', [])) or '—'}")
            print(f"  phải làm gì: {str(up.get('action_required', '')).strip()}")
        return 0

    if a.cmd == "explain":
        rule = reg.get(a.rule_id)
        if not rule:
            print(f"Không có luật '{a.rule_id}'.", file=sys.stderr)
            near = reg.search(a.rule_id)
            if near:
                print("Gần giống: " + ", ".join(r.id for r in near[:5]), file=sys.stderr)
            return 2
        print(render.rule_text(rule))
        return 0

    if a.cmd == "checklist":
        cl = reg.checklists.get(a.asset_class)
        if not cl or a.stage not in cl.get("stages", {}):
            print(f"Không có checklist {a.asset_class}/{a.stage}", file=sys.stderr)
            return 2
        st = cl["stages"][a.stage]
        print(f"{a.stage} — {st.get('title', '')}\n")
        for item in st.get("items", []):
            print(f"  [ ] {item}")
        for rule in reg.rules_for(a.asset_class, a.stage):
            mark = "máy kiểm" if rule.tier in ("A", "B") else "tự kiểm"
            print(f"  [ ] {rule.title}  ({rule.id}, {mark})")
        for item in st.get("extra_items", []):
            print(f"  [ ] {item}")
        if st.get("signature_required"):
            print("\n  CHỮ KÝ HOẠ SĨ: ____________     LEAD DUYỆT: ____________")
        return 0

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
