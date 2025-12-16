"""FastAPI routes for campaign automation."""
from fastapi import APIRouter, HTTPException, status
from typing import Dict, Any
from datetime import datetime
import uuid

from api.models import (
    CreateCampaignRequest,
    CampaignResponse,
    CampaignStatusResponse,
    SyncCampaignResponse,
    ActivateCampaignResponse,
    ScheduleRequest,
    ScheduleResponse,
    CancelScheduleResponse,
    ScheduleStatusResponse,
    CreateAccountRequest,
    AccountResponse,
    ErrorResponse
)
from config.loader import settings, load_campaign_config
from config.validator import validate_campaign_config, validate_account_exists, validate_video_file
from storage.file_store import FileStore
from meta.client import MetaAPIClient
from meta.campaign import create_advantage_plus_campaign, update_campaign_status, sync_campaign_from_meta
from scheduler.manager import get_scheduler_manager
from scheduler.jobs import activate_campaign_job
from utils.logger import setup_logger
from utils.exceptions import (
    MetaAPIError,
    CampaignCreationError,
    ValidationError,
    ConfigError,
    StorageError
)

logger = setup_logger(__name__)
router = APIRouter(prefix="/api/v1", tags=["campaigns"])

# Initialize storage
file_store = FileStore(data_dir=settings.data_dir)


def get_meta_client() -> MetaAPIClient:
    """Get Meta API client instance."""
    return MetaAPIClient(
        access_token=settings.meta_access_token,
        api_version="v22.0"
    )


# ============================================================================
# Campaign Endpoints
# ============================================================================

