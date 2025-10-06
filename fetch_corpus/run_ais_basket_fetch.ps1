# ========================================
# AIS Basket of 8 - CrossRef Fetcher
# PowerShell Helper Script
# ========================================

param(
    [switch]$Full,
    [string]$Journal,
    [string]$FromDate,
    [switch]$NoBibTeX,
    [switch]$Help
)

# Show help
if ($Help) {
    Write-Host @"
AIS Basket of 8 - CrossRef Fetcher
===================================

USAGE:
    .\run_ais_basket_fetch.ps1 [OPTIONS]

OPTIONS:
    -Full           Perform full fetch (ignore previous state)
    -Journal NAME   Fetch only specified journal
    -FromDate DATE  Fetch articles indexed from date (YYYY-MM-DD)
    -NoBibTeX       Skip BibTeX output generation
    -Help           Show this help message

EXAMPLES:
    # Incremental update (recommended)
    .\run_ais_basket_fetch.ps1

    # Full fetch from scratch
    .\run_ais_basket_fetch.ps1 -Full

    # Fetch only MIS Quarterly
    .\run_ais_basket_fetch.ps1 -Journal "MIS Quarterly"

    # Fetch articles indexed since Jan 1, 2024
    .\run_ais_basket_fetch.ps1 -FromDate "2024-01-01"

    # Full fetch without BibTeX
    .\run_ais_basket_fetch.ps1 -Full -NoBibTeX

AVAILABLE JOURNALS:
    - MIS Quarterly
    - Information Systems Research
    - Journal of Management Information Systems
    - Journal of the Association for Information Systems
    - European Journal of Information Systems
    - Information Systems Journal
    - Journal of Information Technology
    - Journal of Strategic Information Systems

OUTPUT FILES:
    data/clean/ais_basket_corpus.parquet    - Main dataset (Parquet)
    data/clean/ais_basket_corpus.json       - Full metadata (JSON)
    output/ais_basket_YYYYMMDD.bib         - Citations (BibTeX)
    output/fetch_summary_YYYYMMDD.json     - Summary report
    output/fetch_log_YYYYMMDD_HHMMSS.log   - Detailed log
    data/crossref_state.json               - State tracking file

"@
    exit 0
}

Write-Host "=====================================" -ForegroundColor Cyan
Write-Host "AIS Basket of 8 - CrossRef Fetcher" -ForegroundColor Cyan
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host ""

# Check if Python is available
try {
    $pythonVersion = python --version 2>&1
    Write-Host "✓ Python found: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "✗ Python not found!" -ForegroundColor Red
    Write-Host "  Please install Python 3.8+ and ensure it's in your PATH" -ForegroundColor Yellow
    exit 1
}

# Check if required packages are installed
Write-Host ""
Write-Host "Checking required packages..." -ForegroundColor Yellow

$requiredPackages = @("requests", "pandas", "tqdm", "pyarrow")
$missingPackages = @()

foreach ($package in $requiredPackages) {
    python -c "import $package" 2>&1 | Out-Null
    if ($LASTEXITCODE -ne 0) {
        $missingPackages += $package
        Write-Host "  ✗ $package - NOT INSTALLED" -ForegroundColor Red
    } else {
        Write-Host "  ✓ $package - installed" -ForegroundColor Green
    }
}

# Install missing packages if needed
if ($missingPackages.Count -gt 0) {
    Write-Host ""
    Write-Host "Missing packages detected!" -ForegroundColor Yellow
    $install = Read-Host "Install missing packages? (y/n)"
    
    if ($install -eq "y") {
        Write-Host "Installing packages..." -ForegroundColor Yellow
        pip install $missingPackages -q
        
        if ($LASTEXITCODE -eq 0) {
            Write-Host "✓ Packages installed successfully!" -ForegroundColor Green
        } else {
            Write-Host "✗ Package installation failed!" -ForegroundColor Red
            exit 1
        }
    } else {
        Write-Host "Cannot proceed without required packages." -ForegroundColor Red
        exit 1
    }
}

