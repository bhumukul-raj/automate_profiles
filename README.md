<div align="center">

# 🤖 Automation Profiles

A collection of automation scripts to streamline development workflows and system management.

[![Python](https://img.shields.io/badge/python-3.11-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](https://opensource.org/licenses/MIT)
[![Automation](https://img.shields.io/badge/Automation-Scripts-orange)](https://github.com/bhumukul-raj/automate_profiles)

</div>

---

## 🎯 Overview

This repository contains a collection of automation tools and scripts designed to enhance development workflows and system management. Each project focuses on specific aspects of automation to improve productivity and maintain consistency across development environments.

## 🚀 Projects

### 1. [Data Science Environment Automation](./dsi-config/)

A comprehensive automation tool that sets up a complete data science development environment with portable VSCode and essential extensions.

**Key Features:**
- 📁 Standardized data science project structure
- 💻 Portable VSCode installation with data science extensions
- 🐍 Conda environment with Python 3.11
- 🔧 Pre-configured development tools (Black, isort, Pylint)
- 📓 Jupyter notebook environment with integrated kernels
- 🎯 Automated dependency management
- 🔒 Isolated and reproducible environments

[➡️ Learn More](./dsi-config/README.md)

### 2. [Cursor IDE Configuration Tools](./cursor-sh_ide/)

A toolkit for managing Cursor IDE configurations, focusing on device ID modification and configuration management.

**Key Features:**
- 🔄 Device ID modification and configuration reset
- 🔐 Telemetry and machine ID management
- 💾 Automatic configuration backups
- 👤 Smart user detection and permissions
- ⚙️ Process management
- 🔄 Update control features

[➡️ Learn More](./cursor-sh_ide/README.md)

## 💻 Requirements

### System Requirements:
- Linux Operating System (x86_64 or ARM64)
- Python 3.11+
- Conda package manager
- Git
- Internet connection

### Project-Specific Requirements:
- Cursor IDE v0.45.x+ (for Cursor IDE tools)
- Appropriate system permissions
- Project-specific dependencies listed in each directory

## 🛠️ Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/bhumukul-raj/automate_profiles.git
   cd automate_profiles
   ```

2. **Choose a project:**
   ```bash
   # For Data Science Environment
   cd dsi-config
   python ds-init-project.py

   # For Cursor IDE Tools
   cd cursor-sh_ide
   chmod +x cursor_linux_id_modifier.sh
   ```

## 📚 Documentation

Each project includes detailed documentation:

- **Data Science Environment:**
  - Complete setup instructions
  - Project structure overview
  - Extension configurations
  - Troubleshooting guide

- **Cursor IDE Tools:**
  - Configuration management
  - Security considerations
  - Usage examples
  - Error handling

## 🤝 Contributing

We welcome contributions! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Contribution Guidelines:
- Follow project-specific coding standards
- Add appropriate documentation
- Include tests where applicable
- Update relevant README files

## 🔒 Security

- Automatic configuration backups
- Secure permission handling
- Process verification
- Configuration validation
- Isolated environments

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

For issues or questions:
1. Check project-specific documentation
2. Review troubleshooting guides
3. Open an issue on GitHub with:
   - Detailed system information
   - Error messages
   - Steps to reproduce

---

<div align="center">

Made with ❤️ by [bhumukul-raj](https://github.com/bhumukul-raj)

⭐ Star this repository if you find these scripts helpful!

</div>