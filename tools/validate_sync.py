#!/usr/bin/env python3
"""
Validation script to check sync between diagrams and markdown files.

Checks:
- All images in diagrams/ have corresponding .md files in _diagrams/
- All .md files have corresponding images
- Naming convention compliance
- No orphaned files
"""

import sys
from pathlib import Path
import re

DIAGRAMS_DIR = Path("diagrams")
MARKDOWN_DIR = Path("_diagrams")
NAMING_PATTERN = r'^\d{4}_[A-Z]+__[A-Z_]+\.(jpg|jpeg|png|md)$'

def validate_naming(filename: str) -> bool:
    """Check if filename follows the YYYY_SLUG__TYPE_DESC.ext convention."""
    return bool(re.match(NAMING_PATTERN, filename))

def main():
    errors = []
    warnings = []
    
    # Check directories exist
    if not DIAGRAMS_DIR.exists():
        errors.append(f"❌ Directory not found: {DIAGRAMS_DIR}")
        print("\n".join(errors))
        sys.exit(1)
    
    if not MARKDOWN_DIR.exists():
        errors.append(f"❌ Directory not found: {MARKDOWN_DIR}")
        print("\n".join(errors))
        sys.exit(1)
    
    # Get all images
    images = {
        p.stem: p 
        for p in DIAGRAMS_DIR.iterdir() 
        if p.suffix.lower() in {'.jpg', '.jpeg', '.png'}
    }
    
    # Get all markdown files
    markdowns = {
        p.stem: p 
        for p in MARKDOWN_DIR.iterdir() 
        if p.suffix == '.md'
    }
    
    # Check for missing markdown files
    for stem, img_path in images.items():
        if stem not in markdowns:
            warnings.append(f"⚠️  Image without markdown: {img_path.name}")
        
        # Check naming convention
        if not validate_naming(img_path.name):
            errors.append(f"❌ Invalid naming: {img_path.name}")
    
    # Check for orphaned markdown files
    for stem, md_path in markdowns.items():
        if stem not in images:
            errors.append(f"❌ Orphaned markdown (no image): {md_path.name}")
        
        # Check naming convention
        if not validate_naming(md_path.name):
            errors.append(f"❌ Invalid naming: {md_path.name}")
    
    # Print results
    print("=" * 50)
    print("DIAGRAM/MARKDOWN SYNC VALIDATION")
    print("=" * 50)
    print(f"Images found: {len(images)}")
    print(f"Markdown files found: {len(markdowns)}")
    print(f"Matched pairs: {len(set(images.keys()) & set(markdowns.keys()))}")
    print()
    
    if errors:
        print("ERRORS:")
        for error in errors:
            print(f"  {error}")
        print()
    
    if warnings:
        print("WARNINGS:")
        for warning in warnings:
            print(f"  {warning}")
        print()
    
    if not errors and not warnings:
        print("✅ All checks passed!")
        print()
        sys.exit(0)
    elif errors:
        print(f"❌ Validation failed with {len(errors)} error(s)")
        sys.exit(1)
    else:
        print(f"⚠️  Validation passed with {len(warnings)} warning(s)")
        sys.exit(0)

if __name__ == "__main__":
    main()
