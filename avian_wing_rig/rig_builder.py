# SPDX-License-Identifier: MIT
"""Procedural demo wing armature builder for tiers L0–L2."""

from __future__ import annotations

from typing import List, Sequence, Tuple

import bpy
from mathutils import Vector

from . import constants as C
from . import drivers as drv


def _get_or_create_collection(name: str) -> bpy.types.Collection:
    col = bpy.data.collections.get(name)
    if col is None:
        col = bpy.data.collections.new(name)
        bpy.context.scene.collection.children.link(col)
    return col


def _ensure_armature(name: str = C.ARMATURE_NAME) -> bpy.types.Object:
    existing = bpy.data.objects.get(name)
    if existing and existing.type == "ARMATURE":
        # Remove old armature data for a clean rebuild
        arm_data = existing.data
        bpy.data.objects.remove(existing, do_unlink=True)
        if arm_data and arm_data.users == 0:
            bpy.data.armatures.remove(arm_data)

    arm_data = bpy.data.armatures.new(name)
    arm_obj = bpy.data.objects.new(name, arm_data)
    col = _get_or_create_collection(C.COLLECTION_NAME)
    col.objects.link(arm_obj)
    return arm_obj


def _edit_bone(
    arm_data: bpy.types.Armature,
    name: str,
    head: Vector,
    tail: Vector,
    parent: str | None = None,
    connect: bool = False,
) -> bpy.types.EditBone:
    eb = arm_data.edit_bones.new(name)
    eb.head = head
    eb.tail = tail
    if parent:
        parent_bone = arm_data.edit_bones.get(parent)
        if parent_bone:
            eb.parent = parent_bone
            eb.use_connect = connect
    return eb


def _side_sign(side: str) -> float:
    return 1.0 if side == "L" else -1.0


def _build_skeletal_chain(arm_data: bpy.types.Armature, side: str, root_parent: str) -> None:
    """Shoulder → Elbow → Wrist chain."""
    s = _side_sign(side)
    # Origin slightly offset from master; wing extends along +X for L, -X for R
    shoulder_head = Vector((0.05 * s, 0.0, 0.15))
    shoulder_tail = shoulder_head + Vector((C.LEN_SHOULDER * s, 0.0, 0.02))
    elbow_tail = shoulder_tail + Vector((C.LEN_ELBOW * s, -0.05, 0.0))
    wrist_tail = elbow_tail + Vector((C.LEN_WRIST * s, 0.02, 0.0))

    _edit_bone(arm_data, C.bone_shoulder(side), shoulder_head, shoulder_tail, root_parent, False)
    _edit_bone(arm_data, C.bone_elbow(side), shoulder_tail, elbow_tail, C.bone_shoulder(side), True)
    _edit_bone(arm_data, C.bone_wrist(side), elbow_tail, wrist_tail, C.bone_elbow(side), True)

    # Fold control — non-deform helper near shoulder
    fold_head = shoulder_head + Vector((0.0, -0.08, 0.08))
    fold_tail = fold_head + Vector((0.0, 0.0, 0.1))
    fb = _edit_bone(arm_data, C.bone_fold(side), fold_head, fold_tail, root_parent, False)
    fb.use_deform = False


def _build_remige_bank(
    arm_data: bpy.types.Armature,
    side: str,
    parent: str,
    prefix_fn,
    count: int,
    origin: Vector,
    direction: Vector,
    spread_axis: Vector,
) -> List[str]:
    """Create a fan of remige bones parented to wrist/elbow region."""
    names: List[str] = []
    s = _side_sign(side)
    for i in range(count):
        name = prefix_fn(side, i)
        t = 0.0 if count <= 1 else i / (count - 1)
        offset = spread_axis * ((t - 0.5) * 0.12)
        head = origin + offset
        tail = head + direction.normalized() * C.LEN_REMIGE + Vector((0.0, 0.0, -0.02 * t))
        # Slight length variation
        tail = head + (tail - head) * (0.85 + 0.25 * (1.0 - abs(t - 0.5) * 2.0))
        eb = _edit_bone(arm_data, name, head, tail, parent, False)
        eb.use_deform = True
        names.append(name)
    return names


def _build_alula(arm_data: bpy.types.Armature, side: str) -> None:
    wrist = arm_data.edit_bones.get(C.bone_wrist(side))
    if wrist is None:
        return
    s = _side_sign(side)
    head = wrist.head + Vector((0.02 * s, 0.04, 0.02))
    tail = head + Vector((C.LEN_ALULA * s * 0.3, C.LEN_ALULA, 0.0))
    eb = _edit_bone(arm_data, C.bone_alula(side), head, tail, C.bone_wrist(side), False)
    eb.use_deform = True


