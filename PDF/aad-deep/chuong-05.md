# Chương 5 — Skins: Advanced Data Management (Quản lý dữ liệu nâng cao — Data Tree)

Chương then chốt của cả cuốn sách: giới thiệu **Data Tree** — cấu trúc dữ liệu phân cấp mà Grasshopper dùng để lưu mọi thứ. Không hiểu Data Tree thì không dựng được các pattern/skin phức tạp cho bề mặt kiến trúc. Chương dùng ví dụ mở đầu để lộ vấn đề, sau đó dạy công cụ xử lý, rồi áp dụng vào 2 ví dụ pattern lớn (hình chữ nhật và lục giác) và kỹ thuật sắp xếp (sorting).

## Vấn đề mở đầu: vì sao thuật toán "đúng logic" vẫn ra sai kết quả

Ví dụ: có 4 mặt tam giác từ Rhino, muốn nối 1 polyline duy nhất qua 12 đỉnh. Tách đỉnh bằng **Deconstruct Brep**, nối **Polyline** — nhưng kết quả không phải 1 polyline 12 đỉnh mà là **4 polyline riêng biệt**, mỗi cái 3 đỉnh. Xem output qua Panel sẽ thấy: dây nối ra khỏi Deconstruct Brep là **dây đứt nét (dashed)**, và dữ liệu tách thành 4 nhóm con: `{0;0}`, `{0;1}`, `{0;2}`, `{0;3}` — mỗi nhóm chứa 3 điểm (đỉnh của 1 tam giác).

**Nguyên tắc**: Grasshopper lưu dữ liệu theo logic **Cha–Con (Parent-Child)** — mỗi "cha" (ở đây là 1 mặt tam giác) sinh ra 1 nhóm con riêng (subset) chứa các "con" của nó (3 đỉnh). Có thể hình dung cấu trúc này như 1 **cây (tree)**: các nhóm con gọi là **branch** (nhánh), mỗi item trong nhánh có 1 **index**. Khi Grasshopper chỉ xử lý dữ liệu đơn giản (không đa nhánh), Data Tree gần như "vô hình" — chỉ có 1 nhánh duy nhất gọi là **trunk** (thân).

Hai quy tắc nền tảng của Data Tree:
1. **Branch là khối kín (watertight)** — không thể tự động nối dữ liệu giữa 2 branch khác nhau. Mọi phép toán áp lên cả cây sẽ tác động **riêng biệt trên từng branch** — đây chính là lý do Polyline chỉ nối được trong từng tam giác (branch), không nối xuyên qua 4 tam giác.
2. **Data Tree có thể chủ động tái cấu trúc** để đạt kết quả mong muốn — dùng các component chuyên biệt.

## 5.1 Manipulating the Data Tree (Thao tác với Data Tree)

4 component cốt lõi để chỉnh cấu trúc cây, nằm trong panel Tree (Sets tab): **Flatten Tree, Unflatten Tree, Graft Tree, Flip Matrix**.

### 5.1.1 Flatten Tree
**Flatten Tree** (Sets > Tree) "làm phẳng" 1 Data Tree — xoá hết thông tin phân nhánh, gộp toàn bộ dữ liệu vào 1 trunk duy nhất `{0}`. Sau khi flatten, dây đứt nét sẽ chuyển thành **dây liền nét**. Cách dùng: nối output cần flatten vào input T của Flatten Tree. Áp dụng vào ví dụ mở đầu: flatten output V của Deconstruct Brep trước khi nối vào Polyline sẽ ra đúng 1 polyline 12 đỉnh. Mỗi input/output của mọi component đều có sẵn tuỳ chọn Flatten ngay trong context menu (right-click) — khi bật, sẽ hiện 1 mũi tên **hướng xuống** cạnh input/output đó.

### 5.1.2 Unflatten Tree
Ngược lại Flatten: **Unflatten Tree** (Sets > Tree) tái cấu trúc 1 list đã bị làm phẳng trở lại thành các branch, dựa theo 1 "cây mẫu" (guide Data Tree, input G). Input T là list phẳng cần cấu trúc lại. **Chỉ hoạt động nếu list phẳng có cùng số lượng dữ liệu với cây mẫu.**

