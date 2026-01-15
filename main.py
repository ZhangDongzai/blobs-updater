#!/usr/bin/env python3

SOURCE_PATH = ""
TARGET_PATH = ""

import sys
import os
import hashlib
import shutil
from typing import List, Tuple, Optional

def parse_blob_line(line: str) -> Tuple[str, str, Optional[str]]:
    """
    Parse a blob line from update.txt
    Format: [-]source[:destination][|sha1sum]
    Returns: (source, destination, sha1sum)
    """
    line = line.strip()
    if not line:
        return "", "", None
    
    # Move - 
    if line.startswith('-'):
        line = line[1:]
    
    # Split by | to separate sha1sum if present
    parts = line.split('|', 1)
    main_part = parts[0]
    sha1sum = parts[1] if len(parts) > 1 else None
    
    # Split by : to separate source and destination
    if ':' in main_part:
        source, destination = main_part.split(':', 1)
    else:
        source = main_part
        destination = source  # destination defaults to source
    
    return source, destination, sha1sum

def get_blobs_between_tags(content: List[str], start_tag: str, end_tag: str) -> List[Tuple[bool, str, str, Optional[str]]]:
    """
    Extract blobs between start_tag and end_tag
    """
    result = []
    in_section = False
    is_delete = False
    
    for line in content:
        line = line.strip()
        if line == start_tag:
            in_section = True
            is_delete = True if start_tag == "#DELETE" else False
            continue
        elif line == end_tag:
            in_section = False
            continue
        
        if in_section:
            try:
                source, destination, sha1sum = parse_blob_line(line)
                result.append((is_delete, source, destination, sha1sum))
            except Exception:
                # Skip invalid lines
                continue
    
    return result

def calculate_sha1(filepath: str) -> str:
    """
    Calculate SHA1 hash of a file
    """
    sha1 = hashlib.sha1()
    with open(filepath, 'rb') as f:
        while True:
            data = f.read(8192)
            if not data:
                break
            sha1.update(data)
    return sha1.hexdigest()

def delete_files(target_path: str, blobs: List[Tuple[bool, str, str, Optional[str]]]):
    """
    Delete files based on the blobs list (where is_delete is True)
    """
    for is_delete, source, destination, sha1sum in blobs:
        if is_delete:
            target_file = os.path.join(target_path, destination.lstrip('/'))
            if os.path.exists(target_file):
                try:
                    os.remove(target_file)
                    #print(f"Deleted: {target_file}")
                except OSError as e:
                    print(f"Error deleting {target_file}: {e}")
            else:
                print(f"File does not exist, skipping delete: {target_file}")

def copy_and_verify_files(source_path: str, target_path: str, blobs: List[Tuple[bool, str, str, Optional[str]]]):
    """
    Copy files from source_path to target_path and verify with SHA1
    """
    for is_delete, source, destination, expected_sha1 in blobs:
        if not is_delete:  # Only process non-delete entries
            source_file = os.path.join(source_path, destination.lstrip('/'))
            target_file = os.path.join(target_path, destination.lstrip('/'))
            
            # Create target directory if it doesn't exist
            target_dir = os.path.dirname(target_file)
            os.makedirs(target_dir, exist_ok=True)
            
            if not os.path.exists(source_file):
                print(f"Source file does not exist: {source_file}")
                continue
            
            try:
                # Copy file
                shutil.copy2(source_file, target_file)
                #print(f"Copied: {source_file} -> {target_file}")
                
                # Verify SHA1 if provided
                if expected_sha1:
                    actual_sha1 = calculate_sha1(target_file)
                    if actual_sha1.lower() != expected_sha1.lower():
                        print(f"SHA1 verification failed for {target_file}")
                        print(f"  Expected: {expected_sha1}")
                        print(f"  Actual:   {actual_sha1}")
                        # Optionally remove the file if verification fails
                        os.remove(target_file) if input("Delete? (y/n) ")[0] == "y" else []
                    
            except Exception as e:
                print(f"Error copying {source_file} to {target_file}: {e}")

def main():
    if len(sys.argv) != 2:
        print("Usage: ./main.py update.txt")
        sys.exit(1)
    
    update_file = sys.argv[1]
    
    if not os.path.exists(update_file):
        print(f"Update file does not exist: {update_file}")
        sys.exit(1)
    
    # Read the update.txt file
    try:
        with open(update_file, 'r', encoding='utf-8') as f:
            content = f.readlines()
    except Exception as e:
        print(f"Error reading update file: {e}")
        sys.exit(1)

    source_path = SOURCE_PATH
    target_path = TARGET_PATH
    
    # Process DELETE section
    delete_blobs = get_blobs_between_tags(content, "#DELETE", "#END")
    print(f"Processing {len(delete_blobs)} delete operations...")
    delete_files(target_path, delete_blobs)
    
    # Process ADD section
    add_blobs = get_blobs_between_tags(content, "#ADD", "#END")
    print(f"Processing {len(add_blobs)} add operations...")
    copy_and_verify_files(source_path, target_path, add_blobs)

if __name__ == "__main__":
    main()
