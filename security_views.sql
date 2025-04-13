-- Security monitoring views

-- View to track personal data access
CREATE VIEW personal_data_access_view AS
SELECT 
    al.id AS log_id,
    al.username,
    al.action_type,
    al.action_time,
    pdl.data_category,
    u.id AS user_id,
    cr.consent_type,
    cr.expires_at AS consent_expires,
    CASE 
        WHEN cr.withdrawal_date IS NOT NULL THEN 'Withdrawn'
        WHEN cr.expires_at < CURRENT_TIMESTAMP THEN 'Expired'
        ELSE 'Valid'
    END AS consent_status
FROM access_log al
JOIN personal_data_locations pdl ON al.table_affected = pdl.table_name
JOIN users u ON pdl.user_id = u.id
LEFT JOIN consent_records cr ON u.id = cr.user_id;

-- View for active access policies
CREATE VIEW active_policies_view AS
SELECT 
    ap.role_name,
    ap.resource_name,
    ap.permission_type,
    ap.created_at,
    ap.created_by
FROM access_policies ap
WHERE ap.is_active = true;

-- View for GDPR compliance status
CREATE VIEW gdpr_compliance_status AS
SELECT 
    u.id AS user_id,
    u.email,
    COUNT(pdl.id) AS personal_data_locations_count,
    COUNT(cr.id) AS active_consents_count,
    MAX(cr.expires_at) AS latest_consent_expiry,
    BOOL_OR(cr.withdrawal_date IS NOT NULL) AS has_withdrawals
FROM users u
LEFT JOIN personal_data_locations pdl ON u.id = pdl.user_id
LEFT JOIN consent_records cr ON u.id = cr.user_id
    AND cr.withdrawal_date IS NULL 
    AND cr.expires_at > CURRENT_TIMESTAMP
GROUP BY u.id, u.email;
