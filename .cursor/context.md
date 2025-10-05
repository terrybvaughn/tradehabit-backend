# TradeHabit Backend - AI Context

## Start Here
→ `docs/shared/` - Complete TradeHabit documentation and architecture

## Backend-Specific Entry Points
- **Mentor Feature**: `mentor/` - Chat UI and tool runner integration
- **Tool Runner**: `mentor/tool_runner/` - Local JSON fixtures and model integration
- **Analytics**: `analytics/` - Behavioral analysis modules
- **API**: `app.py` - Flask entry point with 14 endpoints

## Key Integration Points
- **Frontend Repo**: See `docs/shared/` for cross-repo integration details
- **Mentor API**: `POST /mentor/messages`, `GET /mentor/health`
- **Shared Docs**: `docs/shared/features/mentor/README.md` for Mentor specifics

## Quick Reference
- **Setup**: See `README.md` for local development
- **Architecture**: See `docs/shared/overview/ARCHITECTURE.md`
- **Compatibility**: See `docs/shared/compatibility.yaml` for FE↔BE version mapping
