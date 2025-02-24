# Data Science Project Initializer

A Python script that automates the setup of a complete data science development environment with portable VSCode and essential extensions.

## Features

- 📁 Creates standardized data science project structure
- 💻 Sets up portable VSCode installation
- 🐍 Configures Conda environment with Python 3.11
- 🔧 Installs essential VSCode extensions for data science
- ⚙️ Configures development tools (Black, isort, Pylint)
- 📓 Sets up Jupyter notebook environment

## Prerequisites

- Linux operating system (x86_64 or ARM64)
- Conda package manager installed
- Internet connection for downloading VSCode and extensions

## Usage

1. Copy `ds-init-project.py` to your new project directory
2. Run the script:
```bash
python ds-init-project.py
```

3. Follow the recommended steps after setup:
```bash
# Launch VSCode
./.dsi-config/launch-vscode.sh

# Install extensions
./.dsi-config/install-extensions.sh

# Activate conda environment
conda activate ./.conda-env

# Install required packages
pip install -r .dsi-config/requirements.txt
```

## Project Structure Created

```
project/
├── data/
│   ├── raw/        # Original, immutable data
│   ├── processed/  # Cleaned and processed data
│   └── external/   # Data from external sources
├── notebooks/      # Jupyter notebooks
├── src/           # Source code
├── models/        # Trained models
├── tests/         # Unit tests
├── docs/          # Documentation
└── .dsi-config/   # Configuration and portable VSCode
```

## Installed Extensions

### Python Development
- Python language support (ms-python.python)
- Pylance language server
- Python debugger
- Black formatter
- isort import sorting

### AI Assistance
- IntelliCode
- IntelliCode API usage examples

### Jupyter Support
- Jupyter notebooks
- Jupyter keymap
- Notebook renderers
- Cell tags and slideshow features

### Data Science Tools
- Data Wrangler
- Python Environment Manager
- YAML support

### Development Helpers
- Code Runner
- Auto Docstring
- Error Lens
- Rainbow CSV
- Better Comments
- Spell Checker
- Markdown support

## Configuration Files

The script creates several configuration files:

- `.vscode/settings.json`: VSCode workspace settings
- `.vscode/extensions.json`: Recommended extensions
- `.vscode/launch.json`: Debug configurations
- `.dsi-config/requirements.txt`: Python package requirements
- `.dsi-config/environment.yml`: Conda environment specification
- `.gitignore`: Data science specific ignore patterns

## Portable Setup

The environment is designed to be portable:
- VSCode is installed locally in `.dsi-config/vscode/`
- Extensions are stored in `.dsi-config/vscode/data/extensions/`
- Conda environment is created in `.conda-env/`

## Troubleshooting

If you encounter issues:

1. Check internet connectivity for downloading VSCode and extensions
2. Ensure Conda is properly installed and accessible
3. Verify you have sufficient disk space
4. Check file permissions in the project directory

## Contributing

Feel free to submit issues and enhancement requests!

## Author

Bhumukul Raj (February 2024)

## License

This project is open source and available under the MIT License. 