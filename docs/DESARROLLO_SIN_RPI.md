# Desarrollo de ASZ Cam OS sin Raspberry Pi

Esta guía explica cómo configurar un entorno de desarrollo completo para ASZ Cam OS que funciona en cualquier sistema operativo (Linux, macOS, Windows) sin necesidad de hardware Raspberry Pi físico.

## Tabla de Contenidos

- [Visión General](#visión-general)
- [Configuración del Entorno](#configuración-del-entorno)
- [Componentes de Simulación](#componentes-de-simulación)
- [Ejecutar en Modo Desarrollo](#ejecutar-en-modo-desarrollo)
- [Testing](#testing)
- [Desarrollo con Docker](#desarrollo-con-docker)
- [Funcionalidades Disponibles](#funcionalidades-disponibles)
- [Solución de Problemas](#solución-de-problemas)

## Visión General

El entorno de desarrollo de ASZ Cam OS incluye:

- **Mock Camera**: Simulador realista de cámara libcamera
- **RPi Simulator**: Simulación completa de hardware Raspberry Pi
- **Testing Framework**: Suite de pruebas sin dependencias de hardware
- **Development Scripts**: Scripts automatizados para configuración y ejecución
- **Cross-Platform Support**: Funciona en Linux, macOS y Windows

### Arquitectura del Simulador

```
ASZ Cam OS (Dev Mode)
├── Mock LibCamera
│   ├── Generación de imágenes realistas
│   ├── Simulación de preview en vivo
│   ├── Configuraciones de cámara
│   └── Assets de muestra
├── RPi Simulator
│   ├── GPIO simulation
│   ├── System information
│   ├── Hardware detection
│   └── Service management
└── Testing Framework
    ├── Unit tests
    ├── Integration tests
    ├── Fixtures y mocks
    └── CI/CD support
```

## Configuración del Entorno

### Configuración Automática

La forma más fácil de configurar el entorno de desarrollo es usar el script automatizado:

```bash
# Clonar el repositorio
git clone https://github.com/mynameisrober/ASZ-Cam-OS.git
cd ASZ-Cam-OS

# Ejecutar configuración automática
./scripts/setup_dev_environment.sh
```

Este script:
- Detecta automáticamente tu sistema operativo
- Instala dependencias del sistema necesarias
- Crea un entorno virtual Python
- Instala todas las dependencias Python
- Configura directorios de desarrollo
- Crea archivos de configuración para VSCode
- Genera assets de muestra para la cámara mock

### Configuración Manual

Si prefieres configurar manualmente o el script automático falla:

#### 1. Dependencias del Sistema

**Ubuntu/Debian:**
```bash
sudo apt-get update
sudo apt-get install -y \
    python3-dev python3-venv python3-pip \
    libgl1-mesa-glx libglib2.0-0 \
    libxcb-xinerama0 libfontconfig1 \
    libxkbcommon-x11-0 libdbus-1-3 \
    git curl build-essential pkg-config
```

**macOS (con Homebrew):**
```bash
brew install python@3.9 git
```

**Windows:**
- Instalar Python 3.9+ desde python.org
- Instalar Git desde git-scm.com
- Instalar Visual Studio Build Tools

#### 2. Entorno Virtual Python

```bash
# Crear entorno virtual
python3 -m venv aszcam-dev

# Activar entorno virtual
# Linux/macOS:
source aszcam-dev/bin/activate

# Windows:
aszcam-dev\Scripts\activate

# Instalar dependencias
pip install --upgrade pip
pip install -r requirements.txt
```

#### 3. Crear Estructura de Directorios

```bash
mkdir -p tests/{unit,integration,e2e,fixtures}
mkdir -p assets/mock_images
mkdir -p logs
mkdir -p dev_photos
mkdir -p temp
```

## Componentes de Simulación

### Mock Camera (camera/mock_libcamera.py)

El simulador de cámara proporciona:

- **Generación realista de imágenes**: Crea imágenes con patrones reconocibles
- **Preview en vivo**: Stream de frames con información en tiempo real
- **Configuraciones de cámara**: ISO, exposición, resolución, calidad
- **Assets de muestra**: Imágenes predefinidas para testing consistente

```python
from camera.mock_libcamera import MockLibCamera

# Inicializar cámara mock
camera = MockLibCamera()
camera.initialize()

# Iniciar preview
camera.start_preview()

# Capturar foto
photo = camera.capture_photo(resolution=(1920, 1080), quality=95)

# Obtener información
info = camera.get_camera_info()
print(f"Camera: {info['model']}")
```

### RPi Simulator (core/rpi_simulator.py)

El simulador de Raspberry Pi incluye:

- **GPIO Simulation**: Control completo de pines GPIO
- **System Information**: CPU, memoria, temperatura, voltaje
- **Hardware Detection**: Simulación de componentes de hardware
- **Service Management**: Estados de servicios del sistema

```python
from core.rpi_simulator import RPiSimulator

# Crear simulador
rpi = RPiSimulator()

# Obtener información del sistema
info = rpi.get_system_info()
print(f"Model: {info['model']}")
print(f"Temperature: {info['cpu_temp_c']}°C")

# Simular GPIO
rpi.gpio_setup(18, 'OUT')
rpi.gpio_output(18, True)

# Obtener información de hardware
hardware = rpi.detect_hardware()
```

## Ejecutar en Modo Desarrollo

### Usar el Script de Desarrollo

```bash
# Ejecutar con configuración por defecto
python scripts/run_dev_mode.py

# Ejecutar con opciones específicas
python scripts/run_dev_mode.py --test-mode --log-level DEBUG

# Solo probar el entorno sin ejecutar la aplicación
python scripts/run_dev_mode.py --test-env-only

# Ayuda con todas las opciones
python scripts/run_dev_mode.py --help
```

### Opciones del Script de Desarrollo

- `--mock-camera`: Usar cámara simulada (por defecto: True)
- `--no-mock-camera`: Usar cámara real si está disponible
- `--mock-rpi`: Usar simulador RPi (por defecto: True)
- `--windowed`: Ejecutar en modo ventana (por defecto: True)
- `--fullscreen`: Ejecutar en pantalla completa
- `--test-mode`: Habilitar depuración adicional
- `--log-level`: Nivel de logging (DEBUG, INFO, WARNING, ERROR)

### Variables de Entorno

El modo desarrollo configura automáticamente estas variables:

```bash
ASZ_DEV_MODE=true
ASZ_SIMULATION_MODE=true
ASZ_MOCK_CAMERA=true
ASZ_MOCK_RPI=true
ASZ_WINDOWED_MODE=true
ASZ_DISABLE_FULLSCREEN=true
ASZ_DISABLE_SYSTEMD=true
ASZ_DISABLE_GPIO=true
```

### Ejecución Manual

También puedes ejecutar manualmente configurando las variables:

```bash
# Configurar variables de entorno
export ASZ_DEV_MODE=true
export ASZ_SIMULATION_MODE=true
export ASZ_MOCK_CAMERA=true

# Ejecutar aplicación
python src/main.py --dev
```

## Testing

### Estructura de Pruebas

```
tests/
├── conftest.py              # Configuración pytest y fixtures
├── unit/                    # Pruebas unitarias
│   ├── test_mock_camera.py
│   ├── test_rpi_simulator.py
│   └── test_system_manager.py
├── integration/             # Pruebas de integración
│   ├── test_camera_integration.py
│   └── test_ui_integration.py
├── e2e/                     # Pruebas end-to-end
│   └── test_full_workflow.py
└── fixtures/                # Datos de prueba
    ├── test_images/
    └── sample_configs/
```

### Ejecutar Pruebas

```bash
# Activar entorno virtual
source aszcam-dev/bin/activate

# Ejecutar todas las pruebas
pytest

# Ejecutar solo pruebas unitarias
pytest tests/unit/

# Ejecutar con cobertura
pytest --cov=src --cov-report=html

# Ejecutar pruebas específicas
pytest tests/unit/test_mock_camera.py -v

# Ejecutar pruebas por marcadores
pytest -m unit          # Solo pruebas unitarias
pytest -m integration   # Solo pruebas de integración
pytest -m "not slow"    # Excluir pruebas lentas
```

### Fixtures Disponibles

- `mock_camera`: Instancia de MockLibCamera inicializada
- `mock_rpi_simulator`: Instancia de RPiSimulator
- `temp_storage`: Directorio temporal para almacenamiento
- `mock_camera_frame`: Frame de cámara de prueba
- `qt_app`: Aplicación Qt para pruebas GUI
- `capture_logs`: Capturador de logs configurado

### Ejemplo de Prueba

```python
def test_camera_capture(mock_camera):
    """Test camera photo capture."""
    # Capturar foto
    photo = mock_camera.capture_photo()
    
    # Verificar resultado
    assert photo is not None
    assert isinstance(photo, np.ndarray)
    assert len(photo.shape) == 3  # Height, Width, Channels

def test_rpi_gpio(mock_rpi_simulator):
    """Test GPIO simulation."""
    # Configurar pin
    assert mock_rpi_simulator.gpio_setup(18, 'OUT') == True
    
    # Establecer valor
    assert mock_rpi_simulator.gpio_output(18, True) == True
    
    # Verificar estado
    state = mock_rpi_simulator.get_gpio_state()
    assert state[18]['value'] == True
```

## Desarrollo con Docker

### Dockerfile de Desarrollo

```dockerfile
# docker/Dockerfile.dev
FROM python:3.11-slim

# Instalar dependencias del sistema
RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libxcb-xinerama0 \
    libfontconfig1 \
    libxkbcommon-x11-0 \
    libdbus-1-3 \
    git \
    && rm -rf /var/lib/apt/lists/*

# Crear directorio de trabajo
WORKDIR /app

# Copiar código fuente
COPY . .

# Instalar dependencias Python
RUN pip install -r requirements.txt

# Configurar variables de entorno de desarrollo
ENV ASZ_DEV_MODE=true
ENV ASZ_SIMULATION_MODE=true
ENV ASZ_MOCK_CAMERA=true
ENV ASZ_MOCK_RPI=true

# Comando por defecto
CMD ["python", "scripts/run_dev_mode.py", "--windowed"]
```

### Docker Compose para Desarrollo

```yaml
# docker-compose.dev.yml
version: '3.8'

services:
  aszcam-dev:
    build:
      context: .
      dockerfile: docker/Dockerfile.dev
    volumes:
      - .:/app
      - /tmp/.X11-unix:/tmp/.X11-unix
    environment:
      - DISPLAY=${DISPLAY}
      - ASZ_DEV_MODE=true
    network_mode: host
    stdin_open: true
    tty: true
```

### Ejecutar con Docker

```bash
# Construir imagen de desarrollo
docker build -f docker/Dockerfile.dev -t aszcam-dev .

# Ejecutar en modo desarrollo
docker run -it --rm \
    -v $(pwd):/app \
    -v /tmp/.X11-unix:/tmp/.X11-unix \
    -e DISPLAY=$DISPLAY \
    aszcam-dev

# Usar Docker Compose
docker-compose -f docker-compose.dev.yml up
```

## Funcionalidades Disponibles

### ✅ Completamente Funcional

- **Interfaz de Usuario**: GUI completa con PyQt6
- **Simulación de Cámara**: Captura de fotos y preview
- **Gestión de Fotos**: Almacenamiento y organización
- **Configuraciones**: Todas las configuraciones de cámara
- **Logging**: Sistema de logging completo
- **Testing**: Suite de pruebas completa

### ⚠️ Simulado/Mock

- **Hardware GPIO**: Simulado, no controla hardware real
- **Servicios del Sistema**: Estados simulados
- **Información del Sistema**: Datos simulados de RPi
- **Conectividad de Red**: Simulada para desarrollo

### ❌ No Disponible en Desarrollo

- **Sincronización con Google Photos**: Requiere configuración de API
- **Control de Hardware Real**: LEDs, ventiladores, etc.
- **Acceso a Hardware de Red**: WiFi, Bluetooth real
- **Servicios Systemd**: No ejecuta servicios reales

## Solución de Problemas

### Error: "No module named 'PyQt6'"

```bash
# Reinstalar PyQt6
pip uninstall PyQt6
pip install PyQt6

# En macOS, puede requerir:
brew install python-tk
```

### Error: "Cannot connect to X server"

En Linux, asegúrate de que DISPLAY esté configurado:

```bash
export DISPLAY=:0
```

Para WSL2 en Windows, instalar un servidor X como VcXsrv.

### Error: "libGL error"

En Linux sin GUI:

```bash
# Instalar dependencias GL
sudo apt-get install libgl1-mesa-glx libgl1-mesa-dri

# O usar software rendering
export LIBGL_ALWAYS_SOFTWARE=1
```

### Error: "Permission denied" en scripts

```bash
# Hacer ejecutables los scripts
chmod +x scripts/*.sh
chmod +x scripts/*.py
```

### Problemas de Importación

```bash
# Verificar que el entorno virtual esté activado
which python
# Debe mostrar la ruta del entorno virtual

# Verificar PYTHONPATH
echo $PYTHONPATH

# Ejecutar desde el directorio raíz del proyecto
cd /path/to/ASZ-Cam-OS
```

### Testing Failures

```bash
# Ejecutar un solo test para depurar
pytest tests/unit/test_mock_camera.py::test_mock_camera_initialization -v

# Verificar fixtures
pytest --fixtures tests/

# Limpiar cache de pytest
pytest --cache-clear
```

### Performance Issues

```bash
# Reducir resolución de cámara mock
export ASZ_MOCK_CAMERA_RESOLUTION="640x480"

# Reducir FPS de preview
export ASZ_MOCK_CAMERA_FPS="15"

# Deshabilitar preview para testing
export ASZ_DISABLE_PREVIEW="true"
```

## Desarrollo Avanzado

### Agregar Nuevos Mocks

1. **Crear nuevo módulo mock**:
```python
# src/hardware/mock_sensor.py
class MockSensor:
    def __init__(self):
        self.is_mock = True
    
    def read_data(self):
        return {"temperature": 25.5, "humidity": 60.0}
```

2. **Agregar al simulador**:
```python
# En rpi_simulator.py
from hardware.mock_sensor import MockSensor

class RPiSimulator:
    def __init__(self):
        # ... existing code ...
        self.sensor = MockSensor()
```

3. **Crear pruebas**:
```python
# tests/unit/test_mock_sensor.py
def test_sensor_reading(mock_rpi_simulator):
    data = mock_rpi_simulator.sensor.read_data()
    assert "temperature" in data
```

### Integración Continua

El entorno de desarrollo incluye configuración para CI/CD:

```yaml
# .github/workflows/dev-tests.yml
name: Development Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    - uses: actions/setup-python@v4
      with:
        python-version: '3.9'
    - run: pip install -r requirements.txt
    - run: pytest --cov=src
```

### Debugging con VSCode

Configuración incluida en `.vscode/launch.json`:

```json
{
    "name": "ASZ Cam OS (Development)",
    "type": "python",
    "request": "launch",
    "program": "${workspaceFolder}/src/main.py",
    "env": {
        "ASZ_DEV_MODE": "true"
    },
    "args": ["--dev"]
}
```

## Contribuir

Para contribuir al desarrollo:

1. **Fork del repositorio**
2. **Crear rama de feature**: `git checkout -b feature/nueva-funcionalidad`
3. **Ejecutar tests**: `pytest tests/`
4. **Commit cambios**: `git commit -m "Add: nueva funcionalidad"`
5. **Push a rama**: `git push origin feature/nueva-funcionalidad`
6. **Crear Pull Request**

### Estándares de Código

```bash
# Formatear código
black src/

# Verificar linting
flake8 src/

# Verificar tipos (si usas mypy)
mypy src/
```

---

¡Ahora tienes un entorno de desarrollo completo para ASZ Cam OS que funciona sin hardware Raspberry Pi! 🚀