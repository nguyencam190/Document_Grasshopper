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

## Lead kiểm file hoạ sĩ nộp — không cần mở file 3D

```bash
python -m artspec.cli check  submit/vehicle_exterior/SUV_A.fbx
python -m artspec.cli inbox  submit/            # quét cả lô, bảng tóm tắt
```

```
FILE                    KẾT QUẢ          FAIL  WARN  HỎI   BỎ   LUẬT VI PHẠM
──────────────────────────────────────────────────────────────────────────────
SM_SuvA_Body_LOD0.fbx   ⛔ KHÔNG QUA         2     1    1    3   VEH-TRI-001, VEH-XFM-001
SM_SuvA_Glass_LOD0.fbx  ✅ QUA               0     0    1    3
──────────────────────────────────────────────────────────────────────────────
2 file · 1 cần xử lý · 1 qua gate
```

Trong Claude: *"kiểm giúp tôi thư mục submit hôm nay"* → tool `check_inbox`;
*"file SUV_A sai chỗ nào"* → tool `check_file` trả báo cáo đầy đủ kèm cách sửa.

### Định dạng đọc trực tiếp được

| Định dạng | Đọc được gì | Không có gì |
|---|---|---|
| **`.fbx`** (nhị phân) | tricount, transform, UV set, material slot, custom normal, tên + vị trí bone, tên texture | texel density, hard edge / UV seam, color space |
| **`.gltf` / `.glb`** | như trên, thêm kích thước texture nếu file ảnh nằm cạnh | như trên |
| **`.obj`** | tricount, tên, số material | transform, bone, color space |
| **`.json`** | đầy đủ — do collector Maya sinh ra | — |

`.ma` / `.mb` **không đọc trực tiếp**: `.mb` là nhị phân đóng của Autodesk, `.ma`
là script MEL nên tự parse rất dễ sai. Reader từ chối kèm 2 hướng xử lý: yêu cầu
hoạ sĩ nộp thêm FBX, hoặc chạy `collectors/maya_collect.py` bằng `mayapy`.

> **Chỉ số nào định dạng không có thì báo `SKIP`, không bao giờ đoán.** Báo cáo
> ghi rõ "nguồn này không cung cấp chỉ số đó" — hoạ sĩ không bị đổ oan, và Lead
> biết chính xác khi nào cần thêm file từ Maya.

### Suy `asset_class` để Lead không phải gõ

Theo thứ tự ưu tiên: tham số truyền vào → sidecar `<tên file>.submit.json` →
tên thư mục cha (`submit/vehicle_exterior/…`). Không suy được thì báo lỗi rõ
ràng chứ không áp bừa bộ luật.

## Hai loại lỗi được kiểm

| Loại | Nguồn | Ví dụ luật |
|---|---|---|
| **Lỗi mesh** — sức khoẻ hình học | Tính thẳng từ đỉnh + mặt trong file, không cần biết techspec | `MESH-001` n-gon · `MESH-002` non-manifold · `MESH-003` mặt lật · `MESH-004` lộn cả khối · `MESH-005` đỉnh chưa hàn · `MESH-006` mặt diện tích 0 · `MESH-007` mặt trùng · `MESH-008` đỉnh rời · `MESH-009` lỗ thủng · `MESH-010` index hỏng |
| **Sai techspec** — quy định của dự án | So với số trong `rules/` | `VEH-TRI-001` tricount · `VEH-UV-001` texel density · `VEH-RIG-004` bone bánh xe … |

Luật mesh đặt trong `rules/common/` với `asset_class: "*"` nên áp dụng cho **mọi**
asset class — không phải chép lại cho từng class.

### Cách phát hiện lỗi mesh

Module [`artspec/readers/meshcheck.py`](artspec/readers/meshcheck.py) nhận (đỉnh, mặt)
và trả về **số lượng kèm id** của từng loại lỗi, để thông điệp chỉ đúng chỗ cần sửa:

```
❌ FAIL · MESH-003 — Không được có mặt bị lật
  Ở ĐÂU
    • SM_SuvA_Body_LOD0            2 lỗi: f[54], f[55]
```

Hai chi tiết đáng chú ý:

- **Mặt lật** không dùng phép so từng cặp (nó gắn cờ oan cả mặt hàng xóm). Thay vào
  đó lan truyền hướng qua toàn khối liên thông rồi lấy **nhóm thiểu số** — lật 1 mặt
  thì báo đúng 1 mặt.
- **Lộn cả khối** (`MESH-004`) tách riêng khỏi mặt lật lẻ: khi mọi mặt đều nhất quán
  nhưng thể tích có dấu âm, cả vật thể đang hướng vào trong. Trong Maya nhìn bình
  thường, vào UE5 thì biến mất.

### Chỉ số mesh theo từng định dạng

| | FBX | glTF/GLB | OBJ | metrics.json (Maya) |
|---|:--:|:--:|:--:|:--:|
| n-gon, quad, tris | ✅ | ⊘¹ | ✅ | ✅ |
| non-manifold, lỗ thủng, mặt lật, lộn khối | ✅ | ✅ | ✅ | ✅ |
| mặt diện tích 0, mặt trùng, index hỏng | ✅ | ✅ | ✅ | ✅ |
| đỉnh trùng chưa hàn | ✅ | ⊘¹ | ✅² | ✅ |
| đỉnh rời | ✅ | ✅ | ⊘² | ✅ |

¹ glTF luôn tam giác hoá và tách đỉnh ở mỗi UV seam → các chỉ số này không phản ánh
topology hoạ sĩ dựng. Reader khai `_unavailable`, engine báo `SKIP` chứ không đoán.
² OBJ dùng kho đỉnh toàn cục dùng chung giữa các nhóm.

Collector Maya (`collectors/maya_collect.py`) gọi **cùng module** `meshcheck` — nên
validator trong Maya và validator đọc FBX không bao giờ cho hai kết quả khác nhau.

## Đã có sẵn bộ tool validate? Nối vào, đừng viết lại

Studio thường đã có 5–10 tool kiểm khác nhau. Nối từng cái vào từng chỗ sẽ không
bảo trì nổi, nên tất cả đi qua **một hợp đồng chung**:

```
tool A ──adapter──┐
tool B ──adapter──┼──> ExternalFinding ──> ánh xạ rule_id ──> MỘT báo cáo
tool C ──adapter──┘                         (kèm why, how_to_fix, golden asset)
```

### Chưa biết bộ tool của studio có những gì? Quét trước

```bash
python -m artspec.cli scan-validators D:/pipeline/scripts
```

**Chỉ đọc mã nguồn, không chạy gì** — dùng `ast` để phân tích cú pháp, không
import module nào, nên **không cần Maya** và không có rủi ro thực thi code.

Nó liệt kê hàm nào là validator, mỗi hàm phát ra mã lỗi gì, nhận ra **hàm tổng
hợp** (kiểu `run_all`) và xếp lên đầu, rồi **dựng sẵn khối `adapters.yaml`** cùng
danh sách mã lỗi để dán vào `external_codes`.

```
studio.runner.run_all                     TỔNG HỢP   Chạy toàn bộ validator
studio.checks.geometry.check_topology     3 mã       Kiểm topology
studio.checks.uv.check_uv                 3 mã       Kiểm UV
```

Thêm `--json` để xuất bản tóm tắt gửi đi. Bản tóm tắt chỉ chứa tên hàm, mã lỗi
và dòng mô tả đầu — không chứa logic nghiệp vụ.

Khai báo trong `adapters.yaml` (mẫu: [`adapters.example.yaml`](adapters.example.yaml)) —
hai kiểu tool phổ biến nhất **không cần viết Python**:

