"""
ASZ Cam OS - Test Configuration
Pytest configuration and fixtures for testing ASZ Cam OS without hardware.

Author: ASZ Development Team
Version: 1.0.0
"""

import pytest
import os
import sys
import tempfile
import shutil
import asyncio
from pathlib import Path
from unittest.mock import Mock, MagicMock, patch
import numpy as np
from typing import Generator, Dict, Any, Optional

# Add src to path for imports
project_root = Path(__file__).parent.parent
src_dir = project_root / 'src'
sys.path.insert(0, str(src_dir))

# Set test environment variables
os.environ['ASZ_DEV_MODE'] = 'true'
os.environ['ASZ_SIMULATION_MODE'] = 'true'
os.environ['ASZ_TEST_MODE'] = 'true'
os.environ['ASZ_MOCK_CAMERA'] = 'true'
os.environ['ASZ_MOCK_RPI'] = 'true'


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def temp_storage(tmp_path) -> Path:
    """Create temporary storage directory for tests."""
    storage_path = tmp_path / "test_storage"
    storage_path.mkdir()
    
    # Create subdirectories
    (storage_path / "photos").mkdir()
    (storage_path / "temp").mkdir()
    (storage_path / "logs").mkdir()
    
    return storage_path


@pytest.fixture
def temp_config(tmp_path) -> Path:
    """Create temporary configuration directory for tests."""
    config_path = tmp_path / "test_config"
    config_path.mkdir()
    
    # Create a basic test configuration
    config_file = config_path / "settings.yaml"
    config_file.write_text("""
camera:
  default_resolution: [1920, 1080]
  default_quality: 95
  mock_enabled: true

sync:
  enabled: false
  auto_start: false

storage:
  photos_path: "test_photos"
  temp_path: "test_temp"

ui:
  fullscreen: false
  window_size: [1024, 768]
""")
    
    return config_path


@pytest.fixture
def mock_camera():
    """Create a mock camera instance."""
    from camera.mock_libcamera import MockLibCamera
    
    camera = MockLibCamera()
    camera.initialize()
    yield camera
    camera.cleanup()


@pytest.fixture
def mock_rpi_simulator():
    """Create a mock RPi simulator instance."""
    from core.rpi_simulator import RPiSimulator
    
    simulator = RPiSimulator()
    yield simulator
    simulator.cleanup()


@pytest.fixture
def mock_camera_frame():
    """Create mock camera frame data."""
    # Create fake image data (RGB)
    height, width = 480, 640
    frame = np.random.randint(0, 255, (height, width, 3), dtype=np.uint8)
    
    # Add some recognizable pattern
    frame[100:120, 100:540] = [255, 0, 0]  # Red stripe
    frame[200:220, 100:540] = [0, 255, 0]  # Green stripe
    frame[300:320, 100:540] = [0, 0, 255]  # Blue stripe
    
    return frame


@pytest.fixture
def mock_photo_data():
    """Create mock photo data for testing."""
    return {
        'filename': 'test_photo_001.jpg',
        'timestamp': '2024-01-01T12:00:00Z',
        'resolution': (1920, 1080),
        'quality': 95,
        'iso': 100,
        'exposure': 1000,
        'size_bytes': 1024000,
        'format': 'JPEG'
    }


@pytest.fixture
def sample_photo_metadata():
    """Sample photo metadata for testing."""
    return {
        'camera': {
            'make': 'Raspberry Pi',
            'model': 'Pi Camera v2.1 (Mock)',
            'lens': 'Fixed focus'
        },
        'settings': {
            'iso': 100,
            'exposure_time': '1/100',
            'aperture': 'f/2.8',
            'focal_length': '3.04mm',
            'white_balance': 'auto'
        },
        'image': {
            'width': 1920,
            'height': 1080,
            'format': 'JPEG',
            'quality': 95,
            'color_space': 'sRGB'
        },
        'capture': {
            'timestamp': '2024-01-01T12:00:00Z',
            'location': None,
            'weather': None
        }
    }


@pytest.fixture
def mock_google_photos_api():
    """Create mock Google Photos API."""
    api = Mock()
    api.initialize.return_value = True
    api.authenticate.return_value = True
    api.upload_photo.return_value = {
        'success': True,
        'id': 'mock_photo_id_123',
        'url': 'https://photos.google.com/mock/123'
    }
    api.is_authenticated.return_value = True
    api.get_upload_stats.return_value = {
        'total_uploads': 10,
        'successful_uploads': 9,
        'failed_uploads': 1,
        'queue_size': 0,
        'last_upload': '2024-01-01T12:00:00Z'
    }
    return api


@pytest.fixture
def mock_system_manager():
    """Create mock system manager."""
    from core.system_manager import SystemManager
    
    with patch('core.system_manager.SystemManager') as MockSystemManager:
        mock_manager = MockSystemManager.return_value
        mock_manager.initialize.return_value = True
        mock_manager.run.return_value = 0
        mock_manager.shutdown.return_value = None
        mock_manager.camera_service = Mock()
        mock_manager.sync_service = Mock()
        mock_manager.main_window = Mock()
        
        yield mock_manager


@pytest.fixture
def mock_settings():
    """Create mock settings."""
    settings = Mock()
    settings.camera = Mock()
    settings.camera.default_resolution = (1920, 1080)
    settings.camera.default_quality = 95
    settings.camera.mock_enabled = True
    
    settings.sync = Mock()
    settings.sync.enabled = False
    settings.sync.auto_start = False
    
    settings.storage = Mock()
    settings.storage.photos_path = "test_photos"
    settings.storage.temp_path = "test_temp"
    
    settings.ui = Mock()
    settings.ui.fullscreen = False
    settings.ui.window_size = (1024, 768)
    
    return settings


@pytest.fixture
def qt_app():
    """Create QApplication instance for GUI tests."""
    from PyQt6.QtWidgets import QApplication
    from PyQt6.QtCore import QTimer
    import sys
    
    # Check if QApplication already exists
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    
    # Set up for testing
    app.setQuitOnLastWindowClosed(False)
    
    yield app
    
    # Clean up
    if app:
        app.processEvents()


@pytest.fixture
def mock_main_window(qt_app):
    """Create mock main window for UI tests."""
    from ui.main_window import MainWindow
    
    with patch('ui.main_window.MainWindow') as MockMainWindow:
        mock_window = MockMainWindow.return_value
        mock_window.show.return_value = None
        mock_window.hide.return_value = None
        mock_window.close.return_value = True
        mock_window.update_preview.return_value = None
        mock_window.update_status.return_value = None
        
        yield mock_window


@pytest.fixture
def capture_logs(caplog):
    """Capture logs with specific configuration for ASZ Cam OS."""
    import logging
    
    # Set up logging for tests
    caplog.set_level(logging.DEBUG)
    
    # Add ASZ Cam OS specific loggers
    loggers = [
        'camera.mock_libcamera',
        'core.rpi_simulator',
        'core.system_manager',
        'ui.main_window',
        'sync.sync_service',
        'storage.photo_manager'
    ]
    
    for logger_name in loggers:
        logger = logging.getLogger(logger_name)
        logger.setLevel(logging.DEBUG)
    
    yield caplog


@pytest.fixture
def network_mock():
    """Mock network operations."""
    with patch('requests.get') as mock_get, \
         patch('requests.post') as mock_post:
        
        # Mock successful responses
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {'status': 'ok'}
        mock_response.text = 'OK'
        
        mock_get.return_value = mock_response
        mock_post.return_value = mock_response
        
        yield {
            'get': mock_get,
            'post': mock_post,
            'response': mock_response
        }


