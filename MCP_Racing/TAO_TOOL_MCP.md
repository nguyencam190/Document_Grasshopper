# Tạo tool cho MCP là làm những gì

> Giải thích bằng chính code trong [`artspec/`](artspec/README.md). Mọi ví dụ ở
> đây là code thật đang chạy, không phải minh hoạ.
> Ngày soạn: 2026-09-05.

---

## 1. Hiểu đúng ngay từ đầu

**Một tool = một hàm Python + một bản mô tả.** Hết.

Nhưng phần quan trọng không phải phần bạn tưởng:

| | Tỉ trọng công sức | Ai làm được |
|---|---|---|
| **Viết mô tả** (docstring) | ~70% | **Bạn** — người hiểu nghiệp vụ |
| Viết code lấy dữ liệu | ~30% | Lập trình viên (hoặc tôi) |

Lý do: code chỉ cần chạy đúng. Mô tả mới là thứ quyết định **AI có gọi tool đúng
lúc không, truyền đúng tham số không, và hiểu đúng kết quả không**.

> Cách nghĩ đúng: bạn không lập trình cho AI. Bạn **viết bản mô tả công việc cho
> một đồng nghiệp mới** — người rất giỏi nhưng chưa biết gì về dự án, và **không
> hỏi lại được**. Mọi thứ họ cần biết phải nằm trong bản mô tả đó.

---

## 2. Cái AI thực sự nhìn thấy

Bạn viết hàm này:

```python
@mcp.tool()
def get_budget(asset_class: str, lod: int | None = None,
               platform: str | None = None) -> dict[str, Any]:
    """Tra ngưỡng số cụ thể (tricount, texel density, số material...) của một class.

    Đây là câu hỏi hay gặp nhất: "xe hạng B LOD2 tối đa bao nhiêu tri?".
    Mọi con số trả về đều kèm rule_id — luôn dẫn kèm khi trả lời.
    """
```

SDK tự sinh ra cái này và gửi cho AI:

```jsonc
{
  "name": "get_budget",
  "description": "Tra ngưỡng số cụ thể (tricount, texel density, số material...)
                  của một class.\n\n Đây là câu hỏi hay gặp nhất: \"xe hạng B LOD2
                  tối đa bao nhiêu tri?\". Mọi con số trả về đều kèm rule_id —
                  luôn dẫn kèm khi trả lời.",
  "input_schema": {
    "properties": {
      "asset_class": { "type": "string" },
      "lod":         { "anyOf": [{"type": "integer"}, {"type": "null"}], "default": null },
      "platform":    { "anyOf": [{"type": "string"},  {"type": "null"}], "default": null }
    },
    "required": ["asset_class"]
  }
}
```

Ba điều rút ra:

1. **Docstring của bạn = `description`.** Nguyên văn, không qua xử lý. Viết cẩu
   thả thì AI đoán mò khi nào nên gọi.
2. **Type hints = `input_schema`.** `lod: int | None = None` tự thành "số nguyên,
   không bắt buộc". Bạn không phải viết JSON schema bằng tay.
3. **AI chỉ thấy tên + mô tả + schema.** Nó **không** đọc được code bên trong.
   Nên mọi thứ nó cần biết phải nằm ở 3 chỗ đó.

---

## 3. Giải phẫu một tool — 5 phần

```python
@mcp.tool()                                        # ① đăng ký
def whats_changed_for(                             # ② tên = câu hỏi người dùng
        asset_class: str,                          # ③ tham số + kiểu
        since: str | None = None) -> dict:
    """Khách hàng đã đổi gì ảnh hưởng tới một loại asset, từ mốc nào tới nay.

    Dùng khi hoạ sĩ hỏi "tuần này có gì mới với xe không", "tôi nghỉ 2 tuần,
    đã bỏ lỡ gì".                                  # ④ KHI NÀO gọi

    Danh sách rỗng nghĩa là không có thay đổi nào — nói thẳng như vậy, đừng
    suy đoán.                                      # ④ luật ứng xử
    """
    ...
    return {"found": True, "count": 2, "updates": [...]}   # ⑤ dữ liệu có cấu trúc
```

| Phần | Vai trò | Sai thì sao |
|---|---|---|
| ① `@mcp.tool()` | Đăng ký với server | Không có thì AI không thấy tool |
| ② Tên hàm | Tên tool AI nhìn thấy | Tên kỹ thuật khó hiểu → AI chọn nhầm tool |
| ③ Tham số + type hints | Sinh schema | Thiếu type hint → AI không biết truyền gì |
| ④ Docstring | AI quyết định **khi nào** gọi và **xử lý kết quả ra sao** | **Đây là chỗ hầu hết lỗi phát sinh** |
| ⑤ Giá trị trả về | Dữ liệu AI diễn đạt lại cho người | Trả văn xuôi → AI không lọc/tính tiếp được |