| Kiểu | Dùng cho | Khai báo |
|---|---|---|
| `json_cli` | Tool in ra JSON | `command` + `findings_path` + `fields` |
| `regex_text` | Tool chỉ in text | `command` + `pattern` |
| `maya_batch` | Validator chạy trong Maya — kiểm file nộp | `mayapy` + `module` + `function` |
| `maya_port` | Validator chạy trong Maya **đang mở** | `port` + `module` + `function` |

Hai kiểu Maya dùng chung `adapters/maya_runner.py` chạy bên trong Maya. Hàm
validator của bạn trả về `list[dict]`, `list[object]` hay `{"issues": [...]}`
đều được — runner tự chuẩn hoá, bạn chỉ khai `fields`.

| | `maya_batch` | `maya_port` |
|---|---|---|
| Dùng khi | Lead kiểm file nộp, batch đêm | Hoạ sĩ kiểm scene đang làm |
| Cần Maya mở sẵn | Không | Có |
| Tốn license | **Có** | Không |
| Tốc độ | 30 giây – vài phút/scene | Nhanh (scene đã nạp) |
| Rủi ro | Không | Phải bật commandPort — [`BAO_MAT.md`](../BAO_MAT.md) §5 |

`maya_port` mặc định `open_scene: false` — kiểm đúng scene hoạ sĩ đang mở, không
đụng tới nó. Adapter cũng **từ chối nối tới host khác localhost**, vì commandPort
không có xác thực.

Rồi nối mã lỗi vào luật để báo cáo có đủ 5 phần:

```yaml
# rules/vehicle/VEH-TRI-001.yaml
external_codes: [TRICOUNT_OVER]
```

```
❌ FAIL · VEH-TRI-001 — Giới hạn tricount thân xe ngoại thất
  Ở ĐÂU            SM_Body_LOD0    132450 / 96000        ← tool của bạn
                   SM_Glass_LOD0   9000 / 4000           ← tool của bạn
  GHI CHÚ          Nguồn: tool ngoài 'maya_validator'
  VÌ SAO           Ngân sách GPU cho 12 xe...            ← artspec
  SỬA THẾ NÀO      1. Xác định chỗ tốn tri nhất...       ← artspec
```

**Bốn tính chất quan trọng:**

- Các tool chạy **song song**; một tool hỏng hoặc treo thành một dòng `ERROR`,
  các tool còn lại vẫn chạy
- Mã lỗi **chưa nối** không bị bỏ im lặng — hiện thành `WARN` kèm hướng dẫn khai báo
- Một luật chỉ hiện **một dòng** trong báo cáo, kể cả khi vừa kiểm nội bộ vừa có
  tool ngoài báo: lấy trạng thái xấu hơn, cộng dồn chỗ vi phạm
- Hai luật cùng nhận một mã → **báo lỗi lúc nạp**, không đoán

## Kiến trúc

```
rules/*.yaml ─┐
              ├─> registry ─> engine ─┬─> CLI          (hoạ sĩ chạy lúc export)
waivers/*.yaml┘                       ├─> nightly batch (Lead xem dashboard)
                                      └─> MCP server    (Lead & hoạ sĩ hỏi trong chat)
                          ▲
       ┌──────────────────┴───────────────────┐
  readers/ (fbx, gltf, obj)          collectors/maya_collect.py
  đọc thẳng file nộp lên             chạy trong Maya, đủ chỉ số nhất
```

**Một bộ luật, một engine, nhiều cửa gọi.** Đừng viết luật hai lần — validator
trong Maya và MCP phải đọc chung `rules/`, nếu không hai bên lệch nhau và hoạ sĩ
mất niềm tin vào cả hai.

## Chạy thử

