# NON-NEGOTIABLE RULE — Part-to-Part Topology Continuity

> **Core rule:** the topology MUST be designed as **ONE CONTINUOUS SURFACE FLOW SYSTEM ACROSS
> ADJACENT VEHICLE PARTS**. **NEVER** create independent topology grids for individual parts.

When two vehicle parts are visually or geometrically adjacent, their topology MUST connect and
transition logically between them. The edge flow must NOT stop at the boundary of one part and
restart as a new unrelated grid on the neighboring part.

This is a HARD REQUIREMENT.

Applies to: vehicle exterior models and to every topology-overlay image produced from them.

Quick terms:
- **Topology** — how the quad faces are arranged across the surface.
- **Edge loop** — a continuous ring/run of edges along or around the surface.
- **Pole** — a vertex with 3 or 5+ edges; it breaks reflection flow.
- **Panel gap** — the real shut line between two body panels (e.g. door to fender).

---

## 1. Procedure for EVERY pair of adjacent parts

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

---

## 2. Critical part pairs

### Door ↔ Fender

The door topology MUST connect naturally with the front fender.

**DO NOT create** — two independent topology systems merely touching:

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

**Instead** — the edge flow continues from the fender into the door:

```
    FENDER
    ╲ ╲ ╲ ╲ ╲──────────────→ DOOR
     ╲ ╲ ╲ ╲───────────────→→→→
      ╲ ╲────────────────────→→
       ╲──────────────────────→
```

The transition must follow the actual body curvature and character-line direction.

### Hood ↔ Fender

The hood and fender MUST share a logical topology relationship. The hood-side topology transitions
into the fender topology following the hood/fender curvature and boundary.

Do NOT terminate the hood grid at the hood gap and start a completely independent fender grid.
The topology around the hood gap must support the gap while remaining integrated with the
surrounding body topology.

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

The flow must redirect smoothly.

### Hood ↔ Roof / body center flow

Where surfaces transition from hood toward windshield, roof and upper body structure, topology
must maintain a logical continuous flow. Avoid abrupt topology termination at the windshield
boundary.

The surrounding body topology should redirect around the windshield opening while maintaining
continuity with: hood · A-pillar · roof · side body · fender.

### Roof ↔ A-Pillar ↔ Fender

**DO NOT create** three independent topology islands:

```
    ROOF GRID
       ↓
    A-PILLAR GRID
       ↓
    FENDER GRID
```

**Instead** — one continuous transition system:

```
    ROOF
    → → → → → → →
          ╲
           ╲ A-PILLAR
            ╲
             ╲
              → → → FENDER
```

The topology must redirect naturally around the windshield and side-window boundaries.

### Roof ↔ Glass ↔ Hood

Treat the visible relationship between glass, roof and hood as part of ONE CONTINUOUS TOPOLOGY
FLOW SYSTEM. Do NOT interpret the glass as an isolated unrelated surface.

The topology around the windshield/glass boundary must transition cleanly between: hood ·
windshield boundary · A-pillars · roof · side body.

The glass itself may be a separate physical material/object, but the BODY TOPOLOGY AROUND THE
GLASS must remain continuous.

**IMPORTANT DISTINCTION:** do NOT literally merge transparent glass geometry into the metal body
mesh. Instead, create continuous topology around the shared boundary and maintain clean
supporting loops around the glass opening.

### Roof ↔ Rear Glass ↔ C-Pillar ↔ Quarter Panel

The same continuity rule applies to the rear of the vehicle. Topology must transition logically
through:

```
ROOF → REAR GLASS BOUNDARY → C-PILLAR → QUARTER PANEL → REAR FENDER → REAR BUMPER
```

Do NOT create separate unrelated grids.

### Fender ↔ Wheel Arch ↔ Rocker

The wheel arch must NOT be treated as a circular topology island. The topology around the wheel
opening must transition into:

```
FENDER → WHEEL ARCH → ROCKER → DOOR → REAR QUARTER
```

The loops around the wheel arch must feed back into the surrounding body topology.

### Door ↔ Rocker ↔ Quarter Panel

