"""
Password Manager Module

Provides secure password hashing and verification using Argon2id with SHA256 fallback.
Implements the PasswordManager class for secure password operations in the authentication system.
"""

import hashlib
import logging
from typing import Optional, Tuple

try:
    from argon2 import PasswordHasher, exceptions as argon2_exceptions
    ARGON2_AVAILABLE = True
except ImportError:
    ARGON2_AVAILABLE = False
    logging.warning("argon2-cffi not available. Falling back to SHA256 (less secure). Install with: pip install argon2-cffi")


class PasswordManager:
    """
    Secure password manager implementing Argon2id hashing with SHA256 fallback.
    
    Provides methods for hashing passwords and verifying password hashes.
    Uses Argon2id as the primary hashing algorithm with secure parameters.
    Falls back to SHA256 if argon2-cffi is not available.
    """
    
    def __init__(self):
        """
        Initialize the PasswordManager with secure hashing parameters.
        """
        if ARGON2_AVAILABLE:
            self.ph = PasswordHasher(
                time_cost=3,           # Number of iterations
                memory_cost=65536,     # Memory cost in KiB (64MB)
                parallelism=4,         # Number of parallel threads
                hash_len=32,          # Hash length in bytes
                salt_len=16,          # Salt length in bytes
                type='ID'             # Argon2id variant
            )
            logging.info("PasswordManager initialized with Argon2id")
        else:
            logging.warning("PasswordManager initialized with SHA256 fallback (less secure)")
    
    def hash_password(self, password: str) -> str:
        """
        Hash a password using Argon2id or SHA256 fallback.
        
        Args:
            password (str): Plain text password to hash
            
        Returns:
            str: Hashed password string
            
        Raises:
            ValueError: If password is empty or None
        """
        if not password:
            raise ValueError("Password cannot be empty or None")
        
        if ARGON2_AVAILABLE:
            try:
                return self.ph.hash(password)
            except Exception as e:
                logging.error(f"Error hashing password with Argon2id: {e}")
                raise RuntimeError("Failed to hash password with Argon2id") from e
        else:
            # SHA256 fallback with salt
            try:
                salt = hashlib.sha256(f"fallback_salt_{password}".encode()).hexdigest()[:16]
                hash_obj = hashlib.sha256((password + salt).encode())
                return f"sha256${salt}${hash_obj.hexdigest()}"
            except Exception as e:
                logging.error(f"Error hashing password with SHA256: {e}")
                raise RuntimeError("Failed to hash password with SHA256") from e
    
    def verify_password(self, password: str, hashed_password: str) -> bool:
        """
        Verify a password against its hash.
        
        Args:
            password (str): Plain text password to verify
            hashed_password (str): Hashed password to verify against
            
        Returns:
            bool: True if password matches hash, False otherwise
            
        Raises:
            ValueError: If password or hashed_password is empty or None
        """
        if not password:
            raise ValueError("Password cannot be empty or None")
        if not hashed_password:
            raise ValueError("Hashed password cannot be empty or None")
        
        if ARGON2_AVAILABLE and not hashed_password.startswith("sha256$"):
            try:
                self.ph.verify(hashed_password, password)
                return True
            except argon2_exceptions.VerifyMismatchError:
                return False
            except argon2_exceptions.VerificationError as e:
                logging.error(f"Error verifying password with Argon2id: {e}")
                return False
            except Exception as e:
                logging.error(f"Unexpected error verifying password: {e}")
                return False
        else:
            # SHA256 fallback verification
            try:
                parts = hashed_password.split('$')
                if len(parts) != 3 or parts[0] != "sha256":
                    logging.warning("Invalid SHA256 hash format")
                    return False
                
                salt, stored_hash = parts[1], parts[2]
                hash_obj = hashlib.sha256((password + salt).encode())
                computed_hash = hash_obj.hexdigest()
                
                return computed_hash == stored_hash
            except Exception as e:
                logging.error(f"Error verifying password with SHA256: {e}")
                return False
    
    def is_argon2_available(self) -> bool:
        """
        Check if Argon2id is available.
        
        Returns:
            bool: True if Argon2id is available, False otherwise
        """
        return ARGON2_AVAILABLE
    
    def get_hash_info(self, hashed_password: str) -> Optional[dict]:
        """
        Extract information about the hash algorithm and parameters.
        
        Args:
            hashed_password (str): Hashed password string
            
        Returns:
            Optional[dict]: Dictionary with hash information, or None if invalid format
        """
        if not hashed_password:
            return None
        
        if ARGON2_AVAILABLE and not hashed_password.startswith("sha256$"):
            try:
                # Extract Argon2 parameters from hash
                if hashed_password.startswith('$argon2id$'):
                    parts = hashed_password.split('$')
                    if len(parts) >= 4:
                        algorithm = parts[1]
                        params = parts[2].split(',')
                        param_dict = {}
                        for param in params:
                            if '=' in param:
                                key, value = param.split('=')
                                param_dict[key] = value
                        
                        return {
                            'algorithm': algorithm,
                            'parameters': param_dict,
                            'method': 'argon2id'
                        }
            except Exception as e:
                logging.error(f"Error extracting Argon2 hash info: {e}")
                return None
        elif hashed_password.startswith("sha256$"):
            try:
                parts = hashed_password.split('$')
                if len(parts) == 3:
                    return {
                        'algorithm': 'sha256',
                        'salt_length': len(parts[1]),
                        'method': 'sha256_fallback',
                        'warning': 'Using SHA256 fallback - less secure than Argon2id'
                    }
            except Exception as e:
                logging.error(f"Error extracting SHA256 hash info: {e}")
                return None
        
        return None


# Global instance for easy import
password_manager = PasswordManager()


def hash_password(password: str) -> str:
    """
    Convenience function to hash a password.
    
    Args:
        password (str): Plain text password to hash
        
    Returns:
        str: Hashed password string
    """
    return password_manager.hash_password(password)


def verify_password(password: str, hashed_password: str) -> bool:
    """
    Convenience function to verify a password.
    
    Args:
        password (str): Plain text password to verify
        hashed_password (str): Hashed password to verify against
        
    Returns:
        bool: True if password matches hash, False otherwise
    """
    return password_manager.verify_password(password, hashed_password)