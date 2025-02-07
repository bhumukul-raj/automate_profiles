#!/usr/bin/env python3

"""
Ollama Utilities Module
======================

This module provides shared utilities for Ollama setup and management tools.
It handles common operations like system checks, package management, and logging.

Key Components:
    - System compatibility checks
    - Package management
    - Logging configuration
    - Service management

Usage:
    from ollama_utils import (
        check_and_install_packages,
        setup_logging,
        check_ollama_installed,
        check_ollama_running,
        stop_ollama_service
    )

Author: [Your Name]
License: MIT
Version: 1.0.0
"""

import os
import subprocess
import sys
import shutil
from pathlib import Path
import logging
import platform
from typing import Tuple, Optional, List, Dict, Any

def is_debian_based() -> bool:
    """
    Check if the current system is Debian/Ubuntu based.
    
    Returns:
        bool: True if system is Debian-based, False otherwise
    """
    return os.path.exists('/etc/debian_version')

def install_system_package(package_name: str) -> bool:
    """
    Install a system package using apt package manager.
    
    Args:
        package_name (str): Name of the package to install
        
    Returns:
        bool: True if installation successful, False otherwise
        
    Raises:
        subprocess.CalledProcessError: If package installation fails
    """
    try:
        subprocess.run(['sudo', 'apt-get', 'update'], check=True)
        subprocess.run(['sudo', 'apt-get', 'install', '-y', package_name], check=True)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error installing {package_name}: {e}")
        return False

def ensure_pip_installed() -> bool:
    """
    Ensure pip is installed in the system.
    
    This function checks for pip installation and installs it if missing.
    For Debian-based systems, it uses apt. For others, it uses get-pip.py.
    
    Returns:
        bool: True if pip is available (installed or already present)
        
    Raises:
        SystemExit: If pip installation fails
    """
    try:
        import pip
        return True
    except ImportError:
        print("pip is not installed. Installing pip...")
        if is_debian_based():
            return install_system_package('python3-pip')
        else:
            try:
                subprocess.run(['curl', 'https://bootstrap.pypa.io/get-pip.py', '-o', 'get-pip.py'], check=True)
                subprocess.run([sys.executable, 'get-pip.py'], check=True)
                os.remove('get-pip.py')
                print("pip installed successfully!")
                return True
            except Exception as e:
                print(f"Error installing pip: {e}")
                print("Please install pip manually using:")
                print("  sudo apt-get install python3-pip  # For Debian/Ubuntu")
                print("  sudo yum install python3-pip      # For RHEL/CentOS")
                sys.exit(1)

def check_and_install_packages() -> bool:
    """
    Check and install required Python packages.
    
    This function verifies the presence of required packages and installs
    missing ones using either apt (for Debian-based systems) or pip.
    
    Returns:
        bool: True if all packages are available
        
    Raises:
        SystemExit: If package installation fails
    """
    ensure_pip_installed()
    
    package_mappings = {
        'psutil': 'python3-psutil',
        'tqdm': 'python3-tqdm',
        'requests': 'python3-requests'
    }
    
    missing_packages = []
    
    for package in package_mappings:
        try:
            __import__(package)
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print("Installing required packages...")
        if is_debian_based():
            for package in missing_packages:
                apt_package = package_mappings[package]
                if not install_system_package(apt_package):
                    print(f"Failed to install {apt_package}")
                    sys.exit(1)
        else:
            try:
                pip_packages = [f"{pkg}>=5.9.0" for pkg in missing_packages]
                subprocess.run([sys.executable, '-m', 'pip', 'install'] + pip_packages, check=True)
            except subprocess.CalledProcessError as e:
                print(f"Error installing packages: {e}")
                print("Please install the following packages manually:")
                for package in missing_packages:
                    print(f"  {package}")
                sys.exit(1)
        
        for package in missing_packages:
            try:
                __import__(package)
            except ImportError as e:
                print(f"Error: Package {package} still not available after installation")
                print(f"Error details: {e}")
                sys.exit(1)
    
    return True

def setup_logging(log_name: str) -> logging.Logger:
    """
    Configure and setup logging for Ollama tools.
    
    Args:
        log_name (str): Name of the log file (without extension)
        
    Returns:
        logging.Logger: Configured logger instance
        
    Example:
        >>> logger = setup_logging('ollama_setup')
        >>> logger.info('Starting setup...')
    """
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(Path.home() / f'{log_name}.log'),
            logging.StreamHandler()
        ]
    )
    return logging.getLogger(log_name)

def check_ollama_installed() -> bool:
    """
    Check if Ollama is installed and available in system PATH.
    
    Returns:
        bool: True if Ollama is installed, False otherwise
    """
    return shutil.which('ollama') is not None

def check_ollama_running() -> bool:
    """
    Check if Ollama service is currently running.
    
    Returns:
        bool: True if Ollama service is running, False otherwise
        
    Raises:
        subprocess.CalledProcessError: If process check fails
    """
    try:
        result = subprocess.run(['pgrep', 'ollama'], capture_output=True, text=True)
        return result.returncode == 0
    except subprocess.CalledProcessError:
        return False

def stop_ollama_service() -> bool:
    """
    Stop the Ollama service if it's running.
    
    This function attempts to stop Ollama using systemd if available,
    then falls back to process termination if needed.
    
    Returns:
        bool: True if service was successfully stopped, False otherwise
        
    Example:
        >>> if stop_ollama_service():
        ...     print("Service stopped successfully")
        ... else:
        ...     print("Failed to stop service")
    """
    try:
        systemctl_check = subprocess.run(['systemctl', 'is-active', 'ollama'], capture_output=True, text=True)
        if systemctl_check.stdout.strip() == 'active':
            subprocess.run(['sudo', 'systemctl', 'stop', 'ollama'])
            subprocess.run(['sudo', 'systemctl', 'disable', 'ollama'])
        
        result = subprocess.run(['pgrep', 'ollama'], capture_output=True, text=True)
        if result.returncode == 0:
            subprocess.run(['pkill', 'ollama'])
        return True
    except Exception as e:
        print(f"Error stopping Ollama service: {e}")
        return False 