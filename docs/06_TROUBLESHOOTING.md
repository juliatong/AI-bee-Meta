# Troubleshooting Guide

## Quick Diagnosis

### Check System Health

```bash
# 1. Is service running?
curl http://localhost:8000/docs
# Should return HTML (Swagger UI)

# 2. Can reach Meta API?
curl https://graph.facebook.com/v18.0/
# Should return: {"error": ... } (expected without token)

# 3. Is token valid?
python3 << 'EOF'
import os, requests
from dotenv import load_dotenv
load_dotenv()
token = os.getenv('META_ACCESS_TOKEN')
r = requests.get(f"https://graph.facebook.com/v18.0/me?access_token={token}")
print("✓ Token valid" if r.status_code == 200 else f"✗ Token invalid: {r.json()}")
EOF

# 4. Check data files
ls -lh data/
# Should see: accounts.json, campaigns.json, schedules.json

# 5. Check scheduler
ls -lh data/*.db
# Should see: jobs.db (after first scheduled campaign)
```

---

## Campaign Creation Issues

### Error: "Video file not found"

**Symptoms:**
```json
{
  "error": "FileNotFoundError",
  "message": "Video not found: creatives/video.mp4"
}
```

**Causes:**
1. Video file path in YAML is incorrect
2. Video file doesn't exist
3. File path not relative to project root

**Solutions:**
```bash
# Check file exists
ls -lh creatives/

# Verify path in YAML
cat configs/your_campaign.yaml | grep file_path

# Ensure path is relative to project root
# Correct: "creatives/video.mp4"
# Wrong: "/Users/julia/creatives/video.mp4"
# Wrong: "./creatives/video.mp4"
```

---

### Error: "Video file too large"

**Symptoms:**
```json
{
  "error": "ValueError",
  "message": "Video too large: 4500.5MB. Max 4096MB"
}
```

**Solutions:**
```bash
# Check video size
ls -lh creatives/your_video.mp4

# Compress video (requires ffmpeg)
ffmpeg -i creatives/large_video.mp4 \
  -vcodec libx264 -crf 28 \
  creatives/compressed_video.mp4

# Or use lower resolution
ffmpeg -i creatives/large_video.mp4 \
  -vf scale=1920:1080 \
  creatives/hd_video.mp4
```

---

### Error: "Unsupported video format"

**Symptoms:**
```json
{
  "error": "ValueError",
  "message": "Unsupported format: .avi. Use .mp4 or .mov"
}
```

**Solutions:**
```bash
# Convert to MP4 (requires ffmpeg)
ffmpeg -i creatives/video.avi creatives/video.mp4

# Or convert to MOV
ffmpeg -i creatives/video.avi -c:v libx264 creatives/video.mov
```

---

### Error: "Account not found"

**Symptoms:**
```json
{
  "error": "KeyError",
  "message": "Account acct_123 not found"
}
```

**Causes:**
1. `client_account_id` in YAML doesn't match key in accounts.json
2. Account not configured in accounts.json

**Solutions:**
```bash
# Check accounts.json
cat data/accounts.json | jq 'keys'

# Verify YAML references correct account
cat configs/your_campaign.yaml | grep client_account_id

# Add account if missing
# Edit data/accounts.json
```

---

### Error: "Meta API Error: (#100) Invalid parameter"

**Symptoms:**
```json
{
  "error": "MetaAPIError",
  "message": "Meta API Error: (#100) Invalid parameter",
  "details": {...}
}
```

**Common Causes & Solutions:**

**1. Invalid Pixel ID**
```bash
# Verify pixel ID in Meta Events Manager
# Check accounts.json has correct pixel_id
cat data/accounts.json | jq '.acct_xxx.pixel_id'
```

**2. Invalid Page ID**
```bash
# Verify page ID
# Go to Facebook page → About → Page ID
# Update accounts.json with correct page_id
```

