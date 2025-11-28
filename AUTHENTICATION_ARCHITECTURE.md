# Authentication Architecture Design
## Exercises-and-Evaluation Project

**Version:** 1.0  
**Date:** 2025-11-28  
**Status:** Design Document  

---

## 🎯 Executive Summary

This document outlines a comprehensive authentication architecture for the Exercises-and-Evaluation project that maintains the system's educational mission while adding necessary security layers. The design is modular, reversible, and preserves existing workflows while introducing role-based access control.

### Current System Analysis
- **220+ exercises** with author metadata
- **26 VS Code tasks** requiring authentication integration  
- **Multiple Python scripts** for exercise and sebenta generation
- **Agent system integration** with manifesto compliance
- **Author-only system** currently with minimal access control

---

## 🏗️ Architecture Overview

### Core Design Principles
1. **Educational Accessibility First** - Maintain open access to learning content
2. **Manifesto Alignment** - Preserve educational mission and collaborative spirit
3. **Modular Implementation** - Reversible changes with minimal disruption
4. **Role-Based Security** - Granular permissions based on user roles
5. **Agent Compatibility** - Seamless integration with existing agent workflows

### Authentication Flow
```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   User Request │───▶│ Auth Middleware  │───▶│ Resource Check  │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                                │                        │
                                ▼                        ▼
                       ┌──────────────────┐    ┌─────────────────┐
                       │ JWT Validation  │───▶│ Action Execute  │
                       └──────────────────┘    └─────────────────┘
                                │                        │
                                ▼                        ▼
                       ┌──────────────────┐    ┌─────────────────┐
                       │   Audit Log     │    │   Response     │
                       └──────────────────┘    └─────────────────┘
```

---

## 🔐 Authentication Middleware Architecture

### 1. Core Authentication Module

**File:** `auth/authentication_middleware.py`

```python
class AuthenticationMiddleware:
    """Central authentication handler for all project operations"""
    
    def __init__(self):
        self.jwt_manager = JWTManager()
        self.permission_manager = PermissionManager()
        self.audit_logger = AuditLogger()
    
    def authenticate_request(self, request, required_permission):
        """Main authentication entry point"""
        pass
    
    def get_user_context(self, token):
        """Extract user information from JWT"""
        pass
    
    def check_permission(self, user_role, resource, action):
        """Verify user has required permission"""
        pass
```

### 2. JWT Token Management

**File:** `auth/jwt_manager.py`

```python
class JWTManager:
    """JSON Web Token management for secure authentication"""
    
    # Token expiration: 24 hours for standard, 7 days for remember_me
    ACCESS_TOKEN_EXPIRY = 24 * 60 * 60  # 24 hours
    REFRESH_TOKEN_EXPIRY = 7 * 24 * 60 * 60  # 7 days
    
    def generate_tokens(self, user_data):
        """Generate access and refresh tokens"""
        pass
    
    def validate_token(self, token):
        """Validate JWT token and return payload"""
        pass
    
    def refresh_access_token(self, refresh_token):
        """Generate new access token from refresh token"""
        pass
```

### 3. Permission Management System

**File:** `auth/permission_manager.py`

```python
class PermissionManager:
    """Role-based access control (RBAC) implementation"""
    
    ROLES = {
        'guest': ['read_exercises', 'view_sebentas'],
        'student': ['read_exercises', 'view_sebentas', 'submit_solutions'],
        'teacher': ['read_exercises', 'view_sebentas', 'create_exercises', 
                   'edit_own_exercises', 'generate_tests', 'manage_classes'],
        'admin': ['*']  # Full access
    }
    
    def check_permission(self, user_role, permission):
        """Check if user role grants specific permission"""
        pass
    
    def get_user_permissions(self, user_role):
        """Get all permissions for a user role"""
        pass
```

---

## 🗄️ Database Schema Design

### 1. Users Table

**File:** `auth/database_schema.sql`

