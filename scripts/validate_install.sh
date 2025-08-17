#!/bin/bash
# ASZ Cam OS - Installation Validation Script
# Validates the ASZ Cam OS installation and provides diagnostics
# Author: ASZ Development Team
# Version: 1.0.0

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
BOLD='\033[1m'
NC='\033[0m' # No Color

# Configuration
ASZ_USER="${ASZ_USER:-pi}"
ASZ_HOME="/home/${ASZ_USER}"
ASZ_INSTALL_DIR="${ASZ_INSTALL_DIR:-${ASZ_HOME}/ASZCam}"
VALIDATION_LOG="/tmp/aszcam_validation.log"

# Counters
TOTAL_CHECKS=0
PASSED_CHECKS=0
FAILED_CHECKS=0
WARNING_CHECKS=0

# Helper functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1" | tee -a "$VALIDATION_LOG"
}

log_success() {
    echo -e "${GREEN}[✓]${NC} $1" | tee -a "$VALIDATION_LOG"
    ((PASSED_CHECKS++))
}

log_warning() {
    echo -e "${YELLOW}[⚠]${NC} $1" | tee -a "$VALIDATION_LOG"
    ((WARNING_CHECKS++))
}

log_error() {
    echo -e "${RED}[✗]${NC} $1" | tee -a "$VALIDATION_LOG"
    ((FAILED_CHECKS++))
}

log_header() {
    echo -e "\n${BOLD}=== $1 ===${NC}" | tee -a "$VALIDATION_LOG"
}

increment_total() {
    ((TOTAL_CHECKS++))
}

show_header() {
    clear
    echo "===============================================" | tee "$VALIDATION_LOG"
    echo "    ASZ Cam OS - Installation Validation" | tee -a "$VALIDATION_LOG"
    echo "         $(date)" | tee -a "$VALIDATION_LOG"
    echo "===============================================" | tee -a "$VALIDATION_LOG"
    echo "" | tee -a "$VALIDATION_LOG"
}

check_system_info() {
    log_header "System Information"
    
    # OS Information
    if [ -f /etc/os-release ]; then
        source /etc/os-release
        log_info "Operating System: $PRETTY_NAME"
        log_info "Version: $VERSION"
    fi
    
    # Hardware info
    log_info "Hardware: $(cat /proc/device-tree/model 2>/dev/null || echo 'Unknown')"
    log_info "Kernel: $(uname -r)"
    log_info "Architecture: $(uname -m)"
    
    # Memory info
    local total_mem=$(free -h | awk '/^Mem:/ {print $2}')
    local available_mem=$(free -h | awk '/^Mem:/ {print $7}')
    log_info "Memory: $total_mem total, $available_mem available"
    
    # Disk space
    local disk_usage=$(df -h / | awk 'NR==2 {print $3 " used, " $4 " available (" $5 " full)"}')
    log_info "Disk Usage: $disk_usage"
    
    # Temperature (Raspberry Pi)
    if command -v vcgencmd >/dev/null 2>&1; then
        local temp=$(vcgencmd measure_temp 2>/dev/null | sed 's/temp=//')
        log_info "CPU Temperature: $temp"
    fi
}

check_user_and_permissions() {
    log_header "User and Permissions"
    
    increment_total
    if id "$ASZ_USER" &>/dev/null; then
        log_success "User '$ASZ_USER' exists"
    else
        log_error "User '$ASZ_USER' does not exist"
        return 1
    fi
    
    increment_total
    if groups "$ASZ_USER" | grep -q video; then
        log_success "User '$ASZ_USER' is in video group"
    else
        log_warning "User '$ASZ_USER' is not in video group"
    fi
    
    increment_total
    if [[ -d "$ASZ_HOME" ]]; then
        log_success "Home directory exists: $ASZ_HOME"
    else
        log_error "Home directory missing: $ASZ_HOME"
        return 1
    fi
    
    # Check ownership of key directories
    local directories=(
        "$ASZ_INSTALL_DIR"
        "$ASZ_HOME/.config/aszcam"
        "$ASZ_HOME/Pictures/ASZCam"
    )
    
    for dir in "${directories[@]}"; do
        increment_total
        if [[ -d "$dir" ]]; then
            local owner=$(stat -c '%U' "$dir")
            if [[ "$owner" == "$ASZ_USER" ]]; then
                log_success "Directory ownership correct: $dir"
            else
                log_error "Directory ownership incorrect: $dir (owned by $owner, should be $ASZ_USER)"
            fi
        else
            log_error "Required directory missing: $dir"
        fi
    done
}

