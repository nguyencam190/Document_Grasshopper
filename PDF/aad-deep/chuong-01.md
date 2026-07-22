# Chương 1 — Algorithmic Modeling with Grasshopper (Mô hình hoá thuật toán với Grasshopper)

Chương mở đầu giới thiệu Grasshopper là gì và cách vận hành cơ bản nhất của nó: giao diện, cách đặt component lên canvas, cách dữ liệu chảy qua các component, và các thao tác nền tảng (lưu file, bake ra Rhino, hiển thị, snap điểm, di chuyển bằng vector). Đây là nền tảng bắt buộc trước khi học các chương sâu hơn.

## 1.1 Prerequisites and installation (Điều kiện & cài đặt)

Grasshopper không phải phần mềm độc lập mà là plug-in chạy bên trong Rhinoceros — tức phải có Rhino cài sẵn (bản 5.0 trở lên) mới dùng được. Sách nói rõ: thời điểm viết sách, Grasshopper chỉ chạy trên Windows, chưa hỗ trợ Mac. Cài đặt miễn phí, không giới hạn thời hạn, tải từ trang grasshopper3d.com. Sau khi cài, gõ lệnh `grasshopper` trong command line của Rhino để mở cửa sổ Grasshopper. Sách cũng ghi chú lịch sử: Grasshopper do David Rutten phát triển tại Robert McNeel & Associates, ra đời năm 2007 cho Rhino 4.0 với tên gốc "Explicit History", đổi tên thành Grasshopper năm 2008.

## 1.2 Grasshopper user interface (Giao diện người dùng)

Cửa sổ Grasshopper luôn chạy song song với cửa sổ Rhino: người dùng xây "thuật toán trực quan" (visual algorithm) trong Grasshopper bằng cách nối các **component** (node) lại với nhau, kết quả hình học hiển thị trực tiếp trong viewport Rhino.

Giao diện chia làm 4 phần: (1) **Menu bar** — thanh menu kiểu Windows chuẩn, có nút chuyển đổi giữa nhiều file đang mở cùng lúc; (2) **Component tabs** — các tab chứa icon component, kéo icon từ đây thả vào canvas (component không hoạt động như nút bấm, phải kéo ra); (3) **Canvas toolbar** — thanh công cụ tuỳ chỉnh hiển thị; (4) **Working area (canvas)** — vùng làm việc chính để dựng thuật toán.

### 1.2.1 Component tabs
Component được nhóm theo **Tab** (Params, Maths, Sets, Vector, Curve, Surface, Mesh, Intersect, Transform, Display...), mỗi tab lại chia nhỏ thành các **panel**. Sách dùng quy ước ghi chú `Tên component (Tab > Panel)`, ví dụ `Line (Curve > Primitive)`. Mỗi panel mặc định chỉ hiện một số component phổ biến; để xem toàn bộ, bấm vào dải đen của panel (dropdown) hoặc bật chế độ `View > Obscure Components` để hiện tất cả component kể cả loại ít dùng.

### 1.2.2 Working area — Canvas
Có 2 cách đưa component lên canvas: kéo-thả icon từ tab, hoặc double-click vùng trống để mở **canvas search box**, gõ tên component (Grasshopper tự gợi ý danh sách khớp). Cách gõ tìm kiếm nhanh hơn nhiều khi đã quen tên lệnh.

## 1.3 Components and data (Component và dữ liệu)

Sách phân loại 3 loại component:
1. **Standard components** — component xử lý dữ liệu: nhận input, xử lý, trả output (đa số component thuộc loại này, vd Point cần {x,y,z} để tạo điểm, Loft cần tập curve để tạo surface).
2. **Input-components** — cung cấp dữ liệu do người dùng chỉnh (nằm trong panel Input của tab Params), không cần input nào để hoạt động (vd Number Slider).
3. **Container components** — component "chứa" dữ liệu (không xử lý gì), nằm ở panel Geometry/Primitive của tab Params, nhận diện bằng icon hình lục giác đen.

Một standard component gồm 3 phần: **input** (bên trái), **name** (giữa, có thể đổi tên qua right-click, hoặc hiện icon thay tên nếu bật `Display > Draw Icons`), **output** (bên phải). Ví dụ minh hoạ xuyên suốt: component **Construct Point** (Vector > Point) — khi thả lên canvas mặc định sinh điểm tại gốc toạ độ (0,0,0) vì có sẵn giá trị mặc định.

