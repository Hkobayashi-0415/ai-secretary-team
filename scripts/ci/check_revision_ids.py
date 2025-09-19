#!/usr/bin/env python3
import re, sys, pathlib
bad=[]
for p in pathlib.Path("backend/alembic/versions").glob("*.py"):
    t=p.read_text(encoding="utf-8", errors="ignore")
    m=re.search(r'^\s*revision\s*=\s*["\']([^"\']+)["\']', t, re.M)
    if m and len(m.group(1).strip())>32:
        bad.append((p.name,m.group(1),len(m.group(1))))
if bad:
    print("NG: revision が32文字超：")
    for n,r,l in bad: print(f" - {n}: {r} ({l})")
    sys.exit(1)
print("OK: all revision ids <= 32")
