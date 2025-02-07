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
import platform
import requests
import tqdm
import psutil
import concurrent.futures
import asyncio
import aiohttp
from typing import List, Dict, Optional, Set
from concurrent.futures import ThreadPoolExecutor

# Import shared utilities
from ollama_utils import (
    check_and_install_packages,
    setup_logging,
    check_ollama_installed,
    check_ollama_running,
    stop_ollama_service
)

# Setup logging
logger = setup_logging('ollama_setup')

class SetupManager:
    """Manages the setup process with parallel processing capabilities."""
    
    def __init__(self):
        self.max_workers = min(32, (os.cpu_count() or 1) + 4)
        self.executor = ThreadPoolExecutor(max_workers=self.max_workers)
        self.download_semaphore = asyncio.Semaphore(5)  # Limit concurrent downloads
        self.session = None
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
        self.executor.shutdown(wait=True)
    
    async def download_file(self, url: str, dest_path: Path, desc: str = None) -> bool:
        """Download a file with async IO and progress bar."""
        async with self.download_semaphore:
            try:
                async with self.session.get(url) as response:
                    if response.status != 200:
                        logger.error(f"Failed to download {url}: {response.status}")
                        return False
                    
                    total_size = int(response.headers.get('content-length', 0))
                    with open(dest_path, 'wb') as f, tqdm.tqdm(
                        desc=desc or "Downloading",
                        total=total_size,
                        unit='iB',
                        unit_scale=True,
                        unit_divisor=1024,
                    ) as pbar:
                        async for chunk in response.content.iter_chunked(8192):
                            size = f.write(chunk)
                            pbar.update(size)
                return True
            except Exception as e:
                logger.error(f"Download error: {e}")
                return False
    
    def run_parallel_task(self, func, items, desc: str = None):
        """Run tasks in parallel with progress tracking."""
        with tqdm.tqdm(total=len(items), desc=desc or "Processing") as pbar:
            futures = []
            results = []
            
            def done_callback(future):
                results.append(future.result())
                pbar.update(1)
            
            for item in items:
                future = self.executor.submit(func, item)
                future.add_done_callback(done_callback)
                futures.append(future)
            
            concurrent.futures.wait(futures)
            return results

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
        logger.info("pip is already installed")
        return True
    except ImportError:
        logger.info("pip is not installed. Installing pip...")
        if is_debian_based():
            logger.info("Detected Debian-based system, using apt to install pip")
            return install_system_package('python3-pip')
        else:
            try:
                # Create temp directory inside ollama folder
                temp_dir = Path(__file__).parent / 'temp'
                temp_dir.mkdir(exist_ok=True)
                get_pip_path = temp_dir / 'get-pip.py'
                
                logger.info("Downloading get-pip.py from PyPA...")
                get_pip_url = "https://bootstrap.pypa.io/get-pip.py"
                # Download get-pip.py with progress bar
                response = requests.get(get_pip_url, stream=True)
                total_size = int(response.headers.get('content-length', 0))
                
                logger.info(f"Downloading get-pip.py ({total_size/1024:.1f} KB) to {get_pip_path}")
                with open(get_pip_path, 'wb') as f, tqdm.tqdm(
                    desc="Downloading get-pip.py",
                    total=total_size,
                    unit='iB',
                    unit_scale=True
                ) as pbar:
                    for data in response.iter_content(chunk_size=1024):
                        size = f.write(data)
                        pbar.update(size)
                
                logger.info("Running get-pip.py to install pip...")
                subprocess.run([sys.executable, str(get_pip_path)], check=True)
                
                logger.info("Cleaning up get-pip.py...")
                get_pip_path.unlink()  # Remove get-pip.py
                try:
                    temp_dir.rmdir()  # Try to remove temp directory if empty
                except OSError:
                    pass  # Ignore if directory is not empty
                
                # Verify pip installation
                try:
                    import pip
                    pip_version = pip.__version__
                    logger.info(f"pip {pip_version} installed successfully!")
                    return True
                except ImportError:
                    logger.error("pip installation verification failed")
                    raise
                
            except Exception as e:
                logger.error(f"Error installing pip: {e}")
                logger.info("Please install pip manually using:")
                logger.info("  sudo apt-get install python3-pip  # For Debian/Ubuntu")
                logger.info("  sudo yum install python3-pip      # For RHEL/CentOS")
                # Clean up if file exists
                if get_pip_path.exists():
                    logger.info("Cleaning up get-pip.py after failed installation...")
                    get_pip_path.unlink()
                try:
                    temp_dir.rmdir()  # Try to remove temp directory
                except (OSError, NameError):
                    pass  # Ignore if directory doesn't exist or is not empty
                sys.exit(1)

