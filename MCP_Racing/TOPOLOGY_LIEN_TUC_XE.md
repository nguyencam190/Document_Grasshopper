# Quy tắc BẮT BUỘC — Topology liên tục giữa các mảnh vỏ xe

> **Luật gốc:** Topology của cả chiếc xe phải là **MỘT hệ thống dòng chảy bề mặt duy nhất**,
> chảy xuyên qua ranh giới giữa các mảnh vỏ (part) kề nhau.
> **KHÔNG BAO GIỜ** dựng lưới riêng lẻ cho từng mảnh rồi đặt cạnh nhau.

Bản tiếng Anh của tài liệu này: [`VEHICLE_TOPOLOGY_CONTINUITY.md`](VEHICLE_TOPOLOGY_CONTINUITY.md)

Áp dụng cho: model vỏ ngoài xe (`vehicle_exterior`) và cho mọi ảnh overlay topology sinh ra để
minh hoạ. Đây là luật cứng — không phải gợi ý.

Thuật ngữ nhanh cho người mới:
- **Topology** = cách sắp xếp các ô lưới (quad) trên bề mặt model.
- **Edge loop** = một vòng cạnh chạy liên tục quanh/dọc bề mặt.
- **Pole** = điểm có 3 hoặc 5+ cạnh chụm vào, làm bề mặt gãy phản chiếu.
- **Panel gap** = khe hở giữa 2 mảnh vỏ thật (vd khe giữa cửa và tai xe).

---

## 1. Quy trình cho MỌI cặp mảnh kề nhau

Với mỗi cặp part nằm sát nhau, làm đủ 10 bước:

1. Xác định đường biên chung của 2 mảnh.
2. Xác định hướng cong chủ đạo của bề mặt ở **cả hai** phía.
3. Cho edge flow chạy tiếp từ mảnh này sang mảnh kia.
4. Bẻ hướng topology **từ từ** nếu hướng bề mặt đổi.
5. Giữ khoảng cách quad hợp lý khi chuyển tiếp.
6. Không đổi hướng cạnh đột ngột.
7. Không đổi mật độ lưới đột ngột.
8. Không tạo pole thừa ngay tại biên.
9. Không kết thúc loop khi chưa cần.
10. Giữ dòng phản chiếu (reflection flow) liên tục qua chỗ chuyển tiếp.

Kết quả nhìn bằng mắt phải đọc ra là **một hệ topology liền mạch**.

---

## 2. Các cặp part quan trọng

### Cửa ↔ Tai xe trước (Door ↔ Fender)

**SAI** — hai hệ topology độc lập chỉ chạm nhau:

```
    FENDER
    ┌─────────────┐
    │ /////////   │
    │ /////////   │
    └─────────────┘
                  ||
                  ||
    ┌─────────────┐
    │ /////////   │
    │ /////////   │
    └─────────────┘
    DOOR
```

**ĐÚNG** — edge flow chảy tiếp từ tai xe sang cửa:

```
    FENDER
    ╲ ╲ ╲ ╲ ╲──────────────→ DOOR
     ╲ ╲ ╲ ╲───────────────→→→→
      ╲ ╲────────────────────→→
       ╲──────────────────────→
```

Hướng chuyển tiếp phải bám theo độ cong thân xe thật và hướng **character line**
(đường gân tạo hình chạy dọc thân xe).

### Nắp capo ↔ Tai xe (Hood ↔ Fender)

Không kết thúc lưới capo tại khe capo rồi bắt đầu lưới tai xe hoàn toàn mới.
Topology quanh khe capo phải **đỡ được khe** mà vẫn nằm trong hệ topology thân xe.

```
        HOOD
    → → → → → → →
     → → → → → → →
      ╲
       ╲
        ╲ → → → FENDER
         ╲ → → → → → →
          ╲ → → → → →
```

### Capo ↔ Nóc ↔ Trục giữa thân (Hood ↔ Roof)

Không để topology dừng đột ngột ở biên kính chắn gió. Lưới thân xe phải **vòng quanh**
ô kính và giữ liên tục với: capo · trụ A · nóc · hông xe · tai xe.

