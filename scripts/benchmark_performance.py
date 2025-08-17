#!/usr/bin/env python3
"""
ASZ Cam OS - Performance Benchmark Suite
Comprehensive performance testing and benchmarking for ASZ Cam OS.

Author: ASZ Development Team
Version: 1.0.0
"""

import os
import sys
import time
import json
import psutil
import threading
import subprocess
import tempfile
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from datetime import datetime
import argparse

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

try:
    import numpy as np
    HAS_NUMPY = True
except ImportError:
    HAS_NUMPY = False

try:
    from PIL import Image
    HAS_PIL = True
except ImportError:
    HAS_PIL = False


@dataclass
class BenchmarkResult:
    """Benchmark result data structure."""
    test_name: str
    duration: float
    operations_per_second: float
    memory_used_mb: float
    cpu_percent: float
    details: Dict[str, Any]
    status: str = "PASS"  # PASS, FAIL, SKIP


class PerformanceMonitor:
    """System performance monitoring utility."""
    
    def __init__(self):
        self.monitoring = False
        self.samples = []
        self.monitor_thread = None
    
    def start(self):
        """Start performance monitoring."""
        self.monitoring = True
        self.samples = []
        self.monitor_thread = threading.Thread(target=self._monitor_loop)
        self.monitor_thread.daemon = True
        self.monitor_thread.start()
    
    def stop(self):
        """Stop performance monitoring and return statistics."""
        self.monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=1)
        
        if not self.samples:
            return {}
        
        # Calculate statistics
        cpu_values = [s['cpu_percent'] for s in self.samples]
        memory_values = [s['memory_mb'] for s in self.samples]
        
        return {
            'avg_cpu_percent': sum(cpu_values) / len(cpu_values),
            'max_cpu_percent': max(cpu_values),
            'avg_memory_mb': sum(memory_values) / len(memory_values),
            'max_memory_mb': max(memory_values),
            'sample_count': len(self.samples)
        }
    
    def _monitor_loop(self):
        """Background monitoring loop."""
        while self.monitoring:
            try:
                sample = {
                    'timestamp': time.time(),
                    'cpu_percent': psutil.cpu_percent(),
                    'memory_mb': psutil.virtual_memory().used / 1024 / 1024
                }
                self.samples.append(sample)
                time.sleep(0.1)  # Sample every 100ms
            except:
                break


