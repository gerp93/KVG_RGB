"""
PyInstaller build script for KVG RGB Installer
Builds a standalone Windows installer executable
"""
import PyInstaller.__main__
import sys
import os
import time

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

PyInstaller.__main__.run([
    'installer.py',
    '--name=KVG_RGB_Installer',
    '--onefile',
    '--windowed',
    '--icon=NONE',
    '--clean',
    '--noconfirm',
])
