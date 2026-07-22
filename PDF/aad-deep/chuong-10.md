# Chương 10 — Evolutive Structures: Topology Optimization (Kết cấu tiến hoá — Tối ưu hoá tô-pô)

Chương này do Davide Lombardi viết riêng (1 phần luận án tiến sĩ tại School of Advanced Studies "Gabriele d'Annunzio", hướng dẫn bởi Livio Sacchi và Alberto Pugnale, Đại học Melbourne). Chủ đề: dùng thuật toán tiến hoá để tối ưu hoá hình dạng/kết cấu — tích hợp quyết định thiết kế và kết cấu vào cùng 1 quy trình, thay vì tách rời vai trò kiến trúc sư (hình khối) và kỹ sư (tính toán) như thực hành thông thường.

## Mở đầu: Optimization là gì

Tối ưu hoá tích hợp quyết định thiết kế và kết cấu để tạo lời giải tối ưu trong 1 tập tham số cho trước — thường nhắm tới giảm vật liệu, vượt nhịp xa hơn, khai thác "độ trễ" kết cấu (structural latency), nhưng cũng áp dụng được cho công năng/chương trình/hình khối công trình. 2 hướng chính: **Shape Optimization (tối ưu hình dạng)** và **Topological Optimization (tối ưu tô-pô)** — cả 2 đều tìm lời giải tối ưu theo 1 tập tham số định nghĩa **fitness function (hàm thích nghi/hàm mục tiêu)**.

Cả 2 hướng chia sẻ chung logic quy trình: định nghĩa hình học ban đầu → định nghĩa điều kiện biên kiểm soát tối ưu hoá → định nghĩa 1 hoặc nhiều fitness function. Tuy quy trình nền giống nhau, 2 kỹ thuật khác biệt về khái niệm và thuật toán.

## 10.1 Shape Optimization (Tối ưu hình dạng)

Shape optimization là quá trình tính toán 1 hình học **giảm thiểu (minimize)** fitness function trong phạm vi điều kiện biên, **nhưng giữ nguyên tô-pô ban đầu** (chỉ thay đổi các thông số hình dạng, không thay đổi cấu trúc liên kết). 4 yếu tố: fitness function (thường là bài toán tìm cực tiểu), định nghĩa biến số, thiết lập gối đỡ, định nghĩa domain cho lời giải.

Quy trình 4 bước: (1) mô hình hoá sơ đồ tĩnh và điều kiện biên; (2) dựng mô hình phần tử hữu hạn (FE); (3) phân tích mô hình; (4) trực quan hoá + phân tích kết quả — sau đó, nếu đánh giá kết quả ổn, thêm bước tối ưu hoá.

**Ví dụ minh hoạ**: tối ưu tiết diện 1 dầm công-xôn (cantilever) trong 1 domain tiết diện cho trước — dầm có 1 đầu ngàm cố định (A), 1 đầu tự do (B) chịu tải điểm. Điều kiện biên: liên kết ngàm cứng tại A, không ràng buộc tại B, tải điểm tại B, tính chất vật liệu + danh sách tiết diện khả dụng theo tiêu chuẩn UNI5397-78 và UNI5398-78. Thuật toán tìm tiết diện **giảm thiểu chuyển vị (displacement)** tại B. Tính toán thực hiện bởi **genetic solver** (bàn kỹ hơn ở 10.6) — duyệt qua mọi lời giải khả dĩ, loại bỏ lời giải không đáp ứng tốt fitness function.

