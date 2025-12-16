# User Workflows & Examples

**Audience:** Users creating and managing campaigns
**Purpose:** Learn how to use the system effectively with step-by-step examples
**For code changes:** See `/docs/08_DEVELOPMENT.md`

---

## Common Workflows

### Workflow 1: Create Campaign for Immediate Activation

**Scenario:** Create campaign and activate immediately for testing

**Steps:**

1. **Prepare video**
```bash
cp ~/Downloads/test_ad.mp4 creatives/spring_sale_test.mp4
```

2. **Create campaign config**
```bash
cat > configs/spring_test.yaml << 'EOF'
campaign_id: "spring_test_001"
client_account_id: "client_sg_main"
name: "Spring Sale Test - Immediate"
daily_budget: 1000  # SGD 10.00

video:
  file_path: "creatives/spring_sale_test.mp4"

primary_text: "🌸 Spring Sale! Get 30% off all items today only!"
headline: "Shop Spring Sale"
description: "Limited time offer - don't miss out!"
call_to_action: "SHOP_NOW"

destination_url: "https://client-a.com/spring-sale"
url_parameters: "utm_source=facebook&utm_campaign=spring_test&utm_medium=paid"

# No schedule - will create as PAUSED
EOF
```

3. **Create campaign**
```bash
curl -X POST "http://localhost:8000/api/v1/campaigns" \
  -H "Content-Type: application/json" \
  -d '{"config_path": "configs/spring_test.yaml"}' \
  | jq '.'
```

Expected response:
```json
{
  "internal_id": "spring_test_001",
  "meta_campaign_id": "123456789",
  "meta_adset_id": "987654321",
  "meta_ad_id": "456789123",
  "status": "PAUSED",
  "created_at": "2024-03-10T06:30:00Z"
}
```

4. **Verify in Meta Ads Manager**
- Go to Meta Ads Manager
- Check campaign appears in PAUSED status
- Review campaign structure

5. **Activate immediately**
```bash
curl -X POST "http://localhost:8000/api/v1/campaigns/spring_test_001/activate" \
  | jq '.'
```

6. **Verify activation**
```bash
# Check status
curl "http://localhost:8000/api/v1/campaigns/spring_test_001" | jq '.status'

# Should return: "ACTIVE"
```

---

### Workflow 2: Create Campaign for Scheduled Launch

**Scenario:** Create campaign now, activate tomorrow at 8 AM

**Steps:**

1. **Create campaign config with schedule**
```bash
cat > configs/spring_scheduled.yaml << 'EOF'
campaign_id: "spring_scheduled_001"
client_account_id: "client_sg_main"
name: "Spring Sale - Scheduled Launch"
daily_budget: 5000  # SGD 50.00

video:
  file_path: "creatives/spring_sale_main.mp4"

primary_text: "🌸 Spring Sale starts NOW! Get 30% off all items!"
headline: "Shop Spring Sale"
description: "Limited time offer"
call_to_action: "SHOP_NOW"

destination_url: "https://client-a.com/spring-sale"
url_parameters: "utm_source=facebook&utm_campaign=spring_main"

schedule:
  activate_at: "2024-03-15T08:00:00"  # Tomorrow at 8 AM GMT+8
EOF
```

2. **Create campaign**
```bash
curl -X POST "http://localhost:8000/api/v1/campaigns" \
  -H "Content-Type: application/json" \
  -d '{"config_path": "configs/spring_scheduled.yaml"}' \
  | jq '.'
```

3. **Verify scheduled**
```bash
curl "http://localhost:8000/api/v1/campaigns/spring_scheduled_001" | jq '.scheduled_activation'
```

Expected:
```json
{
  "job_id": "job_abc123",
  "scheduled_time": "2024-03-15T08:00:00",
  "status": "pending"
}
```

4. **Check in Ads Manager**
- Campaign should be in PAUSED status
- Will automatically activate at scheduled time

5. **Day of launch - verify activation** (at 8:05 AM)
```bash
# Check campaign status
curl "http://localhost:8000/api/v1/campaigns/spring_scheduled_001" | jq '.status'

# Should return: "ACTIVE"

# Check schedule status
cat data/schedules.json | jq '.[] | select(.campaign_id=="spring_scheduled_001")'
```

Expected:
```json
{
  "job_id": "job_abc123",
  "campaign_id": "spring_scheduled_001",
  "meta_campaign_id": "123456789",
  "scheduled_time": "2024-03-15T08:00:00",
  "status": "completed",
  "executed_at": "2024-03-15T00:00:05Z"
}
```

---

### Workflow 3: Multi-Client Campaign Launch