```sql
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role ENUM('guest', 'student', 'teacher', 'admin') DEFAULT 'guest',
    full_name VARCHAR(100),
    institution VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE,
    email_verified BOOLEAN DEFAULT FALSE,
    metadata JSON  -- Store additional user information
);
```

### 2. Exercise Authors Enhancement

```sql
-- Extend existing exercise structure with author tracking
ALTER TABLE exercises ADD COLUMN author_id INTEGER;
ALTER TABLE exercises ADD COLUMN created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP;
ALTER TABLE exercises ADD COLUMN modified_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP;
ALTER TABLE exercises ADD COLUMN modified_by INTEGER;

-- Add foreign key constraint
ALTER TABLE exercises ADD CONSTRAINT fk_exercise_author 
    FOREIGN KEY (author_id) REFERENCES users(id);
```

### 3. Audit Log Table

```sql
CREATE TABLE audit_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    action VARCHAR(50) NOT NULL,
    resource_type VARCHAR(50),
    resource_id VARCHAR(50),
    details JSON,
    ip_address VARCHAR(45),
    user_agent TEXT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
);
```

### 4. Sessions Table

```sql
CREATE TABLE sessions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    refresh_token VARCHAR(255) NOT NULL,
    expires_at TIMESTAMP NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_used TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE,
    FOREIGN KEY (user_id) REFERENCES users(id)
);
```

---

## 🔧 Integration Points with Existing Scripts

### 1. Exercise Creation Scripts

**Modified Files:**
- `ExerciseDatabase/_tools/add_exercise_with_types.py`
- `ExerciseDatabase/_tools/add_exercise_minimal.py`
- `ExerciseDatabase/_tools/add_exercise_simple.py`

**Integration Pattern:**
```python
# Add authentication check at script entry point
from auth.authentication_middleware import AuthenticationMiddleware

auth = AuthenticationMiddleware()

def create_exercise(exercise_data):
    # Check if user has permission to create exercises
    user_context = auth.authenticate_request(request, 'create_exercises')
    
    # Add author information to exercise data
    exercise_data['author_id'] = user_context['user_id']
    exercise_data['author_name'] = user_context['full_name']
    
    # Continue with existing exercise creation logic
    return existing_create_exercise_logic(exercise_data)
```

### 2. Sebenta Generation Scripts

**Modified Files:**
- `scripts/generate_sebenta_interactive.py`
- `scripts/run_generate_sebenta_task.py`
- `SebentasDatabase/_tools/generate_sebentas.py`

**Integration Pattern:**
```python
def generate_sebenta(params):
    # Check if user can access sebenta generation
    user_context = auth.authenticate_request(request, 'generate_sebentas')
    
    # Log the generation request
    auth.audit_logger.log_action(
        user_id=user_context['user_id'],
        action='generate_sebenta',
        resource_type='sebenta',
        details=params
    )
    
    # Continue with existing sebenta generation
    return existing_sebenta_generation(params)
```

### 3. VS Code Tasks Integration

**Modified File:** `.vscode/tasks.json`

**Authentication-Enhanced Tasks:**
```json
{
  "label": "📝 Novo Exercício (Autenticado)",
  "type": "shell",
  "command": "python",
  "args": [
    "-c",
    "from auth.cli_auth import require_auth; from ExerciseDatabase._tools.add_exercise_minimal import main; require_auth(); main()"
  ],
  "problemMatcher": []
}
```

---

## 🛡️ Security Considerations

### 1. Password Security
- **Hashing Algorithm:** Argon2id (memory-hard, resistant to GPU attacks)
- **Salt:** Unique per-user salt (16 bytes minimum)
- **Password Policy:** Minimum 8 characters, complexity requirements

### 2. JWT Security
- **Algorithm:** RS256 with asymmetric keys
- **Token Storage:** HttpOnly, Secure cookies for web; secure storage for CLI
- **Refresh Tokens:** Rotated on each use, stored securely

