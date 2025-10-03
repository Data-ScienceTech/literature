# 🚀 Quick Deployment Guide to research.datasciencetech.ca

**Status:** ✅ All files ready in `deploy/` folder and `research_streams_dashboard.zip`

---

## ⚡ FASTEST METHOD: cPanel Upload (5 minutes)

### Step 1: Access Your Hosting
1. Go to your hosting provider's website
2. Login to **cPanel** (control panel)
   - Usually at: `https://datasciencetech.ca:2083`
   - Or: `https://yourhostingprovider.com/cpanel`

### Step 2: Create Subdomain (One-time setup)
1. In cPanel, find and click **"Subdomains"**
2. Enter the following:
   - **Subdomain:** `research`
   - **Domain:** `datasciencetech.ca` (select from dropdown)
   - **Document Root:** `public_html/research` (auto-fills)
3. Click **"Create"**
4. Wait 2-3 minutes for DNS to propagate

### Step 3: Upload Files
1. In cPanel, click **"File Manager"**
2. Navigate to `public_html/research/` folder
3. Click **"Upload"** button at the top
4. Select `research_streams_dashboard.zip` from your computer
5. Wait for upload to complete (should take ~30 seconds)

### Step 4: Extract Files
1. In File Manager, find `research_streams_dashboard.zip`
2. Right-click the ZIP file
3. Select **"Extract"**
4. Click **"Extract Files"** button
5. Wait for extraction to complete
6. **Delete the ZIP file** (right-click → Delete)

### Step 5: Verify & Launch! 🎉
1. Open your browser
2. Go to: **https://research.datasciencetech.ca/**
3. Your dashboard should be live!

---

## 🔧 Alternative: FTP Upload (Automated)

### Option A: Using PowerShell Script (Windows)

1. **Edit `upload_via_ftp.ps1`:**
   - Open the file in a text editor
   - Find lines 8-10:
     ```powershell
     $ftpServer = "ftp.datasciencetech.ca"
     $ftpUsername = "YOUR_FTP_USERNAME"    # ← Change this
     $ftpPassword = "YOUR_FTP_PASSWORD"    # ← Change this
     ```
   - Replace `YOUR_FTP_USERNAME` and `YOUR_FTP_PASSWORD` with your credentials
   - Save the file

2. **Run the script:**
   - Open PowerShell
   - Navigate to this folder
   - Run: `.\upload_via_ftp.ps1`
   - Wait for upload to complete

3. **Visit your site:**
   - Go to: https://research.datasciencetech.ca/

### Option B: Using FileZilla (Manual)

1. **Download FileZilla** (if you don't have it):
   - Go to: https://filezilla-project.org/
   - Download and install the **Client** version

2. **Get your FTP credentials:**
   - From your hosting provider's welcome email, or
   - In cPanel → "FTP Accounts" section
   - You need:
     - **Host:** `ftp.datasciencetech.ca` (or your server IP)
     - **Username:** Your cPanel username
     - **Password:** Your cPanel password
     - **Port:** 21

3. **Connect to your server:**
   - Open FileZilla
   - Click: File → Site Manager → New Site
   - Enter your credentials
   - Click "Connect"

4. **Upload files:**
   - **Left side:** Navigate to your `deploy/` folder
   - **Right side:** Navigate to `/public_html/research/`
   - Select all files in the `deploy/` folder
   - Drag them to the right side
   - Wait for upload to complete (progress bar at bottom)

5. **Visit your site:**
   - Go to: https://research.datasciencetech.ca/

---

## ✅ Post-Deployment Checklist

After uploading, test these:

- [ ] **Main page loads:** https://research.datasciencetech.ca/
- [ ] **Navigation works:** Click on different streams
- [ ] **Search works:** Try searching in the papers database
- [ ] **Charts display:** Verify visualizations show up
- [ ] **Mobile works:** Test on your phone
- [ ] **Links work:** Click a DOI link to verify it opens

---

## 🔍 Troubleshooting

### "This site can't be reached" or "DNS_PROBE_FINISHED_NXDOMAIN"
**Cause:** Subdomain DNS not propagated yet  
**Solution:** Wait 15-30 minutes, then try again. DNS can take up to 48 hours in rare cases.

### "404 Not Found"
**Cause:** Files not in correct location  
**Solution:** 
- Verify files are in `public_html/research/` folder
- Check that `index.html` exists (not `research_streams_dashboard.html`)
- Clear your browser cache (Ctrl+Shift+Delete)

### "403 Forbidden"
**Cause:** File permissions incorrect  
**Solution:**
- In File Manager, select all files
- Right-click → "Change Permissions"
- Set to **644** (or check: Read for Owner, Group, World; Write for Owner only)

### Charts not showing
**Cause:** JavaScript not loading or CDN blocked  
**Solution:**
- Check your internet connection
- Try a different browser
- Disable ad-blockers temporarily
- Check browser console (F12) for errors

### Can't find cPanel
**Solution:**
- Check your hosting provider's welcome email
- Contact your hosting provider's support
- Try: `https://datasciencetech.ca:2083`
- Or: `https://datasciencetech.ca/cpanel`

---

## 📞 Getting Help

### Your Hosting Provider
- **Best for:** cPanel access, FTP credentials, subdomain setup
- **Contact:** Check your hosting account for support options

### Common Hosting Providers
- **GoDaddy:** Login → My Products → Web Hosting → Manage
- **Bluehost:** Login → Hosting → cPanel
- **HostGator:** Login → Hosting → cPanel
- **SiteGround:** Login → Sites → Site Tools

---

## 🎯 What You Have Ready

```
deploy/
├── index.html                    ← Main dashboard (renamed)
├── all_streams.html              ← All research streams
├── papers_database.html          ← Searchable papers
├── methodology.html              ← Technical docs
├── stream_0.html ... stream_14.html  ← 15 individual streams
├── .htaccess                     ← Apache config (HTTPS, caching)
├── robots.txt                    ← SEO
├── sitemap.xml                   ← SEO sitemap
└── README.txt                    ← Full documentation

research_streams_dashboard.zip    ← All above files in one ZIP
upload_via_ftp.ps1               ← Automated FTP upload script
```

**Total:** 19 HTML pages + 4 config files = **23 files ready to deploy**

---

## 🌐 Your Live URLs (after deployment)

| Page | URL |
|------|-----|
| **Main Dashboard** | https://research.datasciencetech.ca/ |
| **All Streams** | https://research.datasciencetech.ca/all_streams.html |
| **Papers Database** | https://research.datasciencetech.ca/papers_database.html |
| **Methodology** | https://research.datasciencetech.ca/methodology.html |
| **Stream 0** | https://research.datasciencetech.ca/stream_0.html |
| ... | (through stream_14.html) |

---

## 🎉 You're Ready!

**Choose your method above and get your Research Streams Dashboard live in minutes!**

The hardest part is done - all files are prepared, optimized, and ready to upload. 🚀

---

*Last updated: October 3, 2025*
*Dashboard Version: 1.0*
*Total Papers Analyzed: 2,890*
*Research Streams: 15*
