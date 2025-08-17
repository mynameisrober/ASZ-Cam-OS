#!/bin/bash
# ASZ Cam OS - Raspberry Pi Configuration Settings
# Automated raspi-config settings for optimal camera performance
# Author: ASZ Development Team
# Version: 1.0.0

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Helper functions
log_info() {
    echo -e "${BLUE}[raspi-config]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[raspi-config]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[raspi-config]${NC} $1"
}

log_error() {
    echo -e "${RED}[raspi-config]${NC} $1"
}

check_raspberry_pi() {
    if ! command -v raspi-config &> /dev/null; then
        log_error "raspi-config not found. This script is for Raspberry Pi only."
        exit 1
    fi
    
    if [[ $EUID -ne 0 ]]; then
        log_error "This script must be run as root"
        exit 1
    fi
    
    log_info "Raspberry Pi detected, proceeding with configuration..."
}

configure_camera() {
    log_info "Enabling camera interface..."
    
    # Enable camera using raspi-config nonint mode
    raspi-config nonint do_camera 0
    
    log_success "Camera interface enabled"
}

configure_interfaces() {
    log_info "Configuring interfaces..."
    
    # Enable I2C
    raspi-config nonint do_i2c 0
    log_info "I2C interface enabled"
    
    # Enable SPI
    raspi-config nonint do_spi 0
    log_info "SPI interface enabled"
    
    # Disable serial console (keep UART enabled for hardware)
    raspi-config nonint do_serial 1
    log_info "Serial console disabled"
    
    # Enable SSH (useful for remote management)
    raspi-config nonint do_ssh 0
    log_info "SSH enabled"
    
    log_success "Interfaces configured"
}

configure_boot_options() {
    log_info "Configuring boot options..."
    
    # Set boot to desktop auto-login
    raspi-config nonint do_boot_behaviour B4
    log_info "Auto-login to desktop enabled"
    
    # Disable wait for network on boot (faster boot)
    raspi-config nonint do_boot_wait 1
    log_info "Boot wait for network disabled"
    
    # Enable splash screen (can be customized later)
    raspi-config nonint do_boot_splash 0
    log_info "Boot splash screen enabled"
    
    log_success "Boot options configured"
}

configure_localization() {
    log_info "Configuring localization..."
    
    # Set locale to en_US.UTF-8 (can be changed by user later)
    raspi-config nonint do_change_locale en_US.UTF-8
    log_info "Locale set to en_US.UTF-8"
    
    # Set timezone to UTC (can be changed by user later)
    raspi-config nonint do_change_timezone UTC
    log_info "Timezone set to UTC"
    
    # Set keyboard layout to US (can be changed by user later)
    raspi-config nonint do_configure_keyboard us
    log_info "Keyboard layout set to US"
    
    # Set WiFi country code (will need to be set by user for their location)
    # raspi-config nonint do_wifi_country US
    log_warning "WiFi country code should be set by user via raspi-config"
    
    log_success "Localization configured"
}

configure_advanced_options() {
    log_info "Configuring advanced options..."
    
    # Expand filesystem to use full SD card
    raspi-config nonint do_expand_rootfs
    log_info "Filesystem expanded to use full SD card"
    
    # Set memory split (already done in boot_config.txt, but ensure it's set)
    raspi-config nonint do_memory_split 128
    log_info "GPU memory split set to 128MB"
    
    # Enable GL driver (Full KMS)
    raspi-config nonint do_gldriver G2
    log_info "OpenGL driver enabled (Full KMS)"
    
    # Disable overscan (for most modern displays)
    raspi-config nonint do_overscan 1
    log_info "Overscan disabled"
    
    log_success "Advanced options configured"
}

configure_performance() {
    log_info "Configuring performance settings..."
    
    # These settings complement the ones in boot_config.txt
    
    # CPU governor is handled by systemd service
    log_info "CPU governor will be set by systemd service"
    
    # GPU memory split already set
    log_info "GPU memory configuration already applied"
    
    # Audio output to auto (can be changed to HDMI/Jack as needed)
    raspi-config nonint do_audio 0
    log_info "Audio output set to auto"
    
    log_success "Performance settings configured"
}

configure_security() {
    log_info "Configuring security settings..."
    
    # Change default pi user password prompt
    log_warning "Default password should be changed!"
    log_warning "Run: passwd pi"
    
    # Enable firewall (if ufw is installed)
    if command -v ufw &> /dev/null; then
        ufw --force enable
        log_info "Firewall enabled"
    fi
    
    log_success "Security configuration complete"
}

update_system() {
    log_info "Updating system packages..."
    
    # Update package lists
    apt-get update
    
    # Upgrade system packages
    apt-get upgrade -y
    
    # Install essential packages if not present
    apt-get install -y \
        curl \
        wget \
        git \
        vim \
        htop \
        tree \
        unzip \
        build-essential
    
    log_success "System packages updated"
}

create_configuration_script() {
    log_info "Creating post-configuration script..."
    
    # Create a script for user to run additional configuration
    cat > /home/pi/configure_aszcam.sh << 'EOF'
#!/bin/bash
# ASZ Cam OS User Configuration Script
# Run this script to configure additional settings

echo "ASZ Cam OS Additional Configuration"
echo "=================================="
echo ""

# WiFi country configuration
echo "Setting WiFi country code (required for WiFi to work):"
echo "Available countries: US, GB, DE, FR, IT, ES, JP, AU, CA, etc."
read -p "Enter your country code (e.g., US): " WIFI_COUNTRY
if [[ ! -z "$WIFI_COUNTRY" ]]; then
    sudo raspi-config nonint do_wifi_country "$WIFI_COUNTRY"
    echo "WiFi country set to $WIFI_COUNTRY"
fi

# Timezone configuration
echo ""
echo "Current timezone: $(timedatectl show --property=Timezone --value)"
read -p "Do you want to change the timezone? (y/N): " CHANGE_TZ
if [[ "$CHANGE_TZ" =~ ^[Yy]$ ]]; then
    sudo dpkg-reconfigure tzdata
fi

# Password change reminder
echo ""
echo "Security Reminder:"
echo "=================="
echo "Please change the default password for security:"
echo "Run: passwd"
echo ""

# Google Photos setup
echo "Google Photos Sync Setup:"
echo "========================"
echo "To enable Google Photos sync:"
echo "1. Visit the ASZ Cam OS settings"
echo "2. Navigate to Sync settings"
echo "3. Enable Google Photos sync"
echo "4. Follow the authentication prompts"
echo ""

echo "Configuration complete!"
echo "Reboot is recommended: sudo reboot"
EOF
    
    chmod +x /home/pi/configure_aszcam.sh
    chown pi:pi /home/pi/configure_aszcam.sh
    
    log_success "User configuration script created at /home/pi/configure_aszcam.sh"
}

show_configuration_summary() {
    echo ""
    echo "==============================================="
    log_success "Raspberry Pi Configuration Complete!"
    echo "==============================================="
    echo ""
    echo "Configured Settings:"
    echo "- Camera interface: Enabled"
    echo "- I2C interface: Enabled"
    echo "- SPI interface: Enabled"
    echo "- SSH: Enabled"
    echo "- Auto-login: Enabled"
    echo "- GPU memory: 128MB"
    echo "- OpenGL driver: Full KMS"
    echo "- Filesystem: Expanded"
    echo "- Locale: en_US.UTF-8"
    echo "- Timezone: UTC"
    echo ""
    echo "Post-Installation Steps:"
    echo "1. Set WiFi country code: sudo raspi-config"
    echo "2. Change default password: passwd"
    echo "3. Configure timezone if needed: sudo dpkg-reconfigure tzdata"
    echo "4. Run user configuration: /home/pi/configure_aszcam.sh"
    echo ""
    echo "Reboot required for all changes to take effect:"
    echo "sudo reboot"
    echo ""
}

# Main function
main() {
    log_info "Starting Raspberry Pi configuration..."
    
    check_raspberry_pi
    update_system
    configure_camera
    configure_interfaces
    configure_boot_options
    configure_localization
    configure_advanced_options
    configure_performance
    configure_security
    create_configuration_script
    
    show_configuration_summary
}

# Run main function if script is executed directly
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi