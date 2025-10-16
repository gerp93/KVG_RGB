"""
Script to build standalone executable with PyInstaller
"""
import PyInstaller.__main__
import shutil
import os

# Clean previous builds
if os.path.exists('dist'):
    shutil.rmtree('dist')
if os.path.exists('build'):
    shutil.rmtree('build')

print("Building standalone executable...")
print("="*60)

# Build the executable
PyInstaller.__main__.run([
    'main.py',
    '--onefile',
    '--name=kvg-rgb',
    '--console',
    '--clean',
    # Add hidden imports for the package structure
    '--hidden-import=kvg_rgb',
    '--hidden-import=kvg_rgb.cli',
    '--hidden-import=kvg_rgb.core',
    # Add icon if you have one
    # '--icon=icon.ico',
])

print("\n" + "="*60)
print("Build complete!")
print("Executable location: dist\\kvg-rgb.exe")
print("="*60)
print("\nYou can now:")
print("1. Test it: .\\dist\\kvg-rgb.exe list")
print("2. Copy it to a folder in your PATH to use from anywhere")
print("3. Share the .exe with others (they don't need Python installed)")
