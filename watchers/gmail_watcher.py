"""
Gmail Watcher

Monitors Gmail for new important emails and creates action files
in the Needs_Action folder for AI processing.

Silver Tier Skill - Requires Gmail API credentials
"""

import os
import sys
import base64
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any, Optional
from email import message_from_bytes

sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from watchers.base_watcher import BaseWatcher
except ImportError:
    from base_watcher import BaseWatcher

try:
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow
    from googleapiclient.discovery import build
    from googleapiclient.errors import HttpError
    GMAIL_AVAILABLE = True
except ImportError:
    GMAIL_AVAILABLE = False


class GmailWatcher(BaseWatcher):
    SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']
    PRIORITY_KEYWORDS = ['urgent', 'asap', 'invoice', 'payment', 'important', 'deadline']
    
    def __init__(self, vault_path: str, credentials_path: Optional[str] = None,
                 token_path: Optional[str] = None, check_interval: int = 120):
        if not GMAIL_AVAILABLE:
            raise ImportError("Gmail API dependencies not installed.")
        
        super().__init__(vault_path, check_interval)
        self.credentials_path = Path(credentials_path) if credentials_path else Path('credentials.json')
        self.token_path = Path(token_path) if token_path else Path('token.json')
        self.service = None
        self.processed_ids: set = set()
        self._load_processed_ids()
    
    def _load_processed_ids(self):
        log_file = self.vault_path / 'Logs' / 'gmail_processed_ids.txt'
        if log_file.exists():
            with open(log_file, 'r') as f:
                self.processed_ids = set(line.strip() for line in f if line.strip())
    
    def _save_processed_id(self, email_id: str):
        log_file = self.vault_path / 'Logs' / 'gmail_processed_ids.txt'
        with open(log_file, 'a') as f:
            f.write(f"{email_id}\n")
    
    def authenticate(self):
        print("Starting Gmail API authentication...")
        if not self.credentials_path.exists():
            print("Error: credentials.json not found")
            return False
        try:
            flow = InstalledAppFlow.from_client_secrets_file(self.credentials_path, self.SCOPES)
            creds = flow.run_local_server(port=0)
            with open(self.token_path, 'w') as token:
                token.write(creds.to_json())
            print("[OK] Authentication successful!")
            print(f"Token saved to: {self.token_path.absolute()}")
            return True
        except Exception as e:
            print(f"[FAIL] Authentication failed: {e}")
            return False
    
    def _connect(self) -> bool:
        try:
            if not self.token_path.exists():
                self.logger.warning("Token not found. Please run --authenticate first.")
                return False
            creds = Credentials.from_authorized_user_file(self.token_path, self.SCOPES)
            if creds.expired and creds.refresh_token:
                creds.refresh(None)
                with open(self.token_path, 'w') as token:
                    token.write(creds.to_json())
            self.service = build('gmail', 'v1', credentials=creds)
            self.logger.info("Connected to Gmail API")
            return True
        except Exception as e:
            self.logger.error(f"Connection failed: {e}")
            return False
    
    def check_for_updates(self) -> List[Dict[str, Any]]:
        if not self.service:
            if not self._connect():
                return []
        try:
            results = self.service.users().messages().list(userId='me', q='is:unread', maxResults=10).execute()
            messages = results.get('messages', [])
            new_emails = []
            for msg in messages:
                msg_id = msg['id']
                if msg_id in self.processed_ids:
                    continue
                full_msg = self.service.users().messages().get(userId='me', id=msg_id, format='full').execute()
                email_data = self._parse_email(full_msg)
                email_data['id'] = msg_id
                new_emails.append(email_data)
            self.logger.info(f"Found {len(new_emails)} new emails")
            return new_emails
        except HttpError as e:
            if e.resp.status == 401:
                self.service = None
            return []
        except Exception as e:
            self.logger.error(f"Error checking emails: {e}")
            return []
    
    def _parse_email(self, message: Dict) -> Dict[str, Any]:
        headers = {h['name']: h['value'] for h in message['payload']['headers']}
        body = ''
        if 'parts' in message['payload']:
            for part in message['payload']['parts']:
                if part['mimeType'] == 'text/plain' and 'data' in part:
                    body = base64.urlsafe_b64decode(part['data']).decode('utf-8', errors='ignore')
                    break
        priority = 'high' if any(kw in headers.get('Subject', '').lower() for kw in self.PRIORITY_KEYWORDS) else 'normal'
        return {'from': headers.get('From', 'Unknown'), 'to': headers.get('To', ''),
                'subject': headers.get('Subject', 'No Subject'), 'date': headers.get('Date', ''),
                'body': body, 'snippet': message.get('snippet', ''), 'priority': priority}
    
    def create_action_file(self, email: Dict[str, Any]) -> Optional[Path]:
        try:
            frontmatter = self.generate_frontmatter(item_type='email', from_email=email['from'],
                subject=self.sanitize_filename(email['subject'], max_length=30),
                received=datetime.now().isoformat(), priority=email['priority'], status='pending', message_id=email['id'])
            content = f"""{frontmatter}
# Email Received

**From:** {email['from']}
**Subject:** {email['subject']}
**Priority:** {email['priority'].upper()}

---

## Message Content

{email['body'] or email.get('snippet', 'No content available')}

---

## Suggested Actions

- [ ] Read email carefully
- [ ] Determine required response
- [ ] Draft reply (if needed)
- [ ] Take action or delegate
- [ ] Mark as read in Gmail
"""
            filename = f"EMAIL_{email['id']}.md"
            filepath = self.needs_action / filename
            filepath.write_text(content, encoding='utf-8')
            self.processed_ids.add(email['id'])
            self._save_processed_id(email['id'])
            self.logger.info(f"Created action file: {filename}")
            return filepath
        except Exception as e:
            self.logger.error(f"Error creating action file: {e}")
            return None
    
    def run(self, authenticate_first: bool = False):
        if authenticate_first:
            if not self.authenticate():
                return
        super().run()


def main():
    import argparse
    parser = argparse.ArgumentParser(description='Gmail Watcher')
    parser.add_argument('vault_path', nargs='?', default='AI_Employee_Vault')
    parser.add_argument('--authenticate', action='store_true')
    parser.add_argument('--interval', type=int, default=120)
    parser.add_argument('--test-connection', action='store_true')
    parser.add_argument('--dry-run', action='store_true')
    args = parser.parse_args()
    
    watcher = GmailWatcher(args.vault_path)
    
    if args.authenticate:
        watcher.authenticate()
        return
    if args.test_connection:
        if watcher._connect():
            print("[OK] Gmail API connection successful!")
        else:
            print("[FAIL] Gmail API connection failed")
        return
    
    print(f'Gmail Watcher starting... Interval: {args.interval}s')
    if args.dry_run:
        for _ in range(5):
            emails = watcher.check_for_updates()
            print(f"Found {len(emails)} emails")
            import time
            time.sleep(args.interval)
    else:
        watcher.run()


if __name__ == '__main__':
    main()