**3. Invalid Ad Account ID**
```bash
# Verify format: act_XXXXX (must include "act_" prefix)
cat data/accounts.json | jq '.acct_xxx.account_id'

# Check in Meta Ads Manager URL
# Should be: adsmanager.facebook.com/...?act=123456789
# In config: "act_123456789"
```

**4. Budget too low**
```bash
# Check minimum budget for your currency/country
# SGD minimum: ~$1.00 = 100 cents
# USD minimum: ~$1.00 = 100 cents

# Update YAML with higher budget
# Example: daily_budget: 1000  # $10.00
```

---

### Error: "Meta API Error: (#190) Access token expired"

**Symptoms:**
```json
{
  "error": "MetaAPIError",
  "message": "Meta API Error: (#190) Access token has expired"
}
```

**Solutions:**
1. Generate new system user token
2. Update .env file
3. Restart service

```bash
# Update .env
nano .env
# Replace META_ACCESS_TOKEN value

# Restart service
# Press Ctrl+C to stop
# Then: uvicorn main:app --reload
```

---

### Error: "Meta API Error: (#283) Requires business_management permission"

**Symptoms:**
```json
{
  "error": "MetaAPIError",
  "message": "Meta API Error: (#283) Missing permission"
}
```

**Solutions:**
1. Check system user token has correct scopes
2. Regenerate token with proper permissions

**Required scopes:**
- `business_management`
- `ads_management`
- `ads_read`

```bash
# Go to Business Manager → System Users → Your System User
# Click "Generate New Token"
# Select all 3 required scopes
# Copy new token to .env
```

---

### Error: "Meta API Error: (#200) Does not have permission to access this object"

**Symptoms:**
```json
{
  "error": "MetaAPIError",
  "message": "Meta API Error: (#200) Insufficient permissions"
}
```

**Causes:**
1. System user not assigned to ad account
2. Wrong permission level on ad account

**Solutions:**
```bash
# Go to Business Manager → System Users → Your System User
# Click "Add Assets" → Ad Accounts
# Select missing ad account
# Permission: "Manage Campaigns"
# Save and wait 5 minutes for propagation
```

---

### Error: Campaign created but shows "Campaign Rejected" in Ads Manager

**Symptoms:**
- Campaign created successfully via API
- Shows as "Rejected" in Meta Ads Manager

**Causes:**
1. Ad copy violates Meta policies
2. Landing page issues
3. Image/video content issues
4. Targeting restrictions

**Solutions:**
```bash
# Check rejection reason in Ads Manager
# Common issues:

# 1. Landing page not accessible
curl -I https://your-landing-page.com
# Should return 200 OK

# 2. Missing privacy policy
# Ensure website has privacy policy linked

# 3. Ad copy issues
# Review Meta advertising policies
# Avoid: excessive capitalization, claims, etc.

# 4. Resubmit after fixing
# Edit campaign in Ads Manager
# Request review
```

---

## Scheduling Issues

### Error: "Scheduled time in the past"

**Symptoms:**
```json
{
  "error": "ValidationError",
  "message": "Scheduled activation time must be in the future"
}
```

**Solutions:**
```bash
# Check current time (GMT+8)
TZ='Asia/Singapore' date

# Update YAML with future time
# Format: "YYYY-MM-DDTHH:MM:SS"
# Example: "2024-03-15T10:00:00" (10 AM Singapore time)
```

---

### Issue: Scheduled campaign didn't activate

**Symptoms:**
- Campaign still PAUSED after scheduled time
- No error in logs

**Diagnosis:**
```bash
# 1. Check if job exists
cat data/schedules.json | jq '.'

# 2. Check job status
cat data/schedules.json | jq '.[] | select(.campaign_id=="your_campaign_id")'

# 3. Check service was running
# Did laptop sleep? Was service stopped?

# 4. Check system time
TZ='Asia/Singapore' date
# Should match expected time zone
```

**Solutions:**

**If service was stopped:**
```bash
# Reschedule campaign
curl -X POST "http://localhost:8000/api/v1/campaigns/your_campaign_id/schedule" \
  -H "Content-Type: application/json" \
  -d '{"activate_at": "2024-03-15T11:00:00"}'
```

**If job failed:**
```bash
# Check error in schedules.json
cat data/schedules.json | jq '.[] | select(.status=="failed")'

# Manual activation
curl -X POST "http://localhost:8000/api/v1/campaigns/your_campaign_id/activate"
```

**Prevent future issues:**
- Keep laptop awake during scheduled times
- Use `caffeinate` on macOS: `caffeinate -i`
- Or deploy to always-on server

---

### Issue: Multiple campaigns scheduled for same time

**Symptoms:**
- Multiple campaigns should activate at same time
- Only some activate

**Cause:**
APScheduler default max workers: 10 (should be sufficient)

**Diagnosis:**
```bash
# Check how many jobs scheduled for same time
cat data/schedules.json | jq '[.[] | select(.scheduled_time=="2024-03-15T08:00:00")] | length'
```

**Solution:**
If >10 campaigns at exact same time, stagger by 1 minute:
```yaml
# Campaign 1
schedule:
  activate_at: "2024-03-15T08:00:00"

# Campaign 2
schedule:
  activate_at: "2024-03-15T08:01:00"

# Campaign 3
schedule:
  activate_at: "2024-03-15T08:02:00"
```

---

### Error: "No beneficiary information for Singapore ads"

**Symptoms:**
```json
{
  "error": "MetaAPIError",
  "message": "Beneficiary is missing: Provide a verified beneficiary",
  "error_subcode": 3858548
}
```

**Cause:**
Singapore regulations require beneficiary information for ads targeting Singapore audiences.

**CRITICAL Understanding:**

System Users can only access entities within their own Business Manager, not partner BM entities.

**Your BM Structure:**
- User's BM: `3723515154528570` (Adrite) - Owns System User
- Partner BM: `828723616406567` (PARTIPOST PTE. LTD.) - Partner relationship

**Why Partner BM Beneficiary Fails:**
- System User created under your BM
- Cannot access partner BM entity `828723616406567`
- Even though ad accounts are shared, entity access is restricted
- This is a **Meta platform limitation**

**Solution:**

Use your own Business Manager ID as beneficiary:

```json
// In data/accounts.json
{
  "acct_iflytek": {
    "account_id": "act_846944580625589",
    "beneficiary_id": "3723515154528570"  // Your BM, NOT partner BM
  }
}
```

**Why This Works:**
- ✅ Your BM is accessible to System User
- ✅ Satisfies Singapore compliance requirements
- ✅ Ensures API spend credits to your BM (Tech Partner goals)
- ✅ Functionally equivalent to partner BM for compliance

**Alternative (Not Recommended):**
Create separate System User in partner BM - but this credits API spend to partner instead of you.

**Verification:**
```bash
# Check beneficiary configuration
cat data/accounts.json | jq '.acct_xxx.beneficiary_id'

# Should show your BM ID: "3723515154528570"
# NOT partner BM ID: "828723616406567"
```

---

## Sync Issues

### Issue: Sync shows no changes but campaign was edited in Ads Manager

**Diagnosis:**
```bash
# Check last sync time
cat data/campaigns.json | jq '.your_campaign_id.last_synced'

# Fetch directly from Meta
curl "https://graph.facebook.com/v18.0/CAMPAIGN_ID?fields=name,status,daily_budget&access_token=YOUR_TOKEN"
```

**Possible Causes:**
1. Sync endpoint not updating local storage
2. Wrong campaign ID being fetched
3. Meta API delay in reflecting changes

**Solutions:**
```bash
# Force sync
curl -X POST "http://localhost:8000/api/v1/campaigns/your_campaign_id/sync"

# Wait 1 minute, try again
sleep 60
curl -X POST "http://localhost:8000/api/v1/campaigns/your_campaign_id/sync"

# Check response for actual changes
```

---

## Data Corruption Issues

### Error: "JSON decode error"

