# Bắt đầu từ đâu — kế hoạch hành động cho Art Lead

> Tài liệu này trả lời đúng một câu: **tôi phải làm gì, theo thứ tự nào.**
> Ba tài liệu kia là lý thuyết và code; đây là việc.
> Ngày soạn: 2026-09-05.

---

## 1. Bạn đang ở đâu

| Thứ | Trạng thái | Ai làm |
|---|---|---|
| Engine kiểm lỗi (`artspec/`) | ✅ Xong, chạy được, có test | Đã xong |
| MCP server, 11 tool | ✅ Xong | Đã xong |
| Đọc thẳng file `.fbx`/`.glb`/`.obj` | ✅ Xong | Đã xong |
| Khung 10 luật mẫu | ⚠️ **Toàn số bịa** | **Bạn phải thay** |
| Quy trình + gate | ⚠️ Có đề xuất, chưa chốt | **Bạn quyết** |
| Golden Asset | ❌ Chưa có | **Bạn làm** |
| Chạy thử với hoạ sĩ thật | ❌ Chưa | **Bạn tổ chức** |

**Nói thẳng:** phần khó nhất còn lại không phải kỹ thuật. Code đã chạy. Thứ còn
thiếu là **nội dung** — số thật, quyết định thật — và chỉ bạn làm được.

---

## 2. Ai làm gì

| Vai | Việc | Thời lượng ước tính |
|---|---|---|
| **Bạn (Art Lead)** | Điền số thật vào luật · chốt gate · làm Golden Asset · duyệt waiver · đọc Error Log hàng tháng | 5–7 ngày công rải trong 6 tuần |
| **TA / pipeline TD** *(nếu có)* | Cài Python, chạy thử, nối vào nút Export trong Maya, dựng batch chạy đêm | 3–5 ngày công |
| **Hoạ sĩ (3 người thử)** | Dùng thật 1 tuần, phản hồi | 30 phút/người |
| **Producer** | Xác nhận NDA cho phép đưa techspec vào AI | 1 cuộc trao đổi |
| **Tôi** | Sửa code, thêm luật Tier B, viết collector còn thiếu | theo yêu cầu |

> Không có TA cũng làm được đến hết Giai đoạn 4 — chỉ cần chạy được lệnh trong
> Terminal/CMD. Từ Giai đoạn 6 (tự động hoá) mới thật sự cần người biết code.

---

## 3. Toàn cảnh

```
GĐ0  Chuẩn bị            2 giờ        ──> biết bắt đầu từ class nào, có Error Log
GĐ1  Điền số thật        3–5 ngày     ──> luật thật, chạy được   ★ QUAN TRỌNG NHẤT
GĐ2  Chốt gate           1 ngày       ──> checklist in ra dùng được
GĐ3  Golden Asset        2–3 ngày     ──> chuẩn tham chiếu
GĐ4  Chạy thử 3 hoạ sĩ   1 tuần       ──> ĐIỂM DỪNG ĐÁNH GIÁ ⛳
GĐ5  Gắn MCP             1–2 ngày     ──> hoạ sĩ hỏi được trong chat
GĐ6  Tự động hoá         2–3 tuần     ──> nút Export + batch đêm
```

**Đừng nhảy cóc.** GĐ5 (MCP) không có ý nghĩa nếu GĐ1 chưa xong — server sẽ trả
lời bằng số bịa. GĐ6 không có ý nghĩa nếu GĐ4 cho thấy hoạ sĩ không dùng.

---

## GIAI ĐOẠN 0 — Chuẩn bị *(2 giờ, làm được ngay hôm nay)*

### 0.1 Chọn asset class thí điểm

Chọn class **nhiều asset nhất và nhiều hoạ sĩ nhất**, không phải class khó nhất.
Với racing open-world thường là `vehicle_exterior` hoặc `environment_prop`.

Lý do: cần đủ người dùng để biết quy trình có chạy không. Class khó mà chỉ 1
người làm thì học được rất ít.

