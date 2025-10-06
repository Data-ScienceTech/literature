# 🚀 Hierarchical Analysis - Quick Reference

## ⚡ Quick Start (30 seconds)

```bash
# Run complete hierarchical analysis
python run_hierarchical_analysis.py

# Output: 3-4 levels of nested research clusters
# Time: 10-20 minutes
```

## 📋 What You Get

```
Level 0: 8-12 macro research areas (e.g., "Digital Innovation")
Level 1: 25-35 research streams (e.g., "Platform Ecosystems")  
Level 2: 60-90 specific topics (e.g., "API Management")
Level 3: 120-180 niche specs (e.g., "REST API Design")
```

## 📁 Key Output Files

| File | What It Contains |
|------|-----------------|
| `papers_hierarchical_clustered.csv` | Dataset with cluster_l0, cluster_l1, cluster_l2, cluster_l3 |
| `hierarchical_dialog_cards.json` | Research stream summaries at each level |
| `hierarchy_leiden.json` | Complete parent-child hierarchy structure |
| `hierarchical_analysis.json` | Quality metrics (silhouette, cohesion) |
| `visualizations/hierarchy_tree.png` | Visual hierarchy diagram |

## 🔧 Configuration (in run_hierarchical_analysis.py)

```python
CORPUS_NAME = "recommended"          # or "hq_2010+", "ais_basket"
CLUSTERING_METHOD = "leiden"          # or "hdbscan", "recursive"
MAX_LEVELS = 4                        # 3-4 recommended
MIN_CLUSTER_SIZE = 20                 # Lower = more granular
```

## 💻 Common Usage Patterns

### Load and Explore

```python
import pandas as pd
import json

# Load clustered data
df = pd.read_csv('data/papers_hierarchical_clustered.csv')

# Load dialog cards
with open('data/hierarchical_dialog_cards.json') as f:
    cards = json.load(f)

# View macro areas
print(df['cluster_l0'].value_counts())

# Get specific stream
stream = df[df['hierarchy_path'] == '2 > 2.1 > 2.1.3']
```

### Find Research Gap

```python
# Small but recent clusters = emerging niches
for cluster_id, card in cards.items():
    if card['level'] == 2 and card['size'] < 30:
        recent_ratio = card.get('recent_papers', 0) / card['size']
        if recent_ratio > 0.6:
            print(f"Emerging: {cluster_id} - {card.get('top_terms', [])[:3]}")
```

### Analyze Bridge Papers

```python
with open('data/hierarchical_network_analysis.json') as f:
    network = json.load(f)

for bridge in network.get('bridge_papers', [])[:5]:
    print(f"Bridges {bridge['n_connections']} clusters")
```

## 🎯 Three Methods Compared

| Method | Speed | Quality | Best For |
|--------|-------|---------|----------|
| **Leiden** ⭐ | Medium | Excellent | Large corpora, robust results |
| **HDBSCAN** | Fast | Good | Variable density, noise handling |
| **Recursive** | Slow | Excellent | Guaranteed quality, small corpora |

## 📊 Quality Thresholds

| Metric | Good | Excellent |
|--------|------|-----------|
| Silhouette | >0.3 | >0.5 |
| Davies-Bouldin | <1.5 | <1.0 |
| Cohesion | >0.6 | >0.8 |

## 🔍 Troubleshooting

| Issue | Solution |
|-------|----------|
| Out of memory | Reduce batch_size to 16 |
| Too many small clusters | Increase MIN_CLUSTER_SIZE to 30 |
| Too few levels | Decrease MIN_CLUSTER_SIZE to 15 |
| Slow clustering | Use HDBSCAN or smaller corpus |
| Missing leidenalg | `pip install leidenalg python-igraph` |

## 📚 Research Applications

1. **Literature Review**: Navigate macro → meso → micro
2. **Gap Analysis**: Find small, recent clusters
3. **Theoretical Integration**: Analyze bridge papers
4. **Trend Analysis**: Track growth within hierarchy

## 🎓 Interpreting Results

### Hierarchy Path
`"2 > 2.1 > 2.1.3"` means:
- Macro area #2 (e.g., Digital Innovation)
- Stream #1 within area 2 (e.g., Platform Ecosystems)  
- Topic #3 within stream (e.g., API Design)

### Cluster Size
- Large (>100): Established area
- Medium (30-100): Active stream
- Small (<30): Emerging niche or specialized topic

### Quality Score
- Silhouette >0.5: Well-separated cluster
- Cohesion >0.7: Highly coherent theme
- Recent ratio >0.5: Growing area

## 🚀 Advanced Usage

### Custom Resolutions

```python
from src.hierarchical_clustering import LeidenMultiResolution

clusterer = LeidenMultiResolution(embeddings, k=15)
hierarchy = clusterer.build_hierarchy(
    resolutions=[0.4, 0.8, 1.5, 2.5],  # Custom
    min_cluster_size=25,
    max_levels=4
)
```

### Compare Methods

```bash
# Run all three
CLUSTERING_METHOD="leiden" python run_hierarchical_analysis.py
CLUSTERING_METHOD="hdbscan" python run_hierarchical_analysis.py  
CLUSTERING_METHOD="recursive" python run_hierarchical_analysis.py
```

## 📈 Expected Output Stats

**IS Recommended Corpus (6,556 papers)**
- Level 0: ~10 clusters
- Level 1: ~30 clusters
- Level 2: ~75 clusters
- Level 3: ~150 clusters
- Total: ~265 clusters
- Time: ~15 minutes

## 💡 Pro Tips

1. **Start with defaults**: Leiden, 4 levels, size 20
2. **Review Level 1 first**: Best balance of detail vs. overview
3. **Check quality metrics**: Ensure silhouette >0.3
4. **Validate with domain knowledge**: Use dialog cards
5. **Explore bridge papers**: Key cross-cutting insights

## 📞 Quick Checks

```bash
# Verify outputs
ls data/hierarchical*.{csv,json}
ls data/visualizations/

# Check quality
python -c "import json; print(json.load(open('data/hierarchical_analysis.json'))['quality_metrics'])"

# Count clusters  
python -c "import pandas as pd; df=pd.read_csv('data/papers_hierarchical_clustered.csv'); print({f'L{i}': df[f'cluster_l{i}'].nunique() for i in range(4)})"
```

## 🎯 One-Liner Analysis

```python
# Complete analysis in one command
!python run_hierarchical_analysis.py && python -c "import pandas as pd, json; df=pd.read_csv('data/papers_hierarchical_clustered.csv'); cards=json.load(open('data/hierarchical_dialog_cards.json')); print(f'✅ {len(df)} papers, {len(cards)} clusters, {df.cluster_l0.nunique()} macro areas')"
```

---

**Need Help?** Check:
- `HIERARCHICAL_ANALYSIS_GUIDE.md` - Comprehensive guide
- `HIERARCHICAL_ANALYSIS_README.md` - Conceptual overview
- `src/hierarchical_clustering.py` - Code documentation

**Status**: ✅ Production Ready | **Version**: 1.0 | **Date**: 2025-01-06
