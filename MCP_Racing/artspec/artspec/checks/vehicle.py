"""Check ĐẶC THÙ của dự án (Tier B).

Đây là chỗ để thêm luật mà YAML thuần không diễn tả được. Mỗi hàm:
  - nhận (rule, metrics), đọc `rule.check["params"]`
  - trả CheckOutcome với `locations` chỉ ĐÚNG đối tượng hoạ sĩ phải mở ra sửa
  - raise CheckError nếu metrics thiếu field (lỗi hệ thống, không phải lỗi hoạ sĩ)

Quy ước trục dùng ở đây: Y = lên (độ cao), X = trái/phải, Z = trước/sau (Maya).
Nếu dự án dùng quy ước khác thì sửa hằng số AXIS_* bên dưới.
"""
from __future__ import annotations

import re
from typing import Any

from ..model import CheckOutcome, Location, Rule
from . import custom_check
from .builtin import CheckError, items_for, _label

AXIS_SIDE = 0    # X — trái/phải
AXIS_UP = 1      # Y — độ cao
AXIS_FWD = 2     # Z — trước/sau


@custom_check("vehicle.transform_frozen")
def transform_frozen(rule: Rule, metrics: dict[str, Any]) -> CheckOutcome:
    eps = float(rule.check.get("params", {}).get("epsilon", 1e-3))
    bad: list[Location] = []
    for it in items_for(rule, metrics):
        name = _label(it)
        scale = it.get("scale")
        rot = it.get("rotation")
        if scale is None or rot is None:
            raise CheckError(f"{rule.id}: '{name}' thiếu 'scale' hoặc 'rotation' trong metrics",
                             metric="meshes[].scale")
        if any(s < 0 for s in scale):
            bad.append(Location(name, f"scale ÂM {tuple(scale)} — mesh đang bị lộn mặt trong ra ngoài"))
        elif any(abs(s - 1.0) > eps for s in scale):
            bad.append(Location(name, f"scale = {tuple(scale)}, phải là (1, 1, 1)"))
        if any(abs(r) > eps for r in rot):
            bad.append(Location(name, f"rotation = {tuple(rot)}, phải là (0, 0, 0)"))
    return CheckOutcome(ok=not bad, locations=bad,
                        expected="scale = (1,1,1) và rotation = (0,0,0)",
                        actual=f"{len(bad)} vấn đề transform" if bad else "đã freeze")


@custom_check("vehicle.hard_edges_are_uv_seams")
def hard_edges_are_uv_seams(rule: Rule, metrics: dict[str, Any]) -> CheckOutcome:
    """Mọi hard edge phải là UV seam (chiều ngược lại không bắt buộc)."""
    max_report = int(rule.check.get("params", {}).get("max_report", 8))
    bad: list[Location] = []
    total = 0
    for it in items_for(rule, metrics):
        name = _label(it)
        if "hard_edges" not in it or "uv_seam_edges" not in it:
            raise CheckError(
                f"{rule.id}: '{name}' thiếu 'hard_edges' hoặc 'uv_seam_edges'. "
                f"Collector phải xuất danh sách id cạnh — xem collectors/README.md",
                metric="hard_edges")
        orphans = sorted(set(it["hard_edges"]) - set(it["uv_seam_edges"]))
        total += len(orphans)
        if orphans:
            shown = ", ".join(f"e[{e}]" for e in orphans[:max_report])
            more = f" … và {len(orphans) - max_report} cạnh nữa" if len(orphans) > max_report else ""
            bad.append(Location(name, f"{len(orphans)} hard edge không phải seam: {shown}{more}"))
    return CheckOutcome(ok=not bad, locations=bad,
                        expected="mọi hard edge đều là UV seam",
                        actual=f"{total} cạnh vi phạm trên {len(bad)} mesh" if bad else "đạt")


@custom_check("vehicle.texture_color_space")
def texture_color_space(rule: Rule, metrics: dict[str, Any]) -> CheckOutcome:
    """Color space suy ra từ hậu tố tên file — quy ước riêng của dự án."""
    smap: dict[str, str] = rule.check.get("params", {}).get("suffix_map", {})
    if not smap:
        raise CheckError(f"{rule.id}: params.suffix_map trống")
    bad: list[Location] = []
    unknown: list[str] = []
    for it in items_for(rule, metrics):
        name = _label(it)
        suffix = next((s for s in smap if name.endswith(s)), None)
        if suffix is None:
            unknown.append(name)
            continue
        want = smap[suffix]
        got = it.get("color_space")
        if got is None:
            raise CheckError(f"{rule.id}: texture '{name}' thiếu 'color_space'",
                             metric="textures[].color_space")
        if str(got).lower() != want.lower():
            bad.append(Location(name, f"color space = {got}, hậu tố {suffix} yêu cầu {want}"))
    note = ""
    if unknown:
        note = ("Không nhận ra hậu tố của: " + ", ".join(unknown[:5]) +
                " — đặt tên theo quy ước hoặc bổ sung vào params.suffix_map.")
    return CheckOutcome(ok=not bad, locations=bad, note=note,
                        expected=" · ".join(f"{k} → {v}" for k, v in smap.items()),
                        actual=f"{len(bad)} texture sai color space" if bad else "đạt")


