#!/usr/bin/env python3
import os
import re

# Regex to find #include <filename.h>
# Captures the filename inside the brackets
include_pattern = re.compile(r'#include\s+<([^>]+)>')

def process_directory(directory):
    # Get a set of all header files in this current directory
    try:
        files = os.listdir(directory)
    except OSError:
        return

    local_headers = set(f for f in files if f.endswith('.h'))
    c_files = [f for f in files if f.endswith('.c') or f.endswith('.cpp')]

    if not local_headers or not c_files:
        return

    for c_file in c_files:
        file_path = os.path.join(directory, c_file)
        
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
                header_name = match.group(1)
                # CHECK: Does this header exist in the current folder?
                if header_name in local_headers:
                    # REPLACE <header.h> with "header.h"
                    new_line = line.replace(f'<{header_name}>', f'"{header_name}"')
                    new_lines.append(new_line)
                    print(f"Fixed: {file_path} -> {header_name}")
                    modified = True
                else:
                    new_lines.append(line)
            else:
                new_lines.append(line)

        # Write back only if we changed something
        if modified:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.writelines(new_lines)

def main():
    print("Scanning kernel tree for incorrect include brackets...")
    # Walk through the entire kernel tree
    for root, dirs, files in os.walk("."):
        # Skip hidden folders like .git
        if "/." in root:
            continue
        process_directory(root)
    print("Done.")

if __name__ == "__main__":
    main()
