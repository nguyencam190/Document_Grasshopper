# Lộ trình — bạn cần làm gì, theo thứ tự nào

> Điểm vào của cả thư mục. Ba tài liệu kia là lý thuyết, `artspec/` là code, đây
> là **việc**.
> Cập nhật: 2026-09-05 (viết lại theo hiện trạng code — bản cũ đã lạc hậu).

---

## 0. Bảng điều khiển — đang ở đâu

### ✅ Đã xong, chạy được ngay

| Thứ | Chi tiết |
|---|---|
| Engine kiểm lỗi | **109 test** pass, không cần AI, không cần mạng |
| **10 luật lỗi mesh** | `MESH-001…010` — áp dụng **mọi** asset class. **Bạn không phải viết** |
| Đọc file trực tiếp | `.fbx` (parser tự viết) · `.gltf/.glb` · `.obj` · `.json` |
| MCP server | 13 tool, tự nạp lại khi luật đổi |
| Điền luật bằng Excel | `import-rules` — **không phải sửa YAML** |
| Bảo mật | Giới hạn thư mục đọc, chống điều khiển qua tên mesh |

### ⚠️ Chờ bạn

| Thứ | Ước tính | Chặn cái gì |
|---|---|---|
| Số thật cho luật riêng của class | 2–3 ngày | Chặn mọi thứ phía sau |
| Chốt 4 gate | 1 ngày | Chặn checklist |
| Golden Asset | 2–3 ngày | Không chặn, nhưng giá trị cao |
| Hỏi producer về NDA | 1 tin nhắn | Chỉ chặn phần MCP, không chặn validator |

### 🔧 Chờ bạn yêu cầu (việc của tôi)

| Thứ | Khi nào cần |
|---|---|
| Texel density + hard edge cho reader FBX | Khi muốn kiểm 2 nhóm luật đó mà không mở Maya |
| Luật Tier B riêng của dự án | Khi bảng CSV có dòng `custom:` |
| Cầu nối Maya (chọn hộ mặt lỗi) | Sau khi chạy ổn định vài tháng — xem [`BAO_MAT.md`](BAO_MAT.md) §5 |

---

## 1. Tuần này — 2 giờ, có kết quả thật ngay

**Điểm khác biệt lớn nhất so với kế hoạch cũ:** 10 luật mesh đã sẵn sàng. Bạn bắt
được lỗi thật **trước khi** điền bất kỳ con số nào.

### Bước 1 · Cài (15 phút)

```bash
cd MCP_Racing/artspec
pip install -r requirements.txt
python -m artspec.cli rules          # phải thấy 20 luật
```

### Bước 2 · Chạy trên asset thật (30 phút)

Lấy 5 file FBX bất kỳ hoạ sĩ đã nộp, bỏ vào một thư mục:

```bash
python -m artspec.cli inbox /duong/dan/toi/submit --stage G1
```

Gate G1 hiện có **13 luật**, trong đó 10 là luật mesh dùng chung. Kết quả:

```
FILE                    KẾT QUẢ          FAIL  WARN  HỎI   BỎ   LUẬT VI PHẠM
SM_SuvA_Body_LOD0.fbx   ⛔ KHÔNG QUA         2     1    0    3   MESH-001, MESH-003
SM_Barrier_LOD0.fbx     ✅ QUA               0     0    0    3
```

> Lệnh trả về mã thoát `1` khi có file không qua gate — đó là **bình thường**,
> không phải lỗi chương trình. Mã `2` mới là lỗi cấu hình. Cột "BỎ" là số luật
> không kiểm được từ định dạng đó (FBX không cho texel density và hard edge).

### Bước 3 · Đọc kỹ một báo cáo chi tiết (30 phút)

```bash
python -m artspec.cli check /duong/dan/SM_SuvA_Body_LOD0.fbx --stage G1
```

Tự hỏi 3 câu:
1. Nó có bắt được lỗi **thật** không, hay báo nhầm?
2. Nếu tôi là hoạ sĩ, đọc xong tôi **sửa được chưa**?
3. Con số nó đọc ra (tricount, số quad) có **khớp với Maya** không?

### Bước 4 · Đối chiếu bằng tay (45 phút)

Mở đúng file đó trong Maya, so tricount với HUD. **Bắt buộc làm** — reader FBX
tôi viết chưa từng chạy trên FBX thật do Maya export. Lệch thì báo tôi.

