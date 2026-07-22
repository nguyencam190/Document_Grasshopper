# Chương 3 — Control: Curves and Surfaces in Grasshopper (Kiểm soát đường cong và mặt cong)

Chương dài nhất và nặng lý thuyết nhất trong 11 chương: giải thích bản chất toán học của NURBS (đường/mặt cong dùng trong Rhino-Grasshopper), cách "định vị" điểm trên đường/mặt bằng hệ toạ độ cục bộ (Local Coordinate System), các cách dựng surface, phân tích độ cong (curvature), và loạt ví dụ ứng dụng (diagrid, space frame, lưới Chebyshev, pattern theo độ cong).

## 3.1 NURBS curves

NURBS (Non-Uniform Rational B-Splines) là cách biểu diễn toán học cho hình học 3D, mô tả được từ đường thẳng/vòng tròn đơn giản đến mặt cong tự do phức tạp nhất. Một đường NURBS được xác định bởi 4 yếu tố:
- **Degree (bậc)**: số nguyên dương. Đường thẳng/polyline có degree 1, vòng tròn NURBS có degree 2, đa số curve tự do có degree 3 hoặc 5. Giá trị degree+1 gọi là **order**.
- **Control points (điểm điều khiển)**: vị trí và **weight** (trọng số) của các điểm này quyết định hình dạng đường cong — weight >1 "hút" đường cong lại gần điểm đó, weight trong khoảng 0–1 "đẩy" đường cong ra xa. Số điểm điều khiển không được nhỏ hơn order.
- **Knots (nút)**: danh sách gồm (degree + số điểm điều khiển − 1) con số, kiểm soát độ mượt của đường cong.
- **Evaluation rule (công thức tính)**: công thức nhận degree, control points, knots làm input, trả ra vị trí 1 điểm trên đường.

Sách minh hoạ: đường NURBS với 7 điểm điều khiển, degree khác nhau cho hình dạng khác nhau — degree=1 trùng với chính đa giác nối các điểm điều khiển (control-polygon). Weight điểm điều khiển >1 kéo đường cong lại gần, weight trong (0,1) đẩy đường cong ra xa.

## 3.2 Parametric representation of a curve (Biểu diễn tham số của đường cong)

Trong Rhino, mỗi điểm trên NURBS curve có toạ độ (x,y,z) theo **World Coordinate System (WCS)** — hệ toạ độ chung toàn không gian. Nhưng còn 1 cách khác để định vị điểm: biểu diễn tham số, dùng 1 biến số **t** chạy từ 0 đến 1 — t=0 là điểm đầu curve, t=1 là điểm cuối, t trong khoảng (0,1) mô tả toàn bộ đường. Đây gọi là **Local Coordinate System (LCS)** — hệ toạ độ "gắn lên" chính đường cong, chỉ cần 1 con số (t) để xác định 1 điểm thay vì 3 toạ độ.

Lưu ý quan trọng: **t không đo khoảng cách/chiều dài**. Có thể hình dung t như "thời gian" 1 hạt chuyển động từ t=0 đến vị trí P(t) — tốc độ hạt này phụ thuộc mật độ điểm điều khiển, hạt sẽ "chậm lại" khi đi qua vùng điểm điều khiển dày đặc. Vì vậy **t=0.5 KHÔNG phải là trung điểm chiều dài của curve** — ngay cả sau khi Rebuild curve trong Rhino để phân bố lại điểm điều khiển đều, t=0.5 vẫn không trùng trung điểm thật.

## 3.3 Analysis of curves in Grasshopper

### 3.3.1 Evaluate Curve
Component **Evaluate Curve** (Curve > Analysis) tìm điểm trên curve theo tham số t: input C (curve) + t (Number Slider). Vì Parametric Representation giả định domain [0,1] nhưng curve trong Rhino thường có domain khác, cần **Reparameterize** (right-click vào component curve, chọn "Reparameterize") để ép domain về [0,1] — làm điều này với mọi curve có domain gốc khác nhau để đồng bộ. Output gồm điểm P (theo WCS) và vector tiếp tuyến T tại điểm đó (hiển thị bằng Vector Display, có thể khuếch đại bằng nhân vô hướng qua component Multiplication).

