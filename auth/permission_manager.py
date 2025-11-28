"""
Role and Permission definitions for the authentication system

This module defines the role-based access control (RBAC) structure
for the Exercises-and-Evaluation project, maintaining educational accessibility
while providing necessary security layers.
"""

from enum import Enum
from typing import List, Dict, Set


class Role(Enum):
    """User roles with increasing permissions"""
    GUEST = "guest"
    STUDENT = "student" 
    TEACHER = "teacher"
    ADMIN = "admin"


class Permission(Enum):
    """Granular permissions for different system actions"""
    
    # Exercise permissions
    READ_EXERCISES = "read_exercises"
    CREATE_EXERCISES = "create_exercises"
    EDIT_OWN_EXERCISES = "edit_own_exercises"
    EDIT_ANY_EXERCISE = "edit_any_exercise"
    DELETE_OWN_EXERCISES = "delete_own_exercises"
    DELETE_ANY_EXERCISE = "delete_any_exercise"
    
    # Sebenta permissions
    VIEW_SEBENTAS = "view_sebentas"
    GENERATE_SEBENTAS = "generate_sebentas"
    EDIT_SEBENTAS = "edit_sebentas"
    
    # Test permissions
    GENERATE_TESTS = "generate_tests"
    VIEW_TESTS = "view_tests"
    GRADE_TESTS = "grade_tests"
    
    # Student permissions
    SUBMIT_SOLUTIONS = "submit_solutions"
    VIEW_OWN_PROGRESS = "view_own_progress"
    
    # Teacher permissions
    MANAGE_CLASSES = "manage_classes"
    VIEW_STUDENT_PROGRESS = "view_student_progress"
    
    # Admin permissions
    MANAGE_USERS = "manage_users"
    VIEW_AUDIT_LOGS = "view_audit_logs"
    SYSTEM_CONFIGURATION = "system_configuration"
    BACKUP_RESTORE = "backup_restore"
    
    # System permissions
    API_ACCESS = "api_access"
    CLI_ACCESS = "cli_access"


