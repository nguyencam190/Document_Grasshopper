# Chương 2 — Data (Quản lý dữ liệu trong Grasshopper)

Chương này dạy cách "chọn lọc, chuyển hướng, chỉnh sửa" dữ liệu — vì trong lập trình trực quan không có thao tác chuột vật lý để chọn 1 đối tượng như CAD, mọi lựa chọn phải làm qua thuật toán/index. Sách dùng 1 ví dụ xuyên suốt: 2 đường cong trong Rhino, chia mỗi đường thành 10 đoạn bằng Divide Curve, sinh ra 11 điểm/đường (tổng 22 điểm), rồi minh hoạ hàng loạt kỹ thuật để chọn/lọc/sắp lại các điểm đó.

## 2.1 Filters (Bộ lọc)

Grasshopper cấu trúc dữ liệu thành **path** (cấp bậc, sẽ học kỹ ở chương 5) chứa các **list**, list chứa các **item** được đánh số thứ tự (**index**) bắt đầu từ 0. Cách sắp xếp mặc định phụ thuộc cách dữ liệu được nạp vào: hình lấy từ Rhino thì theo thứ tự chọn trong Rhino; điểm từ Divide Curve thì theo chiều (direction) của đường cong. Muốn xem cấu trúc dữ liệu, nối component **Panel** (Params > Input) vào output để hiển thị danh sách kèm index.

### 2.1.1 List Item
**List Item** (Sets > List) chọn đúng 1 item theo index: input L = list nguồn, input i = số nguyên chỉ vị trí cần lấy. Có thể chọn nhiều item cùng lúc bằng cách nối nhiều slider vào input i (dùng Merge, hoặc giữ Shift khi kéo nhiều dây). Ví dụ áp dụng: từ 6 vòng tròn set từ Rhino (sắp theo trục x), dùng List Item lấy đúng vòng tròn thứ 4 (index 3) rồi extrude nó bằng component **Extrude** (Surface > Freeform) theo vector Unit Z nhân với 1 hệ số (factor).

### 2.1.2 Cull Index
**Cull Index** (Sets > Sequence) làm ngược lại List Item: **xoá bỏ** đúng (các) item có index chỉ định, giữ lại phần còn lại. Nếu list gốc có N item, output có N trừ số item bị cull.

### 2.1.3 Cull Pattern
**Cull Pattern** (Sets > Sequence) lọc theo 1 mẫu lặp lại các giá trị Boolean (True/False): item ứng với True được giữ, False bị loại. Mẫu Boolean thường dựng bằng nhiều component **Boolean Toggle** (Params > Input, click chuột trái để đổi True/False) gộp lại qua Merge. Mẫu sẽ tự lặp lại cho hết chiều dài list — vd mẫu (True, False) áp vào list 4 phần tử sẽ thành (True, False, True, False); mẫu cũng có thể dài hơn 2 giá trị, vd (True, True, False).

### 2.1.4 Shift List
**Shift List** (Sets > List) dịch chuyển toàn bộ index lên/xuống theo 1 độ lệch (input S — số dương dịch lên, số âm dịch xuống), input L là list cần dịch, input W (Wrap) là Boolean quyết định các phần tử "rơi ra ngoài" có được nối vòng lại cuối/đầu danh sách hay không. Ví dụ: S=-3, W=true → 3 index cuối (8,9,10) quay vòng lên thành 0,1,2 đầu danh sách. Nếu W=false, các phần tử bị đẩy ra ngoài sẽ bị xoá hẳn (danh sách ngắn lại). Ứng dụng minh hoạ: nối điểm i trên Curve 01 với điểm i+1 trên Curve 02 bằng cách shift 1 list trước khi nối Line; kết hợp thêm Cull Index để xoá đường nối thừa ở chỗ vòng nối (điểm cuối nối lại điểm đầu).

### 2.1.5 Split List / List Length
**Split List** (Sets > List) tách 1 list thành 2 list (A và B) tại 1 vị trí index chỉ định. **List Length** (Sets > List) đếm số phần tử trong 1 list — nối Panel vào output L để xem số lượng. Nếu index tách bằng đúng chiều dài list, list A = toàn bộ list gốc còn list B rỗng. Ứng dụng minh hoạ: tách bộ hình học thành 2 nhóm rồi extrude mỗi nhóm với độ cao khác nhau (200 và 100 đơn vị theo hướng Unit Z).

