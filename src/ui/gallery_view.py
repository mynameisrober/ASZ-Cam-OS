"""
ASZ Cam OS - Gallery View
Display and manage captured photos.
"""

import logging
import os
from pathlib import Path
from typing import List

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QScrollArea, QGridLayout, QFrame
)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from PyQt6.QtGui import QPixmap, QFont

from config.settings import settings


class GalleryView(QWidget):
    """Gallery view for displaying captured photos."""
    
    def __init__(self):
        super().__init__()
        self.logger = logging.getLogger(__name__)
        
        # UI components
        self.scroll_area = None
        self.grid_widget = None
        self.grid_layout = None
        self.photos_count_label = None
        
        # Data
        self.photo_items = []
        
        self._setup_ui()
        self.logger.info("Gallery view initialized")
    
    def _setup_ui(self):
        """Set up the gallery user interface."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)
        
        # Header
        header_layout = QHBoxLayout()
        
        title_label = QLabel("Photos")
        title_label.setObjectName("title")
        title_label.setProperty("class", "title")
        
        self.photos_count_label = QLabel("0 photos")
        self.photos_count_label.setProperty("class", "subtitle")
        
        header_layout.addWidget(title_label)
        header_layout.addStretch()
        header_layout.addWidget(self.photos_count_label)
        
        layout.addLayout(header_layout)
        
        # Photos grid
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        
        self.grid_widget = QWidget()
        self.grid_layout = QGridLayout(self.grid_widget)
        self.grid_layout.setSpacing(10)
        
        self.scroll_area.setWidget(self.grid_widget)
        layout.addWidget(self.scroll_area)
        
        # Initial load
        self.refresh_photos()
    
    def refresh_photos(self):
        """Refresh the photo gallery."""
        self.logger.info("Refreshing photo gallery...")
        
        # Clear existing items
        self._clear_grid()
        
        # Get photo files
        photos = self._get_photo_files()
        
        # Update count
        self.photos_count_label.setText(f"{len(photos)} photos")
        
        # Add photos to grid
        self._populate_grid(photos)
    
    def _clear_grid(self):
        """Clear the photo grid."""
        for i in reversed(range(self.grid_layout.count())):
            child = self.grid_layout.itemAt(i).widget()
            if child:
                child.setParent(None)
        self.photo_items.clear()
    
    def _get_photo_files(self) -> List[Path]:
        """Get list of photo files from the photos directory."""
        photos_dir = Path(settings.system.photos_directory)
        
        if not photos_dir.exists():
            return []
        
        # Supported image extensions
        extensions = {'.jpg', '.jpeg', '.png', '.bmp'}
        
        photos = []
        try:
            for file_path in photos_dir.iterdir():
                if file_path.is_file() and file_path.suffix.lower() in extensions:
                    photos.append(file_path)
            
            # Sort by modification time (newest first)
            photos.sort(key=lambda x: x.stat().st_mtime, reverse=True)
            
        except Exception as e:
            self.logger.error(f"Error reading photos directory: {e}")
        
        return photos
    
    def _populate_grid(self, photos: List[Path]):
        """Populate the grid with photo thumbnails."""
        columns = 3  # Number of columns in grid
        
        for index, photo_path in enumerate(photos):
            row = index // columns
            col = index % columns
            
            # Create photo item
            photo_item = self._create_photo_item(photo_path)
            if photo_item:
                self.grid_layout.addWidget(photo_item, row, col)
                self.photo_items.append(photo_item)
    
    def _create_photo_item(self, photo_path: Path):
        """Create a photo item widget."""
        try:
            # Create container frame
            frame = QFrame()
            frame.setFrameStyle(QFrame.Shape.StyledPanel)
            frame.setFixedSize(200, 200)
            frame.setProperty("class", "photoItem")
            
            layout = QVBoxLayout(frame)
            layout.setContentsMargins(5, 5, 5, 5)
            layout.setSpacing(5)
            
            # Load and scale image
            pixmap = QPixmap(str(photo_path))
            if pixmap.isNull():
                # Create placeholder if image can't be loaded
                pixmap = QPixmap(180, 135)
                pixmap.fill(Qt.GlobalColor.lightGray)
            else:
                # Scale to thumbnail size
                pixmap = pixmap.scaled(180, 135, Qt.AspectRatioMode.KeepAspectRatio, 
                                     Qt.TransformationMode.SmoothTransformation)
            
            # Image label
            image_label = QLabel()
            image_label.setPixmap(pixmap)
            image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            image_label.setStyleSheet("background-color: #F8F8F8; border: 1px solid #E0E0E0;")
            
            # Info label
            info_text = photo_path.name
            if len(info_text) > 20:
                info_text = info_text[:17] + "..."
            
            info_label = QLabel(info_text)
            info_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            info_label.setProperty("class", "caption")
            
            layout.addWidget(image_label)
            layout.addWidget(info_label)
            
            # Make clickable (for future full-screen view)
            frame.mousePressEvent = lambda event, path=photo_path: self._on_photo_clicked(path)
            
            return frame
            
        except Exception as e:
            self.logger.error(f"Error creating photo item for {photo_path}: {e}")
            return None
    
    def _on_photo_clicked(self, photo_path: Path):
        """Handle photo item clicked."""
        self.logger.info(f"Photo clicked: {photo_path}")
        # Could implement full-screen photo viewer here
    
    def get_photo_count(self) -> int:
        """Get total number of photos."""
        return len(self.photo_items)
