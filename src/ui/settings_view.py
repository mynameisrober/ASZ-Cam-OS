"""
ASZ Cam OS - Settings View
System settings and configuration interface.
"""

import logging

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QGroupBox, QCheckBox, QSlider, QLineEdit, QComboBox
)
from PyQt6.QtCore import Qt

from config.settings import settings


class SettingsView(QWidget):
    """Settings view for system configuration."""
    
    def __init__(self):
        super().__init__()
        self.logger = logging.getLogger(__name__)
        
        self._setup_ui()
        self.logger.info("Settings view initialized")
    
    def _setup_ui(self):
        """Set up the settings user interface."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)
        
        # Title
        title_label = QLabel("Settings")
        title_label.setProperty("class", "title")
        layout.addWidget(title_label)
        
        # Camera Settings
        camera_group = QGroupBox("Camera Settings")
        camera_layout = QVBoxLayout(camera_group)
        
        # Camera resolution
        res_layout = QHBoxLayout()
        res_layout.addWidget(QLabel("Resolution:"))
        res_combo = QComboBox()
        res_combo.addItems(["1920x1080", "1280x720", "640x480"])
        res_layout.addWidget(res_combo)
        res_layout.addStretch()
        camera_layout.addLayout(res_layout)
        
        # Camera quality
        quality_layout = QHBoxLayout()
        quality_layout.addWidget(QLabel("Quality:"))
        quality_slider = QSlider(Qt.Orientation.Horizontal)
        quality_slider.setRange(50, 100)
        quality_slider.setValue(settings.camera.quality)
        quality_layout.addWidget(quality_slider)
        camera_layout.addLayout(quality_layout)
        
        layout.addWidget(camera_group)
        
        # Sync Settings
        sync_group = QGroupBox("Sync Settings")
        sync_layout = QVBoxLayout(sync_group)
        
        sync_enabled = QCheckBox("Enable Google Photos sync")
        sync_enabled.setChecked(settings.sync.enabled)
        sync_layout.addWidget(sync_enabled)
        
        auto_sync = QCheckBox("Auto sync after capture")
        auto_sync.setChecked(settings.sync.auto_sync)
        sync_layout.addWidget(auto_sync)
        
        layout.addWidget(sync_group)
        
        # System info
        info_group = QGroupBox("System Information")
        info_layout = QVBoxLayout(info_group)
        
        info_layout.addWidget(QLabel("ASZ Cam OS v1.0.0"))
        info_layout.addWidget(QLabel("Camera: Available"))
        info_layout.addWidget(QLabel("Storage: 32GB available"))
        
        layout.addWidget(info_group)
        
        layout.addStretch()
    
    def load_settings(self):
        """Load current settings."""
        pass  # Settings are loaded automatically from config
    
    def save_settings(self):
        """Save current settings."""
        settings.save_config()
