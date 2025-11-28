"""
CLI Authentication Tools for Exercises-and-Evaluation Project

Provides command-line interface for user management and authentication
while maintaining educational accessibility and manifesto alignment.
"""

import os
import sys
import getpass
import argparse
from pathlib import Path
from typing import Optional

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from auth.authentication_middleware import AuthenticationMiddleware, get_authentication_middleware
from auth.permission_manager import Role, Permission
from auth.exceptions import AuthenticationError, AuthorizationError


class CLIAuth:
    """Command-line interface for authentication operations"""
    
    def __init__(self):
        self.auth_middleware = get_authentication_middleware()
    
    def login(self, username: Optional[str] = None) -> bool:
        """
        Handle user login from command line
        
        Args:
            username: Username to login (optional, will prompt if not provided)
            
        Returns:
            True if login successful, False otherwise
        """
        try:
            if not username:
                username = input("Username: ").strip()
            
            password = getpass.getpass("Password: ")
            
            result = self.auth_middleware.authenticate_user(username, password)
            
            # Store tokens in environment variables for CLI usage
            os.environ['AUTH_TOKEN'] = result['access_token']
            os.environ['REFRESH_TOKEN'] = result['refresh_token']
            os.environ['USER_ROLE'] = result['role']
            os.environ['USERNAME'] = result['user']['username']
            
            print(f"✅ Login successful! Welcome, {result['user']['full_name'] or username}")
            print(f"Role: {result['role']}")
            print("Tokens stored in environment variables for this session.")
            
            return True
            
        except AuthenticationError as e:
            print(f"❌ Login failed: {e}")
            return False
        except KeyboardInterrupt:
            print("\n👋 Login cancelled")
            return False
    
    def logout(self):
        """Handle user logout from command line"""
        try:
            access_token = os.getenv('AUTH_TOKEN')
            refresh_token = os.getenv('REFRESH_TOKEN')
            
            if not access_token:
                print("ℹ️  No active session found")
                return
            
            self.auth_middleware.logout_user(access_token, refresh_token)
            
            # Clear environment variables
            for var in ['AUTH_TOKEN', 'REFRESH_TOKEN', 'USER_ROLE', 'USERNAME']:
                if var in os.environ:
                    del os.environ[var]
            
            print("✅ Logged out successfully")
            
        except Exception as e:
            print(f"❌ Logout failed: {e}")
    
    def create_user(self, interactive: bool = True) -> bool:
        """
        Create new user from command line
        
        Args:
            interactive: Whether to prompt for user input
            
        Returns:
            True if user created successfully
        """
        try:
            if interactive:
                print("📝 Create New User")
                print("=" * 30)
                
                username = input("Username: ").strip()
                if not username:
                    print("❌ Username is required")
                    return False
                
                email = input("Email: ").strip()
                if not email:
                    print("❌ Email is required")
                    return False
                
                password = getpass.getpass("Password: ")
                if not password:
                    print("❌ Password is required")
                    return False
                
                confirm_password = getpass.getpass("Confirm Password: ")
                if password != confirm_password:
                    print("❌ Passwords do not match")
                    return False
                
                full_name = input("Full Name (optional): ").strip() or None
                institution = input("Institution (optional): ").strip() or None
                
                # Role selection
                print("\nAvailable Roles:")
                for i, role in enumerate(Role, 1):
                    print(f"{i}. {role.value} - {self.auth_middleware.permission_manager.get_role_description(role)}")
                
                role_choice = input("Select role (1-4, default: guest): ").strip()
                try:
                    role_index = int(role_choice) - 1 if role_choice else 0
                    role = list(Role)[role_index]
                except (ValueError, IndexError):
                    role = Role.GUEST
                
                # Create user
                user_id = self.auth_middleware.create_user(
                    username=username,
                    email=email,
                    password=password,
                    role=role,
                    full_name=full_name,
                    institution=institution
                )
                
                print(f"✅ User created successfully! ID: {user_id}")
                print(f"Username: {username}")
                print(f"Role: {role.value}")
                print("\n📧 Note: Email verification should be implemented in production")
                
                return True
                
        except AuthenticationError as e:
            print(f"❌ User creation failed: {e}")
            return False
        except KeyboardInterrupt:
            print("\n👋 User creation cancelled")
            return False
    
    def check_auth(self) -> bool:
        """Check if current session is authenticated"""
        access_token = os.getenv('AUTH_TOKEN')
        if not access_token:
            print("❌ No authentication token found")
            return False
        
        try:
            user_context = self.auth_middleware.authenticate_token(access_token)
            print(f"✅ Authenticated as: {user_context['username']}")
            print(f"Role: {user_context['role'].value}")
            print(f"Full Name: {user_context.get('full_name', 'N/A')}")
            return True
        except AuthenticationError as e:
            print(f"❌ Authentication failed: {e}")
            return False
    
    def refresh_token(self) -> bool:
        """Refresh access token"""
        refresh_token = os.getenv('REFRESH_TOKEN')
        if not refresh_token:
            print("❌ No refresh token found")
            return False
        
        try:
            new_access_token = self.auth_middleware.refresh_token(refresh_token)
            os.environ['AUTH_TOKEN'] = new_access_token
            print("✅ Access token refreshed successfully")
            return True
        except AuthenticationError as e:
            print(f"❌ Token refresh failed: {e}")
            return False
    
    def list_permissions(self, role_name: Optional[str] = None):
        """List permissions for a role"""
        if role_name:
            try:
                role = self.auth_middleware.permission_manager.validate_role(role_name)
                permissions = self.auth_middleware.permission_manager.get_permissions_for_role(role)
                
                print(f"\n📋 Permissions for {role.value}:")
                print("=" * 40)
                
                for permission in sorted(permissions, key=lambda p: p.value):
                    description = self.auth_middleware.permission_manager.get_permission_description(permission)
                    print(f"• {permission.value}")
                    print(f"  {description}")
                    print()
                
            except ValueError as e:
                print(f"❌ {e}")
        else:
            print("\n📋 Available Roles:")
            print("=" * 30)
            
            for role in Role:
                description = self.auth_middleware.permission_manager.get_role_description(role)
                print(f"• {role.value}")
                print(f"  {description}")
                print()
    
    def status(self):
        """Show authentication system status"""
        print("🔐 Authentication System Status")
        print("=" * 40)
        
        # Check if authenticated
        if os.getenv('AUTH_TOKEN'):
            self.check_auth()
        else:
            print("Status: Not authenticated")
        
        # Check environment variables
        print(f"\nEnvironment Variables:")
        print(f"AUTH_TOKEN: {'✅ Set' if os.getenv('AUTH_TOKEN') else '❌ Not set'}")
        print(f"REFRESH_TOKEN: {'✅ Set' if os.getenv('REFRESH_TOKEN') else '❌ Not set'}")
        print(f"USER_ROLE: {'✅ Set' if os.getenv('USER_ROLE') else '❌ Not set'}")
        print(f"USERNAME: {'✅ Set' if os.getenv('USERNAME') else '❌ Not set'}")
        
        # Check database
        db_path = self.auth_middleware.db_path
        print(f"\nDatabase: {'✅ Exists' if db_path.exists() else '❌ Not found'}")
        print(f"Path: {db_path}")


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description="Authentication CLI for Exercises-and-Evaluation Project",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python -m auth.cli_auth login
  python -m auth.cli_auth login admin
  python -m auth.cli_auth logout
  python -m auth.cli_auth create-user
  python -m auth.cli_auth check-auth
  python -m auth.cli_auth refresh-token
  python -m auth.cli_auth list-permissions teacher
  python -m auth.cli_auth status
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Login command
    login_parser = subparsers.add_parser('login', help='Login to the system')
    login_parser.add_argument('username', nargs='?', help='Username to login')
    
    # Logout command
    subparsers.add_parser('logout', help='Logout from the system')
    
    # Create user command
    create_parser = subparsers.add_parser('create-user', help='Create a new user')
    create_parser.add_argument('--non-interactive', action='store_true', 
                           help='Create user in non-interactive mode')
    
    # Check auth command
    subparsers.add_parser('check-auth', help='Check current authentication status')
    
    # Refresh token command
    subparsers.add_parser('refresh-token', help='Refresh access token')
    
    # List permissions command
    perms_parser = subparsers.add_parser('list-permissions', help='List permissions for role')
    perms_parser.add_argument('role', nargs='?', help='Role to list permissions for')
    
    # Status command
    subparsers.add_parser('status', help='Show authentication system status')
    
    # Parse arguments
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    # Execute command
    cli_auth = CLIAuth()
    
    try:
        if args.command == 'login':
            cli_auth.login(args.username)
        elif args.command == 'logout':
            cli_auth.logout()
        elif args.command == 'create-user':
            cli_auth.create_user(interactive=not args.non_interactive)
        elif args.command == 'check-auth':
            cli_auth.check_auth()
        elif args.command == 'refresh-token':
            cli_auth.refresh_token()
        elif args.command == 'list-permissions':
            cli_auth.list_permissions(args.role)
        elif args.command == 'status':
            cli_auth.status()
        else:
            parser.print_help()
            
    except KeyboardInterrupt:
        print("\n👋 Operation cancelled")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()