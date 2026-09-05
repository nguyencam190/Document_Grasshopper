"""Hai adapter cho validator chạy bên trong Maya.

    maya_batch  — mở Maya không giao diện bằng mayapy, mở scene, chạy validator.
                  Dùng cho: Lead kiểm file hoạ sĩ nộp, batch chạy đêm.
                  Chậm (30 giây – vài phút mỗi scene) và CHIẾM MỘT LICENSE.

    maya_port   — gửi lệnh tới Maya ĐANG MỞ qua commandPort.
                  Dùng cho: hoạ sĩ kiểm scene đang làm dở.
                  Nhanh (scene đã nạp sẵn), không tốn thêm license.
                  Đọc BAO_MAT.md §5 trước khi bật commandPort.

Cả hai dùng chung `maya_runner.py` và cùng một cách khai báo, nên đổi qua lại
chỉ là đổi chữ `type`.
"""
from __future__ import annotations

import json
import shlex
import socket
import subprocess
import tempfile
from pathlib import Path
from typing import Any

from . import ExternalFinding, adapter

RUNNER = Path(__file__).resolve().parent / "maya_runner.py"
DEFAULT_TIMEOUT = 600          # mở một scene xe có thể mất vài phút


def _spec_for_runner(spec: dict[str, Any], path: Path, out: Path,
                     with_scene: bool) -> dict[str, Any]:
    for key in ("module", "function"):
        if key not in spec:
            raise RuntimeError(f"thiếu '{key}' — cần biết gọi hàm nào trong Maya")
    return {
        "scene": str(path) if with_scene else None,
        "module": spec["module"],
        "function": spec["function"],
        "kwargs": spec.get("kwargs") or {},
        "fields": spec.get("fields") or {},
        "out": str(out),
    }


def _to_findings(name: str, out: Path) -> list[ExternalFinding]:
    if not out.is_file():
        raise RuntimeError("Maya không ghi ra file kết quả — xem log Maya. "
                           "Thường do sai tên module/function, hoặc scene không mở được.")
    data = json.loads(out.read_text(encoding="utf-8"))
    if data.get("error"):
        raise RuntimeError("validator trong Maya ném lỗi:\n"
                           + data["error"].strip().splitlines()[-1])
    return [ExternalFinding(source=name, code=r["code"], object=r.get("object", ""),
                            detail=r.get("detail", ""),
                            severity_hint=r.get("severity"))
            for r in data.get("findings", [])]


@adapter("maya_batch")
def maya_batch(spec: dict[str, Any], path: Path) -> list[ExternalFinding]:
    """Chạy validator qua mayapy, tự mở scene.

        - name: maya_val
          type: maya_batch
          mayapy: "C:/Program Files/Autodesk/Maya2026/bin/mayapy.exe"
          module: studio.validate          # module Python của bạn trong Maya
          function: run_all                # hàm trả về danh sách lỗi
          kwargs: {strict: true}           # tham số truyền vào hàm đó (tuỳ chọn)
          fields: {code: type, object: node, detail: message}
          pythonpath: ["D:/pipeline/scripts"]   # nơi chứa module của bạn
          applies_to_ext: [".ma", ".mb"]
          timeout: 600
    """
    mayapy = spec.get("mayapy")
    if not mayapy:
        raise RuntimeError("thiếu 'mayapy' — đường dẫn tới mayapy.exe")

    with tempfile.TemporaryDirectory() as tmp:
        d = Path(tmp)
        out, args = d / "out.json", d / "args.json"
        args.write_text(json.dumps(_spec_for_runner(spec, path, out, True)),
                        encoding="utf-8")
        env = spec.get("env") or {}
        pp = spec.get("pythonpath") or []
        if pp:
            import os
            env = {**os.environ, **env,
                   "PYTHONPATH": os.pathsep.join([*pp, os.environ.get("PYTHONPATH", "")])}
        else:
            import os
            env = {**os.environ, **env}

        proc = subprocess.run([str(mayapy), str(RUNNER), "--args", str(args)],
                              capture_output=True, text=True, env=env,
                              timeout=spec.get("timeout", DEFAULT_TIMEOUT))
        if not out.is_file() and proc.returncode != 0:
            tail = (proc.stderr or proc.stdout).strip().splitlines()[-3:]
            raise RuntimeError(f"mayapy thoát mã {proc.returncode}: " + " | ".join(tail))
        return _to_findings(spec["name"], out)


@adapter("maya_port")
def maya_port(spec: dict[str, Any], path: Path) -> list[ExternalFinding]:
    """Gửi lệnh tới Maya ĐANG MỞ qua commandPort. Kiểm scene đang mở sẵn.

        - name: maya_live
          type: maya_port
          port: 7001                       # phải khớp cmds.commandPort(name=":7001")
          module: studio.validate
          function: run_all
          fields: {code: type, object: node, detail: message}
          open_scene: false                # true = bảo Maya mở file, mất scene đang làm

    Mặc định `open_scene: false` — kiểm ĐÚNG scene hoạ sĩ đang mở, không đụng
    tới nó. Đặt true thì Maya sẽ mở file khác đè lên, thường không phải điều
    bạn muốn.
    """
    port = int(spec.get("port", 7001))
    host = spec.get("host", "127.0.0.1")
    if host not in ("127.0.0.1", "localhost", "::1"):
        raise RuntimeError(
            f"từ chối nối tới '{host}'. commandPort không có xác thực — chỉ dùng "
            f"localhost. Xem BAO_MAT.md §5")

    # Ghi ra thư mục tạm KHÔNG tự xoá: Maya là tiến trình khác, cần đọc lại sau.
    d = Path(tempfile.mkdtemp(prefix="artspec_maya_"))
    try:
        out, args = d / "out.json", d / "args.json"
        args.write_text(json.dumps(
            _spec_for_runner(spec, path, out, bool(spec.get("open_scene")))),
            encoding="utf-8")

        # Một dòng duy nhất: commandPort không trả về được kết quả của code
        # nhiều dòng, nên runner ghi ra file và ta đọc file đó.
        cmd = ("import sys; sys.path.insert(0, {rd!r}); "
               "import maya_runner; maya_runner.run_from_file({af!r})").format(
                   rd=str(RUNNER.parent), af=str(args))

        with socket.create_connection((host, port),
                                      timeout=spec.get("timeout", 60)) as sock:
            sock.sendall(cmd.encode("utf-8") + b"\n")
            sock.settimeout(spec.get("timeout", 60))
            try:
                sock.recv(8192)          # chờ Maya chạy xong; nội dung không dùng
            except socket.timeout:
                raise RuntimeError("Maya không phản hồi trong thời gian cho phép")
        return _to_findings(spec["name"], out)
    except (ConnectionRefusedError, OSError) as e:
        raise RuntimeError(
            f"không nối được tới Maya ở {host}:{port} — {e}. "
            f"Trong Maya chạy: cmds.commandPort(name=':{port}', sourceType='python')"
        ) from e
    finally:
        import shutil
        shutil.rmtree(d, ignore_errors=True)
