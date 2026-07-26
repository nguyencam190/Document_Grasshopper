---
name: phan-tich-video-step-by-step
description: Quy trình phân tích 1 video hoặc 1/nhiều hình ảnh hướng dẫn dựng nguyên 1 mẫu/pattern Grasshopper (khác với tài liệu 1 component đơn lẻ) và viết thành 1 trang con trong "Example Step-by-Step" của Grasshopper.html. Bao gồm cách đọc video không xem trực tiếp được (trích frame bằng ffmpeg, đọc phụ đề .srt), nguyên tắc nghiên cứu kỹ + kết hợp toàn bộ graph rải rác qua nhiều ảnh/frame thành 1 hướng dẫn tổng hợp duy nhất, kiểm tra trùng nội dung trước khi phân tích, và cấu trúc trang cha/con. LUÔN dùng skill này khi user yêu cầu "phân tích step-by-step", "phân tích video này", gửi hình ảnh canvas Grasshopper kèm ý muốn được hướng dẫn cách làm/dựng lại, hoặc đưa 1 video/mẫu dựng sẵn muốn đúc kết thành quy trình từng bước. Không dùng cho tài liệu tham khảo 1 component đơn lẻ (dùng nghien-cuu-grasshopper + xuat-ban-trang-doc).
---

# Phân tích video dựng pattern — Example Step-by-Step

## Đọc video khi không xem trực tiếp được

- Dùng ffmpeg trích frame ra ảnh để đọc canvas Grasshopper trong video (không xem video trực tiếp
  được).
- Nếu video có lời giảng, cần file phụ đề `.srt` đi kèm (user cung cấp) — đọc phụ đề để nắm lời giảng,
  không nghe được audio. Ưu tiên thông tin từ lời giảng hơn suy đoán từ hình khi có mâu thuẫn (vd giá
  trị slider chính xác, mục đích 1 bước — hình chỉ cho thấy TRẠNG THÁI, lời giảng giải thích LÝ DO).

## Nghiên cứu kỹ + kết hợp TOÀN BỘ graph trước khi viết hướng dẫn — bắt buộc

> ⚠️ Áp dụng mỗi khi user gửi hình ảnh (1 hoặc nhiều ảnh canvas GH) hoặc muốn xem video để **hướng
> dẫn cách làm** 1 mẫu/pattern — không riêng lệnh "phân tích step-by-step".

- **Nghiên cứu thật kỹ trước khi viết** — không dừng lại ở lần xem đầu tiên/ấn tượng ban đầu về 1
  frame hay 1 ảnh. Đọc kỹ từng chi tiết nhìn thấy được (tên component, giá trị input, cách nối dây)
  trước khi kết luận.
- **Xem xuyên suốt TẤT CẢ hình/frame có được, không chỉ 1-2 ảnh đại diện** — nếu có nhiều frame từ
  video hoặc nhiều ảnh user gửi, đối chiếu trạng thái graph ở nhiều thời điểm khác nhau (đầu, giữa,
  cuối quy trình) để thấy rõ graph thay đổi thế nào qua từng bước, không chỉ chốt hiểu theo 1 khung
  hình duy nhất.
- **Kết hợp (ghép) tất cả các graph thành 1 bức tranh hoàn chỉnh** — khi thông tin về definition nằm
  rải rác qua nhiều frame/ảnh khác nhau (mỗi ảnh chỉ thấy 1 phần canvas, hoặc canvas thay đổi dần qua
  các bước), phải tự ghép lại thành sơ đồ dây đầy đủ của toàn bộ quy trình trước khi viết hướng dẫn —
  không viết hướng dẫn rời rạc kiểu "ảnh 1 cho thấy X, ảnh 2 cho thấy Y" mà không tổng hợp lại.
