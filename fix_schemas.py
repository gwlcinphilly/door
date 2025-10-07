#!/usr/bin/env python3
"""
Script to fix schema references in router files
"""

import os
import re

def fix_schema_references(file_path):
    """Fix schema references in a file"""
    with open(file_path, 'r') as f:
        content = f.read()
    
    # Replace schemas. with empty string
    content = re.sub(r'schemas\.', '', content)
    
    with open(file_path, 'w') as f:
        f.write(content)
    
    print(f"Fixed {file_path}")

# Fix all router files
router_files = [
    'app/routers/information.py',
    'app/routers/notes.py'
]

for file_path in router_files:
    if os.path.exists(file_path):
        fix_schema_references(file_path)
    else:
        print(f"File not found: {file_path}")

print("Schema references fixed!")