> ### ✅ Xong tuần này khi
> - [ ] Chạy được `inbox` trên 5 asset thật
> - [ ] Đọc hết một báo cáo chi tiết
> - [ ] Đối chiếu tricount với Maya, khớp (hoặc đã báo tôi chỗ lệch)
> - [ ] Biết được: 10 luật mesh bắt được bao nhiêu lỗi thật trên 5 file đó

**Con số cuối cùng đó quyết định có nên đi tiếp không.** Bắt được 0 lỗi trên 5
file nghĩa là mesh của team đã sạch — hãy dồn sức vào luật techspec thay vì mesh.

---

## 2. Lộ trình 6 tuần

```
T1  Chạy thử luật mesh          2 giờ    ──> biết engine có bắt được lỗi thật không
T2  Nền quy trình               1 ngày   ──> Error Log + gate Model Freeze + chọn class
T3  Điền số thật (Excel)        2-3 ngày ──> ★ VIỆC LỚN NHẤT
T4  Golden Asset                2-3 ngày ──> chuẩn tham chiếu
T5  Chạy thử 3 hoạ sĩ           1 tuần   ──> ⛳ ĐIỂM DỪNG ĐÁNH GIÁ
T6  Gắn MCP + tự động hoá       1-2 tuần ──> hoạ sĩ tự chạy được
```

---

### Tuần 2 · Nền quy trình *(1 ngày, không cần code)*

| Việc | Cách làm | Xong khi |
|---|---|---|
| **Mở Error Log** | 1 Google Sheet, 6 cột: Ngày · Asset · Bước sinh lỗi · Bước phát hiện · Mô tả · Giờ mất | Đã ghi ≥ 3 dòng từ review thật |
| **Thêm gate Model Freeze** | Form ký ở cuối [`QUY_TRINH_6_BUOC_QUAN_LY.md`](QUY_TRINH_6_BUOC_QUAN_LY.md) | Team đã nghe, có form in ra |
| **Chọn class thí điểm** | Class nhiều asset nhất + nhiều hoạ sĩ nhất, **không phải class khó nhất** | Đã ghi tên class |
| **Hỏi producer NDA** | *"Techspec có được đưa vào AI assistant nội bộ không? Dữ liệu nằm trên máy studio."* | Có câu trả lời |
| **Đo baseline** | Tháng trước bao nhiêu asset làm lại vì sai spec? Mất bao nhiêu giờ? | Có 2 con số |

> Câu trả lời NDA **không chặn** tuần 3–5. Validator chạy hoàn toàn offline.
> Nó chỉ chặn tuần 6 (phần MCP trong chat).

---

### Tuần 3 · Điền số thật ★ *(2–3 ngày — việc lớn nhất)*

Đây là toàn bộ giá trị còn lại. Chi tiết cách viết:
[`VIET_CHECKLIST.md`](VIET_CHECKLIST.md).

**Ngày 1 — gom**

Quét techspec, gom mọi quy tắc **có con số hoặc quy tắc rõ ràng** vào bảng nháp.
Gặp mâu thuẫn (hai chỗ ghi hai số khác nhau) thì **dừng lại chốt trước** — đây là
lỗi có sẵn, không công cụ nào cứu được.

Mục tiêu: **20–30 quy tắc** cho class thí điểm. Dưới 20 thì chưa cần hệ thống này.

**Ngày 2 — điền vào Excel**

```bash
# mở file này bằng Excel
artspec/checklists/_MAU_THU_THAP.csv
```

Cột `check` dùng cú pháp rút gọn:

| Viết | Nghĩa |
|---|---|
| `triangle_count <= 96000 where lod=0` | so sánh số |
| `texel_density_px_cm within 10.24 +- 0.5` | quanh một giá trị |
| `name matches ^SM_[A-Z]\w+_LOD[0-3]$` | mẫu chữ |
| `material_slots <= 4 where lod=0` | so sánh số |
| `manual: <câu hỏi>` | người kiểm |
| `custom: vehicle.<tên hàm>` | cần tôi viết |

**`why` và `how_to_fix` bắt buộc.** Thiếu là loại dòng đó.

**Ngày 3 — chuyển và thử**

```bash
python -m artspec.cli import-rules checklists/luat_xe.csv                  # xem trước
python -m artspec.cli import-rules checklists/luat_xe.csv --out rules/vehicle
python -m artspec.cli check /duong/dan/SUV_A.fbx
```

