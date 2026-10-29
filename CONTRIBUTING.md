# Component change gates

`tpl-*` repos are a cache keyed by `id@version`. Do not patch them by hand.

1. Edit `components/<id>/templates` and `manifest.json`.
2. Bump `version` whenever templates change.
3. Do not put `/**` headers on JSON, `package.json`, `composer.json`, `requirements.txt`, `.browserslistrc`, or `.csproj`.
4. Destination paths must be rendered names — no `<%= projectName %>` in the filename.
5. PR CI runs `scripts/check_templates.py`, `scripts/check_version_bump.py`, then render+build for each base.

Source comments belong in `.ts` / `.vue` / `.py` / `.cs`, not in machine-parsed files.

## Freshness audit

See [docs/FRESHNESS.md](docs/FRESHNESS.md). Run `python scripts/check_freshness.py` before proposing dependency pin upgrades.

## Freshness audit

See [docs/FRESHNESS.md](docs/FRESHNESS.md). Run `python scripts/check_freshness.py` before proposing dependency pin upgrades. Generated evidence lives in reports/ (gitignored for routine runs; a sample is committed with the introduction of the checker).