def check_disk_space(required_gb=10):
    """Check if there's enough disk space for installation and models."""
    try:
        disk = psutil.disk_usage(str(Path.home()))
        free_gb = disk.free / (1024 * 1024 * 1024)
        logger.info(f"Free disk space: {free_gb:.2f} GB")
        
        if free_gb < required_gb:
            logger.error(f"Insufficient disk space. Need at least {required_gb}GB, but only {free_gb:.2f}GB available.")
            return False
        return True
    except Exception as e:
        logger.error(f"Error checking disk space: {e}")
        return False

def check_gpu_support():
    """Check for GPU support and CUDA availability."""
    try:
        # Check for NVIDIA GPU
        nvidia_smi = subprocess.run(['nvidia-smi'], capture_output=True, text=True)
        if nvidia_smi.returncode == 0:
            logger.info("NVIDIA GPU detected")
            return True, "NVIDIA GPU available"
        
        # Check for AMD GPU
        rocm_smi = subprocess.run(['rocm-smi'], capture_output=True, text=True)
        if rocm_smi.returncode == 0:
            logger.info("AMD GPU detected")
            return True, "AMD GPU available"
        
        logger.info("No GPU detected, will use CPU only")
        return False, "CPU only"
    except Exception as e:
        logger.warning(f"Error checking GPU support: {e}")
        return False, "CPU only"

def download_with_progress(url, dest_path):
    """Download a file with progress bar."""
    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()
        total_size = int(response.headers.get('content-length', 0))
        
        with open(dest_path, 'wb') as file, tqdm.tqdm(
            desc="Downloading",
            total=total_size,
            unit='iB',
            unit_scale=True,
            unit_divisor=1024,
        ) as pbar:
            for data in response.iter_content(chunk_size=1024):
                size = file.write(data)
                pbar.update(size)
        return True
    except Exception as e:
        logger.error(f"Download error: {e}")
        return False

def find_backup_files():
    """Find all available Ollama model backups."""
    backup_dir = Path.home() / 'ollama_models_backup'
    if not backup_dir.exists():
        return []
    
    backups = list(backup_dir.glob('ollama_models_backup_*.tar.gz'))
    return sorted(backups, reverse=True)  # Most recent first

def validate_backup(backup_file):
    """Validate backup file integrity."""
    try:
        with tarfile.open(backup_file, 'r:gz') as tar:
            # Check if it contains expected directories
            members = tar.getmembers()
            if not any(m.name.startswith('models') for m in members):
                logger.warning("Backup doesn't contain models directory")
                return False
            
            # Check for file corruption
            for member in members:
                if member.size < 0:
                    logger.error(f"Corrupted file in backup: {member.name}")
                    return False
        return True
    except Exception as e:
        logger.error(f"Backup validation failed: {e}")
        return False

