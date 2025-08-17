"""
ASZ Cam OS - Camera View
The main camera interface for capturing photos.
"""

import logging
from typing import Optional

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFrame, QGridLayout, QSizePolicy
)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from PyQt6.QtGui import QPixmap, QImage, QFont
import numpy as np
import cv2

from config.settings import settings


class CameraView(QWidget):
    """Main camera view widget for photo capture."""
    
    # Signals
    navigation_requested = pyqtSignal(str)
    photo_captured = pyqtSignal(str)
    
    def __init__(self, camera_service=None):
        super().__init__()
        self.logger = logging.getLogger(__name__)
        self.camera_service = camera_service
        
        # UI components
        self.preview_label = None
        self.capture_button = None
        self.status_label = None
        self.controls_frame = None
        
        # Preview state
        self.is_active = False
        self.last_frame = None
        
        self._setup_ui()
        self._connect_signals()
        
        self.logger.info("Camera view initialized")
    
    def _setup_ui(self):
        """Set up the camera view user interface."""
        # Main layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(20)
        
        # Camera preview area
        self._create_preview_area(layout)
        
        # Camera controls
        self._create_controls(layout)
        
        # Status area
        self._create_status_area(layout)
        
        # Apply styles
        self._apply_styles()
    
    def _create_preview_area(self, parent_layout):
        """Create the camera preview area."""
        # Preview frame
        preview_frame = QFrame()
        preview_frame.setFrameStyle(QFrame.Shape.StyledPanel)
        preview_frame.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        
        preview_layout = QVBoxLayout(preview_frame)
        preview_layout.setContentsMargins(0, 0, 0, 0)
        
        # Preview label
        self.preview_label = QLabel()
        self.preview_label.setObjectName("cameraPreview")
        self.preview_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.preview_label.setMinimumSize(640, 480)
        self.preview_label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.preview_label.setScaledContents(True)
        
        # Default preview content
        self._set_default_preview()
        
        preview_layout.addWidget(self.preview_label)
        parent_layout.addWidget(preview_frame)
    
    def _create_controls(self, parent_layout):
        """Create camera control buttons."""
        self.controls_frame = QFrame()
        self.controls_frame.setFixedHeight(100)
        
        controls_layout = QHBoxLayout(self.controls_frame)
        controls_layout.setContentsMargins(20, 10, 20, 10)
        
        # Add stretch before capture button
        controls_layout.addStretch()
        
        # Capture button (main action)
        self.capture_button = QPushButton("📷")
        self.capture_button.setObjectName("captureButton")
        self.capture_button.setToolTip("Capture Photo (Space)")
        self.capture_button.clicked.connect(self.capture_photo)
        
        controls_layout.addWidget(self.capture_button)
        
        # Add stretch after capture button
        controls_layout.addStretch()
        
        parent_layout.addWidget(self.controls_frame)
    
    def _create_status_area(self, parent_layout):
        """Create status information area."""
        self.status_label = QLabel("Ready to capture")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_label.setObjectName("statusLabel")
        
        parent_layout.addWidget(self.status_label)
    
    def _connect_signals(self):
        """Connect camera service signals."""
        if self.camera_service:
            self.camera_service.preview_frame_ready.connect(self._update_preview)
            self.camera_service.photo_captured.connect(self._on_photo_captured)
            self.camera_service.error_occurred.connect(self._on_camera_error)
            self.camera_service.camera_status_changed.connect(self._on_camera_status_changed)
    
    def _apply_styles(self):
        """Apply custom styles to camera view."""
        self.setStyleSheet("""
            QFrame {
                background-color: #FFFFFF;
            }
            
            QLabel#statusLabel {
                font-size: 16pt;
                color: #666666;
                padding: 10px;
            }
        """)
    
    def _set_default_preview(self):
        """Set default preview content when camera is not active."""
        # Create a placeholder image
        placeholder = QPixmap(640, 480)
        placeholder.fill(Qt.GlobalColor.lightGray)
        
        # Add text overlay would require QPainter here
        self.preview_label.setPixmap(placeholder)
        self.preview_label.setText("ASZ Cam OS\n\nCamera Preview")
        self.preview_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
    
    def activate(self):
        """Activate the camera view and start preview."""
        if self.is_active:
            return
        
        self.logger.info("Activating camera view...")
        self.is_active = True
        
        # Update status
        self.status_label.setText("Starting camera...")
        
        # Start camera preview
        if self.camera_service:
            if self.camera_service.start_preview():
                self.status_label.setText("Ready to capture")
                self.capture_button.setEnabled(True)
            else:
                self.status_label.setText("Camera unavailable")
                self.capture_button.setEnabled(False)
        else:
            self.status_label.setText("No camera service available")
            self.capture_button.setEnabled(False)
            self._show_demo_preview()
    
    def deactivate(self):
        """Deactivate the camera view and stop preview."""
        if not self.is_active:
            return
        
        self.logger.info("Deactivating camera view...")
        self.is_active = False
        
        # Stop camera preview
        if self.camera_service:
            self.camera_service.stop_preview()
        
        # Reset to default preview
        self._set_default_preview()
        self.status_label.setText("Camera stopped")
    
    def capture_photo(self):
        """Capture a photo using the camera service."""
        if not self.camera_service:
            self.logger.warning("No camera service available for capture")
            return
        
        if not self.camera_service.is_available():
            self.logger.warning("Camera not available for capture")
            self.status_label.setText("Camera not available")
            return
        
        # Update UI state
        self.capture_button.setEnabled(False)
        self.status_label.setText("Capturing photo...")
        
        # Trigger capture
        try:
            filepath = self.camera_service.capture_photo()
            if filepath:
                self.logger.info(f"Photo captured: {filepath}")
                self.photo_captured.emit(filepath)
            else:
                self.status_label.setText("Capture failed")
                
        except Exception as e:
            self.logger.error(f"Capture failed: {e}")
            self.status_label.setText("Capture failed")
        
        # Re-enable capture button after a short delay
        QTimer.singleShot(1000, lambda: self.capture_button.setEnabled(True))
    
    def _update_preview(self, frame: np.ndarray):
        """Update the preview display with a new frame."""
        if not self.is_active:
            return
        
        try:
            # Convert frame to Qt format
            height, width, channels = frame.shape
            bytes_per_line = channels * width
            
            # Convert BGR to RGB
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            # Create QImage
            q_image = QImage(frame_rgb.data, width, height, bytes_per_line, QImage.Format.Format_RGB888)
            
            # Convert to QPixmap and display
            pixmap = QPixmap.fromImage(q_image)
            
            # Scale pixmap to fit preview label while maintaining aspect ratio
            scaled_pixmap = pixmap.scaled(
                self.preview_label.size(),
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )
            
            self.preview_label.setPixmap(scaled_pixmap)
            self.last_frame = frame
            
        except Exception as e:
            self.logger.error(f"Preview update failed: {e}")
    
    def _show_demo_preview(self):
        """Show a demo preview when no camera service is available."""
        # This could generate a test pattern or show a static image
        try:
            # Create a simple test pattern
            demo_frame = np.zeros((480, 640, 3), dtype=np.uint8)
            demo_frame[:] = (100, 100, 100)  # Gray background
            
            # Add some text (using OpenCV)
            cv2.putText(demo_frame, "ASZ Cam OS", (200, 200), 
                       cv2.FONT_HERSHEY_SIMPLEX, 2, (255, 255, 255), 3)
            cv2.putText(demo_frame, "Demo Mode", (250, 280), 
                       cv2.FONT_HERSHEY_SIMPLEX, 1, (200, 200, 200), 2)
            
            self._update_preview(demo_frame)
            
        except Exception as e:
            self.logger.error(f"Demo preview failed: {e}")
    
    def _on_photo_captured(self, filepath: str):
        """Handle photo captured signal."""
        self.status_label.setText(f"Photo saved!")
        
        # Show brief success message then reset
        QTimer.singleShot(2000, lambda: self.status_label.setText("Ready to capture"))
    
    def _on_camera_error(self, error_message: str):
        """Handle camera error signal."""
        self.logger.error(f"Camera error in view: {error_message}")
        self.status_label.setText(f"Error: {error_message}")
        self.capture_button.setEnabled(False)
        
        # Try to restart after a delay
        QTimer.singleShot(5000, self._try_restart_camera)
    
    def _on_camera_status_changed(self, is_available: bool):
        """Handle camera status change."""
        if is_available:
            self.status_label.setText("Camera ready")
            self.capture_button.setEnabled(True)
        else:
            self.status_label.setText("Camera disconnected")
            self.capture_button.setEnabled(False)
    
    def _try_restart_camera(self):
        """Try to restart the camera after an error."""
        if self.is_active and self.camera_service:
            self.logger.info("Attempting to restart camera...")
            if self.camera_service.start_preview():
                self.status_label.setText("Camera restarted")
                self.capture_button.setEnabled(True)
            else:
                self.status_label.setText("Camera restart failed")
    
    def resizeEvent(self, event):
        """Handle widget resize to maintain preview aspect ratio."""
        super().resizeEvent(event)
        
        # Update preview if we have a frame
        if self.last_frame is not None:
            self._update_preview(self.last_frame)
    
    def get_camera_info(self) -> dict:
        """Get current camera information."""
        if self.camera_service:
            return self.camera_service.get_camera_info()
        return {}
    
    def is_preview_active(self) -> bool:
        """Check if preview is currently active."""
        return self.is_active