Có 3 cách nạp dữ liệu vào input:
- **1.3.1 Local setting** — right-click vào input slot, chọn "Set Number", gõ giá trị, bấm "Commit Changes".
- **1.3.2 Wired connection** — nối dây từ output của component này sang input của component khác. Ví dụ điển hình: dùng **Number Slider** (Params > Input) kéo dây vào input X/Y/Z của Construct Point; slider tự đổi tên theo tên input nó nối vào (vd "X coordinate"). Kéo grip của slider sẽ cập nhật vị trí điểm theo thời gian thực. Thuộc tính slider (double-click vào tên, không phải grip) cho chỉnh Numeric Domain (min/max) và kiểu làm tròn: R (số thực), N (số nguyên), E (số chẵn), O (số lẻ), cùng số chữ số thập phân (Digits) nếu chọn R. Sách còn dạy mẹo gõ nhanh trong canvas search box: gõ `5` ra slider domain 0–10 giá trị 5; gõ `0<5<50` ra slider domain 0–50 giá trị 5; gõ `0.5` ra slider kiểu R domain 0–1; gõ `0-5` sẽ tạo ra component **Subtraction** (vì dấu `-` được hiểu là phép trừ) chứ không phải slider âm.
- **1.3.4 Setting from Rhino** — right-click input, chọn "Set one Point" (hoặc tương đương), rồi click chọn trực tiếp đối tượng có sẵn trong Rhino; Grasshopper sẽ thu nhỏ cửa sổ để cho chọn. Cách này tạo liên kết sống với hình học Rhino gốc.

### 1.3.3 Warnings and errors (Cảnh báo và lỗi)
Grasshopper dùng màu nền component báo trạng thái: **xám** = đúng/ổn; **cam (warning)** = thường do thiếu dữ liệu đầu vào (vd Line component mới thả ra chưa nối A, B); **đỏ (error)** = sai kiểu dữ liệu ép buộc (vd nối số vào input yêu cầu điểm). Component lỗi đỏ sẽ không sinh kết quả và làm "ngưng" luôn các component phía sau nối với nó. Có thể xem chi tiết lỗi bằng cách hover chuột vào "balloon" cảnh báo phía trên component (bật qua `Display > Canvas Widgets > Message Balloons`).

Container component (Point, Curve, Geometry...) chỉ chấp nhận đúng loại hình học tương ứng — Point component không lấy được Curve. Component **Geometry** (Params > Geometry) là loại linh hoạt nhất, nhận mọi kiểu hình học. Khi đã "Set" dữ liệu từ Rhino, liên kết vẫn sống (xoá hình trong Rhino thì component chuyển cam); muốn "chốt cứng" dữ liệu (ngắt liên kết với Rhino) dùng "Internalise data" trong context menu.

## 1.4 Save and bake (Lưu và Bake)

**1.4.1** File Grasshopper lưu dưới 2 định dạng: `.gh` (nhị phân, không đọc/sửa bằng text editor được) và `.ghx` (XML, đọc/sửa được bằng text editor nhưng dung lượng lớn hơn). File `.gh`/`.ghx` không tự chạy được — phải mở Rhino, load Grasshopper rồi mở file.

**1.4.2** Kết quả preview trong Rhino (màu đỏ mặc định) chỉ là hình ảnh xem trước — không chọn được, không lưu/render như đối tượng Rhino thật, và biến mất nếu đóng file Grasshopper. Muốn biến nó thành đối tượng Rhino thật sự, phải **Bake**: right-click component → Bake..., mở cửa sổ Bake Attributes cho chọn layer, màu, chế độ nhóm (Group). Sau khi bake, vẫn có thể tiếp tục chỉnh input trong Grasshopper để sinh phiên bản khác (không ảnh hưởng bản đã bake).

## 1.5 Display and control (Hiển thị và điều khiển)

**1.5.1** Màu và chất lượng hiển thị preview chỉnh qua Canvas Toolbar: "Document Preview Settings" đổi màu, "Preview Mesh Quality" đổi độ mịn mesh hiển thị (Low/High/Custom). Có thể tắt preview riêng từng component (right-click → Preview) mà không ảnh hưởng chức năng, chỉ ẩn hình — hữu ích khi thuật toán phức tạp, không cần nhìn mọi bước trung gian.

**1.5.2** Khác với Preview, **Enable/Disable** thực sự tắt hoạt động của component (không tính toán nữa), kéo theo mọi component phía sau phụ thuộc vào nó cũng ngưng. Sách giới thiệu **Radial Menu** (bấm phím cách) tập hợp nhiều thao tác nhanh: group, cluster, ẩn/hiện preview, enable/disable, bake, zoom, tắt solver, recompute, tìm kiếm.

