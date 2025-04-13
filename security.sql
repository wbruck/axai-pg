-- Security setup for document management system

-- Basic audit table for tracking access
CREATE TABLE access_log (
    id SERIAL PRIMARY KEY,
    username TEXT NOT NULL,
    action_type TEXT NOT NULL,
    action_time TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    table_affected TEXT NOT NULL,
    record_id INTEGER,
    details TEXT
);

-- GDPR consent tracking
CREATE TABLE consent_records (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id),
    consent_type TEXT NOT NULL,
    given_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP WITH TIME ZONE,
    consent_details TEXT,
    withdrawal_date TIMESTAMP WITH TIME ZONE
);

-- Data access policies
CREATE TABLE access_policies (
    id SERIAL PRIMARY KEY,
    role_name TEXT NOT NULL,
    resource_name TEXT NOT NULL,
    permission_type TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    created_by TEXT NOT NULL,
    is_active BOOLEAN DEFAULT true
);

-- Indexes for performance
CREATE INDEX idx_access_log_time ON access_log(action_time);
CREATE INDEX idx_access_log_user ON access_log(username);
CREATE INDEX idx_consent_user ON consent_records(user_id);
CREATE INDEX idx_consent_type ON consent_records(consent_type);
CREATE INDEX idx_access_policies_role ON access_policies(role_name);
