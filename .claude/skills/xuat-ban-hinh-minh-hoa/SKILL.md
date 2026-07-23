---
name: xuat-ban-hinh-minh-hoa
description: Toàn bộ pipeline tạo và gắn ảnh minh hoạ SVG vào Grasshopper.html — vẽ SVG theo phong cách canvas GH/viewport Rhino thật, đăng ký vào SEED_ASSETS, gắn qua khối .cf-img-block hoặc .cf-carousel-block, và toàn bộ bug đã vá liên quan (ảnh collapse ~3px, ảnh mất khi export, race condition khi seed nhiều ảnh cùng lúc, SVG bị rasterize). LUÔN dùng skill này khi cần "vẽ hình minh hoạ", "thêm ảnh", "publish ảnh" cho bất kỳ trang nào trong Grasshopper.html — dù là trang component đơn lẻ, trang step-by-step, hay carousel nhiều ảnh. Không dùng để quyết định NỘI DUNG cần viết (đó là việc của nghien-cuu-grasshopper/xuat-ban-trang-doc) — skill này chỉ lo phần kỹ thuật tạo/gắn ảnh.
---

# Xuất bản hình minh hoạ vào Project Docs

## Nguyên tắc bản quyền — TUYỆT ĐỐI không thương lượng

**Không bao giờ trích xuất, tái tạo, hay mô phỏng sát nguyên hình ảnh/layout thật từ bất kỳ sách nào**
(AAD — Algorithms-Aided Design, Grasshopper Primer, hay tài liệu khác), **bất kể tình trạng bản quyền/
giấy phép của sách đó** (kể cả sách Creative Commons), và bất kể user có tự trích xuất ảnh ra hộ hay
không. Chỉ vẽ **ảnh minh hoạ nguyên bản (original artwork)** theo phong cách riêng ở
`references/phong-cach-minh-hoa.md`. Nếu user muốn layout "giống sách", chỉ mô phỏng tinh thần bố cục
chung (vd input→component→viewport) bằng hình tự vẽ, không sao chép chi tiết hình gốc.

Text (dịch/diễn giải/tóm tắt nội dung sách) không bị giới hạn như ảnh — nhưng luôn diễn giải bằng lời
riêng, không copy nguyên văn đoạn dài.

## Phong cách vẽ

Mọi ảnh SVG phải mô phỏng đúng diện mạo thật của canvas Grasshopper / viewport Rhino (không vẽ sơ đồ
hộp-mũi tên chung chung kiểu flowchart, trừ khi minh hoạ thuần khái niệm không liên quan tới UI thật).
Xem chi tiết màu sắc, kích thước, cấu trúc SVG mẫu, và checklist lỗi thường gặp (núm input/output lệch
khung, dây nối không khớp toạ độ nub) ở `references/phong-cach-minh-hoa.md`. **Luôn render thử bằng
Playwright và phóng to kiểm tra bằng mắt trước khi publish**, đặc biệt component có ≥3 input.

## Cấu trúc khối ảnh đơn — `.cf-img-block`

```html
<div class="cf-img-block" data-cfimgid="{id}" data-cfimgtype="image" data-align="center" data-name="{ten-file}">
  <div class="cf-img-wrap"><div class="cf-img-inner" style="width:100%;max-width:640px">
    <img style="width:100%;height:auto;display:block" alt="{mo-ta}"><div class="cf-img-resize-h left"></div><div class="cf-img-resize-h right"></div>
  </div></div>
  <div class="cf-img-caption"></div>
</div>
```

Quy tắc bắt buộc (mỗi quy tắc dưới đây đều xuất phát từ 1 bug thật đã gặp — xem mục "Bug đã vá" để
hiểu rõ hậu quả nếu bỏ qua):

- **`max-width` PHẢI đặt trên `.cf-img-inner` (khung ngoài), KHÔNG đặt trên `<img>`** — nếu đặt nhầm
  ở `<img>`, khung chọn trong editor to hơn hẳn ảnh thật, và ảnh bị lệch trái thay vì canh giữa khi
  export/publish.
