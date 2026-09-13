# maya_tools — công cụ chạy bên trong Maya

Các module ở đây **không import gì của `artspec`** để bỏ thẳng vào Maya chạy độc
lập được, giống quy ước của `adapters/maya_runner.py`.

## Cài vào Maya

Mở `cai_dat/cai_maya_tools.py`, copy toàn bộ, dán vào **tab Python** của Script
Editor trong Maya rồi chạy. Script tự tìm thư mục này, nạp hai module và in
hướng dẫn dùng. Chạy lại mỗi phiên Maya.

Chạy `tu_kiem()` ngay sau đó để thử cả quy trình trên một mặt cong nhân tạo —
script tự tạo cảnh thử, tự sơn sẵn hai họ vệt, dựng lưới rồi in báo cáo. Nếu
hỏng, nó báo rõ hỏng ở bước nào để gửi lại cho Claude sửa. Cảnh thử nằm trong
nhóm `retopoTuKiem_grp`, xoá bằng `cmds.delete('retopoTuKiem_grp')`.

---

Quy trình gồm hai bước, mỗi bước một module:

| Bước | Module | Ai làm |
|---|---|---|
| Sơn hướng lưới lên mặt scan | `paint_flow.py` | Hoạ sĩ, bằng tay |
| Dựng lưới quad theo vệt đã sơn | `retopo_paint.py` | Máy |

---

## paint_flow.py — cọ sơn hướng lưới kiểu ZBrush

Cọ sơn vertex color chạy thẳng trong viewport. So với `Paint Vertex Color Tool`
sẵn có của Maya, cọ này thêm ba thứ cần cho việc vẽ hướng lưới:

- **LazyMouse** — đầu cọ bám trễ sau con trỏ nên nét mượt dù tay run. Xử lý
  nhiễu ngay lúc vẽ, đỡ phải lọc nhiễu ở bước dựng lưới.
- **Đổi nhanh hai màu U/V** — `paint_flow.u()` / `paint_flow.v()`, gán phím tắt
  được, không phải mở bảng màu mỗi lần đổi hướng.
- **Bán kính theo pixel màn hình** — cọ giữ nguyên độ lớn cảm nhận khi zoom, cọ
  theo đơn vị thế giới thì zoom ra là cọ bé tí.

```python
import sys; sys.path.append(r"<thư mục maya_tools>")
import paint_flow

paint_flow.start("scan_hood")   # bật cọ, tự tạo color set + bật hiển thị màu
paint_flow.size(60)             # bán kính 60 pixel
paint_flow.lazy(0.2)            # mượt hơn (0.05 rất ì · 1.0 tắt LazyMouse)
paint_flow.v()                  # đổi sang lục = họ vệt ngang
paint_flow.stop()               # trả về công cụ chọn
```

`Ctrl` + kéo = xoá màu. `Ctrl+Z` hoàn tác được từng nét.

**Nét thật mảnh hơn vòng tròn cọ.** Cọ tô đậm ở giữa và nhạt dần ra mép, còn
bước dựng lưới chỉ nhận phần đủ đậm (`color_tol`) — nên vệt được dùng chỉ rộng
khoảng **1/3 đường kính cọ**. Muốn nét dày hơn thì tăng `size()`, hoặc nới
`color_tol` khi gọi `build_from_paint`.

---

## retopo_paint.py — dựng lưới quad từ vệt màu hoạ sĩ vẽ

Phân vai: **hoạ sĩ vẽ hướng lưới, máy dựng mesh.** Hoạ sĩ sơn hai họ vệt màu chỉ
hướng lưới mong muốn lên mặt scan; module đọc các vệt đó, tìm điểm giao, rồi nối
thành lưới quad bám mặt scan.

Không tạo NURBS curve nào trong scene — mọi bước trung gian là mảng điểm numpy,
chỉ chạm vào Maya ở hai đầu (đọc màu vertex vào, ghi mesh quad ra).

### Bước 1 — Hoạ sĩ sơn màu

Dùng `paint_flow` ở trên (hoặc `Mesh Display > Paint Vertex Color Tool` sẵn có
của Maya, nhớ bật `Display > Polygons > Color Set` để thấy màu).

