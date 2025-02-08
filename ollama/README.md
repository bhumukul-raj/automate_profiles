# 🚀 Ollama Setup and Management Tools

A collection of Python scripts for installing, managing, and monitoring Ollama on Linux systems.

## 📋 Core Components

### 1. Installation Scripts

#### `setup_ollama.py`
Main installation script with two installation options:
- **Default Installation**: Standard installation in `~/.ollama`
  ```bash
  python3 setup_ollama.py
  # Choose option 1 for default installation
  ```
- **Custom Installation**: Configurable installation with options for:
  - Binary location (`/usr/local/bin/ollama`, `~/.local/bin/ollama`, or custom)
  - Data directory (under `~/.ollama`)
  - GPU support (NVIDIA/AMD)
  - Service configuration
  ```bash
  python3 setup_ollama.py
  # Choose option 2 for custom installation
  ```

#### `setup_env.py`
Sets up Python environment using Conda:
```bash
python3 setup_env.py
# Creates conda environment 'env_ollama' with required packages
```

### 2. Management Tools

#### `ollama_service_manager.py`
Comprehensive service management tool:
```bash
# Start Ollama service
python3 ollama_service_manager.py start

# Stop Ollama service
python3 ollama_service_manager.py stop

# Check service status
python3 ollama_service_manager.py status

# Monitor resources
python3 ollama_service_manager.py monitor
```

Features:
- Service control (start/stop)
- Resource monitoring (CPU, Memory, GPU)
- Temperature monitoring
- Battery management
- Automatic alerts

#### `uninstall_ollama.py`
Complete removal tool:
```bash
python3 uninstall_ollama.py
# Removes all Ollama files and configurations
```

## 🔧 Installation Guide

1. **Clone Repository**:
   ```bash
   git clone https://github.com/bhumukul-raj/automate_profiles.git
   cd ollama
   ```

2. **Setup Environment**:
   ```bash
   python3 setup_env.py
   conda activate env_ollama
   ```

3. **Install Ollama**:
   ```bash
   python3 setup_ollama.py
   ```
   
   Choose installation type:
   - Option 1: Default Installation
     - Installs in `~/.ollama`
     - Creates standard directory structure:
       ```
       ~/.ollama/
       ├── models/     # AI models storage
       └── config/     # Configuration files
       ```
   
   - Option 2: Custom Installation
     - Configure:
       - Binary location
       - Data directory (subdirectory under ~/.ollama)
       - GPU support
       - Service settings

## 📊 Resource Management

### Monitor System Resources
```bash
python3 ollama_service_manager.py monitor --interval 30
```

Monitors:
- CPU usage and temperature
- Memory utilization
- GPU status (if available)
- Battery level
- System temperature

### Service Control
```bash
# Start service
python3 ollama_service_manager.py start

# Stop service
python3 ollama_service_manager.py stop

# Check status
python3 ollama_service_manager.py status
```

## 🗑️ Uninstallation

Remove Ollama completely:
```bash
python3 uninstall_ollama.py
```

Removes:
- Binary files
- Data directory
- Configuration files
- Service files
- Log files

## 📝 Configuration

### Resource Thresholds
Create `~/.ollama/resource_config.json`:
```json
{
    "cpu_percent_warning": 80.0,
    "memory_percent_warning": 80.0,
    "gpu_memory_percent_warning": 80.0,
    "temperature_warning_celsius": 80.0,
    "battery_minimum_percent": 20.0
}
```

## 🔍 Troubleshooting

### Common Issues

1. **Installation Fails**:
   ```bash
   # Run with sudo for system-wide installation
   sudo python3 setup_ollama.py
   ```

2. **Service Won't Start**:
   ```bash
   # Check service status
   python3 ollama_service_manager.py status
   
   # Check system logs
   journalctl -u ollama
   ```

3. **Permission Issues**:
   ```bash
   # Fix permissions
   sudo chown -R $USER:$USER ~/.ollama
   ```

## 📦 Requirements

- Python 3.7+
- Required packages:
  ```
  psutil==5.9.5
  tqdm==4.65.0
  requests==2.31.0
  colorama>=0.4.6
  typing-extensions>=4.7.1
  aiohttp>=3.8.0
  ```

## 🔒 Security Notes

- Binary installations may require sudo privileges
- Service files are created with appropriate permissions
- Data directory is owned by the user
- No sensitive data is stored in plain text

## 📚 Logging

- Installation logs: `~/ollama_setup.log`
- Uninstall logs: `~/ollama_uninstall.log`
- Service logs: System journal

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Submit a pull request

## 📄 License

MIT License - See LICENSE file for details 