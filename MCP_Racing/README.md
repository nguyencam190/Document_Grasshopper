# MCP_Racing

Thư mục nghiên cứu riêng, **không liên quan tới tài liệu Grasshopper** trong repo này.

Chủ đề: xây dựng MCP server giúp hoạ sĩ 3D nắm techspec và update khách hàng của một dự án
racing game open-world.

| File | Nội dung |
|---|---|
| [`BAT_DAU_TU_DAU.md`](BAT_DAU_TU_DAU.md) | **⭐ ĐỌC ĐẦU TIÊN.** Lộ trình 6 tuần có lệnh cụ thể và mốc "xong khi" cho từng tuần. Bảng điều khiển hiện trạng, 3 điểm quyết định, bảng theo dõi in ra tick được, và bản rút gọn nếu chỉ có 2 giờ/tuần |
| [`CAI_DAT_CLAUDE.md`](CAI_DAT_CLAUDE.md) | **Làm ngay sau khi đọc lộ trình.** Cài artspec vào Claude Desktop từng bước: cấu hình cho Windows/Mac, 5 câu kiểm tra (gồm test chống bịa số), bảng lỗi hay gặp |
| [`VIET_CHECKLIST.md`](VIET_CHECKLIST.md) | **Việc chính của Giai đoạn 1.** Cách viết checklist: phép thử một mục tốt, biến câu tệ thành câu dùng được, cây quyết định tier, và quy trình điền Excel → 1 lệnh → ra luật (không phải sửa YAML) |
| [`QUY_TRINH_6_BUOC_QUAN_LY.md`](QUY_TRINH_6_BUOC_QUAN_LY.md) | Quản lý quy trình 6 bước (Model → Lock Normal → UVW → Texture → Rigging → Import UE5): 4 gate cần thêm, định nghĩa DONE + lỗi hay gặp từng bước, 7 cơ chế quản lý, chỉ số đo lường, checklist mẫu |
| [`artspec/`](artspec/README.md) | **Code chạy được.** Engine kiểm **lỗi mesh** (n-gon, non-manifold, mặt lật, lỗ thủng…) + **sai techspec**, kèm MCP server (Python). Luật để ngoài dạng YAML — thêm luật đặc thù không phải sửa code. Kèm bộ luật mẫu, collector Maya, metrics mẫu |
| [`TAO_TOOL_MCP.md`](TAO_TOOL_MCP.md) | Tạo tool cho MCP là làm những gì: cái AI thực sự nhìn thấy, giải phẫu 1 tool, 4 bước tạo, ví dụ đầy đủ `whats_changed_for`, 7 nguyên tắc + 4 sai lầm, việc nào bạn tự làm được |
| [`BAO_MAT.md`](BAO_MAT.md) | Mức rủi ro từng phần, giới hạn thư mục đọc, vì sao kết luận do engine chứ không do AI, cảnh báo về Maya commandPort, bảng trả lời nhanh cho IT |
| [`NGHIEN_CUU_MCP_ARTSPEC.md`](NGHIEN_CUU_MCP_ARTSPEC.md) | Tài liệu nghiên cứu & thiết kế MCP: MCP là gì, audit quy trình hiện tại, kiến trúc 3 lớp, schema Spec Registry, danh sách Tools/Resources/Prompts, so sánh 3 phương án, stack Python, bảo mật, roadmap 8 phase, rủi ro |

**Thứ tự đọc:** `BAT_DAU_TU_DAU.md` → rồi mở tài liệu khác khi kế hoạch đó chỉ tới.

**Trạng thái:** engine chạy được, 109 test pass. **10 luật lỗi mesh đã sẵn sàng
dùng ngay hôm nay** — không cần điền gì. Phần còn lại là số thật cho luật riêng
của dự án. Bắt đầu ở [`BAT_DAU_TU_DAU.md`](BAT_DAU_TU_DAU.md) mục "Tuần này".
