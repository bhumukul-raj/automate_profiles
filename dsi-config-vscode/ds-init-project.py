#!/usr/bin/env python3

"""
Data Science Project Initializer Script

This script sets up a complete data science development environment including:
1. Project directory structure
2. Portable VSCode installation with data science extensions
3. Conda environment with essential data science packages
4. Configuration files for VSCode, Git, and Python tools

Author: Bhumukul Raj
Date: February 2024
"""

import os
import json
import shutil
import subprocess
import requests
import tarfile
import platform
from pathlib import Path
import sys
import time
import zipfile

def ensure_dsi_config_dir():
    """
    Creates and ensures the existence of .dsi-config directory.
    This directory stores all configuration files and VSCode setup.

    Returns:
        Path: Path object pointing to the .dsi-config directory
    """
    dsi_config_dir = Path('.dsi-config')
    dsi_config_dir.mkdir(exist_ok=True)
    return dsi_config_dir

def get_vscode_download_url():
    """
    Determines the appropriate VSCode download URL based on the system architecture.
    Currently supports Linux x86_64 and ARM64 architectures.

    Returns:
        str: Download URL for VSCode

    Raises:
        SystemExit: If the system architecture is not supported
    """
    system = platform.system().lower()
    machine = platform.machine()

    if system == 'linux':
        if machine == 'x86_64':
            return "https://code.visualstudio.com/sha/download?build=stable&os=linux-x64"
        elif machine == 'aarch64':
            return "https://code.visualstudio.com/sha/download?build=stable&os=linux-arm64"
    else:
        print(f"Unsupported system: {system} {machine}")
        sys.exit(1)

def download_vscode():
    """
    Downloads VSCode from the official website.
    Creates a downloads directory in .dsi-config and saves the archive there.

    Returns:
        Path: Path to the downloaded VSCode archive
    """
    print("Downloading VSCode...")
    url = get_vscode_download_url()

    # Create downloads directory inside .dsi-config
    dsi_config_dir = ensure_dsi_config_dir()
    downloads_dir = dsi_config_dir / 'downloads'
    downloads_dir.mkdir(exist_ok=True)

    # Download VSCode with progress handling
    response = requests.get(url, stream=True)
    tar_path = downloads_dir / 'vscode.tar.gz'

    with open(tar_path, 'wb') as f:
        for chunk in response.iter_content(chunk_size=8192):
            if chunk:
                f.write(chunk)

    return tar_path

def setup_portable_vscode():
    """
    Sets up a portable installation of VSCode.
    This includes:
    1. Checking for existing installation
    2. Downloading VSCode if needed
    3. Extracting to .dsi-config/vscode
    4. Setting up data directory for portable mode
    """
    dsi_config_dir = ensure_dsi_config_dir()
    vscode_dir = dsi_config_dir / 'vscode'

    # Skip if already installed
    if vscode_dir.exists():
        print("VSCode portable installation already exists.")
        return

    # Look for existing archive
    tar_files = list(Path('.').glob('*.tar.gz')) + list(dsi_config_dir.glob('downloads/*.tar.gz'))

    if not tar_files:
        print("No VSCode archive found. Downloading...")
        tar_path = download_vscode()
    else:
        tar_path = tar_files[0]
        print(f"Found existing VSCode archive: {tar_path}")

    # Extract VSCode
    print("Extracting VSCode...")
    with tarfile.open(tar_path, 'r:gz') as tar:
        # Use temporary directory for extraction
        temp_dir = dsi_config_dir / 'temp'
        temp_dir.mkdir(exist_ok=True)
        tar.extractall(temp_dir)

        # Move to final location
        extracted_dir = next(temp_dir.glob('VSCode-*'), None)
        if extracted_dir:
            if vscode_dir.exists():
                shutil.rmtree(vscode_dir)
            shutil.move(str(extracted_dir), str(vscode_dir))
            shutil.rmtree(temp_dir)

    # Setup portable mode
    data_dir = vscode_dir / 'data'
    data_dir.mkdir(exist_ok=True)

    # Move archive to downloads if needed
    if tar_path.parent == Path('.'):
        shutil.move(str(tar_path), str(dsi_config_dir / 'downloads' / tar_path.name))

    print("VSCode portable setup completed!")

