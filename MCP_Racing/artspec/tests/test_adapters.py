"""Kiểm lớp nối nhiều tool validate ngoài vào một báo cáo."""
from __future__ import annotations

import shutil
import sys
import tempfile
import textwrap
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from artspec import adapters, engine, inbox, registry, render  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent

# Ba tool giả: một in JSON, một in text, một cố tình hỏng.
TOOL_JSON = '''
import json, sys
print(json.dumps({"issues": [
    {"type": "TRICOUNT_OVER", "node": "SM_Body_LOD0", "message": "132450 / 96000"},
    {"type": "TRICOUNT_OVER", "node": "SM_Glass_LOD0", "message": "9000 / 4000"},
    {"type": "UNKNOWN_THING",  "node": "SM_Body_LOD0", "message": "cái gì đó lạ"}]}))
sys.exit(1)                      # nhiều tool trả 1 khi tìm thấy lỗi
'''

TOOL_TEXT = '''
print("== BAO CAO ==")
print("UV_OVERLAP      SM_Body_LOD0   3 shell chong nhau")
print("khong phai dong loi")
'''

TOOL_BROKEN = 'import sys; sys.stderr.write("thieu thu vien\\n"); sys.exit(3)'


def write_tools(d: Path) -> None:
    for name, body in (("t_json.py", TOOL_JSON), ("t_text.py", TOOL_TEXT),
                       ("t_broken.py", TOOL_BROKEN)):
        (d / name).write_text(textwrap.dedent(body), encoding="utf-8")


def config(d: Path) -> str:
    py = sys.executable
    return textwrap.dedent(f'''
        - name: maya_validator
          type: json_cli
          command: ["{py}", "{d / 't_json.py'}", "{{file}}"]
          findings_path: issues
          fields: {{code: type, object: node, detail: message}}

        - name: uv_checker
          type: regex_text
          command: ["{py}", "{d / 't_text.py'}", "{{file}}"]
          pattern: '^(?P<code>[A-Z_]+)\\s+(?P<object>\\S+)\\s+(?P<detail>.*)$'

        - name: tool_hong
          type: json_cli
          command: ["{py}", "{d / 't_broken.py'}", "{{file}}"]
          findings_path: issues

        - name: chi_cho_fbx
          type: json_cli
          command: ["{py}", "{d / 't_json.py'}", "{{file}}"]
          findings_path: issues
          applies_to_ext: [".fbx"]
    ''')


def run() -> None:
    c: list[tuple[str, bool, str]] = []

    with tempfile.TemporaryDirectory() as tmpdir:
        d = Path(tmpdir)
        write_tools(d)
        work = d / "artspec"
        shutil.copytree(ROOT, work, ignore=shutil.ignore_patterns(
            "__pycache__", ".venv", "tests"))
        (work / "adapters.yaml").write_text(config(d), encoding="utf-8")

        # luật nhận mã ngoài TRICOUNT_OVER
        rule = (work / "rules" / "vehicle" / "VEH-TRI-001.yaml")
        rule.write_text(rule.read_text(encoding="utf-8")
                        + "\nexternal_codes: [TRICOUNT_OVER]\n", encoding="utf-8")
        target = work / "samples" / "metrics_pass.json"

        cfg = adapters.load_config(work / "adapters.yaml")
        res = adapters.run_all(cfg, target)
        codes = sorted({f.code for f in res.findings})
        c += [
            ("json_cli đọc được lỗi", "TRICOUNT_OVER" in codes, str(codes)),
            ("regex_text đọc được lỗi", "UV_OVERLAP" in codes, str(codes)),
            ("regex_text bỏ qua dòng không khớp", len(
                [f for f in res.findings if f.source == "uv_checker"]) == 1, ""),
            ("chạy được nhiều tool cùng lúc",
             len({f.source for f in res.findings}) == 2,
             str({f.source for f in res.findings})),
            ("tool hỏng không làm sập cả lượt", len(res.errors) == 1, str(res.errors)),
            ("báo rõ tool nào hỏng", "tool_hong" in res.errors[0], res.errors[0]),
            ("lọc theo đuôi file: .json không chạy tool chỉ-cho-fbx",
             "chi_cho_fbx" not in {f.source for f in res.findings}, ""),
            ("giữ nguyên chi tiết của tool",
             any("132450" in f.detail for f in res.findings), ""),
        ]

        reg = registry.load(work)
        c.append(("registry lập chỉ mục mã ngoài",
                  reg.by_code("tricount_over") is not None
                  and reg.by_code("TRICOUNT_OVER").id == "VEH-TRI-001", ""))

        import json as _j
        report = engine.run(reg, _j.loads(target.read_text(encoding="utf-8")),
                            external=res)
        got = {f.rule.id: f for f in report.findings}

        mapped = got.get("VEH-TRI-001")
        c += [
            ("mã đã khai → gắn đúng luật", mapped is not None, str(list(got)[:6])),
            ("gộp 2 lỗi cùng mã thành 1 mục, 2 dòng Ở ĐÂU",
             mapped is not None and len(mapped.locations) == 2,
             str(len(mapped.locations)) if mapped else "-"),
            ("dùng severity của luật, không phải của tool",
             mapped is not None and mapped.status == "FAIL", ""),
        ]
        if mapped:
            txt = render.finding_text(mapped)
            c += [
                ("báo cáo có VÌ SAO lấy từ luật", "VÌ SAO" in txt and "12 xe" in txt, ""),
                ("báo cáo có SỬA THẾ NÀO lấy từ luật", "SỬA THẾ NÀO" in txt, ""),
                ("nêu rõ nguồn là tool ngoài", "maya_validator" in txt, ""),
            ]

        unmapped = [f for f in report.findings if f.rule.id.startswith("EXT:")]
        c += [
            ("mã CHƯA khai không bị bỏ im lặng",
             any(f.rule.id == "EXT:UNKNOWN_THING" for f in unmapped),
             str([f.rule.id for f in unmapped])),
            ("mã chưa khai để mức WARN, không FAIL",
             all(f.status == "WARN" for f in unmapped if f.rule.id != "EXT:TOOL_ERROR"), ""),
            ("hướng dẫn cách khai báo mã đó",
             any("external_codes" in " ".join(f.rule.how_to_fix) for f in unmapped), ""),
            ("tool hỏng hiện thành ERROR",
             any(f.status == "ERROR" for f in report.findings), ""),
        ]

        # hai luật cùng nhận một mã → phải báo lỗi lúc nạp
        other = work / "rules" / "vehicle" / "VEH-NAM-001.yaml"
        other.write_text(other.read_text(encoding="utf-8")
                         + "\nexternal_codes: [TRICOUNT_OVER]\n", encoding="utf-8")
        try:
            registry.load(work)
            c.append(("hai luật trùng mã ngoài → báo lỗi", False, "không raise"))
        except registry.RegistryError as e:
            c.append(("hai luật trùng mã ngoài → báo lỗi rõ ràng",
                      "TRICOUNT_OVER" in str(e) and "VEH-TRI-001" in str(e), str(e)[:70]))

    fails = [x for x in c if not x[1]]
    for name, ok, extra in c:
        print(f"  {'✓' if ok else '✗'} {name}" + (f"   [{extra}]" if not ok and extra else ""))
    print(f"\n{len(c) - len(fails)}/{len(c)} pass")
    if fails:
        raise SystemExit(1)


if __name__ == "__main__":
    run()
