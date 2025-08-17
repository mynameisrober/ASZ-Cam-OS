"""
ASZ Cam OS - Memories View
Vista de recuerdos con "Este día hace X años" y otras funciones de memoria
"""

import os
from pathlib import Path
from datetime import datetime, timedelta
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QScrollArea, QFrame, QGridLayout,
                             QSizePolicy, QMessageBox)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtGui import QPixmap, QFont


class MemoryCard(QFrame):
    """Tarjeta para mostrar un recuerdo"""
    
    memory_selected = pyqtSignal(dict)
    
    def __init__(self, memory_data):
        super().__init__()
        self.memory_data = memory_data
        self.setup_ui()
        
    def setup_ui(self):
        """Configura la interfaz de la tarjeta de recuerdo"""
        self.setFixedSize(300, 200)
        self.setFrameStyle(QFrame.StyledPanel)
        self.setStyleSheet("""
            MemoryCard {
                background-color: #F9F9F9;
                border: 2px solid #E8E8E8;
                border-radius: 12px;
            }
            MemoryCard:hover {
                border: 2px solid #BDBDBD;
                background-color: #F5F5F5;
            }
        """)
        
        layout = QVBoxLayout()
        layout.setContentsMargins(10, 10, 10, 10)
        
        # Título del recuerdo
        title_label = QLabel(self.memory_data.get('title', 'Recuerdo'))
        title_label.setStyleSheet("""
            QLabel {
                font-size: 16px;
                font-weight: bold;
                color: #424242;
                background-color: transparent;
            }
        """)
        layout.addWidget(title_label)
        
        # Descripción/fecha
        desc_label = QLabel(self.memory_data.get('description', ''))
        desc_label.setStyleSheet("""
            QLabel {
                font-size: 12px;
                color: #757575;
                background-color: transparent;
            }
        """)
        desc_label.setWordWrap(True)
        layout.addWidget(desc_label)
        
        # Miniatura de la foto principal (si existe)
        if 'main_photo' in self.memory_data and self.memory_data['main_photo']:
            self.photo_label = QLabel()
            self.photo_label.setFixedSize(280, 100)
            self.photo_label.setScaledContents(True)
            self.photo_label.setAlignment(Qt.AlignCenter)
            self.load_photo_thumbnail()
            layout.addWidget(self.photo_label)
        else:
            # Placeholder sin foto
            placeholder = QLabel("📷 Sin fotos para este recuerdo")
            placeholder.setAlignment(Qt.AlignCenter)
            placeholder.setFixedHeight(100)
            placeholder.setStyleSheet("""
                QLabel {
                    background-color: #F0F0F0;
                    border: 1px solid #E0E0E0;
                    border-radius: 8px;
                    color: #BDBDBD;
                    font-size: 12px;
                }
            """)
            layout.addWidget(placeholder)
        
        # Información adicional
        if 'photo_count' in self.memory_data:
            count_label = QLabel(f"📸 {self.memory_data['photo_count']} fotos")
            count_label.setStyleSheet("""
                QLabel {
                    font-size: 11px;
                    color: #9E9E9E;
                    background-color: transparent;
                }
            """)
            layout.addWidget(count_label)
        
        self.setLayout(layout)
        
        # Hacer clickeable
        self.mousePressEvent = self.on_click
    
    def load_photo_thumbnail(self):
        """Carga la miniatura de la foto principal"""
        try:
            photo_path = self.memory_data['main_photo']
            pixmap = QPixmap(photo_path)
            if not pixmap.isNull():
                scaled_pixmap = pixmap.scaled(
                    280, 100,
                    Qt.KeepAspectRatio,
                    Qt.SmoothTransformation
                )
                self.photo_label.setPixmap(scaled_pixmap)
            else:
                self.set_photo_placeholder()
        except Exception as e:
            print(f"Error cargando miniatura de recuerdo: {e}")
            self.set_photo_placeholder()
    
    def set_photo_placeholder(self):
        """Establece placeholder para la foto"""
        self.photo_label.setText("📷\\nImagen no\\ndisponible")
        self.photo_label.setStyleSheet("""
            QLabel {
                background-color: #F0F0F0;
                color: #BDBDBD;
                font-size: 10px;
                border: 1px solid #E0E0E0;
                border-radius: 4px;
            }
        """)
    
    def on_click(self, event):
        """Maneja el click en la tarjeta"""
        if event.button() == Qt.LeftButton:
            self.memory_selected.emit(self.memory_data)