### 5.1.3 Graft Tree
**Graft Tree** (Sets > Tree) tạo **1 branch riêng cho mỗi item** trong 1 list phẳng — list N item sẽ trở thành cây N branch, mỗi branch chỉ chứa đúng 1 item. Graft Tree hữu ích để "ghép cặp" đúng các bộ dữ liệu tương ứng nhau. Ví dụ: 2 surface, mỗi cái có 4 cạnh (edge) tách bằng Deconstruct Brep — muốn Loft 4 lần giữa từng cặp cạnh tương ứng (a-a', b-b', c-c', d-d'), phải **Graft cả 2 luồng dữ liệu trước khi Merge**. Nếu chỉ Merge mà không Graft, Loft sẽ chạy qua toàn bộ 8 curve theo đúng 1 thứ tự liên tục (a'-b'-c'-d'-a-b-c-d) — sai hoàn toàn ý đồ. Mỗi input/output cũng có sẵn tuỳ chọn Graft trong context menu, hiện mũi tên **hướng lên** khi bật.

### 5.1.4 Flip Matrix
**Flip Matrix** (Sets > Tree) hoán đổi hàng và cột trong cây dữ liệu dạng ma trận — nói cách khác, hoán đổi vai trò giữa **item** và **branch**. Ví dụ: 3 vòng tròn chia 10 điểm mỗi cái bằng Divide Curve → cây gốc có 3 branch (ứng 3 vòng tròn), mỗi branch 10 item (điểm). Muốn nối các điểm tương ứng nhau giữa 3 vòng tròn (A-A'-A'', B-B'-B''...) thay vì nối các điểm trong cùng 1 vòng tròn, phải Flip Matrix trước — cây kết quả có 10 branch, mỗi branch 3 điểm (1 từ mỗi vòng tròn). Có thể xem trực quan cấu trúc cây bằng component **Param Viewer** (Params > Util, double-click để mở).

## 5.2 Skins (Xây dựng hoạ tiết bề mặt / skin)

### 5.2.1 Rectangular based pattern (Pattern lưới chữ nhật)
Ví dụ lớn đầu tiên: dựng pattern 3D kiểu **kim tự tháp cụt (pyramidal frustum)** trên 1 surface — ghép từ 3 nhóm surface con A (khung viền), B (mặt bên xiên), C (nắp trên).

Quy trình:
1. Set + reparameterize surface gốc từ Rhino; chia sub-surface bằng **Isotrim-SubSrf**; tách face và edge của từng sub-surface bằng **Deconstruct Brep** (đặt tên container SubSurfaces và Curves 01 cho dễ theo dõi).
2. Nối 4 cạnh mỗi sub-surface thành 1 polyline, offset polyline đó "áp" theo surface bằng component **Offset on Srf** (Curve > Util — input C=curve cần offset, D=khoảng cách offset, S=surface để offset bám theo).
3. Loft giữa cạnh gốc (Curves 01) và cạnh đã offset (đã Explode Curve thành từng đoạn riêng — Curves 03) để tạo khung viền **A**. Trước khi Loft, phải **Merge sau khi Graft** 2 luồng dữ liệu (như 5.1.3), rồi **Simplify** cấu trúc cây bằng **Simplify Tree** (Sets > Tree, hoặc bật Simplify ngay trong context menu input/output) để loại bỏ các cấp branch dư thừa/trùng lặp không cần thiết.
4. Mặt bên **B**: tính trung điểm mỗi sub-surface bằng Evaluate Surface (MD Slider 0.5;0.5) → scale Curves 03 quanh trung điểm đó bằng hệ số F (Number Slider) → dịch curve đã scale theo hướng normal (N-output Evaluate Surface, dùng nhân vô hướng) → lưu thành Curves 04. Loft giữa Curves 03 và Curves 04 (chỉ cần Graft, KHÔNG Simplify lần này) tạo mặt bên B.
5. Nắp **C**: dùng **Edge Surface** (Surface > Freeform) nối 4 cạnh Curves 04 (tách bằng List Item, có thể zoom-in thêm output param thay vì đặt 4 List Item riêng).

