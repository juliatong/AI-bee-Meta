"""Data models for storage layer."""
from typing import Optional, Dict
from datetime import datetime
from pydantic import BaseModel


class AccountConfig(BaseModel):
    """Client ad account configuration."""
    account_id: str
    client_name: str
    currency: str
    pixel_id: str
    page_id: str
    catalog_id: Optional[str] = None
    domain: Optional[str] = None
    active: bool = True


class MetaIDs(BaseModel):
    """Meta object IDs for a campaign."""
    campaign_id: str
    adset_id: str
    ad_id: str
    creative_id: str
    video_id: str


class CampaignData(BaseModel):
    """Campaign tracking data."""
    internal_id: str
    client_account_id: str
    name: str
    status: str
    daily_budget: int
    meta_ids: MetaIDs
    config_path: str
    created_at: str
    activated_at: Optional[str] = None
    last_updated: str
    last_synced: Optional[str] = None


class ScheduleData(BaseModel):
    """Schedule tracking data."""
    job_id: str
    campaign_id: str
    meta_campaign_id: str
    scheduled_time: str
    status: str  # pending, completed, failed, cancelled
    created_at: str
    executed_at: Optional[str] = None
    error: Optional[str] = None
