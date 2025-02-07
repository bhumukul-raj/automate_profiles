#!/usr/bin/env python3

# Standard library imports only
import os
import subprocess
import sys
import shutil
from pathlib import Path
import datetime
import glob
import tarfile
import logging
import json
import platform

# Import shared utilities
from ollama_utils import (
    check_and_install_packages,
    setup_logging,
    check_ollama_installed,
    check_ollama_running,
    stop_ollama_service
)

def is_debian_based():
    """Check if the system is Debian/Ubuntu based."""
    return os.path.exists('/etc/debian_version')

def install_system_package(package_name):
    """Install a system package using apt."""
    try:
        subprocess.run(['sudo', 'apt-get', 'update'], check=True)
        subprocess.run(['sudo', 'apt-get', 'install', '-y', package_name], check=True)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error installing {package_name}: {e}")
        return False

def ensure_pip_installed():
    """Ensure pip is installed in the system."""
    try:
        # Try to import pip
        import pip
        return True
    except ImportError:
        print("pip is not installed. Installing pip...")
        if is_debian_based():
            return install_system_package('python3-pip')
        else:
            try:
                # For non-Debian systems, use get-pip.py
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

def check_and_install_packages():
    """Check and install required packages if they're missing."""
    # First ensure pip is installed
    ensure_pip_installed()
    
    # Define package mappings (pip package -> apt package)
    package_mappings = {
        'psutil': 'python3-psutil',
        'tqdm': 'python3-tqdm',
        'requests': 'python3-requests'
    }
    
    missing_packages = []
    
    # Check each required package
    for package in package_mappings:
        try:
            __import__(package)
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print("Installing required packages...")
        if is_debian_based():
            # Install using apt for Debian-based systems
            for package in missing_packages:
                apt_package = package_mappings[package]
                if not install_system_package(apt_package):
                    print(f"Failed to install {apt_package}")
                    sys.exit(1)
        else:
            # For non-Debian systems, use pip
            try:
                pip_packages = [f"{pkg}>=5.9.0" for pkg in missing_packages]  # Add version requirements if needed
                subprocess.run([sys.executable, '-m', 'pip', 'install'] + pip_packages, check=True)
            except subprocess.CalledProcessError as e:
                print(f"Error installing packages: {e}")
                print("Please install the following packages manually:")
                for package in missing_packages:
                    print(f"  {package}")
                sys.exit(1)
        
        # Verify installations
        for package in missing_packages:
            try:
                __import__(package)
            except ImportError as e:
                print(f"Error: Package {package} still not available after installation")
                print(f"Error details: {e}")
                sys.exit(1)
    
    return True

# Check and install required packages before importing them
check_and_install_packages()

# Now import third-party packages
import tqdm
import psutil
import requests

# Setup logging
logger = setup_logging('ollama_uninstall')

class UninstallOptions:
    def __init__(self):
        self.remove_models = True
        self.remove_config = True
        self.remove_cache = True
        self.remove_docker = True
        self.backup_before_remove = True
        self.compression_level = 6  # Default compression level

def get_user_preferences():
    """Get user preferences for uninstallation."""
    options = UninstallOptions()
    
    print("\nUninstallation Options:")
    print("----------------------")
    
    options.backup_before_remove = input("Create backup before removing? (Y/n): ").lower() != 'n'
    if options.backup_before_remove:
        while True:
            try:
                level = int(input("Compression level (1-9, higher is smaller but slower) [6]: ") or "6")
                if 1 <= level <= 9:
                    options.compression_level = level
                    break
                print("Please enter a number between 1 and 9")
            except ValueError:
                print("Please enter a valid number")
    
    options.remove_models = input("Remove AI models? (Y/n): ").lower() != 'n'
    options.remove_config = input("Remove configuration files? (Y/n): ").lower() != 'n'
    options.remove_cache = input("Remove cache files? (Y/n): ").lower() != 'n'
    
    # Check if Docker is installed before asking
    if shutil.which('docker'):
        options.remove_docker = input("Remove Ollama Docker images? (Y/n): ").lower() != 'n'
    else:
        options.remove_docker = False
    
    return options

def backup_ollama_models(compression_level):
    """Backup Ollama models if they exist."""
    models_dir = Path.home() / '.ollama/models'
    if not models_dir.exists():
        logger.info("No models directory found to backup.")
        return None
    
    try:
        # Get the size of models directory
        size = subprocess.run(['du', '-sh', str(models_dir)], capture_output=True, text=True)
        if size.returncode == 0:
            logger.info(f"Models directory size: {size.stdout.split()[0]}")
        
        # Create backup directory
        backup_dir = Path.home() / 'ollama_models_backup'
        backup_dir.mkdir(exist_ok=True)
        
        # Create timestamped backup file
        timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_file = backup_dir / f'ollama_models_backup_{timestamp}.tar.gz'
        
        logger.info(f"Creating backup at: {backup_file}")
        logger.info(f"Using compression level: {compression_level}")
        
        # Create tar.gz archive with progress bar
        with tarfile.open(backup_file, f"w:gz", compresslevel=compression_level) as tar:
            for item in tqdm.tqdm(models_dir.rglob('*'), desc="Backing up models"):
                if item.is_file():
                    tar.add(item, arcname=item.relative_to(models_dir.parent))
        
        logger.info("Backup completed successfully!")
        return backup_file
    
    except Exception as e:
        logger.error(f"Error during backup: {e}")
        return None