Toàn bộ pattern điều khiển được qua các tham số: khoảng cách offset, hệ số scale, hệ số dịch, hoặc chính surface gốc. Sách còn minh hoạ dùng **attractor point** (set từ Rhino) để làm khoảng cách offset (độ rộng khung A) **thay đổi động theo khoảng cách tới điểm hút** — đo khoảng cách từ điểm hút tới tâm mỗi sub-surface, remap khoảng cách đó (qua Bounds lấy domain nguồn + Construct Domain định domain đích, vd [0.2, 1.2]) rồi nối kết quả (đã Graft) thẳng vào input D của Offset on Srf — khung càng gần điểm hút càng hẹp lại.

### 5.2.2 Hexagonal based pattern (Pattern lưới lục giác)
Ví dụ thứ 2: cùng logic kim tự tháp cụt nhưng trên lưới **lục giác** thay vì chữ nhật — lưới lục giác dùng plug-in **LunchBox**, component **Hexagon Cells** (LunchBox > Panels, input: surface + số chia U/V) — output **Cells** (đa giác lục giác dạng polyline khép kín) và **Centers** (tâm mỗi ô). Vì lưới áp lên surface hình chữ nhật, các ô ở biên sẽ không phải lục giác đủ 6 cạnh (chỉ 4 hoặc 5 cạnh) — cần lọc bỏ. Cách lọc: **Explode Curve** mỗi ô ra các đoạn, đếm số đoạn bằng List Length (theo từng branch của cây), so sánh điều kiện `x=6` bằng Evaluate → dùng kết quả Boolean làm P-input cho **Cull Pattern**, lọc bỏ những ô không đủ 6 cạnh (phải Flatten input L của Cull Pattern trước để khớp cấu trúc cây với P). Làm tương tự để lọc luôn danh sách tâm ô tương ứng.

Phần còn lại lặp lại logic của pattern chữ nhật (Loft khung, scale+dịch tạo mặt bên, ghép nắp) nhưng nắp lục giác 6 cạnh **không dựng được bằng 1 surface duy nhất** (Edge Surface chỉ nhận tối đa 4 cạnh) nên phải Loft riêng 2 cặp cạnh đối diện (2-4 và 1-5). Vì các cạnh lục giác có chiều ngược nhau (do polyline lục giác vẽ theo chiều ngược kim đồng hồ), phải **Flip Curve** một số cạnh trước khi Loft, nếu không mặt sẽ bị vặn xoắn. Cũng dùng được attractor point tương tự (5.2.1) để điều khiển động độ rộng khung — sách minh hoạ 2 trường hợp domain B đảo ngược nhau (A=0.3,B=0.8 và A=0.8,B=0.3) cho hiệu ứng ngược nhau hoàn toàn.

### 5.2.3 Further Study: Responsive facade (Nghiên cứu thêm: mặt dựng phản ứng)
Sách dẫn ví dụ thực tế: hệ che nắng **Masharabiya** (dạng lưới che truyền thống Ả Rập) của toà tháp trụ sở ADIC tại Abu Dhabi, do công ty Aedas thiết kế — thuật toán đơn giản hoá của mặt dựng này được cung cấp qua mã QR trong sách (không đọc được nội dung cụ thể từ text, chỉ có ảnh + link tham khảo aedas.com).

### 5.2.4 Weaving (Đan sợi — Warp and Weft)
Ứng dụng kỹ thuật Data Tree để mô phỏng **hoạ tiết đan sợi 3D** (kiểu dệt vải, gồm 2 hướng sợi: **warp** — sợi dọc, **weft** — sợi ngang) trên 1 surface, số lượng sợi khai báo theo cả 2 hướng U và V. Nguyên lý: dịch chuyển 1 lưới điểm luân phiên lên/xuống theo vector pháp tuyến (dương/âm xen kẽ) để mô phỏng sợi đan lồng nhau.

