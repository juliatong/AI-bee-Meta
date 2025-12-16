# CLAUDE.md

This file provides guidance to Claude Code when working with this repository.

## What This Is

Meta Ad Campaign Automation - FastAPI service that creates Advantage+ Sales campaigns via Meta Marketing API and schedules activation. Multi-account support with file-based storage.

**Tech Stack:** Python 3.9+, FastAPI, APScheduler, Meta Marketing API (hybrid SDK + API)

## Quick Start

```bash
# First time setup
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
# Edit .env with Meta token
# Edit data/accounts.json with ad accounts

# Start service
uvicorn main:app --reload --host 0.0.0.0 --port 8000
# Docs: http://localhost:8000/docs
```

## Critical Constraints

⚠️ **Real ad accounts** - Be careful with testing
⚠️ **GMT+8 timezone** - All times are Singapore time
⚠️ **System User limitation** - Can only access user's BM (`3723515154528570`), not partner BM
⚠️ **Machine must stay on** - Scheduled jobs won't run if laptop sleeps

## Architecture at a Glance

```
api/routes.py         → FastAPI endpoints
meta/campaign.py      → 6-step campaign creation (hybrid SDK + API)
scheduler/manager.py  → APScheduler for activation
data/*.json           → File-based storage (gitignored)
configs/*.yaml        → Campaign configurations
```

**Hybrid Meta API Approach:**
- Use **SDK** for: Campaign/AdSet/Ad creation (less boilerplate)
- Use **Direct API** for: Video upload, status updates (cleaner file handling)
- See `/docs/02_ARCHITECTURE.md` for operation mapping

## Key Workflows

### Create Campaign
```bash
curl -X POST "http://localhost:8000/api/v1/campaigns" \
  -H "Content-Type: application/json" \
  -d '{"config_path": "configs/campaign.yaml", "start_time": "2024-03-15T08:00:00"}'
```

### Campaign with Start Time
If `start_time` provided:
- Sets AdSet `start_time` field in Meta API
- Creates scheduler job to activate campaign at specified time
- Campaign created in PAUSED status

If `start_time` NOT provided:
- Campaign created in PAUSED status
- Meta defaults start time to creation time
- No scheduler job created

### Campaign Structure
6-step creation process:
1. Upload video → `video_id`
2. Create creative → `creative_id`
3. Create campaign → `campaign_id`
4. Create adset (with Advantage+ config) → `adset_id`
5. Create ad → `ad_id`
6. Store metadata in `campaigns.json`

## Where to Find Details

- `/docs/02_ARCHITECTURE.md` - Technical architecture, Meta API patterns
- `/docs/03_DATA_API.md` - API specs, YAML schema, data models
- `/docs/05_SETUP.md` - First-time installation guide
- `/docs/06_TROUBLESHOOTING.md` - Common issues and solutions
- `/docs/07_WORKFLOWS.md` - Usage examples with curl
- `/docs/08_DEVELOPMENT.md` - Development tasks, code patterns, testing

## Quick Reference

### Common Operations
```bash
# Check campaign status
curl "http://localhost:8000/api/v1/campaigns/CAMPAIGN_ID" | jq '.'

# Sync from Ads Manager
curl -X POST "http://localhost:8000/api/v1/campaigns/CAMPAIGN_ID/sync"

# Activate immediately
curl -X POST "http://localhost:8000/api/v1/campaigns/CAMPAIGN_ID/activate"

# List all campaigns
cat data/campaigns.json | jq 'keys'
```

### File Locations
- Campaign configs: `configs/*.yaml`
- Video files: `creatives/*.mp4` or `*.mov`
- Account configs: `data/accounts.json`
- Campaign tracking: `data/campaigns.json`
- Schedule tracking: `data/schedules.json`

## Important Implementation Notes

### Advantage+ Sales Configuration

**Required AdSet settings:**
```python
{
    'optimization_goal': 'OFFSITE_CONVERSIONS',
    'promoted_object': {
        'pixel_id': pixel_id,
        'custom_event_type': 'PURCHASE'
    },
    'targeting': {
        'advantage_audience': 1  # Advantage+ Audience
    },
    'placement_type': 'PLACEMENT_TYPE_AUTOMATIC',  # Advantage+ Placements
    'bid_strategy': 'LOWEST_COST_WITHOUT_CAP'
}
```

### Campaign YAML Schema

```yaml
campaign_id: "spring_sale_2024"
client_account_id: "acct_123"
name: "Spring Sale Campaign"
daily_budget: 5000  # cents

video:
  file_path: "creatives/video.mp4"

primary_text: "Shop our spring sale!"
headline: "Save 30%"
description: "Limited time"  # optional
call_to_action: "SHOP_NOW"

destination_url: "https://example.com/sale"
url_parameters: "utm_source=facebook"  # optional

# Optional fields
pixel_id: null  # Override account default
page_id: null
catalog_id: null
```

### Business Manager & System User

**CRITICAL:** System Users can only access entities within their own Business Manager.

**User's Setup:**
- User's BM: `3723515154528570` (Adrite) - Owns System User
- Partner BM: `828723616406567` (PARTIPOST) - Partner relationship

**Implications:**
- Singapore beneficiary: Must use user's BM ID (`3723515154528570`)
- API spend attribution: Credits to user's BM (desired for Tech Partner goals)
- Cannot use partner BM entities via System User

**accounts.json Configuration:**
```json
{
  "acct_example": {
    "account_id": "act_123456789",
    "beneficiary_id": "3723515154528570",  // Always user's BM
    "pixel_id": "...",
    "page_id": "..."
  }
}
```

## Security

**DO NOT:**
- Commit `.env`, `data/`, `creatives/` directories
- Log full access tokens
- Use personal user tokens

**DO:**
- Use system user token with proper scopes
- Set restrictive permissions: `chmod 600 .env`
- Back up `data/` directory regularly

## Testing

⚠️ **Testing uses REAL Meta ad accounts**
- Always create campaigns in PAUSED status
- Use minimal budgets for testing
- Verify in Meta Ads Manager before activation
- See `/docs/08_DEVELOPMENT.md` for testing workflow

## Notes for Future Claude Instances

### This is an MVP
- Keep it simple - no over-engineering
- File-based storage is intentional (not a limitation to "fix")
- Local development only - no deployment needed yet
- Manual sync is intentional - no background polling yet

### Post-MVP Features (Deferred)
Do not implement unless explicitly requested:
- Campaign editing
- Multi-video/carousel support
- Image ads
- Email notifications
- Web UI
- Database migration
- Automatic background sync

### Getting Help
1. Check `/docs/06_TROUBLESHOOTING.md`
2. Check `/docs/08_DEVELOPMENT.md` for development tasks
3. Review Meta Marketing API docs: https://developers.facebook.com/docs/marketing-apis
4. Check Meta platform status: https://developers.facebook.com/status
