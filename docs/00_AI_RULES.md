# AI Rules for Meta Ad Campaign Automation System

## Purpose
This document defines rules for AI assistants (Claude Code, Copilot, etc.) working on this codebase.

## Core Principles

### 1. Feature Scope
- **DO NOT** add features beyond what's documented in `/docs/01_PROJECT.md`
- **DO NOT** implement "nice-to-haves" without explicit approval
- This is an MVP - simplicity over completeness
- Refer to `/docs/01_PROJECT.md` for Post-MVP features list

### 2. Architecture Boundaries
- File-based storage (JSON) - DO NOT introduce database unless explicitly requested
- Local development only - DO NOT add deployment configurations
- Hybrid SDK/API approach - follow patterns in `/docs/02_ARCHITECTURE.md`
- No background workers except APScheduler

### 3. Code Style
- Keep it simple - avoid premature abstractions
- No over-engineering for scale
- Explicit is better than implicit
- Error messages must be actionable

### 4. Meta API Integration
- Use SDK for: Campaign/AdSet/Ad/Creative creation
- Use Direct API for: Video upload, status updates, campaign fetching
- Rationale documented in `/docs/02_ARCHITECTURE.md`
- DO NOT use only SDK or only API - use hybrid approach as specified

### 5. Testing Constraints
- Testing uses REAL Meta ad accounts
- Extra validation required before any destructive operations
- Always create campaigns in PAUSED status first
- Video uploads are irreversible - validate before upload

### 6. Security
- Never commit `.env` file
- Never log full access tokens
- Access tokens in environment variables only
- Account credentials in gitignored `data/accounts.json`

### 7. When Uncertain
1. Check `/docs/01_PROJECT.md` for requirements
2. Check `/docs/02_ARCHITECTURE.md` for technical decisions
3. Check `/docs/11_ASSUMPTIONS.md` for known gaps
4. If still uncertain, ask user - DO NOT guess

## Specific Rules

### File Operations
- Store runtime data in `data/` directory (gitignored)
- Store campaign configs in `configs/` directory
- Store video files in `creatives/` directory (gitignored)
- All file writes must be atomic (write to temp, then rename)

### Error Handling
- Validate inputs before API calls
- Fail fast with clear error messages
- Log errors with context (account ID, campaign ID, etc.)
- DO NOT swallow exceptions silently

### Timezone
- ALL times are GMT+8 (Asia/Singapore)
- APScheduler timezone: "Asia/Singapore"
- No timezone conversion logic needed

### Currency
- Budget amounts in YAML are in cents/smallest unit
- Currency defined per account in `accounts.json`
- NO currency conversion - Meta handles it

### Video Format
- Expect 16:9 mobile format
- Validate: file exists, .mp4/.mov, under 4GB
- DO NOT validate aspect ratio (requires video processing library)

## Change Management
- Update `/docs/04_PROGRESS.md` when implementing features
- Document new assumptions in `/docs/11_ASSUMPTIONS.md`
- Update API documentation in `/docs/03_DATA_API.md` when adding endpoints

## What NOT to Add (Unless Explicitly Requested)
- Authentication/authorization for API
- Rate limiting
- Caching
- Database
- Docker/containerization
- CI/CD pipelines
- Advanced video validation
- Email notifications (deferred to post-MVP)
- Web UI
- Monitoring/alerting
- Multi-tenancy (already handled via accounts.json)
