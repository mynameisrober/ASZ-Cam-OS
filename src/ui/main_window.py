"""
ASZ Cam OS - Main Window
Main application window that displays camera preview and controls.
"""

import logging

from PyQt6.QtWidgets import (
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QFrame,
    QSizePolicy,
)
from PyQt6.QtCore import Qt, pyqtSlot
from PyQt6.QtGui import QPixmap, QImage, QFont
import numpy as np
import cv2

try:
    from ..config.settings import settings
except ImportError:
    # Handle relative import issues when running standalone
    import sys
    from pathlib import Path

    if str(Path(__file__).parent.parent) not in sys.path:
        sys.path.insert(0, str(Path(__file__).parent.parent))
    from config.settings import settings


class MainWindow(QMainWindow):
    """Main application window for ASZ Cam OS."""

    def __init__(self, camera_service=None, sync_service=None):
        super().__init__()
        self.logger = logging.getLogger(__name__)
        self.camera_service = camera_service
        self.sync_service = sync_service

        self._setup_ui()
        self._connect_signals()

        self.logger.info("Main window initialized")

    def _setup_ui(self):
        """Set up the user interface."""
        # Set window properties
        self.setWindowTitle("ASZ Cam OS")
        self.setMinimumSize(800, 600)

        # Use development window size if not fullscreen
        if not settings.ui.fullscreen:
            self.resize(1024, 768)

        # Create central widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Main layout
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)

        # Camera preview area (left side)
        self._setup_preview_area(main_layout)

        # Control panel (right side)
        self._setup_control_panel(main_layout)

        # Status bar
        self.statusBar().showMessage("ASZ Cam OS - Ready")

    def _setup_preview_area(self, parent_layout):
        """Set up the camera preview area."""
        # Preview frame
        preview_frame = QFrame()
        preview_frame.setFrameStyle(QFrame.Shape.Box)
        preview_frame.setLineWidth(2)
        preview_frame.setMinimumSize(640, 480)
        preview_frame.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        # Preview layout
        preview_layout = QVBoxLayout(preview_frame)
        preview_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Preview label for camera feed
        self.preview_label = QLabel()
        self.preview_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.preview_label.setStyleSheet(
            "background-color: #2c3e50; color: white; font-size: 18px;"
        )
        self.preview_label.setText("Camera Preview\n\nWaiting for camera...")
        self.preview_label.setMinimumSize(640, 480)
        self.preview_label.setScaledContents(True)

        preview_layout.addWidget(self.preview_label)

        parent_layout.addWidget(preview_frame, 3)  # 3/4 of the width

    def _setup_control_panel(self, parent_layout):
        """Set up the control panel."""
        # Control panel frame
        control_frame = QFrame()
        control_frame.setFrameStyle(QFrame.Shape.Box)
        control_frame.setLineWidth(1)
        control_frame.setMaximumWidth(250)
        control_frame.setMinimumWidth(200)

        # Control layout
        control_layout = QVBoxLayout(control_frame)
        control_layout.setSpacing(10)
        control_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        # Title
        title_label = QLabel("Camera Controls")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setFont(
            QFont(settings.ui.font_family, settings.ui.font_size + 2, QFont.Weight.Bold)
        )
        title_label.setStyleSheet("color: #2c3e50; padding: 10px;")
        control_layout.addWidget(title_label)

        # Capture button
        self.capture_button = QPushButton("📷 Capture Photo")
        self.capture_button.setMinimumHeight(50)
        self.capture_button.setStyleSheet(
            """
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                border-radius: 8px;
                font-size: 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
            QPushButton:pressed {
                background-color: #1f618d;
            }
        """
        )
        self.capture_button.clicked.connect(self._capture_photo)
        control_layout.addWidget(self.capture_button)

        # Status information
        status_frame = QFrame()
        status_frame.setFrameStyle(QFrame.Shape.StyledPanel)
        status_layout = QVBoxLayout(status_frame)

        # Camera status
        self.camera_status_label = QLabel("Camera: Initializing...")
        self.camera_status_label.setWordWrap(True)
        status_layout.addWidget(self.camera_status_label)

        # Sync status
        self.sync_status_label = QLabel("Sync: Ready")
        self.sync_status_label.setWordWrap(True)
        status_layout.addWidget(self.sync_status_label)

        control_layout.addWidget(status_frame)

        # Add stretch to push everything to top
        control_layout.addStretch()

        parent_layout.addWidget(control_frame, 1)  # 1/4 of the width

    def _connect_signals(self):
        """Connect service signals to UI updates."""
        if self.camera_service:
            # Connect camera service signals
            self.camera_service.preview_frame_ready.connect(self._update_preview)
            self.camera_service.photo_captured.connect(self._on_photo_captured)
            self.camera_service.error_occurred.connect(self._on_camera_error)
            self.camera_service.camera_status_changed.connect(self._on_camera_status_changed)

            # Start preview if camera is available
            if self.camera_service.is_initialized:
                self.camera_service.start_preview()
                self.camera_status_label.setText("Camera: Active")
        else:
            self.camera_status_label.setText("Camera: Not available")

        if self.sync_service:
            # Connect sync service signals if needed
            # sync_service.status_changed.connect(self._on_sync_status_changed)
            pass

    @pyqtSlot(np.ndarray)
    def _update_preview(self, frame):
        """Update camera preview with new frame."""
        try:
            # Convert numpy array to QImage
            if frame is not None and frame.size > 0:
                height, width = frame.shape[:2]

                # Convert BGR to RGB
                if len(frame.shape) == 3:
                    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                else:
                    rgb_frame = frame

                # Create QImage
                bytes_per_line = 3 * width
                q_image = QImage(
                    rgb_frame.data, width, height, bytes_per_line, QImage.Format.Format_RGB888
                )

                # Convert to pixmap and set to label
                pixmap = QPixmap.fromImage(q_image)
                scaled_pixmap = pixmap.scaled(
                    self.preview_label.size(),
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation,
                )
                self.preview_label.setPixmap(scaled_pixmap)

        except Exception as e:
            self.logger.error(f"Failed to update preview: {e}")

    @pyqtSlot(str)
    def _on_photo_captured(self, filepath):
        """Handle photo captured event."""
        self.statusBar().showMessage(f"Photo saved: {filepath}", 3000)
        self.logger.info(f"Photo captured: {filepath}")

    @pyqtSlot(str)
    def _on_camera_error(self, error_message):
        """Handle camera error."""
        self.camera_status_label.setText(f"Camera: Error - {error_message}")
        self.statusBar().showMessage(f"Camera Error: {error_message}", 5000)
        self.logger.error(f"Camera error: {error_message}")

    @pyqtSlot(bool)
    def _on_camera_status_changed(self, is_available):
        """Handle camera status change."""
        if is_available:
            self.camera_status_label.setText("Camera: Active")
            self.capture_button.setEnabled(True)
            if self.camera_service:
                self.camera_service.start_preview()
        else:
            self.camera_status_label.setText("Camera: Not available")
            self.capture_button.setEnabled(False)
            self.preview_label.setText("Camera Preview\n\nCamera not available")

    def _capture_photo(self):
        """Capture a photo."""
        if self.camera_service and self.camera_service.is_initialized:
            try:
                # Trigger photo capture
                self.camera_service.capture_photo()
                self.statusBar().showMessage("Capturing photo...", 2000)
            except Exception as e:
                self.logger.error(f"Failed to capture photo: {e}")
                self.statusBar().showMessage(f"Capture failed: {e}", 3000)
        else:
            self.statusBar().showMessage("Camera not available", 2000)

    def closeEvent(self, event):
        """Handle window close event."""
        self.logger.info("Main window closing")

        # Stop camera preview
        if self.camera_service:
            self.camera_service.stop_preview()

        event.accept()

    def close(self):
        """Close the main window."""
        self.logger.info("Close requested")
        super().close()
