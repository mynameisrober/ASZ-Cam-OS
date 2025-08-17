"""
ASZ Cam OS - Centralized Configuration System
Handles all system settings and configurations for the camera OS.
"""

import os
import yaml
import json
from pathlib import Path
from typing import Dict, Any, Optional
from dataclasses import dataclass, asdict


@dataclass
class CameraConfig:
    """Camera-specific configuration settings."""
    default_resolution: tuple = (1920, 1080)
    default_format: str = "JPEG"
    quality: int = 95
    auto_focus: bool = True
    auto_exposure: bool = True
    preview_enabled: bool = True
    capture_timeout: int = 5


@dataclass
class UIConfig:
    """User interface configuration settings."""
    theme: str = "aszcam_theme"
    font_family: str = "SFCamera"
    font_size: int = 12
    fullscreen: bool = True
    auto_hide_cursor: bool = True
    cursor_timeout: int = 3000  # ms
    animation_duration: int = 300  # ms


@dataclass
class SyncConfig:
    """Google Photos sync configuration."""
    enabled: bool = True
    auto_sync: bool = True
    sync_interval: int = 300  # seconds
    max_retry_attempts: int = 3
    retry_delay: int = 60  # seconds
    album_name: str = "ASZ Cam Photos"
    credentials_file: str = "google_credentials.json"


@dataclass
class SystemConfig:
    """System-level configuration settings."""
    auto_start: bool = True
    log_level: str = "INFO"
    log_file: str = "/var/log/aszcam.log"
    data_directory: str = "/home/pi/ASZCam"
    photos_directory: str = "/home/pi/ASZCam/Photos"
    temp_directory: str = "/tmp/aszcam"
    max_photos_storage: int = 1000  # Maximum photos to keep locally


class Settings:
    """Main settings manager for ASZ Cam OS."""
    
    def __init__(self, config_file: Optional[str] = None):
        self.config_file = config_file or self._get_default_config_path()
        self.camera = CameraConfig()
        self.ui = UIConfig()
        self.sync = SyncConfig()
        self.system = SystemConfig()
        self._ensure_directories()
        self.load_config()
    
    def _get_default_config_path(self) -> str:
        """Get the default configuration file path."""
        home = Path.home()
        config_dir = home / ".config" / "aszcam"
        config_dir.mkdir(parents=True, exist_ok=True)
        return str(config_dir / "settings.yaml")
    
    def _ensure_directories(self):
        """Ensure all required directories exist."""
        # Use development-friendly paths if not on Raspberry Pi
        if not self._is_raspberry_pi():
            home = Path.home()
            self.system.data_directory = str(home / "ASZCam")
            self.system.photos_directory = str(home / "ASZCam" / "Photos")
            self.system.log_file = str(home / "ASZCam" / "aszcam.log")
        
        directories = [
            self.system.data_directory,
            self.system.photos_directory,
            self.system.temp_directory,
        ]
        
        for directory in directories:
            Path(directory).mkdir(parents=True, exist_ok=True)
    
    def _is_raspberry_pi(self) -> bool:
        """Check if running on Raspberry Pi."""
        try:
            with open('/proc/cpuinfo', 'r') as f:
                cpuinfo = f.read()
                return 'Raspberry Pi' in cpuinfo or 'BCM' in cpuinfo
        except:
            return False
    
    def load_config(self):
        """Load configuration from file."""
        if not os.path.exists(self.config_file):
            self.save_config()  # Create default config
            return
        
        try:
            with open(self.config_file, 'r') as f:
                data = yaml.safe_load(f) or {}
            
            # Update configurations with loaded data
            if 'camera' in data:
                self._update_dataclass(self.camera, data['camera'])
            if 'ui' in data:
                self._update_dataclass(self.ui, data['ui'])
            if 'sync' in data:
                self._update_dataclass(self.sync, data['sync'])
            if 'system' in data:
                self._update_dataclass(self.system, data['system'])
                
        except Exception as e:
            print(f"Error loading config: {e}")
            print("Using default configuration")
    
    def save_config(self):
        """Save current configuration to file."""
        config_data = {
            'camera': asdict(self.camera),
            'ui': asdict(self.ui),
            'sync': asdict(self.sync),
            'system': asdict(self.system)
        }
        
        try:
            with open(self.config_file, 'w') as f:
                yaml.dump(config_data, f, default_flow_style=False, indent=2)
        except Exception as e:
            print(f"Error saving config: {e}")
    
    def _update_dataclass(self, obj, data: Dict[str, Any]):
        """Update dataclass fields with dictionary data."""
        for key, value in data.items():
            if hasattr(obj, key):
                setattr(obj, key, value)
    
    def get_assets_path(self) -> Path:
        """Get the path to assets directory."""
        # Assuming assets are in the same directory as the source code
        return Path(__file__).parent.parent.parent / "assets"
    
    def get_fonts_path(self) -> Path:
        """Get the path to fonts directory."""
        return self.get_assets_path() / "fonts"
    
    def get_themes_path(self) -> Path:
        """Get the path to themes directory."""
        return self.get_assets_path() / "themes"


# Global settings instance
settings = Settings()