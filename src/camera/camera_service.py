"""
ASZ Cam OS - Camera Service
High-level camera service that manages camera operations and captures.
"""

import logging
from typing import Optional, Tuple, Dict, Any
from pathlib import Path
from datetime import datetime
import threading
import uuid

from PyQt6.QtCore import QObject, pyqtSignal, QTimer
import cv2
import numpy as np
from PIL import Image

from .libcamera_backend import LibCameraBackend
from ..config.settings import settings
import os

# Check if we should use mock camera
USE_MOCK_CAMERA = (
    os.getenv('ASZ_DEV_MODE') == 'true' or
    os.getenv('ASZ_MOCK_CAMERA') == 'true' or
    os.getenv('ASZ_SIMULATION_MODE') == 'true'
)


class CameraService(QObject):
    """Main camera service for photo capture and management."""
    
    # Signals
    photo_captured = pyqtSignal(str)  # filepath
    preview_frame_ready = pyqtSignal(np.ndarray)  # frame data
    error_occurred = pyqtSignal(str)  # error message
    camera_status_changed = pyqtSignal(bool)  # is_available
    
    def __init__(self):
        super().__init__()
        self.logger = logging.getLogger(__name__)
        self.backend: Optional[LibCameraBackend] = None
        self.is_initialized = False
        self.is_capturing = False
        self.preview_active = False
        self.preview_timer = None
        self._lock = threading.Lock()
        
    def initialize(self) -> bool:
        """Initialize the camera service."""
        try:
            self.logger.info("Initializing camera service...")
            
            # Choose backend based on environment
            if USE_MOCK_CAMERA:
                self.logger.info("Using mock camera backend for development")
                from .mock_libcamera import MockLibCamera
                self.backend = MockLibCamera()
            else:
                self.logger.info("Using real libcamera backend")
                self.backend = LibCameraBackend()
            
            if not self.backend.initialize():
                self.error_occurred.emit("Failed to initialize camera backend")
                return False
            
            # Set up preview timer
            if settings.camera.preview_enabled:
                self.preview_timer = QTimer()
                self.preview_timer.timeout.connect(self._update_preview)
                
            self.is_initialized = True
            self.camera_status_changed.emit(True)
            self.logger.info("Camera service initialized successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Camera service initialization failed: {e}")
            self.error_occurred.emit(f"Camera initialization failed: {str(e)}")
            return False
    
    def start_preview(self) -> bool:
        """Start camera preview."""
        if not self.is_initialized or not self.backend:
            self.error_occurred.emit("Camera service not initialized")
            return False
            
        try:
            with self._lock:
                if self.preview_active:
                    return True
                
                if self.backend.start_preview():
                    self.preview_active = True
                    if self.preview_timer:
                        self.preview_timer.start(33)  # ~30 FPS
                    self.logger.info("Camera preview started")
                    return True
                else:
                    self.error_occurred.emit("Failed to start camera preview")
                    return False
                    
        except Exception as e:
            self.logger.error(f"Failed to start preview: {e}")
            self.error_occurred.emit(f"Preview start failed: {str(e)}")
            return False
    
    def stop_preview(self):
        """Stop camera preview."""
        try:
            with self._lock:
                if not self.preview_active:
                    return
                
                if self.preview_timer:
                    self.preview_timer.stop()
                
                if self.backend:
                    self.backend.stop_preview()
                
                self.preview_active = False
                self.logger.info("Camera preview stopped")
                
        except Exception as e:
            self.logger.error(f"Failed to stop preview: {e}")
    
    def _update_preview(self):
        """Update preview frame (called by timer)."""
        if not self.backend or not self.preview_active:
            return
            
        try:
            frame = self.backend.get_preview_frame()
            if frame is not None:
                self.preview_frame_ready.emit(frame)
                
        except Exception as e:
            self.logger.error(f"Preview frame update failed: {e}")
    
    def capture_photo(self, custom_filename: Optional[str] = None) -> Optional[str]:
        """Capture a photo and save it to disk."""
        if not self.is_initialized or not self.backend:
            self.error_occurred.emit("Camera service not initialized")
            return None
            
        if self.is_capturing:
            self.logger.warning("Photo capture already in progress")
            return None
        
        try:
            with self._lock:
                self.is_capturing = True
                
                # Generate filename
                if custom_filename:
                    filename = custom_filename
                else:
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    unique_id = str(uuid.uuid4())[:8]
                    filename = f"ASZ_{timestamp}_{unique_id}.jpg"
                
                # Ensure photos directory exists
                photos_dir = Path(settings.system.photos_directory)
                photos_dir.mkdir(parents=True, exist_ok=True)
                filepath = photos_dir / filename
                
                # Capture photo
                image_data = self.backend.capture_photo(
                    resolution=settings.camera.default_resolution,
                    quality=settings.camera.quality
                )
                
                if image_data is not None:
                    # Save image
                    if self._save_image(image_data, filepath):
                        self.logger.info(f"Photo captured: {filepath}")
                        self.photo_captured.emit(str(filepath))
                        return str(filepath)
                    else:
                        self.error_occurred.emit("Failed to save captured photo")
                        return None
                else:
                    self.error_occurred.emit("Failed to capture photo from camera")
                    return None
                    
        except Exception as e:
            self.logger.error(f"Photo capture failed: {e}")
            self.error_occurred.emit(f"Photo capture failed: {str(e)}")
            return None
        finally:
            self.is_capturing = False
    
    def _save_image(self, image_data: np.ndarray, filepath: Path) -> bool:
        """Save image data to file."""
        try:
            # Convert BGR to RGB if needed
            if len(image_data.shape) == 3 and image_data.shape[2] == 3:
                image_data = cv2.cvtColor(image_data, cv2.COLOR_BGR2RGB)
            
            # Create PIL Image
            if len(image_data.shape) == 3:
                image = Image.fromarray(image_data, 'RGB')
            else:
                image = Image.fromarray(image_data, 'L')
            
            # Save with metadata
            exif_data = self._create_exif_data()
            image.save(
                filepath,
                format='JPEG',
                quality=settings.camera.quality,
                optimize=True,
                exif=exif_data if exif_data else None
            )
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to save image: {e}")
            return False
    
    def _create_exif_data(self) -> Optional[bytes]:
        """Create EXIF data for captured photos."""
        try:
            # Basic EXIF data
            # Note: This is a simplified implementation
            # In a real implementation, you'd use a library like piexif
            return None
            
        except Exception as e:
            self.logger.error(f"Failed to create EXIF data: {e}")
            return None
    
    def get_camera_info(self) -> Dict[str, Any]:
        """Get camera information and capabilities."""
        if not self.backend:
            return {}
        
        return self.backend.get_camera_info()
    
    def set_camera_setting(self, setting: str, value: Any) -> bool:
        """Set a camera setting."""
        if not self.backend:
            return False
        
        return self.backend.set_setting(setting, value)
    
    def get_camera_setting(self, setting: str) -> Any:
        """Get a camera setting value."""
        if not self.backend:
            return None
        
        return self.backend.get_setting(setting)
    
    def cleanup(self):
        """Clean up camera resources."""
        try:
            self.logger.info("Cleaning up camera service...")
            
            # Stop preview
            self.stop_preview()
            
            # Clean up backend
            if self.backend:
                self.backend.cleanup()
            
            self.is_initialized = False
            self.camera_status_changed.emit(False)
            self.logger.info("Camera service cleanup completed")
            
        except Exception as e:
            self.logger.error(f"Camera cleanup failed: {e}")
    
    def is_available(self) -> bool:
        """Check if camera is available."""
        return self.is_initialized and self.backend and self.backend.is_camera_available()
    
    def get_supported_resolutions(self) -> list:
        """Get list of supported camera resolutions."""
        if not self.backend:
            return []
        
        return self.backend.get_supported_resolutions()
    
    def get_supported_formats(self) -> list:
        """Get list of supported image formats."""
        if not self.backend:
            return []
        
        return self.backend.get_supported_formats()
