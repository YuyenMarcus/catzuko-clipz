"""
Affiliate Link Rotator
Rotates through multiple Whop affiliate links to avoid spam detection
"""
import json
import random
from pathlib import Path
from typing import List, Optional
from datetime import datetime

LINKS_FILE = Path("affiliate_links.json")

class LinkRotator:
    """Rotates through affiliate links"""
    
    def __init__(self):
        self.links = self._load_links()
        self.usage_history = self._load_history()
    
    def _load_links(self) -> List[Dict]:
        """Load affiliate links from file"""
        if LINKS_FILE.exists():
            try:
                with open(LINKS_FILE, 'r') as f:
                    data = json.load(f)
                    return data.get('links', [])
            except:
                pass
        
        # Default structure
        default_links = {
            'links': [
                {
                    'url': '',
                    'niche': 'general',
                    'weight': 1,
                    'enabled': True
                }
            ]
        }
        
        # Create default file
        with open(LINKS_FILE, 'w') as f:
            json.dump(default_links, f, indent=2)
        
        return default_links['links']
    
    def _load_history(self) -> Dict:
        """Load usage history"""
        history_file = Path("link_history.json")
        if history_file.exists():
            try:
                with open(history_file, 'r') as f:
                    return json.load(f)
            except:
                pass
        return {}
    
    def _save_history(self):
        """Save usage history"""
        history_file = Path("link_history.json")
        with open(history_file, 'w') as f:
            json.dump(self.usage_history, f, indent=2)
    
    def get_link(self, niche: str = 'general', avoid_recent: bool = True) -> Optional[str]:
        """
        Get a rotated affiliate link
        
        Args:
            niche: Link niche/category (general, trading, ecom, etc.)
            avoid_recent: Avoid links used in last 5 posts
            
        Returns:
            Affiliate link URL
        """
        # Filter enabled links
        enabled_links = [l for l in self.links if l.get('enabled', True)]
        
        if not enabled_links:
            return None
        
        # Filter by niche if specified
        niche_links = [l for l in enabled_links if l.get('niche', 'general') == niche]
        if not niche_links:
            niche_links = enabled_links  # Fallback to all links
        
        # Avoid recently used links
        if avoid_recent and self.usage_history:
            recent_links = list(self.usage_history.keys())[-5:]
            available_links = [l for l in niche_links if l['url'] not in recent_links]
            if available_links:
                niche_links = available_links
        
        # Weighted random selection
        weights = [l.get('weight', 1) for l in niche_links]
        selected = random.choices(niche_links, weights=weights, k=1)[0]
        
        # Record usage
        today = datetime.now().date().isoformat()
        if today not in self.usage_history:
            self.usage_history[today] = []
        self.usage_history[today].append(selected['url'])
        self._save_history()
        
        return selected['url']
    
    def add_link(self, url: str, niche: str = 'general', weight: int = 1):
        """Add a new affiliate link"""
        new_link = {
            'url': url,
            'niche': niche,
            'weight': weight,
            'enabled': True
        }
        
        # Check if already exists
        if any(l['url'] == url for l in self.links):
            print(f"Link already exists: {url}")
            return
        
        self.links.append(new_link)
        self._save_links()
    
    def _save_links(self):
        """Save links to file"""
        with open(LINKS_FILE, 'w') as f:
            json.dump({'links': self.links}, f, indent=2)
    
    def get_stats(self) -> Dict:
        """Get link rotation statistics"""
        today = datetime.now().date().isoformat()
        today_usage = self.usage_history.get(today, [])
        
        link_counts = {}
        for url in today_usage:
            link_counts[url] = link_counts.get(url, 0) + 1
        
        return {
            'total_links': len(self.links),
            'enabled_links': len([l for l in self.links if l.get('enabled', True)]),
            'used_today': len(today_usage),
            'link_distribution': link_counts
        }


# Global instance
rotator = LinkRotator()

def get_affiliate_link(niche: str = 'general') -> str:
    """Get a rotated affiliate link"""
    link = rotator.get_link(niche)
    return link or "Link in bio 🔗"  # Fallback

