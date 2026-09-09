# Unreal Engine 5 Control Rig — rebuild L0–L2

Step-by-step guide to recreate AvianWingRig behavior in **UE5 Control Rig**, matching Blender naming and the fold-first mental model.

Assumes: UE5.3+ , a skeletal mesh with bones named like the Blender demo (or a rename table), and familiarity with the Control Rig editor.

---

## Shared vocabulary

| Concept | Blender | Unreal |
|---------|---------|--------|
| Fold float | `AWR_Master["awr_fold"]` | Control Rig float `awr_fold` (0–1) |
| Alula | `awr_alula` | Float `awr_alula` |
| Trajectory | enum string | Enum / int `awr_trajectory` |
| Shoulder/Elbow/Wrist | `AWR_L_Shoulder` … | Same bone names on skeleton |
| Remiges | `AWR_L_P00` … | Same |

Export from Blender after **Bake Constraints for Export** (or export with deformations baked) so the UE skeleton matches bind pose.

---

## L0 — Game-light Control Rig

### Goal
One float opens/closes the wing; shoulder can still receive a flap additive from AnimBP.

### Steps

1. **Create Control Rig asset**  
   Content Browser → Animation → Control Rig → based on your bird skeleton.

2. **Add controls**
   - `CTRL_Fold` (Float, default 0, clamp 0–1) — or a Null with a float channel.
   - Optional `CTRL_L_ShoulderFlap` / `CTRL_R_ShoulderFlap` (Rotator) for manual flap.

3. **Setup graph — fold lerp**
   For each side (L, R):
   - Read bone `AWR_*_Shoulder`, `_Elbow`, `_Wrist` (or use **Get Transform**).
   - Define two Rotators per bone: `Folded` and `Open` (match `constants.py` angles; convert degrees in UE).
   - **RBF / Interpolate** (or Lerp Rotator):  
     `R = Lerp(Folded, Open, awr_fold)`
   - **Set Bone Transform** (local space) with `R`.

4. **Additive flap**
   - After fold, **Compose** shoulder rotation with `CTRL_*_ShoulderFlap` (local offset).
   - AnimBP can drive that control from a flap curve.

5. **Compile & test**
   - Scrub `awr_fold` 0→1 in Control Rig viewport.
   - Mirror: duplicate nodes for R with negated Z (or Y) where needed.

6. **AnimBP hook**
   - Linked Anim Graph or Control Rig node: expose `awr_fold` as a pin; drive from flight state (glide=1, perch=0).

### Bake / runtime note
L0 is cheap enough to run live in Control Rig. For mobile, bake fold poses to an additive anim sequence.

---

## L1 — Remige banks

### Goal
Primaries / secondaries / tertials fan with fold; tunable influence.

### Steps

1. Ensure remige bones exist on the skeleton (export L1 Blender rig or add sockets/bones in DCC).

2. In Control Rig, add float `awr_fan_influence` (0–1, default 1).

3. For each bank:
   - Index feathers `i = 0 … N-1`.
   - `t = i / (N-1) - 0.5`  → range ≈ [-0.5, 0.5]
   - `spread = t * 2 * MaxSpread * awr_fold * awr_fan_influence`
   - Apply as local Rz (or the axis that fans along the sheet).

4. Parenting:
   - Primaries: under wrist
   - Secondaries / tertials: under elbow (or forearm)

5. Optional **Collection** / array foreach in CR to avoid copy-paste.

### Sheet cohesion
Keep a single fold input — do **not** stagger delays (that creates cascade). If you need soft secondary motion, use a short spring **after** the coherent target, not before.

---

## L2 — Ligaments, alula, trajectories, elastic

### 5a. Elastic return

```
effective_fold = awr_fold * (1 - awr_elastic)
```

Use `effective_fold` everywhere L0/L1 used `awr_fold`.  
Optional: **Spring Interpolate** the displayed fold toward 0 when input is released (input gate from AnimBP).

### 5b. Alula

1. Float `awr_alula` (0–1).
2. Bone `AWR_L_Alula` / `AWR_R_Alula`.
3. Lerp local rotation from retracted → deployed (~50° around the chosen local axis).
4. Expose to AnimBP as “landing” / “slow flight” bool → float.

### 5c. Ligament neighbor coupling

For remige index `i` with neighbor `j = i+1` (last uses `i-1`):

```
base = fan_target(i, effective_fold, influence)
nbr  = current_or_target(j)
out  = Lerp(base, nbr, awr_ligament_strength * 0.35)
```

Apply `out` to bone `i`.  
Use **targets** (not post-solve transforms) if you need a stable non-feedback solve; for a one-pass CR graph, compute all `base[]` first, then blend.

### 5d. Trajectory presets

Add enum:

| Value | Wrist coupling ratio |
|-------|----------------------|
| None | — |
| Linkage | 0.55 |
| ConstantLift | 0.85 |
| ConstantStability | 0.35 |

Implementation sketch:

1. Compute elbow rotation from fold (L0).
2. Compute wrist_base from fold.
3. `wrist = wrist_base + (elbow - elbow_base_from_fold) * ratio`  
   (same idea as Blender `apply_trajectory_coupling`).

Tune ratios against Harvey et al. curves if you need species-accurate paths; store curves as CR Curve floats for hero characters.

---

## Suggested UE asset set

```
CR_AvianWing_L0
CR_AvianWing_L1   (includes L0)
CR_AvianWing_L2   (includes L1)
ABP_BirdFlight    (flap cycle × awr_fold × alula)
```

## Validation checklist

- [ ] `awr_fold=0` silhouette matches tucked reference
- [ ] `awr_fold=1` planform continuous (no cascading delays)
- [ ] L/R mirror signs correct in local space
- [ ] Alula independent of fold
- [ ] Trajectory change alters wrist vs elbow without breaking fold endpoints
- [ ] Control Rig runs under AnimBP at target frame rate

## Porting tips from Blender

- Blender XYZ Euler drivers ≠ UE Quat/Rotator — rebuild with UE lerp, don’t paste expressions blindly.
- Blender `side_sign` for L/R often maps to negating one local axis in UE.
- After changing bind pose, re-capture Folded/Open reference poses with **Zero Key** / bake helpers.

## Roadmap beyond v0.1 docs

- Modular Control Rig modules per wing
- Physics-lite feather jiggle as post-process
- Networked fold replication (quantize 0–1 to byte)


---

**Preferred path:** use the sibling plugin repo [hallower1980/avian-wing-rig-unreal](https://github.com/hallower1980/avian-wing-rig-unreal) for the UE5 plugin, walkthrough, and math library. This document remains a Control Rig wiring reference.
