#!/usr/bin/env python3
"""
ASZ Cam OS - Development Mode Runner
Run ASZ Cam OS in development mode with simulation/mock features enabled.

Author: ASZ Development Team
Version: 1.0.0
"""

import os
import sys
import argparse
import logging
import platform
from pathlib import Path

# Add src to path
current_dir = Path(__file__).parent
project_root = current_dir.parent
src_dir = project_root / 'src'
sys.path.insert(0, str(src_dir))

def setup_logging(log_level: str = 'DEBUG', log_to_file: bool = True):
    """Setup logging for development mode."""
    # Create logs directory
    log_dir = project_root / 'logs'
    log_dir.mkdir(exist_ok=True)
    
    # Configure logging
    log_handlers = [logging.StreamHandler(sys.stdout)]
    
    if log_to_file:
        log_file = log_dir / 'aszcam_dev.log'
        log_handlers.append(logging.FileHandler(str(log_file)))
    
    logging.basicConfig(
        level=getattr(logging, log_level.upper()),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=log_handlers
    )
    
    # Log startup info
    logger = logging.getLogger(__name__)
    logger.info("ASZ Cam OS Development Mode Starting")
    logger.info(f"Platform: {platform.system()} {platform.release()}")
    logger.info(f"Python: {platform.python_version()}")
    logger.info(f"Project root: {project_root}")

def setup_dev_environment(args):
    """Setup development environment variables and configurations."""
    
    # Set base development environment variables
    os.environ['ASZ_DEV_MODE'] = 'true'
    os.environ['ASZ_SIMULATION_MODE'] = 'true'
    os.environ['PYTHONPATH'] = str(src_dir)
    
    # Camera mock settings
    if args.mock_camera:
        os.environ['ASZ_MOCK_CAMERA'] = 'true'
    
    # RPi simulation settings
    if args.mock_rpi:
        os.environ['ASZ_MOCK_RPI'] = 'true'
    
    # UI settings for development
    if args.windowed:
        os.environ['ASZ_WINDOWED_MODE'] = 'true'
        os.environ['ASZ_WINDOW_SIZE'] = '1024x768'
    
    # Test mode settings
    if args.test_mode:
        os.environ['ASZ_TEST_MODE'] = 'true'
        os.environ['ASZ_DEBUG_UI'] = 'true'
    
    # Disable features that don't work in development
    os.environ['ASZ_DISABLE_FULLSCREEN'] = 'true'
    os.environ['ASZ_DISABLE_SYSTEMD'] = 'true'
    os.environ['ASZ_DISABLE_GPIO'] = 'true'
    
    # Storage paths for development
    dev_photos_dir = project_root / 'dev_photos'
    dev_photos_dir.mkdir(exist_ok=True)
    os.environ['ASZ_PHOTOS_PATH'] = str(dev_photos_dir)
    
    temp_dir = project_root / 'temp'
    temp_dir.mkdir(exist_ok=True)
    os.environ['ASZ_TEMP_PATH'] = str(temp_dir)
    
    # Assets path
    assets_dir = project_root / 'assets'
    assets_dir.mkdir(exist_ok=True)
    os.environ['ASZ_ASSETS_PATH'] = str(assets_dir)

def print_dev_info(args):
    """Print development mode information."""
    print("=" * 60)
    print("ASZ Cam OS - Development Mode")
    print("=" * 60)
    print(f"Platform: {platform.system()} {platform.release()}")
    print(f"Python: {platform.python_version()}")
    print(f"Project root: {project_root}")
    print()
    print("Development Settings:")
    print(f"  Mock Camera: {args.mock_camera}")
    print(f"  Mock RPi: {args.mock_rpi}")
    print(f"  Log Level: {args.log_level}")
    print(f"  Windowed Mode: {args.windowed}")
    print(f"  Test Mode: {args.test_mode}")
    print(f"  GUI Backend: {args.gui_backend}")
    print()
    print("Environment Variables Set:")
    for key, value in os.environ.items():
        if key.startswith('ASZ_'):
            print(f"  {key}={value}")
    print("=" * 60)

def check_dependencies():
    """Check if required dependencies are available."""
    logger = logging.getLogger(__name__)
    
    required_modules = [
        'PyQt6',
        'cv2',
        'numpy',
        'PIL'
    ]
    
    missing_modules = []
    
    for module in required_modules:
        try:
            __import__(module)
            logger.debug(f"✓ {module} available")
        except ImportError:
            logger.error(f"✗ {module} not available")
            missing_modules.append(module)
    
    if missing_modules:
        logger.error("Missing required dependencies:")
        for module in missing_modules:
            logger.error(f"  - {module}")
        logger.error("Run: pip install -r requirements.txt")
        return False
    
    return True

