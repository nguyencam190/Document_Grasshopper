# Chương 8 — Digital Fabrication (Chế tạo số — biến ý tưởng thành vật thật)

Chương này ít component Grasshopper thuần tuý, thiên về kiến thức nền công nghệ chế tạo số (CNC, in 3D...) và 1 case-study lớn dựng mẫu bình hoa in 3D bằng chính Grasshopper.

## Mở đầu: từ mô hình số đến vật thể thật

Sách nhấn mạnh: trước cách mạng số, người thiết kế quản lý độ phức tạp công trình bằng cách chia nhỏ thành từng phần, nghiên cứu lắp ráp qua mô hình tỉ lệ và bản vẽ — cách này giới hạn ở hình khối vuông góc, thiếu khả năng xử lý hình dạng phức tạp (trừ vài ngoại lệ như Jørn Utzon, Heinz Isler, Antoni Gaudí). Cách mạng số gỡ bỏ giới hạn này bằng cách gắn trực tiếp đầu ra thiết kế với chế tạo — đặc biệt qua **CNC** (Computer Numerical Control — dùng máy tính điều khiển chuyển động máy công cụ: phay, tiện, cắt laser, waterjet...), bỏ qua hẳn bước vẽ kỹ thuật trung gian. Chế tạo số giúp độ chính xác tăng và "bình thường hoá độ phức tạp" — 1 chi tiết phức tạp có độ khó gia công ngang với chi tiết đơn giản (máy không "vất vả" hơn vì hình dạng lạ). **Rapid Prototyping (tạo mẫu nhanh)** — kỹ thuật chế tạo cộng dồn (additive), đắp vật liệu theo từng lớp — được dự đoán sẽ tác động lớn tới tương lai ngành sản xuất/xây dựng.

## 8.1 Fabrication Techniques (Kỹ thuật chế tạo)

### 8.1.1 Bi-dimensional Cutting (Cắt tấm phẳng 2D)
Biến tấm phẳng (nhôm, thép, gỗ dán, mica...) thành cấu kiện 3D qua các kỹ thuật xếp lớp (stacking), ghép mặt (faceting), hoặc uốn cong tấm phẳng thành hình dạng developable (độ cong Gauss = 0, xem lại 3.8.1). Sách dẫn 2 ví dụ thực tế: cài đặt nghệ thuật **NU:S** (2012, Arturo Tedeschi & Maurizio Degni) ghép các tấm nhôm phẳng cắt bằng waterjet; và tác phẩm điêu khắc của Carlo Borer (2011) bằng cách uốn và ghép các tấm kim loại — hình học là tập hợp các surface Gauss=0.

Các kỹ thuật cắt (cutting-based):
- **CNC Laser cutter**: đốt/nung chảy vật liệu bằng tia laser hội tụ, công suất và tốc độ cắt tuỳ vật liệu. Không dùng được cho mọi vật liệu — vd tấm nhôm phản xạ laser nên không cắt được.
- **CNC Plasma cutter**: cắt bằng dòng khí siêu nóng (plasma) hội tụ — dùng phổ biến cho thép và nhôm.
- **CNC Waterjet cutter**: cắt bằng tia nước áp lực cao trộn hạt mài. Ưu điểm lớn: không sinh vùng ảnh hưởng nhiệt (không làm biến đổi cấu trúc phân tử vật liệu) — dùng được cho dải vật liệu rất rộng, từ thép tới gỗ.

### 8.1.2 Subtractive techniques (Kỹ thuật trừ vật liệu)
**CNC milling (phay CNC)** tạo hình bằng cách loại bỏ vật liệu, có thêm khả năng kiểm soát độ sâu Z so với máy cắt phẳng. Khối vật liệu đặc (gỗ, xốp polystyrene...) có thể phay thành hình mong muốn — nhưng không phải hình nào cũng phay được bằng máy 3 trục (undercut/hình lõm ngược cần chia nhỏ thành nhiều phần). Sách dẫn 2 ví dụ mock-up thực tế từ Illinois School of Architecture (Rhectomic Farm, Kiva).

