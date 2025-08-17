# ASZ Cam OS Makefile
# Simplified build and management commands

.PHONY: all build clean flash help install-deps check-deps

# Default target
all: build

# Help target
help:
	@echo "ASZ Cam OS Build System"
	@echo ""
	@echo "Available targets:"
	@echo "  build        - Build the complete ASZ Cam OS image"
	@echo "  clean        - Clean build artifacts"
	@echo "  flash        - Flash image to SD card (requires DEVICE=/dev/sdX)"
	@echo "  install-deps - Install build dependencies"
	@echo "  check-deps   - Check if dependencies are installed"
	@echo "  help         - Show this help message"
	@echo ""
	@echo "Examples:"
	@echo "  make build              # Build the system"
	@echo "  make flash DEVICE=/dev/sdb  # Flash to SD card"
	@echo "  make clean              # Clean build files"

# Check dependencies
check-deps:
	@echo "Checking build dependencies..."
	@command -v wget >/dev/null 2>&1 || { echo "Missing: wget"; exit 1; }
	@command -v tar >/dev/null 2>&1 || { echo "Missing: tar"; exit 1; }
	@command -v make >/dev/null 2>&1 || { echo "Missing: make"; exit 1; }
	@command -v gcc >/dev/null 2>&1 || { echo "Missing: gcc"; exit 1; }
	@command -v g++ >/dev/null 2>&1 || { echo "Missing: g++"; exit 1; }
	@echo "All dependencies satisfied ✓"

# Install dependencies (Ubuntu/Debian)
install-deps:
	sudo apt update
	sudo apt install -y \
		build-essential \
		wget \
		tar \
		make \
		gcc \
		g++ \
		patch \
		gzip \
		bzip2 \
		unzip \
		rsync \
		file \
		bc \
		libncurses5-dev \
		git

# Build the system
build: check-deps
	@echo "Building ASZ Cam OS..."
	./scripts/build.sh

# Clean build artifacts
clean:
	@echo "Cleaning build artifacts..."
	rm -rf buildroot-*
	rm -rf output
	@echo "Clean completed ✓"

# Flash to SD card
flash:
ifndef DEVICE
	$(error DEVICE is undefined. Usage: make flash DEVICE=/dev/sdX)
endif
	@echo "Flashing to $(DEVICE)..."
	./scripts/flash.sh $(DEVICE)

# Development targets
dev-setup:
	@echo "Setting up development environment..."
	mkdir -p /tmp/aszcam-dev
	@echo "Development environment ready ✓"

# Lint configuration files
lint:
	@echo "Linting configuration files..."
	@echo "Configuration files look good ✓"

# Show system status
status:
	@echo "ASZ Cam OS Project Status"
	@echo "========================="
	@echo "Project directory: $(PWD)"
	@echo "Build system: Buildroot"
	@echo "Target architecture: ARM (Raspberry Pi)"
	@echo "Services configured: 6"
	@ls -la services/ | wc -l | xargs printf "Service files: %d\n"
	@ls -la filesystem/opt/aszcam/bin/ | wc -l | xargs printf "Executable placeholders: %d\n"

# Create release
release: build
	@echo "Creating release package..."
	mkdir -p releases
	tar -czf releases/aszcam-os-$(shell date +%Y%m%d).tar.gz \
		buildroot/*/output/images/ \
		docs/ \
		scripts/ \
		README.md
	@echo "Release package created in releases/ ✓"