@router.post(
    "/campaigns",
    response_model=CampaignResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create new campaign",
    description="Create a new Advantage+ Sales campaign in PAUSED state"
)
async def create_campaign(request: CreateCampaignRequest):
    """Create new campaign from YAML configuration."""
    try:
        # Load campaign configuration
        logger.info(f"Loading campaign config from {request.config_path}")
        campaign_config = load_campaign_config(request.config_path)

        # Validate campaign config
        validate_campaign_config(campaign_config)

        # Load account configuration
        client_account_id = campaign_config['client_account_id']
        accounts = file_store.load('accounts.json')
        validate_account_exists(client_account_id, accounts)
        account_config = accounts[client_account_id]

        # Validate video file exists
        video_path = campaign_config['video']['file_path']
        validate_video_file(video_path)

        # Create Meta API client
        client = get_meta_client()
        account_id = account_config['account_id']

        # Create campaign (6-step process)
        logger.info(f"Creating campaign: {campaign_config['name']}")
        created_ids = create_advantage_plus_campaign(
            client=client,
            account_id=account_id,
            campaign_config=campaign_config,
            account_config=account_config,
            start_time=request.start_time
        )

        # Store campaign metadata
        campaign_id = campaign_config['campaign_id']
        campaign_data = {
            'campaign_id': campaign_id,
            'status': 'PAUSED',
            'created_at': datetime.utcnow().isoformat(),
            'meta_ids': created_ids,
            'account_id': account_id,
            'client_account_id': client_account_id,
            'campaign_name': campaign_config['name'],
            'config_path': request.config_path
        }

        campaigns = file_store.load('campaigns.json')
        campaigns[campaign_id] = campaign_data
        file_store.save('campaigns.json', campaigns)

        logger.info(f"Campaign {campaign_id} created and stored successfully")

        # Auto-schedule if start_time is provided and is in the future
        scheduled_activation = None
        if request.start_time:
            if request.start_time > datetime.now():
                logger.info(f"Auto-scheduling campaign {campaign_id} for activation at {request.start_time}")

                # Generate job ID
                job_id = f"activate_{campaign_id}_{uuid.uuid4().hex[:8]}"
                meta_campaign_id = created_ids['campaign_id']

                # Get scheduler and schedule the job
                scheduler = get_scheduler_manager(data_dir=settings.data_dir)
                scheduler.schedule_campaign_activation(
                    job_id=job_id,
                    campaign_id=campaign_id,
                    meta_campaign_id=meta_campaign_id,
                    activate_at=request.start_time,
                    job_func=activate_campaign_job
                )

                # Store schedule metadata
                schedules = file_store.load('schedules.json')
                schedules[job_id] = {
                    'job_id': job_id,
                    'campaign_id': campaign_id,
                    'meta_campaign_id': meta_campaign_id,
                    'scheduled_time': request.start_time.isoformat(),
                    'status': 'pending',
                    'created_at': datetime.utcnow().isoformat(),
                    'executed_at': None,
                    'error': None
                }
                file_store.save('schedules.json', schedules)

                scheduled_activation = {
                    'job_id': job_id,
                    'scheduled_time': request.start_time.isoformat(),
                    'status': 'pending'
                }
                logger.info(f"Campaign {campaign_id} auto-scheduled successfully")
            else:
                logger.warning(f"start_time {request.start_time} is in the past, skipping auto-scheduling")

        return CampaignResponse(
            campaign_id=campaign_id,
            status='PAUSED',
            created_at=datetime.fromisoformat(campaign_data['created_at']),
            meta_ids=created_ids,
            account_id=account_id,
            campaign_name=campaign_config['name'],
            scheduled_activation=scheduled_activation
        )

    except FileNotFoundError as e:
        logger.error(f"File not found: {e}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Configuration file not found: {e}"
        )
    except (ValidationError, ConfigError) as e:
        logger.error(f"Validation error: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except (MetaAPIError, CampaignCreationError) as e:
        logger.error(f"Meta API error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Campaign creation failed: {e}"
        )
    except Exception as e:
        logger.exception(f"Unexpected error creating campaign: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Unexpected error: {e}"
        )


@router.get(
    "/campaigns/{campaign_id}",
    response_model=CampaignStatusResponse,
    summary="Get campaign status",
    description="Fetch latest campaign status from Meta API"
)
async def get_campaign_status(campaign_id: str):
    """Get campaign status (fetches fresh data from Meta API)."""
    try:
        # Load campaign metadata
        campaigns = file_store.load('campaigns.json')
        if campaign_id not in campaigns:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Campaign not found: {campaign_id}"
            )

        campaign_data = campaigns[campaign_id]
        meta_campaign_id = campaign_data['meta_ids']['campaign_id']

        # Fetch fresh data from Meta API
        client = get_meta_client()
        meta_data = sync_campaign_from_meta(client, meta_campaign_id)

        return CampaignStatusResponse(
            campaign_id=campaign_id,
            meta_campaign_id=meta_campaign_id,
            name=meta_data.get('name', campaign_data['campaign_name']),
            status=meta_data.get('status', 'UNKNOWN'),
            daily_budget=meta_data.get('daily_budget'),
            updated_time=meta_data.get('updated_time'),
            last_synced=datetime.utcnow()
        )

    except HTTPException:
        raise
    except MetaAPIError as e:
        logger.error(f"Meta API error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch campaign from Meta: {e}"
        )
    except Exception as e:
        logger.exception(f"Unexpected error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Unexpected error: {e}"
        )


@router.post(
    "/campaigns/{campaign_id}/sync",
    response_model=SyncCampaignResponse,
    summary="Sync campaign from Meta",
    description="Sync campaign data from Meta Ads Manager to local storage"
)
async def sync_campaign(campaign_id: str):
    """Sync campaign data from Meta Ads Manager."""
    try:
        # Load campaign metadata
        campaigns = file_store.load('campaigns.json')
        if campaign_id not in campaigns:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Campaign not found: {campaign_id}"
            )

        campaign_data = campaigns[campaign_id]
        meta_campaign_id = campaign_data['meta_ids']['campaign_id']

        # Fetch from Meta API
        client = get_meta_client()
        meta_data = sync_campaign_from_meta(client, meta_campaign_id)

        # Sync fields
        updates = {
            'status': meta_data.get('status', campaign_data['status']),
            'campaign_name': meta_data.get('name', campaign_data['campaign_name']),
            'last_synced': datetime.utcnow().isoformat()
        }

        if 'daily_budget' in meta_data:
            updates['daily_budget'] = meta_data['daily_budget']

        # Update local storage
        campaign_data.update(updates)
        campaigns[campaign_id] = campaign_data
        file_store.save('campaigns.json', campaigns)

        logger.info(f"Campaign {campaign_id} synced successfully")

        return SyncCampaignResponse(
            synced=True,
            campaign_id=campaign_id,
            changes=updates
        )

    except HTTPException:
        raise
    except MetaAPIError as e:
        logger.error(f"Meta API error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to sync campaign: {e}"
        )
    except Exception as e:
        logger.exception(f"Unexpected error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Unexpected error: {e}"
        )


