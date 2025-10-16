#!/usr/bin/env python3
"""
Release script for KVG RGB Controller
Cross-platform release automation (Windows, Linux, macOS)
"""
import os
import sys
import subprocess
import shutil
import re
from pathlib import Path


def print_header(text):
    """Print a formatted header"""
    print()
    print("=" * 60)
    print(f"  {text}")
    print("=" * 60)
    print()


def print_step(step_num, text):
    """Print a formatted step"""
    print(f"\n\033[92mStep {step_num}: {text}...\033[0m")


def print_success(text):
    """Print success message"""
    print(f"\033[92m✓ {text}\033[0m")


def print_error(text):
    """Print error message"""
    print(f"\033[91m❌ {text}\033[0m")


def run_command(cmd, description, check=True):
    """Run a command and handle errors"""
    try:
        result = subprocess.run(
            cmd,
            shell=True,
            check=check,
            capture_output=True,
            text=True
        )
        return result.returncode == 0
    except subprocess.CalledProcessError as e:
        if check:
            print_error(f"Failed: {description}")
            print(f"Error: {e.stderr}")
            sys.exit(1)
        return False


def get_current_version():
    """Read current version from __init__.py"""
    init_file = Path("kvg_rgb") / "__init__.py"
    with open(init_file, "r") as f:
        content = f.read()
        match = re.search(r'__version__\s*=\s*["\']([^"\']+)["\']', content)
        if match:
            return match.group(1)
    return "unknown"


def main():
    """Main release process"""
    print_header("KVG RGB Controller Release Script")
    
    # Get current version
    version = get_current_version()
    print(f"\033[93mCurrent version: {version}\033[0m")
    
    # Step 1: Activate venv (informational - venv should already be active)
    print_step(1, "Checking Python environment")
    python_exe = sys.executable
    print(f"Using Python: {python_exe}")
    print_success("Python environment ready")
    
    # Step 2: Clean old builds
    print_step(2, "Cleaning old builds")
    if os.path.exists("dist"):
        shutil.rmtree("dist")
    if os.path.exists("build"):
        shutil.rmtree("build")
    print_success("Old builds cleaned")
    
    # Step 3: Test local installation
    print_step(3, "Testing local installation")
    run_command(
        f"{python_exe} -m pip install -e . --quiet",
        "Install package"
    )
    print_success("Package installed successfully")
    
    # Step 4: Install build dependencies
    print_step(4, "Installing build dependencies")
    run_command(
        f"{python_exe} -m pip install -r requirements-dev.txt --quiet",
        "Install dev requirements"
    )
    print_success("Build dependencies ready")
    
    # Step 5: Build executable
    print_step(5, "Building standalone executable")
    run_command(
        f"{python_exe} build_exe.py",
        "Build executable"
    )
    print_success("Executable built successfully")
    
    # Step 6: Build Python package
    print_step(6, "Building Python package")
    run_command(
        f"{python_exe} -m pip install build --quiet",
        "Install build tools"
    )
    run_command(
        f"{python_exe} -m build",
        "Build Python package"
    )
    print_success("Python package built successfully")
    
    # Summary
    print_header("✅ Release Build Complete!")
    print(f"\033[93mVersion: {version}\033[0m\n")
    print("\033[96mDistribution files created:\033[0m")
    
    # List dist contents
    if os.path.exists("dist"):
        for item in sorted(os.listdir("dist")):
            file_path = Path("dist") / item
            size = file_path.stat().st_size
            size_mb = size / (1024 * 1024)
            if size_mb >= 1:
                size_str = f"{size_mb:.1f} MB"
            else:
                size_kb = size / 1024
                size_str = f"{size_kb:.1f} KB"
            print(f"  📦 {item:40s} ({size_str})")
    
    print("\n\033[96mNext Steps:\033[0m")
    
    # Platform-specific instructions
    if sys.platform == "win32":
        exe_name = "kvg-rgb.exe"
        test_cmd = f".\\dist\\{exe_name} --help"
    else:
        exe_name = "kvg-rgb"
        test_cmd = f"./dist/{exe_name} --help"
    
    print(f"  1. Test executable:     {test_cmd}")
    print(f"  2. Upload to PyPI:      twine upload dist/kvg_rgb-{version}*")
    print(f"  3. Create GitHub release and attach {exe_name}")
    print()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n\033[91mRelease process cancelled by user\033[0m")
        sys.exit(1)
    except Exception as e:
        print_error(f"Unexpected error: {e}")
        sys.exit(1)