**Ghi lại:** class chọn là `________________`

### 0.2 Mở Error Log

Một Google Sheet, 6 cột:

| Ngày | Asset | Bước sinh lỗi | Bước phát hiện | Mô tả lỗi | Giờ mất |
|---|---|---|---|---|---|

Từ hôm nay, mỗi lần bạn bắt được lỗi khi review thì ghi 1 dòng. **Đây là nguồn
dữ liệu quan trọng nhất của cả dự án** — nó cho biết luật nào cần viết trước.

### 0.3 Đo baseline

Nhìn lại 1 tháng qua, trả lời 2 câu:

- Bao nhiêu asset phải làm lại vì sai spec? `______`
- Ước tính tổng số giờ mất vì việc đó? `______`

Hai con số này là thứ bạn dùng để chứng minh hiệu quả với producer sau 3 tháng.
Không đo bây giờ thì sau này không so được.

### 0.4 Hỏi producer về NDA

> "Techspec dự án có được phép đưa vào một AI assistant nội bộ không? Dữ liệu
> nằm trên máy studio, không gửi ra ngoài trừ phần chat với Claude."

Câu trả lời **không chặn** Giai đoạn 1–4 (validator chạy hoàn toàn offline).
Nó chỉ chặn Giai đoạn 5 (MCP).

---

## GIAI ĐOẠN 1 — Điền số thật ★ *(3–5 ngày — việc quan trọng nhất)*

Đây là toàn bộ giá trị của hệ thống. Làm cẩu thả ở đây thì mọi thứ sau vô nghĩa.

### 1.1 Gom quy tắc định lượng

Mở techspec, quét từ đầu đến cuối, gom mọi thứ **có con số hoặc có quy tắc rõ ràng**
vào một bảng nháp:

| Quy tắc | Con số | Áp cho cái gì | Nguồn (trang/mục) |
|---|---|---|---|
| Tricount LOD0 PC | 120,000 | thân xe, không tính bánh | Confluence 3.2 |
| … | | | |

Trong lúc gom, bạn sẽ gặp 3 tình huống — xử lý như sau:

| Gặp gì | Làm gì |
|---|---|
| Hai chỗ ghi hai số khác nhau | **Dừng lại, chốt số đúng trước.** Đây là lỗi có sẵn, MCP không cứu được |
| Quy tắc mơ hồ ("tricount hợp lý") | Hỏi lại người viết, hoặc tự chốt một con số rồi ghi là do bạn chốt |
| Quy tắc không có số ("phải trông thật") | Để riêng — đây là Tier C, sẽ thành câu hỏi tự kiểm |

> **Việc gom này tự nó đã có giá trị**, kể cả nếu bạn dừng dự án ở đây. Nó lộ ra
> chỗ techspec đang mâu thuẫn — thứ mà không ai phát hiện cho tới khi có asset hỏng.

**Ngưỡng để đi tiếp:** gom được ít nhất **30 quy tắc định lượng**. Dưới ngưỡng đó
thì một file PDF 2 trang là đủ, chưa cần hệ thống này.

### 1.2 Sửa file luật — hướng dẫn từng bước

Mỗi luật là 1 file trong `artspec/rules/vehicle/`. Mở bằng Notepad++ / VS Code /
bất kỳ trình soạn text nào. **Không cần biết lập trình** — chỉ sửa số và chữ.

**Ví dụ cụ thể.** Mở `VEH-TRI-001.yaml`, tìm khối này:

```yaml
  # ⚠️ SỐ VÍ DỤ — thay bằng budget thật của dự án
  table:
    - { lod: 0, platform: pc,      value: 120000 }
    - { lod: 1, platform: pc,      value: 45000 }
```

Sửa thành số thật của bạn, xoá dòng cảnh báo:

```yaml
  table:
    - { lod: 0, platform: pc,      value: 96000 }
    - { lod: 1, platform: pc,      value: 38000 }
```

