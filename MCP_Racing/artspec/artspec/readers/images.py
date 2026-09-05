"""Đọc kích thước ảnh từ header — không cần Pillow, không giải nén cả ảnh."""
from __future__ import annotations

import struct
from pathlib import Path

Size = tuple[int, int] | None


def size_of(path: str | Path) -> Size:
    p = Path(path)
    try:
        with open(p, "rb") as fh:
            head = fh.read(32)
            if head[:8] == b"\x89PNG\r\n\x1a\n":
                return struct.unpack(">II", head[16:24])
            if head[:2] == b"\xff\xd8":
                return _jpeg(fh)
            if head[:2] == b"BM":
                fh.seek(18)
                w, h = struct.unpack("<ii", fh.read(8))
                return abs(w), abs(h)
            if head[:4] == b"DDS ":
                h, w = struct.unpack("<II", head[12:20])
                return w, h
            if p.suffix.lower() == ".tga":
                return struct.unpack("<HH", head[12:16])
    except (OSError, struct.error):
        return None
    return None


def _jpeg(fh) -> Size:
    fh.seek(2)
    while True:
        b = fh.read(1)
        if not b:
            return None
        if b != b"\xff":
            continue
        marker = fh.read(1)
        while marker == b"\xff":
            marker = fh.read(1)
        if not marker:
            return None
        m = marker[0]
        if 0xC0 <= m <= 0xCF and m not in (0xC4, 0xC8, 0xCC):
            fh.read(3)
            h, w = struct.unpack(">HH", fh.read(4))
            return w, h
        length = struct.unpack(">H", fh.read(2))[0]
        fh.seek(length - 2, 1)
