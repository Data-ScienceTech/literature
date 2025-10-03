# 🎯 Netlify Deployment - Easiest Option!

## Why Netlify for Squarespace Users?

Since **Squarespace doesn't support FTP or custom HTML files**, **Netlify** is the **perfect solution**!

---

## ✨ Benefits of Netlify

✅ **100% FREE** - Forever, for static sites  
✅ **Drag & Drop** - No coding, no command line  
✅ **Instant deployment** - Live in 30 seconds  
✅ **HTTPS included** - Automatic SSL certificate  
✅ **Custom domain support** - research.datasciencetech.ca  
✅ **Global CDN** - Fast worldwide delivery  
✅ **Easy updates** - Just drag new files  

---

## 🚀 Quick Deployment (3 Minutes!)

### Step 1: Go to Netlify Drop
Open in your browser:
```
https://app.netlify.com/drop
```

*No account required for first deployment!*

### Step 2: Upload Your Dashboard
1. Find `research_streams_dashboard.zip` in your folder
2. **Drag and drop** the ZIP file onto the Netlify Drop page
3. Wait 30 seconds for upload

### Step 3: Your Site is Live!
Netlify gives you a URL like:
```
https://random-name-12345.netlify.app
```

**That's it! Your dashboard is live!** 🎉

Test it: Click the link to see your dashboard.

---

## 🌐 Add Custom Domain (research.datasciencetech.ca)

### Step 1: Create Netlify Account (Free)
1. Click "Sign up" on Netlify
2. Use Google/GitHub login (easiest)
3. Find your deployed site in the dashboard

### Step 2: Add Custom Domain in Netlify
1. Go to your site in Netlify
2. Click **"Domain settings"**
3. Click **"Add custom domain"**
4. Enter: `research.datasciencetech.ca`
5. Click **"Verify"**
6. Netlify will show DNS instructions

### Step 3: Configure DNS in Squarespace
1. Login to Squarespace
2. Go to **Settings** → **Domains** → **DNS Settings**
3. Click **"Add Record"**
4. Select **"CNAME Record"**
5. Enter:
   - **Host:** `research`
   - **Data:** `your-site.netlify.app` (from Netlify)
   - **TTL:** Automatic
6. Click **"Add"**

### Step 4: Wait for DNS Propagation
- Usually takes 15-30 minutes
- Can take up to 48 hours in rare cases
- Test by visiting: `https://research.datasciencetech.ca`

### Step 5: Enable HTTPS (Automatic!)
- Netlify automatically provisions SSL certificate
- Your site will be served over HTTPS
- No configuration needed!

**Done! Your dashboard is live at research.datasciencetech.ca!** 🎊

---

## 🔄 Updating Your Dashboard

### When you make changes:

1. **Regenerate your dashboard:**
   ```powershell
   python deploy_to_web.py
   ```

2. **Go to your Netlify site:**
   - Login to Netlify
   - Go to your site
   - Click **"Deploys"** tab
   - Drag the new `research_streams_dashboard.zip` file
   - Or drag files from `deploy/` folder

3. **Live in 30 seconds!**

---

## 📋 Netlify Drop - Step by Step

### First Time:

```
1. Open browser: https://app.netlify.com/drop

2. You'll see a drag & drop zone

3. Drag your research_streams_dashboard.zip file

4. Wait for upload progress bar (30 seconds)

5. Netlify processes and deploys (automatic)

6. Your site is live! URL appears on screen

7. Click the URL to test your dashboard
```

### With Account (for custom domain):

```
1. Sign up at: https://app.netlify.com/signup

2. Login to dashboard

3. Click "Add new site" → "Deploy manually"

4. Drag your ZIP file or deploy/ folder

5. Site is live immediately

6. Add custom domain (see instructions above)

7. Configure Squarespace DNS

8. HTTPS enabled automatically
```

---

## 💡 Pro Tips

### Tip 1: Site Name
- Netlify assigns random names like `cool-unicorn-12345`
- Change it! Go to Site settings → Change site name
- Pick something memorable: `carlo-research-streams`
- URL becomes: `https://carlo-research-streams.netlify.app`

### Tip 2: Deploy Badge
- Netlify provides a deploy status badge
- Add to your Squarespace site
- Shows if dashboard is up-to-date

