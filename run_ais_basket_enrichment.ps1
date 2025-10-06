# OpenAlex Enrichment Script

Param(
    [switch]$RunEnrichment = $false,
    [switch]$CheckDeps = $false,
    [switch]$Help = $false
)

if ($Help) {
    Write-Host @"
AIS Basket OpenAlex Enrichment Script
====================================

This script enriches the CrossRef corpus with OpenAlex data:
- Missing abstracts (especially Taylor & Francis journals)
- Keywords/subjects (not available in CrossRef)
- Better author affiliations

Usage:
  .\run_ais_basket_enrichment.ps1 [options]

Options:
  -RunEnrichment   Start the enrichment process
  -CheckDeps      Check Python dependencies
  -Help           Show this help message

Examples:
  .\run_ais_basket_enrichment.ps1 -CheckDeps
  .\run_ais_basket_enrichment.ps1 -RunEnrichment

"@
    exit 0
}

# Configuration
$PythonScript = "enrich_ais_basket_openalex.py"
$RequiredPackages = @("requests", "pandas", "numpy", "tqdm", "pyarrow")

# Functions
function Test-PythonPackage {
    param([string]$PackageName)
    
    try {
        $result = python -c "import $PackageName; print('OK')" 2>$null
        return $result -eq "OK"
    }
    catch {
        return $false
    }
}

function Install-MissingPackages {
    param([array]$MissingPackages)
    
    if ($MissingPackages.Count -eq 0) {
        return
    }
    
    Write-Host "`nInstalling missing packages..." -ForegroundColor Yellow
    foreach ($package in $MissingPackages) {
        Write-Host "Installing $package..." -ForegroundColor Cyan
        
        python -m pip install $package
        if ($LASTEXITCODE -ne 0) {
            Write-Host "Failed to install $package" -ForegroundColor Red
            return $false
        }
    }
    
    Write-Host "All packages installed successfully!" -ForegroundColor Green
    return $true
}

function Test-Prerequisites {
    Write-Host "Checking prerequisites..." -ForegroundColor Cyan
    
    # Check Python
    try {
        $pythonVersion = python --version 2>&1
        Write-Host "✓ Python: $pythonVersion" -ForegroundColor Green
    }
    catch {
        Write-Host "✗ Python not found. Please install Python 3.8+." -ForegroundColor Red
        return $false
    }
    
    # Check if script exists
    if (-not (Test-Path $PythonScript)) {
        Write-Host "✗ Script not found: $PythonScript" -ForegroundColor Red
        return $false
    }
    Write-Host "✓ Script found: $PythonScript" -ForegroundColor Green
    
    # Check if CrossRef corpus exists
    $corpusFile = "data\clean\ais_basket_corpus.json"
    if (-not (Test-Path $corpusFile)) {
        Write-Host "✗ CrossRef corpus not found: $corpusFile" -ForegroundColor Red
        Write-Host "  Please run the CrossRef fetcher first." -ForegroundColor Yellow
        return $false
    }
    Write-Host "✓ CrossRef corpus found: $corpusFile" -ForegroundColor Green
    
    # Check packages
    $missingPackages = @()
    foreach ($package in $RequiredPackages) {
        if (Test-PythonPackage $package) {
            Write-Host "✓ Package: $package" -ForegroundColor Green
        } else {
            Write-Host "✗ Package missing: $package" -ForegroundColor Red
            $missingPackages += $package
        }
    }
    
    if ($missingPackages.Count -gt 0) {
        $response = Read-Host "`nInstall missing packages? (y/n)"
        if ($response -eq 'y' -or $response -eq 'Y') {
            if (-not (Install-MissingPackages $missingPackages)) {
                return $false
            }
        } else {
            Write-Host "Cannot continue without required packages." -ForegroundColor Red
            return $false
        }
    }
    
    Write-Host "`n✓ All prerequisites met!" -ForegroundColor Green
    return $true
}

function Start-Enrichment {
    Write-Host @"

Starting OpenAlex Enrichment Process
===================================

This will enrich your CrossRef corpus with OpenAlex data:
Missing abstracts (especially Taylor & Francis journals)
Keywords/concepts (not available in CrossRef)
Enhanced author affiliations

The process will:
1. Load your CrossRef corpus (12564 articles)
2. Query OpenAlex API to find matching articles
3. Extract missing abstracts, keywords, and affiliations
4. Save enriched corpus in JSON and Parquet formats
5. Generate comprehensive enrichment report

Note: This may take 30-45 minutes due to API rate limits.

"@ -ForegroundColor Cyan
    
    $response = Read-Host "Continue? (y/n)"
    if ($response -ne 'y' -and $response -ne 'Y') {
        Write-Host "Enrichment cancelled." -ForegroundColor Yellow
        exit 0
    }
    
    Write-Host "`nStarting enrichment..." -ForegroundColor Green
    Write-Host "Progress will be displayed in real-time.`n" -ForegroundColor Cyan
    
    # Run the enrichment script
    python $PythonScript
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host @"

Enrichment completed successfully!

Output files:
data/clean/ais_basket_corpus_enriched.json (full enriched corpus)
data/clean/ais_basket_corpus_enriched.parquet (analysis-ready format)
output/enrichment_report.json (detailed enrichment statistics)
output/enrichment_log.log (complete process log)

Next steps:
1. Review the enrichment report to see improvements
2. Run analysis on the enriched corpus
3. Compare abstract coverage before/after enrichment

"@ -ForegroundColor Green
    } else {
        Write-Host "`n✗ Enrichment failed. Check the log file for details." -ForegroundColor Red
    }
}

# Main execution
Write-Host @"
AIS Basket OpenAlex Enrichment
=============================
"@ -ForegroundColor Cyan

if ($CheckDeps) {
    Test-Prerequisites | Out-Null
    exit 0
}

if ($RunEnrichment) {
    if (Test-Prerequisites) {
        Start-Enrichment
    }
    exit 0
}

# Default: Show help
Write-Host @"
Use -Help for usage information.
Use -CheckDeps to check dependencies.
Use -RunEnrichment to start the enrichment process.

Example: .\run_ais_basket_enrichment.ps1 -RunEnrichment
"@ -ForegroundColor Yellow