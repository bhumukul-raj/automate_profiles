#!/bin/bash

# Error handling
set -e

# Color definitions
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Log functions
log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

log_debug() {
    echo -e "${BLUE}[DEBUG]${NC} $1"
}

# Get current user
get_current_user() {
    if [ "$EUID" -eq 0 ]; then
        echo "$SUDO_USER"
    else
        echo "$USER"
    fi
}

CURRENT_USER=$(get_current_user)
if [ -z "$CURRENT_USER" ]; then
    log_error "Unable to get username"
    exit 1
fi

# Define configuration file paths (modified for Linux path)
STORAGE_FILE="/home/$CURRENT_USER/.config/Cursor/User/globalStorage/storage.json"
BACKUP_DIR="/home/$CURRENT_USER/.config/Cursor/User/globalStorage/backups"

# Display security warning and get confirmation
show_security_warning() {
    echo
    log_warn "⚠️ SECURITY AND STABILITY WARNING ⚠️"
    echo "This script will make the following changes to your system:"
    echo "1. Modify Cursor's configuration files"
    echo "2. May request to modify system machine-id files"
    echo "3. May attempt to close any running Cursor processes"
    echo
    echo "These changes may have the following impacts:"
    echo "- Modifying machine-id could affect other applications that rely on this identifier"
    echo "- Forcibly closing Cursor may result in data loss if you have unsaved changes"
    echo "- Setting files as immutable may cause issues with future software updates"
    echo
    echo -n "Do you understand these risks and wish to continue? (yes/no): "
    read -r confirmation
    if [[ "$confirmation" != "yes" ]]; then
        log_info "Operation cancelled by user"
        exit 0
    fi
}

# Check permissions
check_permissions() {
    if [ "$EUID" -ne 0 ]; then
        log_error "Please run this script with sudo"
        echo "Example: sudo $0"
        exit 1
    fi
}

# Check and gently close Cursor process
check_and_close_cursor() {
    log_info "Checking for running Cursor processes..."
    
    # Use more precise method to find Cursor process
    CURSOR_PIDS=$(ps aux | grep -E "/[C]ursor|[C]ursor$" | awk '{print $2}' || true)
    
    if [ -z "$CURSOR_PIDS" ]; then
        log_info "No running Cursor process found"
        return 0
    fi
    
    log_warn "Found running Cursor processes"
    ps aux | grep -E "/[C]ursor|[C]ursor$" || true
    
    echo
    log_warn "It is recommended to close Cursor normally before proceeding"
    echo -n "Attempt to close Cursor now? (yes/no/force): "
    read -r close_choice
    
    if [[ "$close_choice" == "no" ]]; then
        log_info "Please close Cursor manually and restart this script"
        exit 0
    fi
    
    if [[ "$close_choice" == "yes" ]]; then
        local attempt=1
        local max_attempts=3
        
        while [ $attempt -le $max_attempts ]; do
            log_info "Sending normal termination signal to Cursor (attempt $attempt/$max_attempts)..."
            
            # Send SIGTERM to each PID
            for pid in $CURSOR_PIDS; do
                kill "${pid}" 2>/dev/null || true
            done
            
            # Wait a moment and check if processes are still running
            sleep 3
            CURSOR_PIDS=$(ps aux | grep -E "/[C]ursor|[C]ursor$" | awk '{print $2}' || true)
            
            if [ -z "$CURSOR_PIDS" ]; then
                log_info "Cursor has been closed successfully"
                return 0
            fi
            
            log_warn "Cursor is still running, waiting a bit longer..."
            ((attempt++))
            sleep 2
        done
        
        # If we get here, normal termination failed
        log_warn "Unable to close Cursor normally after $max_attempts attempts"
        echo -n "Forcibly terminate Cursor? WARNING: This may cause data loss! (yes/no): "
        read -r force_close
        
        if [[ "$force_close" != "yes" ]]; then
            log_info "Please close Cursor manually and restart this script"
            exit 0
        fi
    fi
    
    # Force option selected or normal close failed and force approved
    log_warn "Attempting to forcibly terminate Cursor processes..."
    for pid in $CURSOR_PIDS; do
        log_warn "Force terminating process PID: ${pid}..."
        kill -9 "${pid}" 2>/dev/null || true
    done
    
    sleep 2
    CURSOR_PIDS=$(ps aux | grep -E "/[C]ursor|[C]ursor$" | awk '{print $2}' || true)
    
    if [ -z "$CURSOR_PIDS" ]; then
        log_info "Cursor has been forcibly terminated"
        return 0
    else
        log_error "Unable to terminate Cursor processes"
        log_error "Please close Cursor manually and try again"
        exit 1
    fi
}

