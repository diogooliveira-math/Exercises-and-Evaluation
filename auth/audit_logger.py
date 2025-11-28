"""
Audit Logger for Exercises-and-Evaluation Project

Provides comprehensive audit logging for all authentication and authorization
events, maintaining security while supporting educational transparency requirements.
"""

import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Any, Optional, List
from enum import Enum

from .exceptions import DatabaseConnectionError


class AuditAction(Enum):
    """Audit action types"""
    
    # Authentication actions
    LOGIN_SUCCESS = "login_success"
    LOGIN_FAILED = "login_failed"
    LOGOUT = "logout"
    TOKEN_REFRESH = "token_refresh"
    PASSWORD_CHANGE = "password_change"
    PASSWORD_RESET = "password_reset"
    
    # Authorization actions
    PERMISSION_GRANTED = "permission_granted"
    PERMISSION_DENIED = "permission_denied"
    ROLE_CHANGE = "role_change"
    
    # Exercise actions
    EXERCISE_CREATED = "exercise_created"
    EXERCISE_UPDATED = "exercise_updated"
    EXERCISE_DELETED = "exercise_deleted"
    EXERCISE_VIEWED = "exercise_viewed"
    
    # Sebenta actions
    SEBENTA_GENERATED = "sebenta_generated"
    SEBENTA_VIEWED = "sebenta_viewed"
    SEBENTA_UPDATED = "sebenta_updated"
    
    # Test actions
    TEST_GENERATED = "test_generated"
    TEST_VIEWED = "test_viewed"
    TEST_SUBMITTED = "test_submitted"
    TEST_GRADED = "test_graded"
    
    # User management actions
    USER_CREATED = "user_created"
    USER_UPDATED = "user_updated"
    USER_DELETED = "user_deleted"
    USER_LOCKED = "user_locked"
    USER_UNLOCKED = "user_unlocked"
    
    # System actions
    SYSTEM_CONFIG_CHANGED = "system_config_changed"
    BACKUP_CREATED = "backup_created"
    BACKUP_RESTORED = "backup_restored"
    API_ACCESS = "api_access"
    CLI_ACCESS = "cli_access"


