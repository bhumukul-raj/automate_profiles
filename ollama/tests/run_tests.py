#!/usr/bin/env python3

"""
Ollama Test Runner
=================

This script runs all test files and generates a coverage report.
It will also check for any potential issues in the test files.

Usage:
    python3 run_tests.py [--coverage] [--verbose]
"""

import unittest
import sys
import os
from pathlib import Path
import argparse

try:
    import coverage
except ImportError:
    print("Coverage package not found. Installing...")
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "coverage"])
    import coverage

def run_tests(verbose=False, with_coverage=False):
    """Run all test files and optionally generate coverage report."""
    # Add parent directory to path for imports
    parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    sys.path.append(parent_dir)
    
    if with_coverage:
        # Start coverage measurement
        cov = coverage.Coverage(
            branch=True,
            source=[parent_dir],
            include=[
                os.path.join(parent_dir, "*.py"),
                os.path.join(parent_dir, "*", "*.py")
            ],
            omit=[
                os.path.join(parent_dir, "tests", "*.py"),
                os.path.join(parent_dir, "*", "__pycache__", "*.py"),
                os.path.join(parent_dir, "venv", "*")
            ]
        )
        cov.start()
    
    # Discover and run tests
    loader = unittest.TestLoader()
    start_dir = os.path.dirname(os.path.abspath(__file__))
    suite = loader.discover(start_dir, pattern='test_*.py')
    
    runner = unittest.TextTestRunner(verbosity=2 if verbose else 1)
    result = runner.run(suite)
    
    if with_coverage:
        # Stop coverage measurement and generate report
        cov.stop()
        cov.save()
        
        print("\nCoverage Report:")
        print("================")
        
        # Generate console report
        cov.report()
        
        # Generate HTML report
        html_dir = Path(start_dir) / 'coverage_report'
        html_dir.mkdir(exist_ok=True)
        cov.html_report(directory=str(html_dir))
        print(f"\nDetailed HTML coverage report generated in: {html_dir}")
    
    return result.wasSuccessful()

def main():
    parser = argparse.ArgumentParser(description='Run Ollama tests')
    parser.add_argument('--coverage', action='store_true',
                       help='Generate coverage report')
    parser.add_argument('--verbose', action='store_true',
                       help='Show verbose output')
    
    args = parser.parse_args()
    
    print("Running Ollama Tests")
    print("===================")
    
    success = run_tests(verbose=args.verbose, with_coverage=args.coverage)
    
    if not success:
        print("\nSome tests failed!")
        sys.exit(1)
    else:
        print("\nAll tests passed!")

if __name__ == '__main__':
    main() 