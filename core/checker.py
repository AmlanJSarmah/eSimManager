import os
import platform
import shutil
import subprocess
import sys
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


def _pip_installed(package):
    base_prefix = getattr(sys, "base_prefix", sys.prefix)
    candidates = []
    if os.name == "nt":
        candidates.extend(
            [
                os.path.join(base_prefix, "python.exe"),
                os.path.join(base_prefix, "Scripts", "python.exe"),
                "py",
                "python",
                "python3",
            ]
        )
    else:
        candidates.extend(
            [
                os.path.join(base_prefix, "bin", "python3"),
                os.path.join(base_prefix, "bin", "python"),
                "python3",
                "python",
            ]
        )

    checked = set()
    for interpreter in candidates:
        if interpreter in checked:
            continue
        checked.add(interpreter)

        if os.path.isabs(interpreter) and not os.path.exists(interpreter):
            continue

        try:
            result = subprocess.run(
                [interpreter, "-m", "pip", "show", package],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                check=False,
            )
        except FileNotFoundError:
            continue

        if result.returncode == 0:
            return True
    return False


def _windows_app_installed(name):
    if os.name != "nt":
        return False

    try:
        import winreg
    except ImportError:
        return False

    needle = name.lower()
    uninstall_paths = [
        r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall",
        r"SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall",
    ]

    for root in (winreg.HKEY_LOCAL_MACHINE, winreg.HKEY_CURRENT_USER):
        for base in uninstall_paths:
            try:
                key = winreg.OpenKey(root, base)
            except FileNotFoundError:
                continue

            try:
                index = 0
                while True:
                    subkey_name = winreg.EnumKey(key, index)
                    index += 1
                    try:
                        subkey = winreg.OpenKey(key, subkey_name)
                    except FileNotFoundError:
                        continue

                    try:
                        display_name, _ = winreg.QueryValueEx(subkey, "DisplayName")
                    except FileNotFoundError:
                        display_name = ""
                    finally:
                        winreg.CloseKey(subkey)

                    if display_name and needle in display_name.lower():
                        winreg.CloseKey(key)
                        return True
            except OSError:
                pass
            finally:
                winreg.CloseKey(key)

    return False

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
    pip_dependencies = application.get("dependenciesPip", [])

    results = {}
    for program in programs:
        if program in results:
            continue
        installed = shutil.which(program) is not None
        if not installed and os_name == "window":
            installed = _windows_app_installed(program)
        results[program] = installed

    for package in pip_dependencies:
        if package in results:
            results[package] = results[package] or _pip_installed(package)
            continue
        results[package] = _pip_installed(package)
    return results
