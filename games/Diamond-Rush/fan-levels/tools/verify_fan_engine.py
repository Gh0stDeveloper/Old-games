#!/usr/bin/env python3
"""Strict static gates for the temporary fourth-world DEX.

Passing is necessary, NOT sufficient for an installable Android build.
"""
import argparse,hashlib,json,pathlib,re,struct
B="Lcom/gdxgame/c/a/b;"
def one_method(s,name):
    m=list(re.finditer(r"(?ms)^\.method [^\n]*\b"+re.escape(name)+r"\n.*?^\.end method$",s))
    if len(m)!=1:raise AssertionError(f"Expected one {name}, found {len(m)}")
    return m[0].group()
def require(value,description,where):
    if value not in where:raise AssertionError(f"{description}: missing {value}")
def switched(body,label,expected=4):
    exp=r"(?ms)"+re.escape(label)+r"\s*\n\s*\.packed-switch\s+0x0\s*\n(?P<body>.*?)\.end packed-switch"
    matches=list(re.finditer(exp,body))
    if len(matches)!=1:raise AssertionError(f"{label}: expected 1 switch, got {len(matches)}")
    cases=re.findall(r"(?m)^\s+:[A-Za-z0-9_]+\s*$",matches[0].group("body"))
    if len(cases)!=expected:raise AssertionError(f"{label}: wanted {expected} cases, got {len(cases)}")
def main():
    p=argparse.ArgumentParser()
    p.add_argument("--smali",required=True)
    p.add_argument("--decoded",required=True)
    p.add_argument("--assets",required=True)
    p.add_argument("--out",required=True)
    a=p.parse_args()
    core=pathlib.Path(a.smali).read_text(encoding="utf-8")
    assets=pathlib.Path(a.assets)
    assert ".field private static fanActive:Z" in core
    assert ".field private static fanClassicH:[B" in core
    x=one_method(core,"x()V")
    require('"LEVELS FAN"',"menu label",x)
    n=one_method(core,"N()V")
    require("->fanOpen()Z","menu tap",n)
    require("->d()V","menu fallback",n)
    init=one_method(core,"a()V")
    for world in range(4):
        require(f'"/w{world}.bin"',f"world {world} resource",init)
    require("const/4 v7, 0x4","four-world registry",init)
    region=one_method(core,"T(I)V")
    require('"/map_fan_levels.out"',"world 3 selector",region)
    switched(region,":pswitch_data_1")
    switched(region,":pswitch_data_2")
    y=one_method(core,"y(I)V")
    require(':fan_world5',"world 3 progress loader",y)
    require('"/map_fan_levels.out"',"world 3 progress map",y)
    switched(y,":pswitch_data_0",6)
    j=one_method(core,"j(I)I")
    require("const/4 v0, 0x4","four-world offset bound",j)
    op=one_method(core,"fanOpen()Z")
    for val in ("0x2","0x3","0x4","0x5"):
        require(f"const/4 v0, {val}",f"world init {val}",op)
    require("->fy:I","world offset cursor",op)
    require("add-int/lit8 v0, v0, 0x2","fourth pointer reserved",op)
    require("const/16 v1, 0x1000","temporary buffer capacity",op)
    require("->cT()V","world selector call",op)
    restore=one_method(core,"fanRestore()V")
    require("->fanClassicH:[B","original H restored",restore)
    require("->H:[B","H swapped back",restore)
    state=one_method(core,"p(I)V")
    require("->fanRestore()V","leave fan state",state)
    saving=one_method(core,"V()V")
    require("->fanActive:Z","classic save blocked in fan mode",saving)
    finish=one_method(core,"T()V")
    require("->fanPersistCompletion()V","real level completion callback",finish)
    fp=one_method(core,"fanPersistCompletion()V")
    for term in ('"diamond_rush_fan_levels"','"lost_city.stage_1.completed"','->getPreferences(', '->putBoolean(', '->flush()V'):
        require(term,"isolated completion persistence",fp)
    if "gamedata" in fp:raise AssertionError("Fan completion unexpectedly references classic save")
    for name,label in (("db()V",":pswitch_data_1"),("dc()V",":pswitch_data_0"),("dd()V",":pswitch_data_0")):
        switched(one_method(core,name),label)
    raw=(assets/"w3.bin").read_bytes()
    if raw[:2]!=bytes([1,1]) or struct.unpack_from("<HH",raw,2)!=(44,30) or len(raw)!=3966:
        raise AssertionError("Lost City Stage1 binary geometry changed")
    reference="7b0c23e49ea9bda541f283cf8955a8e4617a03dcd42910dde974a94769e5ea4b"
    if hashlib.sha256(raw).hexdigest()!=reference:
        raise AssertionError("Lost City stage content hash mismatch")
    if len((assets/"map_fan_levels.out").read_bytes())!=10:
        raise AssertionError("Fan selector map data missing")
    # Require that the exact libGDX methods used for saving exist in the shipped DEX.
    decoded=pathlib.Path(a.decoded)
    classes={}
    for cls in ("Application","Preferences"):
        matches=list(decoded.rglob("com/badlogic/gdx/"+cls+".smali"))
        if len(matches)!=1:raise AssertionError(f"Can't locate libGDX {cls}.smali")
        classes[cls]=matches[0].read_text(encoding="utf-8")
    require("getPreferences(Ljava/lang/String;)Lcom/badlogic/gdx/Preferences;","Application contract",classes["Application"])
    require("putBoolean(Ljava/lang/String;Z)Lcom/badlogic/gdx/Preferences;","Preferences contract",classes["Preferences"])
    require("flush()V","Preferences flush",classes["Preferences"])
    result={"stage_geometry":"44x30 one level","dex_menu_hook":True,
            "fourth_world_binary_route":True,"fourth_world_offsets_nonoverlapping":True,
            "fourth_world_map_route":True,"stage_selector_mapping":True,
            "stage_completion_separate_preferences":True,"original_save_guard":True,
            "gameplay_on_android_tested":False,"release_allowed":False,
            "no_apk_generated":True}
    target=pathlib.Path(a.out);target.parent.mkdir(parents=True,exist_ok=True)
    target.write_text(json.dumps(result,indent=2)+"\n")
    print("PASS: fourth-world DEX static integration gates; no APK built; Android verification still required")
if __name__=="__main__":main()
