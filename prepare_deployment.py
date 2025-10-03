"""
Prepare deployment package for datasciencetech.ca
"""

import os
import shutil
from pathlib import Path
import zipfile

def prepare_deployment():
    """Create deployment-ready package."""
    print("🚀 Preparing deployment for datasciencetech.ca...")
    
    # Create deployment directory
    deploy_dir = Path('deploy')
    if deploy_dir.exists():
        shutil.rmtree(deploy_dir)
    deploy_dir.mkdir()
    
    # List of files to deploy
    html_files = [
        'research_streams_dashboard.html',
        'all_streams.html', 
        'papers_database.html',
        'methodology.html'
    ]
    
    # Add all stream files
    for i in range(15):
        html_files.append(f'stream_{i}.html')
    
    # Copy HTML files
    copied_files = []
    for file in html_files:
        if Path(file).exists():
            shutil.copy2(file, deploy_dir / file)
            copied_files.append(file)
            print(f"✅ Copied {file}")
        else:
            print(f"❌ Missing {file}")
    
    # Rename main file to index.html for cleaner URLs
    main_file = deploy_dir / 'research_streams_dashboard.html'
    if main_file.exists():
        main_file.rename(deploy_dir / 'index.html')
        print("✅ Renamed main file to index.html")
    
    # Create .htaccess for Apache servers
    htaccess_content = """# Research Streams Dashboard - Apache Configuration
RewriteEngine On

# Force HTTPS
RewriteCond %{HTTPS} off
RewriteRule ^(.*)$ https://%{HTTP_HOST}%{REQUEST_URI} [L,R=301]

# Clean URLs
RewriteCond %{REQUEST_FILENAME} !-f
RewriteCond %{REQUEST_FILENAME} !-d
RewriteRule ^([^.]+)$ $1.html [NC,L]

# Custom error page
ErrorDocument 404 /research-streams/index.html

# Enable compression
<IfModule mod_deflate.c>
    AddOutputFilterByType DEFLATE text/html text/css application/javascript
</IfModule>

# Browser caching
<IfModule mod_expires.c>
    ExpiresActive On
    ExpiresByType text/html "access plus 1 hour"
    ExpiresByType text/css "access plus 1 month"
    ExpiresByType application/javascript "access plus 1 month"
</IfModule>

# Security headers
<IfModule mod_headers.c>
    Header always set X-Content-Type-Options nosniff
    Header always set X-Frame-Options DENY
    Header always set X-XSS-Protection "1; mode=block"
</IfModule>
"""
    
    with open(deploy_dir / '.htaccess', 'w', encoding='utf-8') as f:
        f.write(htaccess_content)
    print("✅ Created .htaccess file")
    
    # Create deployment README
    readme_content = f"""# Research Streams Dashboard - Deployment Package

## Quick Deploy to datasciencetech.ca

### Files Included:
- index.html (main dashboard)
- all_streams.html (research streams overview)  
- papers_database.html (searchable papers)
- methodology.html (technical documentation)
- stream_0.html to stream_14.html (individual streams)
- .htaccess (Apache configuration)

Total: {len(copied_files) + 1} files ready for deployment

### Deployment Options:

#### Option 1: cPanel File Manager (Easiest)
1. Login to your hosting control panel
2. Go to File Manager → public_html
3. Create folder: research-streams
4. Upload all files from this deploy/ folder
5. Visit: https://datasciencetech.ca/research-streams/

#### Option 2: FTP Upload
1. Connect to ftp.datasciencetech.ca
2. Navigate to public_html/research-streams/
3. Upload all files from this deploy/ folder
4. Set permissions to 644 for all files

#### Option 3: Subdomain (Most Professional)
1. Create subdomain: research.datasciencetech.ca
2. Point to a folder (e.g., public_html/research/)
3. Upload all files to that folder
4. Visit: https://research.datasciencetech.ca/

### Post-Deployment:
- Test all pages load correctly
- Verify search functionality works
- Check all DOI links open properly
- Confirm DataScienceTech.ca attribution visible

### Support:
Contact your hosting provider if you need help with:
- Creating subdomains
- Setting up FTP access
- Configuring DNS settings

Generated: {Path.cwd()}
Dashboard ready for datasciencetech.ca deployment!
"""
    
    with open(deploy_dir / 'DEPLOY_README.txt', 'w', encoding='utf-8') as f:
        f.write(readme_content)
    print("✅ Created deployment README")
    
    # Create ZIP file for easy upload
    zip_path = Path('research_streams_dashboard.zip')
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for file_path in deploy_dir.rglob('*'):
            if file_path.is_file():
                arcname = file_path.relative_to(deploy_dir)
                zipf.write(file_path, arcname)
    
    print(f"✅ Created ZIP package: {zip_path}")
    
    # Summary
    print(f"\n🎉 DEPLOYMENT PACKAGE READY!")
    print(f"📁 Files prepared in: {deploy_dir.absolute()}")
    print(f"📦 ZIP package: {zip_path.absolute()}")
    print(f"📄 Total files: {len(list(deploy_dir.glob('*')))}")
    
    print(f"\n🚀 NEXT STEPS:")
    print(f"1. Login to your datasciencetech.ca hosting control panel")
    print(f"2. Go to File Manager → public_html")
    print(f"3. Create folder: research-streams")
    print(f"4. Upload the ZIP file and extract, OR upload all files from deploy/ folder")
    print(f"5. Visit: https://datasciencetech.ca/research-streams/")
    
    print(f"\n🌐 Your dashboard will be live at:")
    print(f"   Main: https://datasciencetech.ca/research-streams/")
    print(f"   Papers: https://datasciencetech.ca/research-streams/papers_database.html")
    print(f"   Methodology: https://datasciencetech.ca/research-streams/methodology.html")
    
    return deploy_dir, zip_path

