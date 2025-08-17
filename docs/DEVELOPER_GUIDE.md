# ASZ Cam OS - Developer Guide

Comprehensive development guide for contributing to and extending ASZ Cam OS.

## Table of Contents
- [Development Environment Setup](#development-environment-setup)
- [Architecture Overview](#architecture-overview)
- [Code Structure](#code-structure)
- [Development Workflow](#development-workflow)
- [API Reference](#api-reference)
- [Testing](#testing)
- [Contributing Guidelines](#contributing-guidelines)
- [Deployment](#deployment)

## Development Environment Setup

### Prerequisites

#### Host System Requirements
- **Python 3.9+**: Development and testing
- **Git**: Version control
- **IDE**: VS Code, PyCharm, or similar
- **SSH Client**: For Raspberry Pi development

#### Raspberry Pi Development Target
- **Raspberry Pi 4**: 4GB+ RAM recommended for development
- **Raspberry Pi OS**: 64-bit version
- **SSH Access**: Enabled for remote development
- **Camera Module**: For testing camera functionality

### Local Development Setup

```bash
# Clone the repository
git clone https://github.com/mynameisrober/ASZ-Cam-OS.git
cd ASZ-Cam-OS

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # Linux/macOS
# venv\Scripts\activate   # Windows

# Install dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Install development tools
pip install black flake8 pytest pytest-qt mypy
```

### Development Dependencies

Create `requirements-dev.txt`:
```
# Testing
pytest>=7.4.0
pytest-qt>=4.2.0
pytest-cov>=4.1.0
pytest-mock>=3.11.0

# Code Quality
black>=23.7.0
flake8>=6.0.0
mypy>=1.5.0
isort>=5.12.0

# Documentation
sphinx>=7.1.0
sphinx-rtd-theme>=1.3.0

# Development Tools
pre-commit>=3.3.0
tox>=4.6.0
```

### IDE Configuration

#### VS Code Settings
Create `.vscode/settings.json`:
```json
{
    "python.defaultInterpreterPath": "./venv/bin/python",
    "python.linting.enabled": true,
    "python.linting.flake8Enabled": true,
    "python.linting.mypyEnabled": true,
    "python.formatting.provider": "black",
    "python.formatting.blackArgs": ["--line-length", "88"],
    "editor.formatOnSave": true,
    "python.testing.pytestEnabled": true,
    "python.testing.pytestArgs": ["tests/"],
    "files.exclude": {
        "**/__pycache__": true,
        "**/*.pyc": true
    }
}
```

#### Pre-commit Hooks
Create `.pre-commit-config.yaml`:
```yaml
repos:
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.4.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-added-large-files

  - repo: https://github.com/psf/black
    rev: 23.7.0
    hooks:
      - id: black
        language_version: python3

  - repo: https://github.com/pycqa/flake8
    rev: 6.0.0
    hooks:
      - id: flake8

  - repo: https://github.com/pycqa/isort
    rev: 5.12.0
    hooks:
      - id: isort
```

Install pre-commit:
```bash
pre-commit install
```

## Architecture Overview

### System Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    ASZ Cam OS                           │
├─────────────────────────────────────────────────────────┤
│  User Interface (PyQt6)                                │
│  ├── Main Window          ├── Settings Panel          │
│  ├── Camera View          ├── Gallery View             │
│  └── Status Indicators    └── Progress Dialogs        │
├─────────────────────────────────────────────────────────┤
│  Core Services                                         │
│  ├── System Manager       ├── Camera Service          │
│  ├── Sync Service         ├── Photo Manager           │
│  └── Settings Manager     └── Font Manager            │
├─────────────────────────────────────────────────────────┤
│  Hardware Abstraction                                  │
│  ├── libCamera Backend    ├── Storage Backend         │
│  ├── GPIO Interface       └── Display Backend         │
├─────────────────────────────────────────────────────────┤
│  Cloud Integration                                     │
│  ├── Google Photos API    ├── OAuth2 Handler          │
│  └── Upload Queue         └── Sync Manager            │
├─────────────────────────────────────────────────────────┤
│  System Layer                                          │
│  ├── Raspberry Pi OS      ├── X11 Display Server      │
│  ├── systemd Services     └── Hardware Drivers        │
└─────────────────────────────────────────────────────────┘
```

### Component Relationships

#### System Manager
- **Central Coordinator**: Manages system lifecycle
- **Service Orchestration**: Initializes and coordinates other services
- **Error Handling**: Global error handling and recovery
- **Shutdown Management**: Graceful shutdown procedures

#### Camera Service
- **Hardware Interface**: Communicates with camera hardware
- **Preview Management**: Handles live camera preview
- **Photo Capture**: Manages photo capture operations
- **Settings Interface**: Exposes camera configuration options

#### Sync Service
- **Cloud Integration**: Manages Google Photos synchronization
- **Queue Management**: Handles upload queue and priorities
- **Error Recovery**: Implements retry logic and error handling
- **State Persistence**: Maintains sync state across restarts

#### UI Components
- **Event Handling**: Processes user interactions
- **Display Updates**: Updates interface based on system state
- **Signal Integration**: Uses Qt signals for loose coupling
- **Responsive Design**: Adapts to different screen sizes

### Design Patterns

#### Model-View-Controller (MVC)
- **Models**: Configuration, photo metadata, sync state
- **Views**: PyQt6 widgets and windows
- **Controllers**: Service classes handling business logic

#### Observer Pattern
- **Qt Signals/Slots**: Loose coupling between components
- **Event System**: Publish/subscribe for system events
- **Status Updates**: Real-time status propagation

#### Singleton Pattern
- **Global Services**: System manager, settings, API clients
- **Shared Resources**: Camera hardware, configuration

#### Factory Pattern
- **Backend Creation**: Camera backends, storage backends
- **Service Initialization**: Dynamic service instantiation

## Code Structure

### Directory Layout

```
ASZ-Cam-OS/
├── src/                          # Application source code
│   ├── core/                     # Core system components
│   │   ├── __init__.py
│   │   └── system_manager.py     # Main system coordinator
│   ├── camera/                   # Camera functionality
│   │   ├── __init__.py
│   │   ├── camera_service.py     # High-level camera service
│   │   └── libcamera_backend.py  # Hardware abstraction
│   ├── ui/                       # User interface components
│   │   ├── __init__.py
│   │   ├── main_window.py        # Main application window
│   │   ├── camera_view.py        # Camera interface
│   │   ├── gallery_view.py       # Photo gallery
│   │   ├── settings_panel.py     # Settings interface
│   │   └── font_manager.py       # Font handling
│   ├── sync/                     # Cloud synchronization
│   │   ├── __init__.py
│   │   ├── sync_service.py       # Sync coordination
│   │   └── google_photos.py      # Google Photos integration
│   ├── storage/                  # Photo storage management
│   │   ├── __init__.py
│   │   └── photo_manager.py      # Photo file management
│   ├── config/                   # Configuration management
│   │   ├── __init__.py
│   │   └── settings.py           # Settings system
│   └── main.py                   # Application entry point
├── assets/                       # Static assets
│   ├── fonts/                    # Font files
│   └── themes/                   # UI themes
├── scripts/                      # Installation and utility scripts
│   ├── install.sh                # Main installer
│   ├── setup_rpi.sh             # Raspberry Pi setup
│   ├── download_fonts.sh        # Font installation
│   └── configure_system.sh      # System configuration
├── install/                      # System configuration files
│   ├── boot_config.txt          # Raspberry Pi boot config
│   ├── asz-cam-os.service       # systemd service
│   ├── xorg.conf                # X11 configuration
│   └── raspi-config-settings.sh # RPi settings script
├── docs/                         # Documentation
│   ├── INSTALLATION.md
│   ├── USER_GUIDE.md
│   ├── DEVELOPER_GUIDE.md
│   └── TROUBLESHOOTING.md
├── tests/                        # Test suite
│   ├── unit/                     # Unit tests
│   ├── integration/              # Integration tests
│   └── fixtures/                 # Test fixtures
├── requirements.txt              # Production dependencies
├── requirements-dev.txt          # Development dependencies
└── README.md                     # Project overview
```

### Core Components

#### System Manager (`src/core/system_manager.py`)

```python
class SystemManager(QObject):
    """Central system coordinator."""
    
    def __init__(self):
        super().__init__()
        self.app = None
        self.camera_service = None
        self.sync_service = None
        self.main_window = None
        self._setup_logging()
        self._setup_signal_handlers()
    
    def initialize(self) -> bool:
        """Initialize all system components."""
        # Implementation details...
    
    def run(self) -> int:
        """Run the main application loop."""
        # Implementation details...
    
    def shutdown(self):
        """Perform graceful system shutdown."""
        # Implementation details...
```

#### Camera Service (`src/camera/camera_service.py`)

```python
class CameraService(QObject):
    """High-level camera operations."""
    
    # Signals
    photo_captured = pyqtSignal(str)
    preview_frame_ready = pyqtSignal(object)
    error_occurred = pyqtSignal(str)
    
    def __init__(self):
        super().__init__()
        self.backend = None
        self.is_initialized = False
    
    def initialize(self) -> bool:
        """Initialize camera hardware."""
        # Implementation details...
    
    def capture_photo(self, filename: str = None) -> str:
        """Capture a single photo."""
        # Implementation details...
    
    def start_preview(self) -> bool:
        """Start camera preview."""
        # Implementation details...
```

#### Settings System (`src/config/settings.py`)

```python
@dataclass
class CameraConfig:
    """Camera-specific settings."""
    default_resolution: Tuple[int, int] = (1920, 1080)
    quality: int = 85
    format: str = "JPEG"
    preview_enabled: bool = True

class Settings:
    """Central configuration manager."""
    
    def __init__(self, config_file: str = None):
        self.config_file = config_file or self._get_default_config_path()
        self.camera = CameraConfig()
        self.ui = UIConfig()
        self.sync = SyncConfig()
        self.system = SystemConfig()
    
    def load_config(self):
        """Load configuration from file."""
        # Implementation details...
    
    def save_config(self):
        """Save configuration to file."""
        # Implementation details...
```

### Coding Standards

#### Python Style Guide
- **PEP 8**: Follow Python style guidelines
- **Line Length**: Maximum 88 characters (Black default)
- **Imports**: Use isort for import organization
- **Type Hints**: Use type annotations for all public APIs
- **Docstrings**: Google-style docstrings for all public methods

#### Code Example
```python
"""
Module for camera operations.
Provides high-level interface to camera hardware.
"""

import logging
from typing import Optional, Tuple, Dict, Any
from pathlib import Path
from datetime import datetime

from PyQt6.QtCore import QObject, pyqtSignal


class CameraService(QObject):
    """
    High-level camera service for photo capture and management.
    
    This class provides a simplified interface to camera hardware,
    handling initialization, configuration, and photo capture operations.
    
    Attributes:
        photo_captured: Signal emitted when photo is captured
        error_occurred: Signal emitted when error occurs
    """
    
    # Signals
    photo_captured = pyqtSignal(str)  # filepath
    error_occurred = pyqtSignal(str)  # error message
    
    def __init__(self) -> None:
        """Initialize camera service."""
        super().__init__()
        self.logger = logging.getLogger(__name__)
        self._backend: Optional[LibCameraBackend] = None
        self._is_initialized = False
    
    def initialize(self) -> bool:
        """
        Initialize camera hardware and backend.
        
        Returns:
            True if initialization successful, False otherwise.
            
        Raises:
            CameraError: If hardware initialization fails.
        """
        try:
            self.logger.info("Initializing camera service...")
            # Implementation...
            return True
        except Exception as e:
            self.logger.error(f"Camera initialization failed: {e}")
            return False
    
    def capture_photo(
        self, 
        filename: Optional[str] = None,
        resolution: Optional[Tuple[int, int]] = None
    ) -> Optional[str]:
        """
        Capture a photo and save to disk.
        
        Args:
            filename: Optional custom filename
            resolution: Optional resolution override
            
        Returns:
            Path to captured photo file, or None if capture failed.
        """
        # Implementation...
        pass
```

#### Error Handling

```python
class CameraError(Exception):
    """Base exception for camera-related errors."""
    pass

class CameraNotFoundError(CameraError):
    """Raised when camera hardware is not detected."""
    pass

class CaptureError(CameraError):
    """Raised when photo capture fails."""
    pass

# Usage
try:
    photo_path = camera_service.capture_photo()
except CameraNotFoundError:
    logger.error("Camera hardware not detected")
    # Handle gracefully...
except CaptureError as e:
    logger.error(f"Photo capture failed: {e}")
    # Retry or inform user...
```

## Development Workflow

### Git Workflow

#### Branch Strategy
- **main**: Production-ready code
- **develop**: Integration branch for features
- **feature/**: Feature development branches
- **bugfix/**: Bug fix branches
- **release/**: Release preparation branches

#### Branch Naming
- `feature/camera-manual-focus`
- `bugfix/sync-authentication-error`
- `release/v1.1.0`

#### Commit Message Format
```
type(scope): brief description

Longer explanation if needed.

Fixes #123
```

Types:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes
- `refactor`: Code refactoring
- `test`: Test additions/changes
- `chore`: Maintenance tasks

### Development Process

1. **Create Feature Branch**
   ```bash
   git checkout develop
   git pull origin develop
   git checkout -b feature/new-feature-name
   ```

2. **Develop and Test**
   ```bash
   # Make changes
   # Run tests
   pytest tests/
   
   # Run linting
   black src/
   flake8 src/
   mypy src/
   ```

3. **Commit Changes**
   ```bash
   git add .
   git commit -m "feat(camera): add manual focus control"
   ```

4. **Push and Create PR**
   ```bash
   git push origin feature/new-feature-name
   # Create pull request via GitHub
   ```

### Local Development

#### Running on Development Machine

```bash
# Export display for GUI (Linux)
export DISPLAY=:0

# Run with development settings
python src/main.py --dev --mock-camera

# Run with specific config
python src/main.py --config dev_config.yaml
```

#### Development Flags

```python
# src/main.py
import argparse

parser = argparse.ArgumentParser(description='ASZ Cam OS')
parser.add_argument('--dev', action='store_true', help='Development mode')
parser.add_argument('--mock-camera', action='store_true', help='Use mock camera')
parser.add_argument('--verbose', '-v', action='store_true', help='Verbose logging')
parser.add_argument('--config', help='Configuration file path')

args = parser.parse_args()

if args.dev:
    logging.basicConfig(level=logging.DEBUG)
    settings.development_mode = True
```

#### Remote Development on Pi

```bash
# SSH with X forwarding
ssh -X pi@raspberrypi.local

# Or use VS Code Remote SSH extension
# Install "Remote - SSH" extension
# Connect to pi@raspberrypi.local
```

### Testing on Raspberry Pi

#### Deployment Script

Create `scripts/deploy_dev.sh`:
```bash
#!/bin/bash
# Development deployment to Raspberry Pi

PI_HOST="${1:-raspberrypi.local}"
PI_USER="${2:-pi}"

echo "Deploying to ${PI_USER}@${PI_HOST}..."

# Sync source code
rsync -av --exclude='__pycache__' --exclude='.git' \
    src/ "${PI_USER}@${PI_HOST}:~/ASZCam-dev/src/"

# Sync assets
rsync -av assets/ "${PI_USER}@${PI_HOST}:~/ASZCam-dev/assets/"

# Restart service
ssh "${PI_USER}@${PI_HOST}" "sudo systemctl restart asz-cam-os"

echo "Deployment complete"
```

#### Remote Testing

```bash
# Deploy changes
./scripts/deploy_dev.sh

# SSH into Pi and check logs
ssh pi@raspberrypi.local
journalctl -u asz-cam-os -f
```

## API Reference

### Core APIs

#### System Manager API

```python
class SystemManager:
    """System lifecycle management."""
    
    def initialize(self) -> bool:
        """Initialize all system components."""
        
    def shutdown(self) -> None:
        """Shutdown system gracefully."""
        
    def get_system_status(self) -> Dict[str, Any]:
        """Get current system status."""
        
    def restart_service(self, service_name: str) -> bool:
        """Restart a specific service."""
```

#### Camera Service API

```python
class CameraService(QObject):
    """Camera hardware interface."""
    
    # Signals
    photo_captured = pyqtSignal(str)
    preview_frame_ready = pyqtSignal(object)
    error_occurred = pyqtSignal(str)
    camera_status_changed = pyqtSignal(bool)
    
    def capture_photo(
        self, 
        filename: Optional[str] = None,
        settings: Optional[Dict[str, Any]] = None
    ) -> Optional[str]:
        """Capture photo with optional settings override."""
        
    def start_preview(self) -> bool:
        """Start camera preview."""
        
    def stop_preview(self) -> None:
        """Stop camera preview."""
        
    def get_supported_resolutions(self) -> List[Tuple[int, int]]:
        """Get list of supported resolutions."""
        
    def set_camera_setting(self, setting: str, value: Any) -> bool:
        """Configure camera setting."""
```

#### Sync Service API

```python
class SyncService(QObject):
    """Photo synchronization service."""
    
    # Signals
    status_changed = pyqtSignal(str)
    sync_progress = pyqtSignal(int, int)
    photo_synced = pyqtSignal(str)
    error_occurred = pyqtSignal(str)
    
    def start_sync(self, force: bool = False) -> bool:
        """Start synchronization process."""
        
    def sync_photo(self, photo_path: str, priority: int = 1) -> bool:
        """Sync specific photo."""
        
    def get_sync_stats(self) -> Dict[str, Any]:
        """Get synchronization statistics."""
        
    def authenticate_google_photos(self, credentials_path: str) -> bool:
        """Authenticate with Google Photos."""
```

### Configuration API

```python
from src.config.settings import settings

# Access camera settings
resolution = settings.camera.default_resolution
quality = settings.camera.quality

# Modify settings
settings.camera.quality = 95
settings.save_config()

# Access sync settings
sync_enabled = settings.sync.enabled
album_name = settings.sync.album_name

# System settings
photos_dir = settings.system.photos_directory
log_level = settings.system.log_level
```

### Signal/Slot System

```python
# Connect to camera signals
camera_service.photo_captured.connect(self.on_photo_captured)
camera_service.error_occurred.connect(self.on_camera_error)

def on_photo_captured(self, filepath: str):
    """Handle photo captured event."""
    print(f"Photo captured: {filepath}")
    # Trigger sync
    sync_service.sync_photo(filepath, priority=1)

def on_camera_error(self, error_message: str):
    """Handle camera error."""
    print(f"Camera error: {error_message}")
    # Show error dialog
    self.show_error_dialog(error_message)
```

## Testing

### Test Structure

```
tests/
├── unit/                    # Unit tests
│   ├── test_camera_service.py
│   ├── test_sync_service.py
│   ├── test_settings.py
│   └── test_photo_manager.py
├── integration/             # Integration tests
│   ├── test_camera_integration.py
│   ├── test_sync_integration.py
│   └── test_ui_integration.py
├── fixtures/               # Test data and fixtures
│   ├── test_photos/
│   ├── test_configs/
│   └── mock_responses/
└── conftest.py            # Pytest configuration
```

### Unit Testing

#### Test Example

```python
# tests/unit/test_camera_service.py
import pytest
from unittest.mock import Mock, patch, MagicMock
from PyQt6.QtCore import QSignalSpy

from src.camera.camera_service import CameraService, CameraError


@pytest.fixture
def camera_service():
    """Create camera service instance for testing."""
    service = CameraService()
    return service


@pytest.fixture
def mock_backend():
    """Create mock camera backend."""
    backend = Mock()
    backend.initialize.return_value = True
    backend.capture_photo.return_value = b'fake_image_data'
    backend.is_camera_available.return_value = True
    return backend


class TestCameraService:
    """Test camera service functionality."""
    
    def test_initialization_success(self, camera_service, mock_backend):
        """Test successful camera initialization."""
        with patch('src.camera.camera_service.LibCameraBackend', return_value=mock_backend):
            result = camera_service.initialize()
            
            assert result is True
            assert camera_service.is_initialized is True
            mock_backend.initialize.assert_called_once()
    
    def test_initialization_failure(self, camera_service):
        """Test camera initialization failure."""
        with patch('src.camera.camera_service.LibCameraBackend') as mock_class:
            mock_class.return_value.initialize.return_value = False
            
            result = camera_service.initialize()
            
            assert result is False
            assert camera_service.is_initialized is False
    
    def test_photo_capture_success(self, camera_service, mock_backend, tmp_path):
        """Test successful photo capture."""
        camera_service.backend = mock_backend
        camera_service.is_initialized = True
        
        # Mock settings
        with patch('src.camera.camera_service.settings') as mock_settings:
            mock_settings.system.photos_directory = str(tmp_path)
            
            # Set up signal spy
            signal_spy = QSignalSpy(camera_service.photo_captured)
            
            # Capture photo
            result = camera_service.capture_photo()
            
            # Verify results
            assert result is not None
            assert signal_spy.count() == 1
            assert (tmp_path / result.split('/')[-1]).exists()
    
    def test_photo_capture_not_initialized(self, camera_service):
        """Test photo capture when not initialized."""
        signal_spy = QSignalSpy(camera_service.error_occurred)
        
        result = camera_service.capture_photo()
        
        assert result is None
        assert signal_spy.count() == 1
    
    @pytest.mark.asyncio
    async def test_preview_start_stop(self, camera_service, mock_backend):
        """Test preview start and stop operations."""
        camera_service.backend = mock_backend
        camera_service.is_initialized = True
        
        # Start preview
        result = camera_service.start_preview()
        assert result is True
        assert camera_service.preview_active is True
        
        # Stop preview
        camera_service.stop_preview()
        assert camera_service.preview_active is False
```

### Integration Testing

```python
# tests/integration/test_camera_integration.py
import pytest
import tempfile
from pathlib import Path

from src.core.system_manager import SystemManager
from src.camera.camera_service import CameraService
from src.config.settings import Settings


@pytest.fixture
def temp_config_dir():
    """Create temporary configuration directory."""
    with tempfile.TemporaryDirectory() as temp_dir:
        yield temp_dir


@pytest.fixture
def integration_settings(temp_config_dir):
    """Create settings for integration testing."""
    config_file = Path(temp_config_dir) / "test_settings.yaml"
    settings = Settings(str(config_file))
    
    # Override paths for testing
    settings.system.photos_directory = temp_config_dir + "/photos"
    settings.system.data_directory = temp_config_dir + "/data"
    
    return settings


class TestCameraIntegration:
    """Integration tests for camera functionality."""
    
    def test_end_to_end_photo_capture(self, integration_settings):
        """Test complete photo capture workflow."""
        # Initialize system manager
        system_manager = SystemManager()
        system_manager.settings = integration_settings
        
        # Initialize camera service
        camera_service = CameraService()
        assert camera_service.initialize() is True
        
        # Capture photo
        photo_path = camera_service.capture_photo()
        
        # Verify photo was saved
        assert photo_path is not None
        assert Path(photo_path).exists()
        assert Path(photo_path).stat().st_size > 0
        
        # Cleanup
        camera_service.cleanup()
```

### Mock Testing

```python
# tests/conftest.py
import pytest
from unittest.mock import Mock
import numpy as np


@pytest.fixture
def mock_camera_frame():
    """Create mock camera frame data."""
    # Create fake image data (RGB)
    frame = np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)
    return frame


@pytest.fixture
def mock_google_photos_api():
    """Create mock Google Photos API."""
    api = Mock()
    api.initialize.return_value = True
    api.authenticate.return_value = True
    api.upload_photo.return_value = True
    api.is_authenticated.return_value = True
    api.get_upload_stats.return_value = {
        'total_uploads': 10,
        'successful_uploads': 9,
        'failed_uploads': 1,
        'queue_size': 0
    }
    return api
```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=html

# Run specific test file
pytest tests/unit/test_camera_service.py

# Run tests with markers
pytest -m "not slow"

# Run tests verbosely
pytest -v

# Run failed tests only
pytest --lf

# Run tests in parallel
pytest -n auto
```

### Test Configuration

Create `pytest.ini`:
```ini
[tool:pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
markers =
    slow: marks tests as slow (deselect with '-m "not slow"')
    integration: marks tests as integration tests
    unit: marks tests as unit tests
    hardware: marks tests that require hardware
addopts = 
    --strict-markers
    --strict-config
    --tb=short
```

## Contributing Guidelines

### Code Review Process

1. **Create Pull Request**: From feature branch to develop
2. **Automated Checks**: CI runs tests, linting, type checking
3. **Code Review**: At least one reviewer required
4. **Address Feedback**: Make requested changes
5. **Approval**: Reviewer approves changes
6. **Merge**: Squash merge to develop branch

### Code Review Checklist

#### Functionality
- [ ] Code implements required functionality correctly
- [ ] Edge cases are handled appropriately
- [ ] Error handling is comprehensive
- [ ] Performance is acceptable

#### Code Quality
- [ ] Code follows style guidelines
- [ ] Functions and classes are well-documented
- [ ] Variable names are descriptive
- [ ] Code is DRY (Don't Repeat Yourself)

#### Testing
- [ ] Unit tests cover new functionality
- [ ] Integration tests verify end-to-end behavior
- [ ] All tests pass
- [ ] Test coverage is maintained or improved

#### Security
- [ ] No sensitive information in code
- [ ] Input validation is performed
- [ ] Authentication/authorization is proper
- [ ] Dependencies are up to date

### Issue Templates

#### Bug Report Template
```markdown
**Bug Description**
A clear and concise description of what the bug is.

**Steps to Reproduce**
1. Go to '...'
2. Click on '....'
3. Scroll down to '....'
4. See error

**Expected Behavior**
A clear and concise description of what you expected to happen.

**Actual Behavior**
A clear and concise description of what actually happened.

**Environment**
- Raspberry Pi Model: [e.g. Pi 4 4GB]
- OS Version: [e.g. Raspberry Pi OS 64-bit]
- ASZ Cam OS Version: [e.g. 1.0.0]
- Camera Model: [e.g. Pi Camera v3]

**Additional Context**
Add any other context about the problem here.

**Logs**
```
Paste relevant log output here
```
```

#### Feature Request Template
```markdown
**Feature Summary**
A brief description of the feature you'd like to see.

**Problem Statement**
What problem does this feature solve? What use case does it address?

**Proposed Solution**
Describe your preferred solution. How should this feature work?

**Alternative Solutions**
Describe any alternative solutions or features you've considered.

**Implementation Notes**
Any technical considerations or implementation details.

**Additional Context**
Add any other context or screenshots about the feature request here.
```

## Deployment

### Production Build

```bash
# Create production build
./scripts/create_release.sh v1.0.0

# This script:
# 1. Tags the release
# 2. Creates distribution packages
# 3. Runs full test suite
# 4. Generates documentation
# 5. Creates installation packages
```

### Release Process

1. **Version Bump**: Update version numbers
2. **Changelog**: Update CHANGELOG.md
3. **Testing**: Run full test suite on target hardware
4. **Documentation**: Update documentation
5. **Tag Release**: Create git tag
6. **Build Artifacts**: Create installation packages
7. **GitHub Release**: Create release with artifacts

### CI/CD Pipeline

Create `.github/workflows/test.yml`:
```yaml
name: Test Suite

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main, develop ]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: [3.9, 3.10, 3.11]

    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python ${{ matrix.python-version }}
      uses: actions/setup-python@v3
      with:
        python-version: ${{ matrix.python-version }}
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
        pip install -r requirements-dev.txt
    
    - name: Lint with flake8
      run: |
        flake8 src tests
    
    - name: Type check with mypy
      run: |
        mypy src
    
    - name: Test with pytest
      run: |
        pytest --cov=src --cov-report=xml
    
    - name: Upload coverage
      uses: codecov/codecov-action@v3
      with:
        file: ./coverage.xml
```

### Documentation Building

```bash
# Build documentation
cd docs/
make html

# Serve documentation locally
python -m http.server 8000
```

---

This developer guide provides the foundation for contributing to ASZ Cam OS. For questions or clarifications, please open an issue or discussion on the GitHub repository.