> ### ✅ Xong tuần 3 khi
> - [ ] ≥ 20 luật riêng của class, có số thật
> - [ ] `import-rules` chạy, 0 dòng lỗi
> - [ ] Mọi luật có `why` + `how_to_fix` mà hoạ sĩ mới đọc hiểu được
> - [ ] Đã xoá hết luật mẫu cũ trong `rules/vehicle/` (toàn số bịa)
> - [ ] Techspec không còn mâu thuẫn ở class này

---

### Tuần 4 · Golden Asset *(2–3 ngày)*

Chọn 1 asset của class thí điểm, làm đúng 100%, lưu file **từng bước**:

```
GoldenAsset/SUV_Base/
  01_blockout.mb   02_model_freeze.mb   03_normal_locked.mb   04_uv.mb
  05_texture/      06_rig.mb            07_export.fbx         08_ue5_screenshot.png
```

Rồi điền tên nó vào cột `golden_asset` trong Excel, chạy lại `import-rules` —
thông điệp lỗi sẽ tự chỉ tới nó.

Dùng để: onboarding người mới · giải quyết tranh cãi "làm sao mới đúng" · test lại
khi đổi engine.

> ### ✅ Xong khi
> - [ ] Đủ 8 file/thư mục theo từng bước
> - [ ] `python -m artspec.cli check GoldenAsset/SUV_Base/07_export.fbx` → **QUA GATE**
>
> Nếu golden asset của chính bạn không qua gate → **luật đang sai**, không phải
> asset sai. Sửa luật.

---

### Tuần 5 · Chạy thử 3 hoạ sĩ ⛳ *(1 tuần)*

**Cách chạy đơn giản nhất — bạn kiểm hộ, hoạ sĩ chưa cần cài gì:**

Hoạ sĩ nộp FBX vào `submit/<tên class>/`, bạn chạy:

```bash
python -m artspec.cli inbox submit/              # xem toàn cảnh
python -m artspec.cli check submit/vehicle_exterior/SUV_A.fbx    # gửi lại chi tiết
```

**Theo dõi 3 con số:**

| Đo gì | Ghi vào đâu |
|---|---|
| Lỗi bị bắt **trước** khi submit | Error Log |
| Số lần báo **sai** (false positive) | Error Log — mỗi lần là 1 luật cần sửa |
| Hoạ sĩ có tự nguyện chạy lại lần 2 không | Quan sát |

> ### ⛳ ĐIỂM DỪNG — trả lời thật
>
> | Câu hỏi | Nếu KHÔNG |
> |---|---|
> | Bắt được lỗi thật? | Luật chưa đúng chỗ đau → quay lại tuần 3, chọn luật theo Error Log |
> | Báo sai < 1 lần/asset? | Hạ luật hay báo sai xuống `warn`, hoặc sửa luật |
> | Hoạ sĩ **tự nguyện** dùng tiếp? | **Dừng lại.** Vấn đề là quy trình/động lực — làm thêm tuần 6 cũng vô ích |
>
> Cả 3 câu đều CÓ mới đi tiếp.

---

### Tuần 6+ · Gắn MCP và tự động hoá

Theo thứ tự giá trị giảm dần:

**1. Batch chạy đêm** *(giá trị cao nhất, không cần AI)*

```bash
python -m artspec.cli inbox /mnt/depot/exports --json > report.json
```

Cắm vào Task Scheduler / cron. Sáng ra có bảng tổng hợp.

**2. Gắn MCP vào Claude Desktop** *(chỉ khi NDA đã ok)*

Hướng dẫn từng bước: [`CAI_DAT_CLAUDE.md`](CAI_DAT_CLAUDE.md).

```json
{
  "mcpServers": {
    "artspec": {
      "command": "python",
      "args": ["-m", "artspec.server"],
      "cwd": "/duong/dan/MCP_Racing/artspec",
      "env": { "ARTSPEC_ROOT": "/duong/dan/MCP_Racing/artspec" }
    }
  }
}
```

**Bắt buộc thử bước chống bịa:** hỏi một câu mà techspec **không** quy định
(vd *"số vertex tối đa cho decal là bao nhiêu?"*). Trả lời đúng phải là *"techspec
không có quy định này"*. Nó bịa ra số → báo tôi ngay.

**3. Nút Export trong Maya** — chạy validator ngay lúc hoạ sĩ export.

**4. Nhân rộng class còn lại** — 0.5–1 ngày/class khi đã quen bảng Excel.

