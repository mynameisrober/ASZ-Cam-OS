#!/usr/bin/env python3
"""
ASZ Cam OS - Development Test Script
Script para probar la aplicación en modo desarrollo
"""

import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Set development environment
os.environ['ASZ_FULLSCREEN'] = '0'  # Windowed mode for development
os.environ['QT_QPA_PLATFORM'] = 'xcb'  # Use X11 for development

# Import and run main application
from main import main

if __name__ == "__main__":
    print("ASZ Cam OS - Development Mode")
    print("=============================")
    print("Running in windowed mode for development")
    print("Use Ctrl+C to exit")
    print("")
    
    try:
        main()
    except KeyboardInterrupt:
        print("\\nApplication closed by user")
    except Exception as e:
        print(f"\\nError: {e}")
        sys.exit(1)