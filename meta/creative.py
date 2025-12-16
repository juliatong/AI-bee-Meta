"""Video creative upload and management."""
from typing import Dict, Any
from meta.client import MetaAPIClient
from utils.logger import setup_logger
from utils.exceptions import VideoUploadError, MetaAPIError

logger = setup_logger(__name__)


def upload_video_creative(
    client: MetaAPIClient,
    account_id: str,
    video_path: str
) -> str:
    """Upload video and return video ID.

    Args:
        client: Meta API client
        account_id: Ad account ID (with act_ prefix)
        video_path: Path to video file

    Returns:
        str: Video ID

    Raises:
        VideoUploadError: If upload fails
    """
    try:
        video_id = client.upload_video(account_id, video_path)
        return video_id
    except MetaAPIError as e:
        raise VideoUploadError(f"Video upload failed: {e}")
    except Exception as e:
        raise VideoUploadError(f"Unexpected error during video upload: {e}")


def create_video_ad_creative(
    client: MetaAPIClient,
    account_id: str,
    video_id: str,
    page_id: str,
    primary_text: str,
    headline: str,
    description: str,
    call_to_action: str,
    destination_url: str
) -> str:
    """Create video ad creative.

    Args:
        client: Meta API client
        account_id: Ad account ID (with act_ prefix)
        video_id: Video ID from upload
        page_id: Facebook page ID
        primary_text: Primary ad text
        headline: Ad headline
        description: Ad description
        call_to_action: Call to action type (e.g., SHOP_NOW)
        destination_url: Landing page URL

    Returns:
        str: Creative ID

    Raises:
        MetaAPIError: If creation fails
    """
    # Get video thumbnail URL from Meta
    thumbnail_url = client.get_video_thumbnail(video_id)

    creative_params = {
        'name': f"Video Creative - {headline}",
        'object_story_spec': {
            'page_id': page_id,
            'video_data': {
                'video_id': video_id,
                'image_url': thumbnail_url,  # Required for video ads
                'message': primary_text,
                'title': headline,
                'link_description': description,
                'call_to_action': {
                    'type': call_to_action,
                    'value': {
                        'link': destination_url
                    }
                }
            }
        }
    }

    try:
        logger.info(f"Creating video creative for video {video_id}")
        creative_data = client.create_creative(account_id, creative_params)
        creative_id = creative_data.get('id')

        if not creative_id:
            raise MetaAPIError("No creative ID in response")

        logger.info(f"Video creative created: {creative_id}")
        return creative_id
    except Exception as e:
        raise MetaAPIError(f"Failed to create video creative: {e}")