def create_upload_instructions():
    """Create detailed upload instructions."""
    instructions = """
🚀 UPLOAD INSTRUCTIONS FOR DATASCIENCETECH.CA

=== METHOD 1: cPanel File Manager (Recommended) ===

1. LOGIN TO CPANEL
   - Go to your hosting provider's control panel
   - Usually: https://datasciencetech.ca:2083 or similar
   - Enter your username and password

2. OPEN FILE MANAGER
   - Click "File Manager" icon
   - Navigate to "public_html" folder

3. CREATE DIRECTORY
   - Click "New Folder" 
   - Name it: research-streams
   - Double-click to enter the folder

4. UPLOAD FILES
   - Click "Upload" button
   - Select "research_streams_dashboard.zip" 
   - Wait for upload to complete
   - Right-click the ZIP file → "Extract"
   - Delete the ZIP file after extraction

5. TEST YOUR SITE
   - Visit: https://datasciencetech.ca/research-streams/
   - All pages should load correctly

=== METHOD 2: FTP Upload ===

1. GET FTP CREDENTIALS
   - From your hosting provider
   - Host: ftp.datasciencetech.ca (or your server IP)
   - Username: Your cPanel username  
   - Password: Your cPanel password

2. DOWNLOAD FILEZILLA (Free FTP Client)
   - https://filezilla-project.org/download.php
   - Install and open

3. CONNECT TO SERVER
   - File → Site Manager → New Site
   - Enter your FTP credentials
   - Click "Connect"

4. NAVIGATE AND UPLOAD
   - Remote side: Go to public_html/research-streams/
   - Local side: Go to your deploy/ folder
   - Select all HTML files
   - Drag from local to remote side

5. SET PERMISSIONS
   - Select all uploaded files
   - Right-click → "File permissions"
   - Set to 644 (read for all, write for owner)

=== METHOD 3: Subdomain Setup (Most Professional) ===

1. CREATE SUBDOMAIN
   - In cPanel, click "Subdomains"
   - Subdomain: research
   - Domain: datasciencetech.ca
   - Document Root: public_html/research
   - Click "Create"

2. UPLOAD FILES
   - Navigate to public_html/research/
   - Upload all files from deploy/ folder
   - Rename index.html if needed

3. ACCESS YOUR SITE
   - https://research.datasciencetech.ca/
   - Much cleaner URL!

=== TROUBLESHOOTING ===

❌ "Page not found" error:
   - Check file permissions (should be 644)
   - Verify files uploaded to correct directory
   - Clear browser cache

❌ Charts not loading:
   - Check internet connection
   - Verify CDN access (Plotly.js, Font Awesome)
   - Try different browser

❌ Links broken:
   - Ensure all HTML files in same directory
   - Check file names match exactly
   - Verify case sensitivity (Linux servers)

=== SUPPORT ===

Contact your hosting provider if you need help with:
- Accessing cPanel
- Setting up FTP
- Creating subdomains
- DNS configuration

Your Research Streams Dashboard is ready to go live! 🎉
"""
    
    with open('UPLOAD_INSTRUCTIONS.txt', 'w', encoding='utf-8') as f:
        f.write(instructions)
    
    print("✅ Created detailed upload instructions")

if __name__ == "__main__":
    deploy_dir, zip_path = prepare_deployment()
    create_upload_instructions()
    
    print(f"\n📋 SUMMARY:")
    print(f"✅ Deployment package ready")
    print(f"✅ ZIP file created for easy upload") 
    print(f"✅ Instructions provided")
    print(f"✅ All {len(list(deploy_dir.glob('*.html')))} HTML pages included")
    print(f"✅ Apache .htaccess configuration included")
    
    print(f"\n🎯 YOU'RE READY TO DEPLOY!")
    print(f"Just upload the files and your dashboard will be live at datasciencetech.ca! 🚀")
