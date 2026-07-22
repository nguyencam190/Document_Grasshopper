# Chương 4 — Transformations (Phép biến đổi hình học)

Chương này dạy các phép biến đổi hình học: Euclidean (giữ nguyên hình dạng/kích thước), Affine (không giữ kích thước), và các phép biến đổi phức tạp hơn (Orient, Box Morph, Paneling). Sách mở đầu bằng bảng phân loại lý thuyết:

| Loại biến đổi | Giữ nguyên | Không giữ nguyên |
|---|---|---|
| Euclidean | hình dạng, kích thước | vị trí |
| Affine | tính song song | hình dạng, kích thước, vị trí |
| Similarity | hình dạng | kích thước, vị trí |
| Morph | quan hệ tô-pô | tính chất hình học |

Sách minh hoạ 5 trạng thái: (1) hình gốc, (2) Euclidean (xoay), (3) Affine (scale — vẫn giữ song song), (4) Similarity (scale+xoay), (5) Morph. Về toán học, 1 phép biến đổi đo sự thay đổi giữa điểm gốc P(x,y) và điểm mới P'(x',y'); riêng phép tịnh tiến (translate) chỉ đơn giản là cộng/trừ độ lệch dx, dy vào toạ độ gốc: x'=x+dx, y'=y+dy — cả đối tượng được tịnh tiến bằng cách áp công thức này lên toàn bộ (hoặc chỉ) các điểm điều khiển/đỉnh của nó. Về bản chất, tịnh tiến 1 điểm tương đương di chuyển nó theo 1 khoảng cách + hướng + chiều xác định — đúng 3 đặc trưng của **vector**.

## 4.1 Vectors (Vector)

Panel Vector của tab Vector chứa các component dựng/chỉnh vector:
- **Vector 2Pt**: tạo vector từ 2 điểm A (đầu) và B (cuối) mô tả sẵn. Output L = độ lớn (magnitude) của vector, output V = chính vector đó. Dùng **Vector Display** để xem trực quan vector trong Rhino.
- **Unit Vector**: chuẩn hoá 1 vector về độ dài = 1 mà không đổi hướng (có thể làm luôn trong Vector 2Pt bằng cách nối Boolean Toggle=True vào input U).
- **Amplitude**: đặt độ dài mới (A) cho 1 vector cho trước, giữ nguyên hướng/chiều — nếu A âm sẽ đảo chiều vector.
- **Scalar multiplication (nhân vô hướng)**: nhân 1 vector với 1 số N — nếu N>0 giữ chiều, N<0 đảo chiều; độ dài mới = độ dài gốc × N.
- **Unit X, Unit Y, Unit Z**: vector đơn vị theo trục X/Y/Z; input F cho phép đặt độ dài (dùng cơ chế nhân vô hướng có sẵn).

## 4.2 Euclidean transformations

Nhóm phép biến đổi Euclid gồm: tịnh tiến (Move), xoay (Rotate/Rotate Axis), Orient, và Mirror (đối xứng).

### 4.2.1 Translations — Move
**Move** (Transform > Euclidean) tịnh tiến 1 hình học (G) theo vector (T). Ví dụ minh hoạ mở rộng: dùng **Center Box** (Surface > Primitive) tạo 1 khối hộp, dịch theo trục z. Nếu input F của Unit Z được nối với nhiều giá trị (thay vì 1 số), sẽ sinh nhiều vector, cho phép dịch chuyển hàng loạt cùng lúc — ví dụ mô phỏng 1 toà nhà nhiều tầng bằng cách nối **Series** vào input F của Unit Z: N = khoảng cách giữa các tầng, C = tổng số tầng, S = giá trị bắt đầu (S=0 để tầng đầu trùng khối gốc).

