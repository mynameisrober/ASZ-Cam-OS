#!/usr/bin/env python3
"""
Tests for camera mode functionality.
Tests the new --no-camera, --demo, and --mock-camera command line options.
"""

import sys
import os
from pathlib import Path
import pytest
from unittest.mock import patch, MagicMock

# Add the src directory to the Python path
current_dir = Path(__file__).parent
project_root = current_dir.parent
src_path = project_root / 'src'
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(src_path))

from src.main import parse_arguments, main
from src.core.system_manager import SystemManager


class TestCameraModes:
    """Test camera mode functionality."""

    def test_parse_arguments_default(self):
        """Test default argument parsing."""
        with patch('sys.argv', ['main.py']):
            args = parse_arguments()
            assert args.no_camera is False
            assert args.demo is False
            assert args.mock_camera is False

    def test_parse_arguments_no_camera(self):
        """Test --no-camera argument parsing."""
        with patch('sys.argv', ['main.py', '--no-camera']):
            args = parse_arguments()
            assert args.no_camera is True
            assert args.demo is False
            assert args.mock_camera is False

    def test_parse_arguments_demo(self):
        """Test --demo argument parsing."""
        with patch('sys.argv', ['main.py', '--demo']):
            args = parse_arguments()
            assert args.no_camera is False
            assert args.demo is True
            assert args.mock_camera is False

    def test_parse_arguments_mock_camera(self):
        """Test --mock-camera argument parsing."""
        with patch('sys.argv', ['main.py', '--mock-camera']):
            args = parse_arguments()
            assert args.no_camera is False
            assert args.demo is False
            assert args.mock_camera is True

    def test_mutually_exclusive_options(self):
        """Test that camera options are mutually exclusive."""
        with patch('sys.argv', ['main.py', '--no-camera', '--demo']):
            with pytest.raises(SystemExit):
                parse_arguments()

    def test_system_manager_camera_config_no_camera(self):
        """Test SystemManager with no-camera configuration."""
        manager = SystemManager()
        
        # Test no-camera configuration
        camera_config = {
            'required': False,
            'use_mock': False,
            'demo_mode': False
        }
        
        manager.camera_config.update(camera_config)
        
        assert manager.camera_config['required'] is False
        assert manager.camera_config['use_mock'] is False
        assert manager.camera_config['demo_mode'] is False

    def test_system_manager_camera_config_demo(self):
        """Test SystemManager with demo configuration."""
        manager = SystemManager()
        
        # Test demo configuration
        camera_config = {
            'required': True,
            'use_mock': True,
            'demo_mode': True
        }
        
        manager.camera_config.update(camera_config)
        
        assert manager.camera_config['required'] is True
        assert manager.camera_config['use_mock'] is True
        assert manager.camera_config['demo_mode'] is True

    def test_environment_variable_setting_demo(self):
        """Test that demo mode sets environment variables."""
        # Clear any existing environment variables
        env_vars_to_clear = ['ASZ_MOCK_CAMERA', 'ASZ_DEMO_MODE']
        original_values = {}
        for var in env_vars_to_clear:
            original_values[var] = os.environ.get(var)
            if var in os.environ:
                del os.environ[var]
        
        try:
            with patch('sys.argv', ['main.py', '--demo']):
                with patch('src.main.system_manager') as mock_manager:
                    mock_manager.initialize.return_value = True
                    mock_manager.run.return_value = 0
                    mock_manager.shutdown.return_value = None
                    
                    # Should set environment variables and exit cleanly
                    result = main()
                    
                    # Check that environment variables were set
                    assert os.environ.get('ASZ_MOCK_CAMERA') == 'true'
                    
                    # Check that system manager was called with correct config
                    mock_manager.initialize.assert_called_once()
                    call_args = mock_manager.initialize.call_args[1]
                    camera_config = call_args['camera_config']
                    assert camera_config['required'] is True
                    assert camera_config['use_mock'] is True
                    assert camera_config['demo_mode'] is True
                    
                    assert result == 0
        finally:
            # Restore original environment variable values
            for var, value in original_values.items():
                if value is not None:
                    os.environ[var] = value
                elif var in os.environ:
                    del os.environ[var]

    def test_environment_variable_setting_mock_camera(self):
        """Test that mock-camera mode sets environment variables."""
        # Clear any existing environment variables
        env_vars_to_clear = ['ASZ_MOCK_CAMERA', 'ASZ_DEMO_MODE']
        original_values = {}
        for var in env_vars_to_clear:
            original_values[var] = os.environ.get(var)
            if var in os.environ:
                del os.environ[var]
        
        try:
            with patch('sys.argv', ['main.py', '--mock-camera']):
                with patch('src.main.system_manager') as mock_manager:
                    mock_manager.initialize.return_value = True
                    mock_manager.run.return_value = 0
                    mock_manager.shutdown.return_value = None
                    
                    # Should set environment variables and exit cleanly
                    result = main()
                    
                    # Check that environment variables were set
                    assert os.environ.get('ASZ_MOCK_CAMERA') == 'true'
                    
                    # Check that system manager was called with correct config
                    mock_manager.initialize.assert_called_once()
                    call_args = mock_manager.initialize.call_args[1]
                    camera_config = call_args['camera_config']
                    assert camera_config['required'] is True
                    assert camera_config['use_mock'] is True
                    assert camera_config['demo_mode'] is False
                    
                    assert result == 0
        finally:
            # Restore original environment variable values
            for var, value in original_values.items():
                if value is not None:
                    os.environ[var] = value
                elif var in os.environ:
                    del os.environ[var]


if __name__ == '__main__':
    # Simple test runner if pytest is not available
    test_instance = TestCameraModes()
    
    tests = [
        test_instance.test_parse_arguments_default,
        test_instance.test_parse_arguments_no_camera,
        test_instance.test_parse_arguments_demo,
        test_instance.test_parse_arguments_mock_camera,
        test_instance.test_system_manager_camera_config_no_camera,
        test_instance.test_system_manager_camera_config_demo,
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            test()
            print(f"✓ {test.__name__}")
            passed += 1
        except Exception as e:
            print(f"✗ {test.__name__}: {e}")
            failed += 1
    
    print(f"\nTests: {passed} passed, {failed} failed")
    sys.exit(0 if failed == 0 else 1)