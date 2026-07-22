# Chương 9 — Digital Simulation: Particle-Spring Systems (Mô phỏng số — hệ hạt-lò xo)

Chương giới thiệu plug-in **Kangaroo** — công cụ mô phỏng vật lý (particle-spring system) tích hợp trong Grasshopper, dùng cho **form-finding** (tìm hình dạng): thay vì vẽ hình rồi kiểm tra kết cấu, để chính vật lý "tìm ra" hình dạng chịu lực tối ưu.

## Mở đầu: Form-finding và Particle-Spring System

Kết cấu chịu lực bằng nén/kéo dọc trục (axial) chịu tải tốt hơn với tiết diện nhỏ hơn kết cấu chịu uốn. Các kỹ thuật form-finding truyền thống (mô hình vật lý phức tạp, mạng lưới dây treo/hanging chain, vải căng, màng xà phòng) rất khó và tốn thời gian — nên ít nhà thiết kế khai thác được tiềm năng này trước đây. Ngày nay các kỹ thuật đó có thể mô phỏng số bằng **particle-spring system** — mô phỏng hành vi vật lý của vật thể biến dạng được, vốn phát triển ban đầu cho hoạt hình nhân vật và mô phỏng vải. Mô phỏng số cho phép nghiên cứu hình dạng theo thời gian thực, cập nhật lực/gối đỡ/tính chất vật lý linh hoạt.

**Particle-spring system** là phép rời rạc hoá (discretization) 1 mô hình liên tục thành số hữu hạn khối lượng (gọi là **particle** — hạt) nối với nhau bằng lò xo đàn hồi hoàn hảo. 4 thành phần chính:
- **Particles (hạt)**: khối lượng tập trung, thay đổi vị trí/vận tốc khi mô phỏng tiến triển.
- **Springs (lò xo)**: liên kết đàn hồi tuyến tính giữa 2 hạt, tuân theo **định luật Hooke** — mỗi lò xo có 1 độ dài nghỉ ban đầu (resting length) và 1 độ cứng (stiffness, k).
- **Forces (lực)**: trọng lượng/tải trọng ngoài, mô phỏng bằng vector, chỉ áp lên hạt.
- **Anchor Points (điểm neo)**: hạt không đổi vị trí trong suốt mô phỏng.

Khi mô phỏng chạy, hạt di chuyển từ vị trí ban đầu tới khi đạt **trạng thái cân bằng (equilibrium)** — phụ thuộc hình học ban đầu, vector lực, và tính chất lò xo. Theo định luật Hooke, k càng nhỏ thì lò xo giãn càng nhiều. Vì hạt hoạt động như khớp cầu (spherical hinge) **không chịu được moment**, lời giải cân bằng chỉ truyền tải trọng qua lực dọc trục thuần tuý — đây chính là điều kiện lý tưởng cho form-finding kết cấu chịu nén/kéo.

## 9.1 Kangaroo plug-in

Phép tính lặp (iterative) của particle-spring system tiến dần tới trạng thái cân bằng (tổng mọi lực = 0), thực hiện bởi 1 **solver toán học** — mỗi bước lặp tinh chỉnh vị trí/vận tốc hạt từ bước trước, tương tự hoạt hình key-frame, tạo ảo giác chuyển động khi các khung hình được tính liên tục. Có nhiều phần mềm particle-spring khác nhau (vd CADenary của Axel Kilian, Dan Chak, Megan Galbraith, 2002), nhưng đa số là phần mềm độc lập, không tích hợp CAD, khó làm chủ.

**Kangaroo** — engine particle-spring system dựa trên vật lý, phát triển bởi Daniel Piker (cùng nhóm Robert Cervellione, Giulio Piacentino) — dễ dùng, hướng tới người thiết kế, tích hợp thẳng dưới dạng plug-in Grasshopper (tab **Kangaroo** xuất hiện sau khi cài). Daniel Piker là nhà nghiên cứu tiên phong về ứng dụng tính toán trong thiết kế hình dạng/kết cấu phức tạp, từng làm việc tại Advanced Geometry Unit của Arup và Specialist Modelling Group của Foster+Partners.