```bash
pip install -r requirements.txt

python -m artspec.cli rules                                   # liệt kê luật
python -m artspec.cli check   submit/vehicle_exterior/SUV_A.fbx   # kiểm 1 file nộp
python -m artspec.cli inbox   submit/                             # kiểm cả lô
python -m artspec.cli validate samples/metrics_fail.json      # 8 FAIL, 1 WARN, 1 MANUAL
python -m artspec.cli validate samples/metrics_pass.json      # qua gate
python -m artspec.cli validate samples/metrics_fail.json --stage G2   # chỉ gate G2
python -m artspec.cli validate samples/metrics_fail.json --json       # cho script/CI
python -m artspec.cli updates vehicle_exterior --since 2026-08-20
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

Mặc định transport `stdio` (chạy trên máy hoạ sĩ, không mở cổng mạng nào). Khi
triển khai chung cho cả team thì đặt `ARTSPEC_TRANSPORT=streamable-http` — lúc đó
**bắt buộc** bật OAuth 2.1 và giới hạn thư mục đọc:

```bash
export ARTSPEC_FILE_ROOT=/mnt/project/submit:/mnt/project/golden
```

Không đặt = không giới hạn (chấp nhận được với bản local, vì server chạy đúng
quyền của chính người dùng). Chi tiết: [`BAO_MAT.md`](../BAO_MAT.md).

Server tự nạp lại khi file YAML đổi — sửa luật không cần restart.

### Tool đang có

| Tool | Trả lời câu hỏi kiểu |
|---|---|
| `check_file` | "File hoạ sĩ vừa nộp có đạt không?" — đọc thẳng .fbx/.glb/.obj |
| `check_inbox` | "Lô submit hôm nay file nào cần xem?" |
| `supported_formats` | "Định dạng nào kiểm được, thiếu chỉ số gì?" |
| `check_asset` | "Asset của tôi có đạt không?" — từ metrics đã có sẵn |
| `get_budget` | "Xe LOD2 tối đa bao nhiêu tri?" |
| `search_spec` | "Dự án quy định gì về texel density?" |
| `get_rule` | "VEH-UV-002 nói gì?" |
| `get_checklist` | "Trước khi submit tôi phải kiểm gì?" |
| `explain_term` | "Texel density là gì?" |
| `whats_changed_for` | "Tôi nghỉ 2 tuần, khách đổi gì với xe?" |
| `get_update` | "CU-2026-047 khách nói chính xác là gì?" |
| `list_rules` / `list_waivers` | Tổng quan cho Lead |

Resource: `spec://index` · `spec://rules/{asset_class}` · `spec://glossary`.
Prompt: `pre_submit_review`.

`instructions` của server cấm model tự suy ra con số khi tool trả `found=false` —
đây là hàng rào chính chống việc AI bịa spec.

## Điền luật bằng Excel, không sửa YAML

Art Lead điền bảng `checklists/_MAU_THU_THAP.csv` rồi chạy một lệnh:

```bash
python -m artspec.cli import-rules checklists/luat_xe.csv              # xem trước
python -m artspec.cli import-rules checklists/luat_xe.csv --out rules/vehicle
```

Cột `check` dùng cú pháp rút gọn: `triangle_count <= 96000 where lod=0` ·
`name matches ^SM_.+$` · `ngons <= 0 ids ngon_faces` · `inverted_normals is false` ·
`manual: <câu hỏi>` · `custom: <tên hàm>`.

Dòng nào hỏng thì bị bỏ qua kèm báo lỗi **có số dòng để tìm trong Excel**; dòng
đúng vẫn chạy. `why` và `how_to_fix` bắt buộc — thiếu là loại dòng đó. Cách viết:
[`VIET_CHECKLIST.md`](../VIET_CHECKLIST.md).

## Thêm một luật đặc thù của dự án

| Tier | Ví dụ | Phải làm gì |
|---|---|---|
| **A** — số / regex | tricount, đặt tên, số material | **Chỉ thêm 1 file YAML.** Không đụng code |
| **B** — logic riêng | bố trí bone bánh xe, hard edge ⊂ UV seam | 1 file YAML + 1 hàm `@custom_check(...)` trong `artspec/checks/` |
| **C** — người kiểm | decal có bị che không | 1 file YAML `type: manual` → thành câu hỏi trong checklist |

