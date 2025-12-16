"""API request and response models."""
from pydantic import BaseModel, Field, HttpUrl
from typing import Optional, Dict, Any
from datetime import datetime


# ============================================================================
# Campaign Models
# ============================================================================

class CreateCampaignRequest(BaseModel):
    """Request to create a new campaign."""

    config_path: str = Field(
        ...,
        description="Path to campaign YAML configuration file",
        example="configs/example_campaign.yaml"
    )
    start_time: Optional[datetime] = Field(
        None,
        description="Campaign start time in GMT+8 (Singapore time). If future, campaign will be created as PAUSED and auto-scheduled. If None or past, campaign stays PAUSED until manually activated.",
        example="2026-01-03T20:00:00"
    )


class CampaignResponse(BaseModel):
    """Campaign creation response."""

    campaign_id: str = Field(..., description="Internal campaign ID")
    status: str = Field(..., description="Campaign status (PAUSED, ACTIVE, etc.)")
    created_at: datetime = Field(..., description="Creation timestamp")

    meta_ids: Dict[str, str] = Field(
        ...,
        description="Meta platform IDs",
        example={
            "campaign_id": "123456789",
            "adset_id": "987654321",
            "ad_id": "456789123",
            "creative_id": "789123456",
            "video_id": "321654987"
        }
    )

    account_id: str = Field(..., description="Ad account ID (act_xxx)")
    campaign_name: str = Field(..., description="Campaign name")

    # Optional scheduling info
    scheduled_activation: Optional[Dict[str, Any]] = Field(
        None,
        description="Scheduling details if campaign was auto-scheduled",
        example={
            "job_id": "activate_campaign_abc123",
            "scheduled_time": "2026-01-03T20:00:00",
            "status": "pending"
        }
    )


class CampaignStatusResponse(BaseModel):
    """Campaign status response (synced from Meta)."""

    campaign_id: str = Field(..., description="Internal campaign ID")
    meta_campaign_id: str = Field(..., description="Meta campaign ID")
    name: str = Field(..., description="Campaign name")
    status: str = Field(..., description="Current status from Meta")
    daily_budget: Optional[int] = Field(None, description="Daily budget in cents")
    updated_time: Optional[str] = Field(None, description="Last update time from Meta")
    last_synced: datetime = Field(..., description="Last sync timestamp")


class SyncCampaignResponse(BaseModel):
    """Campaign sync response."""

    synced: bool = Field(..., description="Whether sync succeeded")
    campaign_id: str = Field(..., description="Internal campaign ID")
    changes: Dict[str, Any] = Field(..., description="Fields that were updated")


class ActivateCampaignResponse(BaseModel):
    """Campaign activation response."""

    campaign_id: str = Field(..., description="Internal campaign ID")
    meta_campaign_id: str = Field(..., description="Meta campaign ID")
    status: str = Field(..., description="New status (should be ACTIVE)")
    activated_at: datetime = Field(..., description="Activation timestamp")


# ============================================================================
# Scheduling Models
# ============================================================================

class ScheduleRequest(BaseModel):
    """Request to schedule campaign activation."""

    activate_at: datetime = Field(
        ...,
        description="Activation time in GMT+8 (Singapore time)",
        example="2024-03-15T08:00:00"
    )


class ScheduleResponse(BaseModel):
    """Schedule creation response."""

    job_id: str = Field(..., description="Scheduler job ID")
    campaign_id: str = Field(..., description="Internal campaign ID")
    scheduled_time: datetime = Field(..., description="Scheduled activation time (GMT+8)")
    status: str = Field(..., description="Job status (scheduled)")
    created_at: datetime = Field(..., description="Schedule creation timestamp")


class CancelScheduleResponse(BaseModel):
    """Schedule cancellation response."""

    cancelled: bool = Field(..., description="Whether cancellation succeeded")
    campaign_id: str = Field(..., description="Internal campaign ID")
    job_id: str = Field(..., description="Scheduler job ID that was cancelled")


class ScheduleStatusResponse(BaseModel):
    """Schedule status response."""

    campaign_id: str = Field(..., description="Internal campaign ID")
    job_id: str = Field(..., description="Scheduler job ID")
    scheduled_time: datetime = Field(..., description="Scheduled activation time")
    status: str = Field(..., description="Job status (scheduled, completed, failed)")
    created_at: datetime = Field(..., description="Schedule creation timestamp")
    completed_at: Optional[datetime] = Field(None, description="Completion timestamp if job ran")
    error: Optional[str] = Field(None, description="Error message if job failed")


# ============================================================================
# Account Models
# ============================================================================

class CreateAccountRequest(BaseModel):
    """Request to add a new client account."""

    account_id: str = Field(
        ...,
        description="Internal account ID (slug)",
        example="acct_client_a"
    )
    meta_account_id: str = Field(
        ...,
        description="Meta ad account ID (with act_ prefix)",
        example="act_123456789"
    )
    client_name: str = Field(
        ...,
        description="Client display name",
        example="Client A"
    )
    currency: str = Field(
        ...,
        description="Account currency (SGD, USD, MYR, etc.)",
        example="SGD"
    )
    pixel_id: str = Field(
        ...,
        description="Meta Pixel ID",
        example="123456789012345"
    )
    page_id: str = Field(
        ...,
        description="Facebook Page ID",
        example="987654321098765"
    )
    catalog_id: Optional[str] = Field(
        None,
        description="Product catalog ID (optional)",
        example="456789123456789"
    )
    domain: Optional[str] = Field(
        None,
        description="Client domain (optional)",
        example="client-website.com"
    )


class AccountResponse(BaseModel):
    """Account details response."""

    account_id: str = Field(..., description="Internal account ID")
    meta_account_id: str = Field(..., description="Meta ad account ID")
    client_name: str = Field(..., description="Client name")
    currency: str = Field(..., description="Account currency")
    pixel_id: str = Field(..., description="Meta Pixel ID")
    page_id: str = Field(..., description="Facebook Page ID")
    catalog_id: Optional[str] = Field(None, description="Product catalog ID")
    domain: Optional[str] = Field(None, description="Client domain")


# ============================================================================
# Error Models
# ============================================================================

class ErrorResponse(BaseModel):
    """Standard error response."""

    error: str = Field(..., description="Error type")
    message: str = Field(..., description="Error message")
    details: Optional[Dict[str, Any]] = Field(None, description="Additional error details")