Kangaroo cho phép tương tác với hình dạng theo 2 cách:
- **Direct Interaction (tương tác trực tiếp)**: thao tác trực tiếp điểm neo, lực, tính chất lò xo.
- **Parametric/Associative Interaction (tương tác tham số)**: điểm neo/lực/tính chất lò xo được liên kết tham số với các phần khác của mô hình — vd điểm neo là điểm cuối của 1 tập đường thẳng mà vị trí lại do 1 phần khác của thuật toán quyết định.

## 9.2 Kangaroo workflow (Quy trình làm việc Kangaroo)

Quy trình chung áp dụng cho cả mô hình đơn giản (1 dây/chain) lẫn mô hình phức tạp nhiều node (màng đa gối đỡ):

1. **Discretization (rời rạc hoá)**: Kangaroo **không xử lý được NURBS curve/surface trực tiếp** — phải chuyển NURBS-curve thành đoạn thẳng (line), NURBS-surface thành mesh (điểm+cạnh) trước. Các component rời rạc hoá chính nằm trong panel **Extract** của Weaverbird, ngoài ra còn có component hữu ích trong các tab chuẩn của Grasshopper hoặc tab Kangaroo.
2. **Particle-spring system**: sau khi rời rạc hoá, chuyển đoạn thẳng thành lò xo và điểm thành hạt bằng component chuyên dụng trong toolbar Kangaroo; áp vector lực lên hạt; khai báo điểm neo.
3. **Kangaroo Engine**: nối đầy đủ hạt, lò xo, lực, điểm neo vào đúng input tương ứng của Kangaroo Engine; dùng **Boolean Toggle** (Params > Input) bật/tắt (True/False) để chạy/dừng mô phỏng. Trong lúc mô phỏng chạy, hạt di chuyển tới khi đạt cân bằng — nên output của engine mang tính **động (dynamic)**.

## 9.3 Cable simulation (Mô phỏng dây cáp)

Ví dụ đầu tiên: mô phỏng 1 dây cáp đàn hồi mềm treo giữa 2 đầu, chịu tải trọng bản thân. Bước đầu: set 1 đường thẳng ngang từ Rhino qua Curve container.

- **Discretization**: chia đường bằng **Divide Curve** (input N = số đoạn chia — chia càng nhiều điểm, biến dạng cuối càng mượt/chi tiết) rồi tách thành các đoạn riêng bằng **Shatter** (Curve > Division). Các điểm chia từ Divide Curve chính là các hạt (nơi áp lực/ràng buộc).
- **Particle-spring system**: các đoạn thẳng từ Shatter chuyển thành lò xo bằng **Springs From Line** (Kangaroo > Forces) — nối cả input Connection và Rest Length vào cùng 1 nguồn line (qua container "Line" — container này hữu ích để phát hiện nếu lỡ nối nhầm dữ liệu không phải line, component sẽ báo đỏ vì Springs From Line chỉ nhận đúng line-geometry). Các điểm chia (P-output của Divide Curve) nối vào **Unary Force** (Kangaroo > Forces) — áp 1 vector lực lên mọi hạt, vd hướng z âm độ lớn 10 (có thể chỉnh hướng bất kỳ). Điểm neo = 2 đầu của curve gốc.
- **Kangaroo Engine (KangarooPhysics, Kangaroo > Kangaroo)**: input Force objects nhận cả output của Springs From Line lẫn Unary Force (đặt chế độ **flatten**); input AnchorPoints nhận 2 điểm đầu curve; input Geometry nhận output Shatter để hiển thị mô phỏng trực quan. Dùng Boolean Toggle + **Timer** (Params > Util) để chạy/dừng — Toggle=False khởi động mô phỏng, True dừng; Timer định số khung hình/giây (vd right-click Timer, đặt Interval=5ms). Double-click vào KangarooPhysics component cũng mở được 1 panel điều khiển nhanh (stop/play/pause).

