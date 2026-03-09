"""
LinkedIn Poster

Automatically posts updates to LinkedIn for business promotion.
Uses Playwright to automate LinkedIn posting.

Silver Tier Skill - Requires Playwright
"""

import os
import sys
import time
import json
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any, Optional

sys.path.insert(0, str(Path(__file__).parent))

try:
    from base_watcher import BaseWatcher
except ImportError:
    from watchers.base_watcher import BaseWatcher

try:
    from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False


class LinkedInPoster(BaseWatcher):
    LINKEDIN_URL = 'https://www.linkedin.com'
    MAX_POSTS_PER_DAY = 3
    
    def __init__(self, vault_path: str, email: Optional[str] = None,
                 password: Optional[str] = None, session_path: Optional[str] = None,
                 headless: bool = True):
        if not PLAYWRIGHT_AVAILABLE:
            raise ImportError("Playwright not installed. Run: pip install playwright")
        
        self.vault_path = Path(vault_path)
        self.approved_folder = self.vault_path / 'Approved'
        self.done_folder = self.vault_path / 'Done'
        self.logs_folder = self.vault_path / 'Logs'
        
        for folder in [self.approved_folder, self.done_folder, self.logs_folder]:
            folder.mkdir(parents=True, exist_ok=True)
        
        self._setup_logging()
        self.email = email or os.getenv('LINKEDIN_EMAIL')
        self.password = password or os.getenv('LINKEDIN_PASSWORD')
        self.session_path = Path(session_path) if session_path else self.vault_path / 'linkedin_session'
        self.session_path.mkdir(parents=True, exist_ok=True)
        self.headless = headless
        self.posts_today = 0
        self._load_post_count()
    
    def _setup_logging(self):
        import logging
        log_file = self.logs_folder / f'linkedin_{datetime.now().strftime("%Y-%m-%d")}.log'
        logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                          handlers=[logging.FileHandler(log_file, encoding='utf-8'), logging.StreamHandler()])
        self.logger = logging.getLogger('LinkedInPoster')
    
    def _load_post_count(self):
        count_file = self.logs_folder / 'linkedin_post_count.json'
        if count_file.exists():
            with open(count_file, 'r') as f:
                data = json.load(f)
                if data.get('date') == datetime.now().strftime('%Y-%m-%d'):
                    self.posts_today = data.get('count', 0)
    
    def _save_post_count(self):
        count_file = self.logs_folder / 'linkedin_post_count.json'
        with open(count_file, 'w') as f:
            json.dump({'date': datetime.now().strftime('%Y-%m-%d'), 'count': self.posts_today}, f)
    
    def get_approved_posts(self) -> List[Path]:
        posts = []
        try:
            for file_path in self.approved_folder.iterdir():
                if file_path.is_file() and file_path.suffix == '.md':
                    content = file_path.read_text(encoding='utf-8')
                    if 'type: linkedin_post' in content or 'LinkedIn Post Draft' in content:
                        posts.append(file_path)
        except Exception as e:
            self.logger.error(f"Error reading approved folder: {e}")
        return posts
    
    def parse_post_file(self, file_path: Path) -> Dict[str, Any]:
        content = file_path.read_text(encoding='utf-8')
        post_content = ""
        in_content = False
        for line in content.split('\n'):
            if '## Content' in line:
                in_content = True
                continue
            elif in_content:
                if line.startswith('##') or line.startswith('---'):
                    break
                post_content += line + '\n'
        if not post_content.strip():
            lines = content.split('\n')
            in_frontmatter = False
            for i, line in enumerate(lines):
                if line.strip() == '---':
                    in_frontmatter = not in_frontmatter
                elif not in_frontmatter and i > 0:
                    post_content = '\n'.join(lines[i:])
                    break
        return {'file_path': file_path, 'content': post_content.strip(), 'filename': file_path.name}
    
    def publish_post(self, post_data: Dict[str, Any], dry_run: bool = False) -> bool:
        if dry_run:
            self.logger.info(f"[DRY RUN] Would publish: {post_data['filename']}")
            self.logger.info(f"[DRY RUN] Content: {post_data['content'][:100]}...")
            return True
        try:
            with sync_playwright() as p:
                browser = p.chromium.launch_persistent_context(
                    user_data_dir=str(self.session_path), headless=self.headless,
                    args=['--disable-blink-features=AutomationControlled'])
                page = browser.pages[0] if browser.pages else browser.new_page()
                page.goto(self.LINKEDIN_URL, wait_until='domcontentloaded', timeout=60000)
                if not self._is_logged_in(page):
                    if not self._login(page):
                        browser.close()
                        return False
                page.goto(f"{self.LINKEDIN_URL}/feed/update/", wait_until='domcontentloaded', timeout=30000)
                try:
                    editor = page.wait_for_selector('[role="textbox"]', timeout=10000)
                    editor.fill('')
                    editor.fill(post_data['content'])
                    time.sleep(1)
                    post_button = page.query_selector('button:has-text("Post")')
                    if post_button:
                        post_button.click()
                        time.sleep(3)
                        self.posts_today += 1
                        self._save_post_count()
                        self.logger.info("Post published successfully!")
                        return True
                except PlaywrightTimeout:
                    self.logger.error("Editor not found")
                browser.close()
                return False
        except Exception as e:
            self.logger.error(f"Error publishing post: {e}")
            return False
    
    def _is_logged_in(self, page) -> bool:
        try:
            page.wait_for_selector('[data-test-id="topbar-logo"]', timeout=5000)
            return True
        except PlaywrightTimeout:
            return False
    
    def _login(self, page) -> bool:
        try:
            page.wait_for_selector('#session_key', timeout=10000)
            page.fill('#session_key', self.email)
            page.fill('#session_password', self.password)
            page.click('button[type="submit"]')
            page.wait_for_load_state('domcontentloaded', timeout=30000)
            return self._is_logged_in(page)
        except PlaywrightTimeout:
            self.logger.error("Login form not found")
            return False
        except Exception as e:
            self.logger.error(f"Login error: {e}")
            return False
    
    def run(self, dry_run: bool = False):
        self.logger.info("Starting LinkedIn Poster")
        self.logger.info(f"Posts today: {self.posts_today}/{self.MAX_POSTS_PER_DAY}")
        if self.posts_today >= self.MAX_POSTS_PER_DAY:
            self.logger.warning("Daily post limit reached")
            return
        posts = self.get_approved_posts()
        self.logger.info(f"Found {len(posts)} approved post(s)")
        if not posts:
            self.logger.info("No posts to publish")
            return
        for post in posts:
            if self.posts_today >= self.MAX_POSTS_PER_DAY:
                break
            post_data = self.parse_post_file(post)
            self.logger.info(f"Processing: {post_data['filename']}")
            if self.publish_post(post_data, dry_run=dry_run):
                done_path = self.done_folder / f"DONE_{post.name}"
                post.rename(done_path)
                self.logger.info(f"Moved to Done: {done_path.name}")


