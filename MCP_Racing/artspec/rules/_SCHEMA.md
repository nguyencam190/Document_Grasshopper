# Schema của 1 file rule

Mỗi quy tắc = 1 file YAML trong `rules/<asset_class>/`. Tên file = `id` của rule.

| Field | Bắt buộc | Ý nghĩa |
|---|---|---|
| `id` | ✅ | Mã trích dẫn, vd `VEH-TRI-001`. Duy nhất toàn hệ thống |
| `title` | ✅ | Tên ngắn của luật |
| `asset_class` | ✅ | Class áp dụng, vd `vehicle_exterior` |
| `category` | ✅ | `geometry` `uv` `texture` `material` `naming` `transform` `rig` `lod` `export` `visual` |
| `tier` | ✅ | `A` = số/regex máy kiểm · `B` = logic riêng cần hàm · `C` = người kiểm |
| `severity` | ✅ | `fail` (chặn gate) · `warn` (cho qua, ghi lại) · `info` |
| `stage` | ✅ | Gate mà luật này được kiểm: `G0` `G1` `G2` `G3` |
| `check` | ✅ | Khối định nghĩa cách kiểm — xem bên dưới |
| `why` | ✅ | Vì sao có luật này. **Vào thẳng thông điệp lỗi** |
| `how_to_fix` | ✅ | Các bước sửa. **Vào thẳng thông điệp lỗi** |
| `how_to_check` | | Hoạ sĩ tự đo bằng cách nào trong DCC |
| `common_mistakes` | | Danh sách lý do hay mắc. **Vào thẳng thông điệp lỗi** |
| `reference` | | `{golden_asset, note}` — chỉ tới asset mẫu |
| `source` | | `{system, url, section}` — link về techspec gốc |
| `version` | ✅ | Số nguyên, tăng mỗi lần đổi nội dung luật |
| `effective_from` | ✅ | Ngày hiệu lực (YYYY-MM-DD) |
| `status` | ✅ | `active` · `draft` · `superseded` (chỉ `active` mới được chạy) |
| `changed_by_update` | | Mã update khách hàng đã sinh ra thay đổi này |

## Các `check.type` có sẵn

| type | Tier | Dùng cho | Field |
|---|---|---|---|
| `threshold` | A | So sánh 1 số với 1 ngưỡng | `applies_to` `metric` `op` `value` |
| `threshold_table` | A | Ngưỡng đổi theo LOD/platform | `applies_to` `metric` `op` `table` |
| `regex` | A | Kiểm tên | `applies_to` `metric` `pattern` |
| `enum` | A | Giá trị phải nằm trong tập cho phép | `applies_to` `metric` `allowed` |
| `custom` | B | Logic riêng của dự án | `function` `params` |
| `manual` | C | Người kiểm, máy chỉ nhắc | `ask` |

`check.requires` (tuỳ chọn) = danh sách đường dẫn dữ liệu mà luật cần mới có
nghĩa, vd `requires: [skeleton.bones]`. Thiếu thì luật báo **SKIP**, không báo
FAIL — một file body mesh không rig thì luật về bone bánh xe không liên quan
đến nó, báo FAIL là báo sai.

`applies_to` = `{collection: meshes|textures|bones, where: {field: value}}`.
`where` khớp trên **ngữ cảnh gộp**: field của item + các field vô hướng ở gốc metrics
(vd `platform`), nên viết `where: {lod: 0, platform: pc}` được.

## Thêm 1 luật đặc thù của dự án

- **Tier A** — chỉ thêm 1 file YAML. Không đụng code.
- **Tier B** — thêm 1 file YAML + 1 hàm trong `artspec/checks/vehicle.py`
  (hoặc file mới), đăng ký bằng decorator `@custom_check("tên.hàm")`.
- **Tier C** — chỉ thêm 1 file YAML với `type: manual`. Nó thành câu hỏi trong checklist.

Không trường hợp nào phải sửa `server.py` hay `engine.py`.
