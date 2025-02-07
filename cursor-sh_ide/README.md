<div align="center">

# 🔄 Cursor IDE Reset Tool

<p align="center">
  <img src="https://img.shields.io/badge/python-3.6+-blue.svg" alt="Python Version"/>
  <img src="https://img.shields.io/badge/platform-linux-lightgrey.svg" alt="Platform"/>
  <img src="https://img.shields.io/badge/license-MIT-green.svg" alt="License"/>
  <img src="https://img.shields.io/badge/cursor-v0.44.11-orange.svg" alt="Cursor"/>
</p>

<p align="center">
  A powerful tool to reset and reconfigure Cursor IDE settings, with built-in testing capabilities for Linux systems.
</p>

<p align="center">
  <a href="#overview">Overview</a> •
  <a href="#features">Features</a> •
  <a href="#installation">Installation</a> •
  <a href="#usage">Usage</a> •
  <a href="#components">Components</a> •
  <a href="#configuration">Configuration</a> •
  <a href="#troubleshooting">Troubleshooting</a>
</p>

</div>

---

<a id="overview"></a>
## 📖 Overview

<div align="center">
  <table>
    <tr>
      <td>
        This tool is part of the <a href="https://github.com/bhumukul-raj/automate_profiles.git">automate_profiles</a> collection, designed to help manage and reset Cursor IDE configurations efficiently and safely.
      </td>
    </tr>
  </table>
</div>

<a id="features"></a>
## ✨ Features

<div align="center">
  <table>
    <tr>
      <td>🔄</td>
      <td>Complete Cursor IDE configuration reset</td>
    </tr>
    <tr>
      <td>🔐</td>
      <td>Custom telemetry and machine ID configuration</td>
    </tr>
    <tr>
      <td>📦</td>
      <td>Automatic backup of existing settings</td>
    </tr>
    <tr>
      <td>👤</td>
      <td>Smart user detection (works with sudo)</td>
    </tr>
    <tr>
      <td>🛡️</td>
      <td>Secure permission handling</td>
    </tr>
    <tr>
      <td>🧪</td>
      <td>Optional test environment for safe validation</td>
    </tr>
  </table>
</div>

<a id="installation"></a>
## 🚀 Installation

<div >

```bash
# Clone the repository
git clone https://github.com/bhumukul-raj/automate_profiles.git
cd automate_profiles/cursor-sh_ide

# Run the configuration
python3 cursor_reset.py
```

</div>

<a id="components"></a>
## 🛠️ Components

<details>
<summary><b>1. Reset Tool (cursor_reset.py)</b></summary>

- Primary configuration management tool
- Handles configuration reset and modifications
- Creates automatic backups
- Updates telemetry settings

</details>

<details>
<summary><b>2. Test Tool (cursor_test.py)</b></summary>

- Safe testing environment
- Validates operations before actual execution
- Verifies permissions and access
- Ensures data integrity

</details>

<a id="requirements"></a>
## 📋 Requirements

<div align="center">
  <table>
    <tr>
      <th>Requirement</th>
      <th>Version/Details</th>
    </tr>
    <tr>
      <td>Python</td>
      <td>3.6 or higher</td>
    </tr>
    <tr>
      <td>Operating System</td>
      <td>Linux</td>
    </tr>
    <tr>
      <td>Cursor IDE</td>
      <td>v0.44.11</td>
    </tr>
    <tr>
      <td>Permissions</td>
      <td>User with appropriate access</td>
    </tr>
  </table>
</div>

<a id="configuration"></a>
## 🔧 Configuration

<details>
<summary><b>Key Settings</b></summary>

```python
MERCYHACKS_KEY = "1fc0a7b0-c0bd-4d4a-a841-a95841d8e94f"
```

</details>

<details>
<summary><b>File Locations</b></summary>

- `~/.config/Cursor/` - Main configuration directory
- `~/.cursor/` - Additional settings
- `~/.config/cursor-updater/` - Updater configuration

</details>

<a id="usage"></a>
## 📘 Usage

### Basic Commands

```bash
# 1. Test Environment (Recommended First Step)
python3 cursor_test.py

# 2. Reset Configuration
python3 cursor_reset.py

# 3. If Permission Issues Occur
sudo python3 cursor_reset.py
```

### Detailed Operations

<div align="center">
  <table>
    <tr>
      <th width="200">Operation</th>
      <th width="300">Description</th>
      <th width="200">Notes</th>
    </tr>
    <tr>
      <td><b>Test Environment</b></td>
      <td>Validates all operations in a safe environment</td>
      <td>Recommended first step</td>
    </tr>
    <tr>
      <td><b>Reset Configuration</b></td>
      <td>Resets and configures Cursor IDE settings</td>
      <td>Close Cursor IDE first</td>
    </tr>
    <tr>
      <td><b>Modify Settings</b></td>
      <td>Updates telemetry and machine IDs</td>
      <td>Automatic backup created</td>
    </tr>
  </table>
