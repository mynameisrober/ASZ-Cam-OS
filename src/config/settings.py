"""
ASZ Cam OS - Enhanced Configuration System
Comprehensive configuration management for all system aspects including advanced camera controls,
network settings, UI customization, and performance tuning.

Author: ASZ Development Team
Version: 1.0.0
"""

import os
import yaml
import json
import socket
import subprocess
from pathlib import Path
from typing import Dict, Any, Optional, List, Tuple, Union
from dataclasses import dataclass, asdict, field
from enum import Enum


class LogLevel(Enum):
    """Available log levels."""
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class Theme(Enum):
    """Available UI themes."""
    LIGHT = "light"
    DARK = "dark"
    AUTO = "auto"


class ExposureMode(Enum):
    """Camera exposure modes."""
    AUTO = "auto"
    MANUAL = "manual"
    APERTURE_PRIORITY = "aperture_priority"
    SHUTTER_PRIORITY = "shutter_priority"


class WhiteBalanceMode(Enum):
    """White balance modes."""
    AUTO = "auto"
    DAYLIGHT = "daylight"
    CLOUDY = "cloudy"
    TUNGSTEN = "tungsten"
    FLUORESCENT = "fluorescent"
    FLASH = "flash"
    MANUAL = "manual"


class FocusMode(Enum):
    """Camera focus modes."""
    AUTO = "auto"
    MANUAL = "manual"
    CONTINUOUS = "continuous"
    MACRO = "macro"


@dataclass
class CameraConfig:
    """Advanced camera configuration settings."""
    # Basic settings
    default_resolution: Tuple[int, int] = (1920, 1080)
    default_format: str = "JPEG"
    quality: int = 95
    preview_enabled: bool = True
    capture_timeout: int = 5
    
    # Advanced exposure settings
    exposure_mode: str = ExposureMode.AUTO.value
    iso: int = 0  # 0 = auto, 100-3200 manual
    shutter_speed: float = 0.0  # 0 = auto, seconds for manual
    exposure_compensation: float = 0.0  # -2.0 to +2.0 EV
    
    # Focus settings
    focus_mode: str = FocusMode.AUTO.value
    focus_position: float = 0.0  # 0.0-1.0 for manual focus
    
    # White balance
    white_balance_mode: str = WhiteBalanceMode.AUTO.value
    white_balance_temperature: int = 5500  # Kelvin for manual WB
    
    # Image processing
    brightness: float = 0.0  # -1.0 to +1.0
    contrast: float = 0.0  # -1.0 to +1.0
    saturation: float = 0.0  # -1.0 to +1.0
    sharpness: float = 0.0  # -1.0 to +1.0
    
    # Special modes
    hdr_enabled: bool = False
    noise_reduction: bool = True
    image_stabilization: bool = True
    
    # Burst and timelapse settings
    burst_count: int = 3
    burst_interval: float = 0.1  # seconds between shots
    timelapse_interval: int = 5  # seconds between captures
    
    # Available resolutions (populated at runtime)
    available_resolutions: List[Tuple[int, int]] = field(default_factory=list)
    
    # Preview settings
    preview_resolution: Tuple[int, int] = (640, 480)
    preview_framerate: int = 30
    preview_quality: int = 50
    
    def get_supported_modes(self) -> Dict[str, List[str]]:
        """Get all supported camera modes."""
        return {
            'exposure_modes': [mode.value for mode in ExposureMode],
            'white_balance_modes': [mode.value for mode in WhiteBalanceMode],
            'focus_modes': [mode.value for mode in FocusMode]
        }


