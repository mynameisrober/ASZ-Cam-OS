"""
ASZ Cam OS - Main Window
The primary application window that manages all UI components.
"""

import logging
from typing import Optional

from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QStackedWidget, QPushButton, QLabel, QFrame
)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from PyQt6.QtGui import QPixmap, QFont

from .camera_view import CameraView
from .gallery_view import GalleryView
from .settings_view import SettingsView
from .memories_view import MemoriesView
from config.settings import settings


class MainWindow(QMainWindow):
    """Main application window for ASZ Cam OS."""
    
    # Signals
    close_requested = pyqtSignal()
    
    def __init__(self, camera_service=None, sync_service=None):
        super().__init__()
        self.logger = logging.getLogger(__name__)
        self.camera_service = camera_service
        self.sync_service = sync_service
        
        # UI Components
        self.central_widget = None
        self.stacked_widget = None
        self.navigation_bar = None
        
        # Views
        self.camera_view = None
        self.gallery_view = None
        self.settings_view = None
        self.memories_view = None
        
        # Navigation buttons
        self.nav_buttons = {}
        
        # Cursor hide timer
        self.cursor_timer = None
        
        self._setup_ui()
        self._setup_navigation()
        self._connect_signals()
        
        # Start with camera view
        self.show_camera_view()
        
        self.logger.info("Main window initialized")
    
    def _setup_ui(self):
        """Set up the main user interface."""
        self.setWindowTitle("ASZ Cam OS")
        self.setMinimumSize(800, 600)
        
        # Set window properties for kiosk mode
        if settings.ui.fullscreen:
            self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
            self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)
        
        # Create central widget
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        
        # Main layout
        main_layout = QVBoxLayout(self.central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Create stacked widget for views
        self.stacked_widget = QStackedWidget()
        
        # Create views
        self._create_views()
        
        # Create navigation bar
        self._create_navigation_bar()
        
        # Add to main layout
        main_layout.addWidget(self.stacked_widget)
        main_layout.addWidget(self.navigation_bar)
        
        # Apply stylesheet
        self._apply_styles()
    
    def _create_views(self):
        """Create all application views."""
        # Camera View
        self.camera_view = CameraView(self.camera_service)
        self.stacked_widget.addWidget(self.camera_view)
        
        # Gallery View
        self.gallery_view = GalleryView()
        self.stacked_widget.addWidget(self.gallery_view)
        
        # Memories View
        self.memories_view = MemoriesView()
        self.stacked_widget.addWidget(self.memories_view)
        
        # Settings View
        self.settings_view = SettingsView()
        self.stacked_widget.addWidget(self.settings_view)
    
    def _create_navigation_bar(self):
        """Create the bottom navigation bar."""
        self.navigation_bar = QFrame()
        self.navigation_bar.setFixedHeight(80)
        self.navigation_bar.setFrameStyle(QFrame.Shape.NoFrame)
        
        nav_layout = QHBoxLayout(self.navigation_bar)
        nav_layout.setContentsMargins(20, 10, 20, 10)
        nav_layout.setSpacing(20)
        
        # Navigation buttons
        nav_items = [
            ("camera", "📷", "Camera"),
            ("gallery", "🖼️", "Photos"), 
            ("memories", "💭", "Memories"),
            ("settings", "⚙️", "Settings")
        ]
        
        for key, icon, text in nav_items:
            button = QPushButton(f"{icon}")
            button.setObjectName(f"nav_{key}")
            button.setToolTip(text)
            button.setFixedSize(60, 60)
            
            # Store reference
            self.nav_buttons[key] = button
            
            # Connect to navigation
            button.clicked.connect(lambda checked, view=key: self._navigate_to(view))
            
            nav_layout.addWidget(button)
        
        # Add stretch to center buttons
        nav_layout.insertStretch(0)
        nav_layout.addStretch()
    
    def _setup_navigation(self):
        """Set up navigation between views."""
        # Set camera as default active button
        if 'camera' in self.nav_buttons:
            self.nav_buttons['camera'].setProperty('active', True)
    
    def _connect_signals(self):
        """Connect signals between components."""
        # Camera service signals
        if self.camera_service:
            self.camera_service.photo_captured.connect(self._on_photo_captured)
            self.camera_service.error_occurred.connect(self._on_camera_error)
        
        # View-specific signals
        if self.camera_view:
            self.camera_view.navigation_requested.connect(self._navigate_to)
        
        # Setup cursor hide timer
        if settings.ui.auto_hide_cursor:
            self._setup_cursor_timer()
    
    def _setup_cursor_timer(self):
        """Set up timer to auto-hide cursor."""
        self.cursor_timer = QTimer()
        self.cursor_timer.timeout.connect(self._hide_cursor)
        self.cursor_timer.setSingleShot(True)
        self.mouseMoveEvent = self._on_mouse_move
    
    def _on_mouse_move(self, event):
        """Handle mouse movement to show/hide cursor."""
        self.setCursor(Qt.CursorShape.ArrowCursor)
        if self.cursor_timer:
            self.cursor_timer.stop()
            self.cursor_timer.start(settings.ui.cursor_timeout)
        super().mouseMoveEvent(event)
    
    def _hide_cursor(self):
        """Hide the mouse cursor."""
        self.setCursor(Qt.CursorShape.BlankCursor)
    
    def _apply_styles(self):
        """Apply custom styles to the main window."""
        # Navigation bar styling
        nav_style = """
        QFrame {
            background-color: #FFFFFF;
            border-top: 1px solid #E0E0E0;
        }
        
        QPushButton[active="true"] {
            background-color: #333333;
            color: #FFFFFF;
            border-radius: 30px;
        }
        
        QPushButton {
            background-color: #F8F8F8;
            border: 1px solid #E0E0E0;
            border-radius: 30px;
            font-size: 18pt;
        }
        
        QPushButton:hover {
            background-color: #F0F0F0;
        }
        """
        
        self.navigation_bar.setStyleSheet(nav_style)
    
    def _navigate_to(self, view_name: str):
        """Navigate to a specific view."""
        try:
            # Update navigation buttons
            for key, button in self.nav_buttons.items():
                button.setProperty('active', key == view_name)
                button.style().unpolish(button)
                button.style().polish(button)
            
            # Switch to the requested view
            if view_name == "camera":
                self.show_camera_view()
            elif view_name == "gallery":
                self.show_gallery_view()
            elif view_name == "memories":
                self.show_memories_view()
            elif view_name == "settings":
                self.show_settings_view()
            
            self.logger.info(f"Navigated to {view_name} view")
            
        except Exception as e:
            self.logger.error(f"Navigation failed: {e}")
    
    def show_camera_view(self):
        """Show the camera view."""
        self.stacked_widget.setCurrentWidget(self.camera_view)
        if self.camera_view:
            self.camera_view.activate()
    
    def show_gallery_view(self):
        """Show the gallery view."""
        self.stacked_widget.setCurrentWidget(self.gallery_view)
        if self.gallery_view:
            self.gallery_view.refresh_photos()
    
    def show_memories_view(self):
        """Show the memories view."""
        self.stacked_widget.setCurrentWidget(self.memories_view)
        if self.memories_view:
            self.memories_view.load_memories()
    
    def show_settings_view(self):
        """Show the settings view."""
        self.stacked_widget.setCurrentWidget(self.settings_view)
        if self.settings_view:
            self.settings_view.load_settings()
    
    def _on_photo_captured(self, filepath: str):
        """Handle photo captured event."""
        self.logger.info(f"Photo captured: {filepath}")
        
        # Update gallery if it's the current view
        if self.stacked_widget.currentWidget() == self.gallery_view:
            self.gallery_view.refresh_photos()
    
    def _on_camera_error(self, error_message: str):
        """Handle camera error."""
        self.logger.error(f"Camera error: {error_message}")
        # Could show an error dialog or notification here
    
    def keyPressEvent(self, event):
        """Handle key press events."""
        # Navigation shortcuts
        key = event.key()
        
        if key == Qt.Key.Key_1:
            self._navigate_to("camera")
        elif key == Qt.Key.Key_2:
            self._navigate_to("gallery")
        elif key == Qt.Key.Key_3:
            self._navigate_to("memories")
        elif key == Qt.Key.Key_4:
            self._navigate_to("settings")
        elif key == Qt.Key.Key_Space:
            # Trigger camera capture if in camera view
            if self.stacked_widget.currentWidget() == self.camera_view:
                self.camera_view.capture_photo()
        elif key == Qt.Key.Key_Escape:
            # Exit fullscreen or close app
            if self.isFullScreen():
                self.showNormal()
            else:
                self.close()
        elif key == Qt.Key.Key_F11:
            # Toggle fullscreen
            if self.isFullScreen():
                self.showNormal()
            else:
                self.showFullScreen()
        
        super().keyPressEvent(event)
    
    def closeEvent(self, event):
        """Handle window close event."""
        self.logger.info("Main window closing...")
        
        # Stop camera preview
        if self.camera_view:
            self.camera_view.deactivate()
        
        # Save settings
        settings.save_config()
        
        # Accept the close event
        event.accept()
        
        # Emit close signal
        self.close_requested.emit()
    
    def get_current_view(self) -> Optional[QWidget]:
        """Get the currently active view."""
        return self.stacked_widget.currentWidget()
    
    def is_camera_view_active(self) -> bool:
        """Check if camera view is currently active."""
        return self.stacked_widget.currentWidget() == self.camera_view
