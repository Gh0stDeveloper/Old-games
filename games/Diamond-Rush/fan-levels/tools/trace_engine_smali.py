#!/usr/bin/env python3
"""Collect small, traceable smali slices from the original Diamond Rush UI.

Read-only; reports code locations. No modifications or APK generation.
"""
import argparse
import json
from pathlib import Path

TARGETS = [
    ".method private G()V",
    ".method private az()V",
    ".method private M()V",
    ".method private J()V",
    ".method private N()V",
    ".method private L()V",
    ".method private I()V",
    ".method private H()V",
    ".method private a()V",
    ".method private T(I)V",
    ".method private ab()V",
]
NAMES = {"G()V", "az()V", "M()V", "J()V", "N()V", "L()V", "I()V", "H()V", "a()V", "T(I)V", "ab()V", "x()V"}
NEEDLES = ("dT:", "LEADERBOARD", "w0.bin", "w1.bin", "w2.bin", "w3.bin",
           "map_angkor", "map_scotland", "map_tibet", "gamedata", "packed-switch", "sparse-switch")

def extract(path):
    lines = path.read_text(encoding="utf-8").splitlines()
    methods = {}
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        if not line.startswith(".method "):
            i += 1
            continue
        start = i
        while i < len(lines) and lines[i].strip() != ".end method":
            i += 1
        end = min(i, len(lines) - 1)
        name = line.split()[-1]
        if name in NAMES:
            body = lines[start:end + 1]
            refs = [{"line": start + j + 1, "code": t.strip()}
                    for j, t in enumerate(body) if any(x in t for x in NEEDLES)]
            windows = []
            if name in {"T(I)V","a()V","N()V"}:
                for j, line_ in enumerate(body):
                    if any(s in line_ for s in ("/w0.bin","/w1.bin","/w2.bin", "/map_angkor.out","/map_tibet.out", ".packed-switch", "->iw:Lcom/gdxgame/c/k;")):
                        windows.append({
                            "line": start + j + 1,
                            "context": body[max(0, j - 12): min(len(body), j + 25)]
                        })
            methods[name] = {"line_start": start + 1, "line_end": end + 1,
                             "instruction_lines": len(body),
                             "refs": refs[:140], "windows": windows[:25],
                             "head": body[:75] if name in {"G()V", "M()V", "T(I)V", "a()V"} else body[:20]}
        i += 1
    return methods

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--smali",required=True)
    p.add_argument("--out",required=True)
    args=p.parse_args()
    root=Path(args.smali)
    selected=list(root.rglob("com/gdxgame/c/a/b.smali"))
    if len(selected)!=1:
        raise SystemExit("Expected exactly one core class b.smali, got "+str(selected))
    methods=extract(selected[0])
    required={"G()V","az()V","M()V","T(I)V","a()V","ab()V"}
    if not required.issubset(methods):
        raise SystemExit("Missing important methods: "+str(sorted(required-set(methods))))
    result={"file":str(selected[0]),"methods":methods}
    out=Path(args.out);out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(result,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    print("METHOD SIGNATURES:", sorted(methods))
    for name in ("G()V","M()V","T(I)V","a()V","az()V"):
        m=methods[name]
        print("###",name,"lines",m["line_start"],"-",m["line_end"],"refs",len(m["refs"]))
        # Keep summary short in Actions logs, full report uploaded separately.
        for r in m["refs"][:20]:
            print(f'{r["line"]:5d}: {r["code"]}')
    print("PASS: located menu dispatcher, world loader and region selector smali")
if __name__=="__main__":main()
