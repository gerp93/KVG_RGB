"""
PyInstaller build script for KVG RGB Installer
Builds a standalone Windows installer executable with bundled wheel
"""
import PyInstaller.__main__
import sys
import os
import time
import glob

# Try to remove old installer if it exists
old_installer = 'dist/KVG_RGB_Installer.exe'
if os.path.exists(old_installer):
    try:
        os.remove(old_installer)
    except:
        # If locked, wait a bit and try again
        time.sleep(2)
        try:
            os.remove(old_installer)
        except:
            print(f"Warning: Could not remove {old_installer}, it may be in use")

# Find the wheel file to bundle
wheel_files = glob.glob('dist/kvg_rgb-*.whl')
if not wheel_files:
    print("ERROR: No wheel file found in dist/")
    print("Please run 'python -m build' first")
    sys.exit(1)

wheel_file = wheel_files[0]
print(f"Bundling wheel: {wheel_file}")

PyInstaller.__main__.run([
    'installer.py',
    '--name=KVG_RGB_Installer',
    '--onefile',
    '--windowed',
    '--icon=NONE',
    '--clean',
    '--noconfirm',
    f'--add-data={wheel_file};.',  # Bundle the wheel file
])
