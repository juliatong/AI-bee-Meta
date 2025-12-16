# Development Guide

**Audience:** Developers modifying the codebase
**Purpose:** Learn how to extend and maintain the system
**For usage examples:** See `/docs/07_WORKFLOWS.md`

---

## Overview

This guide is for developers working on the Meta Ad Campaign Automation codebase. It covers common development tasks, code patterns, testing strategies, and best practices.

---

## Development Environment

### Prerequisites
- Python 3.9+
- Virtual environment activated
- Dependencies installed (`pip install -r requirements.txt`)
- `.env` configured with Meta API credentials
- `data/accounts.json` configured with test account

### Running Development Server

```bash
# Activate virtual environment
source venv/bin/activate

# Start with auto-reload
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# API docs available at http://localhost:8000/docs
```

### Development Tools

**API Testing:**
- FastAPI Swagger UI: `http://localhost:8000/docs`
- curl for command-line testing
- Postman/Insomnia for complex workflows

**Code Quality:**
- pylint/flake8 for linting (when added)
- pytest for testing (when added)
- Manual testing with real Meta ad accounts

---

## Common Development Tasks

### Task 1: Adding a New API Endpoint

**Example:** Add endpoint to pause a campaign

**Steps:**

1. **Define Pydantic model** in `api/models.py`:
```python
class PauseCampaignRequest(BaseModel):
    """Request to pause a campaign."""
    campaign_id: str = Field(..., description="Internal campaign ID")
    reason: Optional[str] = Field(None, description="Reason for pausing")
```

2. **Add route handler** in `api/routes.py`:
```python
@router.post("/campaigns/{campaign_id}/pause", response_model=StatusResponse)
async def pause_campaign(campaign_id: str, request: PauseCampaignRequest):
    """Pause an active campaign."""
    try:
        # Get campaign data
        campaign = file_store.get_campaign(campaign_id)
        meta_campaign_id = campaign['meta_ids']['campaign_id']

        # Update status via Meta API
        client = get_meta_client()
        result = client.update_campaign_status(meta_campaign_id, 'PAUSED')

        # Sync to update local data
        sync_campaign_from_meta(campaign_id)

        return StatusResponse(
            success=True,
            campaign_id=campaign_id,
            status="PAUSED"
        )
    except Exception as e:
        logger.error(f"Failed to pause campaign: {e}")
        raise HTTPException(status_code=500, detail=str(e))
```

3. **Test with curl:**
```bash
curl -X POST "http://localhost:8000/api/v1/campaigns/test_001/pause" \
  -H "Content-Type: application/json" \
  -d '{"campaign_id": "test_001", "reason": "Testing pause feature"}'
```

4. **Verify in Meta Ads Manager:**
- Check campaign status changed to PAUSED
- Verify change reflected in local `campaigns.json`

5. **Update documentation:**
- Add endpoint to `/docs/03_DATA_API.md`
- Add usage example to `/docs/07_WORKFLOWS.md`

---

### Task 2: Adding a New Campaign Field

**Example:** Add `end_date` field to campaigns

**Steps:**

1. **Update YAML schema documentation** in `/docs/03_DATA_API.md`:
```yaml
schedule:
  activate_at: "2024-03-15T08:00:00"
  end_date: "2024-03-20T23:59:59"  # NEW FIELD
```

2. **Update config validator** in `config/validator.py`:
```python
def validate_schedule(schedule: dict):
    """Validate schedule configuration."""
    if 'activate_at' in schedule:
        validate_datetime(schedule['activate_at'])

    # NEW: Validate end_date
    if 'end_date' in schedule:
        validate_datetime(schedule['end_date'])
        # Ensure end_date is after activate_at
        if 'activate_at' in schedule:
            activate = parse_datetime(schedule['activate_at'])
            end = parse_datetime(schedule['end_date'])
            if end <= activate:
                raise ValidationError("end_date must be after activate_at")
```

3. **Update campaign creation** in `meta/campaign.py`:
```python
# In create_advantage_plus_campaign function
def create_advantage_plus_campaign(
    client: MetaAPIClient,
    account_id: str,
    campaign_config: Dict[str, Any],
    account_config: Dict[str, Any],
    start_time: Optional[datetime] = None,
    end_time: Optional[datetime] = None  # NEW PARAMETER
) -> Dict[str, str]:
    # ...

    # Add end_time to adset params if provided
    if end_time:
        adset_params['end_time'] = end_time.strftime('%Y-%m-%dT%H:%M:%S+0800')
        logger.info(f"Setting AdSet end_time: {adset_params['end_time']}")
```

4. **Update API route** in `api/routes.py`:
```python
# Parse end_time from schedule if present
end_time = None
if schedule and 'end_date' in schedule:
    end_time = parse_datetime(schedule['end_date'])

# Pass to campaign creation
created_ids = create_advantage_plus_campaign(
    client=client,
    account_id=account_id,
    campaign_config=campaign_config,
    account_config=account_config,
    start_time=request.start_time,
    end_time=end_time  # NEW
)
```

