# Phase 00 patch — apply to existing GitHub project

This ZIP is a **full copy of the uploaded prototype with updated docs**, not a fresh app and not a live GitHub checkout. Compare before overwriting newer GitHub files.

Key additions: `AGENTS.md`, `docs/CURRENT_STATE_AUDIT.md`, `docs/GAP_ANALYSIS.md`, `docs/SPEC_INTEGRATION_NOTES.md`, v2 docs and prompts. Updated: `.gitignore`, `docs/TASKS.md`, `docs/PROGRESS.md`, `docs/MASTER_SPEC.md`. Application code and original data were not deliberately changed.

**Do not push blindly:** check `git status`, `git ls-files inputs runtime web`, review the `inputs/` documents for sharing permissions. The revised `.gitignore` cannot remove files already committed in Git history.

Validate: `python run.py validate` and `python -m unittest discover -s tests -v`.
