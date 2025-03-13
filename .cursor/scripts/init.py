#!/usr/bin/env python3
import os
import sys
import shutil
import argparse
from pathlib import Path

def parse_args():
    parser = argparse.ArgumentParser(description='Initialize a new project with Cursor rules')
    parser.add_argument('project_path', help='Path to the new project')
    parser.add_argument('--type', choices=['frontend', 'backend', 'fullstack'], 
                       default='fullstack', help='Type of project to initialize')
    parser.add_argument('--no-mysql', action='store_true', help='Skip MySQL setup')
    parser.add_argument('--no-ant', action='store_true', help='Skip Ant Design setup')
    return parser.parse_args()

def copy_rules(src_dir: Path, dest_dir: Path, project_type: str):
    """Copy relevant rules based on project type"""
    # Copy common rules
    if (src_dir / 'rules' / 'common').exists():
        shutil.copytree(src_dir / 'rules' / 'common', 
                       dest_dir / 'rules' / 'common')
    
    # Copy frontend rules
    if project_type in ['frontend', 'fullstack']:
        if (src_dir / 'rules' / 'frontend').exists():
            shutil.copytree(src_dir / 'rules' / 'frontend', 
                           dest_dir / 'rules' / 'frontend')
    
    # Copy backend rules
    if project_type in ['backend', 'fullstack']:
        if (src_dir / 'rules' / 'backend').exists():
            shutil.copytree(src_dir / 'rules' / 'backend', 
                           dest_dir / 'rules' / 'backend')

def main():
    args = parse_args()
    project_path = Path(args.project_path).resolve()
    
    # Create project directory if it doesn't exist
    project_path.mkdir(parents=True, exist_ok=True)
    
    # Create .cursor directory structure
    cursor_dir = project_path / '.cursor'
    cursor_dir.mkdir(exist_ok=True)
    
    # Copy rules and templates
    current_dir = Path(__file__).parent.parent
    copy_rules(current_dir, cursor_dir, args.type)
    
    # Copy config
    if (current_dir / 'config').exists():
        shutil.copytree(current_dir / 'config', cursor_dir / 'config', 
                       dirs_exist_ok=True)
    
    print(f"Project initialized at {project_path}")
    print(f"Project type: {args.type}")
    print("Configuration complete!")

if __name__ == "__main__":
    main() 