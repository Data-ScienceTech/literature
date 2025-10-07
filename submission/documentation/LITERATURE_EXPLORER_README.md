# 🔬 AIS Basket Literature Explorer

**Interactive web interface for exploring 8,110 academic papers using hybrid text + citation clustering**

## ✨ Quick Start

### Option 1: Open Directly (Simple)
```
Double-click: literature-explorer.html
```

### Option 2: Local Server (Recommended)
```bash
# Python 3
python -m http.server 8000

# Then open: http://localhost:8000/literature-explorer.html
```

### Option 3: PowerShell (Windows)
```powershell
cd C:\Users\carlo\Dropbox\literature_analyzer_v2\literature
python -m http.server 8000
Start-Process "http://localhost:8000/literature-explorer.html"
```

---

## 🎯 What You Get

### 📊 Data
- **8,110 papers** from AIS Basket journals
- **8 major research streams**
- **48 detailed subtopics**
- **2.8M citation edges** mapped

### 🔬 Quality
- **Silhouette score: 0.340** (professional-grade)
- **11.7x better** than text-only clustering
- **88% citation coverage**

### 🛠️ Technology
- **Hybrid clustering**: Text (60%) + Citations (40%)
- **Tools**: OpenAlex, TF-IDF, LSI, NMF, Bibliographic Coupling
- **Optimization**: Sparse matrices, inverted index (15-30x speedup)

---

## 📁 Files

```
literature-explorer.html        ← Main interface
literature-explorer.js          ← Application logic
LITERATURE_EXPLORER_DOCS.md     ← Full documentation

data/clean/hybrid_streams_full_corpus/
├── doc_assignments.csv         ← Paper assignments
├── topics_level1.csv           ← 8 streams  
├── topics_level2.csv           ← 48 subtopics
└── citation_network_stats.json ← Network metrics
```

---

## 🚀 Features

### Navigation
- **3-level hierarchy**: Streams → Subtopics → Papers
- **Breadcrumb navigation**: Easy backtracking
- **Two views**: Topics (visual) or Papers (list)

### Search & Filter
- **Full-text search**: Titles, keywords, authors
- **Filters**: All, Citations only, Recent (2020+), Classics (pre-2010)
- **Real-time updates**: Instant results

### Methodology Display
- **Prominent explanations**: Tools & techniques
- **Performance metrics**: Clustering quality stats
- **Expandable details**: Full paper metadata

---

## 🎨 Interface Preview

```
┌─────────────────────────────────────────┐
│  AIS Basket Literature Explorer         │
│  8,110 Papers | 8 Streams | 0.340 Score │
└─────────────────────────────────────────┘

┌──────────────┬────────────────────────────┐
│ Streams      │  Stream 1: E-commerce      │
│              │  2,021 papers              │
│ ◉ All (8110) │  ┌──────┐ ┌──────┐        │
│ ○ Stream 0   │  │ 1.0  │ │ 1.1  │        │
│ ● Stream 1   │  │ 511  │ │ 407  │        │
│ ○ Stream 2   │  └──────┘ └──────┘        │
│ ○ Stream 3   │                            │
└──────────────┴────────────────────────────┘
```

---

## 📚 Documentation

- **LITERATURE_EXPLORER_DOCS.md**: Complete technical docs
- **HYBRID_CLUSTERING_RESULTS.md**: Analysis results
- **CITATION_ENRICHMENT_COMPLETE.md**: Data collection
- **QUICK_START_HYBRID_CLUSTERING.md**: Python usage

---

## 🔄 Regenerate Data

```bash
cd data/clean

# Run clustering
python stream_extractor_hybrid.py \
  --input ais_basket_corpus_enriched.parquet \
  --outdir hybrid_streams_full_corpus \
  --l1_ks 8 \
  --l2_ks 6 \
  --text_weight 0.6 \
  --citation_weight 0.4

# Frontend auto-loads from hybrid_streams_full_corpus/
```

---

## 🐛 Troubleshooting

### Data not loading?
- Use local server (not file://)
- Check browser console (F12)
- Verify paths in literature-explorer.js

### No results found?
- Clear search box
- Click "All Papers" filter
- Select "All Streams" in sidebar

---

## 🎓 Use Cases

✅ **Literature Reviews**: Browse by topic hierarchy  
✅ **Gap Analysis**: Find underexplored areas  
✅ **Course Design**: Map research to modules  
✅ **Journal Targeting**: See publication patterns  
✅ **Citation Analysis**: Explore research lineage  

---

## 📊 Methodology Summary

### 1. Text Processing
```
TF-IDF → LSI → 200 dimensions (21.95% variance)
```

### 2. Citation Network
```
OpenAlex → 421K refs → Jaccard similarity → 2.8M edges
```

### 3. Hybrid Clustering
```
60% text + 40% citations → 11.7x better quality
```

### 4. Hierarchical Topics
```
L1: Agglomerative (8 streams)
L2: NMF (6 per L1 = 48 total)
L3: NMF (3 per L2 = ~150 total)
```

---

## 🌟 Key Metrics

| Metric | Value |
|--------|-------|
| Papers | 8,110 |
| Streams (L1) | 8 |
| Subtopics (L2) | 48 |
| Micro-topics (L3) | ~150 |
| Citation edges | 2,844,515 |
| Silhouette | 0.340 |
| Improvement | 11.7x |
| Coverage | 88% |
| Sparsity | 91.3% |

---

## 🚀 Next Steps

1. **Open the explorer** (see Quick Start)
2. **Browse streams** in left sidebar
3. **Click topics** to drill down
4. **Search papers** by keyword
5. **Export lists** for your research

---

## 📧 Support

- **Docs**: Read LITERATURE_EXPLORER_DOCS.md
- **Issues**: Check browser console (F12)
- **Data**: Verify CSV files in hybrid_streams_full_corpus/

---

*Powered by OpenAlex, scikit-learn, and Python*  
*Version 1.0 | 2025-10-06*
