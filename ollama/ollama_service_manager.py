#!/usr/bin/env python3

"""
Ollama Service Manager
=====================

A utility script to manage Ollama services and processes.
Use this to start/stop Ollama services and monitor resource usage.

Features:
    - Service management (start/stop/status)
    - Resource monitoring and alerts
    - Temperature monitoring
    - Battery-aware management
    - GPU monitoring and management
    - Automatic resource optimization
    - Process priority management
    - Network usage monitoring

Usage:
    python3 ollama_service_manager.py start [--priority {low|normal|high}]
    python3 ollama_service_manager.py stop
    python3 ollama_service_manager.py status [--json]
    python3 ollama_service_manager.py monitor [--interval SECONDS] [--log-file PATH]
"""

import os
import sys
import subprocess
import psutil
import time
from pathlib import Path
import argparse
from typing import List, Dict, Optional, Tuple, Union
import json
import warnings
import shutil
import pwd
import logging
import signal
from datetime import datetime

# Import shared utilities
from ollama_utils import setup_logging, get_real_user, get_real_home

# Setup logging with rotation
logger = setup_logging('ollama_service')

class ResourceThresholds:
    """Resource threshold configuration with dynamic adjustment."""
    def __init__(self):
        self.cpu_percent_warning = 80.0
        self.memory_percent_warning = 80.0
        self.gpu_memory_percent_warning = 80.0
        self.temperature_warning_celsius = 80.0
        self.battery_minimum_percent = 20.0
        self.network_warning_mbps = 100.0
        self.disk_usage_warning = 90.0
        self.load_from_config()
        
    def load_from_config(self):
        """Load thresholds from config file if exists."""
        config_path = Path(get_real_home()) / '.ollama' / 'resource_config.json'
        if config_path.exists():
            try:
                with open(config_path) as f:
                    config = json.load(f)
                    self.__dict__.update(config)
                logger.info("Loaded custom resource thresholds from config")
            except Exception as e:
                logger.warning(f"Error loading config: {e}")
    
    def adjust_thresholds(self, system_info: Dict):
        """Dynamically adjust thresholds based on system capabilities."""
        if system_info.get('is_laptop', False):
            # More conservative thresholds for laptops
            self.cpu_percent_warning = min(self.cpu_percent_warning, 70.0)
            self.temperature_warning_celsius = min(self.temperature_warning_celsius, 75.0)
        
        if system_info.get('total_memory_gb', 0) < 8:
            # More conservative memory threshold for low-memory systems
            self.memory_percent_warning = min(self.memory_percent_warning, 70.0)

