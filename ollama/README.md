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
  - GPU/CPU mode selection
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
   sudo python3 setup_ollama.py
   ```

   Choose installation type:
   - Option 1: Default Installation
     - Installs in `~/.ollama`
     - Uses default settings
     - Automatic hardware detection
   
   - Option 2: Custom Installation
     - Configure:
       ```
       1. Binary Location:
          - System-wide (/usr/local/bin/ollama)
          - User's bin (~/.local/bin/ollama)
          - Custom location

       2. Data Directory:
          - Default (~/.ollama)
          - Custom subdirectory

       3. Processing Mode:
          - CPU Only (Works on all systems)
          - GPU Mode (If hardware available)
          Note: GPU mode will:
          - Use GPU for supported operations
          - Fall back to CPU when needed
          - Auto-manage resources

       4. Service Configuration:
          - System service (auto-start)
          - Manual start
       ```

## 📊 Usage Guide

### Starting Ollama

1. **If installed as a service**:
   ```bash
   # Check service status
   systemctl status ollama
   
   # Start service if needed
   sudo systemctl start ollama
   ```

2. **Manual start**:
   ```bash
   # Start in background
   ~/.local/bin/ollama serve &
   
   # Or in a new terminal
   ~/.local/bin/ollama serve
   ```

### Basic Commands

```bash
# List available models
ollama list

# Pull a model
ollama pull llama2

# Run a model
ollama run llama2

# Get model information
ollama show llama2

# Remove a model
ollama rm llama2
```

### Popular Models

1. **llama2**
   ```bash
   ollama pull llama2
   ollama run llama2
   # General purpose model, good for most tasks
   ```

2. **codellama**
   ```bash
   ollama pull codellama
   ollama run codellama
   # Specialized for code generation and analysis
   ```

3. **mistral**
   ```bash
   ollama pull mistral
   ollama run mistral
   # Fast and efficient model
   ```

4. **dolphin**
   ```bash
   ollama pull dolphin
   ollama run dolphin
   # Helpful assistant model
   ```

### GPU vs CPU Mode

1. **CPU Mode**:
   - Works on all systems
   - Lower memory requirements
   - Suitable for basic usage
   - More predictable performance

2. **GPU Mode** (NVIDIA/AMD):
   - Faster processing
   - Higher memory requirements
   - Automatic resource management
   - Features:
     - GPU acceleration for supported operations
     - CPU fallback when needed
     - Dynamic resource allocation

### Resource Management

Monitor system resources:
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
sudo python3 uninstall_ollama.py
```

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

1. **Installation Issues**:
   ```bash
   # Run with sudo
   sudo python3 setup_ollama.py
   ```

2. **Permission Problems**:
   ```bash
   # Fix ownership
   sudo chown -R $USER:$USER ~/.ollama
   ```

3. **Service Issues**:
   ```bash
   # Check service status
   systemctl status ollama
   # View logs
   journalctl -u ollama
   ```

4. **GPU Problems**:
   ```bash
   # Check GPU status
   nvidia-smi  # For NVIDIA
   rocm-smi    # For AMD
   ```

## 📚 Logging

- Installation: `~/ollama_setup.log`
- Uninstall: `~/ollama_uninstall.log`
- Service: System journal

## 🔒 Security Notes

- Binary installations may require sudo
- Service files have appropriate permissions
- Data directory owned by user
- No sensitive data stored in plain text

## 📄 License

MIT License - See LICENSE file for details 