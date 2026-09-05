# Viết checklist như thế nào

> Đây là việc chính của Giai đoạn 1 trong [`BAT_DAU_TU_DAU.md`](BAT_DAU_TU_DAU.md).
> Bạn **không phải sửa YAML** — điền một bảng Excel rồi chạy một lệnh.
> Ngày soạn: 2026-09-05.

---

## 1. Hai loại mục, gộp thành một checklist

| Loại | Ai kiểm | Sống ở đâu | Ví dụ |
|---|---|---|---|
| **Luật** | Máy (hoặc người, với Tier C) | `rules/*.yaml` — sinh từ bảng Excel của bạn | "Tricount LOD0 ≤ 96,000" |
| **Mục quy trình** | Người | `checklists/*.yaml` | "Đã quyết định LOD chưa", "Hoạ sĩ đã ký chưa" |

Hệ thống tự gộp hai loại khi in checklist:

```bash
python -m artspec.cli checklist vehicle_exterior G1
```

```
G1 — Model Freeze

  [ ] Quy ước đặt tên mesh xe  (VEH-NAM-001, máy kiểm)
  [ ] Giới hạn tricount thân xe  (VEH-TRI-001, máy kiểm)
  [ ] Không được có n-gon  (MESH-001, máy kiểm)
  [ ] Đã quyết định LOD: số lượng và cách sinh
  [ ] Tôi xác nhận model ĐÃ XONG và hiểu rằng sửa topology sau gate này phải xin duyệt

  CHỮ KÝ HOẠ SĨ: ____________     LEAD DUYỆT: ____________
```

**Nên viết gần như mọi thứ thành luật**, kể cả mục người kiểm (Tier C) — vì luật
có `why` và `how_to_fix` đi kèm, còn mục quy trình thì không. Chỉ để lại ở
`checklists/` những việc **không gắn với asset**: đã họp chưa, đã ký chưa, đã
quyết định chưa.

---

## 2. Phép thử duy nhất của một mục tốt

> **Hai hoạ sĩ khác nhau kiểm cùng một asset có ra cùng kết luận không?**

Không → mục đó chưa viết xong. Đây là phép thử duy nhất cần nhớ; 5 tiêu chí dưới
đây chỉ là cách đạt được nó.

| # | Tiêu chí | Nghĩa là |
|---|---|---|
| 1 | **Nhị phân** | Chỉ đạt hoặc không đạt. Không có "hơi đạt", "tạm ổn" |
| 2 | **Đo được** | Nêu rõ đo bằng gì, ở đâu trong phần mềm |
| 3 | **Một ý** | Không có chữ "và". Hai ý = hai mục |
| 4 | **Có phạm vi** | Áp cho mesh nào, LOD nào, platform nào |
| 5 | **Có lý do** | Hoạ sĩ hiểu vì sao thì tự biết linh hoạt; không hiểu thì hoặc phá luật hoặc làm máy móc |

---

## 3. Biến câu tệ thành câu dùng được

| ❌ Viết như techspec | ✅ Viết như checklist |
|---|---|
| "Tricount phải hợp lý" | "Tricount ≤ 96,000 tris — thân xe LOD0 PC, **không tính bánh**" |
| "UV phải sạch sẽ" | Tách 3 mục: "Không overlap ở channel 0 (trừ mirror đã khai)" · "Texel density 10.24 ±0.5 px/cm" · "UV nằm trong 0–1" |
| "Đặt tên theo chuẩn studio" | "Mọi mesh khớp mẫu `SM_<Xe>_<BộPhận>_LOD<n>`" |
| "Model phải tối ưu và sạch" | Tách: tricount · n-gon · non-manifold · đỉnh trùng · mặt lật |
| "Kiểm tra normal" | "Không có mặt bị lật (tắt Two Sided Lighting, mặt lật sẽ đen)" |
| "Texture đúng quy cách" | Tách: kích thước luỹ thừa 2 · color space theo hậu tố · số material slot |

**Quy luật rút ra:** một câu trong techspec thường đẻ ra **3–5 mục checklist**.
Đó là bình thường — techspec viết cho người đọc hiểu, checklist viết để tick.

---

## 4. Mục này thuộc tier nào

```
Có so sánh được bằng một con số?          ──yes──> Tier A
        │no
Có mẫu chữ cố định (tên, hậu tố)?          ──yes──> Tier A
        │no
Máy đọc được dữ liệu nhưng phải tính?      ──yes──> Tier B  (cần tôi viết hàm)
        │no
Cần mắt người nhìn?                        ────────> Tier C
```

