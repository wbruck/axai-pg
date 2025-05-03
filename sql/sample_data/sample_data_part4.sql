-- Document Clusters and Memberships
BEGIN;

-- Document clusters
INSERT INTO document_clusters (id, name, description, algorithm, parameters) VALUES
(1, 'Technical Documentation', 'Cluster of technical documentation and guides', 'kmeans', '{"n_clusters": 3}'::jsonb),
(2, 'Market Research', 'Cluster of market analysis and research documents', 'kmeans', '{"n_clusters": 3}'::jsonb),
(3, 'Corporate Reports', 'Cluster of formal corporate reports and proposals', 'kmeans', '{"n_clusters": 3}'::jsonb);

-- Cluster memberships
INSERT INTO document_cluster_members (document_id, cluster_id, membership_score, is_primary_cluster) VALUES
(1, 2, 0.92, true),
(2, 1, 0.88, true),
(3, 3, 0.85, true),
(4, 3, 0.87, true),
(5, 1, 0.90, true),
(2, 2, 0.45, false),
(4, 2, 0.40, false);

COMMIT;