class MemoriesLoader(QThread):
    """Hilo para generar recuerdos en segundo plano"""
    
    memories_loaded = pyqtSignal(list)
    
    def __init__(self, photos_directory):
        super().__init__()
        self.photos_directory = photos_directory
    
    def run(self):
        """Genera los recuerdos basados en las fotos existentes"""
        memories = []
        
        try:
            # Generar recuerdos de "Este día"
            memories.extend(self.generate_this_day_memories())
            
            # Generar recuerdos de "Esta semana el año pasado"
            memories.extend(self.generate_this_week_memories())
            
            # Generar recuerdos de "Primer foto"
            memories.extend(self.generate_first_photo_memory())
            
            # Generar recuerdos recientes
            memories.extend(self.generate_recent_memories())
            
        except Exception as e:
            print(f"Error generando recuerdos: {e}")
        
        self.memories_loaded.emit(memories)
    
    def generate_this_day_memories(self):
        """Genera recuerdos de 'Este día hace X años'"""
        memories = []
        today = datetime.now()
        
        # Buscar fotos del mismo día en años anteriores
        for years_ago in range(1, 6):  # Hasta 5 años atrás
            target_date = today - timedelta(days=365 * years_ago)
            photos_on_date = self.find_photos_on_date(target_date)
            
            if photos_on_date:
                memory = {
                    'type': 'this_day',
                    'title': f'Este día hace {years_ago} año{"s" if years_ago > 1 else ""}',
                    'description': f'Tomaste {len(photos_on_date)} foto{"s" if len(photos_on_date) > 1 else ""} el {target_date.strftime("%d de %B de %Y")}',
                    'date': target_date,
                    'photos': photos_on_date,
                    'main_photo': photos_on_date[0] if photos_on_date else None,
                    'photo_count': len(photos_on_date)
                }
                memories.append(memory)
        
        return memories
    
    def generate_this_week_memories(self):
        """Genera recuerdos de esta semana en años anteriores"""
        memories = []
        today = datetime.now()
        
        # Buscar fotos de esta semana en años anteriores
        for years_ago in range(1, 4):  # Hasta 3 años atrás
            start_week = today - timedelta(days=365 * years_ago + today.weekday())
            end_week = start_week + timedelta(days=6)
            
            photos_in_week = self.find_photos_in_range(start_week, end_week)
            
            if photos_in_week:
                memory = {
                    'type': 'this_week',
                    'title': f'Esta semana hace {years_ago} año{"s" if years_ago > 1 else ""}',
                    'description': f'Una semana activa con {len(photos_in_week)} fotos ({start_week.strftime("%d/%m/%Y")} - {end_week.strftime("%d/%m/%Y")})',
                    'date': start_week,
                    'photos': photos_in_week,
                    'main_photo': photos_in_week[0] if photos_in_week else None,
                    'photo_count': len(photos_in_week)
                }
                memories.append(memory)
        
        return memories
    
    def generate_first_photo_memory(self):
        """Genera recuerdo de la primera foto"""
        memories = []
        
        try:
            all_photos = self.get_all_photos()
            if all_photos:
                # Ordenar por fecha de creación
                all_photos.sort(key=lambda x: os.path.getctime(x))
                first_photo = all_photos[0]
                first_date = datetime.fromtimestamp(os.path.getctime(first_photo))
                
                days_ago = (datetime.now() - first_date).days
                
                if days_ago > 7:  # Solo mostrar si es hace más de una semana
                    memory = {
                        'type': 'first_photo',
                        'title': 'Tu primera foto',
                        'description': f'Tu primera foto con ASZ Cam fue tomada hace {days_ago} días el {first_date.strftime("%d de %B de %Y")}',
                        'date': first_date,
                        'photos': [first_photo],
                        'main_photo': first_photo,
                        'photo_count': 1
                    }
                    memories.append(memory)
        except Exception as e:
            print(f"Error generando recuerdo de primera foto: {e}")
        
        return memories
    
    def generate_recent_memories(self):
        """Genera recuerdos de actividad reciente"""
        memories = []
        
        try:
            # Fotos de la última semana
            week_ago = datetime.now() - timedelta(days=7)
            recent_photos = self.find_photos_since(week_ago)
            
            if len(recent_photos) >= 5:  # Solo si hay actividad significativa
                memory = {
                    'type': 'recent_activity',
                    'title': 'Semana activa',
                    'description': f'Has estado muy activo esta semana con {len(recent_photos)} fotos capturadas',
                    'date': week_ago,
                    'photos': recent_photos[:10],  # Máximo 10 fotos
                    'main_photo': recent_photos[0] if recent_photos else None,
                    'photo_count': len(recent_photos)
                }
                memories.append(memory)
        except Exception as e:
            print(f"Error generando recuerdos recientes: {e}")
        
        return memories
    
    def get_all_photos(self):
        """Obtiene todas las fotos disponibles"""
        photo_extensions = {'.jpg', '.jpeg', '.png', '.bmp', '.tiff'}
        photos = []
        
        try:
            photos_path = Path(self.photos_directory)
            if photos_path.exists():
                for file_path in photos_path.iterdir():
                    if file_path.suffix.lower() in photo_extensions:
                        photos.append(str(file_path))
        except Exception as e:
            print(f"Error obteniendo todas las fotos: {e}")
        
        return photos
    
    def find_photos_on_date(self, target_date):
        """Encuentra fotos tomadas en una fecha específica"""
        photos = []
        all_photos = self.get_all_photos()
        
        for photo_path in all_photos:
            try:
                photo_date = datetime.fromtimestamp(os.path.getctime(photo_path))
                if (photo_date.date() == target_date.date() or 
                    abs((photo_date.date() - target_date.date()).days) <= 1):  # ±1 día de tolerancia
                    photos.append(photo_path)
            except:
                continue
        
        return photos
    
    def find_photos_in_range(self, start_date, end_date):
        """Encuentra fotos en un rango de fechas"""
        photos = []
        all_photos = self.get_all_photos()
        
        for photo_path in all_photos:
            try:
                photo_date = datetime.fromtimestamp(os.path.getctime(photo_path))
                if start_date <= photo_date <= end_date:
                    photos.append(photo_path)
            except:
                continue
        
        return photos
    
    def find_photos_since(self, since_date):
        """Encuentra fotos desde una fecha específica"""
        photos = []
        all_photos = self.get_all_photos()
        
        for photo_path in all_photos:
            try:
                photo_date = datetime.fromtimestamp(os.path.getctime(photo_path))
                if photo_date >= since_date:
                    photos.append(photo_path)
            except:
                continue
        
        # Ordenar por fecha (más recientes primero)
        photos.sort(key=lambda x: os.path.getctime(x), reverse=True)
        return photos