### 4.2.2 Rotations — Rotate và Rotate Axis
Xoay là chuyển động của 1 vật rắn quanh: (a) 1 **điểm cố định** (tâm xoay), hoặc (b) 1 **đường thẳng** (trục xoay). Component **Rotate** (Transform > Euclidean) xoay theo 1 mặt phẳng; **Rotate Axis** xoay theo 1 trục thẳng. Ví dụ minh hoạ Rotate: xoay 1 lăng trụ 45° so với vị trí gốc trên 1 surface có hướng bất kỳ — quy trình: dùng Geometry container nhập lăng trụ, tách các mặt bằng **Deconstruct Brep**, lấy mặt đáy bằng List Item (index 6), tính vector pháp tuyến tại tâm mặt đáy bằng Evaluate Surface, dựng mặt phẳng xoay bằng **Plane Normal** (Vector > Plane), nối vào Rotate cùng góc xoay (Number Slider 0–360°) — vì Rotate nhận góc theo **radian**, phải đổi độ sang radian bằng component **Radians** (Maths > Trig).

Cách khác: dùng **Rotate Axis**, cần 1 đường thẳng (input X) làm trục — dựng bằng **Line SDL**. Kết hợp Rotate Axis với Series cho phép tạo **xoay tăng dần** (progressive rotation) — ví dụ mở rộng mô hình toà nhà nhiều tầng ở mục 4.2.1: đặt trục xoay là 1 đường thẳng đứng đi qua trọng tâm khối gốc (tính bằng component Volume), rồi thay vì 1 góc xoay cố định, dùng dãy góc xoay từ Series (input C của Series phải bằng đúng số tầng). Để tính góc xoay tăng dần giữa 2 tầng liên tiếp (relative angle) từ 1 góc xoắn tổng (twist angle — góc giữa tầng đầu và tầng cuối), công thức: **relative angle = twist angle / (số tầng − 1)**. Sách minh hoạ trực quan các cấu hình toà nhà xoắn khác nhau ứng với twist angle 90° và các bước xoay tăng dần khác nhau.

### 4.2.3 Orient component
**Orient** (Transform > Euclidean) gộp cả tịnh tiến lẫn xoay vào 1 phép biến đổi duy nhất: đưa 1 hình học (G) từ vị trí/hướng bất kỳ trong không gian, "gắn" (align) sang 1 vị trí/hướng mới, bằng cách chỉ định 1 mặt phẳng ban đầu (A) và 1 mặt phẳng đích (B) — Orient sẽ khớp mặt phẳng A trùng khít với B, kéo theo toàn bộ hình học di chuyển tương ứng. Ví dụ 1: mặt phẳng ban đầu lấy từ Evaluate Surface (tại điểm LCS 0.5,0.5, output F là tangent plane), mặt phẳng đích là **XY Plane** (Plane > Vector) — kết quả là "làm phẳng" 1 mặt cong về mặt phẳng chuẩn XY.

Ví dụ 2 phức tạp hơn: định hướng lại hàng loạt "rib-surface" (surface dạng sườn) đang nằm rải rác về cùng 1 hàng thẳng trên mặt phẳng XY — mặt phẳng ban đầu của mỗi rib lấy từ vector pháp tuyến N (Evaluate Surface) làm trục z của **Plane Normal**; mặt phẳng đích dựng bằng cách dịch 1 điểm theo trục Y dùng Series làm hệ số nhân vô hướng (N-input = khoảng cách giữa các rib, vd 13 đơn vị; C-input = số lượng rib, tính bằng List Length), tại mỗi điểm dựng 1 XY Plane — cuối cùng Orient toàn bộ rib sang các mặt phẳng đích này, xếp chúng thành 1 hàng đều đặn.

## 4.3 Affine transformations

Nhóm phép biến đổi Affine (Transform > Affine) gồm: scale (co giãn), shear (cắt xiên), projection (chiếu), mapping.

### 4.3.1 Scale component: uniform scaling (co giãn đều)
**Scale** (Transform > Affine) co/giãn đều hình học (G) theo 3 hướng x,y,z cùng lúc, quanh 1 tâm scale (C, có thể là bất kỳ điểm nào) với hệ số scale (F). F phải là số dương, **không được bằng 0** (lỗi toán học). Ba trường hợp: 0<F<1 → thu nhỏ; F=1 → không đổi; F>1 → phóng to.

