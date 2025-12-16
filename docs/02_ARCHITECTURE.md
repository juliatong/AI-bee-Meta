# Architecture Documentation

## System Overview

Python-based FastAPI service that automates Meta Advantage+ Sales campaign creation and scheduling.

**Architecture Pattern:** Layered monolith with clear separation of concerns

## Project Structure

```
/Users/julia/Projects/AI bee/
├── main.py                      # FastAPI application entry point
├── requirements.txt             # Python dependencies
├── .env                         # Environment variables (gitignored)
├── .gitignore
│
├── api/                         # API Layer
│   ├── __init__.py
│   ├── routes.py                # FastAPI route handlers
│   └── models.py                # Pydantic request/response models
│
├── meta/                        # Meta API Integration Layer
│   ├── __init__.py
│   ├── client.py                # Hybrid SDK + API wrapper
│   ├── campaign.py              # Campaign creation orchestration
│   ├── creative.py              # Video upload logic
│   └── validator.py             # API response validation
│
├── scheduler/                   # Scheduling Layer
│   ├── __init__.py
│   ├── manager.py               # APScheduler setup
│   └── jobs.py                  # Job execution functions
│
├── storage/                     # Data Persistence Layer
│   ├── __init__.py
│   ├── file_store.py            # JSON file operations
│   └── models.py                # Data models
│
├── config/                      # Configuration Layer
│   ├── __init__.py
│   ├── loader.py                # YAML + Settings loader
│   └── validator.py             # Config validation
│
├── utils/                       # Utilities
│   ├── __init__.py
│   ├── logger.py                # Logging setup
│   └── exceptions.py            # Custom exceptions
│
├── data/                        # Runtime storage (gitignored)
│   ├── accounts.json            # Client account configurations
│   ├── campaigns.json           # Campaign tracking
│   ├── schedules.json           # Scheduled job tracking
│   └── jobs.db                  # APScheduler SQLite persistence
│
├── configs/                     # Campaign YAML definitions
│   └── example_campaign.yaml    # Template
│
├── creatives/                   # Video files (gitignored)
│   └── .gitkeep
│
└── docs/                        # Documentation
    ├── 00_AI_RULES.md
    ├── 01_PROJECT.md
    ├── 02_ARCHITECTURE.md
    ├── 03_DATA_API.md
    └── 04_PROGRESS.md
```

## ⚠️ CRITICAL: Meta API Deprecation Timeline

**Action Required Before Q1 2026**

### Deprecation Schedule
- **October 2025 (API v24.0)**: Legacy Advantage+ campaign creation APIs disabled
- **Q1 2026 (API v25.0)**: Complete removal of legacy ASC/AAC APIs

### Current Implementation Status
✅ **We are using the NEW unified structure** - No migration needed

Our implementation uses:
- `objective: 'OUTCOME_SALES'` (unified structure)
- Advantage+ enabled via AdSet configuration (not legacy API)

### What This Means
- MVP is future-proof
- No breaking changes expected
- Using recommended API patterns

### If Using Legacy APIs (We're Not)
⚠️ Legacy patterns to avoid:
- Old ASC-specific endpoints
- Legacy campaign creation flows
- Deprecated objective types