### Nóc ↔ Trụ A ↔ Tai xe (Roof ↔ A-Pillar ↔ Fender)

**SAI** — ba đảo topology rời nhau:

```
    ROOF GRID
       ↓
    A-PILLAR GRID
       ↓
    FENDER GRID
```

**ĐÚNG** — một hệ chuyển tiếp liên tục:

```
    ROOF
    → → → → → → →
          ╲
           ╲ A-PILLAR
            ╲
             ╲
              → → → FENDER
```

### Nóc ↔ Kính ↔ Capo (Roof ↔ Glass ↔ Hood)

Coi quan hệ nhìn thấy được giữa kính, nóc và capo là **một hệ dòng chảy topology duy nhất**.
Không coi kính là bề mặt rời rạc không liên quan.

**Phân biệt quan trọng:** KHÔNG gộp hình học kính trong suốt vào mesh vỏ kim loại.
Kính vẫn là vật thể/vật liệu riêng — nhưng **topology vỏ xe quanh kính** phải liên tục,
có support loop sạch bao quanh ô kính.

### Nóc ↔ Kính sau ↔ Trụ C ↔ Hông sau

Luật y hệt cho phía sau xe, chuỗi chuyển tiếp:

```
ROOF → REAR GLASS BOUNDARY → C-PILLAR → QUARTER PANEL → REAR FENDER → REAR BUMPER
```

### Tai xe ↔ Vòm bánh ↔ Bệ hông (Fender ↔ Wheel Arch ↔ Rocker)

Vòm bánh **không phải** một đảo topology hình tròn. Các loop quanh vòm bánh phải đổ ngược
vào topology thân xe xung quanh:

```
FENDER → WHEEL ARCH → ROCKER → DOOR → REAR QUARTER
```

### Cửa ↔ Bệ hông ↔ Hông sau

Cửa phải nối liên tục với tai xe trước, bệ hông và hông sau. Phần dưới cửa chuyển tiếp tự nhiên
vào bệ hông; biên sau cửa chuyển tiếp tự nhiên vào hông sau.
Tránh lưới chữ nhật biệt lập nằm gọn trong cửa.

### Hông sau ↔ Tai xe sau ↔ Cản (Quarter ↔ Rear Fender ↔ Bumper)

Topology hông sau chảy tiếp vào tai xe sau, cản sau, biên cốp và ô đèn hậu — vòng quanh đèn hậu
và cản mà không kết thúc loop vô cớ.

### Cản ↔ Tai xe ↔ Thân (Bumper ↔ Fender ↔ Body)

Không dựng lưới cản độc lập chỉ chạm vào tai xe. Chuyển tiếp phải giữ được: độ cong ·
dòng phản chiếu · mật độ · hướng quad.

### Ô đèn (Lamp openings)

Đèn pha/đèn hậu có thể là vật thể riêng, nhưng topology vỏ xe quanh ô đèn phải chảy:

```
BODY → LAMP OPENING → BODY
```

Dùng loop có kiểm soát quanh ô đèn rồi bẻ các loop đó mượt vào bề mặt xung quanh —
không tạo đảo topology rời.

---

## 3. Luật khe panel (Panel gap)

Khe panel **KHÔNG** có nghĩa là "dừng topology tại đây".

> **PANEL GAP = ĐIỂM BẺ HƯỚNG TOPOLOGY / ĐƯỜNG DẪN BIÊN BỀ MẶT**

Topology hai bên khe vẫn phải liên quan nhau về cấu trúc. Dùng support loop quanh khe để kiểm soát
phần tách rời mà vẫn giữ nguyên hệ dòng chảy bề mặt tổng thể.

## 4. Luật biên part

Với **mọi** biên part nhìn thấy được, tự hỏi: *"Topology của mảnh này đi tiếp về đâu?"*
Câu trả lời luôn phải nhìn ra được bằng mắt. Một edge loop chạm biên chỉ được phép:

1. Chảy tiếp sang bề mặt kề bên, hoặc
2. Bẻ tự nhiên vào một loop hợp lệ khác, hoặc
3. Trở thành support loop có chủ đích quanh một chi tiết, hoặc
4. Kết thúc — chỉ khi có **lý do hình học chính đáng**.