### 3.3.2 Flip Curve
Mỗi curve có 1 **chiều** (direction) từ điểm đầu (t=0) đến điểm cuối (t=1), phụ thuộc thứ tự các điểm điều khiển lúc vẽ. Reparameterize KHÔNG đổi chiều. Muốn đổi chiều dùng **Flip Curve** (Curve > Util). Ví dụ: 2 curve ngược chiều nhau, muốn nối điểm đầu curve 1 với điểm cuối curve 2 bằng Line phải Flip 1 trong 2 trước. Input G của Flip Curve cho phép chỉ định 1 "curve mẫu" — dùng để đồng bộ hoá chiều của cả 1 tập nhiều curve có hướng lộn xộn (merge tất cả rồi Flip theo 1 curve tham chiếu).

### 3.3.3 World to Local conversion — Curve CP
**Curve CP** (Curve > Analysis) chuyển 1 điểm từ WCS sang tham số t cục bộ (LCS) của 1 curve cho trước: tìm điểm P' gần nhất trên curve ứng với điểm ngoài P, output D = khoảng cách lệch giữa P và P'. Nếu P nằm sẵn trên curve, P=P' và D=0.

### 3.3.4 Point on Curve
Nhắc lại từ chương 1: **Point on Curve** hoạt động dựa trên **chiều dài curve** (không phải domain t), nên giá trị 0.5 luôn cho đúng trung điểm thực (khác Evaluate Curve). Không cần Reparameterize trước khi dùng.

### 3.3.5 Evaluate Length
**Evaluate Length** (Curve > Analysis) tìm điểm P cách điểm đầu (t=0) 1 khoảng đo theo chiều dài cung (arc-length, input L), L nằm trong khoảng 0 đến chiều dài curve (tính bằng component **Curve Length**). Output cả P (WCS) lẫn t (LCS).

### 3.3.6 Divide Curve
Nhắc lại chương 1: chia đều curve theo N đoạn chiều dài bằng nhau, ra N+1 điểm (curve hở) hoặc N điểm (curve kín); cũng xuất luôn vector tiếp tuyến T và tham số t tại mỗi điểm chia.

### 3.3.7 Divide Length
**Divide Length** (Curve > Division) chia curve thành các đoạn có chiều dài L cố định; nếu tổng chiều dài curve không chia hết cho L, sẽ dư ra 1 "leftover-arc" ngắn/dài khác L ở cuối.

### 3.3.8 Divide Distance
**Divide Distance** (Curve > Division) chia curve bằng cách tính giao điểm liên tiếp của các vòng tròn bán kính D với curve — cũng có thể sinh leftover-arc nếu khoảng cách D không khớp hết chiều dài.

### 3.3.9 Contour
**Contour** (Curve > Division) tạo tập hợp đường đồng mức (contour) từ 1 curve, dựa trên điểm bắt đầu P, vector pháp tuyến N, và khoảng cách D — trả về giao điểm dạng toạ độ WCS lẫn LCS.

### 3.3.10 Shatter
**Shatter** (Curve > Division) cắt curve thành các **đoạn curve con** (không phải điểm) tại các giá trị t chỉ định. Ví dụ: cắt curve thành 2 phần bằng 1 điểm cắt lấy từ Rhino, nối tham số t (lấy qua Curve CP) vào input t của Shatter, ra 2 curve con hiển thị qua Panel. Có thể dùng luôn output t của Divide Curve làm input cho Shatter để cắt hàng loạt.

## 3.4 Notion of Curvature for planar curves (Khái niệm độ cong của đường cong phẳng)

Độ cong (curvature) tại 1 điểm P đo mức độ đường cong "lệch" khỏi đường tiếp tuyến tại P — thay đổi theo từng điểm. Hai giả định nền tảng: độ cong đường thẳng luôn bằng 0; độ cong vòng tròn luôn không đổi (và tiến về 0 khi bán kính tiến ra vô cực — tức đường thẳng là vòng tròn bán kính vô hạn). Từ đó: **độ cong k = 1/r** (nghịch đảo bán kính).