Rồi điền tiếp 3 field quan trọng nhất — **đây mới là phần làm nên khác biệt**:

```yaml
why: >
  (Vì sao có luật này. Hoạ sĩ hiểu lý do thì tự biết linh hoạt;
   không hiểu thì hoặc phá luật hoặc làm máy móc.)
how_to_fix:
  - (Bước 1 cụ thể, nêu tên lệnh/menu thật trong Maya)
  - (Bước 2)
common_mistakes:
  - (Lỗi bạn đã thật sự bắt gặp khi review — lấy từ Error Log)
```

Ba field này **vào thẳng thông điệp lỗi** mà hoạ sĩ đọc. Viết tốt = hoạ sĩ tự sửa
được. Viết qua loa = họ vẫn phải đi hỏi bạn, và hệ thống mất tác dụng.

### 1.3 Quy tắc mới không có file sẵn

| Loại | Bạn tự làm được? | Cách |
|---|---|---|
| **Có số / so sánh / tên** (Tier A) | ✅ Được | Copy 1 file cũ, đổi `id` + nội dung. Xem `rules/_SCHEMA.md` |
| **Logic riêng** (Tier B) | ❌ Cần tôi | Mô tả luật bằng lời, tôi viết hàm |
| **Người kiểm** (Tier C) | ✅ Được | Copy `VEH-VIS-001.yaml`, đổi câu hỏi |

### 1.4 Chạy thử

```bash
cd MCP_Racing/artspec
pip install -r requirements.txt         # chỉ cần 1 lần
python -m artspec.cli rules             # liệt kê luật đã nạp
python -m artspec.cli validate samples/metrics_pass.json
```

Nếu file YAML viết sai, chương trình báo lỗi ngay và chỉ đúng dòng — sửa rồi chạy lại.

### 1.5 11 câu cần chốt trong lúc làm

**Kỹ thuật**
1. Đơn vị dự án và quy ước pivot?
2. Texel density chuẩn theo từng class? (px/cm)
3. Ánh sáng: Lumen động hay bake tĩnh? → quyết định có cần UV channel 1 không
4. Channel packing? (ORM / RMA / khác — kênh nào là gì)
5. Naming convention cho mesh, texture, bone, material?
6. Giới hạn influence/vertex khi skin?
7. Nanite: class nào bật, class nào không?
8. Budget tricount / texture resolution / material slot theo class?

**Tổ chức**
9. Ai được quyền merge thay đổi luật khi bạn bận?
10. Ai duyệt waiver?
11. Studio có repo git nội bộ để đặt bộ luật không?

### ✅ Xong Giai đoạn 1 khi

- [ ] ≥ 30 luật có số thật, không còn dòng `⚠️ SỐ VÍ DỤ` nào
- [ ] `python -m artspec.cli rules` chạy không lỗi
- [ ] Mọi luật có `why` + `how_to_fix` viết cho người mới đọc hiểu được
- [ ] Techspec không còn mâu thuẫn ở class thí điểm

---

## GIAI ĐOẠN 2 — Chốt gate *(1 ngày)*

### 2.1 Quyết định gate

Đề xuất trong [`QUY_TRINH_6_BUOC_QUAN_LY.md`](QUY_TRINH_6_BUOC_QUAN_LY.md): 6 bước
của bạn + 4 gate (G0 Blockout · **G1 Model Freeze** · G2 Tech Check · G3 In-game QC).

Bạn có thể bỏ bớt, nhưng **đừng bỏ G1**. Lock Normal khoá mesh lại; không có gate
chặn ở đó thì hoạ sĩ vẫn quay lại sửa model và mất trắng bước 2–3–4. Đây là nguồn
rework lớn nhất.

### 2.2 Cập nhật checklist

Sửa `artspec/checklists/vehicle.yaml` cho khớp gate bạn chốt. In ra thử:

```bash
python -m artspec.cli checklist vehicle_exterior G1
```

### 2.3 Công bố với team