class PermissionManager:
    """Manages role-based access control (RBAC)"""
    
    # Role permission matrix
    ROLE_PERMISSIONS: Dict[Role, Set[Permission]] = {
        Role.GUEST: {
            Permission.READ_EXERCISES,
            Permission.VIEW_SEBENTAS,
            Permission.VIEW_TESTS,
            Permission.API_ACCESS,
        },
        
        Role.STUDENT: {
            Permission.READ_EXERCISES,
            Permission.VIEW_SEBENTAS,
            Permission.VIEW_TESTS,
            Permission.SUBMIT_SOLUTIONS,
            Permission.VIEW_OWN_PROGRESS,
            Permission.API_ACCESS,
            Permission.CLI_ACCESS,
        },
        
        Role.TEACHER: {
            Permission.READ_EXERCISES,
            Permission.CREATE_EXERCISES,
            Permission.EDIT_OWN_EXERCISES,
            Permission.DELETE_OWN_EXERCISES,
            Permission.VIEW_SEBENTAS,
            Permission.GENERATE_SEBENTAS,
            Permission.EDIT_SEBENTAS,
            Permission.GENERATE_TESTS,
            Permission.VIEW_TESTS,
            Permission.GRADE_TESTS,
            Permission.MANAGE_CLASSES,
            Permission.VIEW_STUDENT_PROGRESS,
            Permission.API_ACCESS,
            Permission.CLI_ACCESS,
        },
        
        Role.ADMIN: {
            # Admin has all permissions
            permission for permission in Permission
        }
    }
    
    def __init__(self):
        """Initialize permission manager"""
        self._role_cache = {}
        self._permission_cache = {}
    
    def get_permissions_for_role(self, role: Role) -> Set[Permission]:
        """Get all permissions for a specific role"""
        if role in self._role_cache:
            return self._role_cache[role]
        
        permissions = self.ROLE_PERMISSIONS.get(role, set())
        self._role_cache[role] = permissions
        return permissions.copy()
    
    def has_permission(self, role: Role, permission: Permission) -> bool:
        """Check if a role has a specific permission"""
        permissions = self.get_permissions_for_role(role)
        return permission in permissions
    
    def has_any_permission(self, role: Role, permissions: List[Permission]) -> bool:
        """Check if role has any of the specified permissions"""
        role_permissions = self.get_permissions_for_role(role)
        return any(perm in role_permissions for perm in permissions)
    
    def has_all_permissions(self, role: Role, permissions: List[Permission]) -> bool:
        """Check if role has all of the specified permissions"""
        role_permissions = self.get_permissions_for_role(role)
        return all(perm in role_permissions for perm in permissions)
    
    def get_role_hierarchy(self) -> List[Role]:
        """Get roles in order of increasing privilege"""
        return [Role.GUEST, Role.STUDENT, Role.TEACHER, Role.ADMIN]
    
    def can_upgrade_role(self, current_role: Role, target_role: Role) -> bool:
        """Check if a role can be upgraded to another role"""
        hierarchy = self.get_role_hierarchy()
        current_index = hierarchy.index(current_role)
        target_index = hierarchy.index(target_role)
        return target_index > current_index
    
    def get_default_role(self) -> Role:
        """Get the default role for new users"""
        return Role.GUEST
    
    def validate_role(self, role_name: str) -> Role:
        """Convert role name string to Role enum"""
        try:
            return Role(role_name.lower())
        except ValueError:
            raise ValueError(f"Invalid role: {role_name}. Valid roles: {[r.value for r in Role]}")
    
    def get_permission_description(self, permission: Permission) -> str:
        """Get human-readable description of permission"""
        descriptions = {
            Permission.READ_EXERCISES: "View and access exercise content",
            Permission.CREATE_EXERCISES: "Create new exercises",
            Permission.EDIT_OWN_EXERCISES: "Edit exercises created by the user",
            Permission.EDIT_ANY_EXERCISE: "Edit any exercise in the system",
            Permission.DELETE_OWN_EXERCISES: "Delete exercises created by the user",
            Permission.DELETE_ANY_EXERCISE: "Delete any exercise in the system",
            Permission.VIEW_SEBENTAS: "View and access sebenta content",
            Permission.GENERATE_SEBENTAS: "Generate new sebenta documents",
            Permission.EDIT_SEBENTAS: "Edit existing sebenta documents",
            Permission.GENERATE_TESTS: "Generate test documents",
            Permission.VIEW_TESTS: "View and access test content",
            Permission.GRADE_TESTS: "Grade and evaluate test submissions",
            Permission.SUBMIT_SOLUTIONS: "Submit solutions to exercises",
            Permission.VIEW_OWN_PROGRESS: "View personal learning progress",
            Permission.MANAGE_CLASSES: "Manage student classes and groups",
            Permission.VIEW_STUDENT_PROGRESS: "View student learning progress",
            Permission.MANAGE_USERS: "Create, modify, and delete user accounts",
            Permission.VIEW_AUDIT_LOGS: "Access system audit logs",
            Permission.SYSTEM_CONFIGURATION: "Modify system configuration",
            Permission.BACKUP_RESTORE: "Perform system backup and restore operations",
            Permission.API_ACCESS: "Access system APIs",
            Permission.CLI_ACCESS: "Access system via command line interface",
        }
        return descriptions.get(permission, "Unknown permission")
    
    def get_role_description(self, role: Role) -> str:
        """Get human-readable description of role"""
        descriptions = {
            Role.GUEST: "Guest user with read-only access to learning content",
            Role.STUDENT: "Student with access to learning materials and submission capabilities",
            Role.TEACHER: "Teacher with content creation and class management capabilities", 
            Role.ADMIN: "Administrator with full system access and management capabilities",
        }
        return descriptions.get(role, "Unknown role")
    
    def clear_cache(self):
        """Clear permission caches (useful for testing)"""
        self._role_cache.clear()
        self._permission_cache.clear()


# Convenience functions for common permission checks
def can_read_exercises(role: Role) -> bool:
    """Check if role can read exercises"""
    return PermissionManager().has_permission(role, Permission.READ_EXERCISES)


def can_create_exercises(role: Role) -> bool:
    """Check if role can create exercises"""
    return PermissionManager().has_permission(role, Permission.CREATE_EXERCISES)


def can_generate_sebentas(role: Role) -> bool:
    """Check if role can generate sebentas"""
    return PermissionManager().has_permission(role, Permission.GENERATE_SEBENTAS)


def can_generate_tests(role: Role) -> bool:
    """Check if role can generate tests"""
    return PermissionManager().has_permission(role, Permission.GENERATE_TESTS)


def can_manage_users(role: Role) -> bool:
    """Check if role can manage users"""
    return PermissionManager().has_permission(role, Permission.MANAGE_USERS)


def is_admin(role: Role) -> bool:
    """Check if role is admin"""
    return role == Role.ADMIN


def is_teacher_or_admin(role: Role) -> bool:
    """Check if role is teacher or admin"""
    return role in [Role.TEACHER, Role.ADMIN]


def is_student_or_above(role: Role) -> bool:
    """Check if role is student or higher"""
    hierarchy = PermissionManager().get_role_hierarchy()
    return hierarchy.index(role) >= hierarchy.index(Role.STUDENT)