class SystemMonitor:
    """Enhanced system resource monitoring with performance optimizations."""
    
    def __init__(self):
        self.thresholds = ResourceThresholds()
        self._temp_cache = {}
        self._cache_timeout = 5
        self._last_checks = {}
        self._check_intervals = {
            'cpu_temp': 5,
            'gpu_temp': 5,
            'battery': 30,
            'resources': 5,
            'network': 10,
            'disk': 60
        }
        self._system_info = self._get_system_info()
        self.thresholds.adjust_thresholds(self._system_info)
    
    def _get_system_info(self) -> Dict:
        """Get detailed system information."""
        info = {
            'is_laptop': self._is_laptop(),
            'total_memory_gb': psutil.virtual_memory().total / (1024**3),
            'cpu_count': psutil.cpu_count(),
            'gpu_available': self._check_gpu_available(),
            'platform': sys.platform
        }
        return info
    
    def _is_laptop(self) -> bool:
        """Detect if running on a laptop."""
        battery = psutil.sensors_battery()
        return battery is not None
    
    def _check_gpu_available(self) -> str:
        """Check for available GPU hardware."""
        try:
            subprocess.run(['nvidia-smi'], capture_output=True, check=True)
            return "NVIDIA"
        except:
            try:
                subprocess.run(['rocm-smi'], capture_output=True, check=True)
                return "AMD"
            except:
                return "None"
    
    def _should_check(self, check_type: str) -> bool:
        """Determine if enough time has passed for a new check."""
        current_time = time.time()
        last_check = self._last_checks.get(check_type, 0)
        interval = self._check_intervals.get(check_type, 5)
        
        if current_time - last_check >= interval:
            self._last_checks[check_type] = current_time
            return True
        return False
    
    def get_network_usage(self) -> Dict[str, float]:
        """Get network usage statistics."""
        if not self._should_check('network'):
            return self._temp_cache.get('network', {'sent_mbps': 0, 'recv_mbps': 0})
        
        try:
            net_io = psutil.net_io_counters()
            time.sleep(1)  # Measure over 1 second
            net_io_after = psutil.net_io_counters()
            
            sent_mbps = (net_io_after.bytes_sent - net_io.bytes_sent) * 8 / 1_000_000
            recv_mbps = (net_io_after.bytes_recv - net_io.bytes_recv) * 8 / 1_000_000
            
            result = {'sent_mbps': sent_mbps, 'recv_mbps': recv_mbps}
            self._temp_cache['network'] = result
            return result
        except Exception as e:
            logger.debug(f"Error getting network usage: {e}")
            return {'sent_mbps': 0, 'recv_mbps': 0}
    
    def get_disk_usage(self) -> Dict[str, float]:
        """Get disk usage for Ollama directories."""
        if not self._should_check('disk'):
            return self._temp_cache.get('disk', {'percent': 0})
        
        try:
            ollama_path = Path(get_real_home()) / '.ollama'
            usage = psutil.disk_usage(str(ollama_path))
            result = {'percent': usage.percent}
            self._temp_cache['disk'] = result
            return result
        except Exception as e:
            logger.debug(f"Error getting disk usage: {e}")
            return {'percent': 0}

