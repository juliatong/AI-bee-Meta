"""Configuration validation."""
from pathlib import Path
from typing import Dict, Any
from utils.exceptions import ValidationError, ConfigError
from utils.logger import setup_logger

logger = setup_logger(__name__)


def validate_campaign_config(config: Dict[str, Any]) -> None:
    """Validate campaign configuration.

    Args:
        config: Campaign configuration dict

    Raises:
        ConfigError: If configuration is invalid
    """
    # Required fields
    required_fields = [
        'campaign_id',
        'client_account_id',
        'name',
        'daily_budget',
        'video',
        'primary_text',
        'headline',
        'destination_url'
    ]

    for field in required_fields:
        if field not in config:
            raise ConfigError(f"Missing required field: {field}")

    # Validate video section
    if 'file_path' not in config['video']:
        raise ConfigError("Missing required field: video.file_path")

    # Validate budget
    if not isinstance(config['daily_budget'], int) or config['daily_budget'] < 100:
        raise ConfigError(f"daily_budget must be integer >= 100 cents (got: {config['daily_budget']})")

    # Validate call_to_action if present
    valid_ctas = [
        'SHOP_NOW', 'LEARN_MORE', 'SIGN_UP', 'DOWNLOAD', 'WATCH_MORE',
        'APPLY_NOW', 'BOOK_TRAVEL', 'CONTACT_US', 'GET_QUOTE', 'SUBSCRIBE'
    ]
    if 'call_to_action' in config and config['call_to_action'] not in valid_ctas:
        raise ConfigError(f"Invalid call_to_action: {config['call_to_action']}. Must be one of: {valid_ctas}")

    logger.debug(f"Campaign config validated: {config['campaign_id']}")


def validate_video_file(video_path: str) -> None:
    """Validate video file.

    Args:
        video_path: Path to video file

    Raises:
        ValidationError: If video file is invalid
    """
    path = Path(video_path)

    # Check file exists
    if not path.exists():
        raise ValidationError(f"Video file not found: {video_path}")

    # Check file extension
    if path.suffix.lower() not in ['.mp4', '.mov']:
        raise ValidationError(f"Unsupported video format: {path.suffix}. Use .mp4 or .mov")

    # Check file size (4GB Meta limit)
    size_mb = path.stat().st_size / (1024 * 1024)
    if size_mb > 4096:
        raise ValidationError(f"Video file too large: {size_mb:.1f}MB. Maximum 4096MB")

    if size_mb == 0:
        raise ValidationError(f"Video file is empty: {video_path}")

    logger.debug(f"Video file validated: {video_path} ({size_mb:.1f}MB)")


def validate_account_exists(account_id: str, accounts: Dict[str, Any]) -> None:
    """Validate account exists in configuration.

    Args:
        account_id: Internal account ID
        accounts: Accounts configuration dict

    Raises:
        ConfigError: If account not found
    """
    if account_id not in accounts:
        available = ', '.join(accounts.keys())
        raise ConfigError(
            f"Account '{account_id}' not found in accounts.json. "
            f"Available accounts: {available}"
        )

    logger.debug(f"Account validated: {account_id}")
