#!/usr/bin/env python3
"""
Build script for creating platform-specific executables
"""

import subprocess
import sys
import shutil
from pathlib import Path
import os

def clean_build_dirs():
    """Remove old build directories"""
    dirs_to_remove = ['build', 'dist']
    for dir_name in dirs_to_remove:
        if Path(dir_name).exists():
            shutil.rmtree(dir_name)
            print(f"Cleaned {dir_name}/")

def build_executable():
    """Build the executable for current platform"""
    print(f"Building for {sys.platform}...")
    
    # Clean old builds
    clean_build_dirs()
    
    # Create assets directory if it doesn't exist
    Path('assets').mkdir(exist_ok=True)
    
    # PyInstaller command
    cmd = [
        sys.executable, '-m', 'PyInstaller',
        '--clean',
        '--noconfirm',
        'income_summary.spec'
    ]
    
    # Run PyInstaller
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.returncode == 0:
        print("✓ Build completed successfully!")
        
        # Show output location
        if sys.platform == 'darwin':
            app_path = Path('dist/IncomeSummaryGenerator.app')
            if app_path.exists():
                print(f"\n✓ macOS app created: {app_path}")
                print("\nTo install:")
                print(f"1. Drag {app_path} to your Applications folder")
                print("2. Right-click and select 'Open' for first launch")
                
        elif sys.platform == 'win32':
            exe_path = Path('dist/IncomeSummaryGenerator.exe')
            if exe_path.exists():
                print(f"\n✓ Windows executable created: {exe_path}")
                print("\nThe .exe file is portable and can be run from anywhere")
        
        else:
            exe_path = Path('dist/IncomeSummaryGenerator')
            if exe_path.exists():
                print(f"\n✓ Executable created: {exe_path}")
    else:
        print("✗ Build failed!")
        print("Error output:")
        print(result.stderr)
        return False
    
    return True

def create_macos_runner():
    """Create a simple runner script for macOS"""
    runner_content = '''#!/bin/bash
# Income Summary Generator Launcher

# Get the directory of this script
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Change to the app directory
cd "$DIR"

# Run the CLI version
./venv/bin/python src/income_summary_cli.py
'''
    
    runner_path = Path('IncomeSummaryGenerator.command')
    runner_path.write_text(runner_content)
    os.chmod(runner_path, 0o755)
    
    print(f"\n✓ Created macOS launcher: {runner_path}")
    print("Double-click this file to run the app on macOS")

def main():
    print("=" * 60)
    print("Income Summary Generator - Build Script")
    print("=" * 60)
    
    # Check if PyInstaller is installed
    try:
        import PyInstaller
        print(f"✓ PyInstaller {PyInstaller.__version__} found")
    except ImportError:
        print("✗ PyInstaller not found. Installing...")
        subprocess.run([sys.executable, '-m', 'pip', 'install', 'pyinstaller'])
    
    # For macOS, also create a simple launcher
    if sys.platform == 'darwin':
        create_macos_runner()
    
    # Build the executable
    print(f"\nBuilding executable for {sys.platform}...")
    if build_executable():
        print("\n✓ Build completed successfully!")
    else:
        print("\n✗ Build failed!")
        sys.exit(1)

if __name__ == "__main__":
    main()