class AuditLogger:
    """Comprehensive audit logging system"""
    
    def __init__(self, db_path: Optional[Path] = None):
        """
        Initialize audit logger
        
        Args:
            db_path: Path to audit database file
        """
        self.db_path = db_path or Path(__file__).parent.parent / "data" / "audit.db"
        self._ensure_database()
    
    def _ensure_database(self):
        """Create audit database and tables if they don't exist"""
        try:
            self.db_path.parent.mkdir(parents=True, exist_ok=True)
            
            with sqlite3.connect(self.db_path) as conn:
                conn.execute('''
                    CREATE TABLE IF NOT EXISTS audit_log (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        timestamp TEXT NOT NULL,
                        user_id INTEGER,
                        username TEXT,
                        action TEXT NOT NULL,
                        resource_type TEXT,
                        resource_id TEXT,
                        details TEXT,
                        ip_address TEXT,
                        user_agent TEXT,
                        session_id TEXT,
                        success BOOLEAN DEFAULT TRUE,
                        error_message TEXT
                    )
                ''')
                
                # Create indexes for better performance
                conn.execute('''
                    CREATE INDEX IF NOT EXISTS idx_audit_timestamp 
                    ON audit_log(timestamp)
                ''')
                
                conn.execute('''
                    CREATE INDEX IF NOT EXISTS idx_audit_user_id 
                    ON audit_log(user_id)
                ''')
                
                conn.execute('''
                    CREATE INDEX IF NOT EXISTS idx_audit_action 
                    ON audit_log(action)
                ''')
                
                conn.commit()
                
        except sqlite3.Error as e:
            raise DatabaseConnectionError(f"Failed to initialize audit database: {e}")
    
    def log_action(
        self,
        action: AuditAction,
        user_id: Optional[int] = None,
        username: Optional[str] = None,
        resource_type: Optional[str] = None,
        resource_id: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        session_id: Optional[str] = None,
        success: bool = True,
        error_message: Optional[str] = None
    ):
        """
        Log an audit action
        
        Args:
            action: The audit action being logged
            user_id: ID of the user performing the action
            username: Username of the user performing the action
            resource_type: Type of resource being accessed
            resource_id: ID of the resource being accessed
            details: Additional details about the action
            ip_address: IP address of the client
            user_agent: User agent string
            session_id: Session identifier
            success: Whether the action was successful
            error_message: Error message if action failed
        """
        try:
            timestamp = datetime.now(timezone.utc).isoformat()
            details_json = json.dumps(details) if details else None
            
            with sqlite3.connect(self.db_path) as conn:
                conn.execute('''
                    INSERT INTO audit_log (
                        timestamp, user_id, username, action, resource_type,
                        resource_id, details, ip_address, user_agent,
                        session_id, success, error_message
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    timestamp, user_id, username, action.value,
                    resource_type, resource_id, details_json,
                    ip_address, user_agent, session_id,
                    success, error_message
                ))
                conn.commit()
                
        except sqlite3.Error as e:
            # Don't raise exception for audit logging failures
            # to avoid breaking main application flow
            print(f"Warning: Failed to log audit action: {e}")
    
    def log_authentication_event(
        self,
        action: AuditAction,
        username: str,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        success: bool = True,
        error_message: Optional[str] = None,
        user_id: Optional[int] = None
    ):
        """
        Log authentication-related event
        
        Args:
            action: Authentication action
            username: Username attempting authentication
            ip_address: Client IP address
            user_agent: Client user agent
            success: Whether authentication was successful
            error_message: Error message if authentication failed
            user_id: User ID if authentication was successful
        """
        self.log_action(
            action=action,
            user_id=user_id,
            username=username,
            ip_address=ip_address,
            user_agent=user_agent,
            success=success,
            error_message=error_message,
            details={"authentication_method": "standard"}
        )
    
    def log_authorization_event(
        self,
        action: AuditAction,
        user_id: int,
        username: str,
        permission: str,
        resource_type: Optional[str] = None,
        resource_id: Optional[str] = None,
        success: bool = True,
        ip_address: Optional[str] = None
    ):
        """
        Log authorization-related event
        
        Args:
            action: Authorization action
            user_id: ID of the user
            username: Username of the user
            permission: Permission being checked
            resource_type: Type of resource being accessed
            resource_id: ID of the resource being accessed
            success: Whether authorization was granted
            ip_address: Client IP address
        """
        self.log_action(
            action=action,
            user_id=user_id,
            username=username,
            resource_type=resource_type,
            resource_id=resource_id,
            ip_address=ip_address,
            success=success,
            details={"permission": permission}
        )
    
    def log_exercise_action(
        self,
        action: AuditAction,
        user_id: int,
        username: str,
        exercise_id: str,
        exercise_data: Optional[Dict[str, Any]] = None,
        success: bool = True,
        ip_address: Optional[str] = None
    ):
        """
        Log exercise-related action
        
        Args:
            action: Exercise action
            user_id: ID of the user
            username: Username of the user
            exercise_id: ID of the exercise
            exercise_data: Exercise metadata
            success: Whether action was successful
            ip_address: Client IP address
        """
        self.log_action(
            action=action,
            user_id=user_id,
            username=username,
            resource_type="exercise",
            resource_id=exercise_id,
            details=exercise_data,
            ip_address=ip_address,
            success=success
        )
    
    def log_sebenta_action(
        self,
        action: AuditAction,
        user_id: int,
        username: str,
        sebenta_info: Dict[str, Any],
        ip_address: Optional[str] = None
    ):
        """
        Log sebenta-related action
        
        Args:
            action: Sebenta action
            user_id: ID of the user
            username: Username of the user
            sebenta_info: Information about sebenta being generated/viewed
            ip_address: Client IP address
        """
        self.log_action(
            action=action,
            user_id=user_id,
            username=username,
            resource_type="sebenta",
            resource_id=sebenta_info.get("id"),
            details=sebenta_info,
            ip_address=ip_address
        )
    
    def get_user_audit_trail(
        self,
        user_id: Optional[int] = None,
        username: Optional[str] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """
        Get audit trail for a specific user
        
        Args:
            user_id: User ID to filter by
            username: Username to filter by
            limit: Maximum number of records to return
            offset: Number of records to skip
            
        Returns:
            List of audit log entries
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                
                if user_id:
                    query = '''
                        SELECT * FROM audit_log 
                        WHERE user_id = ? 
                        ORDER BY timestamp DESC 
                        LIMIT ? OFFSET ?
                    '''
                    params = (user_id, limit, offset)
                elif username:
                    query = '''
                        SELECT * FROM audit_log 
                        WHERE username = ? 
                        ORDER BY timestamp DESC 
                        LIMIT ? OFFSET ?
                    '''
                    params = (username, limit, offset)
                else:
                    query = '''
                        SELECT * FROM audit_log 
                        ORDER BY timestamp DESC 
                        LIMIT ? OFFSET ?
                    '''
                    params = (limit, offset)
                
                cursor = conn.execute(query, params)
                return [dict(row) for row in cursor.fetchall()]
                
        except sqlite3.Error as e:
            raise DatabaseConnectionError(f"Failed to retrieve audit trail: {e}")
    
    def get_failed_login_attempts(
        self,
        username: Optional[str] = None,
        hours: int = 24
    ) -> List[Dict[str, Any]]:
        """
        Get failed login attempts
        
        Args:
            username: Username to filter by
            hours: Number of hours to look back
            
        Returns:
            List of failed login attempts
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                
                if username:
                    query = '''
                        SELECT * FROM audit_log 
                        WHERE action = ? AND username = ? AND success = FALSE
                        AND timestamp > datetime('now', '-{} hours')
                        ORDER BY timestamp DESC
                    '''.format(hours)
                    params = (AuditAction.LOGIN_FAILED.value, username)
                else:
                    query = '''
                        SELECT * FROM audit_log 
                        WHERE action = ? AND success = FALSE
                        AND timestamp > datetime('now', '-{} hours')
                        ORDER BY timestamp DESC
                    '''.format(hours)
                    params = (AuditAction.LOGIN_FAILED.value,)
                
                cursor = conn.execute(query, params)
                return [dict(row) for row in cursor.fetchall()]
                
        except sqlite3.Error as e:
            raise DatabaseConnectionError(f"Failed to retrieve failed login attempts: {e}")
    
    def get_resource_access_history(
        self,
        resource_type: str,
        resource_id: str,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """
        Get access history for a specific resource
        
        Args:
            resource_type: Type of resource
            resource_id: ID of resource
            limit: Maximum number of records to return
            
        Returns:
            List of access log entries
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                
                query = '''
                    SELECT * FROM audit_log 
                    WHERE resource_type = ? AND resource_id = ?
                    ORDER BY timestamp DESC 
                    LIMIT ?
                '''
                
                cursor = conn.execute(query, (resource_type, resource_id, limit))
                return [dict(row) for row in cursor.fetchall()]
                
        except sqlite3.Error as e:
            raise DatabaseConnectionError(f"Failed to retrieve resource access history: {e}")
    
    def get_audit_statistics(
        self,
        days: int = 30
    ) -> Dict[str, Any]:
        """
        Get audit statistics for the specified period
        
        Args:
            days: Number of days to analyze
            
        Returns:
            Dictionary with audit statistics
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                # Total actions
                total_query = '''
                    SELECT COUNT(*) as total_actions,
                           COUNT(DISTINCT user_id) as unique_users,
                           COUNT(DISTINCT action) as unique_actions
                    FROM audit_log 
                    WHERE timestamp > datetime('now', '-{} days')
                '''.format(days)
                
                # Actions by type
                actions_query = '''
                    SELECT action, COUNT(*) as count
                    FROM audit_log 
                    WHERE timestamp > datetime('now', '-{} days')
                    GROUP BY action
                    ORDER BY count DESC
                '''.format(days)
                
                # Failed logins
                failed_logins_query = '''
                    SELECT COUNT(*) as failed_logins
                    FROM audit_log 
                    WHERE action = ? AND success = FALSE
                    AND timestamp > datetime('now', '-{} days')
                '''.format(days)
                
                total_result = conn.execute(total_query).fetchone()
                actions_result = conn.execute(actions_query).fetchall()
                failed_logins_result = conn.execute(failed_logins_query, (AuditAction.LOGIN_FAILED.value,)).fetchone()
                
                return {
                    "period_days": days,
                    "total_actions": total_result["total_actions"],
                    "unique_users": total_result["unique_users"],
                    "unique_actions": total_result["unique_actions"],
                    "failed_logins": failed_logins_result["failed_logins"],
                    "actions_by_type": [dict(row) for row in actions_result]
                }
                
        except sqlite3.Error as e:
            raise DatabaseConnectionError(f"Failed to retrieve audit statistics: {e}")
    
    def export_audit_logs(
        self,
        output_file: Path,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        user_id: Optional[int] = None
    ):
        """
        Export audit logs to JSON file
        
        Args:
            output_file: Path to output file
            start_date: Start date for export
            end_date: End date for export
            user_id: User ID to filter by
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                
                query = "SELECT * FROM audit_log WHERE 1=1"
                params = []
                
                if start_date:
                    query += " AND timestamp >= ?"
                    params.append(start_date.isoformat())
                
                if end_date:
                    query += " AND timestamp <= ?"
                    params.append(end_date.isoformat())
                
                if user_id:
                    query += " AND user_id = ?"
                    params.append(user_id)
                
                query += " ORDER BY timestamp"
                
                cursor = conn.execute(query, params)
                logs = [dict(row) for row in cursor.fetchall()]
                
                with open(output_file, 'w', encoding='utf-8') as f:
                    json.dump(logs, f, indent=2, ensure_ascii=False)
                    
        except (sqlite3.Error, IOError) as e:
            raise DatabaseConnectionError(f"Failed to export audit logs: {e}")


# Default audit logger instance
_default_audit_logger = None


def get_audit_logger() -> AuditLogger:
    """Get default audit logger instance"""
    global _default_audit_logger
    if _default_audit_logger is None:
        _default_audit_logger = AuditLogger()
    return _default_audit_logger


def log_action(
    action: AuditAction,
    user_id: Optional[int] = None,
    username: Optional[str] = None,
    **kwargs
):
    """
    Convenience function to log audit action
    
    Args:
        action: Audit action to log
        user_id: User ID performing the action
        username: Username performing the action
        **kwargs: Additional arguments for audit log
    """
    audit_logger = get_audit_logger()
    audit_logger.log_action(
        action=action,
        user_id=user_id,
        username=username,
        **kwargs
    )