check_installation_files() {
    log_header "Installation Files"
    
    # Check main installation directory
    increment_total
    if [[ -d "$ASZ_INSTALL_DIR" ]]; then
        log_success "Installation directory exists: $ASZ_INSTALL_DIR"
    else
        log_error "Installation directory missing: $ASZ_INSTALL_DIR"
        return 1
    fi
    
    # Check critical files
    local critical_files=(
        "$ASZ_INSTALL_DIR/src/main.py"
        "$ASZ_INSTALL_DIR/requirements.txt"
        "$ASZ_INSTALL_DIR/venv/bin/python"
        "$ASZ_INSTALL_DIR/venv/bin/pip"
    )
    
    for file in "${critical_files[@]}"; do
        increment_total
        if [[ -f "$file" ]]; then
            log_success "Critical file exists: $(basename "$file")"
        else
            log_error "Critical file missing: $file"
        fi
    done
    
    # Check if main.py is executable
    increment_total
    if [[ -x "$ASZ_INSTALL_DIR/src/main.py" ]]; then
        log_success "main.py is executable"
    else
        log_warning "main.py is not executable"
    fi
    
    # Check virtual environment
    increment_total
    if [[ -f "$ASZ_INSTALL_DIR/venv/bin/python" ]]; then
        local python_version=$("$ASZ_INSTALL_DIR/venv/bin/python" --version 2>&1)
        log_success "Virtual environment Python: $python_version"
    else
        log_error "Virtual environment Python not found"
    fi
}

check_python_dependencies() {
    log_header "Python Dependencies"
    
    local python_executable="$ASZ_INSTALL_DIR/venv/bin/python"
    
    if [[ ! -x "$python_executable" ]]; then
        log_error "Python executable not found or not executable"
        return 1
    fi
    
    # Critical dependencies
    local critical_deps=(
        "PyQt6"
        "PyQt6.QtCore"
        "PyQt6.QtWidgets"
        "PIL"
        "numpy"
        "yaml"
    )
    
    for dep in "${critical_deps[@]}"; do
        increment_total
        if "$python_executable" -c "import $dep" 2>/dev/null; then
            log_success "Python dependency available: $dep"
        else
            log_error "Python dependency missing: $dep"
        fi
    done
    
    # Optional dependencies
    local optional_deps=(
        "google.auth"
        "googleapiclient"
        "requests"
    )
    
    for dep in "${optional_deps[@]}"; do
        increment_total
        if "$python_executable" -c "import $dep" 2>/dev/null; then
            log_success "Optional dependency available: $dep"
        else
            log_warning "Optional dependency missing: $dep (required for Google Photos sync)"
        fi
    done
}

check_system_configuration() {
    log_header "System Configuration"
    
    # Check boot configuration (Raspberry Pi)
    increment_total
    if [[ -f "/boot/config.txt" ]]; then
        if grep -q "camera_auto_detect=1" /boot/config.txt; then
            log_success "Camera auto-detect enabled in boot config"
        else
            log_warning "Camera auto-detect not found in boot config"
        fi
    else
        log_warning "Boot config file not found (not a Raspberry Pi?)"
    fi
    
    # Check GPU memory split
    increment_total
    if command -v vcgencmd >/dev/null 2>&1; then
        local gpu_mem=$(vcgencmd get_mem gpu 2>/dev/null | cut -d'=' -f2)
        if [[ "$gpu_mem" ]]; then
            local gpu_mb=$(echo "$gpu_mem" | sed 's/M//')
            if (( gpu_mb >= 128 )); then
                log_success "GPU memory adequate: $gpu_mem"
            else
                log_warning "GPU memory may be too low: $gpu_mem (recommend 128M+)"
            fi
        fi
    else
        log_warning "Cannot check GPU memory (vcgencmd not available)"
    fi
    
    # Check X11 configuration
    increment_total
    if [[ -f "/etc/X11/xorg.conf" ]]; then
        log_success "X11 configuration file exists"
    else
        log_warning "X11 configuration file not found"
    fi
    
    # Check auto-login configuration
    increment_total
    if [[ -f "/etc/systemd/system/getty@tty1.service.d/override.conf" ]]; then
        if grep -q "autologin" /etc/systemd/system/getty@tty1.service.d/override.conf; then
            log_success "Auto-login configured"
        else
            log_warning "Auto-login configuration found but may not be correct"
        fi
    else
        log_warning "Auto-login configuration not found"
    fi
}

check_camera_hardware() {
    log_header "Camera Hardware"
    
    # Check if libcamera tools are available
    increment_total
    if command -v libcamera-hello >/dev/null 2>&1; then
        log_success "libcamera tools available"
    else
        log_warning "libcamera tools not found"
        return 0  # Don't continue camera tests
    fi
    
    # Test camera detection
    increment_total
    if timeout 10 libcamera-hello --list-cameras >/dev/null 2>&1; then
        local camera_count=$(libcamera-hello --list-cameras 2>&1 | grep -c "Available cameras" 2>/dev/null || echo "0")
        if [[ "$camera_count" -gt 0 ]]; then
            log_success "Camera hardware detected"
        else
            log_warning "libcamera works but no cameras detected"
        fi
    else
        log_warning "Camera detection failed or timed out"
    fi
    
    # Check video devices
    increment_total
    if ls /dev/video* >/dev/null 2>&1; then
        local video_devices=$(ls /dev/video* | wc -l)
        log_success "Video devices available: $video_devices"
    else
        log_warning "No video devices found in /dev/"
    fi
    
    # Check camera permissions
    increment_total
    if [[ -c "/dev/video0" ]]; then
        if groups "$ASZ_USER" | grep -q video; then
            log_success "Camera device permissions OK"
        else
            log_warning "User may not have camera access (not in video group)"
        fi
    else
        log_warning "Primary video device /dev/video0 not found"
    fi
}

check_network_connectivity() {
    log_header "Network Connectivity"
    
    # Check basic connectivity
    increment_total
    if ping -c 1 8.8.8.8 >/dev/null 2>&1; then
        log_success "Internet connectivity available"
    else
        log_warning "No internet connectivity (sync features will not work)"
    fi
    
    # Check DNS resolution
    increment_total
    if nslookup google.com >/dev/null 2>&1; then
        log_success "DNS resolution working"
    else
        log_warning "DNS resolution issues"
    fi
    
    # Check Google APIs reachability
    increment_total
    if curl -s --max-time 10 https://www.googleapis.com >/dev/null 2>&1; then
        log_success "Google APIs reachable"
    else
        log_warning "Cannot reach Google APIs (Google Photos sync may not work)"
    fi
    
    # Check active network interfaces
    local interfaces=$(ip link show | grep "state UP" | cut -d':' -f2 | tr -d ' ')
    if [[ -n "$interfaces" ]]; then
        log_info "Active network interfaces: $(echo "$interfaces" | tr '\n' ' ')"
    fi
}

