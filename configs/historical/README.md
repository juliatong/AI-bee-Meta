# Historical Campaign Configurations

These are test campaigns that were already created during development. They are kept here for historical reference only.

## ⚠️ DO NOT USE THESE FILES

All campaigns in this directory have **already been created** and their campaign IDs are in use. Attempting to create campaigns with these files will result in ID conflicts.

## Historical Campaigns

| File | Campaign ID | Meta Campaign ID | Created | Purpose |
|------|-------------|------------------|---------|---------|
| `example_campaign.yaml` | `iflytek_ainote2_singapore_test_001` | `120238688523930005` | Dec 2-3, 2024 | Initial test campaign |
| `test_scheduled_campaign.yaml` | `iflytek_scheduled_test_002` | `120238690148520005` | Dec 3, 2024 | Testing scheduling feature |
| `test_with_starttime.yaml` | `iflytek_starttime_test_003` | `120238696778160005` | Dec 4, 2024 | First campaign with start_time in Meta API |

## For New Campaigns

Use the workflow templates in the parent directory:

```bash
# Go back to configs directory
cd ..

# Use one of these templates:
cp workflow1_immediate_activation.yaml my_campaign.yaml
cp workflow2_scheduled_launch.yaml my_campaign.yaml
cp workflow7_minimal_budget_test.yaml my_campaign.yaml
cp template_campaign.yaml my_campaign.yaml
```

## Why Keep These?

These files document:
- The evolution of the campaign creation system
- Test configurations that were successful
- Historical reference for troubleshooting
- Development milestones (e.g., first campaign with start_time)

**Last Updated:** December 4, 2024