---

## 4. Bốn bước tạo một tool

### Bước 1 — Viết ra câu hỏi thật của người dùng

Không bắt đầu từ "tôi có dữ liệu gì". Bắt đầu từ **câu hoạ sĩ thật sự gõ vào chat**:

> *"Tuần này khách có đổi gì với xe không?"*
> *"Tôi nghỉ 2 tuần, đã bỏ lỡ gì?"*

Nhiều câu hỏi khác nhau nhưng cùng một nhu cầu → **một tool**. Cùng một dữ liệu
nhưng hai nhu cầu khác nhau → **hai tool**.

### Bước 2 — Viết docstring TRƯỚC khi viết code

Nghe ngược nhưng đây là bước quan trọng nhất. Docstring phải trả lời 4 câu:

| Câu | Ví dụ |
|---|---|
| Tool này làm gì? | "Khách hàng đã đổi gì ảnh hưởng tới một loại asset" |
| **Dùng khi nào?** | "Khi hoạ sĩ hỏi tuần này có gì mới, hoặc vừa đi vắng về" |
| **KHÔNG dùng khi nào?** | *(nếu dễ nhầm với tool khác — vd `check_asset` vs `check_file`)* |
| Kết quả rỗng thì sao? | "Nghĩa là không có thay đổi — nói thẳng, đừng suy đoán" |

Câu thứ tư quan trọng bậc nhất trong dự án của bạn: **nó là hàng rào chống AI bịa
spec.** Không có nó, AI gặp kết quả rỗng sẽ có xu hướng trả lời từ kiến thức chung
về game art — và hoạ sĩ làm sai asset theo con số bịa đó.

### Bước 3 — Viết hàm

Ba nguyên tắc:

```python
# ✅ Trả dữ liệu có cấu trúc, để AI tự diễn đạt lại
return {"found": True, "count": 2, "updates": [...]}

# ❌ Trả văn xuôi đã viết sẵn — AI không lọc, không đếm, không tính tiếp được
return "Có 2 update: CU-2026-047 giảm material xuống 4..."
```

```python
# ✅ Luôn có nhánh "không có" rõ ràng
if not ups:
    return {"found": False, "updates": [],
            "error": f"Không có update nào ảnh hưởng tới '{asset_class}'."}
```

```python
# ✅ Kèm đủ ngữ cảnh để AI trả lời trọn vẹn trong MỘT lần gọi
"affected_rules": [{"rule_id": "VEH-MAT-001", "title": "...", "current_version": 1}]
# ❌ Chỉ trả ["VEH-MAT-001"] → AI phải gọi thêm get_rule 3 lần nữa
```

### Bước 4 — Thử bằng câu hỏi thật

Không thử bằng "gọi tool X". Thử bằng đúng câu hoạ sĩ sẽ gõ:

> *"tôi nghỉ 2 tuần về, có gì mới với xe không?"*

Rồi kiểm 3 điều: **có gọi đúng tool không · có truyền đúng tham số không · có
bịa gì không**. Bước cuối bắt buộc — hỏi một câu mà dữ liệu **không** có
(vd *"khách đổi gì với vegetation?"*) và xem nó có bịa ra không.

---

## 5. Ví dụ đầy đủ — tool `whats_changed_for`

Tool này vừa được thêm thật vào server. Toàn bộ công việc gồm 3 phần:

### 5.1 Dữ liệu — bạn viết *(không cần lập trình)*

`artspec/changelog/CU-2026-047.yaml`:

```yaml
id: CU-2026-047
date_received: 2026-08-28
source: "Ghi chú họp review tuần 35 với khách"
raw_excerpt: |
  (Dán nguyên văn phần khách nói — để truy vết, không diễn giải lại.)
summary_vi: >
  Khách yêu cầu giảm số material slot tối đa của xe từ 6 xuống 4 vì draw call
  vượt ngưỡng trên console.
affects_rules: [VEH-MAT-001]
affects_asset_classes: [vehicle_exterior]
action_required: >
  Xe đã submit giữ nguyên. Xe đang làm phải gộp material trước khi submit.
approved_by: "<Art Lead>"
effective_from: 2026-09-01
status: applied
```

**Đây là 90% giá trị của tool.** Không có file này thì tool trả về rỗng.

### 5.2 Truy vấn dữ liệu — trong `registry.py`

