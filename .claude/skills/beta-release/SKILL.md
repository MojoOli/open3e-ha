---
name: beta-release
description: Publish a beta pre-release (vX.Y.Z-betaN) of open3e-ha on GitHub from the current master, with hand-written release notes grouped per device. Use when the user asks to make/cut/publish a beta, pre-release or test build.
---

# Beta release

Betas are GitHub **pre-releases** tagged on `master`. They are created by hand with `gh release create`, not with
the `Release` workflow (`.github/workflows/release.yml`), which creates stable releases with auto-generated notes.
`manifest.json` is **not** bumped for betas. It stays at the last stable version until the stable release.

## 1. Next tag

```
git fetch -q --tags origin
gh release list --limit 5
```

- Latest release is a beta `vX.Y.Z-betaN` → next is `vX.Y.Z-beta(N+1)`.
- Latest release is stable `vX.Y.Z` → next is `vX.Y.(Z+1)-beta1`.
- Previous tag = the latest release (beta or stable). The notes cover everything since then.

## 2. Check master

- All wanted PRs are merged: `git log --oneline <previous tag>..origin/master`. Anything unexpected → ask.
- CI on master is green: `gh run list --branch master --limit 3`. A failing run → stop and ask.

## 3. Collect changes

```
gh pr list --state merged --limit 30 --json number,title,mergedAt,author
gh release view <previous tag> --json body -q .body
```

- Take the PRs merged after the previous tag (dependabot and CI-only PRs are left out of the notes).
- For each PR, read the diff (`gh pr diff <n>`) and the new `en.json` names
  (`git diff <previous tag> origin/master -- custom_components/open3e/translations/en.json`) so that entries use the
  entity names users see in HA.
- Compare with the previous beta's notes. A feature from an earlier beta that was reverted since then gets a
  `Removed:` entry with a short reason.

## 4. Write the notes

Same format as the earlier betas: one section per device (`Vitocal`, `Vitodens`, `Vitoair`, `Vitocharge`, plus
`General` if needed), only for devices with changes. New entities are listed by name. Add the adjustable range or
"(adjustable)" for number/select entities, and "disabled by default" where it applies. Fixes start with
`Fixed:`, removals with `Removed:`.

```markdown
## What's Changed

### Vitocal
- Heating circuit 2 buffer setpoint offset (DID 934, adjustable 0–20 K)
- Removed: Primary pump speed (DID 1100) from beta2, it can't be written via Open3e

### Vitoair
- Quick mode select is back (intensive / reduced noise, 60 min). Needs Open3e 0.7.10 and a re-run of depict
- Fixed: Frost protection no longer always shows "on"

> **Vitoair users:** <only if users must do something, e.g. update Open3e / re-run depict, or a feature needs testers>

**Full Changelog**: https://github.com/MojoOli/open3e-ha/compare/<previous tag>...<new tag>
```

- Add a `>` note only when users have to act (Open3e version, depict re-run), or when a feature still needs testing
  on real hardware. Name the issue where feedback should go.
- Write the notes to a file in the scratchpad.

## 5. Confirm and publish

Publishing is visible to every user on the beta channel. Show the user the tag, the target commit and the notes, and
publish only after they confirm, unless they already said to go ahead.

```
gh release create <new tag> --target "$(git rev-parse origin/master)" --prerelease \
  --title <new tag> --notes-file <notes file>
git fetch -q --tags && git rev-parse <new tag>^{commit}
```

- `--target` needs the **full** SHA. A short SHA fails with `tag_name is not a valid tag`.
- Check that the tag points at the intended commit, then give the user the release URL.
- Suggest a comment on the issues whose testers should try the beta. Post it only if the user asks.