5. **Test with new config:**
```yaml
# configs/test_end_date.yaml
campaign_id: "test_end_date_001"
# ... other fields ...
schedule:
  activate_at: "2024-03-15T08:00:00"
  end_date: "2024-03-20T23:59:59"
```

6. **Verify in Meta Ads Manager:**
- Check AdSet shows correct end time
- Test that campaign stops at end_date

---

### Task 3: Adding a New Client Account

**Steps:**

1. **Gather account information:**
   - Ad account ID: `act_XXXXX`
   - Pixel ID
   - Page ID
   - Currency (SGD, USD, MYR)
   - Business domain
   - Client name

2. **Add to `data/accounts.json`:**
```json
{
  "client_new": {
    "account_id": "act_123456789",
    "client_name": "New Client Name",
    "currency": "SGD",
    "pixel_id": "987654321098765",
    "page_id": "123456789123456",
    "catalog_id": null,
    "domain": "client-website.com",
    "beneficiary_id": "3723515154528570",
    "active": true
  }
}
```

3. **Verify System User has access:**
```bash
python3 << 'EOF'
import os, requests
from dotenv import load_dotenv

load_dotenv()
token = os.getenv('META_ACCESS_TOKEN')
account_id = "act_123456789"  # Replace with actual

url = f"https://graph.facebook.com/v18.0/{account_id}"
params = {'access_token': token, 'fields': 'id,name,currency'}
response = requests.get(url, params=params)
print(response.json())
EOF
```

4. **Create test campaign config:**
```yaml
# configs/test_new_client.yaml
campaign_id: "new_client_test_001"
client_account_id: "client_new"  # Matches key in accounts.json
name: "New Client - Test Campaign"
daily_budget: 1000
# ... rest of config ...
```

5. **Test campaign creation:**
```bash
curl -X POST "http://localhost:8000/api/v1/campaigns" \
  -H "Content-Type: application/json" \
  -d '{"config_path": "configs/test_new_client.yaml"}'
```

---

### Task 4: Modifying Advantage+ Configuration

**Example:** Change targeting to include age 13-17

**Location:** `meta/campaign.py`, AdSet creation section

**Current code:**
```python
'targeting': {
    'age_min': 18,
    'age_max': 65,
    'geo_locations': geo_locations,
    'targeting_automation': {
        'advantage_audience': 1,
        'individual_setting': {
            'age': 1,
            'gender': 1
        }
    }
}
```

**Modified code:**
```python
# Get age range from config or use defaults
age_min = campaign_config.get('targeting', {}).get('age_min', 18)
age_max = campaign_config.get('targeting', {}).get('age_max', 65)

'targeting': {
    'age_min': age_min,  # Now configurable
    'age_max': age_max,
    'geo_locations': geo_locations,
    'targeting_automation': {
        'advantage_audience': 1,
        'individual_setting': {
            'age': 1,
            'gender': 1
        }
    }
}
```

**Update YAML schema:**
```yaml
# In campaign config
targeting:  # optional
  age_min: 13
  age_max: 17
```

**Test with younger audience:**
- Create campaign with age_min: 13
- Verify in Meta Ads Manager targeting settings

---

## Code Patterns

### Hybrid Meta API Usage

**When to use SDK vs Direct API:**

| Operation | Use | Rationale |
|-----------|-----|-----------|
| Upload video | Direct API | Better file handling |
| Create campaign/adset/ad | SDK | Less boilerplate |
| Update status | Direct API | Simple single-field update |
| Fetch data | Direct API | Simple GET with field selection |

**SDK Pattern:**
```python
from facebook_business.adobjects.adaccount import AdAccount

def create_campaign_sdk(account_id: str, params: dict) -> dict:
    """Use SDK for structured operations."""
    account = AdAccount(f'act_{account_id}')
    campaign = account.create_campaign(params=params)
    return campaign.export_all_data()
```

**Direct API Pattern:**
```python
import requests

def update_status_api(campaign_id: str, status: str, token: str) -> dict:
    """Use direct API for simple updates."""
    url = f"https://graph.facebook.com/v18.0/{campaign_id}"
    data = {'status': status, 'access_token': token}
    response = requests.post(url, data=data)
    return response.json()
```

---

### Error Handling Pattern

**Always use try-except with specific exceptions:**

```python
from utils.exceptions import MetaAPIError, ValidationError
from utils.logger import setup_logger

logger = setup_logger(__name__)

def create_campaign(config: dict):
    try:
        # Validate first
        validate_campaign_config(config)

        # Then execute
        result = meta_api_call(config)

        logger.info(f"Campaign created: {result['id']}")
        return result

    except ValidationError as e:
        logger.error(f"Validation failed: {e}")
        raise HTTPException(status_code=400, detail=str(e))

    except MetaAPIError as e:
        logger.error(f"Meta API error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")
```

