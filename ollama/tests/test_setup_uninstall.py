#!/usr/bin/env python3

import unittest
import sys
import os
from pathlib import Path
import subprocess
import shutil
from unittest.mock import patch, MagicMock, mock_open
import requests

# Add parent directory to path to import modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from setup_ollama import (
    check_disk_space,
    check_gpu_support,
    download_with_progress,
    get_installation_path,
    install_ollama,
    install_models,
    InstallationMode,
    get_installation_preferences,
    get_latest_version,
    get_current_version,
    main
)

from uninstall_ollama import (
    backup_ollama_models,
    cleanup_docker_images,
    check_ollama_files,
    remove_ollama_files,
    UninstallOptions
)

class TestSetupOllama(unittest.TestCase):
    """Test cases for setup_ollama.py functions"""
    
    def setUp(self):
        """Set up test environment"""
        self.test_dir = Path('test_workspace')
        self.test_dir.mkdir(exist_ok=True)
        
        # Create a mock config for testing
        self.config_dir = self.test_dir / '.ollama'
        self.config_dir.mkdir(exist_ok=True)
    
    def tearDown(self):
        """Clean up test environment"""
        if self.test_dir.exists():
            shutil.rmtree(self.test_dir)
    
    @patch('psutil.disk_usage')
    def test_check_disk_space(self, mock_disk_usage):
        """Test disk space checking"""
        # Test sufficient space
        mock_disk_usage.return_value = MagicMock(
            free=20 * 1024 * 1024 * 1024  # 20GB
        )
        self.assertTrue(check_disk_space(required_gb=10))
        
        # Test insufficient space
        mock_disk_usage.return_value = MagicMock(
            free=5 * 1024 * 1024 * 1024  # 5GB
        )
        self.assertFalse(check_disk_space(required_gb=10))
        
        # Test edge case with exactly required space
        mock_disk_usage.return_value = MagicMock(
            free=10 * 1024 * 1024 * 1024  # 10GB
        )
        self.assertTrue(check_disk_space(required_gb=10))
        
        # Test with disk access error
        mock_disk_usage.side_effect = Exception("Disk access error")
        self.assertFalse(check_disk_space(required_gb=10))
    
    @patch('subprocess.run')
    def test_check_gpu_support(self, mock_run):
        """Test GPU support detection"""
        # Test NVIDIA GPU detection
        mock_nvidia = MagicMock()
        mock_nvidia.returncode = 0
        mock_nvidia.stdout = "NVIDIA-SMI 470.182.03   Driver Version: 470.182.03   CUDA Version: 11.4"
        mock_run.return_value = mock_nvidia
        
        has_gpu, info = check_gpu_support()
        self.assertTrue(has_gpu)
        self.assertIn('NVIDIA', info)
        
        # Test AMD GPU detection
        def mock_run_side_effect(*args, **kwargs):
            if 'nvidia-smi' in args[0]:
                mock_fail = MagicMock()
                mock_fail.returncode = 1
                return mock_fail
            if 'rocm-smi' in args[0]:
                mock_amd = MagicMock()
                mock_amd.returncode = 0
                mock_amd.stdout = "ROCm System Management Interface"
                return mock_amd
            mock_fail = MagicMock()
            mock_fail.returncode = 1
            return mock_fail
            
        mock_run.side_effect = mock_run_side_effect
        has_gpu, info = check_gpu_support()
        self.assertTrue(has_gpu)
        self.assertIn('AMD', info)
        
        # Test no GPU
        mock_run.side_effect = lambda *args, **kwargs: MagicMock(returncode=1, stdout="")
        has_gpu, info = check_gpu_support()
        self.assertFalse(has_gpu)
        self.assertIn('CPU', info)
        
        # Test with unexpected error
        mock_run.side_effect = Exception("Unexpected error")
        has_gpu, info = check_gpu_support()
        self.assertFalse(has_gpu)
        self.assertIn('CPU', info)
    
    @patch('requests.get')
    def test_download_with_progress(self, mock_get):
        """Test file download with progress"""
        # Test successful download
        mock_response = MagicMock()
        mock_response.headers = {'content-length': '1024'}
        mock_response.iter_content.return_value = [b'data'] * 10
        mock_get.return_value = mock_response
        
        result = download_with_progress('http://test.url', self.test_dir / 'test.file')
        self.assertTrue(result)
        
        # Test download with no content length
        mock_response.headers = {}
        result = download_with_progress('http://test.url', self.test_dir / 'test.file')
        self.assertTrue(result)
        
        # Test download failure
        mock_get.side_effect = requests.exceptions.RequestException("Download failed")
        result = download_with_progress('http://test.url', self.test_dir / 'test.file')
        self.assertFalse(result)
    
    def test_get_installation_path(self):
        """Test installation path generation"""
        install_path = get_installation_path()
        self.assertTrue(install_path.is_absolute())
        self.assertIn('ollama', str(install_path))
        self.assertTrue(install_path.parent.exists())
    
    @patch('subprocess.run')
    def test_install_ollama(self, mock_run):
        """Test Ollama installation"""
        # Test successful installation
        mock_run.return_value = MagicMock(returncode=0, stdout="Installation successful")
        
        # Create a mock environment
        env = os.environ.copy()
        env['OLLAMA_INSTALL_PATH'] = str(self.test_dir)
        
        with patch.dict(os.environ, env):
            self.assertTrue(install_ollama(self.test_dir))
            mock_run.assert_called()
            # Check if environment was passed correctly
            last_call = mock_run.call_args_list[-1]
            self.assertIn('env', last_call[1])
            self.assertEqual(last_call[1]['env'].get('OLLAMA_INSTALL_PATH'), str(self.test_dir))
        
        # Test failed installation
        mock_run.return_value = MagicMock(returncode=1)
        self.assertFalse(install_ollama(self.test_dir))
        
        # Test installation script download failure
        mock_run.side_effect = subprocess.CalledProcessError(1, 'curl')
        self.assertFalse(install_ollama(self.test_dir))
    
    @patch('subprocess.run')
    def test_install_models(self, mock_run):
        """Test model installation"""
        logger = MagicMock()
        
        # Test successful model installation
        mock_run.return_value = MagicMock(returncode=0)
        self.assertTrue(install_models(['llama2', 'mistral'], logger))
        self.assertEqual(mock_run.call_count, 2)  # One call per model
        
        # Test failed model installation
        mock_run.reset_mock()
        mock_run.return_value = MagicMock(returncode=1)
        self.assertFalse(install_models(['invalid-model'], logger))
        logger.error.assert_called_once()
        
        # Test empty model list
        mock_run.reset_mock()
        logger.reset_mock()
        self.assertTrue(install_models([], logger))
        mock_run.assert_not_called()
    
    def test_installation_mode_class(self):
        """Test InstallationMode class"""
        mode = InstallationMode()
        
        # Test default values
        self.assertFalse(mode.minimal)
        self.assertIsNone(mode.custom_path)
        self.assertTrue(mode.gpu_enabled)
        self.assertTrue(mode.auto_start)
        self.assertEqual(mode.models, [])
        
        # Test setting values
        mode.minimal = True
        mode.custom_path = Path('/custom/path')
        mode.gpu_enabled = False
        mode.auto_start = False
        mode.models = ['llama2']
        
        self.assertTrue(mode.minimal)
        self.assertEqual(mode.custom_path, Path('/custom/path'))
        self.assertFalse(mode.gpu_enabled)
        self.assertFalse(mode.auto_start)
        self.assertEqual(mode.models, ['llama2'])
    
    @patch('builtins.input')
    def test_get_installation_preferences(self, mock_input):
        """Test installation preferences collection"""
        # Test full installation
        mock_input.return_value = '1'
        prefs = get_installation_preferences()
        self.assertFalse(prefs.minimal)
        self.assertIsNone(prefs.custom_path)
        self.assertTrue(prefs.gpu_enabled)
        
        # Test minimal installation
        mock_input.return_value = '2'
        prefs = get_installation_preferences()
        self.assertTrue(prefs.minimal)
        
        # Test custom installation
        mock_input.side_effect = ['3', '/custom/path', 'y', 'y', '1,2']
        prefs = get_installation_preferences()
        self.assertFalse(prefs.minimal)
        self.assertEqual(prefs.custom_path, Path('/custom/path'))
        self.assertTrue(prefs.gpu_enabled)
        self.assertTrue(prefs.auto_start)
        self.assertEqual(prefs.models, ['llama2', 'mistral'])
    
    @patch('requests.get')
    def test_get_latest_version(self, mock_get):
        """Test getting latest version from GitHub"""
        # Test successful version fetch
        mock_response = MagicMock()
        mock_response.json.return_value = {'tag_name': 'v1.0.0'}
        mock_get.return_value = mock_response
        
        version = get_latest_version()
        self.assertEqual(version, 'v1.0.0')
        
        # Test failed version fetch
        mock_get.side_effect = requests.exceptions.RequestException()
        version = get_latest_version()
        self.assertIsNone(version)
    
    @patch('subprocess.run')
    def test_get_current_version(self, mock_run):
        """Test getting current Ollama version"""
        # Test successful version check
        mock_run.return_value = MagicMock(returncode=0, stdout='v1.0.0\n')
        version = get_current_version()
        self.assertEqual(version, 'v1.0.0')
        
        # Test failed version check
        mock_run.side_effect = subprocess.CalledProcessError(1, 'ollama')
        version = get_current_version()
        self.assertIsNone(version)
    
    @patch('setup_ollama.get_installation_preferences')
    @patch('setup_ollama.check_and_install_packages')
    @patch('setup_ollama.check_disk_space')
    @patch('setup_ollama.check_gpu_support')
    @patch('setup_ollama.install_ollama')
    @patch('setup_ollama.install_models')
    @patch('subprocess.Popen')
    def test_main_function(self, mock_popen, mock_install_models, mock_install_ollama,
                          mock_gpu_support, mock_disk_space, mock_check_packages,
                          mock_get_prefs):
        """Test main installation function"""
        # Mock installation preferences
        prefs = InstallationMode()
        prefs.models = ['llama2']
        mock_get_prefs.return_value = prefs
        
        # Mock successful installation
        mock_disk_space.return_value = True
        mock_gpu_support.return_value = (True, 'GPU available')
        mock_install_ollama.return_value = True
        mock_install_models.return_value = True
        
        # Test successful installation
        main()
        mock_install_ollama.assert_called_once()
        mock_install_models.assert_called_once()
        mock_popen.assert_called_once()
        
        # Test disk space check failure
        mock_disk_space.return_value = False
        with self.assertRaises(SystemExit):
            main()
        
        # Test Ollama installation failure
        mock_disk_space.return_value = True
        mock_install_ollama.return_value = False
        with self.assertRaises(SystemExit):
            main()