Sơ đồ thuật toán cụ thể: 2 điểm set từ Rhino định nghĩa 1 line (trục dọc dầm) → gán gối cố định tại A và tải trọng (vector Unit Z, độ lớn từ slider) tại B → khai báo tính chất vật liệu + danh sách tiết diện cần khảo sát, dùng thư viện vật liệu/tiết diện của plug-in **Karamba** (Clemens Presinger, hợp tác Bollinger-Grohmann-Schneider ZT GmbH Vienna — phân tích kết cấu: giàn không gian, khung, vỏ mỏng). Ví dụ chọn thép S275, tiết diện IPE/HE — danh sách tiết diện chính là "quần thể lời giải" mà genetic solver duyệt qua; mỗi tiết diện phân tích bằng phần tử hữu hạn, tiết diện cho chuyển vị nhỏ nhất tại B là lời giải tối ưu. Có thể trực quan hoá toàn bộ quá trình chọn lọc dần tới tiết diện tối ưu.

Lưu ý quan trọng sách nhấn mạnh: solver chỉ chọn tối ưu trong **danh sách hữu hạn** lời giải khả dĩ (bài toán quen thuộc, kết quả tin cậy); với bài toán phức tạp hơn, kinh nghiệm cho thấy lời giải solver trả về **thường không phải "tối ưu tuyệt đối"** mà chỉ "gần với tối ưu". Phép tính tối ưu hoá này do **Galapagos** (solver di truyền tích hợp sẵn Grasshopper, bàn kỹ ở 10.6) thực hiện. Sách nhắc lịch sử nghiên cứu thuật toán tiến hoá tính toán: khởi đầu thập niên 1960 với luận án "On the organization of the intellect" (Lawrence G. Fogel, 1964); phổ biến rộng rãi hơn nhờ cuốn "The Blind Watchmaker" (Richard Dawkins, 1986).

## 10.2 Topology (Tô-pô học)

**Tô-pô học** nghiên cứu quan hệ giữa các phần hình học khi biến dạng — khác hình học phẳng thông thường, tô-pô **không cần đo đạc khoảng cách/góc**, chỉ so sánh cấu trúc hình dạng. Sách minh hoạ bằng ví dụ nổi tiếng: bài toán **7 cây cầu Königsberg** do Euler đặt vấn đề năm 1736 — dù biểu diễn khác hẳn 1 tam giác đều đo đạc chính xác về độ dài/góc, đồ thị tô-pô của bài toán cầu vẫn mô tả cùng 1 vấn đề, vì vị trí và kích thước đối tượng không ảnh hưởng tới tô-pô hệ thống.

2 nguyên lý chính:
- **Nguyên lý liên tục do biến dạng (continuity)**: dù mất tính chất đo đạc/xạ ảnh khi biến dạng, vẫn luôn tồn tại **tương ứng 1-1 (biunique)** giữa các điểm của hình gốc và hình đã biến đổi.
- **Nguyên lý đồng phôi (homomorphism)**: các biến dạng gây **xuyên thấu hoặc chồng lấn vật liệu** đều **không được phép** sau khi biến dạng.

Nguyên lý tô-pô minh hoạ bằng phép biến đổi từ hình vuông thành hình tròn — bản đồ đồng phôi có thể thực hiện phép biến đổi này mà không cắt/chồng lấn. Quan hệ đồng phôi giữa 2 hình được kiểm soát bởi 1 tham số gọi là **genus** — bất biến tô-pô có thể chứng minh toán học rằng: 2 hình đồng phôi phải có cùng giá trị genus (g). Giá trị g của 1 hình tương đương **số lỗ** trong hình học đó, hoặc chính xác hơn là số lượng lớn nhất các đường cong khép kín đơn giản, không giao nhau, có thể vẽ trên surface mà không chia surface thành 2 phần riêng biệt. Về hình thái: 2 hình có cùng số lỗ (hoặc hoàn toàn không có lỗ) thì đồng phôi được với nhau. Vd: hình cầu có genus g=0, hình xuyến (torus) có genus g=1 — chúng **không** đồng phôi, không thể biến hình này thành hình kia (và ngược lại). Nguyên lý đồng phôi vì vậy quyết định **khả năng biến đổi** giữa các hình.

## 10.3 Topology optimization (Tối ưu hoá tô-pô)

