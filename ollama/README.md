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

### 2. Service Management

#### `ollama_service_manager.py`
Comprehensive service management tool with advanced features:

1. **Starting the Service**:
   ```bash
   # Start with default (normal) priority
   python3 ollama_service_manager.py start

   # Start with specific priority
   python3 ollama_service_manager.py start --priority high
   python3 ollama_service_manager.py start --priority low
   ```

2. **Stopping the Service**:
   ```bash
   python3 ollama_service_manager.py stop
   ```

3. **Checking Status**:
   ```bash
   # Regular status output
   python3 ollama_service_manager.py status

   # JSON format output (for scripting)
   python3 ollama_service_manager.py status --json
   ```

4. **Resource Monitoring**:
   ```bash
   # Monitor with default interval (60 seconds)
   python3 ollama_service_manager.py monitor

   # Custom monitoring interval
   python3 ollama_service_manager.py monitor --interval 30

   # Monitor with log file
   python3 ollama_service_manager.py monitor --log-file ~/ollama_monitor.log
   ```

#### Features:

1. **Process Management**:
   - Priority control (high/normal/low)
   - Automatic process detection
   - Graceful shutdown
   - Service state persistence

2. **Resource Monitoring**:
   - CPU usage and temperature
   - Memory utilization
   - GPU status and memory
   - Network bandwidth
   - Disk usage
   - Battery status (for laptops)

3. **Automatic Optimization**:
   - Battery-aware performance adjustment
   - Dynamic CPU core allocation
   - Memory usage optimization
   - GPU resource management

4. **Warning System**:
   ```json
   # Configure warning thresholds in ~/.ollama/resource_config.json
   {
       "cpu_percent_warning": 80.0,
       "memory_percent_warning": 80.0,
       "gpu_memory_percent_warning": 80.0,
       "temperature_warning_celsius": 80.0,
       "battery_minimum_percent": 20.0,
       "network_warning_mbps": 100.0,
       "disk_usage_warning": 90.0
   }
   ```

5. **Status Information**:
   - Process details (PID, CPU, Memory)
   - Resource utilization
   - GPU information (if available)
   - System temperature
   - Battery status
   - Network usage
   - Disk usage

#### Common Use Cases:

1. **Development Environment**:
   ```bash
   # Start with high priority
   python3 ollama_service_manager.py start --priority high
   ```

2. **Server Deployment**:
   ```bash
   # Start service and monitor with logging
   python3 ollama_service_manager.py start
   python3 ollama_service_manager.py monitor --log-file /var/log/ollama_monitor.log
   ```

3. **Laptop Usage**:
   ```bash
   # Start with battery optimization
   python3 ollama_service_manager.py start --priority low
   python3 ollama_service_manager.py monitor --interval 30
   ```

4. **System Integration**:
   ```bash
   # Get status in JSON format for integration
   python3 ollama_service_manager.py status --json
   ```

#### Automatic Actions:

The service manager automatically:
- Adjusts process priority based on system load
- Optimizes for battery life on laptops
- Manages GPU resources efficiently
- Handles process cleanup on shutdown
- Monitors and warns about resource usage
- Stops service if resources are critical

#### Monitoring Output Example:
```
=== Ollama Status Report ===
Status: Running
Timestamp: 2024-01-20T14:30:45

Process Information:
- Number of processes: 1
- CPU Usage: 25.5%
- Memory Usage: 1024.5 MB
- Network Upload: 0.5 Mbps
- Network Download: 1.2 Mbps
- Disk Usage: 45.2%

GPU Information:
- GPU: NVIDIA GeForce RTX 3080
- Memory Used: 2048 MB
- Memory Total: 10240 MB
- Utilization: 30%
- Temperature: 65°C
- Power Usage: 120W

System Temperature:
- CPU: 55.5°C

Battery Status:
- Level: 75.5%
- Charging: Yes
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

## 📝 Configuration

### Resource Thresholds
Create `~/.ollama/resource_config.json`:
```json
{
    "cpu_percent_warning": 80.0,
    "memory_percent_warning": 80.0,
    "gpu_memory_percent_warning": 80.0,
    "temperature_warning_celsius": 80.0,
    "battery_minimum_percent": 20.0,
    "network_warning_mbps": 100.0,
    "disk_usage_warning": 90.0
}
```

## 🔍 Troubleshooting

1. **Service Won't Start**:
   ```bash
   # Check service status
   python3 ollama_service_manager.py status
   # Check system logs
   sudo journalctl -u ollama
   ```

2. **High Resource Usage**:
   ```bash
   # Monitor resources
   python3 ollama_service_manager.py monitor
   # Start with lower priority
   python3 ollama_service_manager.py start --priority low
   ```

3. **GPU Issues**:
   ```bash
   # Check GPU status
   python3 ollama_service_manager.py status
   # Start without GPU
   python3 ollama_service_manager.py start --priority normal
   ```

## 📚 Logging

- Service logs: `~/.ollama/service.log`
- Monitor logs: Specified by `--log-file`
- System journal: `journalctl -u ollama`

## 🔒 Security Notes

- Service manager requires appropriate permissions
- Resource monitoring is non-intrusive
- Process management respects system limits
- Configuration files use secure permissions

## 📄 License

MIT License - See LICENSE file for details 