@custom_check("vehicle.texture_size")
def texture_size(rule: Rule, metrics: dict[str, Any]) -> CheckOutcome:
    p = rule.check.get("params", {})
    max_size = int(p.get("max_size", 4096))
    require_square = bool(p.get("require_square", False))
    bad: list[Location] = []
    for it in items_for(rule, metrics):
        name = _label(it)
        w, h = it.get("width"), it.get("height")
        if w is None or h is None:
            raise CheckError(f"{rule.id}: texture '{name}' thiếu 'width'/'height'",
                             metric="textures[].width / height")
        for axis, v in (("width", w), ("height", h)):
            if v <= 0 or (v & (v - 1)) != 0:
                bad.append(Location(name, f"{axis} = {v} không phải luỹ thừa của 2"))
            elif v > max_size:
                bad.append(Location(name, f"{axis} = {v} vượt giới hạn {max_size}"))
        if require_square and w != h:
            bad.append(Location(name, f"không vuông ({w}×{h})"))
    return CheckOutcome(ok=not bad, locations=bad,
                        expected=f"luỹ thừa của 2, ≤ {max_size}" + (", vuông" if require_square else ""),
                        actual=f"{len(bad)} vấn đề kích thước" if bad else "đạt")


@custom_check("vehicle.wheel_bone_layout")
def wheel_bone_layout(rule: Rule, metrics: dict[str, Any]) -> CheckOutcome:
    """Bone bánh xe: đúng tên, đối xứng trái/phải, cùng độ cao theo cặp trục."""
    p = rule.check.get("params", {})
    required: list[str] = list(p.get("required_bones", []))
    mirror_tol = float(p.get("mirror_tolerance_cm", 0.5))
    height_tol = float(p.get("height_tolerance_cm", 0.5))
    forbid = p.get("forbid_pattern")

    skel = metrics.get("skeleton")
    if not skel or "bones" not in skel:
        raise CheckError(f"{rule.id}: metrics thiếu 'skeleton.bones'",
                         metric="skeleton.bones[].world_position")
    bones = {b["name"]: b for b in skel["bones"]}
    bad: list[Location] = []

    missing = [n for n in required if n not in bones]
    for n in missing:
        bad.append(Location(n, "bone bắt buộc không tồn tại trong skeleton"))

    if forbid:
        rx = re.compile(forbid)
        for n in bones:
            if rx.match(n):
                bad.append(Location(n, "còn sót tên bone mặc định của DCC"))

    def pos(n: str) -> list[float] | None:
        b = bones.get(n)
        if not b:
            return None
        wp = b.get("world_position")
        if wp is None:
            raise CheckError(f"{rule.id}: bone '{n}' thiếu 'world_position'",
                             metric="skeleton.bones[].world_position")
        return wp

    # Cặp trái/phải phải đối xứng qua trục giữa, và cùng độ cao.
    for left, right, label in (("WHL_FL", "WHL_FR", "trước"), ("WHL_RL", "WHL_RR", "sau")):
        if left not in required or right not in required:
            continue
        pl, pr = pos(left), pos(right)
        if pl is None or pr is None:
            continue
        dx = abs(pl[AXIS_SIDE] + pr[AXIS_SIDE])   # đối xứng ⇒ x_trái ≈ −x_phải
        if dx > mirror_tol:
            bad.append(Location(f"{left} / {right}",
                                f"cặp bánh {label} không đối xứng: lệch {dx:.2f} cm "
                                f"(cho phép ≤ {mirror_tol} cm)"))
        dy = abs(pl[AXIS_UP] - pr[AXIS_UP])
        if dy > height_tol:
            bad.append(Location(f"{left} / {right}",
                                f"cặp bánh {label} lệch độ cao {dy:.2f} cm "
                                f"(cho phép ≤ {height_tol} cm)"))
    return CheckOutcome(ok=not bad, locations=bad,
                        expected=f"{', '.join(required)} — đối xứng ±{mirror_tol} cm, "
                                 f"cùng độ cao ±{height_tol} cm",
                        actual=f"{len(bad)} vấn đề" if bad else "đạt")
