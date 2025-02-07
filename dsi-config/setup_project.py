import os
import subprocess
import json
import sys
from pathlib import Path
from typing import Optional, Dict, Any

DEFAULT_PYTHON_VERSION = "3.11"

# Get the directory where the script is located
SCRIPT_DIR = Path(__file__).parent.absolute()
# Get the project root directory (parent of script directory)
PROJECT_ROOT = SCRIPT_DIR.parent.absolute()

def check_requirements_file() -> bool:
    """Check if requirements.txt exists"""
    requirements_path = SCRIPT_DIR / 'requirements.txt'
    if not requirements_path.exists():
        print(f"Error: requirements.txt not found at {requirements_path}!")
        return False
    return True

def create_conda_env(env_name: str, python_version: str = DEFAULT_PYTHON_VERSION) -> bool:
    """
    Create a new conda environment with specified Python version
    
    Args:
        env_name: Name of the conda environment
        python_version: Python version to install
    
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # Check if environment already exists
        result = subprocess.run(['conda', 'env', 'list'], capture_output=True, text=True)
        if env_name in result.stdout:
            print(f"Environment {env_name} already exists")
            return True
        
        print(f"Creating conda environment: {env_name} with Python {python_version}")
        subprocess.run(['conda', 'create', '-n', env_name, f'python={python_version}', '-y'], check=True)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error creating conda environment: {e}")
        return False

def install_requirements() -> bool:
    """Install packages from requirements.txt"""
    if not check_requirements_file():
        return False
        
    try:
        print("Installing required packages...")
        conda_prefix = os.environ.get('CONDA_PREFIX')
        if not conda_prefix:
            print("Error: Conda environment not activated")
            return False
            
        pip_path = os.path.join(conda_prefix, 'bin', 'pip')
        requirements_path = SCRIPT_DIR / 'requirements.txt'
        subprocess.run([pip_path, 'install', '-r', str(requirements_path)], check=True)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error installing requirements: {e}")
        return False

def install_vscode_extensions() -> None:
    """Install VSCode extensions locally for the project"""
    extensions = [
        "ms-python.python",
        "ms-toolsai.jupyter",
        "ms-toolsai.jupyter-keymap",
        "ms-toolsai.jupyter-renderers",
        "ms-python.vscode-pylance",
        "formulahendry.code-runner",
        "continue.continue"
    ]
    
    # Create .vscode directory in the project root
    vscode_dir = PROJECT_ROOT / '.vscode'
    vscode_dir.mkdir(exist_ok=True)
    
    # Create extensions.json file
    extensions_config = {
        "recommendations": extensions
    }
    
    extensions_path = vscode_dir / 'extensions.json'
    try:
        with open(extensions_path, 'w') as f:
            json.dump(extensions_config, f, indent=4)
        print("VSCode extension recommendations configured for the project")
        print("Note: When you open this project in VSCode, it will prompt you to install the recommended extensions")
    except Exception as e:
        print(f"Error configuring extension recommendations: {e}")

def load_existing_settings(settings_path: str) -> Dict[str, Any]:
    """Load existing VSCode settings if they exist"""
    try:
        if os.path.exists(settings_path):
            with open(settings_path, 'r') as f:
                return json.load(f)
    except json.JSONDecodeError as e:
        print(f"Warning: Error parsing existing settings: {e}")
    return {}

def setup_vscode_settings() -> None:
    """Create/update VSCode settings for the project"""
    settings = {
        "python.defaultInterpreterPath": "${workspaceFolder}/dsi-config/.conda/ds_env/bin/python",
        "python.linting.enabled": True,
        "python.formatting.provider": "black",
        "editor.formatOnSave": True,
        "jupyter.alwaysTrustNotebooks": True,
        "python.languageServer": "Pylance",
        "python.analysis.typeCheckingMode": "basic",
        "python.terminal.activateEnvironment": True,
        "jupyter.interactiveWindow.textEditor.executeSelection": True,
        "jupyter.notebookFileRoot": "${workspaceFolder}",
        "terminal.integrated.inheritEnv": True,
        "python.analysis.autoImportCompletions": True,
        "python.analysis.completeFunctionParens": True,
        "python.linting.pylintEnabled": True,
        "python.linting.flake8Enabled": True,
        "python.linting.mypyEnabled": True,
        # Add workspace-specific settings
        "python.envFile": "${workspaceFolder}/.env",
        "python.analysis.extraPaths": ["${workspaceFolder}"],
        # Configure local conda environment
        "python.condaPath": "conda",
        "python.terminal.activateEnvInCurrentTerminal": True,
        "terminal.integrated.defaultProfile.linux": "bash",
        "terminal.integrated.profiles.linux": {
            "bash": {
                "path": "bash",
                "icon": "terminal-bash"
            }
        }
    }
    
    vscode_dir = PROJECT_ROOT / '.vscode'
    vscode_dir.mkdir(exist_ok=True)
    settings_path = vscode_dir / 'settings.json'
    
    try:
        # Merge with existing settings
        existing_settings = load_existing_settings(str(settings_path))
        merged_settings = {**existing_settings, **settings}
                
        with open(settings_path, 'w') as f:
            json.dump(merged_settings, f, indent=4)
        print("VSCode project settings created/updated")
    except Exception as e:
        print(f"Error creating VSCode settings: {e}")

def main() -> None:
    """
    Main function to set up the development environment.
    
    This function:
    1. Creates a conda environment with the specified Python version
    2. Installs required packages from requirements.txt
    3. Sets up project-specific VSCode settings and extension recommendations
    4. Configures development tools like black, pylint, and flake8
    """
    # Get environment name and Python version from command line or use defaults
    env_name = sys.argv[1] if len(sys.argv) > 1 else "ds_env"
    python_version = sys.argv[2] if len(sys.argv) > 2 else DEFAULT_PYTHON_VERSION
    
    print(f"Starting project setup with Python {python_version}...")
    
    if create_conda_env(env_name, python_version):
        # Activate conda environment
        conda_prefix = subprocess.check_output(['conda', 'info', '--base']).decode('utf-8').strip()
        activate_script = os.path.join(conda_prefix, 'etc', 'profile.d', 'conda.sh')
        
        activate_cmd = f"source {activate_script} && conda activate {env_name}"
        print(f"\nActivating environment...")
        
        # Run the activation and pip install in a new shell
        if check_requirements_file():
            requirements_path = SCRIPT_DIR / 'requirements.txt'
            install_cmd = f"{activate_cmd} && pip install -r {requirements_path}"
            subprocess.run(['bash', '-c', install_cmd], check=True)
        
        # Setup project-specific VSCode configuration
        install_vscode_extensions()
        setup_vscode_settings()
        
        print("\nSetup completed successfully!")
        print("Project-specific VSCode configuration has been created.")
        print(f"Please restart VSCode and:")
        print(f"1. Run 'conda activate {env_name}' to activate the environment")
        print("2. Install the recommended extensions when prompted by VSCode")
        print("3. Ensure you open VSCode directly in this project directory")
    else:
        print("Setup failed!")

if __name__ == "__main__":
    main() 