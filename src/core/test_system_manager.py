#!/usr/bin/env python3
"""
Minimal test version of system_manager.py to test relative import issue
"""

import sys
import logging
from pathlib import Path
from typing import Optional

# Test the relative import that should fail
try:
    from ..config.settings import settings
    print("✓ Relative import worked!")
except ImportError as e:
    print(f"✗ Relative import failed: {e}")

# Alternative: test absolute import
try:
    from config.settings import settings
    print("✓ Absolute import worked!")
except ImportError as e:
    print(f"✗ Absolute import failed: {e}")

class SystemManager:
    """Minimal system manager for testing."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        print("SystemManager initialized")

# Global system manager instance
system_manager = SystemManager()