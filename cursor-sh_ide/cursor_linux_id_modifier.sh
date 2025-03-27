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

# Check permissions
check_permissions() {
    if [ "$EUID" -ne 0 ]; then
        log_error "Please run this script with sudo"
        echo "Example: sudo $0"
        exit 1
    fi
}

# Check and kill Cursor process
check_and_kill_cursor() {
    log_info "Checking Cursor process..."
    
    local attempt=1
    local max_attempts=5
    
    # Function: Get process details
    get_process_details() {
        local process_name="$1"
        log_debug "Getting process details for $process_name:"
        ps aux | grep -E "/[C]ursor|[C]ursor$" || true
    }
    
    while [ $attempt -le $max_attempts ]; do
        # Use more precise method to find Cursor process
        CURSOR_PIDS=$(ps aux | grep -E "/[C]ursor|[C]ursor$" | awk '{print $2}' || true)
        
        if [ -z "$CURSOR_PIDS" ]; then
            log_info "No running Cursor process found"
            return 0
        fi
        
        log_warn "Found running Cursor process"
        get_process_details "Cursor"
        
        log_warn "Attempting to close Cursor process..."
        
        # Iterate through each PID and try to terminate
        for pid in $CURSOR_PIDS; do
            if [ $attempt -eq $max_attempts ]; then
                log_warn "Attempting to force terminate process PID: ${pid}..."
                kill -9 "${pid}" 2>/dev/null || true
            else
                kill "${pid}" 2>/dev/null || true
            fi
        done
        
        sleep 2
        
        # Check if any Cursor process is still running
        if ! ps aux | grep -E "/[C]ursor|[C]ursor$" > /dev/null; then
            log_info "Cursor process successfully closed"
            return 0
        fi
        
        log_warn "Waiting for process to close, attempt $attempt/$max_attempts..."
        ((attempt++))
        sleep 1
    done
    
    log_error "Unable to close Cursor process after $max_attempts attempts"
    get_process_details "Cursor"
    log_error "Please close the process manually and try again"
    exit 1
}

# Backup system ID
backup_system_id() {
    log_info "Backing up system ID..."
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
        log_error "Cannot write to configuration file, please check permissions"
        exit 1
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
    
    # Modify system machine-id
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

    # Use enhanced regular expressions and escape
    sed -i "s|\"telemetry\.machineId\": *\"[^\"]*\"|\"telemetry.machineId\": \"${machine_id_escaped}\"|" "$STORAGE_FILE"
    sed -i "s|\"telemetry\.macMachineId\": *\"[^\"]*\"|\"telemetry.macMachineId\": \"${mac_machine_id_escaped}\"|" "$STORAGE_FILE"
    sed -i "s|\"telemetry\.devDeviceId\": *\"[^\"]*\"|\"telemetry.devDeviceId\": \"${device_id_escaped}\"|" "$STORAGE_FILE"
    sed -i "s|\"telemetry\.sqmId\": *\"[^\"]*\"|\"telemetry.sqmId\": \"${sqm_id_escaped}\"|" "$STORAGE_FILE"

    # Set file permissions and owner
    chmod 444 "$STORAGE_FILE"  # Change to read-only permissions
    chown "$CURRENT_USER:$CURRENT_USER" "$STORAGE_FILE"
    
    # Verify permissions
    if [ -w "$STORAGE_FILE" ]; then
        log_warn "Unable to set read-only permissions, trying other method..."
        # On Linux, use chattr command to set immutable attribute
        if command -v chattr &> /dev/null; then
            chattr +i "$STORAGE_FILE" 2>/dev/null || log_warn "chattr setting failed"
        fi
    else
        log_info "Successfully set read-only permissions"
    fi
    
    echo
    log_info "Updated configuration:"
    log_debug "machineId: $machine_id"
    log_debug "macMachineId: $mac_machine_id"
    log_debug "devDeviceId: $device_id"
    log_debug "sqmId: $sqm_id"

    # Add verification at the end of generate_new_config function
    log_info "Verifying configuration file validity..."
    if ! command -v jq &> /dev/null; then
        log_warn "jq command not found, skipping JSON validation"
    else
        if ! jq empty "$STORAGE_FILE" &> /dev/null; then
            log_error "Configuration file format error, restoring backup..."
            cp "$(ls -t "$BACKUP_DIR"/storage.json.backup_* | head -1)" "$STORAGE_FILE"
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

# Show subscription information
show_follow_info() {
    echo
    echo -e "${GREEN}================================${NC}"
    echo -e "${YELLOW}  Follow WeChat Official Account [JianBingGuoZiJuanAI] to discuss more Cursor tips and AI knowledge ${NC}"
    echo -e "${GREEN}================================${NC}"
    echo
}

# Modify disable_auto_update function, add manual instructions for failure handling
disable_auto_update() {
    echo
    log_warn "Do you want to disable Cursor auto-update feature?"
    echo "0) No - Keep default settings (press Enter)"
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
            echo -e "${YELLOW}For additional protection (recommended), execute:${NC}"
            echo -e "${BLUE}sudo chattr +i \"$updater_path\"${NC}"
            echo
            echo -e "${YELLOW}Verification method:${NC}"
            echo "1. Run command: ls -l \"$updater_path\""
            echo "2. Confirm file permissions are r--r--r--"
            echo "3. Run command: lsattr \"$updater_path\""
            echo "4. Confirm 'i' attribute exists (if chattr command was executed)"
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
        
        # Try to set immutable attribute
        if command -v chattr &> /dev/null; then
            chattr +i "$updater_path" 2>/dev/null || {
                log_warn "chattr setting failed"
                show_manual_guide
                return 1
            }
        fi
        
        # Verify setting
        if [ ! -f "$updater_path" ] || [ -w "$updater_path" ]; then
            log_error "Verification failed: File permissions may not be effective"
            show_manual_guide
            return 1
        fi
        
        log_info "Successfully disabled auto-update"
    else
        log_info "Keeping default settings, no changes"
    fi
}

# Main function
main() {
    clear
    # Display Logo
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
    echo -e "${YELLOW}  Follow WeChat Official Account [JianBingGuoZiJuanAI]     ${NC}"
    echo -e "${YELLOW}  Join us to discuss more Cursor tips and AI knowledge (Script is free, follow WeChat Official Account to join group for more tips)  ${NC}"
    echo -e "${BLUE}================================${NC}"
    echo
    echo -e "${YELLOW}[Important Note]${NC} This tool supports Cursor v0.45.x"
    echo -e "${YELLOW}[Important Note]${NC} This tool is free, if it helps you, please follow WeChat Official Account [JianBingGuoZiJuanAI]"
    echo
    
    check_permissions
    check_and_kill_cursor
    backup_config
    generate_new_config
    
    echo
    log_info "Operation completed!"
    show_follow_info
    show_file_tree
    log_info "Please restart Cursor to apply new configuration"
    
    disable_auto_update
}

# Execute main function
main