def get_extension_download_url(extension_id):
    """
    Retrieves the download URL for a VSCode extension from the marketplace.

    Args:
        extension_id (str): Extension ID in format 'publisher.extension'

    Returns:
        bytes: Extension package content if successful, None otherwise
    """
    publisher, extension_name = extension_id.split('.')
    url = f"https://marketplace.visualstudio.com/_apis/public/gallery/publishers/{publisher}/vsextensions/{extension_name}/latest/vspackage"

    headers = {
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
        'Accept': 'application/json;api-version=3.0-preview.1',
        'Accept-Encoding': 'gzip, deflate, br'
    }

    try:
        # Get version info first
        info_url = f"https://marketplace.visualstudio.com/_apis/public/gallery/publishers/{publisher}/vsextensions/{extension_name}/latest"
        info_response = requests.get(info_url, headers=headers)
        if info_response.status_code == 200:
            # Download the extension package
            download_response = requests.get(url, headers={'User-Agent': headers['User-Agent'], 'Accept': '*/*'})
            if download_response.status_code == 200:
                return download_response.content
    except Exception as e:
        print(f"Error downloading {extension_id}: {e}")
    return None

def install_extensions(vscode_dir):
    """
    Installs VSCode extensions for data science development.
    Downloads and extracts extensions to the portable VSCode installation.

    Args:
        vscode_dir (Path): Path to the VSCode installation directory
    """
    print("\nInstalling VSCode extensions...")
    # List of essential extensions for data science
    extensions = [
        # Core Python support
        "ms-python.python",  # Python language support
        "ms-python.vscode-pylance",  # Python language server
        "ms-python.debugpy",  # Python debugger
        "ms-python.black-formatter",  # Code formatting
        "ms-python.isort",  # Import sorting
        # AI-powered coding assistance
        "VisualStudioExptTeam.vscodeintellicode",  # AI-assisted IntelliSense
        "VisualStudioExptTeam.intellicode-api-usage-examples",  # API usage examples
        # Jupyter support
        "ms-toolsai.jupyter",  # Jupyter notebooks
        "ms-toolsai.jupyter-keymap",  # Jupyter keyboard shortcuts
        "ms-toolsai.jupyter-renderers",  # Notebook output renderers
        "ms-toolsai.vscode-jupyter-cell-tags",  # Cell tagging
        "ms-toolsai.vscode-jupyter-slideshow",  # Slideshow mode
        "ms-toolsai.datascience-linter",  # Linting for notebooks
        # Data Science specific tools
        "ms-toolsai.datawrangler",  # Data manipulation
        "donjayamanne.python-environment-manager",  # Environment management
        # Configuration file support
        "redhat.vscode-yaml",  # YAML support
        # Development helpers
        "formulahendry.code-runner",  # Run code snippets
        "njpwerner.autodocstring",  # Auto-generate docstrings
        "usernamehw.errorlens",  # Inline error messages
        "mechatroner.rainbow-csv",  # CSV/TSV file viewing
        "aaron-bond.better-comments",  # Enhanced comments
        "ms-python.pylint",  # Python linting
        "streetsidesoftware.code-spell-checker",  # Spell checking
        "yzhang.markdown-all-in-one"  # Markdown support
    ]

    # Setup extensions directory
    extensions_dir = vscode_dir / 'data' / 'extensions'
    extensions_dir.mkdir(exist_ok=True)

    # Install each extension
    for extension_id in extensions:
        print(f"Installing {extension_id}...")
        extension_data = get_extension_download_url(extension_id)

        if extension_data:
            ext_dir = extensions_dir / extension_id
            ext_dir.mkdir(exist_ok=True)

            # Save and extract extension
            vsix_path = ext_dir / f"{extension_id}.vsix"
            try:
                with open(vsix_path, 'wb') as f:
                    f.write(extension_data)

                with zipfile.ZipFile(vsix_path, 'r') as zip_ref:
                    zip_ref.extractall(ext_dir)
                print(f"Successfully installed {extension_id}")
            except Exception as e:
                print(f"Error installing {extension_id}: {e}")
            finally:
                if vsix_path.exists():
                    vsix_path.unlink()
        else:
            print(f"Failed to download {extension_id}")

        time.sleep(1)  # Rate limiting

def get_conda_env_path():
    """
    Gets the absolute path to the conda environment directory.

    Returns:
        str: Absolute path to the conda environment
    """
    return os.path.abspath(os.path.join('.conda-env'))

