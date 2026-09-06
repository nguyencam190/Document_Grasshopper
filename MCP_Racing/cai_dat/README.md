# Cài MCP server vào Claude Desktop — tự động

Script này làm hộ bước dễ sai nhất: sửa file cấu hình Claude Desktop **mà không
làm mất các server đang có**.

> ⚠️ **Chưa chạy thử trên Windows.** Phần gộp cấu hình đã có 17 test pass, nhưng
> phần tạo môi trường ảo và cài thư viện chỉ mới chạy trên Linux. Nếu vướng, gửi
> tôi thông báo lỗi.

## Cách 1 — bấm đúp *(Windows)*

1. Mở `cai_dat_mcp.bat` bằng Notepad
2. Sửa hai dòng đường dẫn cho đúng máy bạn:
   ```bat
   set MAYA_MCP=D:\MAYA_TOOLS\MayaMCP-main
   set ARTSPEC=D:\Projects\MCP_Racing\artspec
   ```
   Chỉ cài một cái thì xoá dòng kia và bỏ tham số tương ứng ở dòng `python`.
3. Lưu, rồi **bấm đúp** vào file `.bat`

## Cách 2 — gõ lệnh

```bash
# xem trước, không sửa gì cả
python cai_dat_mcp.py --maya-mcp D:/MAYA_TOOLS/MayaMCP-main --dry-run

# làm thật
python cai_dat_mcp.py --maya-mcp D:/MAYA_TOOLS/MayaMCP-main
python cai_dat_mcp.py --artspec  D:/Projects/MCP_Racing/artspec
python cai_dat_mcp.py --maya-mcp ... --artspec ...     # cả hai cùng lúc
```

**Luôn chạy `--dry-run` trước** để xem nó định ghi gì.

## Nó làm gì

| Bước | Việc |
|---|---|
| 1 | Kiểm Python ≥ 3.10 |
| 2 | Tạo `.venv` và cài `requirements.txt` cho từng server |
| 3 | Tìm file cấu hình Claude Desktop theo hệ điều hành |
| 4 | **Gộp** mục mới vào — giữ nguyên server đang có, sao lưu trước khi ghi |
| 5 | In ra việc còn lại phải làm bằng tay |

## Nó KHÔNG làm gì

- **Không ghi đè** file cấu hình. Chỉ thêm, hoặc thay đúng mục cùng tên
- **Không xoá** server nào bạn đã cài trước đó
- **Không sửa** khi file cấu hình hiện tại hỏng — nó báo lỗi và dừng

Mỗi lần chạy đều để lại bản sao lưu `claude_desktop_config.backup-<ngày giờ>.json`
cạnh file gốc. Sai thì đổi tên bản sao lưu về tên cũ là xong.

## Sau khi chạy xong — ba việc phải tự làm

1. **Thoát hẳn Claude Desktop rồi mở lại.** Bấm X không đủ — cấu hình chỉ đọc
   lúc khởi động. Windows: chuột phải icon ở khay hệ thống → Quit. Mac: `Cmd+Q`.
2. **Với MayaMCP:** mở Maya, lần đầu kết nối sẽ hiện hộp thoại bảo mật → bấm
   **"Allow All"**. Phải làm lại mỗi phiên Maya.
3. **Với artspec:** làm test chống bịa — hỏi một điều techspec **không** quy định.
   Trả lời đúng phải là *"techspec không có quy định này"*.

## Lỗi hay gặp

| Báo gì | Sửa thế nào |
|---|---|
| `cần Python 3.10 trở lên` | Cài Python mới, nhớ tích "Add Python to PATH" |
| `Không thấy .../src/maya_mcp_server.py` | Đường dẫn phải trỏ tới thư mục **chứa** `src/`, không phải vào trong `src/` |
| `Đường dẫn phải trỏ tới thư mục CHỨA artspec/` | Trỏ tới `MCP_Racing/artspec`, không phải `MCP_Racing/artspec/artspec` |
| `File cấu hình hiện tại không phải JSON hợp lệ` | Mở file đó ra sửa, hoặc đổi tên nó đi rồi chạy lại |
| `'python' is not recognized` | Python chưa vào PATH. Dùng đường dẫn đầy đủ: `C:\Python312\python.exe cai_dat_mcp.py ...` |

## Test

```bash
python test_cai_dat.py      # 17 check — tập trung vào bước gộp cấu hình
```
