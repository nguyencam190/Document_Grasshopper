# Cài artspec vào Claude Desktop

> Làm một lần trên máy bạn, mất khoảng 20 phút. Sau này phát cho hoạ sĩ thì lặp
> lại đúng các bước này.
> Ngày soạn: 2026-09-05.

---

## Quyết định đã chốt: dùng Claude

Đúng hướng, vì ba lý do:

| | |
|---|---|
| **Đơn giản nhất** | Không phải cài thêm nền tảng nào. Claude Desktop + artspec là đủ |
| **artspec đã nhắm sẵn** | 13 tool viết theo chuẩn MCP, cắm vào là chạy |
| **Không bị khoá** | MCP là **chuẩn mở**, không phải sản phẩm riêng. Sau này muốn đổi sang Hermes, Heym hay công cụ khác thì đổi được, artspec giữ nguyên |

Điểm cuối quan trọng: bạn đang cam kết với **một chuẩn**, không cam kết với một
hãng. Giống chọn xuất FBX thay vì lưu file riêng của một phần mềm.

---

## Bước 1 · Chuẩn bị

### 1.1 Kiểm tra Python

Mở Command Prompt (Windows) hoặc Terminal (Mac):

```bash
python --version        # Windows — phải ra 3.10 trở lên
python3 --version       # Mac
```

Chưa có thì tải ở [python.org](https://www.python.org/downloads/). Trên Windows,
lúc cài **nhớ tích ô "Add Python to PATH"**.

### 1.2 Cài thư viện

```bash
cd <đường dẫn tới>/MCP_Racing/artspec
pip install -r requirements.txt
python -m artspec.cli rules          # phải thấy 20 luật
```

Lệnh cuối chạy được nghĩa là phần khó nhất đã xong.

### 1.3 Ghi lại 2 đường dẫn tuyệt đối

Cần chính xác, không được dùng đường dẫn tương đối:

```bash
# đường dẫn tới thư mục artspec
cd <đường dẫn>/MCP_Racing/artspec && pwd        # Mac/Linux
cd <đường dẫn>\MCP_Racing\artspec && cd         # Windows

# đường dẫn tới python
where python            # Windows  → vd C:\Python312\python.exe
which python3           # Mac      → vd /usr/bin/python3
```

Chép cả hai ra giấy nháp, lát nữa dán vào.

---

## Bước 2 · Mở file cấu hình

**Cách dễ nhất:** trong Claude Desktop mở **Settings → Developer → Edit Config**.
Cửa sổ mở ra sẵn đúng file cần sửa.

Hoặc mở thẳng file:

| Hệ điều hành | Đường dẫn |
|---|---|
| Windows | `%APPDATA%\Claude\claude_desktop_config.json` |
| macOS | `~/Library/Application Support/Claude/claude_desktop_config.json` |

File chưa có thì tạo mới.

---

## Bước 3 · Dán cấu hình

**Windows** — chú ý dùng dấu gạch chéo xuôi `/`, đừng dùng `\`:

```json
{
  "mcpServers": {
    "artspec": {
      "command": "C:/Python312/python.exe",
      "args": ["-m", "artspec.server"],
      "env": {
        "PYTHONPATH": "D:/Projects/MCP_Racing/artspec",
        "ARTSPEC_ROOT": "D:/Projects/MCP_Racing/artspec"
      }
    }
  }
}
```

**macOS:**

```json
{
  "mcpServers": {
    "artspec": {
      "command": "/usr/bin/python3",
      "args": ["-m", "artspec.server"],
      "env": {
        "PYTHONPATH": "/Users/ban/Projects/MCP_Racing/artspec",
        "ARTSPEC_ROOT": "/Users/ban/Projects/MCP_Racing/artspec"
      }
    }
  }
}
```

Thay 3 chỗ: đường dẫn python, và hai đường dẫn artspec (giống nhau).

> **Vì sao dùng `PYTHONPATH` chứ không dùng `cwd`:** Claude khởi động server từ
> một thư mục bất kỳ. `PYTHONPATH` đảm bảo Python tìm thấy module dù đứng ở đâu.
> Đã kiểm chứng chạy đúng từ thư mục khác.

Nếu file đã có sẵn server khác thì thêm `artspec` vào trong `mcpServers`, đừng
ghi đè cả file.

---

## Bước 4 · Thoát hẳn Claude rồi mở lại

**Bấm X đóng cửa sổ là chưa đủ.** Phải thoát hẳn ứng dụng:

- Windows: chuột phải icon Claude ở khay hệ thống (góc dưới phải) → Quit
- Mac: `Cmd + Q`

Rồi mở lại. Cấu hình chỉ được đọc lúc khởi động.

---

## Bước 5 · Kiểm tra — 5 câu hỏi

Hỏi lần lượt trong Claude Desktop:

| # | Hỏi | Kết quả đúng |
|---|---|---|
| 1 | *"Bạn có tool artspec nào?"* | Liệt kê 13 tool |
| 2 | *"Dự án quy định gì về texel density?"* | Trích `VEH-UV-001` **kèm mã luật** |
| 3 | *"Xe LOD2 tối đa bao nhiêu tri?"* | Con số **kèm rule_id** |
| 4 | *"Kiểm giúp tôi file D:/submit/SUV_A.fbx"* | Báo cáo đầy đủ |
| 5 | **Test chống bịa** (bên dưới) | **Nói không có** |

### Test chống bịa — bắt buộc làm

Hỏi một câu mà techspec **không** quy định:

> *"Dự án quy định số vertex tối đa cho decal là bao nhiêu?"*

**Trả lời đúng:** *"Techspec không có quy định này."*

**Trả lời SAI:** nó đưa ra một con số bất kỳ.

Nếu nó bịa ra số → **báo tôi ngay**, phải siết lại phần `instructions` của server.
Đây là bài kiểm tra quan trọng nhất trong cả 5 câu — hoạ sĩ làm sai asset theo
một con số bịa thì tệ hơn nhiều so với việc không có công cụ nào.

---

## Lỗi hay gặp

| Triệu chứng | Nguyên nhân | Cách sửa |
|---|---|---|
| Claude không thấy tool nào | Chưa thoát hẳn app | Quit hoàn toàn rồi mở lại |
| Không thấy tool, đã restart rồi | JSON sai cú pháp | Dán vào [jsonlint.com](https://jsonlint.com) kiểm tra dấu phẩy, ngoặc |
| *"command not found"* | Đường dẫn python sai | Dùng đường dẫn tuyệt đối từ `where python` |
| *"No module named artspec"* | `PYTHONPATH` sai | Trỏ vào thư mục **chứa** thư mục con `artspec/`, không phải vào trong nó |
| Windows báo lỗi đường dẫn | Dùng dấu `\` | Đổi hết sang `/` |
| Tool có nhưng luật rỗng | `ARTSPEC_ROOT` sai | Trỏ tới thư mục chứa `rules/` |

Muốn xem lỗi chi tiết thì chạy tay lệnh này — nó phải im lặng chờ, không báo lỗi:

```bash
PYTHONPATH=<đường dẫn artspec> python -m artspec.server
```

Bấm `Ctrl + C` để thoát.

---

## Sau khi cài xong

### Sửa luật không cần khởi động lại

Server tự nạp lại khi file YAML đổi. Sửa `rules/`, `changelog/`, `waivers/` xong
là hỏi được ngay — không phải restart Claude.

Chỉ khi sửa **code Python** mới cần restart.

### Ba câu hỏi dùng hằng ngày

```
"Kiểm giúp tôi thư mục submit hôm nay"
"SUV_A sai chỗ nào, giải thích cho hoạ sĩ hiểu"
"Tuần này khách đổi gì với xe?"
```

### Khi phát cho hoạ sĩ

Lặp lại đúng 5 bước trên trên máy họ. Bốn lưu ý:

1. Bộ luật để trên **ổ chung hoặc git**, không chép mỗi máy một bản — nếu không
   sẽ mỗi người một phiên bản luật.
2. `ARTSPEC_ROOT` trỏ tới bản dùng chung đó.
3. Bản local (stdio) **không mở cổng mạng nào** — không cần xin phép IT về tường lửa.
4. Chỉ khi chuyển sang **một server dùng chung cho cả team** mới cần OAuth 2.1 và
   `ARTSPEC_FILE_ROOT` — xem [`BAO_MAT.md`](BAO_MAT.md) §4.

---

## Tiếp theo

Quay lại [`BAT_DAU_TU_DAU.md`](BAT_DAU_TU_DAU.md) — bạn đang ở **Tuần 1**. Cài
xong thì chạy thử trên 5 asset thật, rồi sang Tuần 2.

**Nguồn:** [Getting Started with Local MCP Servers on Claude Desktop — Anthropic
Help Center](https://support.claude.com/en/articles/10949351-getting-started-with-local-mcp-servers-on-claude-desktop)
