"""
JWT (JSON Web Token) Manager for Exercises-and-Evaluation Project

Provides secure token-based authentication with refresh token support,
maintaining security while supporting educational accessibility requirements.
"""

import jwt
import secrets
import hashlib
from datetime import datetime, timedelta, timezone
from typing import Dict, Optional, Tuple, Any
from pathlib import Path
import json

from .exceptions import InvalidTokenError, AuthenticationError


class JWTManager:
    """JSON Web Token management for secure authentication"""
    
    # Token expiration settings
    ACCESS_TOKEN_EXPIRY = timedelta(hours=24)  # 24 hours
    REFRESH_TOKEN_EXPIRY = timedelta(days=7)   # 7 days
    
    # Token algorithm
    ALGORITHM = 'HS256'
    
    def __init__(self, secret_key: Optional[str] = None, key_file: Optional[Path] = None):
        """
        Initialize JWT Manager
        
        Args:
            secret_key: Secret key for signing tokens
            key_file: Path to file containing secret key
        """
        self.secret_key = self._get_or_create_secret_key(secret_key, key_file)
        self.blacklisted_tokens = set()
    
    def _get_or_create_secret_key(self, secret_key: Optional[str], key_file: Optional[Path]) -> str:
        """Get existing secret key or create new one"""
        if secret_key:
            return secret_key
        
        if key_file and key_file.exists():
            try:
                with open(key_file, 'r', encoding='utf-8') as f:
                    return f.read().strip()
            except Exception as e:
                raise AuthenticationError(f"Failed to read secret key from {key_file}: {e}")
        
        # Generate new secret key
        new_key = secrets.token_urlsafe(64)
        
        # Save to file if specified
        if key_file:
            try:
                key_file.parent.mkdir(parents=True, exist_ok=True)
                with open(key_file, 'w', encoding='utf-8') as f:
                    f.write(new_key)
                # Set file permissions (read/write for owner only)
                key_file.chmod(0o600)
            except Exception as e:
                raise AuthenticationError(f"Failed to save secret key to {key_file}: {e}")
        
        return new_key
    
    def generate_access_token(self, user_data: Dict[str, Any]) -> str:
        """
        Generate access token for user
        
        Args:
            user_data: Dictionary containing user information
            
        Returns:
            JWT access token string
        """
        now = datetime.now(timezone.utc)
        payload = {
            'user_id': user_data.get('id'),
            'username': user_data.get('username'),
            'email': user_data.get('email'),
            'role': user_data.get('role'),
            'full_name': user_data.get('full_name'),
            'iat': now,
            'exp': now + self.ACCESS_TOKEN_EXPIRY,
            'type': 'access'
        }
        
        return jwt.encode(payload, self.secret_key, algorithm=self.ALGORITHM)
    
    def generate_refresh_token(self, user_data: Dict[str, Any]) -> str:
        """
        Generate refresh token for user
        
        Args:
            user_data: Dictionary containing user information
            
        Returns:
            JWT refresh token string
        """
        now = datetime.now(timezone.utc)
        payload = {
            'user_id': user_data.get('id'),
            'username': user_data.get('username'),
            'iat': now,
            'exp': now + self.REFRESH_TOKEN_EXPIRY,
            'type': 'refresh',
            'jti': secrets.token_urlsafe(32)  # Unique identifier for refresh token
        }
        
        return jwt.encode(payload, self.secret_key, algorithm=self.ALGORITHM)
    
    def generate_token_pair(self, user_data: Dict[str, Any]) -> Tuple[str, str]:
        """
        Generate both access and refresh tokens
        
        Args:
            user_data: Dictionary containing user information
            
        Returns:
            Tuple of (access_token, refresh_token)
        """
        access_token = self.generate_access_token(user_data)
        refresh_token = self.generate_refresh_token(user_data)
        
        return access_token, refresh_token
    
    def validate_access_token(self, token: str) -> Dict[str, Any]:
        """
        Validate access token and return payload
        
        Args:
            token: JWT access token string
            
        Returns:
            Token payload dictionary
            
        Raises:
            InvalidTokenError: If token is invalid or expired
        """
        return self._validate_token(token, expected_type='access')
    
    def validate_refresh_token(self, token: str) -> Dict[str, Any]:
        """
        Validate refresh token and return payload
        
        Args:
            token: JWT refresh token string
            
        Returns:
            Token payload dictionary
            
        Raises:
            InvalidTokenError: If token is invalid or expired
        """
        return self._validate_token(token, expected_type='refresh')
    
    def _validate_token(self, token: str, expected_type: str) -> Dict[str, Any]:
        """
        Internal token validation method
        
        Args:
            token: JWT token string
            expected_type: Expected token type ('access' or 'refresh')
            
        Returns:
            Token payload dictionary
            
        Raises:
            InvalidTokenError: If token is invalid or expired
        """
        # Check if token is blacklisted
        if token in self.blacklisted_tokens:
            raise InvalidTokenError("Token has been revoked")
        
        try:
            payload = jwt.decode(
                token,
                self.secret_key,
                algorithms=[self.ALGORITHM]
            )
            
            # Check token type
            if payload.get('type') != expected_type:
                raise InvalidTokenError(f"Invalid token type. Expected {expected_type}")
            
            # Check expiration
            exp = payload.get('exp')
            if exp and datetime.fromtimestamp(exp, timezone.utc) < datetime.now(timezone.utc):
                raise InvalidTokenError("Token has expired")
            
            return payload
            
        except jwt.ExpiredSignatureError:
            raise InvalidTokenError("Token has expired")
        except jwt.InvalidTokenError as e:
            raise InvalidTokenError(f"Invalid token: {str(e)}")
    
    def refresh_access_token(self, refresh_token: str) -> str:
        """
        Generate new access token from refresh token
        
        Args:
            refresh_token: Valid refresh token
            
        Returns:
            New access token
            
        Raises:
            InvalidTokenError: If refresh token is invalid
        """
        payload = self.validate_refresh_token(refresh_token)
        
        # Create user data for new access token
        user_data = {
            'id': payload['user_id'],
            'username': payload['username'],
            'role': payload.get('role'),  # Role may not be in refresh token
        }
        
        return self.generate_access_token(user_data)
    
    def blacklist_token(self, token: str):
        """
        Add token to blacklist (for logout)
        
        Args:
            token: Token to blacklist
        """
        self.blacklisted_tokens.add(token)
    
    def is_token_blacklisted(self, token: str) -> bool:
        """
        Check if token is blacklisted
        
        Args:
            token: Token to check
            
        Returns:
            True if token is blacklisted
        """
        return token in self.blacklisted_tokens
    
    def get_token_info(self, token: str) -> Dict[str, Any]:
        """
        Get token information without full validation
        
        Args:
            token: JWT token string
            
        Returns:
            Dictionary with token information
        """
        try:
            payload = jwt.decode(
                token,
                self.secret_key,
                algorithms=[self.ALGORITHM],
                options={"verify_exp": False}
            )
            
            return {
                'user_id': payload.get('user_id'),
                'username': payload.get('username'),
                'role': payload.get('role'),
                'type': payload.get('type'),
                'issued_at': payload.get('iat'),
                'expires_at': payload.get('exp'),
                'is_expired': datetime.fromtimestamp(payload.get('exp', 0), timezone.utc) < datetime.now(timezone.utc),
                'is_blacklisted': self.is_token_blacklisted(token)
            }
            
        except jwt.InvalidTokenError:
            return {
                'error': 'Invalid token',
                'is_blacklisted': self.is_token_blacklisted(token)
            }
    
    def extract_user_from_token(self, token: str) -> Dict[str, Any]:
        """
        Extract user information from valid access token
        
        Args:
            token: Valid access token
            
        Returns:
            User information dictionary
        """
        payload = self.validate_access_token(token)
        
        return {
            'id': payload['user_id'],
            'username': payload['username'],
            'email': payload.get('email'),
            'role': payload.get('role'),
            'full_name': payload.get('full_name')
        }
    
    def clear_blacklist(self):
        """Clear all blacklisted tokens"""
        self.blacklisted_tokens.clear()
    
    def rotate_secret_key(self, new_key: Optional[str] = None):
        """
        Rotate secret key (invalidates all existing tokens)
        
        Args:
            new_key: New secret key, or generate random one
        """
        self.secret_key = new_key or secrets.token_urlsafe(64)
        self.clear_blacklist()
    
    @staticmethod
    def hash_token(token: str) -> str:
        """
        Create hash of token for storage (don't store actual tokens)
        
        Args:
            token: Token to hash
            
        Returns:
            SHA-256 hash of token
        """
        return hashlib.sha256(token.encode('utf-8')).hexdigest()
    
    @staticmethod
    def generate_session_id() -> str:
        """
        Generate unique session identifier
        
        Returns:
            Random session ID
        """
        return secrets.token_urlsafe(32)


# Default JWT manager instance
_default_jwt_manager = None


def get_jwt_manager() -> JWTManager:
    """Get default JWT manager instance"""
    global _default_jwt_manager
    if _default_jwt_manager is None:
        # Use default key file location
        key_file = Path(__file__).parent.parent / "auth" / "jwt_secret.key"
        _default_jwt_manager = JWTManager(key_file=key_file)
    return _default_jwt_manager


def create_token_for_user(user_data: Dict[str, Any]) -> Tuple[str, str]:
    """
    Convenience function to create token pair for user
    
    Args:
        user_data: User information dictionary
        
    Returns:
        Tuple of (access_token, refresh_token)
    """
    jwt_manager = get_jwt_manager()
    return jwt_manager.generate_token_pair(user_data)


def validate_user_token(token: str) -> Dict[str, Any]:
    """
    Convenience function to validate user access token
    
    Args:
        token: Access token to validate
        
    Returns:
        User information dictionary
        
    Raises:
        InvalidTokenError: If token is invalid
    """
    jwt_manager = get_jwt_manager()
    return jwt_manager.extract_user_from_token(token)