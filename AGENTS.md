# AGENTS.md — Conventions for future coding agents

This file tells automated coding agents how to work in **AvianWingRig** without breaking the project contract.

## Scope

- All project work lives under this repository root.
- Do **not** clone external repos or vendor proprietary Auto-Rig Pro / marketplace code.
- Prefer drivers and constraints artists can inspect in Blender’s UI over opaque Python per-frame handlers.

## Addon layout

```
avian_wing_rig/
  __init__.py      # bl_info, register/unregister
  constants.py     # bone names, tier enums, angles
  properties.py    # Scene awr_settings
  drivers.py       # fold / fan / ligament / alula / trajectory drivers
  rig_builder.py   # procedural Edit-mode armature
  operators.py     # bpy.types.Operator classes
  ui.py            # View3D > Sidebar > AvianWing panel
```

Install path expectation: zip the `avian_wing_rig/` package folder (the one containing `__init__.py` with `bl_info`), or symlink it into Blender’s `scripts/addons/`.

## Naming (do not rename casually)

| Role | Pattern |
|------|---------|
| Master control | `AWR_Master` |
| Skeleton | `AWR_L/R_Shoulder`, `_Elbow`, `_Wrist` |
| Fold helper | `AWR_L/R_Fold` |
| Primaries / secondaries / tertials | `AWR_L/R_P##`, `_S##`, `_T##` |
| Alula | `AWR_L/R_Alula` |
| Custom props on master | `awr_fold`, `awr_alula`, `awr_tier`, `awr_trajectory`, `awr_elastic`, `awr_ligament_strength`, `awr_fan_influence` |

## Tier contract

- **L0** — reciprocal 3-joint chain + `awr_fold` drivers; mirrored L/R; bake helper. No remiges required.
- **L1** — L0 + remige banks with fold-driven fan drivers and tunable `awr_fan_influence`.
- **L2** — L1 + alula control, ligament neighbor coupling, trajectory presets, elastic return bias.

Implement and keep **L0 solid first**; extend upward. Never break L0 when adding L2 features.

## Blender API notes

- Target **Blender 4.x** (`bl_info["blender"] = (4, 0, 0)`).
- Use bone collections (4.x), not legacy bone layers.
- Drivers: `SINGLE_PROP` on master custom properties; scripted expressions artists can read.
- Avoid `bpy.app.handlers.frame_change_*` unless documented as optional.

## Docs to keep in sync

When changing mechanics or operators, update:

1. `README.md` (install / try path)
2. `docs/MECHANICS.md` (biomechanics ↔ features)
3. `docs/UNREAL_CONTROL_RIG.md` if Control Rig mapping changes
4. `RESEARCH_BRIEF.md` if research assumptions change

## Tests

- Always run `python3 -m py_compile` on all `avian_wing_rig/*.py` and `tests/*.py` when Blender is unavailable.
- If `blender` is on `PATH`, run `tests/test_smoke_blender.py` via `blender --background --python …`.
- Do not require network or binary assets for smoke tests.

## License / attribution

- Code and docs: MIT (`LICENSE`); maintained by [hallower1980](https://github.com/hallower1980) / AvianWingRig contributors.
- Credit Laura Mathews’ public demonstration of avian wing mechanics and cited biomechanics papers in docs; do not claim endorsement.