KHÔNG BAO GIỜ kết thúc một loop chỉ vì mảnh vỏ hết ở đó.

## 5. Cấm tuyệt đối — lưới panel độc lập

Không sinh ra lưới độc lập chỉ chạm nhau cho: cửa · tai xe · capo · nóc · hông sau · cản.

Ảnh kết quả **không được** trông như nhiều mảng quad rời đặt cạnh nhau — phải trông như
một hệ topology ô tô liên tục.

## 6. Bài test dòng chảy topology

Sau khi dựng xong, chọn một edge loop lớn bất kỳ và dõi theo bằng mắt. Người xem có hiểu được
loop đó đi đâu khi chạm tới: cửa · tai xe · capo · nóc · biên kính · trụ A · trụ B · trụ C ·
vòm bánh · bệ hông · hông sau · cản · ô đèn không?

Nếu loop dừng đột ngột hoặc biến thành một lưới không liên quan → **DỰNG LẠI vùng đó**.

## 7. Thứ tự ưu tiên

| Ưu tiên | Hơn |
|---|---|
| Dòng chảy liên tục | Lưới từng panel hoàn hảo |
| Độ cong bề mặt | Hướng cạnh tuỳ tiện |
| Dòng phản chiếu | Quad đều tăm tắp |

Liên tục giữa các part **quan trọng hơn** việc từng panel trông đều đẹp riêng lẻ.

## 8. Checklist chốt cuối

Nhìn cả xe như MỘT vật thể, kiểm đủ trước khi chốt overlay topology:

- [ ] Cửa nối hợp lý với tai xe
- [ ] Cửa nối hợp lý với bệ hông
- [ ] Cửa nối hợp lý với hông sau
- [ ] Tai xe nối hợp lý với capo
- [ ] Tai xe nối hợp lý với vòm bánh
- [ ] Vòm bánh nối hợp lý với bệ hông
- [ ] Capo nối hợp lý với tai xe
- [ ] Topology capo chuyển tiếp đúng về phía kính chắn gió
- [ ] Nóc nối hợp lý với trụ A
- [ ] Trụ A nối hợp lý với tai xe/thân xe
- [ ] Nóc nối hợp lý với trụ C
- [ ] Trụ C nối hợp lý với hông sau
- [ ] Hông sau nối hợp lý với tai xe sau
- [ ] Tai xe sau nối hợp lý với cản
- [ ] Cản nối hợp lý với thân xe xung quanh
- [ ] Ô đèn bẻ topology vào thân xe xung quanh
- [ ] Biên kính có topology đỡ liên tục
- [ ] Khe panel được tôn trọng mà không phá logic topology
- [ ] Không bề mặt lớn nào chứa đảo topology thừa
- [ ] Không panel nào có lưới tuỳ tiện

**Chỉ khi ĐỦ mọi mục trên mới được chốt.**

---

## Phụ lục — Bản gốc tiếng Anh (copy nguyên văn để dùng làm prompt)

