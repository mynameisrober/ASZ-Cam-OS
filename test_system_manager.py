#!/usr/bin/env python3
"""Test script to verify SystemManager can initialize with MainWindow."""

import sys
import os
from pathlib import Path

# Set up environment
os.environ['ASZ_DEV_MODE'] = 'true'
os.environ['ASZ_MOCK_CAMERA'] = 'true'
os.environ['ASZ_TEST_MODE'] = 'true'
os.environ['QT_QPA_PLATFORM'] = 'offscreen'

# Add src to path
sys.path.insert(0, 'src')

try:
    from PyQt6.QtWidgets import QApplication
    
    # Create QApplication first
    app = QApplication([])
    
    print("Testing SystemManager initialization...")
    
    # Import and create SystemManager
    from core.system_manager import SystemManager
    system_manager = SystemManager()
    
    print("✓ SystemManager created successfully")
    
    # Test initialization
    success = system_manager.initialize()
    
    if success:
        print("✓ SystemManager initialized successfully!")
        print(f"  - Qt app: {system_manager.app is not None}")
        print(f"  - Main window: {system_manager.main_window is not None}")
        print(f"  - Camera service: {system_manager.camera_service is not None}")
        print(f"  - Sync service: {system_manager.sync_service is not None}")
        
        # Test main window properties
        if system_manager.main_window:
            window = system_manager.main_window
            print(f"  - Window title: '{window.windowTitle()}'")
            print(f"  - Window size: {window.size().width()}x{window.size().height()}")
            
            # Test shutdown
            system_manager.shutdown_requested.emit()
            print("✓ Shutdown signal emitted successfully")
        
    else:
        print("✗ SystemManager initialization failed")
        sys.exit(1)

except Exception as e:
    print(f"✗ Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("✅ All tests passed!")
