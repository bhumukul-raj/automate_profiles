import os
import subprocess
import json
import sys
from pathlib import Path
from typing import Optional, Dict, Any
import shutil
import tarfile
import requests

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

def create_vscode_launcher() -> None:
    """Create a Python script to launch VSCode with portable mode settings"""
    launcher_content = '''#!/usr/bin/env python3
import subprocess
import os
from pathlib import Path
import tarfile
import requests
import sys

# Get the project root directory
PROJECT_ROOT = Path("''' + str(PROJECT_ROOT) + '''").absolute()
VSCODE_DIR = PROJECT_ROOT / '.vscode-portable'
CODE_DIR = VSCODE_DIR / 'VSCode-linux-x64'
EXTENSIONS_DIR = VSCODE_DIR / 'extensions'
VSCODE_DOWNLOAD_URL = "https://code.visualstudio.com/sha/download?build=stable&os=linux-x64"

def download_vscode():
    """Download and extract portable VSCode if not present"""
    if not CODE_DIR.exists():
        print("Downloading portable VSCode...")
        VSCODE_DIR.mkdir(exist_ok=True)

        # Download VSCode
        response = requests.get(VSCODE_DOWNLOAD_URL, allow_redirects=True)
        tar_path = VSCODE_DIR / "vscode.tar.gz"

        with open(tar_path, 'wb') as f:
            f.write(response.content)

        # Extract VSCode
        print("Extracting VSCode...")
        with tarfile.open(tar_path) as tar:
            tar.extractall(path=VSCODE_DIR)

        # Cleanup
        tar_path.unlink()
        print("VSCode setup complete")

def launch_vscode():
    """Launch portable VSCode with settings"""
    try:
        # Ensure VSCode is downloaded and extracted
        download_vscode()

        # Create required directories
        EXTENSIONS_DIR.mkdir(exist_ok=True)
        USER_DATA_DIR = VSCODE_DIR / 'user-data'
        USER_DATA_DIR.mkdir(exist_ok=True)

        # Set up environment variables
        env_vars = os.environ.copy()
        env_vars.update({
            "VSCODE_PORTABLE": str(VSCODE_DIR),
            "VSCODE_USER_DATA_DIR": str(USER_DATA_DIR),
            "ELECTRON_NO_ATTACH_CONSOLE": "1",
            "ELECTRON_ENABLE_LOGGING": "0",
            "ELECTRON_ENABLE_STACK_DUMPING": "0",
            "VSCODE_SKIP_PRELAUNCH": "1"
        })

        # Launch portable VSCode
        code_executable = CODE_DIR / 'code'
        if not code_executable.exists():
            code_executable = CODE_DIR / 'code-insiders'  # fallback

        if not code_executable.exists():
            print("Error: VSCode executable not found!")
            sys.exit(1)

        subprocess.run([
            str(code_executable),
            '--extensions-dir', str(EXTENSIONS_DIR),
            '--user-data-dir', str(USER_DATA_DIR),
            '--disable-gpu',
            '--no-sandbox',
            '--disable-gpu-compositing',
            '--disable-gpu-memory-buffer-video-frames',
            '--disable-features=Autofill',
            '--disable-smooth-scrolling',
            '--disable-features=CalculateNativeWinOcclusion',
            '--disable-dev-shm-usage',
            '--disable-crash-reporter',
            '--disable-updates',
            '--disable-workspace-trust',
            str(PROJECT_ROOT)
        ], check=True, env=env_vars)
    except subprocess.CalledProcessError as e:
        print(f"Error launching VSCode: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")

if __name__ == "__main__":
    launch_vscode()
'''

    launcher_path = PROJECT_ROOT / 'launch_vscode.py'
    try:
        with open(launcher_path, 'w') as f:
            f.write(launcher_content)
        # Make the launcher executable
        os.chmod(launcher_path, 0o755)
        print(f"Created VSCode launcher script at {launcher_path}")
    except Exception as e:
        print(f"Error creating launcher script: {e}")