def build_wing_rig(
    tier: str = C.TIER_L0,
    mirror: bool = True,
    fan_influence: float = 1.0,
    ligament_strength: float = 0.65,
    elastic: float = 0.15,
) -> bpy.types.Object:
    """
    Create a complete demo wing armature for the requested tier.
    Returns the armature object.
    """
    # Ensure Object mode before swapping armatures
    if bpy.context.mode != "OBJECT":
        bpy.ops.object.mode_set(mode="OBJECT")

    arm_obj = _ensure_armature()
    bpy.context.view_layer.objects.active = arm_obj
    arm_obj.select_set(True)

    bpy.ops.object.mode_set(mode="EDIT")
    arm_data = arm_obj.data

    # Master control bone at origin
    master = _edit_bone(
        arm_data,
        C.MASTER_BONE,
        Vector((0.0, 0.0, 0.0)),
        Vector((0.0, 0.0, 0.2)),
        None,
        False,
    )
    master.use_deform = False

    sides = ("L", "R") if mirror else ("L",)
    remige_map: dict = {}  # side -> {primaries, secondaries, tertials}

    for side in sides:
        _build_skeletal_chain(arm_data, side, C.MASTER_BONE)

        if tier in (C.TIER_L1, C.TIER_L2):
            wrist = arm_data.edit_bones[C.bone_wrist(side)]
            elbow = arm_data.edit_bones[C.bone_elbow(side)]
            s = _side_sign(side)
            # Primaries from wrist, pointing distal
            prim_dir = Vector((1.0 * s, 0.15, -0.05))
            prim_spread = Vector((0.0, 1.0, 0.0))
            primaries = _build_remige_bank(
                arm_data, side, C.bone_wrist(side), C.bone_primary,
                C.PRIMARY_COUNT, wrist.head + Vector((0.05 * s, 0.0, 0.0)),
                prim_dir, prim_spread,
            )
            # Secondaries along forearm
            mid = (elbow.head + wrist.head) * 0.5
            sec_dir = Vector((0.3 * s, 0.6, -0.05))
            secondaries = _build_remige_bank(
                arm_data, side, C.bone_elbow(side), C.bone_secondary,
                C.SECONDARY_COUNT, mid, sec_dir, Vector((0.0, 0.0, 1.0)),
            )
            # Tertials near shoulder/elbow
            tert_origin = elbow.head + Vector((-0.05 * s, 0.0, 0.0))
            tert_dir = Vector((-0.1 * s, 0.5, -0.02))
            tertials = _build_remige_bank(
                arm_data, side, C.bone_elbow(side), C.bone_tertial,
                C.TERTIAL_COUNT, tert_origin, tert_dir, Vector((0.0, 0.0, 0.5)),
            )
            remige_map[side] = {
                "primaries": primaries,
                "secondaries": secondaries,
                "tertials": tertials,
            }

        if tier == C.TIER_L2:
            _build_alula(arm_data, side)

    bpy.ops.object.mode_set(mode="POSE")

    # Master properties
    master_pb = arm_obj.pose.bones[C.MASTER_BONE]
    drv.setup_master_properties(master_pb, tier)
    master_pb[C.PROP_FAN_INFLUENCE] = fan_influence
    master_pb[C.PROP_LIGAMENT] = ligament_strength
    master_pb[C.PROP_ELASTIC] = elastic

    # Layer / bone groups for clarity (Blender 4.x uses collections on armature)
    _organize_bone_collections(arm_obj, tier, sides)

    use_elastic = tier == C.TIER_L2

    for side in sides:
        # L0+: drive skeletal chain from fold
        drv.add_fold_driver_euler(
            arm_obj, C.bone_shoulder(side), 2,  # Z
            C.FOLD_SHOULDER_CLOSED * _side_sign(side),
            C.FOLD_SHOULDER_OPEN * _side_sign(side),
            elastic=use_elastic,
        )
        drv.add_fold_driver_euler(
            arm_obj, C.bone_elbow(side), 1,  # Y flexion
            C.FOLD_ELBOW_CLOSED,
            C.FOLD_ELBOW_OPEN,
            elastic=use_elastic,
        )
        drv.add_fold_driver_euler(
            arm_obj, C.bone_wrist(side), 1,
            C.FOLD_WRIST_CLOSED,
            C.FOLD_WRIST_OPEN,
            elastic=use_elastic,
        )

        # Fold control bone mirrors the float for animator visibility
        fold_pb = arm_obj.pose.bones.get(C.bone_fold(side))
        if fold_pb:
            fold_pb.rotation_mode = "XYZ"
            # Copy fold prop to Z rotation for a visible gizmo feel
            data_path = f'pose.bones["{C.bone_fold(side)}"].rotation_euler'
            try:
                arm_obj.driver_remove(data_path, 2)
            except Exception:
                pass
            fc = arm_obj.driver_add(data_path, 2)
            fc.driver.type = "SCRIPTED"
            v = fc.driver.variables.new()
            v.name = "fold"
            v.type = "SINGLE_PROP"
            v.targets[0].id = arm_obj
            v.targets[0].data_path = f'pose.bones["{C.MASTER_BONE}"]["{C.PROP_FOLD}"]'
            fc.driver.expression = "fold * 1.5708"

        if tier in (C.TIER_L1, C.TIER_L2) and side in remige_map:
            banks = remige_map[side]
            _drive_remige_bank(arm_obj, banks["primaries"], C.FAN_PRIMARY_MAX, tier)
            _drive_remige_bank(arm_obj, banks["secondaries"], C.FAN_SECONDARY_MAX, tier)
            _drive_remige_bank(arm_obj, banks["tertials"], C.FAN_TERTIAL_MAX, tier)

        if tier == C.TIER_L2:
            drv.add_alula_driver(arm_obj, C.bone_alula(side))

    # Default display
    arm_obj.data.display_type = "OCTAHEDRAL"
    arm_obj.show_in_front = True

    bpy.ops.object.mode_set(mode="OBJECT")
    return arm_obj


