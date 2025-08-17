#!/usr/bin/env python3
"""
ASZ Cam OS - Automated System Tests
Comprehensive testing suite for validating ASZ Cam OS functionality.

Author: ASZ Development Team
Version: 1.0.0
"""

import os
import sys
import json
import time
import logging
import subprocess
import tempfile
from pathlib import Path
from typing import Dict, List, Any, Tuple, Optional
from dataclasses import dataclass, asdict
from datetime import datetime
import argparse

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

try:
    import requests
    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False

try:
    from PIL import Image
    HAS_PIL = True
except ImportError:
    HAS_PIL = False


@dataclass
class TestResult:
    """Test result data structure."""
    test_name: str
    status: str  # PASS, FAIL, SKIP
    message: str
    duration: float
    details: Optional[Dict[str, Any]] = None


class TestRunner:
    """Main test runner for ASZ Cam OS system tests."""
    
    def __init__(self, verbose: bool = False):
        self.verbose = verbose
        self.results: List[TestResult] = []
        self.setup_logging()
        
        # Test configuration
        self.test_config = {
            'timeout': 30,
            'temp_dir': tempfile.mkdtemp(prefix='aszcam_test_'),
            'mock_mode': not self._is_raspberry_pi()
        }
        
    def setup_logging(self):
        """Configure logging for test runner."""
        level = logging.DEBUG if self.verbose else logging.INFO
        logging.basicConfig(
            level=level,
            format='%(asctime)s - %(levelname)s - %(message)s',
            datefmt='%H:%M:%S'
        )
        self.logger = logging.getLogger(__name__)
        
    def _is_raspberry_pi(self) -> bool:
        """Check if running on Raspberry Pi."""
        try:
            with open('/proc/cpuinfo', 'r') as f:
                cpuinfo = f.read()
                return 'Raspberry Pi' in cpuinfo or 'BCM' in cpuinfo
        except:
            return False
    
    def run_command(self, cmd: List[str], timeout: int = 10) -> Tuple[int, str, str]:
        """Run a command and return exit code, stdout, stderr."""
        try:
            result = subprocess.run(
                cmd, 
                timeout=timeout,
                capture_output=True,
                text=True
            )
            return result.returncode, result.stdout, result.stderr
        except subprocess.TimeoutExpired:
            return -1, "", "Command timed out"
        except Exception as e:
            return -1, "", str(e)
    
    def test_system_prerequisites(self) -> TestResult:
        """Test system prerequisites and dependencies."""
        start_time = time.time()
        
        try:
            details = {}
            issues = []
            
            # Check Python version
            python_version = sys.version_info
            details['python_version'] = f"{python_version.major}.{python_version.minor}.{python_version.micro}"
            if python_version < (3, 9):
                issues.append(f"Python version {details['python_version']} < 3.9")
            
            # Check essential commands
            essential_commands = ['systemctl', 'python3', 'pip3']
            for cmd in essential_commands:
                exit_code, _, _ = self.run_command(['which', cmd])
                details[f'{cmd}_available'] = exit_code == 0
                if exit_code != 0:
                    issues.append(f"Command '{cmd}' not found")
            
            # Check if running as root when needed
            details['is_root'] = os.geteuid() == 0
            
            # Check available disk space
            statvfs = os.statvfs('/')
            available_gb = (statvfs.f_bavail * statvfs.f_frsize) / (1024**3)
            details['available_disk_gb'] = round(available_gb, 2)
            if available_gb < 2:
                issues.append(f"Low disk space: {available_gb:.1f}GB available")
            
            # Check Raspberry Pi specific items
            if not self.test_config['mock_mode']:
                # Check camera interface
                exit_code, _, _ = self.run_command(['which', 'libcamera-hello'])
                details['libcamera_available'] = exit_code == 0
                if exit_code != 0:
                    issues.append("libcamera tools not found")
                
                # Check GPU memory
                exit_code, stdout, _ = self.run_command(['vcgencmd', 'get_mem', 'gpu'])
                if exit_code == 0:
                    details['gpu_memory'] = stdout.strip()
                else:
                    issues.append("Cannot check GPU memory")
            
            duration = time.time() - start_time
            
            if issues:
                return TestResult(
                    test_name="system_prerequisites",
                    status="FAIL",
                    message=f"Issues found: {'; '.join(issues)}",
                    duration=duration,
                    details=details
                )
            else:
                return TestResult(
                    test_name="system_prerequisites",
                    status="PASS",
                    message="All system prerequisites met",
                    duration=duration,
                    details=details
                )
                
        except Exception as e:
            return TestResult(
                test_name="system_prerequisites",
                status="FAIL",
                message=f"Test failed with exception: {e}",
                duration=time.time() - start_time
            )
    
    def test_installation_integrity(self) -> TestResult:
        """Test ASZ Cam OS installation integrity."""
        start_time = time.time()
        
        try:
            details = {}
            issues = []
            
            # Expected directory structure
            base_dir = Path("/home/pi/ASZCam")
            expected_paths = {
                'base_directory': base_dir,
                'src_directory': base_dir / 'src',
                'venv_directory': base_dir / 'venv',
                'main_script': base_dir / 'src' / 'main.py',
                'python_binary': base_dir / 'venv' / 'bin' / 'python',
                'requirements_file': base_dir / 'requirements.txt'
            }
            
            for name, path in expected_paths.items():
                exists = path.exists()
                details[f'{name}_exists'] = exists
                if not exists:
                    issues.append(f"Missing: {path}")
            
            # Check virtual environment functionality
            if expected_paths['python_binary'].exists():
                exit_code, stdout, stderr = self.run_command([
                    str(expected_paths['python_binary']), 
                    '-c', 
                    'import sys; print(sys.executable)'
                ])
                details['venv_python_works'] = exit_code == 0
                if exit_code != 0:
                    issues.append(f"Virtual environment Python not working: {stderr}")
            
            # Check systemd service
            exit_code, stdout, stderr = self.run_command(['systemctl', 'is-enabled', 'asz-cam-os'])
            details['service_enabled'] = exit_code == 0
            if exit_code != 0:
                issues.append("ASZ Cam OS service not enabled")
            
            exit_code, stdout, stderr = self.run_command(['systemctl', 'is-active', 'asz-cam-os'])
            details['service_active'] = stdout.strip() == 'active'
            
            # Check file permissions
            if base_dir.exists():
                stat = base_dir.stat()
                details['ownership_correct'] = stat.st_uid == 1000  # pi user
                if stat.st_uid != 1000:
                    issues.append("Incorrect file ownership")
            
            duration = time.time() - start_time
            
            if issues:
                return TestResult(
                    test_name="installation_integrity",
                    status="FAIL", 
                    message=f"Installation issues: {'; '.join(issues)}",
                    duration=duration,
                    details=details
                )
            else:
                return TestResult(
                    test_name="installation_integrity",
                    status="PASS",
                    message="Installation integrity verified",
                    duration=duration,
                    details=details
                )
                
        except Exception as e:
            return TestResult(
                test_name="installation_integrity",
                status="FAIL",
                message=f"Test failed with exception: {e}",
                duration=time.time() - start_time
            )
    
    def test_python_dependencies(self) -> TestResult:
        """Test Python dependencies and imports."""
        start_time = time.time()
        
        try:
            details = {}
            issues = []
            
            # Test critical imports
            python_executable = "/home/pi/ASZCam/venv/bin/python"
            if not Path(python_executable).exists():
                python_executable = sys.executable
            
            critical_imports = [
                'PyQt6.QtCore',
                'PyQt6.QtWidgets', 
                'PyQt6.QtGui',
                'PIL',
                'numpy',
                'yaml'
            ]
            
            for module in critical_imports:
                exit_code, stdout, stderr = self.run_command([
                    python_executable,
                    '-c',
                    f'import {module}; print("OK")'
                ])
                
                module_key = module.replace('.', '_')
                details[f'{module_key}_import'] = exit_code == 0
                
                if exit_code != 0:
                    issues.append(f"Cannot import {module}: {stderr}")
            
            # Test optional imports
            optional_imports = [
                'google.auth',
                'googleapiclient',
                'requests'
            ]
            
            for module in optional_imports:
                exit_code, stdout, stderr = self.run_command([
                    python_executable,
                    '-c',
                    f'import {module}; print("OK")'
                ])
                
                module_key = module.replace('.', '_')
                details[f'{module_key}_import'] = exit_code == 0
                
                if exit_code != 0:
                    self.logger.warning(f"Optional import {module} failed: {stderr}")
            
            # Test ASZ Cam OS imports
            aszcam_imports = [
                'src.config.settings',
                'src.core.system_manager'
            ]
            
            original_path = sys.path.copy()
            sys.path.insert(0, '/home/pi/ASZCam')
            
            for module in aszcam_imports:
                try:
                    __import__(module)
                    module_key = module.replace('.', '_')
                    details[f'{module_key}_import'] = True
                except ImportError as e:
                    module_key = module.replace('.', '_')
                    details[f'{module_key}_import'] = False
                    issues.append(f"Cannot import {module}: {e}")
            
            sys.path = original_path
            
            duration = time.time() - start_time
            
            if issues:
                return TestResult(
                    test_name="python_dependencies",
                    status="FAIL",
                    message=f"Dependency issues: {'; '.join(issues)}",
                    duration=duration,
                    details=details
                )
            else:
                return TestResult(
                    test_name="python_dependencies", 
                    status="PASS",
                    message="All Python dependencies available",
                    duration=duration,
                    details=details
                )
                
        except Exception as e:
            return TestResult(
                test_name="python_dependencies",
                status="FAIL",
                message=f"Test failed with exception: {e}",
                duration=time.time() - start_time
            )
    
    def test_camera_hardware(self) -> TestResult:
        """Test camera hardware functionality."""
        start_time = time.time()
        
        try:
            details = {}
            issues = []
            
            if self.test_config['mock_mode']:
                return TestResult(
                    test_name="camera_hardware",
                    status="SKIP",
                    message="Skipped on non-Raspberry Pi system",
                    duration=time.time() - start_time
                )
            
            # Check if libcamera tools are available
            exit_code, stdout, stderr = self.run_command(['which', 'libcamera-hello'])
            details['libcamera_tools_available'] = exit_code == 0
            
            if exit_code != 0:
                return TestResult(
                    test_name="camera_hardware",
                    status="FAIL",
                    message="libcamera tools not available",
                    duration=time.time() - start_time,
                    details=details
                )
            
            # List available cameras
            exit_code, stdout, stderr = self.run_command(['libcamera-hello', '--list-cameras'], timeout=15)
            details['camera_list_success'] = exit_code == 0
            details['camera_list_output'] = stdout
            
            if exit_code != 0:
                issues.append(f"Cannot list cameras: {stderr}")
            else:
                # Parse camera output
                if "Available cameras" in stdout:
                    camera_count = stdout.count(")")  # Each camera ends with )
                    details['camera_count'] = camera_count
                    if camera_count == 0:
                        issues.append("No cameras detected")
                else:
                    issues.append("Unexpected camera list output")
            
            # Test basic camera functionality if camera detected
            if details.get('camera_count', 0) > 0:
                test_image_path = Path(self.test_config['temp_dir']) / 'test_capture.jpg'
                
                exit_code, stdout, stderr = self.run_command([
                    'libcamera-still',
                    '-o', str(test_image_path),
                    '--timeout', '2000',
                    '--width', '640',
                    '--height', '480'
                ], timeout=10)
                
                details['test_capture_success'] = exit_code == 0
                
                if exit_code == 0:
                    # Verify image was created and has reasonable size
                    if test_image_path.exists():
                        file_size = test_image_path.stat().st_size
                        details['test_image_size'] = file_size
                        
                        if file_size < 1000:  # Less than 1KB is suspicious
                            issues.append(f"Test image too small: {file_size} bytes")
                        
                        # Try to open with PIL if available
                        if HAS_PIL:
                            try:
                                with Image.open(test_image_path) as img:
                                    details['test_image_dimensions'] = img.size
                                    details['test_image_format'] = img.format
                            except Exception as e:
                                issues.append(f"Cannot open test image: {e}")
                        
                        # Clean up test image
                        test_image_path.unlink()
                    else:
                        issues.append("Test image was not created")
                else:
                    issues.append(f"Test capture failed: {stderr}")
            
            duration = time.time() - start_time
            
            if issues:
                return TestResult(
                    test_name="camera_hardware",
                    status="FAIL",
                    message=f"Camera issues: {'; '.join(issues)}",
                    duration=duration,
                    details=details
                )
            else:
                return TestResult(
                    test_name="camera_hardware",
                    status="PASS",
                    message=f"Camera hardware working ({details.get('camera_count', 0)} cameras)",
                    duration=duration,
                    details=details
                )
                
        except Exception as e:
            return TestResult(
                test_name="camera_hardware",
                status="FAIL", 
                message=f"Test failed with exception: {e}",
                duration=time.time() - start_time
            )
    
    def test_network_connectivity(self) -> TestResult:
        """Test network connectivity and internet access."""
        start_time = time.time()
        
        try:
            details = {}
            issues = []
            
            # Test basic connectivity
            exit_code, stdout, stderr = self.run_command(['ping', '-c', '3', '8.8.8.8'], timeout=15)
            details['ping_success'] = exit_code == 0
            
            if exit_code != 0:
                issues.append("No internet connectivity (ping failed)")
            
            # Test DNS resolution
            exit_code, stdout, stderr = self.run_command(['nslookup', 'www.google.com'], timeout=10)
            details['dns_resolution'] = exit_code == 0
            
            if exit_code != 0:
                issues.append("DNS resolution failed")
            
            # Test HTTPS connectivity to Google APIs if requests available
            if HAS_REQUESTS:
                try:
                    response = requests.get('https://www.googleapis.com', timeout=10)
                    details['google_apis_reachable'] = response.status_code == 200
                    details['google_apis_status_code'] = response.status_code
                    
                    if response.status_code != 200:
                        issues.append(f"Google APIs not reachable (status: {response.status_code})")
                        
                except Exception as e:
                    details['google_apis_reachable'] = False
                    issues.append(f"Cannot reach Google APIs: {e}")
            else:
                details['requests_available'] = False
                self.logger.warning("requests module not available for HTTP testing")
            
            # Check network interfaces
            exit_code, stdout, stderr = self.run_command(['ip', 'addr', 'show'])
            details['network_interfaces_listed'] = exit_code == 0
            
            if exit_code == 0:
                # Parse for active interfaces
                active_interfaces = []
                for line in stdout.split('\n'):
                    if 'state UP' in line:
                        interface = line.split(':')[1].strip()
                        active_interfaces.append(interface)
                
                details['active_interfaces'] = active_interfaces
                details['interface_count'] = len(active_interfaces)
                
                if not active_interfaces:
                    issues.append("No active network interfaces")
            
            duration = time.time() - start_time
            
            if issues:
                return TestResult(
                    test_name="network_connectivity",
                    status="FAIL",
                    message=f"Network issues: {'; '.join(issues)}",
                    duration=duration,
                    details=details
                )
            else:
                return TestResult(
                    test_name="network_connectivity",
                    status="PASS",
                    message="Network connectivity verified",
                    duration=duration,
                    details=details
                )
                
        except Exception as e:
            return TestResult(
                test_name="network_connectivity",
                status="FAIL",
                message=f"Test failed with exception: {e}",
                duration=time.time() - start_time
            )
    
    def test_service_functionality(self) -> TestResult:
        """Test ASZ Cam OS service functionality."""
        start_time = time.time()
        
        try:
            details = {}
            issues = []
            
            # Check service status
            exit_code, stdout, stderr = self.run_command(['systemctl', 'is-active', 'asz-cam-os'])
            service_active = stdout.strip() == 'active'
            details['service_active'] = service_active
            
            exit_code, stdout, stderr = self.run_command(['systemctl', 'is-enabled', 'asz-cam-os'])
            service_enabled = exit_code == 0
            details['service_enabled'] = service_enabled
            
            if not service_enabled:
                issues.append("Service not enabled for auto-start")
            
            # Get detailed service status
            exit_code, stdout, stderr = self.run_command(['systemctl', 'status', 'asz-cam-os', '--no-pager'])
            details['service_status_output'] = stdout
            
            # Check for recent errors in logs
            exit_code, stdout, stderr = self.run_command([
                'journalctl', '-u', 'asz-cam-os', '--since', '5 minutes ago', '--no-pager'
            ])
            
            if exit_code == 0:
                error_lines = [line for line in stdout.split('\n') if 'ERROR' in line or 'CRITICAL' in line]
                details['recent_errors'] = len(error_lines)
                details['recent_error_lines'] = error_lines[-5:]  # Last 5 errors
                
                if error_lines:
                    issues.append(f"Recent errors in logs: {len(error_lines)}")
            
            # If service is active, test if it's responding
            if service_active:
                # Check if the process is running
                exit_code, stdout, stderr = self.run_command(['pgrep', '-f', 'asz-cam-os'])
                process_running = exit_code == 0
                details['process_running'] = process_running
                
                if not process_running:
                    issues.append("Service marked active but process not found")
                else:
                    # Get process details
                    exit_code, stdout, stderr = self.run_command(['ps', 'aux'])
                    if exit_code == 0:
                        aszcam_processes = [line for line in stdout.split('\n') if 'ASZCam' in line or 'asz-cam' in line]
                        details['aszcam_processes'] = len(aszcam_processes)
            else:
                issues.append("Service is not active")
            
            duration = time.time() - start_time
            
            if issues:
                return TestResult(
                    test_name="service_functionality",
                    status="FAIL",
                    message=f"Service issues: {'; '.join(issues)}",
                    duration=duration,
                    details=details
                )
            else:
                return TestResult(
                    test_name="service_functionality",
                    status="PASS",
                    message="Service functioning correctly",
                    duration=duration,
                    details=details
                )
                
        except Exception as e:
            return TestResult(
                test_name="service_functionality",
                status="FAIL",
                message=f"Test failed with exception: {e}",
                duration=time.time() - start_time
            )
    
    def test_storage_and_permissions(self) -> TestResult:
        """Test storage setup and file permissions."""
        start_time = time.time()
        
        try:
            details = {}
            issues = []
            
            # Check required directories
            required_dirs = [
                Path("/home/pi/ASZCam"),
                Path("/home/pi/Pictures/ASZCam"),
                Path("/home/pi/.config/aszcam"),
                Path("/var/log/aszcam")
            ]
            
            for directory in required_dirs:
                exists = directory.exists()
                details[f'{directory.name}_exists'] = exists
                
                if exists:
                    # Check permissions
                    stat = directory.stat()
                    details[f'{directory.name}_owner'] = stat.st_uid
                    details[f'{directory.name}_permissions'] = oct(stat.st_mode)[-3:]
                    
                    # Check if writable by pi user (uid 1000)
                    writable = os.access(directory, os.W_OK)
                    details[f'{directory.name}_writable'] = writable
                    
                    if not writable:
                        issues.append(f"Directory {directory} not writable")
                else:
                    issues.append(f"Required directory {directory} does not exist")
            
            # Test file creation in photos directory
            photos_dir = Path("/home/pi/Pictures/ASZCam")
            if photos_dir.exists():
                test_file = photos_dir / f"test_{int(time.time())}.txt"
                try:
                    test_file.write_text("test content")
                    details['photo_dir_write_test'] = True
                    test_file.unlink()  # Clean up
                except Exception as e:
                    details['photo_dir_write_test'] = False
                    issues.append(f"Cannot write to photos directory: {e}")
            
            # Check available storage space
            for path in [Path("/"), Path("/home")]:
                if path.exists():
                    statvfs = os.statvfs(str(path))
                    available_gb = (statvfs.f_bavail * statvfs.f_frsize) / (1024**3)
                    total_gb = (statvfs.f_blocks * statvfs.f_frsize) / (1024**3)
                    
                    details[f'{path.name or "root"}_available_gb'] = round(available_gb, 2)
                    details[f'{path.name or "root"}_total_gb'] = round(total_gb, 2)
                    details[f'{path.name or "root"}_usage_percent'] = round((1 - available_gb/total_gb) * 100, 1)
                    
                    if available_gb < 1:
                        issues.append(f"Low storage on {path}: {available_gb:.1f}GB available")
            
            duration = time.time() - start_time
            
            if issues:
                return TestResult(
                    test_name="storage_and_permissions",
                    status="FAIL",
                    message=f"Storage issues: {'; '.join(issues)}",
                    duration=duration,
                    details=details
                )
            else:
                return TestResult(
                    test_name="storage_and_permissions",
                    status="PASS",
                    message="Storage and permissions correct",
                    duration=duration,
                    details=details
                )
                
        except Exception as e:
            return TestResult(
                test_name="storage_and_permissions",
                status="FAIL",
                message=f"Test failed with exception: {e}",
                duration=time.time() - start_time
            )
    
    def run_all_tests(self) -> List[TestResult]:
        """Run all system tests."""
        self.logger.info("Starting ASZ Cam OS system tests...")
        self.logger.info(f"Test configuration: {self.test_config}")
        
        # Define test sequence
        tests = [
            self.test_system_prerequisites,
            self.test_installation_integrity, 
            self.test_python_dependencies,
            self.test_camera_hardware,
            self.test_network_connectivity,
            self.test_service_functionality,
            self.test_storage_and_permissions
        ]
        
        # Run tests
        for test_func in tests:
            self.logger.info(f"Running test: {test_func.__name__}")
            result = test_func()
            self.results.append(result)
            
            # Log test result
            status_color = {
                'PASS': '\033[92m',  # Green
                'FAIL': '\033[91m',  # Red  
                'SKIP': '\033[93m'   # Yellow
            }
            reset_color = '\033[0m'
            
            color = status_color.get(result.status, '')
            self.logger.info(
                f"Test {result.test_name}: {color}{result.status}{reset_color} "
                f"({result.duration:.2f}s) - {result.message}"
            )
            
            if self.verbose and result.details:
                self.logger.debug(f"Test details: {result.details}")
        
        return self.results
    
    def generate_report(self) -> Dict[str, Any]:
        """Generate comprehensive test report."""
        if not self.results:
            return {}
        
        # Calculate summary statistics
        total_tests = len(self.results)
        passed_tests = len([r for r in self.results if r.status == 'PASS'])
        failed_tests = len([r for r in self.results if r.status == 'FAIL'])
        skipped_tests = len([r for r in self.results if r.status == 'SKIP'])
        total_duration = sum(r.duration for r in self.results)
        
        # Overall status
        overall_status = 'PASS' if failed_tests == 0 else 'FAIL'
        
        # Generate report
        report = {
            'timestamp': datetime.now().isoformat(),
            'system_info': {
                'is_raspberry_pi': not self.test_config['mock_mode'],
                'python_version': f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
                'platform': sys.platform
            },
            'summary': {
                'overall_status': overall_status,
                'total_tests': total_tests,
                'passed_tests': passed_tests,
                'failed_tests': failed_tests,
                'skipped_tests': skipped_tests,
                'total_duration': round(total_duration, 2),
                'success_rate': round((passed_tests / total_tests) * 100, 1) if total_tests > 0 else 0
            },
            'test_results': [asdict(result) for result in self.results]
        }
        
        return report
    
    def cleanup(self):
        """Clean up test resources."""
        import shutil
        if Path(self.test_config['temp_dir']).exists():
            shutil.rmtree(self.test_config['temp_dir'])
        self.logger.info("Test cleanup completed")


