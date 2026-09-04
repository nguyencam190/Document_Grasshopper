# Quản lý quy trình 6 bước — 3D artset dự án Racing Open-World

> **Bối cảnh:** Art Lead muốn dựng quy trình 6 bước: Model → Lock Normal → UVW → Texture → Rigging →
> Import UE5. Mục tiêu: hoạ sĩ hiểu kỹ thuật dự án + hạn chế lỗi.
> **Tài liệu này trả lời:** cần thêm gì vào 6 bước đó để nó trở thành một hệ quản lý thật, chứ không
> chỉ là danh sách việc.
> **Liên quan:** [`NGHIEN_CUU_MCP_ARTSPEC.md`](NGHIEN_CUU_MCP_ARTSPEC.md) — checklist trong tài liệu
> này chính là dữ liệu mà MCP server sẽ phục vụ.
> **Ngày soạn:** 2026-09-04.
>
> ⚠️ Mọi con số trong tài liệu là **ví dụ minh hoạ cấu trúc**, không phải số của dự án bạn. Các mục
> ghi `<chốt theo dự án>` là chỗ bạn phải điền từ techspec thật.

---

## 1. Tóm tắt — 3 đề xuất lớn

| # | Đề xuất | Vì sao |
|---|---|---|
| 1 | **Vấn đề không phải thiếu bước, mà là thiếu GATE giữa các bước** | 6 bước của bạn đã đúng. Nhưng bước không chặn được lỗi — chỉ có gate (điều kiện để đi tiếp) mới chặn được |
| 2 | **Thêm 3 gate còn thiếu**: Blockout (trước Model), **Model Freeze** (trước Lock Normal), In-engine QC (sau Import) | Đặc biệt Model Freeze: Lock Normal khoá mesh lại. Sửa topology sau bước 2 = mất trắng bước 2, 3, 4 |
| 3 | **Chuyển việc bắt lỗi vặt từ Lead sang hoạ sĩ + máy** | Lead chỉ nên review thẩm mỹ và quyết định. Tricount/naming/color space là việc của checklist tự chấm và script |

**Một câu tóm tắt cả tài liệu:** *lỗi phải được bắt ở bước sinh ra nó, không phải ở bước cuối.* Một
lỗi scale bắt ở Blockout tốn 10 phút; cũng lỗi đó bắt ở Import UE5 tốn 3 ngày.

---

## 2. Vấn đề của pipeline 6 bước như hiện tại

### 2.1 Chi phí sửa lỗi tăng theo cấp số nhân

```
Bước sinh lỗi →  1.Model   2.Normal   3.UVW   4.Texture   5.Rig   6.UE5
Chi phí sửa   →    1x        2x        4x        8x       15x     30x
                   └──────────── cùng MỘT lỗi, phát hiện càng muộn càng đắt ─────────┘
```

Ví dụ thật: hoạ sĩ model xe sai tỉ lệ 10% (bánh hơi to).
- Bắt ở Blockout: sửa 15 phút.
- Bắt ở Import UE5: sửa model → normal hỏng → UV hỏng → texture phải bake lại → rig phải skin lại →
  import lại. **Mất 3–5 ngày.**

### 2.2 Điểm gãy nghiêm trọng nhất: giữa bước 1 và 2

**Lock Normal khoá mesh lại.** Sau bước 2, mọi thay đổi topology (thêm/bớt edge, weld vertex, đổi
smoothing) đều **phá custom normal** và thường phá luôn UV nếu đã làm.

Nhưng trong pipeline 6 bước của bạn, **không có gì ngăn hoạ sĩ quay lại sửa model sau bước 2.** Đây
là nguồn rework lớn nhất của mọi pipeline hard-surface.

→ Bắt buộc phải có **Gate Model Freeze**: model được duyệt và đóng băng, có chữ ký, trước khi ai đó
được phép chạm vào normal.

### 2.3 Về thứ tự Lock Normal → UVW

Thứ tự bạn chọn (normal trước, UV sau) là hợp lý cho hard-surface, vì **hard edge quyết định chỗ đặt
UV seam**. Nhưng nó sinh ra một ràng buộc phải kiểm tra ở gate 3:

> **Mọi hard edge PHẢI là UV seam.** (Chiều ngược lại thì không bắt buộc — seam có thể nằm ở soft edge.)

