"""
ASZ Cam OS - Photos View
Vista de galería de fotos con grid de imágenes
"""

import os
from pathlib import Path
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QGridLayout, QScrollArea, QFrame,
                             QSizePolicy, QMessageBox)
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QSize
from PyQt5.QtGui import QPixmap, QIcon


class PhotoThumbnail(QFrame):
    """Widget para mostrar una miniatura de foto"""
    
    photo_selected = pyqtSignal(str)
    photo_deleted = pyqtSignal(str)
    
    def __init__(self, photo_path):
        super().__init__()
        self.photo_path = photo_path
        self.setup_ui()
        
    def setup_ui(self):
        """Configura la interfaz de la miniatura"""
        self.setFixedSize(180, 160)
        self.setFrameStyle(QFrame.StyledPanel)
        self.setStyleSheet("""
            PhotoThumbnail {
                background-color: #F5F5F5;
                border: 2px solid #E0E0E0;
                border-radius: 8px;
            }
            PhotoThumbnail:hover {
                border: 2px solid #BDBDBD;
                background-color: #EEEEEE;
            }
        """)
        
        layout = QVBoxLayout()
        layout.setContentsMargins(5, 5, 5, 5)
        
        # Imagen
        self.image_label = QLabel()
        self.image_label.setFixedSize(170, 120)
        self.image_label.setScaledContents(True)
        self.image_label.setAlignment(Qt.AlignCenter)
        self.load_thumbnail()
        
        # Información de la foto
        filename = Path(self.photo_path).name
        self.info_label = QLabel(filename[:15] + "..." if len(filename) > 15 else filename)
        self.info_label.setAlignment(Qt.AlignCenter)
        self.info_label.setStyleSheet("""
            QLabel {
                font-size: 10px;
                color: #757575;
                background-color: transparent;
            }
        """)
        
        layout.addWidget(self.image_label)
        layout.addWidget(self.info_label)
        
        self.setLayout(layout)
        
        # Hacer clickeable
        self.mousePressEvent = self.on_click
    
    def load_thumbnail(self):
        """Carga la miniatura de la imagen"""
        try:
            pixmap = QPixmap(self.photo_path)
            if pixmap.isNull():
                self.set_placeholder()
            else:
                # Escalar manteniendo aspect ratio
                scaled_pixmap = pixmap.scaled(
                    170, 120,
                    Qt.KeepAspectRatio,
                    Qt.SmoothTransformation
                )
                self.image_label.setPixmap(scaled_pixmap)
        except Exception as e:
            print(f"Error cargando miniatura {self.photo_path}: {e}")
            self.set_placeholder()
    
    def set_placeholder(self):
        """Establece placeholder cuando no se puede cargar la imagen"""
        self.image_label.setText("📷\\nImagen\\nno disponible")
        self.image_label.setStyleSheet("""
            QLabel {
                background-color: #F0F0F0;
                color: #BDBDBD;
                font-size: 12px;
                border: 1px solid #E0E0E0;
                border-radius: 4px;
            }
        """)
    
    def on_click(self, event):
        """Maneja el click en la miniatura"""
        if event.button() == Qt.LeftButton:
            self.photo_selected.emit(self.photo_path)


class PhotoLoader(QThread):
    """Hilo para cargar fotos en segundo plano"""
    
    photos_loaded = pyqtSignal(list)
    
    def __init__(self, photos_directory):
        super().__init__()
        self.photos_directory = photos_directory
    
    def run(self):
        """Busca y carga la lista de fotos"""
        photo_extensions = {'.jpg', '.jpeg', '.png', '.bmp', '.tiff'}
        photos = []
        
        try:
            photos_path = Path(self.photos_directory)
            if photos_path.exists():
                for file_path in photos_path.iterdir():
                    if file_path.suffix.lower() in photo_extensions:
                        photos.append(str(file_path))
                
                # Ordenar por fecha de modificación (más recientes primero)
                photos.sort(key=lambda x: os.path.getmtime(x), reverse=True)
                
        except Exception as e:
            print(f"Error cargando fotos: {e}")
        
        self.photos_loaded.emit(photos)


