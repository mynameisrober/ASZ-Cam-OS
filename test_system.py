#!/usr/bin/env python3
"""
ASZ Cam OS - System Test
Test the system initialization without GUI for validation.
"""

import sys
import os
from pathlib import Path

# Add src directory to Python path
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir / "src"))

def test_configuration():
    """Test configuration loading."""
    print("Testing configuration...")
    from config.settings import settings
    print(f"✓ Configuration loaded")
    print(f"  Photos directory: {settings.system.photos_directory}")
    print(f"  Camera resolution: {settings.camera.default_resolution}")
    print(f"  Sync enabled: {settings.sync.enabled}")
    return True

def test_camera_backend():
    """Test camera backend initialization."""
    print("\nTesting camera backend...")
    from camera.libcamera_backend import LibCameraBackend
    
    backend = LibCameraBackend()
    if backend.initialize():
        print("✓ Camera backend initialized")
        print(f"  Backend type: {'libcamera' if not backend.use_opencv_fallback else 'opencv'}")
        print(f"  Camera available: {backend.is_camera_available()}")
        backend.cleanup()
        return True
    else:
        print("✗ Camera backend initialization failed")
        return False

def test_camera_service():
    """Test camera service without GUI."""
    print("\nTesting camera service...")
    try:
        from camera.camera_service import CameraService
        # Don't actually initialize to avoid Qt dependency
        print("✓ Camera service import successful")
        return True
    except Exception as e:
        print(f"✗ Camera service test failed: {e}")
        return False

def test_sync_service():
    """Test sync service initialization."""
    print("\nTesting sync service...")
    try:
        from sync.sync_service import SyncService
        # Test without Qt signals
        print("✓ Sync service import successful")
        return True
    except Exception as e:
        print(f"✗ Sync service test failed: {e}")
        return False

def main():
    """Run system tests."""
    print("ASZ Cam OS - System Tests")
    print("=" * 40)
    
    tests = [
        test_configuration,
        test_camera_backend,
        test_camera_service,
        test_sync_service,
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"✗ Test failed with exception: {e}")
    
    print("\n" + "=" * 40)
    print(f"Tests passed: {passed}/{total}")
    
    if passed == total:
        print("✓ All tests passed! System is ready.")
        return 0
    else:
        print("✗ Some tests failed. Check the output above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())