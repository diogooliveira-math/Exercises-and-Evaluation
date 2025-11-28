"""
Authentication Module for Exercises-and-Evaluation Project

This module provides comprehensive authentication and authorization functionality
while maintaining the project's educational mission and manifesto alignment.

Core Components:
- AuthenticationMiddleware: Central authentication handler
- JWTManager: JSON Web Token management
- PermissionManager: Role-based access control
- AuditLogger: Comprehensive audit logging
"""

from .authentication_middleware import AuthenticationMiddleware
from .jwt_manager import JWTManager
from .permission_manager import PermissionManager, Role, Permission
from .audit_logger import AuditLogger
from .exceptions import AuthenticationError, AuthorizationError, InvalidTokenError

__version__ = "1.0.0"
__author__ = "Exercises-and-Evaluation Team"

__all__ = [
    'AuthenticationMiddleware',
    'JWTManager', 
    'PermissionManager',
    'AuditLogger',
    'Role',
    'Permission',
    'AuthenticationError',
    'AuthorizationError', 
    'InvalidTokenError'
]