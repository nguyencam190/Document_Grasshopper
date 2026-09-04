# artspec — engine kiểm asset 3D + MCP server

Tìm chỗ hoạ sĩ chưa làm đúng techspec, và giải thích cho họ hiểu vì sao và sửa thế nào.

> ⚠️ **Toàn bộ luật trong `rules/` là VÍ DỤ MINH HOẠ CẤU TRÚC, không phải spec của
> dự án bạn.** Mọi con số (120000 tri, 10.24 px/cm, `WHL_FL`…) đều là số bịa để
> chạy thử. Việc đầu tiên phải làm là thay bằng số thật từ techspec.

## Cái này giải quyết gì

| | |
|---|---|
| **Validator** (`engine`) | Bắt lỗi. Chạy được độc lập, không cần AI, không cần MCP |
| **MCP server** (`server.py`) | Giải thích lỗi và trả lời câu hỏi về techspec |

Validator quan trọng hơn và phải làm trước. MCP chỉ thêm phần "vì sao" và "sửa
thế nào" — nó không tìm ra thêm lỗi nào cả.

## Kiến trúc

```
rules/*.yaml ─┐
              ├─> registry ─> engine ─┬─> CLI          (hoạ sĩ chạy lúc export)
waivers/*.yaml┘                       ├─> nightly batch (Lead xem dashboard)
                                      └─> MCP server    (hoạ sĩ hỏi trong chat)

Maya/Max/Blender ──collector──> metrics.json ──┘
```

**Một bộ luật, một engine, nhiều cửa gọi.** Đừng viết luật hai lần — validator
trong Maya và MCP phải đọc chung `rules/`, nếu không hai bên lệch nhau và hoạ sĩ
mất niềm tin vào cả hai.

## Chạy thử

```bash
pip install -r requirements.txt

python -m artspec.cli rules                                   # liệt kê luật
python -m artspec.cli validate samples/metrics_fail.json      # 8 FAIL, 1 WARN, 1 MANUAL
python -m artspec.cli validate samples/metrics_pass.json      # qua gate
python -m artspec.cli validate samples/metrics_fail.json --stage G2   # chỉ gate G2
python -m artspec.cli validate samples/metrics_fail.json --json       # cho script/CI
python -m artspec.cli explain VEH-UV-002
python -m artspec.cli checklist vehicle_exterior G1
```

Exit code: `0` qua gate · `1` có FAIL/ERROR · `2` lỗi cấu hình. Dùng được thẳng
trong hook export hoặc CI.

## Gắn vào Claude Desktop / Claude Code

```json
{
  "mcpServers": {
    "artspec": {
      "command": "python",
      "args": ["-m", "artspec.server"],
      "cwd": "/duong/dan/toi/MCP_Racing/artspec",
      "env": { "ARTSPEC_ROOT": "/duong/dan/toi/MCP_Racing/artspec" }
    }
  }
}
```

Mặc định transport `stdio` (chạy trên máy hoạ sĩ). Khi triển khai chung cho cả
team thì đặt `ARTSPEC_TRANSPORT=streamable-http` — nhưng lúc đó **phải bật OAuth
2.1**, xem `NGHIEN_CUU_MCP_ARTSPEC.md` mục Bảo mật.

Server tự nạp lại khi file YAML đổi — sửa luật không cần restart.

### Tool đang có

| Tool | Trả lời câu hỏi kiểu |
|---|---|
| `check_asset` | "Asset của tôi có đạt không?" |
| `get_budget` | "Xe LOD2 tối đa bao nhiêu tri?" |
| `search_spec` | "Dự án quy định gì về texel density?" |
| `get_rule` | "VEH-UV-002 nói gì?" |
| `get_checklist` | "Trước khi submit tôi phải kiểm gì?" |
| `explain_term` | "Texel density là gì?" |
| `list_rules` / `list_waivers` | Tổng quan cho Lead |

Resource: `spec://index` · `spec://rules/{asset_class}` · `spec://glossary`.
Prompt: `pre_submit_review`.

`instructions` của server cấm model tự suy ra con số khi tool trả `found=false` —
đây là hàng rào chính chống việc AI bịa spec.

## Thêm một luật đặc thù của dự án

| Tier | Ví dụ | Phải làm gì |
|---|---|---|
| **A** — số / regex | tricount, đặt tên, số material | **Chỉ thêm 1 file YAML.** Không đụng code |
| **B** — logic riêng | bố trí bone bánh xe, hard edge ⊂ UV seam | 1 file YAML + 1 hàm `@custom_check(...)` trong `artspec/checks/` |
| **C** — người kiểm | decal có bị che không | 1 file YAML `type: manual` → thành câu hỏi trong checklist |

Không trường hợp nào phải sửa `server.py` hay `engine.py`. Chi tiết field:
[`rules/_SCHEMA.md`](rules/_SCHEMA.md).

## Bốn trạng thái

| | Nghĩa |
|---|---|
| `FAIL` | Chặn gate. Chỉ dành cho luật cứng, máy chắc chắn đúng |
| `WARN` | Cho qua nhưng ghi lại. Dùng khi luật có ngoại lệ hợp lệ, hoặc máy không chắc |
| `MANUAL` | Câu hỏi cho người (Tier C) |
| `ERROR` | **Lỗi của validator**, không phải của hoạ sĩ — luật viết sai hoặc metrics thiếu field. Báo cáo nói rõ điều này để hoạ sĩ không sửa asset theo báo cáo sai |

> Một lần báo sai giết chết mười lần báo đúng. Nghi ngờ thì để `WARN`.

## Waiver

Quy tắc đặc thù hay có ngoại lệ hợp lệ. Không có đường xin chính thức thì hoạ sĩ
sẽ tự lách — bỏ qua validator, submit thẳng, và Lead mất khả năng nhìn thấy vấn đề.

`waivers/waivers.yaml` hạ `FAIL` xuống `WARN` cho đúng cặp (luật, asset), có lý do,
người duyệt và **ngày hết hạn** — hết hạn thì tự mất tác dụng, không cần ai dọn.

## Việc còn phải làm

1. **Thay toàn bộ số trong `rules/` bằng số thật.** Không có bước này thì mọi thứ
   còn lại vô nghĩa.
2. Viết collector FBX/USD (`collectors/`) — nhanh hơn Maya, không tốn license, và
   kiểm đúng cái thật sự đi vào engine.
3. Chạy thử `collectors/maya_collect.py` trên golden asset, đối chiếu vài con số
   bằng tay (script này **chưa được kiểm chứng trên Maya thật**).
4. Nối vào nút Export trong Maya và vào batch chạy đêm.
5. Bổ sung `common_mistakes` cho từng luật sau mỗi tháng đọc Error Log.

## Cấu trúc

```
rules/<class>/*.yaml   luật — thứ bạn phải điền
checklists/*.yaml      checklist theo gate G0-G3
glossary/*.yaml        thuật ngữ theo cách dự án hiểu
waivers/*.yaml         ngoại lệ đã duyệt
samples/*.json         metrics mẫu để chạy thử
collectors/            sinh metrics.json từ DCC
artspec/               engine — hiếm khi phải sửa
  registry.py  đọc & kiểm tính hợp lệ của luật
  checks/      builtin.py (Tier A) · vehicle.py (Tier B, đặc thù dự án)
  engine.py    chạy luật, áp waiver
  render.py    thông điệp lỗi 5 phần
  cli.py       giao diện dòng lệnh
  server.py    MCP server
```
