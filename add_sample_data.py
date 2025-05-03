from axai_pg import (
    Organization, User, Document, Summary, Topic,
    DatabaseManager, PostgresConnectionConfig, GraphNode, GraphRelationship
)
import os

def add_sample_data():
    # Initialize database connection
    conn_config = PostgresConnectionConfig(
        host=os.getenv("POSTGRES_HOST", "postgres"),
        port=5432,
        database=os.getenv("POSTGRES_DB", "test_db"),
        username=os.getenv("POSTGRES_USER", "test_user"),
        password=os.getenv("POSTGRES_PASSWORD", "test_password"),
        schema="public"
    )
    DatabaseManager.initialize(conn_config)
    db = DatabaseManager.get_instance()

    with db.session_scope() as session:
        # Create organizations
        org1 = Organization(name="Tech Corp")
        org2 = Organization(name="Research Institute")
        session.add_all([org1, org2])
        session.flush()

        # Create users
        user1 = User(
            username="johndoe",
            email="john@techcorp.com",
            org_id=org1.id
        )
        user2 = User(
            username="janedoe",
            email="jane@research.org",
            org_id=org2.id
        )
        session.add_all([user1, user2])
        session.flush()

        # Create documents
        doc1 = Document(
            title="Project Proposal",
            content="This is a detailed project proposal for the new AI initiative.",
            owner_id=user1.id,
            org_id=org1.id,
            document_type="proposal",
            status="draft"
        )
        doc2 = Document(
            title="Research Findings",
            content="Analysis of recent experiments and their outcomes.",
            owner_id=user2.id,
            org_id=org2.id,
            document_type="report",
            status="published"
        )
        session.add_all([doc1, doc2])
        session.flush()

        # Create summaries
        summary1 = Summary(
            document_id=doc1.id,
            content="A proposal for implementing AI solutions in business processes.",
            summary_type="abstract",
            tool_agent="gpt-4",
            confidence_score=0.95
        )
        summary2 = Summary(
            document_id=doc2.id,
            content="Key findings from recent research experiments.",
            summary_type="executive",
            tool_agent="gpt-4",
            confidence_score=0.92
        )
        session.add_all([summary1, summary2])
        session.flush()

        # Create topics
        topic1 = Topic(
            name="Artificial Intelligence",
            description="Technologies and applications of AI",
            keywords=["AI", "machine learning", "neural networks"],
            extraction_method="automatic",
            global_importance=0.9
        )
        topic2 = Topic(
            name="Research Methodology",
            description="Scientific research approaches and techniques",
            keywords=["research", "experiments", "analysis"],
            extraction_method="manual",
            global_importance=0.85
        )
        session.add_all([topic1, topic2])
        session.flush()

        # Associate documents with topics
        from axai_pg import DocumentTopic
        doc_topic1 = DocumentTopic(
            document_id=doc1.id,
            topic_id=topic1.id,
            relevance_score=0.95,
            extracted_by_tool="gpt-4"
        )
        doc_topic2 = DocumentTopic(
            document_id=doc2.id,
            topic_id=topic2.id,
            relevance_score=0.92,
            extracted_by_tool="gpt-4"
        )
        session.add_all([doc_topic1, doc_topic2])
        session.flush()

        # Create graph nodes for documents
        graph_node1 = GraphNode(
            document_id=doc1.id,
            node_type="document",
            name="Project Proposal Node",
            description="Graph node representing the project proposal document",
            properties={"keywords": ["AI", "business", "process"]},
            created_by_tool="graph_builder_v1",
            is_active=True
        )
        graph_node2 = GraphNode(
            document_id=doc2.id,
            node_type="document",
            name="Research Findings Node",
            description="Graph node representing the research findings document",
            properties={"keywords": ["research", "experiments", "analysis"]},
            created_by_tool="graph_builder_v1",
            is_active=True
        )
        session.add_all([graph_node1, graph_node2])
        session.flush()

        # Create graph relationships between nodes
        relationship1 = GraphRelationship(
            source_node_id=graph_node1.id,
            target_node_id=graph_node2.id,
            relationship_type="references",
            is_directed=True,
            weight=0.85,
            confidence_score=0.92,
            properties={"context": "The proposal references the research findings"},
            created_by_tool="relationship_detector_v1",
            is_active=True
        )
        relationship2 = GraphRelationship(
            source_node_id=graph_node2.id,
            target_node_id=graph_node1.id,
            relationship_type="supports",
            is_directed=True,
            weight=0.75,
            confidence_score=0.88,
            properties={"context": "The research findings support the proposal"},
            created_by_tool="relationship_detector_v1",
            is_active=True
        )
        session.add_all([relationship1, relationship2])
        session.flush()

        print("Sample data added successfully!")

if __name__ == "__main__":
    add_sample_data() 