**WARP**: chia lưới điểm bằng Divide Surface trên surface đã reparameterize — cây kết quả có U+1 branch (mỗi branch là 1 cột điểm theo hướng V). Nếu dịch trực tiếp theo cấu trúc cây này, mọi điểm ĐẦU mỗi cột sẽ đều được nâng lên giống nhau — SAI với logic dệt thật (cần luân phiên: sợi 1 lên, sợi 2 xuống...). Cách sửa: **Flatten** hết list điểm trước khi Move, dịch bằng 1 dãy hệ số nhân vô hướng luân phiên dương/âm nhân với vector pháp tuyến — dịch xong mới **Unflatten Tree** trở lại (dùng chính list điểm gốc trước khi flatten làm guide G) để khôi phục đúng cấu trúc cột, sau đó dùng **Interpolate** nối từng cột thành 1 sợi cong liên tục (nếu không Unflatten trước, Interpolate sẽ nối lộn xộn xuyên hết mọi cột thành 1 đường duy nhất — sai).

**WEFT**: lặp lại logic tương tự theo hướng còn lại — không cần dựng lại toàn bộ thuật toán, chỉ cần **Flip Matrix** ma trận điểm gốc rồi tái sử dụng phần cuối thuật toán warp. Vì sợi dọc và sợi ngang không được chạm nhau tại điểm giao, vector dịch của weft phải **ngược chiều (Negative component)** so với warp. Nếu bỏ qua bước Negative, 2 lưới curve (warp + weft) sẽ tạo thành 1 mạng lưới đan xen thật — có thể dùng **Network Surface** để dựng luôn 1 surface dệt từ mạng lưới đó thay vì chỉ hiển thị đường.

## 5.3 Sorting strategies using Data Tree (Chiến lược sắp xếp bằng Data Tree)

Ví dụ minh hoạ: 24 điểm phân bố ngẫu nhiên trong lưới 3×5 (không theo thứ tự hàng/cột), muốn dựng surface qua **Surface From Points** (Surface > Freeform) — nhưng component này **đòi hỏi điểm phải được sắp theo đúng thứ tự hàng/cột**, nếu không surface sẽ bị méo/rối (sách minh hoạ hình surface lỗi khi input điểm ngẫu nhiên).

Chiến lược sắp xếp lại gồm 2 bước:

**BƯỚC 1 — Sắp theo trục x (chia cột)**: dùng **Sort List** (Sets > List) — input A là list điểm cần sắp, input K (khoá sắp xếp) lấy từ toạ độ x của từng điểm (qua component **Deconstruct**, Vector > Point). Kết quả: các điểm được nhóm đúng theo 4 cột x, nhưng bên trong mỗi cột vẫn ngẫu nhiên theo y. Output của Sort List là 1 list **phẳng** (trunk duy nhất) — muốn tách thành 4 branch (mỗi branch 1 cột, 6 điểm), dùng component **Allocate N**, thuộc plug-in **Tree8** (do Jissi Choi phát triển, tải miễn phí từ website Grasshopper — 1 phần của bộ công cụ STRAUTO cho mô hình kết cấu tham số dùng SAP2000/MIDAS). Allocate N chia đều 1 list phẳng thành các branch có số item cố định (vd 6 item/branch).

**BƯỚC 2 — Sắp theo trục y trong mỗi cột**: lặp lại Sort List, lần này dùng toạ độ y làm khoá K, áp riêng trên mỗi branch (mỗi cột) đã tách ở bước 1.

Sau 2 bước, điểm đã được sắp đúng thứ tự cả x lẫn y, dùng làm input P cho Surface From Points (đặt input P ở chế độ **Flatten**) để ra surface đúng như mong muốn. Có thể tiếp tục chỉnh toạ độ z của từng điểm (vd qua Rhino Gumball) để surface biến đổi theo — kết luận chương bằng minh hoạ: chỉ cần đổi z của các điểm đã sắp, surface tự động cập nhật hình dạng tương ứng.
