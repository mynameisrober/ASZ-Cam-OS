"""
ASZ Cam OS - Sync Service
Manages photo synchronization with various cloud services including Google Photos.
Handles automatic sync, retry logic, and maintains sync state.

Author: ASZ Development Team
Version: 1.0.0
"""

import os
import time
import logging
import threading
from pathlib import Path
from typing import Dict, List, Optional, Set, Any
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
import json
from enum import Enum

from PyQt6.QtCore import QObject, pyqtSignal, QTimer

from ..config.settings import settings
from .google_photos import google_photos_api


class SyncStatus(Enum):
    """Sync status enumeration."""
    IDLE = "idle"
    SYNCING = "syncing"
    ERROR = "error"
    PAUSED = "paused"
    AUTHENTICATING = "authenticating"


@dataclass
class SyncState:
    """Represents the current sync state."""
    status: SyncStatus = SyncStatus.IDLE
    last_sync: Optional[datetime] = None
    last_error: Optional[str] = None
    photos_pending: int = 0
    photos_synced_today: int = 0
    total_photos_synced: int = 0
    sync_enabled: bool = True
    auto_sync: bool = True


@dataclass
class PhotoSyncRecord:
    """Record of a synced photo."""
    local_path: str
    filename: str
    sync_time: datetime
    cloud_id: Optional[str] = None
    file_size: int = 0
    file_hash: str = ""


