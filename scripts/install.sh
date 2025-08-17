#!/bin/bash
# ASZ Cam OS - Master Installation Script
# Installs and configures ASZ Cam OS on Raspberry Pi
# Author: ASZ Development Team
# Version: 1.0.0

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
ASZ_USER="${ASZ_USER:-pi}"
ASZ_HOME="/home/${ASZ_USER}"
ASZ_INSTALL_DIR="${ASZ_INSTALL_DIR:-${ASZ_HOME}/ASZCam}"
ASZ_SERVICE_USER="${ASZ_SERVICE_USER:-${ASZ_USER}}"
PYTHON_VERSION="3.11"

# Logging
LOG_FILE="/tmp/aszcam_install.log"
exec 1> >(tee -a ${LOG_FILE})
exec 2> >(tee -a ${LOG_FILE} >&2)

# Helper functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

check_root() {
    if [[ $EUID -ne 0 ]]; then
        log_error "This script must be run as root (use sudo)"
        exit 1
    fi
}

check_raspberry_pi() {
    if ! grep -q "Raspberry Pi" /proc/cpuinfo; then
        log_warning "This script is optimized for Raspberry Pi, but will attempt to install anyway"
    else
        log_info "Raspberry Pi detected"
    fi
}

show_header() {
    clear
    echo "==============================================="
    echo "    ASZ Cam OS - Installation Script"
    echo "         Version 1.0.0"
    echo "==============================================="
    echo ""
    echo "This will install ASZ Cam OS on your system."
    echo "Installation directory: ${ASZ_INSTALL_DIR}"
    echo "Service user: ${ASZ_SERVICE_USER}"
    echo ""
}

confirm_installation() {
    read -p "Do you want to continue? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        log_info "Installation cancelled by user"
        exit 0
    fi
}

update_system() {
    log_info "Updating system packages..."
    apt-get update
    apt-get upgrade -y
    log_success "System updated successfully"
}

install_dependencies() {
    log_info "Installing system dependencies..."
    
    # Essential packages
    apt-get install -y \
        python3 \
        python3-pip \
        python3-venv \
        python3-dev \
        git \
        curl \
        wget \
        unzip \
        build-essential \
        cmake \
        pkg-config \
        libjpeg-dev \
        libpng-dev \
        libtiff-dev \
        libavcodec-dev \
        libavformat-dev \
        libswscale-dev \
        libv4l-dev \
        libxvidcore-dev \
        libx264-dev \
        libgtk-3-dev \
        libcanberra-gtk3-module \
        libatlas-base-dev \
        gfortran \
        libhdf5-dev \
        libhdf5-serial-dev \
        libhdf5-103 \
        python3-pyqt6 \
        python3-pyqt6.qtcore \
        python3-pyqt6.qtgui \
        python3-pyqt6.qtwidgets \
        qtbase6-dev \
        qt6-wayland \
        xorg \
        xinit \
        openbox \
        unclutter \
        chromium-browser \
        fonts-dejavu \
        fonts-liberation
    
    # Raspberry Pi specific packages
    if grep -q "Raspberry Pi" /proc/cpuinfo; then
        log_info "Installing Raspberry Pi specific packages..."
        apt-get install -y \
            raspberrypi-kernel-headers \
            libcamera-dev \
            libcamera-apps \
            python3-libcamera \
            python3-picamera2
    fi
    
    log_success "Dependencies installed successfully"
}

create_user_and_directories() {
    log_info "Creating user and directories..."
    
    # Create user if doesn't exist
    if ! id "${ASZ_USER}" &>/dev/null; then
        useradd -m -s /bin/bash "${ASZ_USER}"
        usermod -a -G video,gpio,i2c,spi "${ASZ_USER}"
        log_info "Created user: ${ASZ_USER}"
    else
        log_info "User ${ASZ_USER} already exists"
    fi
    
    # Create directories
    mkdir -p "${ASZ_INSTALL_DIR}"
    mkdir -p "${ASZ_HOME}/.config/aszcam"
    mkdir -p "${ASZ_HOME}/Pictures/ASZCam"
    mkdir -p "/var/log/aszcam"
    
    # Set permissions
    chown -R "${ASZ_USER}:${ASZ_USER}" "${ASZ_INSTALL_DIR}"
    chown -R "${ASZ_USER}:${ASZ_USER}" "${ASZ_HOME}/.config/aszcam"
    chown -R "${ASZ_USER}:${ASZ_USER}" "${ASZ_HOME}/Pictures"
    chown -R "${ASZ_USER}:${ASZ_USER}" "/var/log/aszcam"
    
    log_success "User and directories created successfully"
}

install_python_environment() {
    log_info "Setting up Python virtual environment..."
    
    # Create virtual environment as the target user
    sudo -u "${ASZ_USER}" python3 -m venv "${ASZ_INSTALL_DIR}/venv"
    
    # Upgrade pip
    sudo -u "${ASZ_USER}" "${ASZ_INSTALL_DIR}/venv/bin/pip" install --upgrade pip
    
    log_success "Python virtual environment created"
}

