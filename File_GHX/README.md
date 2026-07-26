# File_GHX — File Grasshopper gốc

Thư mục lưu các file định nghĩa Grasshopper thật (`.gh` / `.ghx`) để backup & tra cứu.

| File | Mô tả |
|---|---|
| `Vonoroi3.ghx` | File định nghĩa dạng XML (dễ đọc/parse). Chứa **2 definition**: (1) Đồng hồ lưới xoắn phyllotaxis, (2) Voronoi hoa hướng dương. |
| `Vonoroi3.gh` | Cùng nội dung, dạng nhị phân gốc của Grasshopper (mở trực tiếp trong Rhino/Grasshopper). |

> `.ghx` là bản XML của cùng file `.gh` — mở file nào trong Grasshopper cũng ra cùng graph. Dùng `.ghx` khi cần đọc/parse chính xác component, kết nối, giá trị slider, cờ Data Tree (Flatten/Graft).