- **BẮT BUỘC có `style="width:100%;height:auto;display:block"` ngay trên thẻ `<img>`** — thiếu style
  này, ảnh vẫn tải đúng dữ liệu nhưng hiển thị co lại còn ~3×3px gần như vô hình.
- Không cần set `src` cho `<img>` — app tự nạp từ IndexedDB lúc mở trang (xem mục SEED_ASSETS).
- Không dùng `<img src="...">` trần thay cho khối `.cf-img-block` — hàm xuất/publish của app chỉ gom
  ảnh có `data-cfimgid`, ảnh `<img src>` trần bị bỏ qua hoàn toàn khi export → mất ảnh.

## Cấu trúc carousel nhiều ảnh — `.cf-carousel-block`

Dùng khi có nhiều ảnh cùng chủ đề, xem lần lượt qua nút next/prev (không phải nhiều `.cf-img-block`
xếp chồng). Reverse-engineer từ app JS (`_cfBuildCarousel`, `_cfBuildCarSlide`, `_cfCarLoadAll` trong
`Grasshopper.html`):

```html
<div class="cf-carousel-block" style="width:760px" data-carids="id1,id2,..." data-align="center">
  <div class="cf-car-wrap"><div class="cf-car-track">
    <div class="cf-car-slide active" data-carslide-align="center">
      <div class="cf-car-slide-wrap"><div class="cf-car-slide-inner">
        <img data-carid="id1" alt="...">
        <div class="cf-car-slide-resize-h left"></div><div class="cf-car-slide-resize-h right"></div>
      </div></div>
      <div class="cf-car-slide-caption" contenteditable="true" data-placeholder="Thêm chú thích..."></div>
    </div>
    <!-- thêm .cf-car-slide cho mỗi ảnh -->
  </div>
  <div class="cf-car-counter">1 / N</div>
  <button class="cf-car-btn prev">&#8249;</button>
  <button class="cf-car-btn next">&#8250;</button>
  </div>
  <div class="cf-car-dots"><div class="cf-car-dot on"></div>...</div>
</div>
```

`_cfCarLoadAll` (chạy tự động khi mở trang) tự nạp `img[data-carid]` từ IndexedDB qua đúng cơ chế
`SEED_ASSETS` như ảnh đơn, và tự nối nav/toolbar/resize — chỉ cần markup tĩnh ở trên, JS lo phần còn
lại lúc runtime.

**Bug đã vá — carousel dư khoảng trống khi publish**: `.cf-carousel-block` mặc định rộng 100% cột nội
dung (~1200px) dù ảnh bên trong hẹp hơn nhiều, gây letterbox 2 bên rất to. Sửa bằng cách gắn thẳng
`style="width:{Npx}px"` (khớp chiều rộng ảnh + đệm nhỏ, vd `760px` cho ảnh 720px) trên
`.cf-carousel-block` — **không dùng preset `data-carwidth="50"/"75"`** vì đó là phần trăm, không phải
kích thước cố định.

## Quy trình đăng ký ảnh (SEED_ASSETS)

1. Vẽ SVG (script Python, dùng chung style ở `references/phong-cach-minh-hoa.md`), lưu file vào
   `assets/images/{id}.svg` trong repo (đường dẫn phẳng, không thư mục con).
2. Thêm `SEED_ASSETS` (khai báo cạnh `SEED_DOCS`): `'{id}':'svg'` cho mỗi ảnh mới — **bắt buộc**, vì
   `data-cfimgid`/`data-carid` chỉ hiển thị được nếu IndexedDB của trình duyệt đang xem có sẵn blob
   đó. Trong `init()`, đoạn code sau seed force-sync fetch từng ảnh trong `SEED_ASSETS` từ
   `assets/images/{id}.{ext}` rồi `_idbPut(id, blob)`.
