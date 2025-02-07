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

Usage:
    python3 ollama_service_manager.py start
    python3 ollama_service_manager.py stop
    python3 ollama_service_manager.py status
    python3 ollama_service_manager.py monitor
"""

import os
import sys
import subprocess
import psutil
import time
from pathlib import Path
import argparse
from typing import List, Dict, Optional, Tuple
import json
import warnings

# Import shared utilities
from ollama_utils import setup_logging

# Setup logging
logger = setup_logging('ollama_service')

class ResourceThresholds:
    """Resource threshold configuration."""
    def __init__(self):
        self.cpu_percent_warning = 80.0
        self.memory_percent_warning = 80.0
        self.gpu_memory_percent_warning = 80.0
        self.temperature_warning_celsius = 80.0
        self.battery_minimum_percent = 20.0
        self.load_from_config()
    
    def load_from_config(self):
        """Load thresholds from config file if exists."""
        config_path = Path.home() / '.ollama' / 'resource_config.json'
        if config_path.exists():
            try:
                with open(config_path) as f:
                    config = json.load(f)
                    self.__dict__.update(config)
            except Exception as e:
                logger.warning(f"Error loading config: {e}")

class SystemMonitor:
    """System resource monitoring."""
    
    def __init__(self):
        self.thresholds = ResourceThresholds()
    
    def get_cpu_temperature(self) -> Optional[float]:
        """Get CPU temperature in Celsius."""
        try:
            # Try reading from thermal zones
            for thermal_zone in Path('/sys/class/thermal').glob('thermal_zone*'):
                try:
                    with open(thermal_zone / 'temp') as f:
                        temp = int(f.read().strip()) / 1000.0  # Convert from millicelsius
                        if temp > 0 and temp < 150:  # Sanity check
                            return temp
                except:
                    continue
            
            # Try using sensors command
            result = subprocess.run(['sensors'], capture_output=True, text=True)
            if result.returncode == 0:
                for line in result.stdout.splitlines():
                    if 'Core 0' in line or 'CPU' in line:
                        temp = float(line.split('+')[1].split('°')[0])
                        return temp
            return None
        except:
            return None
    
    def get_gpu_temperature(self) -> Optional[float]:
        """Get GPU temperature in Celsius."""
        try:
            result = subprocess.run(
                ['nvidia-smi', '--query-gpu=temperature.gpu', '--format=csv,noheader'],
                capture_output=True, text=True
            )
            if result.returncode == 0:
                return float(result.stdout.strip())
        except:
            pass
        return None
    
    def get_battery_status(self) -> Dict:
        """Get battery status information."""
        battery_info = {
            'present': False,
            'percent': 100.0,
            'charging': True,
            'time_remaining': None
        }
        
        try:
            battery = psutil.sensors_battery()
            if battery:
                battery_info.update({
                    'present': True,
                    'percent': battery.percent,
                    'charging': battery.power_plugged,
                    'time_remaining': battery.secsleft if battery.secsleft != -1 else None
                })
        except:
            pass
        
        return battery_info

class OllamaProcess:
    """Class to manage Ollama processes and resources."""
    
    def __init__(self):
        self.service_name = "ollama"
        self.process_names = ["ollama"]
        self.logger = logger
        self.monitor = SystemMonitor()
        self.last_warning_time = 0
        self.warning_cooldown = 300  # 5 minutes between warnings
    
    def get_ollama_processes(self) -> List[psutil.Process]:
        """Get all running Ollama processes."""
        processes = []
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            try:
                # Check both process name and cmdline
                if any(name in proc.name().lower() for name in self.process_names) or \
                   any(name in ' '.join(proc.cmdline()).lower() for name in self.process_names):
                    processes.append(proc)
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        return processes

    def get_resource_usage(self) -> Dict:
        """Get resource usage of Ollama processes."""
        total_cpu = 0.0
        total_memory = 0
        gpu_memory = 0
        
        processes = self.get_ollama_processes()
        
        for proc in processes:
            try:
                total_cpu += proc.cpu_percent()
                total_memory += proc.memory_info().rss
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        
        # Check GPU memory usage if NVIDIA GPU is present
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
                        gpu_memory += int(memory.strip().split()[0])  # Convert MiB to bytes
        except (subprocess.SubprocessError, FileNotFoundError):
            pass
        
        return {
            'cpu_percent': total_cpu,
            'memory_bytes': total_memory,
            'gpu_memory_mb': gpu_memory
        }

    def get_gpu_info(self) -> Dict:
        """Get detailed GPU information."""
        gpu_info = {
            'available': False,
            'name': None,
            'memory_total': 0,
            'memory_used': 0,
            'temperature': None,
            'power_usage': None
        }
        
        try:
            # Try NVIDIA GPU
            result = subprocess.run([
                'nvidia-smi',
                '--query-gpu=name,memory.total,memory.used,temperature.gpu,power.draw',
                '--format=csv,noheader'
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                name, total, used, temp, power = result.stdout.strip().split(',')
                gpu_info.update({
                    'available': True,
                    'name': name.strip(),
                    'memory_total': int(total.split()[0]),
                    'memory_used': int(used.split()[0]),
                    'temperature': float(temp),
                    'power_usage': float(power.split()[0]) if 'N/A' not in power else None
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
        """Check for resource usage warnings."""
        warnings = []
        current_time = time.time()
        
        # Only show warnings every 5 minutes
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
        
        # Temperature
        cpu_temp = self.monitor.get_cpu_temperature()
        if cpu_temp and cpu_temp > self.monitor.thresholds.temperature_warning_celsius:
            warnings.append(f"High CPU temperature: {cpu_temp:.1f}°C")
        
        # Battery
        battery = self.monitor.get_battery_status()
        if battery['present'] and not battery['charging']:
            if battery['percent'] < self.monitor.thresholds.battery_minimum_percent:
                warnings.append(f"Low battery: {battery['percent']:.1f}%")
        
        if warnings:
            self.last_warning_time = current_time
        
        return warnings

    def should_stop_for_resources(self) -> Tuple[bool, str]:
        """Check if services should be stopped due to resource constraints."""
        battery = self.monitor.get_battery_status()
        
        # Stop if battery is critically low
        if battery['present'] and not battery['charging']:
            if battery['percent'] < self.monitor.thresholds.battery_minimum_percent:
                return True, "Battery level critical"
        
        # Stop if temperature is too high
        cpu_temp = self.monitor.get_cpu_temperature()
        if cpu_temp and cpu_temp > self.monitor.thresholds.temperature_warning_celsius + 10:
            return True, "CPU temperature critical"
        
        gpu_info = self.get_gpu_info()
        if gpu_info['available'] and gpu_info['temperature']:
            if gpu_info['temperature'] > self.monitor.thresholds.temperature_warning_celsius + 10:
                return True, "GPU temperature critical"
        
        return False, ""

    def monitor_resources(self, interval: int = 60) -> None:
        """Continuously monitor system resources."""
        try:
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
                
                # Wait for next check
                time.sleep(interval)
        except KeyboardInterrupt:
            self.logger.info("Monitoring stopped by user")

    def start_services(self) -> bool:
        """Start Ollama services."""
        try:
            # Check if already running
            if self.get_ollama_processes():
                self.logger.info("Ollama is already running")
                return True
            
            # Start the service
            self.logger.info("Starting Ollama service...")
            subprocess.run(['ollama', 'serve'], start_new_session=True)
            
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

    def show_status(self) -> None:
        """Display current status of Ollama services."""
        processes = self.get_ollama_processes()
        
        if not processes:
            self.logger.info("Ollama Status: Not Running")
            return
        
        self.logger.info("\n=== Ollama Status Report ===")
        self.logger.info("Status: Running")
        
        # Process Information
        usage = self.get_resource_usage()
        self.logger.info(f"\nProcess Information:")
        self.logger.info(f"- Number of processes: {len(processes)}")
        self.logger.info(f"- CPU Usage: {usage['cpu_percent']:.1f}%")
        self.logger.info(f"- Memory Usage: {usage['memory_bytes'] / (1024*1024):.1f} MB")
        
        # GPU Information
        gpu_info = self.get_gpu_info()
        if gpu_info['available']:
            self.logger.info(f"\nGPU Information:")
            self.logger.info(f"- GPU: {gpu_info['name']}")
            self.logger.info(f"- Memory Used: {gpu_info['memory_used']} MB")
            self.logger.info(f"- Memory Total: {gpu_info['memory_total']} MB")
            if gpu_info['temperature']:
                self.logger.info(f"- Temperature: {gpu_info['temperature']}°C")
            if gpu_info['power_usage']:
                self.logger.info(f"- Power Usage: {gpu_info['power_usage']}W")
        
        # Temperature Information
        cpu_temp = self.monitor.get_cpu_temperature()
        if cpu_temp:
            self.logger.info(f"\nTemperature Information:")
            self.logger.info(f"- CPU Temperature: {cpu_temp:.1f}°C")
        
        # Battery Information
        battery = self.monitor.get_battery_status()
        if battery['present']:
            self.logger.info(f"\nBattery Information:")
            self.logger.info(f"- Battery Level: {battery['percent']:.1f}%")
            self.logger.info(f"- Charging: {'Yes' if battery['charging'] else 'No'}")
            if battery['time_remaining'] and not battery['charging']:
                hours = battery['time_remaining'] // 3600
                minutes = (battery['time_remaining'] % 3600) // 60
                self.logger.info(f"- Time Remaining: {hours}h {minutes}m")
        
        # Process Details
        self.logger.info("\nProcess Details:")
        for proc in processes:
            try:
                self.logger.info(f"- PID: {proc.pid}, Name: {proc.name()}, "
                               f"CPU: {proc.cpu_percent()}%, "
                               f"Memory: {proc.memory_info().rss / (1024*1024):.1f} MB")
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue

def main():
    parser = argparse.ArgumentParser(description='Manage Ollama services')
    parser.add_argument('action', choices=['start', 'stop', 'status', 'monitor'],
                       help='Action to perform (start/stop/status/monitor)')
    parser.add_argument('--interval', type=int, default=60,
                       help='Monitoring interval in seconds (default: 60)')
    
    args = parser.parse_args()
    
    manager = OllamaProcess()
    
    if args.action == 'start':
        manager.start_services()
    elif args.action == 'stop':
        manager.stop_services()
    elif args.action == 'monitor':
        manager.monitor_resources(args.interval)
    else:  # status
        manager.show_status()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logger.info("Operation interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
        sys.exit(1) 