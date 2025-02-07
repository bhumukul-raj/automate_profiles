import os
import shutil
import json
from datetime import datetime

# Configuration
MERCYHACKS_KEY = "1fc0a7b0-c0bd-4d4a-a841-a95841d8e94f"

def check_cursor_installed():
    """Check if Cursor IDE is installed by looking for configuration files."""
    config_path = os.path.expanduser("~/.config/Cursor/User/globalStorage/storage.json")
    updater_path = os.path.expanduser("~/.config/cursor-updater")
    
    return os.path.exists(config_path) or os.path.exists(updater_path)

def delete_cursor_config_files():
    """Delete all Cursor-related configuration files."""
    directories = [
        os.path.expanduser("~/.cursor"),
        os.path.expanduser("~/.config/Cursor"),
        os.path.expanduser("~/.config/cursor-updater")
    ]

    for directory in directories:
        if os.path.exists(directory):
            print(f"Deleting directory: {directory}")
            shutil.rmtree(directory)
        else:
            print(f"Directory does not exist: {directory}")

def modify_storage_json():
    """Modify the storage.json file with the new key."""
    storage_path = os.path.expanduser("~/.config/Cursor/User/globalStorage/storage.json")

    if not os.path.exists(storage_path):
        print(f"Error: storage.json not found at {storage_path}")
        exit(1)

    try:
        with open(storage_path, "r") as file:
            data = json.load(file)
            
        # Create backup before modification
        backup_path = f"{storage_path}.{datetime.now().strftime('%Y%m%d_%H%M%S')}.bak"
        shutil.copyfile(storage_path, backup_path)
        print(f"Created backup at: {backup_path}")
        
        # Update with fields from instructions
        data.update({
            "telemetry.machineId": MERCYHACKS_KEY,
            "telemetry.macMachineId": MERCYHACKS_KEY,
            "telemetry.devDeviceId": MERCYHACKS_KEY,
            "telemetry.sqmId": MERCYHACKS_KEY,
            "lastModified": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S.000Z"),
            "version": "1.0.1"
        })
        
        with open(storage_path, "w") as file:
            json.dump(data, file, indent=4)
            
        print("Successfully updated storage.json")
            
    except json.JSONDecodeError:
        print("Error: storage.json is corrupted or invalid")
        exit(1)
    except Exception as e:
        print(f"Error modifying storage.json: {str(e)}")
        exit(1)

def main():
    print("Checking if Cursor IDE is installed...")
    if not check_cursor_installed():
        print("Cursor IDE is not installed.")
        print("Please install Cursor v0.44.11 first.")
        exit(0)

    print("\nCursor IDE is installed. Choose an option:")
    print("1. Remove all configuration files and uninstall Cursor")
    print("2. Modify configuration settings (update storage.json)")
    choice = input("\nEnter your choice (1 or 2): ").strip()

    if choice == "1":
        confirm = input("\nAre you sure you want to remove all Cursor configuration files? (yes/no): ").strip().lower()
        if confirm == "yes":
            print("\nRemoving all Cursor configuration files...")
            delete_cursor_config_files()
            print("\nAll Cursor configuration files have been removed.")
            print("You can now reinstall Cursor v0.44.11")
        else:
            print("\nOperation canceled.")
            exit(0)
    elif choice == "2":
        print("\nModifying storage.json with the new key...")
        modify_storage_json()
        print("\nConfiguration updated successfully.")
        print("Please restart Cursor IDE for changes to take effect.")
    else:
        print("\nInvalid choice.")
        exit(1)

if __name__ == "__main__":
    main()