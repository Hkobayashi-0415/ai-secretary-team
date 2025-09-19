#!/usr/bin/env bash
set -euo pipefail

# CI-friendly: do not require Alembic CLI or imports; parse version files directly
python3 - <<'PY'
import os, ast, sys, glob

repo = os.path.abspath(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
versions_dir = os.path.join(repo, 'backend', 'alembic', 'versions')
if not os.path.isdir(versions_dir):
    print(f"NG: versions dir not found: {versions_dir}")
    sys.exit(1)

nodes = set()
parents = set()

def extract_values(path):
    with open(path, 'r', encoding='utf-8') as f:
        tree = ast.parse(f.read(), filename=path)
    rev = None
    down = None
    for node in tree.body:
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id == 'revision':
                    if isinstance(node.value, ast.Constant) and isinstance(node.value.value, str):
                        rev = node.value.value
                if isinstance(target, ast.Name) and target.id == 'down_revision':
                    val = node.value
                    if isinstance(val, ast.Constant):
                        down = val.value
                    elif isinstance(val, (ast.Tuple, ast.List)):
                        vals = []
                        for elt in val.elts:
                            if isinstance(elt, ast.Constant):
                                vals.append(elt.value)
                        down = tuple(vals)
    return rev, down

for path in glob.glob(os.path.join(versions_dir, '**', '*.py'), recursive=True):
    # skip archived or non-active dirs
    rel = os.path.relpath(path, versions_dir)
    if rel.split(os.sep, 1)[0].startswith('_archive'):
        continue
    rev, down = extract_values(path)
    if rev:
        nodes.add(rev)
    if down:
        if isinstance(down, (list, tuple)):
            parents.update([d for d in down if d])
        elif isinstance(down, str):
            parents.add(down)

heads = sorted(nodes - parents)
if len(heads) != 1:
    print(f"NG: Alembic heads != 1 (count={len(heads)})")
    print("nodes:", sorted(nodes))
    print("parents:", sorted(parents))
    print("heads:", heads)
    sys.exit(1)
print("OK: Alembic heads = 1", heads[0])
PY
