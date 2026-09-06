"""Cài MCP server vào Claude Desktop — làm hộ những bước dễ sai.

    python cai_dat_mcp.py --maya-mcp D:/MAYA_TOOLS/MayaMCP-main
    python cai_dat_mcp.py --artspec  D:/Projects/MCP_Racing/artspec
    python cai_dat_mcp.py --maya-mcp D:/MAYA_TOOLS/MayaMCP-main --artspec D:/Projects/MCP_Racing/artspec

Nó làm gì:
  1. Kiểm Python >= 3.10
  2. Tạo môi trường ảo và cài thư viện cho từng server
  3. Tìm file cấu hình Claude Desktop
  4. GỘP mục mới vào, GIỮ NGUYÊN các server đang có, và sao lưu trước khi ghi
  5. In ra việc còn lại phải làm bằng tay

Bước 4 là chỗ hay hỏng nhất khi làm tay: người ta thường ghi đè cả file và mất
các server đã cài. Script này không bao giờ ghi đè — chỉ thêm hoặc thay đúng
mục cùng tên, và luôn để lại một bản sao lưu.
"""
from __future__ import annotations

import argparse
import json
import os
import platform
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path

MIN_PY = (3, 10)


def say(icon: str, msg: str) -> None:
    print(f"  {icon}  {msg}")


def config_path() -> Path:
    """Nơi Claude Desktop để file cấu hình, theo hệ điều hành."""
    system = platform.system()
    if system == "Windows":
        base = os.environ.get("APPDATA")
        if not base:
            raise RuntimeError("Không tìm thấy biến môi trường APPDATA")
        return Path(base) / "Claude" / "claude_desktop_config.json"
    if system == "Darwin":
        return Path.home() / "Library" / "Application Support" / "Claude" / "claude_desktop_config.json"
    return Path.home() / ".config" / "Claude" / "claude_desktop_config.json"


def venv_python(root: Path) -> Path:
    sub = "Scripts/python.exe" if platform.system() == "Windows" else "bin/python"
    return root / ".venv" / sub


def make_venv(root: Path, label: str) -> Path:
    """Tạo .venv và cài requirements.txt nếu có. Trả về đường dẫn python trong đó."""
    py = venv_python(root)
    if py.is_file():
        say("✓", f"{label}: đã có sẵn môi trường ảo")
    else:
        say("·", f"{label}: đang tạo môi trường ảo…")
        subprocess.run([sys.executable, "-m", "venv", str(root / ".venv")], check=True)
        say("✓", f"{label}: tạo xong môi trường ảo")

    req = root / "requirements.txt"
    if req.is_file():
        say("·", f"{label}: đang cài thư viện…")
        subprocess.run([str(py), "-m", "pip", "install", "-q", "-r", str(req)], check=True)
        say("✓", f"{label}: cài xong thư viện")
    else:
        say("!", f"{label}: không thấy requirements.txt — bỏ qua bước cài thư viện")
    return py


def verify(py: Path, code: str, label: str, root: Path) -> str | None:
    """Chạy thử import server. Trả về thông báo lỗi, hoặc None nếu chạy được.

    Cài xong mà không thử thì Claude Desktop sẽ im lặng không hiện tool nào và
    rất khó đoán vì sao.
    """
    proc = subprocess.run([str(py), "-c", code], capture_output=True, text=True,
                          cwd=str(root))
    if proc.returncode == 0:
        return None
    return (proc.stderr or proc.stdout).strip()


def fix_mcp_v1(py: Path, err: str, label: str) -> bool:
    """MayaMCP viết cho mcp 1.x nhưng requirements.txt không ghim phiên bản.

    `pip install mcp` kéo về 2.x và code vỡ ngay. Phát hiện đúng lỗi đó thì hạ
    xuống 1.x. Đây là lỗi của repo gốc, không phải của máy bạn.
    """
    if "fastmcp" not in err and "mcp 2" not in err.lower():
        return False
    say("!", f"{label}: repo này viết cho mcp 1.x nhưng requirements.txt không ghim")
    say("·", f"{label}: đang hạ xuống mcp<2…")
    subprocess.run([str(py), "-m", "pip", "install", "-q", "mcp<2"], check=True)
    return True


