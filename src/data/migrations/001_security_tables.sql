-- Security and Access Control Tables

-- User roles table for RBAC
CREATE TABLE IF NOT EXISTS user_roles (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    role_name TEXT NOT NULL,
    assigned_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    assigned_by INTEGER REFERENCES users(id),
    UNIQUE (user_id, role_name)
);

-- Role-based permissions table
CREATE TABLE IF NOT EXISTS role_permissions (
    id SERIAL PRIMARY KEY,
    role_name TEXT NOT NULL,
    resource_name TEXT NOT NULL,
    permission_type TEXT NOT NULL,
    granted_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    granted_by INTEGER REFERENCES users(id),
    CONSTRAINT valid_permission_type CHECK (permission_type IN ('READ', 'CREATE', 'UPDATE', 'DELETE')),
    UNIQUE (role_name, resource_name, permission_type)
);

-- Access audit log
CREATE TABLE IF NOT EXISTS access_log (
    id SERIAL PRIMARY KEY,
    username TEXT NOT NULL,
    action_type TEXT NOT NULL,
    action_time TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    table_affected TEXT NOT NULL,
    record_id INTEGER,
    details TEXT
);

-- Rate limiting table
CREATE TABLE IF NOT EXISTS rate_limits (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    action_type TEXT NOT NULL,
    window_start TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    count INTEGER DEFAULT 1,
    UNIQUE (user_id, action_type, window_start)
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_user_roles_user_id ON user_roles(user_id);
CREATE INDEX IF NOT EXISTS idx_role_permissions_role ON role_permissions(role_name);
CREATE INDEX IF NOT EXISTS idx_access_log_username ON access_log(username);
CREATE INDEX IF NOT EXISTS idx_access_log_action_time ON access_log(action_time);
CREATE INDEX IF NOT EXISTS idx_rate_limits_user_window ON rate_limits(user_id, window_start);
