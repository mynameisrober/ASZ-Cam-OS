# ASZ Cam OS - Technical Specifications

## System Overview

ASZ Cam OS is a custom Linux distribution built specifically for the ASZ Cam camera device. It provides a minimal, fast-booting system optimized for camera operations with Google Photos integration.

## Hardware Specifications

### Supported Platforms
- **Primary**: Raspberry Pi 4B (4GB RAM recommended)
- **Secondary**: Raspberry Pi 4B (2GB RAM minimum)
- **Future**: Raspberry Pi 5 (planned)

### Camera Support
- **libcamera**: Primary camera system (hardware-accelerated)
- **OpenCV**: Fallback for development and testing
- **Supported Formats**: JPEG, PNG, RAW (future)
- **Resolutions**: Up to 1920x1080 @ 30fps

### Storage
- **Primary**: MicroSD card (16GB minimum, 32GB recommended)
- **Photo Storage**: User home directory (`/home/asz/ASZCam/Photos`)
- **System Config**: `/home/asz/.config/asz-cam-os/`

## Software Architecture

### Operating System Layer
```
├── Linux Kernel 5.15+ (Raspberry Pi optimized)
├── Buildroot-based rootfs (minimal)
├── systemd init system
└── Custom ASZ Cam application
```

### Application Architecture
```
ASZ Cam OS Application
├── UI Layer (PyQt5)
│   ├── Main Window & Navigation
│   ├── Camera View
│   ├── Settings Interface
│   ├── Photo Gallery
│   └── Memories System
├── Camera Abstraction Layer
│   ├── libcamera Integration
│   ├── OpenCV Fallback
│   └── Hardware Controls (ISO, Exposure, etc.)
├── Sync Services
│   ├── Google Photos OAuth2
│   ├── Upload Queue Management
│   └── Background Processing
└── System Services
    ├── Boot Optimization
    ├── Power Management
    └── Hardware Monitoring
```

## Performance Specifications

### Boot Time
- **Target**: < 10 seconds (cold boot to camera ready)
- **Optimizations**:
  - Minimal kernel modules
  - Reduced systemd services
  - Direct camera application start
  - Optimized filesystem layout

### Camera Performance
- **Preview**: 30fps @ 1080p
- **Capture**: < 1 second processing time
- **Storage**: Immediate local save + background sync
- **Memory Usage**: < 200MB RAM for core application

### Sync Performance
- **Queue Processing**: Background, non-blocking
- **Upload Speed**: Limited by network bandwidth
- **Retry Logic**: Automatic retry with exponential backoff
- **Offline Operation**: Full functionality without internet

## Security & Privacy

### Data Protection
- **Local Storage**: Photos stored locally first
- **Sync Control**: User-controlled Google Photos integration
- **Credentials**: Secure OAuth2 token storage
- **Privacy**: No data collection beyond Google Photos sync

### Network Security
- **Encryption**: All network traffic encrypted
- **Authentication**: OAuth2 standard implementation
- **Firewall**: Minimal attack surface (camera device only)

## Development Specifications

### Programming Languages
- **Primary**: Python 3.8+
- **UI Framework**: PyQt5
- **Camera**: libcamera + Python bindings
- **Build System**: Buildroot + custom scripts

### Dependencies
```
Core System:
├── Python 3.8+
├── PyQt5
├── OpenCV 4.5+
├── libcamera
├── systemd
└── Linux kernel 5.15+

Python Packages:
├── PyQt5 (UI framework)
├── opencv-python (camera fallback)
├── requests (HTTP client)
├── google-auth* (Google Photos integration)
├── Pillow (image processing)
└── numpy (numerical operations)
```

### Build Environment
- **Host OS**: Ubuntu 20.04+ (recommended)
- **Cross-compilation**: ARM64 targeting
- **Build Time**: 1-2 hours (first build)
- **Output**: Bootable SD card image

## API Specifications

### Google Photos API Integration
```python
# OAuth2 Scopes
SCOPES = [
    'https://www.googleapis.com/auth/photoslibrary.appendonly'
]

# Upload API
POST https://photoslibrary.googleapis.com/v1/uploads
Content-Type: application/octet-stream
X-Goog-Upload-File-Name: {filename}
X-Goog-Upload-Protocol: raw
```

### Camera API (Internal)
```python
# Camera Service Interface
class CameraService:
    def start_camera() -> bool
    def stop_camera() -> bool
    def capture_photo() -> str  # Returns file path
    def get_camera_info() -> dict
    def set_camera_settings(settings: dict) -> bool
```

## File System Layout

```
/
├── boot/                    # Boot files
├── opt/asz-cam-os/         # Application files
│   ├── main.py
│   ├── src/
│   ├── assets/
│   └── requirements.txt
├── etc/
│   ├── systemd/system/
│   │   └── asz-cam.service
│   └── wpa_supplicant/     # WiFi config
├── home/asz/               # User data
│   ├── ASZCam/
│   │   └── Photos/         # Photo storage
│   └── .config/
│       └── asz-cam-os/     # App config
└── var/log/                # System logs
```

## Memory Layout

### RAM Usage (4GB Pi 4B)
- **Linux Kernel**: ~100MB
- **System Services**: ~50MB
- **ASZ Cam App**: ~200MB
- **Camera Buffers**: ~100MB
- **Available for Photos**: ~3.5GB

### Storage Layout (32GB SD Card)
- **Root Filesystem**: ~2GB
- **User Data**: ~29GB available
- **System Logs**: ~1GB reserved

## Network Requirements

### WiFi Specifications
- **Standards**: 802.11n/ac
- **Frequency**: 2.4GHz and 5GHz
- **Security**: WPA2/WPA3
- **Range**: Standard Raspberry Pi WiFi range

### Internet Requirements
- **Sync Operation**: 1Mbps minimum upload
- **Photo Upload**: Variable based on resolution
- **Offline Mode**: Full camera functionality without internet

## Quality Assurance

### Testing Matrix
| Component | Test Type | Coverage |
|-----------|-----------|----------|
| Camera | Unit Tests | Core functionality |
| UI | Integration Tests | Navigation, display |
| Sync | Mock API Tests | Upload, retry logic |
| System | Hardware Tests | Pi 4B validation |
| Performance | Load Tests | Boot time, memory |

### Validation Criteria
- ✅ Boot time < 10 seconds
- ✅ Camera starts automatically
- ✅ SFCamera font loading
- ✅ White/gray color palette
- ✅ Google Photos sync
- ✅ Navigation between all 4 sections
- ✅ Photo capture and storage
- ✅ Memories functionality

## Future Roadmap

### Version 1.1 (Planned)
- RAW photo format support
- Advanced camera controls
- Multi-camera support
- Performance optimizations

### Version 1.2 (Planned)
- Video recording
- Live streaming capabilities
- Mobile app integration
- Cloud backup options

### Hardware Expansion
- Raspberry Pi 5 support
- External storage support
- Professional camera modules
- Additional sensor integration