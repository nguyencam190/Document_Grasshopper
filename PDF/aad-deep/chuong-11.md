# Chương 11 — Environmental Analysis (Phân tích môi trường)

Chương cuối, viết dựa trên nghiên cứu của Maurizio Degni (chuyên gia phân tích năng lượng/môi trường cho hệ thống phức tạp, cộng tác cùng Arturo Tedeschi trong dự án NU:S). Giới thiệu plug-in **GECO** — cầu nối giữa Grasshopper và phần mềm phân tích môi trường **Autodesk Ecotect Analysis**.

## Mở đầu

Nhiều phần mềm phân tích môi trường tồn tại nhưng phần lớn chỉ đóng vai trò "back-end" (phân tích phía sau), đóng góp hạn chế cho khám phá thiết kế toàn diện — vì khó chỉnh sửa ở giai đoạn mô hình hoá nâng cao, người thiết kế thường dựa vào kinh nghiệm cá nhân hơn là phân tích thật, thu hẹp khả năng khám phá nhiều phương án thiết kế theo hướng dữ liệu môi trường. Kết hợp gói phần mềm môi trường và tham số cho phép định hình thiết kế xuyên suốt từ phác thảo ban đầu tới thiết kế cuối, dựa trên phân tích thời gian thực (bức xạ mặt trời, ánh sáng...).

## 11.1 Tools (Công cụ)

Hệ sinh thái Grasshopper có nhiều plug-in phân tích môi trường — 1 số phân tích trọn vẹn, 1 số làm cầu nối tới phần mềm phân tích chuyên dụng khác. **GECO** thuộc nhóm sau: liên kết trực tiếp Grasshopper với **Autodesk Ecotect Analysis** — phần mềm phân tích môi trường mạnh, phát triển năm 1996 bởi Andrew Marsh, được Autodesk mua lại năm 2008.

## 11.2 GECO and Ecotect

**GECO** được phát triển bởi **[uto]** — nhóm thiết kế/nghiên cứu có trụ sở Innsbruck, sáng lập bởi Ursula Frick và Thomas Grabner (cả 2 tốt nghiệp xuất sắc ngành Kiến trúc, Đại học Innsbruck; cũng phát triển các công cụ số khác như PhysX, Flowlines, MeshPaint, MeshEdit — MeshEdit đã nhắc ở mục 6.3.3). GECO cung cấp bộ component cho phép dữ liệu chảy trực tiếp 2 chiều giữa Grasshopper và Ecotect, biến việc tối ưu môi trường thành khả thi.

Ecotect có giao diện trực quan, phân tích toàn diện (hiệu năng nhiệt, bức xạ mặt trời, ánh sáng ngày, bóng đổ, âm học) và có cả môi trường mô hình hoá 3D riêng — nhưng không phù hợp dựng hình dạng phức tạp. GECO lấp khoảng trống giữa mô hình hoá hình dạng và phân tích: cho phép dựng hình tham số trong Grasshopper rồi xuất sang Ecotect, tạo vòng phản hồi thời gian thực để định hình/tối ưu mặt dựng, mái che, công trình...

Tóm tắt chức năng các component GECO:
- Xuất điểm/hình học từ Grasshopper sang Ecotect.
- Thiết lập lưới phân tích (analysis grid).
- Tính toán chiếu sáng ngày (**EcoLightCal**).
- Tính toán bức xạ mặt trời (**EcoSolCal**).
- Nhập phản hồi từ Ecotect về Grasshopper.
- Nhập biểu đồ mặt trời (solar diagram) tính bởi Ecotect vào Grasshopper.
- Component **EcoLua** cho phép tương tác trực tiếp với ngôn ngữ script Lua của Ecotect.