class OllamaProcess:
    """Enhanced class to manage Ollama processes and resources."""
    
    def __init__(self):
        self.service_name = "ollama"
        self.process_names = ["ollama"]
        self.logger = logger
        self.monitor = SystemMonitor()
        self.last_warning_time = 0
        self.warning_cooldown = 300
        self.real_user = get_real_user()
        self.real_home = get_real_home()
    
    def set_process_priority(self, pid: int, priority: str) -> bool:
        """Set process priority (nice value)."""
        try:
            nice_values = {
                'low': 10,
                'normal': 0,
                'high': -10
            }
            nice_value = nice_values.get(priority, 0)
            
            if os.geteuid() == 0:
                os.setpriority(os.PRIO_PROCESS, pid, nice_value)
            else:
                subprocess.run(['sudo', 'renice', str(nice_value), str(pid)], check=True)
            return True
        except Exception as e:
            self.logger.error(f"Error setting process priority: {e}")
            return False
    
    def optimize_for_battery(self):
        """Optimize settings when running on battery."""
        processes = self.get_ollama_processes()
        for proc in processes:
            try:
                # Set CPU affinity to use fewer cores
                cpu_count = psutil.cpu_count()
                if cpu_count > 2:
                    proc.cpu_affinity([0, 1])  # Use only first two cores
                
                # Set to low priority
                self.set_process_priority(proc.pid, 'low')
                
                # Reduce memory usage if possible
                if hasattr(proc, 'nice'):
                    proc.nice(10)  # Lower priority
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
    
    def optimize_for_performance(self):
        """Optimize settings for maximum performance."""
        processes = self.get_ollama_processes()
        for proc in processes:
            try:
                # Use all CPU cores
                proc.cpu_affinity(list(range(psutil.cpu_count())))
                
                # Set to high priority
                self.set_process_priority(proc.pid, 'high')
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
    
    def get_ollama_processes(self) -> List[psutil.Process]:
        """Get all running Ollama processes with enhanced detection."""
        processes = []
        for proc in psutil.process_iter(['pid', 'name', 'cmdline', 'username']):
            try:
                # Check process name, cmdline, and ownership
                if (any(name in proc.name().lower() for name in self.process_names) or
                    any(name in ' '.join(proc.cmdline()).lower() for name in self.process_names)):
                    processes.append(proc)
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        return processes

    def get_resource_usage(self) -> Dict:
        """Get detailed resource usage of Ollama processes."""
        usage = {
            'cpu_percent': 0.0,
            'memory_bytes': 0,
            'gpu_memory_mb': 0,
            'network': {'sent_mbps': 0, 'recv_mbps': 0},
            'disk_percent': 0
        }
        
        processes = self.get_ollama_processes()
        
        for proc in processes:
            try:
                usage['cpu_percent'] += proc.cpu_percent()
                usage['memory_bytes'] += proc.memory_info().rss
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        
        # Get GPU memory usage
        try:
            nvidia_smi = subprocess.run(
                ['nvidia-smi', '--query-compute-apps=pid,used_memory', '--format=csv,noheader'],
                capture_output=True,
                text=True
            )
            if nvidia_smi.returncode == 0:
                for line in nvidia_smi.stdout.splitlines():
                    pid, memory = line.strip().split(',')
                    if any(proc.pid == int(pid) for proc in processes):
                        usage['gpu_memory_mb'] += int(memory.strip().split()[0])
        except:
            pass
        
        # Add network and disk usage
        usage['network'] = self.monitor.get_network_usage()
        usage['disk_percent'] = self.monitor.get_disk_usage()['percent']
        
        return usage

    def get_gpu_info(self) -> Dict:
        """Get comprehensive GPU information."""
        gpu_info = {
            'available': False,
            'name': None,
            'memory_total': 0,
            'memory_used': 0,
            'temperature': None,
            'power_usage': None,
            'utilization': None,
            'driver_version': None
        }
        
        try:
            # Try NVIDIA GPU
            result = subprocess.run([
                'nvidia-smi',
                '--query-gpu=name,memory.total,memory.used,temperature.gpu,power.draw,utilization.gpu,driver_version',
                '--format=csv,noheader'
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                values = result.stdout.strip().split(',')
                gpu_info.update({
                    'available': True,
                    'name': values[0].strip(),
                    'memory_total': int(values[1].split()[0]),
                    'memory_used': int(values[2].split()[0]),
                    'temperature': float(values[3]),
                    'power_usage': float(values[4].split()[0]) if 'N/A' not in values[4] else None,
                    'utilization': float(values[5].split()[0]),
                    'driver_version': values[6].strip()
                })
                return gpu_info
        except:
            pass
        
        try:
            # Try AMD GPU
            result = subprocess.run(['rocm-smi'], capture_output=True, text=True)
            if result.returncode == 0:
                gpu_info['available'] = True
                # Parse rocm-smi output (format varies by version)
                return gpu_info
        except:
            pass
        
        return gpu_info

    def check_resource_warnings(self) -> List[str]:
        """Check for resource usage warnings with enhanced monitoring."""
        warnings = []
        current_time = time.time()
        
        if current_time - self.last_warning_time < self.warning_cooldown:
            return warnings
        
        # CPU Usage
        cpu_percent = psutil.cpu_percent(interval=1)
        if cpu_percent > self.monitor.thresholds.cpu_percent_warning:
            warnings.append(f"High CPU usage: {cpu_percent:.1f}%")
        
        # Memory Usage
        memory = psutil.virtual_memory()
        if memory.percent > self.monitor.thresholds.memory_percent_warning:
            warnings.append(f"High memory usage: {memory.percent:.1f}%")
        
        # GPU Usage
        gpu_info = self.get_gpu_info()
        if gpu_info['available']:
            if gpu_info['temperature'] and gpu_info['temperature'] > self.monitor.thresholds.temperature_warning_celsius:
                warnings.append(f"High GPU temperature: {gpu_info['temperature']}°C")
            if gpu_info['memory_total'] > 0:
                gpu_usage_percent = (gpu_info['memory_used'] / gpu_info['memory_total']) * 100
                if gpu_usage_percent > self.monitor.thresholds.gpu_memory_percent_warning:
                    warnings.append(f"High GPU memory usage: {gpu_usage_percent:.1f}%")
        
        # Network Usage
        network = self.monitor.get_network_usage()
        if network['sent_mbps'] > self.monitor.thresholds.network_warning_mbps:
            warnings.append(f"High network upload: {network['sent_mbps']:.1f} Mbps")
        if network['recv_mbps'] > self.monitor.thresholds.network_warning_mbps:
            warnings.append(f"High network download: {network['recv_mbps']:.1f} Mbps")
        
        # Disk Usage
        disk = self.monitor.get_disk_usage()
        if disk['percent'] > self.monitor.thresholds.disk_usage_warning:
            warnings.append(f"High disk usage: {disk['percent']:.1f}%")
        
        # Temperature
        cpu_temp = self.monitor.get_cpu_temperature()
        if cpu_temp and cpu_temp > self.monitor.thresholds.temperature_warning_celsius:
            warnings.append(f"High CPU temperature: {cpu_temp:.1f}°C")
        
        # Battery
        battery = self.monitor.get_battery_status()
        if battery['present'] and not battery['charging']:
            if battery['percent'] < self.monitor.thresholds.battery_minimum_percent:
                warnings.append(f"Low battery: {battery['percent']:.1f}%")
                # Automatically optimize for battery
                self.optimize_for_battery()
        
        if warnings:
            self.last_warning_time = current_time
        
        return warnings

    def should_stop_for_resources(self) -> Tuple[bool, str]:
        """Check if services should be stopped due to resource constraints."""
        battery = self.monitor.get_battery_status()
        
        # Critical battery level
        if battery['present'] and not battery['charging']:
            if battery['percent'] < self.monitor.thresholds.battery_minimum_percent / 2:
                return True, "Battery level critically low"
        
        # Critical temperature
        cpu_temp = self.monitor.get_cpu_temperature()
        if cpu_temp and cpu_temp > self.monitor.thresholds.temperature_warning_celsius + 10:
            return True, "CPU temperature critical"
        
        gpu_info = self.get_gpu_info()
        if gpu_info['available'] and gpu_info['temperature']:
            if gpu_info['temperature'] > self.monitor.thresholds.temperature_warning_celsius + 10:
                return True, "GPU temperature critical"
        
        # Critical memory usage
        if psutil.virtual_memory().percent > 95:
            return True, "System memory critically low"
        
        return False, ""

    def monitor_resources(self, interval: int = 60, log_file: Optional[str] = None) -> None:
        """Continuously monitor system resources with logging."""
        if log_file:
            file_handler = logging.FileHandler(log_file)
            file_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
            self.logger.addHandler(file_handler)
        
        try:
            self.logger.info("Starting resource monitoring...")
            self.logger.info(f"Monitoring interval: {interval} seconds")
            
            while True:
                # Check warnings
                warnings = self.check_resource_warnings()
                for warning in warnings:
                    self.logger.warning(warning)
                
                # Check if should stop
                should_stop, reason = self.should_stop_for_resources()
                if should_stop:
                    self.logger.warning(f"Stopping services: {reason}")
                    self.stop_services()
                    break
                
                # Show current status
                self.show_status()
                
                # Optimize based on conditions
                battery = self.monitor.get_battery_status()
                if battery['present'] and not battery['charging'] and battery['percent'] < 50:
                    self.optimize_for_battery()
                elif psutil.cpu_percent() < 50 and psutil.virtual_memory().percent < 70:
                    self.optimize_for_performance()
                
                time.sleep(interval)
        
        except KeyboardInterrupt:
            self.logger.info("Monitoring stopped by user")
        except Exception as e:
            self.logger.error(f"Error during monitoring: {e}", exc_info=True)
        finally:
            if log_file:
                self.logger.removeHandler(file_handler)

    def start_services(self, priority: str = 'normal') -> bool:
        """Start Ollama services with specified priority."""
        try:
            # Check if already running
            if self.get_ollama_processes():
                self.logger.info("Ollama is already running")
                return True
            
            # Start the service
            self.logger.info("Starting Ollama service...")
            
            # Create a new process group
            process = subprocess.Popen(
                ['ollama', 'serve'],
                start_new_session=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            
            # Set process priority
            self.set_process_priority(process.pid, priority)
            
            # Wait for service to start
            time.sleep(2)
            
            if self.get_ollama_processes():
                self.logger.info("Ollama service started successfully")
                self.show_status()
                return True
            else:
                self.logger.error("Failed to start Ollama service")
                return False
                
        except Exception as e:
            self.logger.error(f"Error starting services: {e}")
            return False

    def stop_services(self) -> bool:
        """Stop all Ollama services and processes."""
        try:
            processes = self.get_ollama_processes()
            
            if not processes:
                self.logger.info("No Ollama processes found running")
                return True
            
            # Try systemctl first
            try:
                subprocess.run(['sudo', 'systemctl', 'stop', 'ollama'], 
                             check=False, capture_output=True)
            except subprocess.SubprocessError:
                pass
            
            # Kill remaining processes
            for proc in processes:
                try:
                    proc.terminate()
                    self.logger.info(f"Terminated process {proc.pid}")
                except psutil.NoSuchProcess:
                    continue
            
            # Wait for processes to terminate
            time.sleep(2)
            
            # Force kill if any remain
            remaining = self.get_ollama_processes()
            for proc in remaining:
                try:
                    proc.kill()
                    self.logger.info(f"Force killed process {proc.pid}")
                except psutil.NoSuchProcess:
                    continue
            
            if not self.get_ollama_processes():
                self.logger.info("All Ollama processes stopped successfully")
                return True
            else:
                self.logger.error("Some processes could not be stopped")
                return False
                
        except Exception as e:
            self.logger.error(f"Error stopping services: {e}")
            return False

    def show_status(self, json_output: bool = False) -> Optional[str]:
        """Display current status of Ollama services with optional JSON output."""
        processes = self.get_ollama_processes()
        
        status_data = {
            'status': 'running' if processes else 'stopped',
            'timestamp': datetime.now().isoformat(),
            'processes': [],
            'resources': {},
            'gpu': {},
            'system': {}
        }
        
        if not processes:
            if json_output:
                return json.dumps(status_data, indent=2)
            self.logger.info("Ollama Status: Not Running")
            return None
        
        # Process Information
        usage = self.get_resource_usage()
        status_data['resources'] = {
            'cpu_percent': usage['cpu_percent'],
            'memory_mb': usage['memory_bytes'] / (1024*1024),
            'gpu_memory_mb': usage['gpu_memory_mb'],
            'network': usage['network'],
            'disk_percent': usage['disk_percent']
        }
        
        # GPU Information
        gpu_info = self.get_gpu_info()
        if gpu_info['available']:
            status_data['gpu'] = gpu_info
        
        # System Information
        cpu_temp = self.monitor.get_cpu_temperature()
        battery = self.monitor.get_battery_status()
        status_data['system'] = {
            'cpu_temperature': cpu_temp,
            'battery': battery if battery['present'] else None
        }
        
        # Process Details
        for proc in processes:
            try:
                proc_info = {
                    'pid': proc.pid,
                    'name': proc.name(),
                    'cpu_percent': proc.cpu_percent(),
                    'memory_mb': proc.memory_info().rss / (1024*1024),
                    'create_time': datetime.fromtimestamp(proc.create_time()).isoformat()
                }
                status_data['processes'].append(proc_info)
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        
        if json_output:
            return json.dumps(status_data, indent=2)
        
        # Pretty print status
        self.logger.info("\n=== Ollama Status Report ===")
        self.logger.info(f"Status: {status_data['status'].title()}")
        self.logger.info(f"Timestamp: {status_data['timestamp']}")
        
        self.logger.info(f"\nProcess Information:")
        self.logger.info(f"- Number of processes: {len(processes)}")
        self.logger.info(f"- CPU Usage: {status_data['resources']['cpu_percent']:.1f}%")
        self.logger.info(f"- Memory Usage: {status_data['resources']['memory_mb']:.1f} MB")
        self.logger.info(f"- Network Upload: {status_data['resources']['network']['sent_mbps']:.1f} Mbps")
        self.logger.info(f"- Network Download: {status_data['resources']['network']['recv_mbps']:.1f} Mbps")
        self.logger.info(f"- Disk Usage: {status_data['resources']['disk_percent']:.1f}%")
        
        if gpu_info['available']:
            self.logger.info(f"\nGPU Information:")
            self.logger.info(f"- GPU: {gpu_info['name']}")
            self.logger.info(f"- Memory Used: {gpu_info['memory_used']} MB")
            self.logger.info(f"- Memory Total: {gpu_info['memory_total']} MB")
            self.logger.info(f"- Utilization: {gpu_info['utilization']}%")
            if gpu_info['temperature']:
                self.logger.info(f"- Temperature: {gpu_info['temperature']}°C")
            if gpu_info['power_usage']:
                self.logger.info(f"- Power Usage: {gpu_info['power_usage']}W")
        
        if cpu_temp:
            self.logger.info(f"\nSystem Temperature:")
            self.logger.info(f"- CPU: {cpu_temp:.1f}°C")
        
        if battery['present']:
            self.logger.info(f"\nBattery Status:")
            self.logger.info(f"- Level: {battery['percent']:.1f}%")
            self.logger.info(f"- Charging: {'Yes' if battery['charging'] else 'No'}")
            if battery['time_remaining'] and not battery['charging']:
                hours = battery['time_remaining'] // 3600
                minutes = (battery['time_remaining'] % 3600) // 60
                self.logger.info(f"- Time Remaining: {hours}h {minutes}m")
        
        self.logger.info("\nProcess Details:")
        for proc_info in status_data['processes']:
            self.logger.info(
                f"- PID: {proc_info['pid']}, "
                f"Name: {proc_info['name']}, "
                f"CPU: {proc_info['cpu_percent']:.1f}%, "
                f"Memory: {proc_info['memory_mb']:.1f} MB"
            )
        
        return None

def main():
    parser = argparse.ArgumentParser(
        description='Manage Ollama services and monitor resources',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument('action', choices=['start', 'stop', 'status', 'monitor'],
                       help='Action to perform')
    parser.add_argument('--interval', type=int, default=60,
                       help='Monitoring interval in seconds (default: 60)')
    parser.add_argument('--log-file', type=str,
                       help='Log file for monitoring (optional)')
    parser.add_argument('--priority', choices=['low', 'normal', 'high'],
                       default='normal', help='Process priority for start action')
    parser.add_argument('--json', action='store_true',
                       help='Output status in JSON format')
    
    args = parser.parse_args()
    
    manager = OllamaProcess()
    
    try:
        if args.action == 'start':
            manager.start_services(args.priority)
        elif args.action == 'stop':
            manager.stop_services()
        elif args.action == 'monitor':
            manager.monitor_resources(args.interval, args.log_file)
        else:  # status
            json_status = manager.show_status(args.json)
            if args.json and json_status:
                print(json_status)
    except KeyboardInterrupt:
        logger.info("Operation interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logger.info("Operation interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
        sys.exit(1) 