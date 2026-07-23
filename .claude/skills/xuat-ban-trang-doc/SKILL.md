---
name: xuat-ban-trang-doc
description: Quy trình thêm 1 trang component MỚI (hoặc cập nhật 1 trang đã có) vào app "Project Docs" (`Grasshopper.html`, biến `SEED_DOCS`) — kiểm tra trùng lặp, phân loại đúng tab/panel ribbon thật, viết đủ 11 mục theo chuẩn HTML canvas, cập nhật bảng tổng hợp panel cha, khoá trang, bump SEED_VERSION. LUÔN dùng skill này khi user yêu cầu "thêm trang", "viết doc cho", "publish", "cập nhật trang" cho 1 component Grasshopper cụ thể — sau khi đã nghiên cứu nội dung bằng skill `nghien-cuu-grasshopper`. Không dùng cho việc chỉ trả lời trong chat (đó là việc của `nghien-cuu-grasshopper`) hay cho trang "Example Step-by-Step" (dùng skill `phan-tich-video-step-by-step`).
---

# Xuất bản trang component vào Project Docs

Skill này chỉ lo phần **"ghi vào `Grasshopper.html`"** sau khi nội dung đã được nghiên cứu đầy đủ
theo skill `nghien-cuu-grasshopper` (11 mục, không bịa đặt, ưu tiên nguồn chính thức). Nếu chưa
nghiên cứu, chạy skill đó trước.

## File duy nhất cần sửa

`Grasshopper.html` là **app sống đầy đủ** (không phải bản xuất tĩnh) — sửa trực tiếp file này, biến
`SEED_DOCS`/`SEED_VERSION` khai báo ngay trước `let state=...`. Không có bản local nào khác cần
đồng bộ theo. Repo GitHub (private): `https://github.com/nguyencam190/Document_Grasshopper`. Link
live: `https://nguyencam190.github.io/Document_Grasshopper/Grasshopper.html`.

> ⚠️ **QUY TẮC TUYỆT ĐỐI — SỬA `SEED_DOCS` HAY BẤT KỲ NỘI DUNG NÀO CŨNG PHẢI BUMP `SEED_VERSION`**,
> kể cả khi chỉ sửa 1 dòng CSS/style nhỏ, không phải chỉ khi thêm trang mới. Quên bước này từng gây
> ra 1 buổi debug rất dài: sửa xong tưởng đã đúng, push lên, nhưng trình duyệt NÀO ĐÃ TỪNG GHÉ THĂM
> trước đó (kể cả của chính Claude khi tự test) vẫn thấy bản CŨ y nguyên — vì `if(seed_version
> khớp){bỏ qua, dùng localStorage cũ}` khớp version nên không bao giờ đọc lại `SEED_DOCS` mới. Đây
> KHÔNG phải lỗi cache HTTP/CDN (đã loại trừ bằng cửa sổ ẩn danh) — mà là chính logic app tự thiết kế
> để bỏ qua re-seed khi version không đổi. Luôn tăng số này trong CÙNG 1 lần sửa, không tách riêng.

## Cách sửa file — tuỳ môi trường đang chạy

- **Nếu môi trường hiện tại đã có sẵn git clone của repo** (vd Claude Code trên web/remote sandbox —
  trường hợp phổ biến nhất hiện nay): dùng git trực tiếp — Read/Edit tool sửa `Grasshopper.html`,
  rồi `git add/commit/push` theo `Git workflow` ở `CLAUDE.md` gốc (luôn merge thẳng vào `main`).
- **Nếu môi trường KHÔNG có git clone sẵn** (vd chạy từ máy Windows chưa clone repo): dùng GitHub
  Contents API:
  1. Lấy sha hiện tại: `GET /repos/.../contents/Grasshopper.html?ref=main` (field `sha`).
  2. Lấy nội dung thật (file >1MB nên Contents API trả `content:""`): dùng
     `raw.githubusercontent.com/nguyencam190/Document_Grasshopper/main/Grasshopper.html` kèm header
     `Authorization: token TOKEN`.
  3. Lấy token từ Git Credential Manager đã cache sẵn:
     `printf "protocol=https\nhost=github.com\n\n" | git credential fill` (không cần thư mục repo
     local để chạy lệnh này).
  4. Ghi nội dung mới ra file **tạm trong scratchpad session** (KHÔNG phải thư mục project) để dùng
     Edit/Write tool sửa (các tool này bắt buộc cần đường dẫn file thật), rồi encode base64.
  5. `PUT /repos/.../contents/Grasshopper.html` với body `{message, content: base64, sha,
     branch:"main"}` để commit thẳng lên GitHub — không qua `git add/commit/push` cục bộ.

## Quy trình chuẩn khi user tìm hiểu 1 lệnh Grasshopper mới (vd "Deconstruct Brep")

> ⚠️ **Khi user gửi kèm 1 hình ảnh để yêu cầu nghiên cứu — PHẢI xác minh ảnh đó thật sự là canvas/ribbon
> Grasshopper trước khi bắt đầu bất cứ bước nào khác.** Kiểm tra các dấu hiệu nhận biết thật (icon
> component dạng hộp bo góc xám/đen có núm input-output, dây nối cong, tên tab ribbon quen thuộc như
> Params/Maths/Curve..., giao diện Rhino/Grasshopper) — không mặc định ảnh nào cũng là Grasshopper chỉ
> vì user đang hỏi trong ngữ cảnh dự án này. Nếu ảnh **không phải** Grasshopper (phần mềm khác, ảnh
> không liên quan, ảnh mờ không nhận diện được...), DỪNG LẠI và báo rõ cho user thay vì suy đoán/nghiên
> cứu đại một lệnh nào đó. Chỉ tiếp tục nghiên cứu khi đã xác nhận chắc chắn ảnh là Grasshopper thật.

> ⚠️ **BƯỚC 0 — BẮT BUỘC kiểm tra trùng trước khi làm bất cứ gì khác**: lấy `Grasshopper.html` hiện
> tại, tìm trong biến `SEED_DOCS` xem component/lệnh này **đã có trang riêng chưa** (so khớp theo tên
> lệnh, kể cả tên gần giống/viết tắt/khác hoa-thường). Nếu đã có trang rồi thì **DỪNG LẠI**: không
> nghiên cứu lại, không viết lại nội dung, không tạo thêm trang mới trùng lặp — báo ngay cho user
> theo đúng mẫu:
> **"Lệnh [tên lệnh] đã có trong document rồi — trang '[title trang]', là trang con của '[title trang
> cha, tra theo `parentId`]'."** (Nếu trang cha lại có `parentId` khác `seed-grasshopper`, nêu luôn cả
> đường dẫn đầy đủ, vd "Grasshopper → Surface → Loft", không chỉ nêu tên cha trực tiếp.) Sau đó hỏi
> user có muốn cập nhật/bổ sung trang cũ đó hay không. Chỉ tiếp tục từ bước 1 trở xuống khi xác nhận
> component **chưa** có trang nào trong `SEED_DOCS`.