| Tier | Ví dụ | Bạn tự làm được? |
|---|---|---|
| **A** | tricount, tên mesh, số material, n-gon, color space | ✅ Điền bảng là xong |
| **B** | bone bánh xe đối xứng, hard edge ⊂ UV seam, transform freeze | ❌ Ghi `custom: <tên hàm>` rồi nhắn tôi |
| **C** | silhouette, decal bị che, art direction | ✅ Ghi `manual: <câu hỏi>` |

> **Đừng ép Tier C thành FAIL.** Máy báo sai một lần là hoạ sĩ mất niềm tin vào
> cả báo cáo — kể cả những lỗi báo đúng. Tier C để `warn`.

---

## 5. Quy trình thực tế — 4 bước

### Bước 1 · Mở bảng mẫu

```
artspec/checklists/_MAU_THU_THAP.csv
```

Mở bằng Excel. Có sẵn dòng hướng dẫn (bắt đầu bằng `#`, xoá sau khi hiểu) và 5
dòng ví dụ đủ cả 3 tier.

### Bước 2 · Điền

Mỗi dòng là một mục checklist. Cột `check` dùng cú pháp rút gọn — học trong 2 phút:

| Viết thế này | Nghĩa |
|---|---|
| `triangle_count <= 96000 where lod=0` | so sánh số, chỉ áp cho LOD0 |
| `texel_density_px_cm within 10.24 +- 0.5` | quanh một giá trị, sai số cho phép |
| `name matches ^SM_[A-Z]\w+_LOD[0-3]$` | mẫu chữ |
| `color_space in sRGB \| Linear` | thuộc tập cho phép |
| `ngons <= 0 ids ngon_faces` | lỗi mesh, kèm id để hoạ sĩ tìm |
| `inverted_normals is false` | cờ đúng/sai |
| `manual: <câu hỏi>` | Tier C |
| `custom: vehicle.<tên hàm>` | Tier B — cần tôi viết |

**Hai cột bắt buộc, không được bỏ trống:**

- `why` — vì sao có luật này
- `how_to_fix` — các bước sửa (nhiều bước ngăn bằng dấu `|`)

Thiếu một trong hai thì dòng đó bị loại, kèm báo lỗi có số dòng để bạn tìm trong
Excel. **Đây là cố ý:** báo lỗi mà không nói cách sửa thì hoạ sĩ vẫn phải đi hỏi
bạn, và cả hệ thống mất tác dụng.

> Lưu bằng **Excel → Save As → CSV UTF-8**. Đừng sửa file CSV bằng Notepad — ô có
> dấu phẩy sẽ làm lệch cột.

### Bước 3 · Chuyển thành luật

```bash
# xem trước, chưa ghi file nào
python -m artspec.cli import-rules checklists/luat_xe.csv

# ưng rồi thì ghi
python -m artspec.cli import-rules checklists/luat_xe.csv --out rules/vehicle
```

```
Đọc được 5 luật từ checklists/luat_xe.csv
  VEH-TRI-010    FAIL  tier A  G1  Giới hạn tricount thân xe LOD0
  VEH-NAM-010    FAIL  tier A  G1  Quy ước đặt tên mesh xe
  ...
❌ 2 dòng KHÔNG dùng được — sửa rồi chạy lại:
   dòng 24 (VEH-UV-012): thiếu cột 'why' — hoạ sĩ không hiểu lý do thì sẽ phá luật
   dòng 31 (VEH-TEX-015): không hiểu biểu thức: 'width phải là luỹ thừa 2'
```

Dòng hỏng bị bỏ qua và báo rõ, dòng đúng vẫn chạy. **Không bao giờ đoán** — một
luật sai âm thầm nguy hiểm hơn một luật thiếu.

### Bước 4 · Thử ngay

```bash
python -m artspec.cli rules --asset-class vehicle_exterior
python -m artspec.cli check submit/vehicle_exterior/SUV_A.fbx
```

Đọc báo cáo và tự hỏi: **nếu tôi là hoạ sĩ, đọc xong tôi sửa được chưa?**
Chưa → quay lại sửa cột `why` / `how_to_fix`, không phải sửa code.

---

## 6. Bắt đầu từ đâu khi chưa biết viết gì

**Đừng bắt đầu từ techspec. Bắt đầu từ Error Log.**

Lấy 10 lỗi bạn bắt gặp nhiều nhất tháng vừa rồi → viết thành 10 mục đầu tiên. Đó
là checklist có hiệu quả cao nhất, không phải checklist đầy đủ nhất.