### 2.1.6 Reverse List
**Reverse List** (Sets > List) đảo ngược toàn bộ thứ tự index của 1 list (index 10 thành 0, index 9 thành 1...). Có 1 mẹo tương đương: right-click vào bất kỳ input slot nào cũng có tuỳ chọn "Reverse" ngay trong context menu để đảo dữ liệu trước khi nạp vào. Sách minh hoạ 2 cách tìm "điểm cuối cùng" của 1 list có độ dài thay đổi (khi N của Divide Curve đổi): cách 1 là nối chung 1 slider vào cả input N của Divide Curve lẫn input i của List Item (điểm cuối = N); cách 2 (gọn hơn) là Reverse List trước rồi luôn lấy index 0.

## 2.2 Numerical sequences (Dãy số)

### 2.2.1 Series
**Series** (Sets > Sequence) sinh dãy số theo 3 tham số: S (số bắt đầu), N (bước nhảy mỗi số), C (số lượng số cần sinh). Mặc định S=0, N=1, C=10 → dãy (0,1,2,...,9). N có thể âm để sinh dãy giảm dần. Ứng dụng kinh điển: kết hợp Series với **Move** (Transform > Euclidian) để tạo mảng bản sao dịch chuyển hàng loạt — dãy số của Series được nhân vô hướng (scalar multiplication) với 1 vector đơn vị (Unit X/Y/Z) để ra danh sách vector dịch chuyển khác nhau, nối vào input T của Move sẽ sinh 1 chuỗi bản sao dịch dọc theo 1 trục.

### 2.2.2 Data Matching
Khi 1 component nhận từ 2 luồng dữ liệu (2 dây) trở lên, Grasshopper phải "ghép cặp" (match) các item tương ứng theo logic mặc định — hiểu sai logic này sẽ ra kết quả bất ngờ. Ví dụ sách nêu: muốn tạo lưới 5×5 khối hộp (cube grid) bằng cách Move 2 lần (lần 1 theo trục x, lần 2 theo trục y), nếu ghép trực tiếp 5 khối đã dịch theo x với 5 vector dịch theo y, kết quả không phải lưới vuông mà chỉ là 1 đường chéo — vì mỗi khối chỉ ghép đúng 1 vector tương ứng (matching 1-1). Có 3 kiểu Data Matching:
- **Shortest List**: khớp theo độ dài list ngắn hơn, danh sách dài bị "cắt bớt" cho bằng.
- **Longest List** (mặc định): khớp theo độ dài list dài hơn, item cuối của list ngắn được lặp lại để bù cho phần thừa.
- **Cross Reference**: khớp **mọi item của list 1 với mọi item của list 2** (tích Descartes) — đây chính là cách đúng để tạo lưới 2 chiều (hoặc 3 chiều nếu Cross Reference thêm 1 chiều z nữa).
Grasshopper có 3 component tương ứng (Shortest List, Longest List, Cross Reference) trong panel List của tab Sets, dùng để ép kiểu ghép nối thủ công khi cần.

### 2.2.3 Repeat Data
**Repeat Data** (Sets > Sequence) kéo dài 1 dãy số cho đủ độ dài chỉ định bằng cách lặp lại tuần hoàn dữ liệu gốc: input D = dãy gốc, input L = độ dài output mong muốn. Ví dụ (2,6,1) với L=5 → (2,6,1,2,6). Ứng dụng minh hoạ khá dài: dựng 1 surface lượn sóng bằng cách chia 2 đường cong bằng Divide Curve, nối Line giữa các điểm tương ứng, lấy trung điểm mỗi Line bằng Point on Curve, dịch trung điểm theo trục z bằng Move, dựng cung **Arc 3Pt** (Curve > Primitive) qua 3 điểm (điểm trên Curve 01, trung điểm đã dịch, điểm trên Curve 02), rồi **Loft** (Surface > Freeform) qua tập cung đó để ra surface. Muốn bề mặt gợn sóng lên xuống thay vì phẳng đều, thay slider cố định ở input dịch z bằng output của Repeat Data (dãy xen kẽ 2 giá trị, vd 3 và 4) — kết quả là surface có biên dạng lượn sóng theo mẫu lặp.

Component **Loft Options** (Surface > Freeform) nối vào input O của Loft cho phép chỉnh: rebuild số điểm điều khiển (Rbd, dùng khi số curve tiết diện quá ít để tạo surface mượt), đóng loft (close), chỉnh seam, và kiểu loft qua 1 số nguyên: 0=Normal, 1=Loose, 2=Tight, 3=Straight, 4=Developable, 5=Uniform.

