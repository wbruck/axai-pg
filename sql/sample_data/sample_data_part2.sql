-- Documents and Summaries
BEGIN;

-- Documents
INSERT INTO documents (id, title, content, owner_id, org_id, document_type, status, version, file_format, word_count, processing_status, metadata) VALUES
(1, 'Q4 2023 Market Analysis', 'This comprehensive market analysis examines key trends in the technology sector during Q4 2023. Major findings include increased adoption of AI technologies and growing demand for sustainable solutions. The report highlights significant market movements and emerging opportunities.', 1, 1, 'report', 'published', 1, 'markdown', 2500, 'complete', '{"category": "market_research", "department": "research", "confidentiality": "internal"}'::jsonb),

(2, 'Machine Learning Best Practices', 'A guide to implementing machine learning solutions in enterprise environments. This document covers data preprocessing, model selection, validation strategies, and deployment considerations for successful ML implementations.', 2, 1, 'guide', 'published', 1, 'markdown', 3500, 'complete', '{"category": "technical", "department": "engineering", "audience": "developers"}'::jsonb),

(3, 'Project Alpha Proposal', 'Project proposal for implementing a new customer relationship management system. This document outlines the business requirements, technical specifications, and implementation timeline for the proposed CRM upgrade.', 3, 2, 'proposal', 'draft', 1, 'markdown', 1800, 'complete', '{"category": "project", "department": "it", "priority": "high"}'::jsonb),

(4, 'Sustainability Report 2023', 'Annual sustainability report detailing our environmental initiatives and impact. Covers carbon footprint reduction efforts, green technology adoption, and sustainability goals for 2024.', 4, 2, 'report', 'published', 1, 'pdf', 4200, 'complete', '{"category": "sustainability", "department": "operations", "period": "2023"}'::jsonb),

(5, 'API Documentation v2.0', 'Technical documentation for the updated REST API endpoints. Includes authentication methods, request/response formats, and example implementations for all major endpoints.', 6, 3, 'documentation', 'published', 1, 'markdown', 5000, 'complete', '{"category": "technical", "department": "engineering", "version": "2.0"}'::jsonb);

-- Summaries
INSERT INTO summaries (id, document_id, content, summary_type, tool_agent, confidence_score, word_count, language_code, status) VALUES
(1, 1, 'Q4 2023 analysis shows increased AI adoption and sustainability focus in tech sector. Key metrics indicate 25% growth in AI implementations and 40% rise in green tech investments.', 'executive', 'gpt-4', 0.92, 150, 'en', 'final'),

(2, 1, 'Technical analysis of Q4 2023 market trends focusing on AI adoption metrics, sustainability initiatives, and market growth indicators. Includes statistical analysis of key performance metrics.', 'technical', 'gpt-4', 0.89, 250, 'en', 'final'),

(3, 2, 'Comprehensive guide to enterprise ML implementation covering data preparation, model selection, validation, and deployment. Emphasizes practical approaches and best practices.', 'executive', 'gpt-4', 0.95, 180, 'en', 'final'),

(4, 3, 'Proposal for CRM system upgrade including technical requirements, timeline, and budget estimates. ROI analysis projects 30% efficiency improvement.', 'executive', 'gpt-4', 0.88, 120, 'en', 'final'),

(5, 4, 'Annual sustainability report highlighting 15% reduction in carbon footprint, implementation of green technologies, and future environmental goals.', 'executive', 'gpt-4', 0.91, 130, 'en', 'final'),

(6, 5, 'Technical overview of API v2.0 changes including new endpoints, authentication improvements, and backward compatibility considerations.', 'technical', 'gpt-4', 0.94, 160, 'en', 'final');

COMMIT;
