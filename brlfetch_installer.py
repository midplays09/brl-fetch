"""
brlfetch Installer + Updater
Installs or updates brlfetch to ~/.local/bin/brlfetch
Supports updating via a remote URL with -u/--update
"""

import os
import sys
import subprocess
import urllib.request
from pathlib import Path

# Configuration
INSTALL_DIR = Path.home() / ".local" / "bin"
SCRIPT_PATH = INSTALL_DIR / "brlfetch"
REMOTE_URL = "https://raw.githubusercontent.com/yourusername/brlfetch/main/brlfetch.py"  # change to your repo/pastebin raw

# =============================================================================
# COLORS
# =============================================================================
class Colors:
    RESET = '\033[0m'
    BOLD = '\033[1m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    RED = '\033[91m'
    CYAN = '\033[96m'

# =============================================================================
# UTILITY FUNCTIONS
# =============================================================================
def print_step(step, msg):
    print(f"{Colors.BLUE}[{step}]{Colors.RESET} {msg}")

def print_success(msg):
    print(f"{Colors.GREEN}✔ {msg}{Colors.RESET}")

def print_warning(msg):
    print(f"{Colors.YELLOW}⚠ {msg}{Colors.RESET}")

def print_error(msg):
    print(f"{Colors.RED}✖ {msg}{Colors.RESET}")

def check_python():
    print_step(1, "Checking Python version...")
    if sys.version_info < (3,6):
        print_error("Python 3.6+ required")
        return False
    print_success(f"Python {sys.version.split()[0]} OK")
    return True

def install_dependencies():
    print_step(2, "Checking dependencies...")
    try:
        import psutil
        print_success("psutil found")
        return True
    except ImportError:
        print_warning("psutil not found (memory/disk info may show 'unknown')")
        resp = input("Install psutil now? (y/n): ").strip().lower()
        if resp in ["y","yes"]:
            try:
                subprocess.check_call([sys.executable,"-m","pip","install","psutil"])
                print_success("psutil installed")
            except Exception as e:
                print_error(f"Failed to install psutil: {e}")
        return True

def fetch_remote_script(url):
    try:
        with urllib.request.urlopen(url, timeout=10) as r:
            return r.read().decode("utf-8")
    except Exception as e:
        print_error(f"Failed to fetch script from URL: {e}")
        return None

def write_script(content):
    INSTALL_DIR.mkdir(parents=True, exist_ok=True)
    try:
        with open(SCRIPT_PATH, "w") as f:
            f.write(content)
        os.chmod(SCRIPT_PATH, 0o755)
        print_success(f"Installed/Updated to: {SCRIPT_PATH}")
        return True
    except Exception as e:
        print_error(f"Failed to write script: {e}")
        return False

def check_path():
    if str(INSTALL_DIR) in os.environ.get("PATH",""):
        print_success(f"{INSTALL_DIR} is in PATH")
    else:
        print_warning(f"{INSTALL_DIR} is NOT in PATH")
        print(f"Add this to your shell config:\nexport PATH=\"$HOME/.local/bin:$PATH\"")

# =============================================================================
# MAIN INSTALL/UPDATE LOGIC
# =============================================================================
def main():
    update_mode = False
    if len(sys.argv) > 1 and sys.argv[1] in ["-u","--update"]:
        update_mode = True

    print(f"\n{Colors.CYAN}{Colors.BOLD}brlfetch Installer{' (Update Mode)' if update_mode else ''}{Colors.RESET}\n")

    if not check_python():
        sys.exit(1)
    install_dependencies()

    # Fetch remote script
    print_step(3, f"{'Updating' if update_mode else 'Installing'} brlfetch...")
    script_content = fetch_remote_script(REMOTE_URL)
    if not script_content:
        sys.exit(1)
    
    if not write_script(script_content):
        sys.exit(1)
    
    check_path()
    print_success("Done! You can run brlfetch now.\n")

if __name__ == "__main__":
    main()