**1.5.3** Chế độ **Draw Fancy Wires** (`Display > Draw Fancy Wires`) làm dây nối đổi hình theo kiểu dữ liệu truyền qua: dây **cam** = không có dữ liệu; dây **đen mảnh** = 1 giá trị đơn; dây **đen dày** = 2 hoặc nhiều giá trị (list). Dây đứt nét (loại thứ 4) dành cho Data Tree, sẽ nói ở chương 5. Có thể đặt dây "ẩn" (Wire Display > Hidden) — dây chỉ hiện khi chọn 1 trong 2 component nối nó.

## 1.6 Grasshopper flow (Luồng chảy dữ liệu)

Nguyên tắc quan trọng: dây chỉ được nối từ output của component đứng trước (A) sang input của component đứng sau (B) — dữ liệu luôn "chảy" từ trái sang phải, **không thể tạo vòng lặp (loop)** trong Grasshopper thông thường (trừ vài component đặc biệt nói ở chương 7). Luồng Grasshopper giống một "lịch sử dựng hình" (construction history): mọi bước trung gian đều được lưu lại dưới dạng preview. Muốn chỉ thấy kết quả cuối, phải tắt preview mọi component trừ component cuối cùng — nếu không các bước sẽ chồng hình lên nhau trong Rhino.

## 1.7 Basic concepts and operations (Khái niệm & thao tác cơ bản)

Mục này giới thiệu trước một loạt component nền tảng sẽ dùng xuyên suốt sách:

- **1.7.1 Object snap trong Grasshopper**: Grasshopper không có Osnap kiểu CAD truyền thống, thay vào đó dùng logic thuật toán. Component **Point on Curve** (Curve > Analysis) định vị điểm trên đường cong bằng cách "chuẩn hoá" độ dài curve về thang 0–1 (0 = điểm đầu, 1 = điểm cuối, 0.5 = mặc định là điểm giữa); right-click chọn nhanh các mốc (start, quarter, third, mid, two thirds, three quarters, end). Component **End Points** (Curve > Analysis) trả về điểm đầu (S) và điểm cuối (E) của 1 curve. Component **Area** (Surface > Analysis) trả về trọng tâm (centroid) và diện tích (A) của 1 curve phẳng khép kín. Component **Volume** (Surface > Analysis) trả về thể tích (V) và trọng tâm (C) của khối kín 3D; kết quả số có thể hiển thị qua component **Panel** (Params > Input).
- **1.7.2 Merging data**: Component **Merge** (Sets > Tree) gộp 2 hay nhiều luồng dữ liệu thành 1 list duy nhất — ví dụ dùng 1 component Line duy nhất thay vì nối riêng 2 input A/B, bằng cách gộp điểm đầu và điểm cuối qua Merge trước. Khi input D2 được nối dây, Merge tự sinh thêm input D3 (và tiếp tục); thứ tự index D-input quyết định thứ tự dữ liệu trong list kết quả. Có thể thêm input thủ công bằng nút "+" của Zoomable User Interface khi zoom vào component.
- **1.7.3 Dividing a Curve**: Component **Divide Curve** (Curve > Division) chia đều 1 curve theo chiều dài cung: input Curve (C) + số đoạn chia (N) → sinh N+1 điểm nếu curve hở, N điểm nếu curve khép kín, tất cả gom trong 1 list. Có thể xem thứ tự/chỉ số từng điểm bằng component **Point List** (Display > Vector), một component hiển thị thuần tuý (không có output), có input S chỉnh cỡ chữ.
- **1.7.4 Moving an object / vectors**: Vector là thực thể hình học có hướng, chiều và độ dài (magnitude). Component **Move** (Transform > Euclidian) di chuyển hình học theo 1 vector chỉ định. Vector có thể dựng bằng **Vector XYZ** (Vector > Vector, nhập 3 thành phần) hoặc các vector đơn vị dựng sẵn **Unit X / Unit Y / Unit Z** (mặc định độ dài = 1, có thể nhân với 1 số qua input F để khuếch đại độ dài — tức khuếch đại quãng di chuyển).
- **1.7.5 Custom preview**: Có thể đổi màu/độ trong suốt của preview riêng từng component thay vì dùng màu đỏ mặc định toàn cục, bằng component **Custom Preview** (Display > Preview) kết hợp với **Colour Swatch** (Params > Input) — click vào node Colour Swatch mở bảng chọn màu và độ trong suốt.

Ngoài ra, mục 1.7.4 còn nhắc lại nguyên tắc "construction history": khi dùng Move, Grasshopper vẫn hiện cả hình gốc lẫn hình đã di chuyển trừ khi tắt preview của component Geometry gốc — minh hoạ lại đúng nguyên tắc đã nêu ở mục 1.6.
