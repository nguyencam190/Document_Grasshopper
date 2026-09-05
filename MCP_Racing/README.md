# MCP_Racing

Thư mục nghiên cứu riêng, **không liên quan tới tài liệu Grasshopper** trong repo này.

Chủ đề: xây dựng MCP server giúp hoạ sĩ 3D nắm techspec và update khách hàng của một dự án
racing game open-world.

| File | Nội dung |
|---|---|
| [`BAT_DAU_TU_DAU.md`](BAT_DAU_TU_DAU.md) | **⭐ ĐỌC ĐẦU TIÊN.** Kế hoạch hành động: bạn phải làm gì, theo thứ tự nào, mất bao lâu, ai làm. 6 giai đoạn + 5 việc làm ngay tuần này |
| [`VIET_CHECKLIST.md`](VIET_CHECKLIST.md) | **Việc chính của Giai đoạn 1.** Cách viết checklist: phép thử một mục tốt, biến câu tệ thành câu dùng được, cây quyết định tier, và quy trình điền Excel → 1 lệnh → ra luật (không phải sửa YAML) |
| [`QUY_TRINH_6_BUOC_QUAN_LY.md`](QUY_TRINH_6_BUOC_QUAN_LY.md) | Quản lý quy trình 6 bước (Model → Lock Normal → UVW → Texture → Rigging → Import UE5): 4 gate cần thêm, định nghĩa DONE + lỗi hay gặp từng bước, 7 cơ chế quản lý, chỉ số đo lường, checklist mẫu |
| [`artspec/`](artspec/README.md) | **Code chạy được.** Engine kiểm **lỗi mesh** (n-gon, non-manifold, mặt lật, lỗ thủng…) + **sai techspec**, kèm MCP server (Python). Luật để ngoài dạng YAML — thêm luật đặc thù không phải sửa code. Kèm bộ luật mẫu, collector Maya, metrics mẫu |
| [`TAO_TOOL_MCP.md`](TAO_TOOL_MCP.md) | Tạo tool cho MCP là làm những gì: cái AI thực sự nhìn thấy, giải phẫu 1 tool, 4 bước tạo, ví dụ đầy đủ `whats_changed_for`, 7 nguyên tắc + 4 sai lầm, việc nào bạn tự làm được |
| [`NGHIEN_CUU_MCP_ARTSPEC.md`](NGHIEN_CUU_MCP_ARTSPEC.md) | Tài liệu nghiên cứu & thiết kế MCP: MCP là gì, audit quy trình hiện tại, kiến trúc 3 lớp, schema Spec Registry, danh sách Tools/Resources/Prompts, so sánh 3 phương án, stack Python, bảo mật, roadmap 8 phase, rủi ro |

**Thứ tự đọc:** `BAT_DAU_TU_DAU.md` → rồi mở tài liệu khác khi kế hoạch đó chỉ tới.

**Trạng thái:** engine + MCP server đã chạy được với bộ luật MẪU (toàn số bịa).
Phần khó còn lại không phải kỹ thuật mà là nội dung — số thật, quyết định thật.
Bắt đầu ở [`BAT_DAU_TU_DAU.md`](BAT_DAU_TU_DAU.md) mục "Việc làm trong tuần này".
