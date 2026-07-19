# Dự án: Grasshopper Voronoi Pattern

Dự án Rhino + Grasshopper tạo pattern Voronoi dạng **hoa hướng dương / xoắn ốc (phyllotaxis)**.

## Phạm vi nghiên cứu Grasshopper (quan trọng)
Nhu cầu học Grasshopper của user **KHÔNG giới hạn trong dự án Voronoi** — user muốn tìm hiểu sâu
bất kỳ Component/Graph nào của Grasshopper nói chung, kể cả khi không liên quan gì đến pattern
Voronoi/phyllotaxis trong repo này. Khi user hỏi về 1 component GH cụ thể (vd "Deconstruct Brep",
"Graph Mapper", "Cull Pattern"...), dùng skill **`nghien-cuu-grasshopper`**
(`.claude/skills/nghien-cuu-grasshopper/SKILL.md`) để trả lời theo cấu trúc 11 mục cố định, không
tự giới hạn câu trả lời vào bối cảnh dự án Voronoi trừ khi user hỏi rõ về dự án này.

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
- **Toàn bộ tài liệu trong `Grasshopper.html` (app "Project Docs") dành cho người mới bắt đầu tìm
  hiểu Grasshopper, không phải cho người đã biết sẵn.** Khi viết bất kỳ trang nội dung nào (không chỉ
  khi trả lời trong chat), phải giải thích theo cách dễ hiểu nhất có thể: câu ngắn, ví dụ cụ thể thay
  vì mô tả trừu tượng, giải thích rõ mọi thuật ngữ chuyên ngành lần đầu xuất hiện (đừng giả định user
  đã biết "Data Tree", "Cull", "Graft" là gì...), tránh nói lý thuyết/toán học sâu nếu không cần thiết
  cho việc hiểu chức năng. Dễ hiểu không có nghĩa là kém chính xác — vẫn phải tuân thủ đầy đủ quy tắc
  "không bịa đặt" ở skill `nghien-cuu-grasshopper`, chỉ là trình bày phần đúng đó theo cách dễ tiếp
  thu nhất với người mới.

## Quy trình ghi chú lệnh Grasshopper (app "Project Docs")
Project có 1 app ghi chú riêng: **`Document/Grasshopper.html`** là file DUY NHẤT cần sửa (app sống
đầy đủ, không phải bản xuất tĩnh chỉ đọc) — sửa trực tiếp file này, không có bản local riêng nào khác
nữa. Repo GitHub (private): `https://github.com/nguyencam190/Document_Grasshopper`.

> ⚠️ **QUY TẮC TUYỆT ĐỐI — SỬA `SEED_DOCS` HAY BẤT KỲ NỘI DUNG NÀO CŨNG PHẢI BUMP `SEED_VERSION`**,
> kể cả khi chỉ sửa 1 dòng CSS/style nhỏ, không phải chỉ khi thêm trang mới. Quên bước này từng gây
> ra 1 buổi debug rất dài: sửa xong tưởng đã đúng, push lên, nhưng trình duyệt NÀO ĐÃ TỪNG GHÉ THĂM
> trước đó (kể cả của chính Claude khi tự test) vẫn thấy bản CŨ y nguyên — vì `if(seed_version
> khớp){bỏ qua, dùng localStorage cũ}` khớp version nên không bao giờ đọc lại `SEED_DOCS` mới. Đây
> KHÔNG phải lỗi cache HTTP/CDN (đã loại trừ bằng cửa sổ ẩn danh) — mà là chính logic app tự thiết kế
> để bỏ qua re-seed khi version không đổi. Luôn tăng số này trong CÙNG 1 lần sửa, không tách riêng.

- **Link chính user dùng: `https://nguyencam190.github.io/Document_Grasshopper/Grasshopper.html`**
- `Document/index.html` chỉ còn là **1 file redirect tí hon** (`<meta http-equiv="refresh">` +
  `location.replace`) trỏ sang `Grasshopper.html`, để link gốc
  `https://nguyencam190.github.io/Document_Grasshopper/` (nút "Visit site" trong GitHub Settings
  luôn trỏ vào đây) cũng chạy được, không bị 404. KHÔNG chứa nội dung app.

