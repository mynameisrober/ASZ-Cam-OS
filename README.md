# ASZ Cam OS

Sistema operativo personalizado optimizado específicamente para la cámara ASZ Cam, basado en Raspberry Pi con integración nativa de libcamera y OpenCV.

## 🚀 Características Principales

- **Sistema Base Optimizado**: SO minimalista sin servicios innecesarios
- **Integración Nativa**: libcamera y OpenCV integrados a nivel del sistema
- **Boot Rápido**: Tiempo de arranque menor a 15 segundos
- **Interfaz Dedicada**: UI/UX específica para cámara
- **Gestión de Recursos**: Optimización de memoria y CPU para procesamiento de imágenes
- **Conectividad**: WiFi, Bluetooth y servicios de red esenciales
- **Persistencia**: Sistema de archivos optimizado para fotografía

## 🏗️ Arquitectura del Sistema

### Servicios Principales
- **Camera Service**: Control principal de la cámara
- **Photo Manager**: Gestión y organización de fotografías
- **Cloud Sync Service**: Sincronización con servicios en la nube
- **Memory Service**: Función "Este día el año pasado"
- **Network Manager**: Gestión simplificada de conectividad
- **Update Service**: Sistema de actualizaciones OTA

### Estructura del Sistema de Archivos
```
/opt/aszcam/          # Aplicaciones principales
├── bin/              # Ejecutables del sistema ASZ Cam
├── lib/              # Bibliotecas específicas
├── config/           # Configuraciones del sistema
├── ui/               # Interfaz de usuario
└── plugins/          # Plugins y extensiones

/var/aszcam/          # Datos variables
├── photos/           # Almacén de fotografías
├── cache/            # Cache temporal
├── logs/             # Logs del sistema
└── sync/             # Cola de sincronización
```

## 📋 Requisitos del Sistema

### Hardware Mínimo
- **CPU**: ARM Cortex-A72 (Raspberry Pi 4B o superior)
- **RAM**: 2GB mínimo, 4GB recomendado
- **Almacenamiento**: 32GB microSD (Clase 10 o superior)
- **Cámara**: Compatible con libcamera (Pi Camera v3 recomendada)

### Sistema Anfitrión (para compilación)
- **OS**: Ubuntu 20.04+ o Debian 11+
- **RAM**: 8GB mínimo
- **Almacenamiento**: 50GB libres
- **CPU**: Procesador multi-core

## 🔧 Instalación Rápida

### 1. Clonar el Repositorio
```bash
git clone https://github.com/mynameisrober/ASZ-Cam-OS.git
cd ASZ-Cam-OS
```

### 2. Instalar Dependencias
```bash
sudo apt update
sudo apt install -y build-essential wget tar make gcc g++ patch gzip bzip2 unzip rsync file bc
```

### 3. Compilar el Sistema
```bash
./scripts/build.sh
```

### 4. Flashear a Tarjeta SD
```bash
# Identificar la tarjeta SD
lsblk

# Flashear la imagen (reemplazar /dev/sdX con tu dispositivo)
./scripts/flash.sh /dev/sdX
```

## 🔧 Configuración

### Configuración del Sistema
Editar `/opt/aszcam/config/aszcam.conf`:
```ini
[camera]
resolution_width = 4056
resolution_height = 3040
framerate = 30

[storage]
photos_path = "/var/aszcam/photos"
compression_quality = 85

[network]
wifi_enabled = true
ssh_enabled = false
```

### Gestión de Servicios
```bash
# Estado de servicios
systemctl status aszcam-camera

# Reiniciar servicio
systemctl restart aszcam-photo-manager

# Ver logs
journalctl -u aszcam-camera -f
```

## 📈 Optimizaciones de Rendimiento

- **Compilación nativa ARM** con optimizaciones -O3
- **Uso de GPU** para procesamiento de imagen
- **Sistema de cache inteligente** para acceso rápido a fotos
- **Compresión optimizada** de imágenes
- **Gestión de memoria swap** optimizada

## 🔒 Seguridad y Estabilidad

- **Sistema de archivos read-only** para partición del sistema
- **Backup automático** de configuraciones críticas
- **Watchdog** para reinicio automático en caso de fallos
- **Logs centralizados** para debugging
- **Validación de integridad** del sistema

## 📚 Documentación

- [Guía de Instalación Completa](docs/installation.md)
- [Configuración Avanzada](docs/configuration.md)
- [Desarrollo y API](docs/development.md)
- [Solución de Problemas](docs/troubleshooting.md)

## 🚦 Estado del Desarrollo

### ✅ Fase 1: Sistema Base (Completado)
- [x] Imagen base del SO con kernel personalizado
- [x] Scripts de construcción automatizados
- [x] Documentación de instalación y configuración
- [x] Sistema de servicios básicos funcionando

### 🔄 Fase 2: Integración de Cámara (En Progreso)
- [ ] Servicios de cámara completamente integrados
- [ ] API interna para manejo de fotografía
- [ ] Sistema de almacenamiento de fotos optimizado
- [ ] Interfaz básica para captura de fotos

### ⏳ Fase 3: Características Avanzadas (Pendiente)
- [ ] Sincronización en la nube funcionando
- [ ] Sistema de recuerdos implementado
- [ ] UI/UX completa y optimizada
- [ ] Sistema de actualizaciones OTA

## 🤝 Contribuir

1. Fork del proyecto
2. Crear rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit de cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abrir un Pull Request

## 📄 Licencia

Este proyecto está bajo la Licencia MIT. Ver el archivo `LICENSE` para más detalles.

## 📞 Soporte

- **Issues**: [GitHub Issues](https://github.com/mynameisrober/ASZ-Cam-OS/issues)
- **Documentación**: [Wiki del Proyecto](https://github.com/mynameisrober/ASZ-Cam-OS/wiki)
- **Email**: soporte@aszcam.com

---

**ASZ Cam OS** - Transformando la fotografía con tecnología optimizada 📸
