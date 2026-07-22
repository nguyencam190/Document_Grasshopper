# Chương 6 — Smoothness (Độ mượt: Mesh và Subdivision Surface)

Chương giới thiệu hướng mô hình hoá thứ 2 song song với NURBS: **polygon mesh** và kỹ thuật **Subdivision Surface (SubD)** — cách tạo mặt mượt từ lưới đa giác thô, kỹ thuật phát triển cuối thập niên 1970, dùng nhiều trong hoạt hình nhân vật, nay ngày càng quan trọng trong thiết kế công nghiệp vì cho độ mượt khó đạt được bằng NURBS thuần tuý. Sách dẫn 2 tác phẩm minh hoạ của chính tác giả (Arturo Tedeschi, 2011): bàn cà phê "Blossom Table" và "Centerpiece" — cả 2 đều dựng bằng kỹ thuật SubD vì độ phức tạp hình học vượt quá khả năng thực tế của NURBS thuần.

## 6.1 NURBS and Polygon Meshes (NURBS và lưới đa giác)

Có 2 cách định nghĩa hình 3D trong phần mềm mô hình hoá: **biểu diễn (representation)** bằng curve/surface NURBS (chính xác tuyệt đối theo công thức toán — degree, control point, weight, knot như chương 3), hoặc **xấp xỉ (approximation)** bằng polygon mesh. NURBS luôn là 1 thực thể hình học **duy nhất, mượt tự nhiên** (tính mượt vốn có trong công thức toán); còn mesh **không thực sự mượt** — chỉ là tập hợp nhiều đa giác kề nhau, càng nhiều đa giác (càng nhỏ) thì trông càng mượt về mặt thị giác, nhưng bản chất vẫn là các mặt phẳng ghép lại.

## 6.2 Polygon meshes (Cấu trúc lưới đa giác)

3 thành phần của mesh:
- **Vertices (đỉnh)**: điểm toạ độ (x,y,z) theo WCS, quyết định hình dạng mesh.
- **Edges (cạnh)**: đoạn nối 2 đỉnh.
- **Faces (mặt)**: tập đỉnh+cạnh tạo thành 1 đa giác, thường là tam giác hoặc tứ giác. Lưu ý quan trọng: mặt mesh **thường KHÔNG phẳng tuyệt đối** — chỉ mesh tam giác mới chắc chắn phẳng (3 điểm luôn đồng phẳng), còn mesh tứ giác **không được đảm bảo phẳng**. Mesh tứ giác có mặt phẳng gọi là **PQ Mesh (Planar Quadrilateral Mesh)** — rất quan trọng trong kỹ thuật panel hoá kiến trúc freeform (vì panel kính/kim loại thật thường cần phẳng để dễ chế tạo).

Thứ tự kết nối đỉnh quyết định **hướng (orientation)** của mặt — phân biệt mặt trước (front face) và mặt sau (back face): cạnh nối đỉnh theo chiều **ngược kim đồng hồ** là mặt trước. 2 mặt kề nhau **tương thích (compatible)** nếu cùng hướng; mesh gồm toàn mặt tương thích gọi là **orientable mesh (mesh có hướng nhất quán)**. Mỗi mặt có 1 vector pháp tuyến — mặt trước có pháp tuyến hướng ra ngoài, mặt sau hướng vào trong; mesh orientable có mọi pháp tuyến cùng hướng nhất quán, còn "non-orientable mesh" có pháp tuyến lộn xộn (sách minh hoạ hình so sánh).

### 6.2.1 Geometry and topology (Hình học và tô-pô)
Mesh được xác định bởi 2 yếu tố tách biệt: **hình học (geometry)** — vị trí các điểm; và **tô-pô (topology)** — logic kết nối các điểm. Sách minh hoạ 2 cặp ví dụ đối lập: 2 khối hộp mesh có **cùng đỉnh (geometry) nhưng khác cách nối (topology)**; và ngược lại 2 khối hộp mesh có **cùng cách nối (topology) nhưng khác vị trí đỉnh (geometry)** — cho thấy 2 khái niệm độc lập với nhau, đều cần kiểm soát riêng khi dựng mesh.

## 6.3 Creating meshes in Grasshopper (Dựng mesh trong Grasshopper)

Ngoài các mesh nguyên thuỷ có sẵn (plane, box, sphere...), có 3 chiến lược chính để dựng mesh: theo **tô-pô (topology)**, theo **tam giác hoá (triangulation)**, hoặc **chuyển đổi từ NURBS sang mesh**.