Không trường hợp nào phải sửa `server.py` hay `engine.py`. Chi tiết field:
[`rules/_SCHEMA.md`](rules/_SCHEMA.md).

## Năm trạng thái

| | Nghĩa |
|---|---|
| `FAIL` | Chặn gate. Chỉ dành cho luật cứng, máy chắc chắn đúng |
| `WARN` | Cho qua nhưng ghi lại. Dùng khi luật có ngoại lệ hợp lệ, hoặc máy không chắc |
| `MANUAL` | Câu hỏi cho người (Tier C) |
| `SKIP` | Luật không áp dụng cho asset này (`check.requires`), hoặc nguồn dữ liệu không có chỉ số đó. **Không phải lỗi hoạ sĩ** |
| `ERROR` | **Lỗi của validator**, không phải của hoạ sĩ — luật viết sai hoặc metrics thiếu field. Báo cáo nói rõ điều này để hoạ sĩ không sửa asset theo báo cáo sai |

> Một lần báo sai giết chết mười lần báo đúng. Nghi ngờ thì để `WARN`.

## Waiver

Quy tắc đặc thù hay có ngoại lệ hợp lệ. Không có đường xin chính thức thì hoạ sĩ
sẽ tự lách — bỏ qua validator, submit thẳng, và Lead mất khả năng nhìn thấy vấn đề.

`waivers/waivers.yaml` hạ `FAIL` xuống `WARN` cho đúng cặp (luật, asset), có lý do,
người duyệt và **ngày hết hạn** — hết hạn thì tự mất tác dụng, không cần ai dọn.

## Tốc độ

Đo trên mesh tổng hợp, FBX nhị phân, **lần chạy đầu** (mỗi file chỉ kiểm một lần,
không bao giờ được "làm nóng"). Máy đo: Xeon 2.8 GHz 4 nhân.

| Asset | tris | Thời gian | RAM đỉnh |
|---|---|---|---|
| Prop môi trường | 13k | 0.1 s | ~100 MB |
| Xe LOD1 | 45k | 0.5 s | ~100 MB |
| Xe LOD0 | 120k | 2–3 s | ~200 MB |
| Mesh nặng | 500k | 9–12 s | ~0.9 GB |
| **High-poly** | **2M** | **~37 s** | **~3.1 GB** |
| High-poly | 3M | ~57 s | ~5.0 GB |

Ngoại suy: 1 xe 3 LOD ≈ **3 s** · 12 xe ≈ **35 s** · 200 prop ≈ **15 s** ·
depot 2000 asset ≈ **4 phút**.

**RAM là ràng buộc thật, không phải thời gian:** ~1.6–1.8 GB mỗi triệu tam giác.
Máy 16 GB xử lý được tới ~8M tris một file; muốn chạy song song nhiều file thì
chia RAM cho số tiến trình.

**Nút cổ chai là phân tích hình học (~85%), không phải đọc file.** Chạy 20 luật
mất dưới 1 ms — thêm luật gần như miễn phí. Muốn nhanh hơn thì vector hoá
`meshcheck.py` bằng numpy, không phải sửa reader.

> ⚠️ **Máy ảo dùng chung chênh nhau tới 2 lần giữa các lần đo.** Cùng một
> benchmark trên cùng máy này lúc ra 0.6 s, lúc ra 1.2 s cho 120k tris. Đừng tin
> con số của máy khác — chạy `python tests/bench.py --big` trên máy bạn, vài lần.

## Test

