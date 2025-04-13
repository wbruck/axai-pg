CREATE OR REPLACE FUNCTION handle_gdpr_request(
    p_user_id INTEGER,
    p_request_type TEXT
) RETURNS TEXT AS $$
BEGIN
    IF p_request_type = 'anonymize' THEN
        -- Anonymize user data
        UPDATE users 
        SET username = 'anonymized_' || p_user_id::text,
            email = 'anonymous_' || p_user_id::text || '@redacted.local'
        WHERE id = p_user_id;
        
        -- Anonymize user's documents
        UPDATE documents 
        SET title = 'Redacted Document',
            content = 'This content has been redacted per user request.'
        WHERE owner_id = p_user_id;
        
        RETURN 'User data anonymized successfully';
    ELSIF p_request_type = 'export' THEN
        RETURN 'Data export functionality not implemented';
    ELSE
        RETURN 'Invalid request type';
    END IF;
END;
$$ LANGUAGE plpgsql;
