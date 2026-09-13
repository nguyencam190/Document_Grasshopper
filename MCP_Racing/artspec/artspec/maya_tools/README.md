# maya_tools — công cụ chạy bên trong Maya

Các module ở đây **không import gì của `artspec`** để bỏ thẳng vào Maya chạy độc
lập được, giống quy ước của `adapters/maya_runner.py`.

## retopo_paint.py — dựng lưới quad từ vệt màu hoạ sĩ vẽ

Phân vai: **hoạ sĩ vẽ hướng lưới, máy dựng mesh.** Hoạ sĩ sơn hai họ vệt màu chỉ
hướng lưới mong muốn lên mặt scan; module đọc các vệt đó, tìm điểm giao, rồi nối
thành lưới quad bám mặt scan.

Không tạo NURBS curve nào trong scene — mọi bước trung gian là mảng điểm numpy,
chỉ chạm vào Maya ở hai đầu (đọc màu vertex vào, ghi mesh quad ra).

### Bước 1 — Hoạ sĩ sơn màu

1. Chọn mesh scan → `Mesh Display > Paint Vertex Color Tool`.
2. Bật hiển thị màu: `Display > Polygons > Color Set` — không bật thì vẽ xong
   không thấy gì, dễ tưởng brush hỏng.
3. Sơn **hai họ vệt cắt ngang nhau**, mỗi họ một màu (mặc định: đỏ = dọc,
   lục = ngang). Một họ vệt song song với nhau thôi thì không tạo được ô lưới.
4. Để **Opacity = 1** và tắt falloff mềm — brush mờ làm màu bị pha, khó tách
   đâu là điểm thuộc vệt.

### Bước 2 — Chạy dựng lưới

Trong Script Editor (Python) của Maya:

```python
import sys; sys.path.append(r"<đường dẫn tới thư mục maya_tools>")
import retopo_paint

bao_cao = retopo_paint.build_from_paint(
    "scan_hood",              # mesh đã sơn màu
    u_color=(1, 0, 0),        # đỏ  = họ vệt dọc
    v_color=(0, 1, 0),        # lục = họ vệt ngang
    color_tol=0.25,           # nới rộng nếu brush mềm làm màu bị pha
    out_name="hood_retopo",
)
print(retopo_paint.report_text(bao_cao))
```

### Bước 3 — Đọc báo cáo chấm điểm

```
Đã dựng: hood_retopo
  4 nét dọc × 3 nét ngang → 12 điểm giao → 6 quad
  Lệch so với scan: tb 0.0268 · max 0.0465
  Tỉ lệ cạnh: tb 1.12 · max 1.84
  Độ vênh: tb 0.004 · max 0.02
  Pole (đỉnh khác 4 cạnh): 0
```

| Chỉ số | Ý nghĩa | Xử lý khi số xấu |
|---|---|---|
| Lệch so với scan | Tâm quad cách mặt scan bao xa — quad phẳng cắt góc ở chỗ cong | Vẽ thêm nét ở vùng cong để chia nhỏ ô |
| Tỉ lệ cạnh | Cạnh dài / cạnh ngắn, càng gần 1 càng vuông vắn | Vẽ nét đều tay hơn, tránh chỗ dày chỗ thưa |
| Độ vênh | Góc thứ 4 lệch khỏi mặt phẳng 3 góc kia | Như trên — ô nhỏ lại thì hết vênh |
| Pole | Đỉnh trong lòng lưới có số cạnh khác 4, dễ vỡ shading | Sửa tay, hoặc vẽ lại cho lưới đều |

### Giới hạn hiện tại

- **Chưa chạy thử trong Maya thật.** Phần toán học (tách nét, sắp thứ tự, tìm
  giao, xếp lưới, nối quad) đã kiểm bằng dữ liệu giả trên mặt cong có nhiễu; phần
  gọi API Maya (đọc vertex color, snap lên mặt, tạo mesh) cần chạy thử lần đầu.
- **Ô lưới thiếu góc bị bỏ qua**, không ép thành quad méo — chỗ hở sửa tay sau.
- **Chưa conform vào biên part**: hàng/cột ngoài cùng dừng ở điểm giao cuối, chưa
  tự kéo khít vào đường viền part.
- Scan nhiều triệu điểm nên **giảm mật độ trước** (`polyReduce`/`polyRemesh`) rồi
  mới sơn và dựng lưới trên bản nhẹ.
