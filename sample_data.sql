-- Sample data set for document management system
-- Contains realistic data for development and testing

-- Organizations and Users
BEGIN;

-- Organizations
INSERT INTO organizations (id, name, created_at) VALUES
(1, 'Acme Research Labs', '2024-01-15T10:00:00Z'),
(2, 'Global Insights Corp', '2024-01-16T09:30:00Z'),
(3, 'Tech Innovation Partners', '2024-01-17T11:15:00Z');

-- Users across organizations
INSERT INTO users (id, username, email, org_id) VALUES
(1, 'sarah.smith', 'sarah.smith@acmeresearch.com', 1),
(2, 'john.doe', 'john.doe@acmeresearch.com', 1),
(3, 'mary.johnson', 'mary.johnson@globalinsights.com', 2),
(4, 'james.wilson', 'james.wilson@globalinsights.com', 2),
(5, 'robert.brown', 'robert.brown@globalinsights.com', 2),
(6, 'lisa.anderson', 'lisa.anderson@techinnovation.com', 3),
(7, 'michael.davis', 'michael.davis@techinnovation.com', 3);

COMMIT;
