#!/usr/bin/env python3
"""
CI-safe Alembic heads check without importing env.py or requiring Alembic CLI.
Parses backend/alembic/versions/*.py to ensure exactly one head exists.
Skips directories starting with _archive.
"""
import ast
import glob
import os
import sys
from typing import Optional, Tuple, Union


def extract_rev_info(path: str) -> Tuple[Optional[str], Optional[Union[str, tuple]]]:
    with open(path, "r", encoding="utf-8") as f:
        tree = ast.parse(f.read(), filename=path)
    revision = None
    down_revision: Optional[Union[str, tuple]] = None
    for node in tree.body:
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id == "revision":
                    if isinstance(node.value, ast.Constant) and isinstance(node.value.value, str):
                        revision = node.value.value
                if isinstance(target, ast.Name) and target.id == "down_revision":
                    v = node.value
                    if isinstance(v, ast.Constant):
                        down_revision = v.value
                    elif isinstance(v, (ast.Tuple, ast.List)):
                        vals = []
                        for elt in v.elts:
                            if isinstance(elt, ast.Constant):
                                vals.append(elt.value)
                        down_revision = tuple(vals)
    return revision, down_revision


def main() -> int:
    repo = os.path.abspath(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
    versions_dir = os.path.join(repo, "backend", "alembic", "versions")
    if not os.path.isdir(versions_dir):
        print(f"NG: versions dir not found: {versions_dir}")
        return 1

    nodes = set()
    parents = set()

    for path in glob.glob(os.path.join(versions_dir, "**", "*.py"), recursive=True):
        rel = os.path.relpath(path, versions_dir)
        if rel.split(os.sep, 1)[0].startswith("_archive"):
            continue
        rev, down = extract_rev_info(path)
        if rev:
            nodes.add(rev)
        if down:
            if isinstance(down, (list, tuple)):
                parents.update([d for d in down if d])
            else:
                parents.add(down)  # type: ignore[arg-type]

    heads = sorted(nodes - parents)
    if len(heads) != 1:
        print(f"NG: Alembic heads != 1 (count={len(heads)})")
        print("nodes:", sorted(nodes))
        print("parents:", sorted(parents))
        print("heads:", heads)
        return 1
    print("OK: Alembic heads = 1", heads[0])
    return 0


if __name__ == "__main__":
    sys.exit(main())

