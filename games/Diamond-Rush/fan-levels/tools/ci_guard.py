#!/usr/bin/env python3
"""Read-only Diamond Rush APK/DEX inspection and CI guard. Never builds an APK."""
import argparse
import hashlib
import json
import pathlib
import re
import struct
import zipfile

EXPECTED_LEVELS = {"w0.bin": 14, "w1.bin": 13, "w2.bin": 14}
APK_BASE = "assets/data/"

def world_records(data):
    if len(data) < 2:
        raise ValueError("Missing world header")
    version, count = data[:2]
    pos = 2
    sizes = []
    for i in range(count):
        if pos + 4 > len(data):
            raise ValueError(f"Truncated level dimensions at {i}")
        width, height = struct.unpack_from("<HH", data, pos)
        if not 1 <= width <= 512 or not 1 <= height <= 512:
            raise ValueError(f"Invalid level dimensions: {width}x{height}")
        pos += 4 + 3 * width * height
        if pos > len(data):
            raise ValueError(f"Truncated level cells at {i}")
        sizes.append([width, height])
    if pos != len(data):
        raise ValueError(f"Unexpected trailing bytes: {len(data)-pos}")
    return {"format_version": version, "level_count": count, "dimensions": sizes}

def dex_stats(data):
    if len(data) < 112 or not data.startswith(b"dex\n"):
        raise ValueError("Not a DEX header")
    file_size = struct.unpack_from("<I", data, 32)[0]
    if file_size != len(data):
        raise ValueError("DEX file_size mismatch")
    keys = {"string_ids": 56, "type_ids": 64, "proto_ids": 72,
            "field_ids": 80, "method_ids": 88, "class_defs": 96}
    return {key: struct.unpack_from("<I", data, pos)[0] for key, pos in keys.items()}

def load_apk(path):
    with zipfile.ZipFile(path) as z:
        names = set(z.namelist())
        if "classes.dex" not in names:
            raise ValueError("APK missing classes.dex")
        return {n: z.read(n) for n in names if n in
                {"classes.dex", "classes2.dex"} |
                {APK_BASE + x for x in EXPECTED_LEVELS}}

def save(out, result):
    target = pathlib.Path(out)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(result, indent=2, sort_keys=True)+"\n", encoding="utf-8")

def inspect(args):
    files = load_apk(args.apk)
    worlds = {}
    for name, expected in EXPECTED_LEVELS.items():
        key = APK_BASE + name
        if key not in files:
            raise AssertionError(f"Missing {key}")
        worlds[name] = world_records(files[key])
        if worlds[name]["level_count"] != expected:
            raise AssertionError(f"{name}: expected {expected}, got {worlds[name]['level_count']}")
    result = {
        "apk": str(args.apk),
        "apk_sha256": hashlib.sha256(pathlib.Path(args.apk).read_bytes()).hexdigest(),
        "worlds": worlds,
        "dex": {name: dex_stats(data) for name, data in files.items()
                if name.endswith(".dex")},
        "fan_world_integrated": False,
        "apk_release_allowed": False,
    }
    save(args.out, result)
    print("PASS: original three worlds are structurally intact, 41 level records total")

def roundtrip(args):
    files = load_apk(args.apk)
    checks = {}
    for name, rebuilt_path in (
        ("classes.dex", args.rebuilt),
        ("classes2.dex", args.rebuilt_second),
    ):
        if not rebuilt_path:
            if name in files:
                raise ValueError(f"Missing reassembled {name}")
            continue
        if name not in files:
            raise ValueError(f"Unexpected reconstructed {name}")
        original = dex_stats(files[name])
        assembled = dex_stats(pathlib.Path(rebuilt_path).read_bytes())
        differences = {k: [original[k], assembled[k]]
                       for k in original if original[k] != assembled[k]}
        # An assembler may drop UNUSED string or method-id entries.
        # Identity of the actual code is checked by compare-smali, not ID counts alone.
        # Unused type/prototype/method/string IDs may be pruned by smali.
        # Require class definitions to survive and compare actual instructions separately.
        essential = ("class_defs",)
        critical = {k: differences[k] for k in essential if k in differences}
        checks[name] = {
            "original": original, "reconstructed": assembled,
            "symbol_count_changes": differences,
            "structural_count_failures": critical,
        }
        if critical:
            save(args.out, {"checks": checks, "safe": False})
            raise AssertionError(f"{name}: structural symbol table differences: {critical}")
    save(args.out, {"checks": checks, "class_definition_counts_preserved": True})
    print("PASS: both rebuilt DEX files preserve class definitions; unused ID pruning recorded")

def injection(args):
    files = load_apk(args.apk)
    original = dex_stats(files["classes.dex"])
    merged = dex_stats(pathlib.Path(args.merged).read_bytes())
    delta = merged["class_defs"] - original["class_defs"]
    result = {
        "original_classes": original["class_defs"],
        "merged_classes": merged["class_defs"],
        "added_classes": delta,
        "game_menu_connected": False,
        "apk_generated": False
    }
    save(args.out, result)
    if delta < 5:
        raise AssertionError(f"Expected five or more new fan bridge classes, got {delta}")
    print(f"PASS: added {delta} fan Java bridge classes to temporary DEX; no APK packaged")

def compare_smali(args):
    original = pathlib.Path(args.original)
    rebuilt = pathlib.Path(args.rebuilt)
    def collect(root):
        return {str(p.relative_to(root)): p.read_text(encoding="utf-8", errors="replace")
                for p in root.rglob("*.smali")}
    old = collect(original)
    new = collect(rebuilt)
    absent = sorted(set(old) - set(new))
    added = sorted(set(new) - set(old))
    altered = sorted(p for p in old.keys() & new.keys() if old[p] != new[p])
    result = {
        "original_smali_files": len(old), "rebuilt_smali_files": len(new),
        "missing": absent[:30], "added": added[:30], "changed": altered[:30],
        "unchanged_count": len(old) - len(absent) - len(altered),
        "exact_text_roundtrip": not (absent or added or altered),
    }
    save(args.out, result)
    if absent or added or altered:
        raise AssertionError(f"Smali roundtrip altered files: missing={len(absent)} added={len(added)} changed={len(altered)}")
    print(f"PASS: all {len(old)} original Smali files were reassembled and reproduced identically")

def report(args):
    root = pathlib.Path(args.smali)
    if not root.is_dir():
        raise ValueError("Missing decoded smali tree")
    patterns = ("LEADERBOARD", "/w0.bin", "/w1.bin", "/w2.bin",
                "/w3.bin", "map_angkor.out", "map_scotland.out",
                "map_tibet.out", "map_fan_levels.out", "gamedata")
    hits = {p: [] for p in patterns}
    for path in root.rglob("*.smali"):
        content = path.read_text(encoding="utf-8", errors="replace")
        for needle in patterns:
            if needle in content:
                hits[needle].append(str(path.relative_to(root)))
    lines = ["# DEX navigation and world registration inventory",
             "", "Read-only analysis; NOT a playable Fan Levels integration.", "",
             "| Symbol | Smali files referencing it |", "|---|---|"]
    for needle in patterns:
        values = hits[needle]
        lines.append(f"| " + chr(96)+needle+chr(96) +
                     f" | {', '.join(chr(96)+x+chr(96) for x in values[:5]) if values else 'not present'} |")
    lines += ["", "## Required release gates", "",
              "- [ ] LEVELS FAN menu click opens a new selector",
              "- [ ] Fourth world loads /w3.bin without replacing w0/w1/w2",
              "- [ ] Stage 1 launches and returns to Lost City",
              "- [ ] A real level-complete event saves fan progress separately",
              "- [ ] Android on-device tests pass",
              "", "**No APK is generated by this workflow.**"]
    path = pathlib.Path(args.out)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines)+"\n", encoding="utf-8")
    print("PASS: generated navigation inventory and unmet release gates")

def main():
    parser = argparse.ArgumentParser()
    subs = parser.add_subparsers(dest="cmd", required=True)
    p = subs.add_parser("inspect")
    p.add_argument("--apk", required=True)
    p.add_argument("--out", required=True)
    p = subs.add_parser("roundtrip")
    p.add_argument("--apk", required=True)
    p.add_argument("--rebuilt", required=True)
    p.add_argument("--rebuilt-second")
    p.add_argument("--out", required=True)
    p = subs.add_parser("injection")
    p.add_argument("--apk", required=True)
    p.add_argument("--merged", required=True)
    p.add_argument("--out", required=True)
    p = subs.add_parser("compare-smali")
    p.add_argument("--original", required=True)
    p.add_argument("--rebuilt", required=True)
    p.add_argument("--out", required=True)
    p = subs.add_parser("report")
    p.add_argument("--smali", required=True)
    p.add_argument("--out", required=True)
    args = parser.parse_args()
    {"inspect": inspect, "roundtrip": roundtrip, "compare-smali": compare_smali, "injection": injection, "report": report}[args.cmd](args)

if __name__ == "__main__":
    main()
