# SPDX-License-Identifier: MIT
"""Shared naming and tier constants for AvianWingRig."""

from __future__ import annotations

ADDON_ID = "avian_wing_rig"
ADDON_PREFIX = "AWR"

# Bone names (side is L or R)
def bone_shoulder(side: str) -> str:
    return f"{ADDON_PREFIX}_{side}_Shoulder"


def bone_elbow(side: str) -> str:
    return f"{ADDON_PREFIX}_{side}_Elbow"


def bone_wrist(side: str) -> str:
    return f"{ADDON_PREFIX}_{side}_Wrist"


def bone_fold(side: str) -> str:
    return f"{ADDON_PREFIX}_{side}_Fold"


def bone_alula(side: str) -> str:
    return f"{ADDON_PREFIX}_{side}_Alula"


def bone_primary(side: str, index: int) -> str:
    return f"{ADDON_PREFIX}_{side}_P{index:02d}"


def bone_secondary(side: str, index: int) -> str:
    return f"{ADDON_PREFIX}_{side}_S{index:02d}"


def bone_tertial(side: str, index: int) -> str:
    return f"{ADDON_PREFIX}_{side}_T{index:02d}"


MASTER_BONE = f"{ADDON_PREFIX}_Master"
ARMATURE_NAME = f"{ADDON_PREFIX}_WingArmature"
COLLECTION_NAME = f"{ADDON_PREFIX}_Wings"

# Custom property keys on master bone
PROP_FOLD = "awr_fold"
PROP_ALULA = "awr_alula"
PROP_TIER = "awr_tier"
PROP_TRAJECTORY = "awr_trajectory"
PROP_ELASTIC = "awr_elastic"
PROP_LIGAMENT = "awr_ligament_strength"
PROP_FAN_INFLUENCE = "awr_fan_influence"

# Remige counts (magpie-inspired, modest for demo)
PRIMARY_COUNT = 10
SECONDARY_COUNT = 8
TERTIAL_COUNT = 4

# Tier labels
TIER_L0 = "L0"
TIER_L1 = "L1"
TIER_L2 = "L2"
TIERS = (TIER_L0, TIER_L1, TIER_L2)

# Trajectory presets (L2)
TRAJ_NONE = "NONE"
TRAJ_LINKAGE = "LINKAGE"
TRAJ_CONSTANT_LIFT = "CONSTANT_LIFT"
TRAJ_CONSTANT_STABILITY = "CONSTANT_STABILITY"
TRAJECTORIES = (
    TRAJ_NONE,
    TRAJ_LINKAGE,
    TRAJ_CONSTANT_LIFT,
    TRAJ_CONSTANT_STABILITY,
)

# Approximate bone lengths (Blender units) for procedural demo
LEN_SHOULDER = 0.35
LEN_ELBOW = 0.40
LEN_WRIST = 0.28
LEN_REMIGE = 0.45
LEN_ALULA = 0.12

# Fold angles (radians) when fold=1 (fully open) vs fold=0 (folded)
# Folded: wing tucked; open: extended planform
FOLD_SHOULDER_OPEN = 0.15   # slight raise
FOLD_ELBOW_OPEN = -0.10
FOLD_WRIST_OPEN = 0.05
FOLD_SHOULDER_CLOSED = 1.20  # tucked aft
FOLD_ELBOW_CLOSED = 2.10     # strongly flexed
FOLD_WRIST_CLOSED = 1.40

# Remige fan: max local Z rotation spread when open
FAN_PRIMARY_MAX = 0.95
FAN_SECONDARY_MAX = 0.70
FAN_TERTIAL_MAX = 0.45