```python
def updates_for(self, asset_class=None, since=None):
    """Update khách hàng, mới nhất trước. Lọc theo class và mốc thời gian."""
    out = list(self.updates)
    if asset_class:
        out = [u for u in out if asset_class in (u.get("affects_asset_classes") or [])]
    if since:
        cut = _as_date(since)
        out = [u for u in out
               if _as_date(u.get("effective_from") or u.get("date_received")) >= cut]
    return sorted(out, key=lambda u: str(u.get("effective_from", "")), reverse=True)
```

### 5.3 Tool — trong `server.py`

```python
@mcp.tool()
def whats_changed_for(asset_class: str, since: str | None = None) -> dict[str, Any]:
    """Khách hàng đã đổi gì ảnh hưởng tới một loại asset, từ mốc thời gian nào tới nay.

    Dùng khi hoạ sĩ hỏi "tuần này có gì mới với xe không", "tôi nghỉ 2 tuần, đã bỏ
    lỡ gì", hoặc khi họ chuẩn bị bắt tay vào một asset mới.

    `since` dạng YYYY-MM-DD. Bỏ trống = lấy toàn bộ lịch sử.

    Mỗi update kèm danh sách luật bị ảnh hưởng và VERSION HIỆN TẠI của luật đó —
    hãy nêu cả hai khi trả lời, và nhắc `action_required` vì đó là phần quyết
    định hoạ sĩ có phải sửa asset cũ hay không.

    Danh sách rỗng nghĩa là không có thay đổi nào — nói thẳng như vậy, đừng suy
    đoán từ nội dung các luật.
    """
    reg = _reg()
    ups = reg.updates_for(asset_class, since)
    if not ups:
        return {"found": False, "asset_class": asset_class, "updates": [],
                "error": f"Không có update nào của khách ảnh hưởng tới '{asset_class}'."}
    out = []
    for u in ups:
        rules = [{"rule_id": rid,
                  "title": (r := reg.get(rid)) and r.title,
                  "current_version": r.version if r else None}
                 for rid in u.get("affects_rules", [])]
        out.append({"update_id": u["id"], "effective_from": u.get("effective_from"),
                    "summary": u.get("summary_vi"), "source": u.get("source"),
                    "action_required": u.get("action_required"),
                    "affected_rules": rules})
    return {"found": True, "count": len(out), "updates": out}
```

### 5.4 Kết quả AI nhận được

```jsonc
{
  "found": true, "count": 1,
  "updates": [{
    "update_id": "CU-2026-047",
    "effective_from": "2026-09-01",
    "summary": "Khách yêu cầu giảm số material slot tối đa của xe từ 6 xuống 4…",
    "source": "Ghi chú họp review tuần 35 với khách",
    "action_required": "Xe đã submit giữ nguyên. Xe đang làm phải gộp material…",
    "affected_rules": [{"rule_id": "VEH-MAT-001",
                        "title": "Giới hạn số material slot",
                        "current_version": 1}]
  }]
}
```

Hỏi class không có update:

```jsonc
{"found": false, "updates": [],
 "error": "Không có update nào của khách ảnh hưởng tới 'building'."}
```

→ AI trả lời *"không có thay đổi nào"*, không bịa.

---

## 6. Bảy nguyên tắc viết tool tốt

