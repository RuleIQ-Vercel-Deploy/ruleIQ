# History Rewrite Runbook

Use this playbook immediately after rotating credentials in Doppler to scrub leaked values from Git history.

## Prerequisites
- All credentials listed in `SECRET_ROTATION_PLAN.md` are rotated and confirmed in Doppler/infra.
- Every collaborator has paused new pushes to `the-bmad-experiment`.
- `git-filter-repo` installed (`pip install git-filter-repo`).
- Working tree is clean (`git status` shows no changes).

## Workflow
1. **Create a local safety branch**
   ```bash
   git fetch --all
   git checkout the-bmad-experiment
   git pull --ff-only
   ```
2. **Run the purge script with explicit acknowledgement**
   ```bash
   ALLOW_HISTORY_REWRITE=true scripts/tools/purge_secrets.sh
   ```
   The script snapshots `refs/backup/rewrite-backup-YYYYMMDD-HHMMSS` and invokes `git-filter-repo` with the canonical replacements (Neon URL, Stack keys, OpenAI token, Google API key, JWT samples, etc.).
3. **Inspect the rewritten history**
   ```bash
   git log --stat --since=1.month
   git show HEAD~1:path/to/any/sensitive/file
   python3 scripts/ci/scan_secrets.py
   ```
   Ensure the scanner returns "No secrets detected".
4. **Force push once validated**
   ```bash
   git push origin --force --all
   git push origin --force --tags
   ```
5. **Notify the team**
   - Share the new backup ref (`refs/backup/rewrite-backup-*`) in case rollback is required.
   - Ask collaborators to reclone or run `git fetch --all && git reset --hard origin/the-bmad-experiment`.

## Rollback Plan
If anything looks wrong, restore the backup ref created by the script:
```bash
git checkout -b restore-from-rewrite refs/backup/rewrite-backup-YYYYMMDD-HHMMSS
git push origin restore-from-rewrite
```

Document successful execution in the security channel, noting the date/time and confirming Doppler parity.