@router.post(
    "/campaigns/{campaign_id}/activate",
    response_model=ActivateCampaignResponse,
    summary="Activate campaign immediately",
    description="Change campaign status from PAUSED to ACTIVE"
)
async def activate_campaign(campaign_id: str):
    """Activate campaign immediately (change status to ACTIVE)."""
    try:
        # Load campaign metadata
        campaigns = file_store.load('campaigns.json')
        if campaign_id not in campaigns:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Campaign not found: {campaign_id}"
            )

        campaign_data = campaigns[campaign_id]
        meta_campaign_id = campaign_data['meta_ids']['campaign_id']

        # Update status via Meta API
        client = get_meta_client()
        update_campaign_status(client, meta_campaign_id, 'ACTIVE')

        # Sync to verify activation
        meta_data = sync_campaign_from_meta(client, meta_campaign_id)

        # Update local storage
        campaign_data['status'] = meta_data.get('status', 'ACTIVE')
        campaign_data['activated_at'] = datetime.utcnow().isoformat()
        campaign_data['last_synced'] = datetime.utcnow().isoformat()
        campaigns[campaign_id] = campaign_data
        file_store.save('campaigns.json', campaigns)

        logger.info(f"Campaign {campaign_id} activated successfully")

        return ActivateCampaignResponse(
            campaign_id=campaign_id,
            meta_campaign_id=meta_campaign_id,
            status=campaign_data['status'],
            activated_at=datetime.fromisoformat(campaign_data['activated_at'])
        )

    except HTTPException:
        raise
    except MetaAPIError as e:
        logger.error(f"Meta API error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to activate campaign: {e}"
        )
    except Exception as e:
        logger.exception(f"Unexpected error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Unexpected error: {e}"
        )


# ============================================================================
# Scheduling Endpoints (Placeholder - will wire up in Phase 5)
# ============================================================================

@router.post(
    "/campaigns/{campaign_id}/schedule",
    response_model=ScheduleResponse,
    summary="Schedule campaign activation",
    description="Schedule campaign to activate at specific time (GMT+8)"
)
async def schedule_campaign(campaign_id: str, request: ScheduleRequest):
    """Schedule campaign activation for future time."""
    try:
        # Load campaign metadata
        campaigns = file_store.load('campaigns.json')
        if campaign_id not in campaigns:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Campaign not found: {campaign_id}"
            )

        campaign_data = campaigns[campaign_id]
        meta_campaign_id = campaign_data['meta_ids']['campaign_id']

        # Validate activation time is in the future
        activate_at = request.activate_at
        if activate_at <= datetime.now():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Scheduled activation time must be in the future"
            )

        # Generate job ID
        job_id = f"activate_{campaign_id}_{uuid.uuid4().hex[:8]}"

        # Get scheduler
        scheduler = get_scheduler_manager(data_dir=settings.data_dir)

        # Schedule job
        scheduler.schedule_campaign_activation(
            job_id=job_id,
            campaign_id=campaign_id,
            meta_campaign_id=meta_campaign_id,
            activate_at=activate_at,
            job_func=activate_campaign_job
        )

        # Store schedule metadata
        schedules = file_store.load('schedules.json')
        schedules[job_id] = {
            'job_id': job_id,
            'campaign_id': campaign_id,
            'meta_campaign_id': meta_campaign_id,
            'scheduled_time': activate_at.isoformat(),
            'status': 'pending',
            'created_at': datetime.utcnow().isoformat(),
            'executed_at': None,
            'error': None
        }
        file_store.save('schedules.json', schedules)

        logger.info(f"Campaign {campaign_id} scheduled for activation at {activate_at}")

        return ScheduleResponse(
            job_id=job_id,
            campaign_id=campaign_id,
            scheduled_time=activate_at,
            status='pending',
            created_at=datetime.utcnow()
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Unexpected error scheduling campaign: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to schedule campaign: {e}"
        )


