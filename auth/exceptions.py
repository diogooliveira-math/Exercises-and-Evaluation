"""
Custom exceptions for authentication module
"""


class AuthenticationError(Exception):
    """Base exception for authentication failures"""
    pass


class AuthorizationError(Exception):
    """Raised when user lacks permission for an action"""
    pass


class InvalidTokenError(AuthenticationError):
    """Raised when JWT token is invalid or expired"""
    pass


class UserNotFoundError(AuthenticationError):
    """Raised when user is not found in database"""
    pass


class InvalidCredentialsError(AuthenticationError):
    """Raised when provided credentials are invalid"""
    pass


class AccountLockedError(AuthenticationError):
    """Raised when user account is locked due to security reasons"""
    pass


class SessionExpiredError(AuthenticationError):
    """Raised when user session has expired"""
    pass


class PermissionDeniedError(AuthorizationError):
    """Raised when specific permission is denied"""
    pass


class RoleNotFoundError(Exception):
    """Raised when specified role doesn't exist"""
    pass


class DatabaseConnectionError(Exception):
    """Raised when database connection fails"""
    pass