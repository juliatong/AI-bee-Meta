"""Campaign creation orchestration - 6-step process."""
from typing import Dict, Any, Optional
from datetime import datetime
from meta.client import MetaAPIClient
from meta.creative import upload_video_creative, create_video_ad_creative
from meta.validator import extract_id, validate_account_id
from utils.logger import setup_logger
from utils.exceptions import CampaignCreationError, MetaAPIError

logger = setup_logger(__name__)


def create_advantage_plus_campaign(
    client: MetaAPIClient,
    account_id: str,
    campaign_config: Dict[str, Any],
    account_config: Dict[str, Any],
    start_time: Optional[datetime] = None
) -> Dict[str, str]:
    """Create complete Advantage+ Sales campaign (6-step process).

    Steps:
    1. Upload video → video_id
    2. Create creative → creative_id
    3. Create campaign → campaign_id
    4. Create adset → adset_id
    5. Create ad → ad_id
    6. Return all IDs

    Args:
        client: Meta API client
        account_id: Ad account ID (with act_ prefix)
        campaign_config: Campaign configuration from YAML
        account_config: Account configuration from accounts.json
        start_time: Optional campaign start time (GMT+8). If provided, sets AdSet start_time in Meta API.

    Returns:
        dict: Dictionary with all created IDs:
            - campaign_id
            - adset_id
            - ad_id
            - creative_id
            - video_id

    Raises:
        CampaignCreationError: If any step fails
    """
    created_ids = {}

    try:
        # Validate account ID format
        validate_account_id(account_id)

        campaign_name = campaign_config['name']
        logger.info(f"Starting campaign creation: {campaign_name}")

        # Get account assets (with overrides from campaign config)
        pixel_id = campaign_config.get('pixel_id') or account_config['pixel_id']
        page_id = campaign_config.get('page_id') or account_config['page_id']

        # ================================================================
        # Step 1: Upload Video
        # ================================================================
        video_path = campaign_config['video']['file_path']
        logger.info(f"Step 1/6: Uploading video from {video_path}")

        video_id = upload_video_creative(client, account_id, video_path)
        created_ids['video_id'] = video_id

        # ================================================================
        # Step 2: Create AdCreative
        # ================================================================
        logger.info(f"Step 2/6: Creating video ad creative")

        primary_text = campaign_config['primary_text']
        headline = campaign_config['headline']
        description = campaign_config.get('description', '')
        call_to_action = campaign_config.get('call_to_action', 'SHOP_NOW')
        destination_url = campaign_config['destination_url']

        # Add URL parameters if provided
        if 'url_parameters' in campaign_config and campaign_config['url_parameters']:
            url_params = campaign_config['url_parameters']
            separator = '&' if '?' in destination_url else '?'
            destination_url = f"{destination_url}{separator}{url_params}"

        creative_id = create_video_ad_creative(
            client=client,
            account_id=account_id,
            video_id=video_id,
            page_id=page_id,
            primary_text=primary_text,
            headline=headline,
            description=description,
            call_to_action=call_to_action,
            destination_url=destination_url
        )
        created_ids['creative_id'] = creative_id

        # ================================================================
        # Step 3: Create Campaign
        # ================================================================
        logger.info(f"Step 3/6: Creating campaign")

        daily_budget = campaign_config['daily_budget']

        campaign_params = {
            'name': campaign_name,
            'objective': 'OUTCOME_SALES',
            'status': 'PAUSED',  # Always create as PAUSED
            'special_ad_categories': [],
            'daily_budget': daily_budget,  # Campaign Budget Optimization
            'bid_strategy': 'LOWEST_COST_WITHOUT_CAP',
            'buying_type': 'AUCTION'  # Explicitly set buying type
        }

        campaign_data = client.create_campaign(account_id, campaign_params)
        campaign_id = extract_id(campaign_data)
        created_ids['campaign_id'] = campaign_id

        # ================================================================
        # Step 4: Create AdSet (with Advantage+ configuration)
        # ================================================================
        logger.info(f"Step 4/6: Creating AdSet with Advantage+ configuration")

        # Get geo targeting (default to Singapore if not specified)
        geo_locations = campaign_config.get('geo_locations', {'countries': ['SG']})

        adset_params = {
            'name': f"{campaign_name} - AdSet",
            'campaign_id': campaign_id,
            'optimization_goal': 'OFFSITE_CONVERSIONS',
            'billing_event': 'IMPRESSIONS',
            'promoted_object': {
                'pixel_id': pixel_id,
                'custom_event_type': 'PURCHASE'
            },
            # Note: No daily_budget here - using Campaign Budget Optimization (CBO)
            'targeting': {
                'age_min': 18,
                'age_max': 65,
                'geo_locations': geo_locations,
                'targeting_automation': {
                    'advantage_audience': 1,
                    'individual_setting': {
                        'age': 1,
                        'gender': 1
                    }
                }
            },
            'status': 'PAUSED'
        }

        # Add start_time if provided
        if start_time:
            # Format as ISO 8601 string for Meta API (YYYY-MM-DDTHH:MM:SS+HHMM)
            adset_params['start_time'] = start_time.strftime('%Y-%m-%dT%H:%M:%S+0800')
            logger.info(f"Setting AdSet start_time: {adset_params['start_time']}")

        # Add Singapore universal ads declaration if targeting Singapore
        countries = geo_locations.get('countries', [])
        if 'SG' in countries or 'Singapore' in countries:
            adset_params['regional_regulated_categories'] = ['SINGAPORE_UNIVERSAL']

            # Add beneficiary information for Singapore
            beneficiary_id = account_config.get('beneficiary_id')
            if beneficiary_id:
                adset_params['regional_regulation_identities'] = {
                    'singapore_universal_beneficiary': beneficiary_id,
                    'singapore_universal_payer': beneficiary_id
                }
                logger.info(f"Added Singapore beneficiary: {beneficiary_id}")
            else:
                logger.warning("No beneficiary_id configured for Singapore targeting")

        adset_data = client.create_adset(account_id, adset_params)
        adset_id = extract_id(adset_data)
        created_ids['adset_id'] = adset_id

        # ================================================================
        # Step 5: Create Ad
        # ================================================================
        logger.info(f"Step 5/6: Creating Ad")

        ad_params = {
            'name': f"{campaign_name} - Ad",
            'adset_id': adset_id,
            'creative': {
                'creative_id': creative_id
            },
            'status': 'PAUSED'
        }

        ad_data = client.create_ad(account_id, ad_params)
        ad_id = extract_id(ad_data)
        created_ids['ad_id'] = ad_id

        # ================================================================
        # Step 6: Success!
        # ================================================================
        logger.info(
            f"Campaign created successfully! "
            f"Campaign: {campaign_id}, AdSet: {adset_id}, Ad: {ad_id}"
        )

        return created_ids

    except Exception as e:
        # Log all created IDs for debugging
        logger.error(f"Campaign creation failed: {e}")
        logger.error(f"Created IDs before failure: {created_ids}")

        # TODO: Implement rollback (delete created objects)
        # For MVP, manual cleanup in Ads Manager

        raise CampaignCreationError(
            f"Campaign creation failed at step with {len(created_ids)} objects created. "
            f"Error: {e}. "
            f"Created IDs: {created_ids}"
        )


def update_campaign_status(
    client: MetaAPIClient,
    campaign_id: str,
    status: str
) -> Dict[str, Any]:
    """Update campaign status.

    Args:
        client: Meta API client
        campaign_id: Meta campaign ID
        status: New status (ACTIVE or PAUSED)

    Returns:
        dict: Response data

    Raises:
        MetaAPIError: If update fails
    """
    try:
        logger.info(f"Updating campaign {campaign_id} status to {status}")
        result = client.update_campaign_status(campaign_id, status)
        return result
    except Exception as e:
        raise MetaAPIError(f"Failed to update campaign status: {e}")


def sync_campaign_from_meta(
    client: MetaAPIClient,
    campaign_id: str
) -> Dict[str, Any]:
    """Fetch campaign data from Meta API.

    Args:
        client: Meta API client
        campaign_id: Meta campaign ID

    Returns:
        dict: Campaign data from Meta

    Raises:
        MetaAPIError: If fetch fails
    """
    try:
        logger.info(f"Syncing campaign {campaign_id} from Meta")
        campaign_data = client.get_campaign(campaign_id)
        return campaign_data
    except Exception as e:
        raise MetaAPIError(f"Failed to sync campaign: {e}")