### 6.3.1 Creating meshes by topology
Cách cơ bản nhất: mesh tam giác đơn giản nhất chỉ có 3 đỉnh (0,1,2). Component **Construct Mesh** (Mesh > Primitive) có 2 input chính: V (danh sách đỉnh) và F (định nghĩa tô-pô, dùng component **Mesh Triangle**, Mesh > Primitive — input A,B,C lần lượt chỉ định index đỉnh 0,1,2 theo đúng thứ tự tạo mặt). Muốn xem cạnh mesh, bật `Display > Preview Mesh Edges`.

Thêm đỉnh thứ 4 và định nghĩa đúng tô-pô sẽ ra 2 mặt tương thích: Face 1 = (0,1,2), Face 2 = (2,1,3) — cả 2 input A,B,C của Mesh Triangle nhận 2 giá trị (nối 2 mặt cùng lúc). Nếu định nghĩa mặt thứ 2 theo chiều kim đồng hồ (vd (1,2,3) thay vì (2,1,3)), sẽ ra **mesh không nhất quán hướng** — Grasshopper cảnh báo bằng cách tô 2 mặt kề nhau khác màu (mặt sáng = mặt trước, mặt tối = mặt sau). Mở rộng thêm: 5 đỉnh + 3 mặt (0,1,2)/(2,1,3)/(3,1,4) theo đúng chiều ngược kim đồng hồ sẽ ra mesh tam giác 3 mặt nhất quán hướng.

Tương tự, để dựng mặt tứ giác dùng **Mesh Quad** (Mesh > Primitive, 4 input tương ứng 4 đỉnh theo chiều ngược kim đồng hồ). Có thể mở rộng thành nhiều mặt tứ giác nối tiếp bằng cách thêm đỉnh và định nghĩa tô-pô đúng (vd Face 1=(0,1,2,3), Face 2=(1,4,5,2)).

### 6.3.2 Creating meshes by triangulation: Delaunay algorithm
Định nghĩa tô-pô thủ công chỉ khả thi với ít điểm/logic lặp lại — với tập điểm lớn bất kỳ, cần thuật toán **tam giác hoá (triangulation)** tự động. Mục tiêu của thuật toán tam giác hoá là **giảm thiểu chênh lệch giữa các tam giác** để tránh "tam giác gầy" (skinny triangle — tam giác quá dẹt, góc quá nhọn) — vốn gây kết quả sai lệch khi dùng cho mô phỏng vật lý (particle-spring system ở chương 9) hoặc phân tích phần tử hữu hạn (FEM).

Thuật toán phổ biến nhất: **Delaunay triangulation** (đặt theo tên nhà toán học Boris Delaunay), tối đa hoá góc nhỏ nhất trong mọi tam giác được tạo ra — nhờ đó hạn chế tam giác gầy. Quy tắc: xét vòng tròn ngoại tiếp (Delaunay circle) qua 3 đỉnh của 1 mặt tam giác — vòng tròn đó **không được chứa bất kỳ điểm nào khác** bên trong.

Component **Delaunay Mesh** (Mesh > Triangulation) tạo mesh tam giác theo thuật toán Delaunay từ tập điểm P; input PI là mặt phẳng (hoặc tập mặt phẳng) mà thuật toán hoạt động trên đó. Ví dụ ứng dụng thực tế: dựng pattern 3D trên 1 freeform surface bằng Delaunay — dùng plug-in LunchBox component **Triangle Panels B/TriB** dựng lưới tam giác cơ sở, tính trọng tâm mỗi tam giác, dịch trọng tâm theo vector pháp tuyến surface, rồi chạy Delaunay trên bộ 3 đỉnh gốc + trọng tâm đã dịch của mỗi tam giác (merge lại), ra 1 tập mesh 3-mặt (dạng chóp nhỏ) phủ toàn surface.

### 6.3.3 Creating meshes by a NURBS to mesh conversion
Cách thứ 3: chuyển trực tiếp từ NURBS surface sang mesh. Component **Mesh Surface / Mesh UV** (Mesh > Util) chuyển 1 NURBS surface thành **mesh tứ giác (Quadrangular Mesh)**, khai báo số ô chia theo U và V. Có thể chuyển tiếp mesh tứ giác thành mesh tam giác bằng component **Triangulate** (Mesh > Util) — cần cài thêm plug-in **Mesh Edit** (do [uto] — Ursula Frick và Thomas Grabner phát triển).

