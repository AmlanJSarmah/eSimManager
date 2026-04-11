import os
import threading
import tkinter as tk

import customtkinter as ctk

from core.checker import check_installed, detect_os
from core.dependency import install_dependency
from core.installer import install_esim


APPLICATION = {
    "app": "esim",
    "dependenciesUbuntu": ["ngspice", "kicad", "xterm"],
    "dependenciesLinux": ["ngspice", "kicad"],
    "dependenciesWindows": ["ngspice", "kicad"],
    "dependenciesPip": ["matplotlib", "PyQt5"],
}


class InstallerApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("eSim Installer")
        self.geometry("780x560")
        self.minsize(640, 480)
        self._set_app_icon()

        self.os_name = detect_os()
        self._busy = False
        self._status = {}

        ctk.set_appearance_mode("System")
        ctk.set_default_color_theme("blue")

        self._build_ui()
        self.refresh_status()

    def _set_app_icon(self):
        logo_path = os.path.abspath(
            os.path.join(os.path.dirname(__file__), "..", "assets", "esim_logo.png")
        )
        if not os.path.isfile(logo_path):
            return
        try:
            icon = tk.PhotoImage(file=logo_path)
        except tk.TclError:
            return
        self.iconphoto(False, icon)
        self._icon_ref = icon

    def _build_ui(self):
        header = ctk.CTkLabel(self, text="eSim Installer", font=ctk.CTkFont(size=22, weight="bold"))
        header.pack(padx=20, pady=(20, 10), anchor="w")

        status_frame = ctk.CTkFrame(self)
        status_frame.pack(padx=20, pady=(0, 12), fill="x")
        status_label = ctk.CTkLabel(status_frame, text="Status", font=ctk.CTkFont(size=16, weight="bold"))
        status_label.pack(padx=16, pady=(12, 6), anchor="w")

        self.status_box = ctk.CTkTextbox(status_frame, height=160)
        self.status_box.pack(padx=16, pady=(0, 12), fill="x")
        self.status_box.configure(state="disabled")

        actions_frame = ctk.CTkFrame(self)
        actions_frame.pack(padx=20, pady=(0, 12), fill="x")
        actions_label = ctk.CTkLabel(actions_frame, text="Actions", font=ctk.CTkFont(size=16, weight="bold"))
        actions_label.pack(padx=16, pady=(12, 6), anchor="w")

        buttons_frame = ctk.CTkFrame(actions_frame, fg_color="transparent")
        buttons_frame.pack(padx=16, pady=(0, 12), fill="x")
        buttons_frame.grid_columnconfigure(0, weight=1)
        buttons_frame.grid_columnconfigure(1, weight=1)
        buttons_frame.grid_columnconfigure(2, weight=1)

        self.download_button = ctk.CTkButton(
            buttons_frame,
            text="Download eSim",
            command=self._on_download_esim,
        )
        self.download_button.grid(row=0, column=0, padx=6, pady=6, sticky="ew")

        self.install_deps_button = ctk.CTkButton(
            buttons_frame,
            text="Install Missing Dependencies",
            command=self._on_install_dependencies,
        )
        self.install_deps_button.grid(row=0, column=1, padx=6, pady=6, sticky="ew")

        self.refresh_button = ctk.CTkButton(
            buttons_frame,
            text="Refresh Status",
            command=self.refresh_status,
        )
        self.refresh_button.grid(row=0, column=2, padx=6, pady=6, sticky="ew")

        log_frame = ctk.CTkFrame(self)
        log_frame.pack(padx=20, pady=(0, 20), fill="both", expand=True)
        log_label = ctk.CTkLabel(log_frame, text="Activity", font=ctk.CTkFont(size=16, weight="bold"))
        log_label.pack(padx=16, pady=(12, 6), anchor="w")

        self.log_box = ctk.CTkTextbox(log_frame)
        self.log_box.pack(padx=16, pady=(0, 12), fill="both", expand=True)
        self.log_box.configure(state="disabled")

    def _set_status_text(self, text):
        self.status_box.configure(state="normal")
        self.status_box.delete("1.0", "end")
        self.status_box.insert("end", text)
        self.status_box.configure(state="disabled")

    def _append_log(self, message):
        self.log_box.configure(state="normal")
        self.log_box.insert("end", f"{message}\n")
        self.log_box.see("end")
        self.log_box.configure(state="disabled")

    def _log(self, message):
        self.after(0, self._append_log, message)

    def _set_busy(self, busy):
        self._busy = busy
        state = "disabled" if busy else "normal"
        self.download_button.configure(state=state)
        self.install_deps_button.configure(state=state)
        self.refresh_button.configure(state=state)

    def _run_task(self, target):
        if self._busy:
            return

        self._set_busy(True)

        def wrapper():
            try:
                target()
            finally:
                self.after(0, self._set_busy, False)
                self.after(0, self.refresh_status)

        thread = threading.Thread(target=wrapper, daemon=True)
        thread.start()

    def _show_terminal_prompt_modal(self, title, message):
        dialog = ctk.CTkToplevel(self)
        dialog.title(title)
        dialog.geometry("420x180")
        dialog.resizable(False, False)
        dialog.transient(self)
        dialog.update_idletasks()
        dialog.deiconify()
        dialog.wait_visibility()
        dialog.grab_set()

        frame = ctk.CTkFrame(dialog)
        frame.pack(fill="both", expand=True, padx=16, pady=16)

        label = ctk.CTkLabel(frame, text=message, wraplength=360, justify="left")
        label.pack(pady=(10, 20), anchor="w")

        button = ctk.CTkButton(frame, text="OK", command=dialog.destroy)
        button.pack(anchor="e")

        dialog.wait_window()


    def _get_os_dependencies(self):
        if self.os_name == "ubuntu":
            return APPLICATION.get("dependenciesUbuntu", [])
        if self.os_name == "linux":
            return APPLICATION.get("dependenciesLinux", [])
        if self.os_name == "window":
            return APPLICATION.get("dependenciesWindows", [])
        return []

    def _missing_dependencies(self):
        system_deps = self._get_os_dependencies()
        pip_deps = APPLICATION.get("dependenciesPip", [])
        missing_system = [name for name in system_deps if not self._status.get(name, False)]
        missing_pip = [name for name in pip_deps if not self._status.get(name, False)]
        return missing_system, missing_pip

    def _format_status_lines(self):
        lines = []
        os_label = self.os_name or "unknown"
        lines.append(f"OS: {os_label}")
        if not self.os_name:
            lines.append("Unsupported OS. Actions are disabled.")
            return lines

        app_name = APPLICATION.get("app", "esim")
        app_status = "OK" if self._status.get(app_name, False) else "Missing"
        lines.append("")
        lines.append("Application")
        lines.append(f"- {app_name}: {app_status}")

        system_deps = self._get_os_dependencies()
        if system_deps:
            lines.append("")
            lines.append("System dependencies")
            for name in system_deps:
                status = "OK" if self._status.get(name, False) else "Missing"
                lines.append(f"- {name}: {status}")

        pip_deps = APPLICATION.get("dependenciesPip", [])
        if pip_deps:
            lines.append("")
            lines.append("Python dependencies")
            for name in pip_deps:
                status = "OK" if self._status.get(name, False) else "Missing"
                lines.append(f"- {name}: {status}")

        return lines

    def _update_actions(self):
        if not self.os_name:
            self.download_button.grid_remove()
            self.install_deps_button.grid_remove()
            self.refresh_button.configure(state="normal")
            return

        app_name = APPLICATION.get("app", "esim")
        esim_installed = self._status.get(app_name, False)
        missing_system, missing_pip = self._missing_dependencies()
        missing_deps = bool(missing_system or missing_pip)

        if esim_installed:
            self.download_button.grid_remove()
        else:
            self.download_button.grid()

        if missing_deps:
            self.install_deps_button.grid()
        else:
            self.install_deps_button.grid_remove()

    def refresh_status(self):
        if not self.os_name:
            self._status = {}
            self._set_status_text("\n".join(self._format_status_lines()))
            self._update_actions()
            return

        self._status = check_installed(APPLICATION, self.os_name)
        self._set_status_text("\n".join(self._format_status_lines()))
        self._update_actions()

    def _on_download_esim(self):
        if self.os_name != "ubuntu":
            def task():
                self._log("Starting eSim installation...")
                result = install_esim(self.os_name)
                if result.get("success"):
                    self._log("eSim installation completed.")
                else:
                    self._log(f"eSim installation failed: {result.get('error', 'unknown error')}")

                for step in result.get("results", []):
                    returncode = step.get("returncode")
                    if returncode not in (0, None):
                        stderr = (step.get("stderr") or "").strip()
                        if stderr:
                            self._log(f"Error: {stderr}")

            self._run_task(task)
            return

        self._show_terminal_prompt_modal(
            "Ubuntu Installer",
            "The installer will prompt in the terminal for inputs (y/n, proxy, sudo)."
            " Please switch to the terminal to respond.",
        )

        def task():
            self._log("Starting eSim installation...")
            result = install_esim(self.os_name)
            if result.get("success"):
                self._log("eSim installation completed.")
            else:
                self._log(f"eSim installation failed: {result.get('error', 'unknown error')}")

            for step in result.get("results", []):
                returncode = step.get("returncode")
                if returncode not in (0, None):
                    stderr = (step.get("stderr") or "").strip()
                    if stderr:
                        self._log(f"Error: {stderr}")

        self._run_task(task)

    def _on_install_dependencies(self):
        def task():
            missing_system, missing_pip = self._missing_dependencies()
            if not missing_system and not missing_pip:
                self._log("No missing dependencies detected.")
                return

            for name in missing_system:
                self._log(f"Installing system dependency: {name}")
                result = install_dependency(name, self.os_name, "system")
                if result.get("installed"):
                    self._log(f"Installed: {name}")
                else:
                    self._log(f"Failed: {name} ({result.get('error', 'unknown error')})")

            for name in missing_pip:
                self._log(f"Installing Python dependency: {name}")
                result = install_dependency(name, self.os_name, "pip")
                if result.get("installed"):
                    self._log(f"Installed: {name}")
                else:
                    self._log(f"Failed: {name} ({result.get('error', 'unknown error')})")

        self._run_task(task)


def run():
    app = InstallerApp()
    app.mainloop()


if __name__ == "__main__":
    run()
