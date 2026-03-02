"""
Watchers Package

Watcher scripts that monitor external systems and create action files.
"""

from .base_watcher import BaseWatcher
from .filesystem_watcher import FileSystemWatcher

__all__ = ['BaseWatcher', 'FileSystemWatcher']
