"""Kiểm bước gộp cấu hình — chỗ dễ làm mất server đang có nhất."""
from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import cai_dat_mcp as M  # noqa: E402


def fake_maya(d: Path) -> Path:
    r = d / "MayaMCP-main"
    (r / "src").mkdir(parents=True)
    (r / "src" / "maya_mcp_server.py").write_text("", encoding="utf-8")
    return r


def fake_artspec(d: Path) -> Path:
    r = d / "artspec"
    (r / "artspec").mkdir(parents=True)
    (r / "artspec" / "server.py").write_text("", encoding="utf-8")
    return r


def run() -> None:
    c: list[tuple[str, bool, str]] = []
    with tempfile.TemporaryDirectory() as t:
        d = Path(t)
        maya, arts = fake_maya(d), fake_artspec(d)

        # 1. chưa có file cấu hình
        cfg = d / "c1.json"
        M.merge_config(cfg, {"MayaMCP": M.entry_maya_mcp(maya)})
        data = json.loads(cfg.read_text(encoding="utf-8"))
        c += [("chưa có file → tự tạo", cfg.is_file(), ""),
              ("ghi đúng tên server", "MayaMCP" in data["mcpServers"], str(data)),
              ("trỏ đúng file server",
               data["mcpServers"]["MayaMCP"]["args"][0].endswith("src/maya_mcp_server.py"),
               str(data["mcpServers"]["MayaMCP"]["args"]))]

        # 2. GIỮ NGUYÊN server đang có — đây là điều quan trọng nhất
        cfg2 = d / "c2.json"
        cfg2.write_text(json.dumps({
            "mcpServers": {"github": {"command": "npx", "args": ["-y", "gh-mcp"]},
                           "filesystem": {"command": "node", "args": ["fs.js"]}},
            "theme": "dark"}), encoding="utf-8")
        backup, replaced = M.merge_config(cfg2, {"artspec": M.entry_artspec(arts)})
        d2 = json.loads(cfg2.read_text(encoding="utf-8"))
        c += [
            ("GIỮ NGUYÊN server đang có",
             {"github", "filesystem"} <= set(d2["mcpServers"]), str(list(d2["mcpServers"]))),
            ("giữ nguyên cả cài đặt khác ngoài mcpServers",
             d2.get("theme") == "dark", str(d2.get("theme"))),
            ("thêm được server mới", "artspec" in d2["mcpServers"], ""),
            ("không báo nhầm là đã thay thế", replaced == [], str(replaced)),
            ("có sao lưu bản cũ", backup is not None and backup.is_file(), str(backup)),
            ("bản sao lưu còn nguyên nội dung cũ",
             "github" in json.loads(backup.read_text(encoding="utf-8"))["mcpServers"], ""),
        ]

        # 3. trùng tên → thay và báo
        _, replaced = M.merge_config(cfg2, {"artspec": M.entry_artspec(arts)})
        c.append(("cài lại lần hai → báo là đã thay mục cùng tên",
                  replaced == ["artspec"], str(replaced)))

        # 4. JSON hỏng → báo lỗi, KHÔNG phá file
        cfg3 = d / "c3.json"
        cfg3.write_text("{ day khong phai json", encoding="utf-8")
        before = cfg3.read_text(encoding="utf-8")
        try:
            M.merge_config(cfg3, {"artspec": M.entry_artspec(arts)})
            c.append(("JSON hỏng → báo lỗi", False, "không raise"))
        except RuntimeError as e:
            c += [("JSON hỏng → báo lỗi kèm đường dẫn file", "c3.json" in str(e), str(e)[:60]),
                  ("JSON hỏng → KHÔNG ghi đè file của người dùng",
                   cfg3.read_text(encoding="utf-8") == before, "")]

        # 5. sai đường dẫn → nói rõ phải trỏ vào đâu
        try:
            M.entry_maya_mcp(d / "khong_ton_tai")
            c.append(("sai đường dẫn → báo rõ", False, "không raise"))
        except FileNotFoundError as e:
            c.append(("sai đường dẫn → chỉ rõ phải trỏ vào thư mục nào",
                      "maya_mcp_server.py" in str(e), str(e)[:60]))

        # 6. dry-run không đụng file nào
        cfg4 = d / "c4.json"
        rc = M.main(["--artspec", str(arts), "--config", str(cfg4), "--dry-run"])
        c.append(("--dry-run: không tạo file nào", rc == 0 and not cfg4.exists(), ""))

        # 7. cài cả hai cùng lúc
        cfg5 = d / "c5.json"
        M.merge_config(cfg5, {"MayaMCP": M.entry_maya_mcp(maya),
                              "artspec": M.entry_artspec(arts)})
        d5 = json.loads(cfg5.read_text(encoding="utf-8"))["mcpServers"]
        c += [("cài được cả hai server cùng lúc",
               {"MayaMCP", "artspec"} <= set(d5), str(list(d5))),
              ("artspec có đủ biến môi trường",
               {"PYTHONPATH", "ARTSPEC_ROOT"} <= set(d5["artspec"]["env"]), ""),
              ("đường dẫn dùng dấu / (Windows đọc được)",
               "\\" not in json.dumps(d5), "")]

    fails = [x for x in c if not x[1]]
    for name, ok, extra in c:
        print(f"  {'✓' if ok else '✗'} {name}" + (f"   [{extra}]" if not ok and extra else ""))
    print(f"\n{len(c) - len(fails)}/{len(c)} pass")
    if fails:
        raise SystemExit(1)


if __name__ == "__main__":
    run()
