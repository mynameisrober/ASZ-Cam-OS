# ASZ Cam OS - Installation Guide

## Overview
ASZ Cam OS is a custom operating system designed for the ASZ Cam camera device, built on top of Buildroot for Raspberry Pi hardware.

## Hardware Requirements
- Raspberry Pi 4B or newer
- MicroSD card (16GB minimum, 32GB recommended)
- Raspberry Pi Camera Module or USB camera
- Display (HDMI or DSI)
- WiFi connection for Google Photos sync

## Build Instructions

### Prerequisites
- Linux development environment (Ubuntu 20.04+ recommended)
- Required packages:
  ```bash
  sudo apt update
  sudo apt install build-essential git wget python3 python3-pip
  sudo apt install gcc-arm-linux-gnueabihf binutils-arm-linux-gnueabihf
  ```

### Building the OS Image

1. Clone the repository:
   ```bash
   git clone https://github.com/mynameisrober/ASZ-Cam-OS.git
   cd ASZ-Cam-OS
   ```

2. Run the build script:
   ```bash
   ./scripts/build.sh
   ```

3. The build process will:
   - Download Buildroot
   - Configure for ASZ Cam OS
   - Compile the complete operating system
   - Generate bootable SD card image

   **Note**: First build can take 1-2 hours depending on your system.

### Installing to SD Card

1. After successful build, find the image:
   ```bash
   ls build/buildroot-*/output/images/
   ```

2. Write to SD card:
   ```bash
   sudo dd if=build/buildroot-*/output/images/sdcard.img of=/dev/sdX bs=4M status=progress
   sudo sync
   ```
   Replace `/dev/sdX` with your SD card device.

## Development Setup

### Running in Development Mode

For development without Raspberry Pi hardware:

1. Install Python dependencies:
   ```bash
   pip3 install -r requirements.txt
   ```

2. Run development version:
   ```bash
   python3 scripts/dev_run.py
   ```

This runs the application in windowed mode with camera simulation.

### Development Features

- **Camera Simulation**: Generates test frames when no physical camera is available
- **Windowed Mode**: Runs in a regular window instead of fullscreen
- **Debug Output**: Console logging for development

## System Architecture

### Components

1. **Main Application** (`main.py`)
   - Entry point and application lifecycle
   - PyQt5 application setup

2. **UI Framework** (`src/ui/`)
   - `main_window.py`: Main window and navigation
   - `camera_view.py`: Camera interface and controls
   - `settings_view.py`: Configuration interface
   - `photos_view.py`: Photo gallery
   - `memories_view.py`: Memories and "this day" features
   - `theme.py`: ASZ theme system (white/gray palette)

3. **Camera System** (`src/system/`)
   - `camera_service.py`: Camera abstraction layer
   - Supports libcamera and OpenCV backends

4. **Sync Service** (`src/sync/`)
   - `google_photos_sync.py`: Google Photos integration
   - OAuth2 authentication
   - Background upload queue

5. **Build System**
   - `buildroot/`: Custom OS configuration
   - `configs/`: System service configuration
   - `scripts/`: Build and deployment scripts

### Boot Process

1. Raspberry Pi boots custom Linux kernel
2. systemd starts ASZ Cam service
3. Application starts in fullscreen mode
4. Camera initializes automatically
5. Background services start (sync, etc.)

## Configuration

### System Settings

Camera settings, sync preferences, and display options are configured through the Settings interface or can be modified in the system configuration files.

### Google Photos Integration

1. Open Settings → Google Photos
2. Click "Connect Account"
3. Follow OAuth2 authentication process
4. Photos will sync automatically after capture

### Network Configuration

WiFi setup is required for Google Photos sync:
1. Configure WiFi through system settings
2. Enable auto-sync in Settings → Google Photos
3. Set "WiFi Only" option to avoid mobile data usage

## Troubleshooting

### Common Issues

1. **Camera not detected**
   - Verify camera module connection
   - Check if camera is enabled in raspi-config
   - Try different USB cameras for testing

2. **Sync not working**
   - Check internet connection
   - Verify Google Photos authentication
   - Check upload queue in Settings

3. **Performance issues**
   - Ensure adequate power supply (5V 3A minimum)
   - Use high-speed SD card (Class 10 or better)
   - Check system temperature

### Log Files

System logs are available through journalctl:
```bash
journalctl -u asz-cam.service -f
```

Development logs are printed to console when using `dev_run.py`.

## Customization

### Themes

The system uses a white/gray color palette as specified. Custom themes can be added by modifying `src/ui/theme.py`.

### Fonts

SFCamera font integration is handled in the theme system. Additional fonts can be added to `assets/fonts/`.

### Features

New features can be added by extending the existing view classes or adding new modules to the appropriate directories.

## Support

For issues and feature requests, please use the GitHub repository issue tracker.