Vi phạm quy tắc này → tangent basis sai → normal map hiện vệt/seam đen trong UE5. Đây là lỗi hoạ sĩ
rất khó tự nhận ra vì trong Maya/Max nhìn vẫn bình thường, chỉ lộ ra trong engine.

### 2.4 Ba việc thiếu hẳn khỏi danh sách 6 bước

| Thiếu | Hậu quả |
|---|---|
| **Collision mesh** | UE5 tự sinh collision sai → xe đâm xuyên nhà, hoặc va chạm vô hình |
| **LOD chain** | Open-world không có LOD = tụt FPS. Phải quyết định LOD ở bước 1, không phải bước 6 |
| **Blockout / duyệt tỉ lệ** | Tất cả lỗi tỉ lệ và art direction dồn về cuối |

---

## 3. Pipeline đề xuất: 6 bước + 4 gate

```
        ┌─ G0 ─┐        ┌─ G1 ─┐              ┌─ G2 ─┐                    ┌─ G3 ─┐
Brief → │Block │ → 1.Model → │FREEZE│ → 2.Normal → 3.UVW → 4.Texture → │ Tech │ → 5.Rig → 6.UE5 → │In-game│ → DONE
        │ out  │        │ MESH │                    │ Check│                    │  QC   │
        └──────┘        └──────┘                    └──────┘                    └───────┘
         Lead duyệt      Lead duyệt +               Script tự động              Lead + TA
         tỉ lệ, AD       hoạ sĩ ký                  + hoạ sĩ tự chấm            trong engine thật
         (30 phút)       (KHÔNG quay lại được)      (5 phút)                    (15 phút)
```

| Gate | Đặt ở đâu | Ai duyệt | Mất bao lâu | Chặn cái gì |
|---|---|---|---|---|
| **G0 — Blockout** | Trước bước 1 | Art Lead | 30 phút | Sai tỉ lệ, sai scale, sai art direction, sai silhouette |
| **G1 — Model Freeze** | Giữa bước 1 và 2 | Lead duyệt + hoạ sĩ ký | 20 phút | Topology chưa xong, tricount vượt, thiếu LOD/collision plan |
| **G2 — Tech Check** | Sau bước 4 | **Script tự động** + hoạ sĩ tự chấm | 5 phút | Toàn bộ lỗi định lượng: UV, texel, color space, naming, resolution |
| **G3 — In-game QC** | Sau bước 6 | Lead + TA, **trong engine, ánh sáng thật** | 15 phút | Shading lỗi, LOD pop, collision sai, material sai, texture streaming |

**Nguyên tắc vận hành gate:**
- Gate **không đạt** = quay lại bước đó, **không** được đi tiếp. Không có "đi tiếp rồi sửa sau".
- G1 là gate **một chiều**: qua rồi thì mọi thay đổi model phải mở "yêu cầu thay đổi" có Lead duyệt,
  vì nó kéo theo làm lại bước 2-3-4.
- G2 do máy chạy → không tốn thời gian Lead, chạy được bao nhiêu lần cũng được.
- G3 bắt buộc **trong engine**. Rất nhiều lỗi chỉ lộ ra ở đây.

---

## 4. Chi tiết từng bước: định nghĩa DONE + lỗi hay gặp

Đây là phần cần bạn điền số thật vào và biến thành checklist phát cho hoạ sĩ.

### G0 — Blockout (thêm mới)

| Hạng mục | Tiêu chí DONE | Lỗi hay gặp |
|---|---|---|
| Scale thật | Đặt cạnh mannequin/xe chuẩn để so | Xe cao 1.4 m thành 14 m (nhầm đơn vị) |
| Tỉ lệ | Khớp ref trong sai số cho phép | Bánh to, cabin lệch — nhìn quen mắt nên không nhận ra |
| Silhouette | Nhìn từ 4 hướng, đen hoàn toàn vẫn nhận ra vật thể | Chỉ đẹp từ 1 góc |
| Vị trí pivot dự kiến | Đã xác định | Sửa pivot sau khi rig = làm lại rig |

> Chi phí: 30 phút. Tiết kiệm: trung bình 1–3 ngày mỗi asset bị sai tỉ lệ.

---

### Bước 1 — Model

