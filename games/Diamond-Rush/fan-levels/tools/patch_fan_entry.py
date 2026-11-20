#!/usr/bin/env python3
"""Wire the REAL menu to the original stage selector, world index 3.

Experiment only: patch a temporary DEX, guard original "gamedata" by swapping
the in-memory H progress buffer for the fan session, and *do not* package an APK
until on-device launch, exit callbacks and fan-save persistence are implemented.
"""
import argparse
import json
import pathlib
import re

CORE="Lcom/gdxgame/c/a/b;"

def span(text,name):
    hits=list(re.finditer(r"(?ms)^\.method [^\n]*\b"+re.escape(name)+r"\n.*?^\.end method$",text))
    if len(hits)!=1:
        raise AssertionError(f"{name}: wanted one method, found {len(hits)}")
    return hits[0]

FAN_FIELDS=(
    ".field private static fanActive:Z\n"
    ".field private static fanClassicH:[B\n"
)
FAN_METHODS=r""".method private fanRestore()V
    .locals 1

    sget-boolean v0, Lcom/gdxgame/c/a/b;->fanActive:Z

    if-eqz v0, :fan_return

    sget-object v0, Lcom/gdxgame/c/a/b;->fanClassicH:[B

    sput-object v0, Lcom/gdxgame/c/a/b;->H:[B

    const/4 v0, 0x0

    sput-boolean v0, Lcom/gdxgame/c/a/b;->fanActive:Z

    const/4 v0, 0x0

    sput-object v0, Lcom/gdxgame/c/a/b;->fanClassicH:[B

    iput v0, p0, Lcom/gdxgame/c/a/b;->cL:I

    iput v0, p0, Lcom/gdxgame/c/a/b;->cM:I

    :fan_return
    return-void
.end method

.method private fanOpen()Z
    .locals 2

    sget-boolean v0, Lcom/gdxgame/c/a/b;->fanActive:Z

    if-eqz v0, :fan_setup

    const/4 v0, 0x1

    return v0

    :fan_setup
    sget-object v0, Lcom/gdxgame/c/a/b;->H:[B

    sput-object v0, Lcom/gdxgame/c/a/b;->fanClassicH:[B

    const/4 v0, 0x1

    sput-boolean v0, Lcom/gdxgame/c/a/b;->fanActive:Z

    :try_start_0
    const/4 v0, 0x1

    invoke-direct {p0, v0}, Lcom/gdxgame/c/a/b;->y(I)V

    # Fan-only buffer: preserve capacity for all 41 classic indices plus fan.
    sget-object v0, Lcom/gdxgame/c/a/b;->H:[B

    const/16 v1, 0x1000

    invoke-static {v0, v1}, Ljava/util/Arrays;->copyOf([BI)[B

    move-result-object v0

    sput-object v0, Lcom/gdxgame/c/a/b;->H:[B

    # Original layout: three 2-byte world offsets at H[14..19],
    # followed immediately by first world data starting at fy=20.
    # World 3 needs H[20..21], so move data to 22 to prevent overlap.
    iget v0, p0, Lcom/gdxgame/c/a/b;->fy:I

    add-int/lit8 v0, v0, 0x2

    iput v0, p0, Lcom/gdxgame/c/a/b;->fy:I

    # Fan-only session contains four world entries; never written to gamedata.
    sget-object v0, Lcom/gdxgame/c/a/b;->H:[B

    const/4 v1, 0x3

    const/4 v2, 0x4

    aput-byte v2, v0, v1

    # The offset table MUST be built sequentially: world 0, 1, 2, then 3.
    const/4 v0, 0x2

    invoke-direct {p0, v0}, Lcom/gdxgame/c/a/b;->y(I)V

    const/4 v0, 0x3

    invoke-direct {p0, v0}, Lcom/gdxgame/c/a/b;->y(I)V

    const/4 v0, 0x4

    invoke-direct {p0, v0}, Lcom/gdxgame/c/a/b;->y(I)V

    const/4 v0, 0x5

    invoke-direct {p0, v0}, Lcom/gdxgame/c/a/b;->y(I)V

    iget-object v0, p0, Lcom/gdxgame/c/a/b;->aR:Lcom/gdxgame/c/a/h;

    if-eqz v0, :fan_no_music

    invoke-virtual {v0}, Lcom/gdxgame/c/a/h;->d()V

    :fan_no_music
    const/4 v0, 0x3

    iput v0, p0, Lcom/gdxgame/c/a/b;->cL:I

    const/4 v0, 0x0

    iput v0, p0, Lcom/gdxgame/c/a/b;->cM:I

    iput-boolean v0, p0, Lcom/gdxgame/c/a/b;->cb:Z

    sput v0, Lcom/gdxgame/c/a/b;->aL:I

    const/16 v0, 0xf

    invoke-direct {p0, v0}, Lcom/gdxgame/c/a/b;->p(I)V

    const/4 v0, 0x1

    iput-boolean v0, p0, Lcom/gdxgame/c/a/b;->fp:Z

    invoke-direct {p0}, Lcom/gdxgame/c/a/b;->cT()V
    :try_end_0
    .catch Ljava/lang/Exception; {:try_start_0 .. :try_end_0} :fan_failed

    const/4 v0, 0x1

    return v0

    :fan_failed
    move-exception v0

    invoke-direct {p0}, Lcom/gdxgame/c/a/b;->fanRestore()V

    const/4 v0, 0x0

    return v0
.end method
"""

