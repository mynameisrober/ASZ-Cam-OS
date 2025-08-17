# ASZ Cam OS - Guía de Instalación

Guía completa de instalación para ASZ Cam OS - un sistema operativo de cámara personalizado para Raspberry Pi con integración de Google Photos.

## Tabla de Contenidos
- [Descripción General](#descripción-general)
- [Requisitos del Sistema](#requisitos-del-sistema)
- [Prerrequisitos](#prerrequisitos)
- [Métodos de Instalación](#métodos-de-instalación)
- [Instalación Rápida](#instalación-rápida)
- [Instalación Manual](#instalación-manual)
- [Configuración Post-Instalación](#configuración-post-instalación)
- [Configuración de Google Photos](#configuración-de-google-photos)
- [Solución de Problemas](#solución-de-problemas)

## Descripción General

ASZ Cam OS es un sistema operativo ligero y especializado diseñado para Raspberry Pi que transforma tu dispositivo en un sistema de cámara dedicado con capacidades de sincronización en la nube. Incluye:

- **Arranque Rápido**: Optimizado para tiempo de arranque < 10 segundos
- **Enfoque en Cámara**: Optimizado para operaciones de cámara con aceleración de hardware
- **Integración con Google Photos**: Respaldo automático y sincronización de fotos
- **Interfaz Táctil**: Interfaz limpia y responsiva construida con PyQt6
- **Inicio Automático**: Lanza automáticamente la aplicación de cámara al arrancar
- **Seguro**: Sistema mínimo con refuerzo de seguridad

## Requisitos del Sistema

### Requisitos Mínimos
- **Raspberry Pi 4 Model B** (mínimo 2GB RAM, recomendado 4GB+)
- **Tarjeta MicroSD**: 16GB Clase 10 o mejor (recomendado 32GB+)
- **Cámara**: Módulo de Cámara Raspberry Pi v2/v3 o cámara USB compatible
- **Pantalla**: Monitor HDMI o pantalla táctil oficial de Raspberry Pi
- **Fuente de Alimentación**: Fuente oficial de Raspberry Pi (5V/3A)
- **Conexión a Internet**: WiFi o Ethernet para sincronización con Google Photos

### Hardware Soportado
- Raspberry Pi 4 Model B (todas las variantes de RAM)
- Raspberry Pi 400 (con cámara externa)
- Módulo de Cámara Raspberry Pi v1/v2/v3
- Cámaras web USB (compatibles con UVC)
- Pantalla táctil oficial de Raspberry Pi de 7"
- La mayoría de pantallas HDMI (recomendado 1920x1080)

### Configuración Recomendada
- Raspberry Pi 4 (4GB u 8GB)
- Tarjeta MicroSD de alta calidad (SanDisk Extreme, Samsung EVO Select)
- Módulo de Cámara Raspberry Pi v3
- Pantalla táctil oficial de 7" para operación portátil
- Carcasa con montaje para cámara

## Prerrequisitos

### Requisitos de Software en Computadora Host
- [Raspberry Pi Imager](https://www.raspberrypi.org/software/) para grabar tarjetas SD
- Cliente SSH (integrado en macOS/Linux, PuTTY para Windows)
- Git (para construir desde código fuente)

### Configuración de API de Google Photos (Opcional)
Para habilitar la sincronización con Google Photos, necesitarás:

1. **Proyecto de Google Cloud**: Crear un proyecto en [Google Cloud Console](https://console.cloud.google.com/)
2. **API de Photos Library**: Habilitar la API de Photos Library para tu proyecto
3. **Credenciales OAuth2**: Crear credenciales OAuth2 para una aplicación de escritorio
4. **Archivo de Credenciales**: Descargar el archivo JSON de credenciales

Los pasos detallados se proporcionan en la sección [Configuración de Google Photos](#configuración-de-google-photos).

## Métodos de Instalación

Elige uno de los siguientes métodos de instalación:

1. **Instalación Rápida** (Recomendado): Usar el script de instalación automatizada
2. **Instalación Manual**: Configuración manual paso a paso para personalización
3. **Imagen Prebuild**: Grabar una imagen de disco prebuild (si está disponible)

## Instalación Rápida

La forma más rápida de hacer funcionar ASZ Cam OS es usando el script de instalación automatizada.

### Paso 1: Preparar Raspberry Pi OS

1. **Grabar Raspberry Pi OS Lite** en tu tarjeta SD usando Raspberry Pi Imager
   - Elige "Raspberry Pi OS Lite (64-bit)" para mejor rendimiento
   - Habilitar SSH y configurar WiFi en opciones avanzadas
   - Establecer nombre de usuario como `pi` y configurar contraseña

2. **Arrancar y Conectar**
   ```bash
   # SSH a tu Pi (reemplaza con la IP de tu Pi)
   ssh pi@192.168.1.100
   ```

### Paso 2: Descargar ASZ Cam OS

```bash
# Actualizar sistema
sudo apt update && sudo apt upgrade -y

# Instalar git
sudo apt install -y git

# Clonar el repositorio
git clone https://github.com/mynameisrober/ASZ-Cam-OS.git
cd ASZ-Cam-OS
```

### Paso 3: Ejecutar Script de Instalación

```bash
# Hacer el instalador ejecutable
chmod +x scripts/install.sh

# Ejecutar el instalador (requiere sudo)
sudo ./scripts/install.sh
```

El instalador:
- Instalará todas las dependencias
- Configurará el entorno virtual de Python
- Configurará ajustes del sistema
- Instalará servicios systemd  
- Optimizará configuración de arranque
- Configurará X11 y entorno de escritorio
- Descargará fuentes y temas
- Configurará permisos de cámara

### Paso 4: Reiniciar

```bash
sudo reboot
```

Después del reinicio, ASZ Cam OS debería iniciarse automáticamente y mostrar la interfaz de cámara.

## Instalación Manual

Para usuarios avanzados que quieren personalizar el proceso de instalación.

### Paso 1: Preparación del Sistema

```bash
# Actualizar listas de paquetes y sistema
sudo apt update && sudo apt upgrade -y

# Instalar paquetes esenciales
sudo apt install -y git curl wget unzip build-essential cmake pkg-config
sudo apt install -y python3 python3-pip python3-venv python3-dev
sudo apt install -y libcamera-dev libcamera-apps python3-libcamera python3-picamera2
```

### Paso 2: Crear Usuario y Directorios

```bash
# Crear directorios de ASZ Cam
sudo mkdir -p /home/pi/ASZCam
sudo mkdir -p /home/pi/.config/aszcam
sudo mkdir -p /home/pi/Pictures/ASZCam
sudo mkdir -p /var/log/aszcam

# Establecer permisos
sudo chown -R pi:pi /home/pi/ASZCam
sudo chown -R pi:pi /home/pi/.config/aszcam
sudo chown -R pi:pi /home/pi/Pictures
sudo chown -R pi:pi /var/log/aszcam
```

### Paso 3: Instalar ASZ Cam OS

```bash
# Clonar repositorio
git clone https://github.com/mynameisrober/ASZ-Cam-OS.git
cd ASZ-Cam-OS

# Copiar código fuente
cp -r src /home/pi/ASZCam/
cp -r assets /home/pi/ASZCam/
cp requirements.txt /home/pi/ASZCam/

# Crear entorno virtual de Python
python3 -m venv /home/pi/ASZCam/venv

# Instalar dependencias de Python
/home/pi/ASZCam/venv/bin/pip install --upgrade pip
/home/pi/ASZCam/venv/bin/pip install -r /home/pi/ASZCam/requirements.txt
```

### Paso 4: Configuración del Sistema

```bash
# Ejecutar scripts de configuración individuales
sudo ./scripts/setup_rpi.sh      # Optimización de Raspberry Pi
sudo ./scripts/download_fonts.sh # Instalación de fuentes
sudo ./scripts/configure_system.sh # Configuración del sistema

# Instalar servicio systemd
sudo cp install/asz-cam-os.service /etc/systemd/system/
sudo sed -i "s|{ASZ_INSTALL_DIR}|/home/pi/ASZCam|g" /etc/systemd/system/asz-cam-os.service
sudo sed -i "s|{ASZ_USER}|pi|g" /etc/systemd/system/asz-cam-os.service
sudo systemctl daemon-reload
sudo systemctl enable asz-cam-os.service
```

### Paso 5: Aplicar Configuración de Arranque

```bash
# Respaldar configuración original
sudo cp /boot/config.txt /boot/config.txt.backup

# Aplicar configuración de arranque de ASZ Cam
sudo cp install/boot_config.txt /boot/config.txt

# Aplicar configuración X11
sudo cp install/xorg.conf /etc/X11/xorg.conf
```

## Configuración Post-Instalación

### Configuración Inicial

Después del primer arranque, completa la configuración inicial:

1. **Establecer Código de País WiFi** (si no se hizo durante el grabado)
   ```bash
   sudo raspi-config
   # Navegar a Localisation Options > WLAN Country
   ```

2. **Configurar Zona Horaria**
   ```bash
   sudo dpkg-reconfigure tzdata
   ```

3. **Cambiar Contraseña por Defecto**
   ```bash
   passwd
   ```

### Configuración de Cámara

1. **Probar Cámara**
   ```bash
   # Probar con libcamera
   libcamera-hello --list-cameras
   libcamera-still -o test.jpg
   ```

2. **Verificar Cámara en ASZ Cam OS**
   - La vista previa de cámara debería aparecer automáticamente
   - Intenta tomar una foto de prueba
   - Verifica que las fotos se guarden en `/home/pi/Pictures/ASZCam/`

### Validación del Sistema

Ejecuta el script de validación para asegurar que todo esté funcionando:

```bash
cd ASZ-Cam-OS
sudo ./scripts/validate_install.sh
```

Esto verificará:
- Funcionalidad de cámara
- Estado del servicio
- Permisos de archivos
- Conectividad de red
- Configuración de pantalla

## Configuración de Google Photos

Para habilitar el respaldo automático de fotos a Google Photos:

### Paso 1: Crear Proyecto de Google Cloud

1. Ve a [Google Cloud Console](https://console.cloud.google.com/)
2. Crear un nuevo proyecto o seleccionar uno existente
3. Habilitar la **API de Photos Library**:
   - Navegar a "APIs & Services" > "Library"
   - Buscar "Photos Library API"
   - Hacer clic en "Enable"

### Paso 2: Crear Credenciales OAuth2

1. Ir a "APIs & Services" > "Credentials"
2. Hacer clic en "Create Credentials" > "OAuth client ID"
3. Elegir "Desktop application"
4. Nombrarlo "ASZ Cam OS"
5. Descargar el archivo JSON de credenciales

### Paso 3: Subir Credenciales a Pi

```bash
# Copiar archivo de credenciales a Pi (reemplaza con tu archivo)
scp ~/Downloads/credentials.json pi@192.168.1.100:/home/pi/ASZCam/google_credentials.json

# Establecer permisos apropiados
chmod 600 /home/pi/ASZCam/google_credentials.json
```

### Paso 4: Autenticación Inicial

1. **Habilitar Sincronización en Configuración**
   - Abrir ASZ Cam OS
   - Navegar a Configuración > Sincronización
   - Habilitar "Sincronización con Google Photos"

2. **Completar Flujo OAuth**
   - Hacer clic en "Autenticar con Google Photos"
   - Seguir las indicaciones de autenticación
   - Otorgar permisos necesarios

3. **Verificar Sincronización**
   - Tomar una foto de prueba
   - Verificar estado de sincronización en Configuración
   - Verificar que la foto aparezca en tus Google Photos

### Notas de Privacidad y Seguridad

- **Permisos**: ASZ Cam OS solo solicita acceso de solo-agregar a Google Photos
- **Datos**: No se transmite información personal más allá de archivos de fotos
- **Almacenamiento Local**: Los tokens de autenticación se encriptan y almacenan localmente
- **Control**: Puedes deshabilitar la sincronización o revocar el acceso en cualquier momento

## Solución de Problemas

### Problemas Comunes

#### Problemas de Arranque
- **Pantalla negra al arrancar**: Verifica cable HDMI y compatibilidad de pantalla
- **Arranque lento**: Ejecuta `systemctl analyze-blame` para identificar servicios lentos
- **Fallo del servicio**: Verifica `journalctl -u asz-cam-os` para mensajes de error

#### Problemas de Cámara
- **Cámara no detectada**: 
  ```bash
  # Verificar conexión de cámara
  libcamera-hello --list-cameras
  
  # Verificar módulo de cámara habilitado
  sudo raspi-config # Interface Options > Camera
  ```

- **Permiso de cámara denegado**:
  ```bash
  # Agregar usuario al grupo video
  sudo usermod -a -G video pi
  ```

#### Problemas de Sincronización
- **Fallo de autenticación**: 
  - Verifica ubicación y permisos del archivo de credenciales
  - Verifica que el proyecto de Google Cloud tenga habilitada la API de Photos Library
  - Verifica conectividad a internet

- **Errores de carga**: 
  - Verifica `journalctl -u asz-cam-os` para mensajes de error detallados
  - Verifica cuota de almacenamiento de Google Photos
  - Verifica conectividad de red

#### Problemas de Rendimiento
- **Interfaz lenta**: 
  - Verifica división de memoria GPU: `vcgencmd get_mem gpu`
  - Debería mostrar `gpu=128M` o superior
  - Verifica controladores gráficos: `glxinfo | grep renderer`

- **Alto uso de CPU**:
  - Verifica procesos fugitivos: `htop`
  - Verifica configuraciones de resolución de cámara
  - Verifica tamaño de cola de sincronización

### Archivos de Registro

Ubicaciones de registros clave para solución de problemas:

```bash
# Registros del sistema
journalctl -u asz-cam-os -f

# Registros de aplicación
tail -f /var/log/aszcam/aszcam.log

# Registros de arranque del sistema
dmesg | grep -i camera

# Registros X11
cat ~/.local/share/xorg/Xorg.0.log
```

### Opciones de Recuperación

#### Arranque en Modo Seguro
Agregar a `/boot/cmdline.txt`:
```
systemd.unit=rescue.target
```

#### Restablecer Configuración
```bash
# Respaldar configuraciones actuales
cp ~/.config/aszcam/settings.yaml ~/.config/aszcam/settings.yaml.backup

# Restablecer a valores por defecto
rm ~/.config/aszcam/settings.yaml

# Reiniciar servicio
sudo systemctl restart asz-cam-os
```

#### Restablecimiento de Fábrica
```bash
# Detener servicio
sudo systemctl stop asz-cam-os

# Eliminar datos de usuario (PRECAUCIÓN: Esto elimina todas las fotos y configuraciones)
rm -rf ~/.config/aszcam/
rm -rf ~/Pictures/ASZCam/

# Reiniciar servicio (recreará valores por defecto)
sudo systemctl start asz-cam-os
```

### Obtener Ayuda

Si encuentras problemas no cubiertos aquí:

1. **Verificar Registros**: Siempre verifica los registros primero para mensajes de error específicos
2. **Issues de GitHub**: Busca issues existentes o crea uno nuevo en [Repositorio GitHub](https://github.com/mynameisrober/ASZ-Cam-OS/issues)
3. **Foros de Comunidad**: Los foros de Raspberry Pi tienen ayuda extensa relacionada con cámaras
4. **Documentación**: Verifica la [Guía del Usuario](GUIA_USUARIO.md) y [Guía de Solución de Problemas](SOLUCION_PROBLEMAS.md)

### Optimización de Rendimiento

Para rendimiento óptimo:

1. **Usar Tarjeta SD Rápida**: Clase 10 o mejor, preferiblemente Application Performance Class A2
2. **Fuente de Alimentación Adecuada**: Usar fuente oficial de Raspberry Pi
3. **Refrigeración**: Asegurar ventilación adecuada, considerar disipadores de calor para operación sostenida
4. **Red**: Usar Ethernet cableado para mejor rendimiento de sincronización
5. **Actualizaciones Regulares**: Mantener sistema y ASZ Cam OS actualizados

---

## Próximos Pasos

Después de la instalación exitosa:

1. **Lee la [Guía del Usuario](GUIA_USUARIO.md)** para instrucciones detalladas de uso
2. **Configura la sincronización con Google Photos** para respaldo automático
3. **Personaliza configuraciones** para tu caso de uso específico
4. **Configura respaldos regulares** de tu configuración
5. **Explora características avanzadas** en el panel de configuración

**¡Disfruta tu configuración de ASZ Cam OS!** 📷