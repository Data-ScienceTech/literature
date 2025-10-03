# 🚀 Deployment Guide - DataScienceTech.ca

## Complete guide to deploy your Research Streams Discovery Dashboard to datasciencetech.ca

---

## 📋 **Pre-Deployment Checklist**

### **Files to Deploy** (All in current directory)

#### **Core HTML Pages:**
- ✅ `research_streams_dashboard.html` - Main landing page
- ✅ `all_streams.html` - All research streams overview
- ✅ `papers_database.html` - Searchable papers database
- ✅ `methodology.html` - Technical documentation
- ✅ `stream_0.html` through `stream_14.html` - Individual stream pages (15 files)

#### **Optional Assets:**
- `data/` folder - Contains JSON and CSV files (optional, for downloads)
- `README.md` - Documentation (optional)

**Total: 19 HTML files** ready for deployment

---

## 🌐 **Deployment Options**

### **Option 1: Simple Static Hosting (Recommended)**

Your dashboard is 100% static HTML/CSS/JavaScript - no server-side code needed!

#### **A. Using cPanel File Manager** (Most Common)

1. **Login to your hosting control panel**
   - Go to `https://datasciencetech.ca/cpanel` (or your hosting provider's URL)
   - Enter your credentials

2. **Navigate to File Manager**
   - Click "File Manager" in cPanel
   - Navigate to `public_html/` directory

3. **Create a subdirectory** (recommended)
   ```
   public_html/research-streams/
   ```
   Or deploy to root: `public_html/`

4. **Upload all HTML files**
   - Click "Upload" button
   - Select all 19 HTML files
   - Wait for upload to complete

5. **Set permissions**
   - Select all uploaded files
   - Right-click → "Change Permissions"
   - Set to `644` (read for everyone, write for owner)

6. **Access your dashboard**
   - Main page: `https://datasciencetech.ca/research-streams/research_streams_dashboard.html`
   - Or rename to `index.html` for: `https://datasciencetech.ca/research-streams/`

#### **B. Using FTP/SFTP** (FileZilla, WinSCP, etc.)

1. **Get FTP credentials from your hosting provider**
   - Host: `ftp.datasciencetech.ca` or your server IP
   - Username: Your cPanel username
   - Password: Your cPanel password
   - Port: 21 (FTP) or 22 (SFTP)

2. **Connect with FileZilla** (Free FTP client)
   - Download: https://filezilla-project.org/
   - File → Site Manager → New Site
   - Enter your credentials
   - Connect

3. **Upload files**
   - Navigate to `public_html/research-streams/` on remote
   - Select all 19 HTML files from local
   - Drag and drop to upload

4. **Verify upload**
   - Check all files are present
   - Visit `https://datasciencetech.ca/research-streams/research_streams_dashboard.html`

---

### **Option 2: GitHub Pages (Free, Professional)**

Host on GitHub with custom domain - great for version control!

#### **Setup Steps:**

1. **Create GitHub repository**
   ```bash
   # In your literature_analyzer directory
   git init
   git add *.html
   git commit -m "Initial deployment of Research Streams Dashboard"
   ```

2. **Push to GitHub**
   ```bash
   # Create repo on github.com first, then:
   git remote add origin https://github.com/YOUR_USERNAME/research-streams.git
   git branch -M main
   git push -u origin main
   ```

3. **Enable GitHub Pages**
   - Go to repository Settings → Pages
   - Source: Deploy from branch `main`
   - Folder: `/ (root)`
   - Save

4. **Configure custom domain**
   - In GitHub Pages settings, add: `research.datasciencetech.ca`
   - Create CNAME file in repo with: `research.datasciencetech.ca`

5. **Update DNS settings** (at your domain registrar)
   ```
   Type: CNAME
   Name: research
   Value: YOUR_USERNAME.github.io
   TTL: 3600
   ```

6. **Wait for DNS propagation** (5-30 minutes)
   - Access at: `https://research.datasciencetech.ca`

---

### **Option 3: Netlify (Free, Fast, Easy)**

Modern hosting with automatic HTTPS and continuous deployment.

#### **Setup Steps:**

1. **Create Netlify account**
   - Go to https://netlify.com
   - Sign up (free tier is perfect)

2. **Deploy via drag-and-drop**
   - Click "Add new site" → "Deploy manually"
   - Drag your folder with all HTML files
   - Wait for deployment (30 seconds)

3. **Configure custom domain**
   - Site settings → Domain management
   - Add custom domain: `research.datasciencetech.ca`
   - Follow DNS configuration instructions

4. **Update DNS** (at your domain registrar)
   ```
   Type: CNAME
   Name: research
   Value: YOUR_SITE.netlify.app
   TTL: 3600
   ```

5. **Enable HTTPS**
   - Automatic with Netlify
   - Free SSL certificate

6. **Access your site**
   - `https://research.datasciencetech.ca`

---

## 🔧 **Quick Setup Script**

I'll create a deployment package for you:

```bash
# Run this to prepare deployment
python prepare_deployment.py
```

This will create a `deploy/` folder with:
- All HTML files
- Optimized structure
- README for hosting provider

---

## 📝 **Recommended URL Structure**

### **Option A: Subdirectory** (Easiest)
```
https://datasciencetech.ca/research-streams/
├── research_streams_dashboard.html (or index.html)
├── all_streams.html
├── papers_database.html
├── methodology.html
└── stream_0.html ... stream_14.html
```

### **Option B: Subdomain** (Most Professional)
```
https://research.datasciencetech.ca/
├── index.html (renamed from research_streams_dashboard.html)
├── streams.html (renamed from all_streams.html)
├── papers.html (renamed from papers_database.html)
├── methodology.html
└── stream_0.html ... stream_14.html
```

---

## 🎯 **Post-Deployment Steps**

### **1. Rename Main File** (Optional but recommended)
```bash
# Rename for cleaner URL
mv research_streams_dashboard.html index.html
```
Now accessible at: `https://datasciencetech.ca/research-streams/`

### **2. Create .htaccess** (for Apache servers)
```apache
# Enable clean URLs and HTTPS redirect
RewriteEngine On
RewriteCond %{HTTPS} off
RewriteRule ^(.*)$ https://%{HTTP_HOST}%{REQUEST_URI} [L,R=301]

# Custom error pages
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
```

### **3. Test All Pages**
- ✅ Main dashboard loads
- ✅ All 15 stream pages work
- ✅ Papers database search functions
- ✅ Methodology page displays
- ✅ All DOI links work
- ✅ DataScienceTech.ca links work
- ✅ Charts render correctly

### **4. SEO Optimization** (Optional)
Add to `<head>` of index.html:
```html
<meta name="description" content="AI-powered research streams discovery system analyzing 2,890 academic papers using SPECTER2 embeddings and Leiden clustering. Developed by DataScienceTech.ca">
<meta name="keywords" content="research analysis, bibliometrics, AI, machine learning, academic research, data science">
<meta property="og:title" content="Research Streams Discovery Dashboard">
<meta property="og:description" content="Explore 15 research streams from 2,890 academic papers">
<meta property="og:url" content="https://datasciencetech.ca/research-streams/">
<meta property="og:type" content="website">
```

---

## 🔒 **Security & Performance**

### **Security Checklist:**
- ✅ All external CDN links use HTTPS
- ✅ No sensitive data in HTML files
- ✅ No server-side code (pure static)
- ✅ All external links open in new tabs

### **Performance Optimization:**
- ✅ All CSS/JS from CDN (cached globally)
- ✅ Minimal file sizes (HTML only)
- ✅ No database queries (all data embedded)
- ✅ Fast loading times

---

## 📱 **Mobile Responsiveness**

Your dashboard is already mobile-responsive! Test on:
- Desktop browsers (Chrome, Firefox, Safari, Edge)
- Mobile devices (iOS Safari, Android Chrome)
- Tablets (iPad, Android tablets)

All layouts adapt automatically.

---

## 🆘 **Troubleshooting**

### **Issue: Pages not loading**
- Check file permissions (should be 644)
- Verify all files uploaded correctly
- Check browser console for errors (F12)

### **Issue: Charts not displaying**
- Ensure internet connection (CDN access needed)
- Check if Plotly.js CDN is accessible
- Try different browser

### **Issue: Links broken**
- Verify all HTML files in same directory
- Check file names match exactly (case-sensitive on Linux)
- Update any hardcoded paths if needed

### **Issue: Custom domain not working**
- Wait 24-48 hours for DNS propagation
- Verify DNS settings at registrar
- Clear browser cache
- Try incognito/private mode

---

## 📊 **Analytics Setup** (Optional)

### **Add Google Analytics:**
```html
<!-- Add before </head> in all HTML files -->
<script async src="https://www.googletagmanager.com/gtag/js?id=YOUR_GA_ID"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){dataLayer.push(arguments);}
  gtag('js', new Date());
  gtag('config', 'YOUR_GA_ID');
</script>
```

Track:
- Page views
- Search queries
- Paper clicks
- Stream exploration

---

## 🎉 **Launch Checklist**

Before going live:
- [ ] All 19 HTML files uploaded
- [ ] Main page accessible
- [ ] All internal links working
- [ ] DOI links opening correctly
- [ ] DataScienceTech.ca attribution visible
- [ ] Mobile responsive on phone
- [ ] HTTPS enabled (if using custom domain)
- [ ] DNS configured (if using subdomain)
- [ ] Tested on multiple browsers
- [ ] Analytics configured (optional)

---

## 🚀 **Quick Start Commands**

### **For cPanel:**
1. Login to cPanel
2. File Manager → public_html
3. Create folder: `research-streams`
4. Upload all 19 HTML files
5. Visit: `https://datasciencetech.ca/research-streams/research_streams_dashboard.html`

### **For FTP:**
```bash
# Using command line FTP
ftp ftp.datasciencetech.ca
# Enter username and password
cd public_html/research-streams
mput *.html
quit
```

### **For Git deployment:**
```bash
git add *.html
git commit -m "Deploy Research Streams Dashboard"
git push origin main
```

---

## 📞 **Support Resources**

- **Your hosting provider's documentation**
- **FileZilla Guide**: https://wiki.filezilla-project.org/
- **GitHub Pages**: https://pages.github.com/
- **Netlify Docs**: https://docs.netlify.com/

---

## ✅ **Success!**

Once deployed, share your dashboard:
- `https://datasciencetech.ca/research-streams/`
- Or: `https://research.datasciencetech.ca/`

**Your world-class research discovery system is now live!** 🎊

---

*Deployment Guide | DataScienceTech.ca | Research Streams Discovery System*
