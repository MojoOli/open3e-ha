---
name: create-pr
description: Push the current branch and open a GitHub pull request for open3e-ha that follows the repo's PR template. Use when the user asks to open/create/make a PR or draft PR, or to put work up for review.
---

# Create a pull request

## 1. Issue

- If no issue has been mentioned for this work, ask the user whether to create one.
- To create one, use the matching template from `.github/ISSUE_TEMPLATE/` (blank issues are disabled):
  - `bug-report.md` for bugs (label `bug`)
  - `entitiy-request.md` for new entities on a device (label `enhancement`)
  - `feature-request.md` for other features (label `enhancement`)

  Fill in the template's sections (body without the frontmatter), set its label, and keep the title short
  (max 70 characters):
  `gh issue create --title "<title>" --label <label> --body-file -`

## 2. Branch

- The PR goes from a branch into `master`. If the changes are still on `master`, create the branch first.
- Name: `issue/<issueId>-<2-3 words>` or, for bug fixes, `fix/<issueId>-<2-3 words>`, e.g.
  `issue/181-anode-current`, `fix/174-water-heater-off`. Without an issue, leave out the ID:
  `issue/<2-3 words>` / `fix/<2-3 words>`.
- `git status` must be clean and `git log master..HEAD` must contain only this change. Unrelated commits or files →
  stop and ask.
- Verify before publishing:
  - `scripts/test` passes.
  - Every new `key` is in both `translations/en.json` and `translations/de.json`.
  - Every `Features.*` reference resolves.

## 3. Push

```
git push -u origin <branch>
```

## 4. Write the body from the template

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

Without an issue, leave "Context / Issue" with a one-line reason for the change.

- Only claim tests that actually ran in this session.

## 5. Create

```
gh pr create --base master --title "<short imperative summary, max 70 characters>" --body-file - [--draft]
```

- Use `--draft` when the user asks for a draft, or when a check is still pending (e.g. live hardware test).
- Afterwards print the PR URL and say what is still open. When a pending check is done, update the body with
  `gh pr edit <n> --body-file -` and mark it ready with `gh pr ready <n>`, but only when the user asks.
