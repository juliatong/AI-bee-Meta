# Data Structures & API Documentation

## REST API Endpoints

### Base URL
```
http://localhost:8000/api/v1
```

### Authentication
- No authentication in MVP
- Single user, local development

---

## Campaign Endpoints

### 1. Create Campaign

**Endpoint:** `POST /campaigns`

**Description:** Create new Advantage+ Sales campaign in PAUSED status

**Request Body:**
```json
{
  "config_path": "configs/spring_sale.yaml"
}
```

**Response:** `200 OK`
```json
{
  "internal_id": "spring_sale_2024",
  "meta_campaign_id": "123456789",
  "meta_adset_id": "987654321",
  "meta_ad_id": "456789123",
  "status": "PAUSED",
  "created_at": "2024-03-10T14:30:00Z"
}
```

**Errors:**
- `400` - Invalid config, missing required fields
- `404` - Config file not found
- `500` - Meta API error, video upload failed

---

### 2. Get Campaign Status

**Endpoint:** `GET /campaigns/{campaign_id}`

**Description:** Fetch campaign details (fetches live data from Meta API)

**Response:** `200 OK`
```json
{
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
  "scheduled_activation": {
    "job_id": "job_abc123",
    "scheduled_time": "2024-03-15T08:00:00",
    "status": "pending"
  },
  "created_at": "2024-03-10T14:30:00Z",
  "last_synced": "2024-03-10T15:00:00Z"
}
```

**Errors:**
- `404` - Campaign not found

---

### 3. Schedule Campaign Activation

**Endpoint:** `POST /campaigns/{campaign_id}/schedule`

**Description:** Schedule campaign to activate at specific time (GMT+8)

**Request Body:**
```json
{
  "activate_at": "2024-03-15T08:00:00"
}
```

**Response:** `200 OK`
```json
{
  "job_id": "job_abc123",
  "campaign_id": "spring_sale_2024",
  "scheduled_time": "2024-03-15T08:00:00",
  "timezone": "Asia/Singapore",
  "status": "pending"
}
```

**Errors:**
- `400` - Invalid datetime, time in past
- `404` - Campaign not found

---

### 4. Activate Campaign Immediately

**Endpoint:** `POST /campaigns/{campaign_id}/activate`

**Description:** Activate campaign immediately (skip scheduling)

**Response:** `200 OK`
```json
{
  "campaign_id": "spring_sale_2024",
  "status": "ACTIVE",
  "activated_at": "2024-03-10T14:35:00Z"
}
```

**Errors:**
- `404` - Campaign not found
- `500` - Meta API error

---

### 5. Sync Campaign from Ads Manager

**Endpoint:** `POST /campaigns/{campaign_id}/sync`

**Description:** Fetch latest campaign data from Meta API and update local storage

**Response:** `200 OK`
```json
{
  "synced": true,
  "campaign_id": "spring_sale_2024",
  "changes": {
    "status": "ACTIVE",
    "name": "Spring Sale Campaign",
    "daily_budget": 5000,
    "last_synced": "2024-03-15T08:05:00Z"
  }
}
```

**Errors:**
- `404` - Campaign not found
- `500` - Meta API error

---

### 6. Cancel Scheduled Activation

**Endpoint:** `DELETE /campaigns/{campaign_id}/schedule`

**Description:** Cancel pending scheduled activation

**Response:** `200 OK`
```json
{
  "cancelled": true,
  "job_id": "job_abc123",
  "campaign_id": "spring_sale_2024"
}
```

**Errors:**
- `404` - Campaign or schedule not found

---

## Account Endpoints

### 7. Create Account

**Endpoint:** `POST /accounts`

**Description:** Add new client ad account configuration

**Request Body:**
```json
{
  "account_id": "act_123456789",
  "client_name": "Client A",
  "currency": "SGD",
  "pixel_id": "123456789012345",
  "page_id": "987654321098765",
  "catalog_id": null,
  "domain": "client-a.com"
}
```

**Response:** `201 Created`
```json
{
  "internal_id": "acct_123",
  "account_id": "act_123456789",
  "client_name": "Client A",
  "currency": "SGD",
  "created_at": "2024-03-10T14:30:00Z"
}
```

**Errors:**
- `400` - Invalid account data, missing required fields
- `409` - Account already exists

---

### 8. Get Account

**Endpoint:** `GET /accounts/{account_id}`

**Description:** Get client account configuration

**Response:** `200 OK`
```json
{
  "account_id": "act_123456789",
  "client_name": "Client A",
  "currency": "SGD",
  "pixel_id": "123456789012345",
  "page_id": "987654321098765",
  "catalog_id": null,
  "domain": "client-a.com",
  "active": true
}
```