**QUY TẮC MỚI — KHÔNG động vào ổ đĩa local nữa, chỉ làm việc thẳng qua GitHub:**
User yêu cầu rõ: mọi thao tác sửa file phải qua GitHub API, không tạo/sửa file trong thư mục project
trên ổ D: của họ nữa (thư mục `D:\...\Document` git clone cũ vẫn còn nguyên trên máy, không đụng tới,
nhưng không dùng nó để sửa nữa). Quy trình lấy/ghi file qua API (repo: `nguyencam190/Document_Grasshopper`):
1. Lấy sha hiện tại của file: `GET /repos/.../contents/Grasshopper.html?ref=main` (field `sha`).
2. Lấy nội dung thật (file >1MB nên Contents API trả `content:""`): dùng
   `raw.githubusercontent.com/nguyencam190/Document_Grasshopper/main/Grasshopper.html` kèm header
   `Authorization: token TOKEN`.
3. Lấy token từ Git Credential Manager đã cache sẵn:
   `printf "protocol=https\nhost=github.com\n\n" | git credential fill` (không cần thư mục repo local
   để chạy lệnh này, credential nằm ở Windows Credential Manager, dùng được từ bất kỳ đâu).
4. Ghi nội dung mới ra file **tạm trong scratchpad session** (KHÔNG phải thư mục project) để dùng
   Edit/Write tool sửa (các tool này bắt buộc cần đường dẫn file thật), rồi encode base64.
5. `PUT /repos/.../contents/Grasshopper.html` với body `{message, content: base64, sha, branch:"main"}`
   để commit thẳng lên GitHub — không qua `git add/commit/push` cục bộ nữa.

**Quy trình chuẩn khi user tìm hiểu 1 lệnh Grasshopper mới (vd "Deconstruct Brep"):**

> ⚠️ **BƯỚC 0 — BẮT BUỘC kiểm tra trùng trước khi làm bất cứ gì khác**: lấy `Grasshopper.html` hiện
> tại từ GitHub (theo quy trình API trên), tìm trong biến `SEED_DOCS` xem component/lệnh này **đã có
> trang riêng chưa** (so khớp theo tên lệnh, kể cả tên gần giống/viết tắt/khác hoa-thường). Nếu đã có
> trang rồi thì **DỪNG LẠI**: không nghiên cứu lại, không viết lại nội dung, không tạo thêm trang mới
> trùng lặp — báo ngay cho user theo đúng mẫu:
> **"Lệnh [tên lệnh] đã có trong document rồi — trang '[title trang]', là trang con của '[title trang
> cha, tra theo `parentId`]'."** (Nếu trang cha lại có `parentId` khác `seed-grasshopper`, nêu luôn cả
> đường dẫn đầy đủ, vd "Grasshopper → Surface → Loft", không chỉ nêu tên cha trực tiếp.) Sau đó hỏi
> user có muốn cập nhật/bổ sung trang cũ đó hay không. Chỉ tiếp tục từ bước 1 trở xuống khi xác nhận
> component **chưa** có trang nào trong `SEED_DOCS`.

1. Nghiên cứu chức năng lệnh đó (input/output, cách dùng, lưu ý).
2. Thêm 1 trang con mới vào biến `SEED_DOCS` (dùng nội dung `Grasshopper.html` đã lấy ở bước 0),
   đặt tên đúng theo lệnh. **`parentId` PHẢI trỏ vào đúng trang danh mục (tab) mà lệnh đó thuộc về
   trong Grasshopper thật — KHÔNG trỏ thẳng vào trang gốc `seed-grasshopper`.** App đã có sẵn 13
   trang danh mục con của `seed-grasshopper`, khớp đúng các tab ribbon thật của Grasshopper:

   | Tab (title)        | id trang danh mục      |
   |---------------------|--------------------------|
   | Params               | `seed-tab-params`       |
   | Maths                 | `seed-tab-maths`        |
   | Sets                   | `seed-tab-sets`         |
   | Vector                | `seed-tab-vector`       |
   | Curve                 | `seed-tab-curve`        |
   | Surface               | `seed-tab-surface`      |
   | Mesh                  | `seed-tab-mesh`         |
   | Intersect              | `seed-tab-intersect`    |
   | Transform              | `seed-tab-transform`    |
   | Display                | `seed-tab-display`      |
   | Rhino                  | `seed-tab-rhino`        |
   | Wb (Weaverbird)         | `seed-tab-wb`           |
   | Kangaroo2               | `seed-tab-kangaroo2`    |

   Ví dụ: lệnh **Loft** thuộc tab Surface trong Grasshopper thật → `parentId:'seed-tab-surface'`.

   **Phân loại phải khớp 100% với Grasshopper thật, không được áng chừng/đoán đại.** Trước khi gán
   `parentId`, xác nhận đúng tab mà lệnh nằm trong ribbon Grasshopper thật (ưu tiên tra theo đúng thứ
   tự nguồn tham khảo ở đầu CLAUDE.md/skill `nghien-cuu-grasshopper`: tài liệu chính thức Rhino/GH
   trước, rồi AAD, rồi tài liệu Plugin nếu lệnh thuộc Plugin như Kangaroo2/Weaverbird). Nếu tra không
   ra hoặc không chắc chắn lệnh thuộc tab nào, PHẢI dừng lại hỏi user thay vì tự đoán và gán bừa —
   gán sai tab còn tệ hơn không phân loại, vì sẽ làm sai cấu trúc doc lâu dài. Xem cấu trúc doc ở
   [[gh-docs-app-workflow]].
