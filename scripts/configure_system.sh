#!/bin/bash
# ASZ Cam OS - System Configuration Script
# Configures the operating system for optimal camera operation
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
    echo -e "${BLUE}[Config]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[Config]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[Config]${NC} $1"
}

log_error() {
    echo -e "${RED}[Config]${NC} $1"
}

configure_x11_display() {
    log_info "Configuring X11 display system..."
    
    # Create X11 configuration directory
    mkdir -p /etc/X11/xorg.conf.d
    
    # Install X11 configuration files from install directory
    SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
    PROJECT_ROOT="$(dirname "${SCRIPT_DIR}")"
    
    if [[ -f "${PROJECT_ROOT}/install/xorg.conf" ]]; then
        cp "${PROJECT_ROOT}/install/xorg.conf" /etc/X11/
        log_info "Installed custom X11 configuration"
    else
        # Create basic X11 configuration
        cat > /etc/X11/xorg.conf << EOF
# ASZ Cam OS X11 Configuration
Section "ServerLayout"
    Identifier     "Layout0"
    Screen      0  "Screen0"
    InputDevice    "Keyboard0" "CoreKeyboard"
    InputDevice    "Mouse0" "CorePointer"
EndSection

Section "Files"
    ModulePath   "/usr/lib/xorg/modules"
    FontPath     "/usr/share/fonts/X11/misc"
    FontPath     "/usr/share/fonts/X11/cyrillic"
    FontPath     "/usr/share/fonts/X11/100dpi/:unscaled"
    FontPath     "/usr/share/fonts/X11/75dpi/:unscaled"
    FontPath     "/usr/share/fonts/X11/Type1"
    FontPath     "/usr/share/fonts/X11/100dpi"
    FontPath     "/usr/share/fonts/X11/75dpi"
    FontPath     "/var/lib/defoma/x-ttcidfont-conf.d/dirs/TrueType"
EndSection

Section "Module"
    Load  "dbe"
    Load  "extmod"
    Load  "type1"
    Load  "freetype"
    Load  "glx"
EndSection

Section "InputDevice"
    Identifier  "Keyboard0"
    Driver      "kbd"
EndSection

Section "InputDevice"
    Identifier  "Mouse0"
    Driver      "mouse"
    Option      "Protocol" "auto"
    Option      "Device" "/dev/input/mice"
    Option      "Emulate3Buttons" "no"
    Option      "ZAxisMapping" "4 5"
EndSection

Section "Monitor"
    Identifier   "Monitor0"
    VendorName   "Monitor Vendor"
    ModelName    "Monitor Model"
EndSection

Section "Device"
    Identifier  "Videocard0"
    Driver      "fbdev"
EndSection

Section "Screen"
    Identifier "Screen0"
    Device     "Videocard0"
    Monitor    "Monitor0"
    DefaultDepth     24
    Option         "fbdev" "/dev/fb0"
    SubSection "Display"
        Viewport   0 0
        Depth     24
    EndSubSection
EndSection
EOF
        log_info "Created basic X11 configuration"
    fi
    
    log_success "X11 display configuration complete"
}

configure_auto_login() {
    log_info "Configuring auto-login for ${ASZ_USER}..."
    
    # Configure systemd auto-login
    mkdir -p /etc/systemd/system/getty@tty1.service.d
    cat > /etc/systemd/system/getty@tty1.service.d/override.conf << EOF
[Service]
ExecStart=
ExecStart=-/sbin/agetty --autologin ${ASZ_USER} --noclear %I \$TERM
EOF
    
    systemctl daemon-reload
    systemctl enable getty@tty1.service
    
    log_success "Auto-login configured"
}

