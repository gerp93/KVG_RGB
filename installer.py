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
    
    def find_wheel_file(self):
        """Find the .whl file in the same directory as this script"""
        if getattr(sys, 'frozen', False):
            # Running as compiled exe
            exe_dir = Path(sys.executable).parent
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
        # Check pip (more reliable than checking python)
        try:
            result = subprocess.run(
                ["pip", "--version"],
                capture_output=True,
                text=True,
                timeout=5
            )
            version = result.stdout.strip()
            self.python_status.config(text=f"✅ pip found: {version}", fg="green")
            self.log_message(f"pip check: {version}")
        except Exception as e:
            self.python_status.config(text="❌ pip not found in PATH", fg="red")
            self.log_message(f"ERROR: pip not found - {e}")
            self.log_message("Please ensure Python is installed with pip enabled")
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
                ["pip", "show", "kvg-rgb"],
                capture_output=True,
                text=True,
                timeout=5
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
                ["pip", "install", "--upgrade", "--force-reinstall", str(self.wheel_file)],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1
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


def main():
    root = tk.Tk()
    app = InstallerGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