Nguyên lý tô-pô toán học được dùng để nghiên cứu tối ưu hoá tô-pô của hình dạng — hướng nghiên cứu quy tụ kỹ sư, nhà toán học, sau này cả kiến trúc sư, nhằm sử dụng vật liệu hiệu quả hơn. Ý tưởng khởi nguồn khái niệm từ thế kỷ 19, nhưng chỉ được kiểm chứng thực tế vào cuối thập niên 1980 nhờ tiến bộ tính toán số. Thuật toán hoạt động đầu tiên được Xie và Steven giới thiệu năm 1992, gọi là **Evolutionary Structural Optimization (ESO)**.

Đặc điểm chính của ESO: có thể **thay đổi cả tô-pô kết cấu** (không chỉ hình dạng như Shape Optimization); dựa trên quy trình tiến hoá (evolution-based). 4 bước chính: (1) định nghĩa dữ liệu ban đầu (hình học, gối đỡ, tải trọng, vật liệu); (2) định nghĩa tham số tối ưu hoá; (3) phân tích phần tử hữu hạn (FEA); (4) tối ưu hoá kết cấu.

Quy trình cụ thể: bước đầu định nghĩa domain thiết kế **lớn hơn** kết quả cuối cùng mong đợi, cùng gối đỡ/tải/vật liệu — để FEA tính được biến dạng từng phần kết cấu. Bước 2 chia domain thành lưới phần tử hữu hạn (FE) và tính tham số tối ưu; sau FEA, có thể trực quan hoá phân bố ứng suất (vùng ứng suất cao/thấp). Sách minh hoạ ví dụ 2D đơn giản: 1 dầm 2 gối đỡ, chịu tải điểm ở mép dưới (thực hiện bằng phần mềm BES02D, phát triển bởi Prof. Mike Xie).

Sau khi tính xong, loại bỏ vật liệu không hiệu quả bằng **Rejection Criterion (RC)** — định nghĩa theo ứng suất Von Mises — và **Rejection Ratio (RR)**: giá trị phần trăm xác định các phần tử FE nào bị loại bỏ. Vd RR=50% nghĩa là loại mọi phần tử có RC thấp hơn 50% giá trị RC tối đa cho phép. **Hiệu chỉnh đúng giá trị RR quyết định độ chính xác kết quả**: sách minh hoạ so sánh trên cùng 1 ví dụ tối ưu dầm MBB (microbubble beam) với các RR khác nhau — RR cao (90%) chỉ loại bỏ rất ít vật liệu; RR trung bình (50–60%) cho kết quả khớp kỳ vọng thực tế; RR thấp (30%) loại bỏ quá nhiều vật liệu, dẫn tới cấu hình tĩnh **không hợp lệ**.

Sau bước loại vật liệu đầu tiên và đạt cấu hình ổn định, dầm tiếp tục được tối ưu bằng **Evolutionary Rate (ER)** — cộng thêm vào RR. Việc loại bỏ vật liệu kém hiệu quả làm thay đổi phân bố ứng suất, khiến vật liệu còn lại chịu ứng suất tập trung tăng lên — cần thêm tham số giới hạn ứng suất tối đa để mỗi phần tử làm việc ở mức tối ưu cơ học.

**XESO (Extended ESO)**, đề xuất bởi Sasaki, dựa trên ý tưởng: sinh vật thích nghi môi trường bằng cách loại bỏ phần không cần thiết và củng cố phần cần thiết — điển hình là **cây đa (Banyan Tree)**: hệ rễ khí sinh vươn xuống đất để đỡ thân chính, chỉ cấu tạo từ phần thực sự cần thiết về mặt chức năng, không lãng phí vật liệu. Sasaki chỉ ra ESO nguyên bản bị giới hạn bởi 2 yếu tố: (1) tính **đơn hướng** của quá trình tiến hoá (chỉ loại bỏ vật liệu kém hiệu quả, không thể thêm vật liệu); (2) thiếu kiểm soát quá trình tối ưu hoá. XESO khắc phục bằng 2 cải tiến: **chiến lược kiểm soát tối ưu bằng đường đồng mức (contour lines)**; và **tiến hoá 2 chiều (bi-directional)**.

