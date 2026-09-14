# Ludus LitterBox

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

A Ludus role for deploying [LitterBox](https://github.com/BlackSnufkin/LitterBox) - a comprehensive malware analysis sandbox - on Windows systems within Ludus lab environments.

## Overview

LitterBox provides a controlled sandbox environment designed for security professionals to analyze malware and test security tools. This Ludus role automates the deployment and configuration of LitterBox on Windows VMs, providing:

- **Static and Dynamic Analysis**: Comprehensive malware behavior analysis
- **Multiple Analysis Engines**: YARA, PE analysis, memory inspection, and more
- **Isolated Testing Environment**: Safe execution and analysis of suspicious files
- **Web-Based Interface**: Easy-to-use UI running on port 1337
- **API Integration**: GrumpyCats client library for automation

## Security Notice

**CRITICAL**: This tool is designed for isolated lab environments only!
- Deploy only in isolated, non-production systems
- Contains functionality to disable Windows Defender
- Handles potentially malicious files
- Never expose to production networks

## Requirements

### Ludus Host Requirements
- Ludus version 1.3.0 or higher
- Ansible 2.10 or higher
- Required Ansible Collections:
  - `ansible.windows` >= 2.0.0
  - `community.windows` >= 2.0.0
  - `chocolatey.chocolatey` >= 1.5.0

### Target VM Requirements
- **OS**: Windows 10/11, Server 2019/2022 (SERVER 2022 RECOMMENED FOR AV DISABLE)
- **RAM**: Minimum 4GB (8GB recommended)
- **Storage**: 10GB free disk space
- **Privileges**: Administrator access required
- **Network**: Internet access for initial setup

## Installation

### Quick Deploy to Ludus Range

```bash

# Add the role to your Ludus server
ludus ansible roles add professor-moody.ludus_litterbox

# Deploy to specific Windows VMs
ludus range deploy -t user-defined-roles --only-roles ludus_litterbox_role --limit "WS01,WS02"

# Or deploy to all Windows VMs
ludus range deploy -t user-defined-roles  --only-roles ludus_litterbox_role --limit windows
```

## Manual Installation

```
# Clone the repository
git clone https://github.com/professor-moody/ludus_litterbox_role
cd ludus_litterbox_role
ludus roles add -d ludus_litterbox_role
```

# Add directly from Ansible Galaxy
```ludus ansible roles add professor-moody.ludus_litterbox```


## Configuration

### Key Variables (defaults/main.yml)

```yaml
# Core Installation Settings
ludus_litterbox_install: true                              # Enable/disable installation
ludus_litterbox_install_dir: "C:\\Tools\\LitterBox"       # Installation directory
ludus_litterbox_python_version: "3.11.9"                  # Python version to install
ludus_litterbox_repo_url: "https://github.com/BlackSnufkin/LitterBox.git"

# Network Configuration
ludus_litterbox_host: "127.0.0.1"                         # Bind address (use 0.0.0.0 for network access)
ludus_litterbox_port: 1337                                # Web interface port

# Security Settings
ludus_litterbox_disable_defender: true                    # Disable Windows Defender (LAB USE ONLY!)
ludus_litterbox_defender_exclusions: true                 # Add AV exclusions
ludus_litterbox_require_admin: true                       # Require admin privileges

# UI/Access Settings
ludus_litterbox_firewall_rule: true                       # Create firewall exception
ludus_litterbox_desktop_shortcut: true                    # Create desktop shortcut

# Analysis Configuration
ludus_litterbox_analysis_timeout: 300                     # Analysis timeout (seconds)
ludus_litterbox_max_file_size: 104857600                 # Max file size (100MB)
ludus_litterbox_allowed_extensions:                       # Supported file types
  - exe, dll, sys, scr, com
  - bat, ps1, vbs, js
  - doc, docx, xls, xlsx, ppt, pptx, pdf, lnk

# Feature Flags
ludus_litterbox_enable_static: true                       # Static analysis
ludus_litterbox_enable_dynamic: true                      # Dynamic analysis
ludus_litterbox_enable_holygrail: true                   # BYOVD detection
ludus_litterbox_enable_doppelganger: true                # Process similarity
ludus_litterbox_enable_yara: true                        # YARA scanning

# System Settings
ludus_litterbox_install_chocolatey: true                  # Install Chocolatey
ludus_litterbox_install_python: true                      # Install Python if missing
ludus_litterbox_debug: false                              # Enable debug logging
```

## Example Playbooks

### Custom Configuration for Network Access

```yaml
---
  vars:
    ludus_litterbox_host: "0.0.0.0"              # Listen on all interfaces
    ludus_litterbox_port: 8080                   # Custom port
    ludus_litterbox_install_dir: "D:\\Security\\LitterBox"
    ludus_litterbox_debug: true                  # Enable debug logging
    ludus_litterbox_analysis_timeout: 600        # 10 minute timeout
```

### Minimal Installation (Keep Defender Active)

```yaml
---
  vars:
    ludus_litterbox_disable_defender: false      # Keep Defender enabled
    ludus_litterbox_defender_exclusions: false   # No AV exclusions
    ludus_litterbox_enable_dynamic: false        # Static analysis only
```

## Elastic Defend Integration

LitterBox supports [Elastic Defend](https://github.com/BlackSnufkin/LitterBox/wiki/Elastic-Defend-Setup) as an EDR backend. This requires three components:

1. **Elastic Stack** (Elasticsearch + Kibana + Fleet) — deployed separately
2. **Whiskers agent** on the EDR VM — use the companion [`ludus_litterbox_whiskers_agent`](https://github.com/Whispergate/ludus_litterbox_whiskers_agent) role
3. **EDR profile** in LitterBox — configured by this role when enabled

### Prerequisites

- The [`ludus_litterbox_whiskers_agent`](https://github.com/Whispergate/ludus_litterbox_whiskers_agent) role deployed on the EDR Windows VM
- Elastic Stack running and accessible
- Elastic Agent with Elastic Defend enrolled on the EDR Windows VM
- Detection Engine rules enabled in Kibana (Security -> Manage -> Rules)
- Whiskers agent deployed on the EDR VM and whitelisted in Defend's Trusted Applications

### Elasticsearch API Key

The role can **automatically generate** a scoped, read-only API key via the Elasticsearch `_security/api_key` REST API. This is the default behavior — just provide Elasticsearch credentials and leave `ludus_litterbox_elastic_apikey` empty.

**Automatic generation** (recommended):

```yaml
  vars:
    ludus_litterbox_elastic_enabled: true
    ludus_litterbox_elastic_agent_ip: "10.x.x.x"      # EDR VM running Whiskers
    ludus_litterbox_elastic_agent_port: 8080
    ludus_litterbox_elastic_url: "10.x.x.x:9200"      # Elasticsearch host:port
    ludus_litterbox_elastic_username: "elastic"         # User with manage_api_key privilege
    ludus_litterbox_elastic_password: "changeme"        # Use ansible-vault or ludus secrets
    ludus_litterbox_elastic_verify_tls: false
```

The generated key is scoped to read-only access on:
- `.alerts-security.alerts-*` — Detection Engine rule signals
- `.internal.alerts-security.alerts-*` — internal alert indices
- `.ds-logs-endpoint.alerts-*` — Elastic Defend endpoint alerts

Each key is uniquely named per target host (e.g. `litterbox-ws01-1726300800`).

> **Tip:** Store the Elasticsearch password securely using `ansible-vault encrypt_string` or Ludus secrets rather than plain text in your config.

**Manual key** (set `ludus_litterbox_elastic_auto_apikey: false` or provide a key directly):

```yaml
  vars:
    ludus_litterbox_elastic_enabled: true
    ludus_litterbox_elastic_agent_ip: "10.x.x.x"
    ludus_litterbox_elastic_url: "10.x.x.x:9200"
    ludus_litterbox_elastic_apikey: "<base64-key>"     # Pre-created API key
    ludus_litterbox_elastic_auto_apikey: false
```

<details>
<summary>Creating a manual API key in Kibana</summary>

1. Open Kibana (e.g. `https://<elastic-ip>:5601`)
2. Navigate to **Stack Management** -> **API keys** (under Security)
3. Click **Create API key**
4. Set a name (e.g. `litterbox-readonly`)
5. Enable **Restrict privileges** and paste the following role descriptor:

```json
{
  "litterbox_reader": {
    "cluster": ["monitor"],
    "indices": [
      {
        "names": [
          ".alerts-security.alerts-*",
          ".internal.alerts-security.alerts-*",
          ".ds-logs-endpoint.alerts-*"
        ],
        "privileges": ["read"]
      }
    ]
  }
}
```

6. Click **Create API key**
7. Copy the **Encoded** value — this is the base64 string to use as `ludus_litterbox_elastic_apikey`

</details>

### Elastic Defend Variables

| Variable | Default | Description |
|---|---|---|
| `ludus_litterbox_elastic_enabled` | `false` | Enable Elastic Defend EDR profile |
| `ludus_litterbox_elastic_agent_ip` | `""` | IP of the EDR VM running Whiskers |
| `ludus_litterbox_elastic_agent_port` | `8080` | Whiskers agent port |
| `ludus_litterbox_elastic_url` | `""` | Elasticsearch host:port |
| `ludus_litterbox_elastic_apikey` | `""` | Base64-encoded API key (leave empty for auto-generation) |
| `ludus_litterbox_elastic_auto_apikey` | `false` | Auto-generate API key via Elasticsearch API |
| `ludus_litterbox_elastic_username` | `"elastic"` | Elasticsearch user for API key creation |
| `ludus_litterbox_elastic_password` | `""` | Elasticsearch password (use ansible-vault) |
| `ludus_litterbox_elastic_verify_tls` | `false` | Verify Elasticsearch TLS certificate |
| `ludus_litterbox_elastic_wait_alerts` | `90` | Seconds to wait for alerts after execution |
| `ludus_litterbox_elastic_av_block_wait` | `60` | Seconds to wait for AV block verdicts |
| `ludus_litterbox_elastic_exec_timeout` | `60` | Execution timeout in seconds |

### Verify Elastic Integration

After deployment, verify from the LitterBox VM:

```bash
# Check Whiskers agent connectivity
curl http://<edr-vm-ip>:8080/api/info

# Check Elastic connectivity (from LitterBox Python env)
python GrumpyCats/grumpycat.py edr-status
```

## Post-Installation Usage

### Accessing LitterBox

After successful deployment, access LitterBox through:

1. **Web Interface**: 
   - Local: `http://127.0.0.1:1337`
   - Network: `http://<VM_IP>:1337` (if configured for network access)

2. **Desktop Shortcut**: 
   - Double-click "LitterBox" on the desktop

3. **Command Line**:
   ```powershell
   # Using the start script
   C:\Tools\LitterBox\start_litterbox.bat
   
   # Manual start
   cd C:\Tools\LitterBox\LitterBox
   .\venv\Scripts\python.exe litterbox.py
   ```

### API Access with GrumpyCats

The GrumpyCats client library is automatically installed:

```python
# Example API usage
from grumpycat import GrumpyCat

client = GrumpyCat("http://127.0.0.1:1337")
result = client.analyze_file("suspicious.exe")
```

## Maintenance

### Update LitterBox

```powershell
# Update to latest version
cd C:\Tools\LitterBox\LitterBox
git pull
.\venv\Scripts\pip.exe install -r requirements.txt --upgrade
```

### Clean Installation

```powershell
# Remove existing installation
Remove-Item -Path "C:\Tools\LitterBox" -Recurse -Force

# Re-deploy
ludus range deploy -t "litterbox" --limit "TARGET_VM"
```

## Troubleshooting

### Common Issues and Solutions

| Issue | Solution |
|-------|----------|
| **Python Installation Fails** | Manually install Python 3.11+ from python.org, ensure PATH is set |
| **Git Clone Errors** | Check internet connectivity, verify proxy settings if applicable |
| **Port Already in Use** | Change `ludus_litterbox_port` variable or stop conflicting service |
| **Module Import Errors** | Re-run pip install: `.\venv\Scripts\pip.exe install -r requirements.txt` |
| **Firewall Blocking Access** | Verify firewall rule created, check Windows Firewall settings |
| **Insufficient Permissions** | Run Ansible with elevated privileges, check UAC settings |

### Enable Debug Mode

For detailed logging:

```yaml
ludus_litterbox_debug: true
ludus_litterbox_log_level: "DEBUG"
```

Check logs at: `C:\Tools\LitterBox\LitterBox\logs\`

### Verify Installation

```powershell
# Check Python
python --version

# Check git
git --version

# Check LitterBox directory
Test-Path "C:\Tools\LitterBox\LitterBox"

# Check virtual environment
Test-Path "C:\Tools\LitterBox\LitterBox\venv"

# Test Python packages
C:\Tools\LitterBox\LitterBox\venv\Scripts\python.exe -c "import flask; print('Flask OK')"
```

## Directory Structure

After installation, the following structure is created:

```
C:\Tools\LitterBox\
├── LitterBox\              # Main application directory
│   ├── venv\              # Python virtual environment
│   ├── config\            # Configuration files
│   ├── uploads\           # Uploaded samples
│   ├── results\           # Analysis results
│   ├── temp\              # Temporary files
│   ├── logs\              # Application logs
│   ├── database\          # Local database
│   ├── tools\             # Analysis tools
│   ├── Scanners\          # Scanner modules
│   ├── Utils\             # Utility scripts
│   └── GrumpyCats\        # API client library
└── start_litterbox.bat    # Startup script
```

## Tags

The role supports the following Ansible tags for selective execution:

- `litterbox` - Complete LitterBox installation
- `install` - Core installation tasks
- `chocolatey` - Chocolatey package manager
- `python` - Python installation
- `dependencies` - Required dependencies
- `tools` - Analysis tools setup
- `directories` - Directory creation
- `defender` - Windows Defender configuration (use with caution!)
- `dangerous` - High-risk operations
- `elastic` - Elastic Defend EDR profile configuration
- `edr` - EDR integration tasks

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## Additional Resources

- [LitterBox GitHub Repository](https://github.com/BlackSnufkin/LitterBox)
- [Ludus LitterBox Whiskers Agent Role](https://github.com/professor-moody/ludus_litterbox_whiskers_agent) - Companion role for deploying the Whiskers agent on EDR VMs
- [GrumpyCats API Client](https://github.com/BlackSnufkin/GrumpyCats)
- [Ludus Documentation](https://docs.ludus.cloud)
- [Ansible Windows Documentation](https://docs.ansible.com/ansible/latest/collections/ansible/windows/)
- [YARA Documentation](https://yara.readthedocs.io/)

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- [BlackSnufkin](https://github.com/BlackSnufkin) - Original LitterBox author
- [Professor Moody](https://github.com/professor-moody) - Ludus role maintainer
- [Bad Sector Labs](https://github.com/badsectorlabs) - Ludus platform creators
- The security research community for continuous improvements

## Legal Disclaimer

**IMPORTANT**: This tool is intended for authorized security testing and research purposes only. Users are solely responsible for complying with all applicable laws and regulations in their jurisdiction. 


**Role Version**: 1.0.0  
**LitterBox Compatibility**: Latest  
**Last Updated**: 2025  
**Maintained by**: Professor Moody