# Backup system ID
backup_system_id() {
    log_info "Backing up system ID..."
    mkdir -p "$BACKUP_DIR"
    local system_id_file="$BACKUP_DIR/system_id.backup_$(date +%Y%m%d_%H%M%S)"
    
    # Get and backup machine-id
    {
        echo "# Original Machine ID Backup" > "$system_id_file"
        echo "## /var/lib/dbus/machine-id:" >> "$system_id_file"
        cat /var/lib/dbus/machine-id 2>/dev/null >> "$system_id_file" || echo "Not found" >> "$system_id_file"
        
        echo -e "\n## /etc/machine-id:" >> "$system_id_file"
        cat /etc/machine-id 2>/dev/null >> "$system_id_file" || echo "Not found" >> "$system_id_file"
        
        echo -e "\n## hostname:" >> "$system_id_file"
        hostname >> "$system_id_file"
        
        chmod 444 "$system_id_file"
        chown "$CURRENT_USER:$CURRENT_USER" "$system_id_file"
        log_info "System ID backed up to: $system_id_file"
    } || {
        log_error "Backup system ID failed"
        return 1
    }
}

# Backup configuration file
backup_config() {
    # Check file permissions
    if [ -f "$STORAGE_FILE" ] && [ ! -w "$STORAGE_FILE" ]; then
        log_warn "Cannot write to configuration file, attempting to fix permissions..."
        # Try to fix permissions
        if command -v chattr &> /dev/null; then
            chattr -i "$STORAGE_FILE" 2>/dev/null || true
        fi
        chmod 644 "$STORAGE_FILE" 2>/dev/null || {
            log_error "Cannot modify file permissions, please check manually"
            exit 1
        }
    fi
    
    if [ ! -f "$STORAGE_FILE" ]; then
        log_warn "Configuration file does not exist, skipping backup"
        return 0
    fi
    
    mkdir -p "$BACKUP_DIR"
    local backup_file="$BACKUP_DIR/storage.json.backup_$(date +%Y%m%d_%H%M%S)"
    
    if cp "$STORAGE_FILE" "$backup_file"; then
        chmod 644 "$backup_file"
        chown "$CURRENT_USER:$CURRENT_USER" "$backup_file"
        log_info "Configuration backed up to: $backup_file"
    else
        log_error "Backup failed"
        exit 1
    fi
}

# Generate random ID
generate_random_id() {
    # Linux can use /dev/urandom
    head -c 32 /dev/urandom | xxd -p
}

# Generate random UUID
generate_uuid() {
    # Linux uses uuidgen command
    uuidgen | tr '[:upper:]' '[:lower:]'
}

