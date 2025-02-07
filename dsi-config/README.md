# 🚀 Data Science Project Setup

A modern, automated setup tool for data science projects that configures your development environment with best practices.

![Python Version](https://img.shields.io/badge/python-3.11-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![Conda](https://img.shields.io/badge/conda-compatible-brightgreen.svg)

## ✨ Features

- 🐍 Automated Conda environment setup with Python 3.11
- 📦 Pre-configured essential data science packages
- 🛠️ VSCode setup with recommended extensions
- 🔧 Development tools (black, pylint, flake8)
- 📊 Jupyter notebook configuration
- 🎯 Type checking and code quality tools

## 🚀 Quick Start

1. **Clone the repository**
   ```bash
   git clone <your-repo-url>
   cd dsi-config
   ```

2. **Run the setup script**
   ```bash
   python setup_project.py [env_name] [python_version]
   ```
   - `env_name`: Optional. Default is "ds_env"
   - `python_version`: Optional. Default is "3.11"

3. **Activate the environment**
   ```bash
   conda activate ds_env
   ```

## 📦 Included Packages

### Core Data Science
- numpy >= 1.24.0
- pandas >= 2.0.0
- matplotlib >= 3.7.0
- scikit-learn >= 1.3.0
- seaborn >= 0.12.0

### Development Tools
- black >= 23.0.0
- pylint >= 2.17.0
- flake8 >= 6.0.0
- pytest >= 7.0.0

## 🛠️ VSCode Configuration

The setup includes:
- Python and Jupyter extensions
- Code formatting with Black
- Linting with Pylint and Flake8
- Type checking with mypy
- Git integration
- Intelligent code completion

## 📋 Requirements

- Conda package manager
- VSCode
- Git

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- The Python Data Science Community
- VSCode Team for their amazing extensions
- All contributors who help improve this project 