"""
PyInstaller build script for KVG RGB Installer
Builds a standalone Windows installer executable
"""
import PyInstaller.__main__
import sys

PyInstaller.__main__.run([
    'installer.py',
    '--name=KVG_RGB_Installer',
    '--onefile',
    '--windowed',
    '--icon=NONE',
    '--clean',
    '--noconfirm',
])
