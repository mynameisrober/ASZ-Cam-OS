"""
ASZ Cam OS - Settings View
Vista de configuración y ajustes del sistema
"""

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QCheckBox, QComboBox, QSpinBox,
                             QGroupBox, QFormLayout, QScrollArea)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont


class SettingsView(QWidget):
    """Vista de configuración del sistema"""
    
    settings_changed = pyqtSignal(dict)
    
    def __init__(self):
        super().__init__()
        self.settings = self.load_default_settings()
        self.setup_ui()
        
    def setup_ui(self):
        """Configura la interfaz de ajustes"""
        layout = QVBoxLayout()
        layout.setContentsMargins(10, 10, 10, 10)
        
        # Título
        title = QLabel("Ajustes")
        title.setStyleSheet("""
            QLabel {
                font-size: 24px;
                font-weight: bold;
                color: #424242;
                margin-bottom: 20px;
            }
        """)
        layout.addWidget(title)
        
        # Área scrollable para ajustes
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        
        settings_widget = QWidget()
        settings_layout = QVBoxLayout()
        
        # Secciones de configuración
        self.setup_camera_settings(settings_layout)
        self.setup_sync_settings(settings_layout) 
        self.setup_display_settings(settings_layout)
        self.setup_system_settings(settings_layout)
        
        settings_widget.setLayout(settings_layout)
        scroll_area.setWidget(settings_widget)
        
        layout.addWidget(scroll_area)
        
        # Botones de acción
        self.setup_action_buttons(layout)
        
        self.setLayout(layout)
    
    def setup_camera_settings(self, parent_layout):
        """Configuración de cámara"""
        group = QGroupBox("Configuración de Cámara")
        layout = QFormLayout()
        
        # Resolución
        self.resolution_combo = QComboBox()
        self.resolution_combo.addItems([
            "1920x1080 (Full HD)",
            "1280x720 (HD)", 
            "640x480 (VGA)"
        ])
        self.resolution_combo.setCurrentText(self.settings['camera']['resolution'])
        layout.addRow("Resolución:", self.resolution_combo)
        
        # FPS
        self.fps_spin = QSpinBox()
        self.fps_spin.setRange(1, 60)
        self.fps_spin.setValue(self.settings['camera']['fps'])
        layout.addRow("FPS:", self.fps_spin)
        
        # Auto ISO
        self.auto_iso_check = QCheckBox("ISO Automático")
        self.auto_iso_check.setChecked(self.settings['camera']['auto_iso'])
        layout.addRow(self.auto_iso_check)
        
        # Auto Exposición
        self.auto_exposure_check = QCheckBox("Exposición Automática")
        self.auto_exposure_check.setChecked(self.settings['camera']['auto_exposure'])
        layout.addRow(self.auto_exposure_check)
        
        # Estabilización
        self.stabilization_check = QCheckBox("Estabilización de Imagen")
        self.stabilization_check.setChecked(self.settings['camera']['stabilization'])
        layout.addRow(self.stabilization_check)
        
        group.setLayout(layout)
        parent_layout.addWidget(group)
    
    def setup_sync_settings(self, parent_layout):
        """Configuración de sincronización"""
        group = QGroupBox("Sincronización Google Photos")
        layout = QFormLayout()
        
        # Auto sync
        self.auto_sync_check = QCheckBox("Sincronización Automática")
        self.auto_sync_check.setChecked(self.settings['sync']['auto_sync'])
        layout.addRow(self.auto_sync_check)
        
        # Solo WiFi
        self.wifi_only_check = QCheckBox("Solo con WiFi")
        self.wifi_only_check.setChecked(self.settings['sync']['wifi_only'])
        layout.addRow(self.wifi_only_check)
        
        # Calidad de subida
        self.upload_quality_combo = QComboBox()
        self.upload_quality_combo.addItems([
            "Original", "Alta", "Media"
        ])
        self.upload_quality_combo.setCurrentText(self.settings['sync']['upload_quality'])
        layout.addRow("Calidad de Subida:", self.upload_quality_combo)
        
        # Estado de cuenta
        self.account_status_label = QLabel("No conectado")
        self.account_status_label.setStyleSheet("color: #757575;")
        layout.addRow("Estado de Cuenta:", self.account_status_label)
        
        # Botón de conectar/desconectar
        self.connect_button = QPushButton("Conectar Cuenta Google")
        self.connect_button.clicked.connect(self.toggle_google_connection)
        layout.addRow(self.connect_button)
        
        group.setLayout(layout)
        parent_layout.addWidget(group)
    
    def setup_display_settings(self, parent_layout):
        """Configuración de pantalla"""
        group = QGroupBox("Configuración de Pantalla")
        layout = QFormLayout()
        
        # Brillo
        self.brightness_spin = QSpinBox()
        self.brightness_spin.setRange(10, 100)
        self.brightness_spin.setValue(self.settings['display']['brightness'])
        self.brightness_spin.setSuffix("%")
        layout.addRow("Brillo:", self.brightness_spin)
        
        # Auto-apagado
        self.auto_off_spin = QSpinBox()
        self.auto_off_spin.setRange(1, 60)
        self.auto_off_spin.setValue(self.settings['display']['auto_off_minutes'])
        self.auto_off_spin.setSuffix(" min")
        layout.addRow("Auto-apagado:", self.auto_off_spin)
        
        # Mostrar información
        self.show_info_check = QCheckBox("Mostrar Información de Captura")
        self.show_info_check.setChecked(self.settings['display']['show_capture_info'])
        layout.addRow(self.show_info_check)
        
        group.setLayout(layout)
        parent_layout.addWidget(group)
    
    def setup_system_settings(self, parent_layout):
        """Configuración del sistema"""
        group = QGroupBox("Configuración del Sistema")
        layout = QFormLayout()
        
        # Inicio automático
        self.auto_start_check = QCheckBox("Inicio Automático de Cámara")
        self.auto_start_check.setChecked(self.settings['system']['auto_start_camera'])
        layout.addRow(self.auto_start_check)
        
        # Sonidos
        self.sounds_check = QCheckBox("Sonidos del Sistema")
        self.sounds_check.setChecked(self.settings['system']['sounds'])
        layout.addRow(self.sounds_check)
        
        # Información del sistema
        system_info = f"""Versión: ASZ Cam OS 1.0.0
Hardware: Raspberry Pi 4B
Almacenamiento: {self.get_storage_info()}
RAM: 4GB"""
        
        info_label = QLabel(system_info)
        info_label.setStyleSheet("""
            QLabel {
                background-color: #F5F5F5;
                padding: 10px;
                border-radius: 4px;
                font-size: 11px;
                color: #757575;
            }
        """)
        layout.addRow("Información:", info_label)
        
        group.setLayout(layout)
        parent_layout.addWidget(group)
    
    def setup_action_buttons(self, parent_layout):
        """Botones de acción"""
        buttons_layout = QHBoxLayout()
        
        # Guardar
        save_button = QPushButton("Guardar Cambios")
        save_button.clicked.connect(self.save_settings)
        save_button.setStyleSheet("""
            QPushButton {
                background-color: #9E9E9E;
                color: white;
                font-weight: bold;
                padding: 12px 24px;
            }
            QPushButton:hover {
                background-color: #757575;
            }
        """)
        
        # Restablecer
        reset_button = QPushButton("Restablecer")
        reset_button.clicked.connect(self.reset_settings)
        
        # Información
        info_button = QPushButton("Información del Sistema")
        info_button.clicked.connect(self.show_system_info)
        
        buttons_layout.addWidget(save_button)
        buttons_layout.addWidget(reset_button)
        buttons_layout.addWidget(info_button)
        buttons_layout.addStretch()
        
        parent_layout.addLayout(buttons_layout)
    
    def load_default_settings(self):
        """Carga la configuración por defecto"""
        return {
            'camera': {
                'resolution': '1920x1080 (Full HD)',
                'fps': 30,
                'auto_iso': True,
                'auto_exposure': True,
                'stabilization': True
            },
            'sync': {
                'auto_sync': True,
                'wifi_only': True,
                'upload_quality': 'Alta',
                'connected': False
            },
            'display': {
                'brightness': 80,
                'auto_off_minutes': 5,
                'show_capture_info': True
            },
            'system': {
                'auto_start_camera': True,
                'sounds': True
            }
        }
    
    def get_storage_info(self):
        """Obtiene información de almacenamiento"""
        import shutil
        try:
            total, used, free = shutil.disk_usage('/')
            free_gb = free // (2**30)
            return f"{free_gb}GB libres"
        except:
            return "No disponible"
    
    def save_settings(self):
        """Guarda la configuración"""
        # Actualizar settings con valores de la UI
        self.settings['camera']['resolution'] = self.resolution_combo.currentText()
        self.settings['camera']['fps'] = self.fps_spin.value()
        self.settings['camera']['auto_iso'] = self.auto_iso_check.isChecked()
        self.settings['camera']['auto_exposure'] = self.auto_exposure_check.isChecked()
        self.settings['camera']['stabilization'] = self.stabilization_check.isChecked()
        
        self.settings['sync']['auto_sync'] = self.auto_sync_check.isChecked()
        self.settings['sync']['wifi_only'] = self.wifi_only_check.isChecked()
        self.settings['sync']['upload_quality'] = self.upload_quality_combo.currentText()
        
        self.settings['display']['brightness'] = self.brightness_spin.value()
        self.settings['display']['auto_off_minutes'] = self.auto_off_spin.value()
        self.settings['display']['show_capture_info'] = self.show_info_check.isChecked()
        
        self.settings['system']['auto_start_camera'] = self.auto_start_check.isChecked()
        self.settings['system']['sounds'] = self.sounds_check.isChecked()
        
        # Emitir señal de cambios
        self.settings_changed.emit(self.settings)
        
        print("Configuración guardada")
    
    def reset_settings(self):
        """Restablece la configuración por defecto"""
        self.settings = self.load_default_settings()
        self.update_ui_from_settings()
        print("Configuración restablecida")
    
    def update_ui_from_settings(self):
        """Actualiza la UI con los valores de configuración"""
        # Actualizar todos los controles con valores de self.settings
        self.resolution_combo.setCurrentText(self.settings['camera']['resolution'])
        self.fps_spin.setValue(self.settings['camera']['fps'])
        self.auto_iso_check.setChecked(self.settings['camera']['auto_iso'])
        # ... etc para todos los controles
    
    def toggle_google_connection(self):
        """Alterna la conexión con Google"""
        if self.settings['sync']['connected']:
            self.disconnect_google()
        else:
            self.connect_google()
    
    def connect_google(self):
        """Conecta con Google Photos"""
        # Aquí iría la lógica de OAuth2
        self.settings['sync']['connected'] = True
        self.account_status_label.setText("Conectado")
        self.account_status_label.setStyleSheet("color: #4CAF50;")
        self.connect_button.setText("Desconectar Cuenta")
        print("Conectado a Google Photos")
    
    def disconnect_google(self):
        """Desconecta de Google Photos"""
        self.settings['sync']['connected'] = False
        self.account_status_label.setText("No conectado")
        self.account_status_label.setStyleSheet("color: #757575;")
        self.connect_button.setText("Conectar Cuenta Google")
        print("Desconectado de Google Photos")
    
    def show_system_info(self):
        """Muestra información detallada del sistema"""
        from PyQt5.QtWidgets import QMessageBox
        
        info = f"""ASZ Cam OS 1.0.0

Hardware: Raspberry Pi 4B
RAM: 4GB
Almacenamiento: {self.get_storage_info()}

Libcamera: Disponible
OpenCV: {self.get_opencv_version()}
PyQt5: 5.15.x

Desarrollado para ASZ Cam"""
        
        QMessageBox.information(self, "Información del Sistema", info)
    
    def get_opencv_version(self):
        """Obtiene la versión de OpenCV"""
        try:
            import cv2
            return cv2.__version__
        except:
            return "No disponible"