# Generate new configuration
generate_new_config() {
    # Error handling
    if ! command -v xxd &> /dev/null; then
        log_error "xxd command not found, please install xxd using apt-get install xxd"
        exit 1
    fi
    
    if ! command -v uuidgen &> /dev/null; then
        log_error "uuidgen command not found, please install uuidgen using apt-get install uuid-runtime"
        exit 1
    fi
    
    # Check if configuration file exists
    if [ ! -f "$STORAGE_FILE" ]; then
        log_error "Configuration file not found: $STORAGE_FILE"
        log_warn "Please install and run Cursor once before using this script"
        exit 1
    fi
    
    # Ask user if they want to modify system machine-id (instead of doing it automatically)
    echo
    log_warn "Do you want to modify the system machine-id files?"
    echo "This can affect other applications that rely on this identifier."
    echo "It's generally safer to modify only Cursor's configuration."
    echo "0) No - Only modify Cursor's configuration (recommended, press Enter)"
    echo "1) Yes - Modify system machine-id files"
    read -r modify_machine_id
    
    if [ "$modify_machine_id" = "1" ]; then
        if [ -f "/etc/machine-id" ]; then
            log_info "Modifying system machine-id..."
            local new_machine_id=$(uuidgen | tr -d '-')
            
            # Backup original machine-id
            backup_system_id
            
            # Modify machine-id
            echo "$new_machine_id" | sudo tee /etc/machine-id > /dev/null
            if [ -f "/var/lib/dbus/machine-id" ]; then
                sudo ln -sf /etc/machine-id /var/lib/dbus/machine-id
            fi
            log_info "System machine-id updated"
        fi
    else
        log_info "Skipping system machine-id modification"
    fi
    
    # Convert auth0|user_ to byte array hexadecimal
    local machine_id="auth0|user_$(generate_random_id | cut -c 1-32)"
    
    local mac_machine_id=$(generate_random_id)
    local device_id=$(generate_uuid | tr '[:upper:]' '[:lower:]')
    local sqm_id="{$(generate_uuid | tr '[:lower:]' '[:upper:]')}"
    
    # Enhanced escape function
    escape_sed_replacement() {
        echo "$1" | sed -e 's/[\/&]/\\&/g'
    }

    # Escape variables
    machine_id_escaped=$(escape_sed_replacement "$machine_id")
    mac_machine_id_escaped=$(escape_sed_replacement "$mac_machine_id")
    device_id_escaped=$(escape_sed_replacement "$device_id")
    sqm_id_escaped=$(escape_sed_replacement "$sqm_id")

    # Make a temporary copy to work with
    local temp_file=$(mktemp)
    cp "$STORAGE_FILE" "$temp_file"

    # Use enhanced regular expressions and escape
    sed -i "s|\"telemetry\.machineId\": *\"[^\"]*\"|\"telemetry.machineId\": \"${machine_id_escaped}\"|" "$temp_file"
    sed -i "s|\"telemetry\.macMachineId\": *\"[^\"]*\"|\"telemetry.macMachineId\": \"${mac_machine_id_escaped}\"|" "$temp_file"
    sed -i "s|\"telemetry\.devDeviceId\": *\"[^\"]*\"|\"telemetry.devDeviceId\": \"${device_id_escaped}\"|" "$temp_file"
    sed -i "s|\"telemetry\.sqmId\": *\"[^\"]*\"|\"telemetry.sqmId\": \"${sqm_id_escaped}\"|" "$temp_file"

    # Verify the temp file before moving it to the actual location
    if command -v jq &> /dev/null; then
        if ! jq empty "$temp_file" &> /dev/null; then
            log_error "Temporary file format error, modifications aborted"
            rm "$temp_file"
            exit 1
        fi
    fi

    # Move the temp file to the correct location
    mv "$temp_file" "$STORAGE_FILE"

    # Set file permissions and owner
    chmod 644 "$STORAGE_FILE"  # Set to read-write permissions for owner
    chown "$CURRENT_USER:$CURRENT_USER" "$STORAGE_FILE"
    
    # Ask user if they want to set read-only permissions
    echo
    log_warn "Do you want to set read-only permissions on the configuration file?"
    echo "This may help prevent changes, but could cause issues with updates."
    echo "0) No - Keep normal permissions (recommended, press Enter)"
    echo "1) Yes - Set to read-only"
    echo "2) Yes - Set to read-only and immutable (most restrictive)"
    read -r perm_choice
    
    if [ "$perm_choice" = "1" ] || [ "$perm_choice" = "2" ]; then
        chmod 444 "$STORAGE_FILE"  # Change to read-only permissions
        log_info "Set read-only permissions on configuration file"
        
        # Set immutable if requested
        if [ "$perm_choice" = "2" ] && command -v chattr &> /dev/null; then
            chattr +i "$STORAGE_FILE" 2>/dev/null && \
            log_info "Configuration file set as immutable" || \
            log_warn "Failed to set immutable attribute"
        fi
    fi
    
    echo
    log_info "Updated configuration:"
    log_debug "machineId: $machine_id"
    log_debug "macMachineId: $mac_machine_id"
    log_debug "devDeviceId: $device_id"
    log_debug "sqmId: $sqm_id"

    # Verify configuration after all modifications
    log_info "Verifying configuration file validity..."
    if ! command -v jq &> /dev/null; then
        log_warn "jq command not found, skipping JSON validation"
    else
        if ! jq empty "$STORAGE_FILE" &> /dev/null; then
            log_error "Configuration file format error, restoring backup..."
            cp "$(ls -t "$BACKUP_DIR"/storage.json.backup_* | head -1)" "$STORAGE_FILE"
            chmod 644 "$STORAGE_FILE"
            chown "$CURRENT_USER:$CURRENT_USER" "$STORAGE_FILE"
            exit 1
        fi
    fi
}