Với đường cong bất kỳ, dùng khái niệm **osculating circle (vòng tròn mật tiếp)** — vòng tròn khớp sát nhất với curve tại điểm P. Độ cong k tại P = nghịch đảo bán kính vòng tròn mật tiếp đó. Độ cong cũng có thể biểu diễn dưới dạng **vector k** có hướng PO (P tới tâm vòng mật tiếp O) và độ lớn = 1/bán kính. Theo quy ước dấu: dương nếu vòng mật tiếp nằm bên trái theo chiều curve, âm nếu nằm bên phải.

Component **Curvature** (Curve > Analysis) hiển thị trực quan vector k và vòng mật tiếp tại 1 điểm P (theo LCS). Có 2 cách tính giá trị độ cong: lấy nghịch đảo bán kính vòng mật tiếp qua **Deconstruct Arc/DArc** (Curve > Analysis, output R), hoặc lấy độ lớn vector k qua **Vector Length** (Vector > Vector). Component **Curvature Graph** (Curve > Analysis) vẽ đồ thị trực quan độ cong dọc theo curve.

## 3.5 Parametric representation of a surface (Biểu diễn tham số mặt cong)

Tương tự curve, surface cũng có LCS với 2 tham số **u** và **v** (cùng chạy 0–1). Cố định u=u1 cho ra 1 "sectional curve" C1 (isocurve theo hướng v); cố định v=v1 cho ra C2 (isocurve theo hướng u). Các isocurve tạo thành 1 lưới hình chữ nhật khái quát hoá ý tưởng "lưới Descartes" lên mặt cong — vì mọi NURBS-surface về bản chất là biến dạng của 1 mặt phẳng chữ nhật gốc. Surface luôn có domain 2 chiều dạng hình chữ nhật (u,v) dù hình dạng thật (đã trim) có thể là hình tròn/elip — Rhino chỉ **ẩn** phần bị trim đi, domain gốc vẫn luôn là hình chữ nhật. Surface không chứa trọn domain của nó gọi là **Trimmed Surface**; surface chứa trọn domain gọi là **Untrimmed Surface**.

## 3.6 Surface creation (Các cách dựng surface)

Grasshopper cung cấp nhiều component dựng surface (panel Freeform, tab Surface):
- **Extrude** — cách đơn giản nhất: kéo 1 profile curve (hoặc surface) theo 1 vector, ra surface tiết diện không đổi.
- **Boundary Surfaces** — dựng surface phẳng (trim hoặc untrim) từ 1 tập curve biên khép kín, phẳng, liên tục.
- **Loft** — dựng surface đi qua 1 tập curve tiết diện có thứ tự, cần tối thiểu 2 curve. **Loft Options** đi kèm cho chỉnh: đóng surface (closed), chỉnh seam, rebuild, refit tolerance, và 6 kiểu loft (0=Normal, 1=Loose, 2=Tight, 3=Straight, 4=Developable, 5=Uniform).
- **Surface from Points** — dựng surface từ 1 lưới điểm, cần khai báo số điểm theo hướng u (vd lưới 9×6 điểm cần khai U-count=6) — hữu ích khi dựng surface từ hàm toán học (xem lại mục 2.3.2).
- **Edge Surface** — nội suy surface từ 2, 3 hoặc 4 curve biên có thứ tự.
- **Patch** — khớp (fit) 1 surface qua tập điểm/curve (hở hoặc kín), tạo các đường vuông góc gọi là "span" — các span hiếm khi song song với bất kỳ cạnh nào của surface kết quả, nên Patch chỉ nên dùng khi các cách khác không khả thi.
- **Network Surface** — dựng từ 2 tập curve có thứ tự theo 2 hướng u và v, input C chỉnh kiểu liên tục biên (0=Loose, 1=Position, 2=Tangency, 3=Curvature) — kiểm soát biên tốt hơn Loft.
- **Sweep1 / Sweep2** — quét 1 curve tiết diện (S) dọc theo 1 rail curve (Sweep1) hoặc 2 rail curve (Sweep2).
- **Revolution / Rail Revolution** — dựng surface bằng cách xoay 1 profile curve quanh 1 trục, hoặc xoay theo 1 rail curve dẫn hướng.

