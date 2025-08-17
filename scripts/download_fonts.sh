#!/bin/bash
# ASZ Cam OS - Font Download Script
# Downloads and installs the SFCamera fonts and other UI fonts
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
FONTS_DIR="${ASZ_INSTALL_DIR}/assets/fonts"
TEMP_DIR="/tmp/aszcam-fonts"

# Helper functions
log_info() {
    echo -e "${BLUE}[Fonts]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[Fonts]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[Fonts]${NC} $1"
}

log_error() {
    echo -e "${RED}[Fonts]${NC} $1"
}

create_directories() {
    log_info "Creating font directories..."
    
    mkdir -p "${FONTS_DIR}"
    mkdir -p "${TEMP_DIR}"
    mkdir -p "/usr/local/share/fonts/aszcam"
    
    log_success "Font directories created"
}

download_sf_camera_fonts() {
    log_info "Downloading SF Camera fonts..."
    
    # Since SF Camera fonts may not be freely available, we'll use similar alternatives
    # and create a placeholder system
    
    # Create font configuration for SF Camera style
    cat > "${FONTS_DIR}/font-config.json" << EOF
{
    "fonts": {
        "primary": {
            "name": "SF Camera",
            "fallback": ["SF Pro Display", "Roboto", "DejaVu Sans", "Liberation Sans"],
            "weights": ["Light", "Regular", "Medium", "Bold"],
            "sizes": {
                "small": 12,
                "medium": 14,
                "large": 18,
                "xlarge": 24,
                "title": 32
            }
        },
        "monospace": {
            "name": "SF Mono",
            "fallback": ["Roboto Mono", "DejaVu Sans Mono", "Liberation Mono"],
            "weights": ["Regular", "Bold"],
            "sizes": {
                "small": 10,
                "medium": 12,
                "large": 14
            }
        }
    }
}
EOF
    
    log_success "Font configuration created"
}

download_system_fonts() {
    log_info "Downloading system fonts..."
    
    cd "${TEMP_DIR}"
    
    # Download Google Fonts alternatives
    FONTS_TO_DOWNLOAD=(
        "https://fonts.google.com/download?family=Roboto"
        "https://fonts.google.com/download?family=Roboto+Mono"
        "https://fonts.google.com/download?family=Inter"
        "https://fonts.google.com/download?family=Source+Sans+Pro"
    )
    
    # Note: Google Fonts download links require special handling
    # For now, we'll install fonts available in repositories
    
    log_info "Installing available system fonts..."
    apt-get update
    apt-get install -y \
        fonts-roboto \
        fonts-roboto-fontface \
        fonts-inter \
        fonts-source-code-pro \
        fonts-dejavu-core \
        fonts-dejavu-extra \
        fonts-liberation \
        fonts-noto-core \
        fonts-opensans
    
    log_success "System fonts installed"
}

create_custom_fonts() {
    log_info "Creating custom font files..."
    
    # Create CSS font definitions
    cat > "${FONTS_DIR}/aszcam-fonts.css" << EOF
/* ASZ Cam OS Font Definitions */

@font-face {
    font-family: 'ASZ Camera';
    src: local('SF Pro Display'), local('Roboto'), local('DejaVu Sans');
    font-weight: 300;
    font-style: normal;
}

@font-face {
    font-family: 'ASZ Camera';
    src: local('SF Pro Display'), local('Roboto'), local('DejaVu Sans');
    font-weight: 400;
    font-style: normal;
}

@font-face {
    font-family: 'ASZ Camera';
    src: local('SF Pro Display'), local('Roboto'), local('DejaVu Sans');
    font-weight: 500;
    font-style: normal;
}

@font-face {
    font-family: 'ASZ Camera';
    src: local('SF Pro Display'), local('Roboto'), local('DejaVu Sans');
    font-weight: 700;
    font-style: normal;
}

@font-face {
    font-family: 'ASZ Camera Mono';
    src: local('SF Mono'), local('Roboto Mono'), local('DejaVu Sans Mono');
    font-weight: 400;
    font-style: normal;
}

/* Font size classes */
.font-xs { font-size: 10px; }
.font-sm { font-size: 12px; }
.font-md { font-size: 14px; }
.font-lg { font-size: 18px; }
.font-xl { font-size: 24px; }
.font-xxl { font-size: 32px; }

/* Font weight classes */
.font-light { font-weight: 300; }
.font-normal { font-weight: 400; }
.font-medium { font-weight: 500; }
.font-bold { font-weight: 700; }
EOF
    
    log_success "Custom font definitions created"
}

create_qt_font_config() {
    log_info "Creating Qt font configuration..."
    
    # Create Qt font configuration
    cat > "${FONTS_DIR}/qt-fonts.conf" << EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE fontconfig SYSTEM "fonts.dtd">
<fontconfig>
  <!-- ASZ Cam OS Font Configuration -->
  
  <!-- Default font settings -->
  <alias>
    <family>ASZ Camera</family>
    <prefer>
      <family>SF Pro Display</family>
      <family>Roboto</family>
      <family>Inter</family>
      <family>DejaVu Sans</family>
      <family>Liberation Sans</family>
    </prefer>
  </alias>
  
  <alias>
    <family>ASZ Camera Mono</family>
    <prefer>
      <family>SF Mono</family>
      <family>Roboto Mono</family>
      <family>Source Code Pro</family>
      <family>DejaVu Sans Mono</family>
    </prefer>
  </alias>
  
  <!-- Application default fonts -->
  <alias>
    <family>sans-serif</family>
    <prefer>
      <family>Roboto</family>
      <family>Inter</family>
      <family>DejaVu Sans</family>
    </prefer>
  </alias>
  
  <alias>
    <family>monospace</family>
    <prefer>
      <family>Roboto Mono</family>
      <family>Source Code Pro</family>
      <family>DejaVu Sans Mono</family>
    </prefer>
  </alias>
  
  <!-- Font rendering settings -->
  <match target="font">
    <edit name="antialias" mode="assign">
      <bool>true</bool>
    </edit>
    <edit name="hinting" mode="assign">
      <bool>true</bool>
    </edit>
    <edit name="hintstyle" mode="assign">
      <const>hintslight</const>
    </edit>
    <edit name="rgba" mode="assign">
      <const>rgb</const>
    </edit>
    <edit name="lcdfilter" mode="assign">
      <const>lcddefault</const>
    </edit>
  </match>
</fontconfig>
EOF
    
    log_success "Qt font configuration created"
}

