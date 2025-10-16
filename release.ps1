# Release script for KVG RGB Controller
# Usage: .\release.ps1

Write-Host ""
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host "  KVG RGB Controller Release Script  " -ForegroundColor Cyan
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host ""

# Get current version
$versionFile = Get-Content "kvg_rgb\__init__.py"
$versionLine = $versionFile | Select-String '__version__'
$currentVersion = $versionLine -replace '.*"(.*)".*', '$1'
Write-Host "Current version: $currentVersion" -ForegroundColor Yellow
Write-Host ""

# Activate venv
Write-Host "Step 1: Activating virtual environment..." -ForegroundColor Green
& .\venv\Scripts\Activate.ps1
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Failed to activate venv" -ForegroundColor Red
    exit 1
}
Write-Host "✓ Virtual environment activated" -ForegroundColor Green
Write-Host ""

# Clean old builds
Write-Host "Step 2: Cleaning old builds..." -ForegroundColor Green
if (Test-Path "dist") {
    Remove-Item -Recurse -Force "dist"
}
if (Test-Path "build") {
    Remove-Item -Recurse -Force "build"
}
Write-Host "✓ Old builds cleaned" -ForegroundColor Green
Write-Host ""

# Reinstall package locally to test
Write-Host "Step 3: Testing local installation..." -ForegroundColor Green
pip install -e . --quiet
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Failed to install package" -ForegroundColor Red
    exit 1
}
Write-Host "✓ Package installed successfully" -ForegroundColor Green
Write-Host ""

# Install build dependencies if needed
Write-Host "Step 4: Installing build dependencies..." -ForegroundColor Green
pip install -r requirements-dev.txt --quiet
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Failed to install build dependencies" -ForegroundColor Red
    exit 1
}
Write-Host "✓ Build dependencies ready" -ForegroundColor Green
Write-Host ""

# Build executable
Write-Host "Step 5: Building standalone executable..." -ForegroundColor Green
python build_exe.py
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Failed to build executable" -ForegroundColor Red
    exit 1
}
Write-Host "✓ Executable built successfully" -ForegroundColor Green
Write-Host ""

# Build Python package
Write-Host "Step 6: Building Python package..." -ForegroundColor Green
pip install build --quiet
python -m build
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Failed to build Python package" -ForegroundColor Red
    exit 1
}
Write-Host "✓ Python package built successfully" -ForegroundColor Green
Write-Host ""

# Summary
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host "  ✅ Release Build Complete!  " -ForegroundColor Green
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Version: $currentVersion" -ForegroundColor Yellow
Write-Host ""
Write-Host "Distribution files created:" -ForegroundColor Cyan
Write-Host "  📦 Executable:      dist\kvg-rgb.exe" -ForegroundColor White
Write-Host "  📦 Python Wheel:    dist\kvg_rgb-$currentVersion-py3-none-any.whl" -ForegroundColor White
Write-Host "  📦 Source Archive:  dist\kvg-rgb-$currentVersion.tar.gz" -ForegroundColor White
Write-Host ""
Write-Host "Next Steps:" -ForegroundColor Cyan
Write-Host "  1. Test executable:     .\dist\kvg-rgb.exe --help" -ForegroundColor White
Write-Host "  2. Upload to PyPI:      twine upload dist\kvg_rgb-$currentVersion*" -ForegroundColor White
Write-Host "  3. Create GitHub release and attach kvg-rgb.exe" -ForegroundColor White
Write-Host ""
