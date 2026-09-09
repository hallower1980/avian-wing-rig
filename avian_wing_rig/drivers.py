# SPDX-License-Identifier: MIT
"""Driver and constraint helpers artists can inspect in the Graph Editor."""

from __future__ import annotations

from typing import Iterable, Sequence

import bpy

from . import constants as C


def _ensure_custom_prop(bone, name: str, value, min_v=0.0, max_v=1.0, description: str = ""):
    """Create an ID property with UI metadata when possible."""
    bone[name] = value
    try:
        ui = bone.id_properties_ui(name)
        ui.update(min=min_v, max=max_v, description=description, default=value)
    except Exception:
        # Blender < 3.0 style or RNA limitations — property still works
        pass


def setup_master_properties(pose_bone, tier: str):
    """Custom properties on the master control bone."""
    _ensure_custom_prop(pose_bone, C.PROP_FOLD, 0.0, 0.0, 1.0, "Wing fold: 0 folded, 1 open")
    _ensure_custom_prop(pose_bone, C.PROP_ALULA, 0.0, 0.0, 1.0, "Alula deployment")
    pose_bone[C.PROP_TIER] = tier
    pose_bone[C.PROP_TRAJECTORY] = C.TRAJ_NONE
    _ensure_custom_prop(pose_bone, C.PROP_ELASTIC, 0.15, 0.0, 1.0, "Elastic return toward fold rest")
    _ensure_custom_prop(pose_bone, C.PROP_LIGAMENT, 0.65, 0.0, 1.0, "Ligament neighbor coupling")
    _ensure_custom_prop(pose_bone, C.PROP_FAN_INFLUENCE, 1.0, 0.0, 1.0, "Remige fan influence from fold")


def clear_drivers(pose_bone, data_paths: Iterable[str] | None = None):
    """Remove drivers on listed data paths (or all common rotation paths)."""
    if pose_bone.id_data.animation_data is None:
        return
    paths = data_paths or (
        'pose.bones["%s"].rotation_euler' % pose_bone.name,
        'pose.bones["%s"].rotation_euler[0]' % pose_bone.name,
        'pose.bones["%s"].rotation_euler[1]' % pose_bone.name,
        'pose.bones["%s"].rotation_euler[2]' % pose_bone.name,
    )
    ad = pose_bone.id_data.animation_data
    for path in paths:
        try:
            pose_bone.id_data.driver_remove(path)
        except Exception:
            pass
        # Also try indexed removal
        for i in range(3):
            try:
                pose_bone.id_data.driver_remove(path if "[" in path else f"{path}[{i}]", i if "[" not in path else -1)
            except Exception:
                pass


def add_fold_driver_euler(
    arm: bpy.types.Object,
    bone_name: str,
    axis: int,
    closed_angle: float,
    open_angle: float,
    master_name: str = C.MASTER_BONE,
    elastic: bool = False,
):
    """
    Drive one Euler axis from awr_fold on master.
    angle = lerp(closed, open, fold) with optional elastic bias toward closed.
    """
    pb = arm.pose.bones.get(bone_name)
    if pb is None:
        return
    pb.rotation_mode = "XYZ"
    data_path = f'pose.bones["{bone_name}"].rotation_euler'
    # Remove existing driver on this channel
    try:
        arm.driver_remove(data_path, axis)
    except Exception:
        pass

    fcurve = arm.driver_add(data_path, axis)
    drv = fcurve.driver
    drv.type = "SCRIPTED"

    var = drv.variables.new()
    var.name = "fold"
    var.type = "SINGLE_PROP"
    tgt = var.targets[0]
    tgt.id = arm
    tgt.data_path = f'pose.bones["{master_name}"]["{C.PROP_FOLD}"]'

    if elastic:
        var_e = drv.variables.new()
        var_e.name = "elastic"
        var_e.type = "SINGLE_PROP"
        tgt_e = var_e.targets[0]
        tgt_e.id = arm
        tgt_e.data_path = f'pose.bones["{master_name}"]["{C.PROP_ELASTIC}"]'
        # Bias fold toward 0 by elastic amount: effective = fold * (1 - elastic)
        drv.expression = (
            f"{closed_angle:.6f} + ({open_angle:.6f} - {closed_angle:.6f}) "
            f"* (fold * (1.0 - elastic))"
        )
    else:
        drv.expression = (
            f"{closed_angle:.6f} + ({open_angle:.6f} - {closed_angle:.6f}) * fold"
        )


