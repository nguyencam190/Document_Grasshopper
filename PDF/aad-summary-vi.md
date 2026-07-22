# Giới thiệu chung

Sách **"AAD — Algorithms-Aided Design: Parametric Strategies Using Grasshopper"** do kiến trúc sư
Arturo Tedeschi viết, Le Penseur Publisher xuất bản năm 2014, có lời tựa của Fulvio Wirz. Sách dạy
tư duy **thiết kế thuật toán** (dùng quy tắc/công thức để tạo hình thay vì vẽ tay) bằng Grasshopper,
từ khái niệm nền tảng đến kỹ thuật nâng cao (mô phỏng vật lý, tối ưu hoá kết cấu, phân tích môi
trường, chế tạo số). Xen giữa các chương kỹ thuật là các bài luận ngắn (essay) do kiến trúc sư/nhà
nghiên cứu khách mời viết, chia sẻ góc nhìn và dự án thực tế.

## Introduction — AAD: Algorithms-Aided Design

Phần mở đầu kể lại lịch sử chuyển từ **bản vẽ tay** (chỉ cộng dồn nét vẽ, không có quan hệ ràng buộc
giữa các phần) sang **thiết kế thuật toán**. Các kiến trúc sư tiên phong (Gaudí, Isler, Otto, Musmeci)
từng dùng mô hình vật lý (dây treo, màng xà phòng...) để "tìm hình" (form-finding) vì bản vẽ không mô
phỏng được lực. Luigi Moretti đặt ra thuật ngữ "Kiến trúc tham số" năm 1939; Ivan Sutherland tạo ra
Sketchpad (1963) — phần mềm CAD đầu tiên có "ràng buộc" (constraint) giữa các đối tượng; sau đó
Pro/ENGINEER (1987) mang tư duy tham số vào CAD cơ khí. Sách định nghĩa **thuật toán** là một chuỗi
bước rõ ràng nhận input và trả output; **Grasshopper** thuộc nhóm phần mềm "lập trình trực quan"
(visual scripting) — thay vì gõ code, người dùng nối các "node" (khối lệnh) bằng dây trên khung vẽ.
Chương cũng phân biệt hai hướng làm hình: **form-making** (hình xuất phát từ ý tưởng, tinh chỉnh dần)
và **form-finding** (hình "xuất hiện" từ việc phân tích các ràng buộc/lực).

## Chương 1 — Làm quen Grasshopper

Chương giới thiệu Grasshopper: plugin miễn phí cho Rhinoceros do David Rutten phát triển (ra mắt 2007
với tên Explicit History, đổi tên năm 2008), chạy trên Windows. Giao diện gồm 4 phần: thanh menu,
các tab component (nhóm lệnh theo chủ đề, mỗi tab chia thành nhiều "panel"), thanh công cụ canvas và
khung vẽ (canvas). Có 3 loại component: component xử lý dữ liệu (nhận input, trả output), component
nhập liệu (Input, vd Number Slider — thanh trượt số), và component chứa dữ liệu (container, hình lục
giác đen, dùng lưu geometry lấy từ Rhino). Dữ liệu có thể gán theo 3 cách: gán cục bộ (chuột phải),
nối dây từ component khác, hoặc lấy trực tiếp từ Rhino. Trạng thái component thể hiện qua màu nền:
xám (đúng), cam (cảnh báo — thường do thiếu dữ liệu), đỏ (lỗi — sai kiểu dữ liệu). File lưu dạng
`.gh` (nhị phân) hoặc `.ghx` (XML). Vì Grasshopper chỉ tạo hình "xem trước" (preview) tạm thời, muốn
biến thành đối tượng Rhino thật phải **Bake** (chuột phải → Bake). Chương cũng giải thích luồng chảy
dữ liệu một chiều trái→phải (không có vòng lặp gốc), cách bật/tắt hiển thị component, các kiểu dây
nối (cam = không có dữ liệu, mảnh = 1 giá trị, đậm = nhiều giá trị), và loạt lệnh cơ bản: tìm điểm
trên đường (Point on Curve, End Points), Merge gộp dữ liệu, Divide Curve chia đường, Move + Vector để
di chuyển đối tượng.

## Chương 2 — Data: Quản lý dữ liệu

Grasshopper lưu dữ liệu dạng **danh sách (list)**, mỗi phần tử có chỉ số (index) bắt đầu từ 0. Chương
dạy các lệnh **lọc dữ liệu**: List Item (lấy 1 phần tử theo index), Cull Index (xoá 1 phần tử theo
index), Cull Pattern (giữ/loại theo mẫu lặp True-False), Shift List (dịch chuyển index), Split
List/List Length (tách danh sách, đếm số phần tử), Reverse List (đảo thứ tự). Tiếp theo là các lệnh
tạo **dãy số**: Series (dãy số cách đều theo bước nhảy), Range (chia đều một khoảng giá trị), Random
(số ngẫu nhiên trong khoảng), Repeat Data (lặp lại một tập số cho đủ độ dài). Phần "Data Matching"
giải thích cách Grasshopper ghép các danh sách khác độ dài (Shortest List, Longest List, Cross
Reference — dùng Cross Reference để tạo lưới 2D/3D từ các dãy 1D). Mục Mathematical Functions dùng
component Evaluate F(X) để vẽ đường cong/mặt từ công thức toán (ví dụ tái tạo mái Bảo tàng Anh từ 3
phương trình 2 biến). Mục Conditions dạy toán tử so sánh, Dispatch (tách danh sách theo điều kiện
đúng/sai), câu lệnh điều kiện if/then, Contains. Cuối chương là **Remap Numbers** (đổi thang giá trị)
và khái niệm **Attractor** (vật hút) — một điểm/đường dùng để biến đổi hình xung quanh nó tuỳ theo
khoảng cách, ví dụ điểm càng gần attractor thì hình càng phóng to.

## Chương 3 — Control: Curves và Surfaces

Chương giải thích nền tảng hình học **NURBS** (đường cong toán học được định nghĩa bởi bậc (degree),
các điểm điều khiển có trọng số (weight), và knot vector). Mỗi đường/mặt có hệ toạ độ cục bộ (Local
Coordinate System) dùng tham số `t` (đường, chạy từ 0 đến 1) hoặc `u,v` (mặt) — `t` không tỷ lệ thuận
với khoảng cách thực. Loạt component phân tích đường: Evaluate Curve (tìm điểm theo t), Flip Curve
(đảo hướng), Curve CP (đổi toạ độ Thế giới ↔ Cục bộ), Point On Curve (tìm điểm theo % chiều dài),
Divide Curve/Length/Distance (chia đường theo số đoạn/độ dài/khoảng cách), Shatter (cắt đường tại
điểm). Mục **độ cong (curvature)** dùng khái niệm "đường tròn mật tiếp" (osculating circle) để đo độ
cong tại một điểm. Với mặt: các cách tạo mặt (Extrude, Boundary Surfaces, Loft, Surface from Points,
Sweep1/2, Revolution...), phân tích mặt (Evaluate Surface, Isocurve, Divide Surface, Deconstruct Brep
để tách mặt/cạnh/đỉnh — minh hoạ qua ví dụ tạo lưới diagrid và khung không gian). Độ cong mặt gồm
**Gaussian Curvature** (quyết định mặt có "trải phẳng được" — developable surface — hay không, quan
trọng cho chế tạo) và **Mean Curvature** (bằng 0 với mặt cực tiểu như màng xà phòng). Chương kết bằng
kỹ thuật Chebyshev-net (lưới điểm cách đều trên mặt cong) và ví dụ tạo hoạ tiết theo độ cong.

## Chương 4 — Transformations (Phép biến đổi hình học)

Chương phân loại phép biến đổi: **Euclidean** (dịch chuyển/xoay/phản chiếu — giữ nguyên kích thước,
góc), **Affine** (scale/shear — không giữ kích thước nhưng giữ song song), và **Morph** (biến dạng tự
do, chỉ giữ quan hệ tô-pô). Trước hết là các lệnh tạo **vector** (Vector 2Pt, Unit Vector, Amplitude,
nhân vô hướng, Unit X/Y/Z). Nhóm Euclidean gồm Move (di chuyển theo vector), Rotate/Rotate Axis
(xoay), Orient (kết hợp dịch + xoay bằng cách khớp 2 mặt phẳng). Nhóm Affine gồm Scale (phóng to/thu
nhỏ), và đặc biệt **Graph Mapper** — chọn nhanh một hàm toán học (Bezier, Sine, Parabola...) để tạo
dãy giá trị biến thiên phi tuyến thay vì tự viết công thức, dùng để scale nhiều đối tượng theo quy
luật mượt. **Image Sampler** đổi màu sắc/độ sáng của ảnh thành dãy số (0–1) để điều khiển hình học —
ví dụ vùng tối trong ảnh grayscale làm hình co nhỏ lại, tạo hoạ tiết theo ảnh. Cuối chương là **Box
Morph** — biến dạng một hình theo hộp tham chiếu sang hộp đích (giống lệnh Cage/CageEdit của Rhino),
mở rộng thành kỹ thuật **paneling**: tạo lưới hộp xoắn trên một mặt cong (Surface Box) rồi morph một
môđun hình học lặp lại vào từng hộp để phủ kín bề mặt bằng panel.

## Chương 5 — Skins: Quản lý dữ liệu nâng cao (Data Tree)

Chương giải thích **Data Tree** — cấu trúc dữ liệu phân cấp của Grasshopper: mỗi "nhánh" (branch) có
một "đường dẫn" (path, vd `{0;1}`) chứa danh sách các "phần tử" (item). Khi một component xử lý nhiều
đối tượng cùng lúc (vd 4 mặt tam giác), Grasshopper tự tạo 1 nhánh riêng cho mỗi đối tượng — đây là lý
do các lệnh như Polyline vẽ ra nhiều đường riêng biệt thay vì 1 đường nối hết các điểm. 4 lệnh chỉnh
cấu trúc cây được dạy: **Flatten Tree** (gộp hết về 1 nhánh), **Unflatten Tree** (dựng lại nhánh theo
1 cây mẫu), **Graft Tree** (tách mỗi phần tử thành 1 nhánh riêng), **Flip Matrix** (hoán đổi nhánh
↔ phần tử, giống chuyển vị ma trận). Phần thực hành xây 2 kiểu "vỏ" (skin) 3D: hoạ tiết dạng hình chóp
cụt trên lưới chữ nhật (dùng Offset on Srf + Loft, với graft/simplify đúng cách) và trên lưới lục giác
(dùng plugin LunchBox tạo Hexagon Cells, lọc bỏ ô biên không đủ 6 cạnh); cả hai đều dùng điểm attractor
để đổi độ rộng khung theo khoảng cách. Mục dệt (Weaving) tạo hoạ tiết "sợi dọc-sợi ngang" bằng cách
đẩy điểm lưới lên/xuống xen kẽ theo pháp tuyến mặt. Cuối chương dạy chiến lược **sắp xếp lại Data
Tree** (Sort List theo trục x rồi theo trục y, cộng thêm plugin Tree8/Allocate N) để một tập điểm
ngẫu nhiên tạo đúng mặt cong thay vì mặt bị lỗi.

## Chương 6 — Smoothness: SubD và Polygon Mesh

Chương so sánh 2 cách biểu diễn hình 3D: **NURBS** (công thức toán, luôn mượt) và **polygon mesh**
(lưới đa giác gồm đỉnh - vertex, cạnh - edge, mặt - face; càng nhiều mặt càng mượt nhưng không bao giờ
thực sự mượt tuyệt đối). Mesh còn có khái niệm **hướng pháp tuyến** (mặt trước/sau) và phân biệt
**hình học** (geometry, vị trí điểm) với **tô-pô** (topology, cách nối điểm). Có 3 cách tạo mesh trong
Grasshopper: theo tô-pô thủ công (Construct Mesh + Mesh Triangle/Quad, tự định nghĩa thứ tự nối đỉnh),
theo **thuật toán tam giác hoá Delaunay** (tự động nối điểm sao cho tránh tam giác "gầy", tốt cho mô
phỏng), và chuyển đổi từ mặt NURBS sang mesh (Mesh Surface/Mesh UV — chỉ cho kết quả phẳng-đều với
mặt chưa cắt xén). Trọng tâm chương là **SubD (Subdivision Surface)** qua plugin miễn phí
**Weaverbird**: thuật toán **Loop** (dùng cho mesh tam giác, mỗi tam giác chia thành 4) và
**Catmull-Clark** (dùng cho mesh tứ giác) lặp lại nhiều lần để biến mesh thô thành mặt mượt gần giống
NURBS — kỹ thuật phổ biến trong hoạt hình và thiết kế công nghiệp. Các ví dụ thực hành: làm mượt "vỏ"
đã tạo ở chương 5, tạo **Voronoi skin** (dựng chóp trên mỗi ô Voronoi rồi làm mượt), hoạ tiết mờ dần
theo ảnh grayscale (kết hợp Image Sampler), và kỹ thuật loại bỏ các mặt trùng lặp bên trong khi ghép
nhiều khối mesh lại với nhau.

## Essay — Digital Informing Creativity (Ludovico Lombardi, Zaha Hadid Architects)

Bài luận bàn về cách công cụ tính toán (computational design) định hình lại tư duy sáng tạo của kiến
trúc sư, tạo ra một "thẩm mỹ của các quan hệ" (aesthetic of relations) — vẻ đẹp đến từ lực và quy luật
sinh ra hình, giống đàn chim bay hay cấu trúc Gothic. Tác giả cảnh báo hiện tượng lạm dụng công cụ
tham số một cách hời hợt, và nhấn mạnh công cụ tính toán chỉ hỗ trợ chứ không thay thế vai trò sáng
tạo của người thiết kế — cần phân biệt rõ giữa "nhà thiết kế" và "người thạo kỹ thuật" (technical
virtuoso).

## Chương 7 — Loops (Vòng lặp và Fractal)

Grasshopper mặc định **không cho phép vòng lặp** (dữ liệu chỉ chảy một chiều trái→phải), nên các thuật
toán đệ quy (một bước dùng lại kết quả bước trước, lặp lại N lần) cần plugin hỗ trợ. **HoopSnake**
(Yannis Chatzikonstantinou) tạo vòng lặp bằng cách nối đầu ra cuối cùng của chuỗi lệnh ngược lại đầu
vào ban đầu (input S = điều kiện khởi đầu, D* = đầu ra mỗi vòng, B* = số vòng lặp), có nút Step/Auto
Loop All để chạy từng bước hoặc chạy hết. Chương minh hoạ bằng **Koch Snowflake** — đường cong fractal
kinh điển (mỗi đoạn thẳng được thay bằng "gờ" tam giác qua từng vòng lặp) và nhắc lại thuật toán "nửa-
một phần ba" (half-to-third) mà Cecil Balmond dùng để thiết kế Serpentine Pavilion 2002 (Toyo Ito).
Cũng có ví dụ fractal 3D dùng tam giác hoá Delaunay lặp lại. Cuối chương giới thiệu plugin thay thế
**Loop** (Antonio Turiello, dùng 3 component Rnd/Store/Loop kết hợp Timer) cho một cách tiếp cận vòng
lặp khác dựa trên số ngẫu nhiên cập nhật liên tục.

## Chương 8 — Digital Fabrication (Chế tạo số)

Chương hệ thống hoá các kỹ thuật **chế tạo số** — biến mô hình số thành vật thể thật. Nhóm **cắt 2D**
gồm máy CNC Laser, Plasma, Waterjet (cắt bằng tia nước áp lực cao pha hạt mài, không sinh nhiệt nên
dùng được cho nhiều vật liệu). Nhóm **trừ vật liệu** (subtractive) gồm phay CNC (2D/2.5D/3D/5 trục),
cắt dây nóng (hot-wire), cánh tay robot. Nhóm **đắp vật liệu** (additive/in 3D) gồm 3 công nghệ chính:
SLA (nhựa lỏng đóng rắn bằng tia UV), SLS (bột nung chảy bằng laser, không cần đỡ vì bột xung quanh
tự đỡ), FDM (đùn nhựa nóng chảy theo lớp). Một mô hình in 3D được phải thoả các tiêu chí hình học:
**kín nước** (watertight), **manifold** (mỗi cạnh chỉ thuộc tối đa 2 mặt), **hướng pháp tuyến đúng**,
**không tự cắt nhau**; cùng các giới hạn máy in: kích thước tối đa, độ dày thành tối thiểu, độ phân
giải, và trọng lực. Chương minh hoạ toàn bộ quy trình qua ví dụ dựng một chiếc bình hoa in 3D (dùng
Series+Scale+Graph Mapper tạo hình, Rail Revolution bo cạnh mượt, Box Morph biến dạng, Catmull-Clark
làm mượt, Mesh Thicken tạo độ dày thành, xuất file STL). Với vật thể trung/lớn, kỹ thuật **cắt lát**
(sectioning) và **waffling** (cắt lát 2 phương vuông góc) dùng để dựng hình từ tấm phẳng ghép lại. Kết
chương là case study **NU:S** (lắp đặt nghệ thuật + giày in 3D của Tedeschi & Degni) và chiến lược cho
công trình quy mô lớn (panel phẳng lục giác P-Hex Mesh, máy in bê tông cỡ lớn D-Shape của Enrico Dini).

## Essay — Over the Material, Past the Digital: Back to Cities (Stefano Andreani, Harvard GSD)

Bài luận nêu 3 "thời đại kỹ thuật" của kiến trúc: thủ công, cơ khí hoá, và kỹ thuật số (theo Mario
Carpo) — kỷ nguyên số cho phép sản xuất hàng loạt các biến thể khác nhau (mass-customization) với chi
phí tương đương hàng loạt giống hệt nhau. Tác giả giới thiệu các dự án nghiên cứu của nhóm Design
Robotics Group tại Harvard GSD (gạch gốm in robot "[R]evolving Brick", mái vỏ gốm "Floating Ceramic
Shell", đúc bằng robot) kết hợp thiết kế tham số với chế tạo bằng robot để tối ưu hiệu năng vật liệu
và năng lượng.

## Essay — (Digital) Form-finding (Alberto Pugnale)

Bài luận tổng kết lịch sử **form-finding vật lý**: phương pháp dây treo lộn ngược (catenary) của Hooke
để tìm hình vòm chịu nén, mô hình dây của Gaudí (nhà thờ Colonia Güell), lưới dây thép của Frei Otto
(Multihalle Mannheim), màng vải ướt của Heinz Isler, và màng xà phòng tạo "mặt cực tiểu" (minimal
surface). Tác giả sau đó đối chiếu với **tối ưu hoá số** hiện đại — khác biệt cốt lõi là tô-pô công
trình không còn cố định mà chính là đối tượng được tối ưu (ví dụ ga TAV Florence của Isozaki/Sasaki),
và khái niệm "form-improvement" (cải thiện hình có sẵn) thay vì chỉ "tìm hình tối ưu" thuần tuý.

## Chương 9 — Digital Simulation: Particle-Spring Systems (Kangaroo)

Chương dạy mô phỏng vật lý bằng hệ **particle-spring** (hạt-lò xo): các **hạt** (particle, có khối
lượng, di chuyển được), nối nhau bằng **lò xo đàn hồi** (spring, tuân theo định luật Hooke: lực = độ
cứng × độ giãn), chịu tác dụng của **lực** (force) và bị giữ cố định tại các **điểm neo** (anchor
point). Hệ chạy lặp cho tới khi đạt trạng thái cân bằng — mô phỏng đúng cách dây/vải/lưới biến dạng
dưới trọng lực thật. Plugin **Kangaroo** (Daniel Piker) tích hợp việc này vào Grasshopper qua quy
trình: rời rạc hoá hình NURBS thành đường thẳng/mesh (dùng Weaverbird) → biến đường thành lò xo, điểm
thành hạt → gắn vào "Kangaroo Engine" cùng lực và điểm neo → bật/tắt mô phỏng bằng Boolean Toggle.
Chương minh hoạ qua ví dụ **cáp treo** (cable, dùng Divide Curve+Shatter+Springs From Line+Unary
Force), giải thích chi tiết các thông số lò xo (Stiffness - độ cứng, Damping - độ cản, Rest Length -
chiều dài nghỉ có thể nhỏ/lớn/bằng chiều dài ban đầu để mô phỏng vật liệu căng/chùng khác nhau), ví dụ
**đường catenary** chính xác (dùng cung tròn ban đầu, Rest Length gần bằng chiều dài thật để mô phỏng
dây không giãn), mô phỏng **màng/vải** (mesh làm khung lò xo, có thể neo ở góc hoặc theo cạnh, thêm
đường chéo để cứng hơn), và hành vi **vỏ cứng** (Shell component chống bẹp khi mô phỏng vật liệu có
khả năng chịu uốn như thép).

## Essay — Form as Unknown (Lawrence Friesen & Lorenzo Vianello, AA Rome Visiting School)

Bài luận trình bày phương pháp luận của các workshop "Form as Unknown" tại AA Rome: xem **vật liệu là
thông tin tính toán** (material as information), noi theo cách Gaudí, Otto, Musmeci tìm hình từ hành
vi vật liệu thay vì vẽ hình trước. Quy trình gồm 3 bước: **Unmaking** (giải mã hiện tượng vật liệu),
**Making** (viết code mô phỏng lại lực đó), **Synthesis** (biến quan sát thành tham số thiết kế) —
minh hoạ qua case study cầu Basento (Sergio Musmeci) được xem như một mặt căng tìm trạng thái cân bằng.

## Chương 10 — Evolutive Structures: Topology Optimization

Chương phân biệt 2 kiểu tối ưu kết cấu: **tối ưu hình dạng** (shape optimization — chỉ chỉnh kích
thước/tiết diện, giữ nguyên tô-pô) và **tối ưu tô-pô** (topology optimization — cho phép thay đổi cả
cấu trúc liên kết, loại bỏ vùng thừa). Ví dụ tối ưu hình dạng: chọn tiết diện thép tối ưu cho dầm công-
xôn bằng plugin **Karamba** (phân tích phần tử hữu hạn - FEA) kết hợp bộ giải di truyền **Galapagos**
để dò trong danh sách tiết diện có sẵn. Phần tô-pô học giải thích khái niệm "genus" (số lỗ trên một
hình) quyết định 2 hình có biến đổi liên tục thành nhau được không. Thuật toán tối ưu tô-pô chính là
**ESO** (Evolutionary Structural Optimization, Xie & Steven 1992) — loại bỏ dần vật liệu chịu ứng suất
thấp theo "Tỷ lệ loại bỏ" (Rejection Ratio) dựa trên ứng suất Von Mises; và **XESO** (bản mở rộng của
Sasaki, lấy cảm hứng từ cây đa - Banyan Tree) cho phép vừa thêm vừa bớt vật liệu hai chiều, dùng
đường đồng mức ứng suất. Các công trình thực tế minh hoạ: toà nhà văn phòng Akutagawa, ga tàu TAV
Florence (Isozaki/Sasaki), Trung tâm hội nghị Quốc gia Qatar, và mẫu in 3D "Radiolaria". Phần thực
hành dùng plugin **Millipede** để tối ưu dầm Michell Truss, dầm MBB 2D và cầu 3D theo quy trình 4 bước
(định nghĩa không gian thiết kế/điều kiện biên → dựng mô hình phần tử hữu hạn → tối ưu tô-pô → trực
quan hoá kết quả). Cuối chương giới thiệu 2 loại bộ giải tối ưu tổng quát: **bộ giải chính xác** (như
plugin Goat, tìm nghiệm tối ưu duy nhất) và **bộ giải tiến hoá** (như Galapagos, dò nghiệm gần đúng
qua nhiều thế hệ) — minh hoạ bằng bài toán tìm đường ngắn nhất (geodesic) trên một mặt cong.

## Chương 11 — Environmental Analysis (Phân tích môi trường)

Chương giới thiệu plugin **GECO** ([uto] — Ursula Frick & Thomas Grabner) làm cầu nối giữa Grasshopper
và phần mềm phân tích môi trường **Autodesk Ecotect**, cho phép xuất hình học sang Ecotect tính toán
rồi nhập kết quả ngược lại để điều khiển hình học theo thời gian thực. Các nhóm lệnh GECO: liên kết &
xuất dữ liệu (EcoLink, EcoMeshExport), lưới phân tích (điểm "cảm biến" ảo trong không gian — FitGrid,
2dAnalysisGrid), tính toán (đường mặt trời EcoSunPath/EcoSunRays, bức xạ mặt trời EcoSolCal, ánh sáng
EcoLightCal), và nhập kết quả về (EcoObjectRequest, EcoGridRequest). Dữ liệu khí hậu theo vị trí địa
lý được lưu trong **Weather File** (định dạng .WEA, có thể chuyển đổi từ file .EPW). Chương minh hoạ
qua ví dụ **mặt tiền phản hồi** (responsive skin): so sánh góc giữa tia nắng và pháp tuyến mỗi ô mặt
tiền để tự động co giãn lỗ mở — góc càng nhỏ (nắng chiếu thẳng) thì lỗ càng nhỏ lại. Mục **phân tích
bức xạ** (insolation, dùng định luật cosine của Lambert) minh hoạ qua bài tập đặt tấm pin mặt trời tối
ưu; mục **kiểm soát ánh sáng** (Daylight Factor, mức chiếu sáng...) minh hoạ qua phân tích thị giác một
căn phòng và bài tập kết hợp Galapagos + GECO để tối ưu hình dạng tấm che nắng.

## Afterword — Post Digital Strategies (Brian Vesely)

Bài kết luận giới thiệu **tĩnh học đồ hoạ** (graphical statics) như một cách tìm hình thay thế Kangaroo
— dùng vector lực vẽ tay/thuật toán để suy ra hình vòm chịu nén tối ưu (ví dụ minh hoạ qua 13 sơ đồ
từng bước cho một vòm catenary đảo ngược), rồi dùng bộ giải Goat để tối thiểu hoá lực dọc trục và từ
đó tính bề dày vòm. Tác giả nhấn mạnh thông điệp xuyên suốt cuốn sách: Grasshopper và thuật toán nói
chung chỉ là **công cụ tổ chức dữ liệu** — chính người dùng mới quyết định ý nghĩa và giá trị của kết
quả đầu ra, các ví dụ trong sách nên được xem như cách hiểu tư duy tổ chức dữ liệu chứ không phải bài
tập hình thức để làm theo y hệt.

## Phụ lục — I am City, we are City (Francesco Lipari)

Bài luận ngắn suy ngẫm về tương lai đô thị trong bối cảnh công nghệ phát triển nhanh hơn khả năng
thích nghi của con người, dự đoán các thành phố sẽ trở thành "nút" trong một hệ thống đô thị toàn cầu
liên kết bằng dữ liệu, không còn ranh giới địa lý rõ ràng như trước.

## Phụ lục — Parametric Urbanism: a New Frontier for Smart Cities

Bài luận (Fusero, Massimiano, Tedeschi, Lepidi và phần bổ sung của Andrea Galli) đề xuất dùng phần
mềm tham số không chỉ để vẽ 3D đô thị mà làm công cụ hỗ trợ ra quyết định quy hoạch — chuyển từ mô
hình "phản ứng" (reactive) dựa trên bản vẽ tĩnh sang mô hình "chủ động" (proactive) cập nhật liên tục
theo dữ liệu thật (cảm biến, dữ liệu mở). Phần kỹ thuật giới thiệu cách nhập dữ liệu bản đồ
OpenStreetMap vào Grasshopper qua plugin Elk (kèm Finches/gHowl cho shapefile), và khung quy trình
5 bước của Anas Alfaris (MIT) — decomposition, formulation, modeling, integration, exploration — để
tổ chức một dự án quy hoạch phức tạp thành các cụm thuật toán liên kết với nhau.

## Phụ lục — Playful Computation (Arthur Mamou-Mani)

Bài luận giới thiệu 5 dự án thực tế đã dùng Grasshopper: (1) cây gấp origami RIBA Windows (Thượng
Hải) — dùng Galapagos tối ưu kích thước panel cho vừa khổ máy cắt laser; (2) váy vải "Magic Garden" —
dùng Kangaroo mô phỏng lực bản lề (hinge) và lò xo để tạo nếp gấp vải; (3) "Shipwreck" và "Fractal
Cult" tại lễ hội Burning Man — dùng HoopSnake tạo hình fractal Koch snowflake đệ quy; (4) mái nhà
Eco-Resort — kết hợp HoopSnake với dữ liệu góc nắng từ GECO/Ecotect để mái tự điều chỉnh theo mùa;
(5) mái vòm sinh thái Chester Zoo — dùng đường trắc địa (geodesic) tạo lưới gridshell dày hơn ở vùng
trũng, mỏng hơn ở đỉnh. Tác giả nhấn mạnh Grasshopper không chỉ tăng tốc quy trình thiết kế mà còn mở
ra cách tư duy mới, kết nối kiến trúc sư với nhiều lĩnh vực khác (kỹ thuật, chế tạo, vật lý).

## Phụ lục — The CloudBridge

Đoạn trích ngắn từ tạp chí WIRED giới thiệu khái niệm cây cầu "CloudBridge" của Arturo Tedeschi và
Maurizio Degni — một cấu trúc dạng lưới mềm mại nối hai sườn núi, thiết kế bằng thuật toán để vừa ổn
định về kết cấu vừa hoà vào cảnh quan tự nhiên, minh hoạ tinh thần "dùng thiết kế tham số để phá vỡ
giới hạn hình thức truyền thống" của toàn cuốn sách.

## Tài liệu tham khảo / Phụ lục

Sách kết thúc bằng danh mục tài liệu tham khảo chia theo chủ đề: Lý thuyết thiết kế tham số, Thuật
toán, Chế tạo số, Form-finding, Lập trình/Scripting, Hình học kiến trúc, Toán học, và các sách chuyên
khảo (monograph) về Zaha Hadid, Frank Gehry, Sergio Musmeci... Cuối sách có **danh sách QR code đã giải
mã** (Decoded QR list) — 8 mã QR trong sách gốc dẫn tới ảnh phóng to của các sơ đồ thuật toán phức tạp
(chương 5, 7, 8, 9, 10, 11), được liệt kê lại dưới dạng đường link trực tiếp để người đọc bản số có
thể xem không cần quét mã.