@dataclass
class UIConfig:
    """Enhanced user interface configuration."""
    # Theme and appearance
    theme: str = Theme.LIGHT.value
    font_family: str = "SFCamera"
    font_size: int = 12
    font_scale: float = 1.0
    
    # Window and display
    fullscreen: bool = True
    window_width: int = 1920
    window_height: int = 1080
    display_rotation: int = 0  # 0, 90, 180, 270 degrees
    
    # Interface behavior
    auto_hide_cursor: bool = True
    cursor_timeout: int = 3000  # milliseconds
    animation_duration: int = 300  # milliseconds
    touch_mode: bool = True
    
    # Gallery and preview
    gallery_grid_size: int = 4  # items per row
    thumbnail_size: int = 200  # pixels
    preview_zoom_enabled: bool = True
    slideshow_interval: int = 5  # seconds
    
    # Accessibility
    high_contrast: bool = False
    large_ui_elements: bool = False
    screen_reader_support: bool = False
    voice_prompts: bool = False
    
    # Performance
    smooth_animations: bool = True
    gpu_acceleration: bool = True
    vsync_enabled: bool = True
    
    # Notifications
    show_notifications: bool = True
    notification_duration: int = 3000  # milliseconds
    sound_notifications: bool = True
    
    # Customization
    show_grid_lines: bool = False
    show_histogram: bool = False
    show_focus_peaking: bool = False
    show_overexposure_warning: bool = True


@dataclass
class SyncConfig:
    """Enhanced Google Photos synchronization configuration."""
    # Basic sync settings
    enabled: bool = False  # Start disabled by default
    auto_sync: bool = True
    sync_interval: int = 300  # seconds
    
    # Retry and reliability
    max_retry_attempts: int = 3
    retry_delay: int = 60  # seconds
    exponential_backoff: bool = True
    
    # Google Photos settings
    album_name: str = "ASZ Cam Photos"
    credentials_file: str = "google_credentials.json"
    create_monthly_albums: bool = False
    album_privacy: str = "private"  # private, shared
    
    # Upload settings
    upload_quality: str = "original"  # original, high_quality
    compress_images: bool = False
    max_file_size_mb: int = 100
    concurrent_uploads: int = 2
    
    # Content filtering
    upload_raw_files: bool = False
    upload_video_files: bool = True
    min_file_size_kb: int = 10
    
    # Privacy and metadata
    strip_location_data: bool = False
    strip_personal_metadata: bool = False
    add_upload_tags: bool = True
    
    # Bandwidth management
    upload_bandwidth_limit_mbps: int = 0  # 0 = unlimited
    only_sync_on_wifi: bool = True
    pause_on_low_battery: bool = True
    battery_threshold: int = 20  # percent
    
    # Storage management
    delete_after_sync: bool = False
    keep_local_days: int = 30
    max_local_storage_gb: int = 10


@dataclass
class NetworkConfig:
    """Network configuration settings."""
    # WiFi settings
    wifi_enabled: bool = True
    auto_connect: bool = True
    preferred_networks: List[str] = field(default_factory=list)
    
    # Connection management
    connection_timeout: int = 30  # seconds
    retry_attempts: int = 3
    roaming_enabled: bool = True
    
    # Hotspot settings
    hotspot_enabled: bool = False
    hotspot_ssid: str = "ASZ-Cam-{MAC}"
    hotspot_password: str = "aszcam123"
    hotspot_channel: int = 6
    
    # Network monitoring
    monitor_connection: bool = True
    ping_interval: int = 60  # seconds
    ping_hosts: List[str] = field(default_factory=lambda: ["8.8.8.8", "1.1.1.1"])
    
    # Proxy settings
    proxy_enabled: bool = False
    proxy_host: str = ""
    proxy_port: int = 8080
    proxy_username: str = ""
    proxy_password: str = ""
    
    # Advanced settings
    dns_servers: List[str] = field(default_factory=lambda: ["8.8.8.8", "1.1.1.1"])
    dhcp_enabled: bool = True
    static_ip: str = ""
    subnet_mask: str = ""
    gateway: str = ""


@dataclass
class PerformanceConfig:
    """System performance configuration."""
    # CPU settings
    cpu_governor: str = "performance"  # performance, powersave, ondemand
    cpu_max_freq: int = 0  # MHz, 0 = default
    cpu_min_freq: int = 0  # MHz, 0 = default
    
    # Memory settings
    gpu_memory_mb: int = 128
    swap_enabled: bool = False
    swap_size_mb: int = 1024
    memory_limit_mb: int = 0  # 0 = no limit
    
    # Storage settings
    enable_zram: bool = False
    io_scheduler: str = "mq-deadline"  # mq-deadline, kyber, none
    cache_size_mb: int = 64
    
    # Application performance
    thread_pool_size: int = 4
    max_concurrent_operations: int = 8
    gc_threshold: int = 100  # garbage collection frequency
    
    # Power management
    enable_power_saving: bool = False
    idle_timeout: int = 300  # seconds
    suspend_enabled: bool = False
    
    # Temperature management
    thermal_throttling: bool = True
    temp_warning_threshold: int = 70  # Celsius
    temp_critical_threshold: int = 80  # Celsius