def cleanup_docker_images():
    """Remove Ollama-related Docker images."""
    try:
        if not shutil.which('docker'):
            logger.info("Docker not installed, skipping image cleanup")
            return
        
        logger.info("Checking for Ollama Docker images...")
        result = subprocess.run(['docker', 'images', '--format', '{{.Repository}}:{{.Tag}}'], 
                              capture_output=True, text=True)
        
        if result.returncode == 0:
            ollama_images = [img for img in result.stdout.splitlines() 
                           if 'ollama' in img.lower()]
            
            if ollama_images:
                logger.info(f"Found {len(ollama_images)} Ollama-related Docker images")
                for image in ollama_images:
                    logger.info(f"Removing Docker image: {image}")
                    subprocess.run(['docker', 'rmi', '-f', image])
                logger.info("Docker cleanup completed")
            else:
                logger.info("No Ollama Docker images found")
    except Exception as e:
        logger.error(f"Error during Docker cleanup: {e}")

def check_ollama_files():
    """Check for all Ollama-related files and directories in the system."""
    possible_locations = {
        'models': [
            Path.home() / '.ollama/models',
        ],
        'config': [
            Path.home() / '.ollama/config',
            Path.home() / '.config/ollama',
            Path('/etc/ollama'),
        ],
        'cache': [
            Path.home() / '.cache/ollama',
            Path.home() / '.ollama/cache',
        ],
        'binary': [
            Path('/usr/local/bin/ollama'),
            Path('/usr/bin/ollama'),
        ],
        'service': [
            Path('/etc/systemd/system/ollama.service'),
            Path('/etc/init.d/ollama'),
            Path('/lib/systemd/system/ollama.service'),
        ],
        'logs': [
            Path('/var/log/ollama'),
            Path.home() / '.ollama/logs',
        ]
    }
    
    found_files = {category: [] for category in possible_locations}
    
    for category, paths in possible_locations.items():
        for path in paths:
            if path.exists():
                found_files[category].append(path)
                if path.is_dir():
                    try:
                        size = subprocess.run(['du', '-sh', str(path)], capture_output=True, text=True)
                        logger.info(f"Found {category}: {path} (Size: {size.stdout.split()[0] if size.returncode == 0 else 'unknown'})")
                    except:
                        logger.info(f"Found {category}: {path} (Size: unknown)")
                else:
                    logger.info(f"Found {category}: {path}")
    
    return found_files

def remove_ollama_files(found_files, options):
    """Remove Ollama-related files based on user preferences."""
    for category, paths in found_files.items():
        # Skip if user chose not to remove this category
        if category == 'models' and not options.remove_models:
            continue
        if category == 'config' and not options.remove_config:
            continue
        if category == 'cache' and not options.remove_cache:
            continue
        
        for path in paths:
            try:
                if path.exists():
                    logger.info(f"Removing {path}...")
                    if path.is_dir():
                        shutil.rmtree(path)
                    else:
                        path.unlink()
                    logger.info(f"Successfully removed {path}")
            except Exception as e:
                logger.error(f"Error removing {path}: {e}")
                if 'Permission denied' in str(e):
                    logger.warning("You might need to run this script with sudo for some operations.")

def uninstall_ollama():
    """Main function to uninstall Ollama."""
    logger.info("Starting Ollama uninstallation process...")
    
    # Check and install required packages
    check_and_install_packages()
    
    # Import tqdm after ensuring it's installed
    import tqdm
    
    # Get user preferences
    options = get_user_preferences()
    
    # Check for files first
    logger.info("Checking for Ollama files and directories...")
    found_files = check_ollama_files()
    
    if not any(found_files.values()):
        logger.info("No Ollama files found in common locations.")
        return
    
    # Create backup if requested
    if options.backup_before_remove:
        backup_file = backup_ollama_models(options.compression_level)
        if backup_file:
            logger.info(f"Backup created at: {backup_file}")
    
    # Confirm uninstallation
    response = input("\nProceed with uninstallation? (y/n): ")
    if response.lower() != 'y':
        logger.info("Uninstallation aborted.")
        return
    
    # Stop the service
    if not stop_ollama_service():
        response = input("Failed to stop Ollama service. Continue anyway? (y/n): ")
        if response.lower() != 'y':
            logger.info("Uninstallation aborted.")
            return
    
    # Remove files based on user preferences
    remove_ollama_files(found_files, options)
    
    # Cleanup Docker if requested
    if options.remove_docker:
        cleanup_docker_images()
    
    # Final check
    logger.info("Performing final check for remaining files...")
    remaining_files = check_ollama_files()
    
    if any(remaining_files.values()):
        logger.warning("Some Ollama files could not be removed. You may need to run with sudo.")
        for category, paths in remaining_files.items():
            if paths:
                logger.warning(f"Remaining {category}: {', '.join(str(p) for p in paths)}")
    else:
        logger.info("Ollama has been successfully uninstalled!")

if __name__ == "__main__":
    # Check if running as root when necessary
    if os.geteuid() == 0:
        logger.info("Running with root privileges...")
    else:
        logger.info("Note: Some operations might require root privileges.")
        logger.info("If the uninstallation is incomplete, try running with sudo.")
    
    try:
        uninstall_ollama()
    except KeyboardInterrupt:
        logger.info("\nUninstallation interrupted by user.")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
        sys.exit(1) 