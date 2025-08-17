"""
ASZ Cam OS - Camera Service
Servicio de cámara usando libcamera (simulado con OpenCV para desarrollo)
"""

import cv2
import numpy as np
from PyQt5.QtCore import QObject, QTimer, pyqtSignal
from PyQt5.QtGui import QImage, QPixmap
import os
from datetime import datetime
from pathlib import Path


class CameraService(QObject):
    """Servicio de cámara para ASZ Cam OS"""
    
    frame_ready = pyqtSignal(QPixmap)
    photo_captured = pyqtSignal(str)  # Ruta de la foto capturada
    
    def __init__(self):
        super().__init__()
        self.camera = None
        self.timer = QTimer()
        self.timer.timeout.connect(self.capture_frame)
        self.is_active = False
        
        # Configuración de almacenamiento
        self.photos_dir = Path.home() / "ASZCam" / "Photos"
        self.photos_dir.mkdir(parents=True, exist_ok=True)
        
        # Configuración de cámara
        self.camera_settings = {
            'width': 1920,
            'height': 1080,
            'fps': 30
        }
        
    def start_camera(self):
        """Inicia el servicio de cámara"""
        if self.is_active:
            return
            
        try:
            # Intentar usar libcamera primero (en Raspberry Pi)
            # Por ahora usamos OpenCV como fallback para desarrollo
            self.camera = cv2.VideoCapture(0)
            
            if not self.camera.isOpened():
                raise Exception("No se pudo abrir la cámara")
                
            # Configurar resolución
            self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, self.camera_settings['width'])
            self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, self.camera_settings['height'])
            self.camera.set(cv2.CAP_PROP_FPS, self.camera_settings['fps'])
            
            # Iniciar captura de frames
            self.timer.start(33)  # ~30 FPS
            self.is_active = True
            
        except Exception as e:
            print(f"Error al iniciar cámara: {e}")
            # Modo simulación para desarrollo sin cámara
            self.start_simulation_mode()
    
    def start_simulation_mode(self):
        """Modo simulación para desarrollo sin cámara física"""
        self.camera = None
        self.timer.start(100)  # 10 FPS para simulación
        self.is_active = True
        
    def stop_camera(self):
        """Detiene el servicio de cámara"""
        if not self.is_active:
            return
            
        self.timer.stop()
        
        if self.camera:
            self.camera.release()
            self.camera = None
            
        self.is_active = False
    
    def capture_frame(self):
        """Captura un frame de la cámara"""
        if self.camera:
            ret, frame = self.camera.read()
            if ret:
                # Convertir frame a QPixmap
                pixmap = self.cv_frame_to_pixmap(frame)
                self.frame_ready.emit(pixmap)
        else:
            # Modo simulación - generar imagen de prueba
            pixmap = self.generate_test_frame()
            self.frame_ready.emit(pixmap)
    
    def cv_frame_to_pixmap(self, cv_frame):
        """Convierte un frame de OpenCV a QPixmap"""
        height, width, channel = cv_frame.shape
        bytes_per_line = 3 * width
        
        # Convertir BGR a RGB
        rgb_frame = cv2.cvtColor(cv_frame, cv2.COLOR_BGR2RGB)
        
        # Crear QImage
        q_image = QImage(rgb_frame.data, width, height, bytes_per_line, QImage.Format_RGB888)
        
        # Convertir a QPixmap
        return QPixmap.fromImage(q_image)
    
    def generate_test_frame(self):
        """Genera un frame de prueba para simulación"""
        # Crear imagen de prueba con información de tiempo
        width, height = 640, 480
        img = np.ones((height, width, 3), dtype=np.uint8) * 240  # Gris claro
        
        # Agregar texto con timestamp
        timestamp = datetime.now().strftime("%H:%M:%S")
        cv2.putText(img, f"ASZ Cam OS - Modo Simulacion", 
                   (50, height//2 - 30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (100, 100, 100), 2)
        cv2.putText(img, timestamp, 
                   (50, height//2 + 10), cv2.FONT_HERSHEY_SIMPLEX, 1, (60, 60, 60), 2)
        
        # Convertir a QPixmap
        return self.cv_frame_to_pixmap(img)
    
    def capture_photo(self):
        """Captura una foto y la guarda"""
        if not self.is_active:
            return None
            
        try:
            if self.camera:
                ret, frame = self.camera.read()
                if not ret:
                    return None
            else:
                # Modo simulación - crear imagen de prueba de alta resolución
                frame = self.generate_test_photo()
            
            # Generar nombre de archivo
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"ASZ_{timestamp}.jpg"
            filepath = self.photos_dir / filename
            
            # Guardar imagen
            cv2.imwrite(str(filepath), frame)
            
            # Emitir señal de foto capturada
            self.photo_captured.emit(str(filepath))
            
            return str(filepath)
            
        except Exception as e:
            print(f"Error al capturar foto: {e}")
            return None
    
    def generate_test_photo(self):
        """Genera una foto de prueba de alta resolución"""
        width, height = 1920, 1080
        img = np.ones((height, width, 3), dtype=np.uint8) * 245  # Muy gris claro
        
        # Agregar información de captura
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cv2.putText(img, "ASZ Cam OS - Foto de Prueba", 
                   (100, height//2 - 50), cv2.FONT_HERSHEY_SIMPLEX, 2, (100, 100, 100), 4)
        cv2.putText(img, timestamp, 
                   (100, height//2 + 50), cv2.FONT_HERSHEY_SIMPLEX, 1.5, (60, 60, 60), 3)
        
        return img
    
    def get_camera_info(self):
        """Obtiene información de la cámara"""
        if self.camera:
            width = int(self.camera.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(self.camera.get(cv2.CAP_PROP_FRAME_HEIGHT))
            fps = int(self.camera.get(cv2.CAP_PROP_FPS))
            
            return {
                'width': width,
                'height': height,
                'fps': fps,
                'mode': 'libcamera/opencv'
            }
        else:
            return {
                'width': 640,
                'height': 480,
                'fps': 10,
                'mode': 'simulation'
            }