```bash
python tests/test_fbx.py       # 16 check — reader FBX, fixture tự sinh
python tests/test_readers.py   # 18 check — glTF/OBJ + luồng inbox đầu-cuối
python tests/test_updates.py   # 11 check — changelog + tool whats_changed_for
python tests/test_meshcheck.py # 29 check — phân tích mesh + luật MESH-* đầu-cuối
python tests/test_importer.py  # 27 check — CSV → luật, gồm cả bắt lỗi dòng hỏng
python tests/test_adapters.py  # 20 check — nối tool ngoài, gồm cả tool hỏng
python tests/test_maya_adapter.py  # 16 check — hai adapter Maya, chạy với Maya giả
python tests/test_scanner.py   # 18 check — quét mã nguồn validator, không import gì
python tests/test_security.py  # 11 check — giới hạn thư mục + chống điều khiển qua tên mesh
python tests/bench.py          # đo tốc độ trên MÁY CỦA BẠN (thêm --big cho mesh 500k)
```

`test_fbx.py` tự sinh FBX nhị phân rồi đọc lại — kiểm chứng phần đọc container
(offset, kiểu property, mảng nén zlib, node lồng nhau). `test_readers.py` viết
glTF tay theo spec rồi **đối chiếu chéo số tam giác với `trimesh`** (một cài đặt
độc lập) để chắc chắn không phải tôi tự hiểu sai định dạng.

> ⚠️ **Reader FBX chưa chạy trên FBX thật do Maya/Max export.** Test chỉ chứng
> minh phần container đúng. Phần dịch semantic (node nào chứa gì) bám theo cấu
> trúc chuẩn nhưng mỗi DCC ghi hơi khác — **chạy thử trên golden asset và đối
> chiếu tricount với HUD của Maya trước khi tin.**

## Việc còn phải làm

1. **Thay toàn bộ số trong `rules/` bằng số thật.** Không có bước này thì mọi thứ
   còn lại vô nghĩa.
2. Bổ sung tính texel density và hard edge / UV seam cho reader FBX — hiện đang
   báo SKIP, phải dùng collector Maya mới kiểm được 2 nhóm luật đó.
3. Chạy thử reader FBX **và** `collectors/maya_collect.py` trên golden asset, đối
   chiếu tricount / texel density bằng tay (cả hai **chưa kiểm chứng trên Maya thật**).
4. Nối vào nút Export trong Maya và vào batch chạy đêm.
5. Bổ sung `common_mistakes` cho từng luật sau mỗi tháng đọc Error Log.

## Cấu trúc

```
rules/<class>/*.yaml   luật riêng theo class — thứ bạn phải điền
rules/common/*.yaml    luật mesh dùng chung mọi class (asset_class: "*")
changelog/*.yaml       update khách hàng — nối vào luật bị ảnh hưởng
checklists/*.yaml      checklist theo gate G0-G3
checklists/_MAU_THU_THAP.csv   bảng Excel để Art Lead điền luật
glossary/*.yaml        thuật ngữ theo cách dự án hiểu
waivers/*.yaml         ngoại lệ đã duyệt
samples/*.json         metrics mẫu để chạy thử
collectors/            sinh metrics.json từ DCC (Maya)
tests/                 test tự chạy, không cần pytest
artspec/               engine — hiếm khi phải sửa
  adapters/    nối tool validate sẵn có của studio
  readers/     đọc thẳng file nộp: fbxfile.py · gltf.py · obj.py · images.py
               meshcheck.py — phân tích sức khoẻ hình học, dùng chung mọi định dạng
  inbox.py     kiểm 1 file / cả thư mục, bảng tóm tắt cho Lead
  importer.py  chuyển bảng CSV của Art Lead thành file luật YAML
  scanner.py   quét bộ tool validate của studio (chỉ đọc mã nguồn)
  registry.py  đọc & kiểm tính hợp lệ của luật
  checks/      builtin.py (Tier A) · vehicle.py (Tier B, đặc thù dự án)
  engine.py    chạy luật, áp waiver
  render.py    thông điệp lỗi 5 phần
  cli.py       giao diện dòng lệnh
  server.py    MCP server
```
