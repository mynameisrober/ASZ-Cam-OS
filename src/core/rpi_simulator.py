"""
ASZ Cam OS - Raspberry Pi Simulator
Simulates Raspberry Pi specific hardware and system functionality for development environments.
Provides mock implementations for GPIO, system info, and other Pi-specific features.

Author: ASZ Development Team
Version: 1.0.0
"""

import logging
import time
import threading
import random
import json
import platform
import psutil
import os
import sys
from typing import Dict, Any, List, Optional, Union
from pathlib import Path
from dataclasses import dataclass, asdict


@dataclass
class GPIOPin:
    """Mock GPIO pin state."""
    number: int
    mode: str = 'IN'  # 'IN', 'OUT'
    value: bool = False
    pull: str = 'OFF'  # 'UP', 'DOWN', 'OFF'
    function: str = 'GPIO'


@dataclass
class SystemInfo:
    """Mock Raspberry Pi system information."""
    model: str = "Raspberry Pi 4 Model B Rev 1.4 (Mock)"
    serial: str = "000000001234abcd"
    revision: str = "c03114"
    memory_gb: int = 4
    cpu_model: str = "BCM2711"
    cpu_cores: int = 4
    cpu_max_freq_mhz: int = 1500
    gpu_memory_mb: int = 128
    bootloader_version: str = "2024.01.15"
    firmware_version: str = "1.20240115"