| Hạng mục | Tiêu chí DONE | Lỗi hay gặp | Ai check |
|---|---|---|---|
| Đơn vị & scale | Đúng đơn vị dự án (UE5 dùng **cm**) | Maya/Max để đơn vị khác → import vào UE5 sai 100× | Script |
| Transform | Freeze xong: scale = 1,1,1 · rotation = 0 | Scale âm → mesh lộn trong ngoài | Script |
| Pivot | Đúng quy ước dự án `<chốt theo dự án>` | Pivot ở giữa mesh thay vì ở đáy/tâm bánh | Script |
| Tricount | ≤ budget theo class + LOD | Đếm nhầm Faces thay vì Tris | Script |
| Topology sạch | Không n-gon (trừ chỗ được phép), không non-manifold, không face lật, không vertex trùng | Weld sót → hở mesh chỉ thấy trong engine | Script |
| Hierarchy & naming | Đúng convention `<chốt theo dự án>` | Tên `pCube127`, `Box001` lọt vào asset final | Script |
| **LOD plan** | Đã quyết định số LOD + cách sinh (tay/tự động/Nanite) | Để đến bước 6 mới nghĩ tới | Lead |
| **Collision mesh** | Đã có hoặc đã ghi rõ dùng auto-collision | Không có → UE5 sinh collision sai | Lead |

---

### G1 — Model Freeze (gate quan trọng nhất)

Điều kiện qua gate:
- [ ] Toàn bộ checklist bước 1 pass
- [ ] Lead đã xem model trong viewport và duyệt
- [ ] Hoạ sĩ **ký xác nhận**: "tôi xác nhận model đã xong, hiểu rằng sửa topology sau đây phải xin duyệt"
- [ ] File model được lưu bản `_freeze` riêng, không ghi đè

> Chữ ký không phải thủ tục hành chính. Nó chuyển trách nhiệm: hoạ sĩ tự kiểm trước khi ký, thay vì
> ném cho Lead bắt lỗi. Đây là thay đổi tâm lý quan trọng nhất của cả hệ thống.

---

### Bước 2 — Lock Normal

| Hạng mục | Tiêu chí DONE | Lỗi hay gặp |
|---|---|---|
| Đã qua G1 | Bắt buộc | Lock normal trên model chưa duyệt → làm lại toàn bộ |
| Hard edge / smoothing group | Đúng quy ước dự án | Bo góc quá gắt → shading vỡ |
| Custom / weighted normal | Đã áp, kết quả shading sạch | Quên áp cho LOD thấp → LOD1 shading khác LOD0, thấy rõ khi pop |
| Ghi nhận hard edge | Danh sách hard edge được giữ để đối chiếu ở bước 3 | Không ghi → không kiểm được quy tắc hard edge ⊂ UV seam |
| Kiểm tra bằng matcap/chrome | Xoay 360°, không có vệt lạ | Chỉ nhìn với shader mặc định → không thấy lỗi |

---

### Bước 3 — UVW

| Hạng mục | Tiêu chí DONE | Lỗi hay gặp |
|---|---|---|
| **Texel density** | Đồng nhất theo class `<chốt: px/cm>` | **Lỗi số 1 của open-world.** Nhà nét, cột đèn cạnh nó mờ — người chơi thấy ngay |
| **Hard edge ⊂ UV seam** | Mọi hard edge đều là seam | Vi phạm → normal map hiện seam đen trong UE5 |
| Overlap UV channel 0 | Không overlap (trừ mirror có chủ đích, đã khai báo) | Overlap ngoài ý muốn → bake lỗi |
| UV nằm trong 0–1 | Đúng (trừ tiling/UDIM có chủ đích) | UV tràn → texture lặp sai |
| Padding / gutter | Đủ theo resolution `<chốt: px>` | Thiếu padding → bleed màu ở mip thấp |
| **UV channel 1 (lightmap)** | Có/không tuỳ hệ ánh sáng dự án `<chốt: Lumen động hay bake tĩnh>` | Dự án bake mà thiếu channel 1 → phải làm lại toàn bộ asset |
| Hướng UV | Thẳng hàng với hướng vân/anisotropy nếu có | Vân gỗ/kim loại chạy sai hướng |

---

### Bước 4 — Texture

