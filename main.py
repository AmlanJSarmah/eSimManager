from core.checker import detect_os
from sys import exit

APPLICATION = {
    "app" : "eSim",
    "dependenciesUbuntu" :  ["ngspice", "kicad", "python3"]
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


    print(CONSTANTS["os"])