</div>

### Interactive Menu Options

When running `cursor_reset.py`, you'll see these options:

1. **Remove Configuration**
   ```
   Option 1: Remove all configuration files and uninstall Cursor
   ```

2. **Modify Settings**
   ```
   Option 2: Modify configuration settings (update storage.json)
   ```

<a id="workflow"></a>
## 📊 Operations Flow

<div align="center">
  <table>
    <tr>
      <th>Stage</th>
      <th>Operations</th>
    </tr>
    <tr>
      <td><b>1. Preparation</b></td>
      <td>
        • Backup current configuration<br>
        • Verify Cursor is not running<br>
        • Check permissions
      </td>
    </tr>
    <tr>
      <td><b>2. Reset Process</b></td>
      <td>
        • Remove existing configuration<br>
        • Apply fresh settings<br>
        • Configure telemetry IDs
      </td>
    </tr>
    <tr>
      <td><b>3. Validation</b></td>
      <td>
        • Test environment setup<br>
        • Configuration verification<br>
        • Permission checks
      </td>
    </tr>
  </table>
</div>

<a id="important"></a>
## ⚠️ Important Notes

<div align="center">
  <table>
    <tr>
      <td>⚠️</td>
      <td><b>ALWAYS BACKUP YOUR WORK</b> before running the reset tool</td>
    </tr>
    <tr>
      <td>🛑</td>
      <td>Close Cursor IDE completely before using</td>
    </tr>
    <tr>
      <td>👤</td>
      <td>Run without sudo first; use sudo only if necessary</td>
    </tr>
    <tr>
      <td>✅</td>
      <td>Verify your Cursor version matches v0.44.11</td>
    </tr>
  </table>
</div>

<a id="troubleshooting"></a>
## 🔍 Troubleshooting

<details>
<summary><b>Permission Denied</b></summary>

```bash
# Try running with sudo
sudo python3 cursor_reset.py
```

</details>

<details>
<summary><b>Cursor Still Running</b></summary>

```bash
# Check for running instances
pgrep cursor
# Kill if necessary
pkill cursor
```

</details>

<details>
<summary><b>Backup Failed</b></summary>

- Ensure sufficient disk space
- Check directory permissions
- Verify user permissions

</details>

<a id="contributing"></a>
## 🤝 Contributing

<div align="center">
  <table>
    <tr>
      <td>1. Fork the <a href="https://github.com/bhumukul-raj/automate_profiles.git">repository</a></td>
    </tr>
    <tr>
      <td>2. Create your feature branch (`git checkout -b feature/amazing-feature`)</td>
    </tr>
    <tr>
      <td>3. Commit your changes (`git commit -m 'Add some amazing feature'`)</td>
    </tr>
    <tr>
      <td>4. Push to the branch (`git push origin feature/amazing-feature`)</td>
    </tr>
    <tr>
      <td>5. Open a Pull Request</td>
    </tr>
  </table>
</div>

<a id="license"></a>
## 📝 License

<div align="center">
  This project is licensed under the MIT License - see the <a href="LICENSE">LICENSE</a> file for details.
</div>

<a id="acknowledgments"></a>
## 🙏 Acknowledgments

<div align="center">
  <table>
    <tr>
      <td>Cursor IDE Development Team</td>
    </tr>
    <tr>
      <td>Python Community</td>
    </tr>
    <tr>
      <td>All contributors to this project</td>
    </tr>
  </table>
</div>

<a id="security"></a>
## 🔒 Security Notice

<div align="center">
  <table>
    <tr>
      <td>📋</td>
      <td>Review the code before running</td>
    </tr>
    <tr>
      <td>💾</td>
      <td>Backup your data</td>
    </tr>
    <tr>
      <td>🔄</td>
      <td>Use official releases</td>
    </tr>
    <tr>
      <td>🔔</td>
      <td>Report security issues</td>
    </tr>
  </table>
</div>

<a id="support"></a>
## 📞 Support

<div align="center">
  <table>
    <tr>
      <td>Open an issue on <a href="https://github.com/bhumukul-raj/automate_profiles/issues">GitHub</a></td>
    </tr>
    <tr>
      <td>Provide system information</td>
    </tr>
    <tr>
      <td>Include error messages</td>
    </tr>
    <tr>
      <td>Describe steps to reproduce</td>
    </tr>
  </table>
</div>

---

<div align="center">
  Made with ❤️ by <a href="https://github.com/bhumukul-raj">bhumukul-raj</a>
</div>

<a id="back-to-top"></a>
<div align="center">
  <p>
    <a href="#top">Back to Top ⬆️</a>
  </p>
</div>

---

<div align="center">
  Made with ❤️ by <a href="https://github.com/bhumukul-raj">bhumukul-raj</a>
</div> 