3. Viết nội dung vào canvas theo cấu trúc: H1 tên lệnh → Info panel tóm tắt → H2 "Chức năng" →
   H2 "Input/Output" (bảng) → H2 "Cách dùng" (danh sách số) → H2 "Minh họa" (ảnh SVG tự vẽ, vì
   không có ảnh chụp component thật — **phải mô phỏng đúng diện mạo thật của Grasshopper canvas/Rhino
   viewport** theo chuẩn ở `.claude/skills/nghien-cuu-grasshopper/references/phong-cach-minh-hoa.md`,
   không vẽ sơ đồ hộp-mũi tên chung chung) → Warning/Note panel lưu ý → H2 "Ví dụ trong dự án Voronoi".
4. Bump `SEED_VERSION` lên 1 (để mọi trình duyệt tự đồng bộ lại, không cần user xoá cache/localStorage).
5. **Luôn publish kèm ảnh minh họa, tạo bằng CHÍNH pipeline thật của app** (yêu cầu rõ ràng của user —
   "làm đúng" như nút Publish, không tự chế) — quy trình đầy đủ (đã test thành công với "Voronoi"):
   a. Trong 1 tab trình duyệt đã mở `Grasshopper.html` sống (qua `mcp__Claude_Browser`), với ảnh SVG
      mới đã có sẵn ở đâu đó truy cập được (vd fetch từ 1 URL tạm), đăng ký ảnh "đúng chuẩn" của app:
      `const blob=await(await fetch(url)).blob(); const id=uid(); await _idbPut(id,blob);` rồi thay
      thẻ `<img>` thô trong `doc.content` bằng khối `.cf-img-block` có `data-cfimgid="ID"` (xem cấu
      trúc ở `_cfBuildImgBlock` trong `Grasshopper.html`).
   b. **Bẫy quan trọng**: nếu trang đang sửa đang là `state.currentDocId` (đang mở trong editor), bước
      xuất ở dưới sẽ tự động ghi đè `doc.content` bằng snapshot DOM sống (Phase 0 của
      `doExportOptimized`/`doExportWebsite`) — xoá mất chỉnh sửa string vừa làm! Phải set
      `state.currentDocId=null` (đóng hết trang đang mở) trước khi export.
   c. Set chế độ ảnh gốc (không nén thành JPG mất chi tiết SVG):
      `document.querySelector('input[name="imgQuality"][value="original"]').checked=true` (mở modal
      export 1 lần trước đó nếu radio chưa tồn tại trong DOM: `openExportWebsiteModal()`).
   d. Patch `window._saveFile` để bắt Blob thay vì tải xuống (sandbox chặn download thật), gọi
      `await doExportOptimized({docs: state.docs.filter(d=>!d._deleted), title:'...'})` — trả về 1
      file ZIP (không phải HTML đơn), ảnh nằm ở `assets/images/{id}.{ext}` bên trong ZIP.
   e. `fetch()` Blob ZIP đó lên local relay server (POST /upload, xem mục kỹ thuật bên dưới) → lưu
      **vào scratchpad session, TUYỆT ĐỐI không lưu vào ổ D:** → giải nén bằng
      `Expand-Archive` (PowerShell, có sẵn, không cần cài gì).
   f. Lấy đúng file ảnh vừa giải nén (`assets/images/{id}.svg`), `PUT` lên GitHub tại
      `assets/images/{id}.svg` (file mới, không cần `sha`).
   g. **Sửa `SEED_DOCS` dùng ĐÚNG khối `.cf-img-block` + `data-cfimgid="{id}"`** (không dùng `<img
      src="...">` trần — đã thử cách đó và BỊ LỖI: khi user tự bấm nút Publish trong app, hàm xuất chỉ
      gom được ảnh có `data-cfimgid`, ảnh `<img src>` trần bị bỏ qua hoàn toàn → xuất ra thư mục khác
      là mất ảnh, đúng lỗi user báo cáo). Cấu trúc khối cần chèn (xem `_cfBuildImgBlock`):
      ```html
      <div class="cf-img-block" data-cfimgid="{id}" data-cfimgtype="image" data-align="center" data-name="{ten-file}">
        <div class="cf-img-wrap"><div class="cf-img-inner">
          <img style="width:100%;max-width:320px;height:auto;display:block" alt="{mo-ta}"><div class="cf-img-resize-h left"></div><div class="cf-img-resize-h right"></div>
        </div></div>
        <div class="cf-img-caption"></div>
      </div>
      ```
      **BẮT BUỘC có `style="width:...;height:auto;display:block"` ngay trên thẻ `<img>`** — nếu thiếu,
      ảnh vẫn tải đúng dữ liệu (naturalWidth đúng, complete=true) nhưng hiển thị co lại còn ~3×3px gần
      như vô hình (đã tự gặp lỗi thật này, mất nhiều vòng debug mới tìm ra — bình thường app tự đo
      kích thước ảnh sau khi người dùng upload qua UI thật rồi gán width, nhưng ảnh dựng bằng tay qua
      SEED_DOCS thì không có bước đó nên bắt buộc set style tay).
      (không cần set `src` cho `<img>` — app tự nạp từ IndexedDB lúc mở trang, xem bước (h)).
   h. **Bắt buộc thêm vào `SEED_ASSETS`** (khai báo cạnh `SEED_DOCS`): `{id: 'ext'}` cho mỗi ảnh mới.
      Trong `init()`, đoạn code sau seed force-sync phải fetch từng ảnh trong `SEED_ASSETS` từ
      `assets/images/{id}.{ext}` rồi `_idbPut(id, blob)` — bước này bắt buộc, KHÔNG được bỏ, vì
      `data-cfimgid` chỉ hiển thị được nếu IndexedDB của TRÌNH DUYỆT ĐANG XEM có sẵn blob đó. Không có
      bước này thì mọi khách ghé thăm mới sẽ thấy ảnh vỡ (đã tự kiểm chứng bằng cách xoá sạch
      localStorage + IndexedDB rồi tải lại — ảnh hiện đúng VÀ khi tự bấm Publish trong app, ZIP xuất
      ra có đủ cả 2 ảnh).
      **Bẫy race-condition (đã gặp thật khi lên 13 ảnh cùng lúc)**: nếu đoạn fetch+`_idbPut` này chạy
      kiểu "fire-and-forget" (`.forEach(async...)` không đợi), `renderSidebar()`/`openDoc()` có thể
      chạy TRƯỚC khi ảnh kịp nạp xong vào IndexedDB → trang hiện ra nhưng ảnh trống (đúng lỗi user báo
      "không hiển thị hình minh họa"). Bắt buộc gói toàn bộ đoạn nạp ảnh trong 1 IIFE `async` dùng
      `await Promise.all(...)`, và di chuyển `updateUserUI();renderSidebar();if(state.currentDocId)
      openDoc(...)` vào SAU dòng `await` đó — đảm bảo không trang nào được vẽ ra trước khi toàn bộ
      ảnh trong `SEED_ASSETS` đã có sẵn trong IndexedDB. Đã tự test lại: mở nhiều trang liên tiếp chỉ
      cách nhau 100ms sau khi xoá sạch dữ liệu trình duyệt — ảnh vẫn hiện đúng 100%.
   i. Xoá file ảnh cũ (nếu có, đường dẫn phẳng `assets/{ten}.svg` kiểu cũ) bằng
      `DELETE /repos/.../contents/{path}` kèm `sha` hiện tại, tránh rác thừa trong repo.
   j. Bump `SEED_VERSION`, `PUT Grasshopper.html` như bước 5 cũ.

