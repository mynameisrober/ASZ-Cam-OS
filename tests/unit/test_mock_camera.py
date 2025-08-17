"""
Unit tests for Mock LibCamera.
Tests camera simulation functionality without hardware.
"""

import pytest
import numpy as np
import cv2
import time
from pathlib import Path

def test_mock_camera_initialization(mock_camera):
    """Test mock camera initialization."""
    assert mock_camera.is_initialized == True
    assert mock_camera.camera_available == True
    assert mock_camera.is_simulation == True

def test_mock_camera_info(mock_camera):
    """Test mock camera information retrieval."""
    info = mock_camera.get_camera_info()
    
    assert info['backend'] == 'mock_libcamera'
    assert info['available'] == True
    assert info['initialized'] == True
    assert 'model' in info
    assert 'sensor_modes' in info

def test_mock_camera_settings(mock_camera):
    """Test camera settings get/set functionality."""
    # Test setting ISO
    assert mock_camera.set_setting('iso', 400) == True
    assert mock_camera.get_setting('iso') == 400
    
    # Test setting exposure
    assert mock_camera.set_setting('exposure', 2000) == True
    assert mock_camera.get_setting('exposure') == 2000
    
    # Test invalid setting
    assert mock_camera.set_setting('invalid_setting', 100) == False
    assert mock_camera.get_setting('invalid_setting') is None

def test_mock_camera_resolutions(mock_camera):
    """Test supported resolutions."""
    resolutions = mock_camera.get_supported_resolutions()
    
    assert len(resolutions) > 0
    assert (1920, 1080) in resolutions
    assert (640, 480) in resolutions
    
    # All resolutions should be tuples of two integers
    for res in resolutions:
        assert isinstance(res, tuple)
        assert len(res) == 2
        assert isinstance(res[0], int)
        assert isinstance(res[1], int)

def test_mock_camera_formats(mock_camera):
    """Test supported formats."""
    formats = mock_camera.get_supported_formats()
    
    assert 'JPEG' in formats
    assert len(formats) > 0

def test_mock_camera_preview_start_stop(mock_camera):
    """Test preview start and stop functionality."""
    # Initially preview should not be active
    assert mock_camera.preview_active == False
    
    # Start preview
    assert mock_camera.start_preview() == True
    assert mock_camera.preview_active == True
    
    # Get preview frame
    time.sleep(0.1)  # Give it a moment to generate frame
    frame = mock_camera.get_preview_frame()
    assert frame is not None
    assert isinstance(frame, np.ndarray)
    assert len(frame.shape) == 3  # Height, Width, Channels
    
    # Stop preview
    mock_camera.stop_preview()
    assert mock_camera.preview_active == False

def test_mock_camera_preview_frames(mock_camera):
    """Test preview frame generation."""
    mock_camera.start_preview()
    
    # Get multiple frames
    frames = []
    for _ in range(3):
        time.sleep(0.1)
        frame = mock_camera.get_preview_frame()
        if frame is not None:
            frames.append(frame)
    
    mock_camera.stop_preview()
    
    assert len(frames) > 0
    
    # Check frame properties
    for frame in frames:
        assert isinstance(frame, np.ndarray)
        assert len(frame.shape) == 3
        assert frame.dtype == np.uint8

def test_mock_camera_photo_capture(mock_camera):
    """Test photo capture functionality."""
    # Capture photo with default settings
    photo = mock_camera.capture_photo()
    
    assert photo is not None
    assert isinstance(photo, np.ndarray)
    assert len(photo.shape) == 3
    assert photo.dtype == np.uint8
    
    # Check that photo has reasonable dimensions
    height, width, channels = photo.shape
    assert height > 0
    assert width > 0
    assert channels == 3

def test_mock_camera_photo_capture_with_settings(mock_camera):
    """Test photo capture with custom settings."""
    # Set custom resolution
    resolution = (1280, 720)
    quality = 85
    
    photo = mock_camera.capture_photo(resolution=resolution, quality=quality)
    
    assert photo is not None
    assert isinstance(photo, np.ndarray)
    
    # Check that resolution matches
    height, width, channels = photo.shape
    assert (width, height) == resolution
    assert channels == 3

def test_mock_camera_multiple_captures(mock_camera):
    """Test multiple photo captures."""
    photos = []
    
    for i in range(3):
        photo = mock_camera.capture_photo()
        assert photo is not None
        photos.append(photo)
    
    # Should have captured 3 photos
    assert len(photos) == 3
    
    # Photos should be different (counter should increment)
    # At minimum, they shouldn't be identical
    for i in range(1, len(photos)):
        # This comparison may fail if images are identical, but that's unlikely
        # with timestamp differences in generated images
        assert not np.array_equal(photos[0], photos[i])

def test_mock_camera_without_initialization():
    """Test camera behavior without initialization."""
    from camera.mock_libcamera import MockLibCamera
    
    uninitialized_camera = MockLibCamera()
    
    # Should not be initialized
    assert uninitialized_camera.is_initialized == False
    assert uninitialized_camera.camera_available == True  # Mock is always "available"
    
    # Operations should fail gracefully
    assert uninitialized_camera.start_preview() == False
    assert uninitialized_camera.get_preview_frame() is None
    assert uninitialized_camera.capture_photo() is None

def test_mock_camera_cleanup(mock_camera):
    """Test camera cleanup functionality."""
    # Start preview
    mock_camera.start_preview()
    assert mock_camera.preview_active == True
    
    # Cleanup should stop preview
    mock_camera.cleanup()
    
    assert mock_camera.is_initialized == False
    assert mock_camera.camera_available == False
    assert mock_camera.preview_active == False

def test_mock_camera_assets_directory(mock_camera):
    """Test that assets directory is created and managed."""
    assets_dir = mock_camera.assets_dir
    
    assert assets_dir.exists()
    assert assets_dir.is_dir()
    
    # Should have created sample images
    sample_files = list(assets_dir.glob('*.jpg'))
    assert len(sample_files) > 0

@pytest.mark.slow
def test_mock_camera_preview_performance(mock_camera):
    """Test preview frame generation performance."""
    mock_camera.start_preview()
    
    start_time = time.time()
    frame_count = 0
    
    # Count frames for 1 second
    while time.time() - start_time < 1.0:
        frame = mock_camera.get_preview_frame()
        if frame is not None:
            frame_count += 1
        time.sleep(0.01)  # Small delay to not overwhelm
    
    mock_camera.stop_preview()
    
    # Should be generating frames at reasonable rate
    # At least 10 FPS even with processing overhead
    assert frame_count >= 10, f"Only generated {frame_count} frames in 1 second"

def test_mock_camera_concurrent_operations(mock_camera):
    """Test that camera handles concurrent operations correctly."""
    import threading
    
    results = []
    
    def capture_photos():
        for _ in range(3):
            photo = mock_camera.capture_photo()
            results.append(photo is not None)
            time.sleep(0.1)
    
    # Start preview
    mock_camera.start_preview()
    
    # Start photo capture in separate thread
    thread = threading.Thread(target=capture_photos)
    thread.start()
    
    # Continue getting preview frames
    preview_frames = 0
    for _ in range(10):
        frame = mock_camera.get_preview_frame()
        if frame is not None:
            preview_frames += 1
        time.sleep(0.05)
    
    # Wait for photo thread to complete
    thread.join()
    
    mock_camera.stop_preview()
    
    # Both operations should have succeeded
    assert all(results), "Photo captures failed during concurrent preview"
    assert preview_frames > 0, "Preview frames not generated during concurrent captures"

def test_mock_camera_error_handling(mock_camera):
    """Test error handling in various scenarios."""
    # Test capture with invalid resolution
    photo = mock_camera.capture_photo(resolution=(-1, -1))
    # Should still return something (mock is forgiving)
    assert photo is not None
    
    # Test invalid quality values
    photo = mock_camera.capture_photo(quality=0)
    assert photo is not None
    
    photo = mock_camera.capture_photo(quality=200)
    assert photo is not None