### 11.2.1 Interface (Giao diện)
Cần cài đủ 3 phần mềm: **Ecotect** (thương mại, dùng thử 30 ngày hoặc license sinh viên 3 năm, tại autodesk.com), **GECO**, và **Mesh Edit** (xem 6.3.3) — cả GECO và Mesh Edit tải miễn phí tại food4rhino.com. Sau khi cài, xuất hiện panel mới **GECO** trong tab **Extra**.

Component GECO chia 4 nhóm: **Link and export (liên kết & xuất)**, **Analysis grids (lưới phân tích)**, **Calculations (tính toán)**, **Feedbacks (phản hồi)**. Lưu ý: tên component đổi khi thả lên canvas — vd `EcoLink` → hiện thành "Link Ecotect"; `EcoSolCal` → "Insolation Calculation".

### 11.2.2 Link and export
2 component chính: **EcoLink** (Link Ecotect) — công tắc thiết lập kết nối Ecotect↔Grasshopper; **EcoMeshExport** — xuất đối tượng dựng trong Rhino/Grasshopper sang Ecotect để phân tích. Giống nhiều phần mềm phân tích khác, **Ecotect chỉ làm việc trên hình học mesh** (không nhận NURBS trực tiếp).

### 11.2.3 Analysis grid and mesh-analysis
Ecotect phân tích trên **lưới (grid)** hoặc trực tiếp trên **mesh**. Lưới là 1 tập điểm trong không gian, tưởng tượng như "cảm biến" — vd phân tích ánh sáng thường thực hiện tại nhiều điểm trong không gian, không chỉ trên bề mặt đối tượng. Với các phân tích khác (vd insolation — bức xạ), có thể tính trực tiếp trên mặt mesh. Khi cần lưới, phải định nghĩa vị trí không gian và số ô chia — càng nhiều ô, kết quả càng chính xác. 2 component chính dựng lưới: **2dAnalysisGrid** (vẽ lưới theo 1 domain không gian + số ô) và **FitGrid** (khớp lưới theo kích thước đối tượng hiện có trong Ecotect).

### 11.2.4 Calculations
Các loại tính toán GECO hỗ trợ:
- **Biểu đồ mặt trời (solar diagram)**: dùng **EcoSunPath** và **EcoSunRays** (chi tiết ở 11.4).
- **Insolation (bức xạ nhận được)**: dùng **InsolationCalculations** trên mesh hoặc grid, trả về (chi tiết ở 11.6): (1) bức xạ tới (incident); (2) bức xạ hấp thụ/truyền qua; (3) hệ số bầu trời (sky factor) và bức xạ hoạt động quang hợp (PAR); (4) bóng đổ/che khuất và số giờ nắng.
- **Lighting comfort (tiện nghi ánh sáng)**: dùng **LightingCalculations**, trả về (chi tiết ở 11.8): (1) hệ số ánh sáng ngày (Daylight Factor); (2) mức chiếu sáng ngày (Daylight Levels); (3) thành phần bầu trời (Sky Component).

**WEATHER FILES (file thời tiết)**: mọi tính toán môi trường cần dữ liệu khí hậu hợp lệ cho vị trí địa lý cụ thể, lưu trong **Weather File** — chứa bức xạ mặt trời, hướng gió, nhiệt độ, lượng mưa, độ ẩm... Ecotect có sẵn Weather File cho các thành phố lớn; vị trí khác tải từ website Bộ Năng lượng Mỹ (U.S. Department of Energy). File tải về ở định dạng **.EPW (Energy Plus Weather File)**, nhưng Ecotect chỉ đọc được định dạng **.WEA (Weather Data File)** — chuyển đổi bằng công cụ Weather Manager trong Ecotect (`Tools > Run the Weather Tool`, mở file .EPW rồi lưu lại thành .WEA).

### 11.2.5 Feedback/import (Nhập phản hồi)
Sau khi phân tích xong trong Ecotect, kết quả nhập lại vào Grasshopper để điều khiển biến đổi hình học — vd dữ liệu bức xạ dùng để điều khiển kích thước lỗ mở mái che. Có 2 chế độ nhập tuỳ phân tích thực hiện trên grid hay mesh: **EcoGridRequest** (nhập toàn bộ dữ liệu tính trên grid) hoặc **EcoObjectRequest** (nhập dữ liệu tính trực tiếp trên mesh, vd bức xạ, ánh sáng).

