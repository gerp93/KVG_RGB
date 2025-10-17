"""
KVG RGB Controller - Settings & Installer
Comprehensive management tool for KVG RGB Controller on Windows
"""
import sys
import subprocess
import os
from pathlib import Path
import tkinter as tk
from tkinter import messagebox, scrolledtext, ttk, filedialog
import threading
import winreg


class RGBControllerManager:
    def __init__(self, root):
        self.root = root
        self.root.title("KVG RGB Controller - Settings & Installer")
        self.root.geometry("700x600")
        self.root.resizable(False, False)
        
        # Find Python executable
        self.python_exe = self.find_python()
        
        # Find the wheel file
        self.wheel_file = self.find_wheel_file()
        
        # Check installation status
        self.is_installed = self.check_installation()
        
        # Create UI
        self.create_ui()
        
        # Initial status check
        self.refresh_status()
    
    def create_ui(self):
        """Create the main UI"""
        # Header
        header = tk.Label(
            self.root, 
            text="🌈 KVG RGB Controller Manager",
            font=("Arial", 20, "bold"),
            fg="#4A90E2"
        )
        header.pack(pady=15)
        
        # Notebook (tabs)
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill="both", expand=True, padx=10, pady=5)
        
        # Tab 1: Installation
        self.install_tab = tk.Frame(self.notebook)
        self.notebook.add(self.install_tab, text="Installation")
        self.create_install_tab()
        
        # Tab 2: Settings
        self.settings_tab = tk.Frame(self.notebook)
        self.notebook.add(self.settings_tab, text="Settings")
        self.create_settings_tab()
        
        # Tab 3: About
        self.about_tab = tk.Frame(self.notebook)
        self.notebook.add(self.about_tab, text="About")
        self.create_about_tab()
        
        # Status bar
        self.status_bar = tk.Label(
            self.root,
            text="Ready",
            relief=tk.SUNKEN,
            anchor="w",
            bg="#f0f0f0"
        )
        self.status_bar.pack(side="bottom", fill="x")
    
    def create_install_tab(self):
        """Create installation tab"""
        # Status frame
        status_frame = tk.LabelFrame(self.install_tab, text="System Status", padx=10, pady=10)
        status_frame.pack(pady=10, padx=10, fill="x")
        
        self.python_status_label = tk.Label(status_frame, text="🔍 Checking Python...", anchor="w")
        self.python_status_label.pack(fill="x", pady=2)
        
        self.install_status_label = tk.Label(status_frame, text="🔍 Checking installation...", anchor="w")
        self.install_status_label.pack(fill="x", pady=2)
        
        self.version_label = tk.Label(status_frame, text="", anchor="w")
        self.version_label.pack(fill="x", pady=2)
        
        # Action buttons frame
        action_frame = tk.Frame(self.install_tab)
        action_frame.pack(pady=10)
        
        self.install_btn = tk.Button(
            action_frame,
            text="📦 Install / Update",
            command=self.install_package,
            bg="#4CAF50",
            fg="white",
            font=("Arial", 11, "bold"),
            padx=20,
            pady=10,
            width=20
        )
        self.install_btn.grid(row=0, column=0, padx=5)
        
        self.uninstall_btn = tk.Button(
            action_frame,
            text="🗑️ Uninstall",
            command=self.uninstall_package,
            bg="#f44336",
            fg="white",
            font=("Arial", 11, "bold"),
            padx=20,
            pady=10,
            width=20,
            state="disabled"
        )
        self.uninstall_btn.grid(row=0, column=1, padx=5)
        
        self.launch_btn = tk.Button(
            action_frame,
            text="🚀 Launch Web Interface",
            command=self.launch_web_interface,
            bg="#2196F3",
            fg="white",
            font=("Arial", 11, "bold"),
            padx=20,
            pady=10,
            width=20,
            state="disabled"
        )
        self.launch_btn.grid(row=1, column=0, columnspan=2, pady=10)
        
        # Log area
        log_frame = tk.LabelFrame(self.install_tab, text="Installation Log", padx=5, pady=5)
        log_frame.pack(pady=10, padx=10, fill="both", expand=True)
        
        self.log_text = scrolledtext.ScrolledText(
            log_frame,
            height=10,
            wrap=tk.WORD,
            font=("Consolas", 9)
        )
        self.log_text.pack(fill="both", expand=True)
        self.log_text.config(state="disabled")
    
    def create_settings_tab(self):
        """Create settings tab"""
        # Autostart section
        autostart_frame = tk.LabelFrame(self.settings_tab, text="Startup Settings", padx=15, pady=15)
        autostart_frame.pack(pady=10, padx=10, fill="x")
        
        self.autostart_var = tk.BooleanVar()
        self.autostart_check = tk.Checkbutton(
            autostart_frame,
            text="🚀 Start RGB Controller automatically when Windows starts",
            variable=self.autostart_var,
            command=self.toggle_autostart,
            font=("Arial", 10),
            state="disabled"
        )
        self.autostart_check.pack(anchor="w", pady=5)
        
        self.autostart_status_label = tk.Label(
            autostart_frame,
            text="Install the application first to enable autostart",
            fg="gray",
            font=("Arial", 9, "italic")
        )
        self.autostart_status_label.pack(anchor="w", padx=20)
        
        # Shortcut section
        shortcut_frame = tk.LabelFrame(self.settings_tab, text="Desktop Shortcut", padx=15, pady=15)
        shortcut_frame.pack(pady=10, padx=10, fill="x")
        
        tk.Label(
            shortcut_frame,
            text="Create a desktop shortcut to launch the web interface:",
            font=("Arial", 10)
        ).pack(anchor="w", pady=5)
        
        location_frame = tk.Frame(shortcut_frame)
        location_frame.pack(fill="x", pady=5)
        
        tk.Label(location_frame, text="Location:", font=("Arial", 9)).pack(side="left", padx=(0, 5))
        
        self.shortcut_location = tk.StringVar(value=str(Path.home() / "Desktop"))
        self.shortcut_entry = tk.Entry(
            location_frame,
            textvariable=self.shortcut_location,
            font=("Arial", 9),
            width=40,
            state="disabled"
        )
        self.shortcut_entry.pack(side="left", padx=5)
        
        self.browse_btn = tk.Button(
            location_frame,
            text="📁 Browse",
            command=self.browse_shortcut_location,
            state="disabled"
        )
        self.browse_btn.pack(side="left", padx=5)
        
        shortcut_buttons = tk.Frame(shortcut_frame)
        shortcut_buttons.pack(pady=10)
        
        self.create_shortcut_btn = tk.Button(
            shortcut_buttons,
            text="➕ Create Shortcut",
            command=self.create_desktop_shortcut,
            bg="#4CAF50",
            fg="white",
            padx=15,
            pady=5,
            state="disabled"
        )
        self.create_shortcut_btn.pack(side="left", padx=5)
        
        self.remove_shortcut_btn = tk.Button(
            shortcut_buttons,
            text="➖ Remove Shortcut",
            command=self.remove_desktop_shortcut,
            bg="#ff9800",
            fg="white",
            padx=15,
            pady=5,
            state="disabled"
        )
        self.remove_shortcut_btn.pack(side="left", padx=5)
        
        self.shortcut_status_label = tk.Label(
            shortcut_frame,
            text="Install the application first to create shortcuts",
            fg="gray",
            font=("Arial", 9, "italic")
        )
        self.shortcut_status_label.pack(pady=5)
        
        # Data location
        data_frame = tk.LabelFrame(self.settings_tab, text="Data Location", padx=15, pady=15)
        data_frame.pack(pady=10, padx=10, fill="x")
        
        data_path = Path.home() / ".kvg_rgb"
        tk.Label(
            data_frame,
            text=f"Configuration and database stored in:\n{data_path}",
            font=("Arial", 9),
            justify="left"
        ).pack(anchor="w")
        
        tk.Button(
            data_frame,
            text="📂 Open Data Folder",
            command=lambda: os.startfile(data_path) if data_path.exists() else messagebox.showinfo("Info", "Data folder will be created on first run"),
            padx=10,
            pady=5
        ).pack(anchor="w", pady=5)
    
    def create_about_tab(self):
        """Create about tab"""
        about_frame = tk.Frame(self.about_tab)
        about_frame.pack(expand=True, pady=20)
        
        tk.Label(
            about_frame,
            text="🌈 KVG RGB Controller",
            font=("Arial", 18, "bold"),
            fg="#4A90E2"
        ).pack(pady=10)
        
        tk.Label(
            about_frame,
            text="OpenRGB Controller with Web Interface",
            font=("Arial", 11)
        ).pack(pady=5)
        
        info_text = """
This application allows you to control RGB lighting
through OpenRGB with an easy-to-use web interface.

Features:
• Web-based GUI for RGB control
• Command-line interface (CLI)
• Effect presets and custom scenes
• Persistent settings across sessions
• Windows startup integration

Commands:
• kvg-rgb web - Start web interface
• kvg-rgb cli - Interactive CLI mode
• kvg-rgb autostart --enable - Enable autostart
• kvg-rgb --help - Show all commands
"""
        
        tk.Label(
            about_frame,
            text=info_text,
            font=("Arial", 9),
            justify="left",
            bg="#f5f5f5",
            padx=20,
            pady=15
        ).pack(pady=10)
        
        tk.Label(
            about_frame,
            text="GitHub: gerp93/KVG_RGB",
            font=("Arial", 9),
            fg="blue",
            cursor="hand2"
        ).pack()
    
    def find_python(self):
        """Find Python executable"""
        # Try common Python commands
        for cmd in ["python", "python3", "py"]:
            try:
                result = subprocess.run(
                    [cmd, "--version"],
                    capture_output=True,
                    text=True,
                    shell=True,
                    timeout=5
                )
                if result.returncode == 0:
                    # Get full path
                    path_result = subprocess.run(
                        [cmd, "-c", "import sys; print(sys.executable)"],
                        capture_output=True,
                        text=True,
                        shell=True,
                        timeout=5
                    )
                    if path_result.returncode == 0:
                        return path_result.stdout.strip()
            except:
                continue
        
        # Try Windows registry
        try:
            key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Python\PythonCore")
            i = 0
            while True:
                try:
                    version = winreg.EnumKey(key, i)
                    version_key = winreg.OpenKey(key, f"{version}\\InstallPath")
                    path = winreg.QueryValue(version_key, None)
                    python_exe = Path(path) / "python.exe"
                    if python_exe.exists():
                        return str(python_exe)
                    i += 1
                except:
                    break
        except:
            pass
        
        return None
    
    def find_wheel_file(self):
        """Find the wheel file bundled with the installer or in the same directory"""
        # Check if running as PyInstaller bundle
        if getattr(sys, '_MEIPASS', None):
            bundle_dir = Path(sys._MEIPASS)
            wheel_files = list(bundle_dir.glob("kvg_rgb-*.whl"))
            if wheel_files:
                return str(wheel_files[0])
        
        # Check same directory as script
        script_dir = Path(__file__).parent
        wheel_files = list(script_dir.glob("kvg_rgb-*.whl"))
        if wheel_files:
            return str(wheel_files[0])
        
        return None
    
    def check_installation(self):
        """Check if kvg-rgb is installed"""
        if not self.python_exe:
            return False
        
        try:
            result = subprocess.run(
                [self.python_exe, "-m", "pip", "show", "kvg-rgb"],
                capture_output=True,
                text=True,
                timeout=10
            )
            return result.returncode == 0
        except:
            return False
    
    def get_installed_version(self):
        """Get installed version"""
        if not self.python_exe:
            return None
        
        try:
            result = subprocess.run(
                [self.python_exe, "-m", "pip", "show", "kvg-rgb"],
                capture_output=True,
                text=True,
                timeout=10
            )
            if result.returncode == 0:
                for line in result.stdout.split('\n'):
                    if line.startswith('Version:'):
                        return line.split(':', 1)[1].strip()
        except:
            pass
        
        return None
    
    def check_autostart(self):
        """Check if autostart is enabled"""
        startup_folder = Path(os.environ.get('APPDATA')) / 'Microsoft' / 'Windows' / 'Start Menu' / 'Programs' / 'Startup'
        shortcut_path = startup_folder / 'KVG RGB Controller.lnk'
        return shortcut_path.exists()
    
    def refresh_status(self):
        """Refresh all status indicators"""
        # Check Python
        if self.python_exe:
            self.python_status_label.config(
                text=f"✅ Python found: {self.python_exe}",
                fg="green"
            )
        else:
            self.python_status_label.config(
                text="❌ Python not found! Please install Python first.",
                fg="red"
            )
            self.install_btn.config(state="disabled")
            return
        
        # Check installation
        self.is_installed = self.check_installation()
        version = self.get_installed_version()
        
        if self.is_installed:
            self.install_status_label.config(
                text="✅ KVG RGB Controller is installed",
                fg="green"
            )
            if version:
                self.version_label.config(
                    text=f"📦 Version: {version}",
                    fg="blue"
                )
            self.uninstall_btn.config(state="normal")
            self.launch_btn.config(state="normal")
            self.autostart_check.config(state="normal")
            self.shortcut_entry.config(state="normal")
            self.browse_btn.config(state="normal")
            self.create_shortcut_btn.config(state="normal")
            self.remove_shortcut_btn.config(state="normal")
            self.autostart_status_label.config(text="")
            self.shortcut_status_label.config(text="")
            
            # Check autostart status
            if self.check_autostart():
                self.autostart_var.set(True)
                self.autostart_status_label.config(
                    text="✅ Autostart is enabled",
                    fg="green"
                )
            else:
                self.autostart_var.set(False)
                self.autostart_status_label.config(
                    text="ℹ️ Autostart is disabled",
                    fg="gray"
                )
        else:
            self.install_status_label.config(
                text="⚠️ KVG RGB Controller is not installed",
                fg="orange"
            )
            self.version_label.config(text="")
            self.uninstall_btn.config(state="disabled")
            self.launch_btn.config(state="disabled")
            self.autostart_check.config(state="disabled")
            self.shortcut_entry.config(state="disabled")
            self.browse_btn.config(state="disabled")
            self.create_shortcut_btn.config(state="disabled")
            self.remove_shortcut_btn.config(state="disabled")
        
        # Check if wheel file is available
        if not self.wheel_file and not self.is_installed:
            self.install_btn.config(state="disabled")
            self.install_status_label.config(
                text="❌ Installation file not found!",
                fg="red"
            )
    
    def log_message(self, message):
        """Add message to log"""
        self.log_text.config(state="normal")
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.see(tk.END)
        self.log_text.config(state="disabled")
        self.root.update()
    
    def install_package(self):
        """Install or update the package"""
        if not self.wheel_file:
            messagebox.showerror(
                "Error",
                "Installation file not found!\n\n"
                "Please download the installer again."
            )
            return
        
        response = messagebox.askyesno(
            "Confirm Installation",
            "This will install or update KVG RGB Controller.\n\n"
            "Any running instances will be closed.\n\n"
            "Continue?"
        )
        
        if not response:
            return
        
        def install_thread():
            try:
                self.install_btn.config(state="disabled")
                self.uninstall_btn.config(state="disabled")
                self.status_bar.config(text="Installing...")
                
                self.log_message("\n" + "="*50)
                self.log_message("Starting installation...")
                self.log_message("="*50)
                
                # Close running instances
                self.log_message("\n🔍 Checking for running instances...")
                try:
                    subprocess.run(
                        ["taskkill", "/F", "/IM", "kvg-rgb.exe"],
                        capture_output=True,
                        timeout=5
                    )
                    self.log_message("✓ Closed running instances")
                except:
                    self.log_message("ℹ️ No running instances found")
                
                # Install
                self.log_message(f"\n📦 Installing from: {Path(self.wheel_file).name}")
                
                result = subprocess.run(
                    [
                        self.python_exe, "-m", "pip", "install",
                        "--upgrade", "--force-reinstall",
                        self.wheel_file
                    ],
                    capture_output=True,
                    text=True,
                    timeout=120
                )
                
                self.log_message(result.stdout)
                
                if result.returncode == 0:
                    self.log_message("\n" + "="*50)
                    self.log_message("✅ Installation successful!")
                    self.log_message("="*50)
                    
                    self.refresh_status()
                    self.status_bar.config(text="Installation complete!")
                    
                    # Ask about shortcuts
                    if messagebox.askyesno(
                        "Create Shortcuts?",
                        "Installation successful!\n\n"
                        "Would you like to create a desktop shortcut?"
                    ):
                        self.create_desktop_shortcut()
                    
                    if messagebox.askyesno(
                        "Enable Autostart?",
                        "Would you like to start RGB Controller automatically when Windows starts?"
                    ):
                        self.autostart_var.set(True)
                        self.toggle_autostart()
                    
                else:
                    self.log_message("\n❌ Installation failed!")
                    self.log_message(result.stderr)
                    self.status_bar.config(text="Installation failed")
                    messagebox.showerror("Error", "Installation failed. Check the log for details.")
            
            except Exception as e:
                self.log_message(f"\n❌ ERROR: {e}")
                self.status_bar.config(text="Error during installation")
                messagebox.showerror("Error", f"Installation failed:\n{e}")
            
            finally:
                self.install_btn.config(state="normal")
                self.refresh_status()
        
        thread = threading.Thread(target=install_thread, daemon=True)
        thread.start()
    
    def uninstall_package(self):
        """Uninstall the package"""
        response = messagebox.askyesno(
            "Confirm Uninstall",
            "This will remove KVG RGB Controller from your system.\n\n"
            "Your settings and data in ~/.kvg_rgb will be preserved.\n\n"
            "Continue?"
        )
        
        if not response:
            return
        
        def uninstall_thread():
            try:
                self.install_btn.config(state="disabled")
                self.uninstall_btn.config(state="disabled")
                self.status_bar.config(text="Uninstalling...")
                
                self.log_message("\n" + "="*50)
                self.log_message("Starting uninstallation...")
                self.log_message("="*50)
                
                # Close running instances
                self.log_message("\n🔍 Checking for running instances...")
                try:
                    subprocess.run(
                        ["taskkill", "/F", "/IM", "kvg-rgb.exe"],
                        capture_output=True,
                        timeout=5
                    )
                    self.log_message("✓ Closed running instances")
                except:
                    self.log_message("ℹ️ No running instances found")
                
                # Remove autostart if enabled
                if self.check_autostart():
                    self.log_message("\n🗑️ Removing autostart...")
                    self.autostart_var.set(False)
                    self.toggle_autostart()
                
                # Uninstall
                self.log_message(f"\n🗑️ Uninstalling kvg-rgb...")
                
                result = subprocess.run(
                    [self.python_exe, "-m", "pip", "uninstall", "-y", "kvg-rgb"],
                    capture_output=True,
                    text=True,
                    timeout=60
                )
                
                self.log_message(result.stdout)
                
                if result.returncode == 0:
                    self.log_message("\n" + "="*50)
                    self.log_message("✅ Uninstallation successful!")
                    self.log_message("="*50)
                    
                    self.refresh_status()
                    self.status_bar.config(text="Uninstallation complete")
                    
                    messagebox.showinfo(
                        "Uninstall Complete",
                        "KVG RGB Controller has been uninstalled.\n\n"
                        "Your settings in ~/.kvg_rgb have been preserved."
                    )
                else:
                    self.log_message("\n❌ Uninstallation failed!")
                    self.log_message(result.stderr)
                    self.status_bar.config(text="Uninstallation failed")
                    messagebox.showerror("Error", "Uninstallation failed. Check the log for details.")
            
            except Exception as e:
                self.log_message(f"\n❌ ERROR: {e}")
                self.status_bar.config(text="Error during uninstallation")
                messagebox.showerror("Error", f"Uninstallation failed:\n{e}")
            
            finally:
                self.install_btn.config(state="normal")
                self.refresh_status()
        
        thread = threading.Thread(target=uninstall_thread, daemon=True)
        thread.start()
    
    def launch_web_interface(self):
        """Launch the web interface"""
        try:
            self.status_bar.config(text="Launching web interface...")
            self.log_message("\n🚀 Launching web interface...")
            
            # Launch in background
            subprocess.Popen(
                [self.python_exe, "-m", "kvg_rgb.cli", "web"],
                creationflags=subprocess.CREATE_NEW_CONSOLE
            )
            
            self.log_message("✅ Web interface started in new window")
            self.status_bar.config(text="Web interface launched")
            
            messagebox.showinfo(
                "Launched",
                "Web interface has been started!\n\n"
                "Check the new console window for the server URL\n"
                "(usually http://localhost:5000)"
            )
            
        except Exception as e:
            self.log_message(f"❌ Failed to launch: {e}")
            self.status_bar.config(text="Launch failed")
            messagebox.showerror("Error", f"Failed to launch web interface:\n{e}")
    
    def toggle_autostart(self):
        """Enable or disable autostart"""
        try:
            if self.autostart_var.get():
                # Enable autostart
                self.log_message("\n🔧 Enabling autostart...")
                result = subprocess.run(
                    [self.python_exe, "-m", "kvg_rgb.cli", "autostart", "--enable"],
                    capture_output=True,
                    text=True,
                    timeout=10
                )
                
                if result.returncode == 0:
                    self.log_message("✅ Autostart enabled")
                    self.autostart_status_label.config(
                        text="✅ Autostart is enabled",
                        fg="green"
                    )
                    self.status_bar.config(text="Autostart enabled")
                else:
                    raise Exception(result.stderr)
            else:
                # Disable autostart
                self.log_message("\n🔧 Disabling autostart...")
                result = subprocess.run(
                    [self.python_exe, "-m", "kvg_rgb.cli", "autostart", "--disable"],
                    capture_output=True,
                    text=True,
                    timeout=10
                )
                
                if result.returncode == 0:
                    self.log_message("✅ Autostart disabled")
                    self.autostart_status_label.config(
                        text="ℹ️ Autostart is disabled",
                        fg="gray"
                    )
                    self.status_bar.config(text="Autostart disabled")
                else:
                    raise Exception(result.stderr)
        
        except Exception as e:
            self.log_message(f"❌ Failed to toggle autostart: {e}")
            # Revert checkbox
            self.autostart_var.set(not self.autostart_var.get())
            messagebox.showerror("Error", f"Failed to change autostart setting:\n{e}")
    
    def browse_shortcut_location(self):
        """Browse for shortcut location"""
        folder = filedialog.askdirectory(
            title="Select Shortcut Location",
            initialdir=self.shortcut_location.get()
        )
        if folder:
            self.shortcut_location.set(folder)
    
    def create_desktop_shortcut(self):
        """Create a desktop shortcut"""
        try:
            location = Path(self.shortcut_location.get())
            if not location.exists():
                messagebox.showerror("Error", f"Location does not exist:\n{location}")
                return
            
            shortcut_name = "KVG RGB Controller.lnk"
            shortcut_path = location / shortcut_name
            
            self.log_message(f"\n🔧 Creating shortcut at: {shortcut_path}")
            
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
                raise Exception(result.stderr)
            
            if shortcut_path.exists():
                self.log_message(f"✅ Shortcut created successfully!")
                self.shortcut_status_label.config(
                    text=f"✅ Shortcut exists at: {shortcut_name}",
                    fg="green"
                )
                self.status_bar.config(text="Shortcut created")
                messagebox.showinfo(
                    "Success",
                    f"Desktop shortcut created successfully!\n\n"
                    f"Location: {shortcut_path}"
                )
            else:
                raise Exception("Shortcut file was not created")
        
        except Exception as e:
            self.log_message(f"❌ Failed to create shortcut: {e}")
            self.status_bar.config(text="Shortcut creation failed")
            messagebox.showerror("Error", f"Failed to create shortcut:\n{e}")
    
    def remove_desktop_shortcut(self):
        """Remove desktop shortcut"""
        try:
            location = Path(self.shortcut_location.get())
            shortcut_path = location / "KVG RGB Controller.lnk"
            
            if shortcut_path.exists():
                self.log_message(f"\n🗑️ Removing shortcut: {shortcut_path}")
                shortcut_path.unlink()
                self.log_message("✅ Shortcut removed")
                self.shortcut_status_label.config(
                    text="ℹ️ Shortcut has been removed",
                    fg="gray"
                )
                self.status_bar.config(text="Shortcut removed")
                messagebox.showinfo("Success", "Shortcut removed successfully!")
            else:
                messagebox.showinfo("Info", "Shortcut does not exist at this location.")
        
        except Exception as e:
            self.log_message(f"❌ Failed to remove shortcut: {e}")
            messagebox.showerror("Error", f"Failed to remove shortcut:\n{e}")


def main():
    root = tk.Tk()
    app = RGBControllerManager(root)
    root.mainloop()


if __name__ == "__main__":
    main()
