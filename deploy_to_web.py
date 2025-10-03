"""
🚀 Automated Deployment Script for research.datasciencetech.ca
Complete automation for deploying Research Streams Dashboard
"""

import os
import sys
import shutil
import zipfile
from pathlib import Path
import json
from datetime import datetime

class DeploymentAutomation:
    """Automated deployment to research.datasciencetech.ca"""
    
    def __init__(self):
        self.deploy_dir = Path('deploy')
        self.zip_path = Path('research_streams_dashboard.zip')
        self.html_files = []
        
    def prepare_files(self):
        """Prepare all files for deployment."""
        print("\n" + "="*60)
        print("🚀 RESEARCH STREAMS DASHBOARD DEPLOYMENT")
        print("="*60)
        print(f"Target: research.datasciencetech.ca")
        print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*60 + "\n")
        
        # Clean and create deployment directory
        if self.deploy_dir.exists():
            print("🧹 Cleaning existing deployment directory...")
            try:
                # Try to remove old files individually
                for item in self.deploy_dir.iterdir():
                    if item.is_file():
                        item.unlink()
                    elif item.is_dir():
                        shutil.rmtree(item)
            except Exception as e:
                print(f"⚠️  Note: Some files in deploy/ may be in use: {e}")
                print("   Continuing with deployment...")
        else:
            self.deploy_dir.mkdir()
        
        print(f"✅ Using deployment directory: {self.deploy_dir.absolute()}\n")
        
        # List of files to deploy
        self.html_files = [
            'research_streams_dashboard.html',
            'all_streams.html', 
            'papers_database.html',
            'methodology.html'
        ]
        
        # Add all stream files
        for i in range(15):
            self.html_files.append(f'stream_{i}.html')
        
        # Copy HTML files
        print("📋 Copying HTML files to deployment directory:")
        copied_files = []
        missing_files = []
        
        for file in self.html_files:
            if Path(file).exists():
                shutil.copy2(file, self.deploy_dir / file)
                copied_files.append(file)
                print(f"  ✅ {file}")
            else:
                missing_files.append(file)
                print(f"  ❌ MISSING: {file}")
        
        if missing_files:
            print(f"\n⚠️  WARNING: {len(missing_files)} files are missing!")
            print("   Run the dashboard generation scripts first.")
            return False
        
        print(f"\n✅ Copied {len(copied_files)} HTML files")
        return True
    
    def rename_main_file(self):
        """Rename main dashboard to index.html for cleaner URLs."""
        print("\n🔄 Renaming main file for cleaner URLs...")
        main_file = self.deploy_dir / 'research_streams_dashboard.html'
        
        if main_file.exists():
            main_file.rename(self.deploy_dir / 'index.html')
            print("  ✅ research_streams_dashboard.html → index.html")
            print("  🌐 Now accessible at: https://research.datasciencetech.ca/")
        else:
            print("  ❌ Main file not found!")
            return False
        
        return True
    
    def create_htaccess(self):
        """Create .htaccess for Apache configuration."""
        print("\n⚙️  Creating Apache configuration (.htaccess)...")
        
        htaccess_content = """# Research Streams Dashboard - Apache Configuration
# Generated for research.datasciencetech.ca

# Force HTTPS
RewriteEngine On
RewriteCond %{HTTPS} off
RewriteRule ^(.*)$ https://%{HTTP_HOST}%{REQUEST_URI} [L,R=301]

# Enable clean URLs
Options -MultiViews
RewriteCond %{REQUEST_FILENAME} !-f
RewriteCond %{REQUEST_FILENAME} !-d
RewriteRule ^([^.]+)$ $1.html [NC,L]

# Custom error pages
ErrorDocument 404 /index.html

# Enable compression for faster loading
<IfModule mod_deflate.c>
    AddOutputFilterByType DEFLATE text/html
    AddOutputFilterByType DEFLATE text/css
    AddOutputFilterByType DEFLATE application/javascript
    AddOutputFilterByType DEFLATE application/json
</IfModule>

# Browser caching for performance
<IfModule mod_expires.c>
    ExpiresActive On
    ExpiresByType text/html "access plus 1 hour"
    ExpiresByType text/css "access plus 1 month"
    ExpiresByType application/javascript "access plus 1 month"
    ExpiresByType image/png "access plus 1 year"
    ExpiresByType image/jpg "access plus 1 year"
    ExpiresByType image/jpeg "access plus 1 year"
</IfModule>

# Security headers
<IfModule mod_headers.c>
    Header always set X-Content-Type-Options "nosniff"
    Header always set X-Frame-Options "SAMEORIGIN"
    Header always set X-XSS-Protection "1; mode=block"
    Header always set Referrer-Policy "strict-origin-when-cross-origin"
</IfModule>

# Disable directory browsing
Options -Indexes
"""
        
        with open(self.deploy_dir / '.htaccess', 'w', encoding='utf-8') as f:
            f.write(htaccess_content)
        
        print("  ✅ .htaccess created with:")
        print("     - HTTPS redirect")
        print("     - Clean URLs")
        print("     - Compression enabled")
        print("     - Browser caching")
        print("     - Security headers")
        
        return True
    
    def create_robots_txt(self):
        """Create robots.txt for SEO."""
        print("\n🤖 Creating robots.txt for search engines...")
        
        robots_content = """# robots.txt for research.datasciencetech.ca
User-agent: *
Allow: /

# Sitemap
Sitemap: https://research.datasciencetech.ca/sitemap.xml

# Allow indexing of all research streams
Allow: /stream_*.html
Allow: /papers_database.html
Allow: /methodology.html
"""
        
        with open(self.deploy_dir / 'robots.txt', 'w', encoding='utf-8') as f:
            f.write(robots_content)
        
        print("  ✅ robots.txt created (SEO-friendly)")
        
        return True
    
    def create_sitemap(self):
        """Create XML sitemap for SEO."""
        print("\n🗺️  Creating sitemap.xml for SEO...")
        
        base_url = "https://research.datasciencetech.ca"
        today = datetime.now().strftime('%Y-%m-%d')
        
        sitemap_content = f"""<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
    <url>
        <loc>{base_url}/</loc>
        <lastmod>{today}</lastmod>
        <changefreq>monthly</changefreq>
        <priority>1.0</priority>
    </url>
    <url>
        <loc>{base_url}/all_streams.html</loc>
        <lastmod>{today}</lastmod>
        <changefreq>monthly</changefreq>
        <priority>0.9</priority>
    </url>
    <url>
        <loc>{base_url}/papers_database.html</loc>
        <lastmod>{today}</lastmod>
        <changefreq>monthly</changefreq>
        <priority>0.9</priority>
    </url>
    <url>
        <loc>{base_url}/methodology.html</loc>
        <lastmod>{today}</lastmod>
        <changefreq>yearly</changefreq>
        <priority>0.7</priority>
    </url>
"""
        
        # Add all stream pages
        for i in range(15):
            sitemap_content += f"""    <url>
        <loc>{base_url}/stream_{i}.html</loc>
        <lastmod>{today}</lastmod>
        <changefreq>monthly</changefreq>
        <priority>0.8</priority>
    </url>
"""
        
        sitemap_content += "</urlset>"
        
        with open(self.deploy_dir / 'sitemap.xml', 'w', encoding='utf-8') as f:
            f.write(sitemap_content)
        
        print("  ✅ sitemap.xml created with all pages")
        
        return True
    
    def create_deployment_readme(self):
        """Create deployment README."""
        print("\n📝 Creating deployment README...")
        
        readme_content = f"""# Research Streams Dashboard - Deployment Package

**Target Site:** https://research.datasciencetech.ca/
**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**Package Version:** 1.0

---

## 📦 Package Contents

### HTML Files ({len(list(self.deploy_dir.glob('*.html')))} total):
- index.html (main dashboard)
- all_streams.html (research streams overview)  
- papers_database.html (searchable papers database)
- methodology.html (technical documentation)
- stream_0.html to stream_14.html (15 individual stream pages)

### Configuration Files:
- .htaccess (Apache server configuration)
- robots.txt (search engine instructions)
- sitemap.xml (SEO sitemap)

---

## 🚀 DEPLOYMENT OPTIONS

### Option 1: cPanel File Manager (EASIEST - RECOMMENDED)

1. **Login to cPanel**
   - Go to your hosting provider's control panel
   - Usually: https://datasciencetech.ca:2083
   - Enter your hosting credentials

2. **Setup Subdomain** (if not already done)
   - Click "Subdomains" in cPanel
   - Subdomain: `research`
   - Domain: `datasciencetech.ca`
   - Document Root: `public_html/research`
   - Click "Create"

3. **Upload Files**
   - Click "File Manager"
   - Navigate to `public_html/research/`
   - Click "Upload"
   - Upload the ZIP file: `research_streams_dashboard.zip`
   - Right-click ZIP → "Extract"
   - Delete the ZIP file after extraction

4. **Set Permissions**
   - Select all files
   - Right-click → "Change Permissions"
   - Set to 644 (rw-r--r--)

5. **Test**
   - Visit: https://research.datasciencetech.ca/
   - All pages should load correctly!

---

### Option 2: FTP/SFTP Upload

1. **Get FTP Credentials**
   - From your hosting provider
   - Host: ftp.datasciencetech.ca (or server IP)
   - Username: Your cPanel username
   - Password: Your cPanel password
   - Port: 21 (FTP) or 22 (SFTP)

2. **Connect with FileZilla** (free FTP client)
   - Download: https://filezilla-project.org/
   - File → Site Manager → New Site
   - Enter your FTP credentials
   - Click "Connect"

3. **Upload Files**
   - Remote: Navigate to /public_html/research/
   - Local: Navigate to your deploy/ folder
   - Select all files in deploy/ folder
   - Drag and drop to upload
   - Wait for transfer to complete

4. **Verify**
   - All {len(list(self.deploy_dir.glob('*')))} files should be uploaded
   - Visit: https://research.datasciencetech.ca/

---

### Option 3: Command Line (Advanced)

Using scp (secure copy):
```bash
scp -r deploy/* username@datasciencetech.ca:/home/username/public_html/research/
```

Using rsync (recommended for updates):
```bash
rsync -avz --progress deploy/ username@datasciencetech.ca:/home/username/public_html/research/
```

---

## ✅ POST-DEPLOYMENT CHECKLIST

After uploading, verify:
- [ ] Main page loads: https://research.datasciencetech.ca/
- [ ] All 15 stream pages work
- [ ] Papers database search functions correctly
- [ ] Methodology page displays properly
- [ ] All DOI links open in new tabs
- [ ] DataScienceTech.ca attribution is visible
- [ ] Charts and visualizations render
- [ ] Mobile responsive (test on phone)
- [ ] HTTPS is enabled (padlock in browser)

---

## 🌐 YOUR LIVE URLS

Once deployed, your dashboard will be accessible at:

- **Main Dashboard:** https://research.datasciencetech.ca/
- **All Streams:** https://research.datasciencetech.ca/all_streams.html
- **Papers Database:** https://research.datasciencetech.ca/papers_database.html
- **Methodology:** https://research.datasciencetech.ca/methodology.html
- **Individual Streams:** https://research.datasciencetech.ca/stream_0.html (through stream_14.html)

---

## 🔧 TROUBLESHOOTING

### Issue: "Page not found" (404 error)
**Solution:**
- Check files are in correct directory
- Verify file permissions (should be 644)
- Clear browser cache (Ctrl+F5)

### Issue: Charts not displaying
**Solution:**
- Check internet connection (CDN access needed)
- Verify browser allows JavaScript
- Try different browser (Chrome, Firefox, Safari)

### Issue: Subdomain not working
**Solution:**
- Wait 24-48 hours for DNS propagation
- Verify subdomain created in cPanel
- Check nameservers are correct

### Issue: HTTPS not working
**Solution:**
- Install SSL certificate in cPanel (usually free with Let's Encrypt)
- Force HTTPS redirect (already in .htaccess)
- Contact hosting provider for SSL support

---

## 📊 OPTIONAL: Add Google Analytics

To track visitors, add this before `</head>` in index.html:

```html
<!-- Google Analytics -->
<script async src="https://www.googletagmanager.com/gtag/js?id=YOUR_GA_ID"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){{dataLayer.push(arguments);}}
  gtag('js', new Date());
  gtag('config', 'YOUR_GA_ID');
</script>
```

Replace `YOUR_GA_ID` with your Google Analytics tracking ID.

---

## 🆘 SUPPORT

If you need help:
1. **Hosting Provider Support** - For cPanel, FTP, subdomain setup
2. **FileZilla Documentation** - https://wiki.filezilla-project.org/
3. **Apache Documentation** - For .htaccess issues

---

## 📈 PERFORMANCE METRICS

Your dashboard is optimized for:
- ⚡ Fast loading (all static HTML)
- 📱 Mobile responsive
- 🔍 SEO-friendly (sitemap, robots.txt)
- 🔒 Secure (HTTPS, security headers)
- 💾 Browser caching enabled
- 📦 Compression enabled

---

## 🎉 SUCCESS!

Your Research Streams Discovery Dashboard is ready to go live!

**Next step:** Upload files using one of the methods above.

**Your live site:** https://research.datasciencetech.ca/

---

*Deployment Package | DataScienceTech.ca | Research Streams Discovery System*
*Package created: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
"""
        
        with open(self.deploy_dir / 'README.txt', 'w', encoding='utf-8') as f:
            f.write(readme_content)
        
        print("  ✅ Comprehensive README.txt created")
        
        return True
    
    def create_zip_package(self):
        """Create ZIP file for easy upload."""
        print("\n📦 Creating ZIP package for upload...")
        
        if self.zip_path.exists():
            self.zip_path.unlink()
        
        with zipfile.ZipFile(self.zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for file_path in self.deploy_dir.rglob('*'):
                if file_path.is_file():
                    arcname = file_path.relative_to(self.deploy_dir)
                    zipf.write(file_path, arcname)
                    
        file_size = self.zip_path.stat().st_size / (1024 * 1024)  # MB
        print(f"  ✅ ZIP created: {self.zip_path.name} ({file_size:.2f} MB)")
        
        return True
    
    def create_ftp_script(self):
        """Create PowerShell FTP upload script."""
        print("\n🔧 Creating automated FTP upload script...")
        
        ps_script = """# PowerShell FTP Upload Script for research.datasciencetech.ca
# 
# INSTRUCTIONS:
# 1. Edit the variables below with your FTP credentials
# 2. Run this script in PowerShell: .\\upload_via_ftp.ps1
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
"""
        
        with open('upload_via_ftp.ps1', 'w', encoding='utf-8') as f:
            f.write(ps_script)
        
        print("  ✅ PowerShell FTP script created: upload_via_ftp.ps1")
        print("     Edit the script with your FTP credentials and run it!")
        
        return True
    
    def print_deployment_summary(self):
        """Print comprehensive deployment summary."""
        print("\n" + "="*60)
        print("✅ DEPLOYMENT PACKAGE COMPLETE!")
        print("="*60)
        
        # Count files
        html_count = len(list(self.deploy_dir.glob('*.html')))
        total_count = len(list(self.deploy_dir.glob('*')))
        
        print(f"\n📁 Deployment Directory: {self.deploy_dir.absolute()}")
        print(f"📦 ZIP Package: {self.zip_path.absolute()}")
        print(f"📄 HTML Pages: {html_count}")
        print(f"📋 Total Files: {total_count}")
        
        # File size
        zip_size = self.zip_path.stat().st_size / (1024 * 1024)
        print(f"💾 ZIP Size: {zip_size:.2f} MB")
        
        print("\n" + "="*60)
        print("🚀 DEPLOYMENT OPTIONS")
        print("="*60)
        
        print("\n📌 OPTION 1: cPanel Upload (EASIEST)")
        print("   1. Login to your hosting cPanel")
        print("   2. Create subdomain: research.datasciencetech.ca")
        print("   3. Upload research_streams_dashboard.zip")
        print("   4. Extract in public_html/research/")
        print("   5. Visit: https://research.datasciencetech.ca/")
        
        print("\n📌 OPTION 2: FTP Upload (AUTOMATED)")
        print("   1. Edit upload_via_ftp.ps1 with your credentials")
        print("   2. Run: .\\upload_via_ftp.ps1")
        print("   3. Wait for upload to complete")
        print("   4. Visit: https://research.datasciencetech.ca/")
        
        print("\n📌 OPTION 3: FileZilla (MANUAL)")
        print("   1. Download FileZilla FTP client")
        print("   2. Connect to ftp.datasciencetech.ca")
        print("   3. Upload all files from deploy/ folder")
        print("   4. Visit: https://research.datasciencetech.ca/")
        
        print("\n" + "="*60)
        print("🌐 YOUR LIVE URLS (after deployment)")
        print("="*60)
        print("\n  Main: https://research.datasciencetech.ca/")
        print("  Papers: https://research.datasciencetech.ca/papers_database.html")
        print("  Streams: https://research.datasciencetech.ca/all_streams.html")
        print("  Methods: https://research.datasciencetech.ca/methodology.html")
        
        print("\n" + "="*60)
        print("✅ PACKAGE INCLUDES:")
        print("="*60)
        print("  ✅ All HTML pages optimized")
        print("  ✅ Apache .htaccess (HTTPS, compression, caching)")
        print("  ✅ robots.txt (SEO)")
        print("  ✅ sitemap.xml (SEO)")
        print("  ✅ Deployment README")
        print("  ✅ FTP upload script")
        print("  ✅ ZIP package ready")
        
        print("\n" + "="*60)
        print("📋 NEXT STEPS:")
        print("="*60)
        print("  1. Choose your deployment method (cPanel recommended)")
        print("  2. Upload files to your web server")
        print("  3. Test all pages work correctly")
        print("  4. Share your dashboard with the world!")
        
        print("\n" + "="*60)
        print("🎉 YOU'RE READY TO GO LIVE!")
        print("="*60)
        print()
    
    def run(self):
        """Run complete deployment preparation."""
        try:
            # Prepare files
            if not self.prepare_files():
                print("\n❌ Deployment preparation failed!")
                return False
            
            # Rename main file
            if not self.rename_main_file():
                print("\n⚠️  Warning: Could not rename main file")
            
            # Create configuration files
            self.create_htaccess()
            self.create_robots_txt()
            self.create_sitemap()
            
            # Create documentation
            self.create_deployment_readme()
            
            # Create upload tools
            self.create_zip_package()
            self.create_ftp_script()
            
            # Print summary
            self.print_deployment_summary()
            
            return True
            
        except Exception as e:
            print(f"\n❌ ERROR: {e}")
            import traceback
            traceback.print_exc()
            return False


def main():
    """Main deployment automation."""
    deployer = DeploymentAutomation()
    success = deployer.run()
    
    if success:
        print("✅ Deployment preparation successful!")
        print("📦 Ready to upload to research.datasciencetech.ca!")
        return 0
    else:
        print("❌ Deployment preparation failed!")
        return 1


if __name__ == "__main__":
    sys.exit(main())