| Hạng mục | Tiêu chí DONE | Lỗi hay gặp |
|---|---|---|
| **Normal map convention** | **UE5 dùng DirectX (Y−, green channel hướng xuống)** | Xuất OpenGL (Y+) từ Substance/Blender → lồi lõm ngược. Rất hay gặp, khó nhận ra |
| **Color space** | BaseColor = sRGB · Normal/Roughness/Metallic/AO/Mask = **Linear** | Roughness để sRGB → vật liệu nhìn sai hẳn |
| **Channel packing** | Đúng quy ước dự án `<chốt: ORM? RMA? kênh nào là gì>` | Mỗi hoạ sĩ pack một kiểu → material không dùng chung được |
| Resolution | Luỹ thừa của 2, ≤ budget theo class | 1500×1500 → UE5 không nén được tối ưu |
| Số material slot | ≤ budget `<chốt theo dự án>` | Mỗi slot = 1 draw call. Open-world rất nhạy với con số này |
| Naming texture | `T_<Asset>_BC` / `_N` / `_ORM` `<chốt theo dự án>` | Sai tên → không tự gán material được |
| Bake sạch | Không artifact, cage đúng, ray distance đúng | Bake lỗi ở góc lõm, ai cũng bỏ qua vì "nhìn xa không thấy" |
| Kiểm tra ở nhiều ánh sáng | Xem ở ít nhất 3 HDRI khác nhau | Chỉ đẹp trong 1 điều kiện sáng |

---

### G2 — Tech Check (chạy bằng script)

Đây là gate **không tốn thời gian Lead**. Script quét file, xuất báo cáo pass/fail. Hoạ sĩ tự chạy
bao nhiêu lần tuỳ ý trước khi submit.

Những gì script kiểm được (~80% lỗi kỹ thuật):
`scale/transform` · `tricount` · `naming` · `n-gon / non-manifold / face lật` · `UV overlap` ·
`UV ngoài 0-1` · `texel density` · `số UV channel` · `resolution texture` · `power of 2` ·
`color space` · `số material slot` · `thiếu file trong bộ texture`

Những gì script **không** kiểm được (vẫn cần người): thẩm mỹ · silhouette · hard edge đặt hợp lý chưa ·
bake artifact · texel density có *hợp lý* không (khác với có *đồng nhất* không).

---

### Bước 5 — Rigging

| Hạng mục | Tiêu chí DONE | Lỗi hay gặp |
|---|---|---|
| Bone naming | Đúng convention `<chốt theo dự án>` | Sai tên → animation không retarget được |
| Root bone | Ở origin, đúng hướng trục | Root lệch → xe chạy lệch trong game |
| Joint orientation | Nhất quán | Rotation trong engine không như ý |
| Scale trong rig | = 1 ở mọi joint | Scale ≠ 1 → deform sai khi animate |
| Số influence / vertex | ≤ giới hạn dự án `<chốt: UE5 mặc định 8, cấu hình được>` | Vượt → UE5 tự cắt bớt, deform khác trong DCC |
| **Cấu trúc bánh xe** | Khớp với hệ vehicle của engine `<chốt: Chaos Vehicle setup>` | Hierarchy bánh sai → không gắn được vào vehicle blueprint |
| Bind pose | Đúng, lưu lại được | Bind pose sai → không rebind được về sau |
| Kiểm tra deform | Xoay hết biên độ, không thấy vỡ mesh | Chỉ test ở tư thế mặc định |
| **Normal sau skinning** | Vẫn giữ được custom normal | Với xe (rigid) thường ổn; cần kiểm tra chỗ có deform |

---

### Bước 6 — Import UE5

