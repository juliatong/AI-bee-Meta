# Setup Guide - First Time Installation

## Prerequisites

### System Requirements
- **OS:** macOS, Linux, or Windows
- **Python:** 3.9 or higher
- **Disk Space:** Minimum 500MB (more if storing many videos)
- **Network:** Stable internet connection for Meta API calls
- **Memory:** Minimum 2GB RAM available

### Meta Requirements
- Active Business Manager account
- Business Manager must own ad accounts (not shared access)
- Admin role in Business Manager
- Ad accounts must be active and not restricted
- Facebook page connected to ad account
- Meta pixel installed on client website

### Required Information Before Starting
- [ ] Business Manager ID
- [ ] Ad account ID(s) - format: `act_XXXXX`
- [ ] Pixel ID(s) per account
- [ ] Page ID(s) per account
- [ ] Account currency per account (SGD, USD, or MYR)

---

## Step 1: Meta System User Token Setup

### 1.1 Create System User

1. Go to [Meta Business Settings](https://business.facebook.com/settings)
2. Navigate to **Users** → **System Users**
3. Click **Add** button
4. Name: `Campaign Automation Bot` (or your preferred name)
5. Role: **Admin** (required for campaign management)
6. Click **Create System User**

### 1.2 Assign Ad Accounts

1. In system user settings, go to **Assigned Assets** tab
2. Click **Add Assets** → **Ad Accounts**
3. Select all relevant ad accounts
4. Permission level: **Manage Campaigns** (required)
5. Click **Save Changes**

**CRITICAL:** System user must have access to ALL ad accounts you plan to manage.

### 1.3 Generate Access Token

1. In system user settings, click **Generate New Token**
2. Select your app (or create new app if needed)
3. Select required permissions:
   - ✅ `business_management`
   - ✅ `ads_management`
   - ✅ `ads_read`
4. Token expiration: Select **Never Expire** (recommended for automation)
5. Click **Generate Token**
6. **IMPORTANT:** Copy token immediately - it won't be shown again
7. Store securely - you'll need this in Step 3

### 1.4 Verify Token

Test token works:
```bash
curl -X GET \
  "https://graph.facebook.com/v18.0/me/adaccounts?access_token=YOUR_TOKEN"
```

Expected response: List of ad accounts system user can access.

---

## Step 2: Project Setup

### 2.1 Clone/Create Project Directory

```bash
cd /Users/julia/Projects
mkdir "AI bee"  # Or your preferred name
cd "AI bee"
```

### 2.2 Create Python Virtual Environment

```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
# macOS/Linux:
source venv/bin/activate

# Windows:
venv\Scripts\activate
```

**Note:** Keep virtual environment activated for all subsequent steps.

### 2.3 Create Project Structure

```bash
# Create directories
mkdir -p api meta scheduler storage config utils data configs creatives docs

# Create __init__.py files
touch api/__init__.py meta/__init__.py scheduler/__init__.py \
      storage/__init__.py config/__init__.py utils/__init__.py

# Create data directory files (will be populated later)
mkdir -p data
touch data/.gitkeep

# Create creatives directory
mkdir -p creatives
touch creatives/.gitkeep

# Create configs directory
mkdir -p configs
touch configs/.gitkeep
```

### 2.4 Create requirements.txt

```bash
cat > requirements.txt << 'EOF'
fastapi==0.104.1
uvicorn[standard]==0.24.0
pydantic==2.5.0
pydantic-settings==2.1.0
facebook-business==18.0.0
apscheduler==3.10.4
pyyaml==6.0.1
python-dotenv==1.0.0
requests==2.31.0
tenacity==8.2.3
EOF
```

### 2.5 Install Dependencies

```bash
pip install -r requirements.txt
```

**Verify installation:**
```bash
pip list | grep -E "fastapi|facebook-business|apscheduler"
```

Should show all packages installed.

---

## Step 3: Environment Configuration

### 3.1 Create .env File

```bash
cat > .env << 'EOF'
# Meta API Configuration
META_ACCESS_TOKEN=your_system_user_token_here
META_BUSINESS_MANAGER_ID=your_business_manager_id_here

# Optional: Development Settings
LOG_LEVEL=INFO
API_HOST=0.0.0.0
API_PORT=8000
EOF
```

### 3.2 Update .env with Your Values

Edit `.env` and replace:
- `your_system_user_token_here` → Token from Step 1.3
- `your_business_manager_id_here` → Your Business Manager ID

**Find Business Manager ID:**
1. Go to Business Settings
2. URL will be: `https://business.facebook.com/settings/info?business_id=XXXXX`
3. Copy the numeric ID

### 3.3 Secure .env File

```bash
# Set restrictive permissions (macOS/Linux)
chmod 600 .env

# Verify it's gitignored
echo ".env" >> .gitignore
```

**NEVER commit .env to git!**

---

## Step 4: Account Configuration

### 4.1 Create accounts.json

```bash
cat > data/accounts.json << 'EOF'
{
  "acct_test": {
    "account_id": "act_XXXXX",
    "client_name": "Test Client",
    "currency": "SGD",
    "pixel_id": "XXXXX",
    "page_id": "XXXXX",
    "catalog_id": null,
    "domain": null,
    "active": true
  }
}
EOF
```

### 4.2 Update with Real Account Data

For each client ad account, gather:

**Ad Account ID:**
- Go to Meta Ads Manager
- Look at URL: `https://adsmanager.facebook.com/adsmanager/manage/campaigns?act=123456789`
- Account ID is: `act_123456789`

**Pixel ID:**
- Go to Events Manager
- Select pixel
- Settings → Pixel ID

**Page ID:**
- Go to your Facebook page
- About section → Page ID
- Or check URL when on page: `facebook.com/XXXXX`

**Currency:**
- Go to Ad Account Settings
- Currency is set at account creation (cannot change)
- Common: SGD, USD, MYR

**Example with real data:**
```json
{
  "client_sg_main": {
    "account_id": "act_123456789",
    "client_name": "Singapore Client A",
    "currency": "SGD",
    "pixel_id": "987654321098765",
    "page_id": "123456789123456",
    "catalog_id": null,
    "domain": "client-a.com",
    "active": true
  },
  "client_us_main": {
    "account_id": "act_987654321",
    "client_name": "US Client B",
    "currency": "USD",
    "pixel_id": "456789123456789",
    "page_id": "789123456789123",
    "catalog_id": "111222333444555",
    "domain": "client-b.com",
    "active": true
  }
}
```

---

## Step 5: Initial Data Files

### 5.1 Create Empty Data Files

```bash
# campaigns.json - will be populated as campaigns created
echo '{}' > data/campaigns.json

# schedules.json - will be populated as campaigns scheduled
echo '{}' > data/schedules.json

# jobs.db will be created automatically by APScheduler
```

### 5.2 Create Example Campaign Config

```bash
cat > configs/example_campaign.yaml << 'EOF'
# Example campaign configuration
campaign_id: "test_campaign_001"
client_account_id: "acct_test"  # Must match key in accounts.json
name: "Test Campaign - Do Not Activate"
daily_budget: 1000  # SGD 10.00 in cents

video:
  file_path: "creatives/test_video.mp4"

primary_text: "This is a test campaign. Do not activate."
headline: "Test Only"
description: "Testing campaign creation"
call_to_action: "LEARN_MORE"

destination_url: "https://example.com/test"
url_parameters: "utm_source=facebook&utm_campaign=test"

# Do not include schedule - will create as PAUSED only
EOF
```

---

## Step 6: Prepare Test Video

### 6.1 Get Test Video

**Requirements:**
- Format: MP4 or MOV
- Aspect ratio: 16:9 (1920x1080 recommended)
- Size: Under 4GB
- Duration: Recommended 15-60 seconds

### 6.2 Place in Creatives Directory

```bash
# Copy your test video
cp /path/to/your/test_video.mp4 creatives/test_video.mp4

# Verify file
ls -lh creatives/test_video.mp4
```

**IMPORTANT:** Start with LOW BUDGET test video for first campaign.

---

## Step 7: Create .gitignore

```bash
cat > .gitignore << 'EOF'
# Environment
.env
venv/
__pycache__/
*.pyc
*.pyo
*.pyd
.Python

# Data files (contain sensitive info)
data/
!data/.gitkeep

# Creative files (large, client-owned)
creatives/
!creatives/.gitkeep

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Logs
*.log

# APScheduler
*.db

# Temporary files
*.tmp
*.temp
EOF
```

---

## Step 8: Verify Setup

### 8.1 Check Environment Variables

```bash
python3 << 'EOF'
import os
from dotenv import load_dotenv

load_dotenv()

token = os.getenv('META_ACCESS_TOKEN')
bm_id = os.getenv('META_BUSINESS_MANAGER_ID')

print(f"Token loaded: {'✓' if token else '✗'}")
print(f"BM ID loaded: {'✓' if bm_id else '✗'}")
print(f"Token length: {len(token) if token else 0} chars")
EOF
```

Expected output:
```
Token loaded: ✓
BM ID loaded: ✓
Token length: 200+ chars
```

### 8.2 Check File Structure

```bash
tree -L 2 -a
```

Expected structure:
```
.
├── .env
├── .gitignore
├── api/
│   └── __init__.py
├── config/
│   └── __init__.py
├── configs/
│   └── example_campaign.yaml
├── creatives/
│   └── test_video.mp4
├── data/
│   ├── accounts.json
│   ├── campaigns.json
│   └── schedules.json
├── docs/
├── meta/
│   └── __init__.py
├── requirements.txt
├── scheduler/
│   └── __init__.py
├── storage/
│   └── __init__.py
├── utils/
│   └── __init__.py
└── venv/
```

### 8.3 Verify Meta API Access

```bash
python3 << 'EOF'
import os
import requests
from dotenv import load_dotenv

load_dotenv()

token = os.getenv('META_ACCESS_TOKEN')
url = f"https://graph.facebook.com/v18.0/me/adaccounts"
params = {'access_token': token}

response = requests.get(url, params=params)
data = response.json()

if 'data' in data:
    print(f"✓ API Access Working")
    print(f"✓ Found {len(data['data'])} ad accounts")
    for account in data['data']:
        print(f"  - {account['id']}")
else:
    print(f"✗ API Error: {data}")
EOF
```

Expected output:
```
✓ API Access Working
✓ Found 2 ad accounts
  - act_123456789
  - act_987654321
```

---

## Step 9: First Run (After Implementation)

**NOTE:** These commands will work once implementation is complete.

### 9.1 Start API Service

```bash
# Make sure venv is activated
source venv/bin/activate

# Start service
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

Expected output:
```
INFO:     Started server process [12345]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000
```

### 9.2 Test API

Open browser: `http://localhost:8000/docs`

You should see FastAPI Swagger documentation.

### 9.3 Create Test Campaign

```bash
curl -X POST "http://localhost:8000/api/v1/campaigns" \
  -H "Content-Type: application/json" \
  -d '{"config_path": "configs/example_campaign.yaml"}'
```

Expected: Campaign created in Meta Ads Manager in PAUSED status.

---

## Common Setup Issues

### Issue: "Module not found"
**Cause:** Virtual environment not activated or dependencies not installed
**Solution:**
```bash
source venv/bin/activate
pip install -r requirements.txt
```

### Issue: "Token expired or invalid"
**Cause:** Wrong token or token expired
**Solution:**
1. Verify token copied correctly from Meta
2. Generate new token if needed
3. Update .env file

### Issue: "Ad account not accessible"
**Cause:** System user doesn't have permission
**Solution:**
1. Check system user assigned to ad account
2. Verify permission level is "Manage Campaigns"
3. Wait 5 minutes for permissions to propagate

### Issue: "Cannot connect to Meta API"
**Cause:** Network issue or firewall blocking
**Solution:**
1. Check internet connection
2. Test: `curl https://graph.facebook.com/v18.0/`
3. Check firewall/proxy settings

### Issue: "Permission denied on .env"
**Cause:** File permissions too restrictive
**Solution:**
```bash
chmod 600 .env  # Read/write for owner only
```

---

## Security Checklist

- [x] .env file created and secured (chmod 600)
- [x] .env added to .gitignore
- [x] Token stored only in .env (not in code)
- [x] System user token (not personal user token)
- [x] Token set to "Never Expire"
- [x] Virtual environment used (not global Python)
- [x] data/ directory gitignored
- [x] creatives/ directory gitignored

---

## Next Steps

1. ✅ Setup complete
2. → Proceed to implementation (see `/docs/04_PROGRESS.md`)
3. → Create your first campaign using example config
4. → Test scheduling functionality
5. → Add your real campaign configurations

---

## Backup Setup

### Before First Use

```bash
# Backup configuration
cp .env .env.backup
cp data/accounts.json data/accounts.json.backup

# Store backup securely (NOT in git)
# Consider encrypted backup to cloud storage
```

### Regular Backups

```bash
# Create backup script
cat > backup.sh << 'EOF'
#!/bin/bash
BACKUP_DIR="$HOME/backups/meta-automation"
DATE=$(date +%Y%m%d_%H%M%S)

mkdir -p "$BACKUP_DIR"
tar -czf "$BACKUP_DIR/data_$DATE.tar.gz" data/
echo "Backup created: $BACKUP_DIR/data_$DATE.tar.gz"
EOF

chmod +x backup.sh
```

Run daily or after significant changes:
```bash
./backup.sh
```

---

## Getting Help

If setup fails:

1. Check `/docs/06_TROUBLESHOOTING.md`
2. Verify all prerequisites met
3. Review Meta Business Manager settings
4. Test Meta API access directly with curl
5. Check logs for specific error messages

---

## Setup Complete! 🎉

You're ready to start implementation. See `/docs/04_PROGRESS.md` for next steps.
