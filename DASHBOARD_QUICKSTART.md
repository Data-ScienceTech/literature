# 🎯 Quick Start: Interactive Research Stream Explorer

## Launch Dashboard in 3 Steps

### Step 1: Install Dependencies
```powershell
pip install -r requirements_dashboard.txt
```

This installs:
- **Dash** - Web framework for the dashboard
- **Plotly** - Interactive visualizations  
- **Pandas** - Data processing
- **Numpy** - Numerical operations

### Step 2: Start the Dashboard
```powershell
python launch_dashboard.py
```

The launcher will:
✅ Check if you have all required data files  
✅ Verify dependencies are installed  
✅ Start the web server on port 8050

### Step 3: Explore!
Open your browser to: **http://127.0.0.1:8050**

---

## Dashboard Features

### 📊 Overview Tab
- **Sunburst Chart**: Interactive hierarchical visualization
  - Click segments to zoom into clusters
  - Hover for cluster details and top keywords
  - Color-coded by hierarchy level
  
- **Temporal Evolution**: Track how research streams developed over time
  
- **Citation Impact**: Compare influence across clusters

### 🔍 Cluster Explorer Tab
- Select hierarchy level (0-3)
- Choose specific clusters  
- View detailed statistics:
  - Paper count, citations, keyword coverage
  - Top keywords with visual tags
  - Most cited papers with metadata
  
### 🏷️ Keywords Tab
- Keyword co-occurrence network visualization
- Node size = frequency
- Edges = how often keywords appear together
- Discover thematic relationships

### 📈 Statistics Tab
- Comprehensive metrics for each level
- Cluster size distributions
- Quality indicators

---

## What You'll Discover

Your dashboard reveals:

✨ **102 research clusters** organized across **4 hierarchical levels**  
✨ **8,101 papers** from 8 top IS journals (2016-2025)  
✨ **99.9% keyword coverage** (12,548/12,564 papers)  
✨ **Clear thematic streams**:
- Technology Acceptance (highest impact: 314 mean citations)
- E-commerce & Online Behavior  
- Knowledge Management
- AI & Decision Support
- And many more!

---

## Navigation Tips

**Sunburst Chart:**
- Click outer rings → zoom into subclusters
- Click center → zoom out
- Hover → see keywords and paper counts

**Cluster Explorer:**
- Start with Level 0 (broad themes)
- Drill down to Levels 1-3 for specialization
- Compare clusters by switching selections

**Keyword Network:**
- Dense regions = coherent themes
- Bridge keywords = interdisciplinary topics
- Peripheral nodes = niche areas

---

## Troubleshooting

**"Missing data files" error:**
```powershell
python run_hierarchical_analysis.py
```

**"Module not found" error:**
```powershell
pip install -r requirements_dashboard.txt
```

**Port 8050 already in use:**
Edit `dashboard_app.py` line 578, change `port=8050` to another port (e.g., `port=8051`)

**Dashboard won't load:**
- Clear browser cache
- Try incognito/private mode
- Use Chrome or Edge for best performance

---

## System Requirements

- Python 3.8+
- 8GB RAM (recommended for smooth performance)
- Modern web browser (Chrome, Edge, Firefox, Safari)
- ~500MB disk space for data + dependencies

---

## Next Steps

After exploring your dashboard:

1. **Export Insights**: Right-click charts → Download as PNG
2. **Share Findings**: Use screenshots in presentations
3. **Dive Deeper**: Run detailed analysis scripts for specific clusters
4. **Customize**: Edit `dashboard_app.py` to add new visualizations

---

**Full documentation:** See `DASHBOARD_GUIDE.md` for advanced features and customization options.

**Enjoy exploring your research streams! 🔬**