Lý do: techspec có thể có 200 quy tắc, nhưng 80% lỗi thực tế chỉ đến từ khoảng
15 quy tắc. Viết 15 mục đó trước, chạy một tháng, rồi mở rộng theo dữ liệu.

Chưa có Error Log → dùng tạm 3 nguồn này:
1. Ba lỗi gần nhất khiến asset phải làm lại
2. Ba câu hoạ sĩ hay hỏi bạn nhất
3. Ba thứ bạn luôn phải kiểm bằng tay ở mỗi lần review

---

## 7. Sáu sai lầm hay gặp

| # | Sai lầm | Cách sửa |
|---|---|---|
| 1 | **Mục không kiểm được** — "phải trông đẹp" | Hoặc biến thành câu hỏi Tier C cụ thể, hoặc bỏ hẳn |
| 2 | **Nhồi nhiều ý vào một mục** | Tách. Một mục fail thì phải biết ngay fail vì cái gì |
| 3 | **Quên phạm vi** — "tricount ≤ 96k" (LOD nào? platform nào?) | Thêm `where lod=0, platform=pc` |
| 4 | **Copy nguyên văn techspec** | Techspec viết để đọc hiểu, checklist viết để tick |
| 5 | **Checklist quá dài** — 40 mục thì không ai đọc | Mỗi gate 8–15 mục. Quá 20 nghĩa là nhiều mục nên thành luật tự động |
| 6 | **Bỏ trống `why`** | Hoạ sĩ không hiểu lý do sẽ hoặc phá luật, hoặc làm máy móc khi tình huống khác |

---

## 8. Số lượng hợp lý

| Gate | Số mục | Ghi chú |
|---|---|---|
| G0 Blockout | 4–6 | Toàn Tier C, mắt người |
| G1 Model Freeze | 10–15 | 10 luật MESH-* đã có sẵn, bạn chỉ thêm luật riêng của class |
| G2 Tech Check | 8–12 | Gần như toàn Tier A/B, máy chạy nên nhiều cũng không sao |
| G3 In-game QC | 5–8 | Trong engine, người kiểm |

10 luật MESH-001…010 **đã có sẵn và áp dụng cho mọi asset class** — bạn không phải
viết lại chúng. Chỉ viết luật riêng của dự án.

---

## 9. Checklist của chính việc viết checklist

Trước khi coi một mục là xong:

- [ ] Hai người kiểm cùng asset sẽ ra cùng kết luận
- [ ] Chỉ có một ý, không có chữ "và"
- [ ] Nêu rõ áp cho cái gì (mesh nào, LOD nào, platform nào)
- [ ] Cột `why` giải thích được cho hoạ sĩ mới vào nghề
- [ ] Cột `how_to_fix` nêu tên lệnh/menu thật, không nói chung chung
- [ ] Đã chọn đúng mức: `fail` chỉ khi máy chắc chắn đúng và không có ngoại lệ hợp lệ
- [ ] Đã chạy `import-rules` và không có lỗi
- [ ] Đã chạy thử trên một asset thật và báo cáo đọc hiểu được

---

## 10. Khi nào cần nhắn tôi

| Tình huống | Nhắn gì |
|---|---|
| Mục Tier B | Mô tả luật bằng lời + 1 ví dụ đúng, 1 ví dụ sai |
| Cú pháp `check` không diễn tả được ý bạn | Viết ý đó bằng tiếng Việt, tôi thêm dạng mới |
| Muốn tôi điền hộ cả bảng | Gửi techspec (Excel, PDF, ảnh chụp đều được) |
| Báo cáo đọc khó hiểu | Chụp lại báo cáo + nói chỗ nào khó hiểu |

---

## Đọc thêm

| File | Nội dung |
|---|---|
| [`artspec/checklists/_MAU_THU_THAP.csv`](artspec/checklists/_MAU_THU_THAP.csv) | Bảng mẫu để mở bằng Excel |
| [`artspec/rules/_SCHEMA.md`](artspec/rules/_SCHEMA.md) | Ý nghĩa từng field, cho ai muốn sửa YAML trực tiếp |
| [`QUY_TRINH_6_BUOC_QUAN_LY.md`](QUY_TRINH_6_BUOC_QUAN_LY.md) | Định nghĩa DONE + lỗi hay gặp từng bước — nguồn ý tưởng cho checklist |
| [`BAT_DAU_TU_DAU.md`](BAT_DAU_TU_DAU.md) | Kế hoạch tổng thể |
