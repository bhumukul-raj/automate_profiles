#!/usr/bin/env python3

"""
Ollama Setup Script
==================
Simple script to install Ollama using either default or custom installer.
"""

import subprocess
import logging
import os
from pathlib import Path
import sys

# Setup basic logging
logging.basicConfig(level=logging.INFO,
                   format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger('ollama_setup')

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
        
        # 1. Binary Installation Location
        print("\nBinary Installation Location:")
        print("1. System-wide (/usr/local/bin/ollama)")
        print("2. User's bin directory (~/.local/bin/ollama)")
        print("3. Custom location")
    
    while True:
            bin_choice = input("\nSelect binary location (1-3): ").strip()
            if bin_choice == "1":
                bin_path = Path("/usr/local/bin/ollama")
                break
            elif bin_choice == "2":
                bin_path = Path.home() / '.local' / 'bin' / 'ollama'
                bin_path.parent.mkdir(parents=True, exist_ok=True)
                break
            elif bin_choice == "3":
                custom_bin = input("Enter custom binary path: ").strip()
                bin_path = Path(os.path.expanduser(custom_bin))
                bin_path.parent.mkdir(parents=True, exist_ok=True)
                break
            else:
                print("Invalid choice. Please select 1, 2, or 3.")
        
        # 2. Data Directory Location
        while True:
            print("\nData Directory Location:")
            print("1. Default (~/.ollama)")
            print("2. Custom subdirectory in ~/.ollama")
            
            dir_choice = input("\nSelect location (1-2): ").strip()
            
            if dir_choice == "1":
                install_dir = Path.home() / '.ollama'
                break
            elif dir_choice == "2":
                subdir = input("Enter subdirectory name (e.g., 'custom1'): ").strip()
                if '/' in subdir or '\\' in subdir:
                    print("Please enter a simple directory name, not a path")
                    continue
                install_dir = Path.home() / '.ollama' / subdir
                break
            else:
                print("Invalid choice. Please select 1 or 2.")
            
            try:
                if install_dir.exists() and os.listdir(str(install_dir)):
                    choice = input(f"\nDirectory {install_dir} already exists and is not empty. Overwrite? (y/n): ")
                    if choice.lower() != 'y':
                        continue
                
                install_dir.mkdir(parents=True, exist_ok=True)
                break
            except Exception as e:
                logger.error(f"Error creating directory: {e}")
                continue
        
        # 3. GPU/CPU Configuration
        gpu_type = check_gpu()
        print("\nProcessing Mode Configuration:")
        print("Available hardware:")
        if gpu_type == "NVIDIA":
            print("✓ NVIDIA GPU detected")
        elif gpu_type == "AMD":
            print("✓ AMD GPU detected")
        else:
            print("! No GPU detected")
        
        print("\nSelect processing mode:")
        print("1. CPU Only")
        if gpu_type == "NVIDIA":
            print("2. NVIDIA GPU (Recommended)")
        elif gpu_type == "AMD":
            print("2. AMD GPU (Recommended)")
        
        while True:
            mode_choice = input("\nSelect mode (1-2): ").strip()
            if mode_choice == "1":
                gpu_enabled = False
                break
            elif mode_choice == "2" and gpu_type in ["NVIDIA", "AMD"]:
                gpu_enabled = True
                break
            else:
                print("Invalid choice. Please try again.")
        
        # 4. Service Configuration
        print("\nService Configuration:")
        print("1. Enable system service (auto-start on boot)")
        print("2. Run manually (no system service)")
        
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
        
        # Create custom installation script
        install_script = f"""#!/bin/bash
# Custom Ollama installation script

# Create directories
mkdir -p {bin_path.parent}
mkdir -p {models_dir}
mkdir -p {config_dir}

# Download Ollama binary
curl -fsSL https://ollama.ai/download/ollama-linux-amd64 -o {bin_path}
chmod +x {bin_path}

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
User=$USER
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
        result = subprocess.run(['bash', str(script_path)], check=True)
        
        if result.returncode == 0:
            logger.info("\nOllama installed successfully!")
            logger.info(f"Binary location: {bin_path}")
            logger.info(f"Data directory: {install_dir}")
            logger.info(f"Models directory: {models_dir}")
            logger.info(f"Config directory: {config_dir}")
            logger.info(f"GPU support: {'Enabled' if gpu_enabled else 'Disabled'}")
            logger.info(f"System service: {'Enabled' if enable_service else 'Disabled'}")
            
            # Cleanup installation script
            script_path.unlink()
                return True
            else:
            logger.error("Installation failed")
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