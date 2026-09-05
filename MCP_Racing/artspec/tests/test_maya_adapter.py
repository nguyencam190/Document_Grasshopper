"""Kiểm hai adapter Maya bằng Maya GIẢ (mayapy giả + commandPort giả).

Kiểm chứng được: dựng tham số, gọi validator, chuẩn hoá đủ mọi kiểu trả về,
đọc kết quả, xử lý lỗi, chặn host lạ.

KHÔNG kiểm chứng được: hành vi Maya thật (mở scene, khởi tạo standalone, cách
commandPort thật trả lời). Phải chạy thử trên Maya thật trước khi tin.
"""
from __future__ import annotations

import json
import socket
import sys
import tempfile
import textwrap
import threading
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from artspec.adapters import ExternalFinding, maya as maya_ad  # noqa: E402

RUNNER_DIR = str(Path(maya_ad.RUNNER).parent)

# Validator giả của studio — trả về 4 kiểu dữ liệu khác nhau để thử chuẩn hoá.
STUDIO = '''
class Issue:                       # kiểu object có thuộc tính
    def __init__(s, t, n, m): s.type, s.node, s.message = t, n, m

def as_dicts(**kw):
    return [{"type": "TRICOUNT_OVER", "node": "SM_Body", "message": "132450/96000"},
            {"type": "UV_OVERLAP", "node": "SM_Body", "message": "3 shell"}]

def as_objects(**kw):
    return [Issue("NGON_FOUND", "SM_Hood", "5 n-gon")]

def as_wrapped(**kw):
    return {"issues": [{"type": "FLIPPED", "node": "SM_Door", "message": "2 mặt"}]}

def with_kwargs(strict=False, **kw):
    return [{"type": "STRICT_ON" if strict else "STRICT_OFF", "node": "x", "message": ""}]

def empty(**kw):
    return []

def boom(**kw):
    raise ValueError("validator của studio bị lỗi ở đây")
'''

# Gói maya giả — chỉ đủ để runner import và gọi.
MAYA_INIT = ""
MAYA_STANDALONE = "def initialize(name=None): pass\ndef uninitialize(): pass\n"
MAYA_CMDS = '''
opened = []
def file(path, **kw):
    opened.append(path)
    return path
'''

FAKE_MAYAPY = '''
import runpy, sys
sys.path.insert(0, {fake!r})
sys.path.insert(0, {studio!r})
runner = sys.argv[1]
sys.argv = sys.argv[1:]
runpy.run_path(runner, run_name="__main__")
'''


def make_env(d: Path) -> tuple[Path, Path]:
    fake = d / "fakemaya"
    (fake / "maya").mkdir(parents=True)
    (fake / "maya" / "__init__.py").write_text(MAYA_INIT, encoding="utf-8")
    (fake / "maya" / "standalone.py").write_text(MAYA_STANDALONE, encoding="utf-8")
    (fake / "maya" / "cmds.py").write_text(MAYA_CMDS, encoding="utf-8")

    studio = d / "studiolib"
    (studio / "studio").mkdir(parents=True)
    (studio / "studio" / "__init__.py").write_text("", encoding="utf-8")
    (studio / "studio" / "validate.py").write_text(textwrap.dedent(STUDIO), encoding="utf-8")

    mayapy = d / "fake_mayapy.py"
    mayapy.write_text(FAKE_MAYAPY.format(fake=str(fake), studio=str(studio)),
                      encoding="utf-8")
    return mayapy, studio


def batch_spec(mayapy: Path, fn: str, **extra) -> dict:
    return {"name": "maya_val", "type": "maya_batch",
            "mayapy": f"{sys.executable}",
            "module": "studio.validate", "function": fn,
            "fields": {"code": "type", "object": "node", "detail": "message"},
            "_wrapper": str(mayapy), **extra}


def run_batch(mayapy: Path, spec: dict, scene: Path):
    """Gọi adapter nhưng chèn wrapper mayapy giả vào trước runner."""
    real = maya_ad.subprocess.run

    def patched(cmd, **kw):
        return real([cmd[0], spec["_wrapper"], *cmd[1:]], **kw)

    maya_ad.subprocess.run = patched
    try:
        return maya_ad.maya_batch(spec, scene)
    finally:
        maya_ad.subprocess.run = real


class FakePort(threading.Thread):
    """commandPort giả: nhận một dòng code, exec, trả 'ok'."""

    def __init__(self, fake: Path, studio: Path):
        super().__init__(daemon=True)
        self.sock = socket.socket()
        self.sock.bind(("127.0.0.1", 0))
        self.sock.listen(1)
        self.port = self.sock.getsockname()[1]
        self.paths = [str(fake), str(studio)]
        self.error = None

    def run(self):
        conn, _ = self.sock.accept()
        with conn:
            code = conn.recv(65536).decode("utf-8").strip()
            for p in self.paths:
                if p not in sys.path:
                    sys.path.insert(0, p)
            try:
                exec(compile(code, "<port>", "exec"), {})
            except Exception as e:            # noqa: BLE001
                self.error = repr(e)
            conn.sendall(b"ok\n")


