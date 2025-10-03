# 🚀 Automated Upload Guide

## Overview - 3 Ways to Upload Your Dashboard

You now have **fully automated upload capabilities** for deploying to **research.datasciencetech.ca**!

---

## 🎯 Quick Start (Choose One Method)

### Method 1️⃣: One-Click Complete Deployment (EASIEST!)

**Single command does everything: prepare files + upload**

```powershell
python deploy_complete.py
```

**What it does:**
1. ✅ Checks all required files exist
2. ✅ Runs deployment preparation (`deploy_to_web.py`)
3. ✅ Lets you choose upload method (Python or PowerShell)
4. ✅ Uploads files to your server
5. ✅ Shows verification checklist

**Perfect for:** First-time deployment and regular updates

---

### Method 2️⃣: Python FTP Upload (Cross-Platform)

**Interactive Python script with credential management**

```powershell
python auto_upload.py
```

**Features:**
- ✅ Interactive credential setup (asks for FTP details)
- ✅ Saves credentials securely for reuse
- ✅ Tests connection before upload
- ✅ Progress tracking for each file
- ✅ Creates remote directories if needed
- ✅ Shows verification checklist

**Perfect for:** When you want Python-based automation

---

### Method 3️⃣: PowerShell Upload (Windows Enhanced)

**Enhanced PowerShell script with better UI**

```powershell
.\upload_interactive.ps1
```

**Features:**
- ✅ Colorful, user-friendly interface
- ✅ Credential management with secure input
- ✅ Connection testing
- ✅ Upload progress with file sizes
- ✅ Option to open browser after upload
- ✅ Comprehensive error handling

**Perfect for:** Windows users who prefer PowerShell

---

## 📋 Detailed Instructions

### 🔥 Method 1: One-Click Deployment

#### Step 1: Run the script
```powershell
python deploy_complete.py
```

#### Step 2: Follow prompts
The script will:
1. Check if you have all required HTML files
2. Ask if you're ready to deploy (type `y`)
3. Prepare deployment package (19 HTML files + configs)
4. Ask you to choose upload method:
   - Option 1: Python FTP (recommended)
   - Option 2: PowerShell FTP
   - Option 3: Skip (manual upload)

#### Step 3: Enter FTP credentials (first time only)
When prompted, enter:
- **FTP Server:** `ftp.datasciencetech.ca` (or your hosting FTP address)
- **Username:** Your cPanel FTP username
- **Password:** Your FTP password (hidden input)
- **Port:** `21` (or press Enter for default)
- **Remote path:** `/public_html/research/` (or your target directory)

#### Step 4: Wait for upload
The script will:
- Test connection
- Upload all 23 files
- Show progress for each file
- Display success/failure count

#### Step 5: Verify
Visit https://research.datasciencetech.ca/ and test!

---

### 🐍 Method 2: Python Upload Only

If you've already prepared files (ran `deploy_to_web.py`):

```powershell
python auto_upload.py
```

**First-time setup:**
- Script asks for FTP credentials
- Option to save credentials to `upload_config.json`
- Tests connection before proceeding

**Subsequent runs:**
- Detects saved credentials
- Asks if you want to use them
- Quick upload with one confirmation

**What it uploads:**
All files from `deploy/` folder to your server

---

### 💻 Method 3: PowerShell Upload Only

For Windows users with PowerShell:

```powershell
.\upload_interactive.ps1
```

**Interactive features:**
- Beautiful colored output
- Secure password input (hidden)
- Progress bars and file sizes
- Opens browser when done
- Better error messages

**Same functionality as Python version, just prettier!**

---

## 🔐 Credential Management

### Where to find your FTP credentials?

**Option A: Hosting Control Panel (cPanel)**
1. Login to your hosting account
2. Go to cPanel
3. Look for "FTP Accounts" section
4. Your main account credentials are usually shown
5. Or create a new FTP account for this project

**Option B: Hosting Welcome Email**
- Check email from your hosting provider
- Look for "FTP Login Details"
- Usually sent when you first signed up

**Common FTP Settings:**
```
Host: ftp.datasciencetech.ca
Username: your_cpanel_username
Password: your_cpanel_password (or FTP-specific password)
Port: 21 (standard FTP)
Remote Path: /public_html/research/
```

### Saved Credentials

Both Python and PowerShell scripts can save credentials to:
- `upload_config.json` (Python)
- `upload_config.json` (PowerShell)

**Security note:** Passwords are stored in plain text locally. Only save if you trust your computer security.

To reset credentials:
```powershell
# Delete the config file
Remove-Item upload_config.json

# Next run will ask for credentials again
```

---

## 🔄 Update Your Dashboard

When you make changes and want to update the live site:

### Quick Update
```powershell
# One command to prepare and upload
python deploy_complete.py
```

### Manual Steps
```powershell
# 1. Prepare new package
python deploy_to_web.py

# 2. Upload new files
python auto_upload.py
# OR
.\upload_interactive.ps1
```

Files with the same name will be overwritten on the server.

---

## 🧪 Testing Connection

### Test FTP connection without uploading:

**Python:**
```python
python -c "import ftplib; ftp = ftplib.FTP('ftp.datasciencetech.ca'); ftp.login('username', 'password'); print('Connected!'); ftp.quit()"
```

