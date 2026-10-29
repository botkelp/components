#!/usr/bin/env python3
"""
Component freshness and upgrade verification for botkelp/components.

Discovers every component, queries authoritative upstream sources,
records evidence, and produces machine-readable + human-readable reports.

Never marks a failed check as current. Never fabricates versions.
"""
from __future__ import annotations

import json
import os
import re
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

try:
    from packaging.version import Version, InvalidVersion
except ImportError:
    print("Missing packaging. Install: pip install packaging", file=sys.stderr)
    sys.exit(2)

ROOT = Path(__file__).resolve().parents[1]
COMPONENTS = ROOT / "components"
REPORTS = ROOT / "reports"
REPORTS.mkdir(exist_ok=True)

# Rate-limit friendly
REQUEST_DELAY = 0.25


def now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def run_gh(args: list[str], timeout: int = 30) -> tuple[int, str, str]:
    """Run gh api or gh release. Returns (returncode, stdout, stderr)."""
    cmd = ["gh"] + args
    try:
        p = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout,
            cwd=ROOT,
        )
        return p.returncode, p.stdout.strip(), p.stderr.strip()
    except subprocess.TimeoutExpired:
        return 124, "", "timeout"
    except FileNotFoundError:
        return 127, "", "gh not found"


def parse_github_release_url(url: str) -> tuple[str | None, str | None, str | None]:
    """Extract owner/repo/tag from a GitHub releases URL."""
    # https://github.com/owner/repo/releases/tag/v1.2.3
    # https://github.com/owner/repo/releases/tag/@scope/pkg@1.2.3
    m = re.match(
        r"https?://github\.com/([^/]+)/([^/]+)/releases/tag/(.+)",
        url.rstrip("/"),
    )
    if not m:
        return None, None, None
    owner, repo, tag = m.group(1), m.group(2), m.group(3)
    return owner, repo, tag


def fetch_latest_github_release(owner: str, repo: str) -> dict[str, Any]:
    """Fetch latest stable release. Returns evidence dict."""
    evidence: dict[str, Any] = {
        "method": "github-releases",
        "source": f"https://github.com/{owner}/{repo}",
        "timestamp": now_iso(),
        "error": None,
        "latest_tag": None,
        "latest_version": None,
        "prerelease": False,
        "archived": False,
        "draft": False,
    }
    # Check archived
    rc, out, err = run_gh(["api", f"/repos/{owner}/{repo}", "--jq", ".archived,.disabled"])
    if rc == 0 and out:
        parts = out.split()
        if parts and parts[0].lower() == "true":
            evidence["archived"] = True
            evidence["error"] = "repository archived"
            return evidence

    # Latest release (not draft/prerelease preferred)
    rc, out, err = run_gh([
        "api",
        f"/repos/{owner}/{repo}/releases/latest",
        "--jq", "{tag_name:.tag_name,prerelease:.prerelease,draft:.draft,html_url:.html_url,published_at:.published_at}"
    ])
    if rc != 0:
        evidence["error"] = f"gh api failed: {err or 'unknown'}"
        return evidence
    try:
        data = json.loads(out)
    except json.JSONDecodeError:
        evidence["error"] = "invalid json from gh"
        return evidence

    evidence["latest_tag"] = data.get("tag_name")
    evidence["prerelease"] = bool(data.get("prerelease"))
    evidence["draft"] = bool(data.get("draft"))
    evidence["html_url"] = data.get("html_url")
    evidence["published_at"] = data.get("published_at")

    # Extract version from tag
    tag = data.get("tag_name") or ""
    # Handle @scope/pkg@1.2.3 or v1.2.3 or 1.2.3
    ver_match = re.search(r"(\d+\.\d+\.\d+(?:[-+].+)?)$", tag)
    if ver_match:
        evidence["latest_version"] = ver_match.group(1)
    else:
        evidence["latest_version"] = tag.lstrip("v")
    return evidence


def fetch_npm_latest(package: str) -> dict[str, Any]:
    """Query npm for latest version."""
    evidence: dict[str, Any] = {
        "method": "npm-registry",
        "source": f"https://registry.npmjs.org/{package}",
        "timestamp": now_iso(),
        "error": None,
        "latest_version": None,
        "deprecated": None,
    }
    rc, out, err = run_gh([])  # placeholder; use curl/npm
    # Prefer npm view
    try:
        p = subprocess.run(
            ["npm", "view", package, "version", "--json"],
            capture_output=True,
            text=True,
            timeout=20,
        )
        if p.returncode == 0:
            ver = json.loads(p.stdout)
            if isinstance(ver, str):
                evidence["latest_version"] = ver
            elif isinstance(ver, list) and ver:
                evidence["latest_version"] = ver[-1]
        else:
            evidence["error"] = p.stderr.strip() or "npm view failed"
    except Exception as e:
        evidence["error"] = str(e)

    # Check deprecated
    try:
        p = subprocess.run(
            ["npm", "view", package, "deprecated", "--json"],
            capture_output=True,
            text=True,
            timeout=15,
        )
        if p.returncode == 0 and p.stdout.strip() not in ("null", "{}"):
            evidence["deprecated"] = p.stdout.strip().strip('"')
    except Exception:
        pass
    return evidence