Sơn **hai họ vệt cắt ngang nhau**, mỗi họ một màu (mặc định đỏ = dọc,
lục = ngang). Hai họ phải CẮT nhau mới thành ô lưới — các nét song song cùng
hướng thì không có điểm giao nào.

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
    conform_border=True,      # nối thêm dải quad từ rìa lưới ra viền part
)
print(retopo_paint.report_text(bao_cao))
```

Lưới dựng từ điểm giao luôn dừng ở nét vẽ ngoài cùng, còn hở một vành so với
viền part. `conform_border` **không kéo giãn hàng ngoài cùng ra cho khít** (làm
méo cả vùng rìa) mà giữ nguyên lưới rồi **thêm một dải quad nối ra viền** —
đúng cách hoạ sĩ vá biên bằng tay. Đỉnh mới nằm chính xác trên viền part nên hai
part cạnh nhau khâu lại được bằng cách merge đỉnh trùng vị trí.

Chỉ chạy được với part đã tách rời (có viền hở). Mesh kín thì báo "part không có
viền hở" và bỏ qua bước này.

### Bước 3 — Đọc báo cáo chấm điểm

```
Đã dựng: hood_retopo
  4 nét dọc × 3 nét ngang → 12 điểm giao → 6 quad
  Biên: nối 8 đỉnh ra viền part (kéo xa tb 0.31 · max 0.44)
  Lệch so với scan: tb 0.0268 · max 0.0465
  Tỉ lệ cạnh: tb 1.12 · max 1.84
  Độ vênh: tb 0.004 · max 0.02
  Pole (đỉnh khác 4 cạnh): 0
```

| Chỉ số | Ý nghĩa | Xử lý khi số xấu |
|---|---|---|
| Biên · kéo xa | Rìa lưới cách viền part bao xa — dải quad nối ra phải kéo chừng đó | Vẽ nét sát viền part hơn để dải biên khỏi bị kéo dài |
| Lệch so với scan | Tâm quad cách mặt scan bao xa — quad phẳng cắt góc ở chỗ cong | Vẽ thêm nét ở vùng cong để chia nhỏ ô |
| Tỉ lệ cạnh | Cạnh dài / cạnh ngắn, càng gần 1 càng vuông vắn | Vẽ nét đều tay hơn, tránh chỗ dày chỗ thưa |
| Độ vênh | Góc thứ 4 lệch khỏi mặt phẳng 3 góc kia | Như trên — ô nhỏ lại thì hết vênh |
| Pole | Đỉnh trong lòng lưới có số cạnh khác 4, dễ vỡ shading | Sửa tay, hoặc vẽ lại cho lưới đều |

## Giới hạn hiện tại

- **Chưa chạy thử trong Maya thật.** Phần logic thuần của cả hai module có bộ
  kiểm chạy bằng Maya giả (`tests/test_maya_tools.py`). Phần gọi API Maya thật
  (raycast, đọc/ghi vertex color, tạo mesh) phải chạy `tu_kiem()` mới biết.
- **Nét cọ càng rộng, đường tâm càng kém chính xác** ở hai đầu nét: vùng đầu mút
  được dựng lại bằng ngoại suy thẳng nên nét cong hụt độ cong trong đoạn đó. Sai
  số còn lại khoảng 1/5 khoảng cách vertex — muốn chính xác hơn thì vẽ nét mảnh
  hơn, hoặc vẽ dài quá chỗ cần giao một chút rồi để phần thừa ra ngoài.
- **Ô lưới thiếu góc bị bỏ qua**, không ép thành quad méo — chỗ hở sửa tay sau.
- **Dải conform chỉ dày một hàng quad.** Nếu rìa lưới cách viền part quá xa
  (xem "Biên · kéo xa" trong báo cáo), dải đó sẽ dài và méo — vẽ nét sát viền
  hơn thay vì trông chờ dải tự chia nhỏ.
- **Cọ chưa có vòng tròn xem trước** quanh con trỏ như ZBrush — hiện phải ước
  lượng độ lớn cọ qua nét vừa vẽ.
- Scan nhiều triệu điểm nên **giảm mật độ trước** (`polyReduce`/`polyRemesh`) rồi
  mới sơn và dựng lưới trên bản nhẹ.