---

### Retry Logic Pattern

**Use tenacity for API calls:**

```python
from tenacity import retry, stop_after_attempt, wait_exponential

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=10)
)
def upload_video_with_retry(account_id: str, video_path: str) -> str:
    """Upload video with automatic retry on transient errors."""
    return upload_video(account_id, video_path)
```

**When to retry:**
- ✅ 500, 503 errors (server issues)
- ✅ Network timeouts
- ✅ Rate limit errors (with backoff)
- ❌ 400 errors (validation errors - won't fix with retry)
- ❌ 401/403 errors (auth errors - won't fix with retry)

---

### File Storage Pattern

**Atomic writes to prevent corruption:**

```python
import json
from pathlib import Path
import tempfile
import shutil

def atomic_write(file_path: Path, data: dict):
    """Write to temp file, then rename (atomic on POSIX)."""
    # Write to temporary file
    with tempfile.NamedTemporaryFile(
        mode='w',
        dir=file_path.parent,
        delete=False
    ) as tmp_file:
        json.dump(data, tmp_file, indent=2)
        tmp_path = Path(tmp_file.name)

    # Atomic rename
    shutil.move(str(tmp_path), str(file_path))
```

---

## Testing Strategy

### Testing with Real Ad Accounts

**CRITICAL:** This project uses REAL Meta ad accounts. All tests create actual campaigns.

**Safety precautions:**
1. Always create campaigns with `status='PAUSED'`
2. Use minimal budgets (100-1000 cents)
3. Test with dedicated test ad account if available
4. Verify in Meta Ads Manager before activating
5. Delete test campaigns after verification

### Manual Testing Workflow

**For new features:**

1. **Create test config:**
```yaml
campaign_id: "dev_test_feature_001"
client_account_id: "test_account"
name: "DEV TEST - Feature Name"
daily_budget: 100  # Minimum
# ... rest of config
```

2. **Test creation:**
```bash
curl -X POST "http://localhost:8000/api/v1/campaigns" \
  -H "Content-Type: application/json" \
  -d '{"config_path": "configs/dev_test.yaml"}' | jq '.'
```

3. **Verify in Meta:**
- Go to Meta Ads Manager
- Check campaign created correctly
- Verify all fields match expectations

4. **Test edge cases:**
- Invalid input
- Missing required fields
- Network failures (disconnect WiFi mid-creation)

5. **Clean up:**
- Delete test campaign from Meta Ads Manager
- Remove from `data/campaigns.json`

### Future: Automated Testing

**When implementing pytest:**

```python
# tests/test_campaign.py
import pytest
from meta.campaign import create_advantage_plus_campaign

@pytest.fixture
def mock_meta_client():
    """Mock Meta API client to avoid real API calls."""
    # Return mock client
    pass

def test_campaign_creation(mock_meta_client):
    """Test campaign creation logic without hitting real API."""
    # Test logic here
    pass
```

**Note:** Automated testing not implemented in MVP. All testing is manual with real accounts.

---

## Best Practices

### Code Style

**Follow Python conventions:**
- PEP 8 style guide
- Type hints for function parameters
- Docstrings for all functions
- Clear variable names

**Example:**
```python
from typing import Dict, Any, Optional
from datetime import datetime

def create_campaign(
    client: MetaAPIClient,
    account_id: str,
    config: Dict[str, Any],
    start_time: Optional[datetime] = None
) -> Dict[str, str]:
    """Create Meta Advantage+ Sales campaign.

    Args:
        client: Meta API client instance
        account_id: Ad account ID (with act_ prefix)
        config: Campaign configuration dictionary
        start_time: Optional start time in GMT+8

    Returns:
        dict: Created campaign IDs (campaign_id, adset_id, ad_id)

    Raises:
        ValidationError: If config is invalid
        MetaAPIError: If API call fails
    """
    # Implementation
```

---

### Security Considerations

**DO:**
- ✅ Store tokens in environment variables only
- ✅ Use `.gitignore` for `.env` and `data/` directory
- ✅ Use system user tokens (never personal tokens)
- ✅ Log sanitized data (never full tokens)
- ✅ Set restrictive permissions: `chmod 600 .env`
- ✅ Validate all user input before Meta API calls

**DON'T:**
- ❌ Commit `.env` file
- ❌ Commit `data/` directory (contains account details)
- ❌ Commit `creatives/` directory (client videos)
- ❌ Log full access tokens
- ❌ Use personal user access tokens
- ❌ Hardcode credentials in source code

---

### Logging Guidelines

**Use structured logging:**

```python
from utils.logger import setup_logger

logger = setup_logger(__name__)

# Good logging
logger.info(f"Creating campaign: {campaign_name}")
logger.info(f"Video uploaded: {video_id}")
logger.error(f"Campaign creation failed: {error_message}")

# Bad logging
print("Creating campaign...")  # Don't use print()
logger.debug("Debug info")  # Avoid excessive debug logs
```

**Log levels:**
- `ERROR`: Failures that require attention
- `WARNING`: Potential issues, degraded functionality
- `INFO`: Normal operations, key events
- `DEBUG`: Detailed information (use sparingly)

**What to log:**
- Campaign creation start/completion
- Meta API calls (without tokens)
- Validation failures
- Errors with context

**What NOT to log:**
- Full access tokens
- Sensitive client data
- Verbose debug info in production

---

## Debugging Tips

### Common Issues

**Issue: Campaign creation fails at step 3**
```bash
# Check what was created
cat data/campaigns.json | jq '.failed_campaign'

# Check Meta Ads Manager for orphaned resources
# Delete video_id and creative_id manually if needed
```

**Issue: Video upload timeout**
```bash
# Check video file size
ls -lh creatives/video.mp4

# Test upload manually
python3 << 'EOF'
from meta.client import MetaAPIClient
client = MetaAPIClient(token)
video_id = client.upload_video('act_123', 'creatives/video.mp4')
print(f"Video ID: {video_id}")
EOF
```

**Issue: Scheduled job didn't execute**
```bash
# Check if service was running
# Machine must stay awake for jobs

# Check job status
cat data/schedules.json | jq '.job_id'

# Check APScheduler logs
# Look for errors in console output
```

---

### Inspecting Meta API Responses

**Get detailed campaign info:**
```bash
python3 << 'EOF'
import os, requests
from dotenv import load_dotenv

load_dotenv()
token = os.getenv('META_ACCESS_TOKEN')
campaign_id = "123456789"

url = f"https://graph.facebook.com/v18.0/{campaign_id}"
params = {
    'access_token': token,
    'fields': 'id,name,status,objective,daily_budget,created_time'
}
response = requests.get(url, params=params)
print(response.json())
EOF
```

**Get adset info:**
```bash
adset_id="987654321"
curl "https://graph.facebook.com/v18.0/${adset_id}?fields=id,name,status,optimization_goal,targeting,start_time&access_token=${TOKEN}"
```

---

## Git Workflow

### Before Committing

**Check what you're committing:**
```bash
git status
git diff
```

**Ensure sensitive files excluded:**
```bash
# Should be gitignored
ls -la .env data/ creatives/

# Verify gitignore
cat .gitignore | grep -E "\.env|data/|creatives/"
```

**Commit message format:**
```bash
git commit -m "feat: Add end_date field to campaigns

- Update YAML schema with end_date
- Add validation for end_date > start_date
- Pass end_time to Meta API adset creation
- Test with new config file

Refs: #123"
```

---

## Performance Optimization

### Current Status (MVP)
- No optimization implemented
- Sequential processing
- No caching
- Fresh Meta API calls on every GET

### Future Optimizations (Post-MVP)
- Concurrent campaign creation
- Cache frequently accessed data (accounts, configs)
- Rate limiting to avoid Meta API throttling
- Background job queue for heavy operations

---

## Notes for Future Developers

### This is an MVP
- Keep it simple - no over-engineering
- File-based storage is intentional (not a limitation to "fix")
- Local development only - no deployment needed yet
- Manual sync is intentional - no background polling yet

### Key Constraints
- Real ad accounts for testing - be careful
- Machine must stay running for scheduled campaigns
- All times in GMT+8 (Singapore)
- Multi-currency support (SGD, USD, MYR)
- System User can only access user's BM entities

### Post-MVP Features (Deferred)
Do not implement unless explicitly requested:
- Campaign editing (update existing campaigns)
- Multi-video/carousel support
- Image ads
- Email notifications
- Web UI
- Database migration
- Automatic background sync polling

---

## Getting Help

**If stuck:**

1. Check `/docs/06_TROUBLESHOOTING.md` for common issues
2. Check `/docs/07_WORKFLOWS.md` for usage examples
3. Review Meta Marketing API docs: https://developers.facebook.com/docs/marketing-apis
4. Inspect Meta API responses directly with curl
5. Check Meta platform status: https://developers.facebook.com/status
6. Review logs for specific error messages

**Useful Meta API documentation:**
- Campaign creation: https://developers.facebook.com/docs/marketing-api/reference/ad-campaign-group
- AdSet creation: https://developers.facebook.com/docs/marketing-api/reference/ad-campaign
- Advantage+ Sales: https://developers.facebook.com/docs/marketing-api/advantage-plus-sales
- Error codes: https://developers.facebook.com/docs/graph-api/using-graph-api/error-handling
