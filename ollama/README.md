# 🚀 Ollama Setup and Management Tools

<div align="center">

![Ollama Logo](https://raw.githubusercontent.com/ollama/ollama/main/docs/ollama.png)

[![Python Version](https://img.shields.io/badge/python-3.7%2B-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Platform](https://img.shields.io/badge/platform-linux-lightgrey.svg)](https://www.linux.org/)

*A powerful toolkit for managing Ollama installations on Linux systems with automated setup, backup, and cleanup capabilities.*

[Key Features](#key-features) •
[Installation](#installation) •
[Usage](#usage) •
[Configuration](#configuration) •
[Contributing](#contributing)

</div>

---

## 📋 Key Features

### 🔧 Setup Script (`setup_ollama.py`)
- 🚀 Multiple installation modes:
  - Full Installation (with models)
  - Minimal Installation (no models)
  - Custom Installation (configurable)
- 🎮 Automatic GPU detection (NVIDIA/AMD)
- 💾 Smart disk space management
- 📦 Dependency handling
- 🔄 Version management and updates
- 🛠️ Service configuration

### 🗑️ Uninstall Script (`uninstall_ollama.py`)
- 🧹 Complete system cleanup
- 💾 Automatic backup creation
- 🎛️ Configurable removal options
- 🐳 Docker image cleanup
- 🔍 Thorough file scanning

### 🛠️ Utility Module (`ollama_utils.py`)
- 📊 System compatibility checks
- 📦 Package management
- 📝 Logging system
- 🔧 Service management

### 🔄 Service Manager (`ollama_service_manager.py`)
- 💻 Start/stop Ollama services
- 📊 Monitor resource usage (CPU, Memory, GPU)
- 🌡️ Temperature monitoring (CPU/GPU)
- 🔋 Battery-aware management
- 🚨 Resource usage alerts
- 🔍 Process management
- 🔄 Service status checking

## 🔧 Requirements

- Python 3.7 or higher
- Linux-based operating system (Debian/Ubuntu recommended)
- Internet connection
- Sudo privileges

## 📥 Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/bhumukul-raj/automate_profiles.git
   cd ollama
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## 🚀 Usage

### Setting up Ollama

```bash
python3 setup_ollama.py
```

The setup script offers three installation modes:

1. **Full Installation**
   - Includes default models
   - Automatic GPU support
   - Service auto-start
   - Default installation path

2. **Minimal Installation**
   - Core Ollama system only
   - No AI models included
   - Smallest disk space usage
   - Fastest installation

3. **Custom Installation**
   - Choose specific models
   - Configure GPU support
   - Set custom installation path
   - Control service auto-start

#### Available Models
- `llama2` - Meta's Llama 2 model
- `mistral` - Mistral 7B model
- `codellama` - Code specialized Llama model

#### Installation Examples

1. Minimal Installation:
   ```bash
   # Choose option 2 during setup
   python3 setup_ollama.py
   ```

2. Custom Installation with Specific Models:
   ```bash
   # Choose option 3 during setup
   # Select models when prompted
   python3 setup_ollama.py
   ```

### Uninstalling Ollama

```bash
python3 uninstall_ollama.py
```

The uninstall script provides:
1. Backup option for models
2. Configurable cleanup
3. Docker image removal
4. Complete system cleanup

### Managing Ollama Services

The service manager helps you control Ollama processes and monitor resource usage:

```bash
# Start Ollama services
python3 ollama_service_manager.py start

# Stop all Ollama processes
python3 ollama_service_manager.py stop

# Check service status and resource usage
python3 ollama_service_manager.py status

# Continuously monitor resources with alerts
python3 ollama_service_manager.py monitor --interval 30
```

#### Resource Management Features

1. **Automatic Resource Monitoring**
   - CPU usage and temperature
   - Memory utilization
   - GPU memory and temperature
   - Battery level and time remaining
   - Power consumption tracking

2. **Smart Resource Management**
   - Automatic shutdown on low battery
   - Temperature-based throttling
   - Resource usage warnings
   - Configurable thresholds

3. **Battery Protection**
   - Low battery warnings
   - Automatic service stop on critical battery
   - Charging status monitoring
   - Remaining time estimation

4. **Temperature Management**
   - CPU temperature monitoring
   - GPU temperature tracking
   - Thermal throttling protection
   - Configurable temperature limits

5. **Resource Usage Alerts**
   - High CPU usage warnings
   - Memory utilization alerts
   - GPU memory warnings
   - Temperature threshold alerts

#### Configuration

You can customize resource thresholds by creating `~/.ollama/resource_config.json`:

```json
{
    "cpu_percent_warning": 80.0,
    "memory_percent_warning": 80.0,
    "gpu_memory_percent_warning": 80.0,
    "temperature_warning_celsius": 80.0,
    "battery_minimum_percent": 20.0
}
```

## ⚙️ Configuration

### Installation Options
- Custom installation path
- GPU support configuration
- Service management options

### Uninstallation Options
- Backup creation (optional)
- Selective component removal
- Compression level for backups
- Docker cleanup options

## 📝 Logging

Logs are stored in your home directory:
- Setup: `~/ollama_setup.log`
- Uninstall: `~/ollama_uninstall.log`

Log format includes:
- Timestamp
- Log level
- Detailed messages
- Error tracing

## 🔒 Security

- Secure handling of sudo operations
- No hardcoded credentials
- Safe backup management
- Proper file permissions

## 🛠️ Development

### Project Structure
```
ollama/
├── setup_ollama.py      # Installation script
├── uninstall_ollama.py  # Removal script
├── ollama_utils.py      # Shared utilities
├── requirements.txt     # Dependencies
└── README.md           # Documentation
```

### Code Style
- PEP 8 compliant
- Type hints
- Comprehensive docstrings
- Clear error handling

## 🐛 Troubleshooting

### Common Issues

1. Permission Errors
   ```bash
   sudo python3 setup_ollama.py
   ```

2. Missing Dependencies
   ```bash
   pip install -r requirements.txt
   ```

3. Service Issues
   ```bash
   systemctl status ollama
   journalctl -u ollama
   ```

### Error Codes

| Code | Description | Solution |
|------|-------------|----------|
| E001 | Permission denied | Run with sudo |
| E002 | Disk space low | Free up space |
| E003 | Network error | Check connection |

## 🤝 Contributing

We welcome contributions! Please follow these steps:

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

### Guidelines
- Follow PEP 8 style guide
- Add tests for new features
- Update documentation
- Use clear commit messages

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [Ollama Project](https://ollama.ai)
- All contributors
- Open source community

## 📞 Support

- Create an issue for bug reports
- Join our community discussions
- Check the [Wiki](../../wiki) for guides

## 💡 Tips and Best Practices

### Choosing Installation Mode

1. **Full Installation**
   - Best for: General users who want immediate access to models
   - Requires: ~15GB disk space
   - Includes: All basic models

2. **Minimal Installation**
   - Best for: Development/testing environments
   - Requires: ~500MB disk space
   - Includes: Core system only

3. **Custom Installation**
   - Best for: Advanced users with specific needs
   - Disk space: Varies with selected models
   - Fully configurable setup

### Model Management

- Install models later: `ollama pull model_name`
- Remove models: `ollama rm model_name`
- List models: `ollama list`
- Update models: `ollama pull model_name`

### Performance Optimization

1. **GPU Setup**
   - NVIDIA: Install CUDA drivers
   - AMD: Install ROCm drivers
   - Check GPU status: `nvidia-smi` or `rocm-smi`

2. **Memory Management**
   - Minimum RAM: 8GB
   - Recommended: 16GB+
   - GPU Memory: 8GB+ for optimal performance

3. **Disk Space**
   - Keep 20% free space
   - Use SSD for better performance
   - Monitor usage: `du -sh ~/.ollama`

---

<div align="center">
Made with ❤️ by [Your Name/Organization]

⭐ Star us on GitHub — it motivates us a lot!
</div> 