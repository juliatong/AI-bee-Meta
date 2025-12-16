# Campaign Configuration Files

This directory contains YAML configuration files for creating Meta ad campaigns.

## Quick Start

**To create a new campaign:**

1. Copy one of the workflow templates
2. Edit the values to match your campaign
3. Use the API to create the campaign

## Available Templates

### 🚀 Ready-to-Use Workflow Templates

**For immediate activation (testing):**
```bash
cp configs/workflow1_immediate_activation.yaml configs/my_test.yaml
# Edit my_test.yaml, then create campaign
```

**For scheduled launch (future activation):**
```bash
cp configs/workflow2_scheduled_launch.yaml configs/my_launch.yaml
# Edit my_launch.yaml, then create with start_time
```

**For creative testing (minimal budget):**
```bash
cp configs/workflow7_minimal_budget_test.yaml configs/my_creative_test.yaml
# Edit my_creative_test.yaml with small budget
```

**For general use:**
```bash
cp configs/template_campaign.yaml configs/my_campaign.yaml
# Edit my_campaign.yaml with your details
```

### 📋 Files in This Directory

| File | Purpose | Status |
|------|---------|--------|
| `template_campaign.yaml` | General template for any campaign | ✅ Use this |
| `workflow1_immediate_activation.yaml` | Template for Workflow 1 (immediate activation) | ✅ Use this |
| `workflow2_scheduled_launch.yaml` | Template for Workflow 2 (scheduled launch) | ✅ Use this |
| `workflow7_minimal_budget_test.yaml` | Template for Workflow 7 (creative testing) | ✅ Use this |
| `historical/` | Archived test campaigns (already used) | 📁 Reference only |

## Required Fields

Every campaign YAML must have:

```yaml
campaign_id: "unique_id_here"           # Must be unique!
client_account_id: "acct_iflytek"       # Must exist in data/accounts.json
name: "Campaign Name"                   # Shows in Meta Ads Manager
daily_budget: 5000                      # In cents (5000 = $50.00)

video:
  file_path: "creatives/video.mp4"      # Video must exist

primary_text: "Your ad copy"
headline: "Your headline"
call_to_action: "SHOP_NOW"

destination_url: "https://your-site.com/"

geo_locations:
  countries: ["SG"]
```

## Optional Fields

```yaml
description: "Optional description"
url_parameters: "utm_source=facebook&utm_campaign=test"
pixel_id: null       # Override account default
page_id: null        # Override account default
catalog_id: null     # Override account default
```

## Creating Campaigns

### Without Scheduling (PAUSED)

```bash
curl -X POST "http://localhost:8000/api/v1/campaigns" \
  -H "Content-Type: application/json" \
  -d '{"config_path": "configs/my_campaign.yaml"}'
```

Then activate manually:
```bash
curl -X POST "http://localhost:8000/api/v1/campaigns/CAMPAIGN_ID/activate"
```

### With Scheduled Activation

```bash
curl -X POST "http://localhost:8000/api/v1/campaigns" \
  -H "Content-Type: application/json" \
  -d '{
    "config_path": "configs/my_campaign.yaml",
    "start_time": "2026-03-15T08:00:00"
  }'
```

This will:
- Create campaign in PAUSED status
- Set AdSet start_time in Meta API
- Schedule automatic activation at specified time

## Important Notes

### Campaign IDs
- **Must be unique** across all campaigns
- Never reuse a campaign_id
- Check `data/campaigns.json` for existing IDs

### Budgets
- Always in **cents** (smallest currency unit)
- Examples:
  - SGD 10.00 = 1000
  - USD 50.00 = 5000
  - MYR 100.00 = 10000

### Times
- All times in **GMT+8** (Singapore timezone)
- Format: `YYYY-MM-DDTHH:MM:SS`
- Example: `2026-03-15T08:00:00` = March 15, 2026 at 8:00 AM SGT

### Video Files
- Must exist in `creatives/` directory
- Formats: .mp4 or .mov
- Max size: 4GB
- Aspect ratio: 16:9 recommended

### Account Configuration
- `client_account_id` must match a key in `data/accounts.json`
- Account must have:
  - `account_id` (Meta ad account)
  - `pixel_id` (Meta pixel)
  - `page_id` (Facebook page)

## Common Workflows

### Workflow 1: Quick Test
1. Copy `workflow1_immediate_activation.yaml`
2. Update campaign_id, video path, ad copy
3. Create campaign (PAUSED)
4. Activate immediately
5. Monitor results

### Workflow 2: Scheduled Launch
1. Copy `workflow2_scheduled_launch.yaml`
2. Update campaign_id, video path, ad copy, budget
3. Create campaign with `start_time` parameter
4. System schedules activation automatically
5. Campaign goes live at scheduled time

### Workflow 7: Creative Testing
1. Copy `workflow7_minimal_budget_test.yaml`
2. Update campaign_id, test creative path
3. Set budget to 100-500 (very small)
4. Create and activate
5. Monitor for 1-2 hours
6. Scale if good, pause if poor

## Troubleshooting

### "Campaign ID already exists"
- Check `data/campaigns.json` for used IDs
- Use a new, unique campaign_id

### "Video file not found"
- Verify file exists: `ls -lh creatives/your_video.mp4`
- Check path in YAML matches actual file location

### "Account not found"
- Check `data/accounts.json` has matching key
- Verify `client_account_id` spelling

### "Invalid field"
- Review YAML syntax (indentation, colons, quotes)
- Check `/docs/03_DATA_API.md` for field reference

## Documentation

- **Complete API Reference:** `/docs/03_DATA_API.md`
- **User Workflows:** `/docs/07_WORKFLOWS.md`
- **Troubleshooting:** `/docs/06_TROUBLESHOOTING.md`
- **Quick Start:** `CLAUDE.md`

## Examples

### Example 1: Spring Sale Campaign
```yaml
campaign_id: "spring_sale_sg_2024"
client_account_id: "acct_iflytek"
name: "Spring Sale - Singapore"
daily_budget: 10000  # SGD 100.00

video:
  file_path: "creatives/spring_sale.mp4"

primary_text: "🌸 Spring Sale! Get 30% off all items!"
headline: "Shop Spring Sale"
call_to_action: "SHOP_NOW"

destination_url: "https://shop.partipost.com/spring-sale"
url_parameters: "utm_source=facebook&utm_campaign=spring_sale"
```

### Example 2: Product Launch
```yaml
campaign_id: "new_product_launch_001"
client_account_id: "acct_iflytek"
name: "New Product Launch"
daily_budget: 15000  # SGD 150.00

video:
  file_path: "creatives/product_launch.mp4"

primary_text: "Introducing our newest innovation!"
headline: "Shop Now"
call_to_action: "LEARN_MORE"

destination_url: "https://shop.partipost.com/new-product"
```

---

**Last Updated:** December 4, 2024