def main():
    """Main test runner entry point."""
    parser = argparse.ArgumentParser(description='ASZ Cam OS System Tests')
    parser.add_argument('-v', '--verbose', action='store_true', help='Verbose output')
    parser.add_argument('-o', '--output', help='Output file for JSON report')
    parser.add_argument('--mock', action='store_true', help='Force mock mode (non-Pi testing)')
    
    args = parser.parse_args()
    
    # Initialize test runner
    runner = TestRunner(verbose=args.verbose)
    
    if args.mock:
        runner.test_config['mock_mode'] = True
    
    try:
        # Run tests
        results = runner.run_all_tests()
        
        # Generate report
        report = runner.generate_report()
        
        # Output report
        if args.output:
            with open(args.output, 'w') as f:
                json.dump(report, f, indent=2)
            print(f"Report saved to: {args.output}")
        
        # Print summary
        summary = report['summary']
        print(f"\n{'='*50}")
        print(f"ASZ Cam OS System Test Results")
        print(f"{'='*50}")
        print(f"Overall Status: {summary['overall_status']}")
        print(f"Tests: {summary['passed_tests']}/{summary['total_tests']} passed")
        print(f"Success Rate: {summary['success_rate']}%")
        print(f"Total Duration: {summary['total_duration']}s")
        
        if summary['failed_tests'] > 0:
            print(f"\nFailed Tests:")
            for result in results:
                if result.status == 'FAIL':
                    print(f"  - {result.test_name}: {result.message}")
        
        # Return appropriate exit code
        sys.exit(0 if summary['overall_status'] == 'PASS' else 1)
        
    finally:
        runner.cleanup()


if __name__ == "__main__":
    main()