### 2.2.4 Random / Construct Domain
**Random** (Sets > Sequence) sinh N số ngẫu nhiên trong 1 miền số (domain) R; input S là **seed** (hạt giống) — đổi seed sẽ ra bộ số ngẫu nhiên khác dù các input khác giữ nguyên (cùng 1 seed luôn cho cùng 1 kết quả — tính "giả ngẫu nhiên" có thể tái lập). Mặc định sinh số thực; right-click chọn "Integer Numbers" để chỉ sinh số nguyên. **Construct Domain** (Maths > Domain) định nghĩa 1 miền số bằng 2 giá trị min/max, dùng làm input R cho Random.

### 2.2.5 Range
**Range** (Sets > Sequence) chia đều 1 miền số (D) thành N đoạn bằng nhau, sinh ra N+1 giá trị (bao gồm cả 2 đầu mút của domain) — khác Series ở chỗ Range luôn "phủ kín" trọn 1 domain cho trước thay vì tự cộng dồn bước nhảy.

## 2.3 Mathematical Functions (Hàm số toán học)

Component **Evaluate F(X)** (Maths > Script) dùng để định nghĩa dãy số tuân theo 1 hàm toán học, không chỉ sinh dãy số suông.

### 2.3.1 Functions of one variable (Hàm 1 biến)
Hàm 1 biến có miền xác định (domain) trên trục x và miền giá trị (codomain) trên trục y — mỗi giá trị xi input cho ra 1 giá trị yi output. Quy trình dựng: (1) định nghĩa hàm bằng cách double-click vào Evaluate F(X) để mở **Expression Designer** — gõ biểu thức (vd `x^2` cho parabol y=x², toán tử luỹ thừa nằm trong thư viện Operators; danh sách đầy đủ hàm số xem qua nút `f:N>R`), hoặc gõ công thức vào 1 Panel rồi nối vào input F của Evaluate; (2) định nghĩa domain bằng Construct Domain + Range để sinh dãy giá trị x đầu vào. Output r của Evaluate là dãy y tương ứng. Ghép cặp (x,y) làm input cho **Construct Point** rồi vẽ đường cong đi qua các điểm bằng **Interpolate Curve** (Curve > Spline) sẽ ra hình đồ thị của hàm số ngay trên canvas Rhino.

### 2.3.2 Functions of two variables (Hàm 2 biến)
Hàm 2 biến có domain là tập điểm trên mặt phẳng XY, codomain là giá trị trên trục z — mỗi cặp (xi,yi) cho 1 giá trị zi. Quy trình tương tự nhưng domain 2 chiều nên 2 danh sách xi, yi phải được **Cross Reference** trước khi đưa vào Evaluate (để tạo đủ mọi tổ hợp cặp điểm trên lưới). Ví dụ minh hoạ: paraboloid z = -((x²+y²)/4)+4. Sau khi có lưới điểm (xi,yi,zi), dùng component **SrfGrid** (Surface > Freeform, xem thêm ở mục 3.6) để dựng surface từ lưới điểm — input U của SrfGrid cần biết số điểm theo 1 chiều, lấy qua List Length. Sách còn dẫn 1 ví dụ thực tế công phu: mái nhà British Museum Great Court Roof, hình dạng là tổng 3 phương trình 2 biến (trích nguồn: C.J.K. Williams, 2001) — sách không giải thích chi tiết từng số hạng, chỉ minh hoạ để cho thấy hàm 2 biến ứng dụng được vào kiến trúc thật.

## 2.4 Conditions (Điều kiện)

Evaluate F(X) không chỉ dựng đường cong/mặt cong mà còn dùng để lập **điều kiện logic** trong thuật toán.

### 2.4.1 Logical operators / Boolean values
Điều kiện được xây từ biến số và toán tử so sánh: bằng (=), nhỏ hơn (<), lớn hơn (>) — nằm trong panel Operators của tab Maths; các toán tử khác (khác, nhỏ hơn hoặc bằng...) có trong chính Expression Designer. Evaluate trả về giá trị **Boolean** (True/False). Ví dụ ứng dụng: tính bán kính từng vòng tròn bằng **Deconstruct Arc** (Curve > Analysis), so với điều kiện R > 8, vòng thoả điều kiện thì extrude 20 đơn vị, không thoả thì bị cull khỏi danh sách.