**Errors:**
- `404` - Account not found

---

## Data Models

### Campaign YAML Configuration

**Location:** `configs/*.yaml`

**Schema:**
```yaml
# Required fields
campaign_id: string          # Internal identifier (must be unique)
client_account_id: string    # Reference to account in accounts.json
name: string                 # Campaign name in Meta Ads Manager
daily_budget: integer        # Daily budget in cents/smallest currency unit

# Video (required)
video:
  file_path: string          # Path to video file (relative to project root)
  thumbnail: string          # Optional thumbnail path

# Ad copy (required)
primary_text: string         # Primary ad text
headline: string             # Ad headline
description: string          # Optional description
call_to_action: string       # CTA type (default: "SHOP_NOW")

# Destination (required)
destination_url: string      # Landing page URL
url_parameters: string       # Optional URL parameters (e.g., "utm_source=facebook")

# Scheduling (optional)
schedule:
  activate_at: string        # ISO 8601 datetime in GMT+8 (e.g., "2024-03-15T08:00:00")

# Asset overrides (optional - uses account defaults if not specified)
pixel_id: string | null
page_id: string | null
catalog_id: string | null
```

**Example:**
```yaml
campaign_id: "spring_sale_2024"
client_account_id: "acct_123"
name: "Spring Sale - Video Campaign"
daily_budget: 5000

video:
  file_path: "creatives/spring_sale.mp4"

primary_text: "Spring Sale - 30% off all items! Limited time offer."
headline: "Shop Spring Sale"
description: "Save big on your favorites"
call_to_action: "SHOP_NOW"

destination_url: "https://example.com/spring-sale"
url_parameters: "utm_source=facebook&utm_campaign=spring_sale"

schedule:
  activate_at: "2024-03-15T08:00:00"

pixel_id: null
page_id: null
catalog_id: null
```

---

### Account Configuration (accounts.json)

**Location:** `data/accounts.json`

**Structure:**
```json
{
  "internal_account_id": {
    "account_id": "act_XXXXX",
    "client_name": "string",
    "currency": "SGD" | "USD" | "MYR",
    "pixel_id": "string",
    "page_id": "string",
    "catalog_id": "string | null",
    "domain": "string | null",
    "active": boolean
  }
}
```

**Field Descriptions:**
- `internal_account_id`: Key for reference in campaign YAML
- `account_id`: Meta ad account ID (format: act_XXXXX)
- `client_name`: Client business name
- `currency`: Account currency (set when account created, immutable)
- `pixel_id`: Meta pixel ID for conversion tracking
- `page_id`: Facebook page ID for ad publishing
- `catalog_id`: Optional product catalog ID
- `domain`: Optional domain for verification
- `active`: Whether account is active

**Example:**
```json
{
  "acct_123": {
    "account_id": "act_123456789",
    "client_name": "Client A",
    "currency": "SGD",
    "pixel_id": "123456789012345",
    "page_id": "987654321098765",
    "catalog_id": null,
    "domain": "client-a.com",
    "active": true
  }
}
```

---

### Campaign Tracking (campaigns.json)

**Location:** `data/campaigns.json`

**Structure:**
```json
{
  "campaign_internal_id": {
    "internal_id": "string",
    "client_account_id": "string",
    "name": "string",
    "status": "PAUSED" | "ACTIVE" | "ARCHIVED",
    "daily_budget": integer,
    "meta_ids": {
      "campaign_id": "string",
      "adset_id": "string",
      "ad_id": "string",
      "creative_id": "string",
      "video_id": "string"
    },
    "config_path": "string",
    "created_at": "ISO 8601 datetime",
    "activated_at": "ISO 8601 datetime | null",
    "last_updated": "ISO 8601 datetime",
    "last_synced": "ISO 8601 datetime | null"
  }
}
```

**Field Descriptions:**
- `internal_id`: Internal campaign identifier (from YAML campaign_id)
- `client_account_id`: Reference to account in accounts.json
- `name`: Campaign name
- `status`: Current campaign status in Meta
- `daily_budget`: Budget in cents/smallest unit
- `meta_ids`: All Meta object IDs created
- `config_path`: Path to campaign YAML config
- `created_at`: Campaign creation timestamp (UTC)
- `activated_at`: Activation timestamp (UTC, null if not activated)
- `last_updated`: Last modification timestamp (UTC)
- `last_synced`: Last sync with Meta API timestamp (UTC)

---

### Schedule Tracking (schedules.json)

**Location:** `data/schedules.json`

**Structure:**
```json
{
  "job_id": {
    "job_id": "string",
    "campaign_id": "string",
    "meta_campaign_id": "string",
    "scheduled_time": "ISO 8601 datetime",
    "status": "pending" | "completed" | "failed" | "cancelled",
    "created_at": "ISO 8601 datetime",
    "executed_at": "ISO 8601 datetime | null",
    "error": "string | null"
  }
}
```

