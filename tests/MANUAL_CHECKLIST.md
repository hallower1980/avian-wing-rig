# Manual checklist (Blender UI)

Use when Blender is available interactively.

## Install

- [ ] Addon folder `avian_wing_rig/` is on the addons path
- [ ] Preferences → Add-ons → **Avian Wing Rig** enables without errors
- [ ] Sidebar shows **AvianWing** tab

## L0

- [ ] Tier L0 → Add Wing Rig creates `AWR_WingArmature`
- [ ] Bones: Master, L/R Shoulder, Elbow, Wrist, Fold
- [ ] Set Fold 0→1 moves chain toward open silhouette
- [ ] Mirror off builds left only

## L1

- [ ] Add Wing Rig L1 creates P/S/T remige banks
- [ ] Fold opens fans coherently (not staggered cascade)
- [ ] Fan Influence 0 freezes remiges; 1 full spread

## L2

- [ ] Alula bones present; Set/Toggle Alula rotates them independently of fold
- [ ] Ligament strength visibly softens neighbor differences
- [ ] Trajectory Linkage / Constant Lift / Constant Stability change wrist vs elbow relationship
- [ ] Elastic > 0 keeps wing more tucked for the same fold slider value

## Export

- [ ] Bake Constraints for Export writes visual keys on the frame range
- [ ] FBX/glTF export of baked action loads in a game engine or UE

## Regression

- [ ] Re-adding a rig replaces the previous AWR armature cleanly
- [ ] Disable/enable addon does not leave broken operators
