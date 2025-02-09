#!/usr/bin/env python3
import os
import sys
import subprocess
from pathlib import Path

# Get the project root directory (where this script is located)
PROJECT_ROOT = Path(__file__).parent.parent.absolute()
DSI_DIR = PROJECT_ROOT / '.dsi'
DSI_ENV_DIR = DSI_DIR / 'environments'
ADDITIONAL_REQUIREMENTS = Path(__file__).parent / 'additional_requirements.txt'

def get_project_env_name() -> str:
    """Get the environment name based on project directory name"""
    # Use PROJECT_ROOT.name directly since it's already at the correct level
    return PROJECT_ROOT.name.lower().replace("-", "_").replace(" ", "_")

def check_env_exists(env_name: str) -> bool:
    """Check if the conda environment exists"""
    env_path = DSI_ENV_DIR / env_name
    return env_path.exists()

def check_additional_requirements_exists() -> bool:
    """Check if additional_requirements.txt exists"""
    if not ADDITIONAL_REQUIREMENTS.exists():
        print(f"Error: {ADDITIONAL_REQUIREMENTS} not found!")
        print("\nPlease create additional_requirements.txt with your additional packages.")
        print("Example additional_requirements.txt content:")
        print("tensorflow>=2.0.0")
        print("pytorch>=2.0.0")
        print("transformers>=4.0.0")
        return False
    return True

def install_additional_packages() -> bool:
    """Install packages from additional_requirements.txt"""
    try:
        conda_prefix = os.environ.get('CONDA_PREFIX')
        if not conda_prefix:
            print("Error: No conda environment is activated")
            return False

        pip_path = os.path.join(conda_prefix, 'bin', 'pip')
        print("\nInstalling packages from additional_requirements.txt...")
        subprocess.run([
            pip_path, 'install', 
            '-r', str(ADDITIONAL_REQUIREMENTS)
        ], check=True)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error installing packages: {e}")
        return False

def main():
    """Main function to install additional packages"""
    # Get environment name
    env_name = get_project_env_name()
    
    # Check if the project environment exists
    if not check_env_exists(env_name):
        print(f"Error: Project environment '{env_name}' not found!")
        print("\nPlease run setup_project.py first to create the environment.")
        print(f"Command: cd dsi-config && python setup_project.py {env_name}")
        sys.exit(1)
    
    # Check if additional_requirements.txt exists
    if not check_additional_requirements_exists():
        sys.exit(1)
    
    # Check if we're in a conda environment
    if not os.environ.get('CONDA_PREFIX'):
        print(f"Error: Please activate the conda environment first!")
        print(f"\nCommand: conda activate {env_name}")
        sys.exit(1)
    
    # Install the packages
    print(f"Installing additional packages in environment '{env_name}'...")
    if install_additional_packages():
        print("\nAdditional packages installed successfully! ✨")
    else:
        print("\nFailed to install some packages. Please check the error messages above.")
        sys.exit(1)

if __name__ == "__main__":
    main() 