class BenchmarkSuite:
    """Main benchmark suite for ASZ Cam OS."""
    
    def __init__(self, verbose: bool = False):
        self.verbose = verbose
        self.results: List[BenchmarkResult] = []
        self.system_info = self._gather_system_info()
        
        # Test configuration
        self.config = {
            'temp_dir': tempfile.mkdtemp(prefix='aszcam_bench_'),
            'is_raspberry_pi': self._is_raspberry_pi(),
            'test_iterations': 10,
            'image_sizes': [(640, 480), (1920, 1080), (3840, 2160)]
        }
        
        if self.verbose:
            print(f"Benchmark configuration: {self.config}")
            print(f"System info: {self.system_info}")
    
    def _is_raspberry_pi(self) -> bool:
        """Check if running on Raspberry Pi."""
        try:
            with open('/proc/cpuinfo', 'r') as f:
                cpuinfo = f.read()
                return 'Raspberry Pi' in cpuinfo or 'BCM' in cpuinfo
        except:
            return False
    
    def _gather_system_info(self) -> Dict[str, Any]:
        """Gather system information."""
        info = {
            'cpu_count': psutil.cpu_count(),
            'memory_total_gb': psutil.virtual_memory().total / 1024 / 1024 / 1024,
            'python_version': sys.version,
            'platform': sys.platform
        }
        
        # Raspberry Pi specific info
        if self._is_raspberry_pi():
            try:
                # Get Pi model
                with open('/proc/device-tree/model', 'r') as f:
                    info['pi_model'] = f.read().strip('\x00')
            except:
                info['pi_model'] = 'Unknown Pi Model'
            
            try:
                # Get GPU memory
                result = subprocess.run(['vcgencmd', 'get_mem', 'gpu'], 
                                      capture_output=True, text=True)
                if result.returncode == 0:
                    info['gpu_memory'] = result.stdout.strip()
            except:
                pass
            
            try:
                # Get CPU temperature
                result = subprocess.run(['vcgencmd', 'measure_temp'], 
                                      capture_output=True, text=True)
                if result.returncode == 0:
                    info['cpu_temp'] = result.stdout.strip()
            except:
                pass
        
        return info
    
    def benchmark_boot_time(self) -> BenchmarkResult:
        """Benchmark system boot time (estimated)."""
        start_time = time.time()
        
        try:
            details = {}
            
            # Get system uptime
            uptime_seconds = time.time() - psutil.boot_time()
            details['system_uptime_seconds'] = uptime_seconds
            
            # Try to get systemd boot analysis
            try:
                result = subprocess.run(['systemd-analyze'], capture_output=True, text=True, timeout=10)
                if result.returncode == 0:
                    boot_time_line = result.stdout.split('\n')[0]
                    details['systemd_boot_analysis'] = boot_time_line
                    
                    # Extract boot time if possible
                    if 'finished in' in boot_time_line:
                        # Parse something like "Startup finished in 2.5s (kernel) + 8.2s (userspace) = 10.7s"
                        parts = boot_time_line.split('=')
                        if len(parts) > 1:
                            total_time_str = parts[-1].strip().replace('s', '')
                            try:
                                boot_time = float(total_time_str)
                                details['estimated_boot_time_seconds'] = boot_time
                            except ValueError:
                                pass
            except:
                pass
            
            # Check service startup times
            try:
                result = subprocess.run(['systemd-analyze', 'blame'], 
                                      capture_output=True, text=True, timeout=10)
                if result.returncode == 0:
                    lines = result.stdout.split('\n')[:10]  # Top 10 slowest
                    details['slowest_services'] = lines
            except:
                pass
            
            duration = time.time() - start_time
            
            # Estimate performance based on boot time
            estimated_boot = details.get('estimated_boot_time_seconds', uptime_seconds)
            ops_per_sec = 1.0 / max(estimated_boot, 1.0)  # Inverse of boot time
            
            return BenchmarkResult(
                test_name="boot_time",
                duration=duration,
                operations_per_second=ops_per_sec,
                memory_used_mb=0,
                cpu_percent=0,
                details=details
            )
            
        except Exception as e:
            return BenchmarkResult(
                test_name="boot_time",
                duration=time.time() - start_time,
                operations_per_second=0,
                memory_used_mb=0,
                cpu_percent=0,
                details={'error': str(e)},
                status="FAIL"
            )
    
    def benchmark_cpu_performance(self) -> BenchmarkResult:
        """Benchmark CPU performance."""
        start_time = time.time()
        monitor = PerformanceMonitor()
        
        try:
            monitor.start()
            
            # CPU intensive calculation
            iterations = 1000000
            total = 0
            
            for i in range(iterations):
                total += i * i
            
            monitor_stats = monitor.stop()
            duration = time.time() - start_time
            
            details = {
                'iterations': iterations,
                'result': total,
                'monitor_stats': monitor_stats
            }
            
            ops_per_sec = iterations / duration
            
            return BenchmarkResult(
                test_name="cpu_performance",
                duration=duration,
                operations_per_second=ops_per_sec,
                memory_used_mb=monitor_stats.get('avg_memory_mb', 0),
                cpu_percent=monitor_stats.get('avg_cpu_percent', 0),
                details=details
            )
            
        except Exception as e:
            monitor.stop()
            return BenchmarkResult(
                test_name="cpu_performance",
                duration=time.time() - start_time,
                operations_per_second=0,
                memory_used_mb=0,
                cpu_percent=0,
                details={'error': str(e)},
                status="FAIL"
            )
    
    def benchmark_memory_performance(self) -> BenchmarkResult:
        """Benchmark memory allocation and access performance."""
        start_time = time.time()
        monitor = PerformanceMonitor()
        
        try:
            monitor.start()
            
            # Memory intensive operations
            arrays = []
            array_size = 100000  # 100K elements
            num_arrays = 50
            
            # Allocate memory
            for i in range(num_arrays):
                if HAS_NUMPY:
                    arr = np.random.rand(array_size)
                else:
                    arr = [float(j) for j in range(array_size)]
                arrays.append(arr)
            
            # Access memory (sum operations)
            total_sum = 0
            for arr in arrays:
                if HAS_NUMPY:
                    total_sum += np.sum(arr)
                else:
                    total_sum += sum(arr)
            
            # Cleanup
            del arrays
            
            monitor_stats = monitor.stop()
            duration = time.time() - start_time
            
            details = {
                'array_size': array_size,
                'num_arrays': num_arrays,
                'total_elements': array_size * num_arrays,
                'result_sum': total_sum,
                'monitor_stats': monitor_stats,
                'numpy_available': HAS_NUMPY
            }
            
            ops_per_sec = (array_size * num_arrays) / duration
            
            return BenchmarkResult(
                test_name="memory_performance",
                duration=duration,
                operations_per_second=ops_per_sec,
                memory_used_mb=monitor_stats.get('avg_memory_mb', 0),
                cpu_percent=monitor_stats.get('avg_cpu_percent', 0),
                details=details
            )
            
        except Exception as e:
            monitor.stop()
            return BenchmarkResult(
                test_name="memory_performance",
                duration=time.time() - start_time,
                operations_per_second=0,
                memory_used_mb=0,
                cpu_percent=0,
                details={'error': str(e)},
                status="FAIL"
            )
    
    def benchmark_disk_io(self) -> BenchmarkResult:
        """Benchmark disk I/O performance."""
        start_time = time.time()
        monitor = PerformanceMonitor()
        
        try:
            monitor.start()
            
            temp_dir = Path(self.config['temp_dir'])
            test_file = temp_dir / 'disk_benchmark.dat'
            
            # Test parameters
            file_size_mb = 10  # 10MB test file
            block_size = 1024 * 1024  # 1MB blocks
            test_data = b'A' * block_size
            
            # Write test
            write_start = time.time()
            with open(test_file, 'wb') as f:
                for _ in range(file_size_mb):
                    f.write(test_data)
                f.flush()
                os.fsync(f.fileno())  # Ensure data is written to disk
            write_duration = time.time() - write_start
            
            # Read test
            read_start = time.time()
            read_data = []
            with open(test_file, 'rb') as f:
                while True:
                    chunk = f.read(block_size)
                    if not chunk:
                        break
                    read_data.append(chunk)
            read_duration = time.time() - read_start
            
            # Cleanup
            test_file.unlink()
            
            monitor_stats = monitor.stop()
            duration = time.time() - start_time
            
            details = {
                'file_size_mb': file_size_mb,
                'write_duration': write_duration,
                'read_duration': read_duration,
                'write_speed_mbps': file_size_mb / write_duration,
                'read_speed_mbps': file_size_mb / read_duration,
                'monitor_stats': monitor_stats
            }
            
            # Operations per second based on total MB processed
            ops_per_sec = (file_size_mb * 2) / duration  # Read + Write
            
            return BenchmarkResult(
                test_name="disk_io",
                duration=duration,
                operations_per_second=ops_per_sec,
                memory_used_mb=monitor_stats.get('avg_memory_mb', 0),
                cpu_percent=monitor_stats.get('avg_cpu_percent', 0),
                details=details
            )
            
        except Exception as e:
            monitor.stop()
            return BenchmarkResult(
                test_name="disk_io",
                duration=time.time() - start_time,
                operations_per_second=0,
                memory_used_mb=0,
                cpu_percent=0,
                details={'error': str(e)},
                status="FAIL"
            )
    
    def benchmark_image_processing(self) -> BenchmarkResult:
        """Benchmark image processing performance."""
        start_time = time.time()
        monitor = PerformanceMonitor()
        
        try:
            if not HAS_PIL:
                return BenchmarkResult(
                    test_name="image_processing",
                    duration=0,
                    operations_per_second=0,
                    memory_used_mb=0,
                    cpu_percent=0,
                    details={'error': 'PIL not available'},
                    status="SKIP"
                )
            
            monitor.start()
            
            temp_dir = Path(self.config['temp_dir'])
            operations_count = 0
            
            details = {'size_results': {}}
            
            # Test different image sizes
            for width, height in self.config['image_sizes']:
                size_start = time.time()
                
                # Create test image
                if HAS_NUMPY:
                    # Create with numpy for better performance
                    image_data = np.random.randint(0, 256, (height, width, 3), dtype=np.uint8)
                    img = Image.fromarray(image_data)
                else:
                    # Create solid color image
                    img = Image.new('RGB', (width, height), color='red')
                
                # Perform various operations
                operations = [
                    lambda x: x.resize((x.width // 2, x.height // 2)),  # Resize
                    lambda x: x.rotate(45),  # Rotate
                    lambda x: x.convert('L'),  # Convert to grayscale
                ]
                
                processed_images = []
                for op in operations:
                    processed = op(img.copy())
                    processed_images.append(processed)
                    operations_count += 1
                
                # Save and load test
                test_file = temp_dir / f'test_image_{width}x{height}.jpg'
                img.save(test_file, 'JPEG', quality=85)
                loaded_img = Image.open(test_file)
                operations_count += 2  # Save + Load
                
                # Cleanup
                test_file.unlink()
                
                size_duration = time.time() - size_start
                details['size_results'][f'{width}x{height}'] = {
                    'duration': size_duration,
                    'operations': len(operations) + 2
                }
            
            monitor_stats = monitor.stop()
            duration = time.time() - start_time
            
            details['total_operations'] = operations_count
            details['monitor_stats'] = monitor_stats
            details['numpy_available'] = HAS_NUMPY
            
            ops_per_sec = operations_count / duration
            
            return BenchmarkResult(
                test_name="image_processing",
                duration=duration,
                operations_per_second=ops_per_sec,
                memory_used_mb=monitor_stats.get('avg_memory_mb', 0),
                cpu_percent=monitor_stats.get('avg_cpu_percent', 0),
                details=details
            )
            
        except Exception as e:
            monitor.stop()
            return BenchmarkResult(
                test_name="image_processing",
                duration=time.time() - start_time,
                operations_per_second=0,
                memory_used_mb=0,
                cpu_percent=0,
                details={'error': str(e)},
                status="FAIL"
            )
    
    def benchmark_camera_simulation(self) -> BenchmarkResult:
        """Benchmark camera simulation (image generation and processing)."""
        start_time = time.time()
        monitor = PerformanceMonitor()
        
        try:
            monitor.start()
            
            # Simulate camera operations
            num_frames = 30  # Simulate 30 frames
            frame_width, frame_height = 1920, 1080
            
            frames_processed = 0
            
            if HAS_PIL and HAS_NUMPY:
                for frame_num in range(num_frames):
                    # Generate random frame data (simulating camera capture)
                    frame_data = np.random.randint(0, 256, (frame_height, frame_width, 3), dtype=np.uint8)
                    
                    # Convert to PIL Image (simulating camera API)
                    frame = Image.fromarray(frame_data)
                    
                    # Simulate preview processing (resize for display)
                    preview = frame.resize((640, 480))
                    
                    # Simulate photo processing (compress and save)
                    temp_file = Path(self.config['temp_dir']) / f'frame_{frame_num}.jpg'
                    frame.save(temp_file, 'JPEG', quality=85, optimize=True)
                    
                    # Cleanup
                    temp_file.unlink()
                    
                    frames_processed += 1
                    
                    # Small delay to simulate frame rate
                    time.sleep(0.01)
            else:
                # Fallback without numpy/PIL
                for frame_num in range(num_frames):
                    # Simulate some processing work
                    dummy_data = [i * frame_num for i in range(1000)]
                    processed = sum(dummy_data)
                    frames_processed += 1
                    time.sleep(0.01)
            
            monitor_stats = monitor.stop()
            duration = time.time() - start_time
            
            details = {
                'frames_processed': frames_processed,
                'frame_size': f'{frame_width}x{frame_height}',
                'average_fps': frames_processed / duration,
                'monitor_stats': monitor_stats,
                'has_imaging_libs': HAS_PIL and HAS_NUMPY
            }
            
            ops_per_sec = frames_processed / duration
            
            return BenchmarkResult(
                test_name="camera_simulation",
                duration=duration,
                operations_per_second=ops_per_sec,
                memory_used_mb=monitor_stats.get('avg_memory_mb', 0),
                cpu_percent=monitor_stats.get('avg_cpu_percent', 0),
                details=details
            )
            
        except Exception as e:
            monitor.stop()
            return BenchmarkResult(
                test_name="camera_simulation",
                duration=time.time() - start_time,
                operations_per_second=0,
                memory_used_mb=0,
                cpu_percent=0,
                details={'error': str(e)},
                status="FAIL"
            )
    
    def benchmark_network_simulation(self) -> BenchmarkResult:
        """Benchmark network simulation (file transfer simulation)."""
        start_time = time.time()
        monitor = PerformanceMonitor()
        
        try:
            monitor.start()
            
            # Simulate network operations
            file_sizes_mb = [1, 5, 10]  # Different file sizes
            total_operations = 0
            
            details = {'file_transfers': []}
            
            for file_size in file_sizes_mb:
                transfer_start = time.time()
                
                # Create test data
                test_data = b'X' * (file_size * 1024 * 1024)  # MB of data
                
                # Simulate compression (like photo upload)
                compressed_size = len(test_data) // 4  # Simulate 4:1 compression
                
                # Simulate network delay
                time.sleep(0.1 * file_size)  # 100ms per MB
                
                transfer_duration = time.time() - transfer_start
                transfer_speed_mbps = file_size / transfer_duration
                
                details['file_transfers'].append({
                    'size_mb': file_size,
                    'duration': transfer_duration,
                    'speed_mbps': transfer_speed_mbps,
                    'compressed_size': compressed_size
                })
                
                total_operations += 1
            
            monitor_stats = monitor.stop()
            duration = time.time() - start_time
            
            details['total_operations'] = total_operations
            details['monitor_stats'] = monitor_stats
            details['average_speed_mbps'] = sum(t['speed_mbps'] for t in details['file_transfers']) / len(details['file_transfers'])
            
            ops_per_sec = total_operations / duration
            
            return BenchmarkResult(
                test_name="network_simulation",
                duration=duration,
                operations_per_second=ops_per_sec,
                memory_used_mb=monitor_stats.get('avg_memory_mb', 0),
                cpu_percent=monitor_stats.get('avg_cpu_percent', 0),
                details=details
            )
            
        except Exception as e:
            monitor.stop()
            return BenchmarkResult(
                test_name="network_simulation",
                duration=time.time() - start_time,
                operations_per_second=0,
                memory_used_mb=0,
                cpu_percent=0,
                details={'error': str(e)},
                status="FAIL"
            )
    
    def run_all_benchmarks(self) -> List[BenchmarkResult]:
        """Run all benchmark tests."""
        print("Starting ASZ Cam OS performance benchmarks...")
        print(f"System: {self.system_info.get('pi_model', 'Generic System')}")
        print(f"CPU Cores: {self.system_info['cpu_count']}")
        print(f"Memory: {self.system_info['memory_total_gb']:.1f} GB")
        print()
        
        # Define benchmark sequence
        benchmarks = [
            ("Boot Time Analysis", self.benchmark_boot_time),
            ("CPU Performance", self.benchmark_cpu_performance),
            ("Memory Performance", self.benchmark_memory_performance),
            ("Disk I/O Performance", self.benchmark_disk_io),
            ("Image Processing", self.benchmark_image_processing),
            ("Camera Simulation", self.benchmark_camera_simulation),
            ("Network Simulation", self.benchmark_network_simulation)
        ]
        
        # Run benchmarks
        for name, benchmark_func in benchmarks:
            print(f"Running {name}...", end=" ", flush=True)
            
            try:
                result = benchmark_func()
                self.results.append(result)
                
                status_symbol = {
                    'PASS': '✓',
                    'FAIL': '✗',
                    'SKIP': '⊝'
                }
                
                print(f"{status_symbol.get(result.status, '?')} "
                      f"({result.duration:.2f}s, {result.operations_per_second:.1f} ops/s)")
                
                if self.verbose and result.details:
                    print(f"   Details: {result.details}")
                
            except Exception as e:
                print(f"✗ ERROR: {e}")
                result = BenchmarkResult(
                    test_name=benchmark_func.__name__,
                    duration=0,
                    operations_per_second=0,
                    memory_used_mb=0,
                    cpu_percent=0,
                    details={'error': str(e)},
                    status="FAIL"
                )
                self.results.append(result)
        
        return self.results
    
    def generate_report(self) -> Dict[str, Any]:
        """Generate comprehensive benchmark report."""
        if not self.results:
            return {}
        
        # Calculate summary statistics
        total_duration = sum(r.duration for r in self.results)
        avg_ops_per_sec = sum(r.operations_per_second for r in self.results) / len(self.results)
        avg_memory_mb = sum(r.memory_used_mb for r in self.results) / len(self.results)
        avg_cpu_percent = sum(r.cpu_percent for r in self.results) / len(self.results)
        
        passed_tests = len([r for r in self.results if r.status == 'PASS'])
        failed_tests = len([r for r in self.results if r.status == 'FAIL'])
        skipped_tests = len([r for r in self.results if r.status == 'SKIP'])
        
        # Generate report
        report = {
            'timestamp': datetime.now().isoformat(),
            'system_info': self.system_info,
            'config': self.config,
            'summary': {
                'total_benchmarks': len(self.results),
                'passed_benchmarks': passed_tests,
                'failed_benchmarks': failed_tests,
                'skipped_benchmarks': skipped_tests,
                'total_duration': round(total_duration, 2),
                'average_ops_per_sec': round(avg_ops_per_sec, 2),
                'average_memory_mb': round(avg_memory_mb, 2),
                'average_cpu_percent': round(avg_cpu_percent, 2)
            },
            'benchmark_results': [asdict(result) for result in self.results]
        }
        
        return report
    
    def cleanup(self):
        """Clean up benchmark resources."""
        import shutil
        temp_dir = Path(self.config['temp_dir'])
        if temp_dir.exists():
            shutil.rmtree(temp_dir)


def main():
    """Main benchmark entry point."""
    parser = argparse.ArgumentParser(description='ASZ Cam OS Performance Benchmarks')
    parser.add_argument('-v', '--verbose', action='store_true', help='Verbose output')
    parser.add_argument('-o', '--output', help='Output file for JSON report')
    parser.add_argument('--iterations', type=int, default=10, help='Test iterations')
    
    args = parser.parse_args()
    
    # Initialize benchmark suite
    suite = BenchmarkSuite(verbose=args.verbose)
    
    if args.iterations != 10:
        suite.config['test_iterations'] = args.iterations
    
    try:
        # Run benchmarks
        results = suite.run_all_benchmarks()
        
        # Generate report
        report = suite.generate_report()
        
        # Output report
        if args.output:
            with open(args.output, 'w') as f:
                json.dump(report, f, indent=2)
            print(f"\nReport saved to: {args.output}")
        
        # Print summary
        summary = report['summary']
        print(f"\n{'='*60}")
        print(f"ASZ Cam OS Performance Benchmark Results")
        print(f"{'='*60}")
        print(f"System: {report['system_info'].get('pi_model', 'Generic')}")
        print(f"Total Benchmarks: {summary['total_benchmarks']}")
        print(f"Passed: {summary['passed_benchmarks']}")
        print(f"Failed: {summary['failed_benchmarks']}")
        print(f"Skipped: {summary['skipped_benchmarks']}")
        print(f"Total Duration: {summary['total_duration']}s")
        print(f"Average Performance: {summary['average_ops_per_sec']:.1f} ops/s")
        print(f"Average Memory Usage: {summary['average_memory_mb']:.1f} MB")
        print(f"Average CPU Usage: {summary['average_cpu_percent']:.1f}%")
        
        # Performance rating
        if summary['passed_benchmarks'] == summary['total_benchmarks']:
            if summary['average_ops_per_sec'] > 100:
                print(f"\n🚀 Performance Rating: EXCELLENT")
            elif summary['average_ops_per_sec'] > 50:
                print(f"\n✅ Performance Rating: GOOD")
            else:
                print(f"\n⚠️  Performance Rating: ACCEPTABLE")
        else:
            print(f"\n❌ Performance Rating: ISSUES DETECTED")
        
        print(f"{'='*60}")
        
        # Return appropriate exit code
        sys.exit(0 if summary['failed_benchmarks'] == 0 else 1)
        
    finally:
        suite.cleanup()


if __name__ == "__main__":
    main()
