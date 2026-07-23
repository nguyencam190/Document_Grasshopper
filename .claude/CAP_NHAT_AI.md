# Cập nhật AI/Claude — để agent phiên sau không bị lạc hậu

File này lưu thông tin mới nhất mà 1 agent AI (Claude) từng biết được về chính dòng model Claude/
Anthropic và Claude Code — mục đích: agent ở phiên làm việc SAU không bị kẹt ở kiến thức huấn luyện
cũ (training cutoff có thể trễ hơn thực tế nhiều tháng), đọc file này trước là nắm ngay thông tin mới
nhất đã từng xác nhận, không cần tra lại từ đầu.

> **Quy tắc cập nhật**: bất cứ khi nào 1 agent phát hiện thông tin mới hơn những gì ghi ở đây (qua
> system prompt của chính phiên đó — nguồn đáng tin nhất vì do hạ tầng Anthropic bơm trực tiếp mỗi
> phiên, hoặc qua WebSearch khi user hỏi trực tiếp), **cập nhật ngay phần liên quan bên dưới + đổi
> "Cập nhật lần cuối"** — không chờ lịch cố định, không chờ user nhắc.

## Cập nhật lần cuối
2026-07-23 (phiên Claude Code, session `claude/grasshopper-component-research-fecpfg`)

## Model Claude hiện tại — nguồn tin cậy nhất là system prompt của chính phiên đang chạy

System prompt mỗi phiên Claude Code tự bơm thẳng danh sách model mới nhất — đây là nguồn **đáng tin
hơn** training data hay kết quả WebSearch, vì được cập nhật bởi hạ tầng Anthropic theo thời gian
thực, không phụ thuộc lúc model được huấn luyện. Tính đến lần cập nhật cuối ở trên, system prompt ghi:

- **Dòng model mới nhất**: Claude 5 family, Opus 4.8, Haiku 4.5.
- **Model ID cụ thể**:
  - Fable 5 → `claude-fable-5`
  - Opus 4.8 → `claude-opus-4-8`
  - Sonnet 5 → `claude-sonnet-5`
  - Haiku 4.5 → `claude-haiku-4-5-20251001`
- Model đang chạy phiên hiện tại (lúc ghi chú này): Sonnet 5 (`claude-sonnet-5`).
- Khi xây dựng ứng dụng AI, mặc định dùng model mới nhất/mạnh nhất trong danh sách trên.

## Đối chiếu qua WebSearch (2026-07-23) — CẨN THẬN, nhiều nguồn không đáng tin

Đã thử tra thêm qua WebSearch để xác nhận có model mới hơn không. Kết quả tìm được nhắc tới thêm vài
mốc (Opus 4.6 ~th2/2026, Sonnet 4.6 ~17/2/2026, Fable 5 ra mắt ~9/6/2026, Opus 4.8 ~28/5/2026, Sonnet
5 ~30/6/2026) — **các mốc/ngày này KHÔNG xác nhận được qua nguồn chính thức Anthropic**, chỉ tới từ
blog/SEO thứ 3 (taskade.com, releasebot.io, scriptbyai.com...) — loại trang thường tự tạo nội dung
suy đoán/sai lệch về tin tức AI để câu SEO. Một kết quả còn nêu chi tiết đáng ngờ ("Fable 5 bị đình chỉ
theo lệnh kiểm soát xuất khẩu của Mỹ") — **không tin theo, chưa có nguồn chính thức xác nhận**.

**Bài học cho agent tương lai**: khi cần biết thông tin cập nhật về model Claude, luôn ưu tiên system
prompt của chính phiên đang chạy trước (đáng tin nhất). Nếu cần tra thêm, ưu tiên nguồn chính thức
(`anthropic.com/news`, `docs.claude.com`) — không tin ngay bất kỳ blog/trang tổng hợp thứ 3 nào tự
xưng có "timeline"/"changelog" đầy đủ, vì thể loại nội dung này đặc biệt hay bị AI khác tự sinh ra
thông tin sai để lấp khoảng trống.

## Ghi chú Claude Code (CLI/harness dùng trong dự án này)

- Session hiện tại chạy trên **Claude Code remote environment** (không phải máy local) — repo đã có
  sẵn git clone, dùng git trực tiếp để sửa/commit/push (xem `CLAUDE.md` mục "Cách sửa file").
- Có Agent SDK, subagent (Explore, Plan, general-purpose...), MCP tools (GitHub, claude-code-remote)
  — dùng khi phù hợp, không lạm dụng cho việc đơn giản 1 tool là đủ.
