# SPDX-License-Identifier: MIT
"""
AvianWingRig — Blender 4.x addon
Laura Mathews–style avian wing mimicry → animation rigs (L0 / L1 / L2).
"""

bl_info = {
    "name": "Avian Wing Rig",
    "author": "AvianWingRig contributors",
    "version": (0, 1, 0),
    "blender": (4, 0, 0),
    "location": "View3D > Sidebar > AvianWing",
    "description": (
        "Procedural avian wing rigs at three tiers: game-light fold/flap (L0), "
        "production remige banks (L1), and bio/Mathews ligament+alula+trajectories (L2). "
        "Companion Unreal Control Rig docs included in the project."
    ),
    "warning": "",
    "doc_url": "",
    "category": "Rigging",
}

# Reload-friendly imports (Blender F8 / disable-enable)
if "bpy" in locals():
    import importlib

    from . import constants as _constants
    from . import properties as _properties
    from . import drivers as _drivers
    from . import rig_builder as _rig_builder
    from . import operators as _operators
    from . import ui as _ui

    importlib.reload(_constants)
    importlib.reload(_properties)
    importlib.reload(_drivers)
    importlib.reload(_rig_builder)
    importlib.reload(_operators)
    importlib.reload(_ui)

from . import properties
from . import operators
from . import ui


def register():
    properties.register()
    operators.register()
    ui.register()
    print("AvianWingRig v0.1.0 registered")


def unregister():
    ui.unregister()
    operators.unregister()
    properties.unregister()
    print("AvianWingRig unregistered")


if __name__ == "__main__":
    register()
