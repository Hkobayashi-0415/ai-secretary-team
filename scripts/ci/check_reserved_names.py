#!/usr/bin/env python3
import sys, pathlib
reserved={ "con","prn","aux","nul" }|{f"com{i}" for i in range(1,10)}|{f"lpt{i}" for i in range(1,10)}
bad=[]
for p in pathlib.Path(".").rglob("*"):
    if p.is_file() and p.name.lower() in reserved:
        bad.append(str(p))
if bad:
    print("NG: Windows reserved file names detected:")
    print("\n".join(bad)); sys.exit(1)
print("OK: no reserved names")
