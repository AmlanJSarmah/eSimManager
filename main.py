from core.checker import detect_os, check_installed
from sys import exit

APPLICATION = {
    "app" : "esim",
    # More dependencies can be configured here
    "dependenciesUbuntu" :  ["ngspice", "kicad", "python3"],
    "dependenciesLinux" :  ["ngspice", "kicad", "python3"],
    "dependenciesWindows" :  ["ngspice", "kicad", "python"]
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
