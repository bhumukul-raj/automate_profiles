# 🚀 Data Science Project Setup (DSI-Config)

A modern, automated setup tool for data science projects that configures your development environment with best practices and portable VSCode integration.

![Python Version](https://img.shields.io/badge/python-3.11-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![Conda](https://img.shields.io/badge/conda-compatible-brightgreen.svg)

## ✨ Features

- 🐍 Automated Conda environment setup with Python 3.11
- 📦 Pre-configured essential data science packages
- 🛠️ Portable VSCode setup with recommended extensions
- 🔧 Development tools (black, pylint, flake8, mypy)
- 📊 Jupyter notebook configuration with integrated kernels
- 🎯 Type checking and code quality tools
- 🔒 Secure and isolated project environments
- 📱 Portable configuration (.dsi directory structure)

## 🚀 Quick Start

1. **Clone the repository**
   ```bash
   git clone https://github.com/bhumukul-raj/automate_profiles.git
   cd dsi-config
   ```

2. **Run the setup script**
   ```bash
   python setup_project.py [env_name] [python_version]
   ```
   Arguments:
   - `env_name`: Optional. Defaults to project directory name
   - `python_version`: Optional. Default is "3.11"

3. **Launch VSCode with the configured environment**
   ```bash
   python .dsi/launch_vscode.py
   ```

## 📂 Project Structure

```
.dsi/
├── environments/        # Conda environments
├── vscode-portable/     # Portable VSCode installation
├── settings/           # VSCode settings and extensions
│   ├── user-data/     # User-specific settings
│   └── extensions/    # VSCode extensions
└── launch_vscode.py   # VSCode launcher script
```

## 📦 Included Packages

### Core Data Science
- numpy >= 1.24.0
- pandas >= 2.0.0
- matplotlib >= 3.7.0
- scikit-learn >= 1.3.0
- seaborn >= 0.12.0
- jupyter >= 1.0.0

### Development Tools
- black >= 23.0.0 (code formatting)
- pylint >= 2.17.0 (linting)
- flake8 >= 6.0.0 (style guide)
- pytest >= 7.0.0 (testing)
- mypy (type checking)

## 🛠️ VSCode Integration

The setup includes:
- Portable VSCode installation
- Automatic extension installation:
  - Python extension pack
  - Jupyter extension pack
  - Pylance (Python language server)
  - Debugger for Python
  - Cell Tags and Slideshow features
- Pre-configured settings:
  - Format on save with Black
  - Type checking with mypy
  - Integrated terminal configuration
  - Jupyter notebook settings
  - Workspace-specific Python path

## 🔧 Environment Configuration

- Isolated conda environment per project
- Automatic IPython kernel registration
- Project-specific Python interpreter
- Workspace-aware settings
- Portable configuration that can be version controlled

## 📋 Requirements

- Conda package manager
- Git
- Linux operating system (x64)
- Internet connection (for initial setup)

## 🤝 Contributing

We love your input! We want to make contributing to DSI-Config as easy and transparent as possible, whether it's:

- Reporting a bug
- Discussing the current state of the code
- Submitting a fix
- Proposing new features
- Becoming a maintainer

### Development Process

1. **Fork the Repository**
   ```bash
   # Clone your fork
   git clone https://github.com/<your-username>/automate_profiles.git
   cd automate_profiles
   
   # Add upstream remote
   git remote add upstream https://github.com/bhumukul-raj/automate_profiles.git
   ```

2. **Create a Branch**
   ```bash
   # Update your main
   git checkout main
   git pull upstream main
   
   # Create your feature branch
   git checkout -b feature/amazing-feature
   ```

3. **Make Changes**
   - Write your code
   - Follow the project's coding style
   - Add or update tests as needed
   - Update documentation as needed

4. **Test Your Changes**
   ```bash
   # Run tests
   pytest
   
   # Check code style
   black .
   flake8 .
   mypy .
   ```

5. **Commit Your Changes**
   ```bash
   git add .
   git commit -m 'Add some amazing feature'
   ```

6. **Push and Create PR**
   ```bash
   git push origin feature/amazing-feature
   ```
   Then go to GitHub and create a Pull Request from your feature branch

### Pull Request Guidelines

1. Update the README.md with details of changes if needed
2. Update the requirements.txt if you add or update dependencies
3. The PR should work for Python 3.11
4. Include a description of changes and any related issue numbers

### Code Style

- Follow PEP 8 guidelines
- Use type hints for all function parameters and return values
- Keep functions focused and modular
- Add docstrings for all functions and classes
- Use meaningful variable and function names

### Bug Reports

When reporting a bug, please include:

- A quick summary and/or background
- Steps to reproduce
- What you expected would happen
- What actually happens
- Notes (possibly including why you think this might be happening)

### License

By contributing, you agree that your contributions will be licensed under the MIT License.

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- The Python Data Science Community
- VSCode Team for their amazing extensions
- All contributors who help improve this project 