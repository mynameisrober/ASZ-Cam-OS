#!/bin/bash
# ASZ Cam OS - Completion Script for Interrupted Installations
# Detects and completes interrupted ASZ Cam OS installations
# Author: ASZ Development Team
# Version: 1.0.0
#
# Usage:
#   sudo ./complete_install.sh           # Interactive mode
#   sudo ./complete_install.sh --dry-run # Show what would be done without executing
#   sudo ./complete_install.sh --force   # Skip confirmation prompts
#
# Description:
# This script detects incomplete ASZ Cam OS installations and completes them.
# It can recover from interruptions that occur after system dependencies are
# installed but before the virtual environment is created, or from any other
# interruption point in the installation process.

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
BOLD='\033[1m'
NC='\033[0m' # No Color

# Configuration - same as main install script
ASZ_USER="${ASZ_USER:-pi}"
ASZ_HOME="/home/${ASZ_USER}"
ASZ_INSTALL_DIR="${ASZ_INSTALL_DIR:-${ASZ_HOME}/ASZCam}"
ASZ_SERVICE_USER="${ASZ_SERVICE_USER:-${ASZ_USER}}"
PYTHON_VERSION="3.11"

# Script options
DRY_RUN=false
FORCE_MODE=false

# Parse command line arguments
for arg in "$@"; do
    case $arg in
        --dry-run)
            DRY_RUN=true
            shift
            ;;
        --force)
            FORCE_MODE=true
            shift
            ;;
        --help|-h)
            echo "ASZ Cam OS Installation Completion Script"
            echo ""
            echo "Usage: sudo $0 [OPTIONS]"
            echo ""
            echo "Options:"
            echo "  --dry-run    Show what would be done without executing"
            echo "  --force      Skip confirmation prompts"
            echo "  --help       Show this help message"
            echo ""
            echo "This script completes interrupted ASZ Cam OS installations."
            exit 0
            ;;
        *)
            echo "Unknown option: $arg"
            echo "Use --help for usage information"
            exit 1
            ;;
    esac
done

# Logging
LOG_FILE="/tmp/aszcam_complete_install.log"
if [[ "$EUID" -eq 0 ]] && [[ "$DRY_RUN" != "true" ]]; then
    exec 1> >(tee -a ${LOG_FILE})
    exec 2> >(tee -a ${LOG_FILE} >&2)
else
    # If not root or in dry-run mode, don't use complex logging
    LOG_FILE="/dev/null"
fi

# Get script directory for sourcing functions
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
INSTALL_SCRIPT="${SCRIPT_DIR}/install.sh"