def run_application():
    """Import and run the main application."""
    logger = logging.getLogger(__name__)
    
    try:
        # Import main application
        logger.info("Importing main application...")
        
        # Check if we can import the main modules
        try:
            from core.system_manager import system_manager
            logger.info("✓ System manager imported")
        except ImportError as e:
            logger.error(f"✗ Failed to import system manager: {e}")
            return 1
        
        try:
            from camera.mock_libcamera import MockLibCamera
            logger.info("✓ Mock camera imported")
        except ImportError as e:
            logger.error(f"✗ Failed to import mock camera: {e}")
            return 1
        
        try:
            from core.rpi_simulator import RPiSimulator
            logger.info("✓ RPi simulator imported")
        except ImportError as e:
            logger.error(f"✗ Failed to import RPi simulator: {e}")
            return 1
        
        # Import and run main
        from main import main as app_main
        logger.info("Starting main application...")
        return app_main()
        
    except ImportError as e:
        logger.error(f"Error importing main application: {e}")
        logger.error("Make sure you're running from the project root directory")
        logger.error("Current directory: " + str(Path.cwd()))
        logger.error("Expected src directory: " + str(src_dir))
        return 1
    except KeyboardInterrupt:
        logger.info("Development session interrupted by user")
        return 0
    except Exception as e:
        logger.error(f"Error running development mode: {e}", exc_info=True)
        return 1

def create_test_environment():
    """Create a minimal test environment to verify setup."""
    logger = logging.getLogger(__name__)
    
    try:
        # Test mock camera
        logger.info("Testing mock camera...")
        from camera.mock_libcamera import MockLibCamera
        mock_camera = MockLibCamera()
        if mock_camera.initialize():
            logger.info("✓ Mock camera initialized successfully")
        else:
            logger.error("✗ Mock camera initialization failed")
            return False
        
        # Test RPi simulator
        logger.info("Testing RPi simulator...")
        from core.rpi_simulator import RPiSimulator
        rpi_sim = RPiSimulator()
        system_info = rpi_sim.get_system_info()
        logger.info(f"✓ RPi simulator working - Model: {system_info['model']}")
        
        # Test basic UI components (without actually showing them)
        logger.info("Testing UI imports...")
        try:
            # Set environment to avoid display issues in headless mode
            os.environ['QT_QPA_PLATFORM'] = 'offscreen'
            from PyQt6.QtWidgets import QApplication
            from PyQt6.QtCore import QTimer
            logger.info("✓ UI components can be imported")
        except ImportError as e:
            if 'EGL' in str(e) or 'libGL' in str(e):
                logger.warning("⚠ UI components not available (no display/GL), but this is OK for headless testing")
                logger.info("✓ Development environment is functional without GUI")
            else:
                logger.error(f"UI import failed: {e}")
                return False
        
        return True
        
    except Exception as e:
        logger.error(f"Test environment creation failed: {e}", exc_info=True)
        return False

def main():
    """Main entry point for development mode runner."""
    parser = argparse.ArgumentParser(
        description='ASZ Cam OS Development Mode Runner',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s                     # Run with default settings
  %(prog)s --test-mode         # Run with additional debugging
  %(prog)s --no-mock-camera    # Use real camera (if available)
  %(prog)s --fullscreen        # Run in fullscreen mode
  %(prog)s --log-level INFO    # Set log level to INFO
        """
    )
    
    parser.add_argument('--mock-camera', action='store_true', default=True,
                        help='Use mock camera (default: True)')
    parser.add_argument('--no-mock-camera', dest='mock_camera', action='store_false',
                        help='Disable mock camera')
    parser.add_argument('--mock-rpi', action='store_true', default=True,
                        help='Use RPi simulator (default: True)')
    parser.add_argument('--no-mock-rpi', dest='mock_rpi', action='store_false',
                        help='Disable RPi simulation')
    parser.add_argument('--log-level', choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'],
                        default='DEBUG', help='Log level (default: DEBUG)')
    parser.add_argument('--windowed', action='store_true', default=True,
                        help='Run in windowed mode (default: True)')
    parser.add_argument('--fullscreen', dest='windowed', action='store_false',
                        help='Run in fullscreen mode')
    parser.add_argument('--test-mode', action='store_true',
                        help='Enable test mode with additional debugging')
    parser.add_argument('--gui-backend', choices=['PyQt6', 'PyQt5'], default='PyQt6',
                        help='GUI backend to use (default: PyQt6)')
    parser.add_argument('--test-env-only', action='store_true',
                        help='Only test environment setup, don\'t run app')
    parser.add_argument('--no-log-file', action='store_true',
                        help='Disable logging to file')
    
    args = parser.parse_args()
    
    # Setup logging
    setup_logging(args.log_level, not args.no_log_file)
    
    # Setup development environment
    setup_dev_environment(args)
    
    # Print development info
    print_dev_info(args)
    
    # Check dependencies
    if not check_dependencies():
        print("\nDependency check failed. Please install missing dependencies.")
        print("Run: pip install -r requirements.txt")
        return 1
    
    # Create and test environment
    if not create_test_environment():
        print("\nTest environment creation failed.")
        return 1
    
    # If only testing environment, exit here
    if args.test_env_only:
        print("\n✓ Development environment test completed successfully")
        return 0
    
    print("\nStarting ASZ Cam OS in development mode...")
    print("Press Ctrl+C to stop\n")
    
    # Run the application
    try:
        return run_application()
    except KeyboardInterrupt:
        print("\n\nDevelopment mode stopped by user")
        return 0

if __name__ == '__main__':
    sys.exit(main())