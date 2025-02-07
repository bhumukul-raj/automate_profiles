import os
import shutil
import json
from datetime import datetime
import subprocess
from pathlib import Path
import pwd

# Configuration
MERCYHACKS_KEY = "1fc0a7b0-c0bd-4d4a-a841-a95841d8e94f"
TEST_DIR = "cursor_test_environment"

def get_real_user():
    """Get the real user even when running with sudo."""
    try:
        return os.environ.get('SUDO_USER') or os.environ.get('USER') or pwd.getpwuid(os.getuid()).pw_name
    except KeyError:
        return None

def get_user_home():
    """Get the real user's home directory."""
    real_user = get_real_user()
    if real_user:
        return os.path.expanduser(f"~{real_user}")
    return os.path.expanduser("~")

def is_sudo():
    """Check if script is running with sudo privileges."""
    return os.geteuid() == 0

def create_test_environment():
    """Create a test environment by copying necessary Cursor directories."""
    print("\n=== Creating Test Environment ===")
    print(f"Real user: {get_real_user()}")
    print(f"User home: {get_user_home()}")
    
    # Create test directory
    if os.path.exists(TEST_DIR):
        print(f"Cleaning up old test directory: {TEST_DIR}")
        shutil.rmtree(TEST_DIR)
    
    os.makedirs(TEST_DIR)
    print(f"Created test directory: {TEST_DIR}")
    
    # Define source and test paths using real user's home
    user_home = get_user_home()
    source_paths = {
        "config": os.path.join(user_home, ".config/Cursor"),
        "cursor": os.path.join(user_home, ".cursor"),
        "updater": os.path.join(user_home, ".config/cursor-updater")
    }
    
    test_paths = {
        "config": os.path.join(TEST_DIR, ".config/Cursor"),
        "cursor": os.path.join(TEST_DIR, ".cursor"),
        "updater": os.path.join(TEST_DIR, ".config/cursor-updater")
    }
    
    # Copy existing directories to test environment
    real_user = get_real_user()
    uid = pwd.getpwnam(real_user).pw_uid if real_user else os.getuid()
    gid = pwd.getpwnam(real_user).pw_gid if real_user else os.getgid()
    
    for name, source in source_paths.items():
        if os.path.exists(source):
            test_path = test_paths[name]
            os.makedirs(os.path.dirname(test_path), exist_ok=True)
            print(f"Copying {name} directory: {source} -> {test_path}")
            shutil.copytree(source, test_path, dirs_exist_ok=True)
            
            # Fix ownership if running as sudo
            if is_sudo():
                for root, dirs, files in os.walk(test_path):
                    os.chown(root, uid, gid)
                    for d in dirs:
                        os.chown(os.path.join(root, d), uid, gid)
                    for f in files:
                        os.chown(os.path.join(root, f), uid, gid)
    
    return test_paths

def test_file_permissions(test_paths):
    """Test file permissions in the test environment."""
    print("\n=== Testing File Permissions ===")
    
    for name, path in test_paths.items():
        if os.path.exists(path):
            stats = os.stat(path)
            print(f"\nChecking {name} directory: {path}")
            print(f"Owner: {stats.st_uid}")
            print(f"Group: {stats.st_gid}")
            print(f"Permissions: {oct(stats.st_mode)[-3:]}")
            
            # Test write permission
            try:
                test_file = os.path.join(path, "test_write")
                with open(test_file, "w") as f:
                    f.write("test")
                os.remove(test_file)
                print("Write test: Success")
            except Exception as e:
                print(f"Write test: Failed - {str(e)}")

def test_storage_json_modification(test_paths):
    """Test modifying storage.json in test environment."""
    print("\n=== Testing storage.json Modification ===")
    
    storage_path = os.path.join(test_paths["config"], "User/globalStorage/storage.json")
    
    if not os.path.exists(storage_path):
        print(f"Error: storage.json not found at {storage_path}")
        return False
        
    try:
        # Create backup
        backup_path = f"{storage_path}.{datetime.now().strftime('%Y%m%d_%H%M%S')}.bak"
        shutil.copyfile(storage_path, backup_path)
        print(f"Created backup at: {backup_path}")
        
        # Read and modify
        with open(storage_path, "r") as f:
            data = json.load(f)
        
        original_data = data.copy()
        
        # Update with test values
        data.update({
            "telemetry.machineId": MERCYHACKS_KEY,
            "telemetry.macMachineId": MERCYHACKS_KEY,
            "telemetry.devDeviceId": MERCYHACKS_KEY,
            "telemetry.sqmId": MERCYHACKS_KEY,
            "lastModified": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S.000Z"),
            "version": "1.0.1"
        })
        
        # Write modified data
        with open(storage_path, "w") as f:
            json.dump(data, f, indent=4)
        print("Modified storage.json successfully")
        
        # Verify modification
        with open(storage_path, "r") as f:
            verify_data = json.load(f)
        
        if verify_data["telemetry.machineId"] == MERCYHACKS_KEY:
            print("Verification: Success")
        else:
            print("Verification: Failed")
            
        # Restore original data
        with open(storage_path, "w") as f:
            json.dump(original_data, f, indent=4)
        print("Restored original data")
        
        return True
        
    except Exception as e:
        print(f"Error modifying storage.json: {str(e)}")
        return False

def test_directory_deletion(test_paths):
    """Test deleting Cursor directories in test environment."""
    print("\n=== Testing Directory Deletion ===")
    
    for name, path in test_paths.items():
        if os.path.exists(path):
            try:
                print(f"Attempting to delete {name} directory: {path}")
                shutil.rmtree(path)
                if not os.path.exists(path):
                    print("Deletion: Success")
                else:
                    print("Deletion: Failed - Directory still exists")
            except Exception as e:
                print(f"Deletion: Failed - {str(e)}")

def cleanup_test_environment():
    """Clean up the test environment."""
    print("\n=== Cleaning Up Test Environment ===")
    
    if os.path.exists(TEST_DIR):
        try:
            shutil.rmtree(TEST_DIR)
            print("Test environment cleaned up successfully")
        except Exception as e:
            print(f"Error cleaning up test environment: {str(e)}")

def main():
    print("=== Cursor Reset Test Script ===")
    print(f"Running as sudo: {is_sudo()}")
    
    try:
        # Create test environment
        test_paths = create_test_environment()
        
        # Run tests
        test_file_permissions(test_paths)
        test_storage_json_modification(test_paths)
        test_directory_deletion(test_paths)
        
    except Exception as e:
        print(f"\nError during testing: {str(e)}")
    finally:
        # Clean up
        cleanup_test_environment()

if __name__ == "__main__":
    main() 