**Symptoms:**
```
json.decoder.JSONDecodeError: Expecting value: line 1 column 1 (char 0)
```

**Causes:**
1. Corrupted JSON file
2. Empty or incomplete file
3. Manual edit error

**Solutions:**
```bash
# 1. Validate JSON
cat data/campaigns.json | jq '.'
# If error, JSON is corrupted

# 2. Restore from backup
cp data/campaigns.json data/campaigns.json.broken
cp data/campaigns.json.backup data/campaigns.json

# 3. If no backup, rebuild
echo '{}' > data/campaigns.json
# Note: Lost campaign tracking data
```

**Prevention:**
```bash
# Create backup before manual edits
cp data/campaigns.json data/campaigns.json.backup

# Use jq for safe edits
jq '.new_campaign = {...}' data/campaigns.json > data/campaigns.json.new
mv data/campaigns.json.new data/campaigns.json
```

---

### Issue: Lost scheduling data after restart

**Diagnosis:**
```bash
# Check if jobs.db exists
ls -lh data/jobs.db

# Check schedules.json
cat data/schedules.json | jq 'length'
```

**Causes:**
1. jobs.db deleted
2. schedules.json corrupted

**Solutions:**

**If jobs.db missing:**
```bash
# Scheduler will recreate it
# But scheduled jobs are lost
# Reschedule campaigns manually
```

**If schedules.json corrupted:**
```bash
# Restore from backup
cp data/schedules.json.backup data/schedules.json

# Or rebuild from Meta data
# Query Meta for all campaigns
# Reschedule as needed
```

---

## Performance Issues

### Issue: Campaign creation very slow (>60 seconds)

**Expected Time:** 10-30 seconds per campaign

**Diagnosis:**
```bash
# Test Meta API latency
time curl "https://graph.facebook.com/v18.0/me?access_token=YOUR_TOKEN"
# Should be <1 second

# Test video upload specifically
# Check video file size
ls -lh creatives/your_video.mp4
```

**Common Causes:**

**1. Large video file**
```bash
# If >500MB, upload takes longer
# Compress video or use smaller file for testing
```

**2. Network latency**
```bash
# Test connection
ping graph.facebook.com
# Should be <100ms
```

**3. Meta API slowdown**
```bash
# Check Meta API status
# https://developers.facebook.com/status
```

---

### Issue: API service crashes or restarts

**Symptoms:**
- Service stops unexpectedly
- "Connection refused" errors

**Diagnosis:**
```bash
# Check if process running
ps aux | grep uvicorn

# Check for errors
tail -f /var/log/system.log | grep python
```

**Common Causes:**

**1. Out of memory**
```bash
# Check memory usage
top -l 1 | grep PhysMem
# If swap is high, system is low on memory
```

**2. Unhandled exception**
```bash
# Check logs for stack trace
# Look for last error before crash
```

**Solutions:**
```bash
# Add automatic restart (development)
while true; do
    uvicorn main:app --reload
    echo "Service crashed. Restarting in 5 seconds..."
    sleep 5
done
```

---

## Network Issues

### Error: "Connection timeout to Meta API"

**Symptoms:**
```
requests.exceptions.Timeout: HTTPSConnectionPool...
```

**Solutions:**
```bash
# 1. Check internet connection
ping 8.8.8.8

# 2. Check DNS
nslookup graph.facebook.com

# 3. Check firewall
# Ensure port 443 (HTTPS) is not blocked

# 4. Test with curl
curl -v https://graph.facebook.com/v18.0/

# 5. If behind proxy, configure
export HTTPS_PROXY=http://proxy:port
```

---

### Error: SSL certificate verification failed

**Symptoms:**
```
ssl.SSLError: [SSL: CERTIFICATE_VERIFY_FAILED]
```

**Causes:**
1. System certificates outdated
2. Corporate proxy interfering

**Solutions:**

**macOS:**
```bash
# Install certificates
/Applications/Python\ 3.9/Install\ Certificates.command
```

