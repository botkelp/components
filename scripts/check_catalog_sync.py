#!/usr/bin/env python3
"""Fail if catalog.json's component versions drift from the manifests.

`catalog.json` is the published index agents read, and a component's version is
the tpl cache key — `check_version_bump.py` exists precisely so that changed
templates force a new version "so tpl cache cannot reuse a stale hash". That
guarantee is only worth anything if the version agents actually SEE is the
bumped one. Nothing regenerated or checked catalog.json, so a bumped manifest
left the catalog advertising the old version, and the cache-busting the version
gate enforces was silently defeated for exactly the components that changed.

Run with --fix to copy manifest versions into catalog.json.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CATALOG = ROOT / "catalog.json"


def manifest_versions() -> dict[str, str]:
    versions: dict[str, str] = {}
    for path in sorted((ROOT / "components").glob("*/manifest.json")):
        data = json.loads(path.read_text())
        versions[data["id"]] = data["version"]
    return versions


def main() -> int:
    fix = "--fix" in sys.argv[1:]
    wanted = manifest_versions()
    catalog_text = CATALOG.read_text()
    catalog = json.loads(catalog_text)

    drift: list[tuple[str, str, str]] = []
    for entry in catalog:
        cid = entry.get("id")
        if cid not in wanted:
            continue
        if entry.get("version") != wanted[cid]:
            drift.append((cid, entry.get("version"), wanted[cid]))

    missing = sorted(set(wanted) - {e.get("id") for e in catalog})

    if not drift and not missing:
        print(f"catalog sync gate passed ({len(wanted)} components)")
        return 0

    if fix and drift:
        # Rewrite only the drifting version values, so the catalog's existing
        # formatting (and everything else in it) is left byte-for-byte alone.
        for cid, old, new in drift:
            pattern = re.compile(
                r'("id"\s*:\s*"%s"\s*,\s*"name"\s*:\s*"[^"]*"\s*,\s*"version"\s*:\s*)"%s"'
                % (re.escape(cid), re.escape(old))
            )
            catalog_text, n = pattern.subn(r'\1"%s"' % new, catalog_text, count=1)
            if n != 1:
                print(f"could not rewrite {cid} in catalog.json", file=sys.stderr)
                return 2
            print(f"fixed {cid}: {old} -> {new}")
        CATALOG.write_text(catalog_text)
        drift = []

    for cid, old, new in drift:
        print(f"  - {cid}: catalog says {old}, manifest says {new}")
    for cid in missing:
        print(f"  - {cid}: in components/ but absent from catalog.json")

    if drift or missing:
        print(
            f"{len(drift) + len(missing)} catalog drift failure(s). "
            "Run: python scripts/check_catalog_sync.py --fix"
        )
        return 1

    print("catalog sync gate passed after --fix")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
