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

### **Modos de Cámara Opcionales** 🎯

Para pruebas, desarrollo, o demostraciones, ASZ Cam OS puede ejecutarse sin necesidad de una cámara física:

```bash
# Ejecutar sin cámara (para pruebas de interfaz)
python src/main.py --no-camera

# Modo demostración con cámara simulada
python src/main.py --demo

# Modo desarrollo con cámara ficticia
python src/main.py --mock-camera
```

**Casos de Uso:**
- **`--no-camera`**: Perfecto para probar la interfaz de usuario sin hardware
- **`--demo`**: Ideal para demostraciones con datos de muestra
- **`--mock-camera`**: Excelente para desarrollo y contribuciones

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

## 🔌 Referencia de API

### **Control de Cámara**
```python
from src.camera.camera_service import CameraService

camera = CameraService()
camera.initialize()

# Capturar foto
photo_path = camera.capture_photo()

# Configurar ajustes
camera.set_camera_setting('iso', 800)
camera.set_camera_setting('white_balance', 'daylight')
```

### **Gestión de Sincronización**
```python
from src.sync.sync_service import SyncService

sync = SyncService()
sync.initialize()

# Sincronizar foto específica
sync.sync_photo('/path/to/photo.jpg', priority=1)

# Monitorear estado de sincronización
stats = sync.get_sync_stats()
print(f"Fotos sincronizadas: {stats['total_photos_synced']}")
```

### **Configuración**
```python
from src.config.settings import settings

# Acceder a configuraciones de cámara
resolution = settings.camera.default_resolution
quality = settings.camera.quality

# Modificar configuraciones de sincronización
settings.sync.enabled = True
settings.sync.album_name = "Mi Cámara"
settings.save_config()
```

## 🛠️ Desarrollo

### **Configuración de Desarrollo**
```bash
# Clonar y configurar
git clone https://github.com/mynameisrober/ASZ-Cam-OS.git
cd ASZ-Cam-OS

# Crear entorno virtual
python3 -m venv venv
source venv/bin/activate

# Instalar dependencias
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Ejecutar en modo desarrollo
python src/main.py --dev --mock-camera
```

### **Contribuir**
1. Hacer fork del repositorio
2. Crear rama de funcionalidad (`git checkout -b feature/funcionalidad-increible`)
3. Confirmar cambios (`git commit -m 'feat: agregar funcionalidad increíble'`)
4. Subir a rama (`git push origin feature/funcionalidad-increible`)
5. Abrir Pull Request

### **Calidad de Código**
- **Estilo**: Formateador Black, linting flake8
- **Verificación de Tipos**: Análisis estático mypy
- **Pruebas**: pytest con 90%+ de cobertura
- **Documentación**: Docstrings estilo Google

## 🔒 Seguridad y Privacidad

### **Características de Seguridad**
- **Superficie de Ataque Mínima**: Sistema construido específicamente con solo servicios esenciales
- **Credenciales Encriptadas**: Tokens OAuth2 encriptados en reposo
- **Seguridad de Red**: Configuración de firewall y comunicación segura
- **Actualizaciones Regulares**: Gestión automatizada de parches de seguridad

### **Compromiso con la Privacidad**
- **Local-First**: Funcionalidad completa sin dependencia de la nube
- **Control de Datos**: Control completo sobre almacenamiento y compartición de fotos
- **Sincronización Transparente**: Visibilidad clara sobre qué datos se sincronizan
- **Nube Opcional**: Las funciones de nube son completamente opcionales

## 📊 Rendimiento

### **Benchmarks**
- **Tiempo de Arranque**: < 10 segundos desde encendido hasta cámara lista
- **Velocidad de Captura**: < 200ms de retraso del obturador en condiciones óptimas
- **Latencia de Vista Previa**: < 100ms de latencia cámara-a-pantalla
- **Rendimiento de Sincronización**: Hasta 50 fotos/minuto de carga (dependiente de la red)

### **Uso de Recursos**
- **RAM**: 200-400MB uso típico (excluyendo buffers)
- **Almacenamiento**: Sistema base de 2GB + fotos + archivos temporales
- **CPU**: < 20% carga promedio durante operación normal
- **GPU**: Aceleración de hardware para vista previa y procesamiento

## 🎯 Casos de Uso

### **Fotografía Personal**
- **Eventos Familiares**: Captura confiable con respaldo automático
- **Fotografía de Viajes**: Capacidad offline con sincronización cuando hay conexión
- **Seguridad Doméstica**: Captura activada por movimiento con almacenamiento en la nube
- **Proyectos Time-lapse**: Secuencias de captura automatizadas

### **Aplicaciones Profesionales**
- **Fotografía de Eventos**: Captura rápida con respaldo inmediato
- **Fotografía de Productos**: Calidad consistente con controles manuales
- **Documentación Científica**: Preservación y organización de metadatos
- **Proyectos Educativos**: Interfaz amigable para estudiantes con compartición en la nube

