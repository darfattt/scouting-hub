#!/usr/bin/env python3
"""
Fix All Scripts for New Project Structure
This script updates all scripts in the scripts/ folder to work with the new project structure.
"""

import os
import re

def fix_script_imports(script_path):
    """Fix imports in a script file to work with new project structure."""
    print(f"Fixing {script_path}...")
    
    with open(script_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check if already fixed
    if 'project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))' in content:
        print(f"  ✓ {script_path} already fixed")
        return
    
    # Add path setup after imports
    import_section = []
    lines = content.split('\n')
    
    # Find where to insert path setup
    insert_index = 0
    for i, line in enumerate(lines):
        if line.startswith('import ') or line.startswith('from '):
            insert_index = i + 1
        elif line.strip() == '' and insert_index > 0:
            break
    
    # Insert path setup
    path_setup = [
        '',
        '# Add src directory to Python path for imports',
        'project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))',
        'src_path = os.path.join(project_root, \'src\')',
        'sys.path.insert(0, project_root)',
        'sys.path.insert(0, src_path)',
        '',
        '# Change to project root directory',
        'os.chdir(project_root)'
    ]
    
    # Add sys import if not present
    if 'import sys' not in content:
        lines.insert(1, 'import sys')
        insert_index += 1
    
    # Insert path setup
    for i, setup_line in enumerate(path_setup):
        lines.insert(insert_index + i, setup_line)
    
    # Fix import statements
    new_lines = []
    for line in lines:
        # Fix rag_system imports
        if 'from rag_system import' in line:
            line = line.replace('from rag_system import', 'from core.rag_system import')
        
        # Fix vector store paths
        if 'vector_store' in line and 'storage/' not in line and 'exists(' in line:
            line = line.replace('"vector_store', '"storage/vector_store')
        
        new_lines.append(line)
    
    # Write back
    with open(script_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(new_lines))
    
    print(f"  ✓ Fixed {script_path}")

def main():
    """Fix all scripts in the scripts directory."""
    print("=" * 60)
    print("FIXING ALL SCRIPTS FOR NEW PROJECT STRUCTURE")
    print("=" * 60)
    
    scripts_dir = os.path.dirname(os.path.abspath(__file__))
    
    # List of scripts to fix (excluding this script)
    scripts_to_fix = [
        'build_gk_only.py',
        'build_goalkeeper_rag.py',
        'build_smart_rag.py',
        'check_setup.py',
        'setup_models.py'
    ]
    
    fixed_count = 0
    
    for script_name in scripts_to_fix:
        script_path = os.path.join(scripts_dir, script_name)
        if os.path.exists(script_path):
            try:
                fix_script_imports(script_path)
                fixed_count += 1
            except Exception as e:
                print(f"  ✗ Failed to fix {script_name}: {e}")
        else:
            print(f"  - {script_name} not found")
    
    print(f"\n✓ Fixed {fixed_count} scripts")
    print("\nAll scripts should now work with the new project structure!")
    print("\nNext steps:")
    print("1. Test the scripts to make sure they work")
    print("2. Run: python scripts/build_all_rag.py")
    print("3. Or run: python scripts/build_gk_only.py")

if __name__ == "__main__":
    main()
