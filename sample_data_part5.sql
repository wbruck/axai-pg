-- Graph Structure for Document Relationships
BEGIN;

-- Graph nodes representing documents
INSERT INTO graph_nodes (id, document_id, node_type, name, created_by_tool) VALUES
(1, 1, 'document', 'Q4 2023 Market Analysis', 'graph_builder_v1'),
(2, 2, 'document', 'Machine Learning Best Practices', 'graph_builder_v1'),
(3, 3, 'document', 'Project Alpha Proposal', 'graph_builder_v1'),
(4, 4, 'document', 'Sustainability Report 2023', 'graph_builder_v1'),
(5, 5, 'document', 'API Documentation v2.0', 'graph_builder_v1');

-- Graph relationships between documents
INSERT INTO graph_relationships (id, source_node_id, target_node_id, relationship_type, weight, confidence_score, created_by_tool) VALUES
(1, 1, 2, 'references', 0.8, 0.85, 'relationship_detector_v1'),
(2, 2, 3, 'supports', 0.7, 0.80, 'relationship_detector_v1'),
(3, 1, 4, 'related', 0.6, 0.75, 'relationship_detector_v1'),
(4, 3, 5, 'implements', 0.9, 0.95, 'relationship_detector_v1'),
(5, 2, 5, 'references', 0.7, 0.82, 'relationship_detector_v1');

COMMIT;
