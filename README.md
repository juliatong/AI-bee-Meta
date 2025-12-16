# Meta Ad Campaign Automation

A FastAPI-based service for automating Meta (Facebook) Advantage+ Sales campaign creation and scheduling via the Meta Marketing API.

## Overview

This service provides a REST API to programmatically create and schedule Meta advertising campaigns with Advantage+ optimization. It supports multi-account management, scheduled campaign activation, and file-based configuration storage.

## Key Features

- **Automated Campaign Creation**: Create Advantage+ Sales campaigns with a single API call
- **Scheduled Activation**: Schedule campaigns to activate at specific times (Singapore timezone GMT+8)
- **Multi-Account Support**: Manage campaigns across multiple Meta ad accounts
- **Video Ad Support**: Upload and attach video creatives to campaigns
- **YAML Configuration**: Define campaigns using simple YAML files
- **Real-time Sync**: Sync campaign status from Meta Ads Manager
- **Comprehensive API**: RESTful API with interactive documentation

## Tech Stack

- **Python 3.9+**
- **FastAPI** - Modern web framework for APIs
- **APScheduler** - Background job scheduling
- **Meta Marketing API** - Hybrid SDK + direct API integration
- **Pydantic** - Data validation and settings management
- **PyYAML** - Configuration file parsing

## Quick Start

### 1. Install Dependencies

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Configure Credentials

Copy the example environment file and add your Meta API credentials:

```bash
cp .env.example .env
```

Edit `.env` and add:
```
META_ACCESS_TOKEN=your_system_user_token_here
META_BUSINESS_MANAGER_ID=your_business_manager_id_here
```

**Security Note**: Never commit `.env` to version control. Keep your access tokens secure.

### 3. Configure Ad Accounts

Create `data/accounts.json` with your ad account details:

```json
{
  "client_account_1": {
    "account_id": "act_123456789",
    "client_name": "Client Name",
    "currency": "SGD",
    "pixel_id": "your_pixel_id",
    "page_id": "your_page_id",
    "domain": "client-website.com",
    "active": true
  }
}
```

### 4. Start the Service

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Visit http://localhost:8000/docs for interactive API documentation.

## Usage Example

Create a campaign using the API:

```bash
curl -X POST "http://localhost:8000/api/v1/campaigns" \
  -H "Content-Type: application/json" \
  -d '{
    "config_path": "configs/example_campaign.yaml",
    "start_time": "2024-03-15T08:00:00"
  }'
```

### Campaign Configuration (YAML)

```yaml
campaign_id: "spring_sale_2024"
client_account_id: "client_account_1"
name: "Spring Sale Campaign"
daily_budget: 5000  # cents (e.g., $50.00)

video:
  file_path: "creatives/video.mp4"

primary_text: "Shop our spring sale!"
headline: "Save 30%"
description: "Limited time offer"
call_to_action: "SHOP_NOW"

destination_url: "https://example.com/sale"
url_parameters: "utm_source=facebook&utm_campaign=spring_sale"
```

## Documentation

Comprehensive documentation is available in the `/docs` directory:

- **[Setup Guide](docs/05_SETUP.md)** - Detailed first-time setup instructions
- **[Quick Start](QUICK_START.md)** - Minimal 3-minute setup for testing
- **[Architecture](docs/02_ARCHITECTURE.md)** - Technical architecture and design
- **[API Reference](docs/03_DATA_API.md)** - API endpoints and data models
- **[Workflows](docs/07_WORKFLOWS.md)** - Common usage patterns
- **[Troubleshooting](docs/06_TROUBLESHOOTING.md)** - Common issues and solutions
- **[Development](docs/08_DEVELOPMENT.md)** - Development guidelines

## API Endpoints

- `POST /api/v1/campaigns` - Create a new campaign
- `GET /api/v1/campaigns/{campaign_id}` - Get campaign details
- `POST /api/v1/campaigns/{campaign_id}/activate` - Activate campaign immediately
- `POST /api/v1/campaigns/{campaign_id}/sync` - Sync status from Meta
- `GET /api/v1/accounts/{account_id}` - Get ad account details
- `GET /health` - Health check endpoint

Visit http://localhost:8000/docs for the full interactive API documentation.

## Architecture

### 6-Step Campaign Creation Process

1. **Upload Video** - Upload creative to Meta and get video_id
2. **Create Creative** - Create ad creative with video and copy
3. **Create Campaign** - Create Meta campaign object
4. **Create AdSet** - Create AdSet with Advantage+ configuration
5. **Create Ad** - Link creative to AdSet
6. **Store Metadata** - Save campaign data locally

### Advantage+ Sales Configuration

The service automatically configures campaigns for Advantage+ Sales:
- Optimization Goal: `OFFSITE_CONVERSIONS` (Purchase)
- Audience: Advantage+ Audience
- Placements: Advantage+ Placements (automatic)
- Bid Strategy: Lowest cost without cap

## Important Notes

### Production Use Warning

This service interacts with **real Meta ad accounts** and creates **real campaigns**:
- All campaigns are created in PAUSED status by default
- Activation requires explicit API call or scheduled time
- Test with small budgets before production use
- Always verify campaigns in Meta Ads Manager before activation

### Timezone

All scheduled times are in **Singapore timezone (GMT+8)**. Ensure your system time matches or use ISO 8601 format with timezone.

### System Requirements

- Machine must stay running for scheduled jobs to execute
- APScheduler requires persistent process (not suitable for serverless)
- File-based storage requires persistent filesystem

## Security

### Best Practices

- Use System User tokens (not personal user tokens)
- Set token permissions: `ads_management`, `ads_read`, `business_management`
- Never commit `.env` file to version control
- Set restrictive file permissions: `chmod 600 .env`
- Regularly rotate access tokens
- Use HTTPS in production

### Protected Files

These files are automatically excluded from version control:
- `.env` - API credentials
- `data/` - Account and campaign data
- `creatives/` - Video files
- `*.db` - Scheduler database

## Contributing

This is currently a private project. If you'd like to contribute or report issues, please contact the repository owner.

## License

Copyright (c) 2024. All rights reserved.

## Support

For detailed setup instructions, see [docs/05_SETUP.md](docs/05_SETUP.md).

For quick testing, see [QUICK_START.md](QUICK_START.md).

For troubleshooting, see [docs/06_TROUBLESHOOTING.md](docs/06_TROUBLESHOOTING.md).

---

**Built with FastAPI and Meta Marketing API**
