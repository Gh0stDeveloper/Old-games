# Diamond Rush Fan Levels — Engine integration progress

**Branch:** feat/diamond-rush-fan-levels-engine (GitHub user Gh0stDeveloper)
**Scope:** Research/temporary rebuilt DEX only. Do not deliver APK yet.

## What was actually changed in an ephemeral DEX

- The legacy menu item's visual text is changed from LEADERBOARD to LEVELS FAN in the original `x()V` method.
- The original main-menu selection 2 maps to value 4 in menu table `b[0]`. `N()V` case 4 now calls `FanMenuEntry.tryOpen()`. It falls back to the original leaderboard if no runtime adapter has been bound.
- The static resource-path registry `e` now allocates four slots, preserving w0,w1,w2 and appending `/w3.bin`.
- The `T(I)V` world-route switch now recognizes world index 3 and appends `/map_fan_levels.out` to the selector resource path.

## Stage resource

The CI generator recreates exactly the earlier `FAN-LC-01 / Lost City / Stage 1` world:
44 x 30 cells; 1 stage; eastern wing and secret chamber based on a preserved 27 x 26 Angkor Stage 3 core. The generator matches SHA-256 **7b0c23e49ea9bda541f283cf8955a8e4617a03dcd42910dde974a94769e5ea4b**. It neither changes nor commits classic world assets. The previous experimental QA remixes are not new extra worlds.

## What is NOT integrated (release blockers)

- The Android/libGDX runtime has not instantiated `FanRuntimeAdapter` and bound it to `FanMenuEntry`; therefore the menu item still falls back to old behavior in an APK.
- Region selection's SECOND `cL` switch and other world-indexed drawing/progress tables are not yet extended for index 3.
- No independent new World/Stage selection views have been wired into the graphics/input state machine.
- The real exit-completed callback is not connected to `FanRuntimeAdapter.onEngineLevelFinished`.
- No Android runtime test has been performed. The map's exit and room connectivity is not validated in the game engine.
- The existing static 41 classic level records are preserved, but on-device regression for them is pending.

**Policy:** Never call this a playable fourth world until every release blocker above is resolved. Do not commit keystores/passwords. No APK creation in this CI workflow.

## Last confirmed CI

Check the branch's latest GitHub Actions run named `Diamond Rush - Fan Engine DEX Research`. It must check Java navigation/save, actual generated Stage1 geometry, DEX roundtrip, real smali menu/route patch and no release artifacts.
