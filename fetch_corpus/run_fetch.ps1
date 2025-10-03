# PowerShell script to run the IS corpus fetcher with OpenAlex polite pool access
# 
# INSTRUCTIONS:
# 1. Edit the email below to your actual email address
# 2. Run this script: .\fetch_corpus\run_fetch.ps1
# 3. Choose parallel (faster, recommended) or sequential mode
# 
# The email gives you access to OpenAlex's "polite pool" with 100,000 requests/day
# instead of the anonymous limit of ~100 requests per 5 minutes.

# ====== EDIT YOUR EMAIL HERE ======
$EMAIL = "carlosdenner@gmail.com"
# ==================================

# ====== CHOOSE MODE ======
# Set to $true for PARALLEL (2-3x faster, uses 2 workers)
# Set to $false for SEQUENTIAL (slower but more conservative)
$USE_PARALLEL = $true
# =========================

Write-Host "="*70 -ForegroundColor Cyan
Write-Host "  IS Corpus Fetcher - OpenAlex Data Collection" -ForegroundColor Cyan
Write-Host "="*70 -ForegroundColor Cyan
Write-Host ""
Write-Host "Email (polite pool): $EMAIL" -ForegroundColor Yellow
$env:OPENALEX_MAILTO = $EMAIL

if ($USE_PARALLEL) {
    Write-Host "Mode: PARALLEL (2 workers) ⚡" -ForegroundColor Green
    Write-Host "Expected time: ~20-40 minutes" -ForegroundColor Gray
    $SCRIPT = "fetch_corpus/fetch_is_corpus_parallel.py"
} else {
    Write-Host "Mode: SEQUENTIAL" -ForegroundColor Yellow
    Write-Host "Expected time: ~45-90 minutes" -ForegroundColor Gray
    $SCRIPT = "fetch_corpus/fetch_is_corpus.py"
}

Write-Host ""
Write-Host "Fetching 11 premier IS journals from OpenAlex..." -ForegroundColor Green
Write-Host ""

# Run the Python script
$startTime = Get-Date
& "C:/Users/carlo/Dropbox/literature_analyzer_v2/literature/.venv/Scripts/python.exe" $SCRIPT
$endTime = Get-Date
$elapsed = $endTime - $startTime

Write-Host ""
Write-Host "="*70 -ForegroundColor Cyan
Write-Host "✅ Fetch complete!" -ForegroundColor Green
Write-Host "="*70 -ForegroundColor Cyan
Write-Host "Time elapsed: $($elapsed.ToString('hh\:mm\:ss'))" -ForegroundColor Yellow
Write-Host "Output directory: data/clean/" -ForegroundColor Yellow
Write-Host "Main corpus file: data/clean/is_corpus_all.parquet" -ForegroundColor Yellow
Write-Host ""