configure_desktop_environment() {
    log_info "Configuring lightweight desktop environment..."
    
    # Install lightweight window manager
    apt-get update
    apt-get install -y \
        openbox \
        obconf \
        obmenu \
        lxpanel \
        pcmanfm \
        lxterminal \
        unclutter \
        xscreensaver
    
    # Create openbox configuration for ASZ user
    mkdir -p "${ASZ_HOME}/.config/openbox"
    
    # Openbox autostart configuration
    cat > "${ASZ_HOME}/.config/openbox/autostart" << EOF
# ASZ Cam OS Openbox Autostart
# Hide mouse cursor when idle
unclutter -idle 3 &

# Disable screen blanking
xset s off
xset -dpms
xset s noblank

# Start ASZ Cam OS application
cd ${ASZ_INSTALL_DIR}
${ASZ_INSTALL_DIR}/venv/bin/python ${ASZ_INSTALL_DIR}/src/main.py &
EOF
    
    # Create basic openbox menu
    cat > "${ASZ_HOME}/.config/openbox/menu.xml" << EOF
<?xml version="1.0" encoding="UTF-8"?>
<openbox_menu>
<menu id="apps-menu" label="Applications">
    <item label="ASZ Cam">
        <action name="Execute">
            <command>${ASZ_INSTALL_DIR}/venv/bin/python ${ASZ_INSTALL_DIR}/src/main.py</command>
        </action>
    </item>
    <item label="Terminal">
        <action name="Execute">
            <command>lxterminal</command>
        </action>
    </item>
    <item label="File Manager">
        <action name="Execute">
            <command>pcmanfm</command>
        </action>
    </item>
    <separator/>
    <item label="Restart">
        <action name="Restart"/>
    </item>
    <item label="Exit">
        <action name="Exit"/>
    </item>
</menu>
<menu id="root-menu" label="Openbox 3">
    <separator label="ASZ Cam OS"/>
    <menu id="apps-menu"/>
    <separator/>
    <item label="Reconfigure">
        <action name="Reconfigure"/>
    </item>
</menu>
</openbox_menu>
EOF
    
    # Set ownership
    chown -R "${ASZ_USER}:${ASZ_USER}" "${ASZ_HOME}/.config/openbox"
    chmod +x "${ASZ_HOME}/.config/openbox/autostart"
    
    log_success "Desktop environment configured"
}

configure_startup_script() {
    log_info "Configuring startup script..."
    
    # Create .xinitrc for X11 startup
    cat > "${ASZ_HOME}/.xinitrc" << EOF
#!/bin/bash
# ASZ Cam OS X11 Startup Script

# Set display
export DISPLAY=:0

# Configure X11 settings
xset s off         # Don't activate screensaver
xset -dpms         # Disable DPMS (Energy Star) features.
xset s noblank     # Don't blank the video device

# Hide mouse cursor after 3 seconds of inactivity
unclutter -idle 3 -root &

# Start window manager
exec openbox-session
EOF
    
    # Create .bashrc addition for auto-startx
    cat >> "${ASZ_HOME}/.bashrc" << EOF

# ASZ Cam OS - Auto start X11 on login
if [[ -z \$DISPLAY && \$XDG_VTNR -eq 1 ]]; then
    exec startx
fi
EOF
    
    # Set permissions
    chown "${ASZ_USER}:${ASZ_USER}" "${ASZ_HOME}/.xinitrc"
    chown "${ASZ_USER}:${ASZ_USER}" "${ASZ_HOME}/.bashrc"
    chmod +x "${ASZ_HOME}/.xinitrc"
    
    log_success "Startup script configured"
}

configure_plymouth_splash() {
    log_info "Configuring boot splash screen..."
    
    # Install plymouth if not present
    apt-get install -y plymouth plymouth-themes
    
    # Create simple ASZ Cam splash theme
    mkdir -p /usr/share/plymouth/themes/aszcam
    
    cat > /usr/share/plymouth/themes/aszcam/aszcam.plymouth << EOF
[Plymouth Theme]
Name=ASZ Cam OS
Description=ASZ Camera Operating System Boot Splash
ModuleName=script

[script]
ImageDir=/usr/share/plymouth/themes/aszcam
ScriptFile=/usr/share/plymouth/themes/aszcam/aszcam.script
EOF
    
    cat > /usr/share/plymouth/themes/aszcam/aszcam.script << EOF
Window.GetMaxWidth = fun (){
    return Window.GetWidth();
};

Window.GetMaxHeight = fun (){
    return Window.GetHeight();
};

// Create background
background = Image("background.png");
if (background) {
    background = background.Scale(Window.GetMaxWidth(), Window.GetMaxHeight());
    background_sprite = Sprite(background);
    background_sprite.SetPosition(0, 0, -100);
}

// Create logo
logo = Image("logo.png");
if (logo) {
    logo_sprite = Sprite(logo);
    logo_sprite.SetX(Window.GetMaxWidth() / 2 - logo.GetWidth() / 2);
    logo_sprite.SetY(Window.GetMaxHeight() / 2 - logo.GetHeight() / 2);
}

// Progress bar
progress_bar.original_image = Image("progress_bar.png");
progress_bar.sprite = Sprite();
progress_bar.x = Window.GetMaxWidth() / 2 - progress_bar.original_image.GetWidth() / 2;
progress_bar.y = Window.GetMaxHeight() * 0.75;
progress_bar.sprite.SetPosition(progress_bar.x, progress_bar.y, 2);

fun progress_callback(duration, progress) {
    if (progress_bar.original_image) {
        progress_bar.image = progress_bar.original_image.Scale(progress_bar.original_image.GetWidth() * progress, progress_bar.original_image.GetHeight());
        progress_bar.sprite.SetImage(progress_bar.image);
    }
}

Plymouth.SetBootProgressFunction(progress_callback);
EOF
    
    # Create simple placeholder images (1x1 transparent PNGs)
    for img in background logo progress_bar; do
        # Create minimal transparent PNG
        python3 -c "
from PIL import Image
img = Image.new('RGBA', (100, 100), (0, 0, 0, 0))
img.save('/usr/share/plymouth/themes/aszcam/${img}.png')
"
    done
    
    # Set Plymouth theme
    plymouth-set-default-theme aszcam
    update-initramfs -u
    
    log_success "Plymouth splash screen configured"
}

configure_log_rotation() {
    log_info "Configuring log rotation..."
    
    # Create logrotate configuration for ASZ Cam
    cat > /etc/logrotate.d/aszcam << EOF
/var/log/aszcam/*.log {
    daily
    missingok
    rotate 7
    compress
    delaycompress
    notifempty
    create 0644 ${ASZ_USER} ${ASZ_USER}
    postrotate
        systemctl reload asz-cam-os || true
    endscript
}
EOF
    
    log_success "Log rotation configured"
}

configure_network() {
    log_info "Configuring network settings..."
    
    # Configure NetworkManager for WiFi management
    apt-get install -y network-manager
    
    # Create NetworkManager configuration
    cat > /etc/NetworkManager/NetworkManager.conf << EOF
[main]
plugins=ifupdown,keyfile
dhcp=dhclient

[ifupdown]
managed=false

[logging]
level=INFO
domains=CORE,ETHER,IP,WIFI,DEVICE,WIFI_SCAN,DHCP,SUSPEND
EOF
    
    systemctl enable NetworkManager
    
    log_success "Network configuration complete"
}

configure_udev_rules() {
    log_info "Configuring udev rules for camera access..."
    
    # Create udev rules for camera devices
    cat > /etc/udev/rules.d/99-aszcam-camera.rules << EOF
# ASZ Cam OS Camera Device Rules
# Allow camera access for ASZ user

# USB cameras
SUBSYSTEM=="usb", ATTRS{bInterfaceClass}=="0e", GROUP="video", MODE="0664"

# Video4Linux devices
SUBSYSTEM=="video4linux", GROUP="video", MODE="0664"

# Camera devices
KERNEL=="video[0-9]*", GROUP="video", MODE="0664"

# GPIO devices (for Raspberry Pi camera)
SUBSYSTEM=="gpio", GROUP="gpio", MODE="0664"
EOF
    
    udevadm control --reload-rules
    udevadm trigger
    
    log_success "Udev rules configured"
}

configure_security() {
    log_info "Configuring security settings..."
    
    # Configure sudo for ASZ user
    echo "${ASZ_USER} ALL=(ALL) NOPASSWD: /usr/bin/systemctl restart asz-cam-os" > "/etc/sudoers.d/aszcam"
    echo "${ASZ_USER} ALL=(ALL) NOPASSWD: /usr/bin/systemctl stop asz-cam-os" >> "/etc/sudoers.d/aszcam"
    echo "${ASZ_USER} ALL=(ALL) NOPASSWD: /usr/bin/systemctl start asz-cam-os" >> "/etc/sudoers.d/aszcam"
    echo "${ASZ_USER} ALL=(ALL) NOPASSWD: /sbin/reboot" >> "/etc/sudoers.d/aszcam"
    echo "${ASZ_USER} ALL=(ALL) NOPASSWD: /sbin/shutdown -h now" >> "/etc/sudoers.d/aszcam"
    
    chmod 0440 "/etc/sudoers.d/aszcam"
    
    # Basic firewall configuration
    if command -v ufw &> /dev/null; then
        ufw --force enable
        ufw default deny incoming
        ufw default allow outgoing
        ufw allow ssh
        ufw allow from 192.168.0.0/16
        ufw allow from 10.0.0.0/8
        ufw allow from 172.16.0.0/12
    fi
    
    log_success "Security settings configured"
}

optimize_system_services() {
    log_info "Optimizing system services..."
    
    # Disable unnecessary services
    SERVICES_TO_DISABLE=(
        "bluetooth.service"
        "hciuart.service" 
        "avahi-daemon.service"
        "triggerhappy.service"
    )
    
    for service in "${SERVICES_TO_DISABLE[@]}"; do
        if systemctl is-enabled "$service" &>/dev/null; then
            systemctl disable "$service"
            log_info "Disabled service: $service"
        fi
    done
    
    # Enable required services
    SERVICES_TO_ENABLE=(
        "NetworkManager.service"
        "systemd-timesyncd.service"
    )
    
    for service in "${SERVICES_TO_ENABLE[@]}"; do
        systemctl enable "$service"
        log_info "Enabled service: $service"
    done
    
    log_success "System services optimized"
}

create_backup_script() {
    log_info "Creating system backup script..."
    
    cat > "${ASZ_INSTALL_DIR}/scripts/backup_system.sh" << 'EOF'
#!/bin/bash
# ASZ Cam OS System Backup Script

BACKUP_DIR="/home/pi/ASZCam/backups"
BACKUP_DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="${BACKUP_DIR}/aszcam_backup_${BACKUP_DATE}.tar.gz"

mkdir -p "${BACKUP_DIR}"

echo "Creating system backup..."
tar -czf "${BACKUP_FILE}" \
    /home/pi/.config/aszcam \
    /home/pi/Pictures/ASZCam \
    /etc/systemd/system/asz-cam-os.service \
    /etc/X11/xorg.conf \
    --exclude='*.log'

echo "Backup created: ${BACKUP_FILE}"
echo "Cleaning old backups (keeping last 5)..."
ls -t "${BACKUP_DIR}"/aszcam_backup_*.tar.gz | tail -n +6 | xargs -r rm

echo "Backup complete!"
EOF
    
    chmod +x "${ASZ_INSTALL_DIR}/scripts/backup_system.sh"
    chown "${ASZ_USER}:${ASZ_USER}" "${ASZ_INSTALL_DIR}/scripts/backup_system.sh"
    
    log_success "Backup script created"
}

show_config_summary() {
    echo ""
    echo "==============================================="
    log_success "System Configuration Complete!"
    echo "==============================================="
    echo ""
    echo "Configured:"
    echo "- X11 display system"
    echo "- Auto-login for ${ASZ_USER}"
    echo "- Lightweight desktop (Openbox)"
    echo "- Startup scripts and auto-launch"
    echo "- Plymouth boot splash"
    echo "- Log rotation"
    echo "- Network management"
    echo "- Camera device access rules"
    echo "- Security settings"
    echo "- Optimized system services"
    echo "- System backup script"
    echo ""
    echo "System will automatically start ASZ Cam OS on boot"
    echo ""
}

# Main function
main() {
    log_info "Starting system configuration..."
    
    configure_x11_display
    configure_auto_login
    configure_desktop_environment
    configure_startup_script
    configure_plymouth_splash
    configure_log_rotation
    configure_network
    configure_udev_rules
    configure_security
    optimize_system_services
    create_backup_script
    
    show_config_summary
}

# Run main function if script is executed directly
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi