#!/bin/bash
# ASZ Cam OS - Complete Installation Script
# Installs and configures the ASZ Cam OS on Raspberry Pi

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
INSTALL_DIR="/opt/aszcam"
SERVICE_NAME="aszcam"
USER="pi"
PYTHON_ENV="/opt/aszcam/venv"

echo "=============================================="
echo "    ASZ Cam OS Installation Script"
echo "    Custom Camera OS for Raspberry Pi"
echo "=============================================="
echo ""

echo -e "${BLUE}[INFO]${NC} Starting ASZ Cam OS installation..."

# Update system
echo -e "${BLUE}[INFO]${NC} Updating system packages..."
sudo apt update -y

# Install dependencies
echo -e "${BLUE}[INFO]${NC} Installing system dependencies..."
sudo apt install -y python3 python3-pip python3-venv python3-dev git libcamera-apps python3-libcamera python3-picamera2

# Create installation directory
echo -e "${BLUE}[INFO]${NC} Creating installation directory..."
sudo mkdir -p $INSTALL_DIR
sudo chown $USER:$USER $INSTALL_DIR

# Copy files
echo -e "${BLUE}[INFO]${NC} Installing ASZ Cam OS application..."
cp -r . $INSTALL_DIR/
cd $INSTALL_DIR

# Setup Python environment
python3 -m venv $PYTHON_ENV
source $PYTHON_ENV/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

# Make executable
chmod +x src/main.py

# Create service
echo -e "${BLUE}[INFO]${NC} Setting up systemd service..."
sudo tee /etc/systemd/system/${SERVICE_NAME}.service > /dev/null << EOL
[Unit]
Description=ASZ Cam OS - Custom Camera Operating System
After=graphical-session.target

[Service]
Type=simple
User=$USER
WorkingDirectory=$INSTALL_DIR
Environment=DISPLAY=:0
ExecStart=$PYTHON_ENV/bin/python src/main.py
Restart=always
RestartSec=10

[Install]
WantedBy=graphical-session.target
EOL

sudo systemctl daemon-reload
sudo systemctl enable $SERVICE_NAME

echo ""
echo -e "${GREEN}[SUCCESS]${NC} ASZ Cam OS installed successfully!"
echo "Reboot the system to start: sudo reboot"
