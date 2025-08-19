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
import argparse
from pathlib import Path

# Setup proper package imports - add project root to Python path
current_dir = Path(__file__).parent  # This is src/
project_root = current_dir.parent    # This is the project root
sys.path.insert(0, str(project_root))

from src.core.system_manager import system_manager


def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="ASZ Cam OS - Custom camera operating system",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py                     # Normal operation with camera
  python main.py --no-camera         # Run without camera requirement
  python main.py --demo              # Demo mode with mock camera
  python main.py --mock-camera       # Use mock camera for development
        """
    )
    
    camera_group = parser.add_mutually_exclusive_group()
    camera_group.add_argument(
        '--no-camera', 
        action='store_true',
        help='Run without camera requirement (camera service optional)'
    )
    camera_group.add_argument(
        '--demo', 
        action='store_true',
        help='Enable demo mode with mock camera and sample data'
    )
    camera_group.add_argument(
        '--mock-camera', 
        action='store_true',
        help='Use mock camera backend for development'
    )
    
    parser.add_argument(
        '--fullscreen', 
        action='store_true',
        help='Force fullscreen mode (overrides settings)'
    )
    parser.add_argument(
        '--windowed', 
        action='store_true',
        help='Force windowed mode (overrides settings)'
    )
    parser.add_argument(
        '--log-level', 
        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'],
        help='Set logging level (overrides settings)'
    )
    
    return parser.parse_args()


def main():
    """Main application entry point."""
    args = parse_arguments()
    
    print("=" * 50)
    print("    ASZ Cam OS - Camera Operating System")
    print("         Version 1.0.0")
    
    # Show mode information
    if args.no_camera:
        print("         Mode: No Camera")
    elif args.demo:
        print("         Mode: Demo (Mock Camera)")
    elif args.mock_camera:
        print("         Mode: Development (Mock Camera)")
    else:
        print("         Mode: Normal Operation")
    
    print("=" * 50)
    
    try:
        # Set environment variables based on arguments
        if args.demo or args.mock_camera:
            os.environ['ASZ_MOCK_CAMERA'] = 'true'
        
        # Configure camera mode for system manager  
        camera_config = {
            'required': False,  # Changed from 'not args.no_camera' to make camera optional by default
            'use_mock': args.demo or args.mock_camera,
            'demo_mode': args.demo
        }
        
        # Only require camera if explicitly running in normal mode
        if not (args.no_camera or args.demo or args.mock_camera):
            # In normal mode, try to use camera but don't fail if not available
            camera_config['required'] = False
        
        # Initialize the system
        if not system_manager.initialize(camera_config=camera_config):
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
