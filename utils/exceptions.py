"""Custom exceptions for the application."""


class MetaAPIError(Exception):
    """Base exception for Meta API related errors."""
    pass


class VideoUploadError(MetaAPIError):
    """Exception raised when video upload fails."""
    pass


class CampaignCreationError(MetaAPIError):
    """Exception raised when campaign creation fails."""
    pass


class SchedulingError(Exception):
    """Exception raised when scheduling operation fails."""
    pass


class ValidationError(Exception):
    """Exception raised when input validation fails."""
    pass


class ConfigError(Exception):
    """Exception raised when configuration is invalid."""
    pass


class StorageError(Exception):
    """Exception raised when file storage operation fails."""
    pass