## 3.7 Analysis of surfaces using Grasshopper

### 3.7.1 Evaluate Surface
Tương tự Evaluate Curve nhưng cho surface: input S (surface) + toạ độ (u,v) — dùng component **MD Slider** (Params > Input, "multi dimensional slider" — bản mở rộng 2 chiều của Number Slider, domain mặc định 0–1 cho cả u và v) để nhập cặp u,v. Cần Reparameterize surface trước (right-click). Output: điểm P (WCS), vector pháp tuyến N tại P, và mặt phẳng tiếp tuyến F tại P (kích thước hiển thị của mặt phẳng chỉnh qua Display > Preview Plane).

### 3.7.2 World to Local — Surface CP
**Surface CP** (Surface > Analysis) tìm điểm P' gần nhất trên surface ứng với điểm ngoài P, trả về toạ độ (u,v) cục bộ và khoảng lệch D (D=0 nếu P đã nằm trên surface).

### 3.7.3 Reverse Surface Direction
Đảo chiều u/v của surface dùng component **Surface Direction** thuộc plug-in **LunchBox** (do Nathan Miller phát triển) — không phải component gốc của Grasshopper. Input R: 0=không đảo, 1=đảo u, 2=đảo v, 3=đảo cả hai. Thường cần Reparameterize output sau khi đảo.

### 3.7.4 Isocurve
**Isocurve** (Curve > Spline) trích xuất 2 đường isocurve (U và V) đi qua 1 điểm (u,v) cho trước trên surface — có thể xem riêng từng đường bằng cách ẩn phần còn lại.

### 3.7.5 Divide Surface
**Divide Surface** (Surface > Util) sinh 1 lưới điểm trên surface bằng cách chia đều 2 trục u,v theo số nguyên dương chỉ định — output gồm điểm P, vector pháp tuyến N, và toạ độ cục bộ (u,v) tại mỗi điểm.

### 3.7.6 Isotrim
**Isotrim-SubSrf** (Surface > Util) chia surface thành các sub-surface liền kề dựa trên 1 lưới isocurve cắt, phối hợp với **Divide Domain²** (Maths > Domain — chia domain 2 chiều thành lưới cắt theo số U/V). Mỗi sub-surface xuất ra vẫn giữ nguyên tham số hoá theo domain của surface cha (vd sub-surface góc dưới-trái có thể có domain [0;0.1]×[0;0.2]) — muốn mỗi sub-surface có domain riêng chuẩn [0,1] phải Reparameterize từng cái. Đặt U hoặc V của Divide Domain² = 1 sẽ sinh dải (stripe) liên tục thay vì lưới ô vuông — kết hợp Cull Pattern để tạo hoạ tiết dải xen kẽ.

### 3.7.7 Strategy: uneven splitting (Chia lưới không đều)
Divide Domain² mặc định chia đều. Muốn chia không đều: tách domain 2D thành 2 domain 1D (U, V) bằng **Deconstruct Domain²** (Maths > Domain), chỉnh phân bố điểm trong mỗi domain bằng **Graph Mapper** (Params > Input, right-click chọn kiểu đồ thị "Bezier"), rồi gộp lại bằng **Construct Domain²** (Maths > Domain), cuối cùng Isotrim như thường. Kéo grip trên đồ thị Graph Mapper sẽ thay đổi mật độ lưới.

### 3.7.8 Deconstruct Brep
NURBS-surface là 1 đối tượng hình học gồm 3 thành phần: **Face** (mặt), **Edge** (cạnh — đoạn curve biên), **Vertex** (đỉnh — điểm góc). Component **Deconstruct Brep** (Surface > Analysis) tách 1 surface/Brep ra các thành phần này. Thuật ngữ **Brep** (boundary representation) mô tả cách định nghĩa khối rắn bằng ranh giới — 1 khối/polysurface là tập hợp các face+edge được "khâu" lại với nhau; 1 surface NURBS đơn có thể coi là Brep chỉ gồm 1 face. Ví dụ minh hoạ lỗi thường gặp: dùng **Center Box** (Surface > Primitive) tạo khối hộp, nối thẳng vào component Surface sẽ báo lỗi đỏ (data mismatch) vì hộp là Brep gồm 6 mặt ghép — phải Deconstruct Brep trước để tách ra 6 surface riêng lẻ.

