#!/usr/bin/env python3

"""
Ollama Setup Script
==================
Simple script to install Ollama using either default or custom installer.
"""

import subprocess
import logging
import os
import pwd
from pathlib import Path
import sys

# Setup basic logging
logging.basicConfig(level=logging.INFO,
                   format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger('ollama_setup')

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

def check_gpu():
    """Check for available GPU hardware."""
    try:
        # Check for NVIDIA GPU
        nvidia_result = subprocess.run(['nvidia-smi'], capture_output=True)
        if nvidia_result.returncode == 0:
            return "NVIDIA"
    except FileNotFoundError:
        pass

    try:
        # Check for AMD GPU
        amd_result = subprocess.run(['rocm-smi'], capture_output=True)
        if amd_result.returncode == 0:
            return "AMD"
    except FileNotFoundError:
        pass

    return "CPU"

def install_ollama_official():
    """Install Ollama using the default installer."""
    try:
        logger.info("Installing Ollama...")
        # First download the script
        curl_process = subprocess.run(
            ['curl', '-fsSL', 'https://ollama.com/install.sh'],
            capture_output=True,
            text=True
        )
        
        if curl_process.returncode != 0:
            logger.error("Failed to download installation script")
            return False
        
        # Then execute it with sh
        install_process = subprocess.run(
            ['sh'],
            input=curl_process.stdout,
            text=True
        )
        
        if install_process.returncode == 0:
            logger.info("Ollama installed successfully!")
            return True
        else:
            logger.error("Installation failed")
            return False
            
    except Exception as e:
        logger.error(f"Error during installation: {e}")
        return False

def install_ollama_custom():
    """Install Ollama with custom configuration."""
    try:
        logger.info("Starting custom installation...")
        
        # Get real user's home directory
        real_home = Path(get_real_home())
        real_user = get_real_user()
        
        # 1. Binary Installation Location
        print("\nBinary Installation Location:")
        print("1. System-wide (/usr/local/bin/ollama)")
        print(f"2. User's bin directory (~/.local/bin/ollama)")
        print("3. Custom location")
        
        bin_path = None
        while True:
            bin_choice = input("\nSelect binary location (1-3): ").strip()
            if bin_choice == "1":
                bin_path = Path("/usr/local/bin/ollama")
                break
            elif bin_choice == "2":
                bin_path = real_home / '.local' / 'bin' / 'ollama'
                bin_path.parent.mkdir(parents=True, exist_ok=True)
                # Set proper ownership
                os.chown(bin_path.parent, int(os.getenv('SUDO_UID', os.getuid())), 
                        int(os.getenv('SUDO_GID', os.getgid())))
                break
            elif bin_choice == "3":
                custom_bin = input("Enter custom binary path: ").strip()
                bin_path = Path(os.path.expanduser(custom_bin))
                bin_path.parent.mkdir(parents=True, exist_ok=True)
                break
            else:
                print("Invalid choice. Please select 1, 2, or 3.")
        
        # 2. Data Directory Location
        install_dir = None
        while True:
            print("\nData Directory Location:")
            print("1. Default (~/.ollama)")
            print("2. Custom subdirectory in ~/.ollama")
            
            dir_choice = input("\nSelect location (1-2): ").strip()
            
            if dir_choice == "1":
                install_dir = real_home / '.ollama'
                break
            elif dir_choice == "2":
                subdir = input("Enter subdirectory name (e.g., 'custom1'): ").strip()
                if '/' in subdir or '\\' in subdir:
                    print("Please enter a simple directory name, not a path")
                    continue
                install_dir = real_home / '.ollama' / subdir
                break
            else:
                print("Invalid choice. Please select 1 or 2.")
        
        if install_dir.exists() and os.listdir(str(install_dir)):
            choice = input(f"\nDirectory {install_dir} already exists and is not empty. Overwrite? (y/n): ")
            if choice.lower() != 'y':
                logger.info("Installation cancelled by user")
                return False
        
        try:
            install_dir.mkdir(parents=True, exist_ok=True)
            # Set proper ownership for the installation directory
            os.chown(install_dir, int(os.getenv('SUDO_UID', os.getuid())), 
                    int(os.getenv('SUDO_GID', os.getgid())))
        except Exception as e:
            logger.error(f"Error creating directory: {e}")
            return False
        
        # 3. GPU/CPU Configuration
        gpu_type = check_gpu()
        print("\nProcessing Mode Configuration:")
        print("Available hardware:")
        if gpu_type == "NVIDIA":
            print("✓ NVIDIA GPU detected")
            print("  - CUDA support available")
            print("  - Can use either GPU or CPU")
        elif gpu_type == "AMD":
            print("✓ AMD GPU detected")
            print("  - ROCm support available")
            print("  - Can use either GPU or CPU")
        else:
            print("! No GPU detected")
            print("  - Will use CPU only")
        
        print("\nSelect processing mode:")
        print("1. CPU Only (Works on all systems, lower memory usage)")
        if gpu_type in ["NVIDIA", "AMD"]:
            print(f"2. {gpu_type} GPU (Faster processing, requires more memory)")
            print(f"\nNote: Even if GPU mode is selected, Ollama will:")
            print(f"- Fall back to CPU if GPU memory is insufficient")
            print(f"- Use CPU for operations that don't benefit from GPU")
            print(f"- Automatically manage GPU/CPU resource allocation")
        
        gpu_enabled = False
        while True:
            mode_choice = input("\nSelect mode (1-2): ").strip()
            if mode_choice == "1":
                gpu_enabled = False
                logger.info("Selected CPU mode: Will use CPU for all operations")
                break
            elif mode_choice == "2" and gpu_type in ["NVIDIA", "AMD"]:
                gpu_enabled = True
                logger.info(f"Selected GPU mode: Will use {gpu_type} GPU when beneficial")
                break
            else:
                print("Invalid choice. Please try again.")
        
        # 4. Service Configuration
        print("\nService Configuration:")
        print("1. Enable system service (auto-start on boot)")
        print("2. Run manually (no system service)")
        
        enable_service = False
        while True:
            service_choice = input("\nSelect service option (1-2): ").strip()
            if service_choice in ["1", "2"]:
                enable_service = service_choice == "1"
                break
            else:
                print("Invalid choice. Please select 1 or 2.")
        
        # Create required subdirectories
        models_dir = install_dir / 'models'
        config_dir = install_dir / 'config'
        
        models_dir.mkdir(exist_ok=True)
        config_dir.mkdir(exist_ok=True)
        
        # Set proper ownership for subdirectories
        os.chown(models_dir, int(os.getenv('SUDO_UID', os.getuid())), 
                int(os.getenv('SUDO_GID', os.getgid())))
        os.chown(config_dir, int(os.getenv('SUDO_UID', os.getuid())), 
                int(os.getenv('SUDO_GID', os.getgid())))
        
        # Create custom installation script
        install_script = f"""#!/bin/bash
# Custom Ollama installation script

# Create directories
mkdir -p {bin_path.parent}
mkdir -p {models_dir}
mkdir -p {config_dir}

# Download Ollama binary
echo "Downloading Ollama binary..."
if ! curl -fsSL https://github.com/ollama/ollama/releases/download/v0.1.27/ollama-linux-amd64 -o {bin_path}; then
    echo "Failed to download Ollama binary"
    exit 1
fi

# Verify binary was downloaded
if [ ! -f {bin_path} ]; then
    echo "Binary file not found after download"
    exit 1
fi

# Set executable permission
chmod +x {bin_path}
if [ ! -x {bin_path} ]; then
    echo "Failed to set executable permission"
    exit 1
fi

# Set proper ownership
chown {real_user}:{real_user} {bin_path}
chown -R {real_user}:{real_user} {install_dir}

# Verify binary works
if ! {bin_path} --version > /dev/null 2>&1; then
    echo "Binary verification failed"
    exit 1
fi

# Set up environment
export OLLAMA_HOME="{install_dir}"
export OLLAMA_MODELS="{models_dir}"
export OLLAMA_CONFIG="{config_dir}"

# Configure GPU settings
export OLLAMA_GPU="{1 if gpu_enabled else 0}"

# Create service file if enabled
if {str(enable_service).lower()}; then
    cat << EOF | sudo tee /etc/systemd/system/ollama.service
[Unit]
Description=Ollama Service
After=network-online.target

[Service]
Environment=OLLAMA_HOME={install_dir}
Environment=OLLAMA_MODELS={models_dir}
Environment=OLLAMA_CONFIG={config_dir}
Environment=OLLAMA_GPU={1 if gpu_enabled else 0}
ExecStart={bin_path} serve
User={real_user}
Group={real_user}
Restart=always

[Install]
WantedBy=default.target
EOF

    # Enable and start service
    sudo systemctl daemon-reload
    sudo systemctl enable ollama
    sudo systemctl start ollama
fi
"""
        
        # Write and execute custom installation script
        script_path = Path('/tmp/ollama_custom_install.sh')
        script_path.write_text(install_script)
        os.chmod(script_path, 0o755)
        
        logger.info("Running custom installation...")
        result = subprocess.run(['bash', str(script_path)], check=True, capture_output=True, text=True)
        
        if result.returncode == 0:
            logger.info("\nOllama installed successfully!")
            logger.info(f"Binary location: {bin_path}")
            logger.info(f"Data directory: {install_dir}")
            logger.info(f"Models directory: {models_dir}")
            logger.info(f"Config directory: {config_dir}")
            logger.info(f"GPU support: {'Enabled' if gpu_enabled else 'Disabled'}")
            logger.info(f"System service: {'Enabled' if enable_service else 'Disabled'}")
            
            # Verify installation
            verify_cmd = subprocess.run([str(bin_path), '--version'], capture_output=True, text=True)
            if verify_cmd.returncode == 0:
                version_output = verify_cmd.stdout.strip()
                if "Warning: could not connect" in version_output:
                    # Extract just the version number
                    version_line = [line for line in version_output.split('\n') if "client version" in line][0]
                    logger.info(f"Ollama {version_line}")
                else:
                    logger.info(f"Ollama version: {version_output}")
            else:
                logger.error("Installation verification failed")
                return False
            
            # Cleanup installation script
            script_path.unlink()
            
            # Print post-installation instructions
            logger.info("\nPost-installation instructions:")
            if enable_service:
                logger.info("Ollama service is enabled and running.")
                logger.info("You can check its status with: systemctl status ollama")
            else:
                logger.info("To start Ollama, run one of the following commands:")
                logger.info(f"1. Start in the background: {bin_path} serve &")
                logger.info(f"2. Start in a new terminal: {bin_path} serve")
                logger.info("\nNote: When starting for the first time, Ollama will:")
                logger.info("- Generate a new SSH key for secure operations")
                logger.info("- Initialize the runtime environment")
                logger.info("- Set up GPU detection and optimization")
            
            logger.info("\nTo use Ollama:")
            logger.info("1. Start the service using one of the methods above")
            logger.info("2. Pull a model: ollama pull llama2")
            logger.info("3. Run the model: ollama run llama2")
            
            logger.info("\nAvailable Commands:")
            logger.info("- List models:     ollama list")
            logger.info("- Pull a model:    ollama pull <model>")
            logger.info("- Remove a model:  ollama rm <model>")
            logger.info("- Run a model:     ollama run <model>")
            logger.info("- Model info:      ollama show <model>")
            
            logger.info("\nPopular Models:")
            logger.info("- llama2:      General purpose model")
            logger.info("- codellama:   Code generation and analysis")
            logger.info("- mistral:     Fast and efficient model")
            logger.info("- dolphin:     Helpful assistant model")
            
            if gpu_enabled:
                logger.info("\nGPU Support:")
                logger.info("- NVIDIA GPU detected with CUDA support")
                logger.info("- Models will automatically use GPU acceleration")
            
            logger.info("\nFor more information:")
            logger.info("- Documentation: https://github.com/ollama/ollama")
            logger.info("- Model library: https://ollama.ai/library")
            logger.info("- Examples:      https://github.com/ollama/ollama/tree/main/examples")
            
            return True
        else:
            logger.error("Installation failed")
            logger.error(f"Error output: {result.stderr}")
            return False
    
    except Exception as e:
        logger.error(f"Error during custom installation: {e}")
        return False

def show_installation_menu():
    """Display installation options menu."""
    while True:
        print("\nOllama Installation Options:")
        print("1. Default Installation (Recommended)")
        print("2. Custom Installation")
        print("3. Exit")
        
        choice = input("\nSelect an option (1-3): ").strip()
        
        if choice == '1':
            return install_ollama_official()
        elif choice == '2':
            return install_ollama_custom()
        elif choice == '3':
            logger.info("Installation cancelled by user")
            sys.exit(0)
        else:
            print("Invalid choice. Please select 1, 2, or 3.")

if __name__ == "__main__":
    show_installation_menu() 