```text
# NON-NEGOTIABLE RULE — PART-TO-PART TOPOLOGY CONTINUITY

## ABSOLUTE REQUIREMENT

The topology MUST be designed as ONE CONTINUOUS SURFACE FLOW SYSTEM
ACROSS ADJACENT VEHICLE PARTS.

NEVER create independent topology grids for individual parts.

When two vehicle parts are visually or geometrically adjacent,
their topology MUST connect and transition logically between them.

The edge flow must NOT stop at the boundary of one part and restart
as a new unrelated grid on the neighboring part.

This is a HARD REQUIREMENT.

# PART-TO-PART CONTINUITY

For EVERY pair of adjacent vehicle parts:

1. Identify the shared boundary.
2. Identify the dominant surface curvature on both sides.
3. Continue the edge flow from one part into the adjacent part.
4. Redirect the topology gradually if the surface direction changes.
5. Maintain reasonable quad spacing across the transition.
6. Avoid abrupt changes in edge direction.
7. Avoid sudden topology-density changes.
8. Avoid unnecessary poles at the boundary.
9. Avoid terminating loops unnecessarily.
10. Preserve continuous reflection flow across the transition.

The topology must visually read as ONE connected topology system.

# CRITICAL EXAMPLES

## DOOR <-> FENDER

The Door topology MUST connect naturally with the Front Fender.

DO NOT create:

    FENDER
    ┌─────────────┐
    │ /////////   │
    │ /////////   │
    └─────────────┘
                  ||
                  ||
    ┌─────────────┐
    │ /////////   │
    │ /////////   │
    └─────────────┘
    DOOR

This represents two independent topology systems.

Instead, the edge flow must continue from the fender into the door:

    FENDER
    ╲ ╲ ╲ ╲ ╲──────────────→ DOOR
     ╲ ╲ ╲ ╲───────────────→→→→
      ╲ ╲────────────────────→→
       ╲──────────────────────→

The transition must follow the actual body curvature and
character-line direction.

# HOOD <-> FENDER

The Hood and Fender MUST share a logical topology relationship.

The hood-side topology must transition into the fender topology
following the hood/fender curvature and boundary.

Do NOT terminate the hood grid at the hood gap and start a
completely independent fender grid.

The topology around the hood gap must support the gap while
remaining integrated with the surrounding body topology.

Conceptually:

        HOOD
    → → → → → → →
     → → → → → → →
      ╲
       ╲
        ╲ → → → FENDER
         ╲ → → → → → →
          ╲ → → → → →

The flow must redirect smoothly.

# HOOD <-> ROOF / BODY CENTER FLOW

Where surfaces transition from hood toward windshield,
roof and upper body structure, topology must maintain a
logical continuous flow.

Avoid abrupt topology termination at the windshield boundary.

The surrounding body topology should redirect around the
windshield opening while maintaining continuity with:

- hood
- A-pillar
- roof
- side body
- fender

# ROOF <-> A-PILLAR <-> FENDER

The Roof, A-Pillar and Fender must form a continuous topology
transition system.

DO NOT create:

    ROOF GRID
       ↓
    A-PILLAR GRID
       ↓
    FENDER GRID

as three independent topology islands.

Instead:

    ROOF
    → → → → → → →
          ╲
           ╲ A-PILLAR
            ╲
             ╲
              → → → FENDER

The topology must redirect naturally around the windshield
and side-window boundaries.

# ROOF <-> GLASS <-> HOOD

IMPORTANT:

Treat the visible relationship between the Glass, Roof and Hood
as part of ONE CONTINUOUS TOPOLOGY FLOW SYSTEM.

Do NOT interpret the glass as an isolated unrelated surface.

The topology around the windshield/glass boundary must transition
cleanly between:

- hood
- windshield boundary
- A-pillars
- roof
- side body

The glass itself may be a separate physical material/object,
but the BODY TOPOLOGY AROUND THE GLASS must remain continuous.

IMPORTANT DISTINCTION:

Do NOT literally merge transparent glass geometry into the metal
body mesh.

Instead, create continuous topology around the shared boundary
and maintain clean supporting loops around the glass opening.

# ROOF <-> REAR GLASS <-> C-PILLAR <-> QUARTER PANEL

The same continuity rule applies to the rear of the vehicle.

Topology must transition logically through:

ROOF -> REAR GLASS BOUNDARY -> C-PILLAR -> QUARTER PANEL
-> REAR FENDER -> REAR BUMPER

Do NOT create separate unrelated grids.

# FENDER <-> WHEEL ARCH <-> ROCKER

The wheel arch must NOT be treated as a circular topology island.

The topology around the wheel opening must transition into:

FENDER -> WHEEL ARCH -> ROCKER -> DOOR -> REAR QUARTER

The loops around the wheel arch must feed back into the
surrounding body topology.

# DOOR <-> ROCKER <-> QUARTER PANEL

The Door topology must connect continuously with:

- front fender
- rocker
- rear quarter panel

The lower door topology must transition naturally into the
rocker topology.

The rear door boundary must transition naturally into the
quarter panel.

Avoid isolated rectangular topology inside the door.

# QUARTER PANEL <-> REAR FENDER <-> BUMPER

The rear quarter topology must continue naturally into:

- rear fender
- bumper
- trunk boundary
- taillight opening

The topology should redirect around the taillight and bumper
without unnecessary loop termination.

# BUMPER <-> FENDER <-> BODY

Bumper topology must connect logically with adjacent body surfaces.

Do NOT create a completely independent bumper grid that simply
touches the fender.

The transition should preserve:

- curvature
- reflection flow
- density
- quad direction

# LAMP OPENINGS

For headlights and taillights:

The lamp itself may be a separate object.

However, the BODY TOPOLOGY surrounding the lamp opening must
connect continuously with the surrounding body.

The topology must flow:

BODY -> LAMP OPENING -> BODY

rather than creating a disconnected topology island.

Use controlled loops around the opening and smoothly redirect
those loops into the surrounding surface topology.

# PANEL GAP RULE

A panel gap DOES NOT mean:

"STOP THE TOPOLOGY HERE."

Instead:

PANEL GAP = TOPOLOGY REDIRECTION / SURFACE BOUNDARY GUIDE

Topology on both sides of a panel gap must remain structurally
related.

Use supporting loops around the gap to control the separation
while preserving the overall surface-flow system.

# PART BOUNDARY RULE

For EVERY visible part boundary, ask:

"Where does the topology on this part continue?"

The answer must always be visually understandable.

If an edge loop reaches a boundary, it must either:

1. Continue into the adjacent surface,
2. Redirect naturally into another valid loop,
3. Become a deliberate support loop around a feature,
4. Terminate only where there is a legitimate geometric reason.

NEVER terminate a loop simply because the panel ends.

# NO INDEPENDENT PANEL GRIDS

ABSOLUTELY DO NOT generate:

- independent door grid
- independent fender grid
- independent hood grid
- independent roof grid
- independent quarter-panel grid
- independent bumper grid

that merely touch each other.

The final image must NOT look like multiple separate
quad patches placed next to each other.

It must look like ONE continuous automotive topology system.

# TOPOLOGY FLOW TEST

After creating the topology, perform this mental test:

Choose any major edge loop on the vehicle.

Follow it visually.

Can the viewer understand where the loop goes when it reaches:

- Door?
- Fender?
- Hood?
- Roof?
- Glass boundary?
- A-pillar?
- B-pillar?
- C-pillar?
- Wheel arch?
- Rocker?
- Quarter panel?
- Bumper?
- Lamp opening?

If the loop suddenly stops or becomes an unrelated grid,
REDESIGN THAT AREA.

# CONTINUITY PRIORITY

Topology continuity between adjacent parts has HIGHER PRIORITY
than making each individual panel look perfectly uniform.

Prefer:

CONTINUOUS FLOW
over
PERFECT INDIVIDUAL PANEL GRID

Prefer:

SURFACE CURVATURE
over
ARBITRARY EDGE DIRECTION

Prefer:

REFLECTION FLOW
over
UNIFORM QUAD SIZE

# FINAL HARD CHECK

Before producing the final image, inspect the vehicle as ONE object.

Verify:

[ ] Door connects logically with Fender
[ ] Door connects logically with Rocker
[ ] Door connects logically with Quarter Panel
[ ] Fender connects logically with Hood
[ ] Fender connects logically with Wheel Arch
[ ] Wheel Arch connects logically with Rocker
[ ] Hood connects logically with Fender
[ ] Hood topology transitions correctly toward windshield
[ ] Roof connects logically with A-Pillar
[ ] A-Pillar connects logically with Fender/body
[ ] Roof connects logically with C-Pillar
[ ] C-Pillar connects logically with Quarter Panel
[ ] Quarter Panel connects logically with Rear Fender
[ ] Rear Fender connects logically with Bumper
[ ] Bumper connects logically with surrounding body
[ ] Lamp openings redirect topology into surrounding body
[ ] Glass boundaries have continuous supporting topology
[ ] Panel gaps are respected without breaking topology logic
[ ] No major visible surface contains an unnecessary topology island
[ ] No arbitrary topology grid exists on an individual panel

ONLY AFTER ALL CHECKS PASS should the topology overlay be finalized.
```