Họp 30 phút, nói 4 ý:
1. Từ tuần sau có 4 gate, mỗi gate có checklist
2. **Hoạ sĩ tự tick, tự ký trước khi submit**
3. Lead **không** bắt lỗi có trong checklist — sai là trả về ngay, không sửa hộ
4. Có đường xin ngoại lệ chính thức (waiver), đừng tự lách

Ý số 3 là thay đổi tâm lý quan trọng nhất: nó đổi câu hỏi trong đầu hoạ sĩ từ
*"Lead có bắt được không?"* thành *"tôi có dám ký không?"*.

### ✅ Xong khi
- [ ] Checklist in ra dán tường được
- [ ] Team đã nghe và hiểu quy tắc "Lead không sửa hộ"

---

## GIAI ĐOẠN 3 — Golden Asset *(2–3 ngày)*

Chọn 1 asset của class thí điểm, làm đúng 100%, **lưu file riêng của TỪNG BƯỚC**:

```
GoldenAsset/SUV_Base/
  01_blockout.mb
  02_model_freeze.mb
  03_normal_locked.mb
  04_uv.mb
  05_texture/        (đủ bộ, đúng naming, đúng color space)
  06_rig.mb
  07_export.fbx
  08_ue5_screenshot.png
```

Dùng để: onboarding người mới · giải quyết tranh cãi "làm sao mới đúng" · test lại
khi đổi engine/plugin.

Sau đó điền tên nó vào field `reference.golden_asset` của các luật liên quan — thông
điệp lỗi sẽ tự chỉ tới nó.

**Đây là khoản đầu tư sinh lời cao nhất trong toàn bộ danh sách.**

---

## GIAI ĐOẠN 4 — Chạy thử với 3 hoạ sĩ *(1 tuần)* ⛳

### 4.1 Cách chạy

Chọn 3 người, mỗi người 1 asset thật. Cách dùng đơn giản nhất — **bạn kiểm hộ**:

```bash
python -m artspec.cli check  submit/vehicle_exterior/SUV_A.fbx
python -m artspec.cli inbox  submit/
```

Hoạ sĩ nộp FBX vào thư mục `submit/<tên class>/`, bạn chạy 1 lệnh và gửi lại báo cáo.
Chưa cần cài gì trên máy hoạ sĩ.

### 4.2 Theo dõi 3 con số

| Đo gì | Cách |
|---|---|
| Bao nhiêu lỗi bị bắt **trước** khi submit | Đếm từ báo cáo |
| Bao nhiêu lần báo **sai** (false positive) | Ghi lại từng lần — mỗi lần là 1 luật cần sửa |
| Hoạ sĩ có tự nguyện chạy lại lần 2 không | Quan sát |

### 4.3 ⛳ ĐIỂM DỪNG ĐÁNH GIÁ

Hết tuần, trả lời thật:

| Câu hỏi | Nếu KHÔNG |
|---|---|
| Có bắt được lỗi thật không? | Luật viết chưa đúng chỗ đau → quay lại GĐ1, dùng Error Log chọn lại luật |
| Báo sai < 1 lần/asset? | Sửa hoặc hạ luật hay báo sai xuống `warn` |
| Hoạ sĩ có **tự nguyện** dùng tiếp? | **Dừng lại.** Vấn đề là quy trình/động lực, không phải thiếu tính năng — làm thêm GĐ5, GĐ6 cũng vô ích |

**Chỉ đi tiếp khi cả 3 câu đều CÓ.**

---

## GIAI ĐOẠN 5 — Gắn MCP *(1–2 ngày)*

Chỉ làm khi đã qua điểm dừng ở GĐ4 và producer đã đồng ý về NDA.

### 5.1 Cài trên máy bạn trước

Thêm vào file cấu hình Claude Desktop:

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

Thử hỏi trong Claude:
- *"kiểm giúp tôi thư mục submit hôm nay"*
- *"SUV_A sai chỗ nào, giải thích cho hoạ sĩ hiểu"*
- *"xe LOD2 tối đa bao nhiêu tri?"*

