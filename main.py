#!/usr/bin/env python3
"""
ASZ Cam OS - Main Application Entry Point
Sistema operativo personalizado para cámara ASZ Cam
"""

import sys
import os
from pathlib import Path

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import Qt
from ui.main_window import MainWindow
from system.camera_service import CameraService

def main():
    """Main application entry point"""
    # Configure application
    app = QApplication(sys.argv)
    app.setApplicationName("ASZ Cam OS")
    app.setApplicationVersion("1.0.0")
    
    # Set high DPI scaling for Raspberry Pi displays
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)
    
    # Initialize camera service
    camera_service = CameraService()
    
    # Create main window
    main_window = MainWindow(camera_service)
    main_window.show()
    
    # Enable fullscreen on Raspberry Pi (can be disabled for development)
    if os.getenv('ASZ_FULLSCREEN', '1') == '1':
        main_window.showFullScreen()
    
    # Start application event loop
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()