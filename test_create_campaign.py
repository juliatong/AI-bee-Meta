#!/usr/bin/env python3
"""Simple script to test campaign creation."""
import requests
import json

url = "http://localhost:8000/api/v1/campaigns"
data = {"config_path": "configs/example_campaign.yaml"}

print("Creating campaign...")
print(f"Request: POST {url}")
print(f"Body: {json.dumps(data, indent=2)}\n")

response = requests.post(url, json=data)

print(f"Status Code: {response.status_code}")
print(f"Response:\n{json.dumps(response.json(), indent=2)}")