### 3.7.9 Surface Split
Có thể cắt surface bằng 1 curve nằm trên chính surface đó — ví dụ dùng **geodesic** (đường đi ngắn nhất trên mặt cong, tương đương "đường thẳng" trong không gian cong) nối 2 điểm S, E ở 2 cạnh đối diện. Component **Surface Split** (Intersect > Physical) cắt surface S tại curve cắt C, ra 2 trimmed surface. Muốn có untrimmed surface từ kết quả trim, dùng Deconstruct Brep lấy edge rồi dựng lại bằng Edge Surface.

### 3.7.10 Example: diagrid (Lưới chéo)
Ví dụ ứng dụng thực tế đầu tiên: dựng **lưới chéo (diagrid)** trên 1 surface bất kỳ. Quy trình: chia surface thành sub-surface bằng Isotrim, tách 4 đỉnh mỗi sub-surface bằng Deconstruct Brep + List Item, nối Line giữa các đỉnh chéo nhau (0→1, 1→3) để tạo 1 module diagrid, sau đó bỏ List Item để áp dụng cho toàn bộ lưới sub-surface cùng lúc. Vì diagrid dựng từ đỉnh sub-surface phẳng nên chỉ khớp hoàn toàn với surface gốc khi sub-surface đó phẳng — muốn diagrid bám sát bề mặt cong thật, cần **Project** (Curve > Util) chiếu các đường Line lên lại surface gốc (dùng receiver "wireless" nối tới surface gốc), biến đoạn thẳng thành curve cong theo mặt. Thuật toán này không ràng buộc vào 1 surface cụ thể — dùng được cho bất kỳ surface nào. Cuối cùng dùng **Pipe** (Surface > Freeform) quét 1 vòng tròn bán kính chỉ định dọc theo các đường diagrid để tạo thanh 3D thật.

### 3.7.11 Example: space frame (Kết cấu không gian)
Mở rộng ví dụ diagrid: lấy tâm gần đúng mỗi sub-surface qua **Evaluate Surface** với MD Slider (0.5, 0.5) (cần Reparameterize trước vì sub-surface đã mang domain của surface cha). Dùng **Line SDL** (Curve > Primitive — Start, Direction, Length) để tạo đoạn thẳng từ mỗi tâm theo hướng vector pháp tuyến N với chiều dài tuỳ chỉnh — tạo hiệu ứng đẩy các "chóp" ra khỏi mặt phẳng. Lấy điểm cuối các đoạn đó bằng Endpoint, nối với các đỉnh (V-output của Deconstruct Brep) để hoàn thiện các thanh còn lại của kết cấu không gian (space frame) 3D.

### 3.7.12 Grid of equidistant points on a generic surface (Lưới điểm cách đều — Chebyshev-net)
Lưới toạ độ (u,v) mặc định trên surface là 1 dạng "Cartesian Grid biến dạng" — cạnh các ô lưới KHÔNG bằng nhau trừ khi surface phẳng tuyệt đối (curvature=0). Muốn có lưới cạnh đều nhau thật sự, cần phương pháp **Chebyshev-net** — do nhà toán học Nga Pafnuty Chebyshev (1821–1894) phát triển từ bài toán "cắt vải bọc mặt cong" (sách "On the cutting of our clothes", 1878). Với 2 curve giao nhau bất kỳ (u, v) xuất phát từ 1 điểm P trên surface và 1 độ dài cạnh L cho trước, có 1 lưới Chebyshev-net duy nhất tương ứng.

