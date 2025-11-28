-- Authentication Database Schema for Exercises-and-Evaluation Project
-- This schema provides comprehensive user management while maintaining educational accessibility

-- Users table with comprehensive user information
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
    metadata TEXT,  -- JSON for additional user information
    profile_image VARCHAR(255),  -- Path to profile image
    bio TEXT,  -- User biography
    preferences TEXT  -- JSON for user preferences
);

-- Sessions table for refresh token management
CREATE TABLE IF NOT EXISTS sessions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    refresh_token VARCHAR(255) NOT NULL,
    expires_at TIMESTAMP NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_used TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE,
    ip_address VARCHAR(45),  -- IPv4 or IPv6 address
    user_agent TEXT,  -- Client user agent string
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- Password reset tokens table
CREATE TABLE IF NOT EXISTS password_reset_tokens (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    token VARCHAR(255) NOT NULL UNIQUE,
    expires_at TIMESTAMP NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    used BOOLEAN DEFAULT FALSE,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- Email verification tokens table
CREATE TABLE IF NOT EXISTS email_verification_tokens (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    token VARCHAR(255) NOT NULL UNIQUE,
    expires_at TIMESTAMP NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    used BOOLEAN DEFAULT FALSE,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- User roles history table (for audit purposes)
CREATE TABLE IF NOT EXISTS user_role_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    old_role VARCHAR(20),
    new_role VARCHAR(20) NOT NULL,
    changed_by INTEGER,  -- Admin who changed the role
    changed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    reason TEXT,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (changed_by) REFERENCES users(id) ON DELETE SET NULL
);

-- User login history table
CREATE TABLE IF NOT EXISTS login_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    login_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    ip_address VARCHAR(45),
    user_agent TEXT,
    success BOOLEAN DEFAULT TRUE,
    failure_reason TEXT,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- Create indexes for better performance
CREATE UNIQUE INDEX IF NOT EXISTS idx_users_username ON users(username);
CREATE UNIQUE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_users_role ON users(role);
CREATE INDEX IF NOT EXISTS idx_users_active ON users(is_active);
CREATE INDEX IF NOT EXISTS idx_users_created_at ON users(created_at);

CREATE INDEX IF NOT EXISTS idx_sessions_user_id ON sessions(user_id);
CREATE INDEX IF NOT EXISTS idx_sessions_refresh_token ON sessions(refresh_token);
CREATE INDEX IF NOT EXISTS idx_sessions_expires_at ON sessions(expires_at);
CREATE INDEX IF NOT EXISTS idx_sessions_active ON sessions(is_active);

CREATE INDEX IF NOT EXISTS idx_password_reset_user_id ON password_reset_tokens(user_id);
CREATE INDEX IF NOT EXISTS idx_password_reset_token ON password_reset_tokens(token);
CREATE INDEX IF NOT EXISTS idx_password_reset_expires_at ON password_reset_tokens(expires_at);

CREATE INDEX IF NOT EXISTS idx_email_verification_user_id ON email_verification_tokens(user_id);
CREATE INDEX IF NOT EXISTS idx_email_verification_token ON email_verification_tokens(token);
CREATE INDEX IF NOT EXISTS idx_email_verification_expires_at ON email_verification_tokens(expires_at);

CREATE INDEX IF NOT EXISTS idx_user_role_history_user_id ON user_role_history(user_id);
CREATE INDEX IF NOT EXISTS idx_user_role_history_changed_at ON user_role_history(changed_at);

CREATE INDEX IF NOT EXISTS idx_login_history_user_id ON login_history(user_id);
CREATE INDEX IF NOT EXISTS idx_login_history_login_time ON login_history(login_time);
CREATE INDEX IF NOT EXISTS idx_login_history_success ON login_history(success);

-- Insert default admin user (password: admin123, change immediately)
INSERT OR IGNORE INTO users (
    id, username, email, password_hash, role, full_name, is_active, email_verified
) VALUES (
    1, 
    'admin', 
    'admin@exercises-evaluation.local', 
    '240be518fabd2724ddb6f04eeb1da5967448d7e831c08c8fa822809f74c720a9',  -- SHA256 of 'admin123'
    'admin', 
    'System Administrator', 
    TRUE, 
    TRUE
);

-- Insert default guest user (for read-only access)
INSERT OR IGNORE INTO users (
    id, username, email, password_hash, role, full_name, is_active, email_verified
) VALUES (
    2, 
    'guest', 
    'guest@exercises-evaluation.local', 
    '084e0343a0486ff05530df6c705c8bb4'  -- SHA256 of 'guest'
    'guest', 
    'Guest User', 
    TRUE, 
    TRUE
);

-- Create view for active users with their current sessions
CREATE VIEW IF NOT EXISTS active_users_with_sessions AS
SELECT 
    u.id,
    u.username,
    u.email,
    u.role,
    u.full_name,
    u.institution,
    u.last_login,
    s.id as session_id,
    s.expires_at,
    s.ip_address,
    s.user_agent
FROM users u
LEFT JOIN sessions s ON u.id = s.user_id AND s.is_active = TRUE AND s.expires_at > CURRENT_TIMESTAMP
WHERE u.is_active = TRUE;

-- Create trigger to update user role history
CREATE TRIGGER IF NOT EXISTS update_user_role_history
AFTER UPDATE OF role ON users
WHEN OLD.role != NEW.role
BEGIN
    INSERT INTO user_role_history (
        user_id, old_role, new_role, changed_by, reason
    ) VALUES (
        NEW.id, OLD.role, NEW.role, NULL, 'Role updated via system'
    );
END;

-- Create trigger to log login attempts
CREATE TRIGGER IF NOT EXISTS log_login_attempt
AFTER UPDATE OF last_login ON users
WHEN NEW.last_login IS NOT NULL AND (OLD.last_login IS NULL OR NEW.last_login != OLD.last_login)
BEGIN
    INSERT INTO login_history (
        user_id, login_time, success
    ) VALUES (
        NEW.id, NEW.last_login, TRUE
    );
END;