check_systemd_service() {
    log_header "Systemd Service"
    
    # Check if service file exists
    increment_total
    if [[ -f "/etc/systemd/system/asz-cam-os.service" ]]; then
        log_success "Service file exists"
    else
        log_error "Service file missing: /etc/systemd/system/asz-cam-os.service"
        return 1
    fi
    
    # Check if service is enabled
    increment_total
    if systemctl is-enabled asz-cam-os >/dev/null 2>&1; then
        log_success "Service is enabled for auto-start"
    else
        log_error "Service is not enabled for auto-start"
    fi
    
    # Check service status
    increment_total
    local service_status=$(systemctl is-active asz-cam-os 2>/dev/null || echo "inactive")
    case "$service_status" in
        "active")
            log_success "Service is currently active"
            ;;
        "inactive")
            log_warning "Service is not currently running"
            ;;
        "failed")
            log_error "Service has failed"
            ;;
        *)
            log_warning "Service status unknown: $service_status"
            ;;
    esac
    
    # Check for recent service errors
    increment_total
    local error_count=$(journalctl -u asz-cam-os --since "1 hour ago" --no-pager 2>/dev/null | grep -c "ERROR\|CRITICAL" || echo "0")
    if [[ "$error_count" -eq 0 ]]; then
        log_success "No recent service errors"
    else
        log_warning "Recent service errors found: $error_count"
    fi
}

check_storage_and_directories() {
    log_header "Storage and Directories"
    
    # Check required directories
    local required_directories=(
        "$ASZ_INSTALL_DIR"
        "$ASZ_HOME/.config/aszcam"
        "$ASZ_HOME/Pictures/ASZCam"
        "/var/log/aszcam"
    )
    
    for dir in "${required_directories[@]}"; do
        increment_total
        if [[ -d "$dir" ]]; then
            log_success "Directory exists: $dir"
            
            # Check write permissions
            if [[ -w "$dir" ]]; then
                log_success "Directory writable: $dir"
            else
                log_error "Directory not writable: $dir"
            fi
        else
            log_error "Required directory missing: $dir"
        fi
    done
    
    # Check available storage space
    increment_total
    local available_space=$(df -h "$ASZ_HOME" | awk 'NR==2 {print $4}')
    local available_gb=$(df -BG "$ASZ_HOME" | awk 'NR==2 {print $4}' | sed 's/G//')
    
    if [[ "$available_gb" -gt 2 ]]; then
        log_success "Available storage: $available_space"
    else
        log_warning "Low storage space: $available_space available"
    fi
}

run_quick_functional_test() {
    log_header "Quick Functional Test"
    
    local python_executable="$ASZ_INSTALL_DIR/venv/bin/python"
    
    # Test basic import of main modules
    increment_total
    if "$python_executable" -c "
import sys
sys.path.insert(0, '$ASZ_INSTALL_DIR')
from src.config.settings import settings
print('Settings loaded successfully')
" 2>/dev/null; then
        log_success "Core modules can be imported"
    else
        log_error "Cannot import core modules"
    fi
    
    # Test configuration loading
    increment_total
    if "$python_executable" -c "
import sys
import os
# Create test directories to avoid permission errors
test_dirs = ['$ASZ_HOME/.config/aszcam', '$ASZ_HOME/Pictures/ASZCam']
for d in test_dirs:
    os.makedirs(d, exist_ok=True)
sys.path.insert(0, '$ASZ_INSTALL_DIR')
from src.config.settings import Settings
s = Settings()
print('Configuration system working')
" 2>/dev/null; then
        log_success "Configuration system functional"
    else
        log_warning "Configuration system has issues"
    fi
}

show_summary() {
    log_header "Validation Summary"
    
    echo "" | tee -a "$VALIDATION_LOG"
    echo "===============================================" | tee -a "$VALIDATION_LOG"
    echo "           VALIDATION RESULTS" | tee -a "$VALIDATION_LOG"
    echo "===============================================" | tee -a "$VALIDATION_LOG"
    echo "Total Checks: $TOTAL_CHECKS" | tee -a "$VALIDATION_LOG"
    echo -e "${GREEN}Passed: $PASSED_CHECKS${NC}" | tee -a "$VALIDATION_LOG"
    echo -e "${RED}Failed: $FAILED_CHECKS${NC}" | tee -a "$VALIDATION_LOG"
    echo -e "${YELLOW}Warnings: $WARNING_CHECKS${NC}" | tee -a "$VALIDATION_LOG"
    
    local success_rate=0
    if [[ $TOTAL_CHECKS -gt 0 ]]; then
        success_rate=$(( (PASSED_CHECKS * 100) / TOTAL_CHECKS ))
    fi
    echo "Success Rate: ${success_rate}%" | tee -a "$VALIDATION_LOG"
    
    echo "" | tee -a "$VALIDATION_LOG"
    
    if [[ $FAILED_CHECKS -eq 0 ]]; then
        if [[ $WARNING_CHECKS -eq 0 ]]; then
            echo -e "${GREEN}${BOLD}✓ VALIDATION PASSED${NC}" | tee -a "$VALIDATION_LOG"
            echo "ASZ Cam OS installation appears to be working correctly!" | tee -a "$VALIDATION_LOG"
        else
            echo -e "${YELLOW}${BOLD}⚠ VALIDATION PASSED WITH WARNINGS${NC}" | tee -a "$VALIDATION_LOG"
            echo "ASZ Cam OS installation is functional but has some minor issues." | tee -a "$VALIDATION_LOG"
        fi
    else
        echo -e "${RED}${BOLD}✗ VALIDATION FAILED${NC}" | tee -a "$VALIDATION_LOG"
        echo "ASZ Cam OS installation has critical issues that need to be resolved." | tee -a "$VALIDATION_LOG"
    fi
    
    echo "" | tee -a "$VALIDATION_LOG"
    echo "Detailed log saved to: $VALIDATION_LOG" | tee -a "$VALIDATION_LOG"
    
    # Provide next steps
    if [[ $FAILED_CHECKS -gt 0 ]]; then
        echo "" | tee -a "$VALIDATION_LOG"
        echo "RECOMMENDED ACTIONS:" | tee -a "$VALIDATION_LOG"
        echo "1. Review the failed checks above" | tee -a "$VALIDATION_LOG"
        echo "2. Run the installation script again: sudo ./scripts/install.sh" | tee -a "$VALIDATION_LOG"
        echo "3. Check the troubleshooting guide: docs/TROUBLESHOOTING.md" | tee -a "$VALIDATION_LOG"
        echo "4. Report issues at: https://github.com/mynameisrober/ASZ-Cam-OS/issues" | tee -a "$VALIDATION_LOG"
    elif [[ $WARNING_CHECKS -gt 0 ]]; then
        echo "" | tee -a "$VALIDATION_LOG"
        echo "OPTIONAL IMPROVEMENTS:" | tee -a "$VALIDATION_LOG"
        echo "1. Review the warnings above" | tee -a "$VALIDATION_LOG"
        echo "2. Install optional dependencies for full functionality" | tee -a "$VALIDATION_LOG"
        echo "3. Configure Google Photos sync if desired" | tee -a "$VALIDATION_LOG"
    else
        echo "" | tee -a "$VALIDATION_LOG"
        echo "NEXT STEPS:" | tee -a "$VALIDATION_LOG"
        echo "1. Reboot to ensure all changes take effect: sudo reboot" | tee -a "$VALIDATION_LOG"
        echo "2. ASZ Cam OS should start automatically after reboot" | tee -a "$VALIDATION_LOG"
        echo "3. Configure Google Photos sync in settings if desired" | tee -a "$VALIDATION_LOG"
        echo "4. Read the user guide: docs/USER_GUIDE.md" | tee -a "$VALIDATION_LOG"
    fi
}

# Main validation process
main() {
    show_header
    
    log_info "Starting ASZ Cam OS installation validation..."
    log_info "Validation log: $VALIDATION_LOG"
    
    # Run validation checks
    check_system_info
    check_user_and_permissions
    check_installation_files
    check_python_dependencies
    check_system_configuration
    check_camera_hardware
    check_network_connectivity
    check_systemd_service
    check_storage_and_directories
    run_quick_functional_test
    
    # Show final summary
    show_summary
    
    # Return appropriate exit code
    if [[ $FAILED_CHECKS -eq 0 ]]; then
        exit 0
    else
        exit 1
    fi
}

# Handle script interruption
trap 'echo "Validation interrupted!"; exit 130' INT TERM

# Run main function
main "$@"
