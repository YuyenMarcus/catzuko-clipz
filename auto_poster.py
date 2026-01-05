"""
Auto Poster - Full automation for posting to TikTok, Instagram, YouTube Shorts
Uses Selenium with human-like behavior to avoid detection
"""
import time
import random
import pickle
from pathlib import Path
from datetime import datetime, timedelta
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import json

class AutoPoster:
    def __init__(self, headless: bool = False):
        """
        Initialize auto poster
        
        Args:
            headless: Run browser in background (set to True for 24/7 operation)
        """
        self.headless = headless
        self.driver = None
        self.cookies_dir = Path("cookies")
        self.cookies_dir.mkdir(exist_ok=True)
    
    def _init_driver(self, mobile_emulation: bool = False):
        """Initialize Chrome driver with anti-detection settings"""
        options = Options()
        
        if self.headless:
            options.add_argument('--headless')
        
        # Anti-detection settings
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-gpu')
        
        # Mobile emulation for Instagram
        if mobile_emulation:
            mobile_emulation = {
                "deviceMetrics": {"width": 375, "height": 812, "pixelRatio": 3.0},
                "userAgent": "Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Mobile/15E148 Safari/604.1"
            }
            options.add_experimental_option("mobileEmulation", mobile_emulation)
        
        try:
            from webdriver_manager.chrome import ChromeDriverManager
            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=options)
        except:
            # Fallback to system chromedriver
            self.driver = webdriver.Chrome(options=options)
        
        # Execute script to remove webdriver property
        self.driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {
            'source': '''
                Object.defineProperty(navigator, 'webdriver', {
                    get: () => undefined
                })
            '''
        })
    
    def human_delay(self, min_sec: float = 2, max_sec: float = 5):
        """Random delay to mimic human behavior"""
        delay = random.uniform(min_sec, max_sec)
        time.sleep(delay)
    
    def _load_cookies(self, cookies_file: Path):
        """Load saved login session cookies"""
        if not cookies_file.exists():
            raise FileNotFoundError(f"Cookies file not found: {cookies_file}")
        
        with open(cookies_file, 'rb') as f:
            cookies = pickle.load(f)
            for cookie in cookies:
                try:
                    self.driver.add_cookie(cookie)
                except Exception as e:
                    print(f"Warning: Could not add cookie: {e}")
    
    def _save_cookies(self, cookies_file: Path):
        """Save login session cookies for reuse"""
        cookies_file.parent.mkdir(parents=True, exist_ok=True)
        with open(cookies_file, 'wb') as f:
            pickle.dump(self.driver.get_cookies(), f)
        print(f"Cookies saved to: {cookies_file}")
    
    def post_to_tiktok(self, video_path: Path, caption: str, cookies_file: Path) -> bool:
        """
        Auto-post to TikTok
        
        Args:
            video_path: Path to video file
            caption: Caption text
            cookies_file: Path to saved cookies
            
        Returns:
            True if successful, False otherwise
        """
        try:
            self._init_driver()
            
            # Load saved session
            self.driver.get('https://www.tiktok.com')
            self.human_delay(2, 4)
            
            try:
                self._load_cookies(cookies_file)
                self.driver.refresh()
                self.human_delay(3, 6)
            except FileNotFoundError:
                print("No saved cookies found. Please run setup_accounts.py first.")
                return False
            
            # Go to upload page
            self.driver.get('https://www.tiktok.com/upload')
            self.human_delay(4, 8)
            
            # Upload video file
            try:
                file_input = WebDriverWait(self.driver, 30).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, 'input[type="file"]'))
                )
                file_input.send_keys(str(video_path.absolute()))
                
                print("Waiting for video to upload and process...")
                self.human_delay(15, 25)
            except TimeoutException:
                print("Could not find file input. TikTok may have changed their interface.")
                return False
            
            # Add caption
            try:
                caption_box = WebDriverWait(self.driver, 30).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, 'div[contenteditable="true"]'))
                )
                self.human_delay(1, 3)
                
                # Clear existing text
                caption_box.clear()
                self.human_delay(0.5, 1)
                
                # Type caption slowly like human
                for char in caption:
                    caption_box.send_keys(char)
                    time.sleep(random.uniform(0.05, 0.15))
                
                self.human_delay(2, 4)
            except TimeoutException:
                print("Could not find caption box. Trying alternative selector...")
                try:
                    caption_box = self.driver.find_element(By.XPATH, "//div[@contenteditable='true']")
                    caption_box.clear()
                    for char in caption:
                        caption_box.send_keys(char)
                        time.sleep(random.uniform(0.05, 0.15))
                except:
                    print("Failed to add caption")
                    return False
            
            # Click post button
            try:
                post_btn = WebDriverWait(self.driver, 30).until(
                    EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Post') or contains(text(), 'Publish')]"))
                )
                self.human_delay(1, 2)
                post_btn.click()
                
                print("Posted to TikTok!")
                self.human_delay(5, 10)
                
                # Save updated cookies
                self._save_cookies(cookies_file)
                
                return True
            except TimeoutException:
                print("Could not find post button")
                return False
                
        except Exception as e:
            print(f"Error posting to TikTok: {e}")
            import traceback
            traceback.print_exc()
            return False
        finally:
            if self.driver:
                self.driver.quit()
    
    def post_to_instagram(self, video_path: Path, caption: str, cookies_file: Path) -> bool:
        """
        Auto-post to Instagram (uses mobile emulation)
        
        Args:
            video_path: Path to video file
            caption: Caption text
            cookies_file: Path to saved cookies
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Use mobile emulation for Instagram
            self._init_driver(mobile_emulation=True)
            
            # Load saved session
            self.driver.get('https://www.instagram.com')
            self.human_delay(2, 4)
            
            try:
                self._load_cookies(cookies_file)
                self.driver.refresh()
                self.human_delay(3, 6)
            except FileNotFoundError:
                print("No saved cookies found. Please run setup_accounts.py first.")
                return False
            
            # Click create post button (mobile view)
            try:
                create_btn = WebDriverWait(self.driver, 30).until(
                    EC.element_to_be_clickable((By.XPATH, "//svg[@aria-label='New post']/.. | //a[contains(@href, '/create/select/')]"))
                )
                create_btn.click()
                self.human_delay(2, 4)
            except TimeoutException:
                # Try alternative method
                try:
                    self.driver.get('https://www.instagram.com/create/select/')
                    self.human_delay(3, 5)
                except:
                    print("Could not access Instagram create page")
                    return False
            
            # Upload file
            try:
                file_input = WebDriverWait(self.driver, 30).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, 'input[type="file"]'))
                )
                file_input.send_keys(str(video_path.absolute()))
                self.human_delay(5, 10)
            except TimeoutException:
                print("Could not find file input for Instagram")
                return False
            
            # Click Next through the steps
            for step in range(3):
                try:
                    next_btn = WebDriverWait(self.driver, 30).until(
                        EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Next')] | //div[contains(text(), 'Next')]"))
                    )
                    self.human_delay(1, 2)
                    next_btn.click()
                    self.human_delay(2, 4)
                except TimeoutException:
                    if step == 0:
                        print("Could not proceed past upload step")
                        return False
                    break  # May have reached caption step
            
            # Add caption
            try:
                caption_input = WebDriverWait(self.driver, 30).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, 'textarea[aria-label*="caption"], textarea[placeholder*="caption"]'))
                )
                
                # Type caption slowly
                for char in caption:
                    caption_input.send_keys(char)
                    time.sleep(random.uniform(0.05, 0.15))
                
                self.human_delay(2, 4)
            except TimeoutException:
                print("Could not find caption input")
                return False
            
            # Share
            try:
                share_btn = WebDriverWait(self.driver, 30).until(
                    EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Share')] | //div[contains(text(), 'Share')]"))
                )
                share_btn.click()
                
                print("Posted to Instagram!")
                self.human_delay(5, 10)
                
                # Save updated cookies
                self._save_cookies(cookies_file)
                
                return True
            except TimeoutException:
                print("Could not find share button")
                return False
                
        except Exception as e:
            print(f"Error posting to Instagram: {e}")
            import traceback
            traceback.print_exc()
            return False
        finally:
            if self.driver:
                self.driver.quit()
    
    def post_to_youtube_shorts(self, video_path: Path, title: str, description: str, cookies_file: Path) -> bool:
        """
        Auto-post to YouTube Shorts
        
        Args:
            video_path: Path to video file
            title: Video title (will add #Shorts)
            description: Video description
            cookies_file: Path to saved cookies
            
        Returns:
            True if successful, False otherwise
        """
        try:
            self._init_driver()
            
            # Load saved session
            self.driver.get('https://studio.youtube.com')
            self.human_delay(3, 5)
            
            try:
                self._load_cookies(cookies_file)
                self.driver.refresh()
                self.human_delay(5, 10)
            except FileNotFoundError:
                print("No saved cookies found. Please run setup_accounts.py first.")
                return False
            
            # Click Create button
            try:
                create_btn = WebDriverWait(self.driver, 30).until(
                    EC.element_to_be_clickable((By.ID, "create-icon"))
                )
                create_btn.click()
                self.human_delay(1, 3)
            except TimeoutException:
                print("Could not find create button")
                return False
            
            # Click Upload Videos
            try:
                upload_btn = WebDriverWait(self.driver, 30).until(
                    EC.element_to_be_clickable((By.XPATH, "//tp-yt-paper-item[@test-id='upload-beta'] | //ytd-topbar-menu-button-renderer[2]"))
                )
                upload_btn.click()
                self.human_delay(2, 4)
            except TimeoutException:
                # Try direct upload URL
                self.driver.get('https://studio.youtube.com/channel/me/videos/upload')
                self.human_delay(3, 5)
            
            # Upload file
            try:
                file_input = WebDriverWait(self.driver, 30).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, 'input[type="file"]'))
                )
                file_input.send_keys(str(video_path.absolute()))
                self.human_delay(10, 20)
            except TimeoutException:
                print("Could not find file input for YouTube")
                return False
            
            # Add title (must include #Shorts)
            try:
                title_input = WebDriverWait(self.driver, 30).until(
                    EC.presence_of_element_located((By.ID, "textbox"))
                )
                title_input.clear()
                title_text = f"{title} #Shorts" if "#Shorts" not in title else title
                title_input.send_keys(title_text)
                self.human_delay(2, 4)
            except TimeoutException:
                print("Could not find title input")
                return False
            
            # Add description
            try:
                description_inputs = self.driver.find_elements(By.ID, "textbox")
                if len(description_inputs) > 1:
                    description_inputs[1].send_keys(description)
                    self.human_delay(2, 4)
            except:
                print("Could not add description (optional)")
            
            # Click Next through steps (usually 3 steps)
            for step in range(3):
                try:
                    next_btn = WebDriverWait(self.driver, 10).until(
                        EC.element_to_be_clickable((By.ID, "next-button"))
                    )
                    self.human_delay(1, 2)
                    next_btn.click()
                    self.human_delay(2, 4)
                except TimeoutException:
                    break  # May have reached final step
            
            # Publish
            try:
                publish_btn = WebDriverWait(self.driver, 30).until(
                    EC.element_to_be_clickable((By.ID, "done-button"))
                )
                publish_btn.click()
                
                print("Posted to YouTube Shorts!")
                self.human_delay(5, 10)
                
                # Save updated cookies
                self._save_cookies(cookies_file)
                
                return True
            except TimeoutException:
                print("Could not find publish button")
                return False
                
        except Exception as e:
            print(f"Error posting to YouTube: {e}")
            import traceback
            traceback.print_exc()
            return False
        finally:
            if self.driver:
                self.driver.quit()


class SafeAutoPoster:
    """Wrapper that adds safety limits and human-like behavior"""
    
    def __init__(self, headless: bool = False):
        self.poster = AutoPoster(headless=headless)
        self.post_history_file = Path("post_history.json")
        self.post_history = self._load_history()
        self.max_posts_per_day = 5
    
    def _load_history(self) -> dict:
        """Load post history from file"""
        if self.post_history_file.exists():
            try:
                with open(self.post_history_file, 'r') as f:
                    return json.load(f)
            except:
                return {}
        return {}
    
    def _save_history(self):
        """Save post history to file"""
        with open(self.post_history_file, 'w') as f:
            json.dump(self.post_history, f, indent=2)
    
    def should_post(self, account_id: str) -> bool:
        """Check if account can post today (max 5 posts per day)"""
        today = datetime.now().date().isoformat()
        
        if account_id not in self.post_history:
            self.post_history[account_id] = {}
        
        if today not in self.post_history[account_id]:
            self.post_history[account_id][today] = 0
        
        return self.post_history[account_id][today] < self.max_posts_per_day
    
    def record_post(self, account_id: str):
        """Record successful post"""
        today = datetime.now().date().isoformat()
        
        if account_id not in self.post_history:
            self.post_history[account_id] = {}
        
        if today not in self.post_history[account_id]:
            self.post_history[account_id][today] = 0
        
        self.post_history[account_id][today] += 1
        self._save_history()
    
    def post_with_safety(self, platform: str, video_path: Path, caption: str, 
                         account_config: dict) -> bool:
        """
        Post with safety checks and human-like delays
        
        Args:
            platform: 'tiktok', 'instagram', or 'youtube'
            video_path: Path to video file
            caption: Caption text
            account_config: Dict with 'username' and 'cookies_file' keys
            
        Returns:
            True if posted successfully
        """
        account_id = f"{platform}_{account_config['username']}"
        cookies_file = Path(account_config['cookies_file'])
        
        # Check daily limit
        if not self.should_post(account_id):
            print(f"Daily limit reached for {account_id} (max {self.max_posts_per_day} posts/day)")
            return False
        
        # Random delay before posting (15min - 3hrs)
        delay_minutes = random.randint(15, 180)
        print(f"Waiting {delay_minutes} minutes before posting to {platform}...")
        time.sleep(delay_minutes * 60)
        
        # Post
        try:
            if platform == 'tiktok':
                success = self.poster.post_to_tiktok(video_path, caption, cookies_file)
            elif platform == 'instagram':
                success = self.poster.post_to_instagram(video_path, caption, cookies_file)
            elif platform == 'youtube':
                # For YouTube, use caption as title and description
                success = self.poster.post_to_youtube_shorts(
                    video_path, caption, caption, cookies_file
                )
            else:
                print(f"Unknown platform: {platform}")
                return False
            
            if success:
                self.record_post(account_id)
                print(f"✓ Successfully posted to {platform} via {account_config['username']}")
                return True
            else:
                print(f"✗ Failed to post to {platform}")
                return False
                
        except Exception as e:
            print(f"Error posting to {platform}: {e}")
            import traceback
            traceback.print_exc()
            return False

