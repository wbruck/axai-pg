"""
Production Database Initialization Examples

This file demonstrates how to use DatabaseInitializer for production scenarios:
- Initial deployment setup
- Database migrations
- Environment-specific configurations
- Health checks and validation

⚠️  IMPORTANT: These examples are for production scenarios. Be careful when
    running them against production databases. Always test in staging first.
"""

import os
import sys
import logging
from pathlib import Path

from axai_pg.utils.db_initializer import DatabaseInitializer, DatabaseInitializerConfig
from axai_pg.data.config.database import (
    PostgresConnectionConfig,
    PostgresPoolConfig,
    DatabaseManager
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# =============================================================================
# Example 1: Initial Production Deployment
# =============================================================================

def initial_production_setup():
    """
    Example: First-time production database setup.

    This would typically be run during initial deployment to:
    1. Create the database
    2. Apply the schema
    3. Verify the setup

    DO NOT load sample data in production!
    """
    logger.info("Starting initial production setup...")

    # Load configuration from environment (production best practice)
    conn_config = PostgresConnectionConfig.from_env()

    # Configure with production pool settings
    pool_config = PostgresPoolConfig(
        pool_size=10,          # Larger pool for production
        max_overflow=20,       # Allow more overflow connections
        pool_timeout=30,       # Connection timeout
        pool_recycle=3600,     # Recycle connections after 1 hour
        pool_pre_ping=True     # Verify connections before use
    )

    db_config = DatabaseInitializerConfig(
        connection_config=conn_config,
        pool_config=pool_config,
        auto_create_db=True,
        auto_drop_on_exit=False,  # NEVER auto-drop in production!
        wait_timeout=60,
        retry_attempts=10
    )

    db_init = DatabaseInitializer(db_config)

    try:
        # Setup database with schema only (no sample data)
        success = db_init.setup_database(
            load_sample_data=False,
            apply_schema=True
        )

        if not success:
            logger.error("Database setup failed")
            sys.exit(1)

        # Verify setup
        with db_init.session_scope() as session:
            from sqlalchemy import text
            result = session.execute(text("SELECT COUNT(*) FROM organizations"))
            count = result.scalar()
            logger.info(f"Organizations table exists with {count} rows")

        logger.info("✅ Production database setup completed successfully")
        return True

    except Exception as e:
        logger.error(f"❌ Production setup failed: {e}")
        return False


# =============================================================================
# Example 2: Database Schema Update (Migration)
# =============================================================================

def apply_schema_update(schema_file_path: str):
    """
    Example: Apply schema updates to existing database.

    This would be used for rolling out schema changes to production.

    Args:
        schema_file_path: Path to the new schema SQL file

    ⚠️  WARNING: This will apply schema changes directly. Use with caution.
        Consider using proper migration tools (Alembic, Sqitch) for production.
    """
    logger.info(f"Applying schema update from {schema_file_path}...")

    conn_config = PostgresConnectionConfig.from_env()

    db_config = DatabaseInitializerConfig(
        connection_config=conn_config,
        schema_file=schema_file_path,
        auto_create_db=False,  # Database should already exist
        auto_drop_on_exit=False,
    )

    db_init = DatabaseInitializer(db_config)

    try:
        # Apply only the schema (database already exists)
        success = db_init.apply_schema(schema_file_path)

        if not success:
            logger.error("Schema update failed")
            return False

        logger.info("✅ Schema update completed successfully")
        return True

    except Exception as e:
        logger.error(f"❌ Schema update failed: {e}")
        return False


# =============================================================================
# Example 3: Environment-Specific Initialization
# =============================================================================

def environment_specific_setup(environment: str):
    """
    Example: Setup database based on environment (dev, staging, production).

    Args:
        environment: One of 'development', 'staging', 'production'
    """
    logger.info(f"Setting up database for {environment} environment...")

    conn_config = PostgresConnectionConfig.from_env()

    # Environment-specific configurations
    env_configs = {
        'development': {
            'pool_size': 5,
            'max_overflow': 5,
            'load_sample_data': True,
            'auto_drop_on_exit': False,
        },
        'staging': {
            'pool_size': 8,
            'max_overflow': 10,
            'load_sample_data': True,
            'auto_drop_on_exit': False,
        },
        'production': {
            'pool_size': 20,
            'max_overflow': 40,
            'load_sample_data': False,  # Never in production!
            'auto_drop_on_exit': False,
        }
    }

    if environment not in env_configs:
        logger.error(f"Unknown environment: {environment}")
        return False

    config = env_configs[environment]

    pool_config = PostgresPoolConfig(
        pool_size=config['pool_size'],
        max_overflow=config['max_overflow'],
        pool_timeout=30,
        pool_recycle=3600,
        pool_pre_ping=True
    )

    db_config = DatabaseInitializerConfig(
        connection_config=conn_config,
        pool_config=pool_config,
        auto_create_db=True,
        auto_drop_on_exit=config['auto_drop_on_exit'],
        wait_timeout=60,
        retry_attempts=10
    )

    db_init = DatabaseInitializer(db_config)

    try:
        success = db_init.setup_database(
            load_sample_data=config['load_sample_data']
        )

        if not success:
            logger.error(f"Database setup failed for {environment}")
            return False

        logger.info(f"✅ {environment.capitalize()} database setup completed")
        return True

    except Exception as e:
        logger.error(f"❌ Setup failed for {environment}: {e}")
        return False


# =============================================================================
# Example 4: Database Health Check
# =============================================================================

def perform_health_check():
    """
    Example: Verify database connectivity and basic functionality.

    Useful for:
    - Kubernetes liveness/readiness probes
    - Deployment verification
    - Monitoring scripts
    """
    logger.info("Performing database health check...")

    conn_config = PostgresConnectionConfig.from_env()

    db_config = DatabaseInitializerConfig(
        connection_config=conn_config,
        auto_create_db=False,  # Don't create, just check
        wait_timeout=10,
        retry_attempts=3
    )

    db_init = DatabaseInitializer(db_config)

    try:
        # Check if we can connect
        if not db_init._wait_for_database():
            logger.error("❌ Cannot connect to database")
            return False

        # Check if database exists
        if not db_init._database_exists():
            logger.error("❌ Database does not exist")
            return False

        # Initialize DatabaseManager to check table access
        DatabaseManager.initialize(conn_config)
        db_manager = DatabaseManager.get_instance()

        # Verify we can query tables
        with db_manager.session_scope() as session:
            from sqlalchemy import text

            # Check organizations table
            result = session.execute(text("SELECT COUNT(*) FROM organizations"))
            org_count = result.scalar()

            # Check users table
            result = session.execute(text("SELECT COUNT(*) FROM users"))
            user_count = result.scalar()

            logger.info(f"Database health check: {org_count} organizations, {user_count} users")

        logger.info("✅ Database health check passed")
        return True

    except Exception as e:
        logger.error(f"❌ Health check failed: {e}")
        return False


# =============================================================================
# Example 5: Blue-Green Deployment Database Prep
# =============================================================================

def prepare_blue_green_database(target_database: str):
    """
    Example: Prepare a new database for blue-green deployment.

    In blue-green deployments, you might want to:
    1. Create a new database
    2. Apply schema
    3. Optionally copy data from current database
    4. Verify setup
    5. Switch traffic (not shown here)

    Args:
        target_database: Name of the new database to create
    """
    logger.info(f"Preparing blue-green database: {target_database}...")

    # Get base configuration from environment
    base_config = PostgresConnectionConfig.from_env()

    # Create config for new database
    conn_config = PostgresConnectionConfig(
        host=base_config.host,
        port=base_config.port,
        database=target_database,  # New database name
        username=base_config.username,
        password=base_config.password,
        schema=base_config.schema
    )

    db_config = DatabaseInitializerConfig(
        connection_config=conn_config,
        auto_create_db=True,
        auto_drop_on_exit=False,
        wait_timeout=60,
        retry_attempts=10
    )

    db_init = DatabaseInitializer(db_config)

    try:
        # Setup new database
        success = db_init.setup_database(load_sample_data=False)

        if not success:
            logger.error("Failed to setup blue-green database")
            return False

        # Verify setup
        with db_init.session_scope() as session:
            from sqlalchemy import text
            result = session.execute(text("SELECT 1"))
            assert result.scalar() == 1

        logger.info(f"✅ Blue-green database {target_database} ready")
        logger.info("   Next steps:")
        logger.info("   1. Copy data from current database (if needed)")
        logger.info("   2. Run verification tests")
        logger.info("   3. Switch application to new database")
        logger.info("   4. Monitor for issues")

        return True

    except Exception as e:
        logger.error(f"❌ Blue-green database prep failed: {e}")
        return False


# =============================================================================
# Command Line Interface
# =============================================================================

def main():
    """
    CLI for production database operations.

    Usage:
        # Initial setup
        python examples/production_init_example.py init

        # Health check
        python examples/production_init_example.py health

        # Environment-specific setup
        python examples/production_init_example.py env staging

        # Blue-green prep
        python examples/production_init_example.py blue-green my_new_db
    """
    if len(sys.argv) < 2:
        print("Usage: python production_init_example.py <command> [args]")
        print("\nCommands:")
        print("  init                    - Initial production setup")
        print("  health                  - Database health check")
        print("  env <environment>       - Environment-specific setup")
        print("  blue-green <db_name>    - Prepare blue-green database")
        sys.exit(1)

    command = sys.argv[1]

    if command == 'init':
        success = initial_production_setup()
        sys.exit(0 if success else 1)

    elif command == 'health':
        success = perform_health_check()
        sys.exit(0 if success else 1)

    elif command == 'env':
        if len(sys.argv) < 3:
            print("Error: Environment required (development, staging, production)")
            sys.exit(1)
        environment = sys.argv[2]
        success = environment_specific_setup(environment)
        sys.exit(0 if success else 1)

    elif command == 'blue-green':
        if len(sys.argv) < 3:
            print("Error: Database name required")
            sys.exit(1)
        db_name = sys.argv[2]
        success = prepare_blue_green_database(db_name)
        sys.exit(0 if success else 1)

    else:
        print(f"Unknown command: {command}")
        sys.exit(1)


if __name__ == "__main__":
    main()