### 3. API Security
- **Rate Limiting:** 100 requests per minute per user
- **Input Validation:** All inputs sanitized and validated
- **CORS:** Configured for specific origins
- **HTTPS:** Enforced for all communications

### 4. Audit and Monitoring
- **Comprehensive Logging:** All actions logged with user context
- **Failed Login Attempts:** Lockout after 5 failed attempts (15 minutes)
- **Session Management:** Automatic timeout and invalidation

---

## 🔄 Migration Strategy

### Phase 1: Infrastructure Setup (Week 1-2)
1. **Create authentication module structure**
2. **Implement core authentication middleware**
3. **Set up database schema extensions**
4. **Create user management CLI tools**

### Phase 2: Script Integration (Week 3-4)
1. **Integrate authentication into exercise creation scripts**
2. **Add authentication to sebenta generation tools**
3. **Update VS Code tasks with authentication**
4. **Create migration scripts for existing data**

### Phase 3: User Migration (Week 5-6)
1. **Create default admin user**
2. **Migrate existing author information**
3. **Set up role assignments for current users**
4. **Provide user onboarding documentation**

### Phase 4: Testing and Rollout (Week 7-8)
1. **Comprehensive testing of all authentication flows**
2. **Security audit and penetration testing**
3. **Gradual rollout with fallback option**
4. **User training and documentation**

---

## 📊 Role-Based Access Matrix

| Resource/Action | Guest | Student | Teacher | Admin |
|-----------------|-------|---------|---------|-------|
| View Exercises | ✅ | ✅ | ✅ | ✅ |
| View Sebentas | ✅ | ✅ | ✅ | ✅ |
| Submit Solutions | ❌ | ✅ | ✅ | ✅ |
| Create Exercises | ❌ | ❌ | ✅ | ✅ |
| Edit Own Exercises | ❌ | ❌ | ✅ | ✅ |
| Edit Any Exercise | ❌ | ❌ | ❌ | ✅ |
| Generate Tests | ❌ | ❌ | ✅ | ✅ |
| Manage Users | ❌ | ❌ | ❌ | ✅ |
| System Configuration | ❌ | ❌ | ❌ | ✅ |
| View Audit Logs | ❌ | ❌ | ❌ | ✅ |

---

## 🔌 Agent System Integration

### 1. Agent Authentication
```python
# Special authentication tokens for agents
class AgentAuthentication:
    """Handle authentication for automated agents"""
    
    AGENT_TOKENS = {
        'exercise-generator': 'agent_token_exercise_gen',
        'sebenta-generator': 'agent_token_sebenta_gen',
        'test-generator': 'agent_token_test_gen'
    }
    
    def authenticate_agent(self, agent_name, token):
        """Validate agent-specific authentication"""
        pass
```

### 2. Manifesto Compliance
- **Educational Access:** Guest role maintains open access to learning content
- **Collaborative Spirit:** Teacher role encourages content contribution
- **Quality Assurance:** Authentication enables better tracking and improvement
- **Agent Integration:** Automated systems continue functioning with proper authentication

---

## 📁 File Structure

```
auth/
├── __init__.py
├── authentication_middleware.py
├── jwt_manager.py
├── permission_manager.py
├── audit_logger.py
├── cli_auth.py
├── database_schema.sql
├── migration_scripts/
│   ├── 001_create_users_table.sql
│   ├── 002_add_author_tracking.sql
│   └── 003_migrate_existing_authors.py
├── cli_tools/
│   ├── user_manager.py
│   ├── role_manager.py
│   └── auth_setup.py
└── tests/
    ├── test_authentication.py
    ├── test_permissions.py
    └── test_jwt_management.py

# Modified existing files
ExerciseDatabase/_tools/
├── add_exercise_with_types.py (modified)
├── add_exercise_minimal.py (modified)
└── add_exercise_simple.py (modified)

scripts/
├── generate_sebenta_interactive.py (modified)
├── run_generate_sebenta_task.py (modified)
└── generate_test_interactive.py (modified)

.vscode/
└── tasks.json (modified)
```

