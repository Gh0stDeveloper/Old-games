#!/usr/bin/env python3
"""Connect the game's *real* T() stage-finished callback to private fan progress.

Temporary smali DEX only. Uses libGDX Preferences, never the classic 'gamedata'.
No APK built here: still requires Android execution tests and resource integration.
"""
import argparse,json,pathlib,re
GAME="Lcom/gdxgame/c/a/b;"
GDX="Lcom/badlogic/gdx/"
def span(s,name):
    m=list(re.finditer(r"(?ms)^\.method [^\n]*\b"+re.escape(name)+r"\n.*?^\.end method$",s))
    if len(m)!=1:raise AssertionError(f"Missing or ambiguous {name}: {len(m)}")
    return m[0]

HOOK=r""".method private fanPersistCompletion()V
    .locals 3

    :try_start_fan
    sget-boolean v0, Lcom/gdxgame/c/a/b;->fanActive:Z

    if-eqz v0, :fan_done

    iget v0, p0, Lcom/gdxgame/c/a/b;->cL:I

    const/4 v1, 0x3

    if-ne v0, v1, :fan_done

    iget v0, p0, Lcom/gdxgame/c/a/b;->cM:I

    if-nez v0, :fan_done

    sget-object v0, Lcom/badlogic/gdx/Gdx;->app:Lcom/badlogic/gdx/Application;

    const-string v1, "diamond_rush_fan_levels"

    invoke-interface {v0, v1}, Lcom/badlogic/gdx/Application;->getPreferences(Ljava/lang/String;)Lcom/badlogic/gdx/Preferences;

    move-result-object v0

    const-string v1, "lost_city.stage_1.completed"

    const/4 v2, 0x1

    invoke-interface {v0, v1, v2}, Lcom/badlogic/gdx/Preferences;->putBoolean(Ljava/lang/String;Z)Lcom/badlogic/gdx/Preferences;

    move-result-object v0

    invoke-interface {v0}, Lcom/badlogic/gdx/Preferences;->flush()V
    :try_end_fan
    .catch Ljava/lang/Exception; {:try_start_fan .. :try_end_fan} :fan_save_failed

    goto :fan_done

    :fan_save_failed
    move-exception v0

    :fan_done
    return-void
.end method
"""

def patch(s):
    if '->fanPersistCompletion()V' in s:
        raise AssertionError("Completion hook already applied")
    t=span(s,"T()V")
    body=t.group()
    anchor=f"    invoke-direct {{p0}}, {GAME}->V()V\n\n    return-void"
    if body.count(anchor)!=1:raise AssertionError("Stage completion T() body changed")
    body=body.replace(anchor,
        f"    invoke-direct {{p0}}, {GAME}->V()V\n\n"
        f"    invoke-direct {{p0}}, {GAME}->fanPersistCompletion()V\n\n"
        "    return-void")
    s=s[:t.start()]+body+s[t.end():]
    # Guard the original classic persistence from any fan H buffer.
    v=span(s,"V()V").group()
    if f"sget-boolean v0, {GAME}->fanActive:Z" not in v:
        raise AssertionError("Missing fan-mode guard on classic gamedata saving")
    # Keep native victory and unlock behavior intact; a new method saves only the fan key.
    s+="\n"+HOOK+"\n"
    return s,{
        "stage_finish_callback":"T()V",
        "stage_finish_dispatch":"T(I)V, state fq set; stage unlock then T()V",
        "fan_stage_world_index":3,
        "fan_stage_index":0,
        "gdx_preferences_namespace":"diamond_rush_fan_levels",
        "gdx_preferences_key":"lost_city.stage_1.completed",
        "legacy_save_guard_present":True,
        "completion_hook_in_temporary_dex":True,
        "android_stage_exit_verified":False,
        "apk_generated":False,
        "release_allowed":False
    }
def main():
    p=argparse.ArgumentParser()
    p.add_argument("--smali",required=True)
    p.add_argument("--out",required=True)
    args=p.parse_args()
    src=pathlib.Path(args.smali)
    modified,status=patch(src.read_text(encoding="utf-8"))
    src.write_text(modified,encoding="utf-8")
    out=pathlib.Path(args.out)
    out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(status,indent=2)+"\n",encoding="utf-8")
    print("PASS: original stage-finished T() now calls isolated libGDX fan save in temporary DEX")
    print("BLOCKED: no Android gameplay/exit tests and no installable APK")
if __name__=="__main__": main()
