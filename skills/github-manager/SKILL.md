---
name: github-manager
description: Manage GitHub repositories, code, Issues, Pull Requests, Releases, Tags, Actions, and GitHub search/API tasks using local git with gh as the primary platform interface. Use when a request involves GitHub or publishing repository work.
---

# GitHub Manager

Use local `git` for version control and GitHub CLI (`gh`) for GitHub operations. Use `gh api` when the required operation is not covered by a dedicated `gh` command. Work in the user's selected repository and preserve existing repositories and configuration.

## Routing

1. Inspect the current repository, branch, remotes, and working tree before changing anything.
2. Verify authentication with `gh auth status`; use `gh api user` when API access matters. Do not run login automatically.
3. Read [references/workflows.md](references/workflows.md) for the operation-specific procedure (repository, publish, Issue/PR, Release/Tag, Actions, or search/API).
4. Before any publish, push, Release, or other external mutation, run `scripts/scan_sensitive.sh` against the intended files and stop if it finds likely secrets. Never print secret values.
5. Ask for explicit authorization immediately before destructive actions: deleting repositories, force-pushing, `git reset --hard`, changing visibility, or deleting Releases/Tags. Do not infer authorization from a general request to manage GitHub.
6. Report the exact commands run, resulting URLs/identifiers, and any skipped or blocked step.

## Safe defaults

- Prefer normal `git pull`, `git push`, and fast-forward updates.
- Prefer `gh repo create`, `gh repo view`, `gh issue`, `gh pr`, `gh release`, `gh run`, and `gh search` where applicable; use `gh api` for advanced endpoints.
- Never create test repositories or modify/delete repositories outside the user's stated scope.
- Keep sensitive values out of commits, command output, Issues, PRs, Releases, and logs. Use environment variables or platform secret stores when the user has explicitly authorized their use.
- For semantic versioning, validate the target version and tag format before creating a tag or Release.
- Load only the relevant section of the reference guide; do not read all procedures for a simple request.
