# Mechanics: Mathews / biomechanics → AvianWingRig features

This document maps real avian (and Mathews puppet) mechanics onto the L0–L2 rig features.

## 1. Reciprocal three-joint skeletal chain

**Biology / Mathews:** Humerus → ulna/radius → manus behave as a coupled extension system. Tendons and joint geometry make “open the wing” one gesture, not three independent hinges. Mathews’ wearable wings preserve that reciprocal feel so the wearer gets a large planform change with modest effort.

**Rig encoding:**

| Tier | Implementation |
|------|----------------|
| L0+ | Bones `AWR_*_Shoulder` → `_Elbow` → `_Wrist` |
| L0+ | Single float `awr_fold` (0 folded → 1 open) drives Euler lerp on each joint |
| L2 | Optional **trajectory presets** further couple wrist to elbow (see §6) |
| L2 | `awr_elastic` scales effective fold toward 0 (return-to-fold bias) |

Closed vs open angles live in `constants.py` (`FOLD_*_CLOSED` / `FOLD_*_OPEN`) and are easy to retarget per species.

## 2. Inter-feather ligament linkages

**Biology / Mathews:** Remiges are linked by elastic ligaments so feathers open **together**, preserving spacing. A sequential string cascade looks wrong (accordion). PigeonBot (Chang/Lentink) demonstrated underactuated feather arrays driven primarily from wrist/finger motion.

**Rig encoding:**

| Tier | Implementation |
|------|----------------|
| L1 | Each remige gets a fold-driven fan driver; bank opens as one sheet |
| L2 | Neighbor **ligament drivers** blend a remige’s rotation toward its neighbor, weighted by `awr_ligament_strength` |

This is a soft graph (pair edges), not a stiff IK chain — intentional, so artists can still override individual feathers.

## 3. Sheet cohesion between remiges

**Biology:** Barbules hook vanes into a continuous aerodynamic surface.

**Rig encoding:** Approximated by (a) coherent fan drivers, (b) ligament blending, (c) tunable `awr_fan_influence`. True cloth/mesh cohesion is left to the mesh (feather cards / groom) and is out of scope for v0.1 bones.

## 4. Independent alula control

**Biology / Mathews:** The alula (“bird thumb”) deploys at slow speed / landing for extra lift and stall control. Mathews includes operable alula on her builds; ornithologists notice.

**Rig encoding (L2):**

- Bone `AWR_L/R_Alula` parented to wrist
- Master prop `awr_alula` (0–1) + sidebar **Set / Toggle Alula**
- Independent of fold — you can land with fold mid-open and alula up

## 5. Low-effort elastic / gravity return toward fold

**Mathews:** Elastic elements and gravity help the wing return toward a folded rest so actuation stays light.

**Rig encoding (L2):**

- `awr_elastic` ∈ [0,1] reduces effective fold in skeletal drivers:  
  `effective_fold = fold * (1 - elastic)`
- Documented alternative for film: Blender **Spring** or dampened Anim constraint toward rest pose (see operator notes). For games, bake or recreate as a Control Rig spring interp.

## 6. Elbow–wrist trajectory presets

**Literature:** Harvey et al. (gull morphing) describe distinct elbow–wrist paths — anatomical **linkage**, **constant-lift**, and **constant-stability** style trajectories. Stowers et al. describe 3D coupling for morphing wings.

**Rig encoding (L2):**

| Preset | Behavior |
|--------|----------|
| `NONE` | Independent fold lerps only |
| `LINKAGE` | Wrist tracks ~0.55 × elbow flexion residual |
| `CONSTANT_LIFT` | Stronger wrist follow (~0.85) — lift-oriented morph |
| `CONSTANT_STABILITY` | Weaker follow (~0.35) — stability-oriented morph |

Applied via **Apply Trajectory Preset**; stored on master as `awr_trajectory`.

## 7. Human→bird ROM (documented, not fully automated in v0.1)

Mathews added lever length / hinge offsets so a human arm can reach bird-like aft sweep. The demo armature uses exaggerated fold closed angles for silhouette; a future “wearable adapter” bone offset is noted in `RESEARCH_BRIEF.md` but not required for game/film L0–L2.

## 8. Species planform

Demo counts (~10 primaries, 8 secondaries, 4 tertials) are magpie-inspired and kept small for procedural clarity. Change `PRIMARY_COUNT` / `SECONDARY_COUNT` / `TERTIAL_COUNT` in `constants.py` for other species; outlines belong on the mesh.

## Animator mental model

```
awr_fold  ──────────►  shoulder / elbow / wrist  (reciprocal open)
    │
    ├──(L1+)────────►  remige fan banks
    │         └──(L2)► neighbor ligament blend
    │
awr_alula (L2) ─────►  alula bones (independent)
trajectory (L2) ────►  elbow↔wrist coupling ratio
elastic (L2) ───────►  bias toward folded rest
```

One primary gesture (**fold**), plus optional alula and trajectory character.