**Linux:**
```bash
# Update ca-certificates
sudo apt-get update
sudo apt-get install ca-certificates
```

**Temporary workaround (NOT RECOMMENDED):**
```python
# In client.py (development only)
import urllib3
urllib3.disable_warnings()
# verify=False in requests
```

---

## Common User Errors

### Error: "Campaign already exists"

**Symptoms:**
```json
{
  "error": "ValueError",
  "message": "Campaign test_001 already exists"
}
```

**Cause:**
Campaign with same `campaign_id` already created

**Solutions:**
```bash
# Use different campaign_id in YAML
# Example: test_001 → test_002

# Or check existing campaigns
cat data/campaigns.json | jq 'keys'

# Delete old campaign from tracking (doesn't delete from Meta)
jq 'del(.test_001)' data/campaigns.json > data/campaigns.json.new
mv data/campaigns.json.new data/campaigns.json
```

---

### Error: "Invalid datetime format"

**Symptoms:**
```json
{
  "error": "ValidationError",
  "message": "Invalid datetime format"
}
```

**Cause:**
Wrong datetime format in YAML

**Solution:**
```yaml
# Wrong formats:
activate_at: "2024-03-15"  # Missing time
activate_at: "15/03/2024 08:00"  # Wrong format
activate_at: "2024-03-15 08:00:00"  # Space instead of T

# Correct format:
activate_at: "2024-03-15T08:00:00"  # ISO 8601
```

---

## Getting More Help

### Enable Debug Logging

```python
# In utils/logger.py
import logging
logging.basicConfig(
    level=logging.DEBUG,  # Change from INFO to DEBUG
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
```

### Capture Full Request/Response

```python
# In meta/client.py
def api_call_with_logging(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        logger.debug(f"Request: {args}, {kwargs}")
        result = func(*args, **kwargs)
        logger.debug(f"Response: {result}")
        return result
    return wrapper
```

### Test Individual Components

```bash
# Test storage layer
python3 << 'EOF'
from storage.file_store import FileStore
store = FileStore('data')
print(store.load('accounts.json'))
EOF

# Test Meta client
python3 << 'EOF'
from meta.client import MetaAPIClient
from config.loader import settings
client = MetaAPIClient(settings.meta_access_token)
accounts = client.get_accounts()
print(accounts)
EOF
```

---

## Emergency Recovery

### Complete Data Loss

```bash
# 1. Restore from backups
cp ~/backups/meta-automation/data_latest.tar.gz .
tar -xzf data_latest.tar.gz

# 2. If no backups, rebuild accounts.json manually
# Fetch from Meta
curl "https://graph.facebook.com/v18.0/me/adaccounts?fields=name,account_id,currency&access_token=YOUR_TOKEN"

# 3. Recreate campaigns.json from Meta
# Query all campaigns per account
# Manually add to campaigns.json
```

### Service Won't Start

```bash
# 1. Remove virtual environment
rm -rf venv/

# 2. Recreate
python3 -m venv venv
source venv/bin/activate

# 3. Reinstall dependencies
pip install -r requirements.txt

# 4. Restart service
uvicorn main:app --reload
```

---

## Contact & Resources

**Meta Support:**
- [Meta Business Help Center](https://www.facebook.com/business/help)
- [Meta Developer Documentation](https://developers.facebook.com/docs/marketing-apis)

**API Status:**
- [Meta Platform Status](https://developers.facebook.com/status)

**Community:**
- [Meta Marketing API Forum](https://developers.facebook.com/community)

---

## Known Limitations (Not Bugs)

1. **Machine must stay running** - Scheduled campaigns won't activate if laptop sleeps
2. **Manual sync required** - No automatic background polling of Ads Manager
3. **No campaign editing** - Must create new campaign for changes (MVP limitation)
4. **Single user only** - No authentication or multi-user support
5. **File-based storage** - Not suitable for high concurrency or scale
6. **No rollback after activation** - Once campaign active, can't undo via system (must pause in Ads Manager)