def entry_maya_mcp(root: Path) -> dict:
    server = root / "src" / "maya_mcp_server.py"
    if not server.is_file():
        raise FileNotFoundError(
            f"Không thấy {server}\n"
            f"     Kiểm lại đường dẫn — nó phải trỏ tới thư mục CHỨA src/maya_mcp_server.py")
    return {"command": venv_python(root).as_posix(), "args": [server.as_posix()]}


def entry_artspec(root: Path) -> dict:
    pkg = root / "artspec" / "server.py"
    if not pkg.is_file():
        raise FileNotFoundError(
            f"Không thấy {pkg}\n"
            f"     Đường dẫn phải trỏ tới thư mục CHỨA thư mục con artspec/")
    return {"command": venv_python(root).as_posix(),
            "args": ["-m", "artspec.server"],
            "env": {"PYTHONPATH": root.as_posix(), "ARTSPEC_ROOT": root.as_posix()}}


def merge_config(cfg_path: Path, servers: dict[str, dict]) -> tuple[Path | None, list[str]]:
    """Gộp các mục mới vào cấu hình, giữ nguyên phần đang có.

    Trả về (đường dẫn bản sao lưu, danh sách server bị thay thế).
    """
    data: dict = {}
    backup: Path | None = None
    if cfg_path.is_file():
        raw = cfg_path.read_text(encoding="utf-8").strip()
        if raw:
            try:
                data = json.loads(raw)
            except json.JSONDecodeError as e:
                raise RuntimeError(
                    f"File cấu hình hiện tại không phải JSON hợp lệ ({e}).\n"
                    f"     Sửa hoặc đổi tên nó rồi chạy lại: {cfg_path}") from e
        stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        backup = cfg_path.with_suffix(f".backup-{stamp}.json")
        shutil.copy2(cfg_path, backup)

    existing = data.setdefault("mcpServers", {})
    if not isinstance(existing, dict):
        raise RuntimeError("Khoá 'mcpServers' trong file cấu hình không đúng định dạng")

    replaced = [name for name in servers if name in existing]
    existing.update(servers)

    cfg_path.parent.mkdir(parents=True, exist_ok=True)
    cfg_path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n",
                        encoding="utf-8")
    return backup, replaced


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Cài MCP server vào Claude Desktop")
    ap.add_argument("--maya-mcp", type=Path, help="thư mục MayaMCP-main")
    ap.add_argument("--artspec", type=Path, help="thư mục artspec")
    ap.add_argument("--config", type=Path, help="ghi đè đường dẫn file cấu hình")
    ap.add_argument("--dry-run", action="store_true",
                    help="chỉ xem sẽ ghi gì, không sửa file nào")
    a = ap.parse_args(argv)

    if sys.version_info < MIN_PY:
        print(f"LỖI: cần Python {MIN_PY[0]}.{MIN_PY[1]} trở lên, "
              f"đang chạy {sys.version.split()[0]}")
        return 2
    if not (a.maya_mcp or a.artspec):
        ap.print_help()
        return 2

    print(f"\nPython {sys.version.split()[0]} · {platform.system()}\n")
    servers: dict[str, dict] = {}
    problems: list[str] = []
    try:
        if a.maya_mcp:
            root = a.maya_mcp.expanduser().resolve()
            entry = entry_maya_mcp(root)
            if not a.dry_run:
                py = make_venv(root, "MayaMCP")
                code = (f"import sys; sys.path.insert(0, r'{root / 'src'}'); "
                        f"import maya_mcp_server")
                err = verify(py, code, "MayaMCP", root)
                if err and fix_mcp_v1(py, err, "MayaMCP"):
                    err = verify(py, code, "MayaMCP", root)
                if err:
                    say("✗", f"MayaMCP: server KHÔNG chạy được:\n     "
                             + err.splitlines()[-1][:150])
                    problems.append("MayaMCP")
                else:
                    say("✓", "MayaMCP: server chạy thử OK")
            servers["MayaMCP"] = entry
        if a.artspec:
            root = a.artspec.expanduser().resolve()
            entry = entry_artspec(root)
            if not a.dry_run:
                py = make_venv(root, "artspec")
                err = verify(py, "import artspec.server", "artspec", root)
                if err:
                    say("✗", f"artspec: server KHÔNG chạy được:\n     "
                             + err.splitlines()[-1][:150])
                    problems.append("artspec")
                else:
                    say("✓", "artspec: server chạy thử OK")
            servers["artspec"] = entry
    except (FileNotFoundError, subprocess.CalledProcessError) as e:
        print(f"\nLỖI: {e}")
        return 2

    cfg = a.config or config_path()
    print(f"\nFile cấu hình: {cfg}")
    print(json.dumps({"mcpServers": servers}, indent=2, ensure_ascii=False))

    if a.dry_run:
        print("\n(--dry-run: chưa ghi gì cả)")
        return 0

    try:
        backup, replaced = merge_config(cfg, servers)
    except RuntimeError as e:
        print(f"\nLỖI: {e}")
        return 2

    print()
    if backup:
        say("✓", f"đã sao lưu cấu hình cũ: {backup.name}")
    if replaced:
        say("!", f"đã thay mục cùng tên: {', '.join(replaced)}")
    say("✓", f"đã ghi {len(servers)} server vào cấu hình")

    print("\n" + "=" * 66)
    print("CÒN LẠI PHẢI LÀM BẰNG TAY")
    print("=" * 66)
    steps = [("THOÁT HẲN Claude Desktop rồi mở lại.",
              ["Bấm X đóng cửa sổ KHÔNG đủ — cấu hình chỉ đọc lúc khởi động.",
               "Windows: chuột phải icon ở khay hệ thống → Quit",
               "Mac:     Cmd + Q"])]
    if "MayaMCP" in servers:
        steps.append(("Mở Maya. Lần đầu kết nối Maya sẽ hiện hộp thoại bảo mật",
                      ["→ bấm 'Allow All'. Phải làm lại MỖI PHIÊN Maya."]))
    if "MayaMCP" in servers:
        steps.append(("Trong Maya, mở cổng lệnh — CHẠY MỖI PHIÊN MAYA:", [
            'cmds.commandPort(name=":50007", sourceType="mel")',
            "",
            "Dán dòng trên vào Script Editor tab Python.",
            "MayaMCP dùng đúng cổng 50007 (ghi cứng trong code, không đổi được),",
            "và phải là sourceType='mel' vì nó bọc Python trong lệnh MEL."]))
    steps.append(("Hỏi thử trong Claude: \"bạn có tool nào?\"", []))
    if "artspec" in servers:
        steps.append(("Test chống bịa (BẮT BUỘC): hỏi một điều techspec KHÔNG quy định,",
                      ["vd \"số vertex tối đa cho decal là bao nhiêu?\".",
                       "Trả lời đúng phải là \"techspec không có quy định này\"."]))
    for i, (head, rest) in enumerate(steps, 1):
        print(f"{'' if i == 1 else chr(10)}{i}. {head}")
        for line in rest:
            print(f"   {line}")
    if problems:
        print("=" * 66)
        print(f"⚠  {', '.join(problems)} cài xong nhưng CHẠY THỬ KHÔNG QUA.")
        print("   Cấu hình vẫn được ghi, nhưng Claude sẽ không thấy tool.")
        print("   Gửi thông báo lỗi phía trên cho người hỗ trợ.")
        print()
    return 1 if problems else 0


if __name__ == "__main__":
    raise SystemExit(main())