| # | Nguyên tắc | Ví dụ |
|---|---|---|
| 1 | **Đặt tên theo câu hỏi, không theo cấu trúc dữ liệu** | `get_budget` ✅ · `query_rules_table` ❌ |
| 2 | **Docstring viết cho AI đọc, không cho người đọc** | Ghi rõ "dùng khi nào", "không dùng khi nào" — không mô tả thuật toán |
| 3 | **Trả dữ liệu có cấu trúc, không trả văn xuôi** | Trừ trường hợp cố ý (xem sai lầm #3 bên dưới) |
| 4 | **Luôn có nhánh `found: false` kèm lời giải thích** | Hàng rào chống bịa số |
| 5 | **Một tool = một việc** | `check_file` và `check_inbox` tách riêng, dù dùng chung engine |
| 6 | **Đủ ngữ cảnh trong một lần gọi** | Trả kèm `title` + `current_version`, không bắt AI gọi thêm |
| 7 | **Đừng quá 12–15 tool** | Nhiều quá thì AI chọn nhầm. Gộp bằng tham số thay vì tách tool mới |

Về nguyên tắc 7: server hiện có **13 tool** — đã gần trần. Muốn thêm thì nên gộp
bớt trước, đừng thêm mãi.

---

## 7. Bốn sai lầm hay gặp

### ❌ 1. Tool bọc quá mỏng quanh dữ liệu

```python
def get_rules_raw(): ...      # trả về tất cả
def get_rule_field(id, f): ...  # lấy 1 field
```
AI phải gọi 5 lần mới trả lời được một câu. **Tool phải ở tầm câu hỏi của người
dùng, không ở tầm bảng dữ liệu.**

### ❌ 2. Docstring mô tả code thay vì mô tả tình huống

```python
"""Truy vấn danh sách update, lọc theo asset_class và so sánh effective_from."""
```
Đúng về kỹ thuật, vô dụng với AI — nó không biết **khi nào** thì nên gọi.

### ❌ 3. Trả text đã format sẵn khi lẽ ra nên trả dữ liệu

`check_asset` và `check_file` trong server này **cố ý** trả text — vì báo cáo lỗi
5 phần cần giữ nguyên định dạng, và AI chỉ cần diễn đạt lại. Đó là ngoại lệ có
chủ ý. **Mặc định vẫn phải trả dữ liệu có cấu trúc**, để AI còn lọc, đếm, so sánh.

### ❌ 4. Quên dặn AI phải làm gì khi không có dữ liệu

Đây là sai lầm nguy hiểm nhất **trong dự án của bạn**. Không dặn → AI trả lời từ
kiến thức chung về game art → hoạ sĩ làm asset theo con số bịa. Ngoài docstring
từng tool, server còn có `instructions` chung dặn lại điều này một lần nữa cho
mọi tool.

---

## 8. Tool, Resource hay Prompt?

| | Là gì | Ai kích hoạt | Ví dụ trong dự án |
|---|---|---|---|
| **Tool** | Hàm AI gọi khi cần | AI tự quyết | `get_budget`, `check_file` |
| **Resource** | Tài liệu AI đọc, như một file | AI hoặc người chọn | `spec://index`, `spec://glossary` |
| **Prompt** | Mẫu câu lệnh dựng sẵn | **Người** chọn từ menu | `pre_submit_review` |

Cách chọn nhanh:

- Cần **tham số** và trả kết quả khác nhau tuỳ đầu vào → **Tool**
- Nội dung **tĩnh**, đọc cả khối → **Resource**
- Muốn hoạ sĩ **bấm một nút** thay vì tự nghĩ câu hỏi → **Prompt**

---

## 9. Checklist trước khi thêm một tool

- [ ] Viết ra được ít nhất **3 câu hỏi thật** mà hoạ sĩ sẽ gõ để dùng tool này
- [ ] Không tool nào đang có trả lời được 3 câu đó
- [ ] Docstring nói rõ **dùng khi nào** và **kết quả rỗng nghĩa là gì**
- [ ] Có nhánh `found: false` kèm câu giải thích
- [ ] Trả đủ ngữ cảnh để AI không phải gọi thêm tool khác
- [ ] Đã thử bằng một câu hỏi mà dữ liệu **không** có → AI không bịa
- [ ] Tổng số tool vẫn ≤ 15

---

## 10. Bạn tự làm được cái nào

| Việc | Bạn tự làm? |
|---|---|
| Viết file dữ liệu (`changelog/`, `rules/`, `glossary/`) | ✅ Chỉ là YAML — sửa bằng Notepad++ |
| **Viết docstring cho tool mới** | ✅ **Và bạn nên tự viết** — bạn hiểu nghiệp vụ hơn tôi |
| Sửa docstring của tool đang có | ✅ Mở `server.py`, sửa phần trong `"""..."""` |
| Viết code truy vấn dữ liệu | ❌ Nhắn tôi |
| Thêm tool hoàn toàn mới | ❌ Nhắn tôi — kèm docstring bạn đã viết sẵn |

**Cách làm việc hiệu quả nhất:** bạn viết docstring (phần 70% giá trị), gửi tôi,
tôi viết phần code (30% còn lại). Kiểu như:

> *"Tôi muốn một tool trả lời câu: 'asset nào của tôi đang có waiver sắp hết hạn?'.
> Dùng khi hoạ sĩ hoặc Lead rà lại cuối tháng. Rỗng nghĩa là không có cái nào sắp
> hết hạn, nói thẳng."*

Đủ để tôi viết ngay.

---

## Đọc thêm

| File | Nội dung |
|---|---|
| [`artspec/artspec/server.py`](artspec/artspec/server.py) | 13 tool thật — đọc để thấy nhiều kiểu docstring khác nhau |
| [`artspec/README.md`](artspec/README.md) | Cách chạy server, gắn vào Claude Desktop |
| [`BAT_DAU_TU_DAU.md`](BAT_DAU_TU_DAU.md) | Kế hoạch tổng thể — tool chỉ là một mảnh nhỏ |
