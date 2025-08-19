# ASZ Cam OS - Troubleshooting Guide

Comprehensive troubleshooting guide for resolving common issues with ASZ Cam OS.

## Table of Contents
- [Quick Diagnostics](#quick-diagnostics)
- [Installation Issues](#installation-issues)
- [Boot and Startup Problems](#boot-and-startup-problems)
- [Camera Issues](#camera-issues)
- [Display Problems](#display-problems)
- [Network and Sync Issues](#network-and-sync-issues)
- [Performance Problems](#performance-problems)
- [System Recovery](#system-recovery)
- [Advanced Diagnostics](#advanced-diagnostics)

## Quick Diagnostics

### System Health Check

Run this quick diagnostic script to check system status:

```bash
#!/bin/bash
# Quick system health check

echo "=== ASZ Cam OS Health Check ==="
echo "Date: $(date)"
echo "Uptime: $(uptime -p)"
echo ""

# Check service status
echo "--- Service Status ---"
systemctl is-active asz-cam-os && echo "✓ ASZ Cam OS: Running" || echo "✗ ASZ Cam OS: Not running"
systemctl is-active NetworkManager && echo "✓ Network: Running" || echo "✗ Network: Not running"

# Check disk space
echo ""
echo "--- Storage ---"
df -h / | grep -v Filesystem
df -h /home/pi/Pictures/ASZCam 2>/dev/null | grep -v Filesystem || echo "Photos directory not found"

# Check camera
echo ""
echo "--- Camera ---"
if command -v libcamera-hello >/dev/null 2>&1; then
    timeout 5 libcamera-hello --list-cameras 2>/dev/null && echo "✓ Camera detected" || echo "✗ Camera not detected"
else
    echo "✗ libcamera tools not installed"
fi

# Check network
echo ""
echo "--- Network ---"
ping -c 1 8.8.8.8 >/dev/null 2>&1 && echo "✓ Internet connectivity" || echo "✗ No internet connection"

# Check GPU memory
echo ""
echo "--- GPU Memory ---"
vcgencmd get_mem gpu 2>/dev/null || echo "Cannot check GPU memory"

# Recent errors
echo ""
echo "--- Recent Errors ---"
journalctl -u asz-cam-os --since "1 hour ago" --no-pager | grep -i error | tail -3
```

Save as `health_check.sh`, make executable, and run:
```bash
chmod +x health_check.sh
./health_check.sh
```

### Quick Fixes

Before diving into detailed troubleshooting, try these quick fixes:

1. **Restart the service**:
   ```bash
   sudo systemctl restart asz-cam-os
   ```

2. **Reboot the system**:
   ```bash
   sudo reboot
   ```

3. **Check available storage**:
   ```bash
   df -h /
   ```

4. **Check camera connection**:
   ```bash
   libcamera-hello --list-cameras
   ```

## Installation Issues

### Installation Script Fails

#### Problem: Permission denied during installation
```bash
bash: ./scripts/install.sh: Permission denied
```

**Solution:**
```bash
chmod +x scripts/install.sh
sudo ./scripts/install.sh
```

#### Problem: Package installation failures
```
E: Unable to locate package python3-pyqt6.qtcore
E: Couldn't find any package by glob 'python3-pyqt6.qtcore'
```

**Solutions:**
1. **Automatic handling (v1.0.1+)**: The installation script now automatically detects 
   when specific PyQt6 packages are unavailable and uses fallback installation via pip.

2. Manual verification of available packages:
   ```bash
   apt-cache search python3-pyqt6
   apt-cache search qt6
   ```

3. Check system compatibility:
   ```bash
   lsb_release -a
   cat /etc/debian_version
   ```

4. Force pip installation:
   ```bash
   cd /home/pi/ASZCam
   ./venv/bin/pip install PyQt6
   ```
```
E: Unable to locate package python3-libcamera
```

**Solutions:**
1. Update package lists:
   ```bash
   sudo apt update
   sudo apt upgrade -y
   ```

2. Enable camera repository:
   ```bash
   echo "deb http://archive.raspberrypi.org/debian/ bullseye main" | sudo tee -a /etc/apt/sources.list
   sudo apt update
   ```

3. Install packages manually:
   ```bash
   sudo apt install -y python3-pip python3-venv
   sudo apt install -y libcamera-dev libcamera-apps
   ```

#### Problem: Python virtual environment creation fails
```
Error: Command '['/path/to/venv/bin/python3', '-Im', 'ensurepip', '--upgrade', '--default-pip']' returned non-zero exit status 1.
```

**Solutions:**
1. Install python3-venv:
   ```bash
   sudo apt install python3-venv python3-pip
   ```

2. Clear existing venv and recreate:
   ```bash
   rm -rf /home/pi/ASZCam/venv
   python3 -m venv /home/pi/ASZCam/venv
   ```

3. Use system pip if venv fails:
   ```bash
   pip3 install --user -r requirements.txt
   ```

#### Problem: Git clone fails
```
fatal: unable to access 'https://github.com/mynameisrober/ASZ-Cam-OS.git/': Could not resolve host
```

**Solutions:**
1. Check internet connection:
   ```bash
   ping -c 3 github.com
   ```

2. Configure DNS:
   ```bash
   echo "nameserver 8.8.8.8" | sudo tee -a /etc/resolv.conf
   ```

3. Use HTTPS instead of SSH:
   ```bash
   git clone https://github.com/mynameisrober/ASZ-Cam-OS.git
   ```

### Dependency Issues

#### Problem: PyQt6 installation fails on older systems
```
ERROR: Could not find a version that satisfies the requirement PyQt6>=6.5.0
```

**Solutions:**
1. Update pip:
   ```bash
   pip install --upgrade pip
   ```

2. Install system PyQt6 (the installation script now handles this automatically):
   ```bash
   sudo apt install python3-pyqt6
   ```
   Note: On some systems like Raspberry Pi OS Bookworm, specific PyQt6 subpackages 
   (`python3-pyqt6.qtcore`, `python3-pyqt6.qtgui`, etc.) may not be available.
   The installation script will automatically detect this and install PyQt6 via pip instead.

3. Use alternative installation:
   ```bash
   pip install PyQt6 --no-cache-dir
   ```

4. **New in v1.0.1**: Automatic fallback handling
   The installation script now automatically:
   - Checks package availability before attempting installation
   - Uses alternative package names when available (e.g., `qt6-base-dev` instead of `qtbase6-dev`)
   - Falls back to pip installation in virtual environment if system packages are unavailable
   - Continues installation even if optional PyQt6 system packages fail

#### Problem: Google API client installation fails
```
ERROR: Failed building wheel for grpcio
```

**Solutions:**
1. Install build dependencies:
   ```bash
   sudo apt install build-essential python3-dev libffi-dev
   ```

2. Increase swap space:
   ```bash
   sudo dphys-swapfile swapoff
   sudo sed -i 's/CONF_SWAPSIZE=100/CONF_SWAPSIZE=1024/' /etc/dphys-swapfile
   sudo dphys-swapfile setup
   sudo dphys-swapfile swapon
   ```

3. Install pre-compiled wheels:
   ```bash
   pip install --only-binary=all google-api-python-client
   ```

## Boot and Startup Problems

### System Won't Boot

#### Problem: Black screen on boot, no display output

**Diagnostic Steps:**
1. Check HDMI cable and connections
2. Try different HDMI port on display
3. Check power supply (should be 5V/3A for Pi 4)

**Solutions:**
1. Edit `/boot/config.txt` on SD card using another computer:
   ```
   hdmi_force_hotplug=1
   hdmi_drive=2
   hdmi_group=1
   hdmi_mode=16
   ```

2. Disable overscan:
   ```
   disable_overscan=1
   ```

3. Safe mode boot - add to `/boot/cmdline.txt`:
   ```
   systemd.unit=rescue.target
   ```

#### Problem: Boot process hangs at specific service

**Diagnostic:**
```bash
# Check boot time analysis
systemd-analyze blame
systemd-analyze critical-chain
```

**Solutions:**
1. Disable problematic service temporarily:
   ```bash
   sudo systemctl disable service-name
   sudo reboot
   ```

2. Check service logs:
   ```bash
   journalctl -u service-name --no-pager
   ```

3. Reset systemd services:
   ```bash
   sudo systemctl daemon-reload
   sudo systemctl reset-failed
   ```

### ASZ Cam OS Won't Start

#### Problem: Service fails to start
```bash
systemctl status asz-cam-os
● asz-cam-os.service - ASZ Cam OS
   Loaded: loaded (/etc/systemd/system/asz-cam-os.service; enabled; vendor preset: enabled)
   Active: failed (Result: exit-code) since...
```

**Diagnostic Steps:**
```bash
# Check detailed logs
journalctl -u asz-cam-os --no-pager -l

# Check if files exist
ls -la /home/pi/ASZCam/
ls -la /home/pi/ASZCam/venv/bin/python

# Test manual start
cd /home/pi/ASZCam
./venv/bin/python src/main.py
```

**Solutions:**
1. Fix file permissions:
   ```bash
   sudo chown -R pi:pi /home/pi/ASZCam
   chmod +x /home/pi/ASZCam/venv/bin/python
   ```

2. Reinstall Python dependencies:
   ```bash
   cd /home/pi/ASZCam
   ./venv/bin/pip install -r requirements.txt
   ```

3. Reset service configuration:
   ```bash
   sudo systemctl stop asz-cam-os
   sudo systemctl daemon-reload
   sudo systemctl start asz-cam-os
   ```

#### Problem: Python import errors
```
ModuleNotFoundError: No module named 'PyQt6'
```

**Solutions:**
1. Check virtual environment:
   ```bash
   /home/pi/ASZCam/venv/bin/python -c "import PyQt6; print('OK')"
   ```

2. Reinstall in virtual environment:
   ```bash
   cd /home/pi/ASZCam
   ./venv/bin/pip install PyQt6
   ```

3. Check PYTHONPATH:
   ```bash
   echo $PYTHONPATH
   export PYTHONPATH=/home/pi/ASZCam/src:$PYTHONPATH
   ```

### Auto-login Issues

#### Problem: System doesn't auto-login

**Check Configuration:**
```bash
# Check getty service
systemctl status getty@tty1.service

# Check auto-login configuration
cat /etc/systemd/system/getty@tty1.service.d/override.conf
```

**Solutions:**
1. Reconfigure auto-login:
   ```bash
   sudo raspi-config
   # System Options -> Boot / Auto Login -> Console Autologin
   ```

2. Manual configuration:
   ```bash
   sudo mkdir -p /etc/systemd/system/getty@tty1.service.d
   sudo tee /etc/systemd/system/getty@tty1.service.d/override.conf <<EOF
   [Service]
   ExecStart=
   ExecStart=-/sbin/agetty --autologin pi --noclear %I \$TERM
   EOF
   sudo systemctl daemon-reload
   ```

## Camera Issues

### Camera Not Detected

#### Problem: "No cameras available" error

**Diagnostic Steps:**
```bash
# Check if camera is detected by system
libcamera-hello --list-cameras

# Check camera interface in config
grep camera /boot/config.txt

# Check kernel modules
lsmod | grep bcm2835

# Check device nodes
ls -la /dev/video*
```

**Solutions:**
1. Enable camera interface:
   ```bash
   sudo raspi-config
   # Interface Options -> Camera -> Enable
   sudo reboot
   ```

2. Add to `/boot/config.txt`:
   ```
   camera_auto_detect=1
   start_x=1
   ```

3. Load camera modules manually:
   ```bash
   sudo modprobe bcm2835-v4l2
   echo 'bcm2835-v4l2' | sudo tee -a /etc/modules
   ```

4. Check camera cable connection and try different CSI port

#### Problem: Camera detected but preview fails

**Diagnostic:**
```bash
# Test basic camera function
libcamera-still -o test.jpg --timeout 2000

# Check permissions
groups pi | grep -q video && echo "User in video group" || echo "User not in video group"

# Test with different resolution
libcamera-hello --width 640 --height 480
```

**Solutions:**
1. Add user to video group:
   ```bash
   sudo usermod -a -G video pi
   logout  # Re-login required
   ```

2. Check camera permissions:
   ```bash
   sudo chmod 666 /dev/video0
   # Or permanently:
   echo 'SUBSYSTEM=="video4linux", GROUP="video", MODE="0664"' | sudo tee /etc/udev/rules.d/99-camera.rules
   ```

3. Increase GPU memory:
   ```bash
   # Add to /boot/config.txt
   gpu_mem=128
   sudo reboot
   ```

### Camera Performance Issues

#### Problem: Slow camera startup or preview lag

**Diagnostic:**
```bash
# Check system resources
htop
free -h

# Check GPU memory
vcgencmd get_mem gpu

# Check camera settings
v4l2-ctl --list-formats-ext
```

**Solutions:**
1. Optimize GPU memory split:
   ```bash
   # In /boot/config.txt
   gpu_mem=128  # For 4GB Pi
   gpu_mem=256  # For 8GB Pi
   ```

2. Reduce preview resolution:
   ```bash
   # In ASZ Cam OS settings, set preview to 720p instead of 1080p
   ```

3. Check CPU governor:
   ```bash
   cat /sys/devices/system/cpu/cpu*/cpufreq/scaling_governor
   # Should show "performance" or "ondemand"
   ```

4. Disable unnecessary services:
   ```bash
   sudo systemctl disable bluetooth
   sudo systemctl disable avahi-daemon
   ```

#### Problem: Poor image quality

**Check Settings:**
- Camera resolution settings
- JPEG quality settings  
- Lighting conditions
- Focus settings (if manual focus available)

**Solutions:**
1. Adjust camera settings in ASZ Cam OS:
   - Increase JPEG quality to 95%
   - Use highest supported resolution
   - Adjust white balance for lighting
   - Enable image stabilization if available

2. Check lens cleanliness and focus

3. Verify camera module version:
   ```bash
   libcamera-hello --info-text fps --list-cameras
   ```

## Display Problems

### No Display Output

#### Problem: Black screen, no UI visible

**Diagnostic Steps:**
```bash
# Check X server status
ps aux | grep Xorg

# Check display environment
echo $DISPLAY

# Test X11 forwarding over SSH
ssh -X pi@raspberrypi.local
xclock  # Should display a clock
```

**Solutions:**
1. Start X server manually:
   ```bash
   startx
   ```

2. Check X11 configuration:
   ```bash
   sudo cp install/xorg.conf /etc/X11/xorg.conf
   sudo systemctl restart display-manager
   ```

3. Reset display manager:
   ```bash
   sudo systemctl restart lightdm
   # or
   sudo systemctl restart gdm3
   ```

4. Check HDMI configuration in `/boot/config.txt`:
   ```
   hdmi_force_hotplug=1
   hdmi_group=1
   hdmi_mode=16
   disable_overscan=1
   ```

### UI Rendering Issues

#### Problem: Interface appears corrupted or garbled

**Solutions:**
1. Check graphics driver:
   ```bash
   glxinfo | grep renderer
   ```

2. Reset graphics driver in `/boot/config.txt`:
   ```
   dtoverlay=vc4-kms-v3d
   ```

3. Adjust GPU memory:
   ```bash
   # In /boot/config.txt
   gpu_mem=128
   ```

4. Test with different display resolution:
   ```bash
   # In /boot/config.txt
   hdmi_mode=16  # 1080p
   # or
   hdmi_mode=4   # 720p
   ```

#### Problem: Touch input not working (touchscreen)

**Diagnostic:**
```bash
# Check input devices
cat /proc/bus/input/devices | grep -A 5 Touch

# Test touch input
evtest  # Select touch device and test
```

**Solutions:**
1. Install touch drivers:
   ```bash
   sudo apt install xserver-xorg-input-evdev
   ```

2. Configure touch calibration:
   ```bash
   xinput --list
   xinput --set-prop "Device Name" "Coordinate Transformation Matrix" 1 0 0 0 1 0 0 0 1
   ```

3. Add touch configuration to X11:
   ```bash
   sudo tee /etc/X11/xorg.conf.d/99-calibration.conf <<EOF
   Section "InputClass"
       Identifier      "calibration"
       MatchProduct    "ADS7846 Touchscreen"
       Option  "Calibration"   "160 3723 3896 181"
   EndSection
   EOF
   ```

### Font and Display Scaling Issues

#### Problem: Text appears too small or too large

**Solutions:**
1. Adjust display scaling:
   ```bash
   # Set display scale in environment
   export QT_SCALE_FACTOR=1.2
   # Add to ~/.bashrc for persistence
   ```

2. Install better fonts:
   ```bash
   sudo ./scripts/download_fonts.sh
   ```

3. Configure font DPI:
   ```bash
   # In X11 startup scripts
   xrandr --dpi 96
   ```

## Network and Sync Issues

### WiFi Connection Problems

#### Problem: Cannot connect to WiFi

**Diagnostic:**
```bash
# Check WiFi interface
ip link show
iwconfig

# Scan for networks
sudo iwlist wlan0 scan | grep ESSID

# Check current connection
iwgetid
```

**Solutions:**
1. Configure WiFi manually:
   ```bash
   sudo raspi-config
   # System Options -> Wireless LAN
   ```

2. Edit wpa_supplicant:
   ```bash
   sudo nano /etc/wpa_supplicant/wpa_supplicant.conf
   
   network={
       ssid="YourNetworkName"
       psk="YourPassword"
   }
   
   sudo systemctl restart networking
   ```

3. Use NetworkManager:
   ```bash
   sudo apt install network-manager
   sudo systemctl enable NetworkManager
   nmcli dev wifi connect "NetworkName" password "Password"
   ```

4. Check country code:
   ```bash
   sudo raspi-config
   # Localisation Options -> WLAN Country
   ```

#### Problem: WiFi connection drops frequently

**Solutions:**
1. Disable power management:
   ```bash
   sudo iwconfig wlan0 power off
   # Make permanent:
   echo 'iwconfig wlan0 power off' | sudo tee -a /etc/rc.local
   ```

2. Update WiFi driver:
   ```bash
   sudo apt update
   sudo apt upgrade -y
   sudo reboot
   ```

3. Check signal strength:
   ```bash
   iwconfig wlan0 | grep Signal
   ```

4. Use 5GHz instead of 2.4GHz if available

### Google Photos Sync Issues

#### Problem: Authentication fails

**Diagnostic:**
```bash
# Check credentials file
ls -la /home/pi/ASZCam/google_credentials.json

# Check log for auth errors
journalctl -u asz-cam-os | grep -i auth
```

**Solutions:**
1. Re-download credentials from Google Cloud Console
2. Ensure Photos Library API is enabled
3. Check OAuth consent screen configuration
4. Try authentication in headless mode:
   ```bash
   cd /home/pi/ASZCam
   ./venv/bin/python -c "from src.sync.google_photos import google_photos_api; google_photos_api.authenticate()"
   ```

#### Problem: Upload errors

**Common Error Messages and Solutions:**

**"Invalid credentials":**
```bash
# Delete old token and re-authenticate
rm /home/pi/ASZCam/google_photos_token.json
# Restart service to trigger re-auth
sudo systemctl restart asz-cam-os
```

**"Quota exceeded":**
- Check Google Photos storage quota
- Switch to "High Quality" uploads (free unlimited)
- Clean up existing Google Photos storage

**"Network timeout":**
```bash
# Check internet connectivity
ping -c 3 www.google.com

# Test upload manually
curl -I https://photoslibrary.googleapis.com
```

**"Permission denied":**
- Verify OAuth scopes in Google Cloud Console
- Ensure Photos Library API is enabled
- Check OAuth consent screen approval status

#### Problem: Sync appears stuck

**Diagnostic:**
```bash
# Check sync status
journalctl -u asz-cam-os | grep -i sync | tail -10

# Check upload queue
# Look in ASZ Cam OS UI for sync statistics
```

**Solutions:**
1. Restart sync service:
   ```bash
   sudo systemctl restart asz-cam-os
   ```

2. Clear sync queue:
   ```bash
   # Through ASZ Cam OS settings: Sync -> Clear Queue
   ```

3. Reset sync state:
   ```bash
   rm /home/pi/ASZCam/sync_records.json
   sudo systemctl restart asz-cam-os
   ```

## Performance Problems

### Slow System Performance

#### Problem: General system slowdown

**Diagnostic:**
```bash
# Check CPU usage
htop

# Check memory usage
free -h

# Check disk I/O
iotop  # May need: sudo apt install iotop

# Check temperature
vcgencmd measure_temp

# Check for swap usage
swapon -s
```

**Solutions:**
1. Check for overheating:
   ```bash
   vcgencmd measure_temp
   # Should be under 80°C
   ```
   - Add heatsinks or improve ventilation
   - Reduce overclocking if enabled

2. Optimize SD card performance:
   ```bash
   # Check SD card speed
   sudo hdparm -t /dev/mmcblk0
   
   # Use faster SD card (Class 10, A2 rated)
   # Consider USB 3.0 SSD for boot drive
   ```

3. Adjust swap configuration:
   ```bash
   # Reduce swappiness
   echo 'vm.swappiness=10' | sudo tee -a /etc/sysctl.conf
   
   # Disable swap if enough RAM
   sudo dphys-swapfile swapoff
   sudo systemctl disable dphys-swapfile
   ```

4. Clean up unnecessary files:
   ```bash
   sudo apt autoremove -y
   sudo apt autoclean
   
   # Clean logs
   sudo journalctl --vacuum-time=7d
   ```

#### Problem: High memory usage

**Diagnostic:**
```bash
# Check memory-hungry processes
ps aux --sort=-rss | head -10

# Check for memory leaks
valgrind --tool=memcheck /home/pi/ASZCam/venv/bin/python /home/pi/ASZCam/src/main.py
```

**Solutions:**
1. Reduce preview resolution in settings
2. Limit number of cached photos in gallery
3. Restart ASZ Cam OS service periodically:
   ```bash
   # Add to crontab for daily restart
   0 2 * * * /usr/bin/systemctl restart asz-cam-os
   ```

4. Optimize Python memory usage:
   ```bash
   # Set environment variables
   export PYTHONOPTIMIZE=1
   export MALLOC_ARENA_MAX=2
   ```

### Network Performance Issues

#### Problem: Slow photo uploads

**Diagnostic:**
```bash
# Test network speed
speedtest-cli  # Install: sudo apt install speedtest-cli

# Test specific connection to Google
curl -w "%{time_total}\n" -o /dev/null -s "https://www.googleapis.com"

# Check network interface statistics
cat /proc/net/dev
```

**Solutions:**
1. Use wired connection instead of WiFi when possible
2. Optimize upload settings:
   - Reduce image quality for uploads
   - Enable background sync during off-hours
   - Limit concurrent uploads

3. Configure QoS if router supports it
4. Check for network congestion during peak hours

## System Recovery

### Boot Recovery

#### Problem: System won't boot at all

**Recovery Steps:**

1. **SD Card Recovery:**
   - Remove SD card and check on another computer
   - Check file system integrity:
     ```bash
     fsck /dev/sdX1  # Replace X with actual device
     ```
   - Mount and backup important files

2. **Boot from Recovery Image:**
   - Flash new Raspberry Pi OS to separate SD card
   - Mount original SD card as secondary storage
   - Copy important files and configurations

3. **Use Raspberry Pi Recovery Mode:**
   - Hold Shift during boot for recovery options
   - Or create recovery partition on SD card

#### Problem: Corrupted file system

**Recovery:**
```bash
# Boot from external media, then check/repair
sudo fsck -y /dev/mmcblk0p2

# Mount and backup data
sudo mount /dev/mmcblk0p2 /mnt
cp -r /mnt/home/pi/ASZCam /backup/

# Reinstall system if necessary
```

### Configuration Recovery

#### Problem: System boots but ASZ Cam OS won't work

**Recovery Steps:**

1. **Boot to Command Line:**
   ```bash
   # Add to /boot/cmdline.txt temporarily
   systemd.unit=multi-user.target
   ```

2. **Reset ASZ Cam OS:**
   ```bash
   # Stop service
   sudo systemctl stop asz-cam-os
   
   # Backup current config
   cp -r ~/.config/aszcam ~/.config/aszcam.backup
   
   # Remove corrupted config
   rm -rf ~/.config/aszcam
   
   # Reinstall ASZ Cam OS
   cd ASZ-Cam-OS
   sudo ./scripts/install.sh
   ```

3. **Restore from Backup:**
   ```bash
   # If you have a backup
   cp -r /backup/.config/aszcam ~/.config/
   sudo chown -R pi:pi ~/.config/aszcam
   ```

### Data Recovery

#### Problem: Lost photos or settings

**Photo Recovery:**
```bash
# Check default photos directory
ls -la /home/pi/Pictures/ASZCam/

# Search for photos on entire system
find / -name "*.jpg" -o -name "*.jpeg" -o -name "*.png" 2>/dev/null

# Check for deleted files (if deletion was recent)
sudo apt install testdisk
sudo photorec  # Follow prompts to recover deleted photos
```

**Settings Recovery:**
```bash
# Look for backup settings
find /home -name "settings.yaml*" 2>/dev/null
find /home -name "*.backup" 2>/dev/null

# Check if settings are in Git history
cd ASZ-Cam-OS
git log --oneline | head -10
```

## Advanced Diagnostics

### System Monitoring

#### Continuous Monitoring Setup

Create monitoring script:
```bash
#!/bin/bash
# continuous_monitor.sh

LOG_FILE="/tmp/aszcam_monitor.log"

echo "Starting continuous monitoring - $(date)" >> $LOG_FILE

while true; do
    echo "=== $(date) ===" >> $LOG_FILE
    
    # System resources
    echo "CPU: $(cat /proc/loadavg)" >> $LOG_FILE
    echo "Memory: $(free -h | grep Mem:)" >> $LOG_FILE
    echo "Temperature: $(vcgencmd measure_temp)" >> $LOG_FILE
    echo "Disk: $(df -h / | tail -1)" >> $LOG_FILE
    
    # Service status
    systemctl is-active asz-cam-os >> $LOG_FILE
    
    # Network status
    ping -c 1 8.8.8.8 >/dev/null 2>&1 && echo "Network: OK" >> $LOG_FILE || echo "Network: FAIL" >> $LOG_FILE
    
    echo "" >> $LOG_FILE
    sleep 300  # 5 minutes
done
```

#### Log Analysis

```bash
# Analyze system logs for patterns
journalctl --since "1 hour ago" | grep -i error
journalctl --since "1 hour ago" | grep -i warning
journalctl --since "1 hour ago" | grep -i failed

# Check specific service logs
journalctl -u asz-cam-os --since "1 hour ago" --no-pager

# Monitor logs in real-time
journalctl -f -u asz-cam-os

# Export logs for analysis
journalctl -u asz-cam-os --since "24 hours ago" --no-pager > aszcam_logs.txt
```

### Performance Profiling

#### Python Performance Analysis

```bash
# Profile ASZ Cam OS performance
cd /home/pi/ASZCam
./venv/bin/python -m cProfile -o profile_output.pstats src/main.py

# Analyze profile results
./venv/bin/python -c "
import pstats
p = pstats.Stats('profile_output.pstats')
p.sort_stats('cumulative').print_stats(20)
"
```

#### Memory Analysis

```bash
# Monitor memory usage over time
while true; do
    date >> memory_usage.log
    ps aux --no-headers --sort=-rss | head -10 >> memory_usage.log
    echo "---" >> memory_usage.log
    sleep 60
done
```

### Network Diagnostics

#### Detailed Network Analysis

```bash
# Network interface statistics
cat /proc/net/dev

# WiFi signal analysis
iwconfig wlan0

# Network route analysis
ip route show

# DNS resolution test
nslookup www.google.com
nslookup photoslibrary.googleapis.com

# Detailed connectivity test
traceroute www.google.com
mtr --report --report-cycles 10 www.google.com
```

### Hardware Diagnostics

#### Camera Hardware Testing

```bash
# Comprehensive camera test
libcamera-hello --info-text fps --width 1920 --height 1080 --timeout 10000

# Test different camera modes
for mode in 1 2 3 4; do
    echo "Testing mode $mode..."
    libcamera-hello --mode $mode --timeout 5000 --nopreview
done

# Check camera sensor information
v4l2-ctl --list-formats-ext --device=/dev/video0
```

#### GPIO and Hardware Testing

```bash
# Check GPIO status (if using GPIO features)
gpio readall

# Check I2C devices
i2cdetect -y 1

# Check SPI devices
ls -la /dev/spi*

# Temperature sensors
for thermal in /sys/class/thermal/thermal_zone*; do
    echo "$thermal: $(cat $thermal/temp | awk '{print $1/1000"°C"}')"
done
```

---

## Getting Help

If this troubleshooting guide doesn't resolve your issue:

1. **Search Issues**: Check [GitHub Issues](https://github.com/mynameisrober/ASZ-Cam-OS/issues) for similar problems
2. **Create Issue**: Open a new issue with:
   - Detailed problem description
   - Steps to reproduce
   - System information (`uname -a`, Pi model, OS version)
   - Relevant log outputs
   - Screenshots if applicable

3. **Community Support**: 
   - Raspberry Pi Forums
   - Reddit r/RASPBERRY_PI_PROJECTS
   - ASZ Cam OS Discussions

4. **Professional Support**: Consider professional support for production deployments

Remember to always backup your configuration and photos before attempting major troubleshooting steps!