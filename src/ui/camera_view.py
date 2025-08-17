"""
ASZ Cam OS - Camera View
Vista principal de la cámara con preview y controles
"""

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QSlider, QGridLayout, QSpacerItem, QSizePolicy)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QPixmap, QFont


class CameraView(QWidget):
    """Vista principal de la cámara"""
    
    photo_captured = pyqtSignal(str)
    
    def __init__(self, camera_service):
        super().__init__()
        self.camera_service = camera_service
        self.setup_ui()
        self.connect_signals()
        
    def setup_ui(self):
        """Configura la interfaz de la vista de cámara"""
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Preview de la cámara
        self.setup_camera_preview(layout)
        
        # Controles de captura
        self.setup_capture_controls(layout)
        
        # Controles de cámara (ISO, exposición, etc.)
        self.setup_camera_controls(layout)
        
        self.setLayout(layout)
    
    def setup_camera_preview(self, parent_layout):
        """Configura el área de preview de la cámara"""
        # Contenedor para el preview
        preview_layout = QVBoxLayout()
        preview_layout.setContentsMargins(10, 10, 10, 10)
        
        # Label para mostrar el preview
        self.preview_label = QLabel()
        self.preview_label.setMinimumSize(640, 480)
        self.preview_label.setScaledContents(True)
        self.preview_label.setAlignment(Qt.AlignCenter)
        self.preview_label.setStyleSheet("""
            QLabel {
                background-color: #F0F0F0;
                border: 2px solid #E0E0E0;
                border-radius: 8px;
            }
        """)
        
        # Placeholder inicial
        self.set_preview_placeholder()
        
        preview_layout.addWidget(self.preview_label)
        parent_layout.addLayout(preview_layout, 1)  # Expandir
    
    def setup_capture_controls(self, parent_layout):
        """Configura los controles de captura"""
        controls_layout = QHBoxLayout()
        controls_layout.setContentsMargins(20, 10, 20, 10)
        
        # Espaciador izquierdo
        controls_layout.addItem(QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum))
        
        # Botón de captura principal
        self.capture_button = QPushButton("📸 Capturar")
        self.capture_button.clicked.connect(self.capture_photo)
        self.capture_button.setMinimumSize(120, 50)
        self.capture_button.setStyleSheet("""
            QPushButton {
                font-size: 16px;
                font-weight: bold;
                background-color: #BDBDBD;
                border: 2px solid #9E9E9E;
            }
            QPushButton:hover {
                background-color: #9E9E9E;
            }
            QPushButton:pressed {
                background-color: #757575;
                color: white;
            }
        """)
        
        controls_layout.addWidget(self.capture_button)
        
        # Espaciador derecho
        controls_layout.addItem(QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum))
        
        parent_layout.addLayout(controls_layout)
    
    def setup_camera_controls(self, parent_layout):
        """Configura los controles avanzados de cámara"""
        controls_widget = QWidget()
        controls_widget.setMaximumHeight(120)
        controls_layout = QGridLayout()
        
        # ISO Control
        iso_label = QLabel("ISO:")
        iso_label.setStyleSheet("font-weight: bold;")
        self.iso_slider = QSlider(Qt.Horizontal)
        self.iso_slider.setRange(100, 3200)
        self.iso_slider.setValue(400)
        self.iso_value_label = QLabel("400")
        self.iso_slider.valueChanged.connect(lambda v: self.iso_value_label.setText(str(v)))
        
        # Exposición Control
        exposure_label = QLabel("Exposición:")
        exposure_label.setStyleSheet("font-weight: bold;")
        self.exposure_slider = QSlider(Qt.Horizontal)
        self.exposure_slider.setRange(-3, 3)
        self.exposure_slider.setValue(0)
        self.exposure_value_label = QLabel("0")
        self.exposure_slider.valueChanged.connect(lambda v: self.exposure_value_label.setText(str(v)))
        
        # Brillo Control
        brightness_label = QLabel("Brillo:")
        brightness_label.setStyleSheet("font-weight: bold;")
        self.brightness_slider = QSlider(Qt.Horizontal)
        self.brightness_slider.setRange(-100, 100)
        self.brightness_slider.setValue(0)
        self.brightness_value_label = QLabel("0")
        self.brightness_slider.valueChanged.connect(lambda v: self.brightness_value_label.setText(str(v)))
        
        # Organizar en grid
        controls_layout.addWidget(iso_label, 0, 0)
        controls_layout.addWidget(self.iso_slider, 0, 1)
        controls_layout.addWidget(self.iso_value_label, 0, 2)
        
        controls_layout.addWidget(exposure_label, 1, 0)
        controls_layout.addWidget(self.exposure_slider, 1, 1)
        controls_layout.addWidget(self.exposure_value_label, 1, 2)
        
        controls_layout.addWidget(brightness_label, 2, 0)
        controls_layout.addWidget(self.brightness_slider, 2, 1)
        controls_layout.addWidget(self.brightness_value_label, 2, 2)
        
        # Información de cámara
        self.camera_info_label = QLabel()
        self.update_camera_info()
        controls_layout.addWidget(self.camera_info_label, 0, 3, 3, 1)
        
        controls_widget.setLayout(controls_layout)
        parent_layout.addWidget(controls_widget)
    
    def connect_signals(self):
        """Conecta las señales del servicio de cámara"""
        self.camera_service.frame_ready.connect(self.update_preview)
        self.camera_service.photo_captured.connect(self.on_photo_captured)
    
    def start_camera(self):
        """Inicia la cámara"""
        self.camera_service.start_camera()
        self.update_camera_info()
    
    def stop_camera(self):
        """Detiene la cámara"""
        self.camera_service.stop_camera()
        self.set_preview_placeholder()
    
    def update_preview(self, pixmap):
        """Actualiza el preview con un nuevo frame"""
        # Escalar pixmap manteniendo aspect ratio
        scaled_pixmap = pixmap.scaled(
            self.preview_label.size(),
            Qt.KeepAspectRatio,
            Qt.SmoothTransformation
        )
        self.preview_label.setPixmap(scaled_pixmap)
    
    def set_preview_placeholder(self):
        """Establece placeholder cuando no hay preview"""
        self.preview_label.clear()
        self.preview_label.setText("ASZ Cam OS\\n\\nCámara no activa")
        self.preview_label.setAlignment(Qt.AlignCenter)
        self.preview_label.setStyleSheet("""
            QLabel {
                background-color: #F5F5F5;
                border: 2px solid #E0E0E0;
                border-radius: 8px;
                font-size: 18px;
                color: #757575;
            }
        """)
    
    def capture_photo(self):
        """Captura una foto"""
        if self.camera_service.is_active:
            self.camera_service.capture_photo()
            
            # Feedback visual
            self.capture_button.setText("✓ Capturada")
            self.capture_button.setEnabled(False)
            
            # Restaurar botón después de 1 segundo
            from PyQt5.QtCore import QTimer
            QTimer.singleShot(1000, self.reset_capture_button)
    
    def reset_capture_button(self):
        """Restaura el botón de captura"""
        self.capture_button.setText("📸 Capturar")
        self.capture_button.setEnabled(True)
    
    def on_photo_captured(self, filepath):
        """Maneja cuando se captura una foto"""
        print(f"Foto capturada: {filepath}")
        self.photo_captured.emit(filepath)
    
    def update_camera_info(self):
        """Actualiza la información de la cámara"""
        info = self.camera_service.get_camera_info()
        info_text = f"""Cámara: {info['mode']}
Resolución: {info['width']}x{info['height']}
FPS: {info['fps']}"""
        self.camera_info_label.setText(info_text)
        self.camera_info_label.setStyleSheet("""
            QLabel {
                background-color: transparent;
                font-size: 11px;
                color: #757575;
                padding: 10px;
            }
        """)