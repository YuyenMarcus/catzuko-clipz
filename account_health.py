"""
Account Health Tracker
Tracks cookie expiration dates and provides refresh tools
"""
import pickle
import json
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List

COOKIES_DIR = Path("cookies")
HEALTH_FILE = Path("account_health.json")

class AccountHealthTracker:
    """Tracks account health and cookie expiration"""
    
    def __init__(self):
        self.health_data = self._load_health()
        self.cookies_dir = COOKIES_DIR
        self.cookies_dir.mkdir(exist_ok=True)
    
    def _load_health(self) -> Dict:
        """Load health data from file"""
        if HEALTH_FILE.exists():
            try:
                with open(HEALTH_FILE, 'r') as f:
                    return json.load(f)
            except:
                pass
        return {}
    
    def _save_health(self):
        """Save health data to file"""
        with open(HEALTH_FILE, 'w') as f:
            json.dump(self.health_data, f, indent=2)
    
    def update_cookie_date(self, platform: str, account: str):
        """Update cookie last updated date"""
        key = f"{platform}_{account}"
        self.health_data[key] = {
            'platform': platform,
            'account': account,
            'last_updated': datetime.now().isoformat(),
            'expires_in_days': 30  # Default expiration
        }
        self._save_health()
    
    def get_account_health(self) -> List[Dict]:
        """Get health status for all accounts"""
        health_list = []
        
        # Check all cookie files
        for cookie_file in self.cookies_dir.glob("*.pkl"):
            parts = cookie_file.stem.split('_')
            if len(parts) >= 2:
                platform = parts[0]
                account = '_'.join(parts[1:])
                
                key = f"{platform}_{account}"
                health_info = self.health_data.get(key, {})
                
                last_updated = health_info.get('last_updated')
                if last_updated:
                    last_date = datetime.fromisoformat(last_updated)
                    days_since = (datetime.now() - last_date).days
                    days_until_expiry = 30 - days_since
                    
                    status = 'healthy' if days_until_expiry > 7 else 'expiring_soon' if days_until_expiry > 0 else 'expired'
                else:
                    days_until_expiry = None
                    status = 'unknown'
                
                health_list.append({
                    'platform': platform,
                    'account': account,
                    'cookie_file': str(cookie_file),
                    'last_updated': last_updated,
                    'days_until_expiry': days_until_expiry,
                    'status': status,
                    'file_exists': cookie_file.exists()
                })
        
        return health_list
    
    def check_cookie_validity(self, cookie_file: Path) -> bool:
        """Check if cookie file exists and is readable"""
        if not cookie_file.exists():
            return False
        
        try:
            with open(cookie_file, 'rb') as f:
                cookies = pickle.load(f)
                return len(cookies) > 0
        except:
            return False
    
    def upload_cookie(self, platform: str, account: str, cookie_data: bytes):
        """Upload new cookie file"""
        cookie_file = self.cookies_dir / f"{platform}_{account}.pkl"
        
        try:
            with open(cookie_file, 'wb') as f:
                f.write(cookie_data)
            
            self.update_cookie_date(platform, account)
            return True
        except Exception as e:
            print(f"Error saving cookie: {e}")
            return False


# Global instance
health_tracker = AccountHealthTracker()

def get_account_health() -> List[Dict]:
    """Get health status for all accounts"""
    return health_tracker.get_account_health()

def update_cookie_date(platform: str, account: str):
    """Update cookie last updated date"""
    health_tracker.update_cookie_date(platform, account)