### 5.2 Kiểm tra AI không bịa

**Bắt buộc làm bước này.** Hỏi một câu mà techspec **không** quy định, ví dụ:

> "Dự án quy định số vertex tối đa cho decal là bao nhiêu?"

Trả lời đúng phải là *"techspec không có quy định này"*. Nếu nó bịa ra một con số
→ báo tôi ngay, phải siết lại `instructions` của server.

### 5.3 Mở rộng cho team

Máy hoạ sĩ cài giống bạn (stdio, chạy local). Chỉ khi muốn **một server chung**
mới cần chuyển sang `streamable-http` — và lúc đó **bắt buộc bật OAuth 2.1**,
xem [`NGHIEN_CUU_MCP_ARTSPEC.md`](NGHIEN_CUU_MCP_ARTSPEC.md) mục Bảo mật.

---

## GIAI ĐOẠN 6 — Tự động hoá *(2–3 tuần, cần TA)*

Theo thứ tự giá trị giảm dần:

1. **Batch chạy đêm** — quét toàn bộ FBX trong depot, sáng ra có bảng tổng hợp.
   Không cần AI, không cần MCP, và thường là thứ tiết kiệm thời gian nhất.
2. **Nút Export trong Maya** — chạy validator ngay lúc export, chặn lỗi sớm nhất.
3. **Bổ sung texel density + hard edge cho reader FBX** — hiện đang SKIP, phải
   dùng collector Maya. *(Việc của tôi, nói khi cần.)*
4. **Chuẩn hoá các class còn lại** — 0.5–1 ngày/class khi đã quen format.
5. **Sync tự động Confluence → luật** — dạng Pull Request chờ bạn duyệt.

---

## 4. Việc làm trong tuần này

Nếu chỉ làm được 5 việc, làm đúng 5 việc này:

- [ ] **Chọn asset class thí điểm** *(15 phút)*
- [ ] **Mở Error Log** và bắt đầu ghi *(15 phút)*
- [ ] **Thêm gate Model Freeze** vào quy trình, kèm form ký *(1 giờ)*
- [ ] **Bắt đầu gom quy tắc định lượng** vào bảng nháp *(nửa ngày)*
- [ ] **Hỏi producer về NDA** *(1 tin nhắn)*

Ba việc đầu không cần code, không cần tôi, không cần đợi ai — và tự chúng đã chặn
được phần lớn rework.

---

## 5. Khi bí thì nhắn tôi

| Tình huống | Đưa tôi cái gì |
|---|---|
| Muốn tôi điền luật hộ | Bảng số thật (Excel/ảnh chụp techspec cũng được) |
| Cần luật Tier B | Mô tả luật bằng lời + ví dụ đúng/sai |
| Reader FBX đọc sai số | 1 file FBX mẫu + con số đúng đọc từ HUD Maya |
| Cần collector FBX đầy đủ hơn | Nói rõ thiếu chỉ số nào |
| MCP bịa số | Câu hỏi đã hỏi + câu trả lời nó bịa |

---

## Đọc thêm

| File | Khi nào cần |
|---|---|
| [`QUY_TRINH_6_BUOC_QUAN_LY.md`](QUY_TRINH_6_BUOC_QUAN_LY.md) | Làm GĐ2 — chi tiết từng gate, lỗi hay gặp từng bước |
| [`artspec/README.md`](artspec/README.md) | Làm GĐ1, GĐ4, GĐ5 — cách chạy, cách thêm luật |
| [`artspec/rules/_SCHEMA.md`](artspec/rules/_SCHEMA.md) | Làm GĐ1 — ý nghĩa từng field trong file luật |
| [`NGHIEN_CUU_MCP_ARTSPEC.md`](NGHIEN_CUU_MCP_ARTSPEC.md) | Làm GĐ5, hoặc khi cần giải thích cho sếp MCP là gì |