def _drive_remige_bank(
    arm_obj: bpy.types.Object,
    names: Sequence[str],
    max_spread: float,
    tier: str,
) -> None:
    count = len(names)
    for i, name in enumerate(names):
        drv.add_remige_fan_driver(arm_obj, name, i, count, max_spread)
        if tier == C.TIER_L2 and count > 1:
            # Couple to neighbor for ligament-like simultaneous open
            neighbor = names[i + 1] if i < count - 1 else names[i - 1]
            drv.add_ligament_neighbor_driver(arm_obj, name, neighbor)


def _organize_bone_collections(
    arm_obj: bpy.types.Object,
    tier: str,
    sides: Tuple[str, ...],
) -> None:
    """Blender 4.x bone collections for sidebar organization."""
    arm = arm_obj.data
    # Clear default collection assignment confusion by creating named ones
    coll_names = ["CTRL", "SKEL", "REMIGES", "ALULA"]
    existing = {c.name: c for c in arm.collections}
    for cn in coll_names:
        if cn not in existing:
            arm.collections.new(cn)

    def assign(bone_name: str, coll: str):
        bone = arm.bones.get(bone_name)
        if bone is None:
            return
        # Assign to collection
        for c in arm.collections:
            if bone_name in [b.name for b in c.bones]:
                try:
                    c.unassign(bone)
                except Exception:
                    pass
        try:
            arm.collections[coll].assign(bone)
        except Exception:
            pass

    assign(C.MASTER_BONE, "CTRL")
    for side in sides:
        assign(C.bone_fold(side), "CTRL")
        assign(C.bone_shoulder(side), "SKEL")
        assign(C.bone_elbow(side), "SKEL")
        assign(C.bone_wrist(side), "SKEL")
        if tier in (C.TIER_L1, C.TIER_L2):
            for i in range(C.PRIMARY_COUNT):
                assign(C.bone_primary(side, i), "REMIGES")
            for i in range(C.SECONDARY_COUNT):
                assign(C.bone_secondary(side, i), "REMIGES")
            for i in range(C.TERTIAL_COUNT):
                assign(C.bone_tertial(side, i), "REMIGES")
        if tier == C.TIER_L2:
            assign(C.bone_alula(side), "ALULA")


def set_fold(arm_obj: bpy.types.Object, value: float) -> None:
    pb = arm_obj.pose.bones.get(C.MASTER_BONE)
    if pb is None:
        raise RuntimeError("Master bone not found — add a wing rig first")
    pb[C.PROP_FOLD] = max(0.0, min(1.0, float(value)))
    # Tag update
    arm_obj.update_tag()


def set_alula(arm_obj: bpy.types.Object, value: float) -> None:
    pb = arm_obj.pose.bones.get(C.MASTER_BONE)
    if pb is None:
        raise RuntimeError("Master bone not found — add a wing rig first")
    pb[C.PROP_ALULA] = max(0.0, min(1.0, float(value)))
    arm_obj.update_tag()


def apply_trajectory(arm_obj: bpy.types.Object, preset: str, mirror: bool = True) -> None:
    pb = arm_obj.pose.bones.get(C.MASTER_BONE)
    if pb is None:
        raise RuntimeError("Master bone not found — add a wing rig first")
    pb[C.PROP_TRAJECTORY] = preset
    # Prefer sides that actually exist on the armature
    candidates = ("L", "R") if mirror else ("L",)
    sides = tuple(s for s in candidates if arm_obj.pose.bones.get(C.bone_elbow(s)))
    for side in sides:
        drv.apply_trajectory_coupling(arm_obj, side, preset)
    arm_obj.update_tag()


def find_awr_armature(context=None) -> bpy.types.Object | None:
    ctx = context or bpy.context
    obj = ctx.active_object
    if obj and obj.type == "ARMATURE" and obj.pose.bones.get(C.MASTER_BONE):
        return obj
    # Fallback search
    for o in bpy.data.objects:
        if o.type == "ARMATURE" and o.name.startswith(C.ADDON_PREFIX):
            if o.pose.bones.get(C.MASTER_BONE):
                return o
    return None