**Scenario:** Create same campaign for 3 different clients, scheduled for same time

**Steps:**

1. **Create base template**
```bash
cat > configs/template_flash_sale.yaml << 'EOF'
# TEMPLATE - Copy and modify per client
campaign_id: "CHANGE_ME"
client_account_id: "CHANGE_ME"
name: "Flash Sale - 24 Hours Only"
daily_budget: 10000  # $100

video:
  file_path: "creatives/flash_sale.mp4"

primary_text: "⚡ FLASH SALE! 50% off everything for 24 hours only!"
headline: "Shop Flash Sale"
call_to_action: "SHOP_NOW"

destination_url: "CHANGE_ME"
url_parameters: "utm_source=facebook&utm_campaign=flash_sale"

schedule:
  activate_at: "2024-03-20T10:00:00"
EOF
```

2. **Create client-specific configs**

**Client A (Singapore):**
```bash
cp configs/template_flash_sale.yaml configs/flash_sale_sg.yaml
# Edit: campaign_id, client_account_id, destination_url
sed -i '' 's/CHANGE_ME_1/flash_sale_sg_001/' configs/flash_sale_sg.yaml
sed -i '' 's/CHANGE_ME_2/client_sg_main/' configs/flash_sale_sg.yaml
sed -i '' 's|CHANGE_ME_3|https://client-a.com/flash-sale|' configs/flash_sale_sg.yaml
```

**Client B (US):**
```bash
cp configs/template_flash_sale.yaml configs/flash_sale_us.yaml
# Edit for US client
sed -i '' 's/CHANGE_ME_1/flash_sale_us_001/' configs/flash_sale_us.yaml
sed -i '' 's/CHANGE_ME_2/client_us_main/' configs/flash_sale_us.yaml
sed -i '' 's|CHANGE_ME_3|https://client-b.com/flash-sale|' configs/flash_sale_us.yaml
```

**Client C (Malaysia):**
```bash
cp configs/template_flash_sale.yaml configs/flash_sale_my.yaml
# Edit for MY client
sed -i '' 's/CHANGE_ME_1/flash_sale_my_001/' configs/flash_sale_my.yaml
sed -i '' 's/CHANGE_ME_2/client_my_main/' configs/flash_sale_my.yaml
sed -i '' 's|CHANGE_ME_3|https://client-c.com.my/flash-sale|' configs/flash_sale_my.yaml
```

3. **Create all campaigns**
```bash
# Create SG campaign
curl -X POST "http://localhost:8000/api/v1/campaigns" \
  -H "Content-Type: application/json" \
  -d '{"config_path": "configs/flash_sale_sg.yaml"}'

sleep 2  # Brief pause between campaigns

# Create US campaign
curl -X POST "http://localhost:8000/api/v1/campaigns" \
  -H "Content-Type: application/json" \
  -d '{"config_path": "configs/flash_sale_us.yaml"}'

sleep 2

# Create MY campaign
curl -X POST "http://localhost:8000/api/v1/campaigns" \
  -H "Content-Type: application/json" \
  -d '{"config_path": "configs/flash_sale_my.yaml"}'
```

4. **Verify all scheduled**
```bash
cat data/schedules.json | jq '[.[] | select(.scheduled_time=="2024-03-20T10:00:00")] | length'
# Should return: 3
```

5. **Monitor on launch day**
```bash
# Check all statuses at 10:05 AM
for campaign in flash_sale_sg_001 flash_sale_us_001 flash_sale_my_001; do
  echo "Checking $campaign..."
  curl "http://localhost:8000/api/v1/campaigns/$campaign" | jq '.status'
done
```

---

### Workflow 4: Edit Campaign in Ads Manager and Sync

**Scenario:** Campaign running, need to adjust budget in Ads Manager, sync system

**Steps:**

1. **Check current state**
```bash
curl "http://localhost:8000/api/v1/campaigns/spring_sale_001" | jq '{status, daily_budget}'
```

Output:
```json
{
  "status": "ACTIVE",
  "daily_budget": 5000
}
```

2. **Edit in Meta Ads Manager**
- Go to Meta Ads Manager
- Select campaign "Spring Sale - Main"
- Edit → Change daily budget from $50 to $100
- Save

3. **Sync to local system**
```bash
curl -X POST "http://localhost:8000/api/v1/campaigns/spring_sale_001/sync" | jq '.'
```

Output:
```json
{
  "synced": true,
  "campaign_id": "spring_sale_001",
  "changes": {
    "status": "ACTIVE",
    "name": "Spring Sale - Main",
    "daily_budget": 10000,
    "last_synced": "2024-03-15T02:35:00Z"
  }
}
```