> ⚠️ **TUYỆT ĐỐI không nhầm lẫn giữa các component có tên gần giống nhau** — Grasshopper có rất nhiều
> cặp/nhóm tên chỉ khác nhau 1-2 từ nhưng là component KHÁC NHAU hoàn toàn về input/output/chức năng
> (vd `Extrude` ≠ `Extrude Along` ≠ `Extrude Point` ≠ `Extrude Linear`; `Loft` ≠ `Fit Loft`; `Cull
> Pattern` ≠ `Cull Index` ≠ `Cull Nth`; `Curve` ≠ `Curve Closest Point`...). Trước khi viết bất kỳ nội
> dung nào (trang doc, bảng tổng hợp, câu trả lời chat), PHẢI xác nhận tên chính xác 100% qua nguồn
> tham khảo thật (ưu tiên tài liệu chính thức/AAD như quy định ở skill `nghien-cuu-grasshopper`), tự
> hỏi lại "tên này có đang bị viết tắt/gộp nhầm với 1 component khác không" — đặc biệt khi ghi chú nói
> tới 1 component liên quan/thay thế trong phần "Lưu ý"/warning (đã từng ghi nhầm "Extrude Along
> Curve" trong khi tên thật là "Extrude Along", phải sửa lại sau). Nếu không chắc chắn tên chính xác,
> DỪNG LẠI tra cứu thêm hoặc hỏi user, không đoán đại theo trực giác/thói quen đặt tên.

1. Nghiên cứu chức năng lệnh đó (dùng skill `nghien-cuu-grasshopper`: input/output, cách dùng, lưu ý).
2. Thêm 1 trang con mới vào biến `SEED_DOCS`, đặt tên đúng theo lệnh. **`parentId` PHẢI trỏ vào đúng
   trang panel** (`seed-panel-{tab}-{panel}`) mà lệnh đó thuộc về trong Grasshopper thật — KHÔNG trỏ
   thẳng vào trang tab hay trang gốc `seed-grasshopper`. Xem bảng đầy đủ 13 tab × panel ở
   `references/panel-taxonomy.md` (bảng này đã xác nhận bằng ảnh chụp ribbon thật, không phải suy
   đoán — dùng làm nguồn duy nhất cho việc phân loại).
3. **Trước khi viết trang con chi tiết, thêm/cập nhật 1 dòng cho lệnh đó vào bảng tổng hợp trên
   ĐÚNG trang panel cha** (vd lệnh "Loft" → bảng trên trang panel `seed-panel-surface-freeform`):
   - Nếu trang panel cha **CHƯA có bảng tổng hợp** — tạo mới theo đúng mẫu đã dùng ở trang "Geometry"
     (`seed-panel-params-geometry`, xem trực tiếp trong `Grasshopper.html` làm ví dụ tham chiếu):
     bảng 3 cột **Icon | Tên | Chức năng**, icon dùng badge vuông bo góc nền tối `#242424` chứa 1
     icon Tabler (`<i class="ti ti-{tên-icon}">`, font đã sẵn có trong app — xem danh sách class hợp
     lệ tại `https://tabler.io/icons` hoặc cài thử gói npm `@tabler/icons-webfont` để tra cứu chắc
     chắn tên class tồn tại trước khi dùng, tránh bịa tên icon không có thật), không dùng icon
     Grasshopper thật vì không có cách trích xuất chính xác trừ khi user upload ảnh gốc lên GitHub.
   - Nếu trang panel cha **ĐÃ có bảng** (thường là do trước đó đã liệt kê sẵn toàn bộ dropdown panel)
     — tìm đúng dòng có tên lệnh đó, cập nhật lại cột "Chức năng" cho khớp với nội dung đã nghiên
     cứu kỹ (thường mô tả cũ chỉ là 1 câu chung chung, tạm thời).
   - **Sau khi sửa bảng, luôn dùng lại đúng kỹ thuật đã kiểm chứng**: nếu cần chỉnh độ rộng cột, PHẢI
     dùng thao tác kéo cột thật của app qua Playwright (mở trang trong trình duyệt local, drag đúng
     `.tbl-col-resize-handle`, đọc lại `doc.content` sau khi kéo) — **KHÔNG tự viết `<colgroup>` tay**,
     vì app tự chèn thêm 1 cột "#" ẩn (class `tbl-row-num`) làm lệch toàn bộ phép tính cột nếu viết
     colgroup thủ công, từng gây vỡ layout thật.
4. **Viết trang doc theo ĐỦ 11 mục của skill `nghien-cuu-grasshopper`** — trang doc và câu trả lời
   chat dùng CHUNG 1 chuẩn nội dung, chỉ khác định dạng hiển thị (trang doc dùng H1/H2/bảng HTML, chat
   dùng markdown). Cấu trúc canvas theo đúng thứ tự sau:
   - H1 tên lệnh
   - Info panel tóm tắt (icon ℹ️ + mức độ 🟢/🟡/🔴 + 1 câu tóm tắt chức năng)
   - H2 **"Chức năng"** — 1-2 câu, đúng bản chất, không chỉ mô tả bề mặt.
   - H2 **"Khi nào sử dụng"** — khi nào nên dùng; khi nào KHÔNG nên dùng (nếu có).
   - H2 **"Input/Output"** — bảng Input/Output như cũ, giữ cột Tên | Kiểu dữ liệu | Mô tả. **Cột "Tên"
     và "Kiểu dữ liệu" PHẢI rộng bằng nhau, cột "Mô tả" rộng hơn** (đã xác nhận qua thao tác kéo cột
     thật bằng Playwright — không đoán tay): bọc `<table>` trong
     `<div class="tbl-frame"><div class="tbl-outer">...</div></div>`, gắn thẳng
     `data-colwidths="36px,20.02%,20.02%,59.959%"` (tỉ lệ Tên=Kiểu dữ liệu=20%, Mô tả=60%, đã kiểm
     chứng qua render thật, không bị tràn ngang) và `table-layout:fixed;width:100%` trong style của
     `<table>` — dùng lại đúng chuỗi `data-colwidths` này cho MỌI bảng Input/Output mới, không cần kéo
     lại từ đầu mỗi lần vì tỉ lệ cột đã cố định thành chuẩn chung.
   - H2 **"Thuộc tính"** — toàn bộ thuộc tính THỰC SỰ có (right-click menu, Options, Modes, Preview,
     Flatten/Graft/Simplify/Reverse, Internalize Data...). Ghi rõ "không có" nếu component không có
     thuộc tính đặc biệt — không được bỏ qua mục này.
   - H2 **"Cách dùng"** — hướng dẫn từng bước (danh sách số), giữ nguyên như trước (không phải mục
     gốc của skill nhưng hữu ích cho người mới, vẫn giữ lại).
   - Mục **"Minh họa"** — nằm NGAY SAU "Cách dùng" (không đặt cuối trang) vì minh hoạ trực quan hoá
     đúng các bước vừa đọc. **KHÔNG có tiêu đề H2 riêng** (chỉ chèn thẳng khối `.cf-img-block` liền
     sau đoạn `<ol>` của "Cách dùng", không viết `<h2>Minh họa</h2>`) — ảnh tự nó đã rõ nghĩa ngay sau
     phần hướng dẫn, thêm heading là thừa. (Các trang tab/panel tổng quan — không theo chuẩn 11 mục
     này — vẫn giữ nguyên `<h2>Minh họa</h2>` như cũ, không đụng vào.) Về cách tạo/gắn ảnh, xem skill
     `xuat-ban-hinh-minh-hoa`. Cần tối thiểu 1 ví dụ đơn giản; thêm ví dụ thứ 2 nếu có tình huống
     thực tế đáng nêu riêng.
   - H2 **"Ứng dụng"** — lĩnh vực áp dụng, **ưu tiên hướng Parametric Design dùng để xây dựng pattern**
     (hoa văn/hoạ tiết lặp lại có kiểm soát tham số — mặt đứng, lưới pattern, mảng module...) làm góc
     nhìn chính khi component cho phép diễn giải theo hướng này; chỉ dùng góc nhìn khác (Architecture,
     Structural, Analysis...) khi component không có cách nào gắn với pattern một cách tự nhiên/trung
     thực (không gượng ép). Nêu ví dụ thực tế nếu phù hợp.
   - H2 **"Kết nối"** — 3 bảng riêng: "Có thể nhận dữ liệu từ" (Component | Data Type | Có thể nối),
     "Có thể xuất dữ liệu đến" (tương tự), "Không thể kết nối" (Component | Lý do).
   - H2 **"Workflow phổ biến"** — ít nhất 2 workflow thực tế, dạng chuỗi mũi tên (vd
     `Circle → Divide Curve → Points → Move → Polyline`), workflow phổ biến nhất nêu trước. **Sau các
     dòng workflow text, PHẢI thêm 1 ảnh minh hoạ riêng** vẽ chuỗi component của workflow phổ biến
     nhất — khác nội dung với ảnh ở mục "Minh họa" phía trên (mục đó tập trung chi tiết input/output
     của RIÊNG component chính; ảnh này cho thấy TOÀN BỘ chuỗi nhiều component nối với nhau).
   - H2 **"Kiểu dữ liệu"** — liệt kê kiểu dữ liệu hỗ trợ (Point, Curve, Surface, Brep, Mesh, Vector,
     Plane, Number, Boolean, Text, List, Data Tree...); giải thích khác biệt nếu hỗ trợ nhiều kiểu.
   - Warning/Note panel — mục **"Lưu ý"**: lỗi thường gặp, giới hạn, mẹo dùng hiệu quả.
   - H2 **"Ví dụ ứng dụng thực tế"** — **mặc định chọn 1 ví dụ dựng pattern parametric cụ thể** (khớp
     hướng đã chọn ở mục "Ứng dụng" phía trên), nếu có ví dụ liên quan tới dự án Voronoi thì ưu tiên
     nêu ở đây. **Mục này cũng PHẢI có hình minh họa riêng** — minh họa đúng ví dụ ứng dụng cụ thể
     đang mô tả, KHÔNG dùng lại y nguyên ảnh của mục "Minh họa" phía trên (2 ảnh phục vụ 2 mục đích
     khác nhau: 1 ảnh giải thích cách nối dây/component, 1 ảnh minh họa ngữ cảnh ứng dụng thực tế/
     pattern kết quả).

   **Ngắn gọn vẫn áp dụng cho từng mục** (xem quy tắc văn phong ở `CLAUDE.md`) — 11 mục không có
   nghĩa là dài, mỗi mục chỉ cần đủ ý, không lan man. Nếu 1 mục thực sự không có nội dung phù hợp (vd
   component quá đơn giản không có workflow nào khác ngoài 1 cách dùng), vẫn giữ H2 và ghi ngắn gọn
   lý do thay vì bỏ hẳn mục đó — người đọc cần thấy đủ 11 mục nhất quán giữa các trang.
5. **Ngay khi viết xong nội dung trang con** (đủ 11 mục, trước hoặc cùng lúc bump `SEED_VERSION`),
   **BẬT khóa trang** bằng cách thêm `locked:true` vào object của trang đó trong `SEED_DOCS` (field
   `locked` đặt ngay sau `id:'...'`, trước `title:...`) — biến trang thành chỉ đọc, tránh sửa nhầm sau
   này. Chỉ áp dụng cho trang con 1 component cụ thể (`seed-cmd-*`) — KHÔNG khóa trang tab/panel tổng
   quan (`seed-tab-*`/`seed-panel-*`), vì các trang đó còn cần cập nhật bảng "Danh sách component"
   liên tục khi có thêm lệnh mới. Nếu sau này cần sửa lại 1 trang đã khóa, chủ động báo cho user biết
   trang đang khóa và cần mở khóa (`locked:false` hoặc xoá field) trước khi chỉnh sửa.
6. Bump `SEED_VERSION` lên 1 (để mọi trình duyệt tự đồng bộ lại, không cần user xoá cache/localStorage).
7. **Luôn publish kèm ảnh minh họa** — xem skill `xuat-ban-hinh-minh-hoa` cho toàn bộ pipeline tạo/
   gắn ảnh (SVG tự vẽ, cf-img-block, SEED_ASSETS, các bug đã vá).

## Vì sao cấu trúc panel quan trọng

Phân loại sai tab/panel làm sai cấu trúc doc lâu dài, khó sửa về sau vì user điều hướng theo cây
trang. Không đoán bừa — nếu không chắc, dừng lại hỏi user hoặc tra cứu thêm.
