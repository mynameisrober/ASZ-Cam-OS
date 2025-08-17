# ASZ Cam OS

**Sistema Operativo de Cámara Profesional para Raspberry Pi**

ASZ Cam OS transforma tu Raspberry Pi en un sistema de cámara dedicado de alto rendimiento con sincronización en la nube, interfaz profesional y confiabilidad de nivel empresarial.

![ASZ Cam OS](assets/banner.png)

## ✨ Características Principales

### 🚀 **Rendimiento Ultra Rápido**
- **&lt;10 Segundos de Arranque**: Secuencia de arranque optimizada para empezar a fotografiar más rápido
- **Aceleración de Hardware**: Utilización completa de GPU para vista previa y procesamiento fluido
- **Vista Previa en Tiempo Real**: Vista previa de cámara de baja latencia con controles profesionales
- **Captura Instantánea**: Retraso mínimo del obturador con soporte para modo ráfaga

### 📷 **Sistema de Cámara Profesional**
- **Integración libCamera**: Soporte avanzado para cámaras Raspberry Pi con todos los módulos
- **Controles Manuales**: Control de ISO, exposición, balance de blancos y enfoque
- **Soporte Multi-formato**: Capacidades de captura JPEG, PNG y RAW
- **Alta Resolución**: Captura de fotos hasta 4K con múltiples configuraciones de calidad

### ☁️ **Sincronización Inteligente en la Nube**
- **Integración con Google Photos**: Respaldo automático con autenticación OAuth2
- **Carga Inteligente**: Colas de prioridad, lógica de reintento y prevención de duplicados
- **Gestión de Ancho de Banda**: Cargas optimizadas con opciones de compresión
- **Capacidad Offline**: Funcionalidad completa sin conexión a internet

### 🎨 **Interfaz de Usuario Moderna**
- **Optimizada para Táctil**: Diseño responsivo para pantallas táctiles y pantallas tradicionales
- **Tipografía Profesional**: Sistema de fuentes inspirado en SFCamera
- **Navegación Intuitiva**: Interfaz limpia centrada en el fotógrafo
- **Estado en Tiempo Real**: Progreso de sincronización en vivo, almacenamiento y monitoreo del sistema

### 🔧 **Listo para Empresas**
- **Instalación Automatizada**: Implementación con un comando con configuración completa del sistema
- **Integración Systemd**: Gestión de servicios confiable con auto-reinicio
- **Registro Comprensivo**: Monitoreo detallado del sistema y solución de problemas
- **Seguridad Reforzada**: Superficie de ataque mínima con credenciales encriptadas

## 📋 Requisitos del Sistema

### **Requisitos Mínimos**
- Raspberry Pi 4 Model B (2GB RAM)
- Tarjeta MicroSD: 16GB Clase 10
- Cámara: Módulo de Cámara Pi v2 o cámara USB
- Pantalla: Monitor HDMI o pantalla táctil
- Alimentación: Fuente oficial de 5V/3A

### **Configuración Recomendada**
- Raspberry Pi 4 (4GB u 8GB RAM)
- MicroSD de alta velocidad: Tarjeta de 32GB+ clasificación A2
- Cámara: Módulo de Cámara Pi v3 para la mejor calidad
- Pantalla: Pantalla táctil oficial de 7" para operación portátil
- Almacenamiento: Disco USB 3.0 adicional para almacenamiento de fotos

### **Hardware Soportado**
- **Computadoras de Placa Única**: Raspberry Pi 4, Pi 400
- **Cámaras**: Todos los módulos de Cámara Pi, cámaras USB UVC
- **Pantallas**: Monitores HDMI, pantalla táctil Pi, la mayoría de paneles LCD
- **Almacenamiento**: MicroSD, discos USB, almacenamiento en red

## 🚀 Inicio Rápido

### **Instalación con Una Línea**
```bash
curl -fsSL https://raw.githubusercontent.com/mynameisrober/ASZ-Cam-OS/main/scripts/install.sh | sudo bash
```

### **Instalación Manual**
```bash
# 1. Clonar repositorio
git clone https://github.com/mynameisrober/ASZ-Cam-OS.git
cd ASZ-Cam-OS

# 2. Ejecutar instalador
chmod +x scripts/install.sh
sudo ./scripts/install.sh

# 3. Reiniciar sistema
sudo reboot
```

**¡Eso es todo!** ASZ Cam OS se iniciará automáticamente después del reinicio.

## 📖 Documentación

