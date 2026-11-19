# Integration gates — Diamond Rush Fan Levels

The previously supplied laboratory APK v0.18 replaced Angkor's 14 levels with a single fan record and broke the tutorial/selector. The v0.19 build restored the 14 records but only replaced an existing level. Neither was a genuine fourth world.

## Mandatory CI / runtime gates

1. CI: source APK has 14 + 13 + 14 original world records, no truncated data.
2. CI: apktool disassembly and smali-only roundtrip works. Compare class, method, string, field and proto counts (file bytes need not match).
3. DEX: menu item 5 is visually LEVELS FAN and selects a NEW handler (do not globally modify a shared LEADERBOARD string).
4. DEX: world 3 exists alongside w0, w1, w2; all world-indexed tables and route selectors support index 3.
5. DEX: existing tutorial and classic progress behavior preserved.
6. DEX: fan level (w3.bin, index 0) can be started, finished and restarted.
7. DEX: fan completion persisted separately from the original gamedata. Pausing, dying and canceling must not complete it.
8. Release: same protected signing key and package id, incremental versionCode, static signature checks.
9. Real Android: NEW GAME, CONTINUE, all three originals, LEVELS FAN, LOST CITY, STAGE 1, save after force-close.

Until gates 3–7 are implemented, **only diagnostic artifacts are permitted**; no APK or release.

## Exact content locations

- Classic: Angkor = world 0, 14 level records; Scotland = world 1, 13; Tibet = world 2, 14.
- New target: Lost City = world 3, Stage 1 = internal index 0.
- Prior QA replacement: Angkor Stage 3, internal index 2 — not part of final plan.

Do not commit original game DEX, extracted sprite atlases or modified proprietary level blobs as additional public files without rights clearance.
