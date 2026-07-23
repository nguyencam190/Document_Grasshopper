# Bảng phân loại Tab/Panel Grasshopper thật

App đã có sẵn 13 trang danh mục con của `seed-grasshopper`, khớp đúng các tab ribbon thật của
Grasshopper:

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

**Mỗi tab lại chia nhỏ thành nhiều "panel" (nhóm con) — khớp đúng cách Grasshopper thật nhóm icon
trên ribbon** (vd tab Params có 5 panel: Geometry, Primitive, Input, Rhino, Util — xem ribbon thật
trong Grasshopper, KHÔNG suy đoán, vì thứ tự/tên panel dễ sai giữa các phiên bản Rhino). Trang 1
lệnh cụ thể (vd "Loft") phải nằm trong đúng **trang panel** (`seed-panel-{tab}-{panel}`), KHÔNG trỏ
thẳng vào trang tab. Panel đã xác nhận xong (từ ảnh chụp ribbon thật của user):

| Tab | Panel (đúng thứ tự trái→phải) |
|---|---|
| Params | Geometry, Primitive, Input, Rhino, Util |
| Maths | Domain, Matrix, Operators, Polynomials, Script, Time, Trig, Util |
| Sets | List, Sequence, Sets, Text, Tree |
| Vector | Field, Grid, Plane, Point, Vector |
| Curve | Analysis, Division, Primitive, Spline, Util |
| Surface | Analysis, Freeform, Primitive, SubD, Util |
| Mesh | Analysis, Primitive, Triangulation, Util |
| Intersect | Mathematical, Physical, Region, Shape |
| Transform | Affine, Array, Euclidean, Morph, Util |
| Display | Colour, Dimensions, Graphs, Preview, Vector |
| Rhino | Content, Objects, Model, Drafting, Annotations, Render, Viewports |
| Kangaroo2 | Goals-6dof, Goals-Angle, Goals-Co, Goals-Col, Goals-Lin, Goals-Mesh, Goals-On, Goals-Pt, Main, Mesh, Utility |
| Wb (Weaverbird) | Create, Define, Extract, Smoothen, SubD, Transform |

Id mỗi trang panel theo mẫu `seed-panel-{tab-slug}-{panel-slug}` (vd `seed-panel-maths-domain`),
`parentId` trỏ vào đúng trang tab cha (vd `seed-tab-maths`). Ví dụ: lệnh **Loft** thuộc tab Surface,
panel **Freeform** → `parentId` trỏ vào `seed-panel-surface-freeform`.

**Cả 13/13 tab đã có đủ panel, xác nhận bằng ảnh chụp ribbon thật của user (không phải suy đoán/
nghiên cứu online).** Vài lưu ý quan trọng phát hiện được khi đối chiếu ảnh thật với nghiên cứu
online trước đó (bài học: luôn ưu tiên ảnh chụp thật hơn tài liệu online khi có mâu thuẫn):

- **Kangaroo2 thực tế chỉ có 11 panel**, KHÔNG phải 15 như nghiên cứu online suy đoán — panel
  "Goals" (không hậu tố), "Morph", "SubD", "Triangulation" KHÔNG tồn tại trong ribbon thật.
- **Tên panel Wb (Weaverbird) trong ribbon thật KHÔNG có tiền tố "Wb "** (chỉ là "Create", "Define"...
  — không phải "Wb Create", "Wb Define"...) dù nghiên cứu online ghi vậy.
- **"Goals-Co" trong Kangaroo2** — chưa xác định CHẮC CHẮN 100% ý nghĩa viết tắt "Co" (không nhầm
  với "Goals-Col"/Collision đứng cạnh nó). Sau khi nghiên cứu component **Coincident** (component
  đầu tiên trong panel này), có dấu hiệu "Co" là viết tắt nhóm goal có tên bắt đầu bằng "Co-"
  (Coincident, CoSpherical, Concentric, Conicalize...) — vẫn chỉ là GIẢ THUYẾT dựa trên mẫu tên gọi
  (không phải xác nhận qua ảnh ribbon thật), cần thêm component nữa trong panel mới kết luận chắc.

**Phân loại phải khớp 100% với Grasshopper thật, không được áng chừng/đoán đại.** Trước khi gán
`parentId`, xác nhận đúng tab mà lệnh nằm trong ribbon Grasshopper thật (ưu tiên tra theo đúng thứ
tự nguồn tham khảo ở skill `nghien-cuu-grasshopper`: tài liệu chính thức Rhino/GH trước, rồi AAD,
rồi tài liệu Plugin nếu lệnh thuộc Plugin như Kangaroo2/Weaverbird). Nếu tra không ra hoặc không
chắc chắn lệnh thuộc tab nào, PHẢI dừng lại hỏi user thay vì tự đoán và gán bừa — gán sai tab còn
tệ hơn không phân loại, vì sẽ làm sai cấu trúc doc lâu dài.