| Hạng mục | Tiêu chí DONE | Lỗi hay gặp |
|---|---|---|
| **Import Normals** | Chọn **"Import Normals and Tangents"** | Để mặc định "Compute Normals" → **UE5 tính lại normal, xoá sạch công của bước 2** |
| Export tangent từ DCC | FBX đã bật export tangent/binormal | Không có tangent → UE5 tự tính → normal map lệch |
| Scale khi import | = 1 (nếu DCC đã đúng cm) | Ra 100× hoặc 0.01× |
| **Texture compression** | Normal map đặt **TC_Normalmap** | Để mặc định → normal map bị nén sai, nhìn bệt |
| sRGB checkbox | Tắt cho normal/roughness/mask | Bật nhầm → vật liệu sai |
| Material slot | Số lượng và thứ tự khớp DCC | Lệch thứ tự → gán nhầm material |
| LOD | Import đúng LOD chain, hoặc bật Nanite theo quy định `<chốt theo dự án + phiên bản engine>` | Bật Nanite cho asset không phù hợp |
| Collision | Đã có hoặc đã cấu hình auto đúng | Thiếu → nhân vật/xe xuyên vật thể |
| Lightmap resolution | Đúng theo class `<chốt theo dự án>` | Để mặc định → bóng vỡ hoặc tốn bộ nhớ |
| Folder & naming trong UE5 | Đúng cấu trúc dự án | Đặt sai chỗ → pipeline/script không tìm thấy |

---

### G3 — In-game QC (trong engine, ánh sáng thật)

| Kiểm gì | Cách kiểm |
|---|---|
| Shading | Xoay quanh asset dưới ánh sáng level thật, tìm seam/vệt |
| LOD pop | Lùi camera từ từ, xem chuyển LOD có giật hình không |
| Texture streaming | Vào gần/ra xa nhanh, xem texture có bị mờ lâu |
| Collision | Lái xe/đi bộ đâm vào từ nhiều hướng |
| Performance | Xem stat: draw call, tris, texture memory của riêng asset |
| Đặt cạnh asset đã duyệt | So texel density và tông màu với hàng xóm |

> **Bước này không được bỏ.** Rất nhiều lỗi (đặc biệt nhóm normal/tangent và LOD) chỉ tồn tại trong
> engine, không tồn tại trong DCC.

---

## 5. Bảy cơ chế quản lý

Checklist thôi chưa đủ. Đây là các cơ chế làm cho checklist thực sự được dùng.

### 5.1 Golden Asset — asset chuẩn vàng

Chọn **1 asset mỗi class**, làm đúng 100%, đi hết 6 bước, lưu đủ file trung gian của **từng bước**.

| Dùng làm gì | Cách dùng |
|---|---|
| Onboarding | Hoạ sĩ mới mở file của từng bước, thấy "đúng" trông như thế nào |
| Giải quyết tranh cãi | "Làm sao mới đúng?" → mở golden asset ra xem, không cãi nhau |
| Test khi đổi pipeline | Đổi engine/plugin → chạy lại golden asset, biết ngay có gãy gì |

Chi phí: 2–3 ngày cho asset đầu tiên. **Đây là khoản đầu tư sinh lời cao nhất trong toàn bộ danh sách này.**

### 5.2 Checklist tự chấm + chữ ký

Mỗi gate có 1 form. **Hoạ sĩ tự tick, tự ký, rồi mới submit.**

Vì sao hiệu quả: nó đổi câu hỏi trong đầu hoạ sĩ từ *"Lead có bắt được không?"* thành *"tôi có dám ký
không?"*. Hai câu hỏi đó dẫn tới hai hành vi hoàn toàn khác nhau.

Quy tắc kèm theo: **Lead không bắt lỗi có trong checklist.** Nếu Lead phát hiện lỗi mà hoạ sĩ đã tick
"đạt" → trả về ngay, không sửa hộ, không góp ý chi tiết. Làm 2–3 lần là hoạ sĩ tự giác.

### 5.3 Validator tự động ở 2 điểm

| Điểm | Chạy ở đâu | Bắt gì |
|---|---|---|
| **Export** | Script trong Maya/Max/Blender, chạy khi hoạ sĩ bấm Export | Scale, transform, tricount, naming, topology, UV |
| **Import** | UE5 Data Validation / Editor Utility | Compression, material slot, LOD, collision, lightmap |

Ưu tiên làm **validator export trước** — nó chặn lỗi sớm hơn và bao phủ nhiều bước hơn.

> Không cần hoàn hảo ngay. Bắt đầu với 5 kiểm tra hay sai nhất, thêm dần mỗi khi phát hiện lỗi mới.

### 5.4 Error Log — vòng lặp học từ lỗi

Mỗi lần một lỗi bị bắt (ở bất kỳ gate nào), ghi 1 dòng:

| Ngày | Asset | Bước sinh lỗi | Bước phát hiện | Mô tả lỗi | Giờ mất |
|---|---|---|---|---|---|