Có thể scale nhiều đối tượng cùng lúc với cùng 1 hệ số (đồng loạt to/nhỏ theo cùng tỉ lệ), hoặc mỗi đối tượng 1 hệ số riêng — ví dụ 6 khối hộp phóng to dần bằng cách nối **Series** (dãy hệ số tăng dần) vào input F, với input C là trọng tâm riêng của từng khối. Series chỉ sinh được dãy tăng/giảm **tuyến tính** — để có kiểu scale phức tạp hơn (theo 1 hàm toán học phi tuyến), dùng **Graph Mapper** (xem 4.3.2). Ví dụ minh hoạ: dãy hệ số đối xứng (1,2,3,4,5,4,3,2,1) tạo hình dạng parabol; dãy này tương ứng hàm y = -(1/10)x² + x + 1 với 1≤x≤9 nếu dùng Evaluate. Sách nhận xét: thao tác trực tiếp với phương trình toán học phức tạp không dễ, nên Grasshopper cung cấp công cụ thay thế tiện hơn — Graph Mapper.

### 4.3.2 Graph Mapper component
**Graph Mapper** (Params > Input) cho phép **chọn 1 dạng hàm số có sẵn từ danh sách** thay vì gõ công thức, rồi tinh chỉnh bằng cách kéo grip trực tiếp trên đồ thị. Danh sách loại đồ thị (right-click component → Graph types): None, Bezier, Conic, Gaussian, Linear, Parabola, Perlin, Power, Sinc, Sine, Sine Summation, Square Root.

Cách dùng: Graph Mapper thay thế vị trí của Evaluate trong sơ đồ — cần cấp 1 domain đầu vào (qua Construct Domain + Range) và **số lượng giá trị cấp vào Graph Mapper phải bằng đúng số hình học cần scale**. Vì Range luôn sinh N+1 giá trị (N là input N-input), phải lấy số hình học (qua List Length) trừ đi 1 để ra đúng N cần nhập cho Range.

Điểm quan trọng dễ nhầm: Graph Mapper có **2 domain nội bộ** cần set riêng (double-click mở Graph Editor):
- **Domain A** (góc trên-trái cửa sổ): phải khớp với domain đã cấp cho Range (vd [1,9]).
- **Domain B** (góc dưới-phải): tự do định nghĩa, kiểm soát khoảng giá trị đầu ra (output) — vd đặt B=[1,4] thì hệ số scale nhỏ nhất là 1, lớn nhất là 4.
Sách minh hoạ nhiều tổ hợp đồ thị + domain B khác nhau cho ra các tập hệ số scale khác nhau, áp dụng vào ví dụ toà nhà nhiều tầng — mỗi loại Graph Mapper cho ra 1 hình dáng công trình khác biệt hoàn toàn (thu nhỏ dần lên đỉnh, phình giữa, v.v).

### 4.3.3 Image Sampler component
**Image Sampler** (Params > Input) là input-component chuyển **thông tin màu sắc của 1 ảnh** thành giá trị số. Mọi ảnh chữ nhật được coi như 1 domain 2 chiều (u,v) mặc định từ 0–1; mỗi điểm P trên lưới ứng với 1 toạ độ (u,v) sẽ trả về 1 giá trị **cường độ (intensity)** phụ thuộc **color model** đang chọn (RGB, grayscale...). Với grayscale: 0 = đen, 1 = trắng, các giá trị phân số ở giữa là các mức xám.

Mở editor bằng double-click vào component, cho phép nạp file ảnh, chọn color model, và bật/tắt nội suy (interpolate). Input là danh sách điểm toạ độ UV, output là danh sách giá trị cường độ.

