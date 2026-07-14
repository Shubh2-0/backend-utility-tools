# Central Automation Engine (Private Master Repository)

Unified, high-security private repository consolidating all local developer automation scripts, tools, and publishing engines into a single isolated codebase.

## Consolidated Automation Modules

1. **`github-outreach/`**: GitHub open-source issue contributor bot & sync engine with language filters (exclusion of non-English/CJK issues).
2. **`content-publishing/`**: Automated technical content & blog publishing engine for Dev.to, Hashnode, daily tips, and article generation.
3. **`profile-job-updater/`**: Automated job portal profile refresh engine for Naukri, Shine, and Foundit.
4. **`feed-orchestrator/`**: Telemetry, RSS feed synchronization, and portfolio article aggregator.
5. **`dashboard/`**: Local FastAPI control center web dashboard for automation telemetry monitoring.
6. **`linkedin-automation-paused/`**: Offline reference code (all workflows 100% PAUSED & DISABLED).

## Security Policies

- **100% Private Visibility**: Repository is set to `PRIVATE` on GitHub.
- **Zero Secrets in Code**: All authentication tokens and passwords MUST be set via the local `.env` file.
- **Strict Git Ignore**: `.env`, cache logs, `users.db`, and temporary files are hard-ignored via `.gitignore`.
- **LinkedIn Integration**: Remains completely OFF / PAUSED.
