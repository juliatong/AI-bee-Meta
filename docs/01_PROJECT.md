# Meta Ad Campaign Automation System - Project Overview

## Business Context

### Background
- User: Former Meta solutions engineer
- Use case: Automate Meta ad campaign creation for marketing service clients
- Business model: BM-to-BM relationship
  - User's Business Manager owns client ad accounts
  - User's BM acts as execution partner
  - API spend attribution goes to user's BM for Meta Tech Partner goals

### Problem Statement
Manual campaign creation is time-consuming. Need automation to:
1. Create Advantage+ Sales campaigns programmatically
2. Schedule campaigns to activate at specific times
3. Manage multiple client ad accounts from one system
4. Sync changes made in Meta Ads Manager

## MVP Requirements

### Core Features
1. **Campaign Creation**
   - Create Advantage+ Sales campaigns via Meta Marketing API
   - Single video ad per campaign
   - Create in PAUSED (draft) status
   - Full campaign structure: Campaign → AdSet → Ad

2. **Scheduling**
   - Schedule campaigns to activate at specific future time
   - Timezone: GMT+8 (Singapore time)
   - Automatic status change from PAUSED to ACTIVE

3. **Multi-Account Support**
   - Manage multiple client ad accounts
   - Each account has own: pixel, page, catalog, currency
   - Supported currencies: SGD, USD, MYR

4. **Ads Manager Sync**
   - Manual sync endpoint to fetch latest campaign data from Meta
   - Auto-sync after scheduled activation (verify success)
   - Meta Ads Manager is source of truth

5. **Configuration Management**
   - Campaign definitions in YAML files
   - Account configurations in JSON
   - Video files stored locally

### Campaign Specifications

**Objective:** OUTCOME_SALES (Purchase conversions)

**Campaign Type:** Advantage+ Sales Campaigns
- Campaign Budget Optimization (CBO)
- Advantage+ Audience
- Advantage+ Placements

**Budget:** Campaign-level daily budget

**Creative:**
- Single video ad per campaign
- Format: 16:9 mobile format
- File types: MP4, MOV
- Max size: 4GB

**Targeting:** Configurable per campaign (default: Singapore)

**Ad Copy:**
- Primary text
- Headline
- Description (optional)
- Call-to-action (default: SHOP_NOW)
- Destination URL

## User Workflow

### 1. Setup (One-time)
- Generate Meta system user token
- Configure client ad accounts in `data/accounts.json`
- Start API service locally

### 2. Create Campaign
- Create campaign YAML config with video path and settings
- POST to `/api/v1/campaigns` with config path
- System creates campaign in PAUSED status in Meta

### 3. Schedule Activation
- POST to `/api/v1/campaigns/{id}/schedule` with activation time
- System schedules job to activate at specified time (GMT+8)

### 4. Monitor
- GET `/api/v1/campaigns/{id}` to check status
- POST `/api/v1/campaigns/{id}/sync` to sync from Ads Manager
- Check logs for errors

### 5. Manual Activation (Optional)
- POST `/api/v1/campaigns/{id}/activate` to activate immediately

## Technical Stack

**Language:** Python 3.9+

**Framework:** FastAPI

**Storage:** File-based (JSON)
- `data/accounts.json` - Client account configs
- `data/campaigns.json` - Campaign tracking
- `data/schedules.json` - Job tracking
- `data/jobs.db` - APScheduler persistence (SQLite)

**Scheduling:** APScheduler

**Meta API Integration:** Hybrid approach
- facebook-business-sdk for campaign/adset/ad creation
- Direct requests library for video upload and status updates

**Deployment:** Local development (laptop)

## Key Design Decisions

### Simplicity First
- File-based storage (no database)
- Single video per campaign
- Manual sync (no background polling)
- Logs only for errors (no email notifications in MVP)

### Multi-Currency Support
- Each account has currency field (SGD, USD, MYR)
- Budget amounts in YAML are in cents/smallest unit
- Meta API handles currency automatically

### Timezone
- All times in GMT+8 (Asia/Singapore)
- No timezone conversion needed
- APScheduler configured with Asia/Singapore timezone

### Testing Approach
- Testing on real Meta ad accounts
- Extra validation before operations
- Always create campaigns in PAUSED first

### Hybrid SDK + API
- Use SDK where it simplifies code (campaign creation)
- Use direct API where it's cleaner (video upload)
- No dual implementation - pick best tool per operation

## Out of Scope (Post-MVP)

### Deferred Features
- Campaign editing (update existing campaigns)
- Multi-video/carousel support
- Image ads
- Email notifications
- Web UI
- Performance reporting
- Database migration
- Recurring campaigns
- Advanced video validation (aspect ratio, codec)
- Budget minimum validation
- Rate limiting implementation
- Automatic background sync polling

### Not Required
- User authentication (single user system)
- Multi-user support
- Deployment automation
- Monitoring/alerting infrastructure
- CI/CD pipelines

## Client Assets Configuration

Each client ad account requires:
- **Account ID** (act_XXXXX)
- **Pixel ID** (conversion tracking)
- **Page ID** (ad publisher)
- **Currency** (SGD, USD, MYR)
- **Catalog ID** (optional, for product ads)
- **Domain** (optional, for verification)

## Meta API Requirements

### System User Token
- Generated in Business Manager → System Users
- Required scopes:
  - `business_management`
  - `ads_management`
  - `ads_read`
- Token set to "Never Expire"
- Stored in `.env` file (gitignored)

### Ad Account Permissions
- System user must have "Manage Campaigns" permission
- Ad accounts must be owned by user's Business Manager
- Attribution automatically goes to BM that owns system user

## Known Limitations

### Local Development
- Machine must stay running for scheduled campaigns
- If laptop sleeps, scheduled jobs won't execute
- Solution: Keep machine running or deploy to server later

### Manual Sync
- Sync requires calling endpoint
- No automatic detection of Ads Manager changes
- Must manually sync after editing in Ads Manager

### Ad Review Process
- Campaigns go to "pending review" after activation
- Review takes hours, might get rejected
- Must check Ads Manager for review status manually

### State Management
- Local system doesn't auto-sync with Ads Manager
- Manual sync required to update local state
- GET endpoint fetches live data but doesn't persist

## Success Criteria

MVP is successful when:
1. ✅ Can create Advantage+ Sales campaign via API
2. ✅ Campaign appears in Meta Ads Manager in PAUSED status
3. ✅ Can schedule campaign to activate at future time (GMT+8)
4. ✅ Scheduled campaign activates automatically
5. ✅ Can manage multiple client accounts
6. ✅ Can sync campaign status from Ads Manager
7. ✅ System handles multiple currencies correctly
8. ✅ Video upload works for MP4/MOV files

## Stakeholders

**Primary User:** Julia (former Meta solutions engineer)
- Manages campaigns for marketing service clients
- Singapore-based, using GMT+8 timezone
- Working with SGD, USD, MYR currencies

**Clients:** Marketing service customers
- Each has own ad account under Julia's BM
- Campaigns created and managed by Julia
- May use different currencies based on region
