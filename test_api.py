"""Test script for Meta Ad Campaign Automation API."""
import requests
import json
import time
from datetime import datetime

# Configuration
BASE_URL = "http://localhost:8000"
API_BASE = f"{BASE_URL}/api/v1"


def print_header(text):
    """Print a formatted header."""
    print("\n" + "=" * 70)
    print(f"  {text}")
    print("=" * 70)


def print_response(response):
    """Print formatted response."""
    print(f"Status: {response.status_code}")
    try:
        data = response.json()
        print(f"Response:\n{json.dumps(data, indent=2)}")
    except:
        print(f"Response: {response.text}")


def test_health():
    """Test health check endpoint."""
    print_header("Test 1: Health Check")
    response = requests.get(f"{BASE_URL}/health")
    print_response(response)
    return response.status_code == 200


def test_root():
    """Test root endpoint."""
    print_header("Test 2: Root Endpoint")
    response = requests.get(f"{BASE_URL}/")
    print_response(response)
    return response.status_code == 200


def test_create_account():
    """Test creating a client account."""
    print_header("Test 3: Create Account (Optional)")

    account_data = {
        "account_id": "acct_test_client",
        "meta_account_id": "act_123456789012345",  # Replace with real
        "client_name": "Test Client",
        "currency": "SGD",
        "pixel_id": "987654321098765",  # Replace with real
        "page_id": "456789123456789"     # Replace with real
    }

    print(f"Request: POST {API_BASE}/accounts")
    print(f"Body:\n{json.dumps(account_data, indent=2)}")

    response = requests.post(f"{API_BASE}/accounts", json=account_data)
    print_response(response)

    if response.status_code == 409:
        print("\n⚠️  Account already exists (this is OK)")
        return True

    return response.status_code == 201


def test_get_account():
    """Test getting account details."""
    print_header("Test 4: Get Account")

    account_id = "acct_example"  # Change to your account ID
    response = requests.get(f"{API_BASE}/accounts/{account_id}")
    print_response(response)

    return response.status_code == 200


def test_create_campaign():
    """Test creating a campaign."""
    print_header("Test 5: Create Campaign (Main Test)")

    campaign_data = {
        "config_path": "configs/example_campaign.yaml"
    }

    print(f"Request: POST {API_BASE}/campaigns")
    print(f"Body:\n{json.dumps(campaign_data, indent=2)}")
    print("\n⚠️  This will create a REAL campaign in Meta (PAUSED status)")
    print("⚠️  Make sure your .env, accounts.json, and video are configured!")

    input("\nPress ENTER to continue or Ctrl+C to cancel...")

    response = requests.post(f"{API_BASE}/campaigns", json=campaign_data)
    print_response(response)

    if response.status_code == 201:
        data = response.json()
        campaign_id = data['campaign_id']
        meta_campaign_id = data['meta_ids']['campaign_id']

        print(f"\n✅ Campaign created successfully!")
        print(f"   Internal ID: {campaign_id}")
        print(f"   Meta Campaign ID: {meta_campaign_id}")
        print(f"   Status: {data['status']}")
        print(f"\n🔗 View in Ads Manager:")
        print(f"   https://adsmanager.facebook.com/adsmanager/manage/campaigns?act={data['account_id'][4:]}&selected_campaign_ids={meta_campaign_id}")

        return campaign_id

    return None


def test_get_campaign_status(campaign_id):
    """Test getting campaign status."""
    print_header("Test 6: Get Campaign Status")

    response = requests.get(f"{API_BASE}/campaigns/{campaign_id}")
    print_response(response)

    return response.status_code == 200


def test_sync_campaign(campaign_id):
    """Test syncing campaign from Meta."""
    print_header("Test 7: Sync Campaign")

    response = requests.post(f"{API_BASE}/campaigns/{campaign_id}/sync")
    print_response(response)

    return response.status_code == 200


def test_activate_campaign(campaign_id):
    """Test activating campaign."""
    print_header("Test 8: Activate Campaign (Optional)")

    print("⚠️  This will ACTIVATE the campaign (start spending budget!)")
    choice = input("Do you want to activate? (yes/no): ")

    if choice.lower() != 'yes':
        print("Skipped activation test")
        return True

    response = requests.post(f"{API_BASE}/campaigns/{campaign_id}/activate")
    print_response(response)

    if response.status_code == 200:
        print("\n✅ Campaign activated! It will now spend budget.")
        print("⚠️  Remember to PAUSE it in Ads Manager if this is just a test!")

    return response.status_code == 200


def main():
    """Run all tests."""
    print("\n" + "=" * 70)
    print("  Meta Ad Campaign Automation - API Test Suite")
    print("=" * 70)
    print(f"\n📍 Testing API at: {BASE_URL}")
    print(f"⏰ Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    # Check if server is running
    try:
        requests.get(BASE_URL, timeout=2)
    except requests.exceptions.ConnectionError:
        print("\n❌ ERROR: API server is not running!")
        print("\nStart the server first:")
        print('  cd "/Users/julia/Projects/AI bee"')
        print("  python3 main.py")
        return

    results = []
    campaign_id = None

    # Run basic tests
    results.append(("Health Check", test_health()))
    results.append(("Root Endpoint", test_root()))
    results.append(("Get Account", test_get_account()))

    # Ask before creating campaign
    print("\n" + "=" * 70)
    print("  Ready to test campaign creation")
    print("=" * 70)
    print("\n⚠️  IMPORTANT: Campaign creation tests require:")
    print("   1. Valid Meta API credentials in .env")
    print("   2. Configured ad account in data/accounts.json")
    print("   3. Test video file in creatives/ folder")
    print("   4. Updated configs/example_campaign.yaml")

    choice = input("\nRun campaign creation test? (yes/no): ")

    if choice.lower() == 'yes':
        campaign_id = test_create_campaign()

        if campaign_id:
            results.append(("Create Campaign", True))

            # Test campaign operations
            time.sleep(2)  # Give Meta API time to propagate
            results.append(("Get Campaign Status", test_get_campaign_status(campaign_id)))
            results.append(("Sync Campaign", test_sync_campaign(campaign_id)))

            # Optional activation test
            test_activate_campaign(campaign_id)
        else:
            results.append(("Create Campaign", False))
    else:
        print("\nSkipped campaign creation tests")

    # Print summary
    print("\n" + "=" * 70)
    print("  Test Summary")
    print("=" * 70)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}  {test_name}")

    print(f"\n📊 Results: {passed}/{total} tests passed")

    if campaign_id:
        print(f"\n📌 Campaign ID for further testing: {campaign_id}")
        print("\nYou can now:")
        print(f"  - Check status: curl {API_BASE}/campaigns/{campaign_id}")
        print(f"  - Sync: curl -X POST {API_BASE}/campaigns/{campaign_id}/sync")
        print(f"  - Activate: curl -X POST {API_BASE}/campaigns/{campaign_id}/activate")

    print(f"\n⏰ Completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70 + "\n")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Test interrupted by user")
    except Exception as e:
        print(f"\n\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
