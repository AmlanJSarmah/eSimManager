import platform
from pathlib import Path


def _is_ubuntu():
    os_release = Path("/etc/os-release")
    if not os_release.is_file():
        return False

    content = os_release.read_text(encoding="utf-8", errors="ignore").splitlines()
    for line in content:
        if line.startswith("ID="):
            return line.split("=", 1)[1].strip().strip('"') == "ubuntu"
    return False


def detect_os():
    system = platform.system().lower()
    if system.startswith("windows"):
        return "window"
    if system.startswith("linux"):
        return "ubuntu" if _is_ubuntu() else "linux"
    return None