XESO vẽ 1 tập đường đồng mức mô tả trạng thái ứng suất của vật thể, phân vùng theo 3 loại: (a) ứng suất thấp hơn giá trị giới hạn; (b) ứng suất bằng giá trị giới hạn; (c) ứng suất cao hơn giá trị giới hạn. Phương pháp này tăng tốc các bước tối ưu ban đầu vì vật liệu thoả điều kiện Von Mises (σᵢ < σ_max) được giữ lại, phần không thoả bị loại. Sau khi có domain thiết kế đã tối ưu bước đầu, vật liệu tiếp tục được thêm/bớt: tính ứng suất tại giao điểm giữa đường đồng mức và lưới ban đầu, vẽ đường đồng mức mới để xác định nơi thêm/bớt vật liệu — đường đồng mức **nằm trong vật liệu** = vật liệu cần loại bỏ, đường đồng mức **nằm ngoài vật liệu** = vật liệu cần thêm vào.

## 10.4 Works (Công trình thực tế)

### 10.4.1 Akutagawa office building
Toà nhà văn phòng do Hiroshi Ohmori thiết kế và xây dựng năm 2005, dùng phương pháp XESO. Công trình nằm trên khu đất vuông 6×10m gần ga Takatsaki (khu vực thương mại). XESO áp dụng cho 3 mặt đứng (bắc, nam, tây), loại trừ mặt đông và tầng áp mái khỏi quá trình tối ưu. Mô hình phần tử hữu hạn tính trọng lượng bản thân theo phương đứng, cùng lực ngang mô phỏng tác động địa chấn. Tô-pô 3 mặt tiến hoá bằng cách loại bỏ vật liệu ở vùng ít ứng suất, thêm vào vùng ứng suất cao.

### 10.4.2 TAV station in Florence
Đề xuất ga tàu cao tốc Florence của Arata Isozaki và Mutsuro Sasaki, dùng cùng thuật toán đã áp dụng cho Akutagawa. Công trình dài 400m, rộng 40m, cao 20m, gộp toàn bộ chương trình nhà ga trong 1 siêu kết cấu. Quá trình tối ưu biến đổi kết cấu từ hình cầu dạng khung đơn giản 2 đầu thành hình dạng hữu cơ phức tạp hơn — minh hoạ bằng chuỗi sơ đồ mô tả sự tiến hoá kết cấu. Đội thiết kế được hỗ trợ kỹ thuật bởi Buro Happold (London) để định nghĩa trình tự kết cấu. Kết cấu gồm thân thép, dầm ứng lực trước, sàn thép-bê tông. Isozaki, Sasaki và Buro Happold tiếp tục dùng cách tiếp cận này trong nhiều cuộc thi cho tới khi thực hiện được Trung tâm Hội nghị Quốc gia Qatar.

### 10.4.3 Qatar Education City
Phương pháp XESO dùng cho cuộc thi TAV Florence được tái sử dụng để thiết kế **Qatar National Convention Center** tại Doha. Kiến trúc sư Arata Isozaki áp dụng XESO cho khối kết cấu 25m dài × 30m rộng × 20m cao có mái phẳng, tải trọng chính trong tính toán XESO là trọng lượng bản thân kết cấu. Dự án là hình mẫu về hiệu quả tối đa và sử dụng vật liệu tối thiểu — quy trình thiết kế là sự tổng hợp giữa kiến trúc sư, kỹ sư và máy tính. Nhờ kinh nghiệm từ dự án Florence TAV, nhóm thiết kế bắt đầu với mô hình tinh chỉnh hơn ngay từ đầu, rút ngắn đáng kể thời gian phân tích và tối ưu hoá.