create_python_font_helper() {
    log_info "Creating Python font helper module..."
    
    # Create Python font utility
    cat > "${ASZ_INSTALL_DIR}/src/ui/font_manager.py" << EOF
"""
ASZ Cam OS - Font Manager
Manages fonts and typography for the application UI.
"""

import os
import json
from pathlib import Path
from typing import Dict, List, Optional
from PyQt6.QtGui import QFont, QFontDatabase
from PyQt6.QtCore import QStandardPaths

class FontManager:
    """Manages application fonts and typography."""
    
    def __init__(self):
        self.fonts_dir = Path(__file__).parent.parent.parent / "assets" / "fonts"
        self.font_config = self._load_font_config()
        self.loaded_fonts = {}
        self._load_system_fonts()
    
    def _load_font_config(self) -> Dict:
        """Load font configuration from JSON file."""
        config_file = self.fonts_dir / "font-config.json"
        if config_file.exists():
            with open(config_file, 'r') as f:
                return json.load(f)
        return self._get_default_config()
    
    def _get_default_config(self) -> Dict:
        """Get default font configuration."""
        return {
            "fonts": {
                "primary": {
                    "name": "ASZ Camera",
                    "fallback": ["Roboto", "Inter", "DejaVu Sans", "sans-serif"],
                    "weights": ["Light", "Regular", "Medium", "Bold"],
                    "sizes": {
                        "small": 12,
                        "medium": 14, 
                        "large": 18,
                        "xlarge": 24,
                        "title": 32
                    }
                },
                "monospace": {
                    "name": "ASZ Camera Mono",
                    "fallback": ["Roboto Mono", "Source Code Pro", "monospace"],
                    "weights": ["Regular", "Bold"],
                    "sizes": {
                        "small": 10,
                        "medium": 12,
                        "large": 14
                    }
                }
            }
        }
    
    def _load_system_fonts(self):
        """Load and register system fonts."""
        # Add custom fonts from fonts directory
        if self.fonts_dir.exists():
            for font_file in self.fonts_dir.glob("*.ttf"):
                font_id = QFontDatabase.addApplicationFont(str(font_file))
                if font_id >= 0:
                    font_families = QFontDatabase.applicationFontFamilies(font_id)
                    for family in font_families:
                        self.loaded_fonts[family] = str(font_file)
    
    def get_primary_font(self, size: int = 14, weight: str = "Regular") -> QFont:
        """Get primary application font."""
        return self._create_font("primary", size, weight)
    
    def get_monospace_font(self, size: int = 12, weight: str = "Regular") -> QFont:
        """Get monospace font for code/data display."""
        return self._create_font("monospace", size, weight)
    
    def _create_font(self, font_type: str, size: int, weight: str) -> QFont:
        """Create a QFont object with specified parameters."""
        config = self.font_config["fonts"][font_type]
        
        # Try to find the best available font
        font_family = self._find_best_font(config)
        font = QFont(font_family, size)
        
        # Set weight
        qt_weight = self._get_qt_weight(weight)
        font.setWeight(qt_weight)
        
        return font
    
    def _find_best_font(self, config: Dict) -> str:
        """Find the best available font from the configuration."""
        # Check primary font name
        if self._is_font_available(config["name"]):
            return config["name"]
        
        # Check fallback fonts
        for fallback in config["fallback"]:
            if self._is_font_available(fallback):
                return fallback
        
        # Default to system default
        return "sans-serif"
    
    def _is_font_available(self, font_name: str) -> bool:
        """Check if a font is available on the system."""
        font = QFont(font_name)
        font_info = QFontDatabase().font(font_name, "Regular", 12)
        return font_info.family() == font_name or font_name in self.loaded_fonts
    
    def _get_qt_weight(self, weight: str) -> int:
        """Convert weight string to Qt weight constant."""
        weight_map = {
            "Light": QFont.Weight.Light,
            "Regular": QFont.Weight.Normal,
            "Medium": QFont.Weight.Medium,
            "Bold": QFont.Weight.Bold
        }
        return weight_map.get(weight, QFont.Weight.Normal)
    
    def get_available_fonts(self) -> List[str]:
        """Get list of all available fonts."""
        system_fonts = QFontDatabase().families()
        return list(system_fonts) + list(self.loaded_fonts.keys())
    
    def apply_global_font(self, app):
        """Apply global font settings to the application."""
        primary_font = self.get_primary_font(size=14)
        app.setFont(primary_font)
EOF
    
    log_success "Python font helper created"
}

install_fontconfig() {
    log_info "Installing and configuring fontconfig..."
    
    # Install fontconfig if not present
    apt-get install -y fontconfig
    
    # Copy font configuration
    cp "${FONTS_DIR}/qt-fonts.conf" "/etc/fonts/conf.d/99-aszcam-fonts.conf"
    
    # Update font cache
    fc-cache -fv
    
    log_success "Fontconfig installed and configured"
}

set_permissions() {
    log_info "Setting font permissions..."
    
    # Set proper ownership
    chown -R "${ASZ_USER}:${ASZ_USER}" "${FONTS_DIR}"
    
    # Set permissions for system fonts
    chmod 644 /etc/fonts/conf.d/99-aszcam-fonts.conf
    
    log_success "Font permissions set"
}

cleanup_temp_files() {
    log_info "Cleaning up temporary files..."
    
    rm -rf "${TEMP_DIR}"
    
    log_success "Temporary files cleaned up"
}

show_font_summary() {
    echo ""
    echo "==============================================="
    log_success "Font Installation Complete!"
    echo "==============================================="
    echo ""
    echo "Installed:"
    echo "- System fonts (Roboto, Inter, DejaVu, etc.)"
    echo "- Custom font configuration"
    echo "- Python font manager utility"
    echo "- Fontconfig integration"
    echo ""
    echo "Font assets location: ${FONTS_DIR}"
    echo "System font config: /etc/fonts/conf.d/99-aszcam-fonts.conf"
    echo ""
    echo "Available fonts can be tested with:"
    echo "fc-list | grep -E '(Roboto|Inter|DejaVu)'"
    echo ""
}

# Main function
main() {
    log_info "Starting font installation..."
    
    create_directories
    download_sf_camera_fonts
    download_system_fonts
    create_custom_fonts
    create_qt_font_config
    create_python_font_helper
    install_fontconfig
    set_permissions
    cleanup_temp_files
    
    show_font_summary
}

# Run main function if script is executed directly
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi