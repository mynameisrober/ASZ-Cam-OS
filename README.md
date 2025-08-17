# ASZ Cam OS
Sistema Operativo Personalizado para Cámara ASZ Cam

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Platform](https://img.shields.io/badge/Platform-Raspberry%20Pi%204B-red.svg)](https://www.raspberrypi.org/)
[![Python](https://img.shields.io/badge/Python-3.8%2B-blue.svg)](https://www.python.org/)

## Descripción General

ASZ Cam OS es un sistema operativo personalizado diseñado específicamente para la cámara "ASZ Cam", construido sobre Raspberry Pi con un enfoque en facilidad de personalización, estabilidad y sincronización automática con Google Photos.

### Características Principales

- **🚀 Inicio Rápido**: Boot completo en menos de 10 segundos
- **📷 Cámara Automática**: La aplicación de cámara se inicia automáticamente al encender
- **🎨 Diseño Minimalista**: Interfaz limpia con paleta exclusiva de blancos y grises
- **📸 4 Secciones Principales**: Cámara, Ajustes, Fotos, Recuerdos
- **☁️ Sync Automática**: Subida automática a Google Photos
- **💭 Recuerdos**: Función "Este día el año pasado" y más
- **🔧 Altamente Personalizable**: Sistema optimizado para modificaciones

## Arquitectura del Sistema

```
ASZ Cam OS
├── 🖥️ Buildroot Linux (Custom)
├── 📱 PyQt5 Application
├── 📹 libcamera + OpenCV
├── ☁️ Google Photos Integration
└── 🎛️ Raspberry Pi Hardware
```

## Estructura del Proyecto

```
asz-cam-os/
├── 📁 buildroot/              # Configuración del SO base
├── 📁 src/
│   ├── 📁 camera/             # Módulo de cámara
│   ├── 📁 ui/                 # Interfaz de usuario
│   │   ├── main_window.py     # Ventana principal
│   │   ├── camera_view.py     # Vista de cámara
│   │   ├── settings_view.py   # Configuración
│   │   ├── photos_view.py     # Galería de fotos
│   │   ├── memories_view.py   # Recuerdos
│   │   └── theme.py          # Sistema de temas
│   ├── 📁 sync/              # Sincronización Google Photos
│   ├── 📁 storage/           # Gestión de almacenamiento
│   └── 📁 system/            # Servicios del sistema
├── 📁 assets/
│   ├── 📁 fonts/             # Tipografía SFCamera
│   ├── 📁 themes/            # Temas de color
│   └── 📁 icons/             # Iconografía
├── 📁 configs/               # Configuraciones del sistema
├── 📁 scripts/               # Scripts de build y deploy
└── 📁 docs/                  # Documentación
```

## Instalación Rápida

### Para Raspberry Pi (Producción)

```bash
# 1. Clonar el repositorio
git clone https://github.com/mynameisrober/ASZ-Cam-OS.git
cd ASZ-Cam-OS

# 2. Compilar imagen del SO
./scripts/build.sh

# 3. Grabar a tarjeta SD
sudo dd if=build/buildroot-*/output/images/sdcard.img of=/dev/sdX bs=4M
```

### Para Desarrollo (Linux/Windows/Mac)

```bash
# 1. Instalar dependencias Python
pip install -r requirements.txt

# 2. Ejecutar en modo desarrollo
python3 scripts/dev_run.py
```

## Funcionalidades Implementadas

### ✅ Sistema Base
- [x] Estructura de directorios completa
- [x] Configuración buildroot personalizada
- [x] Scripts de compilación automatizados
- [x] Servicios systemd para inicio automático

### ✅ Interfaz de Usuario
- [x] Aplicación PyQt5 con navegación entre 4 secciones
- [x] Tema personalizado blanco/gris
- [x] Sistema de navegación intuitivo
- [x] Soporte para tipografía SFCamera

### ✅ Sistema de Cámara
- [x] Servicio de cámara con libcamera/OpenCV
- [x] Preview en tiempo real
- [x] Controles de cámara (ISO, exposición, brillo)
- [x] Captura de fotos con almacenamiento local
- [x] Modo simulación para desarrollo

### ✅ Galería de Fotos
- [x] Grid de miniaturas de fotos
- [x] Vista detallada de imágenes
- [x] Información de archivos
- [x] Eliminación de fotos individuales/masiva
- [x] Carga asíncrona de imágenes

### ✅ Sistema de Recuerdos
- [x] "Este día hace X años"
- [x] "Esta semana el año pasado"
- [x] Recuerdo de primera foto
- [x] Actividad reciente
- [x] Vista detallada de recuerdos

### ✅ Configuración
- [x] Ajustes de cámara (resolución, FPS, auto-ISO, etc.)
- [x] Configuración de sincronización Google Photos
- [x] Ajustes de pantalla
- [x] Configuración del sistema
- [x] Información detallada del sistema

### ✅ Sincronización Google Photos
- [x] Sistema de autenticación OAuth2
- [x] Cola de subidas con reintentos automáticos
- [x] Procesamiento en segundo plano
- [x] Manejo de errores y reconexión
- [x] Estado de sincronización visible

### ✅ Documentación
- [x] Guía de instalación completa
- [x] Especificaciones técnicas detalladas
- [x] Documentación de arquitectura
- [x] Scripts de desarrollo

## Requisitos del Sistema

### Hardware
- **Raspberry Pi 4B** (4GB RAM recomendado)
- **Tarjeta MicroSD** (32GB recomendado)
- **Cámara**: Raspberry Pi Camera Module o USB
- **Pantalla**: HDMI o DSI
- **Conexión WiFi** para sincronización

### Software
- **Buildroot 2023.11** para compilación
- **Python 3.8+** para desarrollo
- **PyQt5** para interfaz gráfica
- **libcamera** para sistema de cámara

## Criterios de Aceptación ✅

- [x] **Boot < 10 segundos**: Sistema optimizado para inicio rápido
- [x] **App auto-start**: Cámara se inicia automáticamente
- [x] **Tipografía SFCamera**: Integrada en sistema de temas
- [x] **Paleta blanco/gris**: Tema exclusivo implementado
- [x] **Sync Google Photos**: Integración completa con OAuth2
- [x] **4 secciones principales**: Cámara, Ajustes, Fotos, Recuerdos
- [x] **Sistema personalizable**: Estructura modular y configurable
- [x] **Funcionalidad recuerdos**: "Este día" y otras funciones implementadas

## Desarrollo

### Ejecutar en Modo Desarrollo

```bash
# Instalar dependencias
pip install -r requirements.txt

# Ejecutar aplicación (modo ventana)
python3 scripts/dev_run.py
```

### Compilar para Raspberry Pi

```bash
# Compilar imagen completa del SO
./scripts/build.sh

# La imagen resultante estará en:
# build/buildroot-*/output/images/
```

## Contribuir

1. Fork el repositorio
2. Crear rama de feature (`git checkout -b feature/nueva-funcionalidad`)
3. Commit cambios (`git commit -am 'Agregar nueva funcionalidad'`)
4. Push a la rama (`git push origin feature/nueva-funcionalidad`)
5. Crear Pull Request

## Licencia

Este proyecto está bajo la Licencia MIT - ver el archivo [LICENSE](LICENSE) para detalles.

## Soporte

Para reportar bugs o solicitar features, por favor usa el [sistema de issues de GitHub](https://github.com/mynameisrober/ASZ-Cam-OS/issues).

---

**ASZ Cam OS** - Sistema operativo personalizado para capturar y conservar tus momentos especiales 📸✨