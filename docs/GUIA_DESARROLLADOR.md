# ASZ Cam OS - Guía del Desarrollador

Guía comprehensiva de desarrollo para contribuir y extender ASZ Cam OS.

## Tabla de Contenidos
- [Configuración del Entorno de Desarrollo](#configuración-del-entorno-de-desarrollo)
- [Descripción de Arquitectura](#descripción-de-arquitectura)
- [Estructura del Código](#estructura-del-código)
- [Flujo de Trabajo de Desarrollo](#flujo-de-trabajo-de-desarrollo)
- [Referencia de API](#referencia-de-api)
- [Pruebas](#pruebas)
- [Guías de Contribución](#guías-de-contribución)
- [Implementación](#implementación)

## Configuración del Entorno de Desarrollo

### Prerrequisitos

#### Requisitos del Sistema Host
- **Python 3.9+**: Desarrollo y pruebas
- **Git**: Control de versiones
- **IDE**: VS Code, PyCharm, o similar
- **Cliente SSH**: Para desarrollo en Raspberry Pi

#### Target de Desarrollo Raspberry Pi
- **Raspberry Pi 4**: 4GB+ RAM recomendado para desarrollo
- **Raspberry Pi OS**: Versión de 64-bit
- **Acceso SSH**: Habilitado para desarrollo remoto
- **Módulo de Cámara**: Para probar funcionalidad de cámara

### Configuración de Desarrollo Local

```bash
# Clonar el repositorio
git clone https://github.com/mynameisrober/ASZ-Cam-OS.git
cd ASZ-Cam-OS

# Crear entorno virtual
python3 -m venv venv
source venv/bin/activate  # Linux/macOS
# venv\Scripts\activate   # Windows

# Instalar dependencias
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Instalar herramientas de desarrollo
pip install black flake8 pytest pytest-qt mypy
```

### Configuración del IDE

#### Visual Studio Code
```json
// .vscode/settings.json
{
    "python.defaultInterpreterPath": "./venv/bin/python",
    "python.linting.enabled": true,
    "python.linting.flake8Enabled": true,
    "python.formatting.provider": "black",
    "python.testing.pytestEnabled": true,
    "python.testing.pytestArgs": ["tests/"]
}
```

#### PyCharm
- **Configurar Intérprete**: Apuntar a `venv/bin/python`
- **Configurar Ejecutor de Pruebas**: Habilitar pytest
- **Configurar Formateador**: Usar Black para formateo de código
- **Configurar Linter**: Habilitar flake8 y mypy

### Desarrollo Remoto en Raspberry Pi

```bash
# Configurar SSH sin contraseña
ssh-keygen -t rsa -b 4096
ssh-copy-id pi@<raspberry-pi-ip>

# Configurar sync de archivos
# Usar rsync o herramientas de sincronización de IDE

# Ejecutar aplicación en Pi remoto
ssh pi@<raspberry-pi-ip> 'cd ASZ-Cam-OS && ./run_dev.sh'
```

## Descripción de Arquitectura

### Arquitectura del Sistema

ASZ Cam OS sigue una arquitectura modular basada en servicios:

```
┌─────────────────────────────────────────┐
│           Capa de Aplicación            │
│  main.py • Interface Manager • Eventos │
├─────────────────────────────────────────┤
│           Servicios Principales         │
│  Camera • Sync • Storage • Settings    │
├─────────────────────────────────────────┤
│          Capa de Abstracción            │
│  Hardware • Network • FileSystem       │
├─────────────────────────────────────────┤
│           Capa de Hardware              │
│  libCamera • GPIO • Display • I/O      │
└─────────────────────────────────────────┘
```

### Relaciones entre Componentes

#### Gestor del Sistema
- **Responsabilidades**: Inicialización, ciclo de vida, manejo de errores
- **Interfaces**: SystemServiceInterface, EventBus
- **Dependencias**: Todos los servicios principales

#### Servicio de Cámara
- **Responsabilidades**: Captura, configuración, hardware abstraction
- **Interfaces**: CameraInterface, HardwareInterface
- **Dependencias**: libcamera, servicios de almacenamiento

#### Servicio de Sincronización
- **Responsabilidades**: Upload de fotos, gestión de cola, retry logic
- **Interfaces**: CloudInterface, NetworkInterface
- **Dependencias**: Servicios de red, almacenamiento

#### Interfaz de Usuario
- **Responsabilidades**: Presentación, interacción de usuario, navigation
- **Interfaces**: UIInterface, EventInterface
- **Dependencias**: PyQt6, servicios de aplicación

### Patrones de Diseño

#### Patrón Service Locator
```python
class ServiceManager:
    """Gestor centralizado de servicios"""
    _services = {}
    
    @classmethod
    def register_service(cls, name: str, service):
        cls._services[name] = service
    
    @classmethod
    def get_service(cls, name: str):
        return cls._services.get(name)
```

#### Patrón Observer para Eventos
```python
class EventBus:
    """Bus de eventos para comunicación entre componentes"""
    def __init__(self):
        self._listeners = defaultdict(list)
    
    def subscribe(self, event_type: str, callback):
        self._listeners[event_type].append(callback)
    
    def publish(self, event_type: str, data=None):
        for callback in self._listeners[event_type]:
            callback(data)
```

#### Patrón Strategy para Proveedores de Nube
```python
class CloudProvider(ABC):
    """Interfaz abstracta para proveedores de nube"""
    @abstractmethod
    def upload(self, file_path: str) -> bool:
        pass
    
    @abstractmethod
    def authenticate(self) -> bool:
        pass

class GooglePhotosProvider(CloudProvider):
    """Implementación específica para Google Photos"""
    def upload(self, file_path: str) -> bool:
        # Implementación específica
        pass
```

## Estructura del Código

### Diseño de Directorios

```
ASZ-Cam-OS/
├── src/                          # Código fuente de aplicación
│   ├── core/                     # Componentes principales del sistema
│   │   ├── __init__.py
│   │   ├── system_manager.py     # Coordinador principal del sistema
│   │   ├── event_bus.py          # Sistema de eventos
│   │   └── service_manager.py    # Gestor de servicios
│   ├── camera/                   # Funcionalidad de cámara
│   │   ├── __init__.py
│   │   ├── camera_service.py     # Servicio de cámara de alto nivel
│   │   ├── libcamera_backend.py  # Abstracción de hardware
│   │   └── camera_settings.py    # Gestión de configuraciones
│   ├── ui/                       # Componentes de interfaz de usuario
│   │   ├── __init__.py
│   │   ├── main_window.py        # Ventana principal de aplicación
│   │   ├── camera_view.py        # Interfaz de cámara
│   │   ├── gallery_view.py       # Galería de fotos
│   │   ├── settings_panel.py     # Interfaz de configuración
│   │   └── themes/               # Temas y estilos
│   │       ├── __init__.py
│   │       ├── dark_theme.py
│   │       └── light_theme.py
│   ├── sync/                     # Sincronización en la nube
│   │   ├── __init__.py
│   │   ├── sync_service.py       # Coordinación de sincronización
│   │   ├── google_photos.py      # Integración con Google Photos
│   │   ├── upload_queue.py       # Gestión de cola de uploads
│   │   └── retry_logic.py        # Lógica de reintentos
│   ├── storage/                  # Gestión de almacenamiento de fotos
│   │   ├── __init__.py
│   │   ├── photo_manager.py      # Gestión de archivos de fotos
│   │   ├── metadata_handler.py   # Manejo de metadatos EXIF
│   │   └── file_operations.py    # Operaciones de archivos
│   ├── config/                   # Gestión de configuración
│   │   ├── __init__.py
│   │   ├── settings.py           # Sistema de configuración
│   │   ├── config_manager.py     # Carga y guardado de configuración
│   │   └── default_settings.py   # Configuraciones por defecto
│   ├── utils/                    # Utilidades y helpers
│   │   ├── __init__.py
│   │   ├── logger.py             # Sistema de logging
│   │   ├── validators.py         # Validadores de entrada
│   │   └── font_manager.py       # Manejo de fuentes
│   └── main.py                   # Punto de entrada de aplicación
├── assets/                       # Assets estáticos
│   ├── fonts/                    # Archivos de fuentes
│   ├── icons/                    # Iconos de interfaz
│   └── themes/                   # Temas de interfaz
├── scripts/                      # Scripts de instalación y utilidad
│   ├── install.sh                # Instalador principal
│   ├── setup_rpi.sh             # Configuración de Raspberry Pi
│   ├── download_fonts.sh        # Instalación de fuentes
│   └── configure_system.sh      # Configuración del sistema
├── install/                      # Archivos de configuración del sistema
│   ├── boot_config.txt          # Configuración de arranque de Raspberry Pi
│   ├── asz-cam-os.service       # Servicio systemd
│   ├── xorg.conf                # Configuración X11
│   └── raspi-config-settings.sh # Script de configuración RPi
├── docs/                         # Documentación
│   ├── INSTALACION.md
│   ├── GUIA_USUARIO.md
│   ├── GUIA_DESARROLLADOR.md
│   └── SOLUCION_PROBLEMAS.md
├── tests/                        # Suite de pruebas
│   ├── unit/                     # Pruebas unitarias
│   ├── integration/              # Pruebas de integración
│   └── fixtures/                 # Fixtures de pruebas
├── requirements.txt              # Dependencias de producción
├── requirements-dev.txt          # Dependencias de desarrollo
└── README.md                     # Descripción general del proyecto
```

### Componentes Principales

#### Gestor del Sistema (`src/core/system_manager.py`)
Coordinador central que gestiona el ciclo de vida del sistema:

```python
class SystemManager:
    """Gestor principal del sistema ASZ Cam OS"""
    
    def __init__(self):
        self.services = {}
        self.event_bus = EventBus()
        self.running = False
    
    async def initialize(self):
        """Inicializar todos los servicios del sistema"""
        await self._load_configuration()
        await self._initialize_services()
        await self._start_ui()
    
    async def shutdown(self):
        """Apagado ordenado del sistema"""
        await self._stop_services()
        await self._save_configuration()
```

#### Servicio de Cámara (`src/camera/camera_service.py`)
Interfaz de alto nivel para operaciones de cámara:

```python
class CameraService:
    """Servicio de cámara de alto nivel"""
    
    def __init__(self, backend='libcamera'):
        self.backend = self._create_backend(backend)
        self.settings = CameraSettings()
    
    async def capture_photo(self) -> str:
        """Capturar foto y devolver ruta de archivo"""
        settings = self.settings.get_capture_settings()
        return await self.backend.capture(settings)
    
    async def start_preview(self):
        """Iniciar vista previa de cámara"""
        await self.backend.start_preview()
```

#### Sistema de Configuración (`src/config/settings.py`)
Gestión centralizada de configuración:

```python
class Settings:
    """Sistema de configuración centralizado"""
    
    def __init__(self):
        self._settings = {}
        self._callbacks = defaultdict(list)
        self.load_settings()
    
    def get(self, key: str, default=None):
        """Obtener valor de configuración"""
        return self._settings.get(key, default)
    
    def set(self, key: str, value):
        """Establecer valor de configuración"""
        old_value = self._settings.get(key)
        self._settings[key] = value
        self._notify_callbacks(key, old_value, value)
```

### Estándares de Codificación

#### Guía de Estilo Python
- **Formateo**: Black formatter con líneas de 88 caracteres
- **Imports**: isort para ordenamiento de imports
- **Linting**: flake8 para verificación de estilo
- **Type Hints**: mypy para verificación de tipos

#### Ejemplo de Código
```python
from typing import Optional, List, Dict, Any
import logging
from pathlib import Path

logger = logging.getLogger(__name__)


class PhotoManager:
    """Gestiona operaciones de archivos de fotos.
    
    Esta clase maneja el almacenamiento, organización y metadatos
    de fotos capturadas por el sistema de cámara.
    
    Attributes:
        storage_path: Ruta donde se almacenan las fotos
        metadata_handler: Handler para operaciones de metadatos
    """
    
    def __init__(self, storage_path: Path):
        self.storage_path = storage_path
        self.metadata_handler = MetadataHandler()
        
        # Asegurar que el directorio existe
        self.storage_path.mkdir(parents=True, exist_ok=True)
    
    def save_photo(
        self, 
        image_data: bytes, 
        filename: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Path:
        """Guarda foto con metadatos opcionales.
        
        Args:
            image_data: Datos de imagen en bytes
            filename: Nombre de archivo opcional
            metadata: Metadatos opcionales para embed
            
        Returns:
            Ruta del archivo guardado
            
        Raises:
            IOError: Si el guardado falla
            ValueError: Si los datos de imagen son inválidos
        """
        if not image_data:
            raise ValueError("Datos de imagen no pueden estar vacíos")
        
        if filename is None:
            filename = self._generate_filename()
        
        file_path = self.storage_path / filename
        
        try:
            # Guardar archivo de imagen
            with open(file_path, 'wb') as f:
                f.write(image_data)
            
            # Agregar metadatos si se proporcionan
            if metadata:
                self.metadata_handler.add_metadata(file_path, metadata)
            
            logger.info(f"Foto guardada: {file_path}")
            return file_path
            
        except IOError as e:
            logger.error(f"Fallo al guardar foto: {e}")
            raise
    
    def _generate_filename(self) -> str:
        """Genera nombre de archivo único basado en timestamp."""
        from datetime import datetime
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return f"ASZCam_{timestamp}.jpg"
```

#### Manejo de Errores
```python
class ASZCamError(Exception):
    """Excepción base para errores de ASZ Cam OS"""
    pass


class CameraError(ASZCamError):
    """Excepciones relacionadas con cámara"""
    pass


class SyncError(ASZCamError):
    """Excepciones relacionadas con sincronización"""
    pass


# Uso de manejo de errores estructurado
async def capture_photo(self) -> str:
    try:
        return await self.camera_backend.capture()
    except HardwareError as e:
        logger.error(f"Error de hardware de cámara: {e}")
        raise CameraError(f"Fallo de captura: {e}") from e
    except Exception as e:
        logger.error(f"Error inesperado en captura: {e}")
        raise CameraError("Fallo inesperado de captura") from e
```

## Flujo de Trabajo de Desarrollo

### Configuración de Proyecto

#### Clonar y Configurar
```bash
# Clonar repositorio
git clone https://github.com/mynameisrober/ASZ-Cam-OS.git
cd ASZ-Cam-OS

# Configurar entorno de desarrollo
./scripts/setup_dev.sh

# Activar entorno virtual
source venv/bin/activate

# Verificar configuración
python -m pytest tests/ -v
```

#### Estructura de Branches
- **main**: Código estable listo para producción
- **develop**: Rama de desarrollo principal
- **feature/\***: Ramas de características específicas
- **bugfix/\***: Correcciones de errores
- **release/\***: Preparación de releases

### Proceso de Desarrollo

#### 1. Crear Rama de Característica
```bash
git checkout develop
git pull origin develop
git checkout -b feature/nueva-caracteristica
```

#### 2. Desarrollar y Probar
```bash
# Escribir código con TDD
python -m pytest tests/ -v --watch

# Ejecutar linters
black src/ tests/
flake8 src/ tests/
mypy src/

# Probar en Raspberry Pi
./scripts/deploy_dev.sh pi@192.168.1.100
```

#### 3. Commit y Push
```bash
# Commits siguiendo Conventional Commits
git add .
git commit -m "feat: agregar nueva funcionalidad de captura automática"
git push origin feature/nueva-caracteristica
```

#### 4. Crear Pull Request
- **Descripción**: Descripción clara de cambios
- **Tests**: Evidencia de pruebas pasando
- **Documentación**: Actualizar documentación si es necesario
- **Screenshots**: Para cambios de UI

### Estándares de Commit

#### Conventional Commits
```bash
# Formato: <tipo>(<scope>): <descripción>

# Ejemplos:
git commit -m "feat(camera): agregar soporte para captura RAW"
git commit -m "fix(sync): corregir timeout de upload"
git commit -m "docs(user-guide): actualizar sección de instalación"
git commit -m "test(camera): agregar pruebas para configuraciones de exposición"
git commit -m "refactor(ui): simplificar componente de galería"
```

#### Tipos de Commit
- **feat**: Nueva característica
- **fix**: Corrección de error
- **docs**: Cambios de documentación
- **style**: Cambios de formato (no afectan código)
- **refactor**: Refactoring de código
- **test**: Agregar o modificar pruebas
- **chore**: Tareas de mantenimiento

## Referencia de API

### API de Cámara

#### CameraService
```python
class CameraService:
    """Servicio principal de cámara"""
    
    async def capture_photo(
        self, 
        settings: Optional[CaptureSettings] = None
    ) -> PhotoResult:
        """Capturar foto con configuraciones específicas"""
        
    async def start_preview(self) -> None:
        """Iniciar vista previa de cámara"""
        
    async def stop_preview(self) -> None:
        """Detener vista previa de cámara"""
        
    def set_camera_setting(self, key: str, value: Any) -> None:
        """Establecer configuración de cámara"""
        
    def get_camera_setting(self, key: str) -> Any:
        """Obtener configuración de cámara"""
```

#### Configuraciones de Captura
```python
@dataclass
class CaptureSettings:
    """Configuraciones para captura de foto"""
    resolution: Tuple[int, int] = (1920, 1080)
    quality: int = 85
    format: str = "JPEG"
    iso: Optional[int] = None
    exposure: Optional[float] = None
    white_balance: str = "auto"
    
    def validate(self) -> None:
        """Validar configuraciones"""
        if not (10 <= self.quality <= 100):
            raise ValueError("Calidad debe estar entre 10-100")
```

### API de Sincronización

#### SyncService
```python
class SyncService:
    """Servicio de sincronización con la nube"""
    
    async def sync_photo(
        self, 
        photo_path: Path, 
        priority: int = 1
    ) -> SyncResult:
        """Sincronizar foto específica"""
        
    async def sync_all_photos(self) -> List[SyncResult]:
        """Sincronizar todas las fotos pendientes"""
        
    def get_sync_status(self) -> SyncStatus:
        """Obtener estado actual de sincronización"""
        
    def pause_sync(self) -> None:
        """Pausar sincronización"""
        
    def resume_sync(self) -> None:
        """Reanudar sincronización"""
```

#### Estados de Sincronización
```python
class SyncStatus(Enum):
    """Estados de sincronización"""
    IDLE = "idle"
    SYNCING = "syncing"
    PAUSED = "paused"
    ERROR = "error"
    
@dataclass
class SyncResult:
    """Resultado de operación de sincronización"""
    success: bool
    photo_path: Path
    upload_time: Optional[datetime]
    error_message: Optional[str] = None
```

### API de Configuración

#### Settings System
```python
class Settings:
    """Sistema de configuración global"""
    
    def get(self, key: str, default: Any = None) -> Any:
        """Obtener valor de configuración"""
        
    def set(self, key: str, value: Any) -> None:
        """Establecer valor de configuración"""
        
    def subscribe(self, key: str, callback: Callable) -> None:
        """Suscribirse a cambios de configuración"""
        
    def save(self) -> None:
        """Guardar configuración a disco"""
        
    def reset_to_defaults(self) -> None:
        """Restablecer a configuraciones por defecto"""
```

### API de Eventos

#### Event Bus
```python
class EventBus:
    """Bus de eventos para comunicación entre componentes"""
    
    def subscribe(
        self, 
        event_type: str, 
        callback: Callable[[Any], None]
    ) -> None:
        """Suscribirse a tipo de evento"""
        
    def unsubscribe(
        self, 
        event_type: str, 
        callback: Callable[[Any], None]
    ) -> None:
        """Desuscribirse de tipo de evento"""
        
    def publish(self, event_type: str, data: Any = None) -> None:
        """Publicar evento"""
```

#### Tipos de Eventos Estándar
```python
class EventTypes:
    """Tipos de eventos estándar del sistema"""
    
    # Eventos de cámara
    PHOTO_CAPTURED = "camera.photo_captured"
    PREVIEW_STARTED = "camera.preview_started"
    PREVIEW_STOPPED = "camera.preview_stopped"
    
    # Eventos de sincronización
    SYNC_STARTED = "sync.started"
    SYNC_COMPLETED = "sync.completed"
    SYNC_FAILED = "sync.failed"
    
    # Eventos de sistema
    SYSTEM_STARTED = "system.started"
    SYSTEM_STOPPING = "system.stopping"
    LOW_STORAGE = "system.low_storage"
```

## Pruebas

### Configuración de Pruebas

#### Estructura de Pruebas
```
tests/
├── unit/                    # Pruebas unitarias
│   ├── test_camera_service.py
│   ├── test_sync_service.py
│   └── test_settings.py
├── integration/             # Pruebas de integración
│   ├── test_camera_integration.py
│   └── test_sync_integration.py
├── e2e/                    # Pruebas end-to-end
│   └── test_full_workflow.py
├── fixtures/               # Datos de prueba
│   ├── test_photos/
│   └── test_configs/
└── conftest.py             # Configuración de pytest
```

#### Configuración pytest
```python
# conftest.py
import pytest
from pathlib import Path
from unittest.mock import Mock

@pytest.fixture
def temp_storage(tmp_path):
    """Directorio temporal para almacenamiento de pruebas"""
    storage_path = tmp_path / "test_photos"
    storage_path.mkdir()
    return storage_path

@pytest.fixture
def mock_camera():
    """Mock del hardware de cámara"""
    camera = Mock()
    camera.capture.return_value = b"fake_image_data"
    return camera

@pytest.fixture
def sample_photo_data():
    """Datos de foto de muestra para pruebas"""
    return {
        'data': b"fake_jpeg_data",
        'metadata': {
            'timestamp': '2024-01-01T12:00:00Z',
            'resolution': (1920, 1080),
            'iso': 100
        }
    }
```

### Pruebas Unitarias

#### Ejemplo: Test de Servicio de Cámara
```python
import pytest
from unittest.mock import Mock, patch
from src.camera.camera_service import CameraService
from src.camera.camera_settings import CaptureSettings

class TestCameraService:
    """Pruebas para CameraService"""
    
    @pytest.fixture
    def camera_service(self, mock_camera):
        """Configurar servicio de cámara con mock"""
        with patch('src.camera.camera_service.LibCameraBackend') as mock_backend:
            mock_backend.return_value = mock_camera
            return CameraService()
    
    @pytest.mark.asyncio
    async def test_capture_photo_success(self, camera_service, mock_camera):
        """Test captura exitosa de foto"""
        # Configurar mock
        mock_camera.capture.return_value = "/path/to/photo.jpg"
        
        # Ejecutar
        result = await camera_service.capture_photo()
        
        # Verificar
        assert result == "/path/to/photo.jpg"
        mock_camera.capture.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_capture_photo_with_settings(self, camera_service, mock_camera):
        """Test captura con configuraciones personalizadas"""
        # Configurar
        settings = CaptureSettings(
            resolution=(3840, 2160),
            quality=95,
            iso=200
        )
        
        # Ejecutar
        await camera_service.capture_photo(settings)
        
        # Verificar que las configuraciones se aplicaron
        mock_camera.apply_settings.assert_called_with(settings)
        mock_camera.capture.assert_called_once()
    
    def test_set_camera_setting(self, camera_service):
        """Test establecer configuración de cámara"""
        # Ejecutar
        camera_service.set_camera_setting('iso', 400)
        
        # Verificar
        assert camera_service.get_camera_setting('iso') == 400
```

#### Ejemplo: Test de Servicio de Sincronización
```python
import pytest
from unittest.mock import Mock, AsyncMock, patch
from src.sync.sync_service import SyncService
from src.sync.google_photos import GooglePhotosProvider

class TestSyncService:
    """Pruebas para SyncService"""
    
    @pytest.fixture
    def sync_service(self):
        """Configurar servicio de sincronización"""
        with patch('src.sync.sync_service.GooglePhotosProvider') as mock_provider:
            mock_provider.return_value.upload = AsyncMock(return_value=True)
            return SyncService()
    
    @pytest.mark.asyncio
    async def test_sync_photo_success(self, sync_service, temp_storage):
        """Test sincronización exitosa de foto"""
        # Crear archivo de prueba
        test_photo = temp_storage / "test.jpg"
        test_photo.write_bytes(b"fake_image_data")
        
        # Ejecutar
        result = await sync_service.sync_photo(test_photo)
        
        # Verificar
        assert result.success is True
        assert result.photo_path == test_photo
    
    @pytest.mark.asyncio
    async def test_sync_photo_failure(self, sync_service, temp_storage):
        """Test fallo de sincronización"""
        # Configurar fallo
        test_photo = temp_storage / "test.jpg"
        test_photo.write_bytes(b"fake_image_data")
        
        with patch.object(sync_service.provider, 'upload', side_effect=Exception("Network error")):
            # Ejecutar
            result = await sync_service.sync_photo(test_photo)
            
            # Verificar
            assert result.success is False
            assert "Network error" in result.error_message
```

### Pruebas de Integración

#### Ejemplo: Test de Flujo de Captura y Sincronización
```python
import pytest
from src.main import ASZCamApp

@pytest.mark.integration
class TestCameraSyncIntegration:
    """Pruebas de integración cámara-sincronización"""
    
    @pytest.fixture
    async def app(self, temp_storage):
        """Configurar aplicación completa"""
        app = ASZCamApp()
        await app.initialize_test_mode(storage_path=temp_storage)
        yield app
        await app.shutdown()
    
    @pytest.mark.asyncio
    async def test_capture_and_sync_workflow(self, app):
        """Test flujo completo de captura y sincronización"""
        # Capturar foto
        photo_path = await app.camera_service.capture_photo()
        assert photo_path.exists()
        
        # Verificar que se añadió a cola de sincronización
        sync_queue = app.sync_service.get_queue()
        assert photo_path in [item.path for item in sync_queue]
        
        # Ejecutar sincronización
        result = await app.sync_service.sync_all_photos()
        assert all(r.success for r in result)
```

### Pruebas End-to-End

#### Ejemplo: Test de UI Completa
```python
import pytest
from unittest.mock import patch
from PyQt6.QtTest import QTest
from PyQt6.QtCore import Qt
from src.ui.main_window import MainWindow

@pytest.mark.e2e
class TestMainWindowE2E:
    """Pruebas end-to-end de ventana principal"""
    
    @pytest.fixture
    def main_window(self, qtbot):
        """Configurar ventana principal para pruebas"""
        with patch('src.camera.camera_service.CameraService'):
            window = MainWindow()
            qtbot.addWidget(window)
            return window
    
    def test_capture_button_workflow(self, main_window, qtbot):
        """Test flujo completo de botón de captura"""
        # Encontrar botón de captura
        capture_button = main_window.findChild(QPushButton, "capture_button")
        assert capture_button is not None
        
        # Simular clic
        QTest.mouseClick(capture_button, Qt.LeftButton)
        
        # Verificar que se muestra confirmación
        qtbot.waitUntil(lambda: main_window.status_bar.currentMessage() == "Foto capturada")
```

### Ejecutar Pruebas

```bash
# Todas las pruebas
pytest

# Solo pruebas unitarias
pytest tests/unit/

# Con cobertura
pytest --cov=src --cov-report=html

# Modo watch para desarrollo
pytest-watch

# Pruebas específicas
pytest tests/unit/test_camera_service.py::TestCameraService::test_capture_photo_success

# Pruebas marcadas
pytest -m integration
pytest -m "not e2e"  # Excluir pruebas e2e
```

## Guías de Contribución

### Proceso de Contribución

#### 1. Configurar Entorno
```bash
# Fork del repositorio en GitHub
git clone https://github.com/your-username/ASZ-Cam-OS.git
cd ASZ-Cam-OS

# Agregar upstream remote
git remote add upstream https://github.com/mynameisrober/ASZ-Cam-OS.git

# Configurar entorno de desarrollo
./scripts/setup_dev.sh
```

#### 2. Crear Issue
- **Bug Reports**: Usar template de bug report
- **Feature Requests**: Usar template de feature request  
- **Documentación**: Marcar con label "documentation"
- **Discusión**: Usar GitHub Discussions para preguntas

#### 3. Crear Rama de Trabajo
```bash
git checkout develop
git pull upstream develop
git checkout -b feature/mi-nueva-caracteristica
```

#### 4. Desarrollar
- **TDD**: Escribir pruebas primero cuando sea posible
- **Commits pequeños**: Commits frecuentes y enfocados
- **Documentación**: Actualizar docs cuando sea necesario
- **Linting**: Ejecutar linters antes de commit

#### 5. Pull Request
- **Descripción clara**: Explicar qué, por qué, cómo
- **Testing**: Incluir evidencia de pruebas
- **Screenshots**: Para cambios de UI
- **Breaking Changes**: Documentar cambios que rompen compatibilidad

### Estándares de Código

#### Revisión de Código
- **Funcionalidad**: ¿El código hace lo que debe hacer?
- **Legibilidad**: ¿Es fácil de entender?
- **Performance**: ¿Hay problemas de rendimiento?
- **Seguridad**: ¿Hay vulnerabilidades de seguridad?
- **Tests**: ¿Están cubiertos todos los casos importantes?

#### Criterios de Aceptación
- [ ] Todas las pruebas pasan
- [ ] Cobertura de código >= 80%
- [ ] Linters pasan sin errores
- [ ] Documentación actualizada
- [ ] Reviewed y aprobado por maintainer

### Guías Específicas

#### Agregando Nuevas Características
1. **Discutir primero**: Crear issue para discutir diseño
2. **Diseño de API**: Definir interfaces claramente
3. **Tests**: Escribir tests comprensivos
4. **Documentación**: Actualizar user guide y developer guide
5. **Backward Compatibility**: Mantener compatibilidad cuando sea posible

#### Corrigiendo Bugs
1. **Reproducir**: Crear test que reproduzca el bug
2. **Identificar causa raíz**: Entender por qué ocurre
3. **Fix mínimo**: Cambio mínimo que soluciona el problema
4. **Test regression**: Asegurar que el fix funciona
5. **Documentar**: Actualizar troubleshooting guide si es necesario

#### Mejorando Documentación
1. **Identificar gaps**: ¿Qué está mal documentado?
2. **User perspective**: Escribir desde perspectiva del usuario
3. **Ejemplos**: Incluir ejemplos prácticos
4. **Screenshots**: Usar screenshots para cambios de UI
5. **Links**: Mantener links actualizados

## Implementación

### Preparación de Release

#### Versionado Semántico
- **Major (X.0.0)**: Cambios que rompen compatibilidad
- **Minor (x.Y.0)**: Nuevas características compatibles  
- **Patch (x.y.Z)**: Bug fixes compatibles

#### Proceso de Release
```bash
# 1. Crear rama de release
git checkout develop
git checkout -b release/1.2.0

# 2. Actualizar versión
echo "1.2.0" > VERSION
git add VERSION
git commit -m "bump: version 1.2.0"

# 3. Ejecutar tests completos
pytest tests/
./scripts/test_on_pi.sh

# 4. Actualizar changelog
# Editar CHANGELOG.md

# 5. Merge a main
git checkout main
git merge release/1.2.0
git tag v1.2.0

# 6. Push
git push origin main --tags
```

#### Construcción de Distribución
```bash
# Crear imagen del sistema
./scripts/build_image.sh

# Crear packages de instalación
./scripts/build_packages.sh

# Subir releases a GitHub
gh release create v1.2.0 \
  --title "ASZ Cam OS v1.2.0" \
  --notes-file RELEASE_NOTES.md \
  dist/*
```

### Implementación de Producción

#### Instalación Automatizada
```bash
# Script de instalación en una línea
curl -fsSL https://raw.githubusercontent.com/mynameisrober/ASZ-Cam-OS/main/scripts/install.sh | sudo bash
```

#### Configuración de CI/CD
```yaml
# .github/workflows/ci.yml
name: CI/CD Pipeline

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    - uses: actions/setup-python@v4
      with:
        python-version: '3.9'
    - run: pip install -r requirements-dev.txt
    - run: pytest --cov=src
    - run: black --check src/
    - run: flake8 src/
    - run: mypy src/

  build:
    needs: test
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    steps:
    - uses: actions/checkout@v3
    - run: ./scripts/build_image.sh
    - uses: actions/upload-artifact@v3
      with:
        name: disk-image
        path: dist/aszcam-*.img
```

#### Monitoreo y Logging
```python
# src/utils/monitoring.py
import logging
from typing import Dict, Any
import psutil
from datetime import datetime

class SystemMonitor:
    """Monitor de sistema para métricas de rendimiento"""
    
    def get_system_metrics(self) -> Dict[str, Any]:
        """Obtener métricas del sistema"""
        return {
            'cpu_percent': psutil.cpu_percent(),
            'memory_percent': psutil.virtual_memory().percent,
            'disk_usage': psutil.disk_usage('/').percent,
            'temperature': self._get_cpu_temperature(),
            'timestamp': datetime.utcnow().isoformat()
        }
    
    def _get_cpu_temperature(self) -> float:
        """Obtener temperatura de CPU (Raspberry Pi)"""
        try:
            with open('/sys/class/thermal/thermal_zone0/temp') as f:
                temp = int(f.read()) / 1000.0
                return temp
        except:
            return 0.0
```

### Construcción de Documentación

```bash
# Construir documentación
cd docs/
make html

# Servir documentación localmente
python -m http.server 8000
```

---

Esta guía del desarrollador proporciona la base para contribuir a ASZ Cam OS. Para preguntas o aclaraciones, por favor abre un issue o discusión en el repositorio de GitHub.