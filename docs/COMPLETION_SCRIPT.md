# ASZ Cam OS - Installation Completion Script

## Overview

The `complete_install.sh` script is designed to detect and complete interrupted ASZ Cam OS installations. This script is particularly useful when the main installation process gets interrupted after installing system dependencies but before creating the Python virtual environment, or at any other point during installation.

## Features

- **Automatic Detection**: Detects which installation steps are missing
- **Smart Recovery**: Only runs the missing installation steps
- **Dry-Run Mode**: Shows what would be done without making changes
- **Force Mode**: Skips confirmation prompts for automated usage
- **Progress Reporting**: Clear progress indication and error handling
- **Graceful Error Handling**: Continues with non-critical failures

## Usage

### Basic Usage
```bash
sudo ./scripts/complete_install.sh
```

### Command Line Options
```bash
# Show what would be done without executing
sudo ./scripts/complete_install.sh --dry-run

# Skip confirmation prompts
sudo ./scripts/complete_install.sh --force

# Show help
./scripts/complete_install.sh --help
```

## Detection Logic

The script detects missing installation components by checking for:

1. **System Dependencies**: Verifies python3, git, and other critical packages are installed
2. **User and Directories**: Checks if the ASZ service user and required directories exist
3. **Python Virtual Environment**: Verifies virtual environment exists at `/home/pi/ASZCam/venv`
4. **Source Code**: Checks if main.py and requirements.txt are present
5. **Python Packages**: Verifies critical packages like PyQt6, OpenCV, etc. are installed
6. **Raspberry Pi Setup**: Checks if RPi-specific configuration is complete (on RPi only)
7. **Systemd Service**: Verifies the ASZ Cam OS service is installed and enabled

## Installation Steps

The completion script can perform these installation steps as needed:

1. `install_dependencies` - Install system packages and libraries
2. `create_user_and_directories` - Create service user and required directories
3. `install_python_environment` - Create Python virtual environment
4. `copy_source_code` - Copy application source code and assets
5. `install_python_packages` - Install Python dependencies in virtual environment
6. `run_raspberry_pi_setup` - Apply Raspberry Pi specific configurations
7. `install_systemd_service` - Install and enable systemd service

## PyQt6 Configuration

The script includes special handling for PyQt6 system access:

- Detects if PyQt6 is available from system packages
- Creates `.pth` files to allow virtual environment access to system PyQt6
- Falls back to pip installation if system packages aren't available

## Requirements

- Must be run as root (use `sudo`)
- Requires the main ASZ Cam OS repository to be present
- Works on Raspberry Pi OS and compatible Linux distributions

## Examples

### Complete an interrupted installation
```bash
sudo ./scripts/complete_install.sh
```

### Check what would be completed without making changes
```bash
sudo ./scripts/complete_install.sh --dry-run
```

### Automated completion (no prompts)
```bash
sudo ./scripts/complete_install.sh --force
```

## Troubleshooting

### Common Issues

1. **Permission Denied**: Make sure to run with `sudo`
2. **Script Not Found**: Run from the repository root directory
3. **Missing Dependencies**: The script will detect and install missing system dependencies
4. **PyQt6 Issues**: The script handles both system and pip-installed PyQt6

### Logs

Installation logs are saved to `/tmp/aszcam_complete_install.log` (when run as root).

### Validation

The script runs validation after completion to verify the installation is working properly.

## Integration with Main Installation

This script is designed to work alongside the main `install.sh` script:

- Reuses the same configuration variables
- Uses compatible directory structure
- Follows the same installation patterns
- Can be safely run multiple times

## Safety Features

- **Dry-run mode** prevents accidental changes
- **Detection before action** - only runs necessary steps
- **Graceful error handling** - continues with warnings for non-critical failures
- **Backup awareness** - respects existing configurations
- **User confirmation** - prompts before making changes (unless --force is used)