#!/usr/bin/env python3
import re, sys, pathlib, collections
names=collections.defaultdict(list)
for py in pathlib.Path("backend/app/models").rglob("*.py"):
    t=py.read_text(encoding="utf-8", errors="ignore")
    for m in re.finditer(r'__tablename__\s*=\s*["\']([^"\']+)["\']', t):
        names[m.group(1)].append(str(py))
dupes={k:v for k,v in names.items() if len(v)>1}
if dupes:
    print("NG: duplicate __tablename__ detected:")
    for k,v in dupes.items():
        print(f" - {k}:"); [print(f"    - {p}") for p in v]
    sys.exit(1)
print("OK: no duplicate __tablename__")