class SyncService(QObject):
    """Main sync service that coordinates photo synchronization."""
    
    # Signals
    status_changed = pyqtSignal(str)  # SyncStatus
    sync_progress = pyqtSignal(int, int)  # current, total
    photo_synced = pyqtSignal(str)  # photo path
    error_occurred = pyqtSignal(str)  # error message
    authentication_required = pyqtSignal()
    
    def __init__(self):
        super().__init__()
        self.logger = logging.getLogger(__name__)
        
        # Sync state
        self.state = SyncState()
        self.sync_records: Dict[str, PhotoSyncRecord] = {}
        self.pending_photos: Set[str] = set()
        
        # Threading
        self.sync_thread: Optional[threading.Thread] = None
        self.sync_thread_running = False
        self._stop_event = threading.Event()
        
        # Timers
        self.sync_timer = QTimer()
        self.sync_timer.timeout.connect(self._periodic_sync)
        
        # File monitoring
        self.monitored_directories = set()
        self.last_directory_scan = {}
        
        # Load sync state from disk
        self._load_sync_records()
        
    def initialize(self) -> bool:
        """Initialize the sync service."""
        try:
            self.logger.info("Initializing sync service...")
            
            if not settings.sync.enabled:
                self.logger.info("Sync service disabled in settings")
                self.state.sync_enabled = False
                return True
            
            # Initialize Google Photos API
            if google_photos_api.initialize():
                self.logger.info("Google Photos API initialized")
            else:
                self.logger.warning("Google Photos API initialization failed")
                if not google_photos_api.is_authenticated():
                    self.state.status = SyncStatus.AUTHENTICATING
                    self.status_changed.emit(self.state.status.value)
                    self.authentication_required.emit()
            
            # Set up periodic sync if auto-sync is enabled
            if settings.sync.auto_sync and settings.sync.sync_interval > 0:
                self.sync_timer.start(settings.sync.sync_interval * 1000)  # Convert to milliseconds
                self.logger.info(f"Automatic sync enabled (interval: {settings.sync.sync_interval}s)")
            
            # Start monitoring photos directory
            self._start_monitoring()
            
            # Initial sync if authenticated
            if google_photos_api.is_authenticated():
                self._queue_initial_sync()
            
            self.logger.info("Sync service initialized successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to initialize sync service: {e}")
            self.state.status = SyncStatus.ERROR
            self.state.last_error = str(e)
            self.status_changed.emit(self.state.status.value)
            return False
    
    def authenticate_google_photos(self, credentials_path: str) -> bool:
        """Authenticate with Google Photos."""
        try:
            self.state.status = SyncStatus.AUTHENTICATING
            self.status_changed.emit(self.state.status.value)
            
            success = google_photos_api.authenticate(credentials_path)
            
            if success:
                self.state.status = SyncStatus.IDLE
                self.logger.info("Google Photos authentication successful")
                self._queue_initial_sync()
            else:
                self.state.status = SyncStatus.ERROR
                self.state.last_error = "Authentication failed"
                self.error_occurred.emit("Google Photos authentication failed")
            
            self.status_changed.emit(self.state.status.value)
            return success
            
        except Exception as e:
            self.logger.error(f"Authentication error: {e}")
            self.state.status = SyncStatus.ERROR
            self.state.last_error = str(e)
            self.status_changed.emit(self.state.status.value)
            return False
    
    def start_sync(self, force: bool = False) -> bool:
        """Start manual sync process."""
        try:
            if not self.state.sync_enabled:
                self.logger.info("Sync is disabled")
                return False
            
            if self.state.status == SyncStatus.SYNCING and not force:
                self.logger.info("Sync already in progress")
                return False
            
            if not google_photos_api.is_authenticated():
                self.logger.warning("Google Photos not authenticated")
                self.authentication_required.emit()
                return False
            
            self.logger.info("Starting manual sync...")
            self._start_sync_process()
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to start sync: {e}")
            self.state.status = SyncStatus.ERROR
            self.state.last_error = str(e)
            self.status_changed.emit(self.state.status.value)
            return False
    
    def pause_sync(self):
        """Pause sync process."""
        try:
            if self.state.status == SyncStatus.SYNCING:
                self.state.status = SyncStatus.PAUSED
                self.status_changed.emit(self.state.status.value)
                self._stop_event.set()
                self.logger.info("Sync paused")
        except Exception as e:
            self.logger.error(f"Failed to pause sync: {e}")
    
    def resume_sync(self):
        """Resume paused sync."""
        try:
            if self.state.status == SyncStatus.PAUSED:
                self.state.status = SyncStatus.IDLE
                self.status_changed.emit(self.state.status.value)
                self._stop_event.clear()
                self.logger.info("Sync resumed")
        except Exception as e:
            self.logger.error(f"Failed to resume sync: {e}")
    
    def sync_photo(self, photo_path: str, priority: int = 1) -> bool:
        """Sync a specific photo."""
        try:
            path_obj = Path(photo_path)
            if not path_obj.exists():
                self.logger.error(f"Photo not found: {photo_path}")
                return False
            
            # Check if already synced
            file_hash = self._calculate_file_hash(photo_path)
            if self._is_photo_synced(photo_path, file_hash):
                self.logger.info(f"Photo already synced: {path_obj.name}")
                return True
            
            # Add to pending photos
            self.pending_photos.add(photo_path)
            
            # Queue for upload
            success = google_photos_api.upload_photo(photo_path, priority)
            if success:
                self.logger.info(f"Queued photo for sync: {path_obj.name}")
                self._update_pending_count()
            else:
                self.pending_photos.discard(photo_path)
            
            return success
            
        except Exception as e:
            self.logger.error(f"Failed to sync photo {photo_path}: {e}")
            return False
    
    def get_sync_stats(self) -> Dict[str, Any]:
        """Get comprehensive sync statistics."""
        try:
            stats = {
                'status': self.state.status.value,
                'last_sync': self.state.last_sync.isoformat() if self.state.last_sync else None,
                'last_error': self.state.last_error,
                'photos_pending': len(self.pending_photos),
                'photos_synced_today': self.state.photos_synced_today,
                'total_photos_synced': self.state.total_photos_synced,
                'sync_enabled': self.state.sync_enabled,
                'auto_sync': self.state.auto_sync,
                'authenticated': google_photos_api.is_authenticated(),
                'google_photos_stats': google_photos_api.get_upload_stats()
            }
            return stats
            
        except Exception as e:
            self.logger.error(f"Failed to get sync stats: {e}")
            return {}
    
    def enable_sync(self, enabled: bool):
        """Enable or disable sync service."""
        self.state.sync_enabled = enabled
        if enabled:
            self.logger.info("Sync service enabled")
            if settings.sync.auto_sync:
                self.sync_timer.start(settings.sync.sync_interval * 1000)
            self._queue_initial_sync()
        else:
            self.logger.info("Sync service disabled")
            self.sync_timer.stop()
            self.pause_sync()
    
    def enable_auto_sync(self, enabled: bool):
        """Enable or disable automatic sync."""
        self.state.auto_sync = enabled
        if enabled and self.state.sync_enabled:
            self.sync_timer.start(settings.sync.sync_interval * 1000)
            self.logger.info("Auto-sync enabled")
        else:
            self.sync_timer.stop()
            self.logger.info("Auto-sync disabled")
    
    def _periodic_sync(self):
        """Periodic sync triggered by timer."""
        try:
            if (self.state.sync_enabled and 
                self.state.auto_sync and 
                self.state.status == SyncStatus.IDLE and
                google_photos_api.is_authenticated()):
                
                self.logger.info("Starting periodic sync...")
                self._start_sync_process()
        except Exception as e:
            self.logger.error(f"Periodic sync error: {e}")
    
    def _start_sync_process(self):
        """Start the sync process in background thread."""
        try:
            if self.sync_thread and self.sync_thread.is_alive():
                return
            
            self.state.status = SyncStatus.SYNCING
            self.status_changed.emit(self.state.status.value)
            self._stop_event.clear()
            
            self.sync_thread_running = True
            self.sync_thread = threading.Thread(
                target=self._sync_worker,
                name="SyncService-Worker"
            )
            self.sync_thread.daemon = True
            self.sync_thread.start()
            
        except Exception as e:
            self.logger.error(f"Failed to start sync process: {e}")
            self.state.status = SyncStatus.ERROR
            self.state.last_error = str(e)
            self.status_changed.emit(self.state.status.value)
    
    def _sync_worker(self):
        """Background sync worker thread."""
        try:
            self.logger.info("Sync worker started")
            
            # Discover new photos
            new_photos = self._discover_new_photos()
            total_photos = len(new_photos)
            
            if total_photos == 0:
                self.logger.info("No new photos to sync")
                self.state.status = SyncStatus.IDLE
                self.status_changed.emit(self.state.status.value)
                return
            
            self.logger.info(f"Found {total_photos} new photos to sync")
            self.sync_progress.emit(0, total_photos)
            
            # Process photos
            synced_count = 0
            for i, photo_path in enumerate(new_photos):
                if self._stop_event.is_set():
                    self.logger.info("Sync stopped by user")
                    break
                
                try:
                    if self.sync_photo(photo_path, priority=2):  # Normal priority for batch sync
                        synced_count += 1
                        self._record_synced_photo(photo_path)
                        self.photo_synced.emit(photo_path)
                    
                    self.sync_progress.emit(i + 1, total_photos)
                    
                    # Small delay to prevent overwhelming the API
                    time.sleep(0.5)
                    
                except Exception as e:
                    self.logger.error(f"Error syncing photo {photo_path}: {e}")
            
            # Update state
            self.state.photos_synced_today += synced_count
            self.state.total_photos_synced += synced_count
            self.state.last_sync = datetime.now()
            
            if self._stop_event.is_set():
                self.state.status = SyncStatus.PAUSED
            else:
                self.state.status = SyncStatus.IDLE
            
            self.status_changed.emit(self.state.status.value)
            self._save_sync_records()
            
            self.logger.info(f"Sync completed: {synced_count}/{total_photos} photos synced")
            
        except Exception as e:
            self.logger.error(f"Sync worker error: {e}")
            self.state.status = SyncStatus.ERROR
            self.state.last_error = str(e)
            self.status_changed.emit(self.state.status.value)
            self.error_occurred.emit(str(e))
        finally:
            self.sync_thread_running = False
    
    def _discover_new_photos(self) -> List[str]:
        """Discover new photos that need to be synced."""
        new_photos = []
        
        try:
            photos_dir = Path(settings.system.photos_directory)
            if not photos_dir.exists():
                return new_photos
            
            # Supported image extensions
            image_extensions = {'.jpg', '.jpeg', '.png', '.tiff', '.tif', '.bmp', '.webp'}
            
            for photo_file in photos_dir.rglob('*'):
                if (photo_file.is_file() and 
                    photo_file.suffix.lower() in image_extensions):
                    
                    photo_path = str(photo_file)
                    file_hash = self._calculate_file_hash(photo_path)
                    
                    if not self._is_photo_synced(photo_path, file_hash):
                        new_photos.append(photo_path)
            
            return sorted(new_photos, key=lambda x: os.path.getmtime(x), reverse=True)
            
        except Exception as e:
            self.logger.error(f"Error discovering photos: {e}")
            return new_photos
    
    def _is_photo_synced(self, photo_path: str, file_hash: str) -> bool:
        """Check if photo is already synced."""
        try:
            # Check by file path first
            if photo_path in self.sync_records:
                record = self.sync_records[photo_path]
                return record.file_hash == file_hash
            
            # Check by hash (for moved/renamed files)
            for record in self.sync_records.values():
                if record.file_hash == file_hash:
                    return True
            
            return False
            
        except Exception:
            return False
    
    def _record_synced_photo(self, photo_path: str):
        """Record that a photo has been synced."""
        try:
            path_obj = Path(photo_path)
            file_hash = self._calculate_file_hash(photo_path)
            file_size = path_obj.stat().st_size if path_obj.exists() else 0
            
            record = PhotoSyncRecord(
                local_path=photo_path,
                filename=path_obj.name,
                sync_time=datetime.now(),
                file_size=file_size,
                file_hash=file_hash
            )
            
            self.sync_records[photo_path] = record
            self.pending_photos.discard(photo_path)
            
        except Exception as e:
            self.logger.error(f"Failed to record synced photo: {e}")
    
    def _calculate_file_hash(self, file_path: str) -> str:
        """Calculate SHA-256 hash of file."""
        try:
            import hashlib
            hash_sha256 = hashlib.sha256()
            with open(file_path, 'rb') as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_sha256.update(chunk)
            return hash_sha256.hexdigest()
        except Exception:
            return ""
    
    def _load_sync_records(self):
        """Load sync records from disk."""
        try:
            records_file = Path(settings.system.data_directory) / 'sync_records.json'
            if records_file.exists():
                with open(records_file, 'r') as f:
                    data = json.load(f)
                
                # Load sync records
                for path, record_data in data.get('records', {}).items():
                    record = PhotoSyncRecord(
                        local_path=record_data['local_path'],
                        filename=record_data['filename'],
                        sync_time=datetime.fromisoformat(record_data['sync_time']),
                        cloud_id=record_data.get('cloud_id'),
                        file_size=record_data.get('file_size', 0),
                        file_hash=record_data.get('file_hash', '')
                    )
                    self.sync_records[path] = record
                
                # Load state
                state_data = data.get('state', {})
                self.state.total_photos_synced = state_data.get('total_photos_synced', 0)
                if state_data.get('last_sync'):
                    self.state.last_sync = datetime.fromisoformat(state_data['last_sync'])
                
                self.logger.info(f"Loaded {len(self.sync_records)} sync records")
                
        except Exception as e:
            self.logger.error(f"Failed to load sync records: {e}")
    
    def _save_sync_records(self):
        """Save sync records to disk."""
        try:
            records_file = Path(settings.system.data_directory) / 'sync_records.json'
            records_file.parent.mkdir(parents=True, exist_ok=True)
            
            # Prepare data
            records_data = {}
            for path, record in self.sync_records.items():
                records_data[path] = {
                    'local_path': record.local_path,
                    'filename': record.filename,
                    'sync_time': record.sync_time.isoformat(),
                    'cloud_id': record.cloud_id,
                    'file_size': record.file_size,
                    'file_hash': record.file_hash
                }
            
            state_data = {
                'total_photos_synced': self.state.total_photos_synced,
                'last_sync': self.state.last_sync.isoformat() if self.state.last_sync else None
            }
            
            data = {
                'records': records_data,
                'state': state_data,
                'version': '1.0'
            }
            
            with open(records_file, 'w') as f:
                json.dump(data, f, indent=2)
            
        except Exception as e:
            self.logger.error(f"Failed to save sync records: {e}")
    
    def _start_monitoring(self):
        """Start monitoring photos directory for changes."""
        try:
            photos_dir = Path(settings.system.photos_directory)
            if photos_dir.exists():
                self.monitored_directories.add(str(photos_dir))
                self.logger.info(f"Monitoring directory: {photos_dir}")
        except Exception as e:
            self.logger.error(f"Failed to start directory monitoring: {e}")
    
    def _queue_initial_sync(self):
        """Queue initial sync if conditions are met."""
        try:
            if (self.state.sync_enabled and
                google_photos_api.is_authenticated() and
                self.state.status == SyncStatus.IDLE):
                
                # Delay initial sync to allow system to settle
                QTimer.singleShot(5000, self._start_sync_process)  # 5 second delay
                
        except Exception as e:
            self.logger.error(f"Failed to queue initial sync: {e}")
    
    def _update_pending_count(self):
        """Update pending photos count."""
        self.state.photos_pending = len(self.pending_photos)
    
    def cleanup(self):
        """Clean up sync service resources."""
        try:
            self.logger.info("Cleaning up sync service...")
            
            # Stop timers
            self.sync_timer.stop()
            
            # Stop sync thread
            self._stop_event.set()
            self.sync_thread_running = False
            
            if self.sync_thread and self.sync_thread.is_alive():
                self.sync_thread.join(timeout=5)
            
            # Save final state
            self._save_sync_records()
            
            # Cleanup Google Photos API
            google_photos_api.shutdown()
            
            self.logger.info("Sync service cleanup complete")
            
        except Exception as e:
            self.logger.error(f"Error during sync service cleanup: {e}")
