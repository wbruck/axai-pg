-- Security and audit tables for PostgreSQL

-- Audit log for tracking database operations
CREATE TABLE audit_log (
    id SERIAL PRIMARY KEY,
    operation_type VARCHAR(50) NOT NULL,  -- INSERT, UPDATE, DELETE, SELECT
    table_name TEXT NOT NULL,
    record_id INTEGER,  -- Can be NULL for queries that don't target specific records
    user_id INTEGER REFERENCES users(id),
    performed_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    details JSONB  -- Additional operation-specific details
);

-- GDPR-related tracking
CREATE TABLE personal_data_registry (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id),
    table_name TEXT NOT NULL,
    column_name TEXT NOT NULL,
    record_id INTEGER NOT NULL,
    data_category TEXT NOT NULL,  -- e.g., 'contact', 'identification', etc.
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

CREATE TABLE data_subject_requests (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id),
    request_type VARCHAR(50) NOT NULL,  -- 'erasure', 'export', 'access'
    status VARCHAR(50) NOT NULL DEFAULT 'pending',
    requested_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    completed_at TIMESTAMP WITH TIME ZONE,
    handled_by INTEGER REFERENCES users(id),
    request_details JSONB,
    response_details JSONB
);

-- Role-based access control configuration table
CREATE TABLE role_permissions (
    id SERIAL PRIMARY KEY,
    role_name TEXT NOT NULL,
    table_name TEXT NOT NULL,
    permission_type TEXT NOT NULL,  -- 'SELECT', 'INSERT', 'UPDATE', 'DELETE', 'ALL'
    granted_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    granted_by INTEGER REFERENCES users(id),
    UNIQUE (role_name, table_name, permission_type)
);

-- Audit policy configuration
CREATE TABLE audit_policies (
    id SERIAL PRIMARY KEY,
    table_name TEXT NOT NULL,
    operation_type VARCHAR(50) NOT NULL,  -- INSERT, UPDATE, DELETE, SELECT
    is_enabled BOOLEAN NOT NULL DEFAULT true,
    detail_level VARCHAR(50) NOT NULL DEFAULT 'basic',  -- 'basic', 'detailed'
    retention_days INTEGER NOT NULL DEFAULT 90,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

-- Function to handle user data anonymization
CREATE OR REPLACE FUNCTION anonymize_user_data(user_id_param INTEGER) RETURNS VOID AS $$
BEGIN
    -- Update user record
    UPDATE users 
    SET username = 'anonymized_' || user_id_param,
        email = 'anonymized_' || user_id_param || '@anonymous.local'
    WHERE id = user_id_param;
    
    -- Update document ownership
    UPDATE documents 
    SET title = CASE 
            WHEN owner_id = user_id_param THEN 'Anonymized Document'
            ELSE title
        END,
        content = CASE 
            WHEN owner_id = user_id_param THEN 'Content has been anonymized'
            ELSE content
        END
    WHERE owner_id = user_id_param;
    
    -- Log the anonymization
    INSERT INTO audit_log (operation_type, table_name, record_id, user_id, details)
    VALUES ('ANONYMIZE', 'users', user_id_param, user_id_param, 
            jsonb_build_object('reason', 'GDPR_REQUEST'));
            
    -- Update request status if exists
    UPDATE data_subject_requests
    SET status = 'completed',
        completed_at = NOW()
    WHERE user_id = user_id_param 
    AND request_type = 'erasure' 
    AND status = 'pending';
END;
$$ LANGUAGE plpgsql;

-- Indexes for performance
CREATE INDEX idx_audit_log_user ON audit_log(user_id);
CREATE INDEX idx_audit_log_table ON audit_log(table_name);
CREATE INDEX idx_audit_log_operation ON audit_log(operation_type);
CREATE INDEX idx_personal_data_user ON personal_data_registry(user_id);
CREATE INDEX idx_data_requests_user ON data_subject_requests(user_id);
CREATE INDEX idx_data_requests_status ON data_subject_requests(status);
