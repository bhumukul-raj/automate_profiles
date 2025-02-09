# Cursor IDE Configuration Tools

![Python Version](https://img.shields.io/badge/python-3.6+-blue.svg)
![Bash Version](https://img.shields.io/badge/bash-4.0+-yellow.svg)
![Platform](https://img.shields.io/badge/platform-linux-lightgrey.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![Cursor](https://img.shields.io/badge/cursor-v0.45.x-orange.svg)

A comprehensive toolkit for managing Cursor IDE configurations on Linux systems, including device ID modification and configuration reset capabilities.

## Table of Contents
- [Overview](#overview)
- [Features](#features)
- [Installation](#installation)
- [Components](#components)
- [Usage](#usage)
- [Configuration](#configuration)
- [Important Notes](#important-notes)
- [Troubleshooting](#troubleshooting)
- [Security](#security)
- [Support](#support)

## Overview

This toolkit provides two main utilities for managing Cursor IDE configurations:

1. **Device ID Modifier** (`cursor_linux_id_modifier.sh`): A bash script for modifying Cursor IDE device identifiers and telemetry settings.
2. **Configuration Reset Tool** (`cursor_reset.py`): A Python utility for resetting and managing Cursor IDE configurations.

## Features

- Complete device ID modification and configuration reset
- Secure telemetry and machine ID management
- Automatic backup of existing configurations
- Smart user detection and permission handling
- Process management (auto-close Cursor IDE)
- Optional auto-update disabling feature

## Installation

```bash
# Clone the repository
git clone https://github.com/bhumukul-raj/automate_profiles.git
cd automate_profiles/cursor-sh_ide

# Set execute permissions
chmod +x cursor_linux_id_modifier.sh

# For Python script
python3 cursor_reset.py
```

## Components

### 1. Device ID Modifier (cursor_linux_id_modifier.sh)
- Modifies Cursor IDE device identifiers
- Manages telemetry settings
- Creates automatic backups
- Optional auto-update disable feature
- Process management for Cursor IDE

### 2. Reset Tool (cursor_reset.py)
- Complete configuration reset
- Custom telemetry configuration
- Backup functionality
- Configuration modification options

## Usage

### Device ID Modifier

```bash
# Run with sudo (required)
sudo ./cursor_linux_id_modifier.sh
```

Features:
- Automatic backup creation
- Smart process management
- Device ID modification
- Auto-update control
- Permission handling

### Reset Tool

```bash
# Run normally first
python3 cursor_reset.py

# If permission issues occur
sudo python3 cursor_reset.py
```

Options:
1. Remove all configuration files
2. Modify configuration settings

## Configuration Files

Important paths managed by these tools:

```
~/.config/Cursor/User/globalStorage/storage.json
~/.config/cursor-updater
~/.cursor/
```

## Important Notes

- **ALWAYS BACKUP** before using these tools
- Close Cursor IDE before running any tool
- Device ID Modifier requires sudo
- Compatible with Cursor v0.45.x

## Troubleshooting

### Permission Issues
```bash
# For Device ID Modifier
sudo ./cursor_linux_id_modifier.sh

# For Reset Tool
sudo python3 cursor_reset.py
```

### Cursor Process Issues
```bash
# Check for running instances
ps aux | grep -E "/[C]ursor|[C]ursor$"

# Kill if necessary
pkill -f Cursor
```

### Configuration Backup
- Check disk space
- Verify directory permissions
- Ensure correct user permissions

## Security

- Both tools create automatic backups
- Secure permission handling
- Process verification
- Configuration validation

## Support

For issues or questions:
1. Check the troubleshooting section
2. Open an issue on GitHub
3. Provide detailed system information
4. Include error messages

---

Made with ❤️ by [bhumukul-raj](https://github.com/bhumukul-raj) 