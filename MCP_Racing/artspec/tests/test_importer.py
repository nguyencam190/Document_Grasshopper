"""Kiểm bộ chuyển CSV → luật YAML: cú pháp check, bắt lỗi, và luật sinh ra chạy được."""
from __future__ import annotations

import shutil
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from artspec import importer, inbox, registry, render  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent

BAD_CSV = """id,title,asset_class,category,tier,severity,stage,check,why,how_to_check,how_to_fix,common_mistakes,golden_asset,source_section,requires
X-001,Thiếu lý do,vehicle_exterior,geometry,A,fail,G1,triangle_count <= 100,,,Sửa đi,,,,
X-002,Tier sai,vehicle_exterior,geometry,Z,fail,G1,triangle_count <= 100,Vì thế,,Sửa đi,,,,
X-003,Check không hiểu,vehicle_exterior,geometry,A,fail,G1,triangle_count bé hơn 100,Vì thế,,Sửa đi,,,,
X-004,Severity sai,vehicle_exterior,geometry,A,blocker,G1,triangle_count <= 100,Vì thế,,Sửa đi,,,,
X-005,Không có cách sửa,vehicle_exterior,geometry,A,fail,G1,triangle_count <= 100,Vì thế,,,,,,
X-006,Dòng đúng,vehicle_exterior,geometry,A,fail,G1,ngons <= 0 ids ngon_faces,Vì n-gon vỡ shading,Maya HUD,Chia thành quad | Dùng Multi-Cut,Boolean quên dọn,SUV_Base,3.1,
"""


def run() -> None:
    c: list[tuple[str, bool, str]] = []

    # ── cú pháp check
    forms = {
        "triangle_count <= 96000 where lod=0, platform=pc": ("threshold", "value", 96000),
        "texel_density_px_cm within 10.24 +- 0.5": ("threshold_table", "op", "within"),
        "name matches ^SM_.+$": ("regex", "pattern", "^SM_.+$"),
        "color_space in sRGB | Linear": ("enum", "allowed", ["sRGB", "Linear"]),
        "ngons <= 0 ids ngon_faces": ("mesh_defect", "id_metric", "ngon_faces"),
        "inverted_normals is false": ("flag", "equals", False),
        "manual: Có bị che không?": ("manual", "ask", "Có bị che không?"),
        "custom: vehicle.wheel_bone_layout": ("custom", "function", "vehicle.wheel_bone_layout"),
    }
    for expr, (want_type, key, want_val) in forms.items():
        got = importer.parse_check(expr)
        c.append((f"cú pháp: {expr[:42]}",
                  got["type"] == want_type and got.get(key) == want_val, str(got)))
    c.append(("suy ra collection từ metric",
              importer.parse_check("color_space in sRGB")["applies_to"]["collection"] == "textures",
              ""))
    c.append(("đọc 'where' thành bộ lọc",
              importer.parse_check("triangle_count <= 1 where lod=2")["applies_to"]["where"]
              == {"lod": 2}, ""))

    with tempfile.TemporaryDirectory() as d:
        tmp = Path(d)

        # ── bắt lỗi: 5 dòng hỏng, 1 dòng đúng
        bad = tmp / "bad.csv"
        bad.write_text(BAD_CSV, encoding="utf-8")
        res = importer.from_csv(bad)
        c += [
            ("bỏ qua dòng hỏng, giữ dòng đúng", len(res.rules) == 1, str(len(res.rules))),
            ("báo đủ 5 lỗi", len(res.errors) == 5, str(len(res.errors))),
            ("nêu lý do thiếu 'why'", any("why" in e for e in res.errors), str(res.errors[:1])),
            ("nêu lý do thiếu 'how_to_fix'",
             any("how_to_fix" in e for e in res.errors), ""),
            ("nêu lý do check không hiểu",
             any("không hiểu" in e for e in res.errors), ""),
            ("mỗi lỗi có số dòng để tìm trong Excel",
             all(e.startswith("dòng ") for e in res.errors), str(res.errors[:1])),
        ]

        # ── bảng mẫu sinh ra luật CHẠY ĐƯỢC trong engine thật
        work = tmp / "artspec"
        shutil.copytree(ROOT, work, ignore=shutil.ignore_patterns(
            "__pycache__", ".venv", "tests"))
        res = importer.from_csv(ROOT / "checklists" / "_MAU_THU_THAP.csv")
        c.append(("bảng mẫu: 5 luật, 0 lỗi",
                  (len(res.rules), len(res.errors)) == (5, 0), str(res.errors)))
        c.append(("bảng mẫu: nhận ra Tier B cần viết hàm",
                  res.needs_code == [], str(res.needs_code)))
        shutil.rmtree(work / "rules" / "vehicle")
        importer.write_rules(res.rules, work / "rules" / "vehicle")

        reg = registry.load(work)
        c.append(("luật sinh ra nạp được vào registry",
                  len(reg.rules_for("vehicle_exterior")) == 15, ""))
        r = reg.get("VEH-TRI-010")
        c += [
            ("giữ nguyên 'why'", "12 xe" in r.why, ""),
            ("tách how_to_fix thành 3 bước", len(r.how_to_fix) == 3, str(r.how_to_fix)),
            ("tách common_mistakes thành 2 ý", len(r.common_mistakes) == 2, ""),
            ("giữ golden asset", r.reference["golden_asset"] == "SUV_Base", ""),
        ]

        out = inbox.check_file(reg, ROOT / "samples" / "metrics_fail.json", stage="G1")
        got = {f.rule.id: f.status for f in out.report.findings}
        c += [
            ("luật sinh ra CHẠY: bắt tricount vượt",
             got.get("VEH-TRI-010") == "FAIL", str(got.get("VEH-TRI-010"))),
            ("luật sinh ra CHẠY: bắt sai tên", got.get("VEH-NAM-010") == "FAIL", ""),
            ("Tier B thiếu skeleton → SKIP chứ không FAIL",
             got.get("VEH-RIG-010") in (None, "SKIP"), str(got.get("VEH-RIG-010"))),
        ]
        f = next(x for x in out.report.findings if x.rule.id == "VEH-TRI-010")
        c.append(("thông điệp lỗi vẫn đủ 5 phần",
                  all(k in render.finding_text(f)
                      for k in ("Ở ĐÂU", "VÌ SAO", "SỬA THẾ NÀO", "HAY GẶP VÌ", "XEM MẪU ĐÚNG")),
                  ""))

    fails = [x for x in c if not x[1]]
    for name, ok, extra in c:
        print(f"  {'✓' if ok else '✗'} {name}" + (f"   [{extra}]" if not ok and extra else ""))
    print(f"\n{len(c) - len(fails)}/{len(c)} pass")
    if fails:
        raise SystemExit(1)


if __name__ == "__main__":
    run()