The door topology must connect continuously with the front fender, the rocker and the rear
quarter panel. The lower door topology transitions naturally into the rocker topology; the rear
door boundary transitions naturally into the quarter panel.

Avoid isolated rectangular topology inside the door.

### Quarter Panel ↔ Rear Fender ↔ Bumper

The rear quarter topology must continue naturally into the rear fender, bumper, trunk boundary
and taillight opening. The topology should redirect around the taillight and bumper without
unnecessary loop termination.

### Bumper ↔ Fender ↔ Body

Bumper topology must connect logically with adjacent body surfaces. Do NOT create a completely
independent bumper grid that simply touches the fender.

The transition should preserve: curvature · reflection flow · density · quad direction.

### Lamp openings

For headlights and taillights, the lamp itself may be a separate object. However, the BODY
TOPOLOGY surrounding the lamp opening must connect continuously with the surrounding body:

```
BODY → LAMP OPENING → BODY
```

Use controlled loops around the opening and smoothly redirect those loops into the surrounding
surface topology, rather than creating a disconnected topology island.

---

## 3. Panel gap rule

A panel gap DOES NOT mean *"stop the topology here."*

> **PANEL GAP = TOPOLOGY REDIRECTION / SURFACE BOUNDARY GUIDE**

Topology on both sides of a panel gap must remain structurally related. Use supporting loops
around the gap to control the separation while preserving the overall surface-flow system.

## 4. Part boundary rule

For EVERY visible part boundary, ask: *"Where does the topology on this part continue?"*
The answer must always be visually understandable.

If an edge loop reaches a boundary, it must either:

1. Continue into the adjacent surface,
2. Redirect naturally into another valid loop,
3. Become a deliberate support loop around a feature,
4. Terminate only where there is a legitimate geometric reason.

NEVER terminate a loop simply because the panel ends.

## 5. No independent panel grids

ABSOLUTELY DO NOT generate independent door, fender, hood, roof, quarter-panel or bumper grids
that merely touch each other.

The final image must NOT look like multiple separate quad patches placed next to each other.
It must look like ONE continuous automotive topology system.

## 6. Topology flow test

After creating the topology, perform this mental test: choose any major edge loop on the vehicle
and follow it visually. Can the viewer understand where the loop goes when it reaches the door ·
fender · hood · roof · glass boundary · A-pillar · B-pillar · C-pillar · wheel arch · rocker ·
quarter panel · bumper · lamp opening?

If the loop suddenly stops or becomes an unrelated grid, **REDESIGN THAT AREA**.

## 7. Continuity priority

Topology continuity between adjacent parts has HIGHER PRIORITY than making each individual panel
look perfectly uniform.

| Prefer | Over |
|---|---|
| Continuous flow | Perfect individual panel grid |
| Surface curvature | Arbitrary edge direction |
| Reflection flow | Uniform quad size |

## 8. Final hard check

Before producing the final image, inspect the vehicle as ONE object. Verify:

- [ ] Door connects logically with Fender
- [ ] Door connects logically with Rocker
- [ ] Door connects logically with Quarter Panel
- [ ] Fender connects logically with Hood
- [ ] Fender connects logically with Wheel Arch
- [ ] Wheel Arch connects logically with Rocker
- [ ] Hood connects logically with Fender
- [ ] Hood topology transitions correctly toward windshield
- [ ] Roof connects logically with A-Pillar
- [ ] A-Pillar connects logically with Fender/body
- [ ] Roof connects logically with C-Pillar
- [ ] C-Pillar connects logically with Quarter Panel
- [ ] Quarter Panel connects logically with Rear Fender
- [ ] Rear Fender connects logically with Bumper
- [ ] Bumper connects logically with surrounding body
- [ ] Lamp openings redirect topology into surrounding body
- [ ] Glass boundaries have continuous supporting topology
- [ ] Panel gaps are respected without breaking topology logic
- [ ] No major visible surface contains an unnecessary topology island
- [ ] No arbitrary topology grid exists on an individual panel

**ONLY AFTER ALL CHECKS PASS should the topology overlay be finalized.**

---

Vietnamese version of this document: [`TOPOLOGY_LIEN_TUC_XE.md`](TOPOLOGY_LIEN_TUC_XE.md)
