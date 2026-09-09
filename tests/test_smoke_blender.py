# SPDX-License-Identifier: MIT
"""
Headless Blender smoke test.

Usage:
  blender --background --python tests/test_smoke_blender.py

Exits non-zero on failure. Safe to skip if Blender is not installed
(use test_syntax.py instead).
"""

from __future__ import annotations

import sys
from pathlib import Path

# Ensure project root is on path so `avian_wing_rig` imports
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

try:
    import bpy
except ImportError:
    print("SKIP: bpy not available (run inside Blender)")
    sys.exit(0)


def assert_true(cond: bool, msg: str) -> None:
    if not cond:
        print(f"FAIL: {msg}")
        sys.exit(1)


def main() -> None:
    # Fresh scene
    bpy.ops.wm.read_factory_settings(use_empty=True)

    from avian_wing_rig import register, unregister
    from avian_wing_rig import constants as C
    from avian_wing_rig import rig_builder

    register()

    # --- L0 ---
    arm = rig_builder.build_wing_rig(tier=C.TIER_L0, mirror=True)
    assert_true(arm is not None, "L0 armature is None")
    assert_true(C.MASTER_BONE in arm.pose.bones, "Master bone missing")
    assert_true(C.bone_shoulder("L") in arm.pose.bones, "L shoulder missing")
    assert_true(C.bone_elbow("R") in arm.pose.bones, "R elbow missing")
    rig_builder.set_fold(arm, 1.0)
    fold = float(arm.pose.bones[C.MASTER_BONE][C.PROP_FOLD])
    assert_true(abs(fold - 1.0) < 1e-6, f"Fold not 1.0: {fold}")
    print("OK L0 build + fold")

    # --- L1 ---
    arm = rig_builder.build_wing_rig(tier=C.TIER_L1, mirror=True)
    assert_true(C.bone_primary("L", 0) in arm.pose.bones, "L primary missing")
    assert_true(C.bone_secondary("L", 0) in arm.pose.bones, "L secondary missing")
    assert_true(C.bone_tertial("R", 0) in arm.pose.bones, "R tertial missing")
    print("OK L1 remige banks")

    # --- L2 ---
    arm = rig_builder.build_wing_rig(tier=C.TIER_L2, mirror=True)
    assert_true(C.bone_alula("L") in arm.pose.bones, "L alula missing")
    rig_builder.set_alula(arm, 1.0)
    assert_true(
        abs(float(arm.pose.bones[C.MASTER_BONE][C.PROP_ALULA]) - 1.0) < 1e-6,
        "Alula prop not set",
    )
    rig_builder.apply_trajectory(arm, C.TRAJ_LINKAGE)
    assert_true(
        arm.pose.bones[C.MASTER_BONE][C.PROP_TRAJECTORY] == C.TRAJ_LINKAGE,
        "Trajectory not stored",
    )
    print("OK L2 alula + trajectory")

    # Operators exist
    assert_true(hasattr(bpy.ops.awr, "add_wing_rig"), "ops.awr.add_wing_rig missing")
    assert_true(hasattr(bpy.ops.awr, "set_fold"), "ops.awr.set_fold missing")
    assert_true(hasattr(bpy.ops.awr, "bake_for_export"), "ops.awr.bake_for_export missing")

    unregister()
    print("\nBlender smoke test passed.")
    # Quit cleanly when run via --python
    try:
        bpy.ops.wm.quit_blender()
    except Exception:
        pass


if __name__ == "__main__":
    main()