class TestUninstallOllama(unittest.TestCase):
    """Test cases for uninstall_ollama.py functions"""
    
    def setUp(self):
        """Set up test environment"""
        self.test_dir = Path('test_workspace')
        self.test_dir.mkdir(exist_ok=True)
        self.models_dir = self.test_dir / '.ollama' / 'models'
        self.models_dir.mkdir(parents=True)
        
        # Create dummy model files
        (self.models_dir / 'model1').touch()
        (self.models_dir / 'model2').touch()
    
    def tearDown(self):
        """Clean up test environment"""
        if self.test_dir.exists():
            shutil.rmtree(self.test_dir)
    
    def test_backup_ollama_models(self):
        """Test model backup creation"""
        with patch('tarfile.open') as mock_tar:
            result = backup_ollama_models(compression_level=6)
            self.assertIsNotNone(result)
            mock_tar.assert_called_once()
    
    @patch('subprocess.run')
    def test_cleanup_docker_images(self, mock_run):
        """Test Docker image cleanup"""
        # Mock Docker image list
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout='ollama/image1\nollama/image2\n'
        )
        cleanup_docker_images()
        self.assertEqual(mock_run.call_count, 3)  # list + 2 removals
    
    def test_check_ollama_files(self):
        """Test Ollama file detection"""
        files = check_ollama_files()
        self.assertIsInstance(files, dict)
        self.assertTrue(all(isinstance(v, list) for v in files.values()))
    
    def test_remove_ollama_files(self):
        """Test Ollama file removal"""
        options = UninstallOptions()
        options.remove_models = True
        options.remove_config = True
        
        found_files = {
            'models': [self.models_dir],
            'config': [self.test_dir / '.ollama' / 'config']
        }
        
        remove_ollama_files(found_files, options)
        self.assertFalse(self.models_dir.exists())

if __name__ == '__main__':
    unittest.main() 