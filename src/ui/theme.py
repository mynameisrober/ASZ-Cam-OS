"""
ASZ Cam OS - Theme Configuration
Sistema de temas con paleta de blancos y grises, tipografía SFCamera
"""

from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import QFont, QFontDatabase
from PyQt5.QtCore import Qt
from pathlib import Path


class ASZTheme:
    """Configuración de tema para ASZ Cam OS"""
    
    # Paleta de colores (solo blancos y grises)
    COLORS = {
        'white': '#FFFFFF',
        'light_gray': '#F5F5F5',
        'medium_gray': '#E0E0E0',
        'dark_gray': '#BDBDBD',
        'darker_gray': '#9E9E9E',
        'text_dark': '#424242',
        'text_light': '#757575'
    }
    
    @classmethod
    def load_sfcamera_font(cls):
        """Carga la tipografía SFCamera"""
        fonts_path = Path(__file__).parent.parent.parent / 'assets' / 'fonts'
        
        # Por ahora usamos una fuente del sistema similar
        # En una implementación completa, cargaríamos SFCamera desde los assets
        font = QFont("Arial", 12)  # Fallback font
        font.setStyleStrategy(QFont.PreferAntialias)
        
        return font
    
    @classmethod
    def get_main_stylesheet(cls):
        """Retorna el stylesheet principal de la aplicación"""
        return f"""
            QMainWindow {{
                background-color: {cls.COLORS['white']};
                color: {cls.COLORS['text_dark']};
            }}
            
            QWidget {{
                background-color: {cls.COLORS['white']};
                color: {cls.COLORS['text_dark']};
            }}
            
            QLabel {{
                color: {cls.COLORS['text_dark']};
                background-color: transparent;
            }}
            
            QPushButton {{
                background-color: {cls.COLORS['light_gray']};
                color: {cls.COLORS['text_dark']};
                border: 1px solid {cls.COLORS['medium_gray']};
                border-radius: 8px;
                padding: 12px 24px;
                font-weight: 500;
                min-height: 20px;
            }}
            
            QPushButton:hover {{
                background-color: {cls.COLORS['medium_gray']};
            }}
            
            QPushButton:pressed {{
                background-color: {cls.COLORS['dark_gray']};
            }}
            
            QPushButton[selected="true"] {{
                background-color: {cls.COLORS['darker_gray']};
                color: {cls.COLORS['white']};
                border: 1px solid {cls.COLORS['darker_gray']};
            }}
            
            QScrollArea {{
                border: none;
                background-color: {cls.COLORS['white']};
            }}
            
            QScrollBar:vertical {{
                background-color: {cls.COLORS['light_gray']};
                width: 12px;
                border-radius: 6px;
            }}
            
            QScrollBar::handle:vertical {{
                background-color: {cls.COLORS['dark_gray']};
                border-radius: 6px;
                min-height: 20px;
            }}
            
            QScrollBar::handle:vertical:hover {{
                background-color: {cls.COLORS['darker_gray']};
            }}
        """
    
    @classmethod
    def get_navigation_stylesheet(cls):
        """Stylesheet específico para la barra de navegación"""
        return f"""
            NavigationBar {{
                background-color: {cls.COLORS['light_gray']};
                border-top: 1px solid {cls.COLORS['medium_gray']};
                min-height: 60px;
                max-height: 60px;
            }}
            
            NavigationBar QPushButton {{
                background-color: transparent;
                border: none;
                border-radius: 0;
                padding: 16px 20px;
                font-size: 14px;
                font-weight: 500;
                color: {cls.COLORS['text_light']};
            }}
            
            NavigationBar QPushButton:hover {{
                background-color: {cls.COLORS['medium_gray']};
                color: {cls.COLORS['text_dark']};
            }}
            
            NavigationBar QPushButton[selected="true"] {{
                background-color: {cls.COLORS['darker_gray']};
                color: {cls.COLORS['white']};
                border-bottom: 3px solid {cls.COLORS['text_dark']};
            }}
        """
    
    @classmethod
    def apply_to_app(cls, widget):
        """Aplica el tema a toda la aplicación"""
        # Cargar fuente
        font = cls.load_sfcamera_font()
        widget.setFont(font)
        
        # Aplicar stylesheet
        widget.setStyleSheet(cls.get_main_stylesheet() + cls.get_navigation_stylesheet())
    
    @classmethod
    def apply_navigation_button(cls, button):
        """Aplica estilo específico a botones de navegación"""
        button.setMinimumHeight(44)
        button.setMaximumHeight(44)