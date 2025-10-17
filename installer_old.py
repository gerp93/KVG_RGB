"""
KVG RGB Controller - Windows Installer
Simple GUI installer for Windows users who prefer not to use command line
"""
import sys
import subprocess
import os
from pathlib import Path
import tkinter as tk
from tkinter import messagebox, scrolledtext
import threading


class InstallerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("KVG RGB Controller Installer")
        self.root.geometry("600x500")
        self.root.resizable(False, False)
        
        # Find Python executable
        self.python_exe = self.find_python()
        
        # Find the wheel file in the same directory as the installer
        self.wheel_file = self.find_wheel_file()
        
        # Header
        header = tk.Label(
            root, 
            text="🌈 KVG RGB Controller",
            font=("Arial", 20, "bold"),
            fg="#4A90E2"
        )
        header.pack(pady=20)
        
        # Description
        desc = tk.Label(
            root,
            text="OpenRGB controller with web interface and CLI",
            font=("Arial", 10)
        )
        desc.pack()
        
        # Status frame
        status_frame = tk.Frame(root)
        status_frame.pack(pady=20, padx=20, fill="x")
        
        # Check pip
        self.python_status = tk.Label(status_frame, text="🔍 Checking pip...", anchor="w")
        self.python_status.pack(fill="x")
        
        # Check wheel file
        self.wheel_status = tk.Label(status_frame, text="🔍 Checking package...", anchor="w")
        self.wheel_status.pack(fill="x")
        
        # Check existing installation
        self.existing_status = tk.Label(status_frame, text="🔍 Checking existing installation...", anchor="w")
        self.existing_status.pack(fill="x")
        
        # Output log
        log_label = tk.Label(root, text="Installation Log:", font=("Arial", 10, "bold"))
        log_label.pack(pady=(20, 5), padx=20, anchor="w")
        
        self.log = scrolledtext.ScrolledText(root, height=10, state='disabled', bg="#f0f0f0")
        self.log.pack(pady=5, padx=20, fill="both", expand=True)
        
        # Button frame
        button_frame = tk.Frame(root)
        button_frame.pack(pady=20)
        
        self.install_btn = tk.Button(
            button_frame,
            text="Install / Upgrade",
            command=self.start_installation,
            bg="#4CAF50",
            fg="white",
            font=("Arial", 12, "bold"),
            width=15,
            height=2
        )
        self.install_btn.pack(side="left", padx=10)
        
        self.close_btn = tk.Button(
            button_frame,
            text="Close",
            command=root.quit,
            font=("Arial", 12),
            width=15,
            height=2
        )
        self.close_btn.pack(side="left", padx=10)
        
        # Perform initial checks
        self.root.after(100, self.perform_checks)
    
    def find_python(self):
        """Find Python executable in system"""
        # Try common Python commands and locations
        python_names = ['python', 'python3', 'py']
        
        for name in python_names:
            try:
                result = subprocess.run(
                    [name, '--version'],
                    capture_output=True,
                    text=True,
                    timeout=3,
                    shell=True
                )
                if result.returncode == 0:
                    return name
            except:
                continue
        
        # Try to find via registry (Windows)
        try:
            import winreg
            # Try HKEY_CURRENT_USER first
            for root_key in [winreg.HKEY_CURRENT_USER, winreg.HKEY_LOCAL_MACHINE]:
                try:
                    key = winreg.OpenKey(root_key, r"SOFTWARE\Python\PythonCore")
                    num_versions = winreg.QueryInfoKey(key)[0]
                    
                    for i in range(num_versions):
                        version = winreg.EnumKey(key, i)
                        try:
                            install_key = winreg.OpenKey(key, f"{version}\\InstallPath")
                            install_path = winreg.QueryValue(install_key, None)
                            python_exe = os.path.join(install_path, "python.exe")
                            if os.path.exists(python_exe):
                                return python_exe
                        except:
                            continue
                except:
                    continue
        except ImportError:
            pass
        
        return None
    
    def find_wheel_file(self):
        """Find the .whl file - check embedded resource first, then same directory"""
        # First check if we have an embedded wheel file (frozen exe)
        if getattr(sys, 'frozen', False):
            # Running as compiled exe - check for bundled wheel
            exe_dir = Path(sys.executable).parent
            temp_dir = Path(sys._MEIPASS) if hasattr(sys, '_MEIPASS') else exe_dir
            
            # Look in temp dir first (bundled resource)
            wheel_files = list(temp_dir.glob("kvg_rgb-*.whl"))
            if wheel_files:
                return wheel_files[0]
            
            # Fall back to exe directory
            wheel_files = list(exe_dir.glob("kvg_rgb-*.whl"))
            if wheel_files:
                return wheel_files[0]
        else:
            # Running as script
            exe_dir = Path(__file__).parent
            wheel_files = list(exe_dir.glob("kvg_rgb-*.whl"))
            if wheel_files:
                return wheel_files[0]
        
        return None
    
    def log_message(self, message):
        """Add message to log window"""
        self.log.config(state='normal')
        self.log.insert(tk.END, message + "\n")
        self.log.see(tk.END)
        self.log.config(state='disabled')
    
    def perform_checks(self):
        """Perform pre-installation checks"""
        # Check Python and pip
        if not self.python_exe:
            self.python_status.config(text="❌ Python not found", fg="red")
            self.log_message("ERROR: Could not find Python installation")
            self.log_message("Please install Python 3.7+ from https://python.org")
            self.log_message("Make sure to check 'Add Python to PATH' during installation")
            self.install_btn.config(state="disabled")
            return
        
        try:
            result = subprocess.run(
                [self.python_exe, "-m", "pip", "--version"],
                capture_output=True,
                text=True,
                timeout=10,
                shell=True
            )
            if result.returncode == 0:
                version = result.stdout.strip()
                self.python_status.config(text=f"✅ Python + pip found: {version}", fg="green")
                self.log_message(f"Python: {self.python_exe}")
                self.log_message(f"pip: {version}")
            else:
                raise Exception("pip module not available")
        except Exception as e:
            self.python_status.config(text="❌ pip not available", fg="red")
            self.log_message(f"ERROR: pip not found - {e}")
            self.log_message(f"Python found at: {self.python_exe}")
            self.log_message("Please reinstall Python with pip enabled")
            self.install_btn.config(state="disabled")
            return
        
        # Check wheel file
        if self.wheel_file and self.wheel_file.exists():
            self.wheel_status.config(text=f"✅ Package found: {self.wheel_file.name}", fg="green")
            self.log_message(f"Package: {self.wheel_file.name}")
        else:
            self.wheel_status.config(text="❌ Package file not found", fg="red")
            self.log_message("ERROR: No .whl file found in the same directory")
            self.install_btn.config(state="disabled")
            return
        
        # Check existing installation
        try:
            result = subprocess.run(
                [self.python_exe, "-m", "pip", "show", "kvg-rgb"],
                capture_output=True,
                text=True,
                timeout=10,
                shell=True
            )
            if result.returncode == 0:
                # Extract version
                for line in result.stdout.split('\n'):
                    if line.startswith('Version:'):
                        version = line.split(':', 1)[1].strip()
                        self.existing_status.config(text=f"⚠️ Version {version} installed (will upgrade)", fg="orange")
                        self.log_message(f"Existing installation: v{version}")
                        self.install_btn.config(text="Upgrade")
                        break
            else:
                self.existing_status.config(text="✅ No existing installation (fresh install)", fg="green")
                self.log_message("No existing installation found")
        except Exception as e:
            self.existing_status.config(text="❓ Could not check existing installation", fg="gray")
            self.log_message(f"Check skipped: {e}")
    
    def start_installation(self):
        """Start installation in a separate thread"""
        self.install_btn.config(state="disabled")
        self.close_btn.config(state="disabled")
        threading.Thread(target=self.install, daemon=True).start()
    
    def install(self):
        """Perform the installation"""
        self.log_message("\n" + "="*50)
        self.log_message("Starting installation...")
        self.log_message("="*50 + "\n")
        
        try:
            # Close any running instances
            self.log_message("Checking for running kvg-rgb processes...")
            subprocess.run(
                ["taskkill", "/IM", "kvg-rgb.exe", "/F", "/T"],
                capture_output=True,
                timeout=5
            )
            self.log_message("Closed any running instances\n")
            
            # Run pip install
            self.log_message(f"Installing {self.wheel_file.name}...")
            self.log_message("This may take a moment...\n")
            
            process = subprocess.Popen(
                [self.python_exe, "-m", "pip", "install", "--upgrade", "--force-reinstall", str(self.wheel_file)],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
                shell=True
            )
            
            # Stream output to log
            for line in process.stdout:
                self.log_message(line.rstrip())
            
            process.wait()
            
            if process.returncode == 0:
                self.log_message("\n" + "="*50)
                self.log_message("✅ Installation successful!")
                self.log_message("="*50 + "\n")
                self.log_message("You can now use 'kvg-rgb' from the command line")
                self.log_message("Or run 'kvg-rgb web' to start the web interface")
                
                # Ask if user wants to create a desktop shortcut
                create_shortcut = messagebox.askyesno(
                    "Create Desktop Shortcut?",
                    "Installation successful!\n\n"
                    "Would you like to create a desktop shortcut\n"
                    "to launch the RGB Controller web interface?"
                )
                
                if create_shortcut:
                    self.create_desktop_shortcut()
                else:
                    messagebox.showinfo(
                        "Success",
                        "KVG RGB Controller installed successfully!\n\n"
                        "Run 'kvg-rgb web' to start the web interface"
                    )
            else:
                self.log_message("\n❌ Installation failed!")
                messagebox.showerror("Error", "Installation failed. Check the log for details.")
        
        except Exception as e:
            self.log_message(f"\n❌ ERROR: {e}")
            messagebox.showerror("Error", f"Installation failed:\n{e}")
        
        finally:
            self.install_btn.config(state="normal")
            self.close_btn.config(state="normal")
    
    def create_desktop_shortcut(self):
        """Create a desktop shortcut to launch the web interface"""
        try:
            desktop = Path.home() / "Desktop"
            shortcut_name = "KVG RGB Controller.lnk"
            shortcut_path = desktop / shortcut_name
            
            # Escape paths for PowerShell
            shortcut_path_str = str(shortcut_path).replace("\\", "\\\\")
            python_exe_str = str(self.python_exe).replace("\\", "\\\\")
            working_dir_str = str(Path.home()).replace("\\", "\\\\")
            
            # PowerShell script to create shortcut
            ps_script = f"""
$WshShell = New-Object -ComObject WScript.Shell
$Shortcut = $WshShell.CreateShortcut('{shortcut_path_str}')
$Shortcut.TargetPath = '{python_exe_str}'
$Shortcut.Arguments = '-m kvg_rgb.cli web'
$Shortcut.WorkingDirectory = '{working_dir_str}'
$Shortcut.Description = 'Launch KVG RGB Controller Web Interface'
$Shortcut.Save()
"""
            
            result = subprocess.run(
                ["powershell", "-ExecutionPolicy", "Bypass", "-Command", ps_script],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode != 0:
                self.log_message(f"\n⚠️ PowerShell error: {result.stderr}")
            
            if shortcut_path.exists():
                self.log_message(f"\n✅ Desktop shortcut created: {shortcut_name}")
                messagebox.showinfo(
                    "Shortcut Created",
                    f"Desktop shortcut created successfully!\n\n"
                    f"Double-click '{shortcut_name}' on your desktop\n"
                    "to launch the RGB Controller."
                )
            else:
                raise Exception("Shortcut file was not created")
                
        except Exception as e:
            self.log_message(f"\n⚠️ Could not create desktop shortcut: {e}")
            messagebox.showwarning(
                "Shortcut Failed",
                f"Could not create desktop shortcut.\n\n"
                f"You can still run: kvg-rgb web"
            )


def main():
    root = tk.Tk()
    app = InstallerGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
