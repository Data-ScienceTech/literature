# PowerShell FTP Upload Script for research.datasciencetech.ca
# 
# INSTRUCTIONS:
# 1. Edit the variables below with your FTP credentials
# 2. Run this script in PowerShell: .\upload_via_ftp.ps1
# 3. Wait for upload to complete
# 4. Visit https://research.datasciencetech.ca/

# === CONFIGURATION - EDIT THESE ===
$ftpServer = "ftp.datasciencetech.ca"
$ftpUsername = "YOUR_FTP_USERNAME"
$ftpPassword = "YOUR_FTP_PASSWORD"
$remotePath = "/public_html/research/"
$localPath = "deploy"

# === DO NOT EDIT BELOW THIS LINE ===

Write-Host "================================" -ForegroundColor Cyan
Write-Host "FTP UPLOAD TO DATASCIENCETECH.CA" -ForegroundColor Cyan
Write-Host "================================" -ForegroundColor Cyan
Write-Host ""

# Check if credentials are set
if ($ftpUsername -eq "YOUR_FTP_USERNAME") {
    Write-Host "ERROR: Please edit this script and add your FTP credentials!" -ForegroundColor Red
    Write-Host "Edit lines 8-10 with your actual FTP details." -ForegroundColor Yellow
    exit
}

# Get all files to upload
$files = Get-ChildItem -Path $localPath -File

Write-Host "Found $($files.Count) files to upload" -ForegroundColor Green
Write-Host ""

# Upload each file
$successCount = 0
$failCount = 0

foreach ($file in $files) {
    try {
        $ftpUri = "ftp://$ftpServer$remotePath$($file.Name)"
        
        Write-Host "Uploading: $($file.Name)..." -NoNewline
        
        # Create FTP request
        $request = [System.Net.FtpWebRequest]::Create($ftpUri)
        $request.Method = [System.Net.WebRequestMethods+Ftp]::UploadFile
        $request.Credentials = New-Object System.Net.NetworkCredential($ftpUsername, $ftpPassword)
        $request.UseBinary = $true
        $request.UsePassive = $true
        
        # Read file content
        $fileContent = [System.IO.File]::ReadAllBytes($file.FullName)
        $request.ContentLength = $fileContent.Length
        
        # Upload
        $requestStream = $request.GetRequestStream()
        $requestStream.Write($fileContent, 0, $fileContent.Length)
        $requestStream.Close()
        
        # Get response
        $response = $request.GetResponse()
        $response.Close()
        
        Write-Host " SUCCESS" -ForegroundColor Green
        $successCount++
        
    } catch {
        Write-Host " FAILED" -ForegroundColor Red
        Write-Host "  Error: $($_.Exception.Message)" -ForegroundColor Red
        $failCount++
    }
}

Write-Host ""
Write-Host "================================" -ForegroundColor Cyan
Write-Host "UPLOAD COMPLETE!" -ForegroundColor Cyan
Write-Host "================================" -ForegroundColor Cyan
Write-Host "Successful: $successCount files" -ForegroundColor Green
Write-Host "Failed: $failCount files" -ForegroundColor Red
Write-Host ""
Write-Host "Your dashboard should now be live at:" -ForegroundColor Yellow
Write-Host "https://research.datasciencetech.ca/" -ForegroundColor Cyan
Write-Host ""
