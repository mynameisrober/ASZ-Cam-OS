#!/bin/bash
# ASZ Cam OS - Raspberry Pi Setup Script
# Configures Raspberry Pi specific settings for optimal camera performance
# Author: ASZ Development Team
# Version: 1.0.0

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Configuration
ASZ_USER="${ASZ_USER:-pi}"
ASZ_HOME="/home/${ASZ_USER}"
ASZ_INSTALL_DIR="${ASZ_INSTALL_DIR:-${ASZ_HOME}/ASZCam}"

# Helper functions
log_info() {
    echo -e "${BLUE}[RPi Setup]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[RPi Setup]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[RPi Setup]${NC} $1"
}

log_error() {
    echo -e "${RED}[RPi Setup]${NC} $1"
}

check_raspberry_pi() {
    if ! grep -q "Raspberry Pi" /proc/cpuinfo; then
        log_error "This script is only for Raspberry Pi systems"
        exit 1
    fi
    
    # Get Pi model
    PI_MODEL=$(grep "Model" /proc/cpuinfo | cut -d':' -f2 | xargs)
    log_info "Detected: ${PI_MODEL}"
}

enable_camera_module() {
    log_info "Enabling camera module..."
    
    # Enable camera in config.txt
    if ! grep -q "camera_auto_detect=1" /boot/config.txt; then
        echo "camera_auto_detect=1" >> /boot/config.txt
        log_info "Added camera_auto_detect=1 to /boot/config.txt"
    fi
    
    # Enable legacy camera support if needed
    if ! grep -q "start_x=1" /boot/config.txt; then
        echo "start_x=1" >> /boot/config.txt
        log_info "Added start_x=1 to /boot/config.txt"
    fi
    
    log_success "Camera module configuration updated"
}

configure_gpu_memory() {
    log_info "Configuring GPU memory split..."
    
    # Set GPU memory to 128MB for camera operations
    if ! grep -q "gpu_mem=" /boot/config.txt; then
        echo "gpu_mem=128" >> /boot/config.txt
        log_info "Set GPU memory to 128MB"
    else
        # Update existing gpu_mem setting
        sed -i 's/gpu_mem=.*/gpu_mem=128/' /boot/config.txt
        log_info "Updated GPU memory to 128MB"
    fi
    
    log_success "GPU memory configured"
}

optimize_boot_settings() {
    log_info "Optimizing boot settings for fast startup..."
    
    # Disable unnecessary services for faster boot
    SERVICES_TO_DISABLE=(
        "triggerhappy"
        "dphys-swapfile"
        "keyboard-setup"
        "plymouth"
        "plymouth-log"
    )
    
    for service in "${SERVICES_TO_DISABLE[@]}"; do
        if systemctl is-enabled "$service" &>/dev/null; then
            systemctl disable "$service"
            log_info "Disabled service: $service"
        fi
    done
    
    # Optimize boot parameters
    BOOT_CONFIG_UPDATES=(
        "boot_delay=0"
        "disable_splash=1"
        "initial_turbo=30"
        "force_turbo=0"
        "avoid_warnings=1"
    )
    
    for config in "${BOOT_CONFIG_UPDATES[@]}"; do
        key=$(echo "$config" | cut -d'=' -f1)
        if ! grep -q "^$key=" /boot/config.txt; then
            echo "$config" >> /boot/config.txt
            log_info "Added boot setting: $config"
        fi
    done
    
    log_success "Boot optimization complete"
}

configure_display_settings() {
    log_info "Configuring display settings..."
    
    # HDMI settings for reliable display
    HDMI_SETTINGS=(
        "hdmi_force_hotplug=1"
        "hdmi_group=1"
        "hdmi_mode=16"  # 1080p 60Hz
        "hdmi_drive=2"  # Normal HDMI mode
    )
    
    for setting in "${HDMI_SETTINGS[@]}"; do
        key=$(echo "$setting" | cut -d'=' -f1)
        if ! grep -q "^$key=" /boot/config.txt; then
            echo "$setting" >> /boot/config.txt
            log_info "Added display setting: $setting"
        fi
    done
    
    log_success "Display settings configured"
}

configure_audio_settings() {
    log_info "Configuring audio settings..."
    
    # Set audio output to HDMI by default
    if ! grep -q "dtparam=audio=on" /boot/config.txt; then
        echo "dtparam=audio=on" >> /boot/config.txt
        log_info "Enabled audio output"
    fi
    
    log_success "Audio configuration complete"
}

setup_i2c_spi() {
    log_info "Enabling I2C and SPI interfaces..."
    
    # Enable I2C
    if ! grep -q "dtparam=i2c_arm=on" /boot/config.txt; then
        echo "dtparam=i2c_arm=on" >> /boot/config.txt
        log_info "Enabled I2C interface"
    fi
    
    # Enable SPI
    if ! grep -q "dtparam=spi=on" /boot/config.txt; then
        echo "dtparam=spi=on" >> /boot/config.txt
        log_info "Enabled SPI interface"
    fi
    
    # Load modules
    if ! grep -q "i2c-dev" /etc/modules; then
        echo "i2c-dev" >> /etc/modules
        log_info "Added i2c-dev to modules"
    fi
    
    log_success "I2C and SPI interfaces enabled"
}

configure_performance_governor() {
    log_info "Configuring CPU performance governor..."
    
    # Set performance governor for consistent performance
    echo 'GOVERNOR="performance"' > /etc/default/cpufrequtils
    
    # Create service to set governor on boot
    cat > /etc/systemd/system/cpu-governor.service << EOF
[Unit]
Description=Set CPU Governor to Performance
After=multi-user.target

[Service]
Type=oneshot
ExecStart=/bin/bash -c 'for gov in /sys/devices/system/cpu/cpu*/cpufreq/scaling_governor; do echo performance > \$gov; done'
RemainAfterExit=yes

[Install]
WantedBy=multi-user.target
EOF
    
    systemctl enable cpu-governor.service
    
    log_success "CPU performance governor configured"
}

configure_network_settings() {
    log_info "Configuring network settings..."
    
    # Enable predictable network interface names
    if ! grep -q "net.ifnames=0" /boot/cmdline.txt; then
        sed -i 's/$/ net.ifnames=0/' /boot/cmdline.txt
        log_info "Enabled predictable network interface names"
    fi
    
    # Configure WiFi power management
    cat > /etc/systemd/system/wifi-powersave-off.service << EOF
[Unit]
Description=Turn off WiFi power saving
After=multi-user.target

[Service]
Type=oneshot
RemainAfterExit=yes
ExecStart=/sbin/iw dev wlan0 set power_save off

[Install]
WantedBy=multi-user.target
EOF
    
    systemctl enable wifi-powersave-off.service
    
    log_success "Network settings configured"
}

configure_timezone_locale() {
    log_info "Configuring timezone and locale..."
    
    # Set timezone (can be overridden by user later)
    timedatectl set-timezone UTC
    
    # Configure locale
    locale-gen en_US.UTF-8
    update-locale LANG=en_US.UTF-8
    
    log_success "Timezone and locale configured"
}

optimize_filesystem() {
    log_info "Optimizing filesystem settings..."
    
    # Add tmpfs mounts for better performance and SD card longevity
    if ! grep -q "/tmp" /etc/fstab; then
        echo "tmpfs /tmp tmpfs defaults,noatime,nosuid,size=100m 0 0" >> /etc/fstab
        log_info "Added tmpfs mount for /tmp"
    fi
    
    if ! grep -q "/var/tmp" /etc/fstab; then
        echo "tmpfs /var/tmp tmpfs defaults,noatime,nosuid,size=30m 0 0" >> /etc/fstab
        log_info "Added tmpfs mount for /var/tmp"
    fi
    
    if ! grep -q "/var/log" /etc/fstab; then
        echo "tmpfs /var/log tmpfs defaults,noatime,nosuid,mode=0755,size=100m 0 0" >> /etc/fstab
        log_info "Added tmpfs mount for /var/log"
    fi
    
    log_success "Filesystem optimization complete"
}

install_camera_utilities() {
    log_info "Installing camera utilities..."
    
    # Install additional camera tools
    apt-get update
    apt-get install -y \
        v4l-utils \
        ffmpeg \
        imagemagick \
        exiftool
    
    # Test camera detection
    if command -v libcamera-hello >/dev/null 2>&1; then
        log_info "Testing camera detection..."
        timeout 5 libcamera-hello --list-cameras || log_warning "Camera test timed out"
    fi
    
    log_success "Camera utilities installed"
}

configure_user_groups() {
    log_info "Configuring user groups for camera access..."
    
    # Add user to necessary groups
    usermod -a -G video,gpio,i2c,spi,dialout,plugdev,audio "${ASZ_USER}"
    
    log_success "User groups configured"
}

create_performance_profile() {
    log_info "Creating performance profile..."
    
    # Create sysctl settings for performance
    cat > /etc/sysctl.d/99-aszcam-performance.conf << EOF
# ASZ Cam OS Performance Settings
vm.swappiness=10
vm.dirty_background_ratio=15
vm.dirty_ratio=25
kernel.sched_rt_runtime_us=-1
net.core.rmem_max=134217728
net.core.wmem_max=134217728
EOF
    
    log_success "Performance profile created"
}

backup_original_config() {
    log_info "Backing up original configurations..."
    
    # Create backup directory
    mkdir -p /boot/aszcam-backups
    
    # Backup important files
    cp /boot/config.txt /boot/aszcam-backups/config.txt.backup.$(date +%Y%m%d)
    cp /boot/cmdline.txt /boot/aszcam-backups/cmdline.txt.backup.$(date +%Y%m%d)
    
    log_success "Configuration backups created"
}

show_rpi_summary() {
    echo ""
    echo "==============================================="
    log_success "Raspberry Pi Setup Complete!"
    echo "==============================================="
    echo ""
    echo "Configured:"
    echo "- Camera module enabled"
    echo "- GPU memory optimized (128MB)"
    echo "- Boot time optimized"
    echo "- Display settings configured"
    echo "- Audio enabled"
    echo "- I2C/SPI interfaces enabled"
    echo "- Performance governor set"
    echo "- Network settings optimized"
    echo "- Filesystem optimized"
    echo "- User groups configured"
    echo ""
    echo "Backups saved to: /boot/aszcam-backups/"
    echo ""
    log_warning "A reboot is required for all changes to take effect"
    echo ""
}

# Main function
main() {
    log_info "Starting Raspberry Pi specific setup..."
    
    check_raspberry_pi
    backup_original_config
    enable_camera_module
    configure_gpu_memory
    optimize_boot_settings
    configure_display_settings
    configure_audio_settings
    setup_i2c_spi
    configure_performance_governor
    configure_network_settings
    configure_timezone_locale
    optimize_filesystem
    install_camera_utilities
    configure_user_groups
    create_performance_profile
    
    show_rpi_summary
}

# Run main function if script is executed directly
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi