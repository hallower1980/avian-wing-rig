# SPDX-License-Identifier: MIT
"""View3D Sidebar UI panel for AvianWingRig."""

from __future__ import annotations

import bpy

from . import constants as C
from . import rig_builder


class AWR_PT_main_panel(bpy.types.Panel):
    """Main AvianWingRig panel in the 3D Viewport sidebar."""

    bl_label = "Avian Wing Rig"
    bl_idname = "AWR_PT_main_panel"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "AvianWing"

    def draw(self, context):
        layout = self.layout
        settings = context.scene.awr_settings

        # --- Build ---
        box = layout.box()
        box.label(text="Build", icon="ARMATURE_DATA")
        box.prop(settings, "tier")
        box.prop(settings, "mirror")
        if settings.tier in (C.TIER_L1, C.TIER_L2):
            box.prop(settings, "fan_influence")
        if settings.tier == C.TIER_L2:
            box.prop(settings, "ligament_strength")
            box.prop(settings, "elastic")
        box.operator("awr.add_wing_rig", icon="ADD")

        arm = rig_builder.find_awr_armature(context)
        if arm is None:
            layout.label(text="No AWR rig in scene", icon="INFO")
            return

        master = arm.pose.bones.get(C.MASTER_BONE)
        tier = master.get(C.PROP_TIER, "?") if master else "?"

        # --- Fold ---
        box = layout.box()
        box.label(text=f"Controls ({arm.name} · {tier})", icon="DRIVER")
        box.prop(settings, "fold", slider=True)
        row = box.row(align=True)
        row.operator("awr.set_fold", icon="CHECKMARK")
        row.operator("awr.sync_fold_from_master", text="", icon="FILE_REFRESH")

        if master:
            cur = float(master.get(C.PROP_FOLD, 0.0))
            box.label(text=f"Master awr_fold = {cur:.3f}")

        # --- L2 Alula ---
        if tier == C.TIER_L2 or settings.tier == C.TIER_L2:
            box = layout.box()
            box.label(text="Alula (L2)", icon="BONE_DATA")
            box.prop(settings, "alula", slider=True)
            row = box.row(align=True)
            row.operator("awr.set_alula")
            row.operator("awr.toggle_alula", icon="UV_SYNC_SELECT")

        # --- L2 Trajectory ---
        if tier == C.TIER_L2 or settings.tier == C.TIER_L2:
            box = layout.box()
            box.label(text="Trajectory Preset (L2)", icon="IPO_EASE_IN_OUT")
            box.prop(settings, "trajectory")
            box.operator("awr.apply_trajectory", icon="CONSTRAINT")

        # --- Export ---
        box = layout.box()
        box.label(text="Export", icon="EXPORT")
        box.operator("awr.bake_for_export", icon="ACTION")
        box.label(text="Bake visual keys, then FBX/glTF")


CLASSES = (AWR_PT_main_panel,)


def register():
    for cls in CLASSES:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(CLASSES):
        bpy.utils.unregister_class(cls)
