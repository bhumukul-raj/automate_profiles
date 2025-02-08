#!/usr/bin/env python3

import os
import subprocess
import sys
from pathlib import Path

def check_conda_installed():
    """Check if conda is installed and accessible."""
    try:
        subprocess.run(['conda', '--version'], capture_output=True, check=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("Conda is not installed or not in PATH.")
        print("Please install Conda first: https://docs.conda.io/projects/conda/en/latest/user-guide/install/")
        return False

def get_conda_executable():
    """Get the appropriate conda executable path."""
    # Try to find conda in common locations
    possible_conda_paths = [
        os.path.expanduser("~/anaconda3/bin/conda"),
        os.path.expanduser("~/miniconda3/bin/conda"),
        "/opt/conda/bin/conda",
        "conda"  # If it's in PATH
    ]
    
    for conda_path in possible_conda_paths:
        try:
            subprocess.run([conda_path, '--version'], capture_output=True, check=True)
            return conda_path
        except (subprocess.CalledProcessError, FileNotFoundError):
            continue
    
    return None

def create_conda_env(env_name="env_ollama"):
    """Create a new conda environment if it doesn't exist."""
    conda = get_conda_executable()
    if not conda:
        print("Could not find conda executable.")
        return False
    
    # Check if environment already exists
    result = subprocess.run([conda, 'env', 'list'], capture_output=True, text=True)
    if env_name in result.stdout:
        print(f"Conda environment '{env_name}' already exists.")
        return True
    
    print(f"Creating new conda environment: {env_name}")
    try:
        # Create new environment with Python 3.9
        subprocess.run([conda, 'create', '-n', env_name, 'python=3.9', '-y'], check=True)
        print(f"Successfully created conda environment: {env_name}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error creating conda environment: {e}")
        return False

def install_requirements(env_name="env_ollama"):
    """Install required packages in the conda environment."""
    conda = get_conda_executable()
    if not conda:
        return False
    
    # Get the path to the requirements.txt file
    current_dir = Path(__file__).parent
    requirements_file = current_dir / 'requirements.txt'
    
    if not requirements_file.exists():
        print("requirements.txt not found!")
        return False
    
    # Add aiohttp to requirements if not present
    with open(requirements_file, 'r') as f:
        requirements = f.read()
    
    if 'aiohttp' not in requirements:
        with open(requirements_file, 'a') as f:
            f.write('\naiohttp>=3.8.0  # For async HTTP requests\n')
    
    print("Installing required packages...")
    try:
        # Initialize conda first
        subprocess.run([conda, 'init', 'bash'], check=True)
        
        # Get the environment's Python and pip paths
        conda_prefix = os.path.dirname(os.path.dirname(conda))
        if sys.platform.startswith('win'):
            python_path = os.path.join(conda_prefix, 'envs', env_name, 'python.exe')
            pip_path = os.path.join(conda_prefix, 'envs', env_name, 'Scripts', 'pip.exe')
        else:
            python_path = os.path.join(conda_prefix, 'envs', env_name, 'bin', 'python')
            pip_path = os.path.join(conda_prefix, 'envs', env_name, 'bin', 'pip')
        
        if not os.path.exists(python_path):
            print(f"Could not find Python in conda environment: {python_path}")
            return False
            
        # Install packages using the environment's pip directly
        subprocess.run([pip_path, "install", "-r", str(requirements_file)], check=True)
        
        print("Successfully installed required packages.")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error installing packages: {e}")
        return False

def setup_environment():
    """Main function to setup the conda environment."""
    if not check_conda_installed():
        return False
    
    env_name = "env_ollama"
    if not create_conda_env(env_name):
        return False
    
    if not install_requirements(env_name):
        return False
    
    print("\nEnvironment setup completed successfully!")
    print(f"To activate the environment, run: conda activate {env_name}")
    print("Then run: python ollama/setup_ollama.py")
    return True

if __name__ == "__main__":
    setup_environment() 