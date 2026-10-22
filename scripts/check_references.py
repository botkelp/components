#!/usr/bin/env python3
"""Fail if a manifest's requires/conflictsWith names a component id that does not exist.

A dangling id is silently ignored by the resolver, so it reads as a real rule in
the catalog while enforcing nothing (e.g. `firebase-auth`, `vercel-hosting`).
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    manifests = sorted((ROOT / "components").glob("*/manifest.json"))
    ids = {m.parent.name for m in manifests}
    errors: list[str] = []
    for path in manifests:
        data = json.loads(path.read_text())
        for field in ("requires", "conflictsWith"):
            for ref in data.get(field) or []:
                if ref not in ids:
                    errors.append(f"{path.parent.name}: {field} names unknown component id '{ref}'")
    if errors:
        print(f"{len(errors)} dangling reference(s):")
        for err in errors:
            print(f"  - {err}")
        return 1
    print(f"reference gate passed ({len(ids)} components)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