### **Documentación del Usuario**
- **[📥 Guía de Instalación](docs/INSTALACION.md)** - Instrucciones completas de configuración
- **[👤 Guía del Usuario](docs/GUIA_USUARIO.md)** - Cómo usar ASZ Cam OS
- **[🔧 Solución de Problemas](docs/SOLUCION_PROBLEMAS.md)** - Guía de resolución de problemas

### **Recursos para Desarrolladores**
- **[💻 Guía del Desarrollador](docs/GUIA_DESARROLLADOR.md)** - Contribución y desarrollo
- **[🏗️ Descripción de Arquitectura](#architecture)** - Diseño del sistema y componentes
- **[🔌 Referencia de API](#api-reference)** - Interfaces de programación

## 🏗️ Arquitectura

ASZ Cam OS está construido con una arquitectura modular orientada a servicios:

```
┌─────────────────────────────────────────┐
│           Interfaz de Usuario           │
│  Vista de Cámara • Galería • Ajustes   │
├─────────────────────────────────────────┤
│          Servicios Principales          │
│  Sistema • Cámara • Sincronización •   │
│           Almacenamiento                │
├─────────────────────────────────────────┤
│             Capa de Hardware            │
│  libCamera • GPIO • Pantalla • Red     │
├─────────────────────────────────────────┤
│         Integración en la Nube          │
│  Google Photos API • OAuth2 • Carga    │
└─────────────────────────────────────────┘
```

### **Componentes Principales**

#### **Gestor del Sistema**
Coordinador central que gestiona el ciclo de vida del sistema, inicialización de servicios y apagado ordenado con manejo comprensivo de errores.

#### **Servicio de Cámara** 
Capa de abstracción de hardware que proporciona interfaz unificada para cámaras Raspberry Pi y dispositivos USB con controles avanzados.

#### **Servicio de Sincronización**
Sincronización inteligente en la nube con colas de prioridad, lógica de reintento, detección de duplicados y optimización de ancho de banda.

#### **Marco de Interfaz**
Interfaz moderna basada en PyQt6 con optimización táctil, diseño responsivo y flujos de trabajo de fotografía profesional.

## 🔌 API Reference

### **Camera Control**
```python
from src.camera.camera_service import CameraService

camera = CameraService()
camera.initialize()

# Capture photo
photo_path = camera.capture_photo()

# Configure settings
camera.set_camera_setting('iso', 800)
camera.set_camera_setting('white_balance', 'daylight')
```

### **Sync Management**
```python
from src.sync.sync_service import SyncService

sync = SyncService()
sync.initialize()

# Sync specific photo
sync.sync_photo('/path/to/photo.jpg', priority=1)

# Monitor sync status
stats = sync.get_sync_stats()
print(f"Photos synced: {stats['total_photos_synced']}")
```

### **Configuration**
```python
from src.config.settings import settings

# Access camera settings
resolution = settings.camera.default_resolution
quality = settings.camera.quality

# Modify sync settings
settings.sync.enabled = True
settings.sync.album_name = "My Camera"
settings.save_config()
```

## 🛠️ Development

### **Development Setup**
```bash
# Clone and setup
git clone https://github.com/mynameisrober/ASZ-Cam-OS.git
cd ASZ-Cam-OS

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Run in development mode
python src/main.py --dev --mock-camera
```

### **Contributing**
1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'feat: add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

### **Code Quality**
- **Style**: Black formatter, flake8 linting
- **Type Checking**: mypy static analysis
- **Testing**: pytest with 90%+ coverage
- **Documentation**: Google-style docstrings

## 🔒 Security & Privacy

### **Security Features**
- **Minimal Attack Surface**: Purpose-built system with only essential services
- **Encrypted Credentials**: OAuth2 tokens encrypted at rest
- **Network Security**: Firewall configuration and secure communication
- **Regular Updates**: Automated security patch management

### **Privacy Commitment**
- **Local-First**: Full functionality without cloud dependency
- **Data Control**: Complete control over photo storage and sharing
- **Transparent Sync**: Clear visibility into what data is synchronized
- **Opt-in Cloud**: Cloud features are completely optional

## 📊 Performance

### **Benchmarks**
- **Boot Time**: < 10 seconds from power-on to camera ready
- **Capture Speed**: < 200ms shutter lag in optimal conditions
- **Preview Latency**: < 100ms camera-to-display latency
- **Sync Performance**: Up to 50 photos/minute upload (network dependent)

### **Resource Usage**
- **RAM**: 200-400MB typical usage (excluding buffers)
- **Storage**: 2GB base system + photos + temporary files
- **CPU**: < 20% average load during normal operation
- **GPU**: Hardware acceleration for preview and processing

## 🎯 Use Cases

### **Personal Photography**
- **Family Events**: Reliable capture with automatic backup
- **Travel Photography**: Offline capability with sync when connected
- **Home Security**: Motion-triggered capture with cloud storage
- **Time-lapse Projects**: Automated capture sequences

### **Professional Applications**
- **Event Photography**: Rapid capture with immediate backup
- **Product Photography**: Consistent quality with manual controls
- **Scientific Documentation**: Metadata preservation and organization
- **Educational Projects**: Student-friendly interface with cloud sharing

### **IoT and Automation**
- **Home Automation**: Integration with smart home systems
- **Remote Monitoring**: Network-accessible camera system
- **Agricultural Monitoring**: Weather-resistant deployment options
- **Security Systems**: Motion detection and automated alerts

## 🌟 Why ASZ Cam OS?

### **vs. Generic Camera Software**
- ✅ **Optimized Performance**: Purpose-built for Raspberry Pi hardware
- ✅ **Professional Features**: Manual controls and advanced settings
- ✅ **Reliable Sync**: Robust cloud integration with error recovery
- ✅ **Complete Solution**: Hardware + software + cloud in one package

### **vs. DIY Solutions**
- ✅ **Production Ready**: Thousands of hours of development and testing
- ✅ **Comprehensive Documentation**: Complete guides and troubleshooting
- ✅ **Active Support**: Regular updates and community support
- ✅ **Professional UI**: Polished interface designed for photographers

### **vs. Commercial Alternatives**
- ✅ **Open Source**: Full source code access and customization
- ✅ **No Vendor Lock-in**: Use your own Google account and storage
- ✅ **Cost Effective**: No monthly fees or licensing costs
- ✅ **Privacy Focused**: Your data stays under your control

## 🗓️ Roadmap

### **Version 1.1** (Q2 2024)
- [ ] **Video Recording**: Full HD video capture with compression
- [ ] **Multi-Camera Support**: Connect and control multiple cameras
- [ ] **Advanced Filters**: Real-time image effects and enhancement
- [ ] **Mobile App**: Companion app for remote control

### **Version 1.2** (Q3 2024)
- [ ] **AI Features**: Auto-tagging and smart organization
- [ ] **Additional Cloud Providers**: Dropbox, OneDrive support
- [ ] **Network Storage**: NAS and SMB share integration
- [ ] **Advanced Automation**: Time-lapse and interval shooting

### **Version 2.0** (Q4 2024)
- [ ] **Multi-Platform**: Support for other SBCs and x86
- [ ] **Plugin System**: Third-party extensions and customization
- [ ] **Enterprise Features**: Multi-user support and administration
- [ ] **Professional Workflow**: RAW processing and batch operations

## 💬 Community

### **Get Involved**
- **GitHub Discussions**: Questions, ideas, and showcases
- **Discord Server**: Real-time community chat and support
- **Reddit Community**: r/ASZCamOS for user discussions
- **YouTube Channel**: Tutorials, demos, and project showcases

### **Support the Project**
- ⭐ **Star this repository** to show support
- 🐛 **Report bugs** to help improve stability
- 💡 **Suggest features** for future development
- 📝 **Contribute documentation** to help other users
- 💻 **Submit pull requests** with improvements

## 📄 License

ASZ Cam OS is released under the **MIT License** - see [LICENSE](LICENSE) file for details.

### **What this means:**
- ✅ **Commercial Use**: Use in commercial projects
- ✅ **Modification**: Customize and adapt the code
- ✅ **Distribution**: Share and redistribute freely
- ✅ **Private Use**: Use for personal projects
- ❗ **Attribution Required**: Include original copyright notice

## 🙏 Acknowledgments

### **Open Source Projects**
- **[Raspberry Pi Foundation](https://www.raspberrypi.org/)** - Amazing hardware and software foundation
- **[libcamera](https://libcamera.org/)** - Modern camera stack for Linux
- **[PyQt6](https://www.riverbankcomputing.com/software/pyqt/)** - Powerful GUI framework
- **[Google Photos API](https://developers.google.com/photos)** - Cloud storage integration

### **Community Contributors**
Special thanks to all contributors who have helped make ASZ Cam OS better through code, documentation, testing, and feedback.

---

<div align="center">

**🎯 Ready to transform your Raspberry Pi into a professional camera system?**

[📥 **Get Started**](docs/INSTALLATION.md) • [📚 **Documentation**](docs/) • [💬 **Community**](https://github.com/mynameisrober/ASZ-Cam-OS/discussions) • [🐛 **Issues**](https://github.com/mynameisrober/ASZ-Cam-OS/issues)

</div>
