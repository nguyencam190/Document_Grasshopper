# File_GHX — File Grasshopper gốc

Thư mục lưu các file định nghĩa Grasshopper thật (`.gh` / `.ghx`) để backup & tra cứu.

| File | Mô tả |
|---|---|
| `Vonoroi_Phyllotaxis.ghx` | File định nghĩa dạng XML (dễ đọc/parse). Chứa **2 definition**: (1) Đồng hồ lưới xoắn phyllotaxis, (2) Voronoi hoa hướng dương. |
| `Vonoroi_01.ghx` | Voronoi **mạng dây cung (rosette)**: 17 điểm trên vòng → Line all-pairs (Graft) → điểm gieo → Voronoi → cắt trong vòng → offset/fillet → đùn 2 lớp. Xem trang "Voronoi mạng dây cung" trong Example Step-by-Step. |

> `.ghx` là bản XML của file Grasshopper — mở trong Grasshopper ra đúng graph. Dùng `.ghx` khi cần đọc/parse chính xác component, kết nối, giá trị slider, cờ Data Tree (Flatten/Graft).
