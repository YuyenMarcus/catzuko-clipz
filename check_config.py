"""
Configuration Checker
Verifies all required components are properly configured before deployment
"""
import subprocess
import sys
import os
from pathlib import Path

def check_ollama():
    """Check if Ollama is running and accessible"""
    print("\n" + "="*60)
    print("1. CHECKING OLLAMA CONNECTION")
    print("="*60)
    
    try:
        import ollama
        
        # Try to list models
        try:
            models = ollama.list()
            model_names = [m['name'] for m in models.get('models', [])]
            
            if not model_names:
                print("[X] Ollama is running but NO MODELS found!")
                print("   Run: ollama pull llama3.1")
                return False
            
            print(f"[OK] Ollama is running")
            print(f"   Available models: {', '.join(model_names)}")
            
            # Check for llama3.1 specifically
            if 'llama3.1' in model_names or any('llama3.1' in m for m in model_names):
                print("[OK] Llama 3.1 model found")
            else:
                print("[!] Llama 3.1 not found (recommended)")
                print("   Run: ollama pull llama3.1")
            
            # Test a simple generation
            try:
                response = ollama.generate(model=model_names[0], prompt="test")
                print("[OK] Ollama API is responding correctly")
                return True
            except Exception as e:
                print(f"[X] Ollama API test failed: {e}")
                return False
                
        except Exception as e:
            print(f"[X] Cannot connect to Ollama: {e}")
            print("   Make sure Ollama is running:")
            print("   - Windows: Check if Ollama service is running")
            print("   - Mac/Linux: Run 'ollama serve' in terminal")
            return False
            
    except ImportError:
        print("[X] Ollama Python package not installed")
        print("   Run: pip install ollama")
        return False

def check_ffmpeg():
    """Check if FFmpeg is in PATH"""
    print("\n" + "="*60)
    print("2. CHECKING FFMPEG PATH")
    print("="*60)
    
    try:
        # Try to run ffmpeg
        result = subprocess.run(
            ['ffmpeg', '-version'],
            capture_output=True,
            text=True,
            timeout=5
        )
        
        if result.returncode == 0:
            # Extract version info
            version_line = result.stdout.split('\n')[0]
            print(f"[OK] FFmpeg is accessible")
            print(f"   {version_line}")
            
            # Check if ffprobe is also available
            try:
                subprocess.run(['ffprobe', '-version'], capture_output=True, timeout=5, check=True)
                print("[OK] ffprobe is also available")
            except:
                print("[!] ffprobe not found (needed for video info)")
            
            return True
        else:
            print("[X] FFmpeg command failed")
            return False
            
    except FileNotFoundError:
        print("[X] FFmpeg NOT FOUND in PATH")
        print("\n   To fix on Windows:")
        print("   1. Download FFmpeg from https://ffmpeg.org/download.html")
        print("   2. Extract to a folder (e.g., C:\\ffmpeg)")
        print("   3. Add to System PATH:")
        print("      - Right-click 'This PC' -> Properties")
        print("      - Advanced System Settings -> Environment Variables")
        print("      - Edit 'Path' -> Add folder containing ffmpeg.exe")
        print("   4. Restart terminal/Python")
        return False
    except subprocess.TimeoutExpired:
        print("[X] FFmpeg command timed out")
        return False
    except Exception as e:
        print(f"[X] Error checking FFmpeg: {e}")
        return False

def check_vercel_setup():
    """Check Vercel deployment considerations"""
    print("\n" + "="*60)
    print("3. VERCEL/CLOUD CONSIDERATIONS")
    print("="*60)
    
    print("[!] IMPORTANT: Video Processing Limitations")
    print("\n   Your videos are processed LOCALLY on your machine.")
    print("   The Vercel-hosted dashboard has these limitations:\n")
    
    print("   [X] Live Feed videos won't work on Vercel")
    print("      (Vercel has read-only filesystem)")
    print("\n   [OK] Solutions:")
    print("      1. Run dashboard locally: python web_dashboard.py")
    print("      2. Use Cloudflare Tunnel (free):")
    print("         - Install: https://developers.cloudflare.com/cloudflare-one/connections/connect-apps/")
    print("         - Run: cloudflared tunnel --url http://localhost:5000")
    print("      3. Use ngrok (free tier):")
    print("         - Install: https://ngrok.com/")
    print("         - Run: ngrok http 5000")
    print("\n   [OK] What WILL work on Vercel:")
    print("      - Status monitoring")
    print("      - Analytics dashboard")
    print("      - Log viewer")
    print("      - Settings toggles")
    print("      - Queue management")
    print("\n   [*] Recommended Setup:")
    print("      - Vercel: Host dashboard UI (monitoring only)")
    print("      - Local: Run automation + dashboard (full features)")
    print("      - Cloud Storage: Store clips (S3, Cloudinary) for remote access")
    
    return True

def check_database():
    """Check database initialization"""
    print("\n" + "="*60)
    print("4. CHECKING DATABASE")
    print("="*60)
    
    try:
        from models import init_db, get_connection
        
        # Initialize if needed
        init_db()
        
        # Test connection
        conn = get_connection()
        conn.close()
        
        db_file = Path("clipfarm.db")
        if db_file.exists():
            size = db_file.stat().st_size
            print(f"[OK] Database initialized: clipfarm.db ({size} bytes)")
            return True
        else:
            print("[X] Database file not found after initialization")
            return False
            
    except Exception as e:
        print(f"[X] Database check failed: {e}")
        return False

def check_directories():
    """Check required directories exist"""
    print("\n" + "="*60)
    print("5. CHECKING DIRECTORIES")
    print("="*60)
    
    from config import DOWNLOADS_DIR, CLIPS_DIR, READY_TO_POST_DIR
    
    dirs = [
        ("Downloads", DOWNLOADS_DIR),
        ("Clips", CLIPS_DIR),
        ("Ready to Post", READY_TO_POST_DIR),
    ]
    
    all_ok = True
    for name, path in dirs:
        if path.exists():
            print(f"[OK] {name}: {path}")
        else:
            print(f"[!] {name}: {path} (will be created on first run)")
            path.mkdir(parents=True, exist_ok=True)
    
    return True

def main():
    """Run all checks"""
    print("\n" + "="*60)
    print("CLIPFARM CONFIGURATION CHECKER")
    print("="*60)
    print("\nVerifying all components before deployment...")
    
    results = {
        'Ollama': check_ollama(),
        'FFmpeg': check_ffmpeg(),
        'Database': check_database(),
        'Directories': check_directories(),
    }
    
    check_vercel_setup()  # Info only, doesn't fail
    
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    
    all_passed = all(results.values())
    
    for component, passed in results.items():
        status = "[OK] PASS" if passed else "[X] FAIL"
        print(f"{status}: {component}")
    
    if all_passed:
        print("\n[OK] All critical components are configured!")
        print("   You're ready to deploy!")
    else:
        print("\n[!] Some components need attention before deployment.")
        print("   Fix the issues above and run this checker again.")
    
    print("\n" + "="*60)
    
    return 0 if all_passed else 1

if __name__ == "__main__":
    sys.exit(main())