class MemoriesView(QWidget):
    """Vista principal de recuerdos"""
    
    def __init__(self):
        super().__init__()
        self.photos_directory = Path.home() / "ASZCam" / "Photos"
        self.memories = []
        self.memory_cards = []
        self.setup_ui()
        self.load_memories()
        
    def setup_ui(self):
        """Configura la interfaz de recuerdos"""
        layout = QVBoxLayout()
        layout.setContentsMargins(10, 10, 10, 10)
        
        # Header
        header_layout = QHBoxLayout()
        
        title = QLabel("Recuerdos")
        title.setStyleSheet("""
            QLabel {
                font-size: 24px;
                font-weight: bold;
                color: #424242;
            }
        """)
        
        subtitle = QLabel("Revive tus momentos especiales")
        subtitle.setStyleSheet("""
            QLabel {
                font-size: 14px;
                color: #757575;
                margin-top: 5px;
            }
        """)
        
        refresh_button = QPushButton("🔄 Actualizar Recuerdos")
        refresh_button.clicked.connect(self.load_memories)
        
        header_layout.addWidget(title)
        header_layout.addStretch()
        header_layout.addWidget(refresh_button)
        
        layout.addWidget(title)
        layout.addWidget(subtitle)
        layout.addLayout(header_layout)
        layout.addSpacing(20)
        
        # Área scrollable para los recuerdos
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        
        # Widget contenedor para el grid de recuerdos
        self.memories_widget = QWidget()
        self.memories_layout = QGridLayout()
        self.memories_layout.setSpacing(15)
        self.memories_widget.setLayout(self.memories_layout)
        
        self.scroll_area.setWidget(self.memories_widget)
        layout.addWidget(self.scroll_area)
        
        # Placeholder inicial
        self.show_placeholder("Generando recuerdos...")
        
        self.setLayout(layout)
    
    def load_memories(self):
        """Carga los recuerdos"""
        self.show_placeholder("Generando recuerdos...")
        
        # Crear directorio si no existe
        self.photos_directory.mkdir(parents=True, exist_ok=True)
        
        # Generar recuerdos en segundo plano
        self.memories_loader = MemoriesLoader(str(self.photos_directory))
        self.memories_loader.memories_loaded.connect(self.on_memories_loaded)
        self.memories_loader.start()
    
    def on_memories_loaded(self, memories):
        """Maneja cuando los recuerdos han sido generados"""
        self.memories = memories
        self.update_memories_display()
    
    def update_memories_display(self):
        """Actualiza la visualización de los recuerdos"""
        # Limpiar layout existente
        self.clear_layout()
        
        if not self.memories:
            self.show_placeholder(
                "No hay recuerdos disponibles\\n\\n"
                "📷 Captura más fotos para generar recuerdos\\n"
                "Los recuerdos aparecerán cuando tengas fotos de días anteriores"
            )
            return
        
        # Ordenar recuerdos por relevancia/fecha
        self.memories.sort(key=lambda m: m.get('date', datetime.now()), reverse=True)
        
        # Crear tarjetas de recuerdos en grid
        columns = 3  # 3 columnas de recuerdos
        for i, memory_data in enumerate(self.memories):
            row = i // columns
            col = i % columns
            
            memory_card = MemoryCard(memory_data)
            memory_card.memory_selected.connect(self.show_memory_details)
            
            self.memories_layout.addWidget(memory_card, row, col)
            self.memory_cards.append(memory_card)
        
        # Remover placeholder si existe
        self.hide_placeholder()
    
    def clear_layout(self):
        """Limpia el layout de recuerdos"""
        # Remover todas las tarjetas
        for card in self.memory_cards:
            card.deleteLater()
        self.memory_cards.clear()
        
        # Limpiar layout
        while self.memories_layout.count():
            child = self.memories_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
    
    def show_placeholder(self, message):
        """Muestra un placeholder con mensaje"""
        self.placeholder_label = QLabel(message)
        self.placeholder_label.setAlignment(Qt.AlignCenter)
        self.placeholder_label.setStyleSheet("""
            QLabel {
                font-size: 16px;
                color: #BDBDBD;
                background-color: #FAFAFA;
                border: 2px dashed #E0E0E0;
                border-radius: 12px;
                padding: 60px;
            }
        """)
        
        # Agregar al centro del layout
        self.memories_layout.addWidget(self.placeholder_label, 0, 0, 1, 3)
    
    def hide_placeholder(self):
        """Oculta el placeholder"""
        if hasattr(self, 'placeholder_label'):
            self.placeholder_label.deleteLater()
            delattr(self, 'placeholder_label')
    
    def show_memory_details(self, memory_data):
        """Muestra detalles de un recuerdo seleccionado"""
        from PyQt5.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QGridLayout
        
        dialog = QDialog(self)
        dialog.setWindowTitle(f"Recuerdo: {memory_data['title']}")
        dialog.setMinimumSize(700, 600)
        
        layout = QVBoxLayout()
        
        # Título y descripción
        title_label = QLabel(memory_data['title'])
        title_label.setStyleSheet("""
            QLabel {
                font-size: 20px;
                font-weight: bold;
                color: #424242;
                margin-bottom: 10px;
            }
        """)
        
        desc_label = QLabel(memory_data['description'])
        desc_label.setStyleSheet("""
            QLabel {
                font-size: 14px;
                color: #757575;
                margin-bottom: 20px;
            }
        """)
        desc_label.setWordWrap(True)
        
        layout.addWidget(title_label)
        layout.addWidget(desc_label)
        
        # Grid de fotos del recuerdo
        if 'photos' in memory_data and memory_data['photos']:
            photos_scroll = QScrollArea()
            photos_widget = QWidget()
            photos_layout = QGridLayout()
            photos_layout.setSpacing(10)
            
            columns = 4
            for i, photo_path in enumerate(memory_data['photos'][:12]):  # Máximo 12 fotos
                row = i // columns
                col = i % columns
                
                try:
                    photo_label = QLabel()
                    photo_label.setFixedSize(120, 90)
                    photo_label.setScaledContents(True)
                    photo_label.setAlignment(Qt.AlignCenter)
                    photo_label.setStyleSheet("border: 1px solid #E0E0E0; border-radius: 4px;")
                    
                    pixmap = QPixmap(photo_path)
                    if not pixmap.isNull():
                        scaled_pixmap = pixmap.scaled(120, 90, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                        photo_label.setPixmap(scaled_pixmap)
                    else:
                        photo_label.setText("📷")
                    
                    photos_layout.addWidget(photo_label, row, col)
                except Exception as e:
                    print(f"Error cargando foto en recuerdo: {e}")
            
            photos_widget.setLayout(photos_layout)
            photos_scroll.setWidget(photos_widget)
            photos_scroll.setMaximumHeight(300)
            layout.addWidget(photos_scroll)
        else:
            no_photos_label = QLabel("No hay fotos disponibles para este recuerdo")
            no_photos_label.setAlignment(Qt.AlignCenter)
            no_photos_label.setStyleSheet("color: #BDBDBD; font-style: italic;")
            layout.addWidget(no_photos_label)
        
        # Botón cerrar
        close_button = QPushButton("Cerrar")
        close_button.clicked.connect(dialog.close)
        
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        button_layout.addWidget(close_button)
        
        layout.addLayout(button_layout)
        dialog.setLayout(layout)
        dialog.exec_()