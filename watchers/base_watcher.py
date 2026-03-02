"""
Base Watcher Module

Abstract base class for all watcher scripts in the AI Employee system.
All watchers inherit from this class and implement the check_for_updates()
and create_action_file() methods.
"""

import time
import logging
from pathlib import Path
from abc import ABC, abstractmethod
from datetime import datetime
from typing import List, Any, Optional


class BaseWatcher(ABC):
    """
    Abstract base class for all watcher scripts.
    
    Watchers monitor external systems (Gmail, WhatsApp, filesystems, etc.)
    and create actionable .md files in the Needs_Action folder for Claude to process.
    """
    
    def __init__(self, vault_path: str, check_interval: int = 60):
        """
        Initialize the watcher.
        
        Args:
            vault_path: Path to the Obsidian vault root
            check_interval: Seconds between checks (default: 60)
        """
        self.vault_path = Path(vault_path)
        self.needs_action = self.vault_path / 'Needs_Action'
        self.inbox = self.vault_path / 'Inbox'
        self.check_interval = check_interval
        
        # Ensure directories exist
        self.needs_action.mkdir(parents=True, exist_ok=True)
        self.inbox.mkdir(parents=True, exist_ok=True)
        
        # Setup logging
        self._setup_logging()
        
        # Track processed items to avoid duplicates
        self.processed_ids: set = set()
        
    def _setup_logging(self):
        """Setup logging to file and console."""
        log_dir = self.vault_path / 'Logs'
        log_dir.mkdir(parents=True, exist_ok=True)
        
        log_file = log_dir / f'watcher_{self.__class__.__name__}_{datetime.now().strftime("%Y-%m-%d")}.log'
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(self.__class__.__name__)
    
    @abstractmethod
    def check_for_updates(self) -> List[Any]:
        """
        Check the external system for new items.
        
        Returns:
            List of new items to process
        """
        pass
    
    @abstractmethod
    def create_action_file(self, item: Any) -> Optional[Path]:
        """
        Create a .md action file in the Needs_Action folder.
        
        Args:
            item: The item to create an action file for
            
        Returns:
            Path to the created file, or None if failed
        """
        pass
    
    def run(self):
        """
        Main run loop. Continuously checks for updates and creates action files.
        """
        self.logger.info(f'Starting {self.__class__.__name__}')
        self.logger.info(f'Vault path: {self.vault_path}')
        self.logger.info(f'Check interval: {self.check_interval} seconds')
        
        try:
            while True:
                try:
                    items = self.check_for_updates()
                    self.logger.info(f'Found {len(items)} new items')
                    
                    for item in items:
                        filepath = self.create_action_file(item)
                        if filepath:
                            self.logger.info(f'Created action file: {filepath.name}')
                    
                except Exception as e:
                    self.logger.error(f'Error processing items: {e}', exc_info=True)
                
                time.sleep(self.check_interval)
                
        except KeyboardInterrupt:
            self.logger.info(f'{self.__class__.__name__} stopped by user')
        except Exception as e:
            self.logger.error(f'Fatal error: {e}', exc_info=True)
            raise
    
    def generate_frontmatter(self, item_type: str, **kwargs) -> str:
        """
        Generate YAML frontmatter for action files.
        
        Args:
            item_type: Type of item (email, whatsapp, file_drop, etc.)
            **kwargs: Additional metadata fields
            
        Returns:
            Formatted YAML frontmatter string
        """
        kwargs['type'] = item_type
        kwargs['created'] = datetime.now().isoformat()
        kwargs['status'] = kwargs.get('status', 'pending')
        
        frontmatter = '---\n'
        for key, value in kwargs.items():
            frontmatter += f'{key}: {value}\n'
        frontmatter += '---\n\n'
        
        return frontmatter
    
    def sanitize_filename(self, name: str, max_length: int = 50) -> str:
        """
        Sanitize a string for use in filenames.
        
        Args:
            name: The original name
            max_length: Maximum length of the filename
            
        Returns:
            Sanitized filename
        """
        # Remove or replace problematic characters
        sanitized = name.replace('/', '-').replace('\\', '-')
        sanitized = sanitized.replace(':', '-').replace('*', '-')
        sanitized = sanitized.replace('?', '-').replace('"', '-')
        sanitized = sanitized.replace('<', '-').replace('>', '-')
        sanitized = sanitized.replace('|', '-')
        
        # Truncate if too long
        if len(sanitized) > max_length:
            sanitized = sanitized[:max_length]
        
        return sanitized.strip()
