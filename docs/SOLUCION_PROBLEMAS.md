# ASZ Cam OS - Guía de Solución de Problemas

Guía comprensiva de solución de problemas para resolver issues comunes con ASZ Cam OS.

## Tabla de Contenidos
- [Diagnósticos Rápidos](#diagnósticos-rápidos)
- [Problemas de Instalación](#problemas-de-instalación)
- [Problemas de Arranque y Inicio](#problemas-de-arranque-y-inicio)
- [Problemas de Cámara](#problemas-de-cámara)
- [Problemas de Pantalla](#problemas-de-pantalla)
- [Problemas de Red y Sincronización](#problemas-de-red-y-sincronización)
- [Problemas de Rendimiento](#problemas-de-rendimiento)
- [Recuperación del Sistema](#recuperación-del-sistema)
- [Diagnósticos Avanzados](#diagnósticos-avanzados)

## Diagnósticos Rápidos

### Verificación de Salud del Sistema

Ejecuta este script de diagnóstico rápido para verificar el estado del sistema:

```bash
#!/bin/bash
# Verificación rápida de salud del sistema

echo "=== Verificación de Salud de ASZ Cam OS ==="
echo "Fecha: $(date)"
echo "Tiempo activo: $(uptime -p)"
echo ""

# Verificar estado del servicio
echo "--- Estado del Servicio ---"
systemctl is-active asz-cam-os && echo "✓ ASZ Cam OS: Ejecutándose" || echo "✗ ASZ Cam OS: No se está ejecutando"
systemctl is-active NetworkManager && echo "✓ Red: Ejecutándose" || echo "✗ Red: No se está ejecutando"

# Verificar espacio en disco
echo ""
echo "--- Almacenamiento ---"
df -h / | grep -v Filesystem
df -h /home/pi/Pictures/ASZCam 2>/dev/null | grep -v Filesystem || echo "Directorio de fotos no encontrado"

# Verificar cámara
echo ""
echo "--- Cámara ---"
if command -v libcamera-hello >/dev/null 2>&1; then
    timeout 5 libcamera-hello --list-cameras 2>/dev/null && echo "✓ Cámara detectada" || echo "✗ Cámara no detectada"
else
    echo "✗ Herramientas libcamera no instaladas"
fi

# Verificar red
echo ""
echo "--- Red ---"
ping -c 1 8.8.8.8 >/dev/null 2>&1 && echo "✓ Conectividad a internet" || echo "✗ Sin conexión a internet"

# Verificar memoria GPU
echo ""
echo "--- Memoria GPU ---"
vcgencmd get_mem gpu 2>/dev/null || echo "No se puede verificar memoria GPU"

# Errores recientes
echo ""
echo "--- Errores Recientes ---"
journalctl -u asz-cam-os --since "1 hour ago" --no-pager | grep -i error | tail -3
```

Guardar como `verificacion_salud.sh`, hacer ejecutable y ejecutar:
```bash
chmod +x verificacion_salud.sh
./verificacion_salud.sh
```

### Soluciones Rápidas

Antes de profundizar en la solución de problemas detallada, prueba estas soluciones rápidas:

1. **Reiniciar el servicio**:
   ```bash
   sudo systemctl restart asz-cam-os
   ```

2. **Reiniciar el sistema**:
   ```bash
   sudo reboot
   ```

3. **Verificar almacenamiento disponible**:
   ```bash
   df -h /
   ```

4. **Verificar conexión de cámara**:
   ```bash
   libcamera-hello --list-cameras
   ```

## Problemas de Instalación

### El Script de Instalación Falla

#### Síntomas
- El script se detiene con errores
- Dependencias faltantes
- Permisos insuficientes

#### Soluciones

**1. Verificar Conexión a Internet**
```bash
ping -c 3 google.com
```

**2. Actualizar Lista de Paquetes**
```bash
sudo apt update
sudo apt upgrade -y
```

**3. Ejecutar como Root**
```bash
sudo ./scripts/install.sh
```

**4. Limpiar Instalación Parcial**
```bash
sudo rm -rf /home/pi/ASZCam
sudo rm -f /etc/systemd/system/asz-cam-os.service
sudo systemctl daemon-reload
```

**5. Instalación Manual Paso a Paso**
```bash
# Instalar dependencias básicas
sudo apt install -y python3 python3-pip python3-venv git

# Crear directorios
sudo mkdir -p /home/pi/ASZCam
sudo chown pi:pi /home/pi/ASZCam

# Clonar repositorio
git clone https://github.com/mynameisrober/ASZ-Cam-OS.git
cd ASZ-Cam-OS

# Ejecutar scripts individuales
sudo ./scripts/setup_rpi.sh
sudo ./scripts/download_fonts.sh
sudo ./scripts/configure_system.sh
```

### Problemas de Dependencias

#### Python/Pip Issues
```bash
# Reinstalar pip
curl https://bootstrap.pypa.io/get-pip.py | sudo python3

# Instalar dependencias del sistema
sudo apt install -y python3-dev python3-setuptools

# Limpiar caché de pip
pip cache purge
```

#### Libcamera Issues
```bash
# Instalar paquetes libcamera
sudo apt install -y libcamera-dev libcamera-apps python3-libcamera

# Habilitar cámara en raspi-config
sudo raspi-config
# Navegar a Interface Options > Camera > Enable
```

### Problemas de Permisos

#### Errores de Acceso Denegado
```bash
# Agregar usuario a grupos necesarios
sudo usermod -a -G video,camera,gpio pi

# Establecer permisos correctos
sudo chown -R pi:pi /home/pi/ASZCam
sudo chmod -R 755 /home/pi/ASZCam

# Reiniciar para aplicar cambios de grupo
sudo reboot
```

## Problemas de Arranque y Inicio

### El Sistema No Arranca

#### Síntomas
- Pantalla negra al encender
- LED rojo sólido en Raspberry Pi
- No aparece logo de arranque

#### Soluciones

**1. Verificar Fuente de Alimentación**
- Usar fuente oficial de Raspberry Pi (5V/3A)
- Verificar cable USB-C en buen estado
- LED rojo indica problemas de alimentación

**2. Verificar Tarjeta SD**
```bash
# En otra computadora, verificar la tarjeta SD
fsck -f /dev/sdX1  # Reemplazar X con la letra correcta
```

**3. Revisar config.txt**
```bash
# Montar la partición boot y verificar
sudo mount /dev/mmcblk0p1 /mnt
cat /mnt/config.txt

# Verificar configuraciones críticas
grep -E "(gpu_mem|camera|hdmi)" /mnt/config.txt
```

**4. Arranque en Modo Seguro**
```bash
# Agregar al final de /boot/cmdline.txt
systemd.unit=rescue.target

# O usar kernel de recuperación
systemd.unit=emergency.target
```

### ASZ Cam OS No Se Inicia

#### Verificar Estado del Servicio
```bash
# Verificar si el servicio está habilitado
systemctl is-enabled asz-cam-os

# Verificar estado actual
systemctl status asz-cam-os

# Ver logs del servicio
journalctl -u asz-cam-os -f
```

#### Problemas Comunes del Servicio

**1. Archivo de Servicio Faltante**
```bash
# Reinstalar archivo de servicio
sudo cp install/asz-cam-os.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable asz-cam-os
```

**2. Rutas Incorrectas en el Servicio**
```bash
# Verificar rutas en el archivo de servicio
cat /etc/systemd/system/asz-cam-os.service

# Corregir rutas si es necesario
sudo sed -i 's|{ASZ_INSTALL_DIR}|/home/pi/ASZCam|g' /etc/systemd/system/asz-cam-os.service
sudo sed -i 's|{ASZ_USER}|pi|g' /etc/systemd/system/asz-cam-os.service
```

**3. Problemas de Entorno Virtual**
```bash
# Recrear entorno virtual
rm -rf /home/pi/ASZCam/venv
python3 -m venv /home/pi/ASZCam/venv
/home/pi/ASZCam/venv/bin/pip install -r requirements.txt
```

### Arranque Lento

#### Analizar Servicios Lentos
```bash
systemd-analyze
systemd-analyze blame
systemd-analyze critical-chain
```

#### Optimizar Arranque
```bash
# Deshabilitar servicios innecesarios
sudo systemctl disable bluetooth
sudo systemctl disable hciuart
sudo systemctl disable avahi-daemon

# Reducir timeout de red
sudo systemctl edit systemd-networkd-wait-online
# Agregar:
[Service]
ExecStart=
ExecStart=/lib/systemd/systemd-networkd-wait-online --any --timeout=10
```

## Problemas de Cámara

### Cámara No Detectada

#### Verificación Básica
```bash
# Listar dispositivos de cámara
libcamera-hello --list-cameras

# Verificar dispositivos de video
ls -la /dev/video*

# Verificar módulo de cámara habilitado
vcgencmd get_camera
```

#### Conexión Física
1. **Verificar Cable de Conexión**
   - Cable flat bien conectado
   - Contactos limpios
   - Cable no dañado

2. **Verificar Puerto CSI**
   - Conectado al puerto correcto (CSI, no DSI)
   - Pestillo del conector bien cerrado

#### Configuración de Software

**1. Habilitar Cámara en raspi-config**
```bash
sudo raspi-config
# Interface Options > Camera > Enable
sudo reboot
```

**2. Verificar config.txt**
```bash
# Agregar a /boot/config.txt
camera_auto_detect=1
start_x=1
gpu_mem=128
```

**3. Instalar Libcamera**
```bash
sudo apt update
sudo apt install -y libcamera-dev libcamera-apps python3-libcamera
```

### Problemas de Calidad de Imagen

#### Imagen Borrosa o Fuera de Foco
```bash
# Probar diferentes configuraciones de enfoque
libcamera-still -o test.jpg --autofocus-mode auto
libcamera-still -o test.jpg --lens-position 0.0
libcamera-still -o test.jpg --lens-position 10.0
```

#### Exposición Incorrecta
```bash
# Configurar exposición manualmente
libcamera-still -o test.jpg --exposure 100000
libcamera-still -o test.jpg --gain 2.0
libcamera-still -o test.jpg --brightness 0.1
```

#### Balance de Blancos Incorrecto
```bash
# Probar diferentes modos de balance de blancos
libcamera-still -o test.jpg --awb daylight
libcamera-still -o test.jpg --awb indoor
libcamera-still -o test.jpg --awb cloudy
```

### Errores de Captura

#### Error "Camera Busy"
```bash
# Terminar procesos de cámara existentes
sudo pkill -f libcamera
sudo pkill -f rpicam

# Reiniciar servicio
sudo systemctl restart asz-cam-os
```

#### Error "No Space Left"
```bash
# Verificar espacio en disco
df -h /home/pi/Pictures/ASZCam

# Limpiar fotos antiguas
find /home/pi/Pictures/ASZCam -name "*.jpg" -mtime +30 -delete
```

## Problemas de Pantalla

### Pantalla en Negro

#### HDMI No Funciona
```bash
# Forzar salida HDMI en /boot/config.txt
hdmi_force_hotplug=1
hdmi_group=1
hdmi_mode=16

# Para pantalla específica
hdmi_cvt=1920 1080 60

# Reiniciar
sudo reboot
```

#### Resolución Incorrecta
```bash
# Listar modos HDMI disponibles
tvservice -m CEA
tvservice -m DMT

# Establecer modo específico
tvservice -p  # Modo preferido
tvservice -c "CEA 4 HDMI"  # 720p
tvservice -c "CEA 16 HDMI" # 1080p
```

### Pantalla Táctil No Responde

#### Verificar Conexión
```bash
# Verificar dispositivos de entrada
ls -la /dev/input/event*

# Probar eventos táctiles
sudo evtest /dev/input/event0
```

#### Calibración de Pantalla
```bash
# Instalar herramienta de calibración
sudo apt install -y xinput-calibrator

# Ejecutar calibración
DISPLAY=:0 xinput_calibrator

# Aplicar configuración generada a /etc/X11/xorg.conf.d/
```

### Problemas de X11

#### X Server No Inicia
```bash
# Verificar logs de X11
cat /var/log/Xorg.0.log

# Verificar configuración
sudo Xorg -configure

# Probar con configuración mínima
sudo X -config /etc/X11/xorg.conf
```

#### Problemas de Permisos de Display
```bash
# Agregar permisos de X11
xhost +local:

# Configurar variable DISPLAY
export DISPLAY=:0

# Para usuario pi
sudo usermod -a -G tty pi
```

## Problemas de Red y Sincronización

### Sin Conexión a Internet

#### Verificación de Red
```bash
# Verificar interfaces de red
ip link show

# Verificar configuración IP
ip addr show

# Probar DNS
nslookup google.com

# Verificar gateway
ip route show
```

#### WiFi No Conecta
```bash
# Escanear redes WiFi
sudo iwlist wlan0 scan | grep ESSID

# Configurar WiFi manualmente
sudo nano /etc/wpa_supplicant/wpa_supplicant.conf

# Agregar red:
network={
    ssid="TuRedWiFi"
    psk="TuContraseña"
    key_mgmt=WPA-PSK
}

# Reiniciar WiFi
sudo systemctl restart wpa_supplicant
```

### Problemas de Sincronización con Google Photos

#### Autenticación Falla
```bash
# Verificar archivo de credenciales
ls -la /home/pi/ASZCam/google_credentials.json
cat /home/pi/ASZCam/google_credentials.json | jq .

# Verificar permisos
chmod 600 /home/pi/ASZCam/google_credentials.json
```

#### Errores de Upload
```bash
# Verificar logs de sincronización
tail -f /var/log/aszcam/sync.log

# Verificar conectividad a Google
curl -I https://photoslibrary.googleapis.com/

# Verificar cuota de almacenamiento
# (Debe hacerse desde la interfaz de Google Photos)
```

#### Token Expirado
```bash
# Eliminar tokens existentes
rm -f /home/pi/.config/aszcam/google_tokens.json

# Reiniciar servicio para re-autenticar
sudo systemctl restart asz-cam-os
```

### Problemas de Rendimiento de Red

#### Sincronización Lenta
```bash
# Verificar velocidad de red
speedtest-cli

# Verificar latencia
ping -c 10 8.8.8.8

# Optimizar configuración de red
echo 'net.core.rmem_max = 134217728' | sudo tee -a /etc/sysctl.conf
echo 'net.core.wmem_max = 134217728' | sudo tee -a /etc/sysctl.conf
```

## Problemas de Rendimiento

### Sistema Lento

#### Verificar Uso de Recursos
```bash
# Uso de CPU y memoria
htop

# Procesos que más consumen CPU
ps aux --sort=-%cpu | head -10

# Procesos que más consumen memoria
ps aux --sort=-%mem | head -10

# Temperatura del sistema
vcgencmd measure_temp
```

#### Optimizar Rendimiento
```bash
# Aumentar memoria GPU
# En /boot/config.txt:
gpu_mem=128

# Configurar governor de CPU para rendimiento
echo performance | sudo tee /sys/devices/system/cpu/cpu0/cpufreq/scaling_governor

# Deshabilitar servicios innecesarios
sudo systemctl disable bluetooth
sudo systemctl disable avahi-daemon
```

### Problemas de Memoria

#### Memoria Insuficiente
```bash
# Verificar uso de memoria
free -h

# Agregar swap si es necesario
sudo dphys-swapfile swapoff
sudo nano /etc/dphys-swapfile
# Cambiar CONF_SWAPSIZE=1024
sudo dphys-swapfile setup
sudo dphys-swapfile swapon
```

#### Memory Leaks
```bash
# Monitorear memoria de ASZ Cam OS
watch -n 5 'ps aux | grep aszcam'

# Reiniciar servicio periódicamente si es necesario
# Agregar a crontab:
0 */6 * * * sudo systemctl restart asz-cam-os
```

### Problemas de Almacenamiento

#### Disco Lleno
```bash
# Verificar uso de disco
df -h

# Encontrar archivos grandes
sudo find / -type f -size +100M -exec ls -lh {} \;

# Limpiar archivos temporales
sudo apt clean
sudo rm -rf /tmp/*
sudo journalctl --vacuum-time=7d
```

#### Tarjeta SD Corrupta
```bash
# Verificar errores de filesystem
sudo fsck -f /dev/mmcblk0p2

# Verificar salud de la tarjeta SD
sudo badblocks -v /dev/mmcblk0
```

## Recuperación del Sistema

### Modo de Recuperación

#### Acceso por SSH
```bash
# Si SSH aún funciona
ssh pi@raspberry-pi-ip

# Verificar servicios críticos
sudo systemctl status sshd
sudo systemctl status NetworkManager
```

#### Arranque desde USB
1. Crear USB booteable con Raspberry Pi OS
2. Montar tarjeta SD desde USB boot
3. Reparar archivos necesarios

### Restaurar Configuración

#### Backup de Configuración
```bash
# Crear backup regular
tar -czf /backup/aszcam-config-$(date +%Y%m%d).tar.gz \
    /home/pi/.config/aszcam \
    /home/pi/ASZCam/google_credentials.json \
    /etc/systemd/system/asz-cam-os.service
```

#### Restaurar desde Backup
```bash
# Restaurar configuración
sudo systemctl stop asz-cam-os
tar -xzf /backup/aszcam-config-YYYYMMDD.tar.gz -C /
sudo systemctl start asz-cam-os
```

### Reinstalación Completa

#### Preservar Fotos
```bash
# Backup de fotos
rsync -av /home/pi/Pictures/ASZCam/ /backup/photos/
```

#### Reinstalación Limpia
```bash
# Eliminar instalación actual
sudo systemctl stop asz-cam-os
sudo systemctl disable asz-cam-os
sudo rm -rf /home/pi/ASZCam
sudo rm -f /etc/systemd/system/asz-cam-os.service

# Reinstalar
curl -fsSL https://raw.githubusercontent.com/mynameisrober/ASZ-Cam-OS/main/scripts/install.sh | sudo bash
```

## Diagnósticos Avanzados

### Análisis de Logs

#### Logs del Sistema
```bash
# Logs generales del sistema
journalctl --since "1 hour ago"

# Logs específicos de ASZ Cam OS
journalctl -u asz-cam-os --since "today"

# Logs de arranque
journalctl -b

# Logs con prioridad de error
journalctl -p err
```

#### Logs de Aplicación
```bash
# Logs detallados de ASZ Cam
tail -f /var/log/aszcam/aszcam.log

# Logs de sincronización
tail -f /var/log/aszcam/sync.log

# Logs de cámara
tail -f /var/log/aszcam/camera.log
```

### Debugging

#### Modo Debug
```bash
# Ejecutar ASZ Cam OS en modo debug
sudo systemctl stop asz-cam-os
cd /home/pi/ASZCam
./venv/bin/python src/main.py --debug --verbose

# O con logging detallado
ASZ_LOG_LEVEL=DEBUG ./venv/bin/python src/main.py
```

#### Profiling de Rendimiento
```bash
# Usar htop para monitoreo en tiempo real
htop

# Usar iotop para I/O
sudo iotop

# Usar nethogs para red
sudo nethogs

# Perfil de CPU con perf
sudo perf top
```

### Monitoreo Continuo

#### Scripts de Monitoreo
```bash
#!/bin/bash
# monitor_system.sh - Script de monitoreo continuo

while true; do
    echo "$(date): $(vcgencmd measure_temp), CPU: $(cat /proc/loadavg | cut -d' ' -f1)"
    echo "Memory: $(free | grep Mem | awk '{printf("%.1f%%", $3/$2 * 100.0)}')"
    echo "Disk: $(df / | tail -1 | awk '{print $5}')"
    echo "---"
    sleep 60
done > /var/log/system_monitor.log &
```

#### Alertas Automáticas
```bash
#!/bin/bash
# check_alerts.sh - Verificación de alertas del sistema

TEMP=$(vcgencmd measure_temp | cut -d'=' -f2 | cut -d"'" -f1)
DISK_USAGE=$(df / | tail -1 | awk '{print $5}' | sed 's/%//')

# Alerta de temperatura
if (( $(echo "$TEMP > 70" | bc -l) )); then
    echo "ALERTA: Temperatura alta: ${TEMP}°C" | mail -s "ASZ Cam OS Alert" admin@example.com
fi

# Alerta de disco
if [ "$DISK_USAGE" -gt 90 ]; then
    echo "ALERTA: Disco lleno: ${DISK_USAGE}%" | mail -s "ASZ Cam OS Alert" admin@example.com
fi
```

## Contacto y Soporte

### Recursos de Ayuda
- **Documentación**: [Guías completas](../README.md)
- **Issues de GitHub**: [Reportar problemas](https://github.com/mynameisrober/ASZ-Cam-OS/issues)
- **Discusiones**: [Foro de comunidad](https://github.com/mynameisrober/ASZ-Cam-OS/discussions)
- **Discord**: [Chat en tiempo real](https://discord.gg/aszcamos)

### Reportar Problemas

#### Información Requerida
Cuando reportes un problema, incluye:
1. **Versión de ASZ Cam OS**: `cat /home/pi/ASZCam/VERSION`
2. **Modelo de Raspberry Pi**: `cat /proc/cpuinfo | grep Model`
3. **Versión de OS**: `lsb_release -a`
4. **Logs relevantes**: `journalctl -u asz-cam-os --since "1 hour ago"`
5. **Pasos para reproducir**: Descripción detallada
6. **Comportamiento esperado**: Qué debería pasar
7. **Comportamiento actual**: Qué está pasando

#### Template de Issue
```markdown
## Descripción del Problema
[Descripción clara del problema]

## Pasos para Reproducir
1. [Primer paso]
2. [Segundo paso]
3. [Ver error]

## Comportamiento Esperado
[Qué debería pasar]

## Comportamiento Actual
[Qué está pasando]

## Información del Sistema
- ASZ Cam OS Version: [versión]
- Raspberry Pi Model: [modelo]
- OS Version: [versión]

## Logs
```
[Pegar logs relevantes aquí]
```

## Capturas de Pantalla
[Si aplica]
```

---

Esta guía cubre los problemas más comunes con ASZ Cam OS. Si tu problema no está listado aquí, por favor consulta la documentación completa o contacta el soporte de la comunidad.