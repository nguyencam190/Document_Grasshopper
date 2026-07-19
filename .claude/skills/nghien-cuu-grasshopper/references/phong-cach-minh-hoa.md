# Phong cách vẽ hình minh hoạ giống Grasshopper/Rhino thật

Vì không có ảnh chụp màn hình component thật, mọi hình minh hoạ (mục 10 "Ví dụ" của skill) phải là
SVG tự vẽ nhưng **mô phỏng đúng diện mạo thật** của canvas Grasshopper và viewport Rhino — không vẽ
sơ đồ hộp/mũi tên chung chung kiểu flowchart. Mục tiêu: user nhìn vào là nhận ra ngay "đây đúng là
Grasshopper" / "đây đúng là Rhino", để khi mở phần mềm thật, họ khớp được ngay hình đã học với UI thật.

## 1. Canvas Grasshopper (dây nối component)

**Nền canvas**: màu xám rất nhạt gần trắng (`#F5F5F0` – `#FAFAF7`), có lưới chấm nhỏ mờ
(`#E0E0DA`, cách nhau ~15–20px) — không dùng nền trắng tinh hay nền tối.

**Component (khối lệnh)**:
- Hình hộp bo góc nhẹ (radius ~4–6px), nền gradient xám nhạt (`#F0F0F0` → `#D8D8D8`), viền `#8C8C8C`
  dày ~1px.
- Tên lệnh viết in hoa hoặc đúng chữ hoa/thường như GH thật, font sans-serif, đặt giữa khối, cỡ chữ
  vừa đủ đọc.
- **Input**: các núm nhỏ hình chữ nhật bo tròn (grip) nhô ra bên **trái** khối, xếp dọc nếu nhiều input.
- **Output**: núm tương tự nhô ra bên **phải** khối.
- Mỗi núm có 1 chấm tròn nhỏ (nub) ở đầu ngoài cùng — đây là điểm dây nối bám vào.
- Component đang chọn: viền đổi màu cam/đỏ nổi bật (`#FF6600` hoặc tương tự) — chỉ dùng khi minh hoạ
  thao tác "đang chọn/đang kéo".

**Dây nối (wire)**: đường cong Bezier mượt (không phải đường thẳng gấp khúc) màu xám đậm (`#4A4A4A`
hoặc đen nhạt), nối từ chấm output của component nguồn sang chấm input của component đích, độ cong
tự nhiên theo chiều ngang.

**Slider (Number Slider)**: thanh ngang bo góc, có nhãn tên bên trái, khung số hiển thị giá trị hiện
tại bên phải, một núm kéo (nhỏ, màu xám/xanh) nằm trên rãnh trượt.

**Panel**: hộp chữ nhật nền trắng, viền xám mảnh, chữ đen căn trái, dùng để hiển thị output dạng text/số.

**Toggle/Boolean**: nút bo tròn nhỏ ghi "True"/"False", nền xanh lá nhạt khi True, xám khi False.

## 2. Viewport Rhino (kết quả hình học)

- Nền **trắng**, có lưới phối cảnh (perspective grid) màu xám nhạt (`#D0D0D0`), các đường lưới thưa
  dần khi ra xa (hiệu ứng phối cảnh, không phải lưới đều isometric).
- **Trục toạ độ**: trục X màu đỏ, trục Y màu xanh lá — vẽ 2 đoạn ngắn giao nhau tại gốc toạ độ nếu
  cảnh có hiển thị gốc.
- **Nhãn viewport**: chữ nhỏ góc trên-trái, ví dụ `Perspective`, `Top`, `Right` — dùng font mono nhỏ,
  màu xám đậm.
- **Hình học kết quả**: nếu là đường/curve → nét đen mảnh; nếu là mặt/brep ở chế độ Shaded → tô màu
  xám be nhạt (`#C2C2B8` kiểu vật liệu mặc định Rhino) kèm viền wireframe đen mảnh các cạnh chính.
- Điểm (point) hiển thị dạng chấm tròn đỏ nhỏ hoặc dấu `+`.

## 3. Khung SVG mẫu tái sử dụng

Dưới đây là khối SVG mẫu cho 1 component GH — copy và chỉnh tên/số input-output khi vẽ minh hoạ mới:

