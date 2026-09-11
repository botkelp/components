#!/usr/bin/env python3
"""Render one component's create_file actions into an output directory."""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

EJS_EXPR = re.compile(r"<%=\s*([^%]+)\s*%>")
EJS_TAG = re.compile(r"<%[\s\S]*?%>")


def render(text: str, project: str) -> str:
    def repl(match: re.Match[str]) -> str:
        return project

    text = EJS_EXPR.sub(repl, text)
    return EJS_TAG.sub("", text)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("component")
    parser.add_argument("--out", required=True)
    parser.add_argument("--project", default="ci-app")
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1] / "components" / args.component
    manifest = json.loads((root / "manifest.json").read_text())
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    for action in manifest.get("actions", []):
        if action.get("type") != "create_file":
            continue
        src = root / action["templatePath"]
        dest = out / action["destination"]
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(render(src.read_text(), args.project))
    print(f"rendered {args.component} -> {out}")


if __name__ == "__main__":
    main()
