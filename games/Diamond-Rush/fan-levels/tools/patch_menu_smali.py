#!/usr/bin/env python3
"""Patch ONLY the original main-menu option label and action 4.

This deliberately produces a smali research tree / temporary DEX, NOT an APK.
It does NOT claim to bind the libGDX EnginePort or enable a fourth world.
"""
import argparse
import hashlib
import json
import pathlib
import re

CORE="Lcom/gdxgame/c/a/b;"
ORIGINAL="Lcom/gdxgame/c/k;"
NEW="Lghost/diamondrush/fan/FanMenuEntry;"

def get_method(text, name):
    regex=r"(?ms)^\.method [^\n]*\b"+re.escape(name)+r"\n.*?^\.end method$"
    hits=list(re.finditer(regex,text))
    if len(hits)!=1:
        raise AssertionError(f"Need exactly one {name} in the main game class; found {len(hits)}")
    return hits[0]

def patch(text):
    n=get_method(text,"N()V")
    body=n.group()
    # Fall back to the original class k leaderboard when no fan controller exists.
    old=re.compile(
        r"(?m)^[ \t]*iget-object (?P<reg>v[0-9]+), p0, "
        +re.escape(CORE)+"->iw:"+re.escape(ORIGINAL)
        +r"\s*\n\s*invoke-virtual \{(?P=reg)\}, "+re.escape(ORIGINAL)+r"->d\(\)V")
    match=list(old.finditer(body))
    if len(match)!=1:
        raise AssertionError(f"Expected exactly one original Leaderboard action in N(); found {len(match)}")
    source=match[0].group()
    hook=(
        "    invoke-static {}, "+NEW+"->tryOpen()Z\n\n"
        "    move-result v0\n\n"
        "    if-nez v0, :fan_menu_handled\n\n"
        +source.strip("\n")+
        "\n\n    :fan_menu_handled"
    )
    replaced=old.sub(lambda _: hook,body,count=1)
    assert "tryOpen()Z" in replaced and source.strip() in replaced
    text=text[:n.start()]+replaced+text[n.end():]
    x=get_method(text,"x()V")
    render=x.group()
    old_label='const-string v1, "LEADERBOARD"'
    if render.count(old_label)!=1:
        raise AssertionError("Cannot uniquely locate menu label; refusing global rewrite")
    new_render=render.replace(old_label,'const-string v1, "LEVELS FAN"',1)
    text=text[:x.start()]+new_render+text[x.end():]
    # Additional read-only validations: G dispatch, original level routes and region selector
    if "invoke-direct {p0}, "+CORE+"->N()V" not in get_method(text,"G()V").group():
        raise AssertionError("Main menu action dispatcher G changed unexpectedly")
    for route in ('"/w0.bin"','"/w1.bin"','"/w2.bin"'):
        if route not in get_method(text,"a()V").group():
            raise AssertionError(f"Original world route vanished: {route}")
    return text,{
        "main_menu_action_method":"N()V",
        "fan_menu_selection":4,
        "new_menu_text":"LEVELS FAN",
        "new_hook":NEW+"->tryOpen()Z",
        "fallback_legacy_leaderboard":True,
        "fourth_world_registered":False,
        "game_engine_port_bound":False,
        "apk_generated":False,
        "release_allowed":False
    }

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--smali",required=True)
    ap.add_argument("--out",required=True)
    args=ap.parse_args()
    p=pathlib.Path(args.smali)
    before=p.read_text(encoding="utf-8")
    after,info=patch(before)
    if after==before:
        raise AssertionError("Patch didn't change code")
    p.write_text(after,encoding="utf-8")
    info["core_sha256_before"]=hashlib.sha256(before.encode()).hexdigest()
    info["core_sha256_after"]=hashlib.sha256(after.encode()).hexdigest()
    out=pathlib.Path(args.out);out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(info,indent=2)+"\n")
    print("PASS: N() action 4 now calls FanMenuEntry with unbound fallback; display text LEVELS FAN")
    print("NOTE: DO NOT BUILD APK: fourth world and Android GamePort are not connected")

if __name__=="__main__":main()
