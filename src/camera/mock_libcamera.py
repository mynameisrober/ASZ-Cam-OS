"""
ASZ Cam OS - Mock LibCamera
Advanced camera simulator for development environments without Raspberry Pi hardware.
Provides realistic camera behavior simulation for testing and development.

Author: ASZ Development Team
Version: 1.0.0
"""

import logging
import time
import threading
from typing import Optional, Tuple, Dict, Any, List
from pathlib import Path
import random
import json
import os
import sys

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont

# Handle imports for development environment
try:
    from ..config.settings import settings
except ImportError:
    # Fallback for development/testing
    class MockSettings:
        class Camera:
            default_resolution = (1920, 1080)
        camera = Camera()
    settings = MockSettings()


class MockLibCamera:
    """Mock libcamera implementation for development environments."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.is_initialized = False
        self.camera_available = True
        self.preview_active = False
        self.current_frame = None
        self.frame_lock = threading.Lock()
        self.preview_thread = None
        self.stop_preview_event = threading.Event()
        self.is_simulation = True  # Flag to indicate this is a simulation
        
        # Mock camera settings
        self.settings = {
            'iso': 100,
            'exposure': 1000,  # microseconds
            'brightness': 0.5,
            'contrast': 1.0,
            'saturation': 1.0,
            'sharpness': 1.0,
            'white_balance': 'auto',
            'resolution': (1920, 1080),
            'fps': 30,
            'format': 'JPEG'
        }
        
        # Mock camera info
        self.camera_info = {
            'id': 0,
            'model': 'Mock Pi Camera v2.1',
            'resolution': (3280, 2464),
            'sensor_modes': [
                {'width': 3280, 'height': 2464, 'fps': 15},
                {'width': 1920, 'height': 1080, 'fps': 30},
                {'width': 1296, 'height': 972, 'fps': 42},
                {'width': 640, 'height': 480, 'fps': 90}
            ]
        }
        
        # Sample images counter for realistic variation
        self.capture_counter = 0
        
        # Mock asset directory
        self.assets_dir = Path(__file__).parent.parent.parent / 'assets' / 'mock_images'
        
    def initialize(self) -> bool:
        """Initialize the mock camera."""
        try:
            self.logger.info("Initializing mock libcamera...")
            
            # Simulate initialization delay
            time.sleep(0.5)
            
            # Ensure mock assets directory exists
            self.assets_dir.mkdir(parents=True, exist_ok=True)
            
            # Generate sample images if they don't exist
            self._generate_sample_assets()
            
            self.is_initialized = True
            self.camera_available = True
            
            self.logger.info("Mock libcamera initialized successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Mock camera initialization failed: {e}")
            return False
    
    def _generate_sample_assets(self):
        """Generate sample images for realistic testing."""
        sample_images = [
            'sample_photo_1.jpg',
            'sample_photo_2.jpg', 
            'sample_photo_3.jpg',
            'preview_frame.jpg'
        ]
        
        for img_name in sample_images:
            img_path = self.assets_dir / img_name
            if not img_path.exists():
                self._create_sample_image(img_path, img_name)
    
    def _create_sample_image(self, path: Path, name: str):
        """Create a sample image with realistic content."""
        width, height = self.settings['resolution']
        
        # Create image with PIL for better text rendering
        img = Image.new('RGB', (width, height), color=(70, 130, 180))  # Steel blue background
        draw = ImageDraw.Draw(img)
        
        # Try to use a better font, fallback to default
        try:
            font_size = max(20, width // 50)
            font = ImageFont.truetype("/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf", font_size)
        except:
            try:
                font = ImageFont.load_default()
            except:
                font = None
        
        # Add title text
        title = "ASZ Cam OS - Development Mode"
        if font:
            bbox = draw.textbbox((0, 0), title, font=font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
        else:
            text_width, text_height = 300, 20
        
        title_x = (width - text_width) // 2
        title_y = height // 4
        draw.text((title_x, title_y), title, fill='white', font=font)
        
        # Add image-specific content
        if 'preview' in name:
            subtitle = f"Live Preview - {time.strftime('%H:%M:%S')}"
        else:
            subtitle = f"Sample Photo - {name} - {width}x{height}"
        
        if font:
            bbox = draw.textbbox((0, 0), subtitle, font=font)
            sub_width = bbox[2] - bbox[0]
        else:
            sub_width = 200
        
        sub_x = (width - sub_width) // 2
        sub_y = title_y + text_height + 20
        draw.text((sub_x, sub_y), subtitle, fill='lightgray', font=font)
        
        # Add some visual elements to make it look more realistic
        # Draw some geometric shapes
        for i in range(5):
            x1 = random.randint(0, width - 100)
            y1 = random.randint(height // 2, height - 100)
            x2 = x1 + random.randint(20, 80)
            y2 = y1 + random.randint(20, 80)
            
            color = (
                random.randint(100, 255),
                random.randint(100, 255), 
                random.randint(100, 255)
            )
            draw.rectangle([x1, y1, x2, y2], outline=color, width=2)
        
        # Add technical info
        tech_info = [
            f"ISO: {self.settings['iso']}",
            f"Exposure: {self.settings['exposure']}μs",
            f"Format: {self.settings['format']}",
            f"FPS: {self.settings['fps']}"
        ]
        
        info_y = height - 120
        for i, info in enumerate(tech_info):
            draw.text((20, info_y + i * 25), info, fill='yellow', font=font)
        
        # Convert PIL image to CV2 format and save
        cv_image = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
        cv2.imwrite(str(path), cv_image)
        
        self.logger.debug(f"Created sample image: {path}")
    
    def start_preview(self) -> bool:
        """Start camera preview."""
        if not self.is_initialized:
            return False
        
        if self.preview_active:
            return True
        
        try:
            self.stop_preview_event.clear()
            self.preview_thread = threading.Thread(target=self._preview_loop, daemon=True)
            self.preview_thread.start()
            
            self.preview_active = True
            self.logger.info("Mock camera preview started")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to start preview: {e}")
            return False
    
    def _preview_loop(self):
        """Preview frame generation loop."""
        frame_count = 0
        fps = self.settings['fps']
        frame_interval = 1.0 / fps
        
        while not self.stop_preview_event.is_set():
            start_time = time.time()
            
            # Generate preview frame
            frame = self._generate_preview_frame(frame_count)
            
            # Update current frame thread-safely
            with self.frame_lock:
                self.current_frame = frame
            
            frame_count += 1
            
            # Maintain target FPS
            elapsed = time.time() - start_time
            sleep_time = max(0, frame_interval - elapsed)
            if sleep_time > 0:
                time.sleep(sleep_time)
    
    def _generate_preview_frame(self, frame_count: int) -> np.ndarray:
        """Generate a realistic preview frame."""
        width, height = self.settings['resolution']
        
        # Create base frame
        frame = np.zeros((height, width, 3), dtype=np.uint8)
        frame[:] = (60, 120, 160)  # Blue-grey background
        
        # Add timestamp and frame counter
        timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
        frame_text = f"Preview Frame: {frame_count}"
        
        # Add text using OpenCV
        font = cv2.FONT_HERSHEY_SIMPLEX
        font_scale = max(0.5, width / 1920.0)  # Scale font with resolution
        thickness = max(1, int(width / 1920.0 * 2))
        
        # Main title
        text = "ASZ Cam OS - Live Preview"
        (text_width, text_height), baseline = cv2.getTextSize(text, font, font_scale, thickness)
        text_x = (width - text_width) // 2
        text_y = height // 4
        cv2.putText(frame, text, (text_x, text_y), font, font_scale, (255, 255, 255), thickness)
        
        # Timestamp
        cv2.putText(frame, timestamp, (20, 40), font, font_scale * 0.7, (200, 200, 200), thickness)
        
        # Frame counter
        cv2.putText(frame, frame_text, (20, 80), font, font_scale * 0.7, (200, 200, 200), thickness)
        
        # Camera settings display
        settings_text = [
            f"ISO: {self.settings['iso']}",
            f"Exposure: {self.settings['exposure']}μs",
            f"Resolution: {width}x{height}",
            f"FPS: {self.settings['fps']}"
        ]
        
        for i, setting in enumerate(settings_text):
            cv2.putText(frame, setting, (20, height - 100 + i * 25), 
                       font, font_scale * 0.6, (255, 255, 0), thickness)
        
        # Add some dynamic elements to simulate live preview
        # Moving indicator
        indicator_x = int((frame_count * 5) % width)
        cv2.circle(frame, (indicator_x, height // 2), 5, (0, 255, 0), -1)
        
        # Simulated light meter or focus area
        focus_size = 50
        focus_x = width // 2
        focus_y = height // 2 + int(20 * np.sin(frame_count * 0.1))
        
        cv2.rectangle(frame, 
                     (focus_x - focus_size, focus_y - focus_size),
                     (focus_x + focus_size, focus_y + focus_size),
                     (0, 255, 0), 2)
        
        # Add subtle noise to simulate sensor noise
        noise = np.random.randint(0, 10, frame.shape, dtype=np.uint8)
        frame = cv2.add(frame, noise)
        
        return frame
    
    def stop_preview(self):
        """Stop camera preview."""
        if not self.preview_active:
            return
        
        try:
            self.stop_preview_event.set()
            
            if self.preview_thread and self.preview_thread.is_alive():
                self.preview_thread.join(timeout=2.0)
            
            self.preview_active = False
            
            with self.frame_lock:
                self.current_frame = None
            
            self.logger.info("Mock camera preview stopped")
            
        except Exception as e:
            self.logger.error(f"Failed to stop preview: {e}")
    
    def get_preview_frame(self) -> Optional[np.ndarray]:
        """Get current preview frame."""
        if not self.is_initialized or not self.preview_active:
            return None
        
        with self.frame_lock:
            if self.current_frame is not None:
                return self.current_frame.copy()
        
        return None
    
    def capture_photo(self, resolution: Tuple[int, int] = None, 
                     quality: int = 95) -> Optional[np.ndarray]:
        """Capture a high-quality photo."""
        if not self.is_initialized:
            return None
        
        try:
            # Use specified resolution or current setting
            if resolution:
                width, height = resolution
            else:
                width, height = self.settings['resolution']
            
            # Simulate capture delay (realistic for Pi camera)
            time.sleep(0.5)
            
            # Load existing sample image if available, otherwise generate
            sample_files = list(self.assets_dir.glob('sample_photo_*.jpg'))
            
            if sample_files:
                # Cycle through sample images
                sample_file = sample_files[self.capture_counter % len(sample_files)]
                try:
                    image = cv2.imread(str(sample_file))
                    if image is not None:
                        # Resize to requested resolution
                        image = cv2.resize(image, (width, height))
                        
                        # Add capture metadata overlay
                        self._add_capture_metadata(image, quality)
                        
                        self.capture_counter += 1
                        self.logger.info(f"Photo captured using sample image: {sample_file.name}")
                        return image
                except Exception as e:
                    self.logger.warning(f"Could not load sample image {sample_file}: {e}")
            
            # Generate new image if samples not available
            image = self._generate_capture_image(width, height, quality)
            self.capture_counter += 1
            
            self.logger.info(f"Photo captured (generated): {width}x{height}, quality={quality}")
            return image
            
        except Exception as e:
            self.logger.error(f"Failed to capture photo: {e}")
            return None
    
    def _add_capture_metadata(self, image: np.ndarray, quality: int):
        """Add metadata overlay to captured image."""
        height, width = image.shape[:2]
        
        # Add timestamp in corner
        timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
        font = cv2.FONT_HERSHEY_SIMPLEX
        font_scale = max(0.4, width / 3280.0)
        thickness = max(1, int(width / 3280.0 * 2))
        
        # Semi-transparent overlay for text background
        overlay = image.copy()
        cv2.rectangle(overlay, (width - 300, height - 60), (width, height), (0, 0, 0), -1)
        cv2.addWeighted(overlay, 0.7, image, 0.3, 0, image)
        
        # Add text
        cv2.putText(image, timestamp, (width - 290, height - 35), 
                   font, font_scale, (255, 255, 255), thickness)
        cv2.putText(image, f"Quality: {quality}%", (width - 290, height - 10),
                   font, font_scale, (255, 255, 255), thickness)
    
    def _generate_capture_image(self, width: int, height: int, quality: int) -> np.ndarray:
        """Generate a new capture image."""
        # Create high-quality image
        image = np.zeros((height, width, 3), dtype=np.uint8)
        
        # Gradient background for more realistic look
        for y in range(height):
            gradient_value = int(50 + (y / height) * 100)
            image[y, :] = (gradient_value, gradient_value + 20, gradient_value + 40)
        
        # Add various elements to make it look like a real photo
        font = cv2.FONT_HERSHEY_SIMPLEX
        font_scale = max(0.8, width / 1920.0)
        thickness = max(2, int(width / 1920.0 * 3))
        
        # Main subject simulation
        center_x, center_y = width // 2, height // 2
        cv2.circle(image, (center_x, center_y), min(width, height) // 6, (150, 200, 250), -1)
        cv2.circle(image, (center_x, center_y), min(width, height) // 8, (200, 220, 255), -1)
        
        # Add capture info
        capture_info = [
            "ASZ Cam OS",
            f"Captured: {time.strftime('%Y-%m-%d %H:%M:%S')}",
            f"Resolution: {width}x{height}",
            f"Quality: {quality}%",
            f"ISO: {self.settings['iso']}",
            f"Exposure: {self.settings['exposure']}μs"
        ]
        
        for i, info in enumerate(capture_info):
            y_pos = 50 + i * 30
            cv2.putText(image, info, (30, y_pos), font, font_scale * 0.6, (255, 255, 255), thickness)
        
        return image
    
    def get_camera_info(self) -> Dict[str, Any]:
        """Get mock camera information."""
        return {
            **self.camera_info,
            'backend': 'mock_libcamera',
            'available': self.camera_available,
            'initialized': self.is_initialized,
            'preview_active': self.preview_active,
            'current_settings': self.settings.copy()
        }
    
    def set_setting(self, setting: str, value: Any) -> bool:
        """Set camera setting."""
        try:
            if setting in self.settings:
                old_value = self.settings[setting]
                self.settings[setting] = value
                self.logger.debug(f"Setting {setting}: {old_value} -> {value}")
                return True
            else:
                self.logger.warning(f"Unknown setting: {setting}")
                return False
                
        except Exception as e:
            self.logger.error(f"Failed to set {setting}: {e}")
            return False
    
    def get_setting(self, setting: str) -> Any:
        """Get camera setting value."""
        return self.settings.get(setting)
    
    def get_supported_resolutions(self) -> List[Tuple[int, int]]:
        """Get list of supported camera resolutions."""
        return [(mode['width'], mode['height']) for mode in self.camera_info['sensor_modes']]
    
    def get_supported_formats(self) -> List[str]:
        """Get list of supported image formats."""
        return ['JPEG', 'PNG', 'BMP', 'TIFF']
    
    def is_camera_available(self) -> bool:
        """Check if camera is available."""
        return self.camera_available
    
    def cleanup(self):
        """Clean up camera resources."""
        try:
            self.logger.info("Cleaning up mock camera...")
            
            # Stop preview
            self.stop_preview()
            
            self.is_initialized = False
            self.camera_available = False
            
            self.logger.info("Mock camera cleanup completed")
            
        except Exception as e:
            self.logger.error(f"Mock camera cleanup failed: {e}")
    
    def __del__(self):
        """Destructor to ensure cleanup."""
        self.cleanup()