def create_project_structure():
    """
    Creates a standardized data science project structure.
    Sets up directories and configuration files following best practices.
    Includes:
    - Data directories (raw, processed, external)
    - Code directories (src, notebooks, tests)
    - Documentation and model directories
    - Git configuration
    """
    print("\nCreating data science project structure...")

    # Standard directory structure
    directories = [
        'data/raw',         # Original, immutable data
        'data/processed',   # Cleaned and transformed data
        'data/external',    # Data from third-party sources
        'notebooks',        # Jupyter notebooks
        'src',             # Source code
        'models',          # Trained models
        'tests',           # Unit tests
        'docs'             # Documentation
    ]

    for dir_path in directories:
        os.makedirs(dir_path, exist_ok=True)
        print(f"Created directory: {dir_path}")

    # Create .gitignore with data science specific patterns
    gitignore_content = """# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
.env
.venv
env/
venv/
.conda-env/
.dsi-config/

# Jupyter Notebook
.ipynb_checkpoints
*/.ipynb_checkpoints/*

# Data files

#*.csv
#*.dat
#*.out
#*.pid
#*.gz
#*.xls
#*.xlsx
#*.parquet
#*.feather
#*.db
#*.sqlite

# Model files

#*.h5
#*.pkl
#*.model
#*.joblib
#*.pt
#*.pth
#*.onnx
#*.tflite
#*.pb

# IDE
.vscode/
*.swp
*.swo

# Distribution / packaging
dist/
build/
*.egg-info/

# Unit test / coverage reports
htmlcov/
.tox/
.coverage
.coverage.*
.cache
coverage.xml
*.cover
"""

    with open('.gitignore', 'w') as f:
        f.write(gitignore_content)
    print("Created .gitignore file with data science patterns")

    # Create README with project documentation
    readme_content = """# Data Science Project

## Project Structure
```
├── data/
│   ├── raw/        # Original, immutable data
│   ├── processed/  # Cleaned and processed data
│   └── external/   # Data from external sources
├── notebooks/      # Jupyter notebooks
├── src/           # Source code
├── models/        # Trained models
├── tests/         # Unit tests
└── docs/         # Documentation
```
## Development
- Use `notebooks/` for exploration and analysis
- Put reusable code in `src/`
- Save models in `models/`
- Document your work in `docs/`
"""

    with open('README.md', 'w') as f:
        f.write(readme_content)
    print("Created README.md with project documentation")

def setup_python_environment():
    """
    Sets up a conda environment for data science development.
    Includes:
    1. Creating a new conda environment with Python 3.11
    2. Installing Jupyter and IPython kernel
    3. Creating requirements.txt with essential packages
    4. Setting up environment.yml for conda
    """
    env_path = get_conda_env_path()
    print(f"Setting up conda environment in: {env_path}")

    os.makedirs(env_path, exist_ok=True)

    # Create fresh conda environment if needed
    if not os.path.exists(os.path.join(env_path, 'conda-meta')):
        subprocess.run(['conda', 'create', '--prefix', env_path, 'python=3.11', 'ipykernel', 'jupyter', '-y'])

        # Install IPython kernel
        subprocess.run(['conda', 'run', '--prefix', env_path, 'python', '-m', 'ipykernel', 'install', '--user', '--name', 'local-env', '--display-name', 'Python (Local Env)'])

    # Create requirements.txt with essential packages
    dsi_config_dir = ensure_dsi_config_dir()
    requirements_path = dsi_config_dir / 'requirements.txt'
    if not requirements_path.exists():
        with open(requirements_path, 'w') as f:
            f.write('# Core data science packages\n')
            f.write('numpy>=1.24.0\n')
            f.write('pandas>=2.0.0\n')
            f.write('matplotlib>=3.7.0\n')
            f.write('seaborn>=0.12.0\n')
            f.write('#plotly>=5.13.0\n')
            f.write('\n# Machine Learning\n')
            f.write('scikit-learn>=1.2.0\n')
            f.write('#tensorflow>=2.12.0\n')
            f.write('#torch>=2.0.0\n')
            f.write('\n# Deep Learning Utils\n')
            f.write('#tensorboard>=2.12.0\n')
            f.write('#torchvision>=0.15.0\n')
            f.write('\n# Data Processing\n')
            f.write('#scipy>=1.10.0\n')
            f.write('#statsmodels>=0.13.5\n')
            f.write('#pyarrow>=11.0.0\n')
            f.write('\n# Development Tools\n')
            f.write('jupyter>=1.0.0\n')
            f.write('ipykernel>=6.21.0\n')
            f.write('black>=23.1.0\n')
            f.write('isort>=5.12.0\n')
            f.write('pytest>=7.3.0\n')
            f.write('pylint>=2.17.0\n')
            f.write('\n# Web Apps\n')
            f.write('#streamlit>=1.17.0\n')
            f.write('#dash>=2.8.0\n')
            f.write('\n# Utilities\n')
            f.write('tqdm>=4.64.1\n')
            f.write('requests>=2.28.2\n')
            f.write('python-dotenv>=0.21.1\n')

    # Create environment.yml for conda
    environment_path = dsi_config_dir / 'environment.yml'
    if not environment_path.exists():
        with open(environment_path, 'w') as f:
            f.write('name: ds-env\n')
            f.write('channels:\n')
            f.write('  - conda-forge\n')
            f.write('  - defaults\n')
            f.write('dependencies:\n')
            f.write('  - python=3.11\n')
            f.write('  - pip\n')
            f.write('  - numpy\n')
            f.write('  - pandas\n')
            f.write('  - scikit-learn\n')
            f.write('  - matplotlib\n')
            f.write('  - seaborn\n')
            f.write('  - jupyter\n')
            f.write('  - ipykernel\n')
            f.write('  - pip:\n')
            f.write('    - -r requirements.txt\n')

def create_vscode_portable_setup():
    # Create .vscode directory in project root
    vscode_dir = Path('.vscode')
    vscode_dir.mkdir(exist_ok=True)

    env_path = get_conda_env_path()

    # Create basic VSCode settings
    settings = {
        "files.exclude": {
            "**/__pycache__": True,
            "**/.pytest_cache": True,
            "**/*.pyc": True,
            ".dsi-config": True  # Hide the .dsi-config directory by default
        },
        "python.defaultInterpreterPath": "${workspaceFolder}/.conda-env/bin/python",
        "python.analysis.extraPaths": ["${workspaceFolder}"],
        # Python Environment Manager settings
        "python.envManager.enablementScope": "workspace",
        "python.envManager.reloadOnSave": True,
        "python.envManager.showIcons": True,
        "python.envManager.showPackagesLastWrite": True,
        "python.envManager.showPackagesVersion": True,
        # Python extension settings
        "python.condaPath": "conda",
        "python.terminal.activateEnvironment": True,
        "python.terminal.activateEnvInCurrentTerminal": True,
        "python.languageServer": "Pylance",
        "python.analysis.indexing": True,
        "python.analysis.packageIndexDepths": [
            {
                "name": "*",
                "depth": 2
            }
        ],
        # Terminal settings
        "terminal.integrated.defaultProfile.linux": "bash",
        "terminal.integrated.profiles.linux": {
            "bash": {
                "path": "bash",
                "args": ["-l"],
                "overrideName": True
            }
        },
        # Editor settings
        "editor.formatOnSave": True,
        "editor.rulers": [80, 100],
        "editor.codeActionsOnSave": {
            "source.organizeImports": True
        },
        "workbench.startupEditor": "none",
        "files.trimTrailingWhitespace": True,
        # Python formatting
        "python.formatting.provider": "black",
        "python.formatting.blackArgs": ["--line-length", "100"],
        "python.sortImports.args": ["--profile", "black"],
        # Python linting
        "python.linting.enabled": True,
        "python.linting.pylintEnabled": True,
        # Jupyter settings
        "jupyter.askForKernelRestart": False,
        "jupyter.exportWithOutputEnabled": True,
        "jupyter.notebookFileRoot": "${workspaceFolder}",
        "jupyter.generateSVGPlots": True,
        "jupyter.enableCellCodeLens": True,
        "jupyter.enablePlotViewer": True,
        # Additional settings for installed extensions
        "better-comments.tags": [
            {"tag": "!", "color": "#FF2D00", "strikethrough": False, "backgroundColor": "transparent"},
            {"tag": "?", "color": "#3498DB", "strikethrough": False, "backgroundColor": "transparent"},
            {"tag": "//", "color": "#474747", "strikethrough": True, "backgroundColor": "transparent"},
            {"tag": "todo", "color": "#FF8C00", "strikethrough": False, "backgroundColor": "transparent"},
            {"tag": "*", "color": "#98C379", "strikethrough": False, "backgroundColor": "transparent"}
        ],
        "errorLens.enabled": True,
        "errorLens.enabledInProblemsDiagram": True,
        # Git settings
        "git.enableSmartCommit": True,
        "git.autofetch": True,
        # Environment display settings
        "python.analysis.typeCheckingMode": "basic",
        "python.analysis.autoImportCompletions": True,
        "python.analysis.diagnosticMode": "workspace",
        "python.analysis.exclude": [
            "**/.git",
            "**/.dsi-config",
            "**/__pycache__",
            "**/.pytest_cache"
        ]
    }

    # Save settings.json
    with open(vscode_dir / 'settings.json', 'w') as f:
        json.dump(settings, f, indent=4)

    # Create extensions.json with recommended extensions
    extensions = {
        "recommendations": [
            "ms-python.python",
            "ms-python.vscode-pylance",
            "ms-python.debugpy",
            "ms-python.black-formatter",
            "ms-python.isort",
            "VisualStudioExptTeam.vscodeintellicode",
            "VisualStudioExptTeam.intellicode-api-usage-examples",
            "ms-toolsai.jupyter",
            "ms-toolsai.jupyter-keymap",
            "ms-toolsai.jupyter-renderers",
            "ms-toolsai.vscode-jupyter-cell-tags",
            "ms-toolsai.vscode-jupyter-slideshow",
            "ms-toolsai.datascience-linter",
            "ms-toolsai.datawrangler",
            "donjayamanne.python-environment-manager",
            "redhat.vscode-yaml",
            "formulahendry.code-runner",
            "njpwerner.autodocstring",
            "usernamehw.errorlens",
            "mechatroner.rainbow-csv",
            "aaron-bond.better-comments",
            "ms-python.pylint",
            "streetsidesoftware.code-spell-checker",
            "yzhang.markdown-all-in-one"
        ]
    }

    with open(vscode_dir / 'extensions.json', 'w') as f:
        json.dump(extensions, f, indent=4)

    # Create launch.json for debugging configuration
    launch_config = {
        "version": "0.2.0",
        "configurations": [
            {
                "name": "Python: Current File",
                "type": "python",
                "request": "launch",
                "program": "${file}",
                "console": "integratedTerminal",
                "justMyCode": True,
                "env": {
                    "PYTHONPATH": "${workspaceFolder}"
                }
            },
            {
                "name": "Python: Debug Tests",
                "type": "python",
                "request": "launch",
                "program": "${file}",
                "purpose": ["debug-test"],
                "console": "integratedTerminal",
                "justMyCode": False,
                "env": {
                    "PYTHONPATH": "${workspaceFolder}"
                }
            },
            {
                "name": "Python: Streamlit",
                "type": "python",
                "request": "launch",
                "program": "-m streamlit run",
                "args": ["${file}"],
                "console": "integratedTerminal",
                "justMyCode": True,
                "env": {
                    "PYTHONPATH": "${workspaceFolder}"
                }
            }
        ]
    }

    with open(vscode_dir / 'launch.json', 'w') as f:
        json.dump(launch_config, f, indent=4)

def create_launch_script():
    # Create a shell script to launch portable VSCode
    launch_script = """#!/bin/bash
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR/.."
./.dsi-config/vscode/code \\
    --user-data-dir ./.dsi-config/vscode/data \\
    --extensions-dir ./.dsi-config/vscode/data/extensions \\
    --add "$SCRIPT_DIR/.." "$@"
"""

    dsi_config_dir = ensure_dsi_config_dir()
    launch_script_path = dsi_config_dir / 'launch-vscode.sh'
    with open(launch_script_path, 'w') as f:
        f.write(launch_script)

    # Make the script executable
    os.chmod(launch_script_path, 0o755)

    # Create workspace file
    workspace_config = {
        "folders": [
            {
                "path": ".."
            }
        ],
        "settings": {}
    }

    with open(dsi_config_dir / 'workspace.code-workspace', 'w') as f:
        json.dump(workspace_config, f, indent=4)

def create_extension_install_script(vscode_dir):
    print("\nCreating extension installation script...")
    extensions = [
        # Core Python support
        "ms-python.python",
        "ms-python.vscode-pylance",
        "ms-python.debugpy",
        "ms-python.black-formatter",
        "ms-python.isort",
        # IntelliCode and language features
        "VisualStudioExptTeam.vscodeintellicode",
        "VisualStudioExptTeam.intellicode-api-usage-examples",
        # Jupyter support
        "ms-toolsai.jupyter",
        "ms-toolsai.jupyter-keymap",
        "ms-toolsai.jupyter-renderers",
        "ms-toolsai.vscode-jupyter-cell-tags",
        "ms-toolsai.vscode-jupyter-slideshow",
        "ms-toolsai.datascience-linter",
        # Data Science and ML Tools
        "ms-toolsai.datawrangler",
        "donjayamanne.python-environment-manager",
        # YAML Support
        "redhat.vscode-yaml",
        # Additional tools
        "formulahendry.code-runner",
        "njpwerner.autodocstring",
        "usernamehw.errorlens",
        "mechatroner.rainbow-csv",
        "aaron-bond.better-comments",
        "ms-python.pylint",
        "streetsidesoftware.code-spell-checker",
        "yzhang.markdown-all-in-one"
    ]

    # Create the installation script
    install_script = """#!/bin/bash
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR/.."
VSCODE_DIR="./.dsi-config/vscode"
EXTENSIONS_DIR="$VSCODE_DIR/data/extensions"
USER_DATA_DIR="$VSCODE_DIR/data"

echo "Installing VSCode extensions..."

# Set environment variables for CLI mode
export VSCODE_CLI=1
export ELECTRON_RUN_AS_NODE=1
export ELECTRON_NO_ATTACH_CONSOLE=1

# Function to install extension
install_extension() {
    local extension=$1
    echo "Installing $extension..."

    # Try different possible VSCode executable locations
    if [ -f "$VSCODE_DIR/bin/code" ]; then
        "$VSCODE_DIR/bin/code" --install-extension "$extension" \\
            --extensions-dir "$EXTENSIONS_DIR" \\
            --user-data-dir "$USER_DATA_DIR"
    elif [ -f "$VSCODE_DIR/code" ]; then
        "$VSCODE_DIR/code" --install-extension "$extension" \\
            --extensions-dir "$EXTENSIONS_DIR" \\
            --user-data-dir "$USER_DATA_DIR"
    else
        echo "Could not find VSCode executable"
        return 1
    fi

    if [ $? -eq 0 ]; then
        echo "Successfully installed $extension"
    else
        echo "Failed to install $extension"
    fi

    sleep 1
}

# Create extensions directory if it doesn't exist
mkdir -p "$EXTENSIONS_DIR"
"""

    # Add extension installations
    for extension in extensions:
        install_script += f'install_extension "{extension}"\n'

    install_script += """
echo "Extension installation completed!"
echo "Please restart VSCode to activate all extensions."
"""

    # Save the script in .dsi-config directory
    dsi_config_dir = ensure_dsi_config_dir()
    script_path = dsi_config_dir / 'install-extensions.sh'
    with open(script_path, 'w') as f:
        f.write(install_script)

    # Make it executable
    os.chmod(script_path, 0o755)

    print("Created install-extensions.sh script in .dsi-config directory.")
    print("After launching VSCode, run this script to install all extensions.")

def main():
    print("Setting up portable VSCode environment...")

    # Create project structure first
    create_project_structure()

    # Setup Python environment
    setup_python_environment()

    # Install required packages using conda
    env_path = get_conda_env_path()
    dsi_config_dir = ensure_dsi_config_dir()
    subprocess.run(['conda', 'run', '--prefix', env_path, 'pip', 'install', '-r', str(dsi_config_dir / 'requirements.txt')])

    # Setup VSCode
    setup_portable_vscode()
    create_vscode_portable_setup()
    create_launch_script()
    create_extension_install_script(ensure_dsi_config_dir() / 'vscode')

    print("\nPortable VSCode setup completed!")
    print("\nRecommended next steps:")
    print("1. Launch VSCode using: ./.dsi-config/launch-vscode.sh")
    print("2. Install extensions by running: ./.dsi-config/install-extensions.sh")
    print(f"3. Activate conda environment: conda activate {env_path}")
    print("4. Install required packages: pip install -r .dsi-config/requirements.txt")
    print("\nProject structure has been created with data science best practices.")
    print("Check README.md for more information about the project structure.")

    # Move this script to .dsi-config folder
    current_script = Path(__file__).resolve()
    target_path = dsi_config_dir / current_script.name
    shutil.copy2(current_script, target_path)
    print(f"\nScript has been copied to: {target_path}")
    print("You can find it in the .dsi-config folder for future reference.")

if __name__ == "__main__":
    main()

