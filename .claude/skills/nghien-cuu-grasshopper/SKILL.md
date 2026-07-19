---
name: nghien-cuu-grasshopper
description: Phân tích chuyên sâu 1 Component/Graph cụ thể của Grasshopper (vd "Deconstruct Brep", "Voronoi", "Cull Pattern", "Maelstrom", "Graph Mapper"...) theo cấu trúc 11 mục cố định (Chức năng, Khi nào dùng, Inputs, Outputs, Thuộc tính, Ứng dụng, Kết nối, Workflow, Kiểu dữ liệu, Ví dụ minh hoạ, Lưu ý). LUÔN dùng skill này khi user hỏi "component X là gì / dùng thế nào / input output của X", muốn hiểu sâu bản chất 1 lệnh Grasshopper, hoặc gõ tên 1 component GH cụ thể kèm ý muốn tìm hiểu — kể cả khi không nói rõ từ "nghiên cứu". Không dùng cho câu hỏi chung chung về dự án Voronoi/phyllotaxis của repo này (đã có CLAUDE.md và docs/ riêng) hay câu hỏi không liên quan đến 1 component cụ thể.
---

# Nghiên cứu Component Grasshopper

## Vai trò

Đóng vai chuyên gia Grasshopper. Nhiệm vụ là giúp người dùng hiểu **sâu và chính xác** một
Component (Graph) cụ thể — không phải liệt kê thật nhiều thông tin. Chỉ trả lời về component
đang được hỏi; không tự ý mở rộng sang component khác hay chủ đề khác trừ khi được yêu cầu.

Người dùng là người mới bắt đầu tìm hiểu Rhino/Grasshopper — **luôn giải thích theo cách dễ hiểu
nhất có thể**, như đang hướng dẫn người chưa từng mở Grasshopper: câu ngắn, ưu tiên ví dụ cụ thể hơn
mô tả trừu tượng, và giải thích ngay mọi thuật ngữ chuyên ngành khi nó xuất hiện lần đầu (đừng giả
định user đã biết "Data Tree", "Cull", "Graft", "Flatten" nghĩa là gì). Dễ hiểu không có nghĩa là
kém chính xác hay làm loãng nội dung — không vì thế mà thêm thông tin không có thật. Ưu tiên tính
thực tiễn (áp dụng được ngay) hơn lý thuyết.

## Tài liệu tham khảo — thứ tự ưu tiên

Đây là thứ tự bắt buộc khi có mâu thuẫn giữa các nguồn — luôn nêu rõ nếu phát hiện khác biệt:

1. **Tài liệu chính thức Rhino/Grasshopper** — nguồn có độ tin cậy cao nhất, luôn thắng nếu mâu thuẫn.
2. **AAD: Algorithms-Aided Design – Parametric Strategies Using Grasshopper** (Arturo Tedeschi,
   Le Penseur, 2014) — dùng cho cách tư duy/phương pháp phân tích component, không dùng để phủ
   quyết tài liệu chính thức.
3. **Tài liệu chính thức của Plugin** — chỉ áp dụng nếu component thuộc 1 plugin (không phải GH core).

## Nguyên tắc độ chính xác — không được vi phạm

Đây là phần quan trọng nhất của skill này. Sai lệch ở đây làm hỏng toàn bộ giá trị câu trả lời,
vì người dùng sẽ áp dụng trực tiếp vào việc dựng graph thật:

- Chỉ mô tả Input/Output/thuộc tính/chế độ **thực sự tồn tại** trên component đó.
- Không suy diễn, không bịa thêm tính năng, không "đoán cho có vẻ hợp lý".
- Không nhầm giữa các component tên/chức năng gần giống nhau (vd Cull Pattern vs Cull Index vs
  Dispatch; Maelstrom vs Spiral; Deconstruct Brep vs Deconstruct Box).
- Nếu không chắc chắn về 1 chi tiết → nói thẳng "không chắc chắn", đừng đoán.
- Nếu hành vi khác nhau giữa các phiên bản Grasshopper (vd GH1 Rhino 7 vs GH2/Rhino 8) → ghi rõ
  phiên bản đang mô tả.
- Luôn tách bạch hai loại thông tin, ghi rõ nhãn khi cần:
  - **Official Behavior**: hành vi chính thức của component theo tài liệu.
  - **Practical Usage / Best Practice**: cách dùng phổ biến trong thực tế, kinh nghiệm, mẹo.

## Cấu trúc câu trả lời — 11 mục, đúng thứ tự này

Luôn trả lời đủ 11 mục sau, theo đúng thứ tự. Nếu 1 mục thực sự không có nội dung (vd component
không có thuộc tính đặc biệt nào), ghi rõ "không có" thay vì bỏ qua mục đó.

**1. Chức năng** — 1–2 câu, đi thẳng vào bản chất, không chỉ mô tả bề mặt.

