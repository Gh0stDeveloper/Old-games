#!/usr/bin/env python3
"""Extract selected methods into a diagnostic Actions artifact (not the repository)."""
import argparse
import pathlib
import re

names={
    "a()V", "T(I)V", "ab()V", "N()V", "y(I)V", "p(I)V",
    "bf()V", "bg()V", "L()V", "M()V", "F()I", "J()V",
    "cT()V", "z(I)I", "l(II)B", "f()V", "c(Ljava/lang/String;)V",
    "cU()V", "cS()V", "U()V", "V()V", "W()V", "X()V",
    "T()V", "E()V",
}
extra_names={"a(Lb/a/a/a;)V", "G()V"}
p=argparse.ArgumentParser()
p.add_argument("--smali",required=True)
p.add_argument("--out",required=True)
a=p.parse_args()
path=pathlib.Path(a.smali)
text=path.read_text(encoding="utf-8")
lines=text.splitlines()
active=False
total=0
out=[]
for j,line in enumerate(lines):
    if line.startswith(".method "):
        sig=line.split()[-1]
        active=sig in names or sig in extra_names
        if active:
            out.extend(["="*80, f"METHOD {sig} SOURCE LINE {j+1}", "="*80])
    if active:
        out.append(f"{j+1:05d} {line}")
    if active and line.strip()==".end method":
        active=False
        total+=1
if total < 10:raise RuntimeError(f"Expected at least 10 methods, found {total}")
target=pathlib.Path(a.out);target.parent.mkdir(parents=True,exist_ok=True)
target.write_text("\n".join(out)+"\n",encoding="utf-8")
print(f"PASS: extracted {total} DEX methods to diagnostic artifact ({target.stat().st_size} bytes)")
