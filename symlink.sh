#!/bin/bash

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

SOURCE_CHIP="mt6765"
TARGET_CHIP="mt6761"

echo -e "${BLUE}==> Scanning for directory mismatches ($SOURCE_CHIP -> $TARGET_CHIP)...${NC}"

# Find all directories named "mt6765"
# We use process substitution to avoid subshell variable scope issues
count=0

while IFS= read -r src_path; do
    # src_path is something like ./drivers/misc/mediatek/chip/mt6765
    
    # Get the parent directory (e.g., ./drivers/misc/mediatek/chip)
    parent_dir=$(dirname "$src_path")
    
    # Define the target path (e.g., ./drivers/misc/mediatek/chip/mt6761)
    target_path="$parent_dir/$TARGET_CHIP"
    
    # Check if the target directory/symlink already exists
    if [ ! -e "$target_path" ]; then
        echo -e "    ${RED}[MISSING]${NC} $target_path"
        
        # Enter the parent directory so we can create a RELATIVE symlink
        # (Relative links are better than absolute because they don't break if you move the kernel folder)
        pushd "$parent_dir" > /dev/null
        
        # Create the symlink: mt6761 -> mt6765
        ln -s "$SOURCE_CHIP" "$TARGET_CHIP"
        
        if [ $? -eq 0 ]; then
             echo -e "    ${GREEN}[FIXED]${NC}   Created symlink: $TARGET_CHIP -> $SOURCE_CHIP"
             ((count++))
        else
             echo -e "    ${RED}[ERROR]${NC}   Failed to create symlink in $parent_dir"
        fi
        
        popd > /dev/null
    fi

done < <(find . -type d -name "$SOURCE_CHIP")

echo -e "${BLUE}==> Scan complete.${NC}"
if [ $count -eq 0 ]; then
    echo -e "${GREEN}No missing symlinks found. Your tree structure looks correct for these chips.${NC}"
else
    echo -e "${GREEN}Fixed $count missing directories.${NC}"
fi
