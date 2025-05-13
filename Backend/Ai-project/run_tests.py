#!/usr/bin/env python
"""
Test runner script for MockMate project.
Run this script to execute all tests or specific test modules.
"""

import os
import sys
import django
from django.conf import settings
from django.test.utils import get_runner
import argparse

if __name__ == "__main__":
    # Set up command line arguments
    parser = argparse.ArgumentParser(description='Run tests for MockMate project')
    parser.add_argument('--module', '-m', help='Specific test module to run (e.g., tests.test_models)')
    parser.add_argument('--test', '-t', help='Specific test to run (e.g., tests.test_models.CustomUserModelTest)')
    parser.add_argument('--method', '-tm', help='Specific test method to run (e.g., tests.test_models.CustomUserModelTest.test_user_creation)')
    parser.add_argument('--verbose', '-v', action='store_true', help='Verbose output')
    args = parser.parse_args()

    # Setup Django environment
    os.environ['DJANGO_SETTINGS_MODULE'] = 'mockmate.settings'
    django.setup()
    
    # Get the test runner
    TestRunner = get_runner(settings)
    test_runner = TestRunner(verbosity=2 if args.verbose else 1)
    
    # Determine what to test
    if args.method:
        test_suite = args.method
    elif args.test:
        test_suite = args.test
    elif args.module:
        test_suite = args.module
    else:
        test_suite = 'AiQuetionare.tests'
    
    print(f"Running: {test_suite}")
    failures = test_runner.run_tests([test_suite])
    
    sys.exit(bool(failures))
