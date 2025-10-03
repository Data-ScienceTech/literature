# 🚀 Deploying to Squarespace - research.datasciencetech.ca

## Important: Squarespace Limitations

**Squarespace does NOT support:**
- ❌ FTP/SFTP upload
- ❌ Custom HTML file hosting (for most plans)
- ❌ Direct file system access
- ❌ Multiple HTML pages as static files

**What Squarespace DOES support:**
- ✅ Code injection (for single-page dashboards)
- ✅ Custom domain mapping
- ✅ External hosting with iframe embedding
- ✅ Link to externally hosted dashboard

---

## 🎯 Recommended Solutions for Your Dashboard

### Option 1: External Hosting + Squarespace Link ⭐ **RECOMMENDED**

**Best approach for your multi-page dashboard:**

1. **Host your dashboard elsewhere** (free options available):
   - GitHub Pages (free, easy)
   - Netlify (free, drag & drop)
   - Vercel (free, excellent for static sites)
   - Cloudflare Pages (free, fast CDN)

2. **Link from Squarespace:**
   - Create a button/link on your Squarespace site
   - Point to: `https://yourusername.github.io/research-streams/`
   - Or use custom subdomain: `research.datasciencetech.ca`

**Advantages:**
- ✅ Full control over your dashboard
- ✅ Multiple HTML pages work perfectly
- ✅ Free hosting
- ✅ Easy updates
- ✅ Professional custom domain

---

### Option 2: GitHub Pages (FREE & EASY) ⭐

**Perfect for your dashboard! Here's how:**

#### Step 1: Create GitHub Repository
```powershell
# In your project folder
cd c:\Users\carlo\Dropbox\literature_analyzer

# Initialize git (if not already)
git init

# Create .gitignore
echo "*.pyc
__pycache__/
*.npy
upload_config.json" > .gitignore

# Add files
git add deploy/*
git commit -m "Add research streams dashboard"
```

#### Step 2: Push to GitHub
1. Go to https://github.com/new
2. Create repository: `research-streams`
3. Push your code:
```powershell
git remote add origin https://github.com/YOUR_USERNAME/research-streams.git
git branch -M main
git push -u origin main
```

#### Step 3: Enable GitHub Pages
1. Go to repository Settings
2. Click "Pages" in sidebar
3. Source: Deploy from branch → `main` → `/ (root)`
4. Click Save
5. Your site will be live at: `https://YOUR_USERNAME.github.io/research-streams/`

#### Step 4: Custom Domain (Optional)
1. In GitHub Pages settings, add custom domain: `research.datasciencetech.ca`
2. In Squarespace DNS settings:
   - Add CNAME record:
     - Host: `research`
     - Points to: `YOUR_USERNAME.github.io`
3. Wait 15-30 minutes for DNS propagation

**Your dashboard will be live at: research.datasciencetech.ca**

---

### Option 3: Netlify Drop (EASIEST!) ⭐

**Drag and drop deployment:**

#### Steps:
1. Go to https://app.netlify.com/drop
2. Drag your `research_streams_dashboard.zip` file
3. Wait for upload (30 seconds)
4. Site is live instantly at: `random-name.netlify.app`

#### Custom Domain:
1. In Netlify: Site settings → Domain management
2. Add custom domain: `research.datasciencetech.ca`
3. In Squarespace DNS:
   - Add CNAME record:
     - Host: `research`
     - Points to: `your-site.netlify.app`

**Done! Dashboard live with HTTPS automatically!**

---

### Option 4: Embed in Squarespace (Limited)

**For single-page dashboards only:**

If you combine all streams into ONE page:

1. In Squarespace: Add a "Code Block"
2. Paste your HTML
3. Limitations:
   - ❌ Only works for single page
   - ❌ Your dashboard has 19 pages
   - ❌ JavaScript may be restricted
   - ❌ Not recommended for complex dashboards