### Tip 3: Form Submissions
- Netlify supports form handling
- Add forms to your dashboard for feedback
- Submissions go to your email (free tier: 100/month)

### Tip 4: Analytics
- Free tier includes basic analytics
- See visitor counts, popular pages
- No configuration needed

---

## 🔗 Linking from Squarespace

### Add a prominent link on your Squarespace site:

**Option 1: Navigation Menu**
1. In Squarespace, go to Pages
2. Add a link in navigation
3. Text: "Research Streams"
4. URL: `https://research.datasciencetech.ca`
5. Opens in new tab: Yes

**Option 2: Button on Homepage**
1. Add a button block
2. Text: "View Research Streams Dashboard"
3. URL: `https://research.datasciencetech.ca`
4. Style: Make it prominent!

**Option 3: Dedicated Page**
1. Create a page: "Research"
2. Add text explaining your dashboard
3. Add button/link to dashboard
4. Embed preview screenshot

---

## ✅ Verification Checklist

After deployment, test:

- [ ] Main dashboard loads
- [ ] All 19 HTML pages accessible
- [ ] Navigation between pages works
- [ ] Search functionality works
- [ ] Charts display correctly
- [ ] Mobile responsive
- [ ] HTTPS enabled (padlock icon)
- [ ] Custom domain works (if configured)
- [ ] Fast loading speed
- [ ] All DOI links work

---

## 🆘 Troubleshooting

### Issue: "Deploy Failed"
**Solution:**
- Check ZIP file isn't corrupted
- Ensure all HTML files are in ZIP root (not in subfolder)
- Try uploading `deploy/` folder directly instead of ZIP

### Issue: Custom Domain Not Working
**Solution:**
- Wait 30 minutes for DNS propagation
- Check CNAME in Squarespace points to correct Netlify URL
- Verify custom domain added in Netlify
- Check Netlify DNS instructions match Squarespace config

### Issue: "404 Not Found" on Some Pages
**Solution:**
- Ensure all 19 HTML files uploaded
- Check file names exactly match (case-sensitive)
- Verify `index.html` exists (main page)

### Issue: Charts Not Showing
**Solution:**
- Charts use external CDN (Plotly.js)
- Check internet connection
- Verify browser allows JavaScript
- Test in different browser

---

## 📊 Comparison

| Feature | Netlify | GitHub Pages | Traditional Hosting |
|---------|---------|--------------|---------------------|
| **Cost** | FREE | FREE | $5-20/month |
| **Setup Time** | 2 minutes | 10 minutes | 30+ minutes |
| **Difficulty** | Easiest | Medium | Hard |
| **Updates** | Drag & drop | Git push | FTP upload |
| **HTTPS** | Auto | Auto | Manual config |
| **Custom Domain** | Easy | Easy | Easy |
| **Speed** | Fast CDN | Fast CDN | Varies |

**Winner for Squarespace users: Netlify** 🏆

---

## 🎉 Summary

### For Squarespace Users:

1. ✅ **Use Netlify** (not FTP - Squarespace doesn't support it)
2. ✅ **Drag & drop** deployment (easiest method)
3. ✅ **Free forever** for your dashboard
4. ✅ **Custom domain** with Squarespace DNS CNAME
5. ✅ **HTTPS automatic** (secure & professional)
6. ✅ **Easy updates** (just drag new files)

### Your URLs:
- **Squarespace main site:** datasciencetech.ca
- **Research Dashboard:** research.datasciencetech.ca (on Netlify)
- **Perfect integration** between both platforms!

---

## 🚀 Ready to Deploy?

### Right now:
```
1. Open: https://app.netlify.com/drop
2. Drag: research_streams_dashboard.zip
3. Wait: 30 seconds
4. Live: https://your-site.netlify.app
```

### Then later (for custom domain):
```
1. Sign up at Netlify (free)
2. Add domain: research.datasciencetech.ca
3. Configure Squarespace DNS (CNAME)
4. Wait for DNS propagation
5. HTTPS enabled automatically
6. Done!
```

**Your dashboard will be live at research.datasciencetech.ca!** 🎊

---

*Easiest deployment for Squarespace users!*  
*No coding, no command line, no FTP - just drag and drop!* 🚀
