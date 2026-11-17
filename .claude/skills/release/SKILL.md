---
name: release
description: Publish a stable release (vX.Y.Z) of open3e-ha - bump the version in manifest.json, push the bump to master, and create the GitHub release with hand-written notes grouped per device covering all betas since the last stable release. Use when the user asks to make/cut/publish a (stable/final/full) release. For betas use /beta-release.
---

# Stable release

A stable release is a version-bump commit on `master` plus a GitHub release tagged on that commit. HACS installs
the tag, and HA shows the version from `manifest.json`, so the two must match. The `Release` workflow
(`.github/workflows/release.yml`) is not used: it doesn't bump `manifest.json` and only lists PR titles.

## 1. Version

```
git fetch -q --tags origin
gh release list --limit 10
grep '"version"' custom_components/open3e/manifest.json
```

- Previous stable = the latest release without `-beta`. It should match `manifest.json` on `master`.
- New version = `X.Y.Z` of the latest beta (e.g. `v1.0.20-beta3` → `1.0.20`). Without betas since the last stable
  release: patch + 1. Ask the user if they want a minor or major bump instead.

## 2. Check master

- `git status` is clean. Switch to `master` and run `git pull --ff-only origin master`.
- `git log --oneline <latest tag>..origin/master` shows what is new since the last beta. Anything unexpected → ask.
- CI on master is green: `gh run list --branch master --limit 3`. A failing run → stop and ask.
- `scripts/test` passes.

## 3. Release notes

The notes cover everything since the **previous stable** release, i.e. all betas plus anything merged after the
last beta.

```
gh release list --limit 10                   # betas since the previous stable
gh release view <beta tag> --json body -q .body
git log --oneline <previous stable>..origin/master
```

- Start from the beta notes and merge them per device. Then add PRs merged after the last beta (read their diffs and
  the new `en.json` names, as in `/beta-release`). Dependabot and CI-only PRs are left out.
- Entries that cancel each other out across betas are dropped. Something added in beta2 and reverted in beta3
  is not mentioned at all, because stable users never had it.
- A fix for a bug that only existed in an earlier beta is dropped too.
- Use the format of the earlier stable releases (see `gh release view v1.0.19`): no "What's Changed" heading, one
  `## <Device>` section per device, `## All devices` for general changes, and the issue number after each entry.
  Mark changes that need user attention (renamed or changed entities, a new Open3e requirement) with ⚠️.

```markdown
## Vitocal
- Heating circuit 2 buffer setpoint offset (#196)

## Vitoair
- Quick mode select is back (#63)
- ⚠️ Recovered energy, bypass level and the quick mode select need Open3e 0.7.10, then a re-run of depict (#63)

## All devices
- Fixed German translations

**Full Changelog**: https://github.com/MojoOli/open3e-ha/compare/<previous stable>...<new tag>
```

- If a feature needs a newer Open3e, check that the Open3e version is actually released, i.e. on Open3e's
  `master` and not only on `develop`. Otherwise say so in the notes.
- Write the notes to a file in the scratchpad.

## 4. Confirm

Show the user the new version, the notes and the planned commit, and wait for their go-ahead. Pushing to `master`
and publishing a stable release reaches every HACS user, so don't do it on a general "make a release" without
showing this first.

## 5. Bump and push

Change only the `"version"` value in `custom_components/open3e/manifest.json` (no reformatting), then:

```
git commit -am "Release v<X.Y.Z>"
git push origin master
```

- `master` is protected (PR review required, force pushes disabled). Admins can push directly, so a plain push
  works for the repo owner. **Never force-push** `master`: it isn't needed for a version bump and would rewrite
  the history users' installs are based on.
- If the push is rejected (non-fast-forward or permissions), stop and tell the user. Don't retry with `--force`.
  The alternative is a PR with just the version bump.

## 6. Publish

```
gh release create v<X.Y.Z> --target "$(git rev-parse HEAD)" --latest \
  --title v<X.Y.Z> --notes-file <notes file>
git fetch -q --tags && git rev-parse v<X.Y.Z>^{commit}
git show v<X.Y.Z>:custom_components/open3e/manifest.json | grep '"version"'
```

- `--target` needs the **full** SHA. A short SHA fails with `tag_name is not a valid tag`.
- The tag must point at the bump commit, and `manifest.json` in it must show the new version.
- Give the user the release URL. Suggest a comment on issues that this release resolves, and post it only if the
  user asks.