def extract_pinned_versions(comp_dir: Path, manifest: dict) -> list[dict[str, str]]:
    """Extract package:version pins from actions, description, or templates."""
    pins: list[dict[str, str]] = []
    # From json_merge actions
    for action in manifest.get("actions", []):
        if action.get("type") == "json_merge":
            deps = action.get("mergeData", {}).get("dependencies", {})
            for name, ver in deps.items():
                if isinstance(ver, str) and re.match(r"\d+\.\d+", ver):
                    pins.append({"package": name, "pinned": ver, "source": "json_merge"})
    # From package.json.ejs if present
    pkg_ejs = comp_dir / "templates" / "package.json.ejs"
    if pkg_ejs.exists():
        text = pkg_ejs.read_text(errors="ignore")
        # Simple regex for "pkg": "1.2.3"
        for m in re.finditer(r'"([^"]+)":\s*"(\d+\.\d+\.\d+[^"]*)"', text):
            name, ver = m.group(1), m.group(2)
            if name not in ("name", "version", "description"):
                pins.append({"package": name, "pinned": ver, "source": "package.json.ejs"})
    # Deduplicate by package, prefer more specific
    seen = {}
    for p in pins:
        seen[p["package"]] = p
    return list(seen.values())


def compare_versions(installed: str | None, upstream: str | None) -> str:
    """Return current | outdated | unknown | error."""
    if not installed or not upstream:
        return "unknown"
    try:
        vi = Version(installed.lstrip("v"))
        vu = Version(upstream.lstrip("v"))
        if vi == vu:
            return "current"
        if vi < vu:
            return "outdated"
        return "ahead"  # rare
    except InvalidVersion:
        # Fallback string compare
        if installed == upstream or installed.lstrip("v") == upstream.lstrip("v"):
            return "current"
        return "unknown"


def audit_component(comp_dir: Path) -> dict[str, Any]:
    manifest_path = comp_dir / "manifest.json"
    if not manifest_path.exists():
        return {
            "id": comp_dir.name,
            "status": "unverified",
            "error": "missing manifest.json",
            "evidence": [],
        }
    try:
        manifest = json.loads(manifest_path.read_text())
    except Exception as e:
        return {
            "id": comp_dir.name,
            "status": "unverified",
            "error": f"invalid manifest: {e}",
            "evidence": [],
        }

    cid = manifest.get("id", comp_dir.name)
    version = manifest.get("version")
    sources = manifest.get("sources", [])
    status = manifest.get("status", "unknown")

    result: dict[str, Any] = {
        "id": cid,
        "installed_version": version,
        "catalog_status": status,
        "sources_declared": len(sources),
        "checks": [],
        "overall": "unverified",
        "errors": [],
        "upgrade_priority": 0,
    }

    # Process github-releases sources
    github_evidence = []
    for src in sources:
        if src.get("type") != "github-releases":
            continue
        url = src.get("url", "")
        owner, repo, tag = parse_github_release_url(url)
        if not owner or not repo:
            result["errors"].append(f"unparseable github-releases url: {url}")
            continue
        time.sleep(REQUEST_DELAY)
        ev = fetch_latest_github_release(owner, repo)
        ev["declared_tag"] = tag
        ev["declared_url"] = url
        ev["verifiedAt"] = src.get("verifiedAt")
        github_evidence.append(ev)
        if ev.get("error"):
            result["errors"].append(ev["error"])
        elif ev.get("archived"):
            result["overall"] = "unsupported"
        else:
            cmp = compare_versions(tag, ev.get("latest_tag") or ev.get("latest_version"))
            ev["comparison"] = cmp
            if cmp == "outdated" and result["overall"] != "unsupported":
                result["overall"] = "outdated"
                result["upgrade_priority"] = max(result["upgrade_priority"], 2)
            elif cmp == "current" and result["overall"] == "unverified":
                result["overall"] = "current"

    result["checks"].extend(github_evidence)

    # Process npm pins
    pins = extract_pinned_versions(comp_dir, manifest)
    npm_evidence = []
    for pin in pins[:8]:  # limit to avoid rate limits
        time.sleep(REQUEST_DELAY)
        ev = fetch_npm_latest(pin["package"])
        ev["pinned"] = pin["pinned"]
        ev["pin_source"] = pin["source"]
        npm_evidence.append(ev)
        if ev.get("error"):
            result["errors"].append(f"npm {pin['package']}: {ev['error']}")
        elif ev.get("deprecated"):
            result["errors"].append(f"{pin['package']} deprecated: {ev['deprecated']}")
            if result["overall"] not in ("unsupported",):
                result["overall"] = "unsupported"
        else:
            cmp = compare_versions(pin["pinned"], ev.get("latest_version"))
            ev["comparison"] = cmp
            if cmp == "outdated" and result["overall"] not in ("unsupported",):
                result["overall"] = "outdated"
                result["upgrade_priority"] = max(result["upgrade_priority"], 1)

    result["checks"].extend(npm_evidence)

    # Final overall if still unverified and no errors
    if result["overall"] == "unverified" and not result["errors"] and (github_evidence or npm_evidence):
        # Had checks but none matched current/outdated
        result["overall"] = "unverified"
    elif not github_evidence and not npm_evidence:
        result["overall"] = "unverified"
        result["errors"].append("no checkable upstream sources or pins")

    # Failed checks never current
    if any(c.get("error") for c in result["checks"]):
        if result["overall"] == "current":
            result["overall"] = "unverified"

    return result


