import os
import shutil
import subprocess
import tempfile
import urllib.request


def _run_command(command, cwd=None):
    result = subprocess.run(
        command,
        cwd=cwd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        check=False,
    )
    return {
        "command": command,
        "returncode": result.returncode,
        "stdout": result.stdout,
        "stderr": result.stderr,
    }


def _download_file(url):
    file_name = os.path.basename(urllib.request.urlparse(url).path)
    if not file_name:
        file_name = "esim-installer.exe"
    target_path = os.path.join(tempfile.gettempdir(), file_name)

    try:
        with urllib.request.urlopen(url) as response, open(target_path, "wb") as output:
            shutil.copyfileobj(response, output)
    except Exception as exc:
        return {
            "success": False,
            "path": None,
            "error": str(exc),
        }

    return {
        "success": True,
        "path": target_path,
        "error": None,
    }


def _start_installer(installer_path):
    try:
        process = subprocess.Popen([installer_path], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    except Exception as exc:
        return {
            "returncode": 1,
            "stdout": "",
            "stderr": str(exc),
            "started": False,
        }

    return {
        "returncode": 0,
        "stdout": "",
        "stderr": "",
        "started": True,
        "pid": process.pid,
    }


def install_esim(
    os_name,
    esim_dir=None,
    install_kicad=False,
    build_from_source=False,
    windows_installer_url=None,
):
    results = []

    if os_name == "ubuntu":
        base_dir = esim_dir or os.getcwd()
        script_path = os.path.join(base_dir, "install-eSim.sh")
        if not os.path.isfile(script_path):
            return {
                "success": False,
                "error": f"install-eSim.sh not found in {base_dir}",
                "results": results,
            }

        results.append(_run_command(["chmod", "+x", script_path]))
        results.append(_run_command([script_path, "--install"], cwd=base_dir))
        success = all(step["returncode"] == 0 for step in results)
        return {"success": success, "error": None if success else "Install failed", "results": results}

    if os_name == "linux":
        if not shutil.which("flatpak"):
            return {
                "success": False,
                "error": "flatpak not found; install it using your distro package manager",
                "results": results,
            }

        results.append(
            _run_command(
                [
                    "flatpak",
                    "remote-add",
                    "--if-not-exists",
                    "flathub",
                    "https://dl.flathub.org/repo/flathub.flatpakrepo",
                ]
            )
        )

        if build_from_source:
            if not esim_dir:
                return {
                    "success": False,
                    "error": "esim_dir is required to build from source",
                    "results": results,
                }
            results.append(
                _run_command(
                    [
                        "flatpak-builder",
                        "build",
                        "flatpak/org.fossee.eSim.yml",
                        "--install",
                        "--user",
                    ],
                    cwd=esim_dir,
                )
            )
        else:
            results.append(_run_command(["flatpak", "install", "-y", "flathub", "org.fossee.eSim"]))

        if install_kicad:
            results.append(_run_command(["flatpak", "install", "-y", "flathub", "org.kicad.KiCad"]))

        success = all(step["returncode"] == 0 for step in results)
        return {"success": success, "error": None if success else "Install failed", "results": results}

    if os_name == "window":
        if not windows_installer_url:
            return {
                "success": False,
                "error": "windows_installer_url is required to download installer",
                "results": results,
            }

        download = _download_file(windows_installer_url)
        if not download["success"]:
            return {
                "success": False,
                "error": download["error"],
                "results": results,
            }

        results.append(
            {
                "command": ["download", windows_installer_url],
                "returncode": 0,
                "stdout": download["path"],
                "stderr": "",
            }
        )
        results.append(_start_installer(download["path"]))

        success = all(step.get("returncode", 1) == 0 for step in results)
        return {
            "success": success,
            "error": None if success else "Installer launch failed",
            "results": results,
        }

    return {"success": False, "error": "Unknown OS", "results": results}
