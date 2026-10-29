# Component Freshness and Upgrade Verification

This repository includes an automated, evidence-based freshness audit.

## How it works

`scripts/check_freshness.py`:

1. Discovers every directory under `components/` that contains a `manifest.json`.
2. For each component:
   - Parses `sources` of type `github-releases` and queries the GitHub Releases API for the latest non-draft release.
   - Extracts pinned package versions from `actions` (`json_merge`) and `templates/package.json.ejs`.
   - Queries the npm registry for the latest version of those packages.
3. Compares installed/pinned versions against upstream using packaging.version.
4. Classifies each component as:
   - **current** — at least one successful matching check, and no failed checks.
   - **outdated** — at least one check shows a newer stable upstream version.
   - **unsupported** — repository archived or package deprecated.
   - **unverified** — no checkable sources/pins, parse errors, or failed source checks.
5. Records full evidence (timestamp, source URL, method, error if any) in `reports/freshness.json`.
6. Produces a human summary in `reports/SUMMARY.md` and an upgrade queue sorted by priority (security/breaking signals preferred over pure age).

## Rules enforced

- A component is never marked current without verifiable upstream evidence.
- A failed source check is never counted as current.
- Missing metadata and low coverage are visible in the counts.
- Compatibility assessment (breaking changes, framework ranges) is separate from pure version freshness and is not auto-applied here.
- Upgrades are queued only; nothing is automatically merged or overwritten.

## Running locally

```bash
pip install packaging
python scripts/check_freshness.py
```

Reports are written to `reports/`.

## CI

`.github/workflows/freshness.yml` runs:

- On a weekly schedule
- On demand (`workflow_dispatch`)
- On pull requests that touch manifests or the checker

Artifacts are uploaded for inspection. The workflow does not fail the PR solely on outdated components; it surfaces the report so reviewers can act.

## Tests

Unit tests for version comparison, URL parsing, and pin extraction live in `tests/test_freshness.py` and require no network.

Integration checks against live upstreams are performed by the audit itself; their outcomes are recorded as evidence, not assumed.

## Compatibility

Framework compatibility ranges remain in each `manifest.json` `compatibility` object. An upgrade that would violate those ranges must be evaluated separately before any pin change is accepted.
