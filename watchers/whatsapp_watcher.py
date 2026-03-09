"""
WhatsApp Watcher

Monitors WhatsApp Web for new messages with keyword filtering.
Uses Playwright to automate WhatsApp Web and detect urgent messages.

Silver Tier Skill - Requires Playwright
"""

import os
import sys
import time
import json
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any, Optional

sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from watchers.base_watcher import BaseWatcher
except ImportError:
    from base_watcher import BaseWatcher

try:
    from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False


class WhatsAppWatcher(BaseWatcher):
    DEFAULT_KEYWORDS = ['urgent', 'asap', 'invoice', 'payment', 'help', 'emergency', 'deadline']
    WHATSAPP_WEB_URL = 'https://web.whatsapp.com'
    
    def __init__(self, vault_path: str, session_path: Optional[str] = None,
                 keywords: Optional[List[str]] = None, check_interval: int = 30, headless: bool = True):
        if not PLAYWRIGHT_AVAILABLE:
            raise ImportError("Playwright not installed.")
        
        super().__init__(vault_path, check_interval)
        self.session_path = Path(session_path) if session_path else self.vault_path / 'whatsapp_session'
        self.session_path.mkdir(parents=True, exist_ok=True)
        self.keywords = set(keywords) if keywords else set(self.DEFAULT_KEYWORDS)
        self.headless = headless
        self.processed_messages: set = set()
        self._load_processed_messages()
    
    def _load_processed_messages(self):
        log_file = self.vault_path / 'Logs' / 'whatsapp_processed.json'
        if log_file.exists():
            with open(log_file, 'r') as f:
                data = json.load(f)
                self.processed_messages = set(data.get('processed', []))
    
    def _save_processed_messages(self):
        log_file = self.vault_path / 'Logs' / 'whatsapp_processed.json'
        with open(log_file, 'w') as f:
            json.dump({'processed': list(self.processed_messages), 'last_updated': datetime.now().isoformat()}, f, indent=2)
    
    def check_for_updates(self) -> List[Dict[str, Any]]:
        messages = []
        try:
            with sync_playwright() as p:
                browser = p.chromium.launch_persistent_context(
                    user_data_dir=str(self.session_path), headless=self.headless,
                    args=['--disable-blink-features=AutomationControlled', '--no-sandbox'])
                page = browser.pages[0] if browser.pages else browser.new_page()
                self.logger.info("Navigating to WhatsApp Web...")
                page.goto(self.WHATSAPP_WEB_URL, wait_until='domcontentloaded', timeout=60000)
                try:
                    page.wait_for_selector('[data-testid="chat-list"]', timeout=30000)
                    self.logger.info("Connected to WhatsApp Web")
                except PlaywrightTimeout:
                    self.logger.warning("QR code may need scanning")
                    try:
                        page.wait_for_selector('[data-testid="chat-list"]', timeout=60000)
                    except PlaywrightTimeout:
                        self.logger.error("Login timeout")
                        browser.close()
                        return []
                time.sleep(2)
                messages = self._extract_unread_messages(page)
                browser.close()
        except Exception as e:
            self.logger.error(f"Error checking WhatsApp: {e}")
        return messages
    
    def _extract_unread_messages(self, page) -> List[Dict[str, Any]]:
        messages = []
        try:
            unread_data = page.evaluate('''() => {
                const messages = [];
                const chats = document.querySelectorAll('[data-testid="chat-list"] > div[role="row"]');
                chats.forEach(chat => {
                    const unreadBadge = chat.querySelector('[data-testid="unread-chat-msg-count"]');
                    if (unreadBadge) {
                        const contactName = chat.getAttribute('aria-label') || '';
                        const messageText = chat.innerText || '';
                        messages.push({contact: contactName, text: messageText, timestamp: new Date().toISOString()});
                    }
                });
                return messages;
            }''')
            for msg in unread_data:
                text_lower = msg.get('text', '').lower()
                matched_keywords = [kw for kw in self.keywords if kw.lower() in text_lower]
                if matched_keywords:
                    msg_id = f"{msg.get('contact', 'unknown')}_{msg.get('timestamp', '')}"
                    if msg_id in self.processed_messages:
                        continue
                    msg['id'] = msg_id
                    msg['keywords'] = matched_keywords
                    messages.append(msg)
                    self.processed_messages.add(msg_id)
            self._save_processed_messages()
            self.logger.info(f"Found {len(messages)} new messages with keywords")
        except Exception as e:
            self.logger.error(f"Error extracting messages: {e}")
        return messages
    
    def create_action_file(self, message: Dict[str, Any]) -> Optional[Path]:
        try:
            priority = 'high' if 'urgent' in message.get('keywords', []) or 'emergency' in message.get('keywords', []) else 'normal'
            frontmatter = self.generate_frontmatter(item_type='whatsapp',
                from_contact=self.sanitize_filename(message.get('contact', 'Unknown')),
                received=datetime.now().isoformat(), priority=priority, status='pending',
                keywords=','.join(message.get('keywords', [])))
            content = f"""{frontmatter}
# WhatsApp Message

**From:** {message.get('contact', 'Unknown')}
**Received:** {datetime.now().strftime('%B %d, %Y at %I:%M %p')}
**Priority:** {priority.upper()}
**Keywords:** {', '.join(message.get('keywords', []))}

---

## Message Content

{message.get('text', 'No content available')}

---

## Suggested Actions

- [ ] Read message carefully
- [ ] Determine urgency
- [ ] Prepare response
"""
            contact = self.sanitize_filename(message.get('contact', 'Unknown'), max_length=20)
            timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
            filename = f"WHATSAPP_{contact}_{timestamp}.md"
            filepath = self.needs_action / filename
            filepath.write_text(content, encoding='utf-8')
            self.logger.info(f"Created action file: {filename}")
            return filepath
        except Exception as e:
            self.logger.error(f"Error creating action file: {e}")
            return None
    
    def test_connection(self):
        print("Testing WhatsApp Web connection...")
        print("A browser window will open. Scan the QR code with your phone.")
        try:
            with sync_playwright() as p:
                browser = p.chromium.launch_persistent_context(user_data_dir=str(self.session_path), headless=False)
                page = browser.pages[0] if browser.pages else browser.new_page()
                page.goto(self.WHATSAPP_WEB_URL)
                print("\nWaiting for QR code scan...")
                try:
                    page.wait_for_selector('[data-testid="chat-list"]', timeout=120000)
                    print("\n[OK] Successfully connected!")
                    print("Session saved. Future runs will auto-login.")
                except PlaywrightTimeout:
                    print("\n[FAIL] QR code scan timeout")
                browser.close()
        except Exception as e:
            print(f"\n[FAIL] Connection test failed: {e}")


def main():
    import argparse
    parser = argparse.ArgumentParser(description='WhatsApp Watcher')
    parser.add_argument('vault_path', nargs='?', default='AI_Employee_Vault')
    parser.add_argument('--keywords', default=None)
    parser.add_argument('--interval', type=int, default=30)
    parser.add_argument('--session-path', default=None)
    parser.add_argument('--test-connection', action='store_true')
    parser.add_argument('--no-headless', action='store_true')
    args = parser.parse_args()
    
    keywords = [k.strip() for k in args.keywords.split(',')] if args.keywords else None
    
    if args.test_connection:
        watcher = WhatsAppWatcher(args.vault_path, session_path=args.session_path,
                                  keywords=keywords, headless=False)
        watcher.test_connection()
        return
    
    headless = not args.no_headless if hasattr(args, 'no_headless') else True
    print(f'WhatsApp Watcher starting... Keywords: {keywords or WhatsAppWatcher.DEFAULT_KEYWORDS}')
    watcher = WhatsAppWatcher(args.vault_path, session_path=args.session_path,
                             keywords=keywords, check_interval=args.interval, headless=headless)
    watcher.run()


if __name__ == '__main__':
    main()
