#!/usr/bin/env python3
"""Generate Lost City Stage 1 into CI temporary storage from an existing APK.

Never commits an altered APK or proprietary binary map.
"""
import argparse
import hashlib
import json
import pathlib
import struct
import zipfile

ORIGINAL_WORLD_SHA="0b2eb7662959fd1e73b8ee435e96ca9cff87bd159dec845640954ed9658c0ffd"
FAN_WORLD_SHA="7b0c23e49ea9bda541f283cf8955a8e4617a03dcd42910dde974a94769e5ea4b"
WIDTH,HEIGHT=44,30
FAN_ROUTE=bytes.fromhex("07 00 01 01 03 00 00 01 04 04")

def digest(data):
    return hashlib.sha256(data).hexdigest()

def parse_world(data):
    if len(data)<2 or data[0]!=1:raise ValueError("Bad binary world version")
    pos=2;records=[]
    for _ in range(data[1]):
        if pos+4>len(data):raise ValueError("Truncated dimensions")
        w,h=struct.unpack_from("<HH",data,pos);pos+=4
        if not 0<w<=256 or not 0<h<=256:raise ValueError("Bad dimensions")
        layers=[]
        for i in range(3):
            chunk=data[pos:pos+w*h];pos+=w*h
            if len(chunk)!=w*h:raise ValueError("Truncated layer")
            layers.append(chunk)
        records.append((w,h,layers))
    if pos!=len(data):raise ValueError("Trailing bytes")
    return records

def construct(apk):
    with zipfile.ZipFile(apk) as z:
        raw=z.read("assets/data/w0.bin")
        assert all("assets/data/"+x in z.namelist() for x in ("w1.bin","w2.bin"))
    if digest(raw)!=ORIGINAL_WORLD_SHA:raise ValueError("Unknown source w0.bin; refusing remix")
    levels=parse_world(raw)
    if len(levels)!=14 or levels[2][:2]!=(27,26):raise ValueError("Source Stage 3 structure changed")
    w,h,layers=levels[2]
    ground=bytearray(WIDTH*HEIGHT)
    objects=bytearray([255]*(WIDTH*HEIGHT))
    events=bytearray([255]*(WIDTH*HEIGHT))
    for y in range(HEIGHT):
        for x in range(WIDTH):
            ground[y*WIDTH+x]=(0x60,0x61,0x55,0x64)[(x//3+y//3)%4]
    for src,dst in zip(layers,(ground,objects,events)):
        for y in range(h):
            dst[y*WIDTH:y*WIDTH+w]=src[y*w:(y+1)*w]
    def room(x0,y0,x1,y1,val=255):
        assert x0>=27
        for y in range(y0,y1+1):
            for x in range(x0,x1+1):ground[y*WIDTH+x]=val
    room(29,8,42,23);room(27,20,32,22);room(27,21,35,21)
    room(39,6,41,10);room(38,3,42,7);room(40,2,41,2)
    for x in range(32,35):ground[12*WIDTH+x]=0x0a
    for y in range(13,18):ground[y*WIDTH+35]=0x60
    for x in range(38,41):ground[18*WIDTH+x]=0x55
    ground[8*WIDTH+40]=0x0a
    for x,y in ((34,9),(39,12),(36,19),(39,4)):
        for dx,dy,val in ((0,0,0x14),(1,0,0x15),(0,1,0x16),(1,1,0x17)):
            events[(y+dy)*WIDTH+x+dx]=val
    output=b"\x01\x01"+struct.pack("<HH",WIDTH,HEIGHT)+bytes(ground)+bytes(objects)+bytes(events)
    if digest(output)!=FAN_WORLD_SHA:raise AssertionError("Stage diverged from validated baseline")
    return output

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--apk",type=pathlib.Path,required=True)
    ap.add_argument("--out",type=pathlib.Path,required=True)
    a=ap.parse_args()
    data=construct(a.apk)
    a.out.mkdir(parents=True,exist_ok=True)
    (a.out/"w3.bin").write_bytes(data)
    (a.out/"map_fan_levels.out").write_bytes(FAN_ROUTE)
    (a.out/"manifest.json").write_text(json.dumps({
        "world":"Lost City","stage":"Stage 1","world_index":3,"level_index":0,
        "dimensions":[WIDTH,HEIGHT],"source_classic_levels_untouched":41,
        "sha256_w3":digest(data),"sha256_map":digest(FAN_ROUTE),
        "status":"resource generated and validated; runtime UI and completion still pending"
    },indent=2)+"\n")
    print("PASS: regenerated world 3 from source APK, exact stage hash matched (not an APK build)")
if __name__=="__main__":main()
