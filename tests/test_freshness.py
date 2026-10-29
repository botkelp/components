#!/usr/bin/env python3
"""Unit tests for freshness checker logic. No network required for core comparisons."""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from check_freshness import (
    compare_versions,
    parse_github_release_url,
    extract_pinned_versions,
)

def test_compare_versions():
    assert compare_versions("1.2.3", "1.2.3") == "current"
    assert compare_versions("1.2.3", "1.2.4") == "outdated"
    assert compare_versions("2.0.0", "1.9.9") == "ahead"
    assert compare_versions("v1.0.0", "1.0.0") == "current"
    assert compare_versions(None, "1.0.0") == "unknown"
    assert compare_versions("1.0.0", None) == "unknown"
    assert compare_versions("not-a-version", "1.0.0") == "unknown"
    print("compare_versions: ok")

def test_parse_github_url():
    o, r, t = parse_github_release_url("https://github.com/vercel/next.js/releases/tag/v16.4.3")
    assert o == "vercel" and r == "next.js" and t == "v16.4.3"
    o, r, t = parse_github_release_url("https://github.com/clerk/javascript/releases/tag/@clerk/nextjs@7.9.22")
    assert o == "clerk" and r == "javascript" and "@clerk/nextjs@7.9.22" in t
    o, r, t = parse_github_release_url("https://example.com/not-github")
    assert o is None
    print("parse_github_url: ok")

def test_extract_pins():
    # Minimal mock
    class FakeDir:
        def __truediv__(self, other):
            return Path("/nonexistent")
    pins = extract_pinned_versions(Path("/tmp"), {
        "actions": [
            {"type": "json_merge", "mergeData": {"dependencies": {"stripe": "22.6.1", "react": "19.0.0"}}}
        ]
    })
    assert any(p["package"] == "stripe" and p["pinned"] == "22.6.1" for p in pins)
    print("extract_pins: ok")

def test_missing_metadata_handling():
    # Simulate audit_component on missing would be integration; here just ensure helpers don't crash
    assert compare_versions("", "1.0") == "unknown"
    print("missing metadata paths: ok")

if __name__ == "__main__":
    test_compare_versions()
    test_parse_github_url()
    test_extract_pins()
    test_missing_metadata_handling()
    print("All unit tests passed")
