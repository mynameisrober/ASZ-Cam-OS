#!/usr/bin/env python3
"""
ASZ Cam OS - Main Application Entry Point
Custom camera operating system for Raspberry Pi with Google Photos integration.

Author: ASZ Development Team
Version: 1.0.0
License: MIT
"""

import sys
import os
from pathlib import Path

# Setup proper package imports - add project root to Python path
current_dir = Path(__file__).parent  # This is src/
project_root = current_dir.parent    # This is the project root
sys.path.insert(0, str(project_root))

from src.core.system_manager import system_manager


def main():
    """Main application entry point."""
    print("=" * 50)
    print("    ASZ Cam OS - Camera Operating System")
    print("         Version 1.0.0")
    print("=" * 50)
    
    try:
        # Initialize the system
        if not system_manager.initialize():
            print("ERROR: System initialization failed")
            return 1
        
        # Run the application
        exit_code = system_manager.run()
        
        # Perform cleanup
        system_manager.shutdown()
        
        return exit_code
        
    except KeyboardInterrupt:
        print("\nShutdown requested by user")
        system_manager.shutdown()
        return 0
    except Exception as e:
        print(f"FATAL ERROR: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
