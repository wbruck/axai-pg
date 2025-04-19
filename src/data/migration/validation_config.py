"""Configuration settings for migration validation tests."""

from typing import Dict, Any
from dataclasses import dataclass

@dataclass
class ValidationThresholds:
    """Thresholds for validation tests."""
    performance_ratio_limit: float = 1.2  # Python must be within 120% of TypeScript time
    error_rate_limit: float = 0.01  # Maximum 1% error rate
    response_time_ms_limit: int = 1000  # Maximum 1 second response time
    connection_error_limit: int = 3  # Maximum connection errors in test period
    pool_usage_limit: float = 0.8  # Maximum 80% pool utilization

@dataclass
class TestConfiguration:
    """Configuration for validation test runs."""
    batch_size: int = 100  # Number of records per test batch
    test_iterations: int = 5  # Number of times to repeat each test
    timeout_seconds: int = 30  # Test timeout duration
    parallel_tests: int = 3  # Number of parallel test operations

@dataclass
class ValidationConfig:
    """Complete validation configuration."""
    thresholds: ValidationThresholds = ValidationThresholds()
    test_config: TestConfiguration = TestConfiguration()
    
    def get_test_parameters(self) -> Dict[str, Any]:
        """Get test parameters as dictionary."""
        return {
            "performance": {
                "ratio_limit": self.thresholds.performance_ratio_limit,
                "batch_size": self.test_config.batch_size,
                "iterations": self.test_config.test_iterations
            },
            "errors": {
                "rate_limit": self.thresholds.error_rate_limit,
                "connection_limit": self.thresholds.connection_error_limit
            },
            "responsiveness": {
                "time_limit_ms": self.thresholds.response_time_ms_limit,
                "timeout": self.test_config.timeout_seconds
            },
            "connections": {
                "pool_usage_limit": self.thresholds.pool_usage_limit,
                "parallel_operations": self.test_config.parallel_tests
            }
        }

# Default configurations for different environments
VALIDATION_CONFIGS = {
    "development": ValidationConfig(
        thresholds=ValidationThresholds(
            performance_ratio_limit=1.5,  # More lenient in development
            error_rate_limit=0.05,
            response_time_ms_limit=2000,
            connection_error_limit=5,
            pool_usage_limit=0.9
        ),
        test_config=TestConfiguration(
            batch_size=50,
            test_iterations=3,
            timeout_seconds=60,
            parallel_tests=2
        )
    ),
    
    "test": ValidationConfig(
        thresholds=ValidationThresholds(
            performance_ratio_limit=1.3,
            error_rate_limit=0.02,
            response_time_ms_limit=1500,
            connection_error_limit=3,
            pool_usage_limit=0.8
        ),
        test_config=TestConfiguration(
            batch_size=100,
            test_iterations=5,
            timeout_seconds=45,
            parallel_tests=3
        )
    ),
    
    "production": ValidationConfig(
        thresholds=ValidationThresholds(
            performance_ratio_limit=1.2,
            error_rate_limit=0.01,
            response_time_ms_limit=1000,
            connection_error_limit=2,
            pool_usage_limit=0.7
        ),
        test_config=TestConfiguration(
            batch_size=200,
            test_iterations=10,
            timeout_seconds=30,
            parallel_tests=5
        )
    )
}

def get_validation_config(environment: str = "test") -> ValidationConfig:
    """Get validation configuration for specified environment."""
    return VALIDATION_CONFIGS.get(environment.lower(), VALIDATION_CONFIGS["test"])
