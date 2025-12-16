# CLAUDE.md - AI Agent Quick Start

**For AI Assistants Working on This Codebase**

This file provides quick orientation for AI assistants (Claude Code, GitHub Copilot, etc.). Read this first (~2 min), then read `docs/00_AI_RULES.md` for detailed constraints (~3 min).

---

## What You Need to Know

**Project**: Meta Ad Campaign Automation
**Purpose**: FastAPI service that creates Advantage+ Sales campaigns via Meta Marketing API and schedules activation
**Tech Stack**: Python 3.9+, FastAPI, APScheduler, Meta Marketing API (hybrid SDK + API)
**Scope**: MVP - see `docs/01_PROJECT.md` for complete requirements

---

## Critical Constraints

⚠️ **Real ad accounts** - Be careful with testing
⚠️ **GMT+8 timezone** - All times are Singapore time
⚠️ **System User limitation** - Can only access user's BM (`3723515154528570`), not partner BM
⚠️ **Machine must stay on** - Scheduled jobs won't run if laptop sleeps

---

## Where to Find Information

| Need | File |
|------|------|
| **Requirements & Scope** | `docs/01_PROJECT.md` |
| **Technical Architecture** | `docs/02_ARCHITECTURE.md` |
| **API Specs & Data Models** | `docs/03_DATA_API.md` |
| **Troubleshooting** | `docs/06_TROUBLESHOOTING.md` |
| **Usage Examples** | `docs/07_WORKFLOWS.md` |
| **Development Guide** | `docs/08_DEVELOPMENT.md` |
| **AI Behavior Constraints** | `docs/00_AI_RULES.md` ⚠️ **Read this!** |

---

## Key Architectural Decisions (Don't Change These)

1. **File-based storage (JSON)** - Intentional, not a limitation to "fix"
2. **Hybrid SDK + Direct API** - Use SDK for campaigns/adsets/ads, Direct API for video upload/status updates
3. **Local development only** - No deployment configurations
4. **No background workers** - Except APScheduler for scheduled activations
5. **MVP scope** - Keep it simple, no over-engineering

See `docs/00_AI_RULES.md` for full constraints.

---

## Testing Warnings

⚠️ **Testing uses REAL Meta ad accounts**

- Always create campaigns in **PAUSED** status
- Use minimal budgets for testing
- Verify in Meta Ads Manager before activation
- Video uploads are **irreversible** - validate before upload

See `docs/08_DEVELOPMENT.md` for testing workflow.

---

## Security Reminders

**DO NOT:**
- Commit `.env`, `data/`, or `creatives/` directories
- Log full access tokens
- Use personal user tokens

**DO:**
- Use system user tokens with proper scopes
- Set restrictive permissions: `chmod 600 .env`
- Back up `data/` directory regularly

---

## Post-MVP Features (Do NOT Implement)

Unless explicitly requested by user:
- Campaign editing (update existing campaigns)
- Multi-video/carousel support
- Image ads
- Email notifications
- Web UI
- Database migration
- Automatic background sync polling
- Authentication/authorization
- Rate limiting
- Caching
- Docker/containerization

See `docs/00_AI_RULES.md` "What NOT to Add" for complete list.

---

## When Uncertain

1. Check `docs/00_AI_RULES.md` for constraints
2. Check relevant `/docs` file for technical details
3. **Ask user** - Never guess or make assumptions

---

## Quick Project Structure

```
api/routes.py         → FastAPI endpoints
meta/campaign.py      → 6-step campaign creation (hybrid SDK + API)
scheduler/manager.py  → APScheduler for activation
data/*.json           → File-based storage (gitignored)
configs/*.yaml        → Campaign configurations
```

See `docs/02_ARCHITECTURE.md` for complete architecture.

---

## Getting Help

1. **Error?** → Check `docs/06_TROUBLESHOOTING.md`
2. **Modifying code?** → Check `docs/08_DEVELOPMENT.md`
3. **Need examples?** → Check `docs/07_WORKFLOWS.md`
4. **Still stuck?** → Ask user (never implement based on assumptions)

---

**Next Step**: Read `docs/00_AI_RULES.md` for detailed behavior constraints and guardrails.
