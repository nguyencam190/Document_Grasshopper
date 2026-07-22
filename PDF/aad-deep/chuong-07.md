# Chương 7 — Loops (Vòng lặp và Fractal)

Chương ngắn nhưng quan trọng về mặt khái niệm: giải thích vì sao Grasshopper (theo logic mặc định) **không cho phép vòng lặp**, và giới thiệu 2 plug-in phá vỡ giới hạn đó (HoopSnake, Loop) để dựng thuật toán đệ quy (recursive) và fractal.

## Khái niệm mở đầu: Recursive algorithms (Thuật toán đệ quy)

Thuật toán đệ quy định nghĩa giá trị input của bước sau **bằng chính output của bước trước** — lặp lại N lần, mỗi lần lặp (iteration) sinh ra 1 output. Lần lặp đầu tiên bắt đầu từ **edge condition** (điều kiện biên) — 1 hoặc nhiều phần tử khởi tạo không định nghĩa theo kiểu đệ quy (số, hình học, dữ liệu cho sẵn); các lần lặp sau dựa vào vòng dữ liệu (data loop). Thuật toán đệ quy rất mạnh vì chỉ cần 1 quy trình ngắn gọn, lặp lại nhiều lần, đã tạo ra vô số hình dạng phức tạp.

Ví dụ kinh điển: dãy **Fibonacci**, định nghĩa đệ quy Fₙ = Fₙ₋₁ + Fₙ₋₂, với điều kiện biên F₀=0, F₁=1 → dãy 0,1,1,2,3,5,8,13,21,34,55,89...

Sách minh hoạ đệ quy hình học bằng 1 ví dụ chia đường thẳng lặp 3 lần:
1. Vẽ 1 đường thẳng — điều kiện biên "line 0".
2. Chia đường thành 3 đoạn (segment 0, 1, 2).
3. Dịch đoạn giữa (segment 1) đi 3 đơn vị theo trục y → ra "line 1".
4. Lặp lại bước 2–3 dùng chính "line 1" vừa tạo (thay vì "line 0").

Nếu chuyển thẳng quy trình này thành sơ đồ Grasshopper thông thường, chỉ thực hiện được **đúng 1 lần lặp** — muốn lặp 3 lần cần 1 "data loop" (vòng dữ liệu), nhưng điều này **mâu thuẫn với nguyên tắc luồng chảy trái→phải** đã học ở mục 1.6: Grasshopper không cho phép nối dây output của 1 component quay ngược lại input của component đứng trước nó. Theo đúng logic mặc định, cách duy nhất để "lặp" là **thủ công lặp lại chính sơ đồ đó 3 lần** trên canvas (không phải vòng lặp thật). May mắn là có 2 plug-in giải quyết được vấn đề này: **HoopSnake** và **Loop**.

## 7.1 Loops in Grasshopper: HoopSnake component

**HoopSnake** là plug-in do Yannis Chatzikonstantinou phát triển, tải miễn phí (yconst.com/software/hoopsnake, hoặc food4rhino.com). Sau khi cài, xuất hiện 1 component mới trong tab **Extra**. HoopSnake cho phép "phá vỡ" nguyên tắc trái→phải, thực hiện vòng lặp thật.

Cách hoạt động, áp lại ví dụ chia đường ở trên:
1. Đường thẳng gốc (line 0, set từ Rhino qua Curve container) là điều kiện biên — nối vào input **S** của HoopSnake; output **F** của HoopSnake ban đầu = chính input S (không đổi gì ở lần đầu).
2. Mọi input trước đây nối trực tiếp vào curve gốc (input C của Divide Curve và Shatter trong ví dụ trước) giờ phải nối vào **output F** của HoopSnake (không nối thẳng vào curve gốc nữa).
3. Output G của component Move (bước cuối cùng của quy trình) được nối ngược lại vào input **D\*** của HoopSnake — đây chính là dây "vòng lặp" (feedback loop).
4. Input **B\*** quy định số lần lặp cần thực hiện (thường dùng Number Slider).
5. Output **C** trả về **kết quả tích luỹ của mọi lần lặp**, mỗi lần lặp là 1 branch riêng trong Data Tree.

HoopSnake hoạt động như 1 "cỗ máy" (engine) cần được **khởi động thủ công**: double-click vào component để mở control panel, có 2 nút: **Step** (thực hiện đúng 1 lần lặp) và **Auto Loop All** (chạy hết số lần lặp đã đặt ở B\*). Output **I** trả về số đếm lần lặp hiện tại; khi chạy Auto Loop All, quá trình dừng lại khi bộ đếm bằng đúng giá trị B\*.

## 7.2 Fractals (Hình học Fractal)

**Fractal** là hoạ tiết **tự đồng dạng qua nhiều tỉ lệ** (self-similar across scales) — sinh ra bằng cách lặp lại 1 quy trình đơn giản qua vòng lặp (feedback loop), lặp ở tỉ lệ ngày càng nhỏ để tạo hình dạng phức tạp.

