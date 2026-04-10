import platform
import shutil
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

# TODO: Currently we only check applications installed natively. We can add support for flatpaks and snaps
def check_installed(application, os_name):
    dependencies_key = None
    if os_name == "ubuntu":
        dependencies_key = "dependenciesUbuntu"
    elif os_name == "linux":
        dependencies_key = "dependenciesLinux"
    elif os_name == "window":
        dependencies_key = "dependenciesWindows"

    dependencies = application.get(dependencies_key, []) if dependencies_key else []
    programs = []
    app_name = application.get("app")
    if app_name:
        programs.append(app_name)
    programs.extend(dependencies)

    results = {}
    for program in programs:
        if program in results:
            continue
        results[program] = shutil.which(program) is not None
    return results
