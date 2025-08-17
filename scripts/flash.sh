#!/bin/bash
# ASZ Cam OS Flash Script
# Script to flash the generated image to SD card

set -e

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
BUILDROOT_DIR="$PROJECT_DIR/buildroot-2023.02.8"
IMAGE_DIR="$BUILDROOT_DIR/output/images"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

log() {
    echo -e "${GREEN}[FLASH]${NC} $1"
}

warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1"
    exit 1
}

usage() {
    echo "Usage: $0 <device>"
    echo ""
    echo "Example: $0 /dev/sdb"
    echo ""
    echo "Available devices:"
    lsblk -d -o NAME,SIZE,MODEL | grep -E "sd[a-z]|mmcblk"
    exit 1
}

check_device() {
    local device="$1"
    
    if [ ! -b "$device" ]; then
        error "Device $device does not exist or is not a block device"
    fi
    
    if mount | grep -q "$device"; then
        error "Device $device is currently mounted. Please unmount it first."
    fi
    
    log "Device $device looks good for flashing"
}

flash_image() {
    local device="$1"
    local image="$IMAGE_DIR/rootfs.ext2"
    
    if [ ! -f "$image" ]; then
        error "Image not found at $image. Please build the system first."
    fi
    
    warn "This will COMPLETELY ERASE $device!"
    warn "All data on $device will be lost!"
    read -p "Are you sure you want to continue? [y/N]: " -n 1 -r
    echo
    
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        log "Aborted by user"
        exit 0
    fi
    
    log "Flashing ASZ Cam OS to $device..."
    log "Image: $image"
    
    # Flash the image
    sudo dd if="$image" of="$device" bs=4M conv=fsync status=progress
    sync
    
    log "Flashing completed successfully!"
    log "You can now safely remove the SD card and insert it into your Raspberry Pi"
}

main() {
    if [ $# -ne 1 ]; then
        usage
    fi
    
    local device="$1"
    
    log "Starting ASZ Cam OS flash process..."
    check_device "$device"
    flash_image "$device"
    log "Flash process completed!"
}

main "$@"