# Build command arguments
$pythonArgs = @("fetch_corpus\fetch_ais_basket_crossref.py")

if ($Full) {
    $pythonArgs += "--full"
    Write-Host ""
    Write-Host "Mode: FULL FETCH (all articles)" -ForegroundColor Magenta
}
else {
    Write-Host ""
    Write-Host "Mode: INCREMENTAL UPDATE (new/updated articles only)" -ForegroundColor Cyan
}

if ($Journal) {
    $pythonArgs += "--journal", $Journal
    Write-Host "Journal: $Journal" -ForegroundColor Cyan
}

if ($FromDate) {
    $pythonArgs += "--from-date", $FromDate
    Write-Host "From Date: $FromDate" -ForegroundColor Cyan
}

if ($NoBibTeX) {
    $pythonArgs += "--no-bibtex"
    Write-Host "BibTeX output: DISABLED" -ForegroundColor Yellow
}

# Show estimated time
Write-Host ""
Write-Host "Estimated time:" -ForegroundColor Yellow
if ($Full) {
    Write-Host "  Full fetch: 15-30 minutes (depending on network)" -ForegroundColor Gray
} else {
    Write-Host "  Incremental update: 1-5 minutes (if run daily/weekly)" -ForegroundColor Gray
}

Write-Host ""
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host "Starting fetch..." -ForegroundColor Cyan
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host ""

# Run the Python script
$startTime = Get-Date
& python @pythonArgs

$endTime = Get-Date
$duration = $endTime - $startTime

Write-Host ""
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host "Fetch completed!" -ForegroundColor Green
Write-Host "=====================================" -ForegroundColor Cyan
$hours = [math]::Floor($duration.TotalHours)
$minutes = $duration.Minutes
$seconds = $duration.Seconds
Write-Host "Duration: $hours hours $minutes minutes $seconds seconds" -ForegroundColor Cyan
Write-Host ""

# Show output files
Write-Host "Output files:" -ForegroundColor Yellow
if (Test-Path "data\clean\ais_basket_corpus.parquet") {
    $size = (Get-Item "data\clean\ais_basket_corpus.parquet").Length / 1MB
    Write-Host "  ✓ data\clean\ais_basket_corpus.parquet ($([math]::Round($size, 2)) MB)" -ForegroundColor Green
}
if (Test-Path "data\clean\ais_basket_corpus.json") {
    $size = (Get-Item "data\clean\ais_basket_corpus.json").Length / 1MB
    Write-Host "  ✓ data\clean\ais_basket_corpus.json ($([math]::Round($size, 2)) MB)" -ForegroundColor Green
}

# Show latest summary
$latestSummary = Get-ChildItem "output\fetch_summary_*.json" | Sort-Object LastWriteTime -Descending | Select-Object -First 1
if ($latestSummary) {
    Write-Host "  ✓ $($latestSummary.FullName)" -ForegroundColor Green
    
    # Parse and display summary
    $summary = Get-Content $latestSummary.FullName | ConvertFrom-Json
    Write-Host ""
    Write-Host "Summary:" -ForegroundColor Cyan
    Write-Host "  Total articles: $($summary.total_articles)" -ForegroundColor White
    Write-Host "  Date range: $($summary.date_range.earliest) - $($summary.date_range.latest)" -ForegroundColor White
    Write-Host ""
    Write-Host "  By Journal:" -ForegroundColor White
    $summary.by_journal.PSObject.Properties | Sort-Object Value -Descending | ForEach-Object {
        Write-Host "    $($_.Name): $($_.Value)" -ForegroundColor Gray
    }
}

Write-Host ""
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "  1. Review the log file in output/ directory" -ForegroundColor Gray
Write-Host "  2. Use data/clean/ais_basket_corpus.parquet for analysis" -ForegroundColor Gray
Write-Host "  3. Run this script again tomorrow to get latest articles" -ForegroundColor Gray
Write-Host ""
