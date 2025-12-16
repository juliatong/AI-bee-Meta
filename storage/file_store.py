"""File-based storage implementation using JSON."""
import json
import os
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime
from utils.logger import setup_logger
from utils.exceptions import StorageError

logger = setup_logger(__name__)


class FileStore:
    """File-based storage for campaign, account, and schedule data."""

    def __init__(self, data_dir: str = "data"):
        """Initialize file store.

        Args:
            data_dir: Directory for data files
        """
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)

        # Initialize empty data files if they don't exist
        self._ensure_file_exists('accounts.json')
        self._ensure_file_exists('campaigns.json')
        self._ensure_file_exists('schedules.json')

    def _ensure_file_exists(self, filename: str):
        """Ensure data file exists, create with empty dict if not.

        Args:
            filename: Name of file to check/create
        """
        file_path = self.data_dir / filename
        if not file_path.exists():
            with open(file_path, 'w') as f:
                json.dump({}, f, indent=2)
            logger.info(f"Created data file: {filename}")

    def load(self, filename: str) -> Dict[str, Any]:
        """Load JSON file.

        Args:
            filename: Name of file to load

        Returns:
            dict: Loaded data

        Raises:
            StorageError: If file cannot be loaded
        """
        file_path = self.data_dir / filename
        try:
            if not file_path.exists():
                return {}

            with open(file_path, 'r') as f:
                data = json.load(f)
            logger.debug(f"Loaded {filename}: {len(data)} entries")
            return data
        except json.JSONDecodeError as e:
            raise StorageError(f"Invalid JSON in {filename}: {e}")
        except Exception as e:
            raise StorageError(f"Failed to load {filename}: {e}")

    def save(self, filename: str, data: Dict[str, Any]):
        """Save data to JSON file atomically.

        Args:
            filename: Name of file to save
            data: Data to save

        Raises:
            StorageError: If file cannot be saved
        """
        file_path = self.data_dir / filename
        temp_path = file_path.with_suffix('.tmp')

        try:
            # Write to temp file
            with open(temp_path, 'w') as f:
                json.dump(data, f, indent=2, default=str)

            # Atomic rename
            temp_path.replace(file_path)
            logger.debug(f"Saved {filename}: {len(data)} entries")
        except Exception as e:
            # Clean up temp file if exists
            if temp_path.exists():
                temp_path.unlink()
            raise StorageError(f"Failed to save {filename}: {e}")

    # Account operations
    def get_account(self, account_id: str) -> Optional[Dict[str, Any]]:
        """Get account configuration.

        Args:
            account_id: Internal account ID

        Returns:
            dict or None: Account data if found
        """
        accounts = self.load('accounts.json')
        return accounts.get(account_id)

    def add_account(self, account_id: str, account_data: Dict[str, Any]):
        """Add or update account configuration.

        Args:
            account_id: Internal account ID
            account_data: Account configuration data
        """
        accounts = self.load('accounts.json')
        accounts[account_id] = account_data
        self.save('accounts.json', accounts)
        logger.info(f"Added/updated account: {account_id}")

    # Campaign operations
    def get_campaign(self, campaign_id: str) -> Optional[Dict[str, Any]]:
        """Get campaign data.

        Args:
            campaign_id: Internal campaign ID

        Returns:
            dict or None: Campaign data if found
        """
        campaigns = self.load('campaigns.json')
        return campaigns.get(campaign_id)

    def add_campaign(self, campaign_id: str, campaign_data: Dict[str, Any]):
        """Add campaign to storage.

        Args:
            campaign_id: Internal campaign ID
            campaign_data: Campaign data

        Raises:
            StorageError: If campaign already exists
        """
        campaigns = self.load('campaigns.json')

        if campaign_id in campaigns:
            raise StorageError(f"Campaign {campaign_id} already exists")

        campaigns[campaign_id] = campaign_data
        self.save('campaigns.json', campaigns)
        logger.info(f"Added campaign: {campaign_id}")

    def update_campaign(self, campaign_id: str, updates: Dict[str, Any]):
        """Update campaign fields.

        Args:
            campaign_id: Internal campaign ID
            updates: Fields to update

        Raises:
            StorageError: If campaign not found
        """
        campaigns = self.load('campaigns.json')

        if campaign_id not in campaigns:
            raise StorageError(f"Campaign {campaign_id} not found")

        # Update fields
        campaigns[campaign_id].update(updates)
        campaigns[campaign_id]['last_updated'] = datetime.utcnow().isoformat() + 'Z'

        self.save('campaigns.json', campaigns)
        logger.info(f"Updated campaign: {campaign_id}")

    def list_campaigns(self) -> Dict[str, Any]:
        """List all campaigns.

        Returns:
            dict: All campaigns
        """
        return self.load('campaigns.json')

    # Schedule operations
    def get_schedule(self, job_id: str) -> Optional[Dict[str, Any]]:
        """Get schedule data.

        Args:
            job_id: Job ID

        Returns:
            dict or None: Schedule data if found
        """
        schedules = self.load('schedules.json')
        return schedules.get(job_id)

    def add_schedule(self, job_id: str, schedule_data: Dict[str, Any]):
        """Add schedule to storage.

        Args:
            job_id: Job ID
            schedule_data: Schedule data
        """
        schedules = self.load('schedules.json')
        schedules[job_id] = schedule_data
        self.save('schedules.json', schedules)
        logger.info(f"Added schedule: {job_id}")

    def update_schedule(self, job_id: str, updates: Dict[str, Any]):
        """Update schedule fields.

        Args:
            job_id: Job ID
            updates: Fields to update

        Raises:
            StorageError: If schedule not found
        """
        schedules = self.load('schedules.json')

        if job_id not in schedules:
            raise StorageError(f"Schedule {job_id} not found")

        schedules[job_id].update(updates)
        self.save('schedules.json', schedules)
        logger.info(f"Updated schedule: {job_id}")

    def delete_schedule(self, job_id: str):
        """Delete schedule.

        Args:
            job_id: Job ID

        Raises:
            StorageError: If schedule not found
        """
        schedules = self.load('schedules.json')

        if job_id not in schedules:
            raise StorageError(f"Schedule {job_id} not found")

        del schedules[job_id]
        self.save('schedules.json', schedules)
        logger.info(f"Deleted schedule: {job_id}")

    def list_schedules(self) -> Dict[str, Any]:
        """List all schedules.

        Returns:
            dict: All schedules
        """
        return self.load('schedules.json')
