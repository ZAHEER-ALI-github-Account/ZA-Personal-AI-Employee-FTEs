"""
Orchestrator

Main orchestration script that:
1. Monitors the Needs_Action folder for new items
2. Triggers Qwen Code to process items
3. Manages the flow between folders (Pending_Approval → Approved → Done)
4. Updates the Dashboard

For Bronze Tier: This script creates prompts for Qwen Code to process
and generates appropriate commands for the user to run.
"""

import os
import sys
import shutil
import logging
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional, Tuple
import re

# Fix Windows console encoding for Unicode characters
# Only apply if stdout is still the original console
if sys.platform == 'win32' and hasattr(sys.stdout, 'buffer'):
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')


class Orchestrator:
    """
    Main orchestrator for the AI Employee system.
    
    Coordinates the flow of items through the system:
    Needs_Action → Plans → Pending_Approval → Approved → Done
    """
    
    def __init__(self, vault_path: str):
        """
        Initialize the orchestrator.
        
        Args:
            vault_path: Path to the Obsidian vault root
        """
        self.vault_path = Path(vault_path)
        
        # Define folders
        self.folders = {
            'inbox': self.vault_path / 'Inbox',
            'needs_action': self.vault_path / 'Needs_Action',
            'plans': self.vault_path / 'Plans',
            'pending_approval': self.vault_path / 'Pending_Approval',
            'approved': self.vault_path / 'Approved',
            'done': self.vault_path / 'Done',
            'accounting': self.vault_path / 'Accounting',
            'briefings': self.vault_path / 'Briefings',
            'invoices': self.vault_path / 'Invoices',
            'logs': self.vault_path / 'Logs',
        }
        
        # Ensure all folders exist
        for folder in self.folders.values():
            folder.mkdir(parents=True, exist_ok=True)
        
        # Setup logging
        self._setup_logging()
        
        # Dashboard path
        self.dashboard_path = self.vault_path / 'Dashboard.md'
        
        # Company handbook path
        self.handbook_path = self.vault_path / 'Company_Handbook.md'
    
    def _setup_logging(self):
        """Setup logging configuration."""
        log_file = self.folders['logs'] / f'orchestrator_{datetime.now().strftime("%Y-%m-%d")}.log'
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger('Orchestrator')
    
    def get_needs_action_items(self) -> List[Path]:
        """
        Get all .md files in the Needs_Action folder.
        
        Returns:
            List of file paths
        """
        items = []
        try:
            for file_path in self.folders['needs_action'].iterdir():
                if file_path.is_file() and file_path.suffix == '.md':
                    items.append(file_path)
        except Exception as e:
            self.logger.error(f'Error reading Needs_Action folder: {e}')
        return items
    
    def get_pending_approval_items(self) -> List[Path]:
        """
        Get all items pending approval.
        
        Returns:
            List of file paths
        """
        items = []
        try:
            for file_path in self.folders['pending_approval'].iterdir():
                if file_path.is_file() and file_path.suffix == '.md':
                    items.append(file_path)
        except Exception as e:
            self.logger.error(f'Error reading Pending_Approval folder: {e}')
        return items
    
    def get_approved_items(self) -> List[Path]:
        """
        Get all approved items ready for execution.
        
        Returns:
            List of file paths
        """
        items = []
        try:
            for file_path in self.folders['approved'].iterdir():
                if file_path.is_file() and file_path.suffix == '.md':
                    items.append(file_path)
        except Exception as e:
            self.logger.error(f'Error reading Approved folder: {e}')
        return items
    
    def read_file_metadata(self, file_path: Path) -> Dict:
        """
        Read YAML frontmatter from a file.
        
        Args:
            file_path: Path to the file
            
        Returns:
            Dictionary of metadata
        """
        metadata = {}
        try:
            content = file_path.read_text()
            
            # Extract frontmatter
            match = re.search(r'^---\s*\n(.*?)\n---\s*\n', content, re.DOTALL)
            if match:
                frontmatter = match.group(1)
                for line in frontmatter.split('\n'):
                    if ':' in line:
                        key, value = line.split(':', 1)
                        metadata[key.strip()] = value.strip()
        except Exception as e:
            self.logger.error(f'Error reading metadata from {file_path}: {e}')
        
        return metadata
    
    def update_dashboard(self, stats: Dict):
        """
        Update the Dashboard.md with current statistics.

        Args:
            stats: Dictionary of statistics to update
        """
        try:
            if not self.dashboard_path.exists():
                self.logger.warning('Dashboard.md not found')
                return

            # Read with UTF-8 encoding
            content = self.dashboard_path.read_text(encoding='utf-8')

            # Update timestamp
            content = re.sub(
                r'last_updated: .*',
                f'last_updated: {datetime.now().isoformat()}',
                content
            )

            # Update pending actions count (use ASCII-safe emojis)
            pending_count = stats.get('pending_actions', 0)
            pending_status = '[OK] Clear' if pending_count == 0 else f'[!] {pending_count} items'
            content = re.sub(
                r'\*\*Pending Actions\*\*.*\n\|.*\| (.*) \|.*\n',
                f'**Pending Actions** | {pending_count} | {pending_status} |\n',
                content
            )

            # Update in progress count
            in_progress_count = stats.get('in_progress', 0)
            in_progress_status = '[OK] Clear' if in_progress_count == 0 else f'[~] {in_progress_count} items'
            content = re.sub(
                r'\*\*In Progress\*\*.*\n\|.*\| (.*) \|.*\n',
                f'**In Progress** | {in_progress_count} | {in_progress_status} |\n',
                content
            )

            # Update pending approval count (use ASCII-safe emojis)
            approval_count = stats.get('pending_approval', 0)
            approval_status = '[OK] Clear' if approval_count == 0 else f'[>>] {approval_count} awaiting'
            content = re.sub(
                r'\*\*Pending Approval\*\*.*\n\|.*\| (.*) \|.*\n',
                f'**Pending Approval** | {approval_count} | {approval_status} |\n',
                content
            )

            # Write with UTF-8 encoding
            self.dashboard_path.write_text(content, encoding='utf-8')
            self.logger.info('Dashboard updated')

        except Exception as e:
            self.logger.error(f'Error updating dashboard: {e}')
    
    def generate_qwen_prompt(self, items: List[Path]) -> str:
        """
        Generate a prompt for Qwen Code to process items.

        Args:
            items: List of items to process

        Returns:
            Formatted prompt string
        """
        prompt = """# AI Employee Task Processing

You are an AI Employee assistant. Process the following items from the Needs_Action folder.

## Instructions

1. Read each item in the Needs_Action folder
2. Understand the request or task
3. Create a Plan.md file in the Plans folder with:
   - Clear objective
   - Step-by-step actions with checkboxes
   - Flag any items requiring human approval
4. For items requiring approval, create a file in Pending_Approval folder
5. Move processed items to Done folder (or leave if approval needed)

## Company Rules

Refer to Company_Handbook.md for:
- Approval thresholds
- Communication tone guidelines
- File naming conventions
- Security rules

## Items to Process

"""
        
        for item in items:
            metadata = self.read_file_metadata(item)
            content = item.read_text()
            
            prompt += f"\n### File: {item.name}\n"
            prompt += f"Type: {metadata.get('type', 'unknown')}\n"
            prompt += f"Priority: {metadata.get('priority', 'normal')}\n"
            prompt += f"\nContent:\n{content}\n"
            prompt += "\n" + "-" * 50 + "\n"
        
        prompt += """
## Output Format

After processing, provide a summary:
1. What actions were taken
2. What items need human approval
3. Any questions or clarifications needed

Remember: When in doubt, flag for human review. Never take irreversible actions without approval.
"""
        
        return prompt
    
    def process_approved_items(self) -> List[str]:
        """
        Process items in the Approved folder.
        
        For Bronze Tier: This logs what would be done and moves to Done.
        For Silver/Gold: This would actually execute MCP actions.
        
        Returns:
            List of action descriptions
        """
        actions = []
        approved_items = self.get_approved_items()
        
        for item in approved_items:
            metadata = self.read_file_metadata(item)
            action_type = metadata.get('action', 'unknown')
            
            # Log the action that would be taken
            action_desc = f"Would execute: {action_type} for {item.name}"
            actions.append(action_desc)
            self.logger.info(action_desc)
            
            # For Bronze Tier: Just move to Done
            done_path = self.folders['done'] / f'DONE_{item.name}'
            shutil.move(str(item), str(done_path))
            self.logger.info(f'Moved {item.name} to Done')
        
        return actions
    
    def get_status(self) -> Dict:
        """
        Get current system status.
        
        Returns:
            Dictionary of status information
        """
        return {
            'pending_actions': len(self.get_needs_action_items()),
            'in_progress': len(list(self.folders['plans'].iterdir())) if self.folders['plans'].exists() else 0,
            'pending_approval': len(self.get_pending_approval_items()),
            'approved_ready': len(self.get_approved_items()),
            'vault_path': str(self.vault_path),
        }
    
    def run_interactive(self):
        """
        Run the orchestrator in interactive mode.
        
        This generates prompts for the user to run with Claude Code.
        """
        self.logger.info('Starting Orchestrator in interactive mode')
        
        # Get items to process
        items = self.get_needs_action_items()
        approved = self.get_approved_items()
        
        # Process approved items first
        if approved:
            self.logger.info(f'Found {len(approved)} approved items')
            actions = self.process_approved_items()
            for action in actions:
                print(f'  ✓ {action}')
        
        # Generate prompt for new items
        if items:
            self.logger.info(f'Found {items} items in Needs_Action')

            # Generate and display the prompt
            prompt = self.generate_qwen_prompt(items)

            print('\n' + '=' * 60)
            print('QWEN CODE PROMPT')
            print('=' * 60)
            print(prompt)
            print('=' * 60)

            # Save prompt to file for convenience
            prompt_file = self.folders['logs'] / f'qwen_prompt_{datetime.now().strftime("%Y%m%d_%H%M%S")}.md'
            prompt_file.write_text(prompt, encoding='utf-8')

            print(f'\nPrompt saved to: {prompt_file}')
            print(f'\nTo process with Qwen Code, run:')
            print(f'  cd "{self.vault_path}"')
            print(f'  qwen "Process items in Needs_Action folder"')

        else:
            print('\n✅ No items to process in Needs_Action')
        
        # Update dashboard
        status = self.get_status()
        self.update_dashboard(status)
        
        return status


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description='AI Employee Orchestrator')
    parser.add_argument(
        'vault_path',
        nargs='?',
        default=str(Path(__file__).parent / 'AI_Employee_Vault'),
        help='Path to the Obsidian vault'
    )
    parser.add_argument(
        '--watch',
        action='store_true',
        help='Run in watch mode (continuous monitoring)'
    )
    parser.add_argument(
        '--interval',
        type=int,
        default=60,
        help='Watch interval in seconds'
    )
    
    args = parser.parse_args()
    
    orchestrator = Orchestrator(args.vault_path)
    
    if args.watch:
        import time
        print(f'Orchestrator watching {args.vault_path}')
        print(f'Check interval: {args.interval} seconds')
        print('Press Ctrl+C to stop')
        
        try:
            while True:
                orchestrator.run_interactive()
                time.sleep(args.interval)
        except KeyboardInterrupt:
            print('\nOrchestrator stopped')
    else:
        status = orchestrator.run_interactive()
        print(f'\nStatus: {status}')


if __name__ == '__main__':
    main()
