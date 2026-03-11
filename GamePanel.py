import os
import sys
import time
import random
from pathlib import Path

documents = Path.home() / "Documents"
gamepanel_path = documents / "GamePanel"
current_dir = None

# Apps Struktur
apps_structure = {
    "wings": ["wings-core", "wings-rco", "wings-servers", "wings-utilities"],
    "ptero-utils": ["utils", "plugins"],
    "servs": ["saves", "custom"],
    "core": ["servers", "host", "apps", "addons", "guis", "terminal", 
             "stable", "versions", "backups", "revokes", "python", 
             "connections", "databases", "saves"]
}

# Extra Struktur für core
core_extra = {
    "servers": ["saved", "unsaved", "unverified", "verified"],
    "stable": ["info.txt"]
}

# Fake files für Unterordner
dummy_files = ["file1.dll", "file2.dll", "file3.bin", "config.cfg", "readme.txt"]

# Header
os.system("cls")
print("GamePanel v0.0.1\n")

def create_gamepanel():
    global current_dir
    if not gamepanel_path.exists():
        gamepanel_path.mkdir()
        print(f"Created folder: {gamepanel_path}")
    else:
        print("GamePanel folder already exists.")
    current_dir = gamepanel_path

def change_dir(target):
    global current_dir
    if target != "GamePanel":
        print("You can only go to 'GamePanel'.")
        return
    if not gamepanel_path.exists():
        print("GamePanel folder does not exist. Run 'createdir' first.")
        return
    current_dir = gamepanel_path
    print(f"Current directory: {current_dir}")

def create_file(name, ext):
    if current_dir != gamepanel_path:
        print("You must be in GamePanel folder to create files.")
        return
    if ext not in [".py", ".txt"]:
        print("Unsupported file format. Use .py or .txt")
        return
    file_path = current_dir / f"{name}{ext}"
    if file_path.exists():
        print("File already exists.")
        return
    with open(file_path, "w") as f:
        if ext == ".txt":
            f.write("")
        elif ext == ".py":
            f.write("# Created by GamePanel\n")
    print(f"Created file: {file_path}")

def install_app(app_name):
    if current_dir != gamepanel_path:
        print("You must be in GamePanel folder to install apps.")
        return
    if app_name not in apps_structure:
        print(f"Unknown app: {app_name}")
        return
    app_folder = current_dir / app_name
    if app_folder.exists():
        print(f"App '{app_name}' already installed.")
        return
    print(f"Installing {app_name}...")
    time.sleep(1)
    app_folder.mkdir()
    for sub in apps_structure[app_name]:
        sub_path = app_folder / sub
        sub_path.mkdir(exist_ok=True)
        # Dummy Dateien erzeugen in Unterordnern, außer Extra/Stable
        if app_name == "core" and sub in core_extra:
            continue
        for _ in range(random.randint(2,5)):
            dummy_file = random.choice(dummy_files)
            (sub_path / dummy_file).touch()
            print(f"Creating {sub_path / dummy_file}")
            time.sleep(0.1)
    # Extra Struktur für core
    if app_name == "core":
        servers_path = app_folder / "servers"
        for sub in core_extra["servers"]:
            (servers_path / sub).mkdir(exist_ok=True)
        stable_path = app_folder / "stable"
        info_file = stable_path / "info.txt"
        with open(info_file, "w") as f:
            f.write("==GamePanel Stable==\n")
    print(f"Installed app: {app_name}")

def uninstall_app(app_name):
    if current_dir != gamepanel_path:
        print("You must be in GamePanel folder to uninstall apps.")
        return
    app_folder = current_dir / app_name
    if not app_folder.exists():
        print(f"App '{app_name}' is not installed.")
        return
    print(f"Uninstalling {app_name}...")
    time.sleep(1)
    # Lösche alles im App-Ordner
    for root, dirs, files in os.walk(app_folder, topdown=False):
        for file in files:
            file_path = Path(root) / file
            file_path.unlink()
            print(f"Deleting {file_path}")
            time.sleep(0.05)
        for d in dirs:
            dir_path = Path(root) / d
            dir_path.rmdir()
            print(f"Deleting folder {dir_path}")
            time.sleep(0.05)
    app_folder.rmdir()
    print(f"Uninstalled app: {app_name}")

while True:
    command = input("> ").strip()
    if not command:
        continue
    parts = command.split()
    cmd = parts[0].lower()

    if cmd in ("exit", "quit"):
        print("Exiting GamePanel...")
        sys.exit()
    elif cmd == "createdir":
        create_gamepanel()
    elif cmd == "gotodir":
        if len(parts) != 2:
            print("Usage: gotodir <directory>")
            continue
        change_dir(parts[1])
    elif cmd == "createfile":
        if len(parts) != 3:
            print("Usage: createfile <name> <format>")
            continue
        create_file(parts[1], parts[2])
    elif cmd == "install":
        if len(parts) != 2:
            print("Usage: install <app>")
            continue
        install_app(parts[1].lower())
    elif cmd == "uninstall":
        if len(parts) != 2:
            print("Usage: uninstall <app>")
            continue
        uninstall_app(parts[1].lower())
    else:
        print("Unknown command.")
