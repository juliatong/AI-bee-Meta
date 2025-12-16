#!/usr/bin/env python3
"""Inspect existing campaign to understand the correct parameters."""
import requests
import json
from config.loader import settings

# Your working campaign ID
CAMPAIGN_ID = "120236830809450005"
ACCESS_TOKEN = settings.meta_access_token

def fetch_campaign():
    """Fetch campaign details."""
    url = f"https://graph.facebook.com/v22.0/{CAMPAIGN_ID}"
    params = {
        'access_token': ACCESS_TOKEN,
        'fields': 'id,name,objective,status,special_ad_categories'
    }
    response = requests.get(url, params=params)
    return response.json()

def fetch_adsets():
    """Fetch adsets for the campaign."""
    url = f"https://graph.facebook.com/v22.0/{CAMPAIGN_ID}/adsets"
    params = {
        'access_token': ACCESS_TOKEN,
        'fields': 'id,name,optimization_goal,billing_event,bid_strategy,daily_budget,targeting,promoted_object,destination_type,status,regional_regulated_categories,regional_regulation_identities'
    }
    response = requests.get(url, params=params)
    return response.json()

def fetch_ads(adset_id):
    """Fetch ads for an adset."""
    url = f"https://graph.facebook.com/v22.0/{adset_id}/ads"
    params = {
        'access_token': ACCESS_TOKEN,
        'fields': 'id,name,status,creative'
    }
    response = requests.get(url, params=params)
    return response.json()

print("=" * 70)
print("  Inspecting Your Working Campaign")
print("=" * 70)

print("\n📋 Campaign Details:")
campaign = fetch_campaign()
print(json.dumps(campaign, indent=2))

print("\n📋 AdSets:")
adsets = fetch_adsets()
print(json.dumps(adsets, indent=2))

if 'data' in adsets and len(adsets['data']) > 0:
    adset_id = adsets['data'][0]['id']
    print(f"\n📋 Ads in AdSet {adset_id}:")
    ads = fetch_ads(adset_id)
    print(json.dumps(ads, indent=2))
