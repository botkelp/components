#!/usr/bin/env python3
"""Fail if templates changed but version did not."""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def git(*args: str) -> str:
    return subprocess.check_output(["git", *args], cwd=ROOT, text=True).strip()


def main() -> int:
    base = sys.argv[1] if len(sys.argv) > 1 else "origin/main"
    try:
        git("rev-parse", "--verify", base)
    except subprocess.CalledProcessError:
        print(f"skip version bump check (no {base})")
        return 0
    changed = git("diff", "--name-only", f"{base}...HEAD").splitlines()
    by_comp: dict[str, list[str]] = {}
    for path in changed:
        parts = path.split("/")
        if len(parts) < 2 or parts[0] != "components":
            continue
        by_comp.setdefault(parts[1], []).append(path)

    errors: list[str] = []
    for comp, files in sorted(by_comp.items()):
        if not any("/templates/" in f or f.endswith("manifest.json") for f in files):
            continue
        manifest_rel = f"components/{comp}/manifest.json"
        old = subprocess.run(
            ["git", "show", f"{base}:{manifest_rel}"],
            cwd=ROOT,
            text=True,
            capture_output=True,
        )
        new_path = ROOT / manifest_rel
        if not new_path.exists() or old.returncode != 0:
            continue
        new_ver = json.loads(new_path.read_text()).get("version")
        old_ver = json.loads(old.stdout).get("version")
        template_changed = any("/templates/" in f for f in files)
        if template_changed and old_ver == new_ver:
            errors.append(
                f"{comp}: templates changed but version stayed {old_ver}. Bump semver so tpl cache cannot reuse a stale hash."
            )
    if errors:
        print(f"{len(errors)} version gate failure(s):")
        for err in errors:
            print(f"  - {err}")
        return 1
    print("version bump gate passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
