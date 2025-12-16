#!/usr/bin/env python3
"""Clean up incomplete test campaigns."""
import requests
from config.loader import settings

# Incomplete campaigns to delete
CAMPAIGNS_TO_DELETE = [
    "120238656287100005",
    "120238656527760005",
    "120238656605560005"
]

ACCESS_TOKEN = settings.meta_access_token

def delete_campaign(campaign_id):
    """Delete a campaign."""
    url = f"https://graph.facebook.com/v22.0/{campaign_id}"
    params = {
        'access_token': ACCESS_TOKEN
    }

    print(f"Deleting campaign {campaign_id}...", end=" ")
    response = requests.delete(url, params=params)

    if response.status_code == 200:
        result = response.json()
        if result.get('success'):
            print("✅ Deleted")
            return True
        else:
            print(f"❌ Failed: {result}")
            return False
    else:
        print(f"❌ HTTP {response.status_code}: {response.text}")
        return False

print("=" * 70)
print("  Cleaning Up Incomplete Test Campaigns")
print("=" * 70)

deleted_count = 0
for campaign_id in CAMPAIGNS_TO_DELETE:
    if delete_campaign(campaign_id):
        deleted_count += 1

print(f"\n✅ Cleanup complete: {deleted_count}/{len(CAMPAIGNS_TO_DELETE)} campaigns deleted")
