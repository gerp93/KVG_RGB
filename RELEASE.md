# Release Process Guide

Complete guide for releasing new versions of KVG RGB Controller.

---

## 🚀 Quick Release (5 Steps)

### Step 1: Update Version Number

Open `kvg_rgb\__init__.py` and bump the version:
```python
__version__ = "0.2.0"  # Change from "0.1.1" to "0.2.0"
```

**Version Numbering Guide (Semantic Versioning):**
- `0.1.1` → `0.1.2` = Bug fix (PATCH)
- `0.1.1` → `0.2.0` = New feature (MINOR)  
- `0.1.1` → `1.0.0` = Breaking change (MAJOR)

**Examples:**
- Fixed a bug → `0.1.0` to `0.1.1`
- Added new effect → `0.1.0` to `0.2.0`
- Changed CLI commands → `0.1.0` to `1.0.0`

### Step 2: Update Changelog (Optional but Recommended)

Edit `CHANGELOG.md` and move items from `[Unreleased]` to a new version section:
```markdown
## [0.2.0] - 2025-10-16

### Added
- New pulse effect
- Zone-specific color control

### Fixed
- Connection timeout issue
```

### Step 3: Run Release Script

```powershell
.\release.ps1
```

This automatically:
- ✅ Activates virtual environment
- ✅ Cleans old builds
- ✅ Installs dependencies (PyInstaller, build tools)
- ✅ Tests local installation
- ✅ Builds standalone `.exe`
- ✅ Builds Python packages (`.whl` and `.tar.gz`)

### Step 4: Test the Build

```powershell
# Test the executable
.\dist\kvg-rgb.exe --help
.\dist\kvg-rgb.exe list

# Verify all files exist
ls dist\
```

You should see:
- `kvg-rgb.exe` (~8-9 MB)
- `kvg_rgb-0.2.0-py3-none-any.whl` (~6 KB)
- `kvg_rgb-0.2.0.tar.gz` (~7 KB)

### Step 5: Distribute

**For End Users (No Python Required):**
- Share `dist\kvg-rgb.exe` via GitHub releases (recommended), Google Drive, or email

**For Python Developers (Optional):**
- Upload to PyPI (see below)

---

## 📦 Distribution Options

### Option A: GitHub Release (Recommended)

1. Go to your GitHub repository
2. Click **Releases** → **Create a new release**
3. **Tag:** `v0.2.0` (matches your version)
4. **Title:** `KVG RGB v0.2.0`
5. **Description:** Copy from CHANGELOG.md
6. **Attach file:** `dist\kvg-rgb.exe`
7. Click **Publish release**

Users can download the `.exe` directly from GitHub!

### Option B: PyPI (For pip install)

**First Time Setup:**
```powershell
# Install twine
pip install twine

# Create PyPI account at https://pypi.org/account/register/
```

**Each Release:**
```powershell
# After running release.ps1, upload to PyPI:
twine upload dist\kvg_rgb-0.2.0*

# Enter your PyPI username and password when prompted
```

Now anyone can install with:
```powershell
pip install kvg-rgb
```

---

## ✅ Complete Release Checklist

- [ ] Update version in `kvg_rgb\__init__.py`
- [ ] Update `CHANGELOG.md` with new changes
- [ ] Run `.\release.ps1`
- [ ] Test `.\dist\kvg-rgb.exe --help` and `.\dist\kvg-rgb.exe list`
- [ ] Verify all 3 files in `dist\` folder
- [ ] Create GitHub release with `.exe` attachment
- [ ] (Optional) Upload to PyPI: `twine upload dist\kvg_rgb-*`
- [ ] (Optional) Announce release

---

## 🔧 Testing Before Release

```powershell
# Test the executable
.\dist\kvg-rgb.exe --help
.\dist\kvg-rgb.exe list
.\dist\kvg-rgb.exe color 255 0 0

# Test the Python package locally
pip install dist\kvg_rgb-*.whl
kvg-rgb --help
```

---

## 🔧 Testing Before Release

```powershell
# Test the executable
.\dist\kvg-rgb.exe --help
.\dist\kvg-rgb.exe list
.\dist\kvg-rgb.exe color 255 0 0

# Test the Python package locally
pip install dist\kvg_rgb-*.whl
kvg-rgb --help
```

---

## 🐛 Troubleshooting

**"Failed to build executable"**
- Make sure PyInstaller is installed: `pip install -r requirements-dev.txt`
- The release script now auto-installs this for you

**"Failed to build Python package"**
- Make sure build tools are installed: `pip install build`
- The release script handles this automatically

**"twine: command not found"**
- Install twine: `pip install twine`

**Version conflict**
- Version is auto-synced from `kvg_rgb\__init__.py`
- Only update version in that ONE file

**`.exe` not created but Python packages were**
- PyInstaller wasn't installed
- Run: `pip install -r requirements-dev.txt`
- Then run: `python build_exe.py`

---

## 📝 Quick Reference

```powershell
# Full release process
# 1. Edit: kvg_rgb\__init__.py (update version)
# 2. Edit: CHANGELOG.md (document changes)
# 3. Build:
.\release.ps1

# 4. Test:
.\dist\kvg-rgb.exe --help

# 5. Distribute:
# - Upload dist\kvg-rgb.exe to GitHub releases
# - Or: twine upload dist\kvg_rgb-*
```

---

## 📂 What Gets Created

After running `.\release.ps1`, you'll have:

```
dist/
├── kvg-rgb.exe                      # ~8-9 MB - Standalone executable
├── kvg_rgb-X.Y.Z-py3-none-any.whl  # ~6 KB - Python wheel
└── kvg_rgb-X.Y.Z.tar.gz            # ~7 KB - Source archive
```

**Share the `.exe`** with end users → No Python required
**Share the `.whl`** with Python devs → `pip install kvg_rgb-*.whl`
**Upload to PyPI** → Anyone can `pip install kvg-rgb`