**Field Descriptions:**
- `job_id`: APScheduler job ID
- `campaign_id`: Internal campaign ID
- `meta_campaign_id`: Meta campaign ID
- `scheduled_time`: When campaign should activate (GMT+8)
- `status`: Job execution status
- `created_at`: Job creation timestamp (UTC)
- `executed_at`: Job execution timestamp (UTC)
- `error`: Error message if failed

**Status Values:**
- `pending`: Job scheduled, not yet executed
- `completed`: Job executed successfully
- `failed`: Job execution failed (see error field)
- `cancelled`: Job cancelled by user

---

## Meta API Object IDs

### ID Formats

| Object | Format | Example |
|--------|--------|---------|
| Ad Account | `act_XXXXX` | `act_123456789` |
| Campaign | Numeric string | `123456789012345` |
| AdSet | Numeric string | `987654321098765` |
| Ad | Numeric string | `456789123456789` |
| Creative | Numeric string | `789123456789123` |
| Video | Numeric string | `321654987321654` |
| Pixel | Numeric string | `123456789012345` |
| Page | Numeric string | `987654321098765` |

### ID Relationships

```
Ad Account (act_123456789)
  └── Campaign (123456789012345)
        └── AdSet (987654321098765)
              └── Ad (456789123456789)
                    └── Creative (789123456789123)
                          └── Video (321654987321654)

Assets (linked to Ad Account)
  ├── Pixel (123456789012345)
  ├── Page (987654321098765)
  └── Catalog (optional)
```

---

## Error Response Format

**Standard Error Response:**
```json
{
  "error": "ErrorType",
  "message": "Human-readable error message",
  "details": {
    "field": "value",
    "context": "additional context"
  }
}
```

**HTTP Status Codes:**
- `200` - Success
- `201` - Created
- `400` - Bad Request (invalid input)
- `404` - Not Found
- `409` - Conflict (duplicate)
- `500` - Internal Server Error (API error, unexpected error)

**Error Types:**
- `ValidationError` - Invalid input data
- `FileNotFoundError` - Video or config file not found
- `VideoUploadError` - Video upload failed
- `CampaignCreationError` - Campaign creation failed
- `MetaAPIError` - Meta API returned error
- `SchedulingError` - Scheduling operation failed

---

## Currency & Budget Handling

### Currency Support
- **SGD** - Singapore Dollar
- **USD** - US Dollar
- **MYR** - Malaysian Ringgit

### Budget Format
- All budgets in **cents/smallest currency unit**
- Examples:
  - SGD 50.00 = 5000
  - USD 100.00 = 10000
  - MYR 200.00 = 20000

### Budget in API
- Campaign YAML: `daily_budget: 5000` (cents)
- Meta API: Automatically uses account's currency
- No currency conversion logic needed

---

## Timezone Handling

### System Timezone
- **All times in GMT+8** (Asia/Singapore)
- APScheduler timezone: `Asia/Singapore`
- No timezone conversion

### Datetime Format
- **ISO 8601** format
- Example: `2024-03-15T08:00:00`
- Interpreted as GMT+8 (Singapore time)

### Storage
- All timestamps stored in **UTC** with `Z` suffix
- Display converted to GMT+8 when needed
- Example stored: `2024-03-15T00:00:00Z` (UTC)
- Example displayed: `2024-03-15T08:00:00` (GMT+8)

---

## Video Specifications

### Supported Formats
- **MP4** (.mp4)
- **MOV** (.mov)

### Requirements
- **Max size:** 4GB (Meta limit)
- **Aspect ratio:** 16:9 (mobile format) - expected but not validated
- **Recommended codec:** H.264 video, AAC audio

### Validation (MVP)
- ✅ File exists
- ✅ File extension (.mp4 or .mov)
- ✅ File size (under 4GB)
- ❌ Aspect ratio (deferred to post-MVP)
- ❌ Codec validation (deferred to post-MVP)

---

## Sync Behavior

### When Sync Occurs
1. **Manual:** User calls `POST /campaigns/{id}/sync`
2. **Auto:** After scheduled activation (verify success)
3. **On GET:** Always fetches live data from Meta API (but doesn't update storage)

### What Gets Synced
- Campaign status (ACTIVE, PAUSED, ARCHIVED)
- Campaign name
- Daily budget
- Last update timestamp

### Sync Direction
- **One-way:** Meta → Local
- **Source of truth:** Meta Ads Manager
- **No bidirectional sync**

### Conflict Resolution
- Local data always overwritten by Meta data
- No merge logic
- No conflict detection
