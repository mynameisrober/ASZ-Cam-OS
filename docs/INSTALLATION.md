# ASZ Cam OS - Installation Guide

Complete installation guide for ASZ Cam OS - a custom camera operating system for Raspberry Pi with Google Photos integration.

## Table of Contents
- [Overview](#overview)
- [System Requirements](#system-requirements)
- [Prerequisites](#prerequisites)
- [Installation Methods](#installation-methods)
- [Quick Installation](#quick-installation)
- [Manual Installation](#manual-installation)
- [Post-Installation Configuration](#post-installation-configuration)
- [Google Photos Setup](#google-photos-setup)
- [Troubleshooting](#troubleshooting)

## Overview

ASZ Cam OS is a lightweight, specialized operating system designed for Raspberry Pi that transforms your device into a dedicated camera system with cloud synchronization capabilities. It features:

- **Fast Boot Time**: Optimized for &lt; 10 second boot time
- **Camera Focused**: Optimized for camera operations with hardware acceleration
- **Google Photos Integration**: Automatic photo backup and synchronization
- **Touch-Friendly UI**: Clean, responsive interface built with PyQt6
- **Auto-Start**: Automatically launches camera application on boot
- **Secure**: Minimal system with security hardening

## System Requirements

### Minimum Requirements
- **Raspberry Pi 4 Model B** (2GB RAM minimum, 4GB+ recommended)
- **MicroSD Card**: 16GB Class 10 or better (32GB+ recommended)
- **Camera**: Raspberry Pi Camera Module v2/v3 or compatible USB camera
- **Display**: HDMI monitor or official Raspberry Pi touchscreen
- **Power Supply**: Official Raspberry Pi power supply (5V/3A)
- **Internet Connection**: WiFi or Ethernet for Google Photos sync

### Supported Hardware
- Raspberry Pi 4 Model B (all RAM variants)
- Raspberry Pi 400 (with external camera)
- Raspberry Pi Camera Module v1/v2/v3
- USB webcams (UVC compatible)
- Official Raspberry Pi 7" touchscreen
- Most HDMI displays (1920x1080 recommended)

### Recommended Setup
- Raspberry Pi 4 (4GB or 8GB)
- High-quality MicroSD card (SanDisk Extreme, Samsung EVO Select)
- Raspberry Pi Camera Module v3
- Official 7" touchscreen for portable operation
- Case with camera mount

## Prerequisites

### Software Requirements on Host Computer
- [Raspberry Pi Imager](https://www.raspberrypi.org/software/) for flashing SD cards
- SSH client (built-in on macOS/Linux, PuTTY for Windows)
- Git (for building from source)

### Google Photos API Setup (Optional)
To enable Google Photos synchronization, you'll need:

1. **Google Cloud Project**: Create a project in [Google Cloud Console](https://console.cloud.google.com/)
2. **Photos Library API**: Enable the Photos Library API for your project
3. **OAuth2 Credentials**: Create OAuth2 credentials for a desktop application
4. **Credentials File**: Download the credentials JSON file

Detailed steps are provided in the [Google Photos Setup](#google-photos-setup) section.

## Installation Methods

Choose one of the following installation methods:

1. **Quick Installation** (Recommended): Use the automated installer script
2. **Manual Installation**: Step-by-step manual setup for customization
3. **Pre-built Image**: Flash a pre-built disk image (if available)

## Quick Installation

The quickest way to get ASZ Cam OS running is using the automated installer script.

### Step 1: Prepare Raspberry Pi OS

1. **Flash Raspberry Pi OS Lite** to your SD card using Raspberry Pi Imager
   - Choose "Raspberry Pi OS Lite (64-bit)" for best performance
   - Enable SSH and configure WiFi in advanced options
   - Set username to `pi` and configure password

2. **Boot and Connect**
   ```bash
   # SSH into your Pi (replace with your Pi's IP)
   ssh pi@192.168.1.100
   ```

### Step 2: Download ASZ Cam OS

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install git
sudo apt install -y git

# Clone the repository
git clone https://github.com/mynameisrober/ASZ-Cam-OS.git
cd ASZ-Cam-OS
```

### Step 3: Run Installation Script

```bash
# Make installer executable
chmod +x scripts/install.sh

# Run the installer (requires sudo)
sudo ./scripts/install.sh
```

The installer will:
- Install all dependencies
- Set up Python virtual environment
- Configure system settings
- Install systemd services  
- Optimize boot configuration
- Configure X11 and desktop environment
- Download fonts and themes
- Set up camera permissions

### Step 4: Reboot

```bash
sudo reboot
```

After reboot, ASZ Cam OS should automatically start and display the camera interface.

## Manual Installation

For advanced users who want to customize the installation process.

### Step 1: System Preparation

```bash
# Update package lists and system
sudo apt update && sudo apt upgrade -y

# Install essential packages
sudo apt install -y git curl wget unzip build-essential cmake pkg-config
sudo apt install -y python3 python3-pip python3-venv python3-dev
sudo apt install -y libcamera-dev libcamera-apps python3-libcamera python3-picamera2
```

### Step 2: Create User and Directories

```bash
# Create ASZ Cam directories
sudo mkdir -p /home/pi/ASZCam
sudo mkdir -p /home/pi/.config/aszcam
sudo mkdir -p /home/pi/Pictures/ASZCam
sudo mkdir -p /var/log/aszcam

# Set permissions
sudo chown -R pi:pi /home/pi/ASZCam
sudo chown -R pi:pi /home/pi/.config/aszcam
sudo chown -R pi:pi /home/pi/Pictures
sudo chown -R pi:pi /var/log/aszcam
```

### Step 3: Install ASZ Cam OS

```bash
# Clone repository
git clone https://github.com/mynameisrober/ASZ-Cam-OS.git
cd ASZ-Cam-OS

# Copy source code
cp -r src /home/pi/ASZCam/
cp -r assets /home/pi/ASZCam/
cp requirements.txt /home/pi/ASZCam/

# Create Python virtual environment
python3 -m venv /home/pi/ASZCam/venv

# Install Python dependencies
/home/pi/ASZCam/venv/bin/pip install --upgrade pip
/home/pi/ASZCam/venv/bin/pip install -r /home/pi/ASZCam/requirements.txt
```

### Step 4: System Configuration

```bash
# Run individual configuration scripts
sudo ./scripts/setup_rpi.sh      # Raspberry Pi optimization
sudo ./scripts/download_fonts.sh # Font installation
sudo ./scripts/configure_system.sh # System configuration

# Install systemd service
sudo cp install/asz-cam-os.service /etc/systemd/system/
sudo sed -i "s|{ASZ_INSTALL_DIR}|/home/pi/ASZCam|g" /etc/systemd/system/asz-cam-os.service
sudo sed -i "s|{ASZ_USER}|pi|g" /etc/systemd/system/asz-cam-os.service
sudo systemctl daemon-reload
sudo systemctl enable asz-cam-os.service
```

### Step 5: Apply Boot Configuration

```bash
# Backup original config
sudo cp /boot/config.txt /boot/config.txt.backup

# Apply ASZ Cam boot configuration
sudo cp install/boot_config.txt /boot/config.txt

# Apply X11 configuration
sudo cp install/xorg.conf /etc/X11/xorg.conf
```

## Post-Installation Configuration

### Initial Setup

After the first boot, complete the initial setup:

1. **Set WiFi Country Code** (if not done during imaging)
   ```bash
   sudo raspi-config
   # Navigate to Localisation Options > WLAN Country
   ```

2. **Configure Timezone**
   ```bash
   sudo dpkg-reconfigure tzdata
   ```

3. **Change Default Password**
   ```bash
   passwd
   ```

### Camera Configuration

1. **Test Camera**
   ```bash
   # Test with libcamera
   libcamera-hello --list-cameras
   libcamera-still -o test.jpg
   ```

2. **Verify Camera in ASZ Cam OS**
   - Camera preview should appear automatically
   - Try taking a test photo
   - Check that photos are saved to `/home/pi/Pictures/ASZCam/`

### System Validation

Run the validation script to ensure everything is working:

```bash
cd ASZ-Cam-OS
sudo ./scripts/validate_install.sh
```

This will check:
- Camera functionality
- Service status
- File permissions
- Network connectivity
- Display configuration

## Google Photos Setup

To enable automatic photo backup to Google Photos:

### Step 1: Create Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing one
3. Enable the **Photos Library API**:
   - Navigate to "APIs & Services" > "Library"
   - Search for "Photos Library API"
   - Click "Enable"

### Step 2: Create OAuth2 Credentials

1. Go to "APIs & Services" > "Credentials"
2. Click "Create Credentials" > "OAuth client ID"
3. Choose "Desktop application"
4. Name it "ASZ Cam OS"
5. Download the credentials JSON file

### Step 3: Upload Credentials to Pi

```bash
# Copy credentials file to Pi (replace with your file)
scp ~/Downloads/credentials.json pi@192.168.1.100:/home/pi/ASZCam/google_credentials.json

# Set proper permissions
chmod 600 /home/pi/ASZCam/google_credentials.json
```

### Step 4: Initial Authentication

1. **Enable Sync in Settings**
   - Open ASZ Cam OS
   - Navigate to Settings > Sync
   - Enable "Google Photos Sync"

2. **Complete OAuth Flow**
   - Click "Authenticate with Google Photos"
   - Follow the authentication prompts
   - Grant necessary permissions

3. **Verify Sync**
   - Take a test photo
   - Check sync status in Settings
   - Verify photo appears in your Google Photos

### Privacy and Security Notes

- **Permissions**: ASZ Cam OS only requests append-only access to Google Photos
- **Data**: No personal information is transmitted beyond photo files
- **Local Storage**: Authentication tokens are encrypted and stored locally
- **Control**: You can disable sync or revoke access at any time

## Troubleshooting

### Common Issues

#### Boot Issues
- **Black screen on boot**: Check HDMI cable and display compatibility
- **Slow boot**: Run `systemctl analyze-blame` to identify slow services
- **Service failed**: Check `journalctl -u asz-cam-os` for error messages

#### Camera Issues
- **No camera detected**: 
  ```bash
  # Check camera connection
  libcamera-hello --list-cameras
  
  # Check camera module enabled
  sudo raspi-config # Interface Options > Camera
  ```

- **Camera permission denied**:
  ```bash
  # Add user to video group
  sudo usermod -a -G video pi
  ```

#### Sync Issues
- **Authentication failed**: 
  - Check credentials file location and permissions
  - Verify Google Cloud project has Photos Library API enabled
  - Check internet connectivity

- **Upload errors**: 
  - Check `journalctl -u asz-cam-os` for detailed error messages
  - Verify Google Photos storage quota
  - Check network connectivity

#### Performance Issues
- **Slow UI**: 
  - Check GPU memory split: `vcgencmd get_mem gpu`
  - Should show `gpu=128M` or higher
  - Verify graphics drivers: `glxinfo | grep renderer`

- **High CPU usage**:
  - Check for runaway processes: `htop`
  - Verify camera resolution settings
  - Check sync queue size

### Log Files

Key log locations for troubleshooting:

```bash
# System logs
journalctl -u asz-cam-os -f

# Application logs
tail -f /var/log/aszcam/aszcam.log

# System boot logs
dmesg | grep -i camera

# X11 logs
cat ~/.local/share/xorg/Xorg.0.log
```

### Recovery Options

#### Safe Mode Boot
Add to `/boot/cmdline.txt`:
```
systemd.unit=rescue.target
```

#### Reset Configuration
```bash
# Backup current settings
cp ~/.config/aszcam/settings.yaml ~/.config/aszcam/settings.yaml.backup

# Reset to defaults
rm ~/.config/aszcam/settings.yaml

# Restart service
sudo systemctl restart asz-cam-os
```

#### Factory Reset
```bash
# Stop service
sudo systemctl stop asz-cam-os

# Remove user data (CAUTION: This deletes all photos and settings)
rm -rf ~/.config/aszcam/
rm -rf ~/Pictures/ASZCam/

# Restart service (will recreate defaults)
sudo systemctl start asz-cam-os
```

### Getting Help

If you encounter issues not covered here:

1. **Check Logs**: Always check the logs first for specific error messages
2. **GitHub Issues**: Search existing issues or create a new one at [GitHub Repository](https://github.com/mynameisrober/ASZ-Cam-OS/issues)
3. **Community Forums**: Raspberry Pi forums have extensive camera-related help
4. **Documentation**: Check the [User Guide](USER_GUIDE.md) and [Troubleshooting Guide](TROUBLESHOOTING.md)

### Performance Optimization

For optimal performance:

1. **Use Fast SD Card**: Class 10 or better, preferably Application Performance Class A2
2. **Adequate Power Supply**: Use official Raspberry Pi power supply
3. **Cooling**: Ensure adequate ventilation, consider heat sinks for sustained operation
4. **Network**: Use wired Ethernet for best sync performance
5. **Regular Updates**: Keep system and ASZ Cam OS updated

---

## Next Steps

After successful installation:

1. **Read the [User Guide](USER_GUIDE.md)** for detailed usage instructions
2. **Configure Google Photos sync** for automatic backup
3. **Customize settings** for your specific use case
4. **Set up regular backups** of your configuration
5. **Explore advanced features** in the settings panel

**Enjoy your ASZ Cam OS setup!** 📷