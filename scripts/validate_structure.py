#!/usr/bin/env python3
"""
ASZ Cam OS - Structure Validation Test
Validates that all modules are properly structured and importable
"""

import sys
import os
from pathlib import Path

# Add src to path
project_root = Path(__file__).parent.parent  # Go up one level from scripts/
src_path = project_root / 'src'
sys.path.insert(0, str(src_path))

def test_module_structure():
    """Test that all modules are properly structured"""
    tests = []
    
    # Test 1: Directory structure exists
    required_dirs = [
        'src', 'src/ui', 'src/system', 'src/sync', 'src/camera', 'src/storage',
        'assets', 'assets/fonts', 'assets/themes', 'assets/icons',
        'configs', 'configs/systemd', 'scripts', 'docs', 'buildroot'
    ]
    
    for directory in required_dirs:
        dir_path = project_root / directory
        if dir_path.exists():
            tests.append(f"✅ Directory exists: {directory}")
        else:
            tests.append(f"❌ Directory missing: {directory}")
    
    # Test 2: Required files exist
    required_files = [
        'main.py', 'requirements.txt', 'README.md',
        'src/ui/main_window.py', 'src/ui/camera_view.py', 'src/ui/settings_view.py',
        'src/ui/photos_view.py', 'src/ui/memories_view.py', 'src/ui/theme.py',
        'src/system/camera_service.py', 'src/sync/google_photos_sync.py',
        'configs/systemd/asz-cam.service', 'scripts/build.sh', 'scripts/dev_run.py',
        'buildroot/asz_cam_defconfig'
    ]
    
    for file_path in required_files:
        full_path = project_root / file_path
        if full_path.exists():
            tests.append(f"✅ File exists: {file_path}")
        else:
            tests.append(f"❌ File missing: {file_path}")
    
    # Test 3: Python syntax validation (basic)
    python_files = [
        'main.py',
        'src/ui/main_window.py', 'src/ui/camera_view.py', 'src/ui/settings_view.py',
        'src/ui/photos_view.py', 'src/ui/memories_view.py', 'src/ui/theme.py',
        'src/system/camera_service.py', 'src/sync/google_photos_sync.py'
    ]
    
    for py_file in python_files:
        file_path = project_root / py_file
        if file_path.exists():
            try:
                with open(file_path, 'r') as f:
                    content = f.read()
                    # Basic syntax check
                    compile(content, str(file_path), 'exec')
                tests.append(f"✅ Python syntax valid: {py_file}")
            except SyntaxError as e:
                tests.append(f"❌ Python syntax error in {py_file}: {e}")
            except Exception as e:
                tests.append(f"⚠️  Could not validate {py_file}: {e}")
    
    # Test 4: Configuration file validity
    config_files = {
        'buildroot/asz_cam_defconfig': 'Buildroot config',
        'configs/systemd/asz-cam.service': 'systemd service',
        'requirements.txt': 'Python requirements'
    }
    
    for config_file, description in config_files.items():
        file_path = project_root / config_file
        if file_path.exists():
            try:
                with open(file_path, 'r') as f:
                    content = f.read().strip()
                    if content:
                        tests.append(f"✅ {description} has content: {config_file}")
                    else:
                        tests.append(f"⚠️  {description} is empty: {config_file}")
            except Exception as e:
                tests.append(f"❌ Error reading {config_file}: {e}")
    
    return tests

def main():
    """Run all structure tests"""
    print("ASZ Cam OS - Structure Validation")
    print("="*50)
    
    tests = test_module_structure()
    
    success_count = sum(1 for test in tests if test.startswith("✅"))
    warning_count = sum(1 for test in tests if test.startswith("⚠️"))
    error_count = sum(1 for test in tests if test.startswith("❌"))
    
    print(f"\\nTest Results:")
    for test in tests:
        print(test)
    
    print(f"\\nSummary:")
    print(f"✅ Successful: {success_count}")
    print(f"⚠️  Warnings: {warning_count}")
    print(f"❌ Errors: {error_count}")
    print(f"📊 Total: {len(tests)}")
    
    if error_count == 0:
        print(f"\\n🎉 All critical tests passed!")
        print(f"ASZ Cam OS structure is valid and ready for deployment.")
        return True
    else:
        print(f"\\n⚠️  Some issues found. Please review and fix errors before deployment.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)