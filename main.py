from core.checker import detect_os, check_installed
from core.dependency import install_dependency
from sys import exit

APPLICATION = {
    "app" : "esim",
    # More dependencies can be configured here
    "dependenciesUbuntu" :  ["ngspice", "kicad", "xterm"],
    "dependenciesLinux" :  ["ngspice", "kicad"],
    "dependenciesWindows" :  ["ngspice", "kicad"],
    # Pip packages needed independednt of OS
    "dependenciesPip" : ["matplotlib", "PyQt5"]
}

CONSTANTS = {
    "os" : detect_os()
}

if __name__ == "__main__":
    print("Welcome to eSim Installer")
    
    # If we cannot detects os we panic
    if CONSTANTS["os"] == None :
        print("Error: Cannot detect OS")
        exit()

    # Check if app and dependencies are installed
    install_status = check_installed(APPLICATION, CONSTANTS["os"])

    print(install_status)

    # Install missing dependency
    # is_install = install_dependency("kicad", CONSTANTS["os"], "system")
    # print(is_install)