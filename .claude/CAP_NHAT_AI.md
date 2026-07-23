# Cập nhật AI/Claude — để agent phiên sau không bị lạc hậu

File này lưu thông tin mới nhất mà 1 agent AI (Claude) từng biết được về chính dòng model Claude/
Anthropic và Claude Code — mục đích: agent ở phiên làm việc SAU không bị kẹt ở kiến thức huấn luyện
cũ (training cutoff có thể trễ hơn thực tế nhiều tháng), đọc file này trước là nắm ngay thông tin mới
nhất đã từng xác nhận, không cần tra lại từ đầu.

> **Quy tắc cập nhật**: bất cứ khi nào 1 agent phát hiện thông tin mới hơn những gì ghi ở đây (qua
> system prompt của chính phiên đó — nguồn đáng tin nhất vì do hạ tầng Anthropic bơm trực tiếp mỗi
> phiên, hoặc qua WebSearch **giới hạn domain chính thức** khi cần biết thêm chi tiết), **cập nhật
> ngay phần liên quan bên dưới + đổi "Cập nhật lần cuối"** — không chờ lịch cố định, không chờ user
> nhắc.

## Cập nhật lần cuối
2026-07-23 (phiên Claude Code, session `claude/grasshopper-component-research-fecpfg`) — đã tra cứu
qua WebSearch giới hạn `anthropic.com`/`docs.anthropic.com`/`docs.claude.com`/`github.com/anthropics`,
cộng thêm WebFetch trực tiếp `CHANGELOG.md` và chạy `claude --version` để đối chiếu thực tế. Xem mục
Nguồn cuối mỗi phần.

## Model Claude hiện tại (đã xác nhận qua nguồn chính thức Anthropic)

Danh sách model đang phát hành công khai, từ mới/mạnh nhất xuống:

| Model | Model ID | Ra mắt | Ghi chú |
|---|---|---|---|
| **Claude Fable 5** | `claude-fable-5` | 09/06/2026 (redeploy 01/07/2026) | Model "Mythos-class" đầu tiên, mạnh nhất từng phát hành công khai — SOTA hầu hết benchmark (software engineering, knowledge work, vision, nghiên cứu khoa học...). Có giai đoạn tạm ngưng vì quy định kiểm soát xuất khẩu của Mỹ, đã gỡ bỏ 30/06/2026 và redeploy lại 01/07/2026 kèm safeguard an ninh mạng mới + "industry jailbreak framework". Vài câu hỏi nhạy cảm sẽ tự động trả lời bằng Opus 4.8 thay vì Fable 5 (safeguard). |
| **Claude Mythos 5** | `claude-mythos-5` | cùng đợt Fable 5 | Cùng spec/giá với Fable 5, nằm trong chương trình preview mời riêng "Claude Mythos Preview" (`claude-mythos-preview`) thuộc "Project Glasswing". |
| **Claude Opus 4.8** | `claude-opus-4-8` | 28/05/2026 | Cải thiện so với Opus 4.7 ở coding/agentic/reasoning/knowledge work. Giá $5/$25 mỗi triệu token in/out. Fast mode nhanh hơn 2.5×, rẻ hơn 3× so với model trước. Khuyến nghị chính thức: dùng cho coding agentic phức tạp + việc doanh nghiệp. |
| **Claude Sonnet 5** | `claude-sonnet-5` | 30/06/2026 | Sonnet "agentic nhất từ trước tới nay" — cải thiện rõ so với Sonnet 4.6 ở reasoning/tool use/coding. Hiệu năng gần bằng Opus 4.8 nhưng giá rẻ hơn nhiều: $2/$10 mỗi triệu token (giá giới thiệu tới 31/08/2026, sau đó $3/$15). Là model mặc định cho gói Free/Pro, có sẵn ở mọi gói + Claude Code + Claude Platform. **Đây là model đang chạy phiên hiện tại.** |
| **Claude Haiku 4.5** | `claude-haiku-4-5-20251001` | — | Model nhanh nhất, độ thông minh gần ngang các model đầu bảng (near-frontier). |

Khuyến nghị chọn model (theo docs chính thức): không chắc dùng gì → bắt đầu với **Opus 4.8** cho coding
agentic phức tạp/việc doanh nghiệp; cần năng lực cao nhất có thể → **Fable 5**.

## Nguồn chính thức đã đối chiếu (đáng tin — ưu tiên đọc lại nguồn này nếu cần chi tiết hơn)