def run(text):
    if "->fanOpen()Z" in text or "fanClassicH:[B" in text:
        raise AssertionError("Fan entry patch is already installed")
    # Add fields before the first existing method; keep all original DEX classes.
    first=re.search(r"(?m)^\.method ",text)
    if not first:raise AssertionError("No method boundary found")
    text=text[:first.start()]+FAN_FIELDS+"\n"+text[first.start():]
    # Replace ONLY the validated N() case-4 hook. Preserve the original
    # Leaderboard fallback if fanOpen returns false.
    n=span(text,"N()V");segment=n.group()
    needle="    invoke-static {}, Lghost/diamondrush/fan/FanMenuEntry;->tryOpen()Z"
    repl=f"    invoke-direct {{p0}}, {CORE}->fanOpen()Z"
    if segment.count(needle)!=1:raise AssertionError("FanMenuEntry N() hook missing")
    segment=segment.replace(needle,repl,1)
    text=text[:n.start()]+segment+text[n.end():]
    # Restore original progress on returning to the classic menu. The original
    # p(I) state handler remains intact for non-fan sessions.
    p=span(text,"p(I)V");body=p.group()
    old=f"    sput p1, {CORE}->p:I"
    restore=(
        f"    sget-boolean v0, {CORE}->fanActive:Z\n\n"
        "    if-eqz v0, :fan_state_ok\n\n"
        "    const/4 v0, 0x7\n\n"
        "    if-eq p1, v0, :fan_leaving\n\n"
        "    const/4 v0, 0x6\n\n"
        "    if-ne p1, v0, :fan_state_ok\n\n"
        "    :fan_leaving\n"
        f"    invoke-direct {{p0}}, {CORE}->fanRestore()V\n\n"
        "    :fan_state_ok\n"
        +old
    )
    if body.count(old)!=1:raise AssertionError("Expected p(I) state setter once")
    body=body.replace(old,restore,1)
    text=text[:p.start()]+body+text[p.end():]
    # Do not persist a modified fan H buffer into the classic save file.
    # The proper isolated FanProgressStore completion path is a separate gate.
    v=span(text,"V()V");body=v.group()
    old="    const/4 v0, 0x0"
    guard=(
        f"    sget-boolean v0, {CORE}->fanActive:Z\n\n"
        "    if-eqz v0, :fan_normal_save\n\n"
        "    return-void\n\n"
        "    :fan_normal_save\n"
        +old
    )
    if body.count(old)<1:raise AssertionError("V() save entry changed")
    body=body.replace(old,guard,1)
    text=text[:v.start()]+body+text[v.end():]
    # Existing path registration from patch_world_routes must be present.
    for word in ('"/w3.bin"', '"/map_fan_levels.out"'):
        if word not in text:raise AssertionError("Missing fourth world path "+word)
    text+="\n"+FAN_METHODS+"\n"
    required=(f"->{x}" for x in ("fanOpen()Z","fanRestore()V"))
    for sig in required:
        if sig not in text:raise AssertionError("Missing "+sig)
    return text,{
        "main_menu_dispatch":"N()V case 4 → fanOpen()Z",
        "world_index":3,"stage_index":0,
        "fourth_world_bootstrap":"y(1) + buffer growth + y(2..5), cL=3, cM=0, cT()",
        "indexed_world_offsets_initialized_in_order":True,
        "fan_working_buffer_bytes":4096,
        "fan_world_offset_table_bytes":8,
        "fan_world_data_start":22,
        "fourth_world_offset_no_overlap":True,
        "fan_progress_temporarily_swapped":True,
        "classic_save_write_guarded":True,
        "classic_menu_restores_original_in_memory_progress":True,
        "dedicated_world_selector_text_completed":False,
        "on_device_gameplay_verified":False,
        "real_exit_event_bound_to_fan_save":False,
        "release_allowed":False,"apk_generated":False
    }

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--smali",required=True)
    p.add_argument("--out",required=True)
    args=p.parse_args()
    target=pathlib.Path(args.smali)
    altered,result=run(target.read_text(encoding="utf-8"))
    target.write_text(altered,encoding="utf-8")
    output=pathlib.Path(args.out);output.parent.mkdir(parents=True,exist_ok=True)
    output.write_text(json.dumps(result,indent=2)+"\n",encoding="utf-8")
    print("PASS: fan menu dispatch enters independent world-3 selector in temporary DEX")
    print("BLOCKED: world-3 runtime not validated, and fan completion not persisted; NO APK")

if __name__=="__main__":main()
