"""
ASZ Cam OS - Google Photos Sync Service
Servicio de sincronización con Google Photos usando OAuth2 y API
"""

import os
import json
import threading
from pathlib import Path
from datetime import datetime
from PyQt5.QtCore import QObject, pyqtSignal, QTimer

# Simulación de librerías de Google Photos (para desarrollo)
# En producción usarían: google-auth, google-auth-oauthlib, google-api-python-client


class GooglePhotosSync(QObject):
    """Servicio de sincronización con Google Photos"""
    
    # Señales
    authentication_changed = pyqtSignal(bool)  # True si autenticado
    upload_started = pyqtSignal(str)  # Ruta del archivo
    upload_completed = pyqtSignal(str, bool)  # Ruta, éxito
    upload_progress = pyqtSignal(str, int)  # Ruta, porcentaje
    sync_status_changed = pyqtSignal(str)  # Estado de sincronización
    
    def __init__(self):
        super().__init__()
        
        # Configuración
        self.config_dir = Path.home() / ".config" / "asz-cam-os"
        self.config_dir.mkdir(parents=True, exist_ok=True)
        self.credentials_file = self.config_dir / "google_credentials.json"
        self.upload_queue_file = self.config_dir / "upload_queue.json"
        
        # Estado
        self.is_authenticated = False
        self.is_uploading = False
        self.upload_queue = []
        self.failed_uploads = []
        
        # Configuración de Google API (simulada)
        self.client_config = {
            "client_id": "123456789-abcdefghijklmnop.apps.googleusercontent.com",
            "client_secret": "ABCDEF123456",
            "scopes": ["https://www.googleapis.com/auth/photoslibrary.appendonly"]
        }
        
        # Timer para reintentos
        self.retry_timer = QTimer()
        self.retry_timer.timeout.connect(self.process_retry_queue)
        self.retry_timer.start(30000)  # Cada 30 segundos
        
        # Cargar estado
        self.load_authentication_state()
        self.load_upload_queue()
        
    def load_authentication_state(self):
        """Carga el estado de autenticación"""
        try:
            if self.credentials_file.exists():
                with open(self.credentials_file, 'r') as f:
                    credentials_data = json.load(f)
                    # En producción, aquí se validarían los tokens
                    self.is_authenticated = credentials_data.get('authenticated', False)
                    
                print(f"Estado de autenticación cargado: {self.is_authenticated}")
                self.authentication_changed.emit(self.is_authenticated)
        except Exception as e:
            print(f"Error cargando estado de autenticación: {e}")
            self.is_authenticated = False
    
    def load_upload_queue(self):
        """Carga la cola de uploads pendientes"""
        try:
            if self.upload_queue_file.exists():
                with open(self.upload_queue_file, 'r') as f:
                    queue_data = json.load(f)
                    self.upload_queue = queue_data.get('pending', [])
                    self.failed_uploads = queue_data.get('failed', [])
                    
                print(f"Cola de uploads cargada: {len(self.upload_queue)} pendientes, {len(self.failed_uploads)} fallidos")
        except Exception as e:
            print(f"Error cargando cola de uploads: {e}")
    
    def save_upload_queue(self):
        """Guarda la cola de uploads"""
        try:
            queue_data = {
                'pending': self.upload_queue,
                'failed': self.failed_uploads,
                'last_updated': datetime.now().isoformat()
            }
            
            with open(self.upload_queue_file, 'w') as f:
                json.dump(queue_data, f, indent=2)
                
        except Exception as e:
            print(f"Error guardando cola de uploads: {e}")
    
    def authenticate(self):
        """Inicia el proceso de autenticación OAuth2"""
        try:
            # En producción, aquí se abriría el navegador para OAuth2
            print("Iniciando autenticación con Google Photos...")
            self.sync_status_changed.emit("Autenticando...")
            
            # Simulación del proceso OAuth2
            def simulate_auth():
                import time
                time.sleep(2)  # Simular tiempo de autenticación
                
                # Guardar credenciales simuladas
                credentials_data = {
                    'authenticated': True,
                    'access_token': 'fake_access_token_12345',
                    'refresh_token': 'fake_refresh_token_67890',
                    'expires_at': (datetime.now().timestamp() + 3600),  # 1 hora
                    'authenticated_at': datetime.now().isoformat()
                }
                
                with open(self.credentials_file, 'w') as f:
                    json.dump(credentials_data, f, indent=2)
                
                self.is_authenticated = True
                self.authentication_changed.emit(True)
                self.sync_status_changed.emit("Autenticado correctamente")
                print("Autenticación completada")
            
            # Ejecutar autenticación en hilo separado
            auth_thread = threading.Thread(target=simulate_auth)
            auth_thread.daemon = True
            auth_thread.start()
            
            return True
            
        except Exception as e:
            print(f"Error en autenticación: {e}")
            self.sync_status_changed.emit(f"Error de autenticación: {str(e)}")
            return False
    
    def disconnect(self):
        """Desconecta de Google Photos"""
        try:
            # Eliminar credenciales
            if self.credentials_file.exists():
                os.remove(self.credentials_file)
            
            self.is_authenticated = False
            self.authentication_changed.emit(False)
            self.sync_status_changed.emit("Desconectado de Google Photos")
            print("Desconectado de Google Photos")
            
        except Exception as e:
            print(f"Error desconectando: {e}")
    
    def queue_upload(self, photo_path):
        """Agrega una foto a la cola de subida"""
        if not os.path.exists(photo_path):
            print(f"Archivo no existe: {photo_path}")
            return False
        
        # Verificar que no esté ya en cola
        for queued in self.upload_queue:
            if queued['path'] == photo_path:
                print(f"Archivo ya en cola: {photo_path}")
                return False
        
        upload_item = {
            'path': photo_path,
            'filename': Path(photo_path).name,
            'size': os.path.getsize(photo_path),
            'queued_at': datetime.now().isoformat(),
            'attempts': 0
        }
        
        self.upload_queue.append(upload_item)
        self.save_upload_queue()
        
        print(f"Foto agregada a cola de subida: {Path(photo_path).name}")
        
        # Procesar cola si no estamos subiendo
        if not self.is_uploading and self.is_authenticated:
            self.process_upload_queue()
        
        return True
    
    def process_upload_queue(self):
        """Procesa la cola de uploads"""
        if not self.is_authenticated:
            self.sync_status_changed.emit("No autenticado - pausando uploads")
            return
        
        if self.is_uploading:
            return
        
        if not self.upload_queue:
            self.sync_status_changed.emit("Todas las fotos están sincronizadas")
            return
        
        self.is_uploading = True
        self.sync_status_changed.emit(f"Subiendo {len(self.upload_queue)} fotos...")
        
        # Procesar en hilo separado
        upload_thread = threading.Thread(target=self._upload_worker)
        upload_thread.daemon = True
        upload_thread.start()
    
    def _upload_worker(self):
        """Worker que procesa uploads en segundo plano"""
        while self.upload_queue and self.is_authenticated:
            upload_item = self.upload_queue[0]
            
            try:
                photo_path = upload_item['path']
                filename = upload_item['filename']
                
                # Verificar que el archivo sigue existiendo
                if not os.path.exists(photo_path):
                    print(f"Archivo no encontrado, removiendo de cola: {photo_path}")
                    self.upload_queue.pop(0)
                    continue
                
                print(f"Subiendo: {filename}")
                self.upload_started.emit(photo_path)
                
                # Simular progreso de subida
                for progress in range(0, 101, 20):
                    if not self.is_authenticated:
                        break
                    self.upload_progress.emit(photo_path, progress)
                    import time
                    time.sleep(0.5)  # Simular tiempo de subida
                
                if self.is_authenticated:
                    # Simular subida exitosa
                    self.upload_completed.emit(photo_path, True)
                    print(f"Subida completada: {filename}")
                    
                    # Remover de cola
                    self.upload_queue.pop(0)
                else:
                    # Subida interrumpida
                    upload_item['attempts'] += 1
                    if upload_item['attempts'] >= 3:
                        # Mover a lista de fallidos después de 3 intentos
                        failed_item = self.upload_queue.pop(0)
                        failed_item['failed_at'] = datetime.now().isoformat()
                        self.failed_uploads.append(failed_item)
                        print(f"Subida fallida después de 3 intentos: {filename}")
                    
                    self.upload_completed.emit(photo_path, False)
                
            except Exception as e:
                print(f"Error subiendo {upload_item.get('filename', 'unknown')}: {e}")
                
                # Incrementar intentos
                upload_item['attempts'] += 1
                if upload_item['attempts'] >= 3:
                    # Mover a fallidos
                    failed_item = self.upload_queue.pop(0)
                    failed_item['failed_at'] = datetime.now().isoformat()
                    failed_item['error'] = str(e)
                    self.failed_uploads.append(failed_item)
                else:
                    # Mover al final de la cola para reintentar
                    item = self.upload_queue.pop(0)
                    self.upload_queue.append(item)
                
                self.upload_completed.emit(upload_item['path'], False)
        
        self.is_uploading = False
        self.save_upload_queue()
        
        if self.upload_queue:
            self.sync_status_changed.emit(f"{len(self.upload_queue)} fotos pendientes")
        else:
            self.sync_status_changed.emit("Sincronización completada")
    
    def process_retry_queue(self):
        """Procesa reintentos automáticos"""
        if not self.is_authenticated or self.is_uploading:
            return
        
        # Reintentar uploads fallidos ocasionalmente
        if self.failed_uploads:
            # Mover un elemento fallido de vuelta a la cola cada 5 minutos
            current_time = datetime.now()
            for i, failed_item in enumerate(self.failed_uploads):
                try:
                    failed_time = datetime.fromisoformat(failed_item['failed_at'])
                    if (current_time - failed_time).seconds > 300:  # 5 minutos
                        # Mover de vuelta a cola
                        retry_item = self.failed_uploads.pop(i)
                        retry_item['attempts'] = 0  # Reset attempts
                        self.upload_queue.append(retry_item)
                        print(f"Reintentando upload: {retry_item['filename']}")
                        break
                except:
                    continue
        
        # Procesar cola si hay elementos
        if self.upload_queue and not self.is_uploading:
            self.process_upload_queue()
    
    def get_sync_status(self):
        """Obtiene el estado actual de sincronización"""
        return {
            'authenticated': self.is_authenticated,
            'uploading': self.is_uploading,
            'queue_size': len(self.upload_queue),
            'failed_count': len(self.failed_uploads),
            'total_uploads': len(self.upload_queue) + len(self.failed_uploads)
        }
    
    def clear_failed_uploads(self):
        """Limpia la lista de uploads fallidos"""
        cleared_count = len(self.failed_uploads)
        self.failed_uploads.clear()
        self.save_upload_queue()
        print(f"Limpiados {cleared_count} uploads fallidos")
        return cleared_count
    
    def retry_failed_uploads(self):
        """Reintenta todos los uploads fallidos"""
        retry_count = len(self.failed_uploads)
        
        # Mover todos los fallidos de vuelta a la cola
        for failed_item in self.failed_uploads:
            failed_item['attempts'] = 0  # Reset attempts
            self.upload_queue.append(failed_item)
        
        self.failed_uploads.clear()
        self.save_upload_queue()
        
        print(f"Reintentando {retry_count} uploads fallidos")
        
        # Procesar cola
        if not self.is_uploading and self.is_authenticated:
            self.process_upload_queue()
        
        return retry_count