### Reference
- [Meta API Deprecation Announcement](https://developers.facebook.com/docs/marketing-api/changelog)
- Implementation follows current best practices as of December 2024

---

## Technology Stack

### Core
- **Python 3.9+**: Programming language
- **FastAPI**: Web framework for REST API
- **Uvicorn**: ASGI server
- **Pydantic**: Data validation

### Meta API Integration
- **facebook-business-sdk 18.0.0**: Meta Marketing API SDK
- **requests**: HTTP library for direct API calls

### Scheduling
- **APScheduler 3.10.4**: Job scheduling with SQLite persistence

### Configuration
- **PyYAML**: YAML config parsing
- **python-dotenv**: Environment variable management
- **pydantic-settings**: Settings management

### Utilities
- **tenacity**: Retry logic for API calls

## Data Flow

### Campaign Creation Flow

```
User → POST /campaigns → API Layer
                             ↓
                     Load YAML config
                             ↓
                    Validate config
                             ↓
                  Meta API Layer (6-step process)
                             ↓
        ┌────────────────────┴────────────────────┐
        ↓                                         ↓
   1. Upload video → video_id            2. Create creative → creative_id
        ↓                                         ↓
   3. Create campaign → campaign_id       4. Create adset → adset_id
        ↓                                         ↓
   5. Create ad → ad_id                   6. Store metadata
        ↓
   Storage Layer (campaigns.json)
        ↓
   Return campaign IDs to user
```

### Scheduling Flow

```
User → POST /campaigns/{id}/schedule → API Layer
                                           ↓
                                  APScheduler Manager
                                           ↓
                          Store job in jobs.db + schedules.json
                                           ↓
                              [Wait until scheduled time]
                                           ↓
                                  Execute job function
                                           ↓
                        Meta API: Update status PAUSED → ACTIVE
                                           ↓
                          Sync campaign from Meta (verify)
                                           ↓
                     Update campaigns.json + schedules.json
```

### Sync Flow

```
User → POST /campaigns/{id}/sync → API Layer
                                        ↓
                              Get Meta campaign ID
                                        ↓
                      Meta API: Fetch campaign data
                                        ↓
                      Storage Layer: Update local data
                                        ↓
                           Return synced fields
```

## Meta API Integration Strategy

### Hybrid SDK + API Approach

**Decision:** Use SDK for some operations, direct API for others - pick best tool per operation.

**Rationale:**
- SDK: Less boilerplate for structured operations
- Direct API: Cleaner for file upload and simple updates
- No dual implementation - one method per operation

### Operation Mapping

| Operation | Method | Rationale |
|-----------|--------|-----------|
| Video upload | Direct API (requests) | Cleaner multipart file handling |
| Campaign creation | SDK | Typed objects, less boilerplate |
| AdSet creation | SDK | Typed objects, less boilerplate |
| Creative creation | SDK | Typed objects, less boilerplate |
| Ad creation | SDK | Typed objects, less boilerplate |
| Status update | Direct API | Simple single-field update |
| Fetch campaign | Direct API | Simple GET with field selection |

### Meta API Client Design

```python
class MetaAPIClient:
    """Hybrid client using both SDK and direct API"""

    def __init__(self, access_token: str):
        self.access_token = access_token
        self.base_url = "https://graph.facebook.com/v18.0"
        FacebookAdsApi.init(access_token=access_token)

    # Direct API methods
    def upload_video(self, account_id: str, video_path: str) -> str:
        """Use requests for file upload"""

    def update_campaign_status(self, campaign_id: str, status: str) -> dict:
        """Use direct API for simple update"""

    def get_campaign(self, campaign_id: str) -> dict:
        """Use direct API for fetching"""

    # SDK methods
    def create_campaign(self, account_id: str, params: dict) -> dict:
        """Use SDK for structured creation"""

    def create_adset(self, campaign_id: str, params: dict) -> dict:
        """Use SDK for structured creation"""

    def create_ad(self, adset_id: str, params: dict) -> dict:
        """Use SDK for structured creation"""
```

## Campaign Creation (6-Step Process)

### Step 1: Upload Video
- Endpoint: `POST /{ad_account_id}/advideos`
- Method: Direct API with requests library
- Input: Video file path
- Output: `video_id`
- Error handling: File validation before upload

### Step 2: Create AdCreative
- Endpoint: `POST /{ad_account_id}/adcreatives`
- Method: SDK
- Input: video_id, page_id, ad copy
- Output: `creative_id`
- Structure: object_story_spec with video_data

### Step 3: Create Campaign
- Endpoint: `POST /{ad_account_id}/campaigns`
- Method: SDK
- Input: campaign name, objective
- Output: `campaign_id`
- Always create with `status='PAUSED'`

### Step 4: Create AdSet
- Endpoint: `POST /{ad_account_id}/adsets`
- Method: SDK
- Input: campaign_id, budget, targeting
- Output: `adset_id`
- Advantage+ configuration:
  - Campaign Budget Optimization (CBO)
  - Advantage+ Audience (advantage_audience: 1)
  - Advantage+ Placements (placement_type: AUTOMATIC)

### Step 5: Create Ad
- Endpoint: `POST /{ad_account_id}/ads`
- Method: SDK
- Input: adset_id, creative_id
- Output: `ad_id`
- Status: PAUSED

### Step 6: Store Metadata
- Save all IDs to `campaigns.json`
- Track: campaign_id, adset_id, ad_id, creative_id, video_id
- Include: account_id, config_path, timestamps

## Advantage+ Sales Campaign Configuration

### Required Campaign Settings
```python
{
    'name': campaign_name,
    'objective': 'OUTCOME_SALES',
    'status': 'PAUSED',
    'special_ad_categories': []
}
```

### Required AdSet Settings
```python
{
    'name': f"{campaign_name} - AdSet",
    'campaign_id': campaign_id,
    'optimization_goal': 'OFFSITE_CONVERSIONS',
    'promoted_object': {
        'pixel_id': pixel_id,
        'custom_event_type': 'PURCHASE'
    },
    'daily_budget': daily_budget,  # In cents
    'bid_strategy': 'LOWEST_COST_WITHOUT_CAP',
    'targeting': {
        'age_min': 18,
        'age_max': 65,
        'geo_locations': {'countries': ['SG']},  # Configurable
        'advantage_audience': 1  # Advantage+ Audience
    },
    'placement_type': 'PLACEMENT_TYPE_AUTOMATIC',  # Advantage+ Placements
    'status': 'PAUSED'
}
```

### Required Creative Settings
```python
{
    'name': f"{campaign_name} - Creative",
    'object_story_spec': {
        'page_id': page_id,
        'video_data': {
            'video_id': video_id,
            'message': primary_text,
            'title': headline,
            'link_description': description,
            'call_to_action': {
                'type': call_to_action,  # e.g., 'SHOP_NOW'
                'value': {
                    'link': destination_url
                }
            }
        }
    }
}
```

## Scheduling System

### APScheduler Configuration
```python
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore

jobstores = {
    'default': SQLAlchemyJobStore(url='sqlite:///data/jobs.db')
}

scheduler = BackgroundScheduler(
    jobstores=jobstores,
    timezone='Asia/Singapore'  # GMT+8
)
```

### Job Execution
```python
def activate_campaign_job(campaign_id: str):
    """Executed at scheduled time"""
    # 1. Get Meta campaign ID
    meta_campaign_id = get_meta_campaign_id(campaign_id)

    # 2. Update status via Meta API
    client.update_campaign_status(meta_campaign_id, 'ACTIVE')

    # 3. Sync to verify activation
    sync_campaign_from_meta(campaign_id)

    # 4. Mark job completed
    mark_job_completed(campaign_id)
```

### Timezone Handling
- All times in GMT+8 (Asia/Singapore)
- APScheduler configured with timezone='Asia/Singapore'
- Campaign YAML `activate_at` times interpreted as Singapore time
- No timezone conversion logic needed

## Data Storage

### File-Based Storage
- **Format:** JSON
- **Location:** `data/` directory (gitignored)
- **Atomic writes:** Write to temp file, then rename

### Storage Schema

**accounts.json**
```json
{
  "acct_123": {
    "account_id": "act_123456789",
    "client_name": "Client A",
    "currency": "SGD",
    "pixel_id": "123456789012345",
    "page_id": "987654321098765",
    "catalog_id": null,
    "domain": "client-a.com"
  }
}
```

**campaigns.json**
```json
{
  "spring_sale_2024": {
    "internal_id": "spring_sale_2024",
    "client_account_id": "acct_123",
    "name": "Spring Sale Campaign",
    "status": "PAUSED",
    "daily_budget": 5000,
    "meta_ids": {
      "campaign_id": "123456789",
      "adset_id": "987654321",
      "ad_id": "456789123",
      "creative_id": "789123456",
      "video_id": "321654987"
    },
    "config_path": "configs/spring_sale.yaml",
    "created_at": "2024-03-10T14:30:00Z",
    "activated_at": null,
    "last_updated": "2024-03-10T14:30:00Z",
    "last_synced": null
  }
}
```

**schedules.json**
```json
{
  "job_abc123": {
    "job_id": "job_abc123",
    "campaign_id": "spring_sale_2024",
    "meta_campaign_id": "123456789",
    "scheduled_time": "2024-03-15T08:00:00",
    "status": "pending",
    "created_at": "2024-03-10T14:30:00Z",
    "executed_at": null,
    "error": null
  }
}
```

### FileStore Implementation
```python
class FileStore:
    def __init__(self, data_dir: str):
        self.data_dir = Path(data_dir)

    def load(self, filename: str) -> dict:
        """Load JSON file"""

    def save(self, filename: str, data: dict):
        """Atomic save to JSON file"""

    def add_campaign(self, campaign_id: str, data: dict):
        """Add campaign to campaigns.json"""

    def update_campaign(self, campaign_id: str, updates: dict):
        """Update campaign fields"""

    def get_campaign(self, campaign_id: str) -> dict:
        """Get campaign by ID"""
```

## Configuration Management

### Campaign YAML Schema
```yaml
campaign_id: "spring_sale_2024"
client_account_id: "acct_123"
name: "Spring Sale Campaign"
daily_budget: 5000  # cents

video:
  file_path: "creatives/video.mp4"
  thumbnail: "creatives/thumb.jpg"  # optional

primary_text: "Shop our spring sale!"
headline: "Save 30%"
description: "Limited time"  # optional
call_to_action: "SHOP_NOW"

destination_url: "https://example.com/sale"
url_parameters: "utm_source=facebook"  # optional

schedule:  # optional
  activate_at: "2024-03-15T08:00:00"  # GMT+8

# Override account defaults (optional)
pixel_id: null
page_id: null
catalog_id: null
```

### Environment Variables (.env)
```bash
META_ACCESS_TOKEN=your_system_user_token
META_BUSINESS_MANAGER_ID=123456789012345
```

### Settings (Pydantic)
```python
class Settings(BaseSettings):
    meta_access_token: str
    meta_business_manager_id: str
    data_dir: str = "data"
    creatives_dir: str = "creatives"
    configs_dir: str = "configs"

    class Config:
        env_file = ".env"
```

## Error Handling

### Validation Strategy
1. **Pre-flight validation**
   - Campaign config validation
   - Video file validation (exists, format, size)
   - Account existence check
   - Required fields check

2. **API call validation**
   - Response status check
   - Error code handling
   - Retry logic (3 attempts, exponential backoff)

3. **Rollback on failure**
   - Track created resources (video_id, creative_id, etc.)
   - Delete on partial failure
   - Log rollback actions

### Custom Exceptions
```python
class MetaAPIError(Exception): pass
class VideoUploadError(MetaAPIError): pass
class CampaignCreationError(MetaAPIError): pass
class SchedulingError(Exception): pass
class ValidationError(Exception): pass
```

### Retry Logic
```python
from tenacity import retry, stop_after_attempt, wait_exponential

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=10)
)
def api_call_with_retry(func):
    """Retry on transient API errors (500, 503)"""
```

## Video Validation

### Basic Validation (MVP)
```python
def validate_video_file(video_path: str):
    path = Path(video_path)

    # File exists
    if not path.exists():
        raise FileNotFoundError(f"Video not found: {video_path}")

    # File extension
    if path.suffix.lower() not in ['.mp4', '.mov']:
        raise ValueError(f"Unsupported format: {path.suffix}")

    # File size (4GB Meta limit)
    size_mb = path.stat().st_size / (1024 * 1024)
    if size_mb > 4096:
        raise ValueError(f"Video too large: {size_mb:.1f}MB")
```

**Deferred to post-MVP:**
- Aspect ratio validation (requires video processing library)
- Codec validation
- Duration validation

## Sync Implementation

### Sync Strategy
- **On-demand:** Manual call to `/campaigns/{id}/sync`
- **Auto-sync:** After scheduled activation (verify success)
- **Live fetch:** GET endpoint always fetches from Meta API

### Sync Fields
- Campaign status (ACTIVE, PAUSED, ARCHIVED)
- Campaign name
- Daily budget
- Last update timestamp

### Conflict Resolution
- Meta Ads Manager = source of truth
- Local system always overwrites with Meta data
- One-way sync (Meta → Local)
- No bidirectional sync

## Business Manager Structure & System User Access

### BM Relationship Architecture

**User's BM:** `3723515154528570` (Adrite)
- Owns the System User used for API access
- Owns some ad accounts directly
- API spend from this System User credits to this BM
- Critical for Meta Tech Partner status goals

**Partner BM:** `828723616406567` (PARTIPOST PTE. LTD.)
- Partner relationship with user's BM
- May share ad accounts with user's BM
- Can be used as beneficiary in manually created campaigns

### System User Access Limitations

**CRITICAL META PLATFORM LIMITATION:**

System Users can only access entities within their own Business Manager, not partner BM entities, even if those partners have shared ad accounts.

**What This Means:**
- ✅ System User can access: User's BM entities (`3723515154528570`)
- ❌ System User cannot access: Partner BM entities (`828723616406567`)
- ✅ System User can manage: Ad accounts shared by partner
- ❌ System User cannot use: Partner BM as beneficiary (lacks entity access)

**Practical Impact:**
- Manual campaigns (user account) → Can use any accessible BM as beneficiary
- API campaigns (System User) → Limited to user's BM entities only
- API spend attribution → Always credits to BM that owns System User

### Singapore Beneficiary Configuration

**Requirement:** Singapore ads must specify beneficiary via `regional_regulation_identities`

**Implementation:**
```python
# For Singapore-targeted campaigns
if 'SG' in geo_locations['countries']:
    adset_params['regional_regulated_categories'] = ['SINGAPORE_UNIVERSAL']
    adset_params['regional_regulation_identities'] = {
        'singapore_universal_beneficiary': '3723515154528570',  # User's BM
        'singapore_universal_payer': '3723515154528570'
    }
```

**Why User's BM ID:**
- Partner BM (`828723616406567`) inaccessible to System User
- User's BM (`3723515154528570`) ensures API spend attribution
- Both options satisfy Singapore compliance requirements
- Beneficiary difference is cosmetic; spend attribution is strategic

### API Spend Attribution Strategy

**Goal:** Accumulate API spend for Meta Tech Partner qualification

**Critical Decision:** Always use System User from user's BM to ensure:
1. All API spend credits to user's BM (`3723515154528570`)
2. Spend accumulates toward Tech Partner metrics
3. User maintains control of API credentials

**Alternative (Not Recommended):**
- Using System User from partner BM would credit spend to partner
- Would not advance user's Tech Partner goals
- Defeats strategic purpose of automation

## Security Considerations

### Access Control
- No authentication on API (single user, local development)
- Meta API access via system user token
- Token stored in .env (gitignored)

### Data Protection
- Sensitive data (tokens) in environment variables
- Account data in gitignored files
- Never log full access tokens

### API Token Management
- System user token (never expires)
- Required scopes: business_management, ads_management, ads_read
- Generated in Business Manager → System Users
- **Must be created under user's BM** for proper spend attribution

## Performance Considerations

### Rate Limiting
- [UNDECIDED] No rate limiting implemented in MVP
- Meta has rate limits (varies by tier)
- [ASSUMPTION] Single user workload won't hit limits

### Concurrent Operations
- [UNDECIDED] No concurrent campaign creation
- Sequential processing for MVP
- APScheduler handles concurrent job execution

### Caching
- No caching implemented
- Fresh data from Meta API on every GET
- Local storage for tracking only

## Deployment

### MVP Deployment
- Run locally on user's laptop
- No containerization
- No cloud deployment
- Keep machine running for scheduled campaigns

### Running the Service
```bash
# Install dependencies
pip install -r requirements.txt

# Set up environment
cp .env.example .env
# Edit .env with token

# Run service
uvicorn main:app --host 0.0.0.0 --port 8000
```

### Known Limitations
- Machine must stay running for scheduled jobs
- No automatic restart on crash
- No monitoring/alerting
- Manual log checking

## Future Architecture Considerations (Post-MVP)

### Scalability
- Database migration (PostgreSQL/MongoDB)
- Background worker queue (Celery/RQ)
- Caching layer (Redis)
- API rate limiting

### Reliability
- Cloud deployment (AWS/GCP)
- Container orchestration (Docker + Kubernetes)
- Health checks and monitoring
- Automated backups

### Features
- Multi-user support with authentication
- Web UI
- Real-time notifications
- Performance reporting dashboard
- Advanced video processing
