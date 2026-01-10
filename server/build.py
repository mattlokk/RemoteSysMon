#!/usr/bin/env python3
"""
Build Script for RemoteSysMon
Creates distributable packages for Windows and Linux
"""

import os
import sys
import subprocess
import shutil
import platform


def get_platform():
    """Detect current platform"""
    system = platform.system().lower()
    if system == "linux":
        return "linux"
    elif system == "windows":
        return "windows"
    elif system == "darwin":
        return "macos"
    return "unknown"


def clean_build():
    """Clean previous build artifacts"""
    print("🧹 Cleaning previous builds...")
    dirs_to_clean = ['build', 'dist', '__pycache__']
    
    for dir_name in dirs_to_clean:
        if os.path.exists(dir_name):
            shutil.rmtree(dir_name)
            print(f"   Removed {dir_name}/")
    
    # Remove spec file
    if os.path.exists('main.spec'):
        os.remove('main.spec')
        print("   Removed main.spec")


def install_dependencies():
    """Install required packages"""
    print("📦 Installing dependencies...")
    subprocess.run([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'], 
                   check=True)


def build_linux():
    """Build for Linux"""
    print("🐧 Building for Linux...")
    
    # PyInstaller command for Linux
    cmd = [
        'pyinstaller',
        '--onefile',              # Single executable
        '--windowed',             # No console window
        '--name=RemoteSysMon',    # Output name
        '--add-data=core:core',   # Include core module
        '--add-data=gui:gui',     # Include gui module
        '--add-data=config.json:.',  # Include default config
        'main.py'
    ]
    
    # Add icon if available
    if os.path.exists('assets/icon.png'):
        cmd.extend(['--icon=assets/icon.png'])
    
    subprocess.run(cmd, check=True)
    
    print("✅ Linux build complete: dist/RemoteSysMon")
    print("\nTo create AppImage:")
    print("1. Download appimagetool")
    print("2. Create AppDir structure")
    print("3. Run: appimagetool AppDir RemoteSysMon.AppImage")


def build_windows():
    """Build for Windows"""
    print("🪟 Building for Windows...")
    
    # PyInstaller command for Windows
    cmd = [
        'pyinstaller',
        '--onefile',              # Single executable
        '--windowed',             # No console window
        '--name=RemoteSysMon',    # Output name
        '--add-data=core;core',   # Include core module (Windows uses ;)
        '--add-data=gui;gui',     # Include gui module
        '--add-data=config.json;.',  # Include default config
        'main.py'
    ]
    
    # Add icon if available
    if os.path.exists('assets/icon.ico'):
        cmd.extend(['--icon=assets/icon.ico'])
    
    subprocess.run(cmd, check=True)
    
    print("✅ Windows build complete: dist\\RemoteSysMon.exe")


def create_spec_file():
    """Create custom PyInstaller spec file for advanced configuration"""
    spec_content = """# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('core', 'core'),
        ('gui', 'gui'),
        ('config.json', '.'),
    ],
    hiddenimports=['PyQt6.sip'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='RemoteSysMon',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
"""
    
    with open('main.spec', 'w') as f:
        f.write(spec_content)
    
    print("📝 Created custom spec file: main.spec")


def main():
    """Main build process"""
    print("🔨 RemoteSysMon Build Script")
    print("=" * 50)
    
    # Detect platform
    current_platform = get_platform()
    print(f"Platform: {current_platform}")
    print()
    
    # Parse arguments
    if len(sys.argv) > 1:
        if sys.argv[1] == 'clean':
            clean_build()
            return
        elif sys.argv[1] == 'spec':
            create_spec_file()
            return
    
    # Build process
    try:
        # Clean previous builds
        clean_build()
        print()
        
        # Install dependencies
        install_dependencies()
        print()
        
        # Build for current platform
        if current_platform == "linux":
            build_linux()
        elif current_platform == "windows":
            build_windows()
        else:
            print(f"❌ Unsupported platform: {current_platform}")
            sys.exit(1)
        
        print()
        print("🎉 Build completed successfully!")
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Build failed: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
