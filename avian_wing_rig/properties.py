# SPDX-License-Identifier: MIT
"""Scene / addon properties for AvianWingRig."""

from __future__ import annotations

import bpy
from bpy.props import (
    BoolProperty,
    EnumProperty,
    FloatProperty,
    PointerProperty,
)

from .constants import TIER_L0, TRAJ_LINKAGE


class AWR_SceneSettings(bpy.types.PropertyGroup):
    """Sidebar settings for operators."""

    tier: EnumProperty(
        name="Tier",
        description="Rig feature tier to generate",
        items=(
            (TIER_L0, "L0 Game-light", "Fold + shoulder flap, minimal bones"),
            ("L1", "L1 Production", "Remige banks with fold-driven fans"),
            ("L2", "L2 Bio/Mathews", "Ligament coupling, alula, trajectories"),
        ),
        default=TIER_L0,
    )

    fold: FloatProperty(
        name="Fold",
        description="0 = folded rest, 1 = fully open",
        default=0.0,
        min=0.0,
        max=1.0,
        subtype="FACTOR",
    )

    alula: FloatProperty(
        name="Alula",
        description="Independent alula (thumb) deployment (L2)",
        default=0.0,
        min=0.0,
        max=1.0,
        subtype="FACTOR",
    )

    alula_deployed: BoolProperty(
        name="Alula Deployed",
        description="Quick toggle: deploy or retract alula",
        default=False,
    )

    trajectory: EnumProperty(
        name="Trajectory",
        description="Elbow–wrist coupled morphing preset (L2)",
        items=(
            ("NONE", "None", "No extra elbow–wrist coupling"),
            (TRAJ_LINKAGE, "Linkage", "Anatomical linkage-style coupling"),
            ("CONSTANT_LIFT", "Constant Lift", "Preserve lift-oriented wrist path"),
            ("CONSTANT_STABILITY", "Constant Stability", "Stability-oriented morph path"),
        ),
        default="NONE",
    )

    mirror: BoolProperty(
        name="Mirror L/R",
        description="Build both left and right wings",
        default=True,
    )

    fan_influence: FloatProperty(
        name="Fan Influence",
        description="How strongly remiges respond to fold (L1+)",
        default=1.0,
        min=0.0,
        max=1.0,
        subtype="FACTOR",
    )

    ligament_strength: FloatProperty(
        name="Ligament Strength",
        description="Neighbor remige coupling strength (L2)",
        default=0.65,
        min=0.0,
        max=1.0,
        subtype="FACTOR",
    )

    elastic: FloatProperty(
        name="Elastic Return",
        description="Bias toward folded rest (L2 spring-like driver weight)",
        default=0.15,
        min=0.0,
        max=1.0,
        subtype="FACTOR",
    )


def register():
    bpy.utils.register_class(AWR_SceneSettings)
    bpy.types.Scene.awr_settings = PointerProperty(type=AWR_SceneSettings)


def unregister():
    del bpy.types.Scene.awr_settings
    bpy.utils.unregister_class(AWR_SceneSettings)
