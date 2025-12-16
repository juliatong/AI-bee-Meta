# Quick Start - Minimal Setup for Testing

This guide shows the **absolute minimum** you need to test the API.

---

## ⚡ 3-Minute Setup

### 1. Configure Meta API Credentials (2 minutes)

Edit `.env` file:
```bash
nano .env
```

Replace these two lines with your real values:
```
META_ACCESS_TOKEN=YOUR_REAL_TOKEN_HERE
META_BUSINESS_MANAGER_ID=YOUR_REAL_BM_ID_HERE
```

**Where to get these:**
- Token: Business Settings → System Users → Generate Token
- BM ID: Look at your Business Settings URL (the number)

---

### 2. Configure Ad Account (1 minute)

Edit `data/accounts.json`:
```bash
nano data/accounts.json
```

Replace these three IDs:
```json
{
  "acct_example": {
    "account_id": "act_YOUR_ACCOUNT_ID",
    "pixel_id": "YOUR_PIXEL_ID",
    "page_id": "YOUR_PAGE_ID",
    ...
  }
}
```

**Where to get these:**
- Account ID: Ads Manager URL or top-left dropdown (format: `act_123456789`)
- Pixel ID: Events Manager → Your Pixel (15-16 digits)
- Page ID: Your Facebook Page → About → Page ID

---

### 3. Add Test Video (30 seconds)

Copy a video file to the creatives folder:
```bash
cp /path/to/your/video.mp4 "creatives/test_video.mp4"
```

Update the video path in `configs/example_campaign.yaml`:
```bash
nano configs/example_campaign.yaml
```

Change line 11:
```yaml
  file_path: "creatives/test_video.mp4"
```

---

## 🚀 Test It!

### Start the API server:
```bash
cd "/Users/julia/Projects/AI bee"
python3 main.py
```

You should see:
```
INFO:     Uvicorn running on http://0.0.0.0:8000
```

### Run the test script (in a new terminal):
```bash
cd "/Users/julia/Projects/AI bee"
python3 test_api.py
```

The test script will:
- ✅ Test basic endpoints (health, root)
- ✅ Test account retrieval
- ⚠️  **Ask before creating a campaign** (so you don't accidentally create one)
- ✅ Test campaign status and sync
- ⚠️  **Ask before activating** (so you don't accidentally spend money)

---

## 🎯 Alternative: Manual Testing with curl

If you prefer to test manually:

### 1. Start server:
```bash
python3 main.py
```

### 2. Test health check:
```bash
curl http://localhost:8000/health
```

### 3. Create campaign:
```bash
curl -X POST "http://localhost:8000/api/v1/campaigns" \
  -H "Content-Type: application/json" \
  -d '{"config_path": "configs/example_campaign.yaml"}'
```

### 4. Use API docs (easiest):
Open in browser: http://localhost:8000/docs

---

## ✅ What You'll See When It Works

### Test Script Output:
```
======================================================================
  Meta Ad Campaign Automation - API Test Suite
======================================================================

✅ PASS  Health Check
✅ PASS  Root Endpoint
✅ PASS  Get Account

Run campaign creation test? (yes/no): yes

✅ Campaign created successfully!
   Internal ID: example_campaign_001
   Meta Campaign ID: 123456789
   Status: PAUSED

🔗 View in Ads Manager: https://...

📊 Results: 5/5 tests passed
```

### In Meta Ads Manager:
You'll see a new campaign with status **PAUSED** (not spending money).

---

## 🆘 Common Issues

### "MetaAPIError: Invalid token"
→ Check your `META_ACCESS_TOKEN` in `.env` is correct

### "Account not found: acct_example"
→ Make sure the `client_account_id` in YAML matches your `accounts.json` key

### "Video file not found"
→ Check the video file exists: `ls -la creatives/`

### "Connection refused"
→ Make sure the API server is running: `python3 main.py`

---

## 📝 Summary

**Before testing, you MUST configure:**
1. ✅ `.env` - Meta credentials
2. ✅ `data/accounts.json` - Ad account IDs
3. ✅ `creatives/` - Test video file

**Then test with:**
- `python3 test_api.py` (recommended - interactive)
- `curl` commands (manual)
- http://localhost:8000/docs (browser - easiest)

---

**Ready? Let's test! 🚀**