## 11.3 About GECO's components (Cấu trúc chung component GECO)

Đa số component GECO có cấu trúc tương tự nhau, hỗ trợ **kết nối theo tầng (cascading)**. Minh hoạ qua 2 component: **EcoSunPath** (vẽ biểu đồ mặt trời) và **LightingCalculations** (tính tiện nghi ánh sáng).

Cả 2 đều có: input **(E)** nhận giá trị Boolean (thường từ Boolean Toggle) — True để thực thi tính toán tương ứng trong Ecotect; output **(out)** hiển thị thông tin nhận về từ Ecotect; output **(D)** trả về **False** nếu Ecotect còn đang chạy, **True** khi tính toán hoàn tất. Output (D) và input (E) dùng để tạo **chuỗi kết nối tầng**: giá trị Boolean từ (D) component này kích hoạt (E) component tiếp theo — đảm bảo các bước tính toán chạy tuần tự đúng thứ tự, không chạy chồng lấn. Giống component Grasshopper chuẩn, hover chuột vào input/output sẽ hiện thông tin chi tiết.

## 11.4 Solar diagram and shadows (Biểu đồ mặt trời và bóng đổ)

**EcoSunPath** và **EcoSunRays** sinh biểu đồ đường đi mặt trời và vector tia nắng cho 1 vị trí/thời điểm cụ thể — vector tia nắng dùng để vẽ bóng đổ của 1 đối tượng bất kỳ lên 1 mặt phẳng.

Bước bắt buộc đầu tiên của mọi định nghĩa GECO: thiết lập liên kết Ecotect↔Grasshopper qua **Link Ecotect**, bật/tắt bằng Boolean Toggle nối vào input (E). Output (out) trả về log văn bản hiển thị kết quả kiểm tra kết nối. Component EcoLink luôn đứng **độc lập**, không nối với component nào khác ngoài Panel hiển thị log.

Nếu EcoLink hiện trạng thái **cảnh báo (cam)**: kết nối thất bại — khắc phục bằng cách chuyển Toggle True→False→True lại. Nếu hiện trạng thái **lỗi (đỏ)**: Ecotect hoặc GECO chưa cài đặt đúng.

**SUN PATH (đường đi mặt trời)**: sau khi kết nối thành công, **EcoSunPath** trích dữ liệu đường đi mặt trời theo ngày [D] (slider 1–31), tháng [M] (slider 1–12), và vị trí theo **Weather File** [W] — nạp qua component **File Path** (Params > Primitive, right-click chọn "Set One File Path"; file .WEA theo vị trí nằm ở thư mục mặc định `C:\Program Files (x86)\Autodesk\Ecotect Analysis\Weather Data`). Input [E]=True khởi động phân tích, biểu đồ mặt trời xuất hiện trong Rhino. Output: 2 curve — (C) đồng hồ mặt trời (sundial), (S) đường đi mặt trời (sun path); output (T) là số chỉ giờ mặt trời mọc/lặn; input [S] chỉnh tỉ lệ hiển thị 2 curve trên.

**SOLAR RAY (tia nắng)**: sau khi có sun path cho 1 ngày cụ thể, **EcoSunRays** trả về tia nắng tại 1 thời điểm cụ thể — input [D], [M] dùng chung slider với EcoSunPath; input [T] là giờ trong ngày (slider từ giờ mặt trời mọc tới lặn, vd 8.00–18.00). Output V là vector tia nắng (hiển thị qua Vector Display), output P là điểm gốc vector.

