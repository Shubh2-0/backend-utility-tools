# Central Automation Engine (Private)

Unified, high-security repository for local automation modules, workflows, and tools.

## Structure
- `github-outreach/`: Open-source issue contribution and reachout scripts with language filtering (CJK/Non-English exclusion).
- `dashboard/`: FastAPI control dashboard for monitoring automation metrics.
- `linkedin-automation-paused/`: Paused/offline LinkedIn references (No active GitHub Actions workflows).

## Security Policies
- All API tokens and credentials MUST be supplied strictly via environment variables (`.env`).
- No hardcoded secrets, contact info, or tokens are allowed in source tracking.
- External account workflows are strictly disabled.