copy_source_code() {
    log_info "Copying ASZ Cam OS source code..."
    
    # Get the directory where this script is located
    SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
    PROJECT_ROOT="$(dirname "${SCRIPT_DIR}")"
    
    # Copy source files
    cp -r "${PROJECT_ROOT}/src" "${ASZ_INSTALL_DIR}/"
    cp -r "${PROJECT_ROOT}/assets" "${ASZ_INSTALL_DIR}/"
    cp "${PROJECT_ROOT}/requirements.txt" "${ASZ_INSTALL_DIR}/"
    
    # Set permissions
    chown -R "${ASZ_USER}:${ASZ_USER}" "${ASZ_INSTALL_DIR}"
    chmod +x "${ASZ_INSTALL_DIR}/src/main.py"
    
    log_success "Source code copied successfully"
}

install_python_packages() {
    log_info "Installing Python packages..."
    
    # Install packages in virtual environment
    sudo -u "${ASZ_USER}" "${ASZ_INSTALL_DIR}/venv/bin/pip" install -r "${ASZ_INSTALL_DIR}/requirements.txt"
    
    log_success "Python packages installed successfully"
}

run_raspberry_pi_setup() {
    if grep -q "Raspberry Pi" /proc/cpuinfo; then
        log_info "Running Raspberry Pi specific setup..."
        
        SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
        if [[ -f "${SCRIPT_DIR}/setup_rpi.sh" ]]; then
            bash "${SCRIPT_DIR}/setup_rpi.sh"
        else
            log_warning "Raspberry Pi setup script not found, skipping..."
        fi
    fi
}

download_fonts() {
    log_info "Downloading fonts..."
    
    SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
    if [[ -f "${SCRIPT_DIR}/download_fonts.sh" ]]; then
        bash "${SCRIPT_DIR}/download_fonts.sh"
    else
        log_warning "Font download script not found, skipping..."
    fi
}

configure_system() {
    log_info "Configuring system..."
    
    SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
    if [[ -f "${SCRIPT_DIR}/configure_system.sh" ]]; then
        bash "${SCRIPT_DIR}/configure_system.sh"
    else
        log_warning "System configuration script not found, skipping..."
    fi
}

install_systemd_service() {
    log_info "Installing systemd service..."
    
    SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
    PROJECT_ROOT="$(dirname "${SCRIPT_DIR}")"
    
    # Install service file
    if [[ -f "${PROJECT_ROOT}/install/asz-cam-os.service" ]]; then
        cp "${PROJECT_ROOT}/install/asz-cam-os.service" "/etc/systemd/system/"
        
        # Update service file with actual paths
        sed -i "s|{ASZ_INSTALL_DIR}|${ASZ_INSTALL_DIR}|g" "/etc/systemd/system/asz-cam-os.service"
        sed -i "s|{ASZ_USER}|${ASZ_USER}|g" "/etc/systemd/system/asz-cam-os.service"
        
        systemctl daemon-reload
        systemctl enable asz-cam-os.service
        
        log_success "Systemd service installed and enabled"
    else
        log_warning "Service file not found, skipping service installation..."
    fi
}

run_validation() {
    log_info "Running installation validation..."
    
    SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
    if [[ -f "${SCRIPT_DIR}/validate_install.sh" ]]; then
        bash "${SCRIPT_DIR}/validate_install.sh"
    else
        log_warning "Validation script not found, skipping validation..."
    fi
}

show_completion_message() {
    echo ""
    echo "==============================================="
    log_success "ASZ Cam OS Installation Complete!"
    echo "==============================================="
    echo ""
    echo "Installation Details:"
    echo "- Install Directory: ${ASZ_INSTALL_DIR}"
    echo "- Service User: ${ASZ_SERVICE_USER}"
    echo "- Photos Directory: ${ASZ_HOME}/Pictures/ASZCam"
    echo "- Config Directory: ${ASZ_HOME}/.config/aszcam"
    echo "- Log File: /var/log/aszcam/aszcam.log"
    echo ""
    echo "Next Steps:"
    echo "1. Reboot your system: sudo reboot"
    echo "2. The ASZ Cam OS will start automatically after reboot"
    echo "3. Configure Google Photos sync in settings (optional)"
    echo ""
    echo "Manual Start: sudo systemctl start asz-cam-os"
    echo "View Logs: journalctl -u asz-cam-os -f"
    echo ""
    echo "Installation log saved to: ${LOG_FILE}"
    echo ""
}

# Main installation process
main() {
    show_header
    confirm_installation
    
    log_info "Starting ASZ Cam OS installation..."
    
    # Pre-flight checks
    check_root
    check_raspberry_pi
    
    # Installation steps
    update_system
    install_dependencies
    create_user_and_directories
    install_python_environment
    copy_source_code
    install_python_packages
    run_raspberry_pi_setup
    download_fonts
    configure_system
    install_systemd_service
    run_validation
    
    show_completion_message
}

# Handle script interruption
trap 'log_error "Installation interrupted!"; exit 1' INT TERM

# Run main function
main "$@"