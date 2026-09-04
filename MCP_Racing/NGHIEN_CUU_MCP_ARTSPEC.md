# Nghiên cứu: MCP server cho quản lý chất lượng 3D artset — dự án Racing Open-World

> **Trạng thái:** Tài liệu NGHIÊN CỨU & THIẾT KẾ. Chưa viết code — theo đúng yêu cầu "nghiên cứu quy
> trình trước khi bắt đầu làm".
> **Người dùng đích:** Art Lead quản lý chất lượng 3D artset (bạn) + đội hoạ sĩ 3D.
> **Ngày soạn:** 2026-09-04. Các thông tin về MCP/SDK đã được kiểm chứng qua web ở thời điểm này
> (xem [Nguồn tham khảo](#13-nguồn-tham-khảo)) — MCP đang thay đổi nhanh, kiểm tra lại trước khi code.
>
> *Ghi chú repo: repo này vốn là tài liệu Grasshopper. Tài liệu MCP nằm riêng trong thư mục
> `MCP_Racing/`, không đụng vào `Grasshopper.html`.*

---

## Mục lục

1. [Tóm tắt & khuyến nghị](#1-tóm-tắt--khuyến-nghị)
2. [MCP là gì (giải thích cho Art Lead)](#2-mcp-là-gì-giải-thích-cho-art-lead)
3. [Bài toán thật của bạn](#3-bài-toán-thật-của-bạn)
4. [Nghiên cứu quy trình hiện tại (bước bắt buộc trước khi code)](#4-nghiên-cứu-quy-trình-hiện-tại-bước-bắt-buộc-trước-khi-code)
5. [Kiến trúc đề xuất](#5-kiến-trúc-đề-xuất)
6. [Spec Registry — trái tim của hệ thống](#6-spec-registry--trái-tim-của-hệ-thống)
7. [Thiết kế MCP server: Tools / Resources / Prompts](#7-thiết-kế-mcp-server-tools--resources--prompts)
8. [3 phương án triển khai — so sánh](#8-3-phương-án-triển-khai--so-sánh)
9. [Stack kỹ thuật Python](#9-stack-kỹ-thuật-python)
10. [Bảo mật, quyền & NDA](#10-bảo-mật-quyền--nda)
11. [Roadmap theo giai đoạn](#11-roadmap-theo-giai-đoạn)
12. [Rủi ro & câu hỏi cần chốt](#12-rủi-ro--câu-hỏi-cần-chốt)
13. [Nguồn tham khảo](#13-nguồn-tham-khảo)

---

## 1. Tóm tắt & khuyến nghị

**Kết luận ngắn:** MCP là công cụ đúng cho bài toán của bạn, nhưng **80% công việc không nằm ở code
MCP** — nó nằm ở việc chuẩn hoá techspec thành dữ liệu máy đọc được. Nếu bỏ qua bước đó và cắm MCP
thẳng vào Confluence/Notion, kết quả sẽ là một con bot trả lời mơ hồ, đôi khi sai — và với art
production, spec sai = hoạ sĩ làm lại asset = tốn hơn cả không có bot.

**Khuyến nghị 3 điểm:**

| # | Khuyến nghị | Lý do |
|---|---|---|
| 1 | **Phương án C (Hybrid)** — dùng connector Confluence/Notion có sẵn cho tra cứu rộng, + MCP server riêng cho "spec cứng" (budget, naming, checklist, validate) | Connector sẵn có ngay, 0 code; nhưng nó không tra được con số chính xác và không validate được asset |
| 2 | **Xây "Spec Registry" trước, MCP sau** — chuẩn hoá techspec thành YAML có ID + version + link nguồn | Đây là việc khó nhất và có giá trị nhất; kể cả không làm MCP, nó vẫn hữu ích |
| 3 | **Bắt đầu với 1 asset class duy nhất** (đề xuất: Vehicle) | Chứng minh giá trị trong 2-3 tuần thay vì làm cả hệ thống rồi mới biết sai |

**Điều MCP KHÔNG giải quyết được** (nói thẳng để bạn không kỳ vọng sai):
- Không làm hoạ sĩ tự giác đọc spec. Nó chỉ làm việc tra cứu nhanh hơn từ 10 phút xuống 10 giây.
- Không thay được review của Art Lead. Nó bắt được lỗi định lượng (tricount, texel density, naming),
  không bắt được lỗi thẩm mỹ (silhouette xấu, sai art direction).
- Không tự biết khách hàng vừa update gì. Phải có người/quy trình đưa update đó vào hệ thống.

---

## 2. MCP là gì (giải thích cho Art Lead)

**MCP (Model Context Protocol)** là một chuẩn mở do Anthropic tạo ra, cho phép AI (Claude, Cursor,
VS Code…) kết nối với dữ liệu và công cụ của bạn.

Ví von theo ngôn ngữ art pipeline: **MCP giống như plugin cho DCC**. Maya không tự biết pipeline của
studio bạn — bạn viết plugin để nó biết. Claude cũng không tự biết techspec dự án bạn — bạn viết MCP
server để nó biết.

MCP server cung cấp 3 loại "khả năng":

| Loại | Là gì | Ví dụ trong dự án bạn |
|---|---|---|
| **Tools** | Hàm mà AI được phép gọi | `get_budget("vehicle_exterior", lod=0)` → trả về tricount cho phép |
| **Resources** | Dữ liệu AI đọc được (như file) | `spec://techspec/vehicle` → nguyên văn chương Vehicle của techspec |
| **Prompts** | Mẫu câu lệnh dựng sẵn | "Review asset này theo checklist submit" |

**Phiên bản chuẩn mới nhất: `2026-07-28`.** Vài thay đổi quan trọng nếu bạn sắp code:
- **Stateless** — bỏ handshake `initialize` và header `Mcp-Session-Id`. Mỗi request tự mang đủ thông
  tin. Hệ quả tốt: server chạy sau load balancer bình thường, dễ scale.
- **Cache** — `tools/list`, `resources/read`… trả kèm `ttlMs` + `cacheScope`, client tự biết cache
  bao lâu.
- **Auth chặt hơn** — OAuth 2.1, bắt buộc validate `iss` (RFC 9207), chuyển từ Dynamic Client
  Registration sang Client ID Metadata Documents (CIMD).
- **Đã deprecate:** Roots, Sampling, Logging, và transport HTTP+SSE cũ → **đừng dùng cho code mới.**
- Có chính sách vòng đời: tính năng bị deprecate phải sống thêm tối thiểu 12 tháng → chuẩn ổn định
  hơn trước, đỡ lo build xong lại phải viết lại.

---

## 3. Bài toán thật của bạn

Bạn nêu 2 yêu cầu:
> (a) hoạ sĩ phải hiểu hết techspec của dự án — (b) cập nhật mọi update mới nhất của khách hàng.

Dịch sang bài toán kỹ thuật, đây thực chất là **4 nỗi đau khác nhau**, cần 4 cách xử lý khác nhau:

| # | Nỗi đau | Biểu hiện thực tế | MCP giúp được? |
|---|---|---|---|
| P1 | **Tra cứu chậm** | Hoạ sĩ không nhớ tricount LOD2 của xe hạng B → hỏi lead → lead trả lời → mất 15 phút của 2 người | ✅ Rất tốt — đây là use case mạnh nhất |
| P2 | **Spec bị hiểu sai** | Techspec viết "texel density 10.24 px/cm" nhưng hoạ sĩ không biết áp cho mesh nào, đo thế nào | ✅ Tốt — nếu spec có ví dụ + định nghĩa thuật ngữ |
| P3 | **Update khách hàng bị lạc** | Khách gửi mail đổi naming convention → lead biết → 3 hoạ sĩ không biết → 20 asset sai tên | ⚠️ Chỉ giúp một nửa — cần quy trình người, không chỉ tool |
| P4 | **Asset sai spec lọt qua review** | Submit rồi mới phát hiện quá tricount, thiếu LOD, UV overlap | ✅ Tốt — nhưng nên làm bằng validator tự động hơn là chatbot |

**Ưu tiên:** P1 → P2 → P4 → P3. P3 khó nhất vì nó là vấn đề **quy trình**, không phải vấn đề công cụ.

---

## 4. Nghiên cứu quy trình hiện tại (bước bắt buộc trước khi code)

Đây là phần bạn yêu cầu — "nghiên cứu quy trình trước khi bắt đầu làm". Trước khi viết dòng code nào,
cần trả lời được bảng dưới. **Cách làm: tự audit + phỏng vấn 3-4 hoạ sĩ (mỗi người 30 phút).**

### 4.1 Audit techspec hiện tại

| Câu hỏi | Vì sao cần | Ghi kết quả |
|---|---|---|
| Techspec dài bao nhiêu trang / bao nhiêu page Confluence? | Quyết định khối lượng chuẩn hoá | |
| Có bao nhiêu **quy tắc định lượng** (có con số: tricount, texture size, texel density, số material)? | Đây là phần MCP làm tốt nhất | |
| Có bao nhiêu **quy tắc định tính** (art direction, "phải trông thật", "tránh nhìn giả")? | Phần này MCP làm kém — đừng cố nhét vào | |
| Techspec có **mâu thuẫn nội bộ** không? (2 chỗ ghi 2 con số khác nhau) | Nếu có → phải fix TRƯỚC, không MCP nào cứu được | |
| Mỗi quy tắc có **ngày hiệu lực** không? | Không có → hoạ sĩ không biết spec nào còn dùng | |
| Ai có quyền sửa techspec? Sửa xong ai được báo? | Là gốc của P3 | |

### 4.2 Audit luồng update từ khách hàng

| Câu hỏi | Ghi kết quả |
|---|---|
| Khách gửi update qua kênh nào? (mail / Slack / Jira comment / meeting note / file Excel đính kèm) | |
| Trung bình bao nhiêu update/tuần? | |
| Ai là người "dịch" update của khách thành thay đổi techspec? | |
| Từ lúc khách nói đến lúc techspec được sửa: bao lâu? | |
| Có changelog không? Nếu có, ở đâu? | |
| Đã từng có asset phải làm lại vì không biết update? Bao nhiêu lần / tháng? | ← **Con số này chính là ROI của cả dự án** |

### 4.3 Phỏng vấn hoạ sĩ (bản câu hỏi)

1. Trong tuần vừa rồi, bạn cần tra techspec mấy lần? Tra cái gì?
2. Bạn tra bằng cách nào — mở Confluence, hỏi lead, hay đoán theo asset cũ?
3. Có quy tắc nào bạn thấy khó hiểu / mơ hồ không? Kể tên.
4. Lần gần nhất asset bị trả về vì sai spec, lỗi là gì?
5. Nếu có 1 chỗ hỏi được "xe hạng B LOD2 tối đa bao nhiêu tri?" và trả lời trong 5 giây, bạn có dùng
   không? Dùng ở đâu — trong Maya, trên browser, hay trong chat?

> **Câu 5 quyết định kiến trúc.** Nếu hoạ sĩ muốn dùng trong DCC → cần thêm lớp cầu nối, phức tạp
> hơn nhiều. Nếu chấp nhận dùng trong chat → làm được ngay.

### 4.4 Tiêu chí "đủ điều kiện làm MCP"

Chỉ nên sang bước code khi:
- [ ] Có ít nhất **30 quy tắc định lượng** đã chuẩn hoá được (dưới ngưỡng này thì 1 file PDF 2 trang
      là đủ, không cần MCP).
- [ ] Techspec **không còn mâu thuẫn nội bộ** ở asset class định làm thí điểm.
- [ ] Có **1 người chịu trách nhiệm** cập nhật Spec Registry khi khách update (có thể là bạn).
- [ ] Đo được con số P3 ở mục 4.2 (số asset làm lại/tháng) để sau này chứng minh hiệu quả.

---

## 5. Kiến trúc đề xuất

### 5.1 Sai lầm cần tránh

```
❌ SAI:   Claude ──MCP──> Confluence API ──> trả nguyên văn page cho AI tự đọc
```

Vì sao sai:
1. Wiki viết **cho người đọc**, câu văn dài, số nằm lẫn trong đoạn văn → AI đọc ra số sai là chuyện
   thường.
2. Không có **version / ngày hiệu lực** → AI trả lời theo page cũ mà không ai biết.
3. Không **truy vết** được: hoạ sĩ hỏi "sao biết 45k tri?", AI không chỉ ra được nguồn.
4. Không **kiểm chứng** được: bạn không thể review "AI đang trả lời đúng hay sai" nếu không có nguồn
   chuẩn để đối chiếu.

### 5.2 Kiến trúc đúng — 3 lớp

```
┌─ LỚP 1: NGUỒN (nơi con người viết) ──────────────────────────────┐
│  Confluence / Notion / Google Docs   ← techspec gốc              │
│  Mail / Slack / Jira                 ← update khách hàng          │
└──────────────────────────┬───────────────────────────────────────┘
                           │  sync (bán tự động + người duyệt)
                           ▼
┌─ LỚP 2: SPEC REGISTRY (nơi máy đọc) ─────────────────────────────┐
│  Repo git chứa YAML/JSON đã chuẩn hoá:                           │
│    • rules/     mỗi quy tắc = 1 record có id, version, nguồn     │
│    • budgets/   bảng số theo asset_class × LOD × platform        │
│    • naming/    quy ước đặt tên (kèm regex)                      │
│    • glossary/  định nghĩa thuật ngữ theo cách dự án hiểu        │
│    • changelog/ lịch sử thay đổi + ngày hiệu lực                 │
│  ← ĐÂY LÀ SINGLE SOURCE OF TRUTH. Git lo version + review + diff │
└──────────────────────────┬───────────────────────────────────────┘
                           │  đọc (chỉ đọc, nhanh, offline được)
                           ▼
┌─ LỚP 3: MCP SERVER (Python) ─────────────────────────────────────┐
│  Tools · Resources · Prompts  (chi tiết ở mục 7)                 │
│  Mọi câu trả lời BẮT BUỘC kèm: rule_id + version + link nguồn    │
└──────────────────────────┬───────────────────────────────────────┘
                           ▼
        Claude Desktop / Claude Code / (sau này) plugin trong DCC
```

### 5.3 Vì sao Spec Registry nằm trong git

| Lợi ích | Giải thích |
|---|---|
| Version miễn phí | `git log` cho biết quy tắc nào đổi khi nào, do ai |
| Review được | Update khách hàng → tạo Pull Request → bạn duyệt → merge. Không ai lén sửa spec |
| Rollback được | Khách đổi ý → revert 1 commit |
| Diff đọc được | "Tuần này spec đổi gì?" = `git diff` — không cần đọc lại cả wiki |
| Offline | MCP server không phụ thuộc mạng Confluence lúc hoạ sĩ đang cần |

> **Điểm mấu chốt:** Confluence/Notion vẫn giữ nguyên vai trò "nơi con người đọc và thảo luận".
> Spec Registry là bản dịch máy-đọc-được của nó. Hai bên phải có quy trình đồng bộ rõ ràng, nếu không
> sẽ trôi lệch (drift) — xem [rủi ro R3](#12-rủi-ro--câu-hỏi-cần-chốt).

---

## 6. Spec Registry — trái tim của hệ thống

Đây là phần cần bạn (Art Lead) làm, không phải lập trình viên. Dưới đây là **schema đề xuất**.

> ⚠️ **Mọi con số dưới đây là VÍ DỤ MINH HOẠ để bạn hình dung cấu trúc — KHÔNG phải số của dự án
> bạn.** Số thật phải lấy từ techspec thật.

### 6.1 Một quy tắc (`rules/vehicle/VEH-TRI-001.yaml`)

```yaml
id: VEH-TRI-001
title: "Giới hạn tricount thân xe ngoại thất"
asset_class: vehicle_exterior
category: geometry          # geometry | texture | material | naming | uv | rig | lod | export
type: quantitative          # quantitative (có số, máy check được) | qualitative (chỉ người đánh giá)

rule:
  metric: triangle_count
  unit: tris
  scope: "Toàn bộ mesh ngoại thất, KHÔNG tính bánh xe và nội thất"
  limits:                   # ví dụ minh hoạ
    - { lod: 0, platform: pc,      max: 120000 }
    - { lod: 1, platform: pc,      max: 45000  }
    - { lod: 2, platform: pc,      max: 12000  }
    - { lod: 0, platform: console, max: 90000  }
  tolerance_percent: 0      # 0 = cứng, không được vượt

why: "Ngân sách GPU cho 12 xe hiển thị đồng thời trong cảnh đua."
how_to_check: "Maya > Display > Heads Up Display > Poly Count, đọc dòng Tris của selection."
common_mistakes:
  - "Đếm cả bánh xe (bánh có ngân sách riêng, xem VEH-TRI-002)"
  - "Đọc nhầm Faces thay vì Tris"

source:
  system: confluence
  url: "https://<công-ty>.atlassian.net/wiki/spaces/PROJ/pages/12345"
  section: "3.2 Vehicle Geometry Budget"

version: 3
effective_from: 2026-08-15
status: active              # active | superseded | draft
supersedes: VEH-TRI-001@v2
changed_by_update: CU-2026-041
```

**Vì sao từng field quan trọng:**

| Field | Không có nó thì sao |
|---|---|
| `id` | Không trích dẫn được. Hoạ sĩ và lead cãi nhau không có mã số để chỉ |
| `scope` | Nguồn hiểu nhầm số 1 trong art production: "120k tri" — tính cả bánh không? |
| `how_to_check` | Hoạ sĩ đo bằng cách khác → ra số khác → tưởng mình sai |
| `common_mistakes` | Rẻ nhất để giảm lỗi lặp lại. Mỗi lần review bắt lỗi gì, thêm vào đây |
| `why` | Hoạ sĩ hiểu lý do thì tự biết linh hoạt; không hiểu thì hoặc phá luật hoặc làm máy móc |
| `effective_from` + `version` | Trả lời được "spec này áp cho asset tôi làm tháng trước không?" |
| `changed_by_update` | Nối quy tắc ↔ update khách hàng → trả lời được "khách đổi gì ảnh hưởng tới tôi?" |

### 6.2 Một update khách hàng (`changelog/CU-2026-041.yaml`)

```yaml
id: CU-2026-041
date_received: 2026-08-10
source: "Email từ <Producer khách hàng>, tiêu đề 'Vehicle budget revision'"
raw_excerpt: |
  (trích nguyên văn phần liên quan — để truy vết, không diễn giải lại)
summary_vi: "Khách nâng ngân sách tricount LOD0 xe PC từ 100k lên 120k sau khi tối ưu shader."
affects_rules: [VEH-TRI-001]
affects_asset_classes: [vehicle_exterior]
action_required: "Không phải làm lại asset cũ. Asset mới từ 15/08 dùng ngân sách mới."
approved_by: "<Art Lead>"
effective_from: 2026-08-15
status: applied             # received | in_review | applied | rejected
```

> Đây chính là lời giải cho yêu cầu (b) — "cập nhật mọi update mới nhất của khách hàng". Không phải
> đọc mail hộ, mà là **biến mail thành record có cấu trúc, nối được vào quy tắc bị ảnh hưởng.**

### 6.3 Các asset class cần định nghĩa (dự án racing open-world)

Danh sách gợi ý để bạn tick — mỗi class cần bộ budget + naming + checklist riêng:

**Vehicle:** exterior body · wheels/tyres · interior (cockpit) · damage states · liveries/decals ·
glass & transparent parts · engine bay (nếu có)

**Environment (phần nặng nhất của open-world):** road & track surface · terrain / landscape ·
buildings (modular kit) · props (small/medium/large) · vegetation (tree/bush/grass) · rocks & cliffs ·
street furniture (đèn, biển báo, rào chắn) · skybox / distant scenery · decals · trigger/collision mesh

**Chung:** LOD chain rules · collision mesh rules · texel density theo class · material/shader budget ·
texture set & channel packing · UV rules · pivot & transform rules · naming convention · export
settings · file/folder structure

Mỗi class × mỗi loại quy tắc = 1 file YAML. Ước lượng: **150–400 record** cho một dự án open-world
đầy đủ. Đó là lý do phải làm từng class một.

### 6.4 Ước lượng công sức chuẩn hoá

| Việc | Thời gian ước tính |
|---|---|
| Chuẩn hoá 1 asset class (~30 quy tắc) lần đầu | 2–3 ngày công của Art Lead |
| Các class sau (đã quen format) | 0.5–1 ngày/class |
| Duy trì: mỗi update khách hàng | 15–30 phút |

---

## 7. Thiết kế MCP server: Tools / Resources / Prompts

### 7.1 Nguyên tắc thiết kế (quan trọng hơn danh sách tool)

| Nguyên tắc | Vì sao |
|---|---|
| **Mọi câu trả lời phải kèm `rule_id` + `version` + link nguồn** | Hoạ sĩ kiểm chứng được, lead audit được. Không có = không tin được |
| **Không tìm thấy thì nói "không tìm thấy"** | Tool trả `{"found": false, "suggestion": [...]}` — thà không trả lời còn hơn AI đoán ra số sai |
| **Tool trả dữ liệu có cấu trúc, không trả văn xuôi** | Để AI diễn đạt lại theo ngôn ngữ hoạ sĩ; nhưng số liệu thì cứng |
| **Đừng làm quá 12–15 tool** | Nhiều tool quá thì AI chọn sai tool. Gộp bằng tham số thay vì tách tool |
| **Tên tool + mô tả viết cho AI đọc, không cho người đọc** | Mô tả tool là prompt engineering. Ghi rõ "dùng khi nào / không dùng khi nào" |
| **Chỉ đọc trước, ghi sau** | Phase 1 tuyệt đối không cho AI sửa spec. Rủi ro không đáng |

### 7.2 Danh sách Tools đề xuất

| # | Tool | Tham số | Trả về | Giải quyết nỗi đau |
|---|---|---|---|---|
| T1 | `search_spec` | `query`, `asset_class?`, `category?` | Danh sách rule khớp (id, title, tóm tắt, score) | P1 |
| T2 | `get_rule` | `rule_id`, `version?` | Nguyên văn 1 record YAML + link nguồn | P1, P2 |
| T3 | `get_budget` | `asset_class`, `lod?`, `platform?`, `metric?` | Bảng số cụ thể + rule_id | P1 |
| T4 | `get_naming_convention` | `asset_type` | Pattern + regex + 3 ví dụ đúng + 3 ví dụ sai | P1, P4 |
| T5 | `get_checklist` | `asset_class`, `stage` (`wip`/`submit`/`final`) | Checklist dạng list, mỗi mục nối tới rule_id | P4 |
| T6 | `check_asset` | `asset_class`, `metrics` (dict số liệu hoạ sĩ dán vào) | Từng mục pass/fail + rule vi phạm + cách sửa | P4 |
| T7 | `list_updates` | `since?`, `asset_class?`, `status?` | Danh sách update khách hàng | P3 |
| T8 | `get_update` | `update_id` | Chi tiết update + rule bị ảnh hưởng + hành động cần làm | P3 |
| T9 | `whats_changed_for` | `asset_class`, `since` | "Từ ngày X tới nay, những gì ảnh hưởng tới class này" | P3 |
| T10 | `explain_term` | `term` | Định nghĩa theo cách **dự án này** hiểu + cách đo | P2 |
| T11 | `list_asset_classes` | — | Cây asset class + số quy tắc mỗi class | Điều hướng |
| T12 | `get_reference` | `asset_class`, `kind` | Link tới ref image / asset mẫu / blockout chuẩn | P2 |

**Ghi chú thiết kế:**

- **T6 `check_asset` là tool có giá trị cao nhất nhưng cũng dễ sai nhất.** Ở Phase 1, hoạ sĩ **dán
  tay** số liệu vào (tricount, texture size, số material, số UV set). Chỉ khi đã ổn định mới nghĩ tới
  việc lấy số tự động từ DCC — vì lúc đó phải viết plugin Maya/Max/Blender, là dự án riêng.
- **T9 `whats_changed_for` là tool trả lời trực tiếp yêu cầu (b) của bạn.** Hoạ sĩ mở máy sáng thứ
  Hai, hỏi "tuần trước có gì đổi với environment props không?" → có câu trả lời có nguồn.
- **T3 `get_budget` tách riêng khỏi T1/T2** vì đây là câu hỏi được hỏi nhiều nhất, cần trả về con số
  sạch chứ không phải đoạn văn.

### 7.3 Resources đề xuất

Resources = dữ liệu AI đọc nguyên khối (khác Tools là hàm gọi có tham số).

| URI | Nội dung |
|---|---|
| `spec://techspec/{asset_class}` | Toàn bộ quy tắc của 1 class, gộp thành 1 tài liệu đọc được |
| `spec://glossary` | Toàn bộ thuật ngữ dự án |
| `spec://changelog/recent` | 20 update gần nhất |
| `spec://checklist/{asset_class}/{stage}` | Checklist dạng markdown, in ra dán tường được |
| `spec://index` | Bản đồ toàn bộ registry — AI đọc đầu tiên để biết có gì |

Từ spec `2026-07-28`, các response này nên trả kèm `ttlMs` và `cacheScope` để client cache — đặc biệt
có ích với `spec://index` (ít đổi, hay đọc).

### 7.4 Prompts đề xuất

Prompts = mẫu câu lệnh dựng sẵn, hoạ sĩ chọn từ menu thay vì tự nghĩ câu hỏi.

| Prompt | Dùng khi | Nội dung |
|---|---|---|
| `onboard_artist` | Hoạ sĩ mới nhận 1 asset class | Tóm tắt toàn bộ quy tắc class đó theo thứ tự ưu tiên, kèm 5 lỗi hay gặp nhất |
| `pre_submit_review` | Trước khi submit asset | Chạy qua checklist, hỏi hoạ sĩ từng mục, tổng hợp kết quả |
| `weekly_digest` | Sáng thứ Hai | Update khách hàng tuần qua + ảnh hưởng tới class nào |
| `explain_rule_simply` | Hoạ sĩ không hiểu 1 quy tắc | Giải thích rule bằng ngôn ngữ đơn giản + ví dụ + tại sao có luật đó |

---

## 8. 3 phương án triển khai — so sánh

### Phương án A — Chỉ dùng connector có sẵn

Cắm connector Atlassian (Confluence/Jira) hoặc Notion vào Claude, không code gì.

- **Atlassian Rovo MCP Server**: GA từ 02/2026, Claude là đối tác chính thức đầu tiên. Hỗ trợ search
  + tóm tắt Confluence page và Jira issue, tạo/sửa issue và page. Auth bằng OAuth 2.1 hoặc API token,
  **tôn trọng phân quyền sẵn có** — AI chỉ thấy đúng những gì tài khoản đó thấy. Có admin control
  (giới hạn client nào được kết nối) và log sử dụng để audit.
- **Notion MCP Server (remote, chính thức)**: ~16–18 tool, cài bằng OAuth. Notion đang ưu tiên bản
  remote và có thể khai tử bản local.
- **Google Docs**: chưa xác minh được server chính thức trong phiên nghiên cứu này — cần kiểm tra
  riêng nếu techspec nằm ở Google Docs.

| Ưu | Nhược |
|---|---|
| Dùng được **trong ngày**, 0 dòng code | Trả lời theo văn xuôi wiki → dễ ra số sai/mơ hồ |
| Phân quyền chuẩn, đã audit sẵn | Không có version/ngày hiệu lực → không biết spec còn dùng không |
| Không phải maintain gì | Không validate được asset (không có T6) |
| | Không nối được update khách hàng ↔ quy tắc bị ảnh hưởng |

### Phương án B — MCP server riêng hoàn toàn

Tự build Spec Registry + MCP server, không dùng connector.

| Ưu | Nhược |
|---|---|
| Chính xác, có nguồn, có version | Phải chuẩn hoá toàn bộ techspec trước — công sức lớn nhất |
| Validate được asset | Nội dung ngoài registry thì AI mù hoàn toàn |
| Nối được update ↔ quy tắc | Phải maintain sync với wiki, dễ trôi lệch |

### Phương án C — Hybrid ✅ **KHUYẾN NGHỊ**

| Loại câu hỏi | Đi qua |
|---|---|
| "Tricount LOD2 xe hạng B?" · "Đặt tên texture thế nào?" · "Asset tôi có pass không?" | **MCP server riêng** (số cứng, có nguồn, validate được) |
| "Concept xe #7 có gì đặc biệt?" · "Meeting note tuần trước nói gì?" · "Ai đang làm khu vực C?" | **Connector Confluence/Notion** (tìm rộng, không cần chính xác tuyệt đối) |

**Vì sao Hybrid thắng:** bạn không phải chuẩn hoá 100% wiki mới bắt đầu có giá trị. Chuẩn hoá phần
"spec cứng" (~20% nội dung nhưng ~80% câu hỏi) là đủ để chạy; phần còn lại để connector lo.

---

## 9. Stack kỹ thuật Python

> Phần này để tham chiếu khi sang giai đoạn code. Chưa cần đọc kỹ ở giai đoạn nghiên cứu.

### 9.1 SDK

| Hạng mục | Lựa chọn |
|---|---|
| Package | `mcp` — SDK Python chính thức của Model Context Protocol |
| Cài | `pip install "mcp[cli]"` hoặc `uv add "mcp[cli]"` |
| Python | ≥ 3.10 |
| Dòng ổn định | **v2** (v1.x còn tài liệu riêng + migration guide) |
| Hỗ trợ spec | Cả 4 SDK Tier 1 (TypeScript, Python, Go, C#) đã hỗ trợ `2026-07-28` |

Hình dung code (minh hoạ cấu trúc, không phải bản cuối):

```python
from mcp.server import MCPServer

mcp = MCPServer("artspec")

@mcp.tool()
def get_budget(asset_class: str, lod: int = 0, platform: str = "pc") -> dict:
    """Tra ngân sách kỹ thuật (tricount, texture, material) cho một asset class.
    Dùng khi hoạ sĩ hỏi giới hạn số cụ thể. KHÔNG dùng cho câu hỏi định tính về art direction."""
    ...

@mcp.resource("spec://techspec/{asset_class}")
def techspec(asset_class: str) -> str:
    ...
```

SDK tự sinh JSON schema từ type hint và docstring — nên **docstring chính là tài liệu cho AI**, viết
cẩn thận.

> **Lưu ý:** `FastMCP` là framework Python phổ biến cho MCP (FastMCP 1.0 từng được đưa vào SDK chính
> thức; bản độc lập nay đã tới FastMCP 4). Với dự án nội bộ quy mô này, **SDK chính thức `mcp` là đủ**
> — ít phụ thuộc bên ngoài, bám sát spec hơn. Cân nhắc FastMCP chỉ nếu cần các tính năng nâng cao của
> nó (proxy, compose nhiều server, auth dựng sẵn).

### 9.2 Transport

| Transport | Khi nào dùng | Ghi chú |
|---|---|---|
| **stdio** | Phase 1 — chạy local trên máy hoạ sĩ | Đơn giản nhất, không cần server, không cần auth |
| **Streamable HTTP** | Phase 3 — 1 server chung cho cả team | Chuẩn hiện hành. Spec mới đã stateless → chạy sau load balancer bình thường |
| ~~HTTP+SSE~~ | ❌ Không dùng | Transport cũ, đang bị deprecate |

### 9.3 Nơi chạy (host)

Bạn chọn "chưa biết, cứ làm chuẩn". Vậy: **viết server thuần theo chuẩn MCP, không phụ thuộc host.**
Cùng một server sẽ chạy được ở:

| Host | Cách kết nối | Phù hợp với |
|---|---|---|
| Claude Desktop | Local (stdio) hoặc custom connector (remote) | Hoạ sĩ — dễ dùng nhất |
| Claude Code (CLI) | stdio hoặc HTTP | TA / pipeline TD, tích hợp script |
| Cursor / VS Code | stdio | Người viết tool |
| Unreal Engine 5.8 | UE 5.8 (06/2026) có plugin MCP thử nghiệm cho phép LLM nối thẳng vào Editor | Tương lai — validate asset ngay trong engine |

**Custom connector (remote MCP)** dùng được trên Claude, Cowork và Claude Desktop cho các gói Free,
Pro, Max, Team, Enterprise (gói Free giới hạn 1 connector). Cần URL HTTPS + tuỳ chọn OAuth Client ID
/ Secret.

---

## 10. Bảo mật, quyền & NDA

Đây là dự án cho khách hàng → techspec gần như chắc chắn thuộc NDA. Cần chốt trước khi build.

| Vấn đề | Xử lý |
|---|---|
| **Techspec là tài liệu mật của khách** | Xác nhận với producer/legal: được đưa nội dung vào AI assistant không? Gói Team/Enterprise của Claude không dùng dữ liệu để train — nhưng vẫn phải hỏi khách |
| **Phân quyền theo người** | Phase 1 (stdio local) không có auth — chấp nhận được vì mỗi hoạ sĩ chạy trên máy mình với registry họ đã được quyền đọc. Phase 3 (remote) **bắt buộc** OAuth 2.1 |
| **OAuth 2.1 + RFC 9207** | Spec `2026-07-28` yêu cầu validate `iss`; ưu tiên CIMD thay cho Dynamic Client Registration |
| **Không leo thang quyền** | MCP server chỉ đọc registry. Không cấp quyền đọc file hệ thống, không cấp quyền ghi wiki ở Phase 1–2 |
| **Audit** | Log mọi truy vấn (ai hỏi gì, lúc nào, trả rule nào) — vừa để audit, vừa để biết hoạ sĩ hỏi gì nhiều nhất mà bổ sung spec |
| **Registry ở đâu** | Nếu repo private của studio → ổn. Tránh đưa lên dịch vụ public |

---

## 11. Roadmap theo giai đoạn

| Phase | Nội dung | Thời gian | Đầu ra kiểm chứng được |
|---|---|---|---|
| **P0 — Nghiên cứu quy trình** | Chạy hết [mục 4](#4-nghiên-cứu-quy-trình-hiện-tại-bước-bắt-buộc-trước-khi-code): audit techspec, audit luồng update, phỏng vấn 3-4 hoạ sĩ | 1 tuần | Bảng audit đã điền + con số "asset làm lại/tháng" |
| **P0.5 — Bật connector sẵn** | Cắm Atlassian/Notion connector, dùng thử 1 tuần | 1 ngày | Biết được connector trần trụi giải quyết được bao nhiêu %, phần nào còn thiếu |
| **P1 — Spec Registry thí điểm** | Chuẩn hoá **1 asset class** (đề xuất Vehicle) thành YAML theo schema mục 6 | 3–5 ngày | ~30 file YAML trong git |
| **P2 — MCP server tối thiểu** | Python + SDK `mcp`, transport stdio, 5 tool: `search_spec`, `get_rule`, `get_budget`, `get_naming_convention`, `explain_term` | 1–2 tuần | 3 hoạ sĩ dùng thật trong 1 tuần |
| **P3 — Update khách hàng** | Thêm `changelog/`, 3 tool `list_updates` / `get_update` / `whats_changed_for`, prompt `weekly_digest` | 1 tuần | Digest thứ Hai được gửi tự động |
| **P4 — Validate** | `check_asset` + `get_checklist`; hoạ sĩ dán số liệu tay | 1 tuần | Đo được: bao nhiêu lỗi bị bắt TRƯỚC submit |
| **P5 — Nhân rộng** | Chuẩn hoá các asset class còn lại | 0.5–1 ngày/class | Phủ hết artset |
| **P6 — Remote** | Chuyển sang Streamable HTTP + OAuth 2.1, deploy nội bộ, bật log | 1–2 tuần | Cả team dùng, có audit log |
| **P7 — Tự động hoá** *(tuỳ chọn)* | Sync tự động Confluence→Registry (dạng PR chờ duyệt); lấy số liệu tự động từ DCC; tích hợp UE 5.8 MCP | mở | |

**Điểm dừng đánh giá:** hết P2, nếu 3 hoạ sĩ không tự nguyện dùng tiếp thì **dừng lại xem lại**, đừng
làm tiếp P3-P6. Vấn đề khi đó là quy trình/động lực, không phải thiếu tính năng.

---

## 12. Rủi ro & câu hỏi cần chốt

### 12.1 Rủi ro

| # | Rủi ro | Mức | Giảm thiểu |
|---|---|---|---|
| R1 | **Techspec hiện tại mâu thuẫn / thiếu / mơ hồ** → MCP chỉ khuếch đại vấn đề | 🔴 Cao | Đây chính là lý do P0 và P1 phải làm trước. Chuẩn hoá sẽ **lộ ra** các mâu thuẫn — coi đó là lợi ích, không phải trở ngại |
| R2 | **AI trả lời sai số** → hoạ sĩ làm sai asset | 🔴 Cao | Bắt buộc trả kèm rule_id + link nguồn; tool trả "không tìm thấy" thay vì đoán; ghi rõ trong mô tả tool là không được suy diễn số |
| R3 | **Drift** — wiki đổi mà registry không đổi | 🟠 Vừa | 1 người chủ sở hữu duy nhất; check định kỳ; lâu dài thì sync tự động ra PR |
| R4 | **Hoạ sĩ không dùng** | 🟠 Vừa | Bắt đầu từ câu hỏi họ đã hỏi nhiều nhất (từ phỏng vấn P0); đưa vào đúng chỗ họ đang làm việc |
| R5 | **NDA / dữ liệu khách hàng** | 🟠 Vừa | Chốt với producer trước P1; registry ở repo private |
| R6 | **Over-engineer** — build 15 tool mà chỉ 3 tool được dùng | 🟡 Thấp | Roadmap theo phase, có điểm dừng đánh giá sau P2 |
| R7 | **MCP spec đổi** | 🟡 Thấp | Spec `2026-07-28` có chính sách vòng đời tối thiểu 12 tháng; tránh dùng tính năng đã deprecate (Roots, Sampling, Logging, HTTP+SSE) |

### 12.2 Câu hỏi cần bạn chốt trước khi sang code

**Về nội dung:**
1. Techspec hiện đang nằm ở đâu chính xác — Confluence, Notion, hay Google Docs? (Ảnh hưởng tới việc
   connector nào dùng được ngay ở P0.5)
2. Asset class nào nên làm thí điểm? (Gợi ý: class có nhiều quy tắc định lượng nhất và nhiều hoạ sĩ
   nhất — thường là Vehicle hoặc Environment Props)
3. Có bao nhiêu quy tắc định lượng ước tính? Techspec có mâu thuẫn nội bộ không?

**Về tổ chức:**
4. Ai sở hữu Spec Registry (người duy nhất có quyền merge thay đổi)?
5. Bao nhiêu hoạ sĩ trong team? Bao nhiêu người tình nguyện thử ở P2?
6. Đã hỏi producer/khách về việc đưa techspec vào AI assistant chưa?

**Về kỹ thuật:**
7. Studio có repo git nội bộ (GitHub/GitLab private) để đặt registry không?
8. Máy hoạ sĩ có cài được Claude Desktop không? (Chính sách IT của studio)
9. Có TA/pipeline TD nào có thể maintain server sau này không, hay chỉ mình bạn?

---

## 13. Nguồn tham khảo

Đã kiểm chứng trong phiên nghiên cứu này (2026-09-04):

**MCP — chuẩn giao thức**
- [Key Changes — MCP 2026-07-28 changelog](https://modelcontextprotocol.io/specification/2026-07-28/changelog)
- [The 2026-07-28 Specification — MCP Blog](https://blog.modelcontextprotocol.io/posts/2026-07-28/)
- [MCP Specification Version Timeline — hidekazu-konishi.com](https://hidekazu-konishi.com/entry/mcp_specification_version_timeline.html)

**MCP — SDK Python**
- [MCP Python SDK (tài liệu chính thức)](https://py.sdk.modelcontextprotocol.io/)
- [modelcontextprotocol/python-sdk — GitHub](https://github.com/modelcontextprotocol/python-sdk)
- [FastMCP — gofastmcp.com](https://gofastmcp.com/getting-started/welcome)
- [PrefectHQ/fastmcp — GitHub](https://github.com/PrefectHQ/fastmcp)

**Connector có sẵn (Confluence / Notion)**
- [Atlassian Rovo MCP Server is now GA — Inside Atlassian](https://www.atlassian.com/blog/announcements/atlassian-rovo-mcp-ga)
- [atlassian/atlassian-mcp-server — GitHub](https://github.com/atlassian/atlassian-mcp-server)
- [Control Atlassian Rovo MCP server settings — Atlassian Support](https://support.atlassian.com/security-and-access-policies/docs/control-atlassian-rovo-mcp-server-settings/)
- [makenotion/notion-mcp-server — GitHub](https://github.com/makenotion/notion-mcp-server)

**Claude connector / remote MCP**
- [Get started with custom connectors using remote MCP — Anthropic Help Center](https://support.claude.com/en/articles/11175166-get-started-with-custom-connectors-using-remote-mcp)
- [MCP connector — Anthropic Docs](https://docs.anthropic.com/en/docs/agents-and-tools/mcp-connector)

**MCP trong game development**
- [Unreal Engine 5.8 ships MCP server support — byteiota](https://byteiota.com/unreal-engine-5-8-ships-mcp-server-ai-agents-can-now-drive-the-editor/)
- [MCP Server for Game Development: The Complete 2026 Guide — StraySpark](https://www.strayspark.studio/blog/mcp-server-game-development-complete-guide-2026)

---

## Bước tiếp theo

1. Chạy **P0** — điền bảng audit ở [mục 4](#4-nghiên-cứu-quy-trình-hiện-tại-bước-bắt-buộc-trước-khi-code).
2. Trả lời **9 câu hỏi** ở [mục 12.2](#122-câu-hỏi-cần-bạn-chốt-trước-khi-sang-code).
3. Khi đã có câu trả lời → yêu cầu dựng khung Spec Registry (P1) và MCP server tối thiểu (P2).