@pytest.fixture
def gpio_mock():
    """Mock GPIO operations."""
    gpio_state = {}
    
    def mock_setup(pin, mode, pull_up_down='OFF'):
        gpio_state[pin] = {'mode': mode, 'pull': pull_up_down, 'value': False}
        return True
    
    def mock_output(pin, value):
        if pin in gpio_state:
            gpio_state[pin]['value'] = value
            return True
        return False
    
    def mock_input(pin):
        if pin in gpio_state:
            return gpio_state[pin]['value']
        return False
    
    def mock_cleanup(pin=None):
        if pin:
            gpio_state.pop(pin, None)
        else:
            gpio_state.clear()
    
    gpio_mock = Mock()
    gpio_mock.setup = Mock(side_effect=mock_setup)
    gpio_mock.output = Mock(side_effect=mock_output)
    gpio_mock.input = Mock(side_effect=mock_input)
    gpio_mock.cleanup = Mock(side_effect=mock_cleanup)
    gpio_mock.state = gpio_state
    
    yield gpio_mock


@pytest.fixture
def file_system_mock(tmp_path):
    """Mock file system operations with temporary directories."""
    
    # Create mock file system structure
    mock_fs = {
        'photos': tmp_path / 'photos',
        'temp': tmp_path / 'temp',
        'config': tmp_path / 'config',
        'logs': tmp_path / 'logs',
        'assets': tmp_path / 'assets'
    }
    
    # Create directories
    for path in mock_fs.values():
        path.mkdir(parents=True, exist_ok=True)
    
    # Create some sample files
    (mock_fs['photos'] / 'sample1.jpg').write_bytes(b'fake_image_data_1')
    (mock_fs['photos'] / 'sample2.jpg').write_bytes(b'fake_image_data_2')
    
    yield mock_fs
    
    # Cleanup is handled by tmp_path


# Test markers
def pytest_configure(config):
    """Configure custom pytest markers."""
    config.addinivalue_line(
        "markers", "unit: mark test as a unit test"
    )
    config.addinivalue_line(
        "markers", "integration: mark test as an integration test"
    )
    config.addinivalue_line(
        "markers", "e2e: mark test as an end-to-end test"
    )
    config.addinivalue_line(
        "markers", "gui: mark test as a GUI test"
    )
    config.addinivalue_line(
        "markers", "slow: mark test as slow running"
    )
    config.addinivalue_line(
        "markers", "hardware: mark test as requiring real hardware"
    )


# Test collection configuration
def pytest_collection_modifyitems(config, items):
    """Modify test collection to add automatic markers."""
    for item in items:
        # Add unit marker to tests in unit directory
        if "unit" in str(item.fspath):
            item.add_marker(pytest.mark.unit)
        
        # Add integration marker to tests in integration directory
        if "integration" in str(item.fspath):
            item.add_marker(pytest.mark.integration)
        
        # Add e2e marker to tests in e2e directory
        if "e2e" in str(item.fspath):
            item.add_marker(pytest.mark.e2e)
        
        # Add gui marker to GUI-related tests
        if "ui" in str(item.fspath) or "gui" in item.name.lower():
            item.add_marker(pytest.mark.gui)
        
        # Add slow marker to tests that might take long
        if "test_full_workflow" in item.name or "test_system" in item.name:
            item.add_marker(pytest.mark.slow)


# Utility functions for tests
def create_test_image(width: int = 640, height: int = 480) -> np.ndarray:
    """Create a test image with known patterns."""
    image = np.zeros((height, width, 3), dtype=np.uint8)
    
    # Add colored sections for easy verification
    image[:height//3] = [255, 0, 0]  # Red
    image[height//3:2*height//3] = [0, 255, 0]  # Green  
    image[2*height//3:] = [0, 0, 255]  # Blue
    
    return image


def create_test_config() -> Dict[str, Any]:
    """Create a test configuration dictionary."""
    return {
        'camera': {
            'default_resolution': [1920, 1080],
            'default_quality': 95,
            'mock_enabled': True,
            'preview_fps': 30
        },
        'sync': {
            'enabled': False,
            'auto_start': False,
            'retry_attempts': 3
        },
        'storage': {
            'photos_path': 'test_photos',
            'temp_path': 'test_temp',
            'max_photos': 1000
        },
        'ui': {
            'fullscreen': False,
            'window_size': [1024, 768],
            'theme': 'dark'
        }
    }


class AsyncMock(MagicMock):
    """Mock class for async methods."""
    async def __call__(self, *args, **kwargs):
        return super().__call__(*args, **kwargs)