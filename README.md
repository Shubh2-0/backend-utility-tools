# Central Automation Engine (Private)

Unified, high-security repository for local automation modules, workflows, and tools.

## Structure
- `github-outreach/`: Open-source issue contribution and reachout scripts with language filtering (CJK/Non-English exclusion).
- `dashboard/`: FastAPI control dashboard for monitoring automation metrics.
- `instagram-automation/`: Instagram local comment management utilities.

## Security Policies
- All API tokens and credentials MUST be supplied strictly via environment variables (`.env`).
- No hardcoded secrets, contact info, or tokens are allowed in source tracking.
- Workflows on external platforms (e.g. LinkedIn) are strictly disabled to prevent unintended interactions.
