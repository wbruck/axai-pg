-- Security-related database functions

-- Function to cleanup old rate limit records
CREATE OR REPLACE FUNCTION cleanup_rate_limits() 
RETURNS void AS 
$func$
BEGIN
    DELETE FROM rate_limits 
    WHERE window_start < NOW() - INTERVAL '1 day';
END;
$func$ 
LANGUAGE plpgsql;

-- Function to check rate limit
CREATE OR REPLACE FUNCTION check_rate_limit(
    p_user_id INTEGER,
    p_action_type TEXT,
    p_limit INTEGER,
    p_window_seconds INTEGER
) 
RETURNS BOOLEAN AS 
$func$
DECLARE
    v_count INTEGER;
    v_window_start TIMESTAMP WITH TIME ZONE;
BEGIN
    v_window_start := date_trunc('second', NOW() - (p_window_seconds || ' seconds')::interval);
    
    SELECT COUNT(*) INTO v_count
    FROM rate_limits
    WHERE user_id = p_user_id
    AND action_type = p_action_type
    AND window_start >= v_window_start;
    
    RETURN v_count < p_limit;
END;
$func$ 
LANGUAGE plpgsql;

-- Function to verify organization access
CREATE OR REPLACE FUNCTION verify_org_access(
    p_user_id INTEGER,
    p_org_id INTEGER
) 
RETURNS BOOLEAN AS 
$func$
BEGIN
    RETURN EXISTS (
        SELECT 1 
        FROM users 
        WHERE id = p_user_id 
        AND org_id = p_org_id
    );
END;
$func$ 
LANGUAGE plpgsql;

-- Function to verify document access
CREATE OR REPLACE FUNCTION verify_doc_access(
    p_user_id INTEGER,
    p_doc_id INTEGER
) 
RETURNS BOOLEAN AS 
$func$
BEGIN
    RETURN EXISTS (
        SELECT 1 
        FROM documents d
        JOIN users u ON u.org_id = d.org_id
        WHERE d.id = p_doc_id
        AND (d.owner_id = p_user_id OR u.id = p_user_id)
    );
END;
$func$ 
LANGUAGE plpgsql;
