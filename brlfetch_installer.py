import os
import platform
import subprocess
import sys
import urllib.request

VERSION = "1.0.0"
VERSION_URL = "https://raw.githubusercontent.com/midplays09/brl-fetch/main/version.txt"
ASCII_ART = [
    r"   \\\\\\\\\\\\                       ",
    r"    \\\      \\\                      ",
    r"     \\\      \\\                     ",
    r"      \\\      \\\\\\\\\\\\\\\\\      ",
    r"       \\\                    \\\     ",
    r"        \\\                    \\\    ",
    r"         \\\        ______      \\\   ",
    r"          \\\                   ///   ",
    r"           \\\                 ///    ",
    r"            \\\               ///     ",
    r"             \\\////////////////       "
]

# ANSI colors
RESET = "\033[0m"
BOLD = "\033[1m"
RED = "\033[91m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
MAGENTA = "\033[95m"
CYAN = "\033[96m"
WHITE = "\033[97m"

try:
    import psutil
except ImportError:
    psutil = None

# -------------------- System Info -------------------- #
class SystemInfo:
    def __init__(self):
        self.info = {}
        self.collect()

    def collect(self):
        self.info["user"] = self.get_user()
        self.info["host"] = self.get_hostname()
        self.info["os"] = self.get_os()
        self.info["kernel"] = platform.release()
        self.info["uptime"] = self.get_uptime()
        self.info["shell"] = self.get_shell()
        self.info["de"] = self.get_desktop_environment()
        self.info["wm"] = self.get_window_manager()
        self.info["term"] = self.get_terminal()
        self.info["cpu"] = self.get_cpu()
        self.info["gpu"] = self.get_gpu()
        self.info["memory"] = self.get_memory()
        self.info["disk"] = self.get_disk()

    def get_user(self):
        return os.environ.get("USER") or os.environ.get("USERNAME") or "unknown"

    def get_hostname(self):
        return platform.node()

    def get_os(self):
        try:
            with open("/etc/os-release") as f:
                for line in f:
                    if line.startswith("PRETTY_NAME="):
                        return line.strip().split("=")[1].strip('"')
        except:
            pass
        return platform.system()

    def get_uptime(self):
        try:
            if psutil:
                seconds = int(platform.time() - psutil.boot_time())
            else:
                with open("/proc/uptime") as f:
                    seconds = int(float(f.readline().split()[0]))
            days, rem = divmod(seconds, 86400)
            hrs, rem = divmod(rem, 3600)
            mins, _ = divmod(rem, 60)
            parts = []
            if days: parts.append(f"{days}d")
            if hrs: parts.append(f"{hrs}h")
            parts.append(f"{mins}m")
            return " ".join(parts)
        except:
            return "unknown"

    def get_shell(self):
        return os.path.basename(os.environ.get("SHELL", "unknown"))

    def get_desktop_environment(self):
        de = os.environ.get("XDG_CURRENT_DESKTOP") or os.environ.get("DESKTOP_SESSION")
        return de or "unknown"

    def get_window_manager(self):
        # Detect common Linux WMs
        wm = os.environ.get("WAYLAND_DISPLAY")  # wayland hint
        if "HYPRLAND_INSTANCE_SIGNATURE" in os.environ:
            return "HyprLand"
        elif "SWAYSOCK" in os.environ:
            return "Sway"
        elif os.environ.get("i3") or os.environ.get("I3SOCK"):
            return "i3"
        else:
            # fallback using wmctrl
            try:
                out = subprocess.check_output(["wmctrl","-m"], universal_newlines=True)
                for line in out.splitlines():
                    if line.startswith("Name:"):
                        wm = line.split(":",1)[1].strip()
            except:
                wm = None
        return wm or "unknown"

    def get_terminal(self):
        return os.environ.get("TERM_PROGRAM") or os.environ.get("TERM") or "unknown"

    def get_cpu(self):
        cpu = platform.processor()
        if not cpu:
            try:
                with open("/proc/cpuinfo") as f:
                    for line in f:
                        if "model name" in line:
                            cpu = line.split(":",1)[1].strip()
                            break
            except:
                cpu = "unknown"
        if psutil:
            cores = psutil.cpu_count(logical=False)
            threads = psutil.cpu_count(logical=True)
            cpu += f" ({cores}C/{threads}T)"
        return cpu

    def get_gpu(self):
        if platform.system() != "Linux":
            return None
        try:
            out = subprocess.check_output(["lspci"], universal_newlines=True)
            for line in out.splitlines():
                if "VGA" in line or "3D" in line:
                    return line.split(":",2)[-1].strip()
        except:
            return None

    def get_memory(self):
        if not psutil: return "unknown"
        mem = psutil.virtual_memory()
        used = mem.used / (1024**3)
        total = mem.total / (1024**3)
        return f"{used:.1f}GiB / {total:.1f}GiB ({mem.percent}%)"

    def get_disk(self):
        if not psutil: return "unknown"
        try:
            disk = psutil.disk_usage("/")
            used = disk.used / (1024**3)
            total = disk.total / (1024**3)
            return f"{used:.1f}GiB / {total:.1f}GiB ({disk.percent}%)"
        except:
            return "unknown"

# -------------------- Display -------------------- #
def display(info):
    max_art_width = max(len(line) for line in ASCII_ART)
    padding = 4
    user_host = f"{BOLD}{info['user']}@{info['host']}{RESET}"
    sep = "-" * len(f"{info['user']}@{info['host']}")
    info_lines = [
        user_host,
        sep,
        f"{CYAN}OS:{RESET} {info['os']}",
        f"{CYAN}Kernel:{RESET} {info['kernel']}",
        f"{CYAN}Uptime:{RESET} {info['uptime']}",
        f"{CYAN}Shell:{RESET} {info['shell']}",
        f"{CYAN}DE:{RESET} {info['de']}",
        f"{CYAN}WM:{RESET} {info['wm']}",
        f"{CYAN}Terminal:{RESET} {info['term']}",
        f"{CYAN}CPU:{RESET} {info['cpu']}",
    ]
    if info["gpu"]:
        info_lines.append(f"{CYAN}GPU:{RESET} {info['gpu']}")
    info_lines += [
        f"{CYAN}Memory:{RESET} {info['memory']}",
        f"{CYAN}Disk:{RESET} {info['disk']}"
    ]

    max_lines = max(len(ASCII_ART), len(info_lines))
    for i in range(max_lines):
        art_line = ASCII_ART[i] if i < len(ASCII_ART) else " " * max_art_width
        info_text = info_lines[i] if i < len(info_lines) else ""
        print(f"{CYAN}{art_line}{RESET}{' '*padding}{info_text}")

# -------------------- Update Check -------------------- #
def check_update():
    try:
        with urllib.request.urlopen(VERSION_URL, timeout=5) as r:
            latest = r.read().decode().strip()
        if latest != VERSION:
            print(f"{YELLOW}New version available: {latest} (current: {VERSION}){RESET}")
            print(f"Run your installer with -u/--update to get the latest version.")
    except:
        pass

# -------------------- Main -------------------- #
def main():
    check_update()
    si = SystemInfo()
    display(si.info)

if __name__ == "__main__":
    main()
