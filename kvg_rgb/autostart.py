"""
Windows autostart configuration helper
"""
import os
import sys
from pathlib import Path


def get_startup_folder():
    """Get Windows startup folder path"""
    appdata = os.getenv('APPDATA')
    if not appdata:
        return None
    return Path(appdata) / 'Microsoft' / 'Windows' / 'Start Menu' / 'Programs' / 'Startup'


def get_script_path():
    """Get the path to the startup batch file"""
    try:
        import kvg_rgb
        package_dir = Path(kvg_rgb.__file__).parent
        return package_dir / 'scripts' / 'start_kvg_rgb.bat'
    except ImportError:
        return None


def is_autostart_enabled():
    """Check if autostart is currently enabled"""
    startup_folder = get_startup_folder()
    if not startup_folder or not startup_folder.exists():
        return False
    
    shortcut_path = startup_folder / 'KVG RGB Controller.lnk'
    return shortcut_path.exists()


def create_startup_shortcut():
    """Create a shortcut in Windows startup folder using PowerShell"""
    startup_folder = get_startup_folder()
    script_path = get_script_path()
    
    if not startup_folder or not script_path:
        return False, "Could not locate required paths"
    
    if not script_path.exists():
        return False, f"Startup script not found at: {script_path}"
    
    if not startup_folder.exists():
        startup_folder.mkdir(parents=True, exist_ok=True)
    
    shortcut_path = startup_folder / 'KVG RGB Controller.lnk'
    
    # Use PowerShell to create the shortcut (works without pywin32)
    ps_command = f'''
    $WshShell = New-Object -ComObject WScript.Shell
    $Shortcut = $WshShell.CreateShortcut("{shortcut_path}")
    $Shortcut.TargetPath = "{script_path}"
    $Shortcut.WorkingDirectory = "{Path.home()}"
    $Shortcut.WindowStyle = 7
    $Shortcut.Description = "Start KVG RGB Controller"
    $Shortcut.Save()
    '''
    
    try:
        import subprocess
        result = subprocess.run(
            ['powershell', '-Command', ps_command],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if result.returncode == 0 and shortcut_path.exists():
            return True, str(shortcut_path)
        else:
            return False, f"PowerShell error: {result.stderr}"
    except Exception as e:
        return False, f"Error creating shortcut: {e}"


def remove_startup_shortcut():
    """Remove the startup shortcut"""
    startup_folder = get_startup_folder()
    if not startup_folder:
        return False, "Could not locate startup folder"
    
    shortcut_path = startup_folder / 'KVG RGB Controller.lnk'
    
    if shortcut_path.exists():
        try:
            shortcut_path.unlink()
            return True, "Autostart disabled"
        except Exception as e:
            return False, f"Error removing shortcut: {e}"
    else:
        return False, "Autostart was not enabled"


def prompt_autostart_setup():
    """Interactive prompt to set up autostart"""
    print("\n" + "="*60)
    print("  KVG RGB Controller - Autostart Configuration")
    print("="*60)
    
    if is_autostart_enabled():
        print("\n✅ Autostart is currently ENABLED")
        print("   The RGB controller starts automatically when you log in.")
        response = input("\nDisable autostart? [y/N]: ").strip().lower()
        
        if response == 'y':
            success, message = remove_startup_shortcut()
            if success:
                print(f"\n✅ {message}")
            else:
                print(f"\n❌ {message}")
        else:
            print("\n✓ Autostart remains enabled")
    else:
        print("\n❌ Autostart is currently DISABLED")
        print("   The RGB controller will NOT start automatically.")
        print("\nEnabling autostart will:")
        print("  • Start the web interface when you log in to Windows")
        print("  • Run minimized in the background")
        print("  • Restore your last RGB configuration")
        
        response = input("\nEnable autostart? [Y/n]: ").strip().lower()
        
        if response in ('', 'y', 'yes'):
            print("\n⏳ Creating startup shortcut...")
            success, message = create_startup_shortcut()
            
            if success:
                print(f"\n✅ Autostart enabled!")
                print(f"   Shortcut created at: {message}")
                print("\n   KVG RGB will start automatically when you log in.")
                print("   Run 'kvg-rgb autostart' again to disable it.")
            else:
                print(f"\n❌ Failed to enable autostart: {message}")
                print("\n   Manual setup instructions:")
                print("   1. Press Win+R, type: shell:startup")
                print(f"   2. Create a shortcut to: {get_script_path()}")
        else:
            print("\n✓ Autostart remains disabled")
    
    print("\n" + "="*60 + "\n")