- **Mục tiêu cuối cùng: 1 bản hướng dẫn DUY NHẤT, tối ưu nhất và dễ hiểu nhất** về cách làm ra kết quả
  đó — trình bày thành 1 trình tự logic mạch lạc từ đầu tới cuối (không liệt kê nhiều phương án rời
  rạc, không mô tả tách rời theo từng ảnh nguồn). Đây là mục đích chính của việc "kết hợp tất cả các
  graph": biến nhiều nguồn quan sát rời rạc thành 1 quy trình dựng rõ ràng, dễ làm theo nhất.

> ⚠️ **TUYỆT ĐỐI KHÔNG ĐƯỢC BỊA ĐẶT HƯỚNG DẪN SAI** — quy tắc quan trọng nhất của skill này, đứng
> trên cả yêu cầu "hướng dẫn tối ưu/dễ hiểu nhất" ở trên. "Tổng hợp/kết hợp toàn bộ graph" nghĩa là
> GHÉP LẠI đúng những gì thực sự quan sát được qua các ảnh/frame — KHÔNG PHẢI tự bịa thêm bước, tự
> đoán tên component, hay tự suy diễn giá trị input/kết nối để lấp chỗ trống cho hướng dẫn "nghe có
> vẻ mượt/hợp lý hơn". User sẽ dùng hướng dẫn này để dựng lại graph thật trên Grasshopper — 1 bước
> bịa sai (tên component sai, thứ tự nối dây sai, giá trị slider bịa) khiến cả chuỗi graph phía sau
> sai theo, và user debug oan uổng nhiều giờ mà không biết lỗi bắt đầu từ đâu vì tin tưởng hướng dẫn
> là đúng 100%. Khi 1 đoạn/1 bước không đọc rõ được (mờ, bị che, thiếu frame, phụ đề không nhắc tới):
> - Ghi thẳng trong hướng dẫn là **"không xác định được — [lý do cụ thể]"** ngay tại bước đó, không
>   bỏ qua im lặng và cũng không điền đại 1 giá trị/component có vẻ hợp lý để hướng dẫn liền mạch hơn.
> - Nếu suy luận được từ ngữ cảnh xung quanh (vd theo lời giảng, theo kết quả hình học cuối cùng),
>   phải ghi rõ đây là **suy luận**, tách bạch với phần **quan sát trực tiếp** được từ hình/frame —
>   không trộn lẫn 2 loại thông tin này làm 1 khiến user tưởng tất cả đều đã xác nhận chắc chắn.
> - Thà 1 bản hướng dẫn có vài chỗ ghi "không chắc chắn" còn hơn 1 bản hướng dẫn mượt mà nhưng có chi
>   tiết bịa — độ chính xác luôn quan trọng hơn độ mượt/đầy đủ của hướng dẫn.

## Vị trí trang trong app — khác hẳn trang component đơn lẻ

Nội dung **step-by-step dựng nguyên 1 mẫu/pattern** đi vào **1 trang cha riêng, ngang hàng với trang
gốc "Grasshopper"** — KHÔNG áp dụng quy tắc phân loại theo 13 tab/panel GH (đó là của skill
`xuat-ban-trang-doc`, dùng cho tài liệu 1 component; ở đây là quy trình phối hợp nhiều component).

- id trang cha: `seed-step-by-step`, title: **"Example Step-by-Step"**, `parentId: null`.
- Khi user yêu cầu **"phân tích step-by-step"** cho 1 mẫu/video mới, luôn tạo **1 trang con mới bên
  trong `seed-step-by-step`** (`parentId:'seed-step-by-step'`), đặt tên theo mẫu
  `[Tên mẫu] — Quy trình dựng từng bước`.

## Bắt buộc kiểm tra trùng nội dung trước khi phân tích

Không chỉ kiểm tra trùng TÊN — khi user đưa 1 mẫu mới để phân tích:

1. Trích xuất nội dung của **toàn bộ trang con hiện có** trong `seed-step-by-step` (lấy từ
   `Grasshopper.html`/`SEED_DOCS`).
2. So sánh xem quy trình/pattern đó có giống (hoặc rất tương tự) 1 trang đã phân tích trước đó không
   — không chỉ so tên mẫu, mà so cả cách dựng (chuỗi component, thuật toán) mô tả bên trong.