Như đã nói ở 6.2, chỉ mesh tam giác chắc chắn phẳng; mesh tứ giác chỉ phẳng trong 1 số trường hợp — vd surface xoay tròn (rotational) hoặc surface tịnh tiến (translational) khi chuyển bằng Mesh UV sẽ ra PQ Mesh (phẳng). Cách kiểm tra tính phẳng: tách biên mỗi mặt bằng component **Face Boundaries** (Mesh > Analysis, trả về polyline biên mỗi mặt) rồi kiểm tra phẳng bằng component **Planar** (Curve > Analysis); hoặc cách khác dùng **Boundary Surfaces** — component này chỉ vẽ được surface nếu các curve input tạo thành 1 biên phẳng (theo đúng định nghĩa của nó), nên có thể dùng gián tiếp như phép test tính phẳng.

NURBS-to-mesh cũng có thể thực hiện thủ công theo tô-pô: chia sub-surface bằng Isotrim, tách 4 đỉnh mỗi cái bằng Deconstruct Brep, định nghĩa tô-pô cố định, dựng Construct Mesh cho từng sub-surface, rồi gộp lại bằng **Mesh Join** (Mesh > Util) — hoặc dùng **Join Meshes and Weld** (Wb > Extract, thuộc plug-in Weaverbird nói ở mục 6.4) để vừa join vừa "hàn" (weld) các đỉnh trùng nhau (bật/tắt qua Boolean toggle).

Cách chuyển NURBS-to-mesh chỉ **tương thích hoàn toàn với Untrimmed Surface** (surface chứa trọn domain hình chữ nhật của nó, xem 3.5) vì loại này có sẵn lưới isogrid hình chữ nhật để chuyển thẳng thành mesh tứ giác. Với **Trimmed Surface**, có 2 lựa chọn không hoàn hảo: dùng **Mesh Surface** sẽ ra mesh **xấp xỉ** gần đúng biên gốc (không khớp tuyệt đối); dùng **Mesh Brep** (Mesh > Util) sẽ ra mesh **giữ đúng biên gốc** nhưng có thể sinh tam giác gầy. Với trường hợp phức tạp, sách gợi ý 1 chiến lược thủ công 6 bước: (1) thêm 1 điểm gốc O tuỳ ý; (2) chia biên surface thành N phần ra N điểm P; (3) nối Line từ O tới từng điểm P; (4) chia các Line này đều nhau và nối các điểm chia bằng polyline; (5) dùng mạng lưới line ở bước 3+4 để Split surface gốc thành các sub-surface trimmed; (6) tách đỉnh mỗi sub-surface và dựng mesh theo tô-pô như 6.3.1.

## 6.4 SubD in Grasshopper: Weaverbird plug-in

Ý tưởng cốt lõi của Subdivision Surface: từ 1 mesh đa giác thô bất kỳ ("input mesh"), có thể tính ra 1 **"limit surface" (mặt giới hạn) mượt tương ứng**. Thuật toán SubD xử lý input mesh để sinh ra 1 mesh output **ngày càng gần** limit surface đó — mesh đầu vào loại nào (tam giác, tứ giác...) sẽ cần thuật toán SubD tương ứng khác nhau. Sách tập trung 2 thuật toán chính: **Loop subdivision** (dành cho mesh tam giác) và **Catmull-Clark subdivision** (dành cho mesh tứ giác).

Cả 2 thuật toán đều nằm trong plug-in **Weaverbird** do Giulio Piacentino phát triển (kiến trúc sư tốt nghiệp Politecnico di Torino, tiếp tục học tại TU Delft, từng làm việc NIO Architecten, hiện phát triển cho McNeel), tải miễn phí tại giuliopiacentino.com. Sau khi cài, xuất hiện tab mới **Wb** chứa các component subdivision, biến đổi mesh, dựng khối đa giác nguyên thuỷ, và tách thành phần mesh.

## 6.5 Subdivision of triangular meshes: Loop algorithm

**Loop algorithm** (Charles Loop, 1987, luận văn thạc sĩ Toán tại University of Utah) — thuật toán subdivision lặp cho mesh tam giác: mỗi cạnh của mesh gốc được thêm 1 đỉnh mới tại **trung điểm**, các trung điểm nối lại, mỗi tam giác gốc bị thay thế bằng **4 tam giác con**. Mỗi lần lặp (iteration) tiến gần hơn tới limit surface; số lần lặp cần thiết **tỉ lệ nghịch với mức thay đổi hình học** — thường chỉ cần vài lần lặp là đủ gần với kết quả mượt cuối cùng.