**Trang cha riêng cho nội dung Step-by-step (quy trình dựng mẫu từ video):**
Khác với trang tham khảo 1 component đơn lẻ (nhét vào 1 trong 13 trang danh mục ở trên), nội dung
**step-by-step dựng nguyên 1 mẫu/pattern** (đúc kết từ video user quay + tải lên `Video/`) đi vào
**1 trang cha riêng, ngang hàng với trang gốc "Grasshopper"**:

- id: `seed-step-by-step`, title: **"Example Step-by-Step"**, `parentId: null`.
- Khi user yêu cầu **"phân tích step-by-step"** cho 1 mẫu/video mới, luôn tạo **1 trang con mới bên
  trong `seed-step-by-step`** (`parentId:'seed-step-by-step'`), đặt tên theo mẫu
  `[Tên mẫu] — Quy trình dựng từng bước`. Không áp dụng quy tắc phân loại theo 13 tab GH cho loại
  trang này (vì đây là quy trình phối hợp nhiều component, không phải tài liệu 1 component).
- **Bắt buộc kiểm tra trùng nội dung trước khi phân tích, không chỉ kiểm tra trùng tên**: khi user
  đưa 1 mẫu mới để phân tích, trước tiên phải **trích xuất nội dung của toàn bộ trang con hiện có
  trong `seed-step-by-step`** (lấy từ `Grasshopper.html`/`SEED_DOCS`), so sánh xem quy trình/pattern
  đó có giống (hoặc rất tương tự) 1 trang đã phân tích trước đó không — không chỉ so tên mẫu, mà so
  cả cách dựng (chuỗi component, thuật toán) mô tả bên trong. Nếu phát hiện giống, **DỪNG LẠI, không
  phân tích lại từ đầu** — báo ngay cho user theo mẫu: **"Mẫu này giống với phân tích đã có — trang
  '[title trang con]' trong Example Step-by-Step, xem ở đây."** rồi hỏi user có muốn cập nhật/bổ sung
  trang cũ hay tạo trang mới riêng vì thực ra khác biệt. Chỉ tiến hành phân tích + tạo trang mới khi
  xác nhận chưa có nội dung nào tương tự.