3. Nếu phát hiện giống, **DỪNG LẠI, không phân tích lại từ đầu** — báo ngay cho user theo mẫu:
   **"Mẫu này giống với phân tích đã có — trang '[title trang con]' trong Example Step-by-Step, xem
   ở đây."** rồi hỏi user có muốn cập nhật/bổ sung trang cũ hay tạo trang mới riêng vì thực ra khác
   biệt.
4. Chỉ tiến hành phân tích + tạo trang mới khi xác nhận chưa có nội dung nào tương tự.

## Sau khi phân tích xong

Trang con viết theo nhu cầu thực tế của quy trình dựng (không bắt buộc đúng khuôn 11 mục như trang
component đơn lẻ) — thường gồm: sơ đồ luồng tổng quan, danh sách component dùng tới, bảng giá trị
slider/tham số chính, hướng dẫn dựng từng bước, và các điểm bổ sung rút ra từ lời giảng (nếu có phụ
đề). Ảnh minh hoạ dùng skill `xuat-ban-hinh-minh-hoa` (SVG tự vẽ theo phong cách canvas GH thật,
KHÔNG dùng khung chụp trực tiếp từ video nếu chưa xác nhận được quyền sử dụng). Nhớ bump
`SEED_VERSION` và merge vào `main` theo `Git workflow` ở `CLAUDE.md` sau khi xong.

