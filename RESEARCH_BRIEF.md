# Avian Wing Mimicry → Animation Rig Research Brief

Source video: Adam Savage Experiences Anatomically Correct Wings! (https://youtu.be/WT7MLrxor1A)
Maker: Laura Mathews (https://www.lauramathewsart.com/) — scaled Phoenix/magpie puppet mechanics to wearable full-size wings.

## Mechanical principles to encode

1. Reciprocal 3-joint skeletal chain (shoulder/elbow/wrist ≈ humerus/forearm/manus) with coupled extension (tendon–bone reciprocal motion), not three free hinges.
2. Inter-feather ligament graph: each remige linked to neighbors to preserve angle/spacing; prefer simultaneous fan open over sequential string cascade.
3. Sheet cohesion (barbule analogue): soft constraint keeping remiges as a continuous surface.
4. Independent alula control (thumb) for landing / slow-speed poses.
5. Human→bird ROM adapter: extra lever length + hinge so wearer/animator can reach aft sweep.
6. Elastic / gravity return toward folded rest with low actuation effort.
7. Species planform: remige count and outlines matter (magpie ~ discrete remiges; Adam notes ~22 feathers/wing on related builds excluding full coverts).

## Biomechanics literature (for trajectory presets)
- Gull elbow–wrist morphing trajectories (Harvey et al., J R Soc Interface 2021): linkage trajectory vs constant-lift / constant-stability paths.
- PigeonBot underactuated feathers via wrist+finger (Chang/Lentink, Sci Robotics 2020).
- Stowers et al.: 3D elbow–wrist coupling for wing morphing.

## Industry baseline
- Blender Auto-Rig Pro: wing limb option, feather bones, Action constraints for fold; Copy Rotation influence tuning; bake before game export.
- Unreal Control Rig: FK/IK, Modular CR, dynamic chains / spring interp for secondary; marketplace bird packs for AnimBP flight.
- Gap: no open, tiered implementation of ligament underactuation + alula + elbow–wrist trajectory library targeting both Blender and UE.

## Tier definitions
- L0 Game-light: fold float + flap, minimal bones, bake-ready.
- L1 Production: remige banks, fold action, weights, mirror, bake helpers.
- L2 Bio/Mathews: ligament graph, alula, trajectory presets, elastic return.

---

## Implementation status (v0.1)

Encoded in this repository’s Blender addon (`avian_wing_rig/`) and docs:

| # | Principle | v0.1 status |
|---|-----------|-------------|
| 1 | Reciprocal 3-joint + fold | **Done** — drivers on Shoulder/Elbow/Wrist from `awr_fold` |
| 2 | Ligament neighbor graph | **Done (L2)** — neighbor blend drivers + `awr_ligament_strength` |
| 3 | Sheet cohesion | **Approx** — coherent fan + ligament; mesh/groom out of scope |
| 4 | Independent alula | **Done (L2)** — `AWR_*_Alula` + `awr_alula` |
| 5 | Human→bird ROM adapter | **Documented** — exaggerated closed angles; dedicated adapter bone TBD |
| 6 | Elastic / gravity return | **Done (L2)** — `awr_elastic` biases effective fold; UE spring pattern in docs |
| 7 | Species planform | **Partial** — magpie-inspired counts in `constants.py`; outlines = mesh |

See `docs/MECHANICS.md` for the full mapping and `docs/UNREAL_CONTROL_RIG.md` for the UE5 rebuild path.

## Design choices worth revisiting

- Driver expressions vs Action constraints (ARP-style): drivers win for a single fold float; Actions may be better for multi-pose libraries.
- Ligament graph density: pair neighbors only in v0.1; full mesh graph could reduce edge flutter.
- Trajectory ratios (0.55 / 0.85 / 0.35) are teaching defaults, not fitted to a specific gull dataset — replace with measured curves for production bio work.
