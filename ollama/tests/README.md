# Ollama Test Suite

This directory contains the test suite for the Ollama project. The tests are designed to verify the functionality of all major components while ensuring no production code is affected during testing.

## 📋 Table of Contents

- [Overview](#overview)
- [Test Structure](#test-structure)
- [Installation](#installation)
- [Running Tests](#running-tests)
- [Coverage Reports](#coverage-reports)
- [Writing New Tests](#writing-new-tests)
- [Best Practices](#best-practices)
- [Troubleshooting](#troubleshooting)

## 🔍 Overview

The test suite includes:
- Unit tests for all major components
- Mock objects for system calls
- Test isolation
- Coverage reporting
- Automated test discovery

## 📁 Test Structure

```
tests/
├── README.md                 # This file
├── requirements-test.txt     # Test dependencies
├── run_tests.py             # Test runner script
├── test_ollama_utils.py     # Tests for utility functions
├── test_ollama_service_manager.py  # Tests for service management
└── test_setup_uninstall.py  # Tests for setup/uninstall scripts
```

## 📥 Installation

1. Install test dependencies:
   ```bash
   pip install -r requirements-test.txt
   ```

2. Verify installation:
   ```bash
   python3 -c "import pytest, coverage, psutil"
   ```

## 🚀 Running Tests

### Basic Usage

Run all tests:
```bash
./run_tests.py
```

### Advanced Options

1. Run with coverage report:
   ```bash
   ./run_tests.py --coverage
   ```

2. Run with verbose output:
   ```bash
   ./run_tests.py --verbose
   ```

3. Run both coverage and verbose:
   ```bash
   ./run_tests.py --coverage --verbose
   ```

4. Run individual test files:
   ```bash
   python3 test_ollama_utils.py
   python3 test_ollama_service_manager.py
   python3 test_setup_uninstall.py
   ```

## 📊 Coverage Reports

Coverage reports are generated in two formats:
1. Console output (when using --coverage)
2. HTML report in `coverage_report/` directory

To view the HTML report:
```bash
# After running tests with --coverage
firefox coverage_report/index.html  # or any other browser
```

## ✍️ Writing New Tests

### Test File Structure
```python
#!/usr/bin/env python3

import unittest
import sys
import os
from pathlib import Path
from unittest.mock import patch, MagicMock

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class TestNewComponent(unittest.TestCase):
    def setUp(self):
        """Set up test environment"""
        pass
    
    def tearDown(self):
        """Clean up after tests"""
        pass
    
    def test_some_function(self):
        """Test description"""
        # Test implementation
        pass

if __name__ == '__main__':
    unittest.main()
```

### Guidelines for New Tests

1. Test Isolation
   - Use setUp/tearDown for test environment
   - Clean up all temporary files
   - Don't modify production code

2. Mock External Dependencies
   ```python
   @patch('subprocess.run')
   def test_external_call(self, mock_run):
       mock_run.return_value = MagicMock(returncode=0)
       # Test implementation
   ```

3. Test Both Success and Failure
   ```python
   def test_function(self):
       # Test successful case
       self.assertTrue(function(valid_input))
       
       # Test failure case
       self.assertFalse(function(invalid_input))
   ```

## ✅ Best Practices

1. Test Naming
   - Use descriptive names: `test_function_success`, `test_function_failure`
   - Group related tests in classes
   - Add docstrings to test methods

2. Mocking
   - Mock all external system calls
   - Use appropriate mock return values
   - Test both success and failure paths

3. Assertions
   - Use specific assertions: `assertEqual`, `assertTrue`, etc.
   - Include meaningful error messages
   - Test edge cases

4. Test Independence
   - Each test should run independently
   - Clean up after each test
   - Don't rely on test execution order

## 🔧 Troubleshooting

### Common Issues

1. Import Errors
   ```bash
   # Check PYTHONPATH
   export PYTHONPATH="${PYTHONPATH}:/path/to/ollama"
   ```

2. Permission Errors
   ```bash
   # Make test files executable
   chmod +x *.py
   ```

3. Missing Dependencies
   ```bash
   # Reinstall dependencies
   pip install -r requirements-test.txt
   ```

### Debug Tips

1. Use verbose output:
   ```bash
   ./run_tests.py --verbose
   ```

2. Run specific test case:
   ```bash
   python3 -m unittest test_file.TestClass.test_method -v
   ```

3. Debug with print statements:
   ```python
   def test_function(self):
       print("Debug:", variable)  # Will show in verbose mode
   ```

## 🤝 Contributing

When adding new tests:
1. Follow the existing test structure
2. Add appropriate mocks for external calls
3. Update this README if needed
4. Ensure all tests pass before committing
5. Add test coverage for new features

## 📝 Maintenance

Regular maintenance tasks:
1. Update test dependencies
2. Check for deprecated test methods
3. Verify test coverage
4. Clean up old test files
5. Update mocks for system changes

## 🔒 Security

- Never commit sensitive data in tests
- Use dummy values for credentials
- Mock all external API calls
- Clean up test artifacts

## 📞 Support

If you encounter issues:
1. Check the troubleshooting section
2. Review test logs
3. Create an issue with test output
4. Include system information 