Khi chạy, hạt di chuyển theo hướng lực, bị ràng buộc bởi tính chất đàn hồi tuyến tính của lò xo — dây cáp thay đổi hình dạng nhiều lần tới khi đạt trạng thái cân bằng (đường polyline tối màu ở khung cuối). Nếu chỉnh lại hình học gốc/quy trình rời rạc hoá, phải **reset và chạy lại mô phỏng** để thấy ảnh hưởng — nhưng các tham số khác (hướng/độ lớn Unary Force, vị trí điểm neo) **có thể chỉnh ngay trong lúc mô phỏng đang chạy**.

Có thể set điểm neo thủ công từ Rhino thay vì tính bằng End Points, và **di chuyển tay điểm neo ngay trong lúc mô phỏng chạy** — dây sẽ phản ứng như trong thế giới thật. Lưu ý: nếu tương tác thủ công mà không trả điểm neo về đúng vị trí ban đầu trước khi dừng và chạy mô phỏng mới, engine vật lý sẽ "không hiểu" đúng cách ràng buộc mô hình — dễ gây lỗi. Có thể thêm điểm neo mới (set từ Rhino hoặc tính trong Grasshopper) nhưng **điểm neo luôn phải trùng đúng vị trí 1 hạt** — vd đặt điểm neo giữa 1 lò xo (không trùng hạt nào) sẽ không có tác dụng gì.

### 9.3.1 Strategy: continuity (Chiến lược: tính liên tục)
Input/output của Kangaroo luôn là điểm, line, hoặc mesh — không có curve mượt. Muốn dựng lại 1 dây cáp mượt, nối output ParticlesOut vào input V của **NURBS Curve** để nội suy 1 curve liên tục qua các hạt. Lưu ý: cách này **có thể cho kết quả sai về mặt vật lý** — vì NURBS-curve tạo ra "cứng nhắc" quanh mỗi điểm điều khiển, trong khi thực tế hạt hoạt động như khớp cầu không có khả năng chịu moment (không "cứng" ở bất kỳ điểm nào).

## 9.4 Elastic behavior: Hooke's law (Hành vi đàn hồi: Định luật Hooke)

Khi dây đạt cân bằng dưới tác dụng ngoại lực (chống lại bởi độ đàn hồi lò xo), chiều dài mỗi đoạn **tăng lên**. Ví dụ minh hoạ: dây gốc dài 10 đơn vị, chia 5 đoạn 2 đơn vị mỗi đoạn, áp 6 lực Unary Force độ lớn -20 theo Unit Z — kết quả cuối dài 10.46 đơn vị (biến dạng 0.46). Biến dạng **không chia đều** cho mọi đoạn — các lò xo gần điểm neo (phản lực) giãn nhiều hơn vì chúng "gánh" trọng lượng của các lò xo khác.

**Định luật Hooke**: độ dịch chuyển (biến dạng) của 1 vật (coi như lò xo) tỉ lệ thuận trực tiếp với lực tác dụng — khi bỏ tải, vật trở lại hình dạng/kích thước gốc. Công thức: **F = k × x**, trong đó F = lực tác dụng (Newton, N), k = độ cứng (Stiffness, hằng số dương phụ thuộc vật liệu và tiết diện, đơn vị N/cm), x = độ thay đổi chiều dài (biến dạng, cm). Định luật Hooke được nhúng sẵn trong component **Springs From Line**.

