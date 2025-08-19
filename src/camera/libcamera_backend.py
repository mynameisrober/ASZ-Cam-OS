"""
ASZ Cam OS - LibCamera Backend
Low-level camera interface using libcamera for Raspberry Pi.
Falls back to OpenCV for development/testing environments.
"""

import logging
import subprocess
import tempfile
import os
from typing import Optional, Tuple, Dict, Any, List
from pathlib import Path
import threading
import time

import cv2
import numpy as np

from ..config.settings import settings


class LibCameraBackend:
    """LibCamera backend for Raspberry Pi camera operations."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.is_initialized = False
        self.camera_available = False
        self.preview_process = None
        self.current_frame = None
        self.frame_lock = threading.Lock()
        self.use_opencv_fallback = False
        self.opencv_camera = None
        
    def initialize(self) -> bool:
        """Initialize the camera backend."""
        try:
            self.logger.info("Initializing libcamera backend...")
            
            # Check if we're on Raspberry Pi with libcamera
            if self._is_raspberry_pi() and self._check_libcamera():
                self.logger.info("Using libcamera for Raspberry Pi")
                self.use_opencv_fallback = False
                self.camera_available = True
            else:
                self.logger.info("Using OpenCV fallback for development")
                self.use_opencv_fallback = True
                # Try to initialize OpenCV camera
                self.opencv_camera = cv2.VideoCapture(0)
                if self.opencv_camera.isOpened():
                    self.camera_available = True
                else:
                    self.logger.warning("No camera found (OpenCV fallback) - camera features will be unavailable")
                    self.camera_available = False
                    # Don't return False - allow system to continue without camera
            
            self.is_initialized = True
            if self.camera_available:
                self.logger.info("Camera backend initialized successfully")
            else:
                self.logger.info("Camera backend initialized without camera hardware")
            return True
            
        except Exception as e:
            self.logger.error(f"Camera backend initialization failed: {e}")
            # Still allow initialization to succeed, just mark camera as unavailable
            self.is_initialized = True
            self.camera_available = False
            return True
    
    def is_camera_available(self) -> bool:
        """Check if camera hardware is available."""
        return self.is_initialized and self.camera_available
    
    def get_camera_status(self) -> str:
        """Get human-readable camera status."""
        if not self.is_initialized:
            return "Not initialized"
        elif not self.camera_available:
            return "Camera not available"
        elif self.use_opencv_fallback:
            return "Using development camera"
        else:
            return "Camera ready"

    def _is_raspberry_pi(self) -> bool:
        """Check if running on Raspberry Pi."""
        try:
            with open('/proc/cpuinfo', 'r') as f:
                cpuinfo = f.read()
                return 'Raspberry Pi' in cpuinfo or 'BCM' in cpuinfo
        except:
            return False
    
    def _check_libcamera(self) -> bool:
        """Check if libcamera-apps are available."""
        try:
            result = subprocess.run(['libcamera-hello', '--version'], 
                                  capture_output=True, text=True, timeout=5)
            return result.returncode == 0
        except:
            return False
    
    def start_preview(self) -> bool:
        """Start camera preview."""
        if not self.is_initialized or not self.camera_available:
            self.logger.warning("Cannot start preview: camera not available")
            return False
        
        try:
            if self.use_opencv_fallback:
                return self._start_opencv_preview()
            else:
                return self._start_libcamera_preview()
                
        except Exception as e:
            self.logger.error(f"Failed to start preview: {e}")
            return False
    
    def _start_opencv_preview(self) -> bool:
        """Start OpenCV camera preview."""
        if not self.opencv_camera or not self.opencv_camera.isOpened():
            return False
        
        # Set camera properties
        width, height = settings.camera.default_resolution
        self.opencv_camera.set(cv2.CAP_PROP_FRAME_WIDTH, width)
        self.opencv_camera.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
        self.opencv_camera.set(cv2.CAP_PROP_FPS, 30)
        
        self.logger.info("OpenCV preview started")
        return True
    
    def _start_libcamera_preview(self) -> bool:
        """Start libcamera preview (non-blocking)."""
        try:
            # Use libcamera-vid for streaming preview
            width, height = settings.camera.default_resolution
            cmd = [
                'libcamera-vid',
                '--width', str(width),
                '--height', str(height),
                '--framerate', '30',
                '--timeout', '0',  # Continuous
                '--nopreview',     # We'll handle display ourselves
                '--codec', 'mjpeg',
                '--output', '-',   # Output to stdout
                '--flush'
            ]
            
            # Note: This is a simplified approach. In a real implementation,
            # you'd want to use libcamera Python bindings or process the stream
            self.logger.info("LibCamera preview started")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to start libcamera preview: {e}")
            return False
    
    def stop_preview(self):
        """Stop camera preview."""
        try:
            if self.preview_process:
                self.preview_process.terminate()
                self.preview_process.wait(timeout=5)
                self.preview_process = None
            
            self.logger.info("Camera preview stopped")
            
        except Exception as e:
            self.logger.error(f"Failed to stop preview: {e}")
    
    def get_preview_frame(self) -> Optional[np.ndarray]:
        """Get current preview frame."""
        if not self.is_initialized:
            return None
        
        try:
            if self.use_opencv_fallback:
                return self._get_opencv_frame()
            else:
                return self._get_libcamera_frame()
                
        except Exception as e:
            self.logger.error(f"Failed to get preview frame: {e}")
            return None
    
    def _get_opencv_frame(self) -> Optional[np.ndarray]:
        """Get frame from OpenCV camera."""
        if not self.opencv_camera or not self.opencv_camera.isOpened():
            return None
        
        ret, frame = self.opencv_camera.read()
        if ret:
            return frame
        return None
    
    def _get_libcamera_frame(self) -> Optional[np.ndarray]:
        """Get frame from libcamera stream."""
        # This would be implemented with proper libcamera bindings
        # For now, return a placeholder frame for testing
        if self.current_frame is not None:
            with self.frame_lock:
                return self.current_frame.copy()
        
        # Generate a test pattern for development
        width, height = settings.camera.default_resolution
        frame = np.zeros((height, width, 3), dtype=np.uint8)
        frame[:] = (64, 64, 64)  # Grey background
        
        # Add some text
        cv2.putText(frame, "ASZ Cam OS", (50, 100), 
                   cv2.FONT_HERSHEY_SIMPLEX, 2, (255, 255, 255), 3)
        cv2.putText(frame, "LibCamera Mode", (50, 150), 
                   cv2.FONT_HERSHEY_SIMPLEX, 1, (200, 200, 200), 2)
        
        return frame
    
    def capture_photo(self, resolution: Tuple[int, int] = None, 
                     quality: int = 95) -> Optional[np.ndarray]:
        """Capture a high-quality photo."""
        if not self.is_initialized or not self.camera_available:
            self.logger.warning("Cannot capture photo: camera not available")
            return None
        
        try:
            if self.use_opencv_fallback:
                return self._capture_opencv_photo(resolution, quality)
            else:
                return self._capture_libcamera_photo(resolution, quality)
                
        except Exception as e:
            self.logger.error(f"Failed to capture photo: {e}")
            return None
    
    def _capture_opencv_photo(self, resolution: Tuple[int, int], 
                             quality: int) -> Optional[np.ndarray]:
        """Capture photo using OpenCV."""
        if not self.opencv_camera or not self.opencv_camera.isOpened():
            return None
        
        # Set resolution for capture
        if resolution:
            width, height = resolution
            self.opencv_camera.set(cv2.CAP_PROP_FRAME_WIDTH, width)
            self.opencv_camera.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
        
        # Take several frames to let camera adjust
        for _ in range(5):
            ret, frame = self.opencv_camera.read()
            if not ret:
                return None
            time.sleep(0.1)
        
        # Final capture
        ret, frame = self.opencv_camera.read()
        if ret:
            self.logger.info("Photo captured using OpenCV")
            return frame
        
        return None
    
    def _capture_libcamera_photo(self, resolution: Tuple[int, int], 
                                quality: int) -> Optional[np.ndarray]:
        """Capture photo using libcamera-still."""
        try:
            # Create temporary file
            with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as temp_file:
                temp_path = temp_file.name
            
            # Build libcamera-still command
            cmd = ['libcamera-still']
            
            if resolution:
                width, height = resolution
                cmd.extend(['--width', str(width), '--height', str(height)])
            
            cmd.extend([
                '--quality', str(quality),
                '--timeout', '1000',  # 1 second delay
                '--output', temp_path,
                '--nopreview'
            ])
            
            # Execute capture command
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0 and os.path.exists(temp_path):
                # Read the captured image
                image = cv2.imread(temp_path)
                os.unlink(temp_path)  # Clean up temp file
                
                if image is not None:
                    self.logger.info("Photo captured using libcamera-still")
                    return image
            else:
                self.logger.error(f"libcamera-still failed: {result.stderr}")
                if os.path.exists(temp_path):
                    os.unlink(temp_path)
                return None
                
        except subprocess.TimeoutExpired:
            self.logger.error("libcamera-still timeout")
            return None
        except Exception as e:
            self.logger.error(f"libcamera photo capture failed: {e}")
            return None
    
    def get_camera_info(self) -> Dict[str, Any]:
        """Get camera information and capabilities."""
        info = {
            'backend': 'libcamera' if not self.use_opencv_fallback else 'opencv',
            'available': self.camera_available,
            'initialized': self.is_initialized
        }
        
        if self.use_opencv_fallback and self.opencv_camera:
            info.update({
                'width': int(self.opencv_camera.get(cv2.CAP_PROP_FRAME_WIDTH)),
                'height': int(self.opencv_camera.get(cv2.CAP_PROP_FRAME_HEIGHT)),
                'fps': int(self.opencv_camera.get(cv2.CAP_PROP_FPS))
            })
        
        return info
    
    def set_setting(self, setting: str, value: Any) -> bool:
        """Set camera setting."""
        try:
            if self.use_opencv_fallback and self.opencv_camera:
                # Map common settings to OpenCV properties
                property_map = {
                    'brightness': cv2.CAP_PROP_BRIGHTNESS,
                    'contrast': cv2.CAP_PROP_CONTRAST,
                    'saturation': cv2.CAP_PROP_SATURATION,
                    'exposure': cv2.CAP_PROP_EXPOSURE,
                }
                
                if setting in property_map:
                    return self.opencv_camera.set(property_map[setting], value)
            
            # For libcamera, settings would be applied differently
            self.logger.warning(f"Setting {setting} not implemented for current backend")
            return False
            
        except Exception as e:
            self.logger.error(f"Failed to set {setting}: {e}")
            return False
    
    def get_setting(self, setting: str) -> Any:
        """Get camera setting value."""
        try:
            if self.use_opencv_fallback and self.opencv_camera:
                property_map = {
                    'brightness': cv2.CAP_PROP_BRIGHTNESS,
                    'contrast': cv2.CAP_PROP_CONTRAST,
                    'saturation': cv2.CAP_PROP_SATURATION,
                    'exposure': cv2.CAP_PROP_EXPOSURE,
                }
                
                if setting in property_map:
                    return self.opencv_camera.get(property_map[setting])
            
            return None
            
        except Exception as e:
            self.logger.error(f"Failed to get {setting}: {e}")
            return None
    
    def get_supported_resolutions(self) -> List[Tuple[int, int]]:
        """Get list of supported camera resolutions."""
        # Common Raspberry Pi camera resolutions
        resolutions = [
            (640, 480),    # VGA
            (1280, 720),   # HD
            (1920, 1080),  # Full HD
            (2592, 1944),  # Pi Camera v1 max
            (3280, 2464),  # Pi Camera v2 max
        ]
        
        if self.use_opencv_fallback:
            # For OpenCV, test which resolutions work
            tested_resolutions = []
            if self.opencv_camera:
                for width, height in resolutions:
                    self.opencv_camera.set(cv2.CAP_PROP_FRAME_WIDTH, width)
                    self.opencv_camera.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
                    actual_width = int(self.opencv_camera.get(cv2.CAP_PROP_FRAME_WIDTH))
                    actual_height = int(self.opencv_camera.get(cv2.CAP_PROP_FRAME_HEIGHT))
                    if actual_width == width and actual_height == height:
                        tested_resolutions.append((width, height))
            return tested_resolutions
        
        return resolutions
    
    def get_supported_formats(self) -> List[str]:
        """Get list of supported image formats."""
        return ['JPEG', 'PNG', 'BMP']
    
    def is_camera_available(self) -> bool:
        """Check if camera is available."""
        return self.camera_available
    
    def cleanup(self):
        """Clean up camera resources."""
        try:
            self.logger.info("Cleaning up camera backend...")
            
            # Stop any active preview
            self.stop_preview()
            
            # Clean up OpenCV camera
            if self.opencv_camera:
                self.opencv_camera.release()
                self.opencv_camera = None
            
            self.is_initialized = False
            self.camera_available = False
            
            self.logger.info("Camera backend cleanup completed")
            
        except Exception as e:
            self.logger.error(f"Camera backend cleanup failed: {e}")
    
    def __del__(self):
        """Destructor to ensure cleanup."""
        self.cleanup()