Component **wbLoop** (Wb > SubD): input M = mesh cần subdivide, L = số lần lặp (1–3), S = cách xử lý cạnh biên hở (naked edge) của mesh gốc — 3 chế độ: **0 = Fixed** (cạnh biên giữ nguyên vị trí gốc, không di chuyển), **1 = Smooth** (cạnh biên có xu hướng "cong mượt" thành spline), **2 = Corner Fixed** (cạnh biên cong mượt thành spline nhưng 2 đỉnh góc được giữ cố định). Mesh input càng đơn giản/thô thì mesh output càng mượt tinh tế hơn sau vài lần lặp. Loop SubD cũng hoạt động được với mesh có lỗ (hole) — lỗ sẽ trở nên gần như tròn (pseudo rounded) sau khi subdivide.

## 6.5 [ghi đúng số mục sách in — thực chất là 6.6] Subdivision of quadrangular meshes: Catmull-Clark algorithm

(Lưu ý: bản in gốc đánh số trùng "6.5" cho cả 2 mục — đây là lỗi đánh số trong sách gốc, không phải lỗi đọc.)

**Catmull-Clark algorithm** (Edwin Catmull và Jim Clark, 1978) — thuật toán subdivision lặp cho mesh tứ giác (và cả tam giác), thêm đỉnh mới cho mỗi mặt để xấp xỉ dần 1 surface mượt. Sách minh hoạ ứng dụng lại đúng ví dụ "skin" 3D kim tự tháp cụt đã dựng ở chương 5.2.1 (gồm 3 nhóm surface: khung — surfaces set 01, mặt bên — set 02, mặt đáy — set 03): trước khi subdivide, mỗi nhóm surface phải chuyển sang mesh bằng **Mesh Surface**.

Lưu ý kỹ thuật khi chuyển nhiều surface ghép lại thành mesh: số ô chia U/V của Mesh Surface phải đặt sao cho các cạnh **khớp đúng tại đỉnh (tránh T-node)** — nếu không khớp, các mesh liền kề sẽ không "hàn" (weld) đúng được, thuật toán subdivision khi đó chỉ chạy riêng lẻ trên từng mesh rời rạc thay vì 1 khối liên tục. Khi số chia khớp đúng và có thể weld, dùng **Join Meshes and Weld** (Weaverbird > Extract) để gộp thành 1 mesh liên tục duy nhất, sau đó làm mượt bằng **Weaverbird Catmull-Clark Subdivision** (Weaverbird > SubD).

Một lỗi thường gặp khác: các mesh phải **tương thích hướng (compatible)** mới join/weld đúng (xem lại 6.2) — nếu không, sẽ xuất hiện "bóng" (shadow) dọc theo cạnh chung, báo hiệu lỗi hướng. Sách minh hoạ: mesh từ nhóm surface 03 (mặt đáy) bị ngược hướng so với các nhóm còn lại, cần **Mesh Flip** (Mesh > Util) đảo hướng trước khi join. Sau khi sửa hướng, join+weld thành công, chạy Catmull-Clark (input M=mesh, L=số lần lặp, S=xử lý cạnh biên — giống hệt cấu trúc input của wbLoop) ra kết quả mesh mượt liên tục hoàn chỉnh. Cùng chiến lược này cũng áp dụng lại được cho skin lục giác đã dựng ở mục 5.2.2 (sách minh hoạ ảnh trước/sau khi subdivide).

### 6.6.1 Voronoi skin
Giới thiệu **Voronoi diagram** (đặt theo tên nhà toán học Georgii Voronoi) — phép phân chia không gian theo tiêu chí "gần nhất": với tập n điểm gốc S(S₁,...,Sₙ), mỗi điểm Sᵢ sở hữu 1 vùng **Voronoi cell V(Sᵢ)** gồm mọi điểm trong không gian gần Sᵢ hơn bất kỳ điểm gốc nào khác. Voronoi có ứng dụng thực tế đa dạng (vật lý, quy hoạch đô thị — phân chia lãnh thổ theo khoảng cách tới 1 trung tâm) và cũng được giới thiết kế ưa chuộng vì tính thẩm mỹ nội tại.