@dataclass
class SystemConfig:
    """Enhanced system-level configuration."""
    # Basic system settings
    auto_start: bool = True
    log_level: str = LogLevel.INFO.value
    log_file: str = "/var/log/aszcam/aszcam.log"
    
    # Directory settings
    data_directory: str = "/home/pi/ASZCam"
    photos_directory: str = "/home/pi/Pictures/ASZCam"
    temp_directory: str = "/tmp/aszcam"
    backup_directory: str = "/home/pi/ASZCam/backups"
    
    # Storage management
    max_photos_storage: int = 1000
    cleanup_enabled: bool = True
    cleanup_interval_hours: int = 24
    min_free_space_gb: int = 2
    
    # Security settings
    enable_ssh: bool = False
    ssh_port: int = 22
    firewall_enabled: bool = True
    allowed_networks: List[str] = field(default_factory=lambda: ["192.168.0.0/16", "10.0.0.0/8"])
    
    # Update settings
    auto_update_enabled: bool = True
    update_channel: str = "stable"  # stable, beta, dev
    update_check_interval_hours: int = 24
    
    # Backup settings
    auto_backup_enabled: bool = True
    backup_interval_hours: int = 168  # weekly
    backup_retention_days: int = 30
    
    # Monitoring
    health_check_enabled: bool = True
    health_check_interval: int = 300  # seconds
    metrics_enabled: bool = True
    
    # Hardware settings
    hardware_acceleration: bool = True
    gpu_acceleration: bool = True
    camera_led_enabled: bool = True
    
    # Regional settings
    timezone: str = "UTC"
    locale: str = "en_US.UTF-8"
    keyboard_layout: str = "us"


