---
name: phan-tich-video-step-by-step
description: Quy trình phân tích 1 video hướng dẫn dựng nguyên 1 mẫu/pattern Grasshopper (khác với tài liệu 1 component đơn lẻ) và viết thành 1 trang con trong "Example Step-by-Step" của Grasshopper.html. Bao gồm cách đọc video không xem trực tiếp được (trích frame bằng ffmpeg, đọc phụ đề .srt), kiểm tra trùng nội dung trước khi phân tích, và cấu trúc trang cha/con. LUÔN dùng skill này khi user yêu cầu "phân tích step-by-step", "phân tích video này", hoặc đưa 1 video/mẫu dựng sẵn muốn đúc kết thành quy trình từng bước. Không dùng cho tài liệu tham khảo 1 component đơn lẻ (dùng nghien-cuu-grasshopper + xuat-ban-trang-doc).
---

# Phân tích video dựng pattern — Example Step-by-Step

## Đọc video khi không xem trực tiếp được

- Dùng ffmpeg trích frame ra ảnh để đọc canvas Grasshopper trong video (không xem video trực tiếp
  được).
- Nếu video có lời giảng, cần file phụ đề `.srt` đi kèm (user cung cấp) — đọc phụ đề để nắm lời giảng,
  không nghe được audio. Ưu tiên thông tin từ lời giảng hơn suy đoán từ hình khi có mâu thuẫn (vd giá
  trị slider chính xác, mục đích 1 bước — hình chỉ cho thấy TRẠNG THÁI, lời giảng giải thích LÝ DO).

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

## Case study đã có sẵn — Voronoi Pattern

Xem mục "Case study: Voronoi Pattern" ở cuối `CLAUDE.md` cho ví dụ đầy đủ đã hoàn thành (pattern hoa
hướng dương/xoắn ốc) — kể cả danh sách file phân tích liên quan (`docs/voronoi-*.md`,
`docs/voronoi-*.svg`) có thể tham chiếu khi phân tích mẫu mới liên quan tới Mesh/Triangulation/
Voronoi/Attractor.
