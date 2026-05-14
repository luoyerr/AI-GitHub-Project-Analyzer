# Quick Start Script for AI GitHub Analyzer
# This script helps you set up and run the analyzer quickly

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  AI GitHub Analyzer - Quick Start" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check if conda is installed
Write-Host "Checking for Conda..." -ForegroundColor Yellow
try {
    $condaVersion = conda --version 2>&1
    Write-Host "✓ Conda found: $condaVersion" -ForegroundColor Green
} catch {
    Write-Host "✗ Conda not found. Please install Anaconda or Miniconda first." -ForegroundColor Red
    Write-Host "Download from: https://www.anaconda.com/download" -ForegroundColor Yellow
    exit 1
}

# Check if environment exists
$envName = "ai-github-analyzer"
Write-Host ""
Write-Host "Checking for conda environment '$envName'..." -ForegroundColor Yellow
$envExists = conda env list | Select-String $envName

if ($envExists) {
    Write-Host "✓ Environment already exists" -ForegroundColor Green
} else {
    Write-Host "Creating new conda environment..." -ForegroundColor Yellow
    conda create -n $envName python=3.12 -y
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✓ Environment created successfully" -ForegroundColor Green
    } else {
        Write-Host "✗ Failed to create environment" -ForegroundColor Red
        exit 1
    }
}

# Activate environment
Write-Host ""
Write-Host "Activating environment..." -ForegroundColor Yellow
conda activate $envName

# Install dependencies
Write-Host ""
Write-Host "Installing dependencies..." -ForegroundColor Yellow
pip install -e .

if ($LASTEXITCODE -eq 0) {
    Write-Host "✓ Dependencies installed successfully" -ForegroundColor Green
} else {
    Write-Host "✗ Failed to install dependencies" -ForegroundColor Red
    exit 1
}

# Verify installation
Write-Host ""
Write-Host "Verifying installation..." -ForegroundColor Yellow
python main.py version

if ($LASTEXITCODE -eq 0) {
    Write-Host "✓ Installation verified successfully" -ForegroundColor Green
} else {
    Write-Host "✗ Verification failed" -ForegroundColor Red
    exit 1
}

# Display next steps
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Setup Complete!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "1. Activate environment: conda activate $envName" -ForegroundColor White
Write-Host "2. Run analyzer: python main.py analyze <repo_url>" -ForegroundColor White
Write-Host "3. Get help: python main.py --help" -ForegroundColor White
Write-Host ""
Write-Host "Example:" -ForegroundColor Cyan
Write-Host "  python main.py analyze https://github.com/python/cpython" -ForegroundColor White
Write-Host ""
