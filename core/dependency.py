import os
import re
import shutil
import subprocess
import sys


def _run_command(command, use_sudo=False):
    if use_sudo and os.name != "nt" and shutil.which("sudo"):
        command = ["sudo"] + command
    result = subprocess.run(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        check=False,
    )
    return result


def _pick_system_python():
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
                [interpreter, "-m", "pip", "--version"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                check=False,
            )
        except FileNotFoundError:
            continue

        if result.returncode == 0:
            return interpreter
    return None


def _install_pip(package):
    interpreter = _pick_system_python()
    if not interpreter:
        return {
            "name": package,
            "installed": False,
            "error": "No system Python interpreter with pip found",
        }

    result = _run_command([interpreter, "-m", "pip", "install", package])
    return {
        "name": package,
        "installed": result.returncode == 0,
        "error": None if result.returncode == 0 else result.stderr.strip(),
    }


def _pip_to_ubuntu_package(package):
    normalized = package.strip().lower().replace("_", "-")
    return f"python3-{normalized}"


def _install_apt(package):
    if not shutil.which("apt-get"):
        return {
            "name": package,
            "installed": False,
            "error": "apt-get not found",
        }

    update_result = _run_command(["apt-get", "update"], use_sudo=True)
    if update_result.returncode != 0:
        return {
            "name": package,
            "installed": False,
            "error": update_result.stderr.strip(),
        }

    install_result = _run_command(["apt-get", "install", "-y", package], use_sudo=True)
    return {
        "name": package,
        "installed": install_result.returncode == 0,
        "error": None if install_result.returncode == 0 else install_result.stderr.strip(),
    }


def _install_flatpak(app_id):
    if not shutil.which("flatpak"):
        return {
            "name": app_id,
            "installed": False,
            "error": "flatpak not found",
        }

    result = _run_command(["flatpak", "install", "-y", "flathub", app_id])
    return {
        "name": app_id,
        "installed": result.returncode == 0,
        "error": None if result.returncode == 0 else result.stderr.strip(),
    }


def _resolve_winget_id(name):
    if "." in name:
        return name
    if not shutil.which("winget"):
        return None

    result = _run_command(["winget", "search", "--name", name, "--exact"])
    if result.returncode != 0:
        return None

    lines = result.stdout.splitlines()
    for line in lines:
        if not line.strip():
            continue
        if line.startswith("-"):
            continue
        if line.lower().startswith("name"):
            continue
        parts = re.split(r"\s{2,}", line.strip())
        if len(parts) >= 2:
            return parts[1]
    return None


def _install_winget(name):
    if not shutil.which("winget"):
        return {
            "name": name,
            "installed": False,
            "error": "winget not found",
        }

    app_id = _resolve_winget_id(name)
    if app_id:
        result = _run_command(["winget", "install", "--id", app_id, "-e"])
    else:
        result = _run_command(["winget", "install", name])

    return {
        "name": name,
        "installed": result.returncode == 0,
        "error": None if result.returncode == 0 else result.stderr.strip(),
    }


def install_dependency(name, os_name, dep_type):
    if dep_type == "pip":
        if os_name == "ubuntu":
            return _install_apt(_pip_to_ubuntu_package(name))
        return _install_pip(name)

    if dep_type != "system":
        return {
            "name": name,
            "installed": False,
            "error": "Unknown dependency type",
        }

    if os_name == "ubuntu":
        return _install_apt(name)
    if os_name == "linux":
        return _install_flatpak(name)
    if os_name == "window":
        return _install_winget(name)

    return {
        "name": name,
        "installed": False,
        "error": "Unknown OS",
    }
