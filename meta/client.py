"""Hybrid Meta Marketing API client using both SDK and direct API calls."""
import requests
from facebook_business.api import FacebookAdsApi
from facebook_business.adobjects.adaccount import AdAccount
from facebook_business.adobjects.campaign import Campaign
from facebook_business.adobjects.adset import AdSet
from facebook_business.adobjects.ad import Ad
from facebook_business.adobjects.adcreative import AdCreative
from typing import Dict, Any, Optional
from utils.logger import setup_logger
from utils.exceptions import MetaAPIError
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

logger = setup_logger(__name__)


class MetaAPIClient:
    """Hybrid Meta API client using SDK for some operations, direct API for others."""

    def __init__(self, access_token: str, api_version: str = "v22.0"):
        """Initialize Meta API client.

        Args:
            access_token: Meta system user access token
            api_version: Meta API version
        """
        self.access_token = access_token
        self.api_version = api_version
        self.base_url = f"https://graph.facebook.com/{api_version}"

        # Initialize Facebook SDK with API version
        FacebookAdsApi.init(access_token=access_token, api_version=api_version)
        logger.info(f"Meta API client initialized (version: {api_version})")

    def _handle_api_response(self, response: requests.Response) -> Dict[str, Any]:
        """Handle API response and check for errors.

        Args:
            response: requests Response object

        Returns:
            dict: Response data

        Raises:
            MetaAPIError: If API returns error
        """
        try:
            data = response.json()
        except ValueError:
            raise MetaAPIError(f"Invalid JSON response: {response.text}")

        # Check for Meta API error
        if 'error' in data:
            error = data['error']
            error_code = error.get('code', 'unknown')
            error_msg = error.get('message', 'Unknown error')
            raise MetaAPIError(f"Meta API Error (#{error_code}): {error_msg}")

        if not response.ok:
            raise MetaAPIError(f"HTTP {response.status_code}: {response.text}")

        return data

    # ===================================================================
    # Direct API Methods (used for video upload, status updates, fetching)
    # ===================================================================

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type(requests.exceptions.RequestException)
    )
    def upload_video(self, account_id: str, video_path: str) -> str:
        """Upload video using direct API (cleaner file handling).

        Args:
            account_id: Ad account ID (with act_ prefix)
            video_path: Path to video file

        Returns:
            str: Video ID

        Raises:
            MetaAPIError: If upload fails
        """
        url = f"{self.base_url}/{account_id}/advideos"

        try:
            with open(video_path, 'rb') as video_file:
                files = {'source': video_file}
                params = {'access_token': self.access_token}

                logger.info(f"Uploading video: {video_path}")
                response = requests.post(url, files=files, params=params, timeout=300)

            data = self._handle_api_response(response)
            video_id = data.get('id')

            if not video_id:
                raise MetaAPIError(f"No video ID in response: {data}")

            logger.info(f"Video uploaded successfully: {video_id}")
            return video_id

        except FileNotFoundError:
            raise MetaAPIError(f"Video file not found: {video_path}")
        except Exception as e:
            raise MetaAPIError(f"Video upload failed: {e}")

    def get_video_thumbnail(self, video_id: str) -> str:
        """Get video thumbnail URL from Meta API.

        Args:
            video_id: Meta video ID

        Returns:
            str: Thumbnail URL

        Raises:
            MetaAPIError: If fetch fails
        """
        url = f"{self.base_url}/{video_id}"
        params = {
            'access_token': self.access_token,
            'fields': 'picture'
        }

        try:
            response = requests.get(url, params=params, timeout=30)
            data = self._handle_api_response(response)
            thumbnail_url = data.get('picture')

            if not thumbnail_url:
                raise MetaAPIError(f"No thumbnail URL in response: {data}")

            logger.debug(f"Got thumbnail for video {video_id}")
            return thumbnail_url
        except Exception as e:
            raise MetaAPIError(f"Failed to get video thumbnail {video_id}: {e}")

    def get_campaign(self, campaign_id: str) -> Dict[str, Any]:
        """Fetch campaign details using direct API.

        Args:
            campaign_id: Meta campaign ID

        Returns:
            dict: Campaign data

        Raises:
            MetaAPIError: If fetch fails
        """
        url = f"{self.base_url}/{campaign_id}"
        params = {
            'access_token': self.access_token,
            'fields': 'id,name,status,daily_budget,lifetime_budget,updated_time'
        }

        try:
            response = requests.get(url, params=params, timeout=30)
            data = self._handle_api_response(response)
            logger.debug(f"Fetched campaign: {campaign_id}")
            return data
        except Exception as e:
            raise MetaAPIError(f"Failed to fetch campaign {campaign_id}: {e}")

    def update_campaign_status(self, campaign_id: str, status: str) -> Dict[str, Any]:
        """Update campaign status using direct API (simple field update).

        Args:
            campaign_id: Meta campaign ID
            status: New status (ACTIVE or PAUSED)

        Returns:
            dict: Response data

        Raises:
            MetaAPIError: If update fails
        """
        if status not in ['ACTIVE', 'PAUSED', 'ARCHIVED']:
            raise MetaAPIError(f"Invalid status: {status}. Must be ACTIVE, PAUSED, or ARCHIVED")

        url = f"{self.base_url}/{campaign_id}"
        data = {
            'status': status,
            'access_token': self.access_token
        }

        try:
            logger.info(f"Updating campaign {campaign_id} status to {status}")
            response = requests.post(url, data=data, timeout=30)
            result = self._handle_api_response(response)
            logger.info(f"Campaign status updated: {campaign_id} -> {status}")
            return result
        except Exception as e:
            raise MetaAPIError(f"Failed to update campaign status: {e}")

    # ===================================================================
    # SDK Methods (used for campaign/adset/ad/creative creation)
    # ===================================================================

    def create_campaign(self, account_id: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Create campaign using SDK (less boilerplate).

        Args:
            account_id: Ad account ID (with act_ prefix)
            params: Campaign parameters

        Returns:
            dict: Campaign data with ID

        Raises:
            MetaAPIError: If creation fails
        """
        try:
            account = AdAccount(account_id)
            campaign = account.create_campaign(params=params)

            campaign_data = campaign.export_all_data()
            campaign_id = campaign_data.get('id')

            logger.info(f"Campaign created: {campaign_id} - {params.get('name')}")
            return campaign_data
        except Exception as e:
            raise MetaAPIError(f"Failed to create campaign: {e}")

    def create_adset(self, account_id: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Create ad set using direct API (better control for complex nested params).

        Args:
            account_id: Ad account ID (with act_ prefix)
            params: Ad set parameters

        Returns:
            dict: Ad set data with ID

        Raises:
            MetaAPIError: If creation fails
        """
        url = f"{self.base_url}/{account_id}/adsets"

        # Convert nested objects to JSON strings (Meta API expects this)
        import json as json_module
        params_formatted = {}
        for key, value in params.items():
            if isinstance(value, dict) or isinstance(value, list):
                params_formatted[key] = json_module.dumps(value)
            else:
                params_formatted[key] = value

        # Add access token
        params_formatted['access_token'] = self.access_token

        try:
            logger.info(f"Creating adset with formatted params: {params_formatted}")
            response = requests.post(url, data=params_formatted, timeout=30)

            # Log raw response for debugging
            logger.info(f"Adset creation response status: {response.status_code}")
            logger.info(f"Adset creation response body: {response.text}")

            data = self._handle_api_response(response)

            adset_id = data.get('id')
            if not adset_id:
                raise MetaAPIError(f"No adset ID in response: {data}")

            logger.info(f"AdSet created: {adset_id}")
            return data
        except Exception as e:
            raise MetaAPIError(f"Failed to create adset: {e}")

    def create_creative(self, account_id: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Create ad creative using SDK.

        Args:
            account_id: Ad account ID (with act_ prefix)
            params: Creative parameters

        Returns:
            dict: Creative data with ID

        Raises:
            MetaAPIError: If creation fails
        """
        try:
            account = AdAccount(account_id)
            creative = account.create_ad_creative(params=params)

            creative_data = creative.export_all_data()
            creative_id = creative_data.get('id')

            logger.info(f"Creative created: {creative_id}")
            return creative_data
        except Exception as e:
            raise MetaAPIError(f"Failed to create creative: {e}")

    def create_ad(self, account_id: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Create ad using SDK.

        Args:
            account_id: Ad account ID (with act_ prefix)
            params: Ad parameters

        Returns:
            dict: Ad data with ID

        Raises:
            MetaAPIError: If creation fails
        """
        try:
            account = AdAccount(account_id)
            ad = account.create_ad(params=params)

            ad_data = ad.export_all_data()
            ad_id = ad_data.get('id')

            logger.info(f"Ad created: {ad_id}")
            return ad_data
        except Exception as e:
            raise MetaAPIError(f"Failed to create ad: {e}")

    def get_ad_accounts(self) -> list:
        """Get all accessible ad accounts.

        Returns:
            list: List of ad account dicts

        Raises:
            MetaAPIError: If fetch fails
        """
        url = f"{self.base_url}/me/adaccounts"
        params = {
            'access_token': self.access_token,
            'fields': 'id,account_id,name,currency'
        }

        try:
            response = requests.get(url, params=params, timeout=30)
            data = self._handle_api_response(response)
            accounts = data.get('data', [])
            logger.info(f"Found {len(accounts)} ad accounts")
            return accounts
        except Exception as e:
            raise MetaAPIError(f"Failed to fetch ad accounts: {e}")