**PowerShell:**
```powershell
# Built into upload_interactive.ps1
# Just run it and it tests first
.\upload_interactive.ps1
```

---

## 📊 Upload Progress

### What you'll see during upload:

```
============================================================
📤 UPLOADING FILES TO RESEARCH.DATASCIENCETECH.CA
============================================================

📋 Found 23 files to upload
🎯 Target: ftp.datasciencetech.ca/public_html/research/

Proceed with upload? (y/n): y

🔌 Connecting to ftp.datasciencetech.ca...
✅ Connected!

📤 Uploading files...
────────────────────────────────────────────────────────────
📄 index.html (45.23 KB)... ✅
📄 all_streams.html (38.91 KB)... ✅
📄 papers_database.html (156.78 KB)... ✅
📄 methodology.html (23.45 KB)... ✅
📄 stream_0.html (34.12 KB)... ✅
...
────────────────────────────────────────────────────────────

✅ Upload Complete! All 23 files uploaded successfully!
```

---

## ❌ Troubleshooting

### Connection Failed

**Error:** `Connection refused` or `Name or service not known`

**Solutions:**
- Check FTP server address (e.g., `ftp.datasciencetech.ca`)
- Try using server IP instead of domain name
- Check if your hosting uses custom FTP port
- Verify firewall isn't blocking FTP (port 21)

### Login Failed

**Error:** `530 Login authentication failed`

**Solutions:**
- Double-check username and password
- Try logging into cPanel first (validates credentials)
- Check if account is active
- Contact hosting provider if unsure

### Directory Not Found

**Error:** `550 No such file or directory`

**Solutions:**
- The scripts will try to create directories automatically
- Common paths:
  - `/public_html/research/`
  - `/home/username/public_html/research/`
  - `/www/research/`
- Check with hosting provider for exact path

### Timeout Errors

**Error:** `Timeout error` or `Connection timed out`

**Solutions:**
- Check your internet connection
- Try again (temporary network issue)
- Increase timeout in script (edit `request.Timeout = 30000`)
- Use passive mode (already enabled in scripts)

### Permission Denied

**Error:** `550 Permission denied`

**Solutions:**
- Ensure remote directory has write permissions
- Check FTP user has upload rights
- Try creating directory in cPanel first
- Contact hosting support

---

## 🎛️ Advanced Options

### Upload to Different Directory

Edit your `upload_config.json`:
```json
{
  "host": "ftp.datasciencetech.ca",
  "username": "your_username",
  "password": "your_password",
  "port": "21",
  "remotePath": "/public_html/different_folder/"
}
```

### Use SFTP Instead of FTP

The current scripts use FTP. For SFTP (more secure):

**Install pysftp:**
```powershell
pip install pysftp
```

**Use an SFTP client:**
- WinSCP (Windows)
- Cyberduck (Mac/Windows)
- FileZilla (supports SFTP too)

Port for SFTP: `22` (instead of 21)

---

## 📁 What Gets Uploaded

All files from `deploy/` folder (23 total):

### HTML Files (19)
- index.html (main dashboard)
- all_streams.html
- papers_database.html
- methodology.html
- stream_0.html through stream_14.html (15 files)

### Configuration Files (4)
- .htaccess (Apache server config)
- robots.txt (SEO)
- sitemap.xml (SEO)
- README.txt (documentation)

**Total size:** ~0.69 MB

---

## ✅ Verification Checklist

After upload, test these:

### Critical Tests
- [ ] https://research.datasciencetech.ca/ loads
- [ ] Navigation menu works
- [ ] Papers database search works
- [ ] Charts display correctly
- [ ] Mobile responsive (test on phone)

### All Pages
- [ ] Main dashboard (/)
- [ ] All streams (/all_streams.html)
- [ ] Papers database (/papers_database.html)
- [ ] Methodology (/methodology.html)
- [ ] Stream 0-14 (/stream_N.html)

### SEO Files
- [ ] Sitemap accessible (/sitemap.xml)
- [ ] Robots.txt accessible (/robots.txt)

---

## 🚀 Quick Reference Commands

```powershell
# Complete deployment (prepare + upload)
python deploy_complete.py

# Just prepare files
python deploy_to_web.py

# Just upload (Python)
python auto_upload.py

# Just upload (PowerShell)
.\upload_interactive.ps1

# Reset credentials
Remove-Item upload_config.json
```

---

## 💡 Pro Tips

1. **Save Credentials:** Say "yes" when asked to save - makes updates super fast!

2. **Test First:** All scripts test connection before uploading anything

3. **Manual Backup:** Keep `research_streams_dashboard.zip` as backup

4. **Quick Updates:** After making changes, just run `deploy_complete.py` again

5. **Check Logs:** Scripts show exactly which files uploaded successfully

6. **Browser Cache:** After upload, hard refresh (Ctrl+F5) to see changes

---

## 🎉 Success!

Once uploaded, your dashboard is live at:
- **https://research.datasciencetech.ca/**

Share it with the world! 🌍

---

**Questions?** Check the other documentation:
- `QUICK_DEPLOY_GUIDE.md` - Deployment basics
- `DEPLOYMENT_CHECKLIST.txt` - Testing checklist
- `DEPLOYMENT_GUIDE.md` - Comprehensive guide

---

*Last updated: October 3, 2025*
*Dashboard Version: 1.0*
*Automated Upload: Fully Operational! 🚀*
