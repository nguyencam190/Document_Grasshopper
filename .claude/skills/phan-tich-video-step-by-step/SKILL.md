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
- Vẫn giữ nguyên tắc không bịa đặt (xem `nghien-cuu-grasshopper`): đoạn nào không đọc rõ được (mờ,
  bị che, thiếu frame) → ghi rõ "không chắc chắn/không đọc được đoạn này", không suy đoán cho có vẻ
  hợp lý.

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
