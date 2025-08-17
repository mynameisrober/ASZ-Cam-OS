"""
Basic test to verify development environment setup without GUI dependencies.
"""

import pytest
import sys
import os
from pathlib import Path

# Add src to path for imports
project_root = Path(__file__).parent.parent.parent
src_dir = project_root / 'src'
sys.path.insert(0, str(src_dir))

# Set test environment
os.environ['ASZ_DEV_MODE'] = 'true'
os.environ['ASZ_SIMULATION_MODE'] = 'true'
os.environ['ASZ_TEST_MODE'] = 'true'
os.environ['ASZ_MOCK_CAMERA'] = 'true'
os.environ['ASZ_MOCK_RPI'] = 'true'


def test_python_version():
    """Test Python version is adequate."""
    assert sys.version_info >= (3, 9), "Python 3.9+ required"


def test_basic_imports():
    """Test that basic dependencies can be imported."""
    try:
        import numpy
        import cv2
        import PIL
        assert True
    except ImportError as e:
        pytest.fail(f"Basic import failed: {e}")


def test_mock_camera_import():
    """Test that mock camera can be imported."""
    try:
        from camera.mock_libcamera import MockLibCamera
        mock_camera = MockLibCamera()
        assert mock_camera is not None
        assert hasattr(mock_camera, 'is_simulation')
    except ImportError as e:
        pytest.fail(f"Mock camera import failed: {e}")


def test_mock_camera_initialization():
    """Test mock camera initialization."""
    from camera.mock_libcamera import MockLibCamera
    
    camera = MockLibCamera()
    assert camera.initialize() == True
    assert camera.is_initialized == True
    assert camera.camera_available == True
    
    # Test cleanup
    camera.cleanup()


def test_rpi_simulator_import():
    """Test that RPi simulator can be imported."""
    try:
        from core.rpi_simulator import RPiSimulator
        simulator = RPiSimulator()
        assert simulator.is_simulation == True
    except ImportError as e:
        pytest.fail(f"RPi simulator import failed: {e}")


def test_rpi_simulator_basic_functionality():
    """Test basic RPi simulator functionality."""
    from core.rpi_simulator import RPiSimulator
    
    simulator = RPiSimulator()
    
    # Test system info
    info = simulator.get_system_info()
    assert isinstance(info, dict)
    assert 'model' in info
    assert 'is_simulation' in info
    assert info['is_simulation'] == True
    
    # Test GPIO
    assert simulator.gpio_setup(18, 'OUT') == True
    assert simulator.gpio_output(18, True) == True
    
    gpio_state = simulator.get_gpio_state()
    assert 18 in gpio_state
    assert gpio_state[18]['value'] == True
    
    simulator.cleanup()


def test_mock_camera_photo_capture():
    """Test mock camera photo capture without GUI."""
    from camera.mock_libcamera import MockLibCamera
    import numpy as np
    
    camera = MockLibCamera()
    camera.initialize()
    
    # Capture photo
    photo = camera.capture_photo()
    
    assert photo is not None
    assert isinstance(photo, np.ndarray)
    assert len(photo.shape) == 3  # Height, Width, Channels
    
    camera.cleanup()


def test_mock_camera_settings():
    """Test mock camera settings."""
    from camera.mock_libcamera import MockLibCamera
    
    camera = MockLibCamera()
    camera.initialize()
    
    # Test setting values
    assert camera.set_setting('iso', 400) == True
    assert camera.get_setting('iso') == 400
    
    assert camera.set_setting('exposure', 2000) == True
    assert camera.get_setting('exposure') == 2000
    
    camera.cleanup()


def test_environment_detection():
    """Test that environment variables are properly detected."""
    # These should be set by our test setup
    assert os.getenv('ASZ_DEV_MODE') == 'true'
    assert os.getenv('ASZ_MOCK_CAMERA') == 'true'
    assert os.getenv('ASZ_MOCK_RPI') == 'true'


if __name__ == '__main__':
    # Run tests directly without pytest to avoid GUI dependencies
    print("Running basic development environment tests...")
    
    try:
        test_python_version()
        print("✓ Python version check passed")
        
        test_basic_imports()
        print("✓ Basic imports test passed")
        
        test_mock_camera_import()
        print("✓ Mock camera import test passed")
        
        test_mock_camera_initialization()
        print("✓ Mock camera initialization test passed")
        
        test_rpi_simulator_import()
        print("✓ RPi simulator import test passed")
        
        test_rpi_simulator_basic_functionality()
        print("✓ RPi simulator functionality test passed")
        
        test_mock_camera_photo_capture()
        print("✓ Mock camera photo capture test passed")
        
        test_mock_camera_settings()
        print("✓ Mock camera settings test passed")
        
        test_environment_detection()
        print("✓ Environment detection test passed")
        
        print("\n🎉 All development environment tests passed!")
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)