**SHADOWS (bóng đổ)**: dùng dữ liệu trên để vẽ bóng đổ 1 đối tượng mesh bất kỳ lên 1 mặt phẳng — component **MeshShadow** (Mesh > Util), input M = mesh, L = vector tia nắng (nối V-output của EcoSunRays). Output O lưu contour bóng đổ chiếu lên mặt phẳng input P — có thể trực quan hoá bằng cách dựng surface phẳng qua **Boundary Surfaces**.

### 11.4.1 Responsive skin (Mặt dựng phản ứng)
Ứng dụng dữ liệu môi trường vào biến đổi hình học ngay từ giai đoạn ý tưởng: dùng vector tia nắng để điều khiển kích thước cửa sổ mặt đứng, bằng cách so sánh góc giữa vector tia nắng và vector pháp tuyến surface.

Quy trình: dựng 1 freeform surface, chuyển sang mesh bằng **Mesh Surface** (số chia U,V định nghĩa ma trận panel mặt dựng); tính vector pháp tuyến tại tâm mỗi mặt mesh bằng **Face Normals** (Mesh > Analysis); tách cạnh mesh bằng **Face Boundaries** (Mesh > Analysis, trả về polyline khép kín mỗi mặt).

**Lưu ý quan trọng về hướng vector pháp tuyến**: phải kiểm tra bằng Vector Display — vector pháp tuyến phải **cùng chiều với vector tia nắng**, tức hướng **vào trong** bề mặt cần phân tích (không phải hướng ra ngoài như mặc định thường thấy) — nếu ngược, phải đảo bằng component **Reverse** (Vector > Vector). Sau khi hướng đúng, thiết lập kết nối Ecotect qua EcoLink, sinh biểu đồ mặt trời + tia nắng qua EcoSunPath/EcoSunRays cho ngày/giờ cụ thể.

Dùng component **Angle** (Vector > Vector) đo góc (radian) giữa vector tia nắng và pháp tuyến mỗi mặt — góc càng nhỏ (nắng chiếu càng vuông góc/mạnh) thì hệ số scale mở cửa sổ càng nhỏ (cửa nhỏ lại để giảm nắng nóng). Scale cạnh mesh bằng component **Scale** — hệ số phải trong domain (0,1] để co vào trong; dùng **Remap** (xem 2.5) để chuyển giá trị góc đo được sang domain hệ số scale mong muốn.

Cuối cùng, "mặt dựng có lỗ biến thiên" (variable holed skin) được tạo bằng **Loft** giữa từng cạnh gốc và cạnh đã scale tương ứng — như đã học ở chương 5, 2 luồng dữ liệu phải **Graft trước khi Merge**. Sau khi dựng xong, chỉ cần thay đổi input [T] của EcoSunRays (giờ trong ngày) sẽ ra kích thước lỗ mở khác nhau — mô phỏng mặt dựng phản ứng theo thời gian trong ngày.

## 11.5 Exporting geometries and importing data (Xuất hình học và nhập dữ liệu)

Một số phân tích (ánh sáng, bức xạ) đòi hỏi xuất hẳn mesh từ Grasshopper sang Ecotect để tính, rồi nhập kết quả ngược lại.

### 11.5.1 Exporting geometries from Grasshopper to Ecotect
Component chính: **EcoMeshExport** (Export Mesh to Ecotect). Các quy tắc quan trọng khi xuất:
- **Explode mesh**: phải nổ mesh ra từng mặt bằng **Mesh Explode** (Mesh > Analysis) để tăng tương thích.
- **Kiểm tra hướng pháp tuyến**: pháp tuyến phải hướng **ra ngoài** (kiểm tra bằng Face Normals + Vector Display).
- **Flatten dữ liệu**: output F của Mesh Explode phải ở chế độ **Flatten** trước khi nối vào input M của EcoMeshExport — nếu không, Ecotect chỉ nhập được các mặt thuộc branch cuối cùng (bỏ sót phần còn lại).