# Show file tree structure
show_file_tree() {
    local base_dir=$(dirname "$STORAGE_FILE")
    echo
    log_info "File structure:"
    echo -e "${BLUE}$base_dir${NC}"
    echo "├── globalStorage"
    echo "│   ├── storage.json (modified)"
    echo "│   └── backups"
    
    # List backup files
    if [ -d "$BACKUP_DIR" ]; then
        local backup_files=("$BACKUP_DIR"/*)
        if [ ${#backup_files[@]} -gt 0 ] && [ -e "${backup_files[0]}" ]; then
            for file in "${backup_files[@]}"; do
                if [ -f "$file" ]; then
                    echo "│       └── $(basename "$file")"
                fi
            done
        else
            echo "│       └── (empty)"
        fi
    fi
    echo
}

# Modify disable_auto_update function, add manual instructions for failure handling
disable_auto_update() {
    echo
    log_warn "Do you want to disable Cursor auto-update feature?"
    echo "Note: Disabling updates may prevent you from receiving security and feature updates"
    echo "0) No - Keep default settings (recommended, press Enter)"
    echo "1) Yes - Disable auto-update"
    read -r choice
    
    if [ "$choice" = "1" ]; then
        echo
        log_info "Processing auto-update..."
        local updater_path="$HOME/.config/cursor-updater"
        
        # Define manual setup guide
        show_manual_guide() {
            echo
            log_warn "Automatic setup failed, please try manual operation:"
            echo -e "${YELLOW}Manual steps to disable updates:${NC}"
            echo "1. Open terminal"
            echo "2. Copy and paste the following command:"
            echo -e "${BLUE}rm -rf \"$updater_path\" && touch \"$updater_path\" && chmod 444 \"$updater_path\"${NC}"
            echo
            echo -e "${YELLOW}If the above command shows permission error, use sudo:${NC}"
            echo -e "${BLUE}sudo rm -rf \"$updater_path\" && sudo touch \"$updater_path\" && sudo chmod 444 \"$updater_path\"${NC}"
            echo
            log_warn "Please restart Cursor after completion"
        }
        
        if [ -d "$updater_path" ]; then
            rm -rf "$updater_path" 2>/dev/null || {
                log_error "Failed to delete cursor-updater directory"
                show_manual_guide
                return 1
            }
            log_info "Successfully deleted cursor-updater directory"
        fi
        
        touch "$updater_path" 2>/dev/null || {
            log_error "Failed to create block file"
            show_manual_guide
            return 1
        }
        
        if ! chmod 444 "$updater_path" 2>/dev/null || ! chown "$CURRENT_USER:$CURRENT_USER" "$updater_path" 2>/dev/null; then
            log_error "Failed to set file permissions"
            show_manual_guide
            return 1
        fi
        
        # Ask about immutable attribute instead of setting automatically
        echo
        log_warn "Do you want to set the update blocker file as immutable?"
        echo "This makes it harder to change but might cause issues with future operations."
        echo "0) No - Keep normal read-only permissions (recommended, press Enter)"
        echo "1) Yes - Also set immutable attribute"
        read -r immutable_choice
        
        if [ "$immutable_choice" = "1" ] && command -v chattr &> /dev/null; then
            chattr +i "$updater_path" 2>/dev/null && \
            log_info "Update blocker file set as immutable" || \
            log_warn "Failed to set immutable attribute, but file is still read-only"
        fi
        
        # Verify setting
        if [ ! -f "$updater_path" ]; then
            log_error "Verification failed: Update blocker file not found"
            show_manual_guide
            return 1
        elif [ -w "$updater_path" ]; then
            log_warn "Verification notice: File is writable, updates may still occur"
            show_manual_guide
            return 1
        else
            log_info "Successfully disabled auto-update"
        fi
    else
        log_info "Keeping default settings, no changes to update mechanism"
    fi
}

# Main function
main() {
    clear
    # Display simplified logo without promotional content
    echo -e "
    ██████╗██╗   ██╗██████╗ ███████╗ ██████╗ ██████╗ 
   ██╔════╝██║   ██║██╔══██╗██╔════╝██╔═══██╗██╔══██╗
   ██║     ██║   ██║██████╔╝███████╗██║   ██║██████╔╝
   ██║     ██║   ██║██╔══██╗╚════██║██║   ██║██╔══██╗
   ╚██████╗╚██████╔╝██║  ██║███████║╚██████╔╝██║  ██║
    ╚═════╝ ╚═════╝ ╚═╝  ╚═╝╚══════╝ ╚═════╝ ╚═╝  ╚═╝
    "
    echo -e "${BLUE}================================${NC}"
    echo -e "${GREEN}   Cursor Device ID Modifier Tool   ${NC}"
    echo -e "${BLUE}================================${NC}"
    echo
    echo -e "${YELLOW}[Important Note]${NC} This tool supports Cursor v0.45.x"
    echo
    
    show_security_warning
    check_permissions
    check_and_close_cursor
    backup_config
    generate_new_config
    
    echo
    log_info "Operation completed!"
    show_file_tree
    log_info "Please restart Cursor to apply new configuration"
    
    disable_auto_update
}

# Execute main function
main