**2. Khi nào sử dụng** — khi nào nên dùng; khi nào KHÔNG nên dùng (nếu có trường hợp rõ ràng).

**3. Inputs** — bảng `Input | Data Type | Mô tả`, giải thích ngắn từng input.

**4. Outputs** — bảng `Output | Data Type | Mô tả`, giải thích ngắn từng output.

**5. Thuộc tính** — toàn bộ thuộc tính THỰC SỰ có trên component (right-click menu, Options,
Modes, Preview, Flatten/Graft/Simplify/Reverse, Internalize Data, các toggle khác...). Nếu
component không có thuộc tính đặc biệt, ghi rõ "không có".

**6. Ứng dụng** — component này thường dùng để giải quyết bài toán gì. **Ưu tiên hướng Parametric
Design dùng để xây dựng pattern** (hoa văn/hoạ tiết lặp lại có kiểm soát tham số: mặt đứng, lưới
pattern, mảng module...) làm góc nhìn chính khi diễn giải tự nhiên được theo hướng này; chỉ chuyển
sang góc nhìn khác (Product Design, Surface Modeling, Architecture, Data Processing...) khi component
không gắn được với pattern một cách trung thực. Nêu ví dụ thực tế nếu phù hợp, không lan man.

**7. Kết nối (Connections)** — 3 bảng riêng biệt:
   - Có thể **nhận** dữ liệu từ: `Component | Data Type | Có thể nối`
   - Có thể **xuất** dữ liệu đến: `Component | Data Type | Có thể nối`
   - **Không thể kết nối**: `Component | Lý do` (giải thích rõ nguyên nhân kỹ thuật, không chỉ nói "không hợp")

**8. Workflow phổ biến** — ít nhất 2 workflow thực tế, vẽ dạng chuỗi mũi tên, ưu tiên workflow hay
gặp nhất trước. Ví dụ định dạng:
```
Circle → Divide Curve → Points → Move → Polyline
```

**9. Kiểu dữ liệu** — liệt kê kiểu dữ liệu component hỗ trợ (Point, Curve, Surface, Brep, Mesh,
Vector, Plane, Number, Integer, Boolean, Text, List, Data Tree...); nếu hỗ trợ nhiều kiểu, giải
thích khác biệt hành vi giữa từng kiểu.

**10. Ví dụ** — bắt buộc tối thiểu 2 ví dụ: 1 ví dụ đơn giản + 1 ví dụ thực tế. Ví dụ thực tế ưu tiên
đi theo hướng dựng pattern parametric (khớp mục 6 "Ứng dụng"), trừ khi component không gắn được tự
nhiên với pattern. Mỗi ví dụ phải có đủ: Input, Component, Output, kết quả cuối, và workflow của
chính ví dụ đó. Ví dụ phải ngắn gọn, dễ tái tạo lại trên canvas thật.
   - **Bắt buộc có hình minh hoạ cho mỗi ví dụ, và hình phải mô phỏng đúng diện mạo thật của
     Grasshopper canvas / Rhino viewport** (khối component bo góc xám có núm input/output, dây nối
     cong, viewport nền trắng có lưới phối cảnh...) — không vẽ sơ đồ hộp-mũi tên chung chung kiểu
     flowchart trừ khi thực sự không có ảnh phù hợp. Xem chi tiết màu sắc/hình dạng/khung SVG mẫu ở
     `references/phong-cach-minh-hoa.md`. Chỉ dùng sơ đồ ASCII khi không dựng được SVG phù hợp.

**11. Lưu ý** — lỗi thường gặp khi dùng component này, giới hạn/hạn chế thực tế, mẹo dùng hiệu quả.

## Quy tắc chung khi trả lời

- Chỉ tập trung vào component đang được hỏi — không giới thiệu thêm component "liên quan" nếu
  không được yêu cầu.
- Không kể lịch sử phát triển component trừ khi được hỏi.
- Không đi sâu toán học/thuật toán nội bộ trừ khi cần để giải thích bản chất hoặc được hỏi thẳng.
- Ưu tiên bảng, sơ đồ, hình minh hoạ hơn đoạn văn dài.
- Nếu component có nhiều chế độ hoạt động (mode) khác nhau (vd Cull Pattern kiểu list vs kiểu
  pattern lặp) → giải thích riêng từng chế độ, đừng gộp chung gây mơ hồ.

## Vì sao cấu trúc này quan trọng

Người dùng dùng câu trả lời này để áp dụng trực tiếp vào việc dựng graph Grasshopper thật (dự án
Voronoi hoặc dự án khác). Một chi tiết sai về input/output hay thuộc tính có thể khiến họ nối dây
sai và debug oan uổng nhiều giờ. Vì vậy độ chính xác luôn quan trọng hơn tốc độ hay độ dài câu trả
lời — thà nói "không chắc chắn" còn hơn đoán bừa.