Mỗi tháng đọc lại, và làm 3 việc:
1. Lỗi lặp ≥ 3 lần → thêm vào **checklist**
2. Lỗi máy kiểm được → thêm vào **validator**
3. Lỗi do hiểu sai spec → sửa lại **cách viết spec** (thêm ví dụ, thêm "cách đo")

> Cột **"Bước sinh lỗi" vs "Bước phát hiện"** là cột giá trị nhất. Khoảng cách giữa hai cột chính là
> chỗ quy trình đang rò rỉ. Nếu lỗi model toàn bị phát hiện ở bước 6 → gate G1 đang không hoạt động.

### 5.5 Onboarding bằng "asset tập"

Hoạ sĩ mới **không** vào asset thật ngay. Làm 1 asset nhỏ (vd 1 cột đèn, 1 thùng rác) đi **hết 6 bước
+ 4 gate**, có Lead kèm.

Mất 2–3 ngày, đổi lại: hoạ sĩ hiểu toàn bộ pipeline bằng tay, không phải bằng cách đọc tài liệu.
So với việc để họ tự mò trên asset thật rồi hỏng, đây là lựa chọn rẻ hơn nhiều.

### 5.6 Review sớm, nhẹ — thay vì review muộn, nặng

| Cách cũ | Cách đề xuất |
|---|---|
| 1 lần review lớn ở cuối, 1–2 giờ | 4 gate ngắn: 30 + 20 + 5 + 15 phút |
| Lead thành cổ chai | Lead phân bố đều, G2 do máy chạy |
| Phát hiện lỗi khi đã quá muộn | Lỗi bị bắt ngay ở bước sinh ra nó |

Tổng thời gian Lead bỏ ra **ít hơn**, vì không phải xử lý rework.

### 5.7 Asset Tracker — bảng theo dõi trạng thái

Một bảng duy nhất, mỗi asset một dòng, mỗi bước/gate một cột:

| Asset | G0 | 1.Model | G1 | 2.Normal | 3.UVW | 4.Texture | G2 | 5.Rig | 6.UE5 | G3 |
|---|---|---|---|---|---|---|---|---|---|---|
| SUV_A | ✅ | ✅ | ✅ | ✅ | 🔄 | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ |
| Prop_Barrier | ✅ | ✅ | ❌ | — | — | — | — | — | — | — |

Nhìn 5 giây biết: ai đang làm gì, asset nào tắc, gate nào đang trả về nhiều nhất.

Công cụ: Google Sheet là đủ để bắt đầu. Chỉ chuyển sang ShotGrid/ftrack khi Sheet thật sự không đủ.

---

## 6. Đo lường — làm sao biết quy trình có hiệu quả

Không đo thì không biết cải tiến có tác dụng hay không. Bốn chỉ số, đo hàng tháng:

| Chỉ số | Cách tính | Ý nghĩa |
|---|---|---|
| **First-time pass rate** theo gate | % asset qua gate ngay lần đầu | Gate nào < 60% → spec ở bước đó viết chưa rõ, không phải hoạ sĩ kém |
| **Rework rate** | % asset phải quay lại bước trước | Chỉ số đắt nhất. Mục tiêu: giảm liên tục |
| **Khoảng cách sinh lỗi ↔ phát hiện** | Trung bình số bước | Càng gần 0 càng tốt. Xa = gate đang không hoạt động |
| **Giờ rework / tháng** | Cộng từ Error Log | Con số nói chuyện được với producer |

**Cách đọc kết quả:**
- Một gate có pass rate thấp và **lỗi tập trung vào cùng vài hạng mục** → lỗi tại spec, sửa spec.
- Một gate có pass rate thấp nhưng **lỗi phân tán** → lỗi tại đào tạo, làm lại onboarding.
- Một hoạ sĩ có pass rate thấp hơn hẳn cả nhóm → kèm riêng, đừng đổi quy trình cho cả team.

---

## 7. Nối vào MCP server

Tài liệu này và [`NGHIEN_CUU_MCP_ARTSPEC.md`](NGHIEN_CUU_MCP_ARTSPEC.md) khớp trực tiếp vào nhau:

| Thứ tạo ra ở tài liệu này | Trở thành gì trong MCP |
|---|---|
| Checklist mỗi gate | Tool `get_checklist(asset_class, stage)` — `stage` = tên gate |
| Bảng "Định nghĩa DONE" từng bước | Các record `rules/` trong Spec Registry |
| Cột "Lỗi hay gặp" | Field `common_mistakes` của từng rule |
| Cột "Cách check" | Field `how_to_check` |
| Error Log | Nguồn cập nhật `common_mistakes` hàng tháng |
| Validator export/import | Chia sẻ chung một nguồn số liệu với tool `check_asset` |

> **Thứ tự làm đúng:** quy trình trước → checklist trước → MCP sau. MCP chỉ là cách phục vụ checklist
> nhanh hơn. Chưa có checklist thì chưa có gì để MCP phục vụ.

---

## 8. Việc làm ngay (theo thứ tự)

| Tuần | Việc | Kết quả |
|---|---|---|
| 1 | Điền số thật vào 6 bảng ở [mục 4](#4-chi-tiết-từng-bước-định-nghĩa-done--lỗi-hay-gặp) — chỉ cho **1 asset class** thí điểm | 6 checklist dùng được ngay |
| 1 | Mở **Error Log** (1 Google Sheet, 6 cột) | Bắt đầu có dữ liệu |
| 2–3 | Làm **Golden Asset** cho class đó, lưu file từng bước | Chuẩn tham chiếu |
| 2 | Thêm **Gate G1 Model Freeze** vào quy trình, có form ký | Chặn nguồn rework lớn nhất |
| 3–4 | Viết **validator export** với 5 kiểm tra hay sai nhất | G2 chạy tự động |
| 4 | Dựng **Asset Tracker** | Nhìn được toàn cảnh |
| 5+ | Chạy 1 tháng, đọc Error Log, chỉnh checklist | Bắt đầu vòng lặp cải tiến |
| Sau đó | Chuẩn hoá checklist thành YAML → **bắt đầu làm MCP** | Xem tài liệu MCP |

**Thứ tự ưu tiên nếu chỉ làm được 3 việc:** ① Gate Model Freeze · ② Golden Asset · ③ Error Log.
Ba thứ này không cần code, không cần công cụ mới, và chặn được phần lớn rework.

---

## 9. Những chỗ cần bạn chốt

Các mục `<chốt theo dự án>` rải trong tài liệu, gom lại:

**Kỹ thuật:**
1. Đơn vị và quy ước pivot của dự án?
2. Texel density chuẩn theo từng class? (px/cm)
3. Hệ ánh sáng: Lumen động hay bake tĩnh? → quyết định có cần UV channel 1 hay không
4. Channel packing convention? (ORM / RMA / khác)
5. Naming convention cho mesh, texture, bone, material?
6. Giới hạn số influence/vertex khi skin?
7. Chính sách Nanite: class nào bật, class nào không? (theo phiên bản engine dự án dùng)
8. Budget: tricount / texture resolution / material slot theo từng class?

**Quy trình:**
9. Asset class nào làm thí điểm? (gợi ý: class có nhiều asset nhất, không phải class khó nhất)
10. Ai được quyền duyệt gate G1 khi bạn bận?
11. Team có ai viết được script Python cho Maya/Max/Blender không?

---

## Phụ lục: bảng tự chấm mẫu (G1 — Model Freeze)

In ra hoặc làm form, hoạ sĩ tick trước khi submit:

```
ASSET: ______________________  HOẠ SĨ: ______________  NGÀY: __________

[ ] Đơn vị đúng, scale đúng thực tế (đã so với ref chuẩn)
[ ] Transform đã freeze: scale = 1,1,1 · rotation = 0
[ ] Pivot đúng quy ước
[ ] Tricount: ______ / budget ______  → đạt
[ ] Không n-gon (trừ chỗ được phép), không non-manifold, không face lật
[ ] Không vertex trùng (đã weld kiểm tra)
[ ] Naming + hierarchy đúng convention
[ ] Đã quyết định LOD: số lượng ______ · cách sinh ____________
[ ] Đã quyết định collision: ____________
[ ] Tôi đã tự kiểm tra toàn bộ mục trên và xác nhận model ĐÃ XONG.
    Tôi hiểu rằng sau gate này, mọi thay đổi topology phải xin duyệt.

CHỮ KÝ HOẠ SĨ: ____________     LEAD DUYỆT: ____________
```
