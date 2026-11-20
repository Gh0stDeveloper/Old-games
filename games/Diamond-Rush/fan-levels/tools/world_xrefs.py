#!/usr/bin/env python3
"""Read-only map of world-indexed fields and loaders throughout the game class."""
import argparse, pathlib, re, json
FIELDS=["->cL:I","->cM:I","->c:[I","->d:[[I","->e:[Ljava/lang/String;","->aL:I"]
CALLS=["->z(I)I","->l(II)B","->y(I)V","->T(I)V","->cT()V","->ab()V","->f()V"]
a=argparse.ArgumentParser();a.add_argument("--smali",required=True);a.add_argument("--out",required=True)
p=a.parse_args();file=pathlib.Path(p.smali);lines=file.read_text().splitlines()
methods={};active=None
for n,line in enumerate(lines,1):
    if line.startswith(".method "):
        active=line.split()[-1];methods.setdefault(active,[])
    if active:
        for value in FIELDS+CALLS:
            if value in line:
                methods[active].append({"line":n,"xref":value,"context":" | ".join(
                    s.strip() for s in lines[max(0,n-3):min(len(lines),n+4)])})
    if line.strip()==".end method":active=None
hits={m:xs for m,xs in methods.items() if xs}
target=pathlib.Path(p.out);target.parent.mkdir(parents=True,exist_ok=True)
target.write_text(json.dumps({"methods":hits,"total_method_signatures":len(methods)},indent=2)+"\n")
print(f"PASS: identified world-indexed xrefs in {len(hits)} core methods")
for name,entries in sorted(hits.items(),key=lambda kv:-len(kv[1]))[:15]:
    print(f"{name}: {len(entries)} world/selector references")