def add_remige_fan_driver(
    arm: bpy.types.Object,
    bone_name: str,
    index: int,
    count: int,
    max_spread: float,
    master_name: str = C.MASTER_BONE,
    axis: int = 2,
):
    """
    Spread remiges along local Z as fold opens.
    Center feather stays near 0; outer feathers swing more.
    """
    pb = arm.pose.bones.get(bone_name)
    if pb is None:
        return
    pb.rotation_mode = "XYZ"
    # Normalized position in bank [-0.5, 0.5]
    if count <= 1:
        t = 0.0
    else:
        t = (index / (count - 1)) - 0.5
    target_open = t * 2.0 * max_spread  # full spread at fold=1

    data_path = f'pose.bones["{bone_name}"].rotation_euler'
    try:
        arm.driver_remove(data_path, axis)
    except Exception:
        pass

    fcurve = arm.driver_add(data_path, axis)
    drv = fcurve.driver
    drv.type = "SCRIPTED"

    var = drv.variables.new()
    var.name = "fold"
    var.type = "SINGLE_PROP"
    tgt = var.targets[0]
    tgt.id = arm
    tgt.data_path = f'pose.bones["{master_name}"]["{C.PROP_FOLD}"]'

    var_i = drv.variables.new()
    var_i.name = "inf"
    var_i.type = "SINGLE_PROP"
    tgt_i = var_i.targets[0]
    tgt_i.id = arm
    tgt_i.data_path = f'pose.bones["{master_name}"]["{C.PROP_FAN_INFLUENCE}"]'

    drv.expression = f"{target_open:.6f} * fold * inf"


def add_ligament_neighbor_driver(
    arm: bpy.types.Object,
    bone_name: str,
    neighbor_name: str,
    master_name: str = C.MASTER_BONE,
    axis: int = 2,
    blend: float = 0.35,
):
    """
    Soft neighbor coupling: this remige's rotation blends toward neighbor.
    Mimics inter-feather ligaments (simultaneous fan, not cascade).
    Applied as an additive offset on top of the fan driver by averaging.
    """
    pb = arm.pose.bones.get(bone_name)
    nb = arm.pose.bones.get(neighbor_name)
    if pb is None or nb is None:
        return
    pb.rotation_mode = "XYZ"

    data_path = f'pose.bones["{bone_name}"].rotation_euler'
    # Read existing expression if present and wrap it
    existing_expr = None
    if arm.animation_data and arm.animation_data.drivers:
        for fc in arm.animation_data.drivers:
            if fc.data_path == data_path and fc.array_index == axis:
                existing_expr = fc.driver.expression
                break

    try:
        arm.driver_remove(data_path, axis)
    except Exception:
        pass

    fcurve = arm.driver_add(data_path, axis)
    drv = fcurve.driver
    drv.type = "SCRIPTED"

    # Base fan vars
    var = drv.variables.new()
    var.name = "fold"
    var.type = "SINGLE_PROP"
    tgt = var.targets[0]
    tgt.id = arm
    tgt.data_path = f'pose.bones["{master_name}"]["{C.PROP_FOLD}"]'

    var_i = drv.variables.new()
    var_i.name = "inf"
    var_i.type = "SINGLE_PROP"
    tgt_i = var_i.targets[0]
    tgt_i.id = arm
    tgt_i.data_path = f'pose.bones["{master_name}"]["{C.PROP_FAN_INFLUENCE}"]'

    var_l = drv.variables.new()
    var_l.name = "lig"
    var_l.type = "SINGLE_PROP"
    tgt_l = var_l.targets[0]
    tgt_l.id = arm
    tgt_l.data_path = f'pose.bones["{master_name}"]["{C.PROP_LIGAMENT}"]'

    var_n = drv.variables.new()
    var_n.name = "nbr"
    var_n.type = "TRANSFORMS"
    tgt_n = var_n.targets[0]
    tgt_n.id = arm
    tgt_n.bone_target = neighbor_name
    tgt_n.transform_type = ("ROT_X", "ROT_Y", "ROT_Z")[axis]
    tgt_n.transform_space = "LOCAL_SPACE"
    tgt_n.rotation_mode = "AUTO"

    # Extract base open angle from existing expression if possible
    base = "0.0"
    if existing_expr and "*" in existing_expr:
        # existing like "0.123456 * fold * inf"
        base = existing_expr.split("*")[0].strip()
    else:
        base = "0.0"

    # final = base_fan * (1 - lig*blend) + nbr * (lig*blend)
    drv.expression = (
        f"({base} * fold * inf) * (1.0 - lig * {blend:.4f}) "
        f"+ nbr * (lig * {blend:.4f})"
    )


