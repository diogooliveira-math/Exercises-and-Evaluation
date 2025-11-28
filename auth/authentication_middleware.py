"""
Central Authentication Middleware for Exercises-and-Evaluation Project

Provides unified authentication and authorization interface for all system components,
maintaining educational accessibility while ensuring security.
"""

import os
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Any, Optional, Tuple
from functools import wraps

from .jwt_manager import JWTManager, get_jwt_manager
from .permission_manager import PermissionManager, Role, Permission
from .audit_logger import AuditLogger, get_audit_logger, AuditAction
from .password_manager import PasswordManager
from .exceptions import (
    AuthenticationError, AuthorizationError, InvalidTokenError,
    UserNotFoundError, AccountLockedError
)


class AuthenticationMiddleware:
    """Central authentication handler for all project operations"""
    
    def __init__(
        self,
        db_path: Optional[Path] = None,
        jwt_manager: Optional[JWTManager] = None,
        audit_logger: Optional[AuditLogger] = None
    ):
        """
        Initialize authentication middleware
        
        Args:
            db_path: Path to user database
            jwt_manager: JWT manager instance
            audit_logger: Audit logger instance
        """
        self.db_path = db_path or Path(__file__).parent.parent / "data" / "users.db"
        self.jwt_manager = jwt_manager or get_jwt_manager()
        self.permission_manager = PermissionManager()
        self.audit_logger = audit_logger or get_audit_logger()
        self.password_manager = PasswordManager()
        
        self._ensure_database()
    
    def _ensure_database(self):
        """Create user database and tables if they don't exist"""
        try:
            self.db_path.parent.mkdir(parents=True, exist_ok=True)
            
            with sqlite3.connect(self.db_path) as conn:
                # Users table
                conn.execute('''
                    CREATE TABLE IF NOT EXISTS users (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        username VARCHAR(50) UNIQUE NOT NULL,
                        email VARCHAR(100) UNIQUE NOT NULL,
                        password_hash VARCHAR(255) NOT NULL,
                        role VARCHAR(20) NOT NULL DEFAULT 'guest',
                        full_name VARCHAR(100),
                        institution VARCHAR(100),
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        last_login TIMESTAMP,
                        is_active BOOLEAN DEFAULT TRUE,
                        email_verified BOOLEAN DEFAULT FALSE,
                        failed_login_attempts INTEGER DEFAULT 0,
                        locked_until TIMESTAMP,
                        metadata TEXT
                    )
                ''')
                
                # Sessions table
                conn.execute('''
                    CREATE TABLE IF NOT EXISTS sessions (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id INTEGER NOT NULL,
                        refresh_token VARCHAR(255) NOT NULL,
                        expires_at TIMESTAMP NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        last_used TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        is_active BOOLEAN DEFAULT TRUE,
                        FOREIGN KEY (user_id) REFERENCES users(id)
                    )
                ''')
                
                # Create indexes
                conn.execute('CREATE UNIQUE INDEX IF NOT EXISTS idx_users_username ON users(username)')
                conn.execute('CREATE UNIQUE INDEX IF NOT EXISTS idx_users_email ON users(email)')
                conn.execute('CREATE INDEX IF NOT EXISTS idx_sessions_user_id ON sessions(user_id)')
                conn.execute('CREATE INDEX IF NOT EXISTS idx_sessions_refresh_token ON sessions(refresh_token)')
                
                conn.commit()
                
        except sqlite3.Error as e:
            raise AuthenticationError(f"Failed to initialize user database: {e}")
    
    def authenticate_user(self, username: str, password: str, ip_address: Optional[str] = None) -> Dict[str, Any]:
        """
        Authenticate user with username and password
        
        Args:
            username: User's username
            password: User's password
            ip_address: Client IP address
            
        Returns:
            User information dictionary with tokens
            
        Raises:
            AuthenticationError: If authentication fails
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                
                # Get user from database
                cursor = conn.execute(
                    'SELECT * FROM users WHERE username = ? AND is_active = TRUE',
                    (username,)
                )
                user = cursor.fetchone()
                
                if not user:
                    self.audit_logger.log_authentication_event(
                        action=AuditAction.LOGIN_FAILED,
                        username=username,
                        ip_address=ip_address,
                        success=False,
                        error_message="User not found"
                    )
                    raise AuthenticationError("Invalid credentials")
                
                # Check if account is locked
                if user['locked_until']:
                    locked_until = datetime.fromisoformat(user['locked_until'])
                    if locked_until > datetime.now(timezone.utc):
                        self.audit_logger.log_authentication_event(
                            action=AuditAction.LOGIN_FAILED,
                            username=username,
                            ip_address=ip_address,
                            success=False,
                            error_message="Account locked"
                        )
                        raise AccountLockedError(f"Account locked until {locked_until}")
                
                # Verify password using secure password manager
                if not self._verify_password(password, user['password_hash']):
                    # Increment failed login attempts
                    failed_attempts = user['failed_login_attempts'] + 1
                    lock_threshold = 5  # Lock after 5 failed attempts
                    
                    update_data = {'failed_attempts': failed_attempts}
                    if failed_attempts >= lock_threshold:
                        # Lock account for 15 minutes
                        locked_until = (datetime.now(timezone.utc) + timedelta(minutes=15)).isoformat()
                        update_data['locked_until'] = locked_until
                    
                    conn.execute('''
                        UPDATE users 
                        SET failed_login_attempts = :failed_attempts,
                            locked_until = COALESCE(:locked_until, locked_until)
                        WHERE id = :user_id
                    ''', {**update_data, 'user_id': user['id']})
                    
                    conn.commit()
                    
                    self.audit_logger.log_authentication_event(
                        action=AuditAction.LOGIN_FAILED,
                        username=username,
                        ip_address=ip_address,
                        success=False,
                        error_message="Invalid password"
                    )
                    raise AuthenticationError("Invalid credentials")
                
                # Authentication successful - reset failed attempts
                conn.execute('''
                    UPDATE users 
                    SET failed_login_attempts = 0,
                        locked_until = NULL,
                        last_login = CURRENT_TIMESTAMP
                    WHERE id = ?
                ''', (user['id'],))
                conn.commit()
                
                # Create user data for tokens
                user_data = {
                    'id': user['id'],
                    'username': user['username'],
                    'email': user['email'],
                    'role': user['role'],
                    'full_name': user['full_name']
                }
                
                # Generate tokens
                access_token, refresh_token = self.jwt_manager.generate_token_pair(user_data)
                
                # Store refresh token in database
                expires_at = (datetime.now(timezone.utc) + self.jwt_manager.REFRESH_TOKEN_EXPIRY).isoformat()
                conn.execute('''
                    INSERT INTO sessions (user_id, refresh_token, expires_at)
                    VALUES (?, ?, ?)
                ''', (user['id'], refresh_token, expires_at))
                conn.commit()
                
                # Log successful authentication
                self.audit_logger.log_authentication_event(
                    action=AuditAction.LOGIN_SUCCESS,
                    username=username,
                    ip_address=ip_address,
                    success=True,
                    user_id=user['id']
                )
                
                return {
                    'user': user_data,
                    'access_token': access_token,
                    'refresh_token': refresh_token,
                    'role': user['role']
                }
                
        except sqlite3.Error as e:
            raise AuthenticationError(f"Database error during authentication: {e}")
    
    def authenticate_token(self, token: str, required_permission: Optional[Permission] = None) -> Dict[str, Any]:
        """
        Authenticate user using JWT token
        
        Args:
            token: JWT access token
            required_permission: Specific permission required
            
        Returns:
            User context dictionary
            
        Raises:
            AuthenticationError: If token is invalid
            AuthorizationError: If user lacks required permission
        """
        try:
            # Validate token and extract user data
            user_data = self.jwt_manager.extract_user_from_token(token)
            
            # Get full user information from database
            user_info = self._get_user_by_id(user_data['id'])
            if not user_info or not user_info['is_active']:
                raise AuthenticationError("User not found or inactive")
            
            # Check role and permissions
            user_role = self.permission_manager.validate_role(user_info['role'])
            
            if required_permission:
                if not self.permission_manager.has_permission(user_role, required_permission):
                    self.audit_logger.log_authorization_event(
                        action=AuditAction.PERMISSION_DENIED,
                        user_id=user_data['id'],
                        username=user_data['username'],
                        permission=required_permission.value,
                        success=False
                    )
                    raise AuthorizationError(f"Insufficient permissions for {required_permission.value}")
            
            # Log successful authorization
            if required_permission:
                self.audit_logger.log_authorization_event(
                    action=AuditAction.PERMISSION_GRANTED,
                    user_id=user_data['id'],
                    username=user_data['username'],
                    permission=required_permission.value,
                    success=True
                )
            
            return {
                **user_data,
                'role': user_role,
                'full_name': user_info['full_name'],
                'institution': user_info['institution']
            }
            
        except InvalidTokenError as e:
            raise AuthenticationError(f"Invalid token: {e}")
    
    def refresh_token(self, refresh_token: str) -> str:
        """
        Refresh access token using refresh token
        
        Args:
            refresh_token: Valid refresh token
            
        Returns:
            New access token
            
        Raises:
            AuthenticationError: If refresh token is invalid
        """
        try:
            # Validate refresh token
            payload = self.jwt_manager.validate_refresh_token(refresh_token)
            user_id = payload['user_id']
            
            # Check if refresh token exists in database and is active
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                
                cursor = conn.execute('''
                    SELECT * FROM sessions 
                    WHERE refresh_token = ? AND user_id = ? AND is_active = TRUE
                    AND expires_at > CURRENT_TIMESTAMP
                ''', (refresh_token, user_id))
                
                session = cursor.fetchone()
                if not session:
                    raise AuthenticationError("Invalid or expired refresh token")
                
                # Get user information
                user_info = self._get_user_by_id(user_id)
                if not user_info or not user_info['is_active']:
                    raise AuthenticationError("User not found or inactive")
                
                # Generate new access token
                user_data = {
                    'id': user_info['id'],
                    'username': user_info['username'],
                    'email': user_info['email'],
                    'role': user_info['role'],
                    'full_name': user_info['full_name']
                }
                
                new_access_token = self.jwt_manager.generate_access_token(user_data)
                
                # Update session last used timestamp
                conn.execute('''
                    UPDATE sessions 
                    SET last_used = CURRENT_TIMESTAMP
                    WHERE id = ?
                ''', (session['id'],))
                conn.commit()
                
                # Log token refresh
                self.audit_logger.log_action(
                    action=AuditAction.TOKEN_REFRESH,
                    user_id=user_id,
                    username=user_info['username']
                )
                
                return new_access_token
                
        except (InvalidTokenError, sqlite3.Error) as e:
            raise AuthenticationError(f"Token refresh failed: {e}")
    
    def logout_user(self, token: str, refresh_token: Optional[str] = None):
        """
        Logout user and invalidate tokens
        
        Args:
            token: Access token to invalidate
            refresh_token: Refresh token to invalidate
        """
        try:
            # Extract user information from token
            user_data = self.jwt_manager.extract_user_from_token(token)
            
            # Blacklist access token
            self.jwt_manager.blacklist_token(token)
            
            # Deactivate refresh token if provided
            if refresh_token:
                with sqlite3.connect(self.db_path) as conn:
                    conn.execute('''
                        UPDATE sessions 
                        SET is_active = FALSE
                        WHERE refresh_token = ? AND user_id = ?
                    ''', (refresh_token, user_data['id']))
                    conn.commit()
            
            # Log logout
            self.audit_logger.log_action(
                action=AuditAction.LOGOUT,
                user_id=user_data['id'],
                username=user_data['username']
            )
            
        except (InvalidTokenError, sqlite3.Error) as e:
            # Don't raise exception for logout failures
            print(f"Warning: Logout failed: {e}")
    
    def _get_user_by_id(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Get user information by ID"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                
                cursor = conn.execute(
                    'SELECT * FROM users WHERE id = ?',
                    (user_id,)
                )
                user = cursor.fetchone()
                return dict(user) if user else None
                
        except sqlite3.Error:
            return None
    
    def _verify_password(self, password: str, password_hash: str) -> bool:
        """
        Verify password against hash using secure password manager
        """
        return self.password_manager.verify_password(password, password_hash)
    
    def _hash_password(self, password: str) -> str:
        """
        Hash password for storage using secure password manager
        """
        return self.password_manager.hash_password(password)
    
    def create_user(
        self,
        username: str,
        email: str,
        password: str,
        role: Role = Role.GUEST,
        full_name: Optional[str] = None,
        institution: Optional[str] = None
    ) -> int:
        """
        Create new user
        
        Args:
            username: Unique username
            email: Unique email address
            password: User password
            role: User role
            full_name: User's full name
            institution: User's institution
            
        Returns:
            New user ID
            
        Raises:
            AuthenticationError: If user creation fails
        """
        try:
            password_hash = self._hash_password(password)
            
            with sqlite3.connect(self.db_path) as conn:
                # Insert new user
                cursor = conn.execute('''
                    INSERT INTO users (
                        username, email, password_hash, role, full_name, institution
                    ) VALUES (?, ?, ?, ?, ?, ?)
                ''', (username, email, password_hash, role.value, full_name, institution))
                
                user_id = cursor.lastrowid
                conn.commit()
                
                # Log user creation
                self.audit_logger.log_action(
                    action=AuditAction.USER_CREATED,
                    user_id=user_id,
                    username=username,
                    resource_type="user",
                    resource_id=str(user_id),
                    details={
                        "role": role.value,
                        "email": email,
                        "full_name": full_name,
                        "institution": institution
                    }
                )
                
                return user_id
                
        except sqlite3.IntegrityError as e:
            if "username" in str(e):
                raise AuthenticationError("Username already exists")
            elif "email" in str(e):
                raise AuthenticationError("Email already exists")
            else:
                raise AuthenticationError(f"User creation failed: {e}")
        except sqlite3.Error as e:
            raise AuthenticationError(f"Database error during user creation: {e}")


# Decorator for requiring authentication
def require_auth(required_permission: Optional[Permission] = None):
    """
    Decorator to require authentication for a function
    
    Args:
        required_permission: Specific permission required
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Get authentication middleware
            auth_middleware = AuthenticationMiddleware()
            
            # Get token from environment or kwargs
            token = os.getenv('AUTH_TOKEN') or kwargs.get('auth_token')
            if not token:
                raise AuthenticationError("No authentication token provided")
            
            # Authenticate and authorize
            user_context = auth_middleware.authenticate_token(token, required_permission)
            
            # Add user context to kwargs
            kwargs['user_context'] = user_context
            
            return func(*args, **kwargs)
        return wrapper
    return decorator


# Decorator for requiring specific role
def require_role(required_role: Role):
    """
    Decorator to require specific role
    
    Args:
        required_role: Required user role
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Get authentication middleware
            auth_middleware = AuthenticationMiddleware()
            
            # Get token from environment or kwargs
            token = os.getenv('AUTH_TOKEN') or kwargs.get('auth_token')
            if not token:
                raise AuthenticationError("No authentication token provided")
            
            # Authenticate and check role
            user_context = auth_middleware.authenticate_token(token)
            
            if user_context['role'] != required_role:
                raise AuthorizationError(f"Requires {required_role.value} role")
            
            # Add user context to kwargs
            kwargs['user_context'] = user_context
            
            return func(*args, **kwargs)
        return wrapper
    return decorator


# Default authentication middleware instance
_default_auth_middleware = None


def get_authentication_middleware() -> AuthenticationMiddleware:
    """Get default authentication middleware instance"""
    global _default_auth_middleware
    if _default_auth_middleware is None:
        _default_auth_middleware = AuthenticationMiddleware()
    return _default_auth_middleware