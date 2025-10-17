"""
Complete Release Build Script
Builds both the Python wheel and Windows installer executable
"""
import subprocess
import sys
import os
import shutil
import time

def clean_build_artifacts():
    """Clean up old build artifacts"""
    print("🧹 Cleaning build artifacts...")
    dirs_to_clean = ['build', 'kvg_rgb.egg-info', 'dist/*.tar.gz']
    
    for dir_name in ['build', 'kvg_rgb.egg-info']:
        if os.path.exists(dir_name):
            try:
                shutil.rmtree(dir_name)
                print(f"   ✓ Removed {dir_name}/")
            except Exception as e:
                print(f"   ⚠️ Could not remove {dir_name}: {e}")
    
    # Remove tar.gz files but keep .whl and .exe
    if os.path.exists('dist'):
        for file in os.listdir('dist'):
            if file.endswith('.tar.gz'):
                try:
                    os.remove(os.path.join('dist', file))
                    print(f"   ✓ Removed dist/{file}")
                except Exception as e:
                    print(f"   ⚠️ Could not remove {file}: {e}")
    print()

def build_wheel():
    """Build the Python wheel package"""
    print("📦 Building Python wheel...")
    result = subprocess.run([sys.executable, '-m', 'build'], capture_output=True, text=True)
    
    if result.returncode == 0:
        print("   ✅ Wheel built successfully!")
        # Find and print wheel file
        for file in os.listdir('dist'):
            if file.endswith('.whl'):
                size = os.path.getsize(os.path.join('dist', file)) / 1024
                print(f"   📄 {file} ({size:.2f} KB)")
        return True
    else:
        print("   ❌ Wheel build failed!")
        print(result.stderr)
        return False

def build_installer():
    """Build the Windows installer executable"""
    print("\n🖥️ Building Windows installer...")
    
    # Try to remove old installer
    old_installer = 'dist/KVG_RGB_Installer.exe'
    if os.path.exists(old_installer):
        print("   🔄 Removing old installer...")
        for attempt in range(3):
            try:
                os.remove(old_installer)
                print("   ✓ Old installer removed")
                break
            except:
                if attempt < 2:
                    print(f"   ⏳ Waiting... (attempt {attempt + 1}/3)")
                    time.sleep(2)
                else:
                    print("   ⚠️ Could not remove old installer - it may be running")
                    print("   Please close KVG_RGB_Installer.exe and run: python build_installer.py")
                    return False
    
    result = subprocess.run([sys.executable, 'build_installer.py'], capture_output=True, text=True)
    
    if result.returncode == 0 and os.path.exists(old_installer):
        size = os.path.getsize(old_installer) / (1024 * 1024)
        print(f"   ✅ Installer built successfully!")
        print(f"   📄 KVG_RGB_Installer.exe ({size:.2f} MB)")
        return True
    else:
        print("   ❌ Installer build failed!")
        if result.stderr:
            print(result.stderr)
        return False

def main():
    """Main build process"""
    print("=" * 60)
    print("🚀 KVG RGB - Complete Release Build")
    print("=" * 60)
    print()
    
    # Step 1: Clean
    clean_build_artifacts()
    
    # Step 2: Build wheel
    if not build_wheel():
        print("\n❌ Build failed at wheel stage")
        return 1
    
    # Step 3: Build installer
    if not build_installer():
        print("\n⚠️ Wheel built but installer failed")
        print("You can manually build the installer later with: python build_installer.py")
        return 1
    
    # Success!
    print("\n" + "=" * 60)
    print("✅ Release build complete!")
    print("=" * 60)
    print("\n📦 Distribution files ready in dist/:")
    print("   • kvg_rgb-X.X.X-py3-none-any.whl")
    print("   • KVG_RGB_Installer.exe")
    print("\n🎯 Next steps:")
    print("   1. Test the installer")
    print("   2. Create GitHub release with tag")
    print("   3. Upload both files to the release")
    print()
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