### 10.4.4 Radiolaria
Song song với việc áp dụng XESO, cần có công nghệ xây dựng phù hợp với kết cấu tiến hoá. Để xây Akutagawa Office Building, khuôn đúc lấy nguyên lý từ ngành đóng tàu. Với Qatar Education City, Buro Happold dùng hệ module tiền chế lắp tại chỗ — cách này vô tình "phủ nhận" ý tưởng kết cấu dòng chảy liên tục ban đầu của Sasaki và Isozaki. Hiện tại công nghệ xây dựng tiến hoá dùng **in 3D** đang được nghiên cứu — vd tác phẩm của kiến trúc sư Andrea Morgante, thực hiện bởi kỹ sư Enrico Dini dùng máy in D-Shape. Dự án lấy cảm hứng từ vi sinh vật **Radiolaria**, được in nguyên khối, không cần cốp pha, trực tiếp từ mô hình CAD đã kiểm định tĩnh học.

## 10.5 Examples (Ví dụ thực hành với plug-in)

Mở đầu bằng ví dụ lịch sử: năm 1904, **Anthony Michell** tối ưu tô-pô 1 dầm để tự đỡ và đỡ tải trọng trong khi giảm thiểu trọng lượng/vật liệu — **Michell Truss (giàn Michell)** gồm 1 dầm phẳng đỡ 1 tải tại 1 đầu, đầu còn lại là 1 vùng gối đỡ hình tròn.

Bài toán Michell Truss có thể tính bằng plug-in **Millipede** (phát triển bởi Kaijima Sawako và Michalatos Panagiotis — hỗ trợ phân tích FEM, form-finding, tối ưu tô-pô, sawapan.eu), dùng bộ component tối ưu tô-pô 2D. Quy trình 4 bước: (1) định nghĩa design space và điều kiện biên (hình học ban đầu, gối, tải); (2) dựng mô hình phần tử hữu hạn; (3) tối ưu tô-pô; (4) trực quan hoá và phân tích kết quả.

Chi tiết thuật toán: hình học ban đầu (design space) là 1 hình chữ nhật (dựng trong Grasshopper hoặc set từ Rhino), nối vào component **2DBoundaryRegion**. Gối đỡ mô hình bằng **2DSupportRegion** + **Stock Support Type** — vùng gối là 1 vòng tròn đặt tại tâm trục dầm, kiểu gối "fixed" (cố định mọi chuyển vị/xoay theo mọi phương); có thể bật/tắt từng ràng buộc riêng qua Boolean Toggle nối vào từng input của Stock Support Type (bài toán 2D nên không cần ràng buộc chuyển vị trục z, xoay trục x,y). Tải trọng mô hình qua **2DBoundaryLoad** — 1 hình chữ nhật đặt ở đầu dầm, hướng Unit Y âm. Cường độ tải trọng **không ảnh hưởng tới kết quả tối ưu tô-pô** — có thể đặt tải tuỳ ý (vd L=-1 N/m²) hoặc chỉ dựa vào trọng lượng bản thân.

Hệ thống được lắp ráp bằng component **Topostruct2DModel** (dựng mô hình phần tử hữu hạn), có input thứ 2 điều khiển độ phân giải mô hình — giá trị mặc định XR=12 thường quá thấp cho ứng dụng thực tế, nên tăng lên (đánh đổi thời gian tính toán lâu hơn). Component **Topostruct2DSolver** là lõi tính toán FEM + tối ưu tô-pô, cung cấp sẵn 1 bộ công cụ nội bộ chọn trực tiếp trên component (khác component Grasshopper chuẩn). Sách nêu 4/10 input quan trọng: **FE** (nhận mô hình FEM đã dựng — nên nối cuối cùng vì tự động khởi động phân tích ngay khi nối); **SWC** (self weight — số nguyên: 0=không tính trọng lượng bản thân, 1=tính 1 lần); **O** (số lần lặp solver, nên đặt O=1 để kiểm soát từng bước, giá trị cao hơn tốn thời gian và có thể mất kiểm soát tiến trình); **T** (target density — mật độ vật liệu mục tiêu, gần 0 loại bỏ cực đoan, gần 1 loại bỏ quá ít).

