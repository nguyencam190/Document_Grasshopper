# Collector — hợp đồng dữ liệu giữa DCC và engine

Engine `artspec` **không đọc file Maya/Max/Blender**. Nó đọc một file `metrics.json`
do collector sinh ra. Lý do:

- Mở một scene xe hoàn chỉnh bằng `mayapy` mất 30 giây đến vài phút và **chiếm một
  license seat** — không thể để hoạ sĩ chờ ngần ấy mỗi lần hỏi một câu.
- Tách như vậy thì cùng một engine chạy được từ Maya, từ 3ds Max, từ Blender, hoặc
  từ file FBX/USD đã export — chỉ cần viết collector mới, không đụng vào luật.

## Sơ đồ

```
Maya / Max / Blender ──collector──> metrics.json ──engine──> report
                                          │
                                          └──> MCP server (check_asset)
```

## Hợp đồng `metrics.json`

Field vô hướng ở gốc (`platform`, `unit`…) được gộp vào ngữ cảnh khi khớp `where`
của luật, nên luật viết `where: {lod: 0, platform: pc}` là hợp lệ.

```jsonc
{
  "asset": "SUV_A",                  // bắt buộc — dùng để tra waiver
  "asset_class": "vehicle_exterior", // bắt buộc — quyết định áp bộ luật nào
  "source_file": "SUV_A.mb",
  "dcc": "maya-2026",
  "unit": "cm",
  "platform": "pc",

  "meshes": [{
    "name": "SM_SuvA_Body_LOD0",
    "lod": 0,
    "triangle_count": 132450,
    "scale": [1, 1, 1],
    "rotation": [0, 0, 0],
    "uv_sets": ["map1"],
    "material_slots": 6,
    "texel_density_px_cm": 10.2,
    "hard_edges": [12, 44, 45],      // id cạnh hard
    "uv_seam_edges": [12, 44]        // id cạnh là UV border
  }],

  "textures": [{
    "name": "T_SuvA_N",
    "width": 4096, "height": 4096,
    "color_space": "Linear"
  }],

  "skeleton": {
    "max_influences_per_vertex": 4,
    "bones": [{"name": "WHL_FL", "world_position": [-78.0, 34.0, 132.0]}]
  }
}
```

**Nguyên tắc: thiếu field thì báo ERROR, không đoán.** Engine sẽ trả finding
`status=ERROR` ghi rõ "lỗi của validator, không phải lỗi của hoạ sĩ" và chỉ đúng
field đang thiếu. Đừng bao giờ để collector điền giá trị mặc định thay cho số thật —
một con số bịa còn tệ hơn một lỗi báo rõ ràng.

## Thêm collector mới

Chỉ cần xuất đúng JSON trên. Không phải import gì từ `artspec`.
Gợi ý thứ tự ưu tiên:

1. **FBX/USD** (`collectors/` — chưa viết) — nhanh nhất, không cần license, và
   kiểm đúng cái thật sự đi vào engine. **Nên làm trước.**
2. **Maya** (`maya_collect.py`) — bắt lỗi sớm hơn, ngay lúc hoạ sĩ bấm Export.
3. **UE5** — kiểm sau khi import (compression, LOD, collision, lightmap).