3. Gắn khối `.cf-img-block`/`.cf-carousel-block` vào đúng vị trí trong `content` của trang (xem
   `xuat-ban-trang-doc` cho vị trí chuẩn theo mục — vd "Minh họa" ngay sau "Cách dùng", "Ví dụ ứng
   dụng thực tế" có ảnh riêng không dùng lại ảnh mục "Minh họa").
4. Bump `SEED_VERSION`, commit/push/merge theo Git workflow ở `CLAUDE.md`.
5. **Verify bằng Playwright trước khi coi là xong**: mở `Grasshopper.html` qua local HTTP server
   (không dùng `file://` — bị CORS chặn fetch ảnh), gọi `openDoc(id)`, kiểm tra
   `document.querySelectorAll('.cf-img-block img')` có `complete:true` và `naturalWidth>0`, chụp
   screenshot đối chiếu bằng mắt (không tin số liệu đơn thuần, ảnh có thể tải đúng nhưng bố cục sai).

## Bẫy race-condition khi seed nhiều ảnh cùng lúc

Nếu đoạn fetch+`_idbPut` trong `init()` chạy kiểu "fire-and-forget" (`.forEach(async...)` không đợi),
`renderSidebar()`/`openDoc()` có thể chạy TRƯỚC khi ảnh kịp nạp xong vào IndexedDB → trang hiện ra
nhưng ảnh trống. Bắt buộc gói toàn bộ đoạn nạp ảnh trong 1 IIFE `async` dùng `await Promise.all(...)`,
và di chuyển `updateUserUI();renderSidebar();if(state.currentDocId) openDoc(...)` vào SAU dòng `await`
đó — đảm bảo không trang nào được vẽ ra trước khi toàn bộ ảnh trong `SEED_ASSETS` đã có sẵn trong
IndexedDB.

## Bug đã vá (lịch sử — để không lặp lại)

- **SVG bị rasterize khi export mất chất lượng**: hàm `_compressForExportBlob()` từng rasterize MỌI
  ảnh qua canvas ở chế độ "Nén ảnh tự động" (mặc định), biến SVG (vector) thành JPG/PNG (raster) —
  mất nét. Đã thêm `if(blob.type==='image/svg+xml')return blob;` ngay cạnh chỗ chặn video/gif.
- **Ảnh biến mất khi Export/Publish dù trang live vẫn hiện đúng**: `doExportWebsite()` và
  `doExportOptimized()` có đoạn `media.style.cssText='display:block;max-width:100%;height:auto;...'`
  ghi đè TOÀN BỘ style ảnh khi export, xoá mất `width`/`max-width` gốc của `<img>`. Đã sửa: giữ lại
  CẢ `width` VÀ `max-width` gốc (`const _origW=media.style.width||'100%'`,
  `const _origMaxW=media.style.maxWidth||'100%'`) rồi nối vào cssText mới thay vì ghi đè mất, ở cả 2
  hàm export. Khi debug ảnh không hiện ở bản export/publish (khác bản xem trực tiếp), luôn nghi ngờ
  style bị ghi đè kiểu này trước.
- **Ảnh minh hoạ luôn hiện nhỏ trừ khi tự kéo tay resize lên 100%**: `<img>` set `width:100%` để co
  giãn theo container, nhưng `.cf-img-inner` (CSS `display:inline-block`) không có `width` mặc định
  → phần trăm không resolve được, ảnh rơi về kích thước nội tại gốc (thường nhỏ). Đã sửa: thêm
  `width:100%` vào rule mặc định `.cf-img-inner{...}` — cả bản trong editor sống LẪN bản CSS riêng
  cho trang export/publish trong `_buildViewerShellCss()` (dùng chung bởi `doExportWebsite()` và
  `doExportOptimized()`) — thiếu 1 trong 2 chỗ vẫn còn bug ở nơi chưa sửa.

## Quy trình "publish đúng như nút Publish của app" (khi cần mô phỏng chính xác pipeline export)

Chỉ cần khi user yêu cầu rõ mô phỏng đúng hành vi nút Publish thật (thay vì chỉ ghi thẳng vào
`SEED_DOCS`/`SEED_ASSETS` như quy trình chuẩn ở trên, vốn đã đủ cho phần lớn trường hợp):

1. Trong 1 tab trình duyệt đã mở `Grasshopper.html` sống, đăng ký ảnh đúng chuẩn app:
   `const blob=await(await fetch(url)).blob(); const id=uid(); await _idbPut(id,blob);` rồi thay
   `<img>` thô bằng khối `.cf-img-block` có `data-cfimgid="ID"` (xem `_cfBuildImgBlock`).
2. **Bẫy quan trọng**: nếu trang đang sửa đang là `state.currentDocId` (đang mở trong editor), bước
   export sẽ tự động ghi đè `doc.content` bằng snapshot DOM sống (Phase 0 của
   `doExportOptimized`/`doExportWebsite`) — xoá mất chỉnh sửa string vừa làm! Phải set
   `state.currentDocId=null` trước khi export.
3. Set chế độ ảnh gốc (không nén JPG mất chi tiết SVG):
   `document.querySelector('input[name="imgQuality"][value="original"]').checked=true`.
4. Patch `window._saveFile` để bắt Blob thay vì tải xuống (sandbox chặn download thật), gọi
   `await doExportOptimized({docs: state.docs.filter(d=>!d._deleted), title:'...'})` — trả về ZIP,
   ảnh nằm ở `assets/images/{id}.{ext}` bên trong.
5. Lấy file ảnh ra đĩa qua 1 local relay server nhỏ (POST /upload), giải nén bằng `Expand-Archive`
   (PowerShell) hoặc `unzip`.
6. `PUT` ảnh lên GitHub tại `assets/images/{id}.svg`, xoá file ảnh cũ nếu có đường dẫn phẳng kiểu cũ.
7. Bump `SEED_VERSION`, `PUT`/push `Grasshopper.html`.

## Hệ thống logo dự án (khác cơ chế SEED_ASSETS)

App có **2 hệ thống logo RIÊNG BIỆT** — dễ sửa nhầm chỗ:

1. `state.projectLogo` → phần tử `#sbSpaceIcon` trong sidebar cũ — ở "new UI" hiện tại phần tử này bị
   `display:none!important` nên **sửa CSS ở đây KHÔNG có tác dụng gì**, user không nhìn thấy nó.
2. `state.headerLogo` → phần tử `#headerLogoWrap`/`#hdrLogoBox`, đây là **logo thật sự hiển thị**,
   nằm ở đầu thanh rail icon dọc bên trái (`#mainHeader`). Set style qua JS trong `_hdrLogoInit()`.

Khi user báo lỗi "logo không vừa khung"/"logo bị cắt", **luôn hỏi rõ vị trí trước khi sửa** (icon ở
rìa trái ngoài cùng = rail logo/`#hdrLogoBox`, icon phía trên chữ "Recent" trong sidebar = phần tử cũ
hiện đã ẩn).

Logo mặc định bake vào seed qua `SEED_HEADER_LOGO` (khai báo cạnh `SEED_ASSETS`, trỏ tới
`assets/images/logo-grasshopper.png`) — khác cơ chế `SEED_ASSETS`/`data-cfimgid`, logo lưu thẳng dạng
`data:` URL trong `state.headerLogo.imgDataUrl` VÀ `state.projectLogo.imgDataUrl` (bản export dùng
field khác nhau cho rail-logo so với sidebar logo). Đổi ảnh logo vẫn phải bump `SEED_VERSION`.

## Ghi chú hạ tầng deploy liên quan ảnh

- GitHub Pages dùng Jekyll, **bỏ qua mọi thư mục/file bắt đầu bằng `_`** → cần `.nojekyll` rỗng ở root
  repo để phục vụ đúng các file đó.
- GitHub Pages **luôn public với ai có link dù repo private** (free tier không hỗ trợ Pages riêng tư).
- GitHub Pages cache HTML ~10 phút — sau khi push, trình duyệt có thể vẫn thấy bản cũ vài phút. Cần
  xem ngay: thêm `?v=x` vào cuối URL.
