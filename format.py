#!/usr/bin/env python3

import sys
import re

def parse_git_diff(diff_file):
    with open(diff_file, 'r') as f:
        lines = f.readlines()
    
    delete_lines = []
    add_lines = []
    
    in_diff_section = False
    
    for line in lines:
        line = line.rstrip('\n')
        
        # Check if this is a diff header line
        if line.startswith('diff --git'):
            in_diff_section = True
            continue
        
        # Check if this is a hunk header
        if line.startswith('@@'):
            continue
            
        # Skip context lines (starting with space)
        if line.startswith(' '):
            continue
            
        # Skip lines starting with --- or +++
        if line.startswith('---') or line.startswith('+++'):
            continue
            
        # Process deletion lines (starting with -) but not the header
        if line.startswith('-') and not line.startswith('---'):
            # Skip comment lines (starting with -#)
            if not line.startswith('-#'):
                delete_lines.append(line[1:])  # Remove the leading '-'
        
        # Process addition lines (starting with +) but not the header
        elif line.startswith('+') and not line.startswith('+++'):
            # Skip comment lines (starting with +#)
            if not line.startswith('+#'):
                add_lines.append(line[1:])  # Remove the leading '+'
    
    return delete_lines, add_lines

def main():
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} git-diff.txt")
        sys.exit(1)
    
    diff_file = sys.argv[1]
    
    try:
        delete_lines, add_lines = parse_git_diff(diff_file)
        
        # Print DELETE section
        print("#DELETE")
        for line in delete_lines:
            print(line) if line != "" else []
        print("#END")
        print()  # Empty line for readability
        
        # Print ADD section
        print("#ADD")
        for line in add_lines:
            print(line) if line != "" else []
        print("#END")
        
    except FileNotFoundError:
        print(f"Error: File '{diff_file}' not found.")
        sys.exit(1)
    except Exception as e:
        print(f"Error processing file: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