# Helper functions for logging
log_info() {
    echo -e "${BLUE}[COMPLETE]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[ÉXITO]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[ADVERTENCIA]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

log_header() {
    echo -e "\n${BOLD}=== $1 ===${NC}"
}

log_dry_run() {
    echo -e "${YELLOW}[DRY-RUN]${NC} Would execute: $1"
}

# Execute command or show what would be executed in dry-run mode
execute_or_dry_run() {
    local cmd="$1"
    local description="$2"
    
    if [[ "$DRY_RUN" == "true" ]]; then
        log_dry_run "$description"
        log_dry_run "Command: $cmd"
    else
        eval "$cmd"
    fi
}

# Reimplement key functions from install.sh to avoid complex sourcing
check_package_available() {
    local package_name="$1"
    apt-cache show "$package_name" &>/dev/null
    return $?
}

install_packages_with_fallback() {
    local packages=("$@")
    local failed_packages=()
    
    for package in "${packages[@]}"; do
        if check_package_available "$package"; then
            log_info "Installing $package..."
            if ! apt-get install -y "$package"; then
                log_warning "Failed to install $package, but continuing..."
                failed_packages+=("$package")
            fi
        else
            log_warning "Package $package not available in repositories"
            failed_packages+=("$package")
        fi
    done
    
    return 0
}

install_dependencies() {
    log_info "Installing system dependencies..."
    
    # Critical system packages that must succeed
    local critical_packages=(
        python3
        python3-pip
        python3-venv
        python3-dev
        git
        curl
        wget
        unzip
        build-essential
        cmake
        pkg-config
    )
    
    log_info "Installing critical system packages..."
    apt-get install -y "${critical_packages[@]}"
    
    # Development libraries (continue even if some fail)
    local dev_packages=(
        libjpeg-dev
        libpng-dev
        libtiff-dev
        libavcodec-dev
        libavformat-dev
        libswscale-dev
        libv4l-dev
        libxvidcore-dev
        libx264-dev
        libgtk-3-dev
        libcanberra-gtk3-module
        libatlas-base-dev
        gfortran
    )
    
    log_info "Installing development libraries..."
    install_packages_with_fallback "${dev_packages[@]}"
    
    # Check for PyQt6 system packages
    local pyqt6_packages=(
        python3-pyqt6
        python3-pyqt6.qtcore
        python3-pyqt6.qtgui
        python3-pyqt6.qtwidgets
    )
    
    log_info "Checking for PyQt6 system packages..."
    if check_package_available "python3-pyqt6"; then
        log_info "Installing PyQt6 system packages..."
        install_packages_with_fallback "${pyqt6_packages[@]}"
    else
        log_warning "System PyQt6 packages not available, will install via pip in virtual environment"
    fi
    
    # GUI and system packages (optional)
    local gui_packages=(
        xorg
        xinit
        openbox
        unclutter
        chromium-browser
        fonts-dejavu
        fonts-liberation
    )
    
    log_info "Installing GUI and system packages..."
    install_packages_with_fallback "${gui_packages[@]}"
    
    # Raspberry Pi specific packages
    if grep -q "Raspberry Pi" /proc/cpuinfo; then
        log_info "Installing Raspberry Pi specific packages..."
        local rpi_packages=(
            raspberrypi-kernel-headers
            libcamera-dev
            libcamera-apps
            python3-libcamera
            python3-picamera2
        )
        install_packages_with_fallback "${rpi_packages[@]}"
    fi
    
    log_success "Dependencies installation completed"
}

create_user_and_directories() {
    log_info "Creating user and directories..."
    
    if [[ "$DRY_RUN" == "true" ]]; then
        log_dry_run "Would create user ${ASZ_USER} if not exists"
        log_dry_run "Would create directories: ${ASZ_INSTALL_DIR}, ${ASZ_HOME}/.config/aszcam, etc."
        log_dry_run "Would set appropriate permissions"
        return 0
    fi
    
    # Create user if doesn't exist
    if ! id "${ASZ_USER}" &>/dev/null; then
        useradd -m -s /bin/bash "${ASZ_USER}"
        
        # Add user to groups that exist
        local groups_to_add=()
        for group in video gpio i2c spi; do
            if getent group "$group" >/dev/null 2>&1; then
                groups_to_add+=("$group")
            else
                log_warning "Group $group does not exist on this system"
            fi
        done
        
        if [[ ${#groups_to_add[@]} -gt 0 ]]; then
            local groups_str=$(IFS=,; echo "${groups_to_add[*]}")
            usermod -a -G "$groups_str" "${ASZ_USER}"
            log_info "Added user ${ASZ_USER} to groups: $groups_str"
        fi
        
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
    
    if [[ "$DRY_RUN" == "true" ]]; then
        log_dry_run "Would create virtual environment at ${ASZ_INSTALL_DIR}/venv"
        log_dry_run "Would upgrade pip in virtual environment"
        return 0
    fi
    
    # Create virtual environment as the target user
    sudo -u "${ASZ_USER}" python3 -m venv "${ASZ_INSTALL_DIR}/venv"
    
    # Upgrade pip
    sudo -u "${ASZ_USER}" "${ASZ_INSTALL_DIR}/venv/bin/pip" install --upgrade pip
    
    log_success "Python virtual environment created"
}

copy_source_code() {
    log_info "Copying ASZ Cam OS source code..."
    
    # Get the project root directory
    PROJECT_ROOT="$(dirname "${SCRIPT_DIR}")"
    
    if [[ "$DRY_RUN" == "true" ]]; then
        log_dry_run "Would copy source files from ${PROJECT_ROOT}/src to ${ASZ_INSTALL_DIR}/"
        log_dry_run "Would copy assets from ${PROJECT_ROOT}/assets to ${ASZ_INSTALL_DIR}/"
        log_dry_run "Would copy requirements.txt"
        log_dry_run "Would set appropriate permissions"
        return 0
    fi
    
    # Copy source files
    cp -r "${PROJECT_ROOT}/src" "${ASZ_INSTALL_DIR}/" 2>/dev/null || log_warning "Source directory not found"
    cp -r "${PROJECT_ROOT}/assets" "${ASZ_INSTALL_DIR}/" 2>/dev/null || log_warning "Assets directory not found"
    cp "${PROJECT_ROOT}/requirements.txt" "${ASZ_INSTALL_DIR}/" 2>/dev/null || log_warning "Requirements file not found"
    
    # Set permissions
    chown -R "${ASZ_USER}:${ASZ_USER}" "${ASZ_INSTALL_DIR}"
    chmod +x "${ASZ_INSTALL_DIR}/src/main.py" 2>/dev/null || log_warning "main.py not found to make executable"
    
    log_success "Source code copied successfully"
}

install_python_packages() {
    log_info "Installing Python packages..."
    
    if [[ ! -f "${ASZ_INSTALL_DIR}/requirements.txt" ]]; then
        log_error "Requirements file not found. Please copy source code first."
        return 1
    fi
    
    # Upgrade pip first
    sudo -u "${ASZ_USER}" "${ASZ_INSTALL_DIR}/venv/bin/pip" install --upgrade pip
    
    # Check if PyQt6 is available from system packages
    local pyqt6_system_available=false
    if python3 -c "import PyQt6" 2>/dev/null; then
        pyqt6_system_available=true
        log_info "PyQt6 available from system packages"
    fi
    
    # Install packages in virtual environment
    if sudo -u "${ASZ_USER}" "${ASZ_INSTALL_DIR}/venv/bin/pip" install -r "${ASZ_INSTALL_DIR}/requirements.txt"; then
        log_success "Python packages installed successfully"
    else
        log_warning "Some Python packages failed to install, trying individual installation..."
        
        # Try to install PyQt6 specifically if it failed
        if ! sudo -u "${ASZ_USER}" "${ASZ_INSTALL_DIR}/venv/bin/python" -c "import PyQt6" 2>/dev/null; then
            log_info "Installing PyQt6 via pip as fallback..."
            
            # Try different PyQt6 installation methods
            if ! sudo -u "${ASZ_USER}" "${ASZ_INSTALL_DIR}/venv/bin/pip" install PyQt6>=6.5.0; then
                log_warning "PyQt6 6.5+ failed, trying PyQt6 without version constraint..."
                if ! sudo -u "${ASZ_USER}" "${ASZ_INSTALL_DIR}/venv/bin/pip" install PyQt6; then
                    log_warning "PyQt6 installation failed, trying PyQt6-Qt6..."
                    sudo -u "${ASZ_USER}" "${ASZ_INSTALL_DIR}/venv/bin/pip" install PyQt6-Qt6 || log_warning "PyQt6-Qt6 also failed"
                fi
            fi
        fi
        
        # Try to install other critical packages individually
        local critical_packages=(
            "opencv-python>=4.8.0"
            "Pillow>=10.0.0"
            "numpy>=1.24.0"
            "PyYAML>=6.0"
        )
        
        for package in "${critical_packages[@]}"; do
            if ! sudo -u "${ASZ_USER}" "${ASZ_INSTALL_DIR}/venv/bin/pip" install "$package"; then
                log_warning "Failed to install $package, but continuing..."
            fi
        done
        
        log_success "Python packages installation completed with some warnings"
    fi
    
    # Verify critical packages are available
    log_info "Verifying critical Python packages..."
    local python_bin="${ASZ_INSTALL_DIR}/venv/bin/python"
    
    # Check PyQt6
    if sudo -u "${ASZ_USER}" "$python_bin" -c "import PyQt6; print('PyQt6 version:', PyQt6.QtCore.QT_VERSION_STR)" 2>/dev/null; then
        log_success "PyQt6 is available and working"
    else
        log_warning "PyQt6 verification failed - GUI functionality may be limited"
    fi
    
    # Check other critical modules
    local modules_to_check=("cv2:OpenCV" "PIL:Pillow" "numpy:NumPy" "yaml:PyYAML")
    for module_check in "${modules_to_check[@]}"; do
        module_name="${module_check%%:*}"
        friendly_name="${module_check##*:}"
        if sudo -u "${ASZ_USER}" "$python_bin" -c "import $module_name" 2>/dev/null; then
            log_success "$friendly_name is available"
        else
            log_warning "$friendly_name verification failed"
        fi
    done
}

run_raspberry_pi_setup() {
    if grep -q "Raspberry Pi" /proc/cpuinfo; then
        log_info "Running Raspberry Pi specific setup..."
        
        if [[ -f "${SCRIPT_DIR}/setup_rpi.sh" ]]; then
            bash "${SCRIPT_DIR}/setup_rpi.sh"
        else
            log_warning "Raspberry Pi setup script not found, skipping..."
        fi
    else
        log_info "Not a Raspberry Pi, skipping RPi-specific setup"
    fi
}

install_systemd_service() {
    log_info "Installing systemd service..."
    
    PROJECT_ROOT="$(dirname "${SCRIPT_DIR}")"
    
    if [[ "$DRY_RUN" == "true" ]]; then
        log_dry_run "Would copy service file from ${PROJECT_ROOT}/install/asz-cam-os.service"
        log_dry_run "Would update service file with paths"
        log_dry_run "Would enable asz-cam-os.service"
        return 0
    fi
    
    # Install service file
    if [[ -f "${PROJECT_ROOT}/install/asz-cam-os.service" ]]; then
        cp "${PROJECT_ROOT}/install/asz-cam-os.service" "/etc/systemd/system/"
        
        # Update service file with real paths
        sed -i "s|{ASZ_INSTALL_DIR}|${ASZ_INSTALL_DIR}|g" "/etc/systemd/system/asz-cam-os.service"
        sed -i "s|{ASZ_USER}|${ASZ_USER}|g" "/etc/systemd/system/asz-cam-os.service"
        
        systemctl daemon-reload
        systemctl enable asz-cam-os.service
        
        log_success "Systemd service installed and enabled"
    else
        log_warning "Service file not found, skipping service installation..."
    fi
}

download_fonts() {
    log_info "Downloading fonts..."
    
    if [[ -f "${SCRIPT_DIR}/download_fonts.sh" ]]; then
        bash "${SCRIPT_DIR}/download_fonts.sh"
    else
        log_warning "Font download script not found, skipping..."
    fi
}

configure_system() {
    log_info "Configuring system..."
    
    if [[ -f "${SCRIPT_DIR}/configure_system.sh" ]]; then
        bash "${SCRIPT_DIR}/configure_system.sh"
    else
        log_warning "System configuration script not found, skipping..."
    fi
}

run_validation() {
    log_info "Running installation validation..."
    
    if [[ -f "${SCRIPT_DIR}/validate_install.sh" ]]; then
        bash "${SCRIPT_DIR}/validate_install.sh"
    else
        log_warning "Validation script not found, skipping validation..."
    fi
}

# Function to check if root
check_root() {
    if [[ $EUID -ne 0 ]]; then
        log_error "Este script debe ejecutarse como root (usa sudo)"
        exit 1
    fi
}

# Function to detect installation state
detect_installation_state() {
    log_header "Detecting Installation State"
    
    local missing_steps=()
    
    # Check if system dependencies are installed
    if ! command -v python3 >/dev/null 2>&1 || ! command -v git >/dev/null 2>&1; then
        missing_steps+=("install_dependencies")
        log_warning "System dependencies missing"
    else
        log_success "System dependencies appear to be installed"
    fi
    
    # Check if user and directories exist
    if ! id "${ASZ_USER}" &>/dev/null || [[ ! -d "${ASZ_INSTALL_DIR}" ]]; then
        missing_steps+=("create_user_and_directories")
        log_warning "User or directories missing"
    else
        log_success "User and directories exist"
    fi
    
    # Check if Python virtual environment exists
    if [[ ! -f "${ASZ_INSTALL_DIR}/venv/bin/python" ]]; then
        missing_steps+=("install_python_environment")
        log_warning "Python virtual environment missing"
    else
        log_success "Python virtual environment exists"
    fi
    
    # Check if source code is copied
    if [[ ! -f "${ASZ_INSTALL_DIR}/src/main.py" ]] || [[ ! -f "${ASZ_INSTALL_DIR}/requirements.txt" ]]; then
        missing_steps+=("copy_source_code")
        log_warning "Source code missing"
    else
        log_success "Source code appears to be copied"
    fi
    
    # Check if Python packages are installed
    if [[ -f "${ASZ_INSTALL_DIR}/venv/bin/python" ]]; then
        if ! sudo -u "${ASZ_USER}" "${ASZ_INSTALL_DIR}/venv/bin/python" -c "import PyQt6, cv2, PIL, numpy, yaml" 2>/dev/null; then
            missing_steps+=("install_python_packages")
            log_warning "Python packages missing or incomplete"
        else
            log_success "Python packages appear to be installed"
        fi
    fi
    
    # Check if Raspberry Pi setup is done (if on RPi)
    if grep -q "Raspberry Pi" /proc/cpuinfo; then
        if [[ ! -f "/boot/aszcam-backups/config.txt.backup."* ]]; then
            missing_steps+=("run_raspberry_pi_setup")
            log_warning "Raspberry Pi setup not completed"
        else
            log_success "Raspberry Pi setup appears to be done"
        fi
    fi
    
    # Check if systemd service is installed
    if [[ ! -f "/etc/systemd/system/asz-cam-os.service" ]]; then
        missing_steps+=("install_systemd_service")
        log_warning "Systemd service not installed"
    else
        log_success "Systemd service appears to be installed"
    fi
    
    # Store missing steps for later use
    echo "${missing_steps[@]}" > /tmp/aszcam_missing_steps
    
    if [[ ${#missing_steps[@]} -eq 0 ]]; then
        log_success "Installation appears to be complete!"
        return 0
    else
        log_info "Found ${#missing_steps[@]} incomplete installation steps:"
        for step in "${missing_steps[@]}"; do
            log_info "  - $step"
        done
        return 1
    fi
}

# Function to configure PyQt6 system access
configure_pyqt6_system_access() {
    log_info "Configuring PyQt6 system access in virtual environment..."
    
    local venv_site_packages="${ASZ_INSTALL_DIR}/venv/lib/python*/site-packages"
    local system_pyqt6=""
    
    # Find system PyQt6 installation
    for path in /usr/lib/python3*/dist-packages /usr/local/lib/python3*/dist-packages; do
        if [[ -d "${path}/PyQt6" ]]; then
            system_pyqt6="$path"
            break
        fi
    done
    
    if [[ -n "$system_pyqt6" ]] && [[ -d "$system_pyqt6/PyQt6" ]]; then
        log_info "Found system PyQt6 at: $system_pyqt6"
        
        # Create .pth file to include system PyQt6
        echo "$system_pyqt6" | sudo -u "${ASZ_USER}" tee ${venv_site_packages}/system-pyqt6.pth > /dev/null
        
        log_success "PyQt6 system access configured"
    else
        log_warning "System PyQt6 not found, will rely on pip installation"
    fi
}

# Function to run missing installation steps
complete_installation() {
    log_header "Completing Installation"
    
    if [[ ! -f "/tmp/aszcam_missing_steps" ]]; then
        log_error "Missing steps information not found. Run detection first."
        return 1
    fi
    
    local missing_steps=($(cat /tmp/aszcam_missing_steps))
    
    if [[ ${#missing_steps[@]} -eq 0 ]]; then
        log_success "No installation steps missing!"
        return 0
    fi
    
    log_info "Completing ${#missing_steps[@]} missing installation steps..."
    
    # Execute missing steps in order
    for step in "${missing_steps[@]}"; do
        log_info "Executing step: $step"
        
        case "$step" in
            "install_dependencies")
                install_dependencies
                ;;
            "create_user_and_directories")
                create_user_and_directories
                ;;
            "install_python_environment")
                install_python_environment
                configure_pyqt6_system_access
                ;;
            "copy_source_code")
                copy_source_code
                ;;
            "install_python_packages")
                install_python_packages
                ;;
            "run_raspberry_pi_setup")
                run_raspberry_pi_setup
                ;;
            "install_systemd_service")
                install_systemd_service
                ;;
            *)
                log_warning "Unknown step: $step, skipping..."
                ;;
        esac
        
        log_success "Completed step: $step"
    done
    
    # Always run these final steps
    log_info "Running final configuration steps..."
    
    download_fonts || log_warning "Font download failed, continuing..."
    configure_system || log_warning "System configuration failed, continuing..."
    
    log_success "Installation completion finished!"
}

# Function to run validation
run_final_validation() {
    log_header "Running Final Validation"
    
    if [[ -f "${SCRIPT_DIR}/validate_install.sh" ]]; then
        run_validation
    else
        log_warning "Validation script not available, running basic checks..."
        
        # Basic validation
        if [[ -f "${ASZ_INSTALL_DIR}/venv/bin/python" ]] && \
           [[ -f "${ASZ_INSTALL_DIR}/src/main.py" ]] && \
           [[ -f "/etc/systemd/system/asz-cam-os.service" ]]; then
            log_success "Basic validation checks passed"
        else
            log_error "Basic validation checks failed"
            return 1
        fi
    fi
}

# Function to show completion message
show_completion_message() {
    echo ""
    echo "==============================================="
    log_success "¡ASZ Cam OS Installation Completion Finished!"
    echo "==============================================="
    echo ""
    echo "Installation Details:"
    echo "- Installation Directory: ${ASZ_INSTALL_DIR}"
    echo "- Service User: ${ASZ_SERVICE_USER}"
    echo "- Photos Directory: ${ASZ_HOME}/Pictures/ASZCam"
    echo "- Configuration Directory: ${ASZ_HOME}/.config/aszcam"
    echo "- Log File: /var/log/aszcam/aszcam.log"
    echo ""
    echo "Next Steps:"
    echo "1. Restart your system: sudo reboot"
    echo "2. ASZ Cam OS will start automatically after reboot"
    echo "3. Configure Google Photos sync in settings (optional)"
    echo ""
    echo "Manual Control:"
    echo "Start Service: sudo systemctl start asz-cam-os"
    echo "View Logs: journalctl -u asz-cam-os -f"
    echo ""
    echo "Completion log saved to: ${LOG_FILE}"
    echo ""
}

# Function to show header
show_header() {
    clear
    echo "================================================="
    echo "    ASZ Cam OS - Installation Completion Script"
    echo "              Version 1.0.0"
    echo "================================================="
    echo ""
    echo "This script will detect and complete any missing"
    echo "installation steps from an interrupted installation."
    echo ""
    echo "Installation Directory: ${ASZ_INSTALL_DIR}"
    echo "Service User: ${ASZ_SERVICE_USER}"
    if [[ "$DRY_RUN" == "true" ]]; then
        echo "Mode: DRY-RUN (no changes will be made)"
    fi
    if [[ "$FORCE_MODE" == "true" ]]; then
        echo "Mode: FORCE (skip confirmations)"
    fi
    echo ""
}

# Main function
main() {
    show_header
    
    # Initial checks
    check_root
    
    if [[ "$DRY_RUN" == "true" ]]; then
        log_info "Running in DRY-RUN mode - no changes will be made"
        echo ""
    fi
    
    # Detect what needs to be completed
    if detect_installation_state; then
        log_success "Installation is already complete!"
        
        if [[ "$FORCE_MODE" != "true" ]]; then
            read -p "Do you want to run validation anyway? (y/N): " -n 1 -r
            echo
            if [[ $REPLY =~ ^[Yy]$ ]]; then
                run_final_validation
            fi
        else
            run_final_validation
        fi
    else
        echo ""
        if [[ "$FORCE_MODE" == "true" ]]; then
            complete_installation
            run_final_validation
            show_completion_message
        else
            read -p "Do you want to complete the missing installation steps? (Y/n): " -n 1 -r
            echo
            if [[ ! $REPLY =~ ^[Nn]$ ]]; then
                complete_installation
                run_final_validation
                show_completion_message
            else
                log_info "Installation completion cancelled by user"
            fi
        fi
    fi
    
    # Clean up
    rm -f /tmp/aszcam_missing_steps
}

# Handle script interruption
trap 'log_error "Completion script interrupted!"; rm -f /tmp/aszcam_missing_steps; exit 1' INT TERM

# Run main function
main "$@"