**5. Server dùng chung** — chuyển `streamable-http`, **bắt buộc** OAuth 2.1 +
`ARTSPEC_FILE_ROOT`. Xem [`BAO_MAT.md`](BAO_MAT.md) §4.

---

## 3. Ba điểm quyết định

| Khi nào | Quyết định gì | Dữ liệu để quyết |
|---|---|---|
| Cuối tuần 1 | Có đáng đầu tư tiếp không | Số lỗi mesh bắt được trên 5 asset thật |
| Cuối tuần 3 | Techspec đủ chín chưa | Có ≥ 20 luật rõ ràng, không mâu thuẫn |
| **Cuối tuần 5** | **Nhân rộng hay dừng** | Hoạ sĩ có tự nguyện dùng không |

Điểm thứ ba quan trọng nhất. Đừng bỏ qua nó chỉ vì đã bỏ công 5 tuần.

---

## 4. Bảng theo dõi — in ra tick

```
TUẦN 1  [ ] Cài đặt        [ ] Chạy inbox 5 asset   [ ] Đọc 1 báo cáo chi tiết
        [ ] Đối chiếu tricount với Maya
        → Bắt được ______ lỗi mesh thật / 5 file

TUẦN 2  [ ] Error Log mở   [ ] Gate Model Freeze    [ ] Chọn class: ____________
        [ ] Hỏi NDA        [ ] Baseline: ____ asset làm lại, ____ giờ

TUẦN 3  [ ] Gom ____ quy tắc   [ ] Điền Excel   [ ] import-rules 0 lỗi
        [ ] Xoá luật mẫu cũ    [ ] Chạy thử trên asset thật

TUẦN 4  [ ] Golden Asset đủ 8 bước    [ ] Golden asset QUA GATE

TUẦN 5  [ ] 3 hoạ sĩ dùng 1 tuần
        → Bắt trước submit: ____   Báo sai: ____   Tự nguyện dùng tiếp: Có / Không
        ⛳ ĐI TIẾP  /  QUAY LẠI T3  /  DỪNG

TUẦN 6  [ ] Batch đêm   [ ] MCP + thử chống bịa   [ ] Nút Export Maya
```

---

## 5. Nếu bạn chỉ có 2 giờ mỗi tuần

Lộ trình rút gọn, cùng thứ tự nhưng giãn ra:

| Tuần | Việc duy nhất |
|---|---|
| 1 | Cài + chạy `inbox` trên 5 asset |
| 2 | Mở Error Log, bắt đầu ghi |
| 3 | Thêm gate Model Freeze |
| 4–7 | Mỗi tuần điền 6–8 dòng Excel |
| 8 | `import-rules` + chạy thử |
| 9–11 | Golden Asset |
| 12 | Chạy thử với 3 hoạ sĩ |

Chậm hơn nhưng **không bỏ bước nào**. Thứ tự quan trọng hơn tốc độ.

---

## 6. Gửi tôi cái gì để tôi làm tiếp

| Bạn có | Tôi làm |
|---|---|
| Bảng số thật (Excel / PDF / ảnh chụp techspec) | Điền hộ cả bộ luật |
| Một dòng `custom:` trong Excel | Viết hàm Tier B |
| Tricount reader đọc lệch so với Maya | Sửa parser FBX |
| Muốn kiểm texel density mà không mở Maya | Bổ sung cho reader FBX |
| Đã chạy ổn vài tháng, muốn chọn hộ mặt lỗi trong viewport | Cầu nối Maya |

---

## Bản đồ tài liệu

| File | Đọc khi |
|---|---|
| [`VIET_CHECKLIST.md`](VIET_CHECKLIST.md) | **Tuần 3** — cách viết từng mục |
| [`QUY_TRINH_6_BUOC_QUAN_LY.md`](QUY_TRINH_6_BUOC_QUAN_LY.md) | **Tuần 2** — chi tiết 4 gate |
| [`CAI_DAT_CLAUDE.md`](CAI_DAT_CLAUDE.md) | **Tuần 6** — cài vào Claude Desktop |
| [`artspec/README.md`](artspec/README.md) | Tuần 1, 5, 6 — cách chạy |
| [`BAO_MAT.md`](BAO_MAT.md) | Trước khi nói chuyện với IT / producer |
| [`TAO_TOOL_MCP.md`](TAO_TOOL_MCP.md) | Khi muốn thêm tool mới |
| [`NGHIEN_CUU_MCP_ARTSPEC.md`](NGHIEN_CUU_MCP_ARTSPEC.md) | Khi cần giải thích MCP cho sếp |
