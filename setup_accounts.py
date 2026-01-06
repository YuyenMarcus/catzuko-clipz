"""
Setup Accounts - One-time script to login and save cookies
Run this ONCE for each platform account you want to use
"""
import pickle
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

class AccountSetup:
    def __init__(self):
        self.cookies_dir = Path("cookies")
        self.cookies_dir.mkdir(exist_ok=True)
    
    def _init_driver(self, mobile: bool = False):
        """Initialize Chrome driver"""
        options = Options()
        
        # Mobile emulation for Instagram
        if mobile:
            mobile_emulation = {
                "deviceMetrics": {"width": 375, "height": 812, "pixelRatio": 3.0},
                "userAgent": "Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X) AppleWebKit/605.1.15"
            }
            options.add_experimental_option("mobileEmulation", mobile_emulation)
        
        try:
            from webdriver_manager.chrome import ChromeDriverManager
            service = Service(ChromeDriverManager().install())
            driver = webdriver.Chrome(service=service, options=options)
        except:
            driver = webdriver.Chrome(options=options)
        
        return driver
    
    def setup_tiktok(self, account_name: str = "account1"):
        """Setup TikTok account - login and save cookies"""
        print(f"\n{'='*60}")
        print(f"Setting up TikTok account: {account_name}")
        print(f"{'='*60}")
        print("\n1. A browser window will open")
        print("2. Login to TikTok manually")
        print("3. Once logged in, press Enter here to save cookies")
        print("\nPress Enter to start...")
        input()
        
        driver = self._init_driver()
        
        try:
            driver.get('https://www.tiktok.com/login')
            print("\n✓ Browser opened. Please login to TikTok...")
            print("   After logging in, come back here and press Enter")
            input("\nPress Enter after you've logged in...")
            
            # Save cookies
            cookies_file = self.cookies_dir / f"tiktok_{account_name}.pkl"
            with open(cookies_file, 'wb') as f:
                pickle.dump(driver.get_cookies(), f)
            
            print(f"\n✅ TikTok cookies saved to: {cookies_file}")
            print("   You can now use this account for auto-posting!")
            
            # Update account health tracker
            try:
                from account_health import update_cookie_date
                update_cookie_date('tiktok', account_name)
            except:
                pass
            
        except Exception as e:
            print(f"\n❌ Error: {e}")
        finally:
            driver.quit()
    
    def setup_instagram(self, account_name: str = "account1"):
        """Setup Instagram account - login and save cookies"""
        print(f"\n{'='*60}")
        print(f"Setting up Instagram account: {account_name}")
        print(f"{'='*60}")
        print("\n1. A browser window will open (mobile view)")
        print("2. Login to Instagram manually")
        print("3. Once logged in, press Enter here to save cookies")
        print("\nPress Enter to start...")
        input()
        
        driver = self._init_driver(mobile=True)
        
        try:
            driver.get('https://www.instagram.com/accounts/login/')
            print("\n✓ Browser opened (mobile view). Please login to Instagram...")
            print("   After logging in, come back here and press Enter")
            input("\nPress Enter after you've logged in...")
            
            # Save cookies
            cookies_file = self.cookies_dir / f"instagram_{account_name}.pkl"
            with open(cookies_file, 'wb') as f:
                pickle.dump(driver.get_cookies(), f)
            
            print(f"\n✅ Instagram cookies saved to: {cookies_file}")
            print("   You can now use this account for auto-posting!")
            
            # Update account health tracker
            try:
                from account_health import update_cookie_date
                update_cookie_date('instagram', account_name)
            except:
                pass
            
        except Exception as e:
            print(f"\n❌ Error: {e}")
        finally:
            driver.quit()
    
    def setup_youtube(self, account_name: str = "account1"):
        """Setup YouTube account - login and save cookies"""
        print(f"\n{'='*60}")
        print(f"Setting up YouTube account: {account_name}")
        print(f"{'='*60}")
        print("\n1. A browser window will open")
        print("2. Login to YouTube/Google manually")
        print("3. Navigate to YouTube Studio")
        print("4. Once there, press Enter here to save cookies")
        print("\nPress Enter to start...")
        input()
        
        driver = self._init_driver()
        
        try:
            driver.get('https://accounts.google.com/signin')
            print("\n✓ Browser opened. Please login to Google/YouTube...")
            print("   After logging in, navigate to https://studio.youtube.com")
            print("   Then come back here and press Enter")
            input("\nPress Enter after you've logged in and are on YouTube Studio...")
            
            # Save cookies
            cookies_file = self.cookies_dir / f"youtube_{account_name}.pkl"
            with open(cookies_file, 'wb') as f:
                pickle.dump(driver.get_cookies(), f)
            
            print(f"\n✅ YouTube cookies saved to: {cookies_file}")
            print("   You can now use this account for auto-posting!")
            
            # Update account health tracker
            try:
                from account_health import update_cookie_date
                update_cookie_date('youtube', account_name)
            except:
                pass
            
        except Exception as e:
            print(f"\n❌ Error: {e}")
        finally:
            driver.quit()
    
    def setup_all(self):
        """Interactive setup for all platforms"""
        print("\n" + "="*60)
        print("CLIPFARM ACCOUNT SETUP")
        print("="*60)
        print("\nThis script will help you save login sessions for auto-posting.")
        print("You only need to do this ONCE per account.")
        print("\nCookies typically last 30 days before needing to refresh.")
        print("\n" + "="*60)
        
        while True:
            print("\nWhat would you like to setup?")
            print("1. TikTok account")
            print("2. Instagram account")
            print("3. YouTube account")
            print("4. Setup all platforms (one at a time)")
            print("5. Exit")
            
            choice = input("\nEnter choice (1-5): ").strip()
            
            if choice == "1":
                account_name = input("Enter account name (e.g., 'account1'): ").strip() or "account1"
                self.setup_tiktok(account_name)
            elif choice == "2":
                account_name = input("Enter account name (e.g., 'account1'): ").strip() or "account1"
                self.setup_instagram(account_name)
            elif choice == "3":
                account_name = input("Enter account name (e.g., 'account1'): ").strip() or "account1"
                self.setup_youtube(account_name)
            elif choice == "4":
                account_name = input("Enter account name (e.g., 'account1'): ").strip() or "account1"
                print("\nSetting up all platforms...")
                self.setup_tiktok(account_name)
                self.setup_instagram(account_name)
                self.setup_youtube(account_name)
            elif choice == "5":
                print("\nSetup complete! You can now use auto-posting.")
                break
            else:
                print("Invalid choice. Please try again.")


if __name__ == "__main__":
    setup = AccountSetup()
    setup.setup_all()