Component **Voronoi** (Mesh > Triangulation) tạo Voronoi diagram phẳng từ tập điểm (P), trên mặt phẳng (PI), giới hạn trong 1 biên (B — boundary). Có thể set thêm bán kính tuỳ chọn R để giới hạn vùng mở rộng của mỗi cell — nếu không set R, mặc định bán kính vô hạn khiến các cell "hợp nhất" lấp đầy khoảng trống giữa chúng.

Ứng dụng: dựng "Voronoi skin" — biến mỗi Voronoi cell thành đáy của 1 hình chóp rồi làm mượt bằng subdivision. Quy trình: dùng **Discontinuity** (Curve > Analysis) lấy các điểm gãy khúc (đỉnh) định nghĩa mỗi cell — mỗi cell thành 1 branch riêng chứa n đỉnh tuỳ hình dạng cell; dịch trọng tâm mỗi cell theo hướng z âm; Merge đỉnh cell + trọng tâm đã dịch (Graft cả D1, D2) rồi tam giác hoá bằng Delaunay Mesh — kết quả là 40 mesh hình chóp **rời rạc, chưa nối liền** với nhau. Muốn liên tục, dùng **Weaverbird Join Meshes and Weld** (input M+ đặt chế độ Flatten) để gộp và hàn toàn bộ lại thành 1 mesh thống nhất trước khi subdivide.

Chiến lược này cũng áp dụng được cho Voronoi **không phẳng** (trên freeform surface) qua kỹ thuật **remap** (mục 2.5): dựng Voronoi trên mặt phẳng trước, remap toạ độ các điểm gãy khúc (Discontinuity) về domain [0,1] (dùng Remap Numbers), rồi vì surface đích đã reparameterize cũng có domain [0,1], dùng Evaluate Surface + Polyline để "tái tạo" đúng cấu trúc Voronoi đó lên surface tự do.

### 5.6.2 [ghi đúng số mục sách, thực chất 6.6.2] Fading pattern (Hoạ tiết mờ dần)
Ví dụ cuối chương: kết hợp thuật toán subdivision với **Image Sampler** (đã học ở 4.3.3) để tạo pattern 3D "mờ dần" theo 1 ảnh grayscale. Quy trình: dựng lưới 2D từ surface bằng plug-in LunchBox component **Diamond Panels** (LunchBox > Panels — trả về cả mặt tứ giác/hình thoi lẫn mặt tam giác); tách đỉnh và tính trọng tâm mỗi mặt hình thoi; dịch trọng tâm theo hướng pháp tuyến với hệ số vô hướng; gộp 4 đỉnh biên + trọng tâm đã dịch của mỗi mặt vào 1 branch riêng; dùng **Delaunay Mesh** tạo mesh hình chóp cho mỗi branch.

Để có hiệu ứng "mờ dần" (không đồng đều), hệ số dịch trọng tâm không được là hằng số — lấy trực tiếp từ **Image Sampler** (giá trị cường độ ảnh grayscale 0–1) làm hệ số nhân vô hướng thay vì slider cố định. Lưu ý kỹ thuật: các hình chóp sẽ bị lỗi hướng lộn xộn nếu không định nghĩa đúng mặt phẳng làm việc cho từng mặt hình thoi — dùng **Plane Normal** (Vector > Plane, input Z = vector pháp tuyến N từ Evaluate Surface) để định nghĩa đúng mặt phẳng riêng cho mỗi mặt, nối (đã Graft) vào input PI của Delaunay Mesh. Sau khi có tập hình chóp đúng hướng, Merge với output "Triangles" thứ 2 của Diamond Panels (để giữ các cạnh viền đều đặn), rồi làm mượt toàn bộ bằng Catmull-Clark (sau khi join+weld, dữ liệu flatten).

### 6.6.3 Strategy: cull adjacent faces (Chiến lược: xoá mặt kề trùng)
Chiến lược thực dụng cuối chương: khi ghép nhiều khối "mesh-box" lại với nhau (hình dạng phức tạp gồm nhiều hộp mesh join lại), các mặt bên trong bị **chồng lấp/trùng nhau** (2 hộp kề nhau chung 1 mặt tiếp giáp) cần được xoá bỏ để chỉ giữ lại vỏ ngoài. Component **Cull Duplicates** giúp lọc các điểm trùng nhau (coincident) và trả về index của các mặt **không bị chồng lấp** (non-overlapped faces) — dùng làm cơ sở để loại bỏ các mặt trùng lặp bên trong khối ghép, chỉ giữ lại lớp vỏ ngoài của hình khối tổng thể.
