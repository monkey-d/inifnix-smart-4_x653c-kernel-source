#!/usr/bin/env python3
import os
import re

# Regex to find #include <filename.h>
# Captures the filename inside the brackets
include_pattern = re.compile(r'#include\s+<([^>]+)>')

def process_directory(directory):
    try:
        files = os.listdir(directory)
    except OSError:
        return

    # 1. Identify all header files available in this folder
    local_headers = set(f for f in files if f.endswith('.h'))

    # 2. Identify files we want to scan (Now includes .h)
    target_files = [f for f in files if f.endswith(('.c', '.cpp', '.h'))]

    if not local_headers or not target_files:
        return

    for file_name in target_files:
        file_path = os.path.join(directory, file_name)
        
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                lines = f.readlines()
        except IOError:
            continue

        modified = False
        new_lines = []

        for line in lines:
            match = include_pattern.search(line)
            if match:
                included_header = match.group(1)
                
                # THE LOGIC:
                # If the file being requested (<foo.h>) actually exists 
                # inside this very same folder, change <foo.h> to "foo.h"
                if included_header in local_headers:
                    new_line = line.replace(f'<{included_header}>', f'"{included_header}"')
                    new_lines.append(new_line)
                    print(f"Fixed: {file_path} -> {included_header}")
                    modified = True
                else:
                    new_lines.append(line)
            else:
                new_lines.append(line)

        if modified:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.writelines(new_lines)

def main():
    print("Scanning kernel tree (Sources AND Headers) for incorrect include brackets...")
    for root, dirs, files in os.walk("."):
        if "/." in root: # Skip hidden .git folders
            continue
        process_directory(root)
    print("Done.")

if __name__ == "__main__":
    main()
