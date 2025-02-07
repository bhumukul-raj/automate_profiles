#!/usr/bin/env python3

import unittest
import sys
import os
from pathlib import Path
import subprocess
import psutil
from unittest.mock import patch, MagicMock

# Add parent directory to path to import modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ollama_service_manager import (
    ResourceThresholds,
    SystemMonitor,
    OllamaProcess
)

class TestResourceThresholds(unittest.TestCase):
    """Test cases for ResourceThresholds class"""
    
    def setUp(self):
        """Set up test environment"""
        self.test_config = {
            'cpu_percent_warning': 90.0,
            'memory_percent_warning': 85.0,
            'gpu_memory_percent_warning': 85.0,
            'temperature_warning_celsius': 85.0,
            'battery_minimum_percent': 15.0
        }
        
        # Create test config file
        self.config_path = Path.home() / '.ollama' / 'resource_config.json'
        self.config_path.parent.mkdir(parents=True, exist_ok=True)
        
    def tearDown(self):
        """Clean up test environment"""
        if self.config_path.exists():
            self.config_path.unlink()
        try:
            self.config_path.parent.rmdir()
        except OSError:
            pass
    
    def test_default_thresholds(self):
        """Test default threshold values"""
        thresholds = ResourceThresholds()
        self.assertEqual(thresholds.cpu_percent_warning, 80.0)
        self.assertEqual(thresholds.memory_percent_warning, 80.0)
        self.assertEqual(thresholds.gpu_memory_percent_warning, 80.0)
        self.assertEqual(thresholds.temperature_warning_celsius, 80.0)
        self.assertEqual(thresholds.battery_minimum_percent, 20.0)
    
    @patch('builtins.open')
    def test_load_from_config(self, mock_open):
        """Test loading thresholds from config file"""
        mock_open.side_effect = FileNotFoundError
        thresholds = ResourceThresholds()
        self.assertEqual(thresholds.cpu_percent_warning, 80.0)  # Default value

class TestSystemMonitor(unittest.TestCase):
    """Test cases for SystemMonitor class"""
    
    def setUp(self):
        """Set up test environment"""
        self.monitor = SystemMonitor()
    
    @patch('pathlib.Path.glob')
    def test_get_cpu_temperature(self, mock_glob):
        """Test CPU temperature reading"""
        # Mock thermal zone file
        mock_thermal = MagicMock()
        mock_thermal.__truediv__.return_value = MagicMock()
        mock_glob.return_value = [mock_thermal]
        
        with patch('builtins.open', unittest.mock.mock_open(read_data='45000')):
            temp = self.monitor.get_cpu_temperature()
            self.assertEqual(temp, 45.0)
    
    @patch('subprocess.run')
    def test_get_gpu_temperature(self, mock_run):
        """Test GPU temperature reading"""
        # Mock nvidia-smi output
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout='55\n'
        )
        temp = self.monitor.get_gpu_temperature()
        self.assertEqual(temp, 55.0)
    
    @patch('psutil.sensors_battery')
    def test_get_battery_status(self, mock_battery):
        """Test battery status reading"""
        # Mock battery info
        mock_battery.return_value = MagicMock(
            percent=75.5,
            power_plugged=True,
            secsleft=3600
        )
        status = self.monitor.get_battery_status()
        self.assertEqual(status['percent'], 75.5)
        self.assertTrue(status['charging'])
        self.assertEqual(status['time_remaining'], 3600)

class TestOllamaProcess(unittest.TestCase):
    """Test cases for OllamaProcess class"""
    
    def setUp(self):
        """Set up test environment"""
        self.ollama = OllamaProcess()
    
    @patch('psutil.process_iter')
    def test_get_ollama_processes(self, mock_process_iter):
        """Test getting Ollama processes"""
        # Mock process list
        mock_process = MagicMock()
        mock_process.name.return_value = 'ollama'
        mock_process.cmdline.return_value = ['ollama', 'serve']
        mock_process_iter.return_value = [mock_process]
        
        processes = self.ollama.get_ollama_processes()
        self.assertEqual(len(processes), 1)
        self.assertEqual(processes[0].name(), 'ollama')
    
    def test_get_resource_usage(self):
        """Test resource usage monitoring"""
        with patch.object(self.ollama, 'get_ollama_processes') as mock_get_processes:
            # Mock process with resource usage
            mock_process = MagicMock()
            mock_process.cpu_percent.return_value = 25.0
            mock_process.memory_info.return_value = MagicMock(rss=1024*1024*100)  # 100MB
            mock_get_processes.return_value = [mock_process]
            
            usage = self.ollama.get_resource_usage()
            self.assertEqual(usage['cpu_percent'], 25.0)
            self.assertEqual(usage['memory_bytes'], 1024*1024*100)
    
    @patch('subprocess.run')
    def test_get_gpu_info(self, mock_run):
        """Test GPU information gathering"""
        # Mock nvidia-smi output
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout='GeForce RTX 3080,10240,2048,65,150.5'
        )
        
        gpu_info = self.ollama.get_gpu_info()
        self.assertTrue(gpu_info['available'])
        self.assertEqual(gpu_info['name'], 'GeForce RTX 3080')
        self.assertEqual(gpu_info['memory_total'], 10240)
        self.assertEqual(gpu_info['memory_used'], 2048)
        self.assertEqual(gpu_info['temperature'], 65.0)
        self.assertEqual(gpu_info['power_usage'], 150.5)
    
    def test_check_resource_warnings(self):
        """Test resource warning checks"""
        with patch.object(self.ollama.monitor, 'get_cpu_temperature') as mock_cpu_temp:
            mock_cpu_temp.return_value = 85.0
            warnings = self.ollama.check_resource_warnings()
            self.assertTrue(any('CPU temperature' in w for w in warnings))
    
    def test_should_stop_for_resources(self):
        """Test resource-based stop conditions"""
        with patch.object(self.ollama.monitor, 'get_battery_status') as mock_battery:
            # Test critical battery
            mock_battery.return_value = {
                'present': True,
                'percent': 15.0,
                'charging': False
            }
            should_stop, reason = self.ollama.should_stop_for_resources()
            self.assertTrue(should_stop)
            self.assertIn('Battery', reason)

if __name__ == '__main__':
    unittest.main() 