Thay vì Evaluate, có thể dùng thẳng component **Dispatch** (Sets > List): so 1 list dữ liệu với 1 list Boolean tương ứng, trả về 2 output — list A (các item ứng True) và list B (các item ứng False) — tiện hơn khi cần xử lý riêng cả 2 nhánh (đúng/sai) thay vì chỉ giữ nhánh đúng như Cull Pattern.

Sách cũng chỉ mẹo dùng **Concatenate** (Sets > Text) để ghép chuỗi văn bản làm điều kiện "động" — gõ `"x>"` vào 1 Panel (không Enter, xác nhận bằng OK) rồi nối với 1 Number Slider để tạo chuỗi kiểu `"x>8.0"`, sau đó dùng chuỗi này làm input F của Evaluate — cho phép thay đổi ngưỡng so sánh bằng slider thay vì gõ tay số cố định trong Expression Designer.

### 2.4.2 Conditional: if/then
Evaluate hỗ trợ cú pháp điều kiện `if(test, A, B)` — trả về A nếu test đúng, B nếu sai. A/B không nhất thiết là số, có thể là chuỗi văn bản (vd trả về "cat" khi điều kiện sai).

### 2.4.3 Other operators: Contains
Toán tử `Contains(s, "p")` kiểm tra chuỗi p có nằm trong tập dữ liệu s không, trả Boolean. Có thể dùng để kiểm tra 1 danh sách hình học (qua container Geometry, đưa qua Panel làm "cầu nối" chuyển thành text mô tả) có chứa đối tượng loại "line" hay không — Panel mô tả kiểu hình học bằng text (vd "Line"), Contains so khớp text đó.

## 2.5 Remapping numbers / Attractors (Ánh xạ lại số & điểm hút)

**Remap Numbers** (Maths > Domain) chuyển đổi tỉ lệ 1 dãy số từ miền gốc [A,B] sang miền đích [A',B'] — input V (list cần remap), S (domain gốc, thường lấy tự động bằng component **Bounds**, Maths > Domain), T (domain đích, dùng Construct Domain). Ví dụ (2,4,6,8) domain gốc [2,8] remap sang [0,1] → (0, 0.33, 0.67, 1.0).

### 2.5.1 Attractors (Điểm/đường hút)
**Attractor** là 1 thực thể hình học (điểm, đường...) dùng để chi phối/biến đổi hình học xung quanh nó theo khoảng cách — càng gần attractor ảnh hưởng càng mạnh. Đây là kỹ thuật rất quan trọng trong thiết kế tham số. Ví dụ minh hoạ: dựng lưới vòng tròn (Circle, Primitive > Curve, bán kính 1, dàn lưới 2 chiều bằng Move+Series), đo khoảng cách từ 1 điểm attractor (set từ Rhino) tới tâm mỗi vòng tròn, remap khoảng cách đó về domain [0,1] để làm hệ số scale, rồi dùng **Scale** (Transform > Euclidean, input C = tâm scale, F = hệ số) để co giãn từng vòng tròn theo khoảng cách tới attractor — vòng gần attractor bị scale nhỏ gần 0 (không được scale bằng đúng 0 vì sẽ mất hình), vòng xa giữ nguyên kích thước gần 1. Có thể dùng **Boundary** (Surface > Freeform) biến các curve thành surface phẳng, và trực quan hoá hệ số scale bằng màu gradient qua component **Gradient** (Params > Input, right-click chọn preset màu).

Attractor cũng có thể là 1 đường cong: dùng **Curve Closest Point** (Curve > Analysis) đo khoảng cách D từ tâm mỗi hình đến điểm gần nhất trên đường cong đó, rồi remap tương tự. Giá trị remap còn dùng để **di chuyển** (không chỉ scale) — vd dịch tâm điểm theo trục z, đổi domain đích thành [3,15] để khuếch đại hiệu ứng.

Có thể dùng **nhiều attractor cùng lúc**: cộng các khoảng cách riêng lẻ từ mỗi attractor bằng component **Addition** (Maths > Operators) trước khi remap. Đảo ngược 2 đầu domain đích (vd [0.82, 0.01] thay vì [0.01, 0.82]) sẽ đảo chiều hiệu ứng (gần attractor to ra thay vì nhỏ đi). Để giới hạn phạm vi ảnh hưởng của attractor, có thể chia khoảng cách cho 1 số tuỳ ý (thu hẹp phạm vi tác động) và dùng component **Minimum** (Maths > Util) để chặn hệ số scale không vượt quá 1 ngưỡng nhất định (vd không cho lớn hơn 0.8) — các giá trị vượt ngưỡng sẽ tự động được thay bằng đúng ngưỡng đó.
