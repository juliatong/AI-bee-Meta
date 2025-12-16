"""Job execution functions for scheduled campaign activation."""
from datetime import datetime
from typing import Dict, Any

from meta.client import MetaAPIClient
from meta.campaign import sync_campaign_from_meta
from storage.file_store import FileStore
from config.loader import settings
from utils.logger import setup_logger
from utils.exceptions import MetaAPIError

logger = setup_logger(__name__)

# Initialize storage
file_store = FileStore(data_dir=settings.data_dir)


def activate_campaign_job(campaign_id: str, meta_campaign_id: str):
    """Job function to activate a campaign.

    This function is executed by APScheduler at the scheduled time.

    Args:
        campaign_id: Internal campaign ID
        meta_campaign_id: Meta campaign ID

    Raises:
        MetaAPIError: If activation fails
    """
    logger.info(f"Executing activation job for campaign {campaign_id} (Meta ID: {meta_campaign_id})")

    try:
        # Load schedules
        schedules = file_store.load('schedules.json')
        schedule_key = None

        # Find schedule entry for this campaign
        for key, schedule in schedules.items():
            if schedule.get('campaign_id') == campaign_id:
                schedule_key = key
                break

        # Initialize Meta API client
        client = MetaAPIClient(
            access_token=settings.meta_access_token,
            api_version="v22.0"
        )

        # Update campaign status to ACTIVE
        logger.info(f"Updating campaign {meta_campaign_id} status to ACTIVE")
        client.update_campaign_status(meta_campaign_id, 'ACTIVE')

        # Sync to verify activation
        logger.info(f"Syncing campaign {meta_campaign_id} to verify activation")
        meta_data = sync_campaign_from_meta(client, meta_campaign_id)

        # Update campaigns.json
        campaigns = file_store.load('campaigns.json')
        if campaign_id in campaigns:
            campaigns[campaign_id]['status'] = meta_data.get('status', 'ACTIVE')
            campaigns[campaign_id]['activated_at'] = datetime.utcnow().isoformat()
            campaigns[campaign_id]['last_synced'] = datetime.utcnow().isoformat()
            file_store.save('campaigns.json', campaigns)
            logger.info(f"Updated campaign {campaign_id} status in campaigns.json")

        # Update schedules.json
        if schedule_key and schedule_key in schedules:
            schedules[schedule_key]['status'] = 'completed'
            schedules[schedule_key]['executed_at'] = datetime.utcnow().isoformat()
            schedules[schedule_key]['result'] = 'success'
            file_store.save('schedules.json', schedules)
            logger.info(f"Marked schedule {schedule_key} as completed")

        logger.info(f"Campaign {campaign_id} activated successfully")

    except MetaAPIError as e:
        logger.error(f"Meta API error during activation: {e}")

        # Mark job as failed in schedules.json
        if schedule_key and schedule_key in schedules:
            schedules[schedule_key]['status'] = 'failed'
            schedules[schedule_key]['executed_at'] = datetime.utcnow().isoformat()
            schedules[schedule_key]['result'] = 'failed'
            schedules[schedule_key]['error'] = str(e)
            file_store.save('schedules.json', schedules)
            logger.error(f"Marked schedule {schedule_key} as failed")

        raise

    except Exception as e:
        logger.exception(f"Unexpected error during activation: {e}")

        # Mark job as failed
        if schedule_key and schedule_key in schedules:
            schedules[schedule_key]['status'] = 'failed'
            schedules[schedule_key]['executed_at'] = datetime.utcnow().isoformat()
            schedules[schedule_key]['result'] = 'failed'
            schedules[schedule_key]['error'] = str(e)
            file_store.save('schedules.json', schedules)

        raise