Cách dựng hình học (áp dụng cho cả mặt phẳng lẫn surface tự do): vẽ vòng tròn (hoặc mặt cầu trong không gian 3D) bán kính L quanh điểm gốc O, giao với 2 isocurve u, v để ra điểm 1 và điểm 2; từ điểm 1, điểm 2 vẽ tiếp 2 vòng tròn/mặt cầu bán kính L, giao nhau ra điểm 3 — lặp lại cho cả 4 góc phần tư để phủ kín lưới. Phương pháp này về bản chất là mở rộng 3 chiều của logic **Divide Distance** (mục 3.3.8). Phương pháp cũng áp dụng được với curve u, v không vuông góc (ra lưới hình thoi cạnh đều) và curve cong (không nhất thiết thẳng) — nhưng khi đó thường để lại 1 vùng "dư" (leftover area) không phủ kín hết, khác với lưới chia theo domain (luôn khớp khít vì độ dài đoạn phụ thuộc chia đều domain). **Lưu ý: Grasshopper KHÔNG có sẵn component để lặp (iterate) dựng Chebyshev-net** — cần add-on hỗ trợ vòng lặp (nói ở chương 7). Đặc điểm quan trọng của lưới cách đều: có thể "trải phẳng" (flatten) thành lưới vuông đều — nền tảng để dựng kết cấu gridshell từ các tấm phẳng có thể uốn cong được.

## 3.8 Notion of Curvature for surfaces (Độ cong mặt cong)

Tại 1 điểm P trên surface tự do, có vô số mặt phẳng chứa vector pháp tuyến n tại P; mỗi mặt phẳng giao với surface ra 1 curve, mỗi curve có 1 giá trị độ cong (theo osculating circle, như mục 3.4). Trong tập vô số giá trị độ cong đó, tồn tại **Minimum Principal Curvature (K₁)** và **Maximum Principal Curvature (K₂)** — ứng với 2 curve C₁, C₂ vuông góc nhau. Vector tiếp tuyến của C₁, C₂ tại P gọi là **Minimum/Maximum Principal Curvature Direction**.

Từ K₁, K₂ định nghĩa 2 đại lượng quan trọng: **Gaussian Curvature G = K₁ × K₂**; **Mean Curvature M = (K₁+K₂)/2**.

### 3.8.1 Gaussian Curvature
Surface có Gaussian Curvature = 0 tại mọi điểm gọi là **Developable Surface (surface khai triển được)** — có thể "trải phẳng" ra mặt phẳng mà không bị biến dạng, rất hữu ích trong chế tạo vì dựng được từ tấm phẳng uốn cong (kim loại, bìa, gỗ dán...) và luôn chứa 1 tập đường thẳng (ruling) giúp đơn giản hoá kết cấu (dầm thẳng). Điều kiện G=0 xảy ra khi K₁=0 hoặc K₂=0 (tích với 0 luôn bằng 0). Ví dụ: mặt trụ (cylinder) có K₁=0 (theo đường sinh — generatrix, là đường thẳng) và K₂=1/r (theo đường tròn tiết diện) → G=0. Tương tự với mặt nón.

Component **Principal Curvature** (Surface > Analysis) xuất vector hướng K'/K'' và giá trị C'/C'' của 2 độ cong chính; **Surface Curvature** (Surface > Analysis) xuất trực tiếp Gaussian Curvature (G) và Mean Curvature (M).

Các dạng developable surface điển hình: mặt phẳng, trụ, "generalized cylinder" (tiết diện là elip/parabol/curve mượt bất kỳ), nón, "generalized cone" (tập đường thẳng qua 1 đỉnh và mọi điểm trên 1 curve mượt), **Oloid** (khối hình học do Paul Schatz phát hiện năm 1929), "tangent developable surface" (hợp các đường tiếp tuyến của 1 curve tự do).

