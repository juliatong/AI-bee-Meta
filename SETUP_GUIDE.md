# Environment Setup Guide

## ✅ Step 1: Dependencies Installed
All Python dependencies have been installed successfully.

---

## 🔑 Step 2: Configure Meta API Credentials

You need to get your Meta System User Access Token. Follow these steps:

### 2.1 Get System User Access Token

1. **Go to Meta Business Settings**: https://business.facebook.com/settings
2. **Navigate to**: Users → System Users
3. **Create or select** your system user (e.g., "Campaign Automation Bot")
4. **Generate Token**:
   - Click "Generate New Token"
   - Select your Meta App
   - Required permissions:
     - ✅ `business_management`
     - ✅ `ads_management`
     - ✅ `ads_read`
   - Set to **"Never Expire"** (for production use)
   - Copy the token

5. **Update `.env` file**:

```bash
# Edit the .env file
nano .env
```

Replace these lines:
```
META_ACCESS_TOKEN=PLACEHOLDER_TOKEN_REPLACE_WITH_YOUR_REAL_TOKEN
META_BUSINESS_MANAGER_ID=PLACEHOLDER_BM_ID_REPLACE_WITH_YOUR_REAL_ID
```

With your real credentials:
```
META_ACCESS_TOKEN=YOUR_ACTUAL_TOKEN_HERE
META_BUSINESS_MANAGER_ID=YOUR_BM_ID_HERE
```

### 2.2 Get Business Manager ID

- Go to Business Settings: https://business.facebook.com/settings
- Look at the URL - the number after `/business/settings/` is your BM ID
- Example: `https://business.facebook.com/settings/123456789012345` → BM ID is `123456789012345`

---

## 🏢 Step 3: Configure Test Ad Account

You need to configure at least one client ad account for testing.

### 3.1 Get Ad Account Details

1. **Go to Ads Manager**: https://adsmanager.facebook.com/
2. **Select your ad account**
3. **Note down these IDs**:
   - **Ad Account ID**: In the URL or top-left dropdown (format: `act_123456789`)
   - **Pixel ID**: Go to Events Manager → Data Sources → Your Pixel → Settings
   - **Page ID**: Go to your Facebook Page → About → Page ID (or check Page Settings)

### 3.2 Update `data/accounts.json`

```bash
# Edit the accounts file
nano data/accounts.json
```

Replace the placeholder values:

```json
{
  "acct_example": {
    "account_id": "act_YOUR_REAL_ACCOUNT_ID",
    "client_name": "Test Client",
    "currency": "SGD",
    "pixel_id": "YOUR_PIXEL_ID",
    "page_id": "YOUR_PAGE_ID",
    "catalog_id": null,
    "domain": "example.com",
    "active": true
  }
}
```

**Example with real format**:
```json
{
  "acct_test_client": {
    "account_id": "act_123456789012345",
    "client_name": "Test Client",
    "currency": "SGD",
    "pixel_id": "987654321098765",
    "page_id": "456789123456789",
    "catalog_id": null,
    "domain": "test-client.com",
    "active": true
  }
}
```

---

## 🎥 Step 4: Add Test Video

You need a test video file to create campaigns.

### 4.1 Video Requirements

- **Format**: MP4 or MOV
- **Max size**: 4GB (Meta limit)
- **Recommended aspect ratio**: 16:9 (mobile format)
- **Minimum duration**: 1 second
- **Recommended**: 15-60 seconds

### 4.2 Add Video File

1. Place your video in the `creatives/` folder:
```bash
cp /path/to/your/video.mp4 "creatives/test_video.mp4"
```

2. Update `configs/example_campaign.yaml`:
```bash
nano configs/example_campaign.yaml
```

Update these fields:
```yaml
campaign_id: "test_campaign_001"  # Change to unique ID
client_account_id: "acct_example"  # Match your accounts.json key
name: "Test Campaign - My First Campaign"

video:
  file_path: "creatives/test_video.mp4"  # Your video filename

primary_text: "Your ad copy goes here!"
headline: "Your Headline"
description: "Your description"
destination_url: "https://your-website.com"
```

---

## ✅ Step 5: Verify Setup

Once you've completed steps 2-4, verify your setup:

### 5.1 Check .env File
```bash
cat .env
```

Should show:
- Real token (not PLACEHOLDER)
- Real BM ID (not PLACEHOLDER)

### 5.2 Check accounts.json
```bash
cat data/accounts.json
```

Should show:
- Real ad account ID starting with `act_`
- Real Pixel ID (15-16 digits)
- Real Page ID (15-16 digits)

### 5.3 Check Video File
```bash
ls -lh creatives/
```

Should show your video file with size > 0

---

## 🚀 Step 6: Test API Server

Once everything is configured, start the API server:

```bash
cd "/Users/julia/Projects/AI bee"
python3 main.py
```

You should see:
```
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000
```

Visit http://localhost:8000/docs to see the API documentation.

---

## 🧪 Step 7: Test Campaign Creation

### Test with curl:

```bash
curl -X POST "http://localhost:8000/api/v1/campaigns" \
  -H "Content-Type: application/json" \
  -d '{"config_path": "configs/example_campaign.yaml"}'
```

### Or use the interactive API docs:
1. Go to http://localhost:8000/docs
2. Click on `POST /api/v1/campaigns`
3. Click "Try it out"
4. Enter: `{"config_path": "configs/example_campaign.yaml"}`
5. Click "Execute"

---

## 📋 Setup Checklist

- [ ] Step 1: Dependencies installed ✅ (Done!)
- [ ] Step 2: Meta API credentials configured in `.env`
- [ ] Step 3: Ad account details configured in `data/accounts.json`
- [ ] Step 4: Test video added to `creatives/` folder
- [ ] Step 5: Campaign config updated in `configs/example_campaign.yaml`
- [ ] Step 6: API server starts successfully
- [ ] Step 7: Test campaign creation works

---

## 🆘 Troubleshooting

### Issue: "Meta API Error"
- Check your access token is valid
- Verify token has correct permissions (ads_management, ads_read, business_management)
- Check ad account ID format starts with `act_`

### Issue: "Video file not found"
- Check file path in YAML config is correct
- Verify video file exists: `ls -la creatives/`

### Issue: "Account not found"
- Verify `client_account_id` in YAML matches a key in `accounts.json`
- Check spelling and capitalization

### Issue: "Import errors"
- Make sure you're in the project directory
- Verify all dependencies installed: `pip3 list | grep fastapi`

---

## 📚 Next Steps After Setup

Once your setup is complete and you can create campaigns:

1. **Phase 5: Implement Scheduler** - Add campaign scheduling functionality
2. **Test scheduling** - Schedule campaigns for future activation
3. **Polish & Error Handling** - Improve error messages and edge cases

---

**Current Status**: Step 1 complete, waiting for Steps 2-4 configuration.

Let me know when you've completed the configuration steps and I can help you test!
