# Comparison: AvianWingRig vs common alternatives

## Summary

| Approach | Fold underactuation | Remige ligaments | Alula | Trajectory library | Open / inspectable | Bake for games |
|----------|--------------------|------------------|-------|--------------------|--------------------|----------------|
| **AvianWingRig L0** | Yes (1 float) | — | — | — | MIT, drivers | Yes |
| **AvianWingRig L1** | Yes | Soft (fan + influence) | — | — | MIT | Yes |
| **AvianWingRig L2** | Yes + elastic | Neighbor coupling | Yes | Linkage / lift / stability | MIT | Yes |
| Auto-Rig Pro wings | Action / fold tools | Feather bones, Copy Rot | Manual | Manual | Proprietary | Yes (bake) |
| Hand-keyed FK | Animator-dependent | Animator-dependent | Manual | Manual | N/A | Yes |
| UE marketplace bird packs | Often AnimBP flaps | Varies (usually cards) | Rare | Rare | Marketplace license | Native UE |

## Auto-Rig Pro (ARP)

**Strengths:** Mature production pipeline, feather bone helpers, Action constraints for fold poses, Copy Rotation influence tuning, excellent bake-before-export workflow, broad limb library beyond wings.

**Gaps vs AWR goals:** Proprietary; not an open teaching implementation of Mathews-style ligament underactuation + alula + published elbow–wrist trajectory presets. ARP is a general character tool; AWR is a focused, documented biomechanics→rig translation.

**Interop:** Artists can use ARP for the body and AWR (or AWR ideas) for wing modules. Never copy ARP code into this repo.

## Hand FK / custom studio rigs

**Strengths:** Full artistic control; can match any reference.

**Gaps:** Expensive to maintain reciprocal coupling and simultaneous remige open by hand. Easy to slip into sequential “cascade” fans. Hard to share a standard fold float with Unreal.

**When to prefer:** Hero close-ups that break biology on purpose; then bake overrides on top of AWR.

## Unreal Control Rig + marketplace bird packs

**Strengths:** Real-time, AnimBP locomotion, Modular Control Rig, spring interpolation for secondary motion, shipping-ready flight cycles in many packs.

**Gaps:** Most packs prioritize flap cycles and mesh cards over explicit ligament graphs or alula controls. Few expose a researched trajectory preset library. Marketplace licenses vary; not always suitable as an open reference implementation.

**AWR role:** Blender side generates / prototypes the mechanical model; `docs/UNREAL_CONTROL_RIG.md` rebuilds the same fold→joint→remige→alula logic in UE5 so both DCCs share vocabulary (`awr_fold`, bank names, tiers).

## What AWR deliberately is not

- Not a full character auto-rigger
- Not a feather groom / card generator
- Not a physics CFD solver
- Not a wearable hardware CAD package

It is a **tiered, open, bake-friendly encoding** of specific avian mechanical principles for animation.

## Choosing a tier

- **Ship a mobile/game bird quickly** → L0
- **Cinematic bird with readable remiges** → L1
- **Bio-faithful / educational / Mathews-like demo** → L2, then bake or port to Control Rig
