#!/usr/bin/env python3
"""Make fourth-world *resource registration* explicit in a temporary smali tree.

No APK output. This does not create selector UI or finish-progress hooks.
Each original world path and case is retained verbatim.
"""
import argparse
import json
import pathlib
import re

GAME="Lcom/gdxgame/c/a/b;"

def method_span(text,name):
    matches=list(re.finditer(r"(?ms)^\.method [^\n]*\b"+re.escape(name)+r"\n.*?^\.end method$",text))
    if len(matches)!=1:
        raise AssertionError(f"Expected exactly one method {name}, got {len(matches)}")
    return matches[0]

def alter(method,original,replacement,description):
    if method.count(original)!=1:
        raise AssertionError(f"{description}: expected exact anchor once, got {method.count(original)}")
    return method.replace(original,replacement,1)

def apply(text):
    m=method_span(text,"a()V")
    init=m.group()
    # Metadata indexed by world must have slot 3 as well. Reuse Angkor's
    # *visual sprite index* and region palette, not its game-level data.
    c_old=(
        "    new-array v0, v7, [I\n\n"
        "    fill-array-data v0, :array_a\n\n"
        f"    sput-object v0, {GAME}->c:[I"
    )
    c_new=(
        "    const/4 v1, 0x4\n\n"
        "    new-array v0, v1, [I\n\n"
        "    fill-array-data v0, :array_a\n\n"
        "    const/4 v1, 0x3\n\n"
        "    const/16 v2, 0x1c\n\n"
        "    aput v2, v0, v1\n\n"
        f"    sput-object v0, {GAME}->c:[I"
    )
    init=alter(init,c_old,c_new,"fourth visual metadata index")
    d_old="    new-array v0, v7, [[I"
    d_new="    const/4 v1, 0x4\n\n    new-array v0, v1, [[I"
    init=alter(init,d_old,d_new,"fourth region palette array")
    d_tail=(
        "    fill-array-data v2, :array_d\n\n"
        "    aput-object v2, v0, v1\n\n"
        f"    sput-object v0, {GAME}->d:[[I"
    )
    d_extra=(
        "    fill-array-data v2, :array_d\n\n"
        "    aput-object v2, v0, v1\n\n"
        "    const/4 v1, 0x3\n\n"
        "    const/16 v2, 0xd\n\n"
        "    new-array v2, v2, [I\n\n"
        "    fill-array-data v2, :array_b\n\n"
        "    aput-object v2, v0, v1\n\n"
        f"    sput-object v0, {GAME}->d:[[I"
    )
    init=alter(init,d_tail,d_extra,"world 3 visual palette")

    # v7 is 3 in the old initializer and is only changed directly before
    # constructing the world-resource array. Earlier menu arrays remain untouched.
    old="    new-array v0, v7, [Ljava/lang/String;"
    init=alter(init,old,"    const/4 v7, 0x4\n\n"+old,"world path array allocation")
    old=(
        '    const-string v2, "/w2.bin"\n\n'
        '    aput-object v2, v0, v1\n\n'
        f'    sput-object v0, {GAME}->e:[Ljava/lang/String;'
    )
    replacement=(
        '    const-string v2, "/w2.bin"\n\n'
        '    aput-object v2, v0, v1\n\n'
        '    const/4 v1, 0x3\n\n'
        '    const-string v2, "/w3.bin"\n\n'
        '    aput-object v2, v0, v1\n\n'
        f'    sput-object v0, {GAME}->e:[Ljava/lang/String;'
    )
    init=alter(init,old,replacement,"register world 3")
    text=text[:m.start()]+init+text[m.end():]
    m=method_span(text,"T(I)V")
    region=m.group()
    # The first switch on cL has 0,1,2 for Angkor, Scotland and Tibet.
    # Add world index 3 ONLY to this resource-path switch. The second UI
    # switch still lacks a world-3 branch and is an explicit release blocker.
    old=(
        '    :pswitch_8\n'
        f'    sget-object v0, {GAME}->aJ:Ljava/lang/StringBuffer;\n\n'
        '    const-string v1, "/map_tibet.out"\n\n'
        '    invoke-virtual {v0, v1}, Ljava/lang/StringBuffer;->append(Ljava/lang/String;)Ljava/lang/StringBuffer;\n\n'
        '    goto :goto_1'
    )
    replacement=old+(
        '\n\n    :fan_world_map_3\n'
        f'    sget-object v0, {GAME}->aJ:Ljava/lang/StringBuffer;\n\n'
        '    const-string v1, "/map_fan_levels.out"\n\n'
        '    invoke-virtual {v0, v1}, Ljava/lang/StringBuffer;->append(Ljava/lang/String;)Ljava/lang/StringBuffer;\n\n'
        '    goto :goto_1'
    )
    region=alter(region,old,replacement,"world 3 map route")
    switch=re.compile(r"(?ms)(:pswitch_data_1\s*\n\s*\.packed-switch 0x0\s*\n)(.*?)(\s*\.end packed-switch)")
    matches=list(switch.finditer(region))
    if len(matches)!=1:
        raise AssertionError(f"Need exactly one second region route switch, found {len(matches)}")
    case_lines=[x.strip() for x in matches[0].group(2).splitlines() if x.strip()]
    if case_lines!=[":pswitch_6",":pswitch_7",":pswitch_8"]:
        raise AssertionError(f"Unexpected original region switch cases: {case_lines}")
    region=region[:matches[0].start(3)]+"\n        :fan_world_map_3"+region[matches[0].start(3):]
    # The world-specific UI sprite loader has another three-way switch.
    # World 3 uses the existing Angkor region sprite while still loading its
    # OWN map and level data.
    visual_old=(
        "    :pswitch_data_2\n"
        "    .packed-switch 0x0\n"
        "        :pswitch_b\n"
        "        :pswitch_c\n"
        "        :pswitch_d\n"
        "    .end packed-switch"
    )
    visual_new=visual_old.replace(
        "        :pswitch_d\n", "        :pswitch_d\n        :pswitch_b\n")
    region=alter(region,visual_old,visual_new,"world 3 region texture")
    text=text[:m.start()]+region+text[m.end():]
    # y(I) initializes map/world progress data from a binary world file and
    # associated .out map. It takes p1=worldIndex+2.
    m=method_span(text,"y(I)V")
    saved=m.group()
    y_old=(
        '    :pswitch_3\n'
        '    if-nez v0, :cond_2\n\n'
        '    const-string v0, "/map_tibet.out"\n\n'
        '    :cond_2'
    )
    y_new=(
        '    :pswitch_3\n'
        '    if-nez v0, :cond_2\n\n'
        '    const-string v0, "/map_tibet.out"\n\n'
        '    goto :cond_2\n\n'
        '    :fan_world5\n'
        '    const-string v0, "/map_fan_levels.out"\n\n'
        '    goto :cond_2\n\n'
        '    :cond_2'
    )
    saved=alter(saved,y_old,y_new,"world index 3 y(I) resource input")
    switch_tail=(
        '    :pswitch_data_0\n'
        '    .packed-switch 0x0\n'
        '        :pswitch_0\n'
        '        :pswitch_0\n'
        '        :pswitch_1\n'
        '        :pswitch_2\n'
        '        :pswitch_3\n'
        '    .end packed-switch'
    )
    saved=alter(saved,switch_tail,switch_tail.replace(
        '        :pswitch_3\n', '        :pswitch_3\n        :fan_world5\n'),
        "world 3 progress-load dispatch")
    text=text[:m.start()]+saved+text[m.end():]
    assert text.count('"/w3.bin"')==1 and text.count('"/map_fan_levels.out"')==2
    return text,{
        "fourth_world_binary_route_registered":True,
        "world_indexed_visual_metadata_extended":True,
        "world_3_progress_loader_route_registered":True,
        "fourth_world_selection_map_route_registered":True,
        "world_index":3,"world_path":"/w3.bin",
        "fan_route_path":"/map_fan_levels.out",
        "original_worlds_preserved":True,
        "world3_gameplay_ui_integrated":False,
        "fan_save_connected":False,
        "release_allowed":False
    }

def main():
    p=argparse.ArgumentParser();p.add_argument("--smali",required=True);p.add_argument("--out",required=True)
    a=p.parse_args()
    path=pathlib.Path(a.smali)
    old=path.read_text(encoding="utf-8")
    new,result=apply(old)
    path.write_text(new,encoding="utf-8")
    dst=pathlib.Path(a.out);dst.parent.mkdir(parents=True,exist_ok=True)
    dst.write_text(json.dumps(result,indent=2)+"\n",encoding="utf-8")
    print("PASS: world 3 binary, map, UI palette and progress-loader routes installed in temporary DEX")
    print("BLOCKED: fourth-world UI tables and real save callbacks not yet connected, no APK allowed")

if __name__=="__main__":main()