def install_vscode_extensions() -> None:
    """Install VSCode extensions in portable mode"""
    extensions = [
        # Core Python and Data Science
        "ms-python.python",                # Python language support
        "ms-python.vscode-pylance",        # Python language server
        "ms-toolsai.jupyter",              # Jupyter notebooks
        "ms-toolsai.jupyter-renderers",    # Jupyter notebook output renderers
        "ms-toolsai.jupyter-keymap",       # Jupyter keyboard shortcuts
        "ms-toolsai.vscode-jupyter-cell-tags",  # Jupyter cell tags
        "ms-toolsai.vscode-jupyter-slideshow",  # Jupyter slideshow
        "mechatroner.rainbow-csv",         # CSV/TSV file support
        "GrapeCity.gc-excelviewer"         # Excel viewer
    ]

    # Create all required directories
    vscode_dir = PROJECT_ROOT / '.vscode-portable'
    code_dir = vscode_dir / 'VSCode-linux-x64'
    extensions_dir = vscode_dir / 'extensions'

    # Wait for VSCode download if not present
    if not code_dir.exists():
        print("Please run launch_vscode.py first to download and setup VSCode")
        return

    code_executable = code_dir / 'code'
    if not code_executable.exists():
        code_executable = code_dir / 'code-insiders'

    if not code_executable.exists():
        print("Error: VSCode executable not found!")
        return

    # Install extensions
    for extension in extensions:
        try:
            print(f"Installing extension {extension} in project directory...")
            subprocess.run(
                [str(code_executable),
                 '--extensions-dir', str(extensions_dir),
                 '--install-extension', extension,
                 '--force'],
                check=True,
                capture_output=True,
                text=True,
                env={
                    **os.environ,
                    "VSCODE_PORTABLE": str(vscode_dir)
                }
            )
        except subprocess.CalledProcessError as e:
            print(f"Failed to install extension {extension}: {e.stderr}")
        except Exception as e:
            print(f"Error installing extension {extension}: {str(e)}")

    # Create extensions.json file for recommendations
    extensions_config = {
        "recommendations": [
            "ms-python.python",
            "ms-python.vscode-pylance",
            "ms-toolsai.jupyter",
            "ms-toolsai.jupyter-renderers",
            "mechatroner.rainbow-csv",
            "GrapeCity.gc-excelviewer"
        ]
    }

    extensions_path = PROJECT_ROOT / '.vscode' / 'extensions.json'
    try:
        with open(extensions_path, 'w') as f:
            json.dump(extensions_config, f, indent=4)
        print("VSCode extension recommendations configured for the project")
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
        # Python settings
        "python.defaultInterpreterPath": "${workspaceFolder}/dsi-config/.conda/ds_env/bin/python",
        "python.linting.enabled": True,
        "python.formatting.provider": "black",
        "python.analysis.typeCheckingMode": "basic",
        "python.analysis.autoImportCompletions": True,
        "python.analysis.completeFunctionParens": True,
        "python.terminal.activateEnvironment": True,
        "python.terminal.activateEnvInCurrentTerminal": True,

        # Jupyter settings
        "jupyter.alwaysTrustNotebooks": True,
        "jupyter.interactiveWindow.textEditor.executeSelection": True,
        "jupyter.notebookFileRoot": "${workspaceFolder}",
        "jupyter.askForKernelRestart": False,
        "jupyter.enableCellCodeLens": True,
        "jupyter.enablePlotViewer": True,

        # Editor settings
        "editor.formatOnSave": True,
        "editor.rulers": [88, 100],
        "editor.renderWhitespace": "selection",
        "editor.wordWrap": "on",
        "files.trimTrailingWhitespace": True,

        # Terminal settings
        "terminal.integrated.inheritEnv": True,
        "terminal.integrated.defaultProfile.linux": "bash",
        "terminal.integrated.profiles.linux": {
            "bash": {
                "path": "bash",
                "icon": "terminal-bash"
            }
        },

        # Workspace settings
        "python.envFile": "${workspaceFolder}/.env",
        "python.analysis.extraPaths": ["${workspaceFolder}"],
        "python.condaPath": "conda",

        # CSV/Excel settings
        "csv-preview.separator": ",",
        "csv-preview.quoteMark": "\"",
        "csv-preview.numberFormat": "en-US",

        # Disable telemetry and updates
        "telemetry.telemetryLevel": "off",
        "update.mode": "none",
        "extensions.autoUpdate": False,
        "extensions.autoCheckUpdates": False,
        "workbench.enableExperiments": False,
        "workbench.settings.enableNaturalLanguageSearch": False
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
    """Main function to set up the development environment."""
    # Get environment name and Python version from command line or use defaults
    env_name = sys.argv[1] if len(sys.argv) > 1 else "ds_env"
    python_version = sys.argv[2] if len(sys.argv) > 2 else DEFAULT_PYTHON_VERSION

    print(f"Starting project setup with Python {python_version}...")

    # Clean up existing configurations
    vscode_portable = PROJECT_ROOT / '.vscode-portable'
    if vscode_portable.exists():
        print("Cleaning up existing portable VSCode configuration...")
        shutil.rmtree(vscode_portable)

    vscode_dir = PROJECT_ROOT / '.vscode'
    if vscode_dir.exists():
        print("Cleaning up existing VSCode configuration...")
        shutil.rmtree(vscode_dir)

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

        # Setup VSCode configuration
        setup_vscode_settings()
        install_vscode_extensions()
        create_vscode_launcher()

        print("\nSetup completed successfully!")
        print("Project-specific VSCode configuration has been created.")
        print("IMPORTANT: Always use ./launch_vscode.py to open VSCode for this project")
        print("Do not open the project through VSCode's normal interface")
    else:
        print("Setup failed!")

if __name__ == "__main__":
    main()