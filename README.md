# ASZ Cam OS

Sistema operativo personalizado para cámara ASZ Cam basado en Raspberry Pi con libcamera/OpenCV.

## Descripción

ASZ Cam OS es un sistema operativo completo y personalizado diseñado específicamente para la cámara "ASZ Cam" construida sobre Raspberry Pi. El sistema ofrece una experiencia de cámara minimalista y eficiente con sincronización automática a Google Photos.

## Características

### 🎯 Interfaz Minimalista
- Diseño limpio en blanco y grises exclusivamente
- Tipografía personalizada SFCamera
- Auto-inicio directo a la aplicación de cámara
- Navegación intuitiva por menús

### 📷 Funcionalidades de Cámara
- Captura de fotos de alta calidad con libcamera
- Preview en tiempo real
- Control automático de exposición y enfoque
- Soporte para resoluciones múltiples
- Fallback a OpenCV para desarrollo

### 🔄 Sincronización Automática
- Integración con Google Photos API
- Subida automática de fotos capturadas
- Gestión de reintentos en caso de fallos de red
- Respeto total a la privacidad del usuario

### 🎛️ Módulos Principales
- **Cámara**: Pantalla principal de captura
- **Galería**: Visualización de fotos capturadas
- **Recuerdos**: "Este día el año pasado" y momentos históricos
- **Ajustes**: Configuración del sistema y cámara

## Requisitos del Sistema

### Hardware
- Raspberry Pi 4B (recomendado) o Raspberry Pi 3B+
- Cámara oficial de Raspberry Pi v2 o v3
- Tarjeta microSD de al menos 32GB (Clase 10)
- Fuente de alimentación oficial
- Display HDMI (opcional para configuración)

### Software Base
- Raspberry Pi OS Lite (Bookworm)
- Python 3.11+
- libcamera-apps
- Qt6/PyQt6

## Instalación

### 1. Preparación de la Raspberry Pi

```bash
# Actualizar el sistema
sudo apt update && sudo apt upgrade -y

# Habilitar la cámara
sudo raspi-config
# Navegar a: Interface Options > Camera > Enable

# Reiniciar
sudo reboot
```

### 2. Instalación Automática

```bash
# Clonar el repositorio
git clone https://github.com/mynameisrober/ASZ-Cam-OS.git
cd ASZ-Cam-OS

# Ejecutar el script de instalación
chmod +x scripts/install.sh
./scripts/install.sh
```

### 3. Configuración Manual (Opcional)

```bash
# Crear directorio de instalación
sudo mkdir -p /opt/aszcam
sudo chown pi:pi /opt/aszcam

# Copiar archivos
cp -r . /opt/aszcam/

# Configurar entorno Python
cd /opt/aszcam
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Configurar servicio systemd
sudo cp systemd/aszcam.service /etc/systemd/system/
sudo systemctl enable aszcam
sudo systemctl start aszcam
```

## Configuración

### Archivo de Configuración Principal

El sistema utiliza un archivo de configuración YAML localizado en:
```
~/.config/aszcam/settings.yaml
```

### Configuración de Cámara

```yaml
camera:
  default_resolution: [1920, 1080]
  default_format: "JPEG"
  quality: 95
  auto_focus: true
  auto_exposure: true
  preview_enabled: true
```

### Configuración de Sincronización

```yaml
sync:
  enabled: true
  auto_sync: true
  sync_interval: 300
  album_name: "ASZ Cam Photos"
```

## Uso

### Navegación

- **Tecla 1**: Vista de cámara
- **Tecla 2**: Galería de fotos
- **Tecla 3**: Recuerdos
- **Tecla 4**: Configuración
- **Barra espaciadora**: Capturar foto
- **ESC**: Salir de pantalla completa
- **F11**: Alternar pantalla completa

### Captura de Fotos

1. El sistema inicia automáticamente en la vista de cámara
2. Presiona el botón de captura circular o la barra espaciadora
3. La foto se guarda automáticamente en `/home/pi/ASZCam/Photos/`
4. Si está habilitada, la sincronización con Google Photos ocurre automáticamente

### Configuración de Google Photos

1. Ir a **Configuración** > **Sincronización**
2. Habilitar sincronización con Google Photos
3. Seguir el flujo de autenticación OAuth2
4. Las fotos se subirán automáticamente al álbum configurado

## Desarrollo

### Estructura del Proyecto

```
asz-cam-os/
├── src/                    # Código fuente principal
│   ├── core/              # Módulos core del sistema
│   ├── ui/                # Interfaz de usuario
│   ├── camera/            # Módulo de cámara
│   ├── sync/              # Sincronización Google Photos
│   └── config/            # Configuración del sistema
├── assets/                # Recursos (fonts, icons, themes)
├── scripts/               # Scripts de instalación
├── docs/                  # Documentación
├── systemd/               # Archivos de servicio
├── configs/               # Configuraciones del sistema
└── requirements.txt       # Dependencias Python
```

### Ejecutar Tests

```bash
# Tests del sistema (sin GUI)
python3 test_system.py

# Tests con cámara real (en Raspberry Pi)
cd src && python3 main.py
```

### Desarrollo Local

```bash
# Instalar dependencias de desarrollo
pip install -r requirements.txt

# Ejecutar en modo desarrollo
cd src && python3 main.py
```

## Arquitectura Técnica

### Stack Tecnológico

- **Backend**: Python 3.11+
- **GUI**: PyQt6 con tema personalizado
- **Cámara**: libcamera-apps + OpenCV fallback
- **Sincronización**: Google Photos API
- **Sistema**: systemd service
- **Configuración**: YAML + dataclasses

### Módulos Principales

- **SystemManager**: Gestión del ciclo de vida del sistema
- **CameraService**: Control de alto nivel de la cámara
- **LibCameraBackend**: Interface con libcamera/OpenCV
- **SyncService**: Sincronización con servicios en la nube
- **MainWindow**: Ventana principal con navegación

## Troubleshooting

### Problemas Comunes

**La cámara no funciona**
```bash
# Verificar que la cámara está conectada
libcamera-hello --list-cameras

# Verificar permisos
sudo usermod -a -G video pi
```

**El servicio no inicia**
```bash
# Verificar estado del servicio
systemctl status aszcam

# Ver logs del servicio
journalctl -u aszcam -f
```

**Problemas de sincronización**
```bash
# Verificar conectividad
ping google.com

# Verificar credenciales
ls ~/.config/aszcam/
```

### Logs del Sistema

Los logs se encuentran en:
- Servicio systemd: `journalctl -u aszcam`
- Aplicación: `/home/pi/ASZCam/aszcam.log`
- Sistema: `/var/log/syslog`

## Contribución

Las contribuciones son bienvenidas. Por favor:

1. Fork el repositorio
2. Crear una rama para tu feature: `git checkout -b feature/nueva-funcionalidad`
3. Hacer commit de tus cambios: `git commit -am 'Añadir nueva funcionalidad'`
4. Push a la rama: `git push origin feature/nueva-funcionalidad`
5. Crear un Pull Request

## Licencia

Este proyecto está licenciado bajo la Licencia MIT. Ver el archivo [LICENSE](LICENSE) para más detalles.

## Créditos

- **Tipografía**: SFCamera de San Francisco family
- **Inspiración**: Aplicaciones de cámara modernas minimalistas
- **Tecnologías**: Raspberry Pi Foundation, Qt Project, OpenCV, Google

## Soporte

Para soporte técnico:
- Crear un issue en GitHub
- Documentación completa en `/docs/`
- Wiki del proyecto: [GitHub Wiki](https://github.com/mynameisrober/ASZ-Cam-OS/wiki)

---

**ASZ Cam OS v1.0.0** - Sistema operativo personalizado para cámara ASZ Cam