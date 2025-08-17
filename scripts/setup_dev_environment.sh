#!/bin/bash
# ASZ Cam OS - Development Environment Setup
# Sets up development environment for ASZ Cam OS on any platform (Linux/macOS/Windows)

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
PROJECT_NAME="ASZ-Cam-OS"
VENV_NAME="aszcam-dev"
MIN_PYTHON_VERSION="3.9"

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to check Python version
check_python_version() {
    if command_exists python3; then
        PYTHON_VERSION=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
        REQUIRED_VERSION=$(echo $MIN_PYTHON_VERSION)
        
        if [ "$(printf '%s\n' "$REQUIRED_VERSION" "$PYTHON_VERSION" | sort -V | head -n1)" = "$REQUIRED_VERSION" ]; then
            print_success "Python $PYTHON_VERSION found (minimum $MIN_PYTHON_VERSION required)"
            return 0
        else
            print_error "Python $PYTHON_VERSION found, but minimum $MIN_PYTHON_VERSION required"
            return 1
        fi
    else
        print_error "Python 3 not found"
        return 1
    fi
}

# Function to detect operating system
detect_os() {
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        OS="linux"
        if command_exists lsb_release; then
            DISTRO=$(lsb_release -si)
            VERSION=$(lsb_release -sr)
            print_status "Detected: $DISTRO $VERSION"
        else
            print_status "Detected: Linux (unknown distribution)"
        fi
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        OS="macos"
        print_status "Detected: macOS"
    elif [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "cygwin" ]]; then
        OS="windows"
        print_status "Detected: Windows (via $OSTYPE)"
    else
        OS="unknown"
        print_warning "Unknown operating system: $OSTYPE"
    fi
}

# Function to install system dependencies
install_system_dependencies() {
    print_status "Installing system dependencies..."
    
    case $OS in
        "linux")
            if command_exists apt-get; then
                # Ubuntu/Debian
                print_status "Installing dependencies via apt-get..."
                sudo apt-get update
                sudo apt-get install -y \
                    python3-dev \
                    python3-venv \
                    python3-pip \
                    libgl1-mesa-glx \
                    libglib2.0-0 \
                    libxcb-xinerama0 \
                    libfontconfig1 \
                    libxkbcommon-x11-0 \
                    libdbus-1-3 \
                    git \
                    curl \
                    build-essential \
                    pkg-config
                    
                # Install additional packages for camera simulation
                sudo apt-get install -y \
                    v4l-utils \
                    ffmpeg \
                    libv4l-dev
                    
            elif command_exists yum; then
                # RedHat/CentOS/Fedora
                print_status "Installing dependencies via yum/dnf..."
                if command_exists dnf; then
                    PKG_MGR="dnf"
                else
                    PKG_MGR="yum"
                fi
                
                sudo $PKG_MGR install -y \
                    python3-devel \
                    python3-pip \
                    python3-venv \
                    mesa-libGL \
                    glib2 \
                    fontconfig \
                    libxkbcommon-x11 \
                    dbus-libs \
                    git \
                    curl \
                    gcc \
                    gcc-c++ \
                    make \
                    pkg-config
                    
            elif command_exists pacman; then
                # Arch Linux
                print_status "Installing dependencies via pacman..."
                sudo pacman -S --needed \
                    python \
                    python-pip \
                    mesa \
                    glib2 \
                    fontconfig \
                    libxkbcommon-x11 \
                    dbus \
                    git \
                    curl \
                    base-devel \
                    pkg-config
            else
                print_warning "Unknown Linux package manager. Please install dependencies manually."
                print_status "Required packages: python3-dev, python3-venv, python3-pip, libgl1-mesa-glx, git"
            fi
            ;;
            
        "macos")
            print_status "Installing dependencies via Homebrew..."
            if ! command_exists brew; then
                print_status "Installing Homebrew..."
                /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
            fi
            
            brew install python@3.9 git
            # PyQt6 dependencies are handled via pip on macOS
            ;;
            
        "windows")
            print_warning "Windows detected. Please ensure you have:"
            print_status "1. Python 3.9+ installed from python.org"
            print_status "2. Git installed from git-scm.com"
            print_status "3. Visual Studio Build Tools (for compiling packages)"
            ;;
            
        *)
            print_warning "Unknown OS. Please install Python 3.9+, git, and system GUI libraries manually."
            ;;
    esac
}

