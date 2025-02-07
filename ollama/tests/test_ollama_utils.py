#!/usr/bin/env python3

import unittest
import sys
import os
from pathlib import Path
import subprocess
import shutil
from unittest.mock import patch, MagicMock

# Add parent directory to path to import modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ollama_utils import (
    is_debian_based,
    install_system_package,
    ensure_pip_installed,
    check_and_install_packages,
    setup_logging,
    check_ollama_installed,
    check_ollama_running,
    stop_ollama_service
)

class TestOllamaUtils(unittest.TestCase):
    """Test cases for ollama_utils.py functions"""
    
    def setUp(self):
        """Set up test environment"""
        self.test_dir = Path('test_workspace')
        self.test_dir.mkdir(exist_ok=True)
    
    def tearDown(self):
        """Clean up test environment"""
        if self.test_dir.exists():
            shutil.rmtree(self.test_dir)
    
    def test_is_debian_based(self):
        """Test is_debian_based function"""
        with patch('os.path.exists') as mock_exists:
            # Test Debian-based system
            mock_exists.return_value = True
            self.assertTrue(is_debian_based())
            
            # Test non-Debian system
            mock_exists.return_value = False
            self.assertFalse(is_debian_based())
    
    @patch('subprocess.run')
    def test_install_system_package(self, mock_run):
        """Test install_system_package function"""
        # Test successful installation
        mock_run.return_value = MagicMock(returncode=0)
        self.assertTrue(install_system_package('test-package'))
        
        # Test failed installation
        mock_run.side_effect = subprocess.CalledProcessError(1, 'apt-get')
        self.assertFalse(install_system_package('test-package'))
    
    @patch('ollama_utils.install_system_package')
    @patch('subprocess.run')
    def test_ensure_pip_installed(self, mock_run, mock_install):
        """Test ensure_pip_installed function"""
        with patch.dict('sys.modules', {'pip': None}):
            # Test non-Debian system with failed pip installation
            mock_install.return_value = False
            mock_run.side_effect = Exception("Failed to install pip")
            with self.assertRaises(SystemExit):
                ensure_pip_installed()
            
            # Test successful installation on Debian system
            mock_install.return_value = True
            self.assertTrue(ensure_pip_installed())
    
    def test_setup_logging(self):
        """Test setup_logging function"""
        logger = setup_logging('test_logger')
        self.assertIsNotNone(logger)
        self.assertEqual(logger.name, 'test_logger')
    
    @patch('shutil.which')
    def test_check_ollama_installed(self, mock_which):
        """Test check_ollama_installed function"""
        # Test Ollama installed
        mock_which.return_value = '/usr/local/bin/ollama'
        self.assertTrue(check_ollama_installed())
        
        # Test Ollama not installed
        mock_which.return_value = None
        self.assertFalse(check_ollama_installed())
    
    @patch('subprocess.run')
    def test_check_ollama_running(self, mock_run):
        """Test check_ollama_running function"""
        # Test Ollama running
        mock_run.return_value = MagicMock(returncode=0)
        self.assertTrue(check_ollama_running())
        
        # Test Ollama not running
        mock_run.return_value = MagicMock(returncode=1)
        self.assertFalse(check_ollama_running())
    
    @patch('subprocess.run')
    def test_stop_ollama_service(self, mock_run):
        """Test stop_ollama_service function"""
        # Test successful stop
        mock_run.return_value = MagicMock(returncode=0)
        self.assertTrue(stop_ollama_service())
        
        # Test failed stop
        mock_run.side_effect = Exception('Failed to stop service')
        self.assertFalse(stop_ollama_service())

if __name__ == '__main__':
    unittest.main() 