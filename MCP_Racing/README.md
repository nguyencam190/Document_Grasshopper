# MCP_Racing

Thư mục nghiên cứu riêng, **không liên quan tới tài liệu Grasshopper** trong repo này.

Chủ đề: xây dựng MCP server giúp hoạ sĩ 3D nắm techspec và update khách hàng của một dự án
racing game open-world.

| File | Nội dung |
|---|---|
| [`QUY_TRINH_6_BUOC_QUAN_LY.md`](QUY_TRINH_6_BUOC_QUAN_LY.md) | **Đọc trước.** Quản lý quy trình 6 bước (Model → Lock Normal → UVW → Texture → Rigging → Import UE5): 4 gate cần thêm, định nghĩa DONE + lỗi hay gặp từng bước, 7 cơ chế quản lý, chỉ số đo lường, checklist mẫu |
| [`artspec/`](artspec/README.md) | **Code chạy được.** Engine kiểm asset + MCP server (Python). Luật để ngoài dạng YAML — thêm luật đặc thù không phải sửa code. Kèm bộ luật mẫu, collector Maya, metrics mẫu |
| [`NGHIEN_CUU_MCP_ARTSPEC.md`](NGHIEN_CUU_MCP_ARTSPEC.md) | Tài liệu nghiên cứu & thiết kế MCP: MCP là gì, audit quy trình hiện tại, kiến trúc 3 lớp, schema Spec Registry, danh sách Tools/Resources/Prompts, so sánh 3 phương án, stack Python, bảo mật, roadmap 8 phase, rủi ro |

**Thứ tự đọc:** quy trình trước → MCP sau. MCP chỉ là cách phục vụ checklist nhanh hơn; chưa có
checklist thì chưa có gì để MCP phục vụ.

**Trạng thái:** engine + MCP server đã chạy được với bộ luật MẪU. Việc tiếp theo là
thay số ví dụ trong `artspec/rules/` bằng số thật của dự án.