Input E=True để xuất. Quy trình xuất kiểm soát bởi input N (3 giá trị): **N=0**: xuất mesh hiện tại, xoá mọi hình học đang có trong Ecotect; **N=1**: xuất mesh hiện tại, chỉ xoá mesh đã xuất lần gần nhất (mesh đang chọn trong Ecotect); **N=2**: xuất mesh hiện tại, giữ nguyên mọi hình học có sẵn trong Ecotect (có thể gây lỗi chồng lấn).

Các input khác:
- **[C]**: hệ số scale mesh xuất. Ecotect thường làm việc theo mm — để [C]=0 (mặc định) nếu Rhino cũng đơn vị mm; đặt [C]=1000 nếu Rhino đơn vị mét.
- **[F]**: liên quan lưới phân tích — Boolean Toggle=True để khớp lưới phân tích theo mesh vừa xuất.
- **[T]** và **[M]**: gán loại phần tử (element type) và vật liệu (material) cho mesh — [T] có 16 loại từ 0–15 (vd 1=Roof, 2=Floor, 3=Ceiling, 4=Wall, 5=Partition, 6=Window, 7=Panel, 8=Door, 9=Point, 10=Specimen, 11=Light, 12=Appliance, 13=Line, 14=Solar collector, 15=Camera).
- **[Z]**: định nghĩa **zone** của Ecotect — vùng/thể tích kín đồng nhất, thường (không luôn luôn) trùng khái niệm "phòng". Zone quản lý giống layer CAD, đặt tên qua gõ text vào Panel nối [Z]. Nếu dùng nhiều EcoMeshExport, phải đặt cùng giá trị [Z] để xuất các mesh khác nhau vào chung 1 zone.

### 11.5.2 Importing data from Ecotect
2 cách nhập dữ liệu tuỳ phân tích thực hiện trên mesh hay grid:
- **EcoObjectRequest** (Object Request): dùng cho mesh — trả dữ liệu tính tại tâm mỗi mặt mesh, cần input I là chỉ số mặt mesh (lấy từ output I của EcoMeshExport). 2 output chính: **Val** (giá trị số kết quả phân tích) và **RGB** (gradient màu gán theo giá trị số).
- **EcoGridRequest** (ImportAnalysisGrid): dùng cho grid.

Cả 2 đều có input [A] chọn thuộc tính (attribute) cụ thể trong toàn bộ dữ liệu trả về — vd chọn "Total Radiation" thì [A]=0. Danh sách thuộc tính khả dụng xem qua tooltip khi hover chuột vào input, tuỳ loại phân tích (bức xạ, ánh sáng ngày, CFD...).

## 11.6 Insolation analysis (Phân tích bức xạ)