def restore_backup(backup_file):
    """Restore models from a backup file."""
    try:
        logger.info(f"Starting backup restoration from: {backup_file}")
        
        # Validate backup first
        if not validate_backup(backup_file):
            logger.error("Backup validation failed")
            return False
        
        # Get backup size
        size = subprocess.run(['du', '-sh', str(backup_file)], capture_output=True, text=True)
        if size.returncode == 0:
            logger.info(f"Backup size: {size.stdout.split()[0]}")
        
        # Check disk space
        backup_size_bytes = backup_file.stat().st_size
        required_space_gb = (backup_size_bytes * 2) / (1024**3)  # Double the backup size for safety
        if not check_disk_space(required_space_gb):
            return False
        
        # Create models directory
        models_dir = Path.home() / '.ollama'
        models_dir.mkdir(parents=True, exist_ok=True)
        
        # Extract with progress bar
        with tarfile.open(backup_file, "r:gz") as tar:
            members = tar.getmembers()
            with tqdm.tqdm(members, desc="Restoring") as pbar:
                for member in pbar:
                    tar.extract(member, path=models_dir)
                    pbar.set_description(f"Restoring {member.name[:30]}...")
        
        logger.info("Models restored successfully!")
        return True
    except Exception as e:
        logger.error(f"Error restoring backup: {e}")
        return False

def get_installation_path():
    """Get the custom installation path for Ollama."""
    home_dir = Path.home()
    custom_path = home_dir / 'ollama_installation'
    custom_path.mkdir(parents=True, exist_ok=True)
    return custom_path

async def install_ollama_async(setup: SetupManager, install_path: Path) -> bool:
    """Install Ollama asynchronously."""
    try:
        logger.info(f"Installing Ollama in: {install_path}")
        
        # Download the Ollama install script
        curl_command = ['curl', '-fsSL', 'https://ollama.ai/install.sh']
        install_script = subprocess.run(curl_command, capture_output=True, text=True)
        
        if install_script.returncode != 0:
            logger.error("Failed to download Ollama installation script")
            return False
        
        # Create environment variables for custom installation
        env = os.environ.copy()
        env['OLLAMA_INSTALL_PATH'] = str(install_path)
        
        # Run the installation script
        install_process = subprocess.run(
            ['bash'],
            input=install_script.stdout,
            env=env,
            text=True
        )
        
        return install_process.returncode == 0
    except Exception as e:
        logger.error(f"Error during installation: {e}")
        return False

def handle_backup_restoration():
    """Handle the backup restoration process."""
    backups = find_backup_files()
    if not backups:
        print("No previous backups found. Proceeding with fresh installation.")
        return False
    
    print("\nFound previous Ollama model backups:")
    for i, backup in enumerate(backups, 1):
        size = subprocess.run(['du', '-sh', str(backup)], capture_output=True, text=True)
        size_str = size.stdout.split()[0] if size.returncode == 0 else "unknown size"
        timestamp = backup.stem.split('_')[-2:]  # Get date and time from filename
        print(f"{i}. {backup.name} (Size: {size_str}, Date: {timestamp[0]})")
    
    while True:
        response = input("\nWould you like to restore a backup? (y/n): ")
        if response.lower() == 'n':
            return False
        elif response.lower() == 'y':
            if len(backups) == 1:
                return restore_backup(backups[0])
            
            while True:
                try:
                    choice = int(input(f"Enter backup number (1-{len(backups)}): "))
                    if 1 <= choice <= len(backups):
                        return restore_backup(backups[choice - 1])
                    print("Invalid choice. Please try again.")
                except ValueError:
                    print("Please enter a valid number.")
        print("Please enter 'y' or 'n'.")

def get_latest_version():
    """Get the latest Ollama version from GitHub."""
    try:
        response = requests.get('https://api.github.com/repos/ollama/ollama/releases/latest')
        response.raise_for_status()
        return response.json()['tag_name']
    except Exception as e:
        logger.error(f"Error checking latest version: {e}")
        return None

def get_current_version():
    """Get currently installed Ollama version."""
    try:
        result = subprocess.run(['ollama', 'version'], capture_output=True, text=True)
        if result.returncode == 0:
            return result.stdout.strip()
        return None
    except Exception:
        return None

class InstallationMode:
    def __init__(self):
        self.minimal = False  # Minimal installation without models
        self.custom_path = None  # Custom installation path
        self.gpu_enabled = True  # Enable/disable GPU support
        self.auto_start = True  # Auto-start service after installation
        self.models = []  # List of models to pre-install

