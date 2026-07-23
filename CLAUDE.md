# Dự án: Grasshopper

Đây là dự án **tài liệu Grasshopper tổng hợp cho người mới bắt đầu**, không giới hạn ở 1 pattern cụ
thể nào. Trọng tâm chính là xây dựng và duy trì app tra cứu **"Project Docs"** (`Grasshopper.html`)
— bao phủ CHUNG mọi Component/lệnh của Grasshopper (Params, Maths, Sets, Vector, Curve, Surface,
Mesh, Intersect, Transform, Display, Rhino, Plugin Kangaroo2/Weaverbird...). Dự án **Voronoi Pattern**
(pattern hoa hướng dương/xoắn ốc) chỉ là **1 case study cụ thể** đã làm trong quá trình học, xem chi
tiết ở mục [Case study: Voronoi Pattern](#case-study-voronoi-pattern) cuối file — không phải toàn bộ
mục tiêu của dự án.

File này là **điểm vào (entry point)** — mọi quy trình chi tiết nằm trong skill tương ứng ở
`.claude/skills/`, xem [Bản đồ skill](#bản-đồ-skill---aios-của-dự-án) bên dưới. CLAUDE.md chỉ giữ lại
những gì áp dụng CHUNG cho mọi tác vụ (văn phong, quy tắc tuyệt đối, git workflow) và tài liệu tham
chiếu case study.

## Bản đồ skill — AIOS của dự án

| Tình huống | Skill dùng |
|---|---|
| User hỏi/tìm hiểu 1 component GH cụ thể (trả lời trong chat) | `nghien-cuu-grasshopper` |
| Ghi kết quả nghiên cứu đó thành 1 trang mới/cập nhật trong `Grasshopper.html` | `xuat-ban-trang-doc` |
| Vẽ/gắn ảnh minh hoạ SVG cho bất kỳ trang nào | `xuat-ban-hinh-minh-hoa` |
| Phân tích 1 video dựng nguyên 1 mẫu/pattern thành quy trình từng bước | `phan-tich-video-step-by-step` |

4 skill trên phối hợp với nhau theo đúng thứ tự luồng việc thật: **nghiên cứu → viết trang → thêm
ảnh** (2 skill đầu dùng chung 1 chuẩn nội dung 11 mục; skill ảnh dùng chung cho mọi loại trang, kể cả
trang step-by-step). Đọc SKILL.md tương ứng khi vào đúng tình huống — không cần đọc hết 4 skill mỗi
lần, chỉ mục lục ở đây và các quy tắc chung dưới đây là bắt buộc đọc trước mọi tác vụ.

## Phạm vi nghiên cứu Grasshopper (quan trọng)
Nhu cầu học Grasshopper của user **KHÔNG giới hạn trong dự án Voronoi** — user muốn tìm hiểu sâu
bất kỳ Component/Graph nào của Grasshopper nói chung, kể cả khi không liên quan gì đến pattern
Voronoi/phyllotaxis trong repo này. Khi user hỏi về 1 component GH cụ thể (vd "Deconstruct Brep",
"Graph Mapper", "Cull Pattern"...), dùng skill **`nghien-cuu-grasshopper`** để trả lời theo cấu trúc
11 mục cố định, không tự giới hạn câu trả lời vào bối cảnh dự án Voronoi trừ khi user hỏi rõ về dự
án này.

## Bối cảnh & văn phong (áp dụng cho MỌI nội dung — chat lẫn trang doc)
- User: người mới với Rhino/Grasshopper, cần giải thích ở mức người mới, hướng dẫn từng bước.
- Không xem trực tiếp được video → xem skill `phan-tich-video-step-by-step` cho cách đọc video qua
  frame ffmpeg + phụ đề `.srt`.
- **Toàn bộ tài liệu trong `Grasshopper.html` (app "Project Docs") dành cho người mới bắt đầu tìm
  hiểu Grasshopper, không phải cho người đã biết sẵn.** Khi viết bất kỳ trang nội dung nào (không chỉ
  khi trả lời trong chat), phải giải thích theo cách dễ hiểu nhất có thể: câu ngắn, ví dụ cụ thể thay
  vì mô tả trừu tượng, giải thích rõ mọi thuật ngữ chuyên ngành lần đầu xuất hiện (đừng giả định user
  đã biết "Data Tree", "Cull", "Graft" là gì...), tránh nói lý thuyết/toán học sâu nếu không cần thiết
  cho việc hiểu chức năng. Dễ hiểu không có nghĩa là kém chính xác — vẫn phải tuân thủ đầy đủ quy tắc
  "không bịa đặt" ở skill `nghien-cuu-grasshopper`, chỉ là trình bày phần đúng đó theo cách dễ tiếp
  thu nhất với người mới.
- **Viết ngắn gọn, súc tích — tránh diễn giải dài dòng** (user tự nhận xét nội dung hiện tại đôi khi
  dài quá mức cần thiết). Mỗi câu chỉ nên chứa 1 ý chính; mỗi đoạn "Chức năng"/"Cách dùng" tối đa
  2-3 câu, không lặp lại ý đã nói ở câu trước bằng từ ngữ khác, không thêm câu đệm/câu chuyển ý không
  mang thông tin mới (vd tránh kiểu "Điều này rất quan trọng vì..." nếu không thực sự cần giải thích
  thêm). Cắt bỏ tính từ/trạng từ thừa (vd "vô cùng", "rất là", "một cách rất") — nói thẳng vào chức
  năng. Áp dụng cho MỌI nội dung: trang doc trong `Grasshopper.html` lẫn câu trả lời trong chat. Ngắn
  gọn không được đánh đổi lấy thiếu chính xác hay bỏ sót thông tin bắt buộc (Input/Output, cảnh báo...)
  — chỉ cắt phần diễn giải thừa, không cắt nội dung cốt lõi.

## File & repo

Project có 1 app ghi chú duy nhất: **`Grasshopper.html`** là file DUY NHẤT cần sửa (app sống đầy đủ,
không phải bản xuất tĩnh chỉ đọc). Repo GitHub (private): `https://github.com/nguyencam190/Document_Grasshopper`.

- **Link chính user dùng: `https://nguyencam190.github.io/Document_Grasshopper/Grasshopper.html`**
- `index.html` chỉ là **1 file redirect tí hon** (`<meta http-equiv="refresh">` + `location.replace`)
  trỏ sang `Grasshopper.html`, để link gốc `https://nguyencam190.github.io/Document_Grasshopper/`
  (nút "Visit site" trong GitHub Settings luôn trỏ vào đây) cũng chạy được, không bị 404. KHÔNG chứa
  nội dung app.
- Dữ liệu trang (`state.docs`) của app nằm trong **localStorage của trình duyệt**, KHÔNG nằm trong
  file HTML. Vì vậy nội dung phải baked vào source qua `SEED_DOCS`/`SEED_VERSION` (khai báo ngay
  trước `let state=...`) để bất kỳ trình duyệt/máy nào mở `Grasshopper.html` cũng tự đồng bộ đúng.

> ⚠️ **QUY TẮC TUYỆT ĐỐI — SỬA `SEED_DOCS` HAY BẤT KỲ NỘI DUNG NÀO CŨNG PHẢI BUMP `SEED_VERSION`**,
> kể cả khi chỉ sửa 1 dòng CSS/style nhỏ, không phải chỉ khi thêm trang mới. Quên bước này từng gây
> ra 1 buổi debug rất dài: sửa xong tưởng đã đúng, push lên, nhưng trình duyệt NÀO ĐÃ TỪNG GHÉ THĂM
> trước đó (kể cả của chính Claude khi tự test) vẫn thấy bản CŨ y nguyên — vì `if(seed_version
> khớp){bỏ qua, dùng localStorage cũ}` khớp version nên không bao giờ đọc lại `SEED_DOCS` mới. Đây
> KHÔNG phải lỗi cache HTTP/CDN (đã loại trừ bằng cửa sổ ẩn danh) — mà là chính logic app tự thiết kế
> để bỏ qua re-seed khi version không đổi. Luôn tăng số này trong CÙNG 1 lần sửa, không tách riêng.
> Nhớ `localStorage.setItem(STORE_KEY,...)` ngay sau khi force-sync trong `init()` nếu sửa code app —
> thiếu dòng này thì state đúng trong bộ nhớ nhưng không được lưu lại, lần reload sau lại về dữ liệu cũ.

## Cách sửa file — tuỳ môi trường đang chạy

- **Có sẵn git clone của repo** (trường hợp phổ biến hiện nay — Claude Code trên web/remote sandbox):
  dùng git trực tiếp (Read/Edit tool + `git add/commit/push`), xem [Git workflow](#git-workflow).
- **KHÔNG có git clone sẵn** (vd chạy từ máy chưa clone repo): dùng GitHub Contents API — quy trình
  chi tiết ở đầu skill `xuat-ban-trang-doc` (lấy `sha`, đọc nội dung qua `raw.githubusercontent.com`,
  lấy token qua `git credential fill`, ghi file tạm ở scratchpad rồi `PUT` base64 lên GitHub).

Trình duyệt sandbox của Claude (khi cần mở `Grasshopper.html` để test/verify qua Playwright) **chặn
`file://`** (CORS chặn fetch ảnh) — luôn phục vụ qua 1 local HTTP server nhỏ
(`python3 -m http.server`) rồi mở `http://localhost:PORT/...`, không mở thẳng file.

## Git workflow
User muốn mọi commit trong repo này **push/merge thẳng vào nhánh `main`**, không giữ lại lâu trên
nhánh làm việc riêng chờ review — đây là repo tài liệu cá nhân, không cần quy trình PR. Nếu 1 phiên
làm việc bị hệ thống gán 1 nhánh tính năng riêng (vd `claude/...`) để phát triển, vẫn commit ở đó theo
yêu cầu hệ thống, nhưng ngay khi có thể (user xác nhận, hoặc cuối phiên) phải **merge nhánh đó thẳng
vào `main` và push**, không để `main` bị tụt lại phía sau — vì trang live (GitHub Pages) chạy từ
`main`, tụt nhánh nghĩa là thay đổi không lên được trang thật.

Push cần `git config user.email` dạng `<username>@users.noreply.github.com` — email thật bị GitHub
chặn (GH007) nếu tài khoản đang bật ẩn email. Không tự sửa `git config` nếu chưa được cấu hình sẵn —
hỏi user trước.

## Case study: Voronoi Pattern
Đây là **1 ví dụ ứng dụng cụ thể** đã thực hành trong lúc học Grasshopper — dựng pattern Voronoi
dạng **hoa hướng dương / xoắn ốc (phyllotaxis)**. Không phải trọng tâm của cả dự án (xem phần đầu
file), nhưng vẫn giữ lại đầy đủ ở đây vì nhiều tài liệu/video liên quan đã có sẵn và có thể còn dùng
tiếp (vd làm case study mới trong "Example Step-by-Step" — xem skill `phan-tich-video-step-by-step`,
hoặc đối chiếu khi học component liên quan tới Mesh/Triangulation/Voronoi).

### File liên quan
- `Video/Voronoi Pattern (Grasshopper Tutorial).mp4` — video tutorial gốc (Parametric House, ~15 phút, 720p).
- `Video/voronoi-alpha-1-wheel-system-youtube_2USQihHa.mp4` — showcase **vành xe Voronoi** (Handlebar3D,
  ~16 phút) = mục tiêu nâng cao đã thử phân tích. KHÔNG phải tutorial (thuật toán khổng lồ, cố tình khó copy).
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

### Bổ sung từ lời giảng (phụ đề) — ưu tiên hơn suy đoán từ hình
- **Polar Count phải là SỐ CHẴN** (để chia đôi /2 ở các Series sau).
- **Maelstrom Angle mặc định RADIAN** → chuột phải đổi sang Degrees (~50–120°). First < Second (bán kính trong/ngoài).
- **Dispatch mục đích = tạo KHE HỞ** giữa các dải (không chỉ giảm mật độ); true-false-false → khe to hơn.
- **Voronoi cần Flatten** điểm trước khi nối.
- **Thực chất ~3 lần Cull**: (1) Cull Index=0 xoá ĐIỂM trùng ở tâm (trước Voronoi); (2) Cull Series [0,12,…] xoá vòng Ô tâm; (3) Cull Series [11,23,…] xoá vòng Ô ngoài.
- **Series dùng Expression**: Step=`x/2`, Count=`x/2`, Start(ngoài)=`x/2−1` — nối số chia N vào input.
- Đây là **bản ĐƠN GIẢN HOÁ**, không phải Fibonacci thật.
- (Tôi không nghe được audio; đọc được vì có file phụ đề .srt.)

### Tóm tắt kỹ thuật
Voronoi này KHÔNG ngẫu nhiên. Điểm gieo được bố trí theo lưới xoắn ốc:
`Line SDL → Polar Array(32) → Maelstrom(xoắn) → Divide Curve(24) → Cull(bỏ điểm tâm) → Voronoi → Cells`.
Mấu chốt là **Maelstrom** bẻ cong các tia toả tròn thành xoắn ốc trước khi lấy điểm.