class RPiSimulator:
    """Raspberry Pi hardware and system simulator for development."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.is_simulation = True
        
        # GPIO state simulation
        self.gpio_pins: Dict[int, GPIOPin] = {}
        self.gpio_initialized = False
        self.gpio_lock = threading.Lock()
        
        # System information
        self.system_info = SystemInfo()
        
        # Mock sensors and hardware states
        self.temperature_c = 45.0  # CPU temperature
        self.voltage_v = 5.1  # Input voltage
        self.throttle_state = 0x0  # No throttling
        
        # Camera-related hardware state
        self.camera_led_state = False
        self.camera_interface_enabled = True
        
        # Storage and memory simulation
        self.storage_stats = {
            'root_total_gb': 32.0,
            'root_used_gb': 8.5,
            'boot_total_mb': 256.0,
            'boot_used_mb': 45.0
        }
        
        # Network interface simulation
        self.network_interfaces = {
            'eth0': {
                'type': 'ethernet',
                'mac': '01:23:45:67:89:ab',
                'ip': '192.168.1.100',
                'status': 'up',
                'speed_mbps': 100
            },
            'wlan0': {
                'type': 'wifi',
                'mac': 'b8:27:eb:12:34:56', 
                'ip': '192.168.1.101',
                'status': 'up',
                'signal_strength': -45,
                'ssid': 'MockNetwork'
            }
        }
        
        # Service states
        self.services_state = {
            'ssh': 'active',
            'bluetooth': 'inactive', 
            'camera': 'active',
            'i2c': 'active',
            'spi': 'inactive'
        }
        
        self.logger.info("RPi Simulator initialized")
    
    def is_raspberry_pi(self) -> bool:
        """Always returns True in simulation mode."""
        return True
    
    def get_system_info(self) -> Dict[str, Any]:
        """Get simulated Raspberry Pi system information."""
        # Add some dynamic values
        current_info = asdict(self.system_info)
        current_info.update({
            'uptime_seconds': int(time.time() % 86400),  # Mock uptime
            'load_average': [0.15, 0.25, 0.30],
            'cpu_temp_c': self.get_cpu_temperature(),
            'voltage_v': self.get_voltage(),
            'throttle_state': self.throttle_state,
            'is_simulation': True
        })
        
        return current_info
    
    def get_cpu_info(self) -> Dict[str, Any]:
        """Get CPU information."""
        return {
            'model': self.system_info.cpu_model,
            'cores': self.system_info.cpu_cores,
            'max_frequency_mhz': self.system_info.cpu_max_freq_mhz,
            'current_frequency_mhz': random.randint(600, self.system_info.cpu_max_freq_mhz),
            'usage_percent': psutil.cpu_percent(),
            'temperature_c': self.get_cpu_temperature()
        }
    
    def get_cpu_temperature(self) -> float:
        """Get simulated CPU temperature."""
        # Simulate temperature variation
        base_temp = 45.0
        variation = random.uniform(-5.0, 15.0)
        self.temperature_c = max(35.0, min(75.0, base_temp + variation))
        return round(self.temperature_c, 1)
    
    def get_voltage(self) -> float:
        """Get simulated input voltage."""
        # Simulate slight voltage variations
        base_voltage = 5.1
        variation = random.uniform(-0.1, 0.1)
        self.voltage_v = max(4.8, min(5.4, base_voltage + variation))
        return round(self.voltage_v, 2)
    
    def get_memory_info(self) -> Dict[str, Any]:
        """Get memory information."""
        # Get actual system memory but present it as Pi memory
        memory = psutil.virtual_memory()
        
        return {
            'total_mb': self.system_info.memory_gb * 1024,
            'available_mb': int(memory.available / 1024 / 1024),
            'used_mb': int(memory.used / 1024 / 1024),
            'percent': memory.percent,
            'gpu_memory_mb': self.system_info.gpu_memory_mb,
            'gpu_memory_split': f"{self.system_info.gpu_memory_mb}MB"
        }
    
    def get_storage_info(self) -> Dict[str, Any]:
        """Get storage information."""
        # Simulate Pi storage layout
        return {
            'root_partition': {
                'total_gb': self.storage_stats['root_total_gb'],
                'used_gb': self.storage_stats['root_used_gb'],
                'available_gb': self.storage_stats['root_total_gb'] - self.storage_stats['root_used_gb'],
                'usage_percent': (self.storage_stats['root_used_gb'] / self.storage_stats['root_total_gb']) * 100
            },
            'boot_partition': {
                'total_mb': self.storage_stats['boot_total_mb'],
                'used_mb': self.storage_stats['boot_used_mb'],
                'available_mb': self.storage_stats['boot_total_mb'] - self.storage_stats['boot_used_mb']
            },
            'sd_card_health': 'Good',
            'mount_points': {
                '/': f"{self.storage_stats['root_used_gb']:.1f}GB / {self.storage_stats['root_total_gb']:.1f}GB",
                '/boot': f"{self.storage_stats['boot_used_mb']:.0f}MB / {self.storage_stats['boot_total_mb']:.0f}MB"
            }
        }
    
    def get_network_info(self) -> Dict[str, Any]:
        """Get network interface information."""
        return {
            'interfaces': self.network_interfaces,
            'hostname': 'aszcam-dev',
            'default_route': '192.168.1.1'
        }
    
    # GPIO Simulation
    def gpio_setup(self, pin: int, mode: str, pull_up_down: str = 'OFF') -> bool:
        """Setup a GPIO pin."""
        try:
            with self.gpio_lock:
                if not self.gpio_initialized:
                    self.gpio_initialized = True
                    self.logger.debug("Mock GPIO initialized")
                
                self.gpio_pins[pin] = GPIOPin(
                    number=pin,
                    mode=mode,
                    pull=pull_up_down
                )
                
                self.logger.debug(f"GPIO pin {pin} setup: mode={mode}, pull={pull_up_down}")
                return True
                
        except Exception as e:
            self.logger.error(f"GPIO setup failed for pin {pin}: {e}")
            return False
    
    def gpio_output(self, pin: int, value: bool) -> bool:
        """Set GPIO pin output value."""
        try:
            with self.gpio_lock:
                if pin not in self.gpio_pins:
                    self.logger.error(f"GPIO pin {pin} not setup")
                    return False
                
                gpio_pin = self.gpio_pins[pin]
                if gpio_pin.mode != 'OUT':
                    self.logger.error(f"GPIO pin {pin} not configured for output")
                    return False
                
                gpio_pin.value = value
                
                # Special handling for camera LED
                if pin == 32:  # Common camera LED pin
                    self.camera_led_state = value
                    self.logger.debug(f"Camera LED: {'ON' if value else 'OFF'}")
                
                self.logger.debug(f"GPIO pin {pin} output: {value}")
                return True
                
        except Exception as e:
            self.logger.error(f"GPIO output failed for pin {pin}: {e}")
            return False
    
    def gpio_input(self, pin: int) -> Optional[bool]:
        """Read GPIO pin input value."""
        try:
            with self.gpio_lock:
                if pin not in self.gpio_pins:
                    self.logger.error(f"GPIO pin {pin} not setup")
                    return None
                
                gpio_pin = self.gpio_pins[pin]
                if gpio_pin.mode != 'IN':
                    self.logger.error(f"GPIO pin {pin} not configured for input")
                    return None
                
                # Simulate input reading with some randomness for switches/buttons
                if gpio_pin.pull == 'UP':
                    # Pull-up: normally high, occasionally low
                    gpio_pin.value = random.random() > 0.1
                elif gpio_pin.pull == 'DOWN':
                    # Pull-down: normally low, occasionally high  
                    gpio_pin.value = random.random() > 0.9
                else:
                    # No pull: random floating value
                    gpio_pin.value = random.choice([True, False])
                
                self.logger.debug(f"GPIO pin {pin} input: {gpio_pin.value}")
                return gpio_pin.value
                
        except Exception as e:
            self.logger.error(f"GPIO input failed for pin {pin}: {e}")
            return None
    
    def gpio_cleanup(self, pin: Optional[int] = None):
        """Cleanup GPIO pins."""
        try:
            with self.gpio_lock:
                if pin is not None:
                    if pin in self.gpio_pins:
                        del self.gpio_pins[pin]
                        self.logger.debug(f"GPIO pin {pin} cleaned up")
                else:
                    self.gpio_pins.clear()
                    self.gpio_initialized = False
                    self.logger.debug("All GPIO pins cleaned up")
                    
        except Exception as e:
            self.logger.error(f"GPIO cleanup failed: {e}")
    
    def get_gpio_state(self) -> Dict[int, Dict[str, Any]]:
        """Get current state of all GPIO pins."""
        with self.gpio_lock:
            return {pin: asdict(gpio_pin) for pin, gpio_pin in self.gpio_pins.items()}
    
    # Camera Hardware Simulation
    def is_camera_enabled(self) -> bool:
        """Check if camera interface is enabled."""
        return self.camera_interface_enabled
    
    def enable_camera(self) -> bool:
        """Enable camera interface."""
        self.camera_interface_enabled = True
        self.logger.info("Camera interface enabled")
        return True
    
    def disable_camera(self) -> bool:
        """Disable camera interface."""
        self.camera_interface_enabled = False
        self.logger.info("Camera interface disabled") 
        return True
    
    def get_camera_led_state(self) -> bool:
        """Get camera LED state."""
        return self.camera_led_state
    
    def set_camera_led(self, state: bool) -> bool:
        """Set camera LED state."""
        self.camera_led_state = state
        # Also update GPIO pin if it exists
        if 32 in self.gpio_pins:
            self.gpio_pins[32].value = state
        self.logger.debug(f"Camera LED: {'ON' if state else 'OFF'}")
        return True
    
    # System Services Simulation
    def get_service_status(self, service: str) -> Optional[str]:
        """Get system service status."""
        return self.services_state.get(service)
    
    def start_service(self, service: str) -> bool:
        """Start a system service."""
        if service in self.services_state:
            self.services_state[service] = 'active'
            self.logger.info(f"Service {service} started")
            return True
        return False
    
    def stop_service(self, service: str) -> bool:
        """Stop a system service."""
        if service in self.services_state:
            self.services_state[service] = 'inactive'
            self.logger.info(f"Service {service} stopped")
            return True
        return False
    
    def get_all_services_status(self) -> Dict[str, str]:
        """Get status of all monitored services."""
        return self.services_state.copy()
    
    # Boot Configuration Simulation
    def read_boot_config(self) -> Dict[str, Any]:
        """Read simulated boot configuration."""
        return {
            'camera_auto_detect': 1,
            'start_x': 1,
            'gpu_mem': self.system_info.gpu_memory_mb,
            'disable_overscan': 1,
            'hdmi_force_hotplug': 1,
            'hdmi_group': 2,
            'hdmi_mode': 82,  # 1080p 60Hz
            'dtparam': ['i2c_arm=on', 'spi=on'],
            'enable_uart': 1
        }
    
    def write_boot_config(self, config: Dict[str, Any]) -> bool:
        """Write boot configuration (simulated)."""
        # In simulation, just validate and log
        required_keys = ['gpu_mem', 'camera_auto_detect']
        
        for key in required_keys:
            if key not in config:
                self.logger.error(f"Missing required boot config key: {key}")
                return False
        
        self.logger.info(f"Boot configuration updated (simulated): {config}")
        return True
    
    # Hardware Detection
    def detect_hardware(self) -> Dict[str, Any]:
        """Detect available hardware components."""
        return {
            'camera': {
                'detected': True,
                'model': 'Mock Pi Camera v2.1',
                'interface': 'CSI'
            },
            'audio': {
                'detected': True,
                'devices': ['bcm2835-audio', 'USB Audio']
            },
            'i2c': {
                'detected': True,
                'devices': []  # Would list I2C devices
            },
            'spi': {
                'detected': True,
                'devices': []
            },
            'gpio': {
                'detected': True,
                'pins_available': 40,
                'pins_in_use': list(self.gpio_pins.keys())
            },
            'usb': {
                'ports': 4,
                'devices': []  # Would list USB devices
            }
        }
    
    # Performance Monitoring
    def get_performance_stats(self) -> Dict[str, Any]:
        """Get system performance statistics."""
        return {
            'cpu': self.get_cpu_info(),
            'memory': self.get_memory_info(),
            'storage': self.get_storage_info(),
            'temperature': {
                'cpu': self.get_cpu_temperature(),
                'gpu': self.get_cpu_temperature() - 5.0  # GPU usually runs cooler
            },
            'voltage': {
                'core': self.get_voltage(),
                'sdram_c': self.get_voltage() - 0.1,
                'sdram_i': self.get_voltage() - 0.15
            },
            'throttling': {
                'current': False,
                'has_occurred': False,
                'state': self.throttle_state
            }
        }
    
    def set_performance_governor(self, governor: str) -> bool:
        """Set CPU performance governor."""
        valid_governors = ['ondemand', 'performance', 'powersave', 'conservative']
        if governor in valid_governors:
            self.logger.info(f"CPU governor set to: {governor}")
            return True
        return False
    
    # System Control
    def reboot_system(self, delay_seconds: int = 0) -> bool:
        """Simulate system reboot."""
        self.logger.warning(f"System reboot requested (simulated) - delay: {delay_seconds}s")
        # In simulation mode, just log and return
        return True
    
    def shutdown_system(self, delay_seconds: int = 0) -> bool:
        """Simulate system shutdown."""
        self.logger.warning(f"System shutdown requested (simulated) - delay: {delay_seconds}s")
        return True
    
    # Utility Methods
    def run_vcgencmd(self, command: str) -> Optional[str]:
        """Simulate vcgencmd output."""
        vcgen_commands = {
            'measure_temp': f"temp={self.get_cpu_temperature()}'C",
            'measure_volts core': f"volt={self.get_voltage()}V",
            'get_mem gpu': f"gpu={self.system_info.gpu_memory_mb}M",
            'get_mem arm': f"arm={self.system_info.memory_gb * 1024 - self.system_info.gpu_memory_mb}M",
            'get_throttled': f"throttled={hex(self.throttle_state)}",
            'version': f"version={self.system_info.firmware_version}"
        }
        
        result = vcgen_commands.get(command)
        if result:
            self.logger.debug(f"vcgencmd {command}: {result}")
        else:
            self.logger.warning(f"Unknown vcgencmd command: {command}")
        
        return result
    
    def get_device_tree_info(self) -> Dict[str, Any]:
        """Get device tree information."""
        return {
            'model': self.system_info.model,
            'serial': self.system_info.serial,
            'revision': self.system_info.revision,
            'compatible': 'raspberrypi,4-model-b',
            'bootloader': {
                'version': self.system_info.bootloader_version,
                'date': '2024-01-15'
            }
        }
    
    def cleanup(self):
        """Clean up simulator resources."""
        try:
            self.gpio_cleanup()
            self.logger.info("RPi Simulator cleanup completed")
        except Exception as e:
            self.logger.error(f"RPi Simulator cleanup failed: {e}")


# Global simulator instance
rpi_simulator = RPiSimulator()