Phân loại máy phay theo số trục/kiểu chuyển động:
- **2D mill**: cắt ở 1 độ sâu Z cố định, giống máy cắt.
- **2.5D mill**: hoạt động 3 trục nhưng chỉ thao tác đồng thời trên 2 trục tại 1 thời điểm.
- **3D mill**: thao tác đồng thời cả 3 trục.
- **5-axis mill** (tiên tiến hơn): di chuyển 4+ trục, hạn chế ràng buộc về hình dạng gia công được.
Máy phay được điều khiển bằng đường chạy dao (tooling path) mô tả từ hình học số. Sách dẫn ví dụ tác phẩm điêu khắc "Aura" của Zaha Hadid Architects, phay bằng máy CNC 6 trục trên vật liệu bọt polyurethane.

- **Hot-wire foam cutter**: cắt xốp polystyrene (hoặc vật liệu tương tự) bằng dây điện trở nung nóng — có loại cắt trên 1 mặt phẳng, có loại cắt đa mặt phẳng, thường dùng tạo hình 3D nhanh.
- **Robotic arms (cánh tay robot)**: hỗ trợ nhiều kỹ thuật chế tạo khác (gắn đầu phay, dây nung, kẹp/gấp, tạo hình tấm...) — độ linh hoạt cao được cả giới học thuật lẫn văn phòng thiết kế tiên phong khai thác. Sách dẫn ví dụ công nghệ **RoboFold** (robofold.com) tạo hình tấm kim loại bằng robot thay vì khuôn dập đắt tiền truyền thống.

### 8.1.3 Additive techniques (Kỹ thuật cộng vật liệu — in 3D)
**Additive Manufacturing (AM)**, còn gọi Rapid Prototyping hay in 3D, tạo vật thể bằng cách đắp từng lớp vật liệu chồng lên nhau — cho phép tạo hình bất khả thi với kỹ thuật trừ vật liệu (hình phân nhánh, xoắn phức tạp, bộ phận chuyển động lồng vào nhau, dù hiện tại còn giới hạn ở tỉ lệ nhỏ). Nguyên lý: cắt lát (slice) mô hình số thành các lớp mỏng theo 1 độ phân giải xác định, mỗi lớp mô tả đường đắp vật liệu. Quy trình 3 bước: (1) dựng mô hình 3D số đạt tiêu chuẩn in được (mục 8.2); (2) chuyển mô hình sang định dạng mã máy đọc được; (3) in 3D thật.

Định dạng phổ biến nhất: **STL (Standard Tessellation Language)**, phát triển bởi 3D Systems — chuyển mô hình 3D thành lưới tam giác, xuất toạ độ mỗi đỉnh theo quy tắc bàn tay phải (right-hand rule); càng nhiều lần chia tam giác thì mô hình càng mượt. STL có dạng ASCII hoặc Binary (Binary phổ biến hơn vì file nhỏ hơn).

