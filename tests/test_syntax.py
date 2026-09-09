#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""
Pure-Python checks that do not require Blender.
- py_compile all addon modules
- Verify bl_info and expected symbols via AST
- Verify package layout
"""

from __future__ import annotations

import ast
import py_compile
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ADDON = ROOT / "avian_wing_rig"
MODULES = [
    "__init__.py",
    "constants.py",
    "properties.py",
    "drivers.py",
    "rig_builder.py",
    "operators.py",
    "ui.py",
]


def fail(msg: str) -> None:
    print(f"FAIL: {msg}")
    sys.exit(1)


def main() -> None:
    if not ADDON.is_dir():
        fail(f"Addon package missing: {ADDON}")

    # 1) Syntax compile
    for name in MODULES:
        path = ADDON / name
        if not path.is_file():
            fail(f"Missing module: {path}")
        try:
            py_compile.compile(str(path), doraise=True)
        except py_compile.PyCompileError as exc:
            fail(f"Syntax error in {name}: {exc}")
        print(f"OK compile: {name}")

    # Also compile this test and smoke script
    for extra in (
        ROOT / "tests" / "test_syntax.py",
        ROOT / "tests" / "test_smoke_blender.py",
    ):
        if extra.is_file():
            py_compile.compile(str(extra), doraise=True)
            print(f"OK compile: {extra.relative_to(ROOT)}")

    # 2) bl_info present
    init_src = (ADDON / "__init__.py").read_text(encoding="utf-8")
    tree = ast.parse(init_src)
    bl_info = None
    for node in tree.body:
        if isinstance(node, ast.Assign):
            for t in node.targets:
                if isinstance(t, ast.Name) and t.id == "bl_info":
                    bl_info = ast.literal_eval(node.value)
    if not isinstance(bl_info, dict):
        fail("bl_info not found or not a literal dict")
    if bl_info.get("blender", (0,))[0] < 4:
        fail(f"bl_info blender version should be 4.x, got {bl_info.get('blender')}")
    if "name" not in bl_info or "version" not in bl_info:
        fail("bl_info missing name/version")
    print(f"OK bl_info: {bl_info['name']} {bl_info['version']} blender>={bl_info['blender']}")

    # 3) register / unregister
    for fn in ("register", "unregister"):
        if f"def {fn}(" not in init_src:
            fail(f"__init__.py missing {fn}()")
    print("OK register/unregister present")

    # 4) Operator bl_idnames expected
    ops_src = (ADDON / "operators.py").read_text(encoding="utf-8")
    expected_ops = [
        "awr.add_wing_rig",
        "awr.set_fold",
        "awr.set_alula",
        "awr.toggle_alula",
        "awr.apply_trajectory",
        "awr.bake_for_export",
    ]
    for op in expected_ops:
        if op not in ops_src:
            fail(f"Operator id missing: {op}")
    print(f"OK operators: {len(expected_ops)} ids")

    # 5) Constants naming
    const_src = (ADDON / "constants.py").read_text(encoding="utf-8")
    for token in (
        "MASTER_BONE",
        "awr_fold",
        "awr_alula",
        "awr_tier",
        "awr_trajectory",
        "PRIMARY_COUNT",
    ):
        if token not in const_src:
            fail(f"constants.py missing token: {token}")
    print("OK naming constants")

    # 6) Required docs exist
    for rel in (
        "README.md",
        "LICENSE",
        "AGENTS.md",
        "RESEARCH_BRIEF.md",
        "docs/MECHANICS.md",
        "docs/COMPARISON.md",
        "docs/UNREAL_CONTROL_RIG.md",
        "tests/MANUAL_CHECKLIST.md",
    ):
        if not (ROOT / rel).is_file():
            fail(f"Missing deliverable: {rel}")
    print("OK docs present")

    # 7) Soft check: modules must not import bpy at module level in constants
    # (constants should be pure)
    const_tree = ast.parse(const_src)
    for node in ast.walk(const_tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                if alias.name == "bpy" or alias.name.startswith("bpy."):
                    fail("constants.py should not import bpy")
        if isinstance(node, ast.ImportFrom) and node.module and node.module.startswith("bpy"):
            fail("constants.py should not import from bpy")
    print("OK constants is bpy-free")

    print("\nAll syntax/structure checks passed.")


if __name__ == "__main__":
    main()
