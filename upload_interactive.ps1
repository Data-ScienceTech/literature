# Enhanced PowerShell FTP Upload Script for research.datasciencetech.ca
# Interactive mode with credential storage and progress tracking

param(
    [string]$ConfigFile = "upload_config.json",
    [switch]$Interactive = $false
)

# Color functions
function Write-Success { param($msg) Write-Host $msg -ForegroundColor Green }
function Write-Error-Custom { param($msg) Write-Host $msg -ForegroundColor Red }
function Write-Info { param($msg) Write-Host $msg -ForegroundColor Cyan }
function Write-Warning-Custom { param($msg) Write-Host $msg -ForegroundColor Yellow }

# Banner
function Show-Banner {
    Write-Host ""
    Write-Host "============================================================" -ForegroundColor Cyan
    Write-Host "   🚀 AUTOMATED UPLOAD TO RESEARCH.DATASCIENCETECH.CA" -ForegroundColor Cyan
    Write-Host "============================================================" -ForegroundColor Cyan
    Write-Host ""
}

# Load or create configuration
function Get-FTPConfig {
    param($ConfigPath)
    
    if (Test-Path $ConfigPath) {
        Write-Info "📋 Found existing configuration"
        $useExisting = Read-Host "Use saved credentials? (y/n)"
        
        if ($useExisting -eq 'y') {
            $config = Get-Content $ConfigPath | ConvertFrom-Json
            Write-Success "✅ Loaded saved credentials"
            return $config
        }
    }
    
    Write-Info "`n📝 Let's set up your FTP credentials..."
    Write-Host "(Find these in your hosting provider's cPanel)" -ForegroundColor Gray
    Write-Host ""
    
    $ftpServer = Read-Host "FTP Server (e.g., ftp.datasciencetech.ca)"
    $ftpUsername = Read-Host "FTP Username"
    $ftpPasswordSecure = Read-Host "FTP Password" -AsSecureString
    $ftpPassword = [Runtime.InteropServices.Marshal]::PtrToStringAuto(
        [Runtime.InteropServices.Marshal]::SecureStringToBSTR($ftpPasswordSecure))
    $ftpPort = Read-Host "FTP Port (press Enter for 21)"
    if ([string]::IsNullOrWhiteSpace($ftpPort)) { $ftpPort = "21" }
    $remotePath = Read-Host "Remote path (e.g., /public_html/research/)"
    
    $config = @{
        host = $ftpServer
        username = $ftpUsername
        password = $ftpPassword
        port = $ftpPort
        remotePath = $remotePath
    }
    
    $save = Read-Host "`n💾 Save credentials for future use? (y/n)"
    if ($save -eq 'y') {
        $config | ConvertTo-Json | Set-Content $ConfigPath
        Write-Success "✅ Credentials saved to $ConfigPath"
    }
    
    return $config
}

# Test FTP connection
function Test-FTPConnection {
    param($Config)
    
    Write-Host ""
    Write-Info "============================================================"
    Write-Info "🔌 TESTING FTP CONNECTION"
    Write-Info "============================================================"
    Write-Host ""
    
    try {
        Write-Host "Connecting to $($Config.host)..." -NoNewline
        
        $ftpUri = "ftp://$($Config.host):$($Config.port)/"
        $request = [System.Net.FtpWebRequest]::Create($ftpUri)
        $request.Method = [System.Net.WebRequestMethods+Ftp]::ListDirectory
        $request.Credentials = New-Object System.Net.NetworkCredential($Config.username, $Config.password)
        $request.UsePassive = $true
        $request.Timeout = 10000
        
        $response = $request.GetResponse()
        $response.Close()
        
        Write-Success " ✅ Connected successfully!"
        return $true
        
    } catch {
        Write-Error-Custom " ❌ Connection failed!"
        Write-Host ""
        Write-Error-Custom "Error: $($_.Exception.Message)"
        Write-Host ""
        Write-Warning-Custom "Please check:"
        Write-Host "  - FTP server address is correct"
        Write-Host "  - Username and password are correct"
        Write-Host "  - Port is correct (usually 21)"
        Write-Host "  - Your firewall allows FTP connections"
        return $false
    }
}

# Create remote directory if needed
function Ensure-RemoteDirectory {
    param($Config, $Path)
    
    # Try to create directory (ignore if exists)
    try {
        $ftpUri = "ftp://$($Config.host):$($Config.port)$Path"
        $request = [System.Net.FtpWebRequest]::Create($ftpUri)
        $request.Method = [System.Net.WebRequestMethods+Ftp]::MakeDirectory
        $request.Credentials = New-Object System.Net.NetworkCredential($Config.username, $Config.password)
        $request.UsePassive = $true
        
        $response = $request.GetResponse()
        $response.Close()
        Write-Info "📁 Created remote directory: $Path"
    } catch {
        # Directory probably exists, that's fine
    }
}

# Upload a single file
function Upload-File {
    param($Config, $LocalFile, $RemoteFileName)
    
    try {
        $ftpUri = "ftp://$($Config.host):$($Config.port)$($Config.remotePath)$RemoteFileName"
        
        # Create request
        $request = [System.Net.FtpWebRequest]::Create($ftpUri)
        $request.Method = [System.Net.WebRequestMethods+Ftp]::UploadFile
        $request.Credentials = New-Object System.Net.NetworkCredential($Config.username, $Config.password)
        $request.UseBinary = $true
        $request.UsePassive = $true
        
        # Read file
        $fileContent = [System.IO.File]::ReadAllBytes($LocalFile.FullName)
        $request.ContentLength = $fileContent.Length
        
        # Upload
        $requestStream = $request.GetRequestStream()
        $requestStream.Write($fileContent, 0, $fileContent.Length)
        $requestStream.Close()
        
        # Get response
        $response = $request.GetResponse()
        $response.Close()
        
        return $true
        
    } catch {
        Write-Error-Custom "  Error: $($_.Exception.Message)"
        return $false
    }
}