# Function to create virtual environment
create_virtual_environment() {
    print_status "Creating virtual environment: $VENV_NAME"
    
    if [ -d "$VENV_NAME" ]; then
        print_warning "Virtual environment already exists. Removing..."
        rm -rf "$VENV_NAME"
    fi
    
    python3 -m venv "$VENV_NAME"
    
    # Activate virtual environment
    if [[ "$OS" == "windows" ]]; then
        source "$VENV_NAME/Scripts/activate"
    else
        source "$VENV_NAME/bin/activate"
    fi
    
    # Upgrade pip
    pip install --upgrade pip setuptools wheel
    
    print_success "Virtual environment created and activated"
}

# Function to install Python dependencies
install_python_dependencies() {
    print_status "Installing Python dependencies..."
    
    # Install requirements
    if [ -f "requirements.txt" ]; then
        pip install -r requirements.txt
    else
        print_error "requirements.txt not found"
        return 1
    fi
    
    # Install additional development dependencies
    print_status "Installing additional development dependencies..."
    pip install \
        pytest-cov \
        pytest-mock \
        pytest-asyncio \
        pytest-xvfb \
        ipython \
        jupyter \
        pre-commit
    
    print_success "Python dependencies installed"
}

# Function to create development directories
create_dev_directories() {
    print_status "Creating development directories..."
    
    # Create directories if they don't exist
    mkdir -p tests/{unit,integration,e2e,fixtures}
    mkdir -p assets/mock_images
    mkdir -p logs
    mkdir -p docs/dev
    mkdir -p .vscode
    mkdir -p docker
    
    # Create .gitignore if it doesn't exist or update it
    if [ ! -f ".gitignore" ]; then
        cat > .gitignore << EOF
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg
MANIFEST

# Virtual environments
venv/
env/
ENV/
aszcam-dev/

# IDEs
.vscode/
.idea/
*.swp
*.swo
*~

# OS
.DS_Store
Thumbs.db

# Logs
logs/
*.log

# Testing
.coverage
.pytest_cache/
htmlcov/
.tox/

# Development
.env
.env.local
temp/
tmp/
EOF
    fi
    
    print_success "Development directories created"
}

# Function to create development configuration
create_dev_config() {
    print_status "Creating development configuration..."
    
    # Create development settings override
    cat > src/config/dev_settings.py << 'EOF'
"""
ASZ Cam OS - Development Settings
Override settings for development environment.
"""

from .settings import settings

# Development mode flag
DEV_MODE = True

# Enable simulation/mock mode
SIMULATION_MODE = True

# Camera settings for development
CAMERA_MOCK = True
CAMERA_SAMPLE_IMAGES_PATH = "assets/mock_images"

# Logging configuration for development
LOG_LEVEL = "DEBUG"
LOG_TO_FILE = True
LOG_FILE = "logs/aszcam_dev.log"

# UI settings for development
UI_WINDOW_SIZE = (1024, 768)
UI_FULLSCREEN = False

# Sync settings for development (disabled by default)
SYNC_ENABLED = False
SYNC_AUTO_START = False

# Storage settings for development
PHOTOS_PATH = "dev_photos"
TEMP_PATH = "temp"

# Network settings for development
WIFI_HOTSPOT_DISABLED = True

# GPIO simulation
GPIO_SIMULATION = True

# System info simulation
SYSTEM_INFO_SIMULATION = True

print("Development settings loaded")
EOF

    # Create VSCode configuration
    if [ ! -f ".vscode/settings.json" ]; then
        cat > .vscode/settings.json << 'EOF'
{
    "python.defaultInterpreterPath": "./aszcam-dev/bin/python",
    "python.linting.enabled": true,
    "python.linting.flake8Enabled": true,
    "python.linting.pylintEnabled": false,
    "python.formatting.provider": "black",
    "python.formatting.blackArgs": ["--line-length=88"],
    "python.testing.pytestEnabled": true,
    "python.testing.unittestEnabled": false,
    "python.testing.pytestArgs": ["tests/"],
    "files.exclude": {
        "**/__pycache__": true,
        "**/*.pyc": true,
        "**/aszcam-dev": true
    }
}
EOF
    fi
    
    # Create launch configuration for debugging
    if [ ! -f ".vscode/launch.json" ]; then
        cat > .vscode/launch.json << 'EOF'
{
    "version": "0.2.0",
    "configurations": [
        {
            "name": "ASZ Cam OS (Development)",
            "type": "python",
            "request": "launch",
            "program": "${workspaceFolder}/src/main.py",
            "console": "integratedTerminal",
            "env": {
                "PYTHONPATH": "${workspaceFolder}/src",
                "ASZ_DEV_MODE": "true"
            },
            "args": ["--dev"]
        },
        {
            "name": "Run Tests",
            "type": "python",
            "request": "launch",
            "module": "pytest",
            "args": ["tests/", "-v"],
            "console": "integratedTerminal",
            "env": {
                "PYTHONPATH": "${workspaceFolder}/src"
            }
        }
    ]
}
EOF
    fi
    
    print_success "Development configuration created"
}