---

## 🚀 Implementation Roadmap

### Immediate Actions (Week 1)
1. ✅ Create authentication module structure
2. ✅ Implement basic JWT management
3. ✅ Set up user database schema
4. ✅ Create CLI authentication tools

### Short-term Goals (Week 2-4)
1. 🔄 Integrate authentication into exercise creation scripts
2. 🔄 Add authentication to sebenta generation tools
3. 🔄 Update VS Code tasks
4. 🔄 Create user migration scripts

### Medium-term Goals (Week 5-8)
1. 📋 Comprehensive testing and security audit
2. 📋 User onboarding and documentation
3. 📋 Gradual rollout with monitoring
4. 📋 Performance optimization

### Long-term Considerations
- 🔄 Single Sign-On (SSO) integration
- 🔄 Multi-factor authentication (MFA)
- 🔄 Advanced audit and analytics
- 🔄 API rate limiting and quotas

---

## 📈 Success Metrics

### Security Metrics
- ✅ Zero unauthorized access attempts
- ✅ 100% action audit coverage
- ✅ < 2 seconds authentication latency
- ✅ 99.9% authentication uptime

### Usability Metrics
- ✅ < 30 seconds user onboarding time
- ✅ < 5 clicks to access resources
- ✅ 95% user satisfaction rate
- ✅ Zero disruption to existing workflows

### Educational Mission Metrics
- ✅ Maintained open access to learning content
- ✅ Increased teacher participation in content creation
- ✅ Improved exercise quality tracking
- ✅ Enhanced collaboration features

---

## 🔒 Security Checklist

### Authentication Security
- [ ] Strong password hashing (Argon2id)
- [ ] Secure JWT implementation
- [ ] Session management
- [ ] Rate limiting
- [ ] Account lockout protection

### Data Protection
- [ ] Input validation and sanitization
- [ ] SQL injection prevention
- [ ] XSS protection
- [ ] CSRF protection
- [ ] Secure file handling

### Monitoring and Auditing
- [ ] Comprehensive audit logging
- [ ] Failed login monitoring
- [ ] Anomaly detection
- [ ] Security incident response
- [ ] Regular security audits

---

## 📚 Documentation Requirements

### User Documentation
1. **User Guide:** How to authenticate and use the system
2. **Role Guide:** Understanding permissions and capabilities
3. **Troubleshooting:** Common authentication issues
4. **Security Best Practices:** Password management and security

### Developer Documentation
1. **API Documentation:** Authentication endpoints and usage
2. **Integration Guide:** How to integrate with existing scripts
3. **Security Guidelines:** Secure coding practices
4. **Migration Guide:** Step-by-step migration process

### Administrator Documentation
1. **Setup Guide:** Initial system configuration
2. **User Management:** Creating and managing users
3. **Audit Guide:** Monitoring and reviewing logs
4. **Backup and Recovery:** Data protection procedures

---

## 🎯 Conclusion

This authentication architecture provides a robust, secure, and manifesto-aligned solution for the Exercises-and-Evaluation project. The design maintains the system's educational mission while adding necessary security layers and enabling better content management and collaboration.

### Key Benefits
1. **Enhanced Security:** Comprehensive authentication and authorization
2. **Educational Accessibility:** Open access maintained for learning content
3. **Improved Collaboration:** Better tracking and quality assurance
4. **Agent Compatibility:** Seamless integration with existing automated systems
5. **Modular Design:** Reversible implementation with minimal disruption

### Next Steps
1. Review and approve this architecture design
2. Assign development resources for implementation
3. Establish timeline and milestones
4. Begin Phase 1 implementation

---

**Document Status:** Ready for Review  
**Next Review Date:** 2025-12-05  
**Contact:** Authentication Architecture Team