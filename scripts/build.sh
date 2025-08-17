#!/bin/bash
# ASZ Cam OS - Build Script
# Script para compilar y generar la imagen del sistema operativo

set -e

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
BUILD_DIR="$PROJECT_ROOT/build"
BUILDROOT_VERSION="2023.11"
BUILDROOT_DIR="$BUILD_DIR/buildroot-$BUILDROOT_VERSION"

echo "ASZ Cam OS - Build Script"
echo "========================="

# Crear directorio de build
mkdir -p "$BUILD_DIR"
cd "$BUILD_DIR"

# Descargar buildroot si no existe
if [ ! -d "$BUILDROOT_DIR" ]; then
    echo "Descargando Buildroot $BUILDROOT_VERSION..."
    wget "https://buildroot.org/downloads/buildroot-$BUILDROOT_VERSION.tar.gz"
    tar -xzf "buildroot-$BUILDROOT_VERSION.tar.gz"
    rm "buildroot-$BUILDROOT_VERSION.tar.gz"
fi

cd "$BUILDROOT_DIR"

# Copiar configuración personalizada
echo "Configurando ASZ Cam OS..."
cp "$PROJECT_ROOT/buildroot/asz_cam_defconfig" "configs/asz_cam_defconfig"

# Crear directorio overlay
OVERLAY_DIR="$BUILDROOT_DIR/board/asz-cam/overlay"
mkdir -p "$OVERLAY_DIR/opt/asz-cam-os"
mkdir -p "$OVERLAY_DIR/etc/systemd/system"
mkdir -p "$OVERLAY_DIR/home/asz"

# Copiar aplicación
cp -r "$PROJECT_ROOT/src"/* "$OVERLAY_DIR/opt/asz-cam-os/"
cp "$PROJECT_ROOT/main.py" "$OVERLAY_DIR/opt/asz-cam-os/"
cp "$PROJECT_ROOT/requirements.txt" "$OVERLAY_DIR/opt/asz-cam-os/"
chmod +x "$OVERLAY_DIR/opt/asz-cam-os/main.py"

# Copiar configuración systemd
cp "$PROJECT_ROOT/configs/systemd/asz-cam.service" "$OVERLAY_DIR/etc/systemd/system/"

# Copiar assets
cp -r "$PROJECT_ROOT/assets" "$OVERLAY_DIR/opt/asz-cam-os/"

# Configurar buildroot
echo "Aplicando configuración..."
make asz_cam_defconfig

# Mostrar configuración
echo "Configuración aplicada. Para compilar:"
echo "  cd $BUILDROOT_DIR"
echo "  make menuconfig  # (opcional, para modificar configuración)"
echo "  make -j\$(nproc)   # compilar (puede tomar 1-2 horas)"
echo ""
echo "La imagen resultante estará en:"
echo "  $BUILDROOT_DIR/output/images/"

# Opción para compilar directamente
read -p "¿Quieres compilar ahora? (esto puede tomar 1-2 horas) [y/N]: " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "Iniciando compilación..."
    make -j$(nproc)
    
    echo ""
    echo "¡Compilación completada!"
    echo "Imagen generada en: $BUILDROOT_DIR/output/images/"
    echo ""
    echo "Para crear SD card:"
    echo "  sudo dd if=output/images/sdcard.img of=/dev/sdX bs=4M status=progress"
    echo "  (reemplaza /dev/sdX con tu tarjeta SD)"
fi