**Insolation (bức xạ nhận được)** — 1 trong những tham số quan trọng nhất của hiệu quả năng lượng thụ động: năng lượng nhận trên 1 bề mặt trong 1 khoảng thời gian, đo bằng Wh/m². Ecotect tính insolation dựa trên **định luật cosine Lambert (Lambert's cosine law)**.

Hình học và vật liệu công trình nên được thiết kế để **tối đa hoá bức xạ vào mùa đông, tối thiểu hoá vào mùa hè**. Tối ưu năng lượng thường xoay quanh khái niệm **passive solar gain (thu nhiệt thụ động)** — sự tăng nhiệt độ trong không gian do bức xạ mặt trời. Insolation cũng then chốt để định vị/kích thước đúng bộ thu năng lượng mặt trời (solar collector) và pin quang điện.

Component tính: **EcoSolCal** (Insolation Calculations). Quy trình: định nghĩa mesh cần phân tích → chạy Ecotect qua EcoLink → xuất mesh theo quy tắc mục 11.5, kết nối theo tầng (cascade) với EcoMeshExport.

Input chính của EcoSolCal:
- **[W]**: Weather File (như 11.2.4).
- **[I]**: loại địa hình (Terrain Types) — 0=vị trí hở gió, 1=nông thôn, 2=ngoại ô, 3=đô thị đông đúc.
- **[C]**: loại tính toán — 1=bức xạ tới trực tiếp, 2=hấp thụ-truyền qua, 3=hệ số bầu trời + PAR.
- **[S]**: **Sky Subdivision** — kỹ thuật Ecotect chia vòm trời để tính toán; giá trị càng nhỏ độ chính xác càng cao, nhập số 1–15 (có thể đặt 50 để chạy nhanh, độ chính xác thấp hơn).
- **[G]**: chuyển đổi phân tích giữa Object và Grid (mặc định Object).
- **[DP]**: domain ngày bắt đầu/kết thúc trong năm (Construct Domain, A/B trong 1–365, theo lịch Julian; mặc định [1,365]).
- **[TP]**: domain giờ bắt đầu/kết thúc (Construct Domain, A/B trong 0.00–23.99).

Nhập kết quả bằng **EcoObjectRequest**, kết nối tầng với EcoSolCal, input I nối output I của EcoMeshExport (chỉ số mặt). Output **RGB** hữu ích để tạo minh hoạ gradient màu qua component **Mesh Colours** (Mesh > Primitive) — trực quan hoá kết quả ngay ở giai đoạn ý tưởng. Output **Val** trả về giá trị số cho tính toán tiếp theo.

### 11.6.1 Practical Exercise: Positioning photovoltaic panels (Bài tập thực hành: bố trí tấm pin quang điện)
Bài tập minh hoạ (chi tiết đầy đủ qua mã QR, không có text): dùng phân tích insolation để định vị tấm pin mặt trời trên 1 mái che — thuật toán chia mái thành các panel, xác định panel nào có insolation cao nhất để đặt pin.

## 11.7 Analysis Grids (Lưới phân tích)

Nhiều tính toán (đặc biệt ánh sáng) thực hiện trên grid — tập điểm coi như "cảm biến" đặt trong không gian. 2 cách định nghĩa grid:
- **EcoFitGrid** (FitGrid): khớp grid theo phạm vi đối tượng đã chọn trong Ecotect.
- **Eco2DGrid** (2dAnalysisGrid): tự định nghĩa kích thước + vị trí grid thủ công.

Cả 2 cách đều cần thêm 2 component: **EcoGridRequest** (ImportAnalysisGrid — nhập giá trị phân tích) và **EcoMeshGrid** (MeshGrid — vẽ grid trong Rhino).

**FITGRID**: kết nối tầng với EcoMeshExport. Input:
- **[A]**: mặt phẳng tham chiếu — slider 0 (XY), 1 (YZ), 2 (XZ).
- **[T]**: kiểu khớp — 0=grid nằm bên trong hình học mesh, 1=bao quanh hình học, 2=khớp theo đúng hình dạng thật, 3=lớn hơn đối tượng.
- **[Cx], [Cy], [Cz]**: số ô chia theo 3 hướng chính.
- **[O]**: độ lệch (offset) so với mặt phẳng tham chiếu.

Sau khi phân tích hoàn tất, nhập kết quả qua **EcoGridRequest** — input [A] chọn thuộc tính (vd với phân tích ánh sáng ngày ở mục 11.8: A=0 trả về Daylight Factor, A=1 trả về Daylighting Levels — các thuộc tính khác chọn theo số hiển thị trong context menu). **EcoMeshGrid** sinh mesh tô màu theo giá trị phân tích.

**2D ANALYSIS GRID**: **Eco2DGrid** hữu ích khi tự định nghĩa thủ công đặc điểm lưới: mặt phẳng [A], chiều rộng domain [W], chiều cao domain [H], số ô chia theo 2 hướng W, H. Khuyến nghị: nên tạo grid sao cho domain W và H **cùng dấu** (cả dương hoặc cả âm) — nói cách khác, grid phải nằm trọn trong **1 trong 4 góc phần tư** không gian Rhino.

## 11.8 Light Control (Kiểm soát ánh sáng)

Phân bố ánh sáng ảnh hưởng lớn tới hiệu quả năng lượng công trình và tiện nghi thị giác — tối ưu phân bố ánh sáng là chiến lược cốt lõi của thiết kế thụ động. Component **EcoLightCal** (LightingCalculations) phân tích mức độ chiếu sáng và phân bố ánh sáng theo các tham số: **Daylight Factors, Daylighting Levels, Internally Reflected, Externally Reflected, Sky Component**.

Tính toán phân bố ánh sáng cần biết mức ánh sáng bên ngoài công trình (gồm ánh nắng trực tiếp và chiếu sáng gián tiếp từ bầu trời). Giá trị độ chiếu sáng bầu trời (sky illuminance, đơn vị lux) suy ra từ phân tích thống kê mức chiếu sáng bầu trời ngoài trời động — sách dẫn 1 hình minh hoạ mức lux thiết kế theo vĩ độ. Có nhiều công cụ online để tra mức lux khuyến nghị theo vị trí cụ thể.

### 11.8.1 Visual comfort of a room (Tiện nghi thị giác trong phòng)
Ví dụ: phân tích tiện nghi thị giác 1 phòng hình hộp có 1 mặt kính hướng đông.

**SETTING THE GEOMETRY**: dựng hộp kích thước 12000×6000×6000mm (dài×rộng×cao) trong Rhino/Grasshopper. Nổ hộp thành từng mặt riêng — mặt hướng đông thu vào container Surface đặt tên "window" (cửa sổ), các mặt còn lại vào container "panels". Chuyển 2 nhóm surface sang mesh (mỗi surface chỉ chia 1 ô U,V để mỗi surface ra đúng 1 mặt mesh — cho phép gán vật liệu khác nhau cho window/panels). Nổ 2 nhóm mesh bằng Mesh Explode, flatten dữ liệu nhóm panels.

**EXPORTING MESHES INTO ECOTECT**: xuất bằng 2 component EcoMeshExport riêng biệt — nhóm mesh mặt cửa sổ đặt [T]=6 (loại Window); nhóm panel dùng giá trị mặc định [T]=7 (Panel).

**SETTING THE ANALYSIS GRID**: dùng EcoFitGrid — mặt phẳng song song XY ([A]=0), offset 700mm ([O]), grid nằm trong đối tượng ([T]=0), số ô 10×10 theo [Cx],[Cy] ([Cz] không liên quan vì phân tích chỉ trên grid 2D tại độ cao cố định 700mm so với mặt tham chiếu).

**LIGHTING ANALYSIS**: chạy **EcoLightCal** — input [P] (precision, độ chính xác) đặt 2 (High Precision), input [L] (sky illuminance) đặt 7300 lux (theo hình minh hoạ 11.6), input [T] chọn phân tích trên grid (0, mặc định) hay trên điểm đối tượng (1), input [C] chọn loại tính toán ánh sáng cần trả về.

Nhập kết quả bằng **EcoGridRequest**, vẽ mesh tô màu bằng **EcoMeshGrid** — như mục 11.7, input [A] của EcoGridRequest chọn thuộc tính cụ thể. Có thể hiển thị trực tiếp giá trị số ngay trên grid bằng component **Text Tag 3D** (Display > Dimensions): input L nhận điểm grid (P-output của EcoGridRequest), input T nhận giá trị đã tính, input S chỉnh cỡ chữ hiển thị.

### 11.8.2 Practical Exercise Galapagos + GECO, visual comfort optimization (Bài tập thực hành: tối ưu tiện nghi thị giác)
Bài tập kết hợp: dùng **Galapagos** (chương 10) để tối ưu tiện nghi thị giác 1 không gian bằng cách thay đổi số lượng và hình dạng của các thiết bị che nắng (sun shading devices) — chi tiết đầy đủ dẫn qua mã QR, không có trong text đọc được.