- [Introducing Claude Sonnet 5](https://www.anthropic.com/news/claude-sonnet-5)
- [Introducing Claude Opus 4.8](https://www.anthropic.com/news/claude-opus-4-8)
- [Claude Fable 5 and Claude Mythos 5](https://www.anthropic.com/news/claude-fable-5-mythos-5)
- [Redeploying Claude Fable 5](https://www.anthropic.com/news/redeploying-fable-5)
- [Models overview — Claude Platform Docs](https://docs.anthropic.com/en/docs/about-claude/models/overview)
- [Anthropic Newsroom](https://www.anthropic.com/news) — kiểm tra trang này để thấy tin mới nhất, thay vì tin bất kỳ blog thứ 3 nào.

## Bài học rút ra khi tra cứu

- **Giới hạn `allowed_domains` về `anthropic.com`/`docs.anthropic.com`/`docs.claude.com` khi WebSearch**
  cho ra kết quả đáng tin hẳn so với tìm kiếm mở — tìm mở lần trước từng dính nhiều blog/SEO thứ 3
  (taskade.com, releasebot.io, scriptbyai.com...) tự tạo nội dung suy đoán về tin tức AI.
- **Đừng vội bác bỏ chi tiết "nghe có vẻ giật gân"**: lần tra trước, thông tin "Fable 5 bị đình chỉ do
  kiểm soát xuất khẩu" ban đầu bị đánh giá là "đáng ngờ, chưa xác nhận" — hoá ra là SỰ THẬT, đã xác nhận
  qua chính bài "Redeploying Claude Fable 5" của Anthropic. Bài học: không tin ngay nguồn không chính
  thức, nhưng cũng không tự động gạt bỏ chỉ vì nghe lạ — luôn tìm cách đối chiếu qua nguồn gốc trước khi
  kết luận đúng/sai.
- System prompt của phiên đang chạy vẫn là nguồn nhanh nhất cho câu hỏi "model nào đang có" (không cần
  tra cứu), nhưng để biết NGÀY ra mắt, GIÁ, hay CHI TIẾT tính năng thì phải tra thêm như trên.

## Claude Code CLI — phiên bản & tính năng mới nhất (đã xác nhận 2026-07-23)

- **Phiên bản CLI hiện tại: `2.1.218`** — xác nhận trực tiếp bằng cách chạy `claude --version` NGAY
  trong session này (không chỉ tin theo tài liệu online), khớp đúng với version mới nhất ghi trong
  `CHANGELOG.md` chính thức của repo `anthropics/claude-code`. Cách tra nhanh version mới nhất: fetch
  `https://raw.githubusercontent.com/anthropics/claude-code/main/CHANGELOG.md` (WebFetch từng bị chặn
  403 với vài trang `anthropic.com`, nhưng `raw.githubusercontent.com` fetch được bình thường — đáng
  thử trước khi kết luận WebFetch "luôn bị chặn" trong 1 sandbox).
- Session hiện tại chạy trên **Claude Code remote environment** (không phải máy local) — repo đã có
  sẵn git clone, dùng git trực tiếp để sửa/commit/push (xem `CLAUDE.md` mục "Cách sửa file").

**Tính năng lớn gần đây (từ thông báo chính thức "Enabling Claude Code to work more autonomously" +
`claude-code-auto-mode` engineering post):**

- **Auto mode** — chế độ tự động duyệt hành động qua model-classifier thay vì hỏi người dùng từng
  bước, nằm giữa "duyệt tay hoàn toàn" và "không rào chắn gì". 2 lớp phòng vệ: (1) lớp input — probe
  quét nội dung đọc được (file, web fetch, output shell/tool ngoài) để phát hiện prompt-injection
  trước khi đưa vào context; (2) lớp output — 1 transcript classifier (chạy trên Sonnet 4.6) đánh giá
  từng hành động trước khi thực thi, đóng vai trò thay người duyệt.
- **Checkpoint / `/rewind`** — tự động lưu trạng thái code trước mỗi thay đổi; bấm `Esc` 2 lần hoặc
  gõ `/rewind` để quay lại checkpoint trước đó, chọn khôi phục code/hội thoại/cả hai.
- **Subagent** — giao việc chuyên biệt cho agent con (vd 1 agent dựng backend API song song lúc agent
  chính làm frontend) để chạy song song.
- **Hooks** — tự động chạy hành động ở các mốc cụ thể (vd chạy test suite sau khi sửa code, lint
  trước khi commit).
- **Background tasks** — giữ tiến trình chạy dài (dev server...) hoạt động nền, không chặn tiến độ
  các việc khác.
- **Claude Cowork** — sản phẩm agentic thứ 3 của Anthropic (cùng `claude.ai` và Claude Code), cho
  phép Claude làm nhiều việc song song, tự chủ hơn (multitask autonomously).

**Vài dòng changelog gần nhất đáng chú ý** (từ `CHANGELOG.md`, mới nhất trước — số hiệu có thể lệch 1
vài bản so với lúc agent sau đọc file này, luôn tra lại nếu cần chính xác tuyệt đối):
- `2.1.218` — `/code-review` chạy như subagent nền; sửa lỗi hỏng đường dẫn Windows; cải thiện permission prompt/xử lý lỗi MCP.
- `2.1.216` — thêm cấu hình cô lập filesystem; sửa lỗi chậm bậc 2 (quadratic slowdown) ở session dài.
- `2.1.215` — `/verify` và `/code-review` không còn tự chạy ngầm định — phải gọi tay.
- `2.1.212` — `/fork` copy hội thoại sang background session; thêm tìm kiếm toàn session + giới hạn số subagent spawn.
- `2.1.208` — thêm chế độ screen reader; hỗ trợ chuột trong menu fullscreen.

Có Agent SDK, subagent (Explore, Plan, general-purpose...), MCP tools (GitHub, claude-code-remote) —
dùng khi phù hợp, không lạm dụng cho việc đơn giản 1 tool là đủ.

## Nguồn tra cứu Claude Code

- [CHANGELOG.md — anthropics/claude-code](https://github.com/anthropics/claude-code/blob/main/CHANGELOG.md) (nguồn chính xác nhất theo version, luôn tra lại ở đây nếu cần).
- [Enabling Claude Code to work more autonomously](https://www.anthropic.com/news/enabling-claude-code-to-work-more-autonomously)
- [How we built Claude Code auto mode](https://www.anthropic.com/engineering/claude-code-auto-mode)
- [Making Claude Code more secure and autonomous with sandboxing](https://www.anthropic.com/engineering/claude-code-sandboxing)
- [Best practices for Claude Code](https://www.anthropic.com/engineering/claude-code-best-practices)