def get_installation_preferences() -> InstallationMode:
    """
    Get user preferences for installation mode.
    
    Returns:
        InstallationMode: Configuration object with user preferences
    """
    options = InstallationMode()
    
    # Get dynamic user information
    home_dir = Path.home()
    username = os.getenv('USER') or os.getenv('USERNAME') or 'user'
    
    print("\nOllama Installation Options:")
    print("---------------------------")
    
    # Ask for installation type
    print("\nInstallation Types and Paths:")
    print("1. Full Installation (with default models)")
    print(f"   ├── Binary: /usr/local/bin/ollama")
    print(f"   ├── Models: {home_dir}/.ollama/models")
    print(f"   ├── Config: {home_dir}/.ollama/config")
    print(f"   └── Service: /etc/systemd/system/ollama.service")
    print("   * Requires ~15GB space for models")
    
    print("\n2. Minimal Installation (no models)")
    print(f"   ├── Binary: /usr/local/bin/ollama")
    print(f"   ├── Config: {home_dir}/.ollama/config")
    print(f"   └── Service: /etc/systemd/system/ollama.service")
    print("   * Requires ~500MB space")
    
    print("\n3. Custom Installation")
    print(f"   ├── Choose your own installation path")
    print(f"   ├── Select specific models to install")
    print(f"   └── Configure GPU and service options")
    print("   * Space required depends on selected models")
    
    while True:
        try:
            choice = int(input("\nSelect installation type (1-3): "))
            if 1 <= choice <= 3:
                break
            print("Please enter a number between 1 and 3")
        except ValueError:
            print("Please enter a valid number")
    
    if choice == 2:
        options.minimal = True
    elif choice == 3:
        # Custom path
        print("\nCustom Installation Path:")
        print(f"Default paths are:")
        print(f"1. System path: /usr/local/bin/ollama")
        print(f"2. Home directory: {home_dir}/ollama_custom")
        print(f"3. Current directory: {os.getcwd()}/ollama_custom")
        
        custom_path = input("\nEnter custom installation path (or press Enter for home directory): ").strip()
        if not custom_path:
            custom_path = str(home_dir / 'ollama_custom')
        
        # Expand ~ and environment variables in the path
        custom_path = os.path.expanduser(os.path.expandvars(custom_path))
        options.custom_path = Path(custom_path).resolve()
        
        print(f"\nSelected path: {options.custom_path}")
        print(f"Space required in {options.custom_path}: Depends on selected options")
        
        # GPU support
        gpu_choice = input("\nEnable GPU support? (Y/n): ").lower()
        options.gpu_enabled = gpu_choice != 'n'
        
        # Auto-start
        autostart = input("Auto-start service after installation? (Y/n): ").lower()
        options.auto_start = autostart != 'n'
        
        # Model selection
        print("\nAvailable Models (with approximate sizes):")
        print("Popular Models:")
        print("1.  llama2      - Meta's Llama 2 model                (~4GB)")
        print("2.  mistral     - Mistral 7B model                    (~4GB)")
        print("3.  codellama   - Code specialized Llama              (~4GB)")
        print("4.  neural-chat - Intelligent chat model              (~4GB)")
        print("5.  starling-lm - Starling advanced model            (~4GB)")
        print("6.  dolphin-phi - Phi-2 based model                  (~2.7GB)")
        print("7.  phi         - Microsoft's Phi-2 model            (~2.7GB)")
        print("8.  tinyllama   - Lightweight Llama model            (~1.5GB)")
        print("9.  gemma       - Google's Gemma model               (~4GB)")
        print("10. stable-lm   - Stability AI model                 (~4GB)")
        print("\nOther Options:")
        print("11. Custom      - Enter your own model name")
        print("12. None        - No models")
        
        model_choice = input("\nSelect models (comma-separated numbers, or type 'list' to see all available models): ").strip()
        
        if model_choice.lower() == 'list':
            print("\nFetching complete list of available models...")
            try:
                result = subprocess.run(['ollama', 'list'], capture_output=True, text=True)
                if result.returncode == 0:
                    print("\nAll Available Models:")
                    print(result.stdout)
                else:
                    print("Could not fetch model list. Continuing with known models.")
            except Exception as e:
                print(f"Error fetching model list: {e}")
            model_choice = input("\nSelect models (comma-separated numbers): ").strip()
        
        if model_choice:
            model_map = {
                '1': 'llama2',
                '2': 'mistral',
                '3': 'codellama',
                '4': 'neural-chat',
                '5': 'starling-lm',
                '6': 'dolphin-phi',
                '7': 'phi',
                '8': 'tinyllama',
                '9': 'gemma',
                '10': 'stable-lm'
            }
            
            selected_models = []
            custom_models = []
            
            for choice in model_choice.split(','):
                choice = choice.strip()
                if choice == '11':  # Custom model option
                    while True:
                        custom_model = input("Enter custom model name (or 'done' to finish): ").strip()
                        if custom_model.lower() == 'done':
                            break
                        if custom_model:
                            custom_models.append(custom_model)
                elif choice in model_map:
                    selected_models.append(model_map[choice])
            
            options.models = selected_models + custom_models
            
            if options.models:
                print("\nSelected Models:")
                for model in options.models:
                    if model in model_map.values():
                        print(f"- {model} (Standard model)")
                    else:
                        print(f"- {model} (Custom model)")
                
                # Calculate approximate size (4GB for standard models, estimate for custom)
                total_size = sum(4 if model in model_map.values() else 4 for model in options.models)
                print(f"\nEstimated total space required for selected models: ~{total_size}GB")
                print("Note: Actual size may vary for custom models")
    
    return options

