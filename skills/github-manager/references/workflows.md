# GitHub Manager workflows

## Repository and publishing

Inspect first:
```bash
git remote -v
git status --short --branch
gh repo view --json nameWithOwner,visibility,defaultBranchRef
```
Create or publish only when requested:
```bash
gh repo create OWNER/REPO --public --source=. --remote=origin --push
git add <files>
git commit -m "<message>"
git push -u origin HEAD
```
Use `gh api` for fields not exposed by `gh repo`; confirm the target owner and visibility before mutation.

## README, Issues, and Pull Requests

Use `gh issue create/list/view`, `gh pr create/list/view/merge`, and `gh repo edit` for ordinary operations. Put long bodies in a temporary file and pass `--body-file`; avoid embedding secrets or tokens. Review `git diff` and `git status` before opening a PR.

## Releases, Tags, and semantic versioning

Use annotated semantic tags (`vMAJOR.MINOR.PATCH`) and verify the working tree and target commit first:
```bash
git tag -a v1.2.3 -m "Release v1.2.3"
git push origin v1.2.3
gh release create v1.2.3 --generate-notes
```
Do not overwrite or delete tags/releases without explicit authorization.

## Actions

Inspect workflows and runs with `gh workflow list`, `gh workflow view`, `gh run list`, and `gh run view`. Trigger or rerun only when requested. Use `gh api` for workflow files, dispatch inputs, artifacts, or repository settings that dedicated commands do not expose.

## Search and advanced API

Use `gh search repos`, `gh search code`, `gh search issues`, and `gh search prs` for supported searches. For advanced queries, use `gh api` with explicit `--method`, `-H`, and `-f`/`-F` parameters. Prefer read-only API calls while diagnosing; confirm response fields before making a mutation.

## Sensitive data and blocked operations

Run `scripts/scan_sensitive.sh <path>` before publication. It checks common `.env` files, private keys, certificates, tokens, passwords, and API-key patterns. Treat matches as a stop for review, not as permission to delete or rewrite files. Destructive operations require a new explicit user instruction at the point of action.
