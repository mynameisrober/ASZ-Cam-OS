# ASZ Cam OS Installation Guide

## Overview
ASZ Cam OS is a custom operating system designed specifically for the ASZ Camera, built on Raspberry Pi hardware with optimized libcamera and OpenCV integration.

## System Requirements

### Hardware Requirements
- **Raspberry Pi**: 4B or newer (ARM Cortex-A72)
- **RAM**: 2GB minimum, 4GB recommended
- **Storage**: 32GB microSD card (Class 10 or higher)
- **Camera**: Pi Camera v3 or compatible libcamera device
- **Power**: Official Raspberry Pi power supply (5V 3A)

### Host System Requirements (for building)
- **OS**: Ubuntu 20.04+ or Debian 11+
- **RAM**: 8GB minimum for building
- **Storage**: 50GB free space
- **CPU**: Multi-core processor (build time: 1-3 hours)

## Building the System

### 1. Clone the Repository
```bash
git clone https://github.com/mynameisrober/ASZ-Cam-OS.git
cd ASZ-Cam-OS
```

### 2. Install Build Dependencies
```bash
sudo apt update
sudo apt install -y \
    build-essential \
    wget \
    tar \
    make \
    gcc \
    g++ \
    patch \
    gzip \
    bzip2 \
    unzip \
    rsync \
    file \
    bc \
    libncurses5-dev \
    git
```

### 3. Build the Operating System
```bash
./scripts/build.sh
```

This process will:
- Download Buildroot (if needed)
- Configure the build with ASZ Cam settings
- Compile the kernel with camera optimizations
- Build all packages and services
- Generate the system image

**Note**: Initial build takes 1-3 hours depending on your system.

## Flashing to SD Card

### 1. Identify Your SD Card
```bash
lsblk
```

Look for your SD card device (usually `/dev/sdb` or `/dev/mmcblk0`).

### 2. Flash the Image
```bash
./scripts/flash.sh /dev/sdX
```

Replace `/dev/sdX` with your actual SD card device.

**Warning**: This will completely erase the SD card!

## First Boot

### 1. Insert SD Card
- Insert the flashed SD card into your Raspberry Pi
- Connect the Pi Camera module
- Connect power supply

### 2. Boot Process
- The system should boot in under 15 seconds
- ASZ Cam services will start automatically
- Default login: `root` (no password initially)

### 3. Initial Configuration
After first boot, you can configure:
- WiFi settings
- Camera parameters
- Cloud sync (if desired)

## Directory Structure

The system follows this layout:
```
/opt/aszcam/          # Main application directory
├── bin/              # ASZ Cam executables
├── lib/              # System libraries
├── config/           # Configuration files
├── ui/               # User interface components
└── plugins/          # Extensions and plugins

/var/aszcam/          # Data directory
├── photos/           # Photo storage
├── cache/            # Temporary cache
├── logs/             # System logs
└── sync/             # Cloud sync queue
```

## Configuration

### System Configuration
Edit `/opt/aszcam/config/aszcam.conf` to modify:
- Camera settings
- Storage options
- Network configuration
- Cloud sync settings

### Service Management
```bash
# Check service status
systemctl status aszcam-camera

# Restart a service
systemctl restart aszcam-photo-manager

# View service logs
journalctl -u aszcam-camera -f
```

## Services

ASZ Cam OS includes these core services:

1. **aszcam-camera**: Main camera control service
2. **aszcam-photo-manager**: Photo organization and management
3. **aszcam-cloud-sync**: Cloud synchronization (optional)
4. **aszcam-memory**: "This day last year" feature
5. **aszcam-network**: Simplified network management
6. **aszcam-update**: Over-the-air update system

## Troubleshooting

### Build Issues
- Ensure all dependencies are installed
- Check available disk space (50GB+ needed)
- Verify internet connection for package downloads

### Boot Issues
- Check SD card integrity
- Verify power supply (5V 3A minimum)
- Ensure camera module is properly connected

### Camera Issues
- Verify camera module connection
- Check `/var/aszcam/logs/camera.log` for errors
- Test with `libcamera-still --list-cameras`

### Network Issues
- Check WiFi configuration in `/etc/wpa_supplicant/`
- Verify network service: `systemctl status aszcam-network`

## Performance Optimization

### Memory Usage
- The system is designed to use <1GB RAM in normal operation
- Swap is enabled by default for memory management
- Photo cache automatically manages disk usage

### Storage Optimization
- Photos are stored efficiently with configurable compression
- RAW format support for professional use
- Automatic cleanup of temporary files

### Power Management
- CPU frequency scaling enabled
- Optimized for low power consumption
- Sleep mode available when inactive

## Updates

The system supports over-the-air updates:
```bash
# Check for updates
systemctl start aszcam-update

# View update logs
journalctl -u aszcam-update
```

## Support

For issues and questions:
- Check system logs: `journalctl -xe`
- Review service status: `systemctl --failed`
- Monitor resource usage: `htop` or `systemctl status`

## License

ASZ Cam OS is distributed under the MIT License. See LICENSE file for details.