# Upload all files
function Upload-AllFiles {
    param($Config)
    
    Write-Host ""
    Write-Info "============================================================"
    Write-Info "📤 UPLOADING FILES TO RESEARCH.DATASCIENCETECH.CA"
    Write-Info "============================================================"
    Write-Host ""
    
    $deployPath = "deploy"
    
    if (-not (Test-Path $deployPath)) {
        Write-Error-Custom "❌ Deploy directory not found: $deployPath"
        Write-Warning-Custom "   Run: python deploy_to_web.py first"
        return $false
    }
    
    $files = Get-ChildItem -Path $deployPath -File
    
    if ($files.Count -eq 0) {
        Write-Error-Custom "❌ No files found in $deployPath"
        return $false
    }
    
    Write-Host "📋 Found $($files.Count) files to upload"
    Write-Host "🎯 Target: $($Config.host)$($Config.remotePath)"
    Write-Host ""
    
    $proceed = Read-Host "Proceed with upload? (y/n)"
    if ($proceed -ne 'y') {
        Write-Warning-Custom "Upload cancelled."
        return $false
    }
    
    # Ensure remote directory exists
    Ensure-RemoteDirectory -Config $Config -Path $Config.remotePath
    
    Write-Host ""
    Write-Info "📤 Uploading files..."
    Write-Host ("─" * 60)
    
    $successCount = 0
    $failCount = 0
    
    foreach ($file in $files) {
        $fileName = $file.Name
        $fileSize = "{0:N2}" -f ($file.Length / 1KB)
        
        Write-Host "📄 $fileName ($fileSize KB)..." -NoNewline
        
        if (Upload-File -Config $Config -LocalFile $file -RemoteFileName $fileName) {
            Write-Success " ✅"
            $successCount++
        } else {
            Write-Error-Custom " ❌"
            $failCount++
        }
    }
    
    Write-Host ("─" * 60)
    Write-Host ""
    
    if ($failCount -eq 0) {
        Write-Success "✅ Upload Complete! All $successCount files uploaded successfully!"
    } else {
        Write-Warning-Custom "⚠️  Upload completed with errors"
        Write-Host "   Successful: $successCount/$($files.Count)"
        Write-Host "   Failed: $failCount/$($files.Count)"
    }
    
    return $true
}

# Show verification steps
function Show-Verification {
    Write-Host ""
    Write-Info "============================================================"
    Write-Info "✅ VERIFICATION & TESTING"
    Write-Info "============================================================"
    Write-Host ""
    
    $baseUrl = "https://research.datasciencetech.ca"
    
    Write-Success "🌐 Your dashboard should now be live!"
    Write-Host ""
    Write-Host "🔗 Test these URLs:" -ForegroundColor Yellow
    Write-Host "  1. Main page: $baseUrl/" -ForegroundColor Cyan
    Write-Host "  2. Papers DB: $baseUrl/papers_database.html" -ForegroundColor Cyan
    Write-Host "  3. All streams: $baseUrl/all_streams.html" -ForegroundColor Cyan
    Write-Host "  4. Methodology: $baseUrl/methodology.html" -ForegroundColor Cyan
    Write-Host "  5. Stream 0: $baseUrl/stream_0.html" -ForegroundColor Cyan
    
    Write-Host ""
    Write-Host "📋 Verification Checklist:" -ForegroundColor Yellow
    Write-Host "  [ ] Main page loads"
    Write-Host "  [ ] Navigation works between pages"
    Write-Host "  [ ] Search functions in papers database"
    Write-Host "  [ ] Charts and visualizations display"
    Write-Host "  [ ] Mobile responsive (test on phone)"
    Write-Host "  [ ] All DOI links work"
    
    Write-Host ""
    $openBrowser = Read-Host "Open main page in browser now? (y/n)"
    if ($openBrowser -eq 'y') {
        Start-Process $baseUrl
    }
    
    Write-Host ""
    Write-Success "🎉 Congratulations! Your Research Streams Dashboard is live!"
    Write-Host ""
}

# Main execution
function Main {
    Show-Banner
    
    try {
        # Step 1: Get configuration
        $config = Get-FTPConfig -ConfigPath $ConfigFile
        
        # Step 2: Test connection
        if (-not (Test-FTPConnection -Config $config)) {
            Write-Host ""
            $retry = Read-Host "Retry with different credentials? (y/n)"
            if ($retry -eq 'y') {
                if (Test-Path $ConfigFile) {
                    Remove-Item $ConfigFile
                }
                Main
                return
            }
            Write-Error-Custom "`n❌ Cannot proceed without valid FTP connection"
            exit 1
        }
        
        # Step 3: Upload files
        if (-not (Upload-AllFiles -Config $config)) {
            Write-Error-Custom "`n❌ Upload failed!"
            exit 1
        }
        
        # Step 4: Show verification
        Show-Verification
        
        Write-Host ""
        Write-Success "✅ Deployment complete!"
        Write-Host ""
        
    } catch {
        Write-Host ""
        Write-Error-Custom "❌ An error occurred: $($_.Exception.Message)"
        Write-Host ""
        exit 1
    }
}

# Run
Main
