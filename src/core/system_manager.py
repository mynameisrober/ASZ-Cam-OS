"""
ASZ Cam OS - System Manager
Central system management for the camera operating system.
Handles initialization, lifecycle, and coordination between modules.
"""

import sys
import logging
import signal
import threading
import time
from pathlib import Path
from typing import Optional

from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QTimer, QObject, pyqtSignal
from PyQt6.QtGui import QFont, QFontDatabase

from ..config.settings import settings


class SystemManager(QObject):
    """Main system manager for ASZ Cam OS."""
    
    # Signals
    shutdown_requested = pyqtSignal()
    camera_error = pyqtSignal(str)
    sync_status_changed = pyqtSignal(bool)
    
    def __init__(self):
        super().__init__()
        self.app: Optional[QApplication] = None
        self.main_window = None
        self.camera_service = None
        self.sync_service = None
        self.shutdown_in_progress = False
        self._setup_logging()
        self._setup_signal_handlers()
        
    def _setup_logging(self):
        """Configure system logging."""
        log_level = getattr(logging, settings.system.log_level.upper())
        
        # Create formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        
        # File handler (if not running in development)
        handlers = [console_handler]
        if settings.system.log_file and not self._is_development():
            try:
                file_handler = logging.FileHandler(settings.system.log_file)
                file_handler.setFormatter(formatter)
                handlers.append(file_handler)
            except Exception as e:
                print(f"Warning: Could not set up file logging: {e}")
        
        # Configure root logger
        logging.basicConfig(
            level=log_level,
            handlers=handlers,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        
        self.logger = logging.getLogger(__name__)
        self.logger.info("ASZ Cam OS System Manager initialized")
    
    def _setup_signal_handlers(self):
        """Set up signal handlers for graceful shutdown."""
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
    
    def _signal_handler(self, signum, frame):
        """Handle system signals for graceful shutdown."""
        self.logger.info(f"Received signal {signum}, initiating shutdown...")
        self.shutdown()
    
    def _is_development(self) -> bool:
        """Check if running in development environment."""
        return not Path("/opt/aszcam").exists()
    
    def initialize(self) -> bool:
        """Initialize the system and all components."""
        try:
            self.logger.info("Initializing ASZ Cam OS...")
            
            # Initialize Qt Application
            if not self._initialize_qt():
                return False
            
            # Load and apply theme
            if not self._load_theme():
                self.logger.warning("Could not load theme, using default")
            
            # Initialize camera service
            if not self._initialize_camera():
                self.logger.error("Failed to initialize camera service")
                return False
            
            # Initialize sync service
            if not self._initialize_sync():
                self.logger.warning("Failed to initialize sync service")
            
            # Initialize main window
            if not self._initialize_main_window():
                self.logger.error("Failed to initialize main window")
                return False
            
            self.logger.info("ASZ Cam OS initialization completed successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"System initialization failed: {e}")
            return False
    
    def _initialize_qt(self) -> bool:
        """Initialize Qt application and load fonts."""
        try:
            # Create QApplication if it doesn't exist
            if not QApplication.instance():
                self.app = QApplication(sys.argv)
                self.app.setApplicationName("ASZ Cam OS")
                self.app.setApplicationVersion("1.0")
                self.app.setOrganizationName("ASZ")
            else:
                self.app = QApplication.instance()
            
            # Load custom fonts
            self._load_fonts()
            
            # Set application properties for kiosk mode
            if settings.ui.fullscreen:
                self.app.setAttribute(0x10000000)  # AA_DisableWindowContextHelpButton
            
            return True
            
        except Exception as e:
            self.logger.error(f"Qt initialization failed: {e}")
            return False
    
    def _load_fonts(self):
        """Load custom fonts from assets."""
        try:
            fonts_path = settings.get_fonts_path() / "SFCamera"
            if fonts_path.exists():
                font_files = [
                    "SFCamera-Regular.otf",
                    "SFCamera-Bold.otf",
                    "SFCamera-Medium.otf",
                    "SFCamera-Semibold.otf"
                ]
                
                for font_file in font_files:
                    font_path = fonts_path / font_file
                    if font_path.exists():
                        font_id = QFontDatabase.addApplicationFont(str(font_path))
                        if font_id == -1:
                            self.logger.warning(f"Failed to load font: {font_file}")
                        else:
                            self.logger.info(f"Loaded font: {font_file}")
                
                # Set default application font
                font = QFont(settings.ui.font_family, settings.ui.font_size)
                self.app.setFont(font)
            else:
                self.logger.warning("SFCamera fonts directory not found")
                
        except Exception as e:
            self.logger.error(f"Font loading failed: {e}")
    
    def _load_theme(self) -> bool:
        """Load and apply the application theme."""
        try:
            theme_path = settings.get_themes_path() / f"{settings.ui.theme}.qss"
            if theme_path.exists() and theme_path.stat().st_size > 0:
                with open(theme_path, 'r') as f:
                    theme_content = f.read()
                    self.app.setStyleSheet(theme_content)
                    self.logger.info(f"Applied theme: {settings.ui.theme}")
                    return True
            else:
                self.logger.warning(f"Theme file not found or empty: {theme_path}")
                return False
                
        except Exception as e:
            self.logger.error(f"Theme loading failed: {e}")
            return False
    
    def _initialize_camera(self) -> bool:
        """Initialize camera service."""
        try:
            from ..camera.camera_service import CameraService
            self.camera_service = CameraService()
            self.camera_service.error_occurred.connect(self.camera_error)
            
            if self.camera_service.initialize():
                self.logger.info("Camera service initialized successfully")
                return True
            else:
                self.logger.error("Camera service initialization failed")
                return False
                
        except ImportError as e:
            self.logger.error(f"Could not import camera service: {e}")
            return False
        except Exception as e:
            self.logger.error(f"Camera initialization failed: {e}")
            return False
    
    def _initialize_sync(self) -> bool:
        """Initialize sync service."""
        try:
            if not settings.sync.enabled:
                self.logger.info("Sync service disabled in settings")
                return True
            
            from ..sync.sync_service import SyncService
            self.sync_service = SyncService()
            self.sync_service.status_changed.connect(self.sync_status_changed)
            
            if self.sync_service.initialize():
                self.logger.info("Sync service initialized successfully")
                return True
            else:
                self.logger.warning("Sync service initialization failed")
                return False
                
        except ImportError as e:
            self.logger.warning(f"Could not import sync service: {e}")
            return False
        except Exception as e:
            self.logger.warning(f"Sync initialization failed: {e}")
            return False
    
    def _initialize_main_window(self) -> bool:
        """Initialize main application window."""
        try:
            from ..ui.main_window import MainWindow
            self.main_window = MainWindow(
                camera_service=self.camera_service,
                sync_service=self.sync_service
            )
            
            # Connect shutdown signal
            self.shutdown_requested.connect(self.main_window.close)
            
            self.logger.info("Main window initialized successfully")
            return True
            
        except ImportError as e:
            self.logger.error(f"Could not import main window: {e}")
            return False
        except Exception as e:
            self.logger.error(f"Main window initialization failed: {e}")
            return False
    
    def run(self) -> int:
        """Run the application main loop."""
        if not self.app or not self.main_window:
            self.logger.error("System not properly initialized")
            return 1
        
        try:
            # Show main window
            if settings.ui.fullscreen:
                self.main_window.showFullScreen()
            else:
                self.main_window.show()
            
            # Hide cursor if configured
            if settings.ui.auto_hide_cursor:
                self._setup_cursor_timer()
            
            self.logger.info("ASZ Cam OS started successfully")
            return self.app.exec()
            
        except Exception as e:
            self.logger.error(f"Application execution failed: {e}")
            return 1
    
    def _setup_cursor_timer(self):
        """Set up timer to auto-hide cursor."""
        self.cursor_timer = QTimer()
        self.cursor_timer.timeout.connect(self._hide_cursor)
        self.cursor_timer.setSingleShot(True)
        self.cursor_timer.start(settings.ui.cursor_timeout)
    
    def _hide_cursor(self):
        """Hide the mouse cursor."""
        if self.main_window:
            self.main_window.setCursor(0)  # Qt.BlankCursor
    
    def shutdown(self):
        """Perform graceful shutdown of the system."""
        if self.shutdown_in_progress:
            return
        
        self.shutdown_in_progress = True
        self.logger.info("Shutting down ASZ Cam OS...")
        
        try:
            # Stop sync service
            if self.sync_service:
                self.sync_service.stop()
            
            # Stop camera service
            if self.camera_service:
                self.camera_service.cleanup()
            
            # Close main window
            if self.main_window:
                self.main_window.close()
            
            # Save configuration
            settings.save_config()
            
            # Quit application
            if self.app:
                self.app.quit()
            
            self.logger.info("ASZ Cam OS shutdown completed")
            
        except Exception as e:
            self.logger.error(f"Error during shutdown: {e}")


# Global system manager instance
system_manager = SystemManager()