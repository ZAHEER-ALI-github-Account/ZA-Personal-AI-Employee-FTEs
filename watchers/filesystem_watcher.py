"""
File System Watcher

Monitors a "drop folder" for new files and creates action files
in the Needs_Action folder for AI processing.

This is the simplest watcher to set up and test for the Bronze Tier.
"""

import shutil
import hashlib
import sys
from pathlib import Path
from typing import List, Dict, Any, Optional

# Handle both package import and direct script execution
try:
    from .base_watcher import BaseWatcher
except ImportError:
    from base_watcher import BaseWatcher


class FileSystemWatcher(BaseWatcher):
    """
    Watches a designated drop folder for new files.
    
    When a new file is detected, it creates an action file in Needs_Action
    with metadata about the dropped file.
    """
    
    def __init__(self, vault_path: str, drop_folder: Optional[str] = None, check_interval: int = 30):
        """
        Initialize the file system watcher.
        
        Args:
            vault_path: Path to the Obsidian vault root
            drop_folder: Path to the drop folder (defaults to vault/Drop_Folder)
            check_interval: Seconds between checks
        """
        super().__init__(vault_path, check_interval)
        
        if drop_folder:
            self.drop_folder = Path(drop_folder)
        else:
            self.drop_folder = self.vault_path / 'Drop_Folder'
        
        # Create drop folder if it doesn't exist
        self.drop_folder.mkdir(parents=True, exist_ok=True)
        
        # Track file hashes to detect new files
        self.known_files: Dict[str, str] = {}
        
        # Load existing files on startup
        self._scan_existing_files()
    
    def _scan_existing_files(self):
        """Scan the drop folder for existing files on startup."""
        try:
            for file_path in self.drop_folder.iterdir():
                if file_path.is_file():
                    file_hash = self._compute_hash(file_path)
                    self.known_files[str(file_path)] = file_hash
                    self.logger.info(f'Known file: {file_path.name}')
        except Exception as e:
            self.logger.error(f'Error scanning existing files: {e}')
    
    def _compute_hash(self, file_path: Path) -> str:
        """
        Compute MD5 hash of a file for change detection.
        
        Args:
            file_path: Path to the file
            
        Returns:
            MD5 hash string
        """
        hash_md5 = hashlib.md5()
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b''):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()
    
    def check_for_updates(self) -> List[Path]:
        """
        Check the drop folder for new files.
        
        Returns:
            List of new file paths
        """
        new_files = []
        
        try:
            for file_path in self.drop_folder.iterdir():
                if not file_path.is_file():
                    continue
                
                file_str = str(file_path)
                
                # Skip already known files
                if file_str in self.known_files:
                    continue
                
                # Skip action files (avoid loops)
                if file_path.suffix == '.md':
                    continue
                
                # New file detected
                new_files.append(file_path)
                self.known_files[file_str] = self._compute_hash(file_path)
                self.logger.info(f'New file detected: {file_path.name}')
                
        except Exception as e:
            self.logger.error(f'Error checking drop folder: {e}')
        
        return new_files
    
    def create_action_file(self, file_path: Path) -> Optional[Path]:
        """
        Create an action file for the dropped file.
        
        Args:
            file_path: Path to the dropped file
            
        Returns:
            Path to the created action file
        """
        try:
            # Get file metadata
            stat = file_path.stat()
            file_size = stat.st_size
            file_type = file_path.suffix.lower().replace('.', '')
            
            # Generate action file content
            frontmatter = self.generate_frontmatter(
                item_type='file_drop',
                original_name=file_path.name,
                file_type=file_type,
                size=file_size,
                priority='normal'
            )
            
            content = f"""{frontmatter}
# File Drop for Processing

A new file has been dropped for AI processing.

## File Details

- **Original Name**: {file_path.name}
- **File Type**: {file_type.upper()}
- **Size**: {self._format_size(file_size)}
- **Location**: `{file_path.absolute()}`
- **Dropped At**: {file_path.stat().st_ctime}

## Suggested Actions

- [ ] Review file contents
- [ ] Determine required action
- [ ] Process or respond as needed
- [ ] Move to appropriate folder after processing

## Notes

<!-- Add any additional context or instructions here -->

"""
            
            # Create action file
            safe_name = self.sanitize_filename(file_path.stem)
            action_filename = f'FILE_{safe_name}_{file_path.suffix}.md'
            action_path = self.needs_action / action_filename
            
            action_path.write_text(content)
            
            self.logger.info(f'Created action file: {action_path.name}')
            
            return action_path
            
        except Exception as e:
            self.logger.error(f'Error creating action file: {e}')
            return None
    
    def _format_size(self, size_bytes: int) -> str:
        """
        Format file size in human-readable format.
        
        Args:
            size_bytes: Size in bytes
            
        Returns:
            Formatted size string
        """
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024:
                return f'{size_bytes:.1f} {unit}'
            size_bytes /= 1024
        return f'{size_bytes:.1f} TB'


def main():
    """Main entry point for running the watcher."""
    import sys
    
    # Get vault path from command line or use default
    if len(sys.argv) > 1:
        vault_path = sys.argv[1]
    else:
        # Default to sibling directory
        vault_path = str(Path(__file__).parent.parent / 'AI_Employee_Vault')
    
    print(f'File System Watcher starting...')
    print(f'Vault: {vault_path}')
    print(f'Drop folder: {Path(vault_path) / "Drop_Folder"}')
    print('Press Ctrl+C to stop')
    print('-' * 50)
    
    watcher = FileSystemWatcher(vault_path)
    watcher.run()


if __name__ == '__main__':
    main()
