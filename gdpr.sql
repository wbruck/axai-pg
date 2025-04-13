CREATE TABLE personal_data_locations (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id),
    table_name TEXT NOT NULL,
    column_name TEXT NOT NULL,
    data_category TEXT NOT NULL CHECK (data_category IN ('contact', 'identity', 'personal')),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE OR REPLACE FUNCTION anonymize_user(p_user_id INTEGER) RETURNS VOID AS $$
BEGIN
    -- Anonymize user record
    UPDATE users 
    SET username = 'anonymized_' || p_user_id::text,
        email = 'anonymous_' || p_user_id::text || '@redacted.local'
    WHERE id = p_user_id;
    
    -- Anonymize user's documents
    UPDATE documents 
    SET title = 'Redacted Document',
        content = 'This content has been redacted per user request.'
    WHERE owner_id = p_user_id;
END;
$$ LANGUAGE plpgsql;

CREATE INDEX idx_personal_data_user ON personal_data_locations(user_id);
CREATE INDEX idx_personal_data_category ON personal_data_locations(data_category);