def add_alula_driver(
    arm: bpy.types.Object,
    bone_name: str,
    master_name: str = C.MASTER_BONE,
    open_angle: float = 0.85,
    axis: int = 2,
):
    """Drive alula bone from awr_alula property."""
    pb = arm.pose.bones.get(bone_name)
    if pb is None:
        return
    pb.rotation_mode = "XYZ"
    data_path = f'pose.bones["{bone_name}"].rotation_euler'
    try:
        arm.driver_remove(data_path, axis)
    except Exception:
        pass
    fcurve = arm.driver_add(data_path, axis)
    drv = fcurve.driver
    drv.type = "SCRIPTED"
    var = drv.variables.new()
    var.name = "alula"
    var.type = "SINGLE_PROP"
    tgt = var.targets[0]
    tgt.id = arm
    tgt.data_path = f'pose.bones["{master_name}"]["{C.PROP_ALULA}"]'
    drv.expression = f"{open_angle:.6f} * alula"


def apply_trajectory_coupling(
    arm: bpy.types.Object,
    side: str,
    preset: str,
    master_name: str = C.MASTER_BONE,
):
    """
    Couple elbow and wrist rotations based on trajectory preset.
    LINKAGE: wrist tracks ~0.55 * elbow flexion (anatomical reciprocal).
    CONSTANT_LIFT: wrist opens more aggressively as elbow extends.
    CONSTANT_STABILITY: wrist lags elbow (more stable morph).
    """
    elbow = C.bone_elbow(side)
    wrist = C.bone_wrist(side)
    ep = arm.pose.bones.get(elbow)
    wp = arm.pose.bones.get(wrist)
    if ep is None or wp is None:
        return

    ratios = {
        C.TRAJ_NONE: None,
        C.TRAJ_LINKAGE: 0.55,
        C.TRAJ_CONSTANT_LIFT: 0.85,
        C.TRAJ_CONSTANT_STABILITY: 0.35,
    }
    ratio = ratios.get(preset)
    if ratio is None:
        return

    # Drive wrist Y from elbow Y * ratio, blended with fold baseline
    wp.rotation_mode = "XYZ"
    data_path = f'pose.bones["{wrist}"].rotation_euler'
    axis = 1  # Y — flexion axis for our procedural layout
    try:
        arm.driver_remove(data_path, axis)
    except Exception:
        pass

    fcurve = arm.driver_add(data_path, axis)
    drv = fcurve.driver
    drv.type = "SCRIPTED"

    var_f = drv.variables.new()
    var_f.name = "fold"
    var_f.type = "SINGLE_PROP"
    tgt_f = var_f.targets[0]
    tgt_f.id = arm
    tgt_f.data_path = f'pose.bones["{master_name}"]["{C.PROP_FOLD}"]'

    var_e = drv.variables.new()
    var_e.name = "elb"
    var_e.type = "TRANSFORMS"
    tgt_e = var_e.targets[0]
    tgt_e.id = arm
    tgt_e.bone_target = elbow
    tgt_e.transform_type = "ROT_Y"
    tgt_e.transform_space = "LOCAL_SPACE"
    tgt_e.rotation_mode = "AUTO"

    closed = C.FOLD_WRIST_CLOSED
    opened = C.FOLD_WRIST_OPEN
    # Base fold lerp + extra coupling from elbow deviation
    drv.expression = (
        f"{closed:.6f} + ({opened:.6f} - {closed:.6f}) * fold "
        f"+ (elb - ({closed:.6f} + ({opened:.6f} - {closed:.6f}) * fold)) * {ratio:.4f}"
    )


def bake_pose_constraints(arm: bpy.types.Object, frame_start: int, frame_end: int):
    """
    Visual-key bake helper: insert visual loc/rot keys so constraints/drivers
    can be cleared for game export. Artists can also use Pose > Animation > Bake.
    """
    bpy.context.view_layer.objects.active = arm
    bpy.ops.object.mode_set(mode="POSE")
    bpy.ops.pose.select_all(action="SELECT")
    try:
        bpy.ops.nla.bake(
            frame_start=frame_start,
            frame_end=frame_end,
            only_selected=True,
            visual_keying=True,
            clear_constraints=False,
            clear_parents=False,
            use_current_action=True,
            bake_types={"POSE"},
        )
    except Exception:
        # Fallback: manual visual keyframe each frame
        for frame in range(frame_start, frame_end + 1):
            bpy.context.scene.frame_set(frame)
            bpy.ops.anim.keyframe_insert_menu(type="BUILTIN_KSI_VisualLocRot")
