# BotKelp components

Public source for the **individual components** BotKelp actually uses.

You can browse, copy, and reuse these files. That is the point of this repository.

## What we are providing

Each folder under [`components/`](components/) is one component:

- `manifest.json` — id, version, `requires` / `provides`, npm packages, and the generator actions
- `templates/` — the files the generator applies (EJS templates; most are plain source with no templating)

The same list is in [`CATALOG.md`](CATALOG.md) and [`catalog.json`](catalog.json).

This repository is the **source of truth** for BotKelp's component catalog. The MCP generator and website load these files (not a private copy). It is not a demo and not a cleaned-up excerpt.

## What we are not providing

- **Not a complete application.** Cloning this repo will not give you a running site.
- **Not assembled / generated project builds.** Combinations produced by `generate_scaffold` or `get_scaffold_template` (a full Next.js app with several components already wired together) are **not published here**.
- **Not the BotKelp service.** The MCP server, billing, accounts, and generation engine live elsewhere and are not in this repository.

If you want a generated project, use the BotKelp MCP tools with an account key. If you want to copy a navbar, a Supabase client, or Tailwind config, use this repo.

## How to copy a component

1. Open `components/<id>/`.
2. Read `manifest.json` for npm packages and env vars.
3. Copy the files under `templates/` into your app at the `destination` paths listed in the manifest.
4. Install the listed `dependencies` / `devDependencies`.
5. Respect the licences of any upstream library the component wraps (Next.js, Tailwind, shadcn/ui, Supabase, and so on). Those remain their own.

`nextjs-base` is the **base component** the others sit on. It is still one component, not a product app we ship as a complete build.

## Licence

BotKelp-authored files are under the [BotKelp Limited Use Licence](LICENSE).

INTLEACHT RESEARCH LIMITED trading as BotKelp is named on every file. You may copy individual component source into your own projects. You may not present this catalog or the generator as your own product, and you may not strip operator attribution from files as published here.

Third-party projects named in a component keep their own licences. Copying a component does not re-licence Next.js, Tailwind, Prisma, or anything else.

## Site

The registry on the BotKelp website shows the same components, with copyable file contents.
repo: https://github.com/botkelp/components