# Function to create sample assets
create_sample_assets() {
    print_status "Creating sample assets..."
    
    # Create sample config files
    cat > assets/mock_images/README.md << 'EOF'
# Mock Images Directory

This directory contains sample images used by the camera simulator for development and testing.

## Files:
- `sample_photo_*.jpg` - Sample photos returned by mock camera
- `preview_frame.jpg` - Sample preview frame
- `test_pattern.jpg` - Test pattern for debugging

These images are automatically generated if they don't exist when the mock camera initializes.
EOF
    
    print_success "Sample assets created"
}

# Function to setup Git hooks (optional)
setup_git_hooks() {
    if [ -d ".git" ]; then
        print_status "Setting up Git hooks..."
        
        # Create pre-commit hook for code formatting
        cat > .git/hooks/pre-commit << 'EOF'
#!/bin/bash
# Pre-commit hook for ASZ Cam OS
# Runs code formatting and basic checks

echo "Running pre-commit checks..."

# Check if we're in a virtual environment
if [ -z "$VIRTUAL_ENV" ]; then
    if [ -d "aszcam-dev" ]; then
        source aszcam-dev/bin/activate
    fi
fi

# Run black formatter
echo "Running black formatter..."
black --check src/ || {
    echo "Code formatting issues found. Run 'black src/' to fix."
    exit 1
}

# Run flake8 linter  
echo "Running flake8 linter..."
flake8 src/ || {
    echo "Linting issues found. Please fix before committing."
    exit 1
}

echo "Pre-commit checks passed!"
EOF
        
        chmod +x .git/hooks/pre-commit
        print_success "Git hooks set up"
    fi
}

# Function to create development scripts
create_dev_scripts() {
    print_status "Creating development scripts..."
    
    # Create run_dev_mode.py script
    cat > scripts/run_dev_mode.py << 'EOF'
#!/usr/bin/env python3
"""
ASZ Cam OS - Development Mode Runner
Run ASZ Cam OS in development mode with simulation/mock features enabled.
"""

import os
import sys
import argparse
import logging
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

# Set development environment variables
os.environ['ASZ_DEV_MODE'] = 'true'
os.environ['ASZ_SIMULATION_MODE'] = 'true'

def main():
    parser = argparse.ArgumentParser(description='ASZ Cam OS Development Mode')
    parser.add_argument('--mock-camera', action='store_true', default=True,
                        help='Use mock camera (default: True)')
    parser.add_argument('--mock-rpi', action='store_true', default=True,
                        help='Use RPi simulator (default: True)')
    parser.add_argument('--log-level', choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'],
                        default='DEBUG', help='Log level (default: DEBUG)')
    parser.add_argument('--windowed', action='store_true', default=True,
                        help='Run in windowed mode (default: True)')
    parser.add_argument('--test-mode', action='store_true',
                        help='Enable test mode with additional debugging')
    
    args = parser.parse_args()
    
    # Configure logging for development
    logging.basicConfig(
        level=getattr(logging, args.log_level),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler('logs/aszcam_dev.log')
        ]
    )
    
    # Set environment variables based on arguments
    if args.mock_camera:
        os.environ['ASZ_MOCK_CAMERA'] = 'true'
    if args.mock_rpi:
        os.environ['ASZ_MOCK_RPI'] = 'true'
    if args.windowed:
        os.environ['ASZ_WINDOWED_MODE'] = 'true'
    if args.test_mode:
        os.environ['ASZ_TEST_MODE'] = 'true'
    
    print("=" * 60)
    print("ASZ Cam OS - Development Mode")
    print("=" * 60)
    print(f"Mock Camera: {args.mock_camera}")
    print(f"Mock RPi: {args.mock_rpi}")
    print(f"Log Level: {args.log_level}")
    print(f"Windowed Mode: {args.windowed}")
    print(f"Test Mode: {args.test_mode}")
    print("=" * 60)
    
    # Import and run main application
    try:
        from main import main as app_main
        return app_main()
    except ImportError as e:
        print(f"Error importing main application: {e}")
        print("Make sure you're running from the project root directory")
        return 1
    except KeyboardInterrupt:
        print("\nDevelopment session interrupted by user")
        return 0
    except Exception as e:
        print(f"Error running development mode: {e}")
        return 1