**Not recommended for your multi-page dashboard.**

---

## 🚀 RECOMMENDED: Automated GitHub Pages Deployment

I can create a script that automates GitHub Pages deployment!

### Features:
- ✅ One-click deployment to GitHub
- ✅ Automatic GitHub Pages setup
- ✅ Custom domain configuration
- ✅ Free hosting forever
- ✅ Easy updates (git push)
- ✅ HTTPS included automatically
- ✅ Fast CDN delivery

### Would you like me to create this automation?

---

## 🌐 Custom Domain Setup (Squarespace DNS)

Once you choose a hosting option (GitHub Pages, Netlify, etc.):

### In Squarespace:
1. Go to Settings → Domains → DNS Settings
2. Add CNAME Record:
   - **Host:** `research`
   - **Points to:** (depends on hosting):
     - GitHub Pages: `YOUR_USERNAME.github.io`
     - Netlify: `your-site.netlify.app`
     - Vercel: `your-site.vercel.app`
3. Save and wait 15-30 minutes

### Your dashboard will be accessible at:
`https://research.datasciencetech.ca`

---

## 💡 Comparison of Hosting Options

| Platform | Cost | Ease | Custom Domain | HTTPS | Updates |
|----------|------|------|---------------|-------|---------|
| **GitHub Pages** | FREE | Easy | ✅ Yes | ✅ Auto | Git push |
| **Netlify** | FREE | Easiest | ✅ Yes | ✅ Auto | Drag & drop |
| **Vercel** | FREE | Easy | ✅ Yes | ✅ Auto | Git push |
| **Cloudflare Pages** | FREE | Easy | ✅ Yes | ✅ Auto | Git push |
| **Traditional FTP** | Paid | Hard | ✅ Yes | Manual | FTP upload |
| **Squarespace Direct** | Paid | N/A | ✅ Yes | ✅ Yes | ❌ Not supported |

---

## 🎯 My Recommendation for You

### Best Solution: **GitHub Pages** or **Netlify**

**GitHub Pages if:**
- You're comfortable with git
- Want version control
- Plan to make frequent updates
- Want professional workflow

**Netlify if:**
- You want drag-and-drop simplicity
- Don't want to learn git
- Want instant deployment
- Prefer web interface

**Both are:**
- ✅ 100% FREE
- ✅ Support custom domains
- ✅ Include HTTPS automatically
- ✅ Have global CDN (fast worldwide)
- ✅ Perfect for your dashboard

---

## 🚀 Next Steps

### I can create automated deployment scripts for:

1. **GitHub Pages deployment** (git-based, professional)
2. **Netlify deployment** (API-based, drag-and-drop)
3. **Manual preparation for Netlify Drop** (simplest)

### Which would you prefer?

Let me know and I'll create the automation scripts!

---

## 📞 Questions?

**Q: Can I use Squarespace directly?**
A: Not for multi-page dashboards. Squarespace is designed for their page builder, not custom HTML applications.

**Q: Will the FTP scripts work?**
A: No, Squarespace doesn't support FTP. You need external hosting.

**Q: Is GitHub Pages really free?**
A: Yes! Forever. Perfect for static sites like your dashboard.

**Q: How do I update my dashboard later?**
A: 
- GitHub Pages: `git push` (automated)
- Netlify: Drag new files to web interface
- Both support automated deployment scripts

**Q: What about the custom domain?**
A: Works perfectly with all free hosting options. Add CNAME in Squarespace DNS.

---

## 🎊 Summary

**Your Squarespace account is perfect for your main website, but your Research Streams Dashboard needs external hosting.**

**Recommended workflow:**
1. Deploy dashboard to GitHub Pages or Netlify (FREE)
2. Set up custom domain: `research.datasciencetech.ca`
3. Link from your main Squarespace site
4. Update easily whenever needed

**Let me know which hosting option you prefer, and I'll create the automation scripts!** 🚀