def main():
    import argparse
    parser = argparse.ArgumentParser(description='LinkedIn Poster')
    parser.add_argument('vault_path', nargs='?', default='AI_Employee_Vault')
    parser.add_argument('--email', default=None)
    parser.add_argument('--password', default=None)
    parser.add_argument('--dry-run', action='store_true')
    parser.add_argument('--test-login', action='store_true')
    parser.add_argument('--no-headless', action='store_true')
    args = parser.parse_args()
    
    email = args.email or os.getenv('LINKEDIN_EMAIL')
    password = args.password or os.getenv('LINKEDIN_PASSWORD')
    
    if not email:
        print("Error: LinkedIn email required. Set --email or LINKEDIN_EMAIL env var.")
        return
    
    poster = LinkedInPoster(args.vault_path, email=email, password=password, headless=not args.no_headless)
    
    if args.test_login:
        print("Testing LinkedIn login...")
        try:
            with sync_playwright() as p:
                browser = p.chromium.launch_persistent_context(user_data_dir=str(poster.session_path), headless=False)
                page = browser.pages[0] if browser.pages else browser.new_page()
                page.goto(LinkedInPoster.LINKEDIN_URL)
                if poster._is_logged_in(page):
                    print("[OK] Already logged in")
                elif poster._login(page):
                    print("[OK] Login successful")
                else:
                    print("[FAIL] Login failed")
                browser.close()
        except Exception as e:
            print(f"[FAIL] Test failed: {e}")
        return
    
    poster.run(dry_run=args.dry_run)


if __name__ == '__main__':
    main()