def install_models(models: List[str], logger: logging.Logger) -> bool:
    """
    Install specified Ollama models.
    
    Args:
        models: List of model names to install
        logger: Logger instance for output
    
    Returns:
        bool: True if all models installed successfully
    """
    for model in models:
        logger.info(f"Installing model: {model}")
        try:
            result = subprocess.run(['ollama', 'pull', model], capture_output=True, text=True)
            if result.returncode == 0:
                logger.info(f"Successfully installed {model}")
            else:
                logger.error(f"Failed to install {model}: {result.stderr}")
                return False
        except Exception as e:
            logger.error(f"Error installing {model}: {e}")
            return False
    return True

async def async_setup_ollama(options):
    """Asynchronous setup process."""
    async with SetupManager() as setup:
        # Parallel system checks
        system_checks = [
            setup.executor.submit(check_disk_space),
            setup.executor.submit(check_gpu_support),
            setup.executor.submit(check_and_install_packages)
        ]
        
        # Wait for all checks to complete
        results = await asyncio.gather(*(
            asyncio.wrap_future(future)
            for future in system_checks
        ))
        
        if not all(results):
            logger.error("System checks failed")
            return False
        
        # Download and install Ollama
        install_path = options.custom_path or get_installation_path()
        if not await install_ollama_async(setup, install_path):
            return False
        
        # Install models in parallel if needed
        if not options.minimal and options.models:
            await install_models_async(setup, options.models)
        
        return True

async def install_models_async(setup: SetupManager, models: List[str]) -> bool:
    """Install multiple models in parallel."""
    async def install_model(model: str) -> bool:
        try:
            logger.info(f"Installing model: {model}")
            process = await asyncio.create_subprocess_exec(
                'ollama', 'pull', model,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await process.communicate()
            
            if process.returncode == 0:
                logger.info(f"Successfully installed {model}")
                return True
            else:
                logger.error(f"Failed to install {model}: {stderr.decode()}")
                return False
        except Exception as e:
            logger.error(f"Error installing {model}: {e}")
            return False
    
    # Install models concurrently with a limit
    tasks = [install_model(model) for model in models]
    results = await asyncio.gather(*tasks)
    return all(results)

def main():
    """Main setup function with async support."""
    try:
        # Get installation preferences
        install_options = get_installation_preferences()
        
        # Run async setup
        asyncio.run(async_setup_ollama(install_options))
        
    except KeyboardInterrupt:
        logger.info("Setup interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    main() 