4. **Verify sync**
```bash
curl "http://localhost:8000/api/v1/campaigns/spring_sale_001" | jq '.daily_budget'
# Should return: 10000
```

---

### Workflow 5: Cancel Scheduled Campaign

**Scenario:** Scheduled campaign for next week, client changed mind, need to cancel

**Steps:**

1. **Check scheduled campaigns**
```bash
cat data/schedules.json | jq '.[] | select(.status=="pending")'
```

2. **Cancel specific campaign**
```bash
curl -X DELETE "http://localhost:8000/api/v1/campaigns/spring_sale_002/schedule" | jq '.'
```

Output:
```json
{
  "cancelled": true,
  "job_id": "job_def456",
  "campaign_id": "spring_sale_002"
}
```

3. **Verify cancellation**
```bash
cat data/schedules.json | jq '.job_def456.status'
# Should return: "cancelled"
```

4. **Campaign remains in Ads Manager as PAUSED**
- Can manually activate later if needed
- Or delete from Ads Manager if not needed

---

### Workflow 6: Batch Campaign Creation

**Scenario:** Create 10 campaigns for different products, all launching same day

**Steps:**

1. **Prepare videos**
```bash
# Organize by product
cp ~/Videos/product_a.mp4 creatives/prod_a_ad.mp4
cp ~/Videos/product_b.mp4 creatives/prod_b_ad.mp4
# ... etc
```

2. **Create configs programmatically**
```bash
cat > generate_campaigns.sh << 'EOF'
#!/bin/bash

PRODUCTS=("product_a" "product_b" "product_c" "product_d" "product_e")
LAUNCH_TIME="2024-03-25T08:00:00"

for product in "${PRODUCTS[@]}"; do
  cat > "configs/campaign_${product}.yaml" << YAML
campaign_id: "launch_${product}_001"
client_account_id: "client_sg_main"
name: "Product Launch - ${product^}"
daily_budget: 5000

video:
  file_path: "creatives/${product}_ad.mp4"

primary_text: "New ${product^} now available! Limited time offer."
headline: "Shop ${product^}"
call_to_action: "SHOP_NOW"

destination_url: "https://client-a.com/products/${product}"
url_parameters: "utm_source=facebook&utm_campaign=${product}_launch"

schedule:
  activate_at: "${LAUNCH_TIME}"
YAML
done
EOF

chmod +x generate_campaigns.sh
./generate_campaigns.sh
```

3. **Create all campaigns**
```bash
for config in configs/campaign_product_*.yaml; do
  echo "Creating from $config..."
  curl -X POST "http://localhost:8000/api/v1/campaigns" \
    -H "Content-Type: application/json" \
    -d "{\"config_path\": \"$config\"}"
  sleep 3  # Pause between creations
done
```

4. **Verify all scheduled**
```bash
cat data/schedules.json | jq '[.[] | select(.scheduled_time=="2024-03-25T08:00:00")] | length'
# Should match number of campaigns
```

---

### Workflow 7: Testing with Minimal Budget

**Scenario:** Test new creative before full launch

**Steps:**

1. **Create test campaign with minimal budget**
```bash
cat > configs/creative_test.yaml << 'EOF'
campaign_id: "creative_test_001"
client_account_id: "client_sg_main"
name: "TEST - New Creative Concept"
daily_budget: 100  # SGD 1.00 - minimum for testing

video:
  file_path: "creatives/new_concept.mp4"

primary_text: "Testing new ad concept - do not scale"
headline: "Test Ad"
call_to_action: "LEARN_MORE"

destination_url: "https://client-a.com/test"
EOF
```

2. **Create and immediately activate**
```bash
# Create
RESPONSE=$(curl -X POST "http://localhost:8000/api/v1/campaigns" \
  -H "Content-Type: application/json" \
  -d '{"config_path": "configs/creative_test.yaml"}')

echo $RESPONSE | jq '.'

# Activate
curl -X POST "http://localhost:8000/api/v1/campaigns/creative_test_001/activate"
```

3. **Monitor for 1 hour**
```bash
# Check every 15 minutes
watch -n 900 'curl "http://localhost:8000/api/v1/campaigns/creative_test_001" | jq ".status"'
```

4. **Pause if results poor, scale if results good**
- If poor: Pause in Ads Manager
- If good: Create full-budget campaign with same creative

```bash
# If scaling, create production version
cp configs/creative_test.yaml configs/creative_prod.yaml
# Edit: campaign_id, name, daily_budget (increase to 5000+)
# Create production campaign
```

---