Ví dụ ứng dụng chính: dựng pattern hình tròn trên 1 freeform surface theo ảnh grayscale — chuyển điểm từ WCS sang toạ độ uv bằng **Surface CP**, dùng normal vector N để dựng vòng tròn bằng **Circle CNR**, bán kính cố định ban đầu. Sau đó lấy chính output uvP của Surface CP làm input cho Image Sampler để lấy giá trị cường độ (0–1) — dùng trực tiếp giá trị này làm **hệ số scale (F)** cho component Scale, co các vòng tròn theo độ sáng ảnh: vùng sáng (gần 1) hầu như không scale, vùng tối (gần 0) scale nhỏ gần như biến mất. Lưu ý surface gốc phải được Reparameterize trước. Vùng ảnh **đen tuyệt đối** trả về hệ số scale=0 (lỗi toán học như đã nói ở 4.3.1) — khắc phục bằng component **Maximum** để thay mọi giá trị 0 bằng 1 giá trị nhỏ khác (vd 0.1).

Image Sampler cũng dùng được với ảnh màu qua nhiều color model khác — ví dụ RGB trả về bộ 3 giá trị (kênh) 0–255. Component **ARGB** (Display > Colour) tách riêng 4 kênh Alpha/Red/Green/Blue từ 1 màu — mặc định output trong khoảng 0–1, right-click chọn "Integer Channels" để đổi về thang 0–255. Ví dụ minh hoạ: dùng ảnh màu để điều khiển độ đẩy ra (offset) khác nhau của các phần surface tương ứng vùng màu đỏ trong ảnh — tạo hiệu ứng gờ nổi theo hoạ tiết ảnh gốc.

## 4.4 Other transformations: Box Morph

**Box Morph** (Transform > Morph) biến dạng hình học bằng cách "kéo giãn" 1 khối hộp tham chiếu (reference box) sang khớp với 1 khối hộp đích (target box) — tương tự lệnh Cage/CageEdit trong Rhino. Cần 3 input:
1. **G** — hình học cần morph.
2. **R** — khối hộp tham chiếu bao quanh hình học G, thường dựng bằng **Bounding Box** (Surface > Primitive).
3. **T** — khối hộp đích, dựng bằng bất kỳ box-component nào của Grasshopper.

Box Morph biến đổi khối R thành khối T, kéo theo hình học G bên trong bị biến dạng tương ứng. Ví dụ đơn giản dùng **Center Box** làm target box.

Có thể morph **nhiều hình học cùng lúc** vào 1 khối đích duy nhất: đặt Bounding Box ở chế độ "Union Box" (right-click) để bao trọn tất cả hình học vào 1 box duy nhất trước. Target box trong trường hợp này có thể dùng **Twisted Box** (Transform > Morph) — dựng khối hộp "vặn xoắn" từ 8 điểm góc (có thể set từ Rhino hoặc dựng trong Grasshopper); di chuyển 8 điểm góc này trong Rhino sẽ làm hình học morph biến dạng theo thời gian thực.

### 4.4.1 Paneling (Ốp panel)
Mở rộng logic Box Morph sang **nhiều target box cùng lúc** — kỹ thuật cốt lõi để dựng hệ mặt dựng panel hoá (paneling) trên 1 surface tự do. Quy trình 2 bước:
1. **Tạo tập twisted box (T) trên surface**: component **Surface Box** (Transform > Morph) sinh các khối hộp xoắn bám theo bề mặt, dựa trên 1 domain 2 chiều (D — số ô chia theo u,v, vd lưới 20×20) và chiều cao (H).
2. **Morph 1 hình học (G, bao trong Bounding Box R) vào từng target box T** — mỗi target box nhận 1 bản sao đã biến dạng của G, tạo thành hệ panel phủ kín surface.

Nếu nối 1 dãy giá trị ngẫu nhiên (Random) vào input H của Surface Box thay vì 1 số cố định, mỗi panel sẽ có chiều cao khác nhau ngẫu nhiên — tạo hiệu ứng bề mặt gồ ghề, không đều, minh hoạ khả năng "làm giàu" hình dạng panel chỉ bằng cách thay đổi input số học đơn giản.
