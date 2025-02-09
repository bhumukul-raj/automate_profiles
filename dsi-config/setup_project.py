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
# Define .dsi directory for all configurations
DSI_DIR = PROJECT_ROOT / '.dsi'
DSI_ENV_DIR = DSI_DIR / 'environments'
DSI_VSCODE_DIR = DSI_DIR / 'vscode-portable'
DSI_SETTINGS_DIR = DSI_DIR / 'settings'

def setup_dsi_directories() -> None:
    """Create necessary .dsi directories"""
    DSI_DIR.mkdir(exist_ok=True)
    DSI_ENV_DIR.mkdir(exist_ok=True)
    DSI_VSCODE_DIR.mkdir(exist_ok=True)
    DSI_SETTINGS_DIR.mkdir(exist_ok=True)

def check_requirements_file() -> bool:
    """Check if requirements.txt exists"""
    requirements_path = SCRIPT_DIR / 'requirements.txt'
    if not requirements_path.exists():
        print(f"Error: requirements.txt not found at {requirements_path}!")
        return False
    return True

def create_conda_env(env_name: str, python_version: str = DEFAULT_PYTHON_VERSION) -> bool:
    """Create a new conda environment in the .dsi directory"""
    try:
        env_path = DSI_ENV_DIR / env_name
        
        # Check if environment already exists
        if env_path.exists():
            print(f"Environment {env_name} already exists at {env_path}")
            return True

        print(f"Creating conda environment: {env_name} with Python {python_version}")
        subprocess.run([
            'conda', 'create', '--prefix', str(env_path),
            f'python={python_version}', 'ipykernel', '-y'
        ], check=True)
        
        # Force reinstall ipykernel to ensure it's properly linked
        subprocess.run([
            'conda', 'install', '--prefix', str(env_path),
            'ipykernel', '--update-deps', '--force-reinstall', '-y'
        ], check=True)
        
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
        
        # Install and register IPython kernel
        print("\nInstalling and registering IPython kernel...")
        python_path = os.path.join(conda_prefix, 'bin', 'python')
        subprocess.run([
            python_path, '-m', 'ipykernel', 'install',
            '--user',
            '--name', 'ds_env',
            '--display-name', 'Python (DS Environment)'
        ], check=True)
        print("IPython kernel installed and registered successfully")
        
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error installing requirements: {e}")
        return False

def create_vscode_launcher() -> None:
    """Create a Python script to launch VSCode with portable mode settings"""
    launcher_content = f'''#!/usr/bin/env python3
import subprocess
import os
from pathlib import Path
import sys

PROJECT_ROOT = Path("{PROJECT_ROOT}").absolute()
DSI_DIR = PROJECT_ROOT / '.dsi'
VSCODE_DIR = DSI_DIR / 'vscode-portable'
CODE_DIR = VSCODE_DIR / 'VSCode-linux-x64'
USER_DATA_DIR = DSI_DIR / 'settings/user-data'
EXTENSIONS_DIR = DSI_DIR / 'settings/extensions'

def launch_vscode():
    try:
        # Create required directories
        USER_DATA_DIR.mkdir(parents=True, exist_ok=True)
        EXTENSIONS_DIR.mkdir(parents=True, exist_ok=True)

        # Set up environment variables
        env_vars = os.environ.copy()
        env_vars.update({{
            "VSCODE_PORTABLE": str(VSCODE_DIR),
            "VSCODE_EXTENSIONS": str(EXTENSIONS_DIR),
            "VSCODE_USER_DATA_DIR": str(USER_DATA_DIR),
            "ELECTRON_NO_ATTACH_CONSOLE": "1"
        }})

        code_executable = CODE_DIR / 'bin' / 'code'  # Updated path to executable
        if not code_executable.exists():
            print("Error: VSCode executable not found!")
            sys.exit(1)

        subprocess.run([
            str(code_executable),
            '--extensions-dir', str(EXTENSIONS_DIR),
            '--user-data-dir', str(USER_DATA_DIR),
            str(PROJECT_ROOT)
        ], check=True, env=env_vars)
    except Exception as e:
        print(f"Error launching VSCode: {{e}}")

if __name__ == "__main__":
    launch_vscode()
'''

    launcher_path = DSI_DIR / 'launch_vscode.py'
    try:
        with open(launcher_path, 'w') as f:
            f.write(launcher_content)
        os.chmod(launcher_path, 0o755)
        print(f"Created VSCode launcher script at {launcher_path}")
    except Exception as e:
        print(f"Error creating launcher script: {e}")

def get_latest_vscode_url() -> str:
    """Get the latest VSCode download URL for Linux"""
    try:
        # Get the latest version info from VSCode update server
        version_url = "https://update.code.visualstudio.com/api/releases/stable/linux-x64"
        response = requests.get(version_url)
        response.raise_for_status()
        return response.json()[0]['url']
    except Exception as e:
        print(f"Error getting latest VSCode URL: {e}")
        # Fallback to a known stable version URL
        return "https://update.code.visualstudio.com/latest/linux-x64/stable"

def download_vscode() -> bool:
    """Download VSCode for Linux"""
    # Direct download URL for VSCode Linux x64 (stable)
    vscode_url = "https://code.visualstudio.com/sha/download?build=stable&os=linux-x64"
    
    # Ensure the directory exists
    DSI_VSCODE_DIR.mkdir(parents=True, exist_ok=True)
    download_path = DSI_VSCODE_DIR / "vscode.tar.gz"

    try:
        print("Downloading VSCode...")
        headers = {
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36',
            'Accept': 'application/octet-stream',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Referer': 'https://code.visualstudio.com/Download'
        }
        
        # First get the redirect URL
        session = requests.Session()
        response = session.get(vscode_url, headers=headers, allow_redirects=False)
        if response.status_code == 302:  # Redirect
            download_url = response.headers['Location']
        else:
            download_url = vscode_url

        # Now download the file
        print(f"Starting download from: {download_url}")
        response = session.get(download_url, stream=True, headers=headers)
        response.raise_for_status()
        
        total_size = int(response.headers.get('content-length', 0))
        current_size = 0
        
        with open(download_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
                    current_size += len(chunk)
                    if total_size:
                        progress = (current_size / total_size) * 100
                        print(f"\rDownload progress: {progress:.1f}%", end='')
        print("\nDownload complete!")

        print("Extracting VSCode...")
        with tarfile.open(download_path, 'r:gz') as tar:
            tar.extractall(path=DSI_VSCODE_DIR)

        # Cleanup
        download_path.unlink()
        
        # Make the VSCode binary executable
        code_executable = DSI_VSCODE_DIR / 'VSCode-linux-x64' / 'bin' / 'code'
        if code_executable.exists():
            os.chmod(code_executable, 0o755)
            print("Made VSCode executable")
            
        return True
    except requests.RequestException as e:
        print(f"Error downloading VSCode: {e}")
        if download_path.exists():
            download_path.unlink()
        return False
    except tarfile.TarError as e:
        print(f"Error extracting VSCode: {e}")
        if download_path.exists():
            download_path.unlink()
        return False
    except Exception as e:
        print(f"Unexpected error: {e}")
        if download_path.exists():
            download_path.unlink()
        return False

def install_vscode_extensions() -> None:
    """Install VSCode extensions in portable mode"""
    # Core extensions (dependencies will be auto-installed)
    extensions = [
        "ms-python.python",          # This will auto-install pylance
        "ms-toolsai.jupyter",        # This will auto-install all jupyter extensions
        "ms-toolsai.jupyter-keymap", # Jupyter keymap
        "ms-toolsai.jupyter-renderers", # Jupyter notebook renderers
        "ms-python.vscode-pylance",  # Python language server
        "ms-toolsai.vscode-jupyter-cell-tags", # Jupyter cell tags
        "ms-toolsai.vscode-jupyter-slideshow", # Jupyter slideshow
        "ms-python.debugpy",         # Python debugger
        "donjayamanne.python-extension-pack", # Comprehensive Python tools
    ]

    # Download VSCode if not present
    code_dir = DSI_VSCODE_DIR / 'VSCode-linux-x64'
    if not code_dir.exists():
        if not download_vscode():
            print("Failed to download VSCode")
            return

    code_executable = code_dir / 'bin' / 'code'
    if not code_executable.exists():
        print("Error: VSCode executable not found!")
        return

    # Create extensions directory
    extensions_dir = DSI_SETTINGS_DIR / 'extensions'
    extensions_dir.mkdir(parents=True, exist_ok=True)

    # Install extensions in CLI mode
    try:
        print("Installing VSCode extensions...")
        env_vars = {
            **os.environ,
            "VSCODE_PORTABLE": str(DSI_VSCODE_DIR),
            "VSCODE_EXTENSIONS": str(extensions_dir),
            "ELECTRON_RUN_AS_NODE": "1",
            "ELECTRON_NO_ATTACH_CONSOLE": "1",
            "DONT_PROMPT_WSL_INSTALL": "1"
        }

        # First make the executable runnable
        os.chmod(code_executable, 0o755)

        for extension in extensions:
            print(f"\nInstalling {extension} and its dependencies...")
            cmd = [
                str(code_executable),
                '--extensions-dir', str(extensions_dir),
                '--install-extension', extension
            ]
            
            try:
                result = subprocess.run(
                    cmd,
                    env=env_vars,
                    capture_output=True,
                    text=True,
                    check=True
                )
                # Only print successful installations
                for line in result.stdout.splitlines():
                    if "successfully installed" in line.lower():
                        print(line.strip())
            except subprocess.CalledProcessError as e:
                print(f"Failed to install {extension}")
                print(f"Error: {e.stderr}")

        print("\nExtension installation completed!")
    except Exception as e:
        print(f"Error installing extensions: {str(e)}")

    # Create extensions.json file for recommendations
    vscode_dir = PROJECT_ROOT / '.vscode'
    vscode_dir.mkdir(exist_ok=True)
    
    # Full list of extensions for recommendations
    all_extensions = [
        "ms-python.python",
        "ms-python.vscode-pylance",
        "ms-toolsai.jupyter",
        "ms-toolsai.jupyter-renderers",
        "ms-toolsai.jupyter-keymap",
        "ms-toolsai.vscode-jupyter-cell-tags",
        "ms-toolsai.vscode-jupyter-slideshow"
    ]
    
    extensions_config = {
        "recommendations": all_extensions
    }

    extensions_path = vscode_dir / 'extensions.json'
    try:
        with open(extensions_path, 'w') as f:
            json.dump(extensions_config, f, indent=4)
        print("VSCode extension recommendations configured")
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
    """Create/update VSCode settings"""
    settings = {
        # Python settings
        "python.defaultInterpreterPath": str(DSI_ENV_DIR / "ds_env" / "bin" / "python"),
        "python.linting.enabled": True,
        "python.formatting.provider": "black",
        "python.analysis.typeCheckingMode": "basic",
        
        # Jupyter settings
        "jupyter.alwaysTrustNotebooks": True,
        "jupyter.notebookFileRoot": "${workspaceFolder}",
        
        # Editor settings
        "editor.formatOnSave": True,
        "editor.rulers": [88, 100],
        
        # Terminal settings
        "terminal.integrated.inheritEnv": False,
        "terminal.integrated.defaultProfile.linux": "bash",
        "terminal.integrated.env.linux": {
            "PYTHONPATH": "${workspaceFolder}"
        },
        
        # Disable update notifications and recommendations
        "extensions.autoUpdate": False,
        "extensions.autoCheckUpdates": False,
        "extensions.ignoreRecommendations": True,
        "update.mode": "none",
        "update.showReleaseNotes": False,
        "workbench.enableExperiments": False,
        "workbench.settings.enableNaturalLanguageSearch": False,
        "workbench.startupEditor": "none",
        
        # Disable telemetry
        "telemetry.telemetryLevel": "off",
        "telemetry.enableTelemetry": False,
        
        # Disable notifications
        "notifications.autocheck": False,
        "notifications.showSetupForExtensions": False,
        
        # Workspace settings
        "python.envFile": "${workspaceFolder}/.env",
        "python.analysis.extraPaths": ["${workspaceFolder}"]
    }

    # Create settings in both user and workspace locations
    settings_locations = [
        DSI_SETTINGS_DIR / 'user-data' / 'User' / 'settings.json',  # User settings
        PROJECT_ROOT / '.vscode' / 'settings.json'  # Workspace settings
    ]

    for settings_path in settings_locations:
        try:
            settings_path.parent.mkdir(parents=True, exist_ok=True)
            with open(settings_path, 'w') as f:
                json.dump(settings, f, indent=4)
            print(f"Created VSCode settings at: {settings_path}")
        except Exception as e:
            print(f"Error creating VSCode settings at {settings_path}: {e}")

def main() -> None:
    """Main function to set up the development environment."""
    env_name = sys.argv[1] if len(sys.argv) > 1 else "ds_env"
    python_version = sys.argv[2] if len(sys.argv) > 2 else DEFAULT_PYTHON_VERSION

    print(f"Starting project setup with Python {python_version}...")
    
    # Create .dsi directory structure
    setup_dsi_directories()

    # Clean up existing configurations if needed
    if DSI_VSCODE_DIR.exists():
        shutil.rmtree(DSI_VSCODE_DIR)
    if DSI_SETTINGS_DIR.exists():
        shutil.rmtree(DSI_SETTINGS_DIR)

    if create_conda_env(env_name, python_version):
        # Setup VSCode configuration
        setup_vscode_settings()
        install_vscode_extensions()
        create_vscode_launcher()

        print("\nSetup completed successfully!")
        print(f"Project environment and settings are in: {DSI_DIR}")
        print(f"To launch VSCode, run: python {DSI_DIR}/launch_vscode.py")
    else:
        print("Setup failed!")

if __name__ == "__main__":
    main()