### Workflow 8: Disaster Recovery - Service Crashed

**Scenario:** Service crashed mid-campaign creation, need to recover

**Steps:**

1. **Check what was created**
```bash
# Check campaigns.json
cat data/campaigns.json | jq 'to_entries | last'

# Check Meta Ads Manager
# Look for partially created campaigns
```

2. **Identify partial campaign**
```bash
# If campaign in campaigns.json but incomplete meta_ids
cat data/campaigns.json | jq '.incomplete_campaign.meta_ids'

# If some IDs missing, campaign partially created
```

3. **Clean up in Meta Ads Manager**
- Delete incomplete campaign/adset/ad
- Or complete manually if mostly done

4. **Remove from local tracking**
```bash
# Remove incomplete campaign
jq 'del(.incomplete_campaign)' data/campaigns.json > data/campaigns.json.new
mv data/campaigns.json.new data/campaigns.json
```

5. **Retry campaign creation**
```bash
# Use same config
curl -X POST "http://localhost:8000/api/v1/campaigns" \
  -H "Content-Type: application/json" \
  -d '{"config_path": "configs/original_campaign.yaml"}'
```

---

### Workflow 9: End of Campaign - Archive

**Scenario:** Campaign finished, want to archive for records

**Steps:**

1. **Export campaign data**
```bash
# Get full campaign details
curl "http://localhost:8000/api/v1/campaigns/spring_sale_001" > archives/spring_sale_001_$(date +%Y%m%d).json
```

2. **Pause in Meta Ads Manager**
- Go to Ads Manager
- Select campaign
- Pause (or let it end naturally if end date set)

3. **Sync final status**
```bash
curl -X POST "http://localhost:8000/api/v1/campaigns/spring_sale_001/sync"
```

4. **Move video to archive**
```bash
mkdir -p archives/creatives
mv creatives/spring_sale.mp4 archives/creatives/spring_sale_001.mp4
```

5. **Archive campaign config**
```bash
mkdir -p archives/configs
mv configs/spring_sale.yaml archives/configs/spring_sale_001.yaml
```

6. **Keep in campaigns.json for historical tracking**
- Don't delete from campaigns.json
- Serves as permanent record

---

## Quick Reference Commands

### Create Campaign
```bash
curl -X POST "http://localhost:8000/api/v1/campaigns" \
  -H "Content-Type: application/json" \
  -d '{"config_path": "configs/CAMPAIGN.yaml"}'
```

### Schedule Activation
```bash
curl -X POST "http://localhost:8000/api/v1/campaigns/CAMPAIGN_ID/schedule" \
  -H "Content-Type: application/json" \
  -d '{"activate_at": "2024-MM-DDTHH:MM:SS"}'
```

### Activate Immediately
```bash
curl -X POST "http://localhost:8000/api/v1/campaigns/CAMPAIGN_ID/activate"
```

### Check Status
```bash
curl "http://localhost:8000/api/v1/campaigns/CAMPAIGN_ID" | jq '.status'
```

### Sync from Ads Manager
```bash
curl -X POST "http://localhost:8000/api/v1/campaigns/CAMPAIGN_ID/sync"
```

### Cancel Schedule
```bash
curl -X DELETE "http://localhost:8000/api/v1/campaigns/CAMPAIGN_ID/schedule"
```

### List All Campaigns
```bash
cat data/campaigns.json | jq 'keys'
```

### List Scheduled Campaigns
```bash
cat data/schedules.json | jq '.[] | select(.status=="pending") | {campaign_id, scheduled_time}'
```

---

## Tips & Best Practices

### Before Creating Campaigns
- [ ] Test video file plays correctly
- [ ] Check video file size (<4GB)
- [ ] Verify account has sufficient budget
- [ ] Double-check landing page is live
- [ ] Review ad copy for policy compliance

### During Campaign Creation
- [ ] Start with low budget for testing
- [ ] Create as PAUSED first
- [ ] Verify in Ads Manager before activating
- [ ] Keep machine running if scheduling

### After Campaign Active
- [ ] Monitor first hour closely
- [ ] Sync status if edited in Ads Manager
- [ ] Check for rejection in Ads Manager
- [ ] Back up campaign configs

### Scheduling Best Practices
- [ ] Schedule at least 1 hour in advance
- [ ] Keep machine running/awake during activation
- [ ] Verify scheduled time in GMT+8
- [ ] Check schedules.json after scheduling

### Multi-Campaign Launches
- [ ] Stagger activation by 1 minute each
- [ ] Test one campaign first
- [ ] Use templates for consistency
- [ ] Keep configs organized by client/date
