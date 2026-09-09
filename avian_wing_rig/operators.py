# SPDX-License-Identifier: MIT
"""Blender operators for AvianWingRig."""

from __future__ import annotations

import bpy

from . import constants as C
from . import drivers as drv
from . import rig_builder


class AWR_OT_add_wing_rig(bpy.types.Operator):
    """Add a procedural avian wing armature at the selected tier."""

    bl_idname = "awr.add_wing_rig"
    bl_label = "Add Wing Rig"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        settings = context.scene.awr_settings
        try:
            arm = rig_builder.build_wing_rig(
                tier=settings.tier,
                mirror=settings.mirror,
                fan_influence=settings.fan_influence,
                ligament_strength=settings.ligament_strength,
                elastic=settings.elastic,
            )
        except Exception as exc:
            self.report({"ERROR"}, f"Failed to build wing rig: {exc}")
            return {"CANCELLED"}

        self.report(
            {"INFO"},
            f"Created {arm.name} tier {settings.tier} "
            f"({'L+R' if settings.mirror else 'L only'})",
        )
        return {"FINISHED"}


class AWR_OT_set_fold(bpy.types.Operator):
    """Set the master fold control (0 folded … 1 open)."""

    bl_idname = "awr.set_fold"
    bl_label = "Set Fold"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        arm = rig_builder.find_awr_armature(context)
        if arm is None:
            self.report({"ERROR"}, "No AWR armature found — Add Wing Rig first")
            return {"CANCELLED"}
        settings = context.scene.awr_settings
        try:
            rig_builder.set_fold(arm, settings.fold)
        except Exception as exc:
            self.report({"ERROR"}, str(exc))
            return {"CANCELLED"}
        # Force depsgraph update so drivers re-evaluate
        context.view_layer.update()
        self.report({"INFO"}, f"Fold set to {settings.fold:.3f}")
        return {"FINISHED"}


class AWR_OT_set_alula(bpy.types.Operator):
    """Set alula deployment (L2)."""

    bl_idname = "awr.set_alula"
    bl_label = "Set Alula"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        arm = rig_builder.find_awr_armature(context)
        if arm is None:
            self.report({"ERROR"}, "No AWR armature found")
            return {"CANCELLED"}
        master = arm.pose.bones.get(C.MASTER_BONE)
        if master is None or master.get(C.PROP_TIER) != C.TIER_L2:
            self.report({"WARNING"}, "Alula requires an L2 rig")
            # Still set the property if present
        settings = context.scene.awr_settings
        value = settings.alula
        try:
            rig_builder.set_alula(arm, value)
        except Exception as exc:
            self.report({"ERROR"}, str(exc))
            return {"CANCELLED"}
        context.view_layer.update()
        self.report({"INFO"}, f"Alula set to {value:.3f}")
        return {"FINISHED"}


class AWR_OT_toggle_alula(bpy.types.Operator):
    """Toggle alula between retracted (0) and deployed (1)."""

    bl_idname = "awr.toggle_alula"
    bl_label = "Toggle Alula"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        arm = rig_builder.find_awr_armature(context)
        if arm is None:
            self.report({"ERROR"}, "No AWR armature found")
            return {"CANCELLED"}
        master = arm.pose.bones.get(C.MASTER_BONE)
        if master is None:
            self.report({"ERROR"}, "Master bone missing")
            return {"CANCELLED"}
        current = float(master.get(C.PROP_ALULA, 0.0))
        new_val = 0.0 if current > 0.5 else 1.0
        rig_builder.set_alula(arm, new_val)
        context.scene.awr_settings.alula = new_val
        context.scene.awr_settings.alula_deployed = new_val > 0.5
        context.view_layer.update()
        self.report({"INFO"}, f"Alula {'deployed' if new_val > 0.5 else 'retracted'}")
        return {"FINISHED"}


class AWR_OT_apply_trajectory(bpy.types.Operator):
    """Apply an elbow–wrist trajectory preset (L2)."""

    bl_idname = "awr.apply_trajectory"
    bl_label = "Apply Trajectory Preset"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        arm = rig_builder.find_awr_armature(context)
        if arm is None:
            self.report({"ERROR"}, "No AWR armature found")
            return {"CANCELLED"}
        settings = context.scene.awr_settings
        preset = settings.trajectory
        try:
            rig_builder.apply_trajectory(arm, preset, mirror=settings.mirror)
        except Exception as exc:
            self.report({"ERROR"}, str(exc))
            return {"CANCELLED"}
        context.view_layer.update()
        self.report({"INFO"}, f"Trajectory preset: {preset}")
        return {"FINISHED"}


class AWR_OT_bake_for_export(bpy.types.Operator):
    """Bake visual pose (drivers/constraints) to keyframes for game export."""

    bl_idname = "awr.bake_for_export"
    bl_label = "Bake Constraints for Export"
    bl_options = {"REGISTER", "UNDO"}

    frame_start: bpy.props.IntProperty(name="Start", default=1)
    frame_end: bpy.props.IntProperty(name="End", default=60)

    def invoke(self, context, event):
        scene = context.scene
        self.frame_start = scene.frame_start
        self.frame_end = scene.frame_end
        return context.window_manager.invoke_props_dialog(self)

    def execute(self, context):
        arm = rig_builder.find_awr_armature(context)
        if arm is None:
            self.report({"ERROR"}, "No AWR armature found")
            return {"CANCELLED"}
        context.view_layer.objects.active = arm
        arm.select_set(True)
        try:
            drv.bake_pose_constraints(arm, self.frame_start, self.frame_end)
        except Exception as exc:
            self.report({"ERROR"}, f"Bake failed: {exc}")
            return {"CANCELLED"}
        self.report(
            {"INFO"},
            f"Baked visual pose frames {self.frame_start}–{self.frame_end}. "
            "Review Action, then optionally clear drivers before FBX export.",
        )
        return {"FINISHED"}


class AWR_OT_sync_fold_from_master(bpy.types.Operator):
    """Pull fold value from master bone into the sidebar slider."""

    bl_idname = "awr.sync_fold_from_master"
    bl_label = "Sync Fold from Rig"
    bl_options = {"REGISTER"}

    def execute(self, context):
        arm = rig_builder.find_awr_armature(context)
        if arm is None:
            self.report({"ERROR"}, "No AWR armature found")
            return {"CANCELLED"}
        master = arm.pose.bones[C.MASTER_BONE]
        context.scene.awr_settings.fold = float(master.get(C.PROP_FOLD, 0.0))
        context.scene.awr_settings.alula = float(master.get(C.PROP_ALULA, 0.0))
        return {"FINISHED"}


CLASSES = (
    AWR_OT_add_wing_rig,
    AWR_OT_set_fold,
    AWR_OT_set_alula,
    AWR_OT_toggle_alula,
    AWR_OT_apply_trajectory,
    AWR_OT_bake_for_export,
    AWR_OT_sync_fold_from_master,
)


def register():
    for cls in CLASSES:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(CLASSES):
        bpy.utils.unregister_class(cls)
