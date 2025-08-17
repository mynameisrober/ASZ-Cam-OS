"""
ASZ Cam OS - Main Window
Ventana principal con navegación entre las 4 secciones principales
"""

from PyQt5.QtWidgets import (QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, 
                             QStackedWidget, QPushButton, QLabel)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont, QIcon

from ui.camera_view import CameraView
from ui.settings_view import SettingsView
from ui.photos_view import PhotosView
from ui.memories_view import MemoriesView
from ui.theme import ASZTheme


class NavigationBar(QWidget):
    """Barra de navegación principal"""
    section_changed = pyqtSignal(int)
    
    def __init__(self):
        super().__init__()
        self.current_section = 0
        self.setup_ui()
        
    def setup_ui(self):
        """Configura la interfaz de navegación"""
        layout = QHBoxLayout()
        layout.setSpacing(0)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Botones de navegación
        self.buttons = []
        sections = [
            ("Cámara", 0),
            ("Ajustes", 1), 
            ("Fotos", 2),
            ("Recuerdos", 3)
        ]
        
        for name, index in sections:
            button = QPushButton(name)
            button.clicked.connect(lambda checked, i=index: self.set_section(i))
            button.setObjectName(f"nav_button_{index}")
            ASZTheme.apply_navigation_button(button)
            self.buttons.append(button)
            layout.addWidget(button)
            
        # Seleccionar cámara por defecto
        self.buttons[0].setProperty("selected", True)
        self.buttons[0].style().unpolish(self.buttons[0])
        self.buttons[0].style().polish(self.buttons[0])
        
        self.setLayout(layout)
        
    def set_section(self, index):
        """Cambia a la sección especificada"""
        if index == self.current_section:
            return
            
        # Deseleccionar botón anterior
        self.buttons[self.current_section].setProperty("selected", False)
        self.buttons[self.current_section].style().unpolish(self.buttons[self.current_section])
        self.buttons[self.current_section].style().polish(self.buttons[self.current_section])
        
        # Seleccionar nuevo botón
        self.buttons[index].setProperty("selected", True)
        self.buttons[index].style().unpolish(self.buttons[index])
        self.buttons[index].style().polish(self.buttons[index])
        
        self.current_section = index
        self.section_changed.emit(index)


class MainWindow(QMainWindow):
    """Ventana principal de ASZ Cam OS"""
    
    def __init__(self, camera_service):
        super().__init__()
        self.camera_service = camera_service
        self.setup_ui()
        
    def setup_ui(self):
        """Configura la interfaz principal"""
        self.setWindowTitle("ASZ Cam OS")
        self.setMinimumSize(800, 600)
        
        # Aplicar tema
        ASZTheme.apply_to_app(self)
        
        # Widget central
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Layout principal
        layout = QVBoxLayout()
        layout.setSpacing(0)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Stack de vistas
        self.stacked_widget = QStackedWidget()
        
        # Crear vistas
        self.camera_view = CameraView(self.camera_service)
        self.settings_view = SettingsView()
        self.photos_view = PhotosView()
        self.memories_view = MemoriesView()
        
        # Agregar vistas al stack
        self.stacked_widget.addWidget(self.camera_view)
        self.stacked_widget.addWidget(self.settings_view)
        self.stacked_widget.addWidget(self.photos_view)
        self.stacked_widget.addWidget(self.memories_view)
        
        # Barra de navegación
        self.nav_bar = NavigationBar()
        self.nav_bar.section_changed.connect(self.change_section)
        
        # Agregar widgets al layout
        layout.addWidget(self.stacked_widget, 1)  # Expandir vista principal
        layout.addWidget(self.nav_bar)
        
        central_widget.setLayout(layout)
        
        # Mostrar cámara por defecto
        self.stacked_widget.setCurrentIndex(0)
        
    def change_section(self, index):
        """Cambia a la sección especificada"""
        self.stacked_widget.setCurrentIndex(index)
        
        # Activar/pausar cámara según la sección
        if index == 0:  # Cámara
            self.camera_view.start_camera()
        else:
            self.camera_view.stop_camera()
    
    def closeEvent(self, event):
        """Maneja el cierre de la aplicación"""
        self.camera_view.stop_camera()
        event.accept()