class EnhancedSettings:
    """Enhanced settings manager for ASZ Cam OS with advanced configuration options."""
    
    def __init__(self, config_file: Optional[str] = None):
        """Initialize settings with all configuration sections."""
        self.config_file = config_file or self._get_default_config_path()
        
        # Initialize all configuration sections
        self.camera = CameraConfig()
        self.ui = UIConfig()
        self.sync = SyncConfig()
        self.network = NetworkConfig()
        self.performance = PerformanceConfig()
        self.system = SystemConfig()
        
        # Runtime state
        self._config_watchers = []
        self._last_modified = 0
        
        # Initialize
        self._ensure_directories()
        self.load_config()
        self._detect_hardware_capabilities()
    
    def _get_default_config_path(self) -> str:
        """Get the default configuration file path."""
        home = Path.home()
        config_dir = home / ".config" / "aszcam"
        config_dir.mkdir(parents=True, exist_ok=True)
        return str(config_dir / "settings.yaml")
    
    def _ensure_directories(self):
        """Ensure all required directories exist."""
        directories = [
            self.system.data_directory,
            self.system.photos_directory,
            self.system.temp_directory,
            self.system.backup_directory,
        ]
        
        for directory in directories:
            try:
                Path(directory).mkdir(parents=True, exist_ok=True)
            except PermissionError:
                # For development environments, use temp directory
                import tempfile
                temp_base = tempfile.gettempdir()
                rel_path = Path(directory).name
                temp_dir = Path(temp_base) / "aszcam" / rel_path
                temp_dir.mkdir(parents=True, exist_ok=True)
                
                # Update the directory path
                if directory == self.system.data_directory:
                    self.system.data_directory = str(temp_dir.parent / "ASZCam")
                elif directory == self.system.photos_directory:
                    self.system.photos_directory = str(temp_dir.parent / "Photos")
                elif directory == self.system.temp_directory:
                    self.system.temp_directory = str(temp_dir.parent / "temp")
                elif directory == self.system.backup_directory:
                    self.system.backup_directory = str(temp_dir.parent / "backups")
    
    def _detect_hardware_capabilities(self):
        """Detect hardware capabilities and update settings accordingly."""
        try:
            # Detect Raspberry Pi model and adjust performance settings
            if self._is_raspberry_pi():
                with open('/proc/device-tree/model', 'r') as f:
                    model = f.read().strip('\x00')
                    
                    # Adjust settings based on Pi model
                    if 'Pi 4' in model:
                        self.performance.thread_pool_size = 4
                        self.performance.max_concurrent_operations = 8
                        if '8GB' in model:
                            self.performance.gpu_memory_mb = 256
                    elif 'Pi 3' in model:
                        self.performance.thread_pool_size = 2
                        self.performance.max_concurrent_operations = 4
                        self.performance.gpu_memory_mb = 64
            
            # Detect available camera resolutions (would be done by camera service)
            # This is a placeholder - actual detection happens at runtime
            self.camera.available_resolutions = [
                (640, 480), (1280, 720), (1920, 1080), (2592, 1944), (3840, 2160)
            ]
            
        except Exception:
            pass  # Use defaults if detection fails
    
    def _is_raspberry_pi(self) -> bool:
        """Check if running on Raspberry Pi."""
        try:
            with open('/proc/cpuinfo', 'r') as f:
                cpuinfo = f.read()
                return 'Raspberry Pi' in cpuinfo or 'BCM' in cpuinfo
        except:
            return False
    
    def load_config(self):
        """Load configuration from file with validation."""
        if not os.path.exists(self.config_file):
            self.save_config()  # Create default config
            return
        
        try:
            with open(self.config_file, 'r') as f:
                data = yaml.safe_load(f) or {}
            
            # Update all configuration sections
            config_sections = [
                ('camera', self.camera),
                ('ui', self.ui), 
                ('sync', self.sync),
                ('network', self.network),
                ('performance', self.performance),
                ('system', self.system)
            ]
            
            for section_name, config_obj in config_sections:
                if section_name in data:
                    self._update_dataclass(config_obj, data[section_name])
            
            # Validate configuration
            self._validate_config()
            
            # Update last modified time
            self._last_modified = os.path.getmtime(self.config_file)
            
        except Exception as e:
            print(f"Error loading config: {e}")
            print("Using default configuration")
    
    def save_config(self):
        """Save current configuration to file with backup."""
        # Create backup of existing config
        if os.path.exists(self.config_file):
            backup_file = f"{self.config_file}.backup"
            try:
                with open(self.config_file, 'r') as src, open(backup_file, 'w') as dst:
                    dst.write(src.read())
            except:
                pass
        
        # Prepare configuration data
        config_data = {
            'version': '1.0.0',
            'timestamp': str(Path(self.config_file).stat().st_mtime if os.path.exists(self.config_file) else 0),
            'camera': asdict(self.camera),
            'ui': asdict(self.ui),
            'sync': asdict(self.sync),
            'network': asdict(self.network),
            'performance': asdict(self.performance),
            'system': asdict(self.system)
        }
        
        try:
            # Ensure directory exists
            Path(self.config_file).parent.mkdir(parents=True, exist_ok=True)
            
            # Write configuration
            with open(self.config_file, 'w') as f:
                yaml.dump(config_data, f, default_flow_style=False, indent=2)
            
            # Update last modified time
            self._last_modified = os.path.getmtime(self.config_file)
            
        except Exception as e:
            print(f"Error saving config: {e}")
    
    def _validate_config(self):
        """Validate configuration values and fix invalid ones."""
        # Camera validation
        if self.camera.quality < 1 or self.camera.quality > 100:
            self.camera.quality = 95
        
        if self.camera.iso < 0 or self.camera.iso > 3200:
            self.camera.iso = 0
        
        # UI validation  
        if self.ui.font_size < 8 or self.ui.font_size > 72:
            self.ui.font_size = 12
        
        if self.ui.display_rotation not in [0, 90, 180, 270]:
            self.ui.display_rotation = 0
        
        # Performance validation
        if self.performance.gpu_memory_mb < 16:
            self.performance.gpu_memory_mb = 128
        
        if self.performance.thread_pool_size < 1:
            self.performance.thread_pool_size = 4
    
    def _update_dataclass(self, obj, data: Dict[str, Any]):
        """Update dataclass fields with dictionary data."""
        for key, value in data.items():
            if hasattr(obj, key):
                # Type checking and conversion
                field_type = type(getattr(obj, key))
                try:
                    if field_type == bool:
                        value = bool(value)
                    elif field_type == int:
                        value = int(value)
                    elif field_type == float:
                        value = float(value)
                    elif field_type == list:
                        value = list(value) if isinstance(value, (list, tuple)) else [value]
                    
                    setattr(obj, key, value)
                except (ValueError, TypeError):
                    # Skip invalid values
                    continue
    
    def get_assets_path(self) -> Path:
        """Get the path to assets directory."""
        return Path(__file__).parent.parent.parent / "assets"
    
    def get_fonts_path(self) -> Path:
        """Get the path to fonts directory."""
        return self.get_assets_path() / "fonts"
    
    def get_themes_path(self) -> Path:
        """Get the path to themes directory."""
        return self.get_assets_path() / "themes"
    
    def reset_to_defaults(self, section: Optional[str] = None):
        """Reset configuration to defaults."""
        if section is None:
            # Reset all sections
            self.camera = CameraConfig()
            self.ui = UIConfig()
            self.sync = SyncConfig()
            self.network = NetworkConfig()
            self.performance = PerformanceConfig()
            self.system = SystemConfig()
        else:
            # Reset specific section
            if section == 'camera':
                self.camera = CameraConfig()
            elif section == 'ui':
                self.ui = UIConfig()
            elif section == 'sync':
                self.sync = SyncConfig()
            elif section == 'network':
                self.network = NetworkConfig()
            elif section == 'performance':
                self.performance = PerformanceConfig()
            elif section == 'system':
                self.system = SystemConfig()
        
        self.save_config()
    
    def export_config(self, export_file: str):
        """Export configuration to a file."""
        config_data = {
            'camera': asdict(self.camera),
            'ui': asdict(self.ui),
            'sync': asdict(self.sync),
            'network': asdict(self.network),
            'performance': asdict(self.performance),
            'system': asdict(self.system)
        }
        
        with open(export_file, 'w') as f:
            yaml.dump(config_data, f, default_flow_style=False, indent=2)
    
    def import_config(self, import_file: str):
        """Import configuration from a file."""
        with open(import_file, 'r') as f:
            data = yaml.safe_load(f)
        
        # Update configurations
        for section_name in ['camera', 'ui', 'sync', 'network', 'performance', 'system']:
            if section_name in data:
                config_obj = getattr(self, section_name)
                self._update_dataclass(config_obj, data[section_name])
        
        self._validate_config()
        self.save_config()
    
    def get_config_summary(self) -> Dict[str, Any]:
        """Get a summary of current configuration."""
        return {
            'config_file': self.config_file,
            'camera': {
                'resolution': self.camera.default_resolution,
                'quality': self.camera.quality,
                'exposure_mode': self.camera.exposure_mode,
                'focus_mode': self.camera.focus_mode
            },
            'ui': {
                'theme': self.ui.theme,
                'fullscreen': self.ui.fullscreen,
                'font_size': self.ui.font_size
            },
            'sync': {
                'enabled': self.sync.enabled,
                'auto_sync': self.sync.auto_sync,
                'album_name': self.sync.album_name
            },
            'network': {
                'wifi_enabled': self.network.wifi_enabled,
                'hotspot_enabled': self.network.hotspot_enabled
            },
            'performance': {
                'cpu_governor': self.performance.cpu_governor,
                'gpu_memory_mb': self.performance.gpu_memory_mb,
                'thread_pool_size': self.performance.thread_pool_size
            }
        }


# Create enhanced settings instance (backward compatible)
settings = EnhancedSettings()

# Maintain backward compatibility  
Settings = EnhancedSettings