Ví dụ minh hoạ tính tay: dây neo dài gốc 80cm, độ cứng k=2 N/cm, chịu tải trọng 100N → biến dạng x = F/k = 100/2 = 50cm. Nếu bỏ tải, dây trở lại đúng 80cm ban đầu — độ dài dây đạt được khi bỏ tải gọi là **Rest Length (chiều dài nghỉ)**, không phải lúc nào cũng trùng chiều dài ban đầu (giải thích chi tiết bên dưới). Thời gian đạt cân bằng phụ thuộc cả Stiffness lẫn **Damping Constant** (hằng số cản, liên quan ma sát/lực cản) — Damping càng lớn thì tốc độ biến dạng càng chậm, nhưng **không ảnh hưởng tới độ lớn biến dạng cuối cùng**, chỉ ảnh hưởng tốc độ đạt tới đó.

Các thuộc tính của **Springs From Line** (Kangaroo > Forces):
- **Connection**: nhận input là line (bắt buộc; loại hình học khác cho kết quả null). Chiều dài ban đầu của mỗi line gọi là **Start Length**.
- **Stiffness**: giá trị k theo Hooke — k càng cao thì biến dạng càng nhỏ, xác định bởi vật liệu và tiết diện lò xo.
- **Damping**: ảnh hưởng tốc độ biến dạng, không ảnh hưởng độ lớn biến dạng cuối. Mặc định = 10.
- **Rest Length**: chiều dài lò xo "muốn" đạt tới khi bỏ tải — quan trọng để mô phỏng hành vi vật liệu khác nhau. 3 trường hợp:
  1. **Rest Length = Start Length**: mô phỏng hành vi đàn hồi hoàn hảo thuần tuý — nối trực tiếp chính line (Lines) vào input Rest Length. Đây là cách tất cả ví dụ trước đó trong chương dùng.
  2. **Rest Length < Start Length**: mô phỏng hiệu ứng "căng trước" (pre-tensioning) làm ngắn lò xo lại — mô phỏng vật liệu chịu kéo có xu hướng tự co ngắn/thu nhỏ diện tích. Thực hiện bằng cách đo chiều dài ban đầu (component **Length**) rồi nhân với 1 hệ số **Rest Length Factor** trong khoảng 0–1.
  3. **Rest Length > Start Length**: mô phỏng hiện tượng lò xo "chùng/giãn dài ra" — cũng dùng Length nhân với Rest Length Factor, lần này trong khoảng 1 đến N.
- **Upper/Lower cutoff**: giới hạn hoạt động của lò xo, trên/dưới ngưỡng nào đó — mặc định cả 2 đều = 0.
- **Plasticity**: độ biến dạng đàn hồi tối đa so với Rest Length.

## 9.5 Catenary simulation (Mô phỏng đường dây chuyền / catenary)

**Catenary (đường dây chuyền)** — hình dạng của 1 dây/xích hoàn toàn mềm dẻo, mật độ đều, không co giãn, treo giữa 2 điểm đầu. Phương trình: **y = a·cosh(x/a)**, trong đó a là khoảng cách từ trục x tới điểm trên curve có tiếp tuyến độ dốc = 0 (đáy đường cong). Có thể dựng curve này trực tiếp qua **Evaluate F(X)** (với a=2 trong ví dụ sách), hoặc dùng thẳng component có sẵn **Catenary** (Curve > Spline) — nhúng sẵn công thức trên, input: điểm đầu A, điểm cuối B, chiều dài L, hướng trọng lực G.

Catenary cũng mô phỏng được bằng particle-spring, nhưng phải đáp ứng đủ **4 điều kiện định nghĩa**: (1) treo tại 2 đầu; (2) hoàn toàn mềm dẻo; (3) mật độ đều; (4) **không co giãn (inextensible)**. Mô phỏng dây thẳng biến dạng ở mục 9.3 **không đáp ứng đủ điều kiện 4** — dù đặt Stiffness rất cao, lò xo vẫn không hoàn toàn "không co giãn" — nên kết quả hơi khác catenary thật.

