"""Chạy BÊN TRONG Maya — gọi validator của studio rồi ghi kết quả ra JSON.

Dùng chung cho cả hai adapter (`maya_batch` chạy qua mayapy, `maya_port` gửi
qua commandPort tới Maya đang mở).

Không import gì của artspec, để bỏ vào Maya chạy độc lập được.

Vì sao ghi ra FILE thay vì in ra màn hình: Maya in rất nhiều thứ linh tinh lẫn
vào stdout, và commandPort không trả về được kết quả của code nhiều dòng. Ghi
file rồi đọc từ ngoài là cách duy nhất chắc chắn.
"""
from __future__ import annotations

import json
import traceback


def _as_rows(raw):
    """Chuẩn hoá thứ validator trả về thành danh sách dict.

    Chấp nhận: list[dict] · list[object có thuộc tính] · dict chứa một danh sách
    · object có .findings/.issues/.errors
    """
    for attr in ("findings", "issues", "errors", "results"):
        if hasattr(raw, attr):
            raw = getattr(raw, attr)
            break
    if isinstance(raw, dict):
        for key in ("findings", "issues", "errors", "results"):
            if isinstance(raw.get(key), list):
                raw = raw[key]
                break
        else:
            raw = [raw]
    if not isinstance(raw, (list, tuple)):
        return []
    rows = []
    for item in raw:
        if isinstance(item, dict):
            rows.append(item)
        elif hasattr(item, "__dict__"):
            rows.append({k: v for k, v in vars(item).items()
                         if not k.startswith("_")})
        else:
            rows.append({"code": str(item)})
    return rows


def _pick(row, name, default=""):
    val = row.get(name, default)
    if isinstance(val, (list, tuple)):
        return ", ".join(str(v) for v in val)
    return "" if val is None else str(val)


def run(spec):
    """spec: dict với các khoá scene, module, function, kwargs, fields, out."""
    result = {"findings": [], "error": None}
    try:
        if spec.get("scene"):
            from maya import cmds
            cmds.file(spec["scene"], open=True, force=True,
                      ignoreVersion=True, prompt=False)

        import importlib
        mod = importlib.import_module(spec["module"])
        fn = getattr(mod, spec["function"])
        raw = fn(**(spec.get("kwargs") or {}))

        f = spec.get("fields") or {}
        for row in _as_rows(raw):
            code = _pick(row, f.get("code", "code"))
            if not code:
                continue
            entry = {"code": code,
                     "object": _pick(row, f.get("object", "object")),
                     "detail": _pick(row, f.get("detail", "detail"))}
            if f.get("severity"):
                entry["severity"] = _pick(row, f["severity"]).lower()
            result["findings"].append(entry)
    except Exception:                                    # noqa: BLE001
        result["error"] = traceback.format_exc()

    with open(spec["out"], "w", encoding="utf-8") as fh:
        json.dump(result, fh, ensure_ascii=False)
    return result


def run_from_file(args_path):
    """Điểm vào khi gọi qua commandPort — đọc tham số từ file JSON."""
    with open(args_path, encoding="utf-8") as fh:
        return run(json.load(fh))


if __name__ == "__main__":
    import sys
    if "--args" in sys.argv:
        spec_path = sys.argv[sys.argv.index("--args") + 1]
        with open(spec_path, encoding="utf-8") as fh:
            spec = json.load(fh)
        try:
            import maya.standalone
            maya.standalone.initialize(name="python")
            run(spec)
        finally:
            try:
                import maya.standalone
                maya.standalone.uninitialize()
            except Exception:                            # noqa: BLE001
                pass
