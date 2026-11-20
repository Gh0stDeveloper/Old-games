#!/usr/bin/env python3
"""Show LOST CITY and STAGE 1 only for world index 3 in the ORIGINAL renderer."""
import argparse,json,pathlib,re
CORE="Lcom/gdxgame/c/a/b;"
def method(text,name):
    ms=list(re.finditer(r"(?ms)^\.method [^\n]*\b"+re.escape(name)+r"\n.*?^\.end method$",text))
    if len(ms)!=1:raise AssertionError(f"Expected exactly one {name}, got {len(ms)}")
    return ms[0]
def patch(content):
    m=method(content,"ak()V")
    s=m.group()
    if ".locals 17" not in s.splitlines()[:3]:
        raise AssertionError("Renderer register allocation changed")
    title=(
        "    aget v3, v3, v5\n\n"
        "    aget-object v3, v1, v3\n\n"
        "    const/16 v5, 0xf"
    )
    newtitle=(
        "    aget v3, v3, v5\n\n"
        "    aget-object v3, v1, v3\n\n"
        "    const/4 v1, 0x3\n\n"
        "    if-ne v5, v1, :fan_world_title_ready\n\n"
        '    const-string v3, "LOST CITY"\n\n'
        "    :fan_world_title_ready\n"
        "    const/16 v5, 0xf"
    )
    if s.count(title)!=1:raise AssertionError("World title load anchor no longer unique")
    s=s.replace(title,newtitle,1)
    stage=(
        "    aget v3, v3, v4\n\n"
        "    aget-object v3, v1, v3\n\n"
        "    const/16 v5, 0x32"
    )
    newstage=(
        "    aget v3, v3, v4\n\n"
        "    aget-object v3, v1, v3\n\n"
        "    iget v4, v0, "+CORE+"->cL:I\n\n"
        "    const/4 v1, 0x3\n\n"
        "    if-ne v4, v1, :fan_stage_title_ready\n\n"
        '    const-string v3, "STAGE 1"\n\n'
        "    :fan_stage_title_ready\n"
        "    const/16 v5, 0x32"
    )
    if s.count(stage)!=1:raise AssertionError("Stage title load anchor no longer unique")
    s=s.replace(stage,newstage,1)
    return content[:m.start()]+s+content[m.end():],{
        "render_method":"ak()V",
        "fan_world":3,
        "fan_region_text":"LOST CITY",
        "fan_stage_index":0,
        "fan_stage_text":"STAGE 1",
        "original_world_renderers_preserved":True,
        "requires_android_visual_check":True,
        "apk_generated":False}
def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--smali",required=True)
    ap.add_argument("--out",required=True)
    a=ap.parse_args()
    p=pathlib.Path(a.smali);updated,info=patch(p.read_text())
    p.write_text(updated)
    out=pathlib.Path(a.out);out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(info,indent=2)+"\n")
    print("PASS: dedicated LOST CITY / STAGE 1 headings in original DEX selector renderer (no APK)")
if __name__=="__main__":main()