Sau khi nối FE-input, FEA tự chạy. Hướng tối ưu tô-pô kiểm soát bằng công cụ **STEP** nhúng trong solver (chạy từng bước lặp) — lặp nhiều lần cho ra cấu hình tối ưu dần. Có thể trực quan hoá kết quả thời gian thực qua **2DMeshResult** — hiển thị ứng suất Von Mises, dòng ứng suất chính (Principal tension), chuyển vị (Deflection). Topostruct2DSolver có 2 output: **FE** (để trực quan hoá) và **maxu** (giá trị chuyển vị tối đa, dùng hiển thị biến dạng vật lý — thường giá trị này rất nhỏ so với kích thước vật thể nên cần nhân với 1 hệ số khuếch đại qua Multiplication để nhìn rõ biến dạng; lưu ý việc khuếch đại chỉ ảnh hưởng **hiển thị**, không ảnh hưởng chuyển vị thật).

Ví dụ 2D thứ 2: dầm **MBB (MBB-beam)** chịu trọng lượng bản thân — mô hình ban đầu đơn giản: dầm chữ nhật, 2 gối đỡ, không tải ngoài. Chiến lược giống Michell Truss, khác 2 điểm: không có tải ngoài, và có tính trọng lượng bản thân của bê tông cốt thép trong lúc dựng mô hình FE. Có 2 vùng gối: 1 chịu chuyển vị theo cả x,y; 1 chỉ chịu chuyển vị theo y. Tính chất vật liệu chọn từ thư viện "Stock" của Millipede (ở đây chọn bê tông cốt thép).

Ví dụ thứ 3, mở rộng sang **3D**: tối ưu tô-pô 1 kết cấu cầu — mô hình sơ đồ là 1 khối chữ nhật 3D, 2 gối đỡ, không tải ngoài, tính trọng lượng bản thân bê tông cốt thép — chiến lược tương tự nhưng cả design space lẫn gối đỡ đều 3D. Điểm mới: vì tối ưu hoá tiến hoá cần giữ nguyên 1 phần khung không đổi (framework), cần thêm 1 khối hình học phụ (hộp chữ nhật cùng chiều dài dầm gốc, chiều cao tuỳ ý) đặt bên trong design space — khối này là input cho **3DDensityRegion**, định nghĩa vùng **không tham gia tối ưu hoá (non-design space)**. Mọi component còn lại là phiên bản 3D tương ứng của các component 2D đã dùng ở 2 ví dụ trước. Kết quả trực quan hoá bằng **3DisoMesh** — render hình học, hiển thị ứng suất nội và chuyển vị tối đa.

Quan sát kết quả cho thấy hành vi XESO (nền tảng của Millipede): xuất phát từ 1 khung giữ nguyên trong suốt quá trình tối ưu, XESO **không chỉ loại bỏ vật liệu ứng suất thấp mà còn thêm vật liệu ở nơi cần thiết** — vd thêm vật liệu tại các gối đỡ và tại điểm nối giữa đầu dầm và khung.

Sách kết luận mục này: các ví dụ chỉ là **bước tiếp cận đầu tiên** với tối ưu tô-pô — sự đơn giản khi thao tác trên giao diện Grasshopper không tương xứng với độ phức tạp toán học thật sự đằng sau lời giải; khuyến nghị mạnh mẽ nên tiếp cận vấn đề từ góc độ lý thuyết vững chắc và kiểm soát tốt các biến trong quá trình tính toán. Thuật toán tiến hoá còn ứng dụng được ngoài tối ưu kết cấu, vì XESO là kỹ thuật linh hoạt, có thể dùng cho bất kỳ bài toán nào hưởng lợi từ thuật toán cải tiến liên tục.

## 10.6 Optimization: finding solutions with Grasshopper (Tìm lời giải tối ưu bằng Grasshopper)

