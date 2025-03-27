import os
import shutil
import json
import uuid
import sys
from datetime import datetime

# Display security warning
def show_security_warning():
    """Display warning message and get confirmation from user."""
    print("\n⚠️  SECURITY AND STABILITY WARNING ⚠️")
    print("This script will make changes to your Cursor IDE configuration:")
    print("1. It can delete configuration files, which may remove your preferences")
    print("2. It can modify identification settings which may affect licensing")
    print("\nThese changes may have the following impacts:")
    print("- Loss of preferences, settings, and history")
    print("- Potential issues with future Cursor updates")
    print("- Cursor might need to be reinstalled or reconfigured")
    
    confirmation = input("\nDo you understand these risks and wish to continue? (yes/no): ").strip().lower()
    if confirmation != "yes":
        print("\nOperation cancelled by user")
        sys.exit(0)

def check_cursor_installed():
    """Check if Cursor IDE is installed by looking for configuration files."""
    config_path = os.path.expanduser("~/.config/Cursor/User/globalStorage/storage.json")
    updater_path = os.path.expanduser("~/.config/cursor-updater")
    
    return os.path.exists(config_path) or os.path.exists(updater_path)

def create_directory_backup(directory):
    """Create a backup of a directory before deletion."""
    if not os.path.exists(directory):
        return False
        
    # Create backups directory if it doesn't exist
    backup_root = os.path.expanduser("~/cursor_config_backups")
    os.makedirs(backup_root, exist_ok=True)
    
    # Create timestamped backup directory
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_dir = f"{backup_root}/{os.path.basename(directory)}_{timestamp}"
    
    try:
        print(f"Creating backup of {directory} to {backup_dir}")
        shutil.copytree(directory, backup_dir)
        print(f"Backup created successfully")
        return True
    except Exception as e:
        print(f"Error creating backup: {str(e)}")
        return False

def delete_cursor_config_files():
    """Delete all Cursor-related configuration files with proper safeguards."""
    directories = [
        os.path.expanduser("~/.cursor"),
        os.path.expanduser("~/.config/Cursor"),
        os.path.expanduser("~/.config/cursor-updater")
    ]

    # First, back up all directories
    backup_success = True
    for directory in directories:
        if os.path.exists(directory):
            if not create_directory_backup(directory):
                backup_success = False
    
    if not backup_success:
        confirm = input("\nSome backups failed. Continue with deletion anyway? (yes/no): ").strip().lower()
        if confirm != "yes":
            print("Operation canceled due to backup failures.")
            return
    
    # Then delete directories
    for directory in directories:
        if os.path.exists(directory):
            print(f"Deleting directory: {directory}")
            try:
                shutil.rmtree(directory)
                print(f"Successfully deleted {directory}")
            except Exception as e:
                print(f"Error deleting {directory}: {str(e)}")
        else:
            print(f"Directory does not exist: {directory}")
    
    print("\nBackups of configuration are stored in ~/cursor_config_backups")

def generate_random_id():
    """Generate a random UUID for configuration."""
    return str(uuid.uuid4())

def modify_storage_json():
    """Modify the storage.json file with new random identifiers."""
    storage_path = os.path.expanduser("~/.config/Cursor/User/globalStorage/storage.json")

    if not os.path.exists(storage_path):
        print(f"Error: storage.json not found at {storage_path}")
        exit(1)

    try:
        # Create backup first
        backup_dir = os.path.expanduser("~/.config/Cursor/User/globalStorage/backups")
        os.makedirs(backup_dir, exist_ok=True)
        backup_path = f"{backup_dir}/storage.json.{datetime.now().strftime('%Y%m%d_%H%M%S')}.bak"
        shutil.copyfile(storage_path, backup_path)
        print(f"Created backup at: {backup_path}")
        
        # Read current file
        with open(storage_path, "r") as file:
            data = json.load(file)
        
        # Generate new unique identifiers
        machine_id = generate_random_id()
        device_id = generate_random_id()
        sqm_id = f"{{{generate_random_id().upper()}}}"
        
        # Update with fields
        data.update({
            "telemetry.machineId": machine_id,
            "telemetry.macMachineId": machine_id,
            "telemetry.devDeviceId": device_id,
            "telemetry.sqmId": sqm_id,
            "lastModified": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S.000Z")
        })
        
        # Save to temporary file first
        temp_path = f"{storage_path}.temp"
        with open(temp_path, "w") as file:
            json.dump(data, file, indent=4)
            
        # Verify JSON is valid
        try:
            with open(temp_path, "r") as file:
                json.load(file)
            # Move temp file to actual location if valid
            shutil.move(temp_path, storage_path)
            print("Successfully updated storage.json")
            
            # Show the new IDs
            print("\nNew configuration values:")
            print(f"Machine ID: {machine_id}")
            print(f"Device ID: {device_id}")
            print(f"SQM ID: {sqm_id}")
            
        except json.JSONDecodeError:
            print("Error: Generated file is corrupted, reverting from backup")
            shutil.copyfile(backup_path, storage_path)
            if os.path.exists(temp_path):
                os.remove(temp_path)
            exit(1)
            
    except json.JSONDecodeError:
        print("Error: storage.json is corrupted or invalid")
        exit(1)
    except Exception as e:
        print(f"Error modifying storage.json: {str(e)}")
        exit(1)

def main():
    # Show security warning first
    show_security_warning()
    
    print("Checking if Cursor IDE is installed...")
    if not check_cursor_installed():
        print("Cursor IDE is not installed.")
        print("Please install Cursor first.")
        exit(0)

    print("\nCursor IDE is installed. Choose an option:")
    print("1. Remove all configuration files and uninstall Cursor")
    print("2. Modify configuration settings (update storage.json with random IDs)")
    
    while True:
        choice = input("\nEnter your choice (1 or 2): ").strip()
        
        if choice == "1":
            confirm = input("\nAre you sure you want to remove all Cursor configuration files? This will delete all settings and preferences. (yes/no): ").strip().lower()
            if confirm == "yes":
                print("\nRemoving all Cursor configuration files...")
                delete_cursor_config_files()
                print("\nAll Cursor configuration files have been removed.")
                print("You can now reinstall Cursor if needed.")
            else:
                print("\nOperation canceled.")
            break
        elif choice == "2":
            print("\nModifying storage.json with new random IDs...")
            modify_storage_json()
            print("\nConfiguration updated successfully.")
            print("Please restart Cursor IDE for changes to take effect.")
            break
        else:
            print("\nInvalid choice. Please enter 1 or 2.")

if __name__ == "__main__":
    main()