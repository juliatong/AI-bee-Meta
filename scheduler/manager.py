"""APScheduler manager for campaign activation scheduling."""
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from apscheduler.executors.pool import ThreadPoolExecutor
from datetime import datetime
from pathlib import Path
import pytz

from utils.logger import setup_logger

logger = setup_logger(__name__)

# Singapore timezone (GMT+8)
SINGAPORE_TZ = pytz.timezone('Asia/Singapore')

class SchedulerManager:
    """Manages APScheduler for campaign activation jobs."""

    def __init__(self, data_dir: str = "data"):
        """Initialize scheduler manager.

        Args:
            data_dir: Directory for job database
        """
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)

        # Configure job stores
        jobstores = {
            'default': SQLAlchemyJobStore(url=f'sqlite:///{self.data_dir}/jobs.db')
        }

        # Configure executors
        executors = {
            'default': ThreadPoolExecutor(10)
        }

        # Job defaults
        job_defaults = {
            'coalesce': False,
            'max_instances': 1
        }

        # Initialize scheduler
        self.scheduler = BackgroundScheduler(
            jobstores=jobstores,
            executors=executors,
            job_defaults=job_defaults,
            timezone=SINGAPORE_TZ
        )

        logger.info("Scheduler manager initialized (timezone: Asia/Singapore)")

    def start(self):
        """Start the scheduler."""
        if not self.scheduler.running:
            self.scheduler.start()
            logger.info("Scheduler started")

    def shutdown(self):
        """Shutdown the scheduler."""
        if self.scheduler.running:
            self.scheduler.shutdown(wait=True)
            logger.info("Scheduler shutdown")

    def schedule_campaign_activation(
        self,
        job_id: str,
        campaign_id: str,
        meta_campaign_id: str,
        activate_at: datetime,
        job_func
    ) -> str:
        """Schedule campaign activation job.

        Args:
            job_id: Unique job identifier
            campaign_id: Internal campaign ID
            meta_campaign_id: Meta campaign ID
            activate_at: Datetime to activate (must be timezone-aware or Singapore time)
            job_func: Function to execute

        Returns:
            str: Job ID
        """
        # Ensure activate_at is timezone-aware (Singapore time)
        if activate_at.tzinfo is None:
            activate_at = SINGAPORE_TZ.localize(activate_at)

        # Add job to scheduler
        job = self.scheduler.add_job(
            func=job_func,
            trigger='date',
            run_date=activate_at,
            args=[campaign_id, meta_campaign_id],
            id=job_id,
            replace_existing=True
        )

        logger.info(f"Scheduled job {job_id} for campaign {campaign_id} at {activate_at}")
        return job.id

    def cancel_job(self, job_id: str) -> bool:
        """Cancel scheduled job.

        Args:
            job_id: Job identifier

        Returns:
            bool: True if cancelled, False if not found
        """
        try:
            self.scheduler.remove_job(job_id)
            logger.info(f"Cancelled job: {job_id}")
            return True
        except Exception as e:
            logger.warning(f"Failed to cancel job {job_id}: {e}")
            return False

    def get_job(self, job_id: str):
        """Get job details.

        Args:
            job_id: Job identifier

        Returns:
            Job object or None
        """
        return self.scheduler.get_job(job_id)

    def list_jobs(self):
        """List all scheduled jobs.

        Returns:
            list: List of job objects
        """
        return self.scheduler.get_jobs()


# Global scheduler instance
_scheduler_manager = None

def get_scheduler_manager(data_dir: str = "data") -> SchedulerManager:
    """Get singleton scheduler manager instance.

    Args:
        data_dir: Directory for job database

    Returns:
        SchedulerManager: Scheduler manager instance
    """
    global _scheduler_manager
    if _scheduler_manager is None:
        _scheduler_manager = SchedulerManager(data_dir=data_dir)
    return _scheduler_manager
