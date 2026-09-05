"""Kiểm bộ quét mã nguồn validator.

Điểm quan trọng nhất được kiểm: scanner KHÔNG chạy và KHÔNG import mã nguồn.
Bộ mẫu dưới đây có file `import maya` và file ném lỗi ngay khi nạp — nếu scanner
import thật thì test sẽ vỡ.
"""
from __future__ import annotations

import sys
import tempfile
import textwrap
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import yaml  # noqa: E402

from artspec import scanner  # noqa: E402

FILES = {
    "studio/__init__.py": "",
    "studio/checks/__init__.py": "",
    "studio/checks/geometry.py": '''
        from maya import cmds                 # sẽ nổ nếu scanner import thật
        def check_topology(nodes=None, strict=False):
            """Kiểm topology."""
            return [{"code": "GEO_NGON", "object": "x", "message": "m"},
                    {"code": "GEO_NONMANIFOLD", "object": "x", "message": "m"}]
        def _helper(): return 1
    ''',
    "studio/checks/uv.py": '''
        def check_uv(mesh=None):
            """Kiểm UV."""
            return [{"code": "UV_OVERLAP", "object": mesh, "message": ""}]
    ''',
    "studio/utils/__init__.py": "",
    "studio/utils/helpers.py": '''
        def load_config(path):
            """Không phải validator."""
            return {}
    ''',
    "studio/runner.py": '''
        from studio.checks import geometry, uv
        def run_all(strict=False):
            """Chạy toàn bộ."""
            out = []
            out += geometry.check_topology(strict=strict)
            out += uv.check_uv()
            return out
    ''',
    "studio/explode.py": 'raise RuntimeError("nổ ngay khi import")\n',
    "studio/broken.py": "def check_x(\n",
    "__pycache__/junk.py": "def check_cache(): return []\n",
}


def build(d: Path) -> Path:
    root = d / "pipeline"
    for rel, body in FILES.items():
        p = root / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(textwrap.dedent(body).lstrip(), encoding="utf-8")
    return root


def run() -> None:
    c: list[tuple[str, bool, str]] = []
    with tempfile.TemporaryDirectory() as t:
        root = build(Path(t))
        before = set(sys.modules)
        res = scanner.scan(root)
        names = [f"{x['module']}.{x['function']}" for x in res["candidates"]]

        c += [
            ("không import mã nguồn (file 'nổ khi import' vẫn yên)",
             set(sys.modules) == before, "có module lạ được nạp"),
            ("không cần Maya — file `import maya` vẫn đọc được",
             any("geometry" in n for n in names), str(names)),
            ("tìm được các validator",
             {"studio.checks.geometry.check_topology",
              "studio.checks.uv.check_uv"} <= set(names), str(names)),
            ("nhận ra hàm TỔNG HỢP dù tên không có chữ check/validate",
             "studio.runner.run_all" in names, str(names)),
            ("hàm tổng hợp xếp đầu tiên",
             names and names[0] == "studio.runner.run_all", str(names[:2])),
            ("bỏ qua hàm không phải validator",
             "studio.utils.helpers.load_config" not in names, ""),
            ("bỏ qua hàm bắt đầu bằng _",
             not any(x["function"].startswith("_") for x in res["candidates"]), ""),
            ("bỏ qua thư mục __pycache__",
             not any("junk" in n for n in names), str(names)),
        ]

        codes = res["error_codes"]
        c += [
            ("gom đủ mã lỗi",
             {"GEO_NGON", "GEO_NONMANIFOLD", "UV_OVERLAP"} <= set(codes), str(list(codes))),
            ("mỗi mã ghi rõ nằm ở hàm nào",
             "studio.checks.geometry.check_topology" in codes["GEO_NGON"],
             str(codes.get("GEO_NGON"))),
            ("file lỗi cú pháp: báo rõ, không làm sập cả lượt",
             len(res["unreadable"]) == 1 and "broken.py" in res["unreadable"][0],
             str(res["unreadable"])),
        ]

        agg = next(x for x in res["candidates"] if x["function"] == "run_all")
        c.append(("hàm tổng hợp liệt kê được nó gọi những gì",
                  set(agg["aggregates"]) == {"check_topology", "check_uv"},
                  str(agg["aggregates"])))

        y = scanner.suggest_adapters(res)
        parsed = yaml.safe_load("\n".join(
            l for l in y.splitlines() if not l.lstrip().startswith("#")))
        c += [
            ("adapters.yaml sinh ra đúng cú pháp YAML", isinstance(parsed, list), type(parsed).__name__),
            ("mục đầu tiên là hàm tổng hợp",
             parsed and parsed[0]["function"] == "run_all", str(parsed[:1])),
            ("có đủ khoá bắt buộc",
             parsed and {"name", "type", "module", "function"} <= set(parsed[0]), ""),
            ("ghi rõ chỗ nào đang ĐOÁN phải sửa", "ĐOÁN" in y, ""),
            ("khuyên khai mỗi hàm tổng hợp là đủ", "TỔNG HỢP" in y, ""),
        ]
        c.append(("danh sách mã lỗi để dán vào luật",
                  "GEO_NGON" in scanner.suggest_rule_codes(res), ""))

    fails = [x for x in c if not x[1]]
    for name, ok, extra in c:
        print(f"  {'✓' if ok else '✗'} {name}" + (f"   [{extra}]" if not ok and extra else ""))
    print(f"\n{len(c) - len(fails)}/{len(c)} pass")
    if fails:
        raise SystemExit(1)


if __name__ == "__main__":
    run()