### **IoT y Automatización**
- **Automatización del Hogar**: Integración con sistemas domésticos inteligentes
- **Monitoreo Remoto**: Sistema de cámara accesible por red
- **Monitoreo Agrícola**: Opciones de implementación resistentes al clima
- **Sistemas de Seguridad**: Detección de movimiento y alertas automatizadas

## 🌟 ¿Por qué ASZ Cam OS?

### **vs. Software de Cámara Genérico**
- ✅ **Rendimiento Optimizado**: Construido específicamente para hardware Raspberry Pi
- ✅ **Características Profesionales**: Controles manuales y configuraciones avanzadas
- ✅ **Sincronización Confiable**: Integración robusta en la nube con recuperación de errores
- ✅ **Solución Completa**: Hardware + software + nube en un paquete

### **vs. Soluciones DIY**
- ✅ **Listo para Producción**: Miles de horas de desarrollo y pruebas
- ✅ **Documentación Comprensiva**: Guías completas y solución de problemas
- ✅ **Soporte Activo**: Actualizaciones regulares y soporte de la comunidad
- ✅ **Interfaz Profesional**: Interfaz pulida diseñada para fotógrafos

### **vs. Alternativas Comerciales**
- ✅ **Código Abierto**: Acceso completo al código fuente y personalización
- ✅ **Sin Dependencia de Proveedor**: Usa tu propia cuenta de Google y almacenamiento
- ✅ **Costo Efectivo**: Sin tarifas mensuales o costos de licencias
- ✅ **Enfocado en Privacidad**: Tus datos permanecen bajo tu control

## 🗓️ Hoja de Ruta

### **Versión 1.1** (Q2 2024)
- [ ] **Grabación de Video**: Captura de video Full HD con compresión
- [ ] **Soporte Multi-Cámara**: Conectar y controlar múltiples cámaras
- [ ] **Filtros Avanzados**: Efectos de imagen en tiempo real y mejoras
- [ ] **Aplicación Móvil**: App complementaria para control remoto

### **Versión 1.2** (Q3 2024)
- [ ] **Características IA**: Auto-etiquetado y organización inteligente
- [ ] **Proveedores de Nube Adicionales**: Soporte para Dropbox, OneDrive
- [ ] **Almacenamiento en Red**: Integración con NAS y comparticiones SMB
- [ ] **Automatización Avanzada**: Captura time-lapse e intervalos

### **Versión 2.0** (Q4 2024)
- [ ] **Multi-Plataforma**: Soporte para otros SBCs y x86
- [ ] **Sistema de Plugins**: Extensiones de terceros y personalización
- [ ] **Características Empresariales**: Soporte multi-usuario y administración
- [ ] **Flujo de Trabajo Profesional**: Procesamiento RAW y operaciones por lotes

## 💬 Comunidad

### **Involúcrate**
- **Discusiones en GitHub**: Preguntas, ideas y exhibiciones
- **Servidor Discord**: Chat y soporte de la comunidad en tiempo real
- **Comunidad Reddit**: r/ASZCamOS para discusiones de usuarios
- **Canal YouTube**: Tutoriales, demos y exhibiciones del proyecto

### **Apoya el Proyecto**
- ⭐ **Dale estrella a este repositorio** para mostrar apoyo
- 🐛 **Reporta errores** para ayudar a mejorar la estabilidad
- 💡 **Sugiere características** para desarrollo futuro
- 📝 **Contribuye documentación** para ayudar a otros usuarios
- 💻 **Envía pull requests** con mejoras

## 📄 Licencia

ASZ Cam OS se distribuye bajo la **Licencia MIT** - consulta el archivo [LICENSE](LICENSE) para más detalles.

### **Qué significa esto:**
- ✅ **Uso Comercial**: Usar en proyectos comerciales
- ✅ **Modificación**: Personalizar y adaptar el código
- ✅ **Distribución**: Compartir y redistribuir libremente
- ✅ **Uso Privado**: Usar para proyectos personales
- ❗ **Atribución Requerida**: Incluir aviso de copyright original

## 🙏 Reconocimientos

### **Proyectos de Código Abierto**
- **[Raspberry Pi Foundation](https://www.raspberrypi.org/)** - Increíble base de hardware y software
- **[libcamera](https://libcamera.org/)** - Stack de cámara moderno para Linux
- **[PyQt6](https://www.riverbankcomputing.com/software/pyqt/)** - Poderoso framework GUI
- **[Google Photos API](https://developers.google.com/photos)** - Integración de almacenamiento en la nube

### **Contribuidores de la Comunidad**
Agradecimientos especiales a todos los contribuidores que han ayudado a mejorar ASZ Cam OS a través de código, documentación, pruebas y retroalimentación.

---

<div align="center">

**🎯 ¿Listo para transformar tu Raspberry Pi en un sistema de cámara profesional?**

[📥 **Comenzar**](docs/INSTALACION.md) • [📚 **Documentación**](docs/) • [💬 **Comunidad**](https://github.com/mynameisrober/ASZ-Cam-OS/discussions) • [🐛 **Issues**](https://github.com/mynameisrober/ASZ-Cam-OS/issues)

</div>