Ví dụ kinh điển: **đường cong bông tuyết Koch (Koch snowflake curve)**, nghiên cứu bởi nhà toán học Thuỵ Điển Helge von Koch (1870–1924) — 1 trong những curve fractal được mô tả sớm nhất. Cách dựng: bắt đầu từ 1 đoạn thẳng (step 0); thay đoạn 1/3 giữa bằng 2 đoạn bằng nhau ghép thành 2 cạnh của 1 tam giác đều (step 1); lặp lại quy tắc này cho mỗi đoạn thẳng con ở mỗi bước tiếp theo (step 2, 3, 4...). Về bản chất toán học, đường Koch là **giới hạn của 1 chuỗi xấp xỉ vô hạn** — theo trích dẫn sách dẫn từ Rudy Rucker: "chúng ta có thể coi giới hạn của quá trình vô hạn này là 1 đường cong thực sự tồn tại, nếu không phải trong không gian vật lý, thì ít nhất như 1 đối tượng toán học". Sách trình bày sơ đồ Grasshopper cụ thể dựng Koch curve bằng HoopSnake (dùng hệ số hình học `(x/2)*sqrt(3)` liên quan tam giác đều).

### 7.2.1 Further Study: Practical Fractals (Nghiên cứu thêm: Fractal ứng dụng thực tế)
Sách dẫn ví dụ công trình thực tế: **Serpentine Pavilion 2002** của Toyo Ito và Cecil Balmond — dù kết cấu bề mặt trông ngẫu nhiên phức tạp, thực chất bắt nguồn từ 1 quy tắc rất đơn giản. Sách trích trực tiếp lời Cecil Balmond mô tả thuật toán: chia cạnh hình vuông theo tỉ lệ 1/2 đến 1/3, các đường không giao nhau buộc phải "vượt ra ngoài" hình vuông gốc để tạo hình vuông mới tiếp tục quy tắc — kéo dài các đường sẽ tạo ra vô số điểm giao cắt, một số là kết cấu chịu lực chính, một số là giằng phụ, phần còn lại tạo hoạ tiết bề mặt "ngẫu nhiên có kiểm soát" trên toàn khối hộp.

### 7.2.2 Tridimensional fractals (Fractal 3 chiều)
Fractal 3D tuân theo cùng logic fractal 2D. Ví dụ minh hoạ: dựng fractal 3D từ 3 điểm gốc, lặp 3 lần theo quy trình: (1) dựng mesh tam giác qua 3 điểm bằng **Delaunay Triangulation**; (2) dịch trọng tâm mỗi mặt tam giác theo 1 hướng; (3) dùng điểm trọng tâm đã dịch cùng các đỉnh cũ để dựng lại 3 mặt tam giác mới bằng Delaunay Triangulation — lặp lại toàn bộ quy trình qua n lần lặp để ra hình fractal 3D ngày càng phức tạp (sách minh hoạ kết quả sau 3 lần lặp).

## 7.3 Loops in Grasshopper: Loop component

Giải pháp thay thế cho HoopSnake: plug-in **Loop** do Antonio Turiello phát triển (Generative Designer, Independent Researcher, Authorized Rhinoceros Trainer — food4rhino.com/project/loop). Phương pháp Loop dùng 3 component chính: **Rnd, Store, Loop**.

- **Rnd** và **Store** là 2 phần thuộc plug-in **Generation** (bộ công cụ mở rộng hỗ trợ khám phá/animate/chế tạo hình dạng sinh học tính toán — generative shape). **Rnd** sinh 1 dãy số giả ngẫu nhiên, cập nhật mỗi khi có **Timer** (Params > Util) chạy hoặc khi thực hiện lệnh **Recompute** (Solution > Recompute). **Store** lưu giữ dữ liệu giữa các lần cập nhật.
- **Loop** thực hiện việc lặp bằng cách **thay input ban đầu của 1 quy trình bằng chính output cuối cùng** của quy trình đó (đúng cơ chế feedback loop).

Ví dụ minh hoạ: **Rnd** sinh 3 giá trị nội suy ngẫu nhiên trong 1 domain — 2 giá trị đầu là toạ độ tham số (u,v) của 1 điểm P trên mặt cầu ban đầu, giá trị thứ 3 là bán kính của 1 mặt cầu mới (lưu trong Store) tiếp xúc với mặt cầu gốc tại điểm P(u,v). Component Loop (nối với Timer) cập nhật lại Rnd, thay input S đã reparameterize của Evaluate Surface bằng output G của Move — theo logic này, mỗi lần lặp sinh ra 1 mặt cầu mới và lưu lại, tạo ra nhiều cấu hình khác nhau: cầu màu tối bán kính nhỏ kết hợp cầu màu sáng bán kính lớn hơn, tạo bố cục ngẫu nhiên có kiểm soát.
