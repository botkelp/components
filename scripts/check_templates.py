#!/usr/bin/env python3
"""Fail if generated templates would not parse as the destination format."""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1] / "components"
BLOCK = re.compile(r"^/\*\*")

STRICT_SUFFIX = (
    ".json",
    ".json.ejs",
    "package.json.ejs",
    "composer.json.ejs",
    "nest-cli.json.ejs",
    "angular.json.ejs",
    "tsconfig.json.ejs",
    "tsconfig.app.json.ejs",
    "tsconfig.spec.json.ejs",
    "tsconfig.build.json.ejs",
    "tsconfig.node.json.ejs",
    ".eslintrc.json.ejs",
    ".prettierrc.ejs",
    ".browserslistrc.ejs",
    "requirements.txt.ejs",
    "requirements-dev.txt.ejs",
    ".csproj.ejs",
    "composer.lock.ejs",
)


def dest_is_strict(template_path: str, destination: str) -> bool:
    blob = f"{template_path} {destination}".lower()
    if destination.endswith(".csproj") or "<%= " in destination:
        return True
    return any(blob.endswith(s) or destination.endswith(s.replace(".ejs", "")) for s in STRICT_SUFFIX)


def main() -> int:
    errors: list[str] = []
    if not ROOT.is_dir():
        print("components/ missing", file=sys.stderr)
        return 2

    for manifest_path in sorted(ROOT.glob("*/manifest.json")):
        comp = manifest_path.parent.name
        try:
            manifest = json.loads(manifest_path.read_text())
        except json.JSONDecodeError as exc:
            errors.append(f"{manifest_path}: invalid JSON ({exc})")
            continue
        if not manifest.get("version"):
            errors.append(f"{manifest_path}: missing version")
        for action in manifest.get("actions", []):
            if action.get("type") != "create_file":
                continue
            dest = action.get("destination") or ""
            tmpl = action.get("templatePath") or ""
            if "<%=" in dest or "<%" in dest:
                errors.append(f"{comp}: destination still has EJS: {dest}")
            src = manifest_path.parent / tmpl
            if not src.is_file():
                errors.append(f"{comp}: missing template {tmpl}")
                continue
            text = src.read_text(encoding="utf-8", errors="replace")
            if dest_is_strict(tmpl, dest) and BLOCK.match(text.lstrip("\ufeff")):
                errors.append(f"{comp}: comment header on data file {tmpl} -> {dest}")

    if errors:
        print(f"{len(errors)} template gate failure(s):")
        for err in errors:
            print(f"  - {err}")
        return 1
    print("template gates passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
