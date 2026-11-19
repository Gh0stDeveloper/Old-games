# Diamond Rush Fan Levels — Engine integration branch

This branch is **experimental**. The existing Android 7–16 APK under `games/Diamond-Rush/` is only a **read-only CI input**; do not modify it in-place.

## Target

`LEVELS FAN → LOST CITY → STAGE 1 → exit → fan-only persistent progress`

Original Angkor, Scotland and Tibet (41 level records) must remain intact. The fan world must be a genuine additional world, **not** an Angkor replacement or a relabeled leaderboard.

## CI workflow

`.github/workflows/diamond-rush-fan-engine.yml` runs on commits to this branch. On Ubuntu it installs `apktool` and `smali`, checks the original world's formats, disassembles and reassembles `classes.dex`, compares DEX symbol table counts and publishes text-only diagnostic reports in Actions. It deliberately **does not package or sign any APK**.

When the DEX roundtrip works, locate and connect:
- Menu render: `Lcom/gdxgame/c/a/b;->x()V`
- Menu actions: `G()V`; state transitions: `p(I)V`; input: `az()V` and `a(Lb/a/a/a;)V`
- Worlds: `a()V` registering `/w0.bin`, `/w1.bin`, `/w2.bin`
- Region selector: `T(I)V`; level loader: `ab()V`
- Stage-complete event and isolated save namespace: still to be wired and proven on Android

**Warning**: Those are research leads, not a complete patch specification. The selected menu item must be traced before redirecting it.

## Security and distribution

Do not commit private keystores, passwords, app signing secrets, user progress or decoded proprietary asset bundles. The existing public repository already stores an adapted APK; this work does not publish additional copies. Public distribution of fan modifications must respect the original rights holders.

## Current status

GitHub Actions workflow and DEX roundtrip pipeline: committed for CI validation.
Actual in-game `LEVELS FAN` selector and independent stage saving: **not implemented yet**.
No new APK should be delivered until the complete user-visible route exists.
