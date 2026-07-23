# Hoàn thành — dịch/diễn giải Grasshopper Primer 3rd Edition (Mode Lab) sang tiếng Việt

Nguồn: `PDF/Mode Lab Grasshopper Primer Third Edition (Mode Lab) (z-library.sk, 1lib.sk, z-lib.sk).pdf`
(145 trang, đọc toàn bộ text bằng PyMuPDF cho từng range trang đã xác nhận đúng theo mục lục).

## File đã tạo

| File | Phần | Trang PDF | Số từ |
|---|---|---|---|
| `f0.md` | F.0 Hello Grasshopper | 15–34 | 3,134 |
| `f1.md` | F.1 Anatomy of a Grasshopper Definition | 35–52 | 3,242 |
| `f2.md` | F.2 Building Blocks of Algorithms | 53–74 | 4,164 |
| `f3.md` | F.3 Designing with Lists | 75–96 | 3,886 |
| `f4.md` | F.4 Designing with Data Trees | 97–122 | 4,699 |

Tổng: **19,125 từ** tiếng Việt (không tính bảng/heading markdown).

## Ghi chú quá trình làm

- Đã xác nhận đúng số trang PDF khớp mục lục (kiểm tra tiêu đề mở đầu mỗi phần tại đúng trang PDF nêu
  trong yêu cầu — vd trang PDF 15 mở đầu "F.0 HELLO GRASSHOPPER", trang PDF 35 mở đầu "F.1 ANATOMY OF
  A GRASSHOPPER DEFINITION"...).
- Toàn bộ nội dung được đọc trực tiếp từ text PDF thật (không bịa), viết lại bằng tiếng Việt theo lời
  riêng, giữ nguyên tên chính xác của mọi component Grasshopper được nhắc tới (đường dẫn tab/panel
  kiểu `Vector/Grid/Hexagonal`, tên input/output như `(S)`, `(Ex)`, `(Ey)`...).
- Với các ví dụ thực hành có đánh số bước (numbered steps) trong sách (F.2.1.0, F.2.2.3, F.2.2.4,
  F.2.3, F.3.6, F.4.0.2, F.4.3.5, F.4.3.6), đã giữ **đúng trình tự từng bước kéo-thả/nối dây** như
  sách viết, để sau này dùng vẽ minh hoạ theo đúng thứ tự.
- Vài đoạn chỉ có hình/bảng minh hoạ không kèm text mô tả rõ (vd bảng hoán vị trong F.3.2, hình cây
  path remap trong F.4.3.4, bảng Venn diagram trong F.2.4) — đã ghi chú ngắn gọn là "minh hoạ hình
  ảnh, không có mô tả text chi tiết đi kèm" thay vì suy đoán thêm nội dung.
- File tạm `_raw_f*.txt` (text thô trích từ PDF, dùng làm nguồn tham chiếu khi viết) đã được xoá sau
  khi hoàn tất, không cần giữ lại.