Về định nghĩa: developable surface luôn là **ruled surface** (surface sinh bởi chuyển động của 1 đường thẳng gọi là generatrix/ruling) — nhưng ngược lại không đúng, không phải ruled surface nào cũng developable. 1 ruled surface là developable khi góc xoắn (twist angle) giữa 2 tiếp tuyến ở 2 đầu mỗi ruling bằng 0 (ruling khi đó gọi là "torsal ruling"). Nếu chỉ có sẵn 1 rail curve, có thể tính ra rail curve thứ 2 sao cho twist angle luôn = 0. Nhưng nếu CẢ 2 rail curve đã cố định sẵn (không tự do chọn), việc chia đều 2 curve rồi nối thẳng các điểm tương ứng KHÔNG đảm bảo ra developable surface — cần thuật toán/plug-in chuyên dụng để tìm đúng các ruling "không xoắn". Sách dẫn ví dụ thực tế: kiến trúc sư Frank Gehry thường nghiên cứu hình học bằng mô hình vật lý làm từ vật liệu tấm dẻo để tìm ra các mặt developable cho công trình (dẫn ảnh MARTa Herford Museum và Fisher Center for the Performing Arts).

### 3.8.2 Sign of Gaussian Curvature
Với surface không developable, Gaussian Curvature có thể dương hoặc âm: **dương** khi K₁ và K₂ cùng dấu (osculating circle của C₁, C₂ nằm cùng phía so với generatrix); **âm** khi K₁, K₂ khác dấu (osculating circle nằm khác phía) — đây là dạng mặt yên ngựa (saddle). G=0 khi C₂ là đường thẳng.

### 3.8.3 Mean Curvature
Surface có Mean Curvature = 0 tại mọi điểm gọi là **Minimal Surface (mặt cực tiểu)** — ví dụ mặt catenoid (sinh bởi xoay 1 đường catenary quanh trục của nó). Định nghĩa M=0 tương đương K₁=−K₂ (2 độ cong chính bằng nhau về độ lớn, ngược dấu). Màng xà phòng (soap film) căng giữa 1 khung biên là ví dụ vật lý điển hình của minimal surface, vì diện tích màng luôn tự co về mức tối thiểu có thể.

### 3.8.4 Strategy: developable test (Kiểm tra surface có developable hay không)
Có thể kiểm tra trực quan bằng component **Osculating Circles** (Surface > Analysis): vẽ 2 vòng tròn mật tiếp (theo 2 hướng chính) tại 1 điểm P (LCS). Nếu surface developable, ít nhất 1 trong 2 vòng tròn sẽ suy biến thành **đường thẳng** (bán kính vô hạn) — nhận biết qua trạng thái "đúng" (gray, không lỗi) của component Line nối 2 đầu vòng đó. Để kiểm tra toàn surface, sinh 1 lưới điểm bằng Divide Surface rồi tính osculating circle tại mọi điểm trong lưới.

### 3.8.5 Example: curvature pattern (Hoạ tiết theo độ cong)
Ví dụ ứng dụng: dùng chính giá trị Mean Curvature đo được để điều khiển 1 hoạ tiết vòng tròn trên surface — nơi độ cong lớn thì vòng tròn to hơn (hoặc ngược lại), tạo hiệu ứng hoạ tiết phản ánh hình dạng surface. Quy trình: dựng surface bằng Gumball chỉnh gờ nổi (ridge) để tạo biến thiên độ cong rõ rệt → chia sub-surface bằng Divide Domain + Isotrim → lấy tâm mỗi sub-surface qua Evaluate Surface (MD Slider 0.5,0.5) → dùng **Circle CNR** (input C = tâm, N = pháp tuyến từ Evaluate Surface) vẽ vòng tròn tại mỗi tâm, bán kính R lấy từ Mean Curvature (M-output của Surface Curvature) thay vì slider cố định. Vì Mean Curvature có thể âm, lọc qua **Absolute** (Math > Operators) để lấy giá trị dương, và dùng **Minimum** để chặn trần bán kính (vd không vượt 0.150). Dùng thêm **Cull Pattern** kết hợp điều kiện Evaluate (vd x>0.025) để chỉ giữ vòng tròn đủ lớn. Cuối cùng dùng **Surface Split** cắt surface gốc bằng các vòng tròn này để tạo surface có lỗ hoạ tiết (holed surface) — kết quả tại index 0 của output F là surface gốc đã bị cắt, các index còn lại là các mảnh "scrap" (vụn cắt ra), lọc bằng List Item hoặc Cull Index tuỳ mục đích muốn giữ phần nào.
