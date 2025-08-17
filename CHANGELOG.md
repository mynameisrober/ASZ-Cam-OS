# ASZ Cam OS - Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Initial project structure and build system
- Buildroot configuration for Raspberry Pi
- Core systemd services definition:
  - Camera Service (aszcam-camera)
  - Photo Manager (aszcam-photo-manager)  
  - Cloud Sync Service (aszcam-cloud-sync)
  - Memory Service (aszcam-memory)
  - Network Manager (aszcam-network)
  - Update Service (aszcam-update)
- Build and flash scripts
- Kernel configuration optimized for camera operations
- System configuration templates
- Comprehensive documentation
- Makefile for simplified build management
- Directory structure following specified layout

### Technical Specifications
- Target: Raspberry Pi 4B+ (ARM Cortex-A72)
- Build System: Buildroot 2023.02.8
- Init System: systemd
- Camera Support: libcamera with Pi Camera v3 optimization
- Network: WiFi with WPA supplicant
- Storage: ext4 filesystem optimized for photo operations
- Memory: <1GB RAM usage target with swap support

### Performance Optimizations
- Kernel compiled with camera-specific drivers
- ARM-native compilation with -O3 optimizations  
- Memory management with zram/zswap
- Minimal service footprint for fast boot (<15 seconds target)
- GPU acceleration support for image processing

### Security Features
- Read-only system partition
- Systemd service hardening
- User isolation for camera services
- Automatic integrity checking
- Secure update mechanism

## [0.1.0] - 2024-08-17

### Added
- Initial release with foundational structure
- Complete build system setup
- Service architecture definition
- Documentation framework