```svg
<!-- 1 component GH mẫu, kích thước ~140x60 -->
<g>
  <rect x="0" y="0" width="140" height="60" rx="6" fill="url(#ghBody)" stroke="#8C8C8C" stroke-width="1"/>
  <text x="70" y="34" text-anchor="middle" font-family="Segoe UI, sans-serif" font-size="13" fill="#222">Tên Component</text>
  <!-- input nub bên trái -->
  <rect x="-8" y="22" width="10" height="16" rx="3" fill="#E8E8E8" stroke="#8C8C8C"/>
  <circle cx="-3" cy="30" r="2.5" fill="#4A4A4A"/>
  <!-- output nub bên phải -->
  <rect x="138" y="22" width="10" height="16" rx="3" fill="#E8E8E8" stroke="#8C8C8C"/>
  <circle cx="143" cy="30" r="2.5" fill="#4A4A4A"/>
</g>
<defs>
  <linearGradient id="ghBody" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0%" stop-color="#F0F0F0"/>
    <stop offset="100%" stop-color="#D8D8D8"/>
  </linearGradient>
</defs>
```

Dây nối giữa 2 component (dùng path bezier, không dùng line thẳng):

```svg
<path d="M 143,30 C 180,30 180,30 210,30" stroke="#4A4A4A" stroke-width="1.5" fill="none"/>
```

Khung viewport Rhino mẫu (nền trắng + lưới phối cảnh + nhãn góc):

```svg
<g>
  <rect x="0" y="0" width="240" height="160" fill="#FFFFFF" stroke="#B0B0B0"/>
  <!-- lưới phối cảnh đơn giản: các đường ngang thưa dần -->
  <g stroke="#D8D8D8" stroke-width="1">
    <line x1="0" y1="140" x2="240" y2="140"/>
    <line x1="0" y1="120" x2="240" y2="120"/>
    <line x1="0" y1="105" x2="240" y2="105"/>
    <line x1="0" y1="94" x2="240" y2="94"/>
  </g>
  <text x="6" y="14" font-family="Consolas, monospace" font-size="10" fill="#555">Perspective</text>
</g>
```

## 4. Lỗi thường gặp — PHẢI tự kiểm tra trước khi publish

Đã tự mắc lỗi này nhiều lần khi vẽ tay toạ độ SVG cho component có nhiều input (Fit Loft, Extrude):
**núm input (nub) bị đặt ở toạ độ y NẰM NGOÀI phạm vi y của khung component**, khiến núm "nổi" lơ lửng
phía trên/dưới khung thay vì gắn đúng cạnh trái/phải khung, và dây nối (wire) trông như không chạm
vào graph. Lỗi cụ thể đã gặp: khung Fit Loft có `y="110" height="130"` (phạm vi y: 110–240) nhưng núm
"C" lại vẽ ở `y="86"` — nằm hẳn phía TRÊN khung, cách xa 8–24px, dây nối tới đó nhìn tách rời hoàn toàn
khỏi component.

**Quy tắc bắt buộc khi vẽ 1 component có N input nubs**:
1. Xác định trước `y` và `height` của khung `<rect>` component. Mọi núm input/output PHẢI có toạ độ y
   (tâm núm) nằm trong khoảng `[box.y + margin, box.y + box.height − margin]` (margin ~10–15px), không
   được vượt ra ngoài khung ở cả 2 phía.
2. Nếu component có nhiều input (như Fit Loft có C/Nu/Du/Dv), chia đều khoảng trống bên dưới phần tiêu
   đề (thường chừa ~30–40px đầu khung cho tên component) cho từng núm — không nhồi núm đầu tiên lên
   sát mép trên khung hoặc để tràn lên phía ngoài.
3. Toạ độ điểm cuối của dây nối (`path d="M ... C ... targetX,targetY"`) PHẢI trùng khớp CHÍNH XÁC với
   toạ độ tâm `<circle>` của núm đích (không áng chừng bằng mắt) — copy đúng số `cx,cy` của núm vào
   điểm cuối path, không tự bịa số gần đúng.
4. Sau khi vẽ xong, **luôn render thử bằng trình duyệt (Playwright hoặc mở file trực tiếp) và phóng to
   kiểm tra bằng mắt từng điểm nối** trước khi publish — đặc biệt các component có ≥3 input, vì càng
   nhiều núm càng dễ tính sai toạ độ. Đừng chỉ tin vào việc "số liệu nhìn hợp lý" khi đọc code SVG.

## 5. Khi nào không cần theo style này

Nếu minh hoạ là sơ đồ khái niệm thuần tuý (vd giải thích thuật toán, không phải "đây là canvas GH
thật" hay "đây là kết quả trong Rhino") thì vẫn có thể dùng sơ đồ đơn giản hơn — nhưng ưu tiên mặc
định luôn là mô phỏng UI thật khi minh hoạ ví dụ Input/Component/Output ở mục 10.