Solver tối ưu hoá giúp tìm lời giải tốt nhất trong tập phương án khả thi. Có nhiều solver, chia 2 nhóm:
1. **Exact solvers (solver chính xác)**: tìm đúng lời giải tối ưu, luôn cho cùng kết quả mỗi lần chạy.
2. **Heuristic solvers (solver dò tìm/xấp xỉ)**: tìm lời giải **gần đúng** khi không có lời giải chính xác — kết quả có thể khác nhau giữa các lần chạy.

Nhóm 1 gồm solver tuyến tính; nhóm 2 gồm solver tiến hoá (evolutionary — áp dụng nguyên lý tiến hoá tự nhiên vào bài toán tìm tối ưu). Sách giới thiệu 2 solver trong Grasshopper: **Galapagos** (tích hợp sẵn, do David Rutten phát triển) và **Goat** (plug-in, do Simon Flory phát triển — tiến sĩ Toán học Vienna University of Technology, chuyên xử lý hình học/hình học kiến trúc).

### 10.6.1 Optimization problems (Cấu trúc 1 bài toán tối ưu)
1 bài toán tối ưu gồm 2 thành phần: **hàm mục tiêu (objective function)** cần cực tiểu/cực đại hoá, và **tập biến số** ảnh hưởng giá trị hàm mục tiêu (thường định nghĩa bằng 1 khoảng giá trị, có điểm đầu/cuối). Ví dụ cơ bản: tìm điểm trên 1 curve gần nhất với 1 điểm ngoài A cho trước — hàm mục tiêu là d(t) (khoảng cách theo tham số t), biến số duy nhất là t trong [0,1]. Lời giải tối ưu là giá trị t làm d(t) nhỏ nhất.

### 10.6.2 Exact solvers. Goat plug-in
Chuyển bài toán trên thành sơ đồ Grasshopper: tính khoảng cách giữa điểm A và 1 điểm P trên curve (đã reparameterize), vị trí P kiểm soát bởi input t của Evaluate Curve. Kéo slider để đọc khoảng cách qua Panel và "tự dò" giá trị t cho khoảng cách nhỏ nhất — cách này bất tiện, khó chính xác. Dùng **Goat** để tìm chính xác: sau cài đặt, tìm trong `Special > Util` — component có 2 cổng **output** đặc biệt (khác component chuẩn có input):
1. **Variables**: nhận 1 hoặc nhiều Number Slider (trong Grasshopper, biến số của bài toán tối ưu luôn là Number Slider).
2. **Objective**: nhận 1 output số cần tối ưu (min/max).

Double-click Goat mở cửa sổ cài đặt: chọn **Minimum/Maximum** (ví dụ chọn Minimum cho D-output của component Distance); chọn thuật toán tối ưu **Local hay Global** — thuật toán Local tìm lời giải chính xác quanh giá trị khởi tạo của biến, thuật toán Global dò toàn bộ giá trị khả dĩ; với bài toán phức tạp, thường nên chạy Global trước rồi Local sau. Bấm OK khởi động — slider tự di chuyển theo hướng dẫn của Goat tới khi đạt giá trị tối ưu (khoảng cách nhỏ nhất), đọc kết quả qua giá trị t trên slider và giá trị D trên Panel.

### 10.6.3 Evolutionary solvers. Galapagos
Solver heuristic tiến hoá dùng khi bài toán có **nhiều biến số** và không tìm được lời giải chính xác bằng solver exact. **Galapagos** là solver tiến hoá tích hợp sẵn Grasshopper. Ví dụ minh hoạ: cho 1 freeform surface đã reparameterize, 2 điểm cố định A, B ở 2 cạnh đối diện — dùng Galapagos tìm **đường đi ngắn nhất (shortest path)** trên surface nối 2 điểm.

Đường path được mô tả bằng 1 curve nội suy linh hoạt (flexible interpolated curve) nằm trên surface, 2 đầu cố định A, B, hình dạng kiểm soát bởi toạ độ (u,v) của 1 tập điểm nội suy P (P₀, P₁,..., Pₙ) — thay đổi toạ độ các điểm này sẽ ra chiều dài curve khác nhau. Solver heuristic tìm toạ độ điểm nội suy tương ứng curve có chiều dài **ngắn nhất** trong mọi phương án khả thi.

Curve dựng bằng component **Curve on Surface** (Curve > Spline) — nội suy curve trên 1 surface (S), qua 1 tập điểm (uv) theo LCS. Cần 3 nhóm toạ độ uv, gộp qua Merge:
- **D1**: toạ độ cố định của điểm đầu A, chuyển sang LCS qua **Surface CP** (xem 3.7.2).
- **D2**: toạ độ (uv) của tập điểm P bất kỳ trên surface — dựng bằng Construct Point với toạ độ lấy từ slider domain [0,1]. Thay vì nhiều slider rời rạc, dùng **Gene Pool** (Params > Util) — component nhúng sẵn 1 tập slider. Dùng 2 Gene Pool riêng cho u và v; số lượng slider (Gene Count), khoảng giá trị, số chữ số thập phân chỉnh qua double-click Gene Pool. Càng nhiều slider (điểm nội suy) thì curve kết quả càng chính xác.
- **D3**: toạ độ cố định của điểm cuối B, cũng chuyển qua Surface CP.

Output L của Curve on Surface (chiều dài curve) thay đổi theo vị trí (uv) — có cả phần cố định (A, B) lẫn phần biến đổi (P), phù hợp để định nghĩa bài toán tối ưu. Dùng **Galapagos** (Params > Util) — tương tự Goat, cũng có 2 cổng: **Genome** (tương đương Variables — nhận toàn bộ slider trong 2 Gene Pool) và **Fitness** (tương đương Objective — nối vào output L của Curve on Surface).

Double-click Galapagos mở "Galapagos Editor" — chọn Fitness Minimize/Maximize (ở đây Minimize, vì muốn đường ngắn nhất). Mở tab **Solver**, bấm **Start Solver** để chạy — quá trình có thể mất từ vài phút tới vài giờ tuỳ độ phức tạp. Có thể dừng (**Stop Solver**) khi giá trị hiển thị góc dưới-phải cửa sổ ổn định (tiệm cận 1 số cố định). Kết quả cuối là bộ slider (toạ độ uv các điểm nội suy) tương ứng curve đường đi ngắn nhất — lấy trực tiếp qua output C của Curve on Surface.

Solver tiến hoá vận hành theo nguyên lý tiến hoá thật: dựa trên 1 **quần thể (population)** các lời giải ứng viên, "đấu tranh" đạt đặc điểm di truyền tốt hơn qua đột biến (mutation), lai ghép (crossover), thay đổi ngẫu nhiên — khác hẳn solver exact chỉ nhắm 1 lời giải tối ưu duy nhất. Về cơ bản, solver tiến hoá thực hiện "chọn lọc tự nhiên" giữa các lời giải khả dĩ, chỉ thành viên tốt nhất (theo đúng Fitness đã định nghĩa) mới "sống sót" qua các thế hệ.

### 10.5.4 [đánh số theo bản in gốc — thực chất 10.6.4] Target values (Giá trị mục tiêu)
Cả solver exact lẫn tiến hoá đều hoạt động bằng cách min/max hoá 1 fitness function. Có trường hợp muốn hàm fitness đạt đúng **1 giá trị mục tiêu cụ thể** (không phải cực tiểu/cực đại tuyệt đối) — khi đó, thay vì tối ưu trực tiếp giá trị fitness, tối thiểu hoá **giá trị tuyệt đối của hiệu số** giữa fitness và giá trị mục tiêu. Ví dụ minh hoạ: fitness là khoảng cách giữa 2 điểm, giá trị mục tiêu đặt là 500 — tối thiểu hoá `|khoảng cách − 500|` (đặt Fitness ở chế độ Minimize) sẽ ép khoảng cách tiến gần đúng 500 thay vì tiến về 0.