class PhotosView(QWidget):
    """Vista de galería de fotos"""
    
    def __init__(self):
        super().__init__()
        self.photos_directory = Path.home() / "ASZCam" / "Photos"
        self.photos = []
        self.thumbnails = []
        self.setup_ui()
        self.load_photos()
        
    def setup_ui(self):
        """Configura la interfaz de la galería"""
        layout = QVBoxLayout()
        layout.setContentsMargins(10, 10, 10, 10)
        
        # Header
        header_layout = QHBoxLayout()
        
        title = QLabel("Fotos")
        title.setStyleSheet("""
            QLabel {
                font-size: 24px;
                font-weight: bold;
                color: #424242;
            }
        """)
        
        self.photos_count_label = QLabel("Cargando...")
        self.photos_count_label.setStyleSheet("color: #757575; font-size: 14px;")
        
        refresh_button = QPushButton("🔄 Actualizar")
        refresh_button.clicked.connect(self.load_photos)
        
        delete_all_button = QPushButton("🗑️ Eliminar Todas")
        delete_all_button.clicked.connect(self.delete_all_photos)
        delete_all_button.setStyleSheet("""
            QPushButton {
                background-color: #FFCDD2;
                color: #D32F2F;
            }
            QPushButton:hover {
                background-color: #F8BBD9;
            }
        """)
        
        header_layout.addWidget(title)
        header_layout.addWidget(self.photos_count_label)
        header_layout.addStretch()
        header_layout.addWidget(refresh_button)
        header_layout.addWidget(delete_all_button)
        
        layout.addLayout(header_layout)
        
        # Área scrollable para las fotos
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        
        # Widget contenedor para el grid de fotos
        self.photos_widget = QWidget()
        self.photos_layout = QGridLayout()
        self.photos_layout.setSpacing(10)
        self.photos_widget.setLayout(self.photos_layout)
        
        self.scroll_area.setWidget(self.photos_widget)
        layout.addWidget(self.scroll_area)
        
        # Placeholder inicial
        self.show_placeholder("Cargando fotos...")
        
        self.setLayout(layout)
    
    def load_photos(self):
        """Carga las fotos desde el directorio"""
        self.show_placeholder("Cargando fotos...")
        
        # Crear directorio si no existe
        self.photos_directory.mkdir(parents=True, exist_ok=True)
        
        # Cargar fotos en segundo plano
        self.photo_loader = PhotoLoader(str(self.photos_directory))
        self.photo_loader.photos_loaded.connect(self.on_photos_loaded)
        self.photo_loader.start()
    
    def on_photos_loaded(self, photos):
        """Maneja cuando las fotos han sido cargadas"""
        self.photos = photos
        self.update_photos_display()
        
        # Actualizar contador
        count = len(photos)
        if count == 0:
            self.photos_count_label.setText("No hay fotos")
        elif count == 1:
            self.photos_count_label.setText("1 foto")
        else:
            self.photos_count_label.setText(f"{count} fotos")
    
    def update_photos_display(self):
        """Actualiza la visualización de las fotos"""
        # Limpiar layout existente
        self.clear_layout()
        
        if not self.photos:
            self.show_placeholder("No hay fotos todavía\\n\\n📷 Ve a Cámara para capturar fotos")
            return
        
        # Crear miniaturas en grid
        columns = 4  # 4 columnas de fotos
        for i, photo_path in enumerate(self.photos):
            row = i // columns
            col = i % columns
            
            thumbnail = PhotoThumbnail(photo_path)
            thumbnail.photo_selected.connect(self.show_photo_details)
            
            self.photos_layout.addWidget(thumbnail, row, col)
            self.thumbnails.append(thumbnail)
        
        # Remover placeholder si existe
        self.hide_placeholder()
    
    def clear_layout(self):
        """Limpia el layout de fotos"""
        # Remover todas las miniaturas
        for thumbnail in self.thumbnails:
            thumbnail.deleteLater()
        self.thumbnails.clear()
        
        # Limpiar layout
        while self.photos_layout.count():
            child = self.photos_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
    
    def show_placeholder(self, message):
        """Muestra un placeholder con mensaje"""
        self.placeholder_label = QLabel(message)
        self.placeholder_label.setAlignment(Qt.AlignCenter)
        self.placeholder_label.setStyleSheet("""
            QLabel {
                font-size: 18px;
                color: #BDBDBD;
                background-color: #FAFAFA;
                border: 2px dashed #E0E0E0;
                border-radius: 12px;
                padding: 40px;
            }
        """)
        
        # Agregar al centro del layout
        self.photos_layout.addWidget(self.placeholder_label, 0, 0, 1, 4)
    
    def hide_placeholder(self):
        """Oculta el placeholder"""
        if hasattr(self, 'placeholder_label'):
            self.placeholder_label.deleteLater()
            delattr(self, 'placeholder_label')
    
    def show_photo_details(self, photo_path):
        """Muestra detalles de una foto seleccionada"""
        from PyQt5.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QPushButton
        
        dialog = QDialog(self)
        dialog.setWindowTitle("Vista de Foto")
        dialog.setMinimumSize(600, 500)
        
        layout = QVBoxLayout()
        
        # Imagen grande
        image_label = QLabel()
        pixmap = QPixmap(photo_path)
        if not pixmap.isNull():
            scaled_pixmap = pixmap.scaled(
                550, 400,
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation
            )
            image_label.setPixmap(scaled_pixmap)
        else:
            image_label.setText("No se pudo cargar la imagen")
        
        image_label.setAlignment(Qt.AlignCenter)
        image_label.setStyleSheet("border: 1px solid #E0E0E0;")
        
        # Información de la foto
        try:
            file_stat = os.stat(photo_path)
            file_size = file_stat.st_size // 1024  # KB
            mod_time = os.path.getmtime(photo_path)
            from datetime import datetime
            date_str = datetime.fromtimestamp(mod_time).strftime("%d/%m/%Y %H:%M:%S")
            
            info_text = f"Archivo: {Path(photo_path).name}\\nTamaño: {file_size} KB\\nFecha: {date_str}"
        except:
            info_text = f"Archivo: {Path(photo_path).name}"
        
        info_label = QLabel(info_text)
        info_label.setStyleSheet("color: #757575; font-size: 12px; padding: 10px;")
        
        # Botones
        buttons_layout = QHBoxLayout()
        
        delete_button = QPushButton("🗑️ Eliminar")
        delete_button.clicked.connect(lambda: self.delete_photo(photo_path, dialog))
        delete_button.setStyleSheet("""
            QPushButton {
                background-color: #FFCDD2;
                color: #D32F2F;
            }
        """)
        
        close_button = QPushButton("Cerrar")
        close_button.clicked.connect(dialog.close)
        
        buttons_layout.addWidget(delete_button)
        buttons_layout.addStretch()
        buttons_layout.addWidget(close_button)
        
        layout.addWidget(image_label)
        layout.addWidget(info_label)
        layout.addLayout(buttons_layout)
        
        dialog.setLayout(layout)
        dialog.exec_()
    
    def delete_photo(self, photo_path, dialog=None):
        """Elimina una foto"""
        reply = QMessageBox.question(
            self, 
            "Eliminar Foto",
            f"¿Estás seguro de que quieres eliminar esta foto?\\n\\n{Path(photo_path).name}",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            try:
                os.remove(photo_path)
                print(f"Foto eliminada: {photo_path}")
                self.load_photos()  # Recargar galería
                if dialog:
                    dialog.close()
            except Exception as e:
                QMessageBox.warning(self, "Error", f"No se pudo eliminar la foto:\\n{str(e)}")
    
    def delete_all_photos(self):
        """Elimina todas las fotos"""
        if not self.photos:
            QMessageBox.information(self, "Información", "No hay fotos para eliminar.")
            return
        
        reply = QMessageBox.question(
            self, 
            "Eliminar Todas las Fotos",
            f"¿Estás seguro de que quieres eliminar TODAS las {len(self.photos)} fotos?\\n\\nEsta acción no se puede deshacer.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            deleted_count = 0
            for photo_path in self.photos[:]:  # Copia de la lista
                try:
                    os.remove(photo_path)
                    deleted_count += 1
                except Exception as e:
                    print(f"Error eliminando {photo_path}: {e}")
            
            QMessageBox.information(
                self, 
                "Fotos Eliminadas", 
                f"Se eliminaron {deleted_count} fotos correctamente."
            )
            
            self.load_photos()  # Recargar galería