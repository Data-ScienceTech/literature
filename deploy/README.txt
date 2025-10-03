# Research Streams Dashboard - Deployment Package

**Target Site:** https://research.datasciencetech.ca/
**Generated:** 2025-10-03 11:59:40
**Package Version:** 1.0

---

## 📦 Package Contents

### HTML Files (19 total):
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
   - All 22 files should be uploaded
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
  function gtag(){dataLayer.push(arguments);}
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
*Package created: 2025-10-03 11:59:40*
