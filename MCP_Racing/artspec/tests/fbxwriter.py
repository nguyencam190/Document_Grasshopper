"""Ghi FBX nhị phân — CHỈ dùng để tạo fixture cho test.

Không phải một phần của artspec. Mục đích: kiểm chứng phần đọc container của
readers/fbxfile.py (offset, kiểu property, mảng nén zlib, node lồng nhau).
"""
from __future__ import annotations

import struct
import zlib
from typing import Any

MAGIC = b"Kaydara FBX Binary  \x00\x1a\x00"


def prop(v: Any, *, kind: str | None = None, compress: bool = False) -> bytes:
    if kind == "I" or (kind is None and isinstance(v, int) and -2**31 <= v < 2**31):
        return b"I" + struct.pack("<i", v)
    if kind == "L" or (kind is None and isinstance(v, int)):
        return b"L" + struct.pack("<q", v)
    if kind == "D" or (kind is None and isinstance(v, float)):
        return b"D" + struct.pack("<d", v)
    if kind == "S" or (kind is None and isinstance(v, str)):
        b = v.encode("utf-8")
        return b"S" + struct.pack("<I", len(b)) + b
    if kind in ("d", "i"):
        fmt = {"d": "d", "i": "i"}[kind]
        raw = struct.pack("<" + fmt * len(v), *v)
        if compress:
            packed = zlib.compress(raw)
            return kind.encode() + struct.pack("<III", len(v), 1, len(packed)) + packed
        return kind.encode() + struct.pack("<III", len(v), 0, len(raw)) + raw
    raise TypeError(f"không encode được {v!r} (kind={kind})")


class N:
    def __init__(self, name: str, props: list[bytes] | None = None,
                 children: list["N"] | None = None):
        self.name = name
        self.props = props or []
        self.children = children or []

    def encode(self, start: int) -> bytes:
        head = 4 + 4 + 4 + 1 + len(self.name)
        plist = b"".join(self.props)
        body_start = start + head + len(plist)
        kids = b""
        for c in self.children:
            chunk = c.encode(body_start + len(kids))
            kids += chunk
        if self.children:
            kids += b"\x00" * 13
        end = body_start + len(kids)
        return (struct.pack("<III", end, len(self.props), len(plist))
                + bytes([len(self.name)]) + self.name.encode() + plist + kids)


def write(path: str, top: list[N], version: int = 7400) -> str:
    out = MAGIC + struct.pack("<I", version)
    for n in top:
        out += n.encode(len(out))
    out += b"\x00" * 13
    with open(path, "wb") as fh:
        fh.write(out)
    return path


def p70(entries: list[tuple[str, list[float]]]) -> N:
    rows = []
    for key, vals in entries:
        props = [prop(key, kind="S"), prop("Lcl Translation", kind="S"),
                 prop("", kind="S"), prop("A", kind="S")]
        props += [prop(float(v), kind="D") for v in vals]
        rows.append(N("P", props))
    return N("Properties70", [], rows)
