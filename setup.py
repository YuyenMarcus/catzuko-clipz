"""
Setup script for Clipfarm
Helps verify all dependencies are installed correctly
"""
import subprocess
import sys
from pathlib import Path

def check_python_version():
    """Check Python version"""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("[X] Python 3.8+ required")
        return False
    print(f"[OK] Python {version.major}.{version.minor}.{version.micro}")
    return True

def check_package(package_name, import_name=None):
    """Check if a Python package is installed"""
    if import_name is None:
        import_name = package_name
    
    try:
        __import__(import_name)
        print(f"[OK] {package_name}")
        return True
    except ImportError:
        print(f"[X] {package_name} - Install with: pip install {package_name}")
        return False

def check_command(command, name):
    """Check if a command-line tool is available"""
    try:
        result = subprocess.run(
            [command, '--version'],
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            print(f"[OK] {name}")
            return True
        else:
            print(f"[X] {name} - Not found in PATH")
            return False
    except FileNotFoundError:
        print(f"[X] {name} - Not found in PATH")
        return False

def check_ollama():
    """Check if Ollama is installed and running"""
    try:
        import ollama
        models = ollama.list()
        model_names = [m['name'] for m in models.get('models', [])]
        if model_names:
            print(f"[OK] Ollama (models: {', '.join(model_names)})")
            return True
        else:
            print("[!] Ollama installed but no models found. Run: ollama pull llama3.1")
            return False
    except Exception as e:
        print(f"[X] Ollama - {e}")
        print("   Download from https://ollama.ai")
        return False

def create_directories():
    """Create necessary directories"""
    dirs = [
        "downloads",
        "clips",
        "ready_to_post/tiktok",
        "ready_to_post/instagram",
        "ready_to_post/youtube_shorts"
    ]
    
    for dir_path in dirs:
        Path(dir_path).mkdir(parents=True, exist_ok=True)
    
    print("[OK] Created directories")

def main():
    """Run all checks"""
    print("Clipfarm Setup Check")
    print("=" * 50)
    
    all_ok = True
    
    print("\n1. Python Version:")
    if not check_python_version():
        all_ok = False
    
    print("\n2. Python Packages:")
    packages = [
        ("yt-dlp", "yt_dlp"),
        ("feedparser", "feedparser"),
        ("openai-whisper", "whisper"),
        ("ollama", "ollama"),
        ("moviepy", "moviepy"),
        ("selenium", "selenium"),
    ]
    
    for package_name, import_name in packages:
        if not check_package(package_name, import_name):
            all_ok = False
    
    print("\n3. Command-Line Tools:")
    if not check_command("ffmpeg", "FFmpeg"):
        all_ok = False
    
    print("\n4. Ollama:")
    check_ollama()  # Warning only, not critical
    
    print("\n5. Directories:")
    create_directories()
    
    print("\n" + "=" * 50)
    if all_ok:
        print("\n[OK] All critical dependencies are installed!")
        print("\nNext steps:")
        print("1. Edit config.py and add YouTube channel IDs")
        print("2. Run: python main.py")
    else:
        print("\n[!] Some dependencies are missing.")
        print("Install missing packages with: pip install -r requirements.txt")
        print("Install FFmpeg from: https://ffmpeg.org/download.html")
    
    print("\n" + "=" * 50)

if __name__ == "__main__":
    main()