def run_checks() -> None:
    c: list[tuple[str, bool, str]] = []
    with tempfile.TemporaryDirectory() as t:
        d = Path(t)
        mayapy, studio = make_env(d)
        scene = d / "SUV_A.mb"
        scene.write_bytes(b"fake")

        # ── maya_batch: các kiểu trả về khác nhau
        out = run_batch(mayapy, batch_spec(mayapy, "as_dicts"), scene)
        c += [
            ("batch: đọc list[dict]", len(out) == 2, str(len(out))),
            ("batch: giữ đúng mã lỗi",
             [f.code for f in out] == ["TRICOUNT_OVER", "UV_OVERLAP"], ""),
            ("batch: giữ đối tượng và chi tiết",
             out[0].object == "SM_Body" and "132450" in out[0].detail, str(out[0])),
            ("batch: gắn đúng tên nguồn", out[0].source == "maya_val", ""),
        ]
        o2 = run_batch(mayapy, batch_spec(mayapy, "as_objects"), scene)
        c.append(("batch: đọc được list object (không phải dict)",
                  len(o2) == 1 and o2[0].code == "NGON_FOUND", str(o2)))
        o3 = run_batch(mayapy, batch_spec(mayapy, "as_wrapped"), scene)
        c.append(("batch: đọc được dict bọc ngoài {'issues': [...]}",
                  len(o3) == 1 and o3[0].code == "FLIPPED", str(o3)))
        o4 = run_batch(mayapy, batch_spec(mayapy, "with_kwargs",
                                          kwargs={"strict": True}), scene)
        c.append(("batch: truyền được kwargs vào hàm",
                  o4 and o4[0].code == "STRICT_ON", str(o4)))
        c.append(("batch: validator sạch → danh sách rỗng",
                  run_batch(mayapy, batch_spec(mayapy, "empty"), scene) == [], ""))

        try:
            run_batch(mayapy, batch_spec(mayapy, "boom"), scene)
            c.append(("batch: validator ném lỗi → báo rõ", False, "không raise"))
        except RuntimeError as e:
            c.append(("batch: validator ném lỗi → nêu nguyên văn",
                      "lỗi ở đây" in str(e), str(e)[:60]))
        try:
            run_batch(mayapy, batch_spec(mayapy, "khong_co_ham_nay"), scene)
            c.append(("batch: sai tên hàm → báo rõ", False, "không raise"))
        except RuntimeError as e:
            c.append(("batch: sai tên hàm → báo rõ",
                      "khong_co_ham_nay" in str(e) or "AttributeError" in str(e),
                      str(e)[:60]))
        try:
            maya_ad.maya_batch({"name": "x", "module": "m", "function": "f"}, scene)
            c.append(("batch: thiếu mayapy → báo rõ", False, "không raise"))
        except RuntimeError as e:
            c.append(("batch: thiếu mayapy → báo rõ", "mayapy" in str(e), ""))

        # ── maya_port
        srv = FakePort(d / "fakemaya", studio)
        srv.start()
        spec = {"name": "maya_live", "type": "maya_port", "port": srv.port,
                "module": "studio.validate", "function": "as_dicts",
                "fields": {"code": "type", "object": "node", "detail": "message"}}
        got = maya_ad.maya_port(spec, scene)
        c += [
            ("port: nhận được kết quả từ Maya đang mở", len(got) == 2, str(len(got))),
            ("port: không có lỗi phía Maya", srv.error is None, str(srv.error)),
            ("port: mặc định KHÔNG mở đè scene đang làm",
             len(got) == 2 and got[0].code == "TRICOUNT_OVER", ""),
        ]
        try:
            maya_ad.maya_port({**spec, "host": "192.168.1.50"}, scene)
            c.append(("port: chặn host ngoài localhost", False, "không raise"))
        except RuntimeError as e:
            c.append(("port: chặn host ngoài localhost, dẫn BAO_MAT",
                      "localhost" in str(e) and "BAO_MAT" in str(e), str(e)[:60]))
        try:
            maya_ad.maya_port({**spec, "port": 1}, scene)
            c.append(("port: Maya chưa bật cổng → hướng dẫn bật", False, "không raise"))
        except RuntimeError as e:
            c.append(("port: Maya chưa bật cổng → hướng dẫn lệnh bật",
                      "commandPort" in str(e), str(e)[:60]))

    fails = [x for x in c if not x[1]]
    for name, ok, extra in c:
        print(f"  {'✓' if ok else '✗'} {name}" + (f"   [{extra}]" if not ok and extra else ""))
    print(f"\n{len(c) - len(fails)}/{len(c)} pass")
    if fails:
        raise SystemExit(1)


if __name__ == "__main__":
    run_checks()