**Chi tiết kỹ thuật quan trọng (để không lặp lại lỗi):**
- **Đã sửa lỗi app tự làm mất chất lượng SVG khi export**: hàm `_compressForExportBlob()` trong
  `Grasshopper.html` trước đây rasterize MỌI ảnh qua canvas ở chế độ "Nén ảnh tự động" (mặc định),
  biến SVG (vector) thành JPG/PNG (raster) — mất nét, không co giãn được nữa. Đã thêm dòng chặn
  `if(blob.type==='image/svg+xml')return blob;` ngay cạnh chỗ chặn video/gif, để SVG luôn giữ nguyên
  dù ở chế độ nén hay gốc. Đã tự test lại bằng đúng chế độ mặc định (không ép "original") — xác nhận
  ảnh xuất ra vẫn đuôi `.svg`, không còn bị đổi thành `.jpg` nữa.
- (Lịch sử: có lúc `index.html` bị `git rm --cached`/gitignore, có lúc bản xuất tĩnh
  `Grasshopper-Voronoi-Docs.html` được publish thay vì app sống — **cả 2 đã bị đảo lại**. Trạng thái
  CUỐI CÙNG: `Grasshopper.html` = app sống, giống hệt `index.html`, cả 2 cùng tồn tại và cùng nội
  dung trên đĩa local; chỉ `Grasshopper.html` được push lên GitHub.)
- Dữ liệu trang (`state.docs`) của app nằm trong **localStorage của trình duyệt**, KHÔNG nằm trong
  file HTML. Vì vậy nội dung phải baked vào source qua `SEED_DOCS`/`SEED_VERSION` (khai báo ngay
  trước `let state=...`) để bất kỳ trình duyệt/máy nào mở `Grasshopper.html` cũng tự đồng bộ đúng.
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

## Git workflow
User muốn mọi commit trong repo này **push/merge thẳng vào nhánh `main`**, không giữ lại lâu trên
nhánh nhánh làm việc riêng chờ review — đây là repo tài liệu cá nhân, không cần quy trình PR. Nếu 1
phiên làm việc bị hệ thống gán 1 nhánh tính năng riêng (vd `claude/...`) để phát triển, vẫn commit ở
đó theo yêu cầu hệ thống, nhưng ngay khi có thể (user xác nhận, hoặc cuối phiên) phải **merge nhánh đó
thẳng vào `main` và push**, không để `main` bị tụt lại phía sau — vì trang live (GitHub Pages) chạy từ
`main`, tụt nhánh nghĩa là thay đổi không lên được trang thật.