Cách khắc phục để xấp xỉ catenary chính xác hơn: dùng 1 **cung tròn (arc)** làm hình học khởi tạo (dựng bằng **Arc 3Pt** qua 3 điểm A, B, C), với chiều dài cung đặt bằng đúng chiều dài catenary mong muốn (vd 20 đơn vị). Quy trình:
- **Initial geometry**: cung dài 20 đơn vị qua 3 điểm.
- **Discretization**: chia cung bằng Divide Curve (N=50 → 51 điểm cách đều), nối polyline qua các điểm, tách đoạn bằng Shatter (ra 50 line, mỗi đoạn dài 20/50=0.4 đơn vị).
- **Particle-spring system**: chuyển đoạn thành lò xo qua Springs From Line (qua Line container trung gian). Để mô phỏng tính "không co giãn": đặt Rest Length **nhỏ hơn** Start Length bằng hệ số nhân 0.995, kèm Stiffness rất cao (7000) — ép lò xo gần như cứng tuyệt đối. Áp trọng lực bằng Unary Force (hướng Z, độ lớn -1) lên mọi hạt, nối vào Force objects của Kangaroo. Merge 2 điểm neo A, B nối vào AnchorPoints.

Khi chạy mô phỏng, cung phân đoạn di chuyển theo hướng Z âm, dần mang đúng hình dạng catenary — chiều dài mỗi đoạn gần như không đổi so với 0.4 đơn vị ban đầu (chứng tỏ điều kiện "không co giãn" được đáp ứng gần đúng). Sách lưu ý về độ chính xác vật lý: giá trị Unary Force (đại diện trọng lượng bản thân) trước đó chỉ đặt tuỳ ý — chính xác hơn nên tính bằng cách **chia tổng trọng lượng dây cho số hạt** — vd catenary nặng 10N chia cho 51 hạt → mỗi vector lực = 10/51 = 0.196N. Sách minh hoạ thêm ví dụ mở rộng: 1 tập catenary có điểm đầu nằm trên 2 khung freeform.

## 9.6 Membrane simulation (Mô phỏng màng căng)

Mô phỏng màng/vải cần 1 **lưới lò xo** (grid of springs). Cách phổ biến: chuyển NURBS surface thành mesh, tách cạnh/đỉnh làm lò xo/hạt.

- **Discretization**: chuyển surface từ Rhino sang mesh bằng **Mesh Surface**, tách cạnh bằng **wbEdges** và đỉnh bằng **wbVertices** (Weaverbird > Extract).
- **Particle-spring system**: cạnh nối vào Connection-input của Springs From Line; Rest Length đặt là bội số của Start Length qua slider để linh hoạt điều chỉnh độ căng. Đỉnh (P-output của wbVertices) nối Unary Force (vd -20 theo Z). 4 góc mesh tách riêng bằng **MeshCorners** (Kangaroo > Utility) nối vào AnchorPoints.
- **Kangaroo Engine**: Force objects nhận cả Springs lẫn Unary Force (flatten); Geometry nhận output wbEdges (L) để hiện dạng khung dây, hoặc nối trực tiếp output (M) của Mesh Surface vào Geometry để hiện dạng mặt (mesh face) thay vì chỉ khung dây.

Tương tự dây cáp, điểm neo màng cũng chỉnh tay được từ Rhino trong lúc mô phỏng chạy (cùng lưu ý phải trả về đúng vị trí gốc trước khi reset). Màng có thể neo tại nhiều điểm bất kỳ (miễn trùng vị trí hạt), hoặc neo dọc theo **cạnh biên** bằng cách lấy các đỉnh biên hở (naked edge) qua component **Naked Vertices** (Kangaroo > Utility — trích đỉnh không có mặt bao quanh 1 phía).

Đặt **Rest Length Factor = 0** làm màng có xu hướng **tối thiểu hoá diện tích** — mô phỏng đúng hành vi màng xà phòng căng (tensioned-film, xem lại minimal surface ở 3.8.3). Mô hình lưới lò xo cơ bản (chỉ có cạnh, không đường chéo) hoạt động giống 1 **lưới dây (cable net)** hơn là màng vật liệu cứng thật — muốn mô phỏng vật liệu tấm cứng hơn (không biến dạng thành hình thoi), cần thêm **đường chéo** vào mỗi ô lưới mesh, dùng 2 component Springs From Line riêng biệt cho cạnh và đường chéo (để kiểm soát độc lập). Khi đó cấu hình mô phỏng không còn giống cable-net mà giống vật liệu tấm thật — nếu giảm Rest Length Factor sẽ tạo nếp gấp kiểu origami. Có thể thử nhiều cấu hình đường chéo khác nhau (1 đường chéo/ô cho hành vi bất đối xứng bằng cách đặt Rest Length khác nhau cho cạnh/chéo), hoặc dùng component **WarpWeft** (Kangaroo > Mesh) tách cạnh mesh theo 2 hướng dệt (warp/weft) riêng biệt.

### 9.5.1 [đánh số theo bản in gốc — thực chất 9.6.1] Practical Exercise: multi-supported membrane
Sách dẫn ví dụ thực tế: **Bach Chamber Music Hall** của Zaha Hadid Architects (Manchester, UK, 2009) — 1 dải vải căng liên tục cuộn quanh bao bọc cả nghệ sĩ và khán giả. Bài tập thực hành (chi tiết đầy đủ dẫn qua mã QR, không có trong text): thay vì nghiên cứu toàn bộ dải vải, trích 1 mặt cắt đơn giản hoá — mô hình nghiên cứu hành vi của 1 màng căng trên khung đỡ dạng giàn gồm 2 dầm ngang tự do (free-form) và 11 dầm đứng dạng cung có tiết diện biến đổi.

## 9.7 Shell behavior (Hành vi vỏ mỏng — Shell)

Vì hạt hoạt động như khớp cầu không chịu moment, 1 mô hình rời rạc thuần tuý **không thể tự đứng cứng** nếu không có ràng buộc bổ sung. Ví dụ: 1 mesh-sphere (khối cầu mesh) mô phỏng rơi theo hướng Z âm dưới trọng lực sẽ **bị "nhàu" (crumple)** khi chạm sàn (mặt phẳng XY) — dù đã gia cường bằng đường chéo mesh và Stiffness cao. Để tránh nhàu, dùng component **Shell** (Kangaroo > Utility).

Quy trình ví dụ mesh-sphere:
- **Discretization**: tách cạnh/đỉnh từ 1 mesh-sphere set từ Rhino. Điểm (hạt) nối Unary Force; đường chéo mỗi mặt định nghĩa bằng cách nối các đỉnh đối diện nhau, dùng **Mesh Explode** và **Deconstruct Mesh**.
- **Particle-spring system**: gộp cạnh + đường chéo bằng Merge thành 1 list. Vì mesh-sphere có mặt tam giác quanh 2 cực, cạnh và đường chéo có thể **trùng nhau (overlap)** — gây sai lệch mô phỏng nếu không xử lý. Dùng **removeDuplicateLines** (Kangaroo > Utility) loại bỏ các line trùng nhau trong 1 dung sai (tolerance) cho trước. Output Q nối vào cả Connection-input lẫn Rest Length-input của Springs (Stiffness đặt 5000). Cuối cùng, component **Shell** nhận mesh input, trả về 1 "shell force" (lực vỏ) với 2 tham số: **Strength** (độ lớn lực, vd 500) và **AngleFactor** (hệ số góc, vd 1) — lực này chống lại xu hướng nhàu, mô phỏng độ cứng chống uốn (bending resistance) như thật.

Component Shell hữu ích khi mô phỏng vật liệu có khả năng **chống uốn** (bending resistance) như tấm thép hoặc cao su — khác với lưới lò xo/màng thuần tuý (chỉ chịu kéo/nén dọc trục, không chống uốn được).