3 công nghệ in 3D phổ biến nhất:
- **Stereolithography (SLA)** — phát triển bởi Charles Hull năm 1983. Gồm 4 thành phần: bể chứa nhựa resin lỏng nhạy sáng, bệ đỡ có lỗ di chuyển được, tia UV, và máy tính điều khiển cả tia UV lẫn bệ đỡ. Bệ đỡ ban đầu đặt ngay dưới 1 lớp resin mỏng; tia UV làm đông cứng resin theo đúng hình dạng lớp cắt; bệ hạ xuống đúng 1 độ dày lớp để in tiếp lớp sau, lặp lại tới hết. Sau khi hoàn thành, rửa bằng dung môi lỏng và nung trong lò UV để hoàn thiện nhựa. Resin chưa đông giữ dạng lỏng, không chống đỡ được phần nhô ra bên trên — vì vậy thường cần cấu trúc đỡ (support). SLA cho độ phân giải rất cao nhưng chậm và đắt.
- **Selective Laser Sintering (SLS)** — phát triển bởi Carl Deckard (Đại học Texas) năm 1986. Gồm 4 thành phần: laser công suất cao, khay chứa bột, con lăn, bệ chế tạo. Con lăn trải 1 lớp bột mỏng (nhựa, kim loại, gốm, thuỷ tinh...) lên bệ, laser thiêu kết (sintering) đúng phần cắt lát 2D của vật thể; bệ hạ xuống 1 lớp, con lăn trải lớp bột mới — lặp lại tới hết. SLS **không cần cấu trúc đỡ** vì phần đã thiêu kết luôn được bột chưa thiêu kết bao quanh nâng đỡ. Sách dẫn ví dụ đôi giày tham số "NU:S parametric shoes" (2012) in bằng SLS bột nylon.
- **Fuse Deposition Modeling (FDM)** — phát triển bởi Scott Crump năm 1988. Tạo hình bằng cách nung chảy sợi nhựa (filament) và đắp từng lớp mỏng lên bệ. Giống SLA, FDM cũng cần cấu trúc đỡ cho phần nhô ra — 1 số máy FDM in được đa vật liệu, cho phép in support bằng vật liệu dễ tháo (vd sợi tan trong nước). FDM dùng 2 loại nhựa chính: ABS, hoặc phiên bản hữu cơ hơn là PLA.

Sách nhắc thêm 1 kỹ thuật mới lạ: **MX3D-Metal** (Joris Laarman hợp tác với Autodesk) — dùng cánh tay robot đắp kim loại nóng chảy trực tiếp lên 1 surface kim loại có sẵn, không cần cấu trúc đỡ vì kim loại đông cứng rất nhanh.

Về mặt khái niệm, kỹ thuật additive **đảo ngược tư duy tối ưu hoá truyền thống**: trước đây tối ưu gắn liền với đơn giản hoá thao tác cắt, tăng độ tương đồng giữa các cấu kiện, tìm developable surface hoặc panel phẳng... Với additive, tối ưu hoá là tìm hình dạng đáp ứng đúng chỉ tiêu hiệu năng (vd dùng ít vật liệu nhất) — mở đường cho các chiến lược form-finding tiên tiến như **topology optimization** (sẽ học ở chương 10) ngày càng quan trọng trong kiến trúc và thiết kế sản phẩm.

## 8.2 Modeling Printable Objects (Dựng mô hình in được)

Hiện tại in 3D khả thi chủ yếu ở quy mô nhỏ (giới hạn build volume của máy in thương mại cao cấp khoảng 1000×1000×500mm). Dựng mô hình cho in 3D về kỹ thuật không khác dựng mô hình 3D thông thường, nhưng phải tuân theo ràng buộc riêng của công nghệ in và vật liệu.

### 8.2.1 Main characteristics of a printable 3D model (Đặc điểm bắt buộc của mô hình in được)
4 tiêu chí **hình học (Geometric)**:
- **G1. Closed (watertight) geometry — hình học kín/không rò rỉ**: mỗi surface/mesh có mặt trong (đỏ trong hình minh hoạ sách) và mặt ngoài (xám); vật thể chỉ in được nếu **không có mặt trong nào lộ ra ngoài** (hoàn toàn kín, không hở).
- **G2. Manifold mesh — mesh "đa tạp"**: chỉ mesh manifold mới in đúng được. Mesh là manifold nếu **không có cạnh nào bị 3 mặt trở lên dùng chung**. Mesh non-manifold thường do mô hình không nhất quán hoặc các đối tượng chồng lấn — mục 6.6.3 đã dạy cách loại bỏ mặt chồng lấn.
- **G3. Orientable mesh (correct normals) — mesh có hướng nhất quán**: mọi pháp tuyến mặt phải theo cùng 1 logic hướng (xem lại 6.2).
- **G4. No self-intersections — không tự giao cắt**: hình học không được chứa các đối tượng giao cắt nhau mà chưa qua phép Boolean.

4 ràng buộc **kỹ thuật (Constraint)**:
- **C1. Maximum size (build volume)**: vật thể không được vượt kích thước khay in tối đa của từng máy; vật lớn hơn phải chia nhỏ để lắp ráp sau.
- **C2. Minimum wall-thickness (độ dày thành tối thiểu)**: tuỳ công nghệ/vật liệu — vd SLS in nhựa có độ dày thành tối thiểu khoảng 0.7mm.
- **C3. Resolution (độ phân giải)**: độ phân giải ngang XY (bước di chuyển nhỏ nhất của đầu in, đo bằng micron, 100 micron=0.1mm) và độ phân giải đứng Z (độ dày mỗi lớp in) — chi tiết nhỏ hơn 2 độ phân giải này sẽ không in được.
- **C4. Gravity (trọng lực)**: vật thể in ra là vật lý thật, phải tuân luật trọng lực — có thể kiểm tra trọng tâm/mô phỏng ổn định bằng phần mềm ngoài trước khi in.

### 8.2.2 Example: parametric modeling of a vase (Ví dụ: dựng bình hoa tham số)
Case-study lớn: mẫu bình hoa **Pandora | AL** (Arturo Tedeschi, 2011), in trên máy in để bàn thông thường (build volume 200×200×200mm). Quy trình chi tiết:

1. **Dựng đường cong NURBS kín** trong ô vuông 100×100mm.
2. **Dịch chuyển theo trục Z** bằng nhân vô hướng: Series sinh dãy hệ số nhân với Unit Z, bước 10mm; vì giới hạn build volume theo Z là 200mm, đặt C-input của Series = 18 (→ tổng chiều cao 180mm).
3. **Scale mỗi đường cong đã dịch**: tâm scale = trọng tâm mỗi curve (qua component Area), hệ số scale lấy từ **Graph Mapper** (kiểu Bezier) — vì build volume X,Y giới hạn 200mm, đặt domain Y của Graph Mapper là [0,2] để hệ số scale tối đa (=2) vẫn nằm trong giới hạn khay in.
4. **Xoay mỗi đường cong quanh 1 trục trung tâm** bằng **Rotate Axis**, góc xoay (radian) lấy từ dãy Series.
5. **Loft** toàn bộ các đường cong đã xoay+scale → ra 1 untrimmed surface (chưa in được — chưa có độ dày, chưa kín).
6. Tạo nắp đáy bằng **Boundary Surfaces**, Join lại với surface Loft, gán độ dày thành bằng **Mesh Thicken** (Weaverbird > Transform) — nhưng cách này cho ra **cạnh sắc** (không mượt).

Để có cạnh mượt, sách dùng chiến lược thay thế: trích 1 isocurve dọc từ surface Loft (tại t=1 dùng Evaluate Curve), nối với 1 curve nối từ trọng tâm đường cong đáy (curve 0) tới điểm đầu isocurve; chia curve ghép này bằng Divide Curve (28 điểm trong ví dụ), dựng lại thành 1 curve mượt tự do (không phẳng) bằng **Nurbs Curve**; sau đó **xoay curve này quanh 1 trục** bằng **Rail Revolution** (Surface > Freeform, input R = curve dẫn hướng "Curve 02", trục xoay = "Line 01") → ra 1 NURBS surface có cạnh mượt tự nhiên.

Bước tiếp theo: **morph** surface này bằng **Box Morph** — reference box (R) là bounding box của surface (dùng **Bounding Box**, Surface > Primitive), target box (T) là 1 biến dạng của bounding box đó, dựng bằng cách tách và dịch các đỉnh, rồi tái tạo lại bằng **Twisted Box** (Transform > Morph). Kết quả sau morph được chuyển thành mesh bằng **Mesh Surface**, làm mượt bằng **Weaverbird Catmull-Clark**, cuối cùng gán độ dày thành 2.0mm bằng **Mesh Thicken** — cho ra 1 vật thể mesh watertight, in được thật sự.

Trước khi in, mesh cuối cùng nên bake vào Rhino và kiểm tra bằng lệnh `check` (công cụ chẩn đoán lỗi hình học của Rhino) — nếu không lỗi, export sang định dạng STL (`File > Save As` hoặc `Export > STL`) để chuyển cho máy in hoặc phần mềm khác.

## 8.3 Modeling objects for cutting based operations (Dựng mô hình cho chế tạo bằng cắt)

Vật thể quy mô trung bình (ngoài khả năng của kỹ thuật additive hiện tại) thường chế tạo bằng cắt, lắp ráp từ nhiều phần theo kỹ thuật **sectioning (cắt lát)** hoặc **waffling (lưới ô caro 2 hướng)**.

### 8.3.1 Example: sectioning and waffling
**Sectioning (cắt lát)**: cắt 1 mô hình theo 1 hướng thành các lát cắt phẳng song song, khoảng cách bằng độ dày vật liệu cần phay — dán các lát lại theo thứ tự sẽ xấp xỉ hình dạng gốc. Cũng có thể phay trực tiếp từ 1 khối đặc nhưng hình lõm ngược (undercut) đòi hỏi máy phay 3D. Sectioning tạo tính liên tục dọc theo hướng cắt nhưng **hạn chế liên tục theo hướng vuông góc với mặt cắt** — 1 mẹo thường dùng: chừa khoảng cách nhỏ giữa các lát để tạo ảo giác liên tục theo hướng đó.

Quy trình dựng thuật toán sectioning 1 hướng: xác định hướng cắt, dựng dãy mặt phẳng cắt, giao mặt phẳng với mô hình để ra các đường cắt (section). Cụ thể: dùng **Divide Distance** chia 1 cạnh biên (của surface hình chữ nhật) theo khoảng cách bằng đúng độ dày vật liệu; tại mỗi điểm chia dựng mặt phẳng bằng **Plane Normal**; giao mặt phẳng với Brep gốc bằng component **Sec** (Intersect > Mathematical) để ra đường cắt. Mỗi đường cắt được offset (theo mặt phẳng của nó) bằng **Offset** (Curve > Util) — offset có thể sinh gián đoạn, khắc phục bằng cách chia N phần rồi dựng lại curve mượt bằng **Nurbs** (component tương tự Nurbs Curve).

Nối đường cắt gốc với bản offset mượt bằng 2 đoạn nối 2 đầu, gộp 4 curve vào 1 branch bằng **Merge** (chế độ simplify), rồi **Join** để ra danh sách curve phẳng khép kín — dùng **Orient** (xem lại 4.2.3) để đưa từng curve về đúng mặt phẳng XY chuẩn bị cho máy cắt/phay. Vì hầu hết máy CNC **không đọc được curve NURBS**, phải chuyển curve thành cung tròn (arc) và đoạn thẳng (segment) — 2 chiến lược: (1) chia curve thành rất nhiều điểm rồi nối polyline qua các điểm đó; (2) dùng lệnh `Convert` của Rhino để chuyển curve thành arc/polyline theo 1 dung sai (tolerance) đặt trước. Sau khi chuyển đổi, các hình được sắp xếp (nesting) để tối ưu vật liệu — làm thủ công, qua phần mềm bên thứ 3, hoặc plug-in chuyên dụng.

**Waffling** — kỹ thuật cắt lát theo **2 hướng vuông góc** thay vì 1 hướng, tạo cấu trúc dạng lưới caro/waffle. Có nhiều plug-in Grasshopper tự động hoá quy trình này. Sách liệt kê các biến thể waffling theo hình dạng gốc và hướng cắt: **Radial** (toả tròn), **Symmetrical** (đối xứng), **2D-Adaptive**, **1D-Adaptive** (ảnh minh hoạ từ Hassan Ragab).

Nguyên tắc chung của waffling: tính mọi giao điểm có thể giữa các "rib" (sườn/mặt phẳng cắt), trả về danh sách đoạn giao cắt (intersection-segments); tại mỗi đoạn giao, tạo 2 hộp miền (domain box) A' và B', sau đó dùng phép **Solid Difference** (trừ khối) A−A' và B−B' để "khoét khe" cho phép 2 rib lắp khít vào nhau như đồ chơi lắp ghép waffle. Sách dẫn ví dụ thực tế: "Parametric Soft Wall" của Studio Kami (Rome, 2012).

## 8.4 NU:S Installation

Mục này là 1 bài luận/case-study nghệ thuật (không có nội dung kỹ thuật Grasshopper cụ thể) do Antonella Buono (Fashion Designer, giảng viên Fashion Design tại UARC cho Philadelphia University) viết, mô tả dự án sắp đặt nghệ thuật **"NU:S — Fashion clothes Architecture"** (Arturo Tedeschi & Maurizio Degni), trưng bày tại Chiostro del Bramante rồi Bảo tàng Nghệ thuật Đương đại Roma. Dự án lấy cảm hứng từ không gian tu viện Bramante và logic toán học kiến trúc Phục Hưng, diễn giải lại qua ngôn ngữ tham số, đồng thời gắn với kỹ năng may đo cao cấp (haute couture) — nêu bật sự tương đồng giữa cách mạng công nghệ số hiện tại với việc giới nghệ sĩ Phục Hưng thế kỷ 15 ứng dụng phối cảnh (perspective) vào hội hoạ. Sách cũng dẫn thêm ảnh đôi giày tham số "NU:S parametric shoes" (2012, Maurizio Degni, Alessio Spinelli, Arturo Tedeschi) in bằng bột nylon thiêu kết.

## 8.5 Large-scale objects (Vật thể quy mô lớn)

Với công trình quy mô lớn (pavilion, mái che, vỏ mỏng, nhà, toà nhà) cần cân nhắc thêm yếu tố kỹ thuật/kết cấu/công năng, thường lắp ráp từ nhiều cấu kiện chế tạo riêng lẻ chịu tải trọng phối hợp. Sách nêu 2 hướng nghiên cứu chính:

**1. Computational approach (tiếp cận tính toán)**: thách thức truyền thống khi dựng mặt dựng freeform là **xấp xỉ surface bằng các panel phẳng cùng kích thước** để giảm chi phí sản xuất và tái sử dụng khuôn — trước đây thường làm bằng cách tam giác hoá surface (nhưng có nhược điểm: kết cấu đỡ nặng, node kết cấu phức tạp). Kỹ thuật tính toán hiện đại cho phép tìm **PQ Mesh** (Planar Quad Mesh — mesh tứ giác phẳng, xem 6.3.3) từ freeform surface bất kỳ, và trong 1 số điều kiện còn tìm được **P-Hex Mesh** (Planar Hexagonal Mesh — mesh lục giác phẳng) — ưu điểm của P-Hex Mesh là mỗi node kết cấu chỉ nối đúng 3 thanh (đơn giản hoá đáng kể node kết cấu so với node tam giác nối 6 thanh). Chiến lược **developable surface** (xem 3.8.1) cũng quan trọng: vì mọi developable surface đều là ruled surface, luôn tìm được tập đường thẳng (rulings) — dùng trực tiếp làm trục các dầm thẳng, đơn giản hoá kết cấu đỡ.

**2. Innovative fabrication (chế tạo cách tân)**: thay vì tối ưu trong khuôn khổ chế tạo truyền thống, hướng này phát triển hẳn phương pháp chế tạo mới. Sách dẫn ví dụ công ty tiên phong **D-Shape**, do kỹ sư/nhà phát minh người Ý Enrico Dini dẫn dắt, thử nghiệm thành công kỹ thuật in 3D (additive) ở quy mô lớn — máy in D-Shape kích thước 5m×6m được giới thiệu là **máy in 3D quy mô lớn đầu tiên trên thế giới**. Công nghệ này buộc người thiết kế phải suy nghĩ lại hoàn toàn cách quan niệm và tối ưu hoá kết cấu.
