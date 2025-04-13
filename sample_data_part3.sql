-- Topics and Document-Topic Relationships
BEGIN;

-- Topics
INSERT INTO topics (id, name, description, extraction_method, global_importance) VALUES
(1, 'Artificial Intelligence', 'Topics related to AI and machine learning technologies', 'manual', 0.9),
(2, 'Market Analysis', 'Market research and analysis topics', 'manual', 0.8),
(3, 'Technical Documentation', 'Technical guides and documentation', 'manual', 0.7),
(4, 'Sustainability', 'Environmental and sustainability topics', 'manual', 0.8),
(5, 'Project Management', 'Project planning and implementation', 'manual', 0.7);

-- Document-Topic relationships
INSERT INTO document_topics (document_id, topic_id, relevance_score, extracted_by_tool) VALUES
(1, 2, 0.95, 'topic_analyzer_v1'),
(1, 1, 0.75, 'topic_analyzer_v1'),
(2, 1, 0.90, 'topic_analyzer_v1'),
(2, 3, 0.85, 'topic_analyzer_v1'),
(3, 5, 0.90, 'topic_analyzer_v1'),
(3, 3, 0.70, 'topic_analyzer_v1'),
(4, 4, 0.95, 'topic_analyzer_v1'),
(5, 3, 0.95, 'topic_analyzer_v1');

COMMIT;
