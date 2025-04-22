#!/usr/bin/env python3
"""
Utility script to validate migration progress and run comparison tests.
Provides command-line interface for developers to check migration status.
"""

import asyncio
import argparse
import logging
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List
from .validation_tests import MigrationValidator
from .health_monitor import HealthMonitor
from ..config.environments import Environments
from ..config.database import DatabaseManager

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MigrationValidator:
    """Runs validation tests and generates reports."""
    
    def __init__(self, environment: str = "test"):
        self.environment = environment
        self.validator = None
        self.health_monitor = None
        self.results: Dict[str, Any] = {}
    
    async def setup(self):
        """Initialize validator and monitoring."""
        # Set up database connection
        config = Environments.get_config(self.environment)
        DatabaseManager.initialize(config.conn_config, config.pool_config)
        
        # Initialize components
        self.validator = MigrationValidator()
        self.health_monitor = HealthMonitor()
    
    async def run_validation(self, tests: List[str]) -> Dict[str, Any]:
        """Run specified validation tests."""
        self.results = {
            "timestamp": datetime.now(),
            "environment": self.environment,
            "tests": {},
            "health_check": {},
            "summary": {
                "total_tests": 0,
                "passed_tests": 0,
                "failed_tests": 0
            }
        }
        
        try:
            # Run selected tests
            if "all" in tests or "operations" in tests:
                self.results["tests"]["operations"] = await self._run_operation_tests()
            
            if "all" in tests or "performance" in tests:
                self.results["tests"]["performance"] = await self._run_performance_tests()
            
            if "all" in tests or "errors" in tests:
                self.results["tests"]["error_handling"] = await self._run_error_tests()
            
            # Run health check
            self.results["health_check"] = await self._run_health_check()
            
            # Calculate summary
            for category, result in self.results["tests"].items():
                self.results["summary"]["total_tests"] += len(result)
                self.results["summary"]["passed_tests"] += sum(1 for r in result.values() if r["passed"])
                self.results["summary"]["failed_tests"] += sum(1 for r in result.values() if not r["passed"])
            
            return self.results
            
        except Exception as e:
            logger.error(f"Validation failed: {str(e)}")
            self.results["error"] = str(e)
            return self.results
    
    async def _run_operation_tests(self) -> Dict[str, Any]:
        """Run basic operation comparison tests."""
        results = {}
        try:
            # Run document operations test
            results["document_operations"] = {
                "passed": False,
                "details": {}
            }
            
            operation_results = await self.validator.compare_document_operations()
            results["document_operations"]["passed"] = all(operation_results.values())
            results["document_operations"]["details"] = operation_results
            
        except Exception as e:
            logger.error(f"Operation tests failed: {str(e)}")
            results["error"] = str(e)
        
        return results
    
    async def _run_performance_tests(self) -> Dict[str, Any]:
        """Run performance comparison tests."""
        results = {}
        try:
            # Test basic operations performance
            results["basic_operations"] = {
                "passed": False,
                "details": {}
            }
            
            # Run performance test multiple times for accuracy
            perf_results = []
            for _ in range(5):
                perf_result = await self.validator.test_performance_comparison()
                perf_results.append(perf_result)
            
            # Calculate average performance
            avg_performance = sum(r["duration_ratio"] for r in perf_results) / len(perf_results)
            results["basic_operations"]["passed"] = avg_performance <= 1.2  # Within 20% of TypeScript
            results["basic_operations"]["details"] = {
                "average_ratio": avg_performance,
                "individual_tests": perf_results
            }
            
        except Exception as e:
            logger.error(f"Performance tests failed: {str(e)}")
            results["error"] = str(e)
        
        return results
    
    async def _run_error_tests(self) -> Dict[str, Any]:
        """Run error handling comparison tests."""
        results = {}
        try:
            # Test error handling scenarios
            results["error_handling"] = {
                "passed": False,
                "details": {}
            }
            
            error_results = await self.validator.test_error_handling()
            results["error_handling"]["passed"] = error_results["matching_behavior"]
            results["error_handling"]["details"] = error_results
            
        except Exception as e:
            logger.error(f"Error handling tests failed: {str(e)}")
            results["error"] = str(e)
        
        return results
    
    async def _run_health_check(self) -> Dict[str, Any]:
        """Run health check using monitor."""
        try:
            metrics = await self.health_monitor._collect_metrics()
            issues = self.health_monitor._check_health(metrics)
            
            return {
                "metrics": metrics,
                "issues": issues,
                "healthy": len(issues) == 0
            }
            
        except Exception as e:
            logger.error(f"Health check failed: {str(e)}")
            return {
                "error": str(e),
                "healthy": False
            }
    
    def save_results(self, output_dir: str = "migration_logs"):
        """Save validation results to file."""
        try:
            # Create output directory
            output_path = Path(output_dir)
            output_path.mkdir(exist_ok=True)
            
            # Generate filename with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"validation_results_{timestamp}.json"
            
            # Save results
            with (output_path / filename).open("w") as f:
                json.dump(self.results, f, default=str, indent=2)
            
            logger.info(f"Results saved to {output_path / filename}")
            
        except Exception as e:
            logger.error(f"Failed to save results: {str(e)}")

def main():
    parser = argparse.ArgumentParser(description="Run migration validation tests")
    parser.add_argument(
        "--tests",
        choices=["all", "operations", "performance", "errors"],
        default="all",
        help="Specify which tests to run"
    )
    parser.add_argument(
        "--environment",
        choices=["development", "test", "production"],
        default="test",
        help="Specify the environment for validation"
    )
    parser.add_argument(
        "--output-dir",
        default="migration_logs",
        help="Directory for validation results"
    )
    
    args = parser.parse_args()
    
    async def run():
        validator = MigrationValidator(args.environment)
        await validator.setup()
        
        logger.info(f"Running validation tests: {args.tests}")
        results = await validator.run_validation([args.tests])
        
        validator.save_results(args.output_dir)
        
        # Print summary
        print("\nValidation Summary:")
        print(f"Total Tests: {results['summary']['total_tests']}")
        print(f"Passed: {results['summary']['passed_tests']}")
        print(f"Failed: {results['summary']['failed_tests']}")
        print(f"\nDetails saved to: {args.output_dir}")
        
        # Exit with appropriate status
        return results['summary']['failed_tests'] == 0

    success = asyncio.run(run())
    exit(0 if success else 1)

if __name__ == "__main__":
    main()
