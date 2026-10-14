---
name: create-pr
description: Push the current branch and open a GitHub pull request for open3e-ha that follows the repo's PR template. Use when the user asks to open/create/make a PR or draft PR, or to put work up for review.
---

# Create a pull request

## 1. Check the branch

- Never open a PR from `master`. If the work is on `master`, ask before creating a branch
  (naming: `feat/<topic>-<issue>`, `fix/<topic>-<issue>`).
- `git status` must be clean and `git log master..HEAD` must contain only this change. Unrelated commits or files →
  stop and ask.
- Verify before publishing:
  - `scripts/test` passes.
  - Every new `key` is in both `translations/en.json` and `translations/de.json`.
  - Every `Features.*` reference resolves.

## 2. Push

```
git push -u origin <branch>
```

If the push fails on auth, tell the user rather than switching remotes or protocols.

## 3. Write the body from the template

Always read `.github/PULL_REQUEST_TEMPLATE.md` first and use exactly its sections. Do not add extra top-level sections.

```markdown
## Description

<What the PR adds/changes, grouped per DID or feature: entity keys, units, device class, refresh interval,
entity category, enabled-by-default or not, required device/capabilities. Call out deliberate choices
(e.g. a `rw` DID exposed read-only, sensors disabled by default).>

Tested: <what was actually run and what it showed — unit tests, sample payloads from the issue, live check.
Name anything still pending, e.g. "Live check against a real Vitocal still pending.">

## Context / Issue

Resolves #<issue>
```

- No "Generated with Claude Code" footer.
- Only claim tests that actually ran in this session.
- Write it in English, even if the issue is in German.

## 4. Create

```
gh pr create --base master --title "<imperative summary, no issue number>" --body-file - [--draft]
```

- Use `--draft` when the user asks for a draft, or when a check is still pending (e.g. live hardware test).
- Afterwards print the PR URL and say what is still open. When a pending check is done, update the body with
  `gh pr edit <n> --body-file -` and mark it ready with `gh pr ready <n>`, but only when the user asks.