> ⚠️ **3 THÀNH PHẦN BẮT BUỘC — MỌI trang step-by-step đều PHẢI có đủ, không được thiếu:**
> 1. **Hướng dẫn dựng TỪNG BƯỚC** — danh sách số (`<ol>`), mỗi bước 1 hành động rõ ràng: thả
>    component gì, nối cổng nào vào cổng nào, đặt slider bao nhiêu. Không viết gộp cả quy trình thành
>    1 đoạn văn; phải tách thành các bước làm theo được ngay trên canvas.
> 2. **Hình minh hoạ KÉO GRAPH** — ít nhất 1 ảnh SVG vẽ theo phong cách **canvas Grasshopper thật**
>    (khối component bo góc có núm input/output, dây nối cong, tên cổng) thể hiện **cách nối dây các
>    component** của quy trình — KHÔNG chỉ có sơ đồ luồng dạng hộp-mũi tên chung chung hay ảnh kết
>    quả hình học. Sơ đồ luồng/storyboard hình học là bổ sung tốt, nhưng KHÔNG thay thế được ảnh kéo
>    graph: người mới cần thấy đúng component nào nối với component nào trên canvas để làm theo. Nếu
>    quy trình dài, chia thành nhiều ảnh kéo graph theo từng cụm bước (storyboard nối dây). Xem cách
>    vẽ khối component + dây nối ở skill `xuat-ban-hinh-minh-hoa`.
> 3. **Dòng "→ Kết quả" ở MỖI bước** — ngay sau nội dung mỗi bước (mỗi `<li>` top-level) phải có 1
>    dòng note nói **bước đó tạo ra kết quả/hình học gì** (vd "→ Kết quả: 15 tia xoè đều 360° quanh
>    tâm", "→ Kết quả: lưới ô Voronoi gọn trong vòng tròn"). Người mới cần biết mỗi thao tác dẫn tới
>    trạng thái nào để tự đối chiếu khi làm. Chuẩn markup dùng thống nhất (nền xanh nhạt, viền trái):
>    `<div style="margin:5px 0 3px;padding:3px 10px;border-left:3px solid #4a90d9;background:rgba(74,144,217,0.09);font-size:13px">→ <strong>Kết quả:</strong> …</div>` — đặt TRƯỚC `</li>` của
>    đúng bước đó (với danh sách lồng, đặt ở `</li>` cấp cao nhất, không nhét vào từng sub-bullet).
>
> Thiếu 1 trong 3 thành phần này coi như trang chưa hoàn thành. (Trang chỉ có sơ đồ luồng + ảnh kết
> quả mà thiếu ảnh kéo graph cụ thể, hoặc bước không có dòng "→ Kết quả", đều là lỗi đã từng mắc.)

> ⚠️ **PHẢI thể hiện cờ DATA TREE trên cổng (Flatten / Graft / Simplify / Reverse)** — đây là thiếu
> sót từng mắc (vẽ graph mà bỏ qua Flatten). Các cờ này bật/tắt trên từng input/output (hiện ở GH bằng
> icon nhỏ trên núm cổng: ↓ = Flatten, ⤴ = Graft...) và **quyết định graph chạy đúng hay sai** — vd
> `Divide Curve` output bật Flatten, `Boundary Surfaces` input Edges bật Flatten. Khi dựng trang từ 1
> graph thật:
> - Nếu có **file .gh/.ghx**: parse ra để đọc chính xác cổng nào bật cờ gì. File .ghx là XML — mỗi
>   param lưu `<item name="Mapping">` (1=Flatten, 2=Graft) và `Simplify`/`Reverse` (bool). File .gh
>   nhị phân thì giải nén bằng `zlib.decompress(data, -15)` (deflate raw) rồi mới đọc. LUÔN xin file
>   .ghx khi user muốn bản ghi chính xác — đọc file thật gần như 100%, hơn hẳn đọc ảnh chụp bằng mắt.
> - Trên **ảnh kéo graph**: vẽ 1 badge nhỏ (vd ô đỏ có ↓) ngay tại cổng có Flatten/Graft, và **ghi rõ
>   trong bước tương ứng** ("input Edges của Boundary Surfaces bật Flatten"). Bỏ qua cờ = hướng dẫn
>   sai, user dựng theo sẽ ra data tree lệch.

> ⚠️ **TUYỆT ĐỐI KHÔNG SÓT component NÀO hay slider NÀO đã nối trong file .ghx** — khi dựng trang từ
> 1 file .gh/.ghx thật, ảnh kéo graph + hướng dẫn phải phản ánh **ĐẦY ĐỦ** mọi object và mọi slider có
> dây nối, không được lược bớt "cho gọn". Đây là lỗi từng mắc (vẽ thiếu component/slider so với file
> gốc). Quy trình bắt buộc để đảm bảo không sót:
> - **Liệt kê TOÀN BỘ object trước khi vẽ**: parse file đếm hết `<chunk name="Object">` (component) và
>   mọi `Number Slider`/`Panel`/`Value List` — lập danh sách đầy đủ (tên + InstanceGuid + giá trị).
> - **Bám theo mọi kết nối (`Source`)**: mỗi input param có thể có nhiều `<item name="Source">` (GUID
>   nguồn) — theo hết từng dây, không bỏ dây nào. Slider nào có GUID xuất hiện trong 1 `Source` = slider
>   ĐÃ NỐI, bắt buộc vẽ; chỉ được bỏ qua object hoàn toàn KHÔNG có dây (rời rạc, disabled) và phải nói rõ.
> - **Đối chiếu số lượng sau khi vẽ**: đếm lại số component + số slider trong ảnh/hướng dẫn PHẢI KHỚP số
>   đã liệt kê từ file (trừ các object rời đã ghi chú). Lệch số = còn sót, phải bổ sung trước khi publish.
> - Nếu graph quá lớn để vẽ trong 1 ảnh, **chia nhiều ảnh kéo graph** (theo cụm) nhưng tổng các ảnh vẫn
>   phải phủ hết 100% object + slider đã nối — chia nhỏ KHÔNG phải lý do để bỏ bớt.

## Case study đã có sẵn — Voronoi Pattern

Xem mục "Case study: Voronoi Pattern" ở cuối `CLAUDE.md` cho ví dụ đầy đủ đã hoàn thành (pattern hoa
hướng dương/xoắn ốc) — kể cả danh sách file phân tích liên quan (`docs/voronoi-*.md`,
`docs/voronoi-*.svg`) có thể tham chiếu khi phân tích mẫu mới liên quan tới Mesh/Triangulation/
Voronoi/Attractor.