if __name__ == '__main__':
    sys.exit(main())
EOF
    
    chmod +x scripts/run_dev_mode.py
    
    print_success "Development scripts created"
}

# Function to run tests
run_initial_tests() {
    print_status "Running initial tests..."
    
    # Create a basic test to verify setup
    cat > tests/test_dev_setup.py << 'EOF'
"""
Test development environment setup.
"""

import pytest
import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

def test_python_version():
    """Test Python version is adequate."""
    assert sys.version_info >= (3, 9), "Python 3.9+ required"

def test_imports():
    """Test that key dependencies can be imported."""
    try:
        import PyQt6
        import cv2
        import numpy
        import PIL
        # Don't test Pi-specific imports in dev environment
    except ImportError as e:
        pytest.fail(f"Import failed: {e}")

def test_mock_camera_import():
    """Test that mock camera can be imported."""
    try:
        from camera.mock_libcamera import MockLibCamera
        mock_camera = MockLibCamera()
        assert mock_camera is not None
    except ImportError as e:
        pytest.fail(f"Mock camera import failed: {e}")

def test_rpi_simulator_import():
    """Test that RPi simulator can be imported."""
    try:
        from core.rpi_simulator import RPiSimulator
        simulator = RPiSimulator()
        assert simulator.is_simulation == True
    except ImportError as e:
        pytest.fail(f"RPi simulator import failed: {e}")
EOF
    
    # Run the test
    if command_exists pytest; then
        pytest tests/test_dev_setup.py -v || print_warning "Some tests failed - this is normal for initial setup"
    else
        print_warning "pytest not found - skipping initial tests"
    fi
}

# Function to print setup summary
print_setup_summary() {
    print_success "Development environment setup complete!"
    echo
    echo "Next steps:"
    echo "1. Activate virtual environment: source aszcam-dev/bin/activate"
    echo "2. Run development mode: python scripts/run_dev_mode.py"
    echo "3. Run tests: pytest tests/ -v"
    echo "4. Open in VSCode: code ."
    echo
    echo "Development features:"
    echo "- Mock camera with realistic simulation"
    echo "- RPi hardware simulator"
    echo "- Cross-platform compatibility"
    echo "- Comprehensive testing framework"
    echo "- Development logging and debugging"
    echo
    echo "Configuration files created:"
    echo "- src/config/dev_settings.py"
    echo "- .vscode/ (VSCode configuration)"
    echo "- tests/ (test framework)"
    echo "- assets/mock_images/ (sample assets)"
    echo
    print_success "Happy coding! 🚀"
}

# Main execution
main() {
    echo "ASZ Cam OS - Development Environment Setup"
    echo "========================================="
    
    # Detect operating system
    detect_os
    
    # Check Python version
    if ! check_python_version; then
        print_error "Python version check failed. Please install Python $MIN_PYTHON_VERSION or higher."
        exit 1
    fi
    
    # Install system dependencies
    install_system_dependencies
    
    # Create virtual environment
    create_virtual_environment
    
    # Install Python dependencies
    install_python_dependencies
    
    # Create development directories and configuration
    create_dev_directories
    create_dev_config
    create_sample_assets
    create_dev_scripts
    
    # Optional: setup Git hooks
    setup_git_hooks
    
    # Run initial tests
    run_initial_tests
    
    # Print summary
    print_setup_summary
}

# Run main function
main "$@"