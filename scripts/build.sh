#!/bin/bash
# ASZ Cam OS Build Script
# Main build script for generating the custom OS image

set -e

# Configuration
BUILDROOT_VERSION="2023.02.8"
BUILDROOT_DIR="buildroot-${BUILDROOT_VERSION}"
OUTPUT_DIR="output"
CONFIG_NAME="aszcam_defconfig"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

log() {
    echo -e "${GREEN}[BUILD]${NC} $1"
}

warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1"
    exit 1
}

# Check dependencies
check_dependencies() {
    log "Checking build dependencies..."
    
    local deps=("wget" "tar" "make" "gcc" "g++" "patch" "gzip" "bzip2" "unzip" "rsync" "file" "bc")
    for dep in "${deps[@]}"; do
        if ! command -v "$dep" &> /dev/null; then
            error "Missing dependency: $dep"
        fi
    done
    
    log "All dependencies satisfied"
}

# Download and setup buildroot
setup_buildroot() {
    if [ ! -d "$BUILDROOT_DIR" ]; then
        log "Downloading Buildroot ${BUILDROOT_VERSION}..."
        wget -O buildroot.tar.xz "https://buildroot.org/downloads/buildroot-${BUILDROOT_VERSION}.tar.xz"
        tar -xf buildroot.tar.xz
        rm buildroot.tar.xz
    fi
    
    log "Setting up ASZ Cam external tree..."
    export BR2_EXTERNAL="$(pwd)"
    cd "$BUILDROOT_DIR"
}

# Configure buildroot
configure_buildroot() {
    log "Configuring buildroot with ASZ Cam settings..."
    make BR2_EXTERNAL="$(pwd)/.." "${CONFIG_NAME}"
}

# Build the system
build_system() {
    log "Starting ASZ Cam OS build process..."
    log "This may take 1-3 hours depending on your system..."
    
    make -j$(nproc)
    
    log "Build completed successfully!"
}

# Post-build setup
post_build() {
    log "Setting up ASZ Cam specific configurations..."
    
    # Copy systemd services
    mkdir -p "${OUTPUT_DIR}/target/etc/systemd/system"
    cp ../services/*.service "${OUTPUT_DIR}/target/etc/systemd/system/"
    
    # Create ASZ Cam directories
    mkdir -p "${OUTPUT_DIR}/target/opt/aszcam"/{bin,lib,config,ui,plugins}
    mkdir -p "${OUTPUT_DIR}/target/var/aszcam"/{photos,cache,logs,sync}
    
    # Set permissions
    chroot "${OUTPUT_DIR}/target" /bin/bash -c "
        groupadd -r aszcam
        useradd -r -g aszcam -d /opt/aszcam -s /bin/false aszcam
        chown -R aszcam:aszcam /opt/aszcam /var/aszcam
        chmod 755 /opt/aszcam/bin
        chmod 644 /opt/aszcam/config
    "
    
    log "Post-build configuration completed"
}

# Main execution
main() {
    log "Starting ASZ Cam OS build process..."
    
    check_dependencies
    setup_buildroot
    configure_buildroot
    build_system
    post_build
    
    log "ASZ Cam OS build completed!"
    log "Image available at: ${BUILDROOT_DIR}/${OUTPUT_DIR}/images/"
}

# Execute main function
main "$@"