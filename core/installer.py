import os
import shutil
import subprocess
import tempfile
import urllib.request
import ctypes

WINDOWS_INSTALLER_URL = "https://static.fossee.in/esim/installation-files/eSim-2.5_installer.exe"
UBUNTU_SOURCE_ZIP_URL = "https://static.fossee.in/esim/installation-files/eSim-2.5.zip"


def _run_command(command, cwd=None, stream_output=False):
    if stream_output:
        result = subprocess.run(
            command,
            cwd=cwd,
            check=False,
        )
    else:
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
        "stdout": result.stdout or "",
        "stderr": result.stderr or "",
    }


def _download_file(url):
    file_name = os.path.basename(urllib.request.urlparse(url).path)
    if not file_name:
        file_name = "esim-installer.exe"
    target_path = os.path.join(tempfile.gettempdir(), file_name)

    try:
        print(f"Downloading {url}")
        print(f"Saving to {target_path}")
        with urllib.request.urlopen(url) as response, open(target_path, "wb") as output:
            content_length = response.getheader("Content-Length")
            total_bytes = None
            if content_length and content_length.isdigit():
                total_bytes = int(content_length)
            downloaded = 0
            last_percent = -1
            while True:
                chunk = response.read(1024 * 1024)
                if not chunk:
                    break
                output.write(chunk)
                downloaded += len(chunk)
                if total_bytes:
                    percent = int(downloaded * 100 / total_bytes)
                    if percent >= last_percent + 5 or percent == 100:
                        print(f"Download progress: {percent}%")
                        last_percent = percent
            if total_bytes:
                print("Download complete")
            else:
                print(f"Download complete: {downloaded} bytes")
    except Exception as exc:
        print(f"Download error: {exc}")
        return {
            "success": False,
            "path": None,
            "error": str(exc),
        }

    print("Download finished successfully")
    return {
        "success": True,
        "path": target_path,
        "error": None,
    }


def _extract_zip(zip_path, target_dir):
    print(f"Extracting {zip_path}")
    result = _run_command(["unzip", zip_path, "-d", target_dir])
    if result["returncode"] != 0:
        print(f"Extraction error: {result['stderr'].strip() or 'unzip failed'}")
        raise RuntimeError(result["stderr"].strip() or "unzip failed")
    print("Extraction complete")


def _detect_single_root_dir(target_dir):
    entries = [
        name
        for name in os.listdir(target_dir)
        if not name.startswith(".")
    ]
    if len(entries) == 1:
        candidate = os.path.join(target_dir, entries[0])
        if os.path.isdir(candidate):
            return candidate
    return target_dir


def _start_installer(installer_path):
    if os.name == "nt":
        try:
            result = ctypes.windll.shell32.ShellExecuteW(None, "runas", installer_path, None, None, 1)
        except Exception as exc:
            return {
                "returncode": 1,
                "stdout": "",
                "stderr": str(exc),
                "started": False,
            }

        if result <= 32:
            return {
                "returncode": 1,
                "stdout": "",
                "stderr": f"ShellExecute failed with code {result}",
                "started": False,
            }

        return {
            "returncode": 0,
            "stdout": "",
            "stderr": "",
            "started": True,
            "pid": None,
        }

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
    windows_installer_url=WINDOWS_INSTALLER_URL,
    ubuntu_source_url=UBUNTU_SOURCE_ZIP_URL,
):
    results = []

    if os_name == "ubuntu":
        if esim_dir:
            base_dir = esim_dir
        else:
            download = _download_file(ubuntu_source_url)
            if not download["success"]:
                return {
                    "success": False,
                    "error": download["error"],
                    "results": results,
                }
            extract_dir = tempfile.mkdtemp(prefix="esim-src-")
            try:
                _extract_zip(download["path"], extract_dir)
            except Exception as exc:
                print(f"Extraction failed: {exc}")
                return {
                    "success": False,
                    "error": str(exc),
                    "results": results,
                }
            base_dir = _detect_single_root_dir(extract_dir)

        script_path = os.path.join(base_dir, "install-eSim.sh")
        if not os.path.isfile(script_path):
            return {
                "success": False,
                "error": f"install-eSim.sh not found in {base_dir}",
                "results": results,
            }

        results.append(_run_command(["chmod", "+x", script_path]))
        print("Starting eSim install script")
        results.append(_run_command([script_path, "--install"], cwd=base_dir, stream_output=True))
        success = all(step["returncode"] == 0 for step in results)
        return {"success": success, "error": None if success else "Install failed", "results": results}

    if os_name == "linux":
        if not shutil.which("flatpak"):
            return {
                "success": False,
                "error": "flatpak not found; install it using your distro package manager",
                "results": results,
            }

        print("Configuring flathub remote")
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
            print("Building eSim from source with flatpak-builder")
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
            print("Installing eSim from flathub")
            results.append(_run_command(["flatpak", "install", "-y", "flathub", "org.fossee.eSim"]))

        if install_kicad:
            print("Installing KiCad from flathub")
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
        print("Starting Windows installer")
        results.append(_start_installer(download["path"]))

        success = all(step.get("returncode", 1) == 0 for step in results)
        return {
            "success": success,
            "error": None if success else "Installer launch failed",
            "results": results,
        }

    return {"success": False, "error": "Unknown OS", "results": results}
