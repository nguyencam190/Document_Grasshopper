# Dự án: Grasshopper Voronoi Pattern

Dự án Rhino + Grasshopper tạo pattern Voronoi dạng **hoa hướng dương / xoắn ốc (phyllotaxis)**.

## Cấu trúc
- `Video/Voronoi Pattern (Grasshopper Tutorial).mp4` — video tutorial gốc (Parametric House, ~15 phút, 720p).
- `Video/voronoi-alpha-1-wheel-system-youtube_2USQihHa.mp4` — showcase **vành xe Voronoi** (Handlebar3D,
  ~16 phút) = **MỤC TIÊU CUỐI CÙNG** user hướng tới. KHÔNG phải tutorial (thuật toán khổng lồ, cố tình khó copy).
- `Phu_de/*.srt` — phụ đề tiếng Anh cho từng video (user cung cấp; tôi đọc .srt để nắm lời giảng, không nghe audio được).
- `docs/voronoi-alpha-wheel-phan-tich.md` + `docs/wheel-ref/*` — phân tích video vành xe + ảnh kết quả.
- `docs/voronoi-wheel-grasshopper-canluu.md` — 13 nguyên lý Grasshopper cần hiểu từ video vành xe
  (GH là tool-builder, Group/Cluster, Attractor, Graph Mapper, Data Trees, Design↔Surface Toggle,
  Voronoi cần Boundary, bake nhiều loại...). Kèm "cây kỹ năng" ưu tiên học.
- `docs/voronoi-sunflower-pattern.md` — **tài liệu phân tích đầy đủ**: sơ đồ dây, danh sách
  component, bảng slider, hướng dẫn dựng từng bước. Xem file này trước khi làm việc liên quan pattern.
- `docs/voronoi-flow-diagram.svg` + `.png` — sơ đồ luồng trực quan (7 bước, theme-aware).
- `docs/voronoi-frame-by-frame.md` — **timeline chi tiết từng giây** (mốc [mm:ss], giá trị slider theo
  từng bước, bảng giá trị chốt). Phân tích qua 918 frame 1fps + 185 keyframe scene-change.
- `docs/voronoi-giai-thich-chi-tiet.md` — **giải thích chức năng + cách làm + ý nghĩa** từng giai đoạn
  (mức người mới), kèm bảng "vặn nút gì đổi gì".
- `docs/voronoi-build-steps.svg` + `.png` — **storyboard kéo & nối graph 9 bước** (mỗi khung tô xanh
  component mới thả, nhãn cổng cần nối) — dùng khi thực hành dựng trên canvas.
- `docs/voronoi-loi-giang-tomtat.md` — **tóm tắt LỜI GIẢNG** (từ phụ đề `Phu_de/*.srt`). Bổ sung nhiều
  điểm chỉ nghe mới biết (xem "điểm bổ sung" dưới).

## Bổ sung từ lời giảng (phụ đề) — ưu tiên hơn suy đoán từ hình
- **Polar Count phải là SỐ CHẴN** (để chia đôi /2 ở các Series sau).
- **Maelstrom Angle mặc định RADIAN** → chuột phải đổi sang Degrees (~50–120°). First < Second (bán kính trong/ngoài).
- **Dispatch mục đích = tạo KHE HỞ** giữa các dải (không chỉ giảm mật độ); true-false-false → khe to hơn.
- **Voronoi cần Flatten** điểm trước khi nối.
- **Thực chất ~3 lần Cull**: (1) Cull Index=0 xoá ĐIỂM trùng ở tâm (trước Voronoi); (2) Cull Series [0,12,…] xoá vòng Ô tâm; (3) Cull Series [11,23,…] xoá vòng Ô ngoài.
- **Series dùng Expression**: Step=`x/2`, Count=`x/2`, Start(ngoài)=`x/2−1` — nối số chia N vào input.
- Đây là **bản ĐƠN GIẢN HOÁ**, không phải Fibonacci thật.
- (Tôi không nghe được audio; đọc được vì có file phụ đề .srt.)

## Tóm tắt kỹ thuật
Voronoi này KHÔNG ngẫu nhiên. Điểm gieo được bố trí theo lưới xoắn ốc:
`Line SDL → Polar Array(32) → Maelstrom(xoắn) → Divide Curve(24) → Cull(bỏ điểm tâm) → Voronoi → Cells`.
Mấu chốt là **Maelstrom** bẻ cong các tia toả tròn thành xoắn ốc trước khi lấy điểm.

## Bối cảnh
- User: người mới với Rhino/Grasshopper, cần giải thích ở mức người mới, hướng dẫn từng bước.
- Không xem trực tiếp được video → dùng ffmpeg trích frame ra ảnh để đọc canvas Grasshopper.

## Quy trình ghi chú lệnh Grasshopper (app "Project Docs")
Project có 1 app ghi chú riêng tại `Document/index.html` (chỉ lưu **local**, không push lên GitHub
nữa — xem lý do bên dưới), dùng để soạn nội dung + xuất bản. Repo GitHub (private):
`https://github.com/nguyencam190/Document_Grasshopper`.
**Trang user xem: `https://nguyencam190.github.io/Document_Grasshopper/Grasshopper.html`**
(không còn `index.html` public — file gốc đã bị xoá khỏi repo theo yêu cầu user, chỉ giữ file
export tĩnh `Grasshopper.html` ở root repo).

**Quy trình chuẩn khi user tìm hiểu 1 lệnh Grasshopper mới (vd "Deconstruct Brep"):**
1. Nghiên cứu chức năng lệnh đó (input/output, cách dùng, lưu ý).
2. Tạo 1 trang con mới trong app, đặt tên đúng theo lệnh, nằm dưới trang cha "Grasshopper".
3. Viết nội dung vào canvas theo cấu trúc: H1 tên lệnh → Info panel tóm tắt → H2 "Chức năng" →
   H2 "Input/Output" (bảng) → H2 "Cách dùng" (danh sách số) → H2 "Minh họa" (ảnh SVG tự vẽ, vì
   không có ảnh chụp component thật) → Warning/Note panel lưu ý → H2 "Ví dụ trong dự án Voronoi".
4. Dùng chính tính năng **Push/Publish → Xuất Website → Portable HTML** của app để xuất ra 1 trang
   xem được (không tự viết tay HTML thay thế) — đây là yêu cầu rõ ràng của user.
5. Commit + `git push` **đè lên file `Grasshopper.html` ở root repo** (không phải `index.html` —
   file đó đã bị xoá khỏi GitHub theo yêu cầu user, chỉ còn giữ local để tiếp tục soạn/export).

**Chi tiết kỹ thuật quan trọng (để không lặp lại lỗi):**
- `Document/index.html` là **local-only** (đã `git rm --cached` + thêm vào `.gitignore`) — vẫn còn
  file thật trên đĩa để dùng làm công cụ soạn thảo/export, chỉ là không còn push/hiện công khai nữa.
- Dữ liệu trang (`state.docs`) của app nằm trong **localStorage của trình duyệt**, KHÔNG nằm trong
  file `index.html`. Vì `index.html` giờ không public nữa, SEED_DOCS/SEED_VERSION chỉ còn ý nghĩa khi
  tôi tự mở app cục bộ để soạn nội dung mới — không ảnh hưởng tới `Grasshopper.html` (đã là file tĩnh,
  tự chứa toàn bộ nội dung qua biến `_WS_DOCS` + các `<div class="ws-doc">`, không đọc localStorage
  của trang nội dung).
- **Bài học quan trọng**: từng bump `SEED_VERSION` để ép đồng bộ lại localStorage của mọi trình duyệt
  (kể cả khi đã có dữ liệu cũ) — đây là cách duy nhất tránh lỗi "trình duyệt hiện nội dung cũ vĩnh
  viễn" khi dùng `if(saved){...}else{seed}`. Nhớ `localStorage.setItem(STORE_KEY,...)` ngay sau khi
  force-sync, nếu không state đúng trong bộ nhớ nhưng KHÔNG được lưu lại → lần reload sau lại về dữ
  liệu cũ (đã gặp bug này 1 lần).
- Trình duyệt sandbox của Claude (Claude_Browser) **chặn `file://` và chặn tải file xuống Downloads
  thật** → không thể dùng nút "Tải xuống" của app trực tiếp để lấy file ra đĩa.
- Cách lấy được file export thật ra đĩa: dựng 1 local PowerShell HttpListener server nhỏ nhận
  `POST /upload` (có CORS `Access-Control-Allow-Origin: *`), sau đó trong trang (qua `javascript_exec`)
  patch `window._saveFile` để bắt Blob thay vì tải xuống, gọi `doExportWebsite()` thật của app, rồi
  `fetch()` Blob đó lên server local → server ghi thẳng ra file trên đĩa. Tránh route hàng MB text
  qua context của model.
- GitHub Pages mặc định dùng Jekyll, **bỏ qua mọi thư mục/file bắt đầu bằng `_`** (vd `_exported/`)
  → phải có file `.nojekyll` rỗng ở root repo để phục vụ đúng các file đó.
- GitHub Pages **luôn public với ai có link dù repo private** (free tier không hỗ trợ Pages riêng tư).
- GitHub Pages cache HTML ~10 phút (`Cache-Control: max-age=600`) — sau khi push, trình duyệt user có
  thể vẫn thấy bản cũ vài phút dù server đã có bản mới. Nếu cần xem ngay: thêm `?v=x` vào cuối URL.
- Push cần set `git config user.email` dạng `<username>@users.noreply.github.com` — email thật bị
  GitHub chặn (GH007, "would publish a private email address") nếu tài khoản đang bật ẩn email.
