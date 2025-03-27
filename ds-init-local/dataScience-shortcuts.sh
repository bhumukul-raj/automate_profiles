#!/bin/bash
# =============================
# Create Desktop Shortcuts Script
# Version: 1.1
# Author: Bhumukulraj
# =============================

# Colors and formatting
BOLD='\033[1m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Symbols
CHECK="✓"
CROSS="✗"
ARROW="➜"

# Default Configuration
SOURCE_DIR="/media/bhumukul-raj/ssd_DataScience6/data-science-projects-git-local"
DESKTOP_DIR="$HOME/Desktop"
DRY_RUN=false

# Counters
TOTAL=0
CREATED=0
REMOVED=0
SKIPPED=0

# =============================
# Functions
# =============================

print_usage() {
    echo -e "${BOLD}Usage:${NC}"
    echo -e "  $0 [options]"
    echo -e "\n${BOLD}Options:${NC}"
    echo -e "  -s, --source <dir>    Source directory path (default: $SOURCE_DIR)"
    echo -e "  -d, --desktop <dir>   Desktop directory path (default: $DESKTOP_DIR)"
    echo -e "  -n, --dry-run         Simulate the operation without making changes"
    echo -e "  -h, --help            Display this help message and exit"
}

print_header() {
    echo -e "${BOLD}${BLUE}"
    echo "=============================================="
    echo "       Desktop Shortcut Creator v1.1          "
    echo "=============================================="
    echo -e "${NC}"
}

print_section() {
    echo -e "${BOLD}${YELLOW}$1${NC}"
}

print_status() {
    if [ "$1" == "success" ]; then
        echo -e "${GREEN}  ${CHECK} $2${NC}"
    elif [ "$1" == "error" ]; then
        echo -e "${RED}  ${CROSS} $2${NC}"
    elif [ "$1" == "warning" ]; then
        echo -e "${YELLOW}  ${ARROW} $2${NC}"
    elif [ "$1" == "info" ]; then
        echo -e "${BLUE}  ➜ $2${NC}"
    fi
}

validate_directories() {
    print_section "Validating Directories"
    
    if [ ! -d "$SOURCE_DIR" ]; then
        print_status "error" "Source directory not found: $SOURCE_DIR"
        exit 1
    else
        print_status "success" "Source directory verified: ${BOLD}$SOURCE_DIR"
    fi

    if [ ! -d "$DESKTOP_DIR" ]; then
        print_status "error" "Desktop directory not found: $DESKTOP_DIR"
        exit 1
    else
        print_status "success" "Desktop directory verified: ${BOLD}$DESKTOP_DIR"
    fi
    
    if [ "$DRY_RUN" = true ]; then
        print_status "warning" "DRY RUN MODE: No actual changes will be made"
    fi
}

verify_symlink() {
    local shortcut="$1"
    local target="$2"
    
    if [ -L "$shortcut" ]; then
        local current_target=$(readlink "$shortcut")
        if [ "$current_target" == "$target" ]; then
            return 0  # Already points to the correct target
        fi
    fi
    return 1  # Not a symlink or points to wrong target
}

create_shortcuts() {
    print_section "Processing Projects"
    
    local count=$(ls -l "$SOURCE_DIR" | grep -c ^d)
    print_status "info" "Found ${BOLD}$count projects${NC} in source directory"

    for item in "$SOURCE_DIR"/*; do
        if [ -d "$item" ]; then
            ((TOTAL++))
            local project_name=$(basename "$item")
            local shortcut_path="$DESKTOP_DIR/$project_name"

            echo -e "\n${BOLD}Processing: ${BLUE}$project_name${NC}"
            
            if verify_symlink "$shortcut_path" "$item"; then
                print_status "info" "Shortcut already exists and points to the correct target"
                ((SKIPPED++))
                continue
            elif [ -L "$shortcut_path" ]; then
                print_status "warning" "Existing shortcut points to wrong target"
                
                if [ "$DRY_RUN" = true ]; then
                    print_status "info" "Would remove existing shortcut (dry run)"
                    ((REMOVED++))
                else
                    if rm "$shortcut_path"; then
                        print_status "success" "Removed existing shortcut"
                        ((REMOVED++))
                    else
                        print_status "error" "Failed to remove existing shortcut"
                        ((SKIPPED++))
                        continue
                    fi
                fi
            elif [ -e "$shortcut_path" ]; then
                print_status "error" "Path exists but is not a symlink: $shortcut_path"
                ((SKIPPED++))
                continue
            fi

            if [ "$DRY_RUN" = true ]; then
                print_status "info" "Would create new shortcut to $item (dry run)"
                ((CREATED++))
            else
                if ln -s "$item" "$shortcut_path"; then
                    print_status "success" "Created new shortcut"
                    ((CREATED++))
                else
                    print_status "error" "Failed to create shortcut"
                    ((SKIPPED++))
                fi
            fi
        fi
    done
}

show_summary() {
    print_section "Operation Summary"
    
    echo -e "${BOLD}Total Projects:${NC} $TOTAL"
    echo -e "${GREEN}${CHECK} Successfully Created:${NC} $CREATED"
    echo -e "${YELLOW}${ARROW} Removed Existing:${NC} $REMOVED"
    echo -e "${RED}${CROSS} Skipped/Failed:${NC} $SKIPPED"
    
    if [ "$DRY_RUN" = true ]; then
        echo -e "\n${BOLD}${YELLOW}Dry run completed. No actual changes were made.${NC}"
        echo -e "Run without the --dry-run option to apply changes."
    else
        echo -e "\n${BOLD}${GREEN}Operation completed successfully!${NC}"
    fi
}

# =============================
# Parse Command-Line Arguments
# =============================

while [[ "$#" -gt 0 ]]; do
    case $1 in
        -s|--source) SOURCE_DIR="$2"; shift ;;
        -d|--desktop) DESKTOP_DIR="$2"; shift ;;
        -n|--dry-run) DRY_RUN=true ;;
        -h|--help) print_usage; exit 0 ;;
        *) echo "Unknown parameter: $1"; print_usage; exit 1 ;;
    esac
    shift
done

# =============================
# Main Execution
# =============================

clear
print_header
validate_directories
create_shortcuts
show_summary