@router.delete(
    "/campaigns/{campaign_id}/schedule",
    response_model=CancelScheduleResponse,
    summary="Cancel scheduled activation",
    description="Cancel a pending scheduled activation"
)
async def cancel_schedule(campaign_id: str):
    """Cancel scheduled campaign activation."""
    try:
        # Load schedules
        schedules = file_store.load('schedules.json')

        # Find schedule for this campaign
        job_id = None
        for jid, schedule in schedules.items():
            if schedule.get('campaign_id') == campaign_id and schedule.get('status') == 'pending':
                job_id = jid
                break

        if not job_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No pending schedule found for campaign: {campaign_id}"
            )

        # Get scheduler
        scheduler = get_scheduler_manager(data_dir=settings.data_dir)

        # Cancel job
        cancelled = scheduler.cancel_job(job_id)

        if cancelled:
            # Update schedule status
            schedules[job_id]['status'] = 'cancelled'
            schedules[job_id]['cancelled_at'] = datetime.utcnow().isoformat()
            file_store.save('schedules.json', schedules)

            logger.info(f"Cancelled schedule {job_id} for campaign {campaign_id}")

            return CancelScheduleResponse(
                cancelled=True,
                job_id=job_id,
                campaign_id=campaign_id
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to cancel job: {job_id}"
            )

    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Unexpected error cancelling schedule: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to cancel schedule: {e}"
        )


# ============================================================================
# Account Endpoints
# ============================================================================

@router.post(
    "/accounts",
    response_model=AccountResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Add client account",
    description="Add new client ad account configuration"
)
async def create_account(request: CreateAccountRequest):
    """Add new client account."""
    try:
        # Load accounts
        accounts = file_store.load('accounts.json')

        # Check if account already exists
        if request.account_id in accounts:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Account already exists: {request.account_id}"
            )

        # Create account data
        account_data = {
            'account_id': request.meta_account_id,
            'client_name': request.client_name,
            'currency': request.currency,
            'pixel_id': request.pixel_id,
            'page_id': request.page_id,
            'catalog_id': request.catalog_id,
            'domain': request.domain
        }

        # Save account
        accounts[request.account_id] = account_data
        file_store.save('accounts.json', accounts)

        logger.info(f"Account {request.account_id} created successfully")

        return AccountResponse(
            account_id=request.account_id,
            meta_account_id=request.meta_account_id,
            client_name=request.client_name,
            currency=request.currency,
            pixel_id=request.pixel_id,
            page_id=request.page_id,
            catalog_id=request.catalog_id,
            domain=request.domain
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Unexpected error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Unexpected error: {e}"
        )


@router.get(
    "/accounts/{account_id}",
    response_model=AccountResponse,
    summary="Get account details",
    description="Retrieve client account configuration"
)
async def get_account(account_id: str):
    """Get client account details."""
    try:
        accounts = file_store.load('accounts.json')

        if account_id not in accounts:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Account not found: {account_id}"
            )

        account_data = accounts[account_id]

        return AccountResponse(
            account_id=account_id,
            meta_account_id=account_data['account_id'],
            client_name=account_data['client_name'],
            currency=account_data['currency'],
            pixel_id=account_data['pixel_id'],
            page_id=account_data['page_id'],
            catalog_id=account_data.get('catalog_id'),
            domain=account_data.get('domain')
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Unexpected error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Unexpected error: {e}"
        )
