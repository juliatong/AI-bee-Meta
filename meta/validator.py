"""Meta API response validation."""
from typing import Dict, Any, Optional
from utils.exceptions import MetaAPIError
from utils.logger import setup_logger

logger = setup_logger(__name__)


def validate_api_response(response: Dict[str, Any], expected_fields: Optional[list] = None) -> None:
    """Validate Meta API response.

    Args:
        response: API response data
        expected_fields: List of expected fields in response

    Raises:
        MetaAPIError: If response is invalid
    """
    # Check for error in response
    if 'error' in response:
        error = response['error']
        error_code = error.get('code', 'unknown')
        error_msg = error.get('message', 'Unknown error')
        error_type = error.get('type', 'Unknown')

        raise MetaAPIError(
            f"Meta API Error: ({error_type} #{error_code}) {error_msg}"
        )

    # Check for expected fields
    if expected_fields:
        missing_fields = [field for field in expected_fields if field not in response]
        if missing_fields:
            logger.warning(f"Missing expected fields in response: {missing_fields}")


def extract_id(response: Dict[str, Any], id_field: str = 'id') -> str:
    """Extract ID from API response.

    Args:
        response: API response data
        id_field: Name of ID field (default: 'id')

    Returns:
        str: Extracted ID

    Raises:
        MetaAPIError: If ID not found in response
    """
    object_id = response.get(id_field)

    if not object_id:
        raise MetaAPIError(f"No '{id_field}' field in response: {response}")

    return str(object_id)


def validate_campaign_status(status: str) -> None:
    """Validate campaign status.

    Args:
        status: Campaign status

    Raises:
        MetaAPIError: If status is invalid
    """
    valid_statuses = ['ACTIVE', 'PAUSED', 'DELETED', 'ARCHIVED']

    if status not in valid_statuses:
        raise MetaAPIError(
            f"Invalid campaign status: {status}. "
            f"Must be one of: {', '.join(valid_statuses)}"
        )


def validate_account_id(account_id: str) -> None:
    """Validate ad account ID format.

    Args:
        account_id: Ad account ID

    Raises:
        MetaAPIError: If format is invalid
    """
    if not account_id.startswith('act_'):
        raise MetaAPIError(
            f"Invalid account ID format: {account_id}. "
            "Must start with 'act_'"
        )

    # Extract numeric part
    numeric_part = account_id[4:]
    if not numeric_part.isdigit():
        raise MetaAPIError(
            f"Invalid account ID format: {account_id}. "
            "Must be act_<numeric_id>"
        )