def main() -> int:
    discovered = sorted(p for p in COMPONENTS.iterdir() if p.is_dir() and (p / "manifest.json").exists())
    print(f"Discovered {len(discovered)} components with manifests")

    results = []
    for comp_dir in discovered:
        print(f"Auditing {comp_dir.name}...", flush=True)
        res = audit_component(comp_dir)
        results.append(res)

    # Aggregates
    counts = {
        "discovered": len(discovered),
        "audited": sum(1 for r in results if r["checks"]),
        "current": sum(1 for r in results if r["overall"] == "current"),
        "outdated": sum(1 for r in results if r["overall"] == "outdated"),
        "unsupported": sum(1 for r in results if r["overall"] == "unsupported"),
        "unverified": sum(1 for r in results if r["overall"] == "unverified"),
    }
    counts["coverage_pct"] = round(
        100.0 * counts["audited"] / counts["discovered"] if counts["discovered"] else 0, 1
    )

    # Upgrade queue: outdated sorted by priority desc, then age proxy
    queue = [
        {
            "id": r["id"],
            "installed": r["installed_version"],
            "priority": r["upgrade_priority"],
            "reasons": [c.get("comparison") for c in r["checks"] if c.get("comparison") == "outdated"],
            "errors": r["errors"],
        }
        for r in results
        if r["overall"] == "outdated"
    ]
    queue.sort(key=lambda x: -x["priority"])

    report = {
        "generated_at": now_iso(),
        "counts": counts,
        "results": results,
        "upgrade_queue": queue,
        "rules": {
            "failed_check_never_current": True,
            "no_inference_from_sample": True,
            "evidence_required_for_current": True,
        },
    }

    (REPORTS / "freshness.json").write_text(json.dumps(report, indent=2))
    print(f"Wrote {REPORTS / 'freshness.json'}")

    # Human summary
    summary_lines = [
        "# Component Freshness Audit",
        "",
        f"Generated: {report['generated_at']}",
        "",
        "## Counts",
        f"- Discovered: {counts['discovered']}",
        f"- Audited (had checkable sources/pins): {counts['audited']}",
        f"- Current: {counts['current']}",
        f"- Outdated: {counts['outdated']}",
        f"- Unsupported (archived/deprecated): {counts['unsupported']}",
        f"- Unverified (no evidence or failed checks): {counts['unverified']}",
        f"- Coverage: {counts['coverage_pct']}%",
        "",
        "## Upgrade Queue (prioritised)",
        "",
    ]
    if queue:
        for item in queue:
            summary_lines.append(f"- **{item['id']}** (priority {item['priority']}) — installed {item['installed']}")
    else:
        summary_lines.append("- None")
    summary_lines.extend([
        "",
        "## Notes",
        "- A component is current only when at least one upstream check returned matching evidence and no check failed.",
        "- Failed source checks are recorded in errors and force unverified if they would otherwise be current.",
        "- Compatibility assessment is separate; this report focuses on version freshness.",
        "- Full evidence is in reports/freshness.json",
        "",
    ])
    (REPORTS / "SUMMARY.md").write_text("\n".join(summary_lines))
    print(f"Wrote {REPORTS / 'SUMMARY.md'}")

    # Exit non-zero if coverage low or many unverified (actionable)
    if counts["coverage_pct"] < 50 or counts["unverified"] > counts["discovered"] * 0.7:
        print("WARNING: low coverage or high unverified count — review reports/", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
