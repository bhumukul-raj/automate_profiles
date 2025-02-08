#!/usr/bin/env python3

"""
Ollama Uninstall Script
======================
Simple script to completely remove Ollama and all its files.
"""

import subprocess
import logging
import os
from pathlib import Path
import sys
import shutil
import pwd

# Setup basic logging
logging.basicConfig(level=logging.INFO,
                   format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger('ollama_uninstall')

def get_real_user():
    """Get the real user even when running with sudo."""
    try:
        return pwd.getpwuid(int(os.getenv('SUDO_UID', os.getuid()))).pw_name
    except (KeyError, TypeError):
        return os.getenv('USER', os.getenv('USERNAME', 'user'))

def get_real_home():
    """Get the real user's home directory even when running with sudo."""
    real_user = get_real_user()
    try:
        return pwd.getpwnam(real_user).pw_dir
    except KeyError:
        return os.path.expanduser('~')

def stop_ollama_service():
    """Stop the Ollama service if it's running."""
    try:
        # Try stopping with systemctl first
        subprocess.run(['sudo', 'systemctl', 'stop', 'ollama'], check=False)
        subprocess.run(['sudo', 'systemctl', 'disable', 'ollama'], check=False)
        
        # Kill any remaining processes
        subprocess.run(['pkill', 'ollama'], check=False)
        return True
    except Exception as e:
        logger.error(f"Error stopping Ollama service: {e}")
        return False

def remove_ollama():
    """Remove all Ollama files and directories."""
    try:
        logger.info("Starting Ollama removal...")
        
        # Stop the service first
        logger.info("Stopping Ollama service...")
        stop_ollama_service()
        
        # Get the real user's home directory
        real_home = Path(get_real_home())
        logger.info(f"Using home directory: {real_home}")
        
        # List of locations to clean
        paths_to_remove = [
            # Binary locations
            Path('/usr/local/bin/ollama'),
            Path('/usr/bin/ollama'),
            real_home / '.local' / 'bin' / 'ollama',
            
            # Data directories
            real_home / '.ollama',
            Path('/var/lib/ollama'),
            
            # Configuration
            Path('/etc/ollama'),
            real_home / '.config' / 'ollama',
            
            # Service files
            Path('/etc/systemd/system/ollama.service'),
            Path('/lib/systemd/system/ollama.service'),
            
            # Logs
            Path('/var/log/ollama'),
            real_home / '.ollama_logs'
        ]
        
        # Remove all paths
        for path in paths_to_remove:
            if path.exists():
                logger.info(f"Removing {path}")
                try:
                    if path.is_dir():
                        shutil.rmtree(path)
                    else:
                        path.unlink()
                except PermissionError:
                    logger.info(f"Attempting to remove {path} with sudo...")
                    subprocess.run(['sudo', 'rm', '-rf', str(path)], check=False)
            except Exception as e:
                logger.error(f"Error removing {path}: {e}")
        
        # Clean up Docker images if Docker is installed
        try:
            subprocess.run(['docker', 'images'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            logger.info("Removing Ollama Docker images...")
            subprocess.run(['docker', 'rmi', '-f', 'ollama/ollama'], check=False)
        except:
            pass
        
        # Reload systemd daemon
        subprocess.run(['sudo', 'systemctl', 'daemon-reload'], check=False)
        
        logger.info("Ollama has been completely removed from the system.")
        return True
        
    except Exception as e:
        logger.error(f"Error during uninstallation: {e}")
        return False

if __name__ == "__main__":
    try:
    if os.geteuid() == 0:
        logger.info("Running with root privileges...")
    else:
        logger.info("Note: Some operations might require root privileges.")
            logger.info("If uninstallation is incomplete, try running with sudo.")
    
        remove_ollama()
    except KeyboardInterrupt:
        logger.info("\nUninstallation interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        sys.exit(1) 