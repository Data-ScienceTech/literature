# Literature Explorer - Complete Documentation

## 🎯 Overview

The **AIS Basket Literature Explorer** is an interactive web application for exploring 8,110 academic papers from premier Information Systems journals, clustered using advanced hybrid text + citation network analysis.

---

## 📊 What Makes This Special

### Hybrid Clustering Breakthrough
- **11.7x better clustering** than text-only approaches (silhouette: 0.340 vs 0.029)
- Combines **text similarity** (60%) + **citation networks** (40%)
- **Professional-grade quality** (silhouette > 0.3)

### Complete Literature Mapping
- **8,110 papers** from AIS Basket journals (2024 snapshot)
- **2.8 million citation edges** mapped
- **88% citation coverage** (7,133 papers with reference data)
- **3-level hierarchy**: Streams → Subtopics → Papers

---

## 🛠️ Technical Architecture

### Data Pipeline

```
1. DATA COLLECTION
   ├─ CrossRef API → Basic metadata (12,564 papers)
   ├─ OpenAlex API → Citations + enrichment (99.9% match rate)
   └─ Output: ais_basket_corpus_enriched.parquet

2. TEXT PROCESSING
   ├─ TF-IDF Vectorization → 27,372 terms
   ├─ LSI Reduction → 200 dimensions (21.95% variance)
   └─ Text feature matrix: 8,110 × 200

3. CITATION NETWORK
   ├─ Extract 421,339 references
   ├─ Bibliographic coupling (Jaccard similarity)
   ├─ Inverted index optimization (15-30x speedup)
   └─ Sparse matrix: 2.8M edges, 91.3% sparsity

4. HYBRID CLUSTERING
   ├─ L1: Agglomerative clustering → 8 major streams
   ├─ L2: NMF within each L1 → 48 subtopics
   └─ L3: NMF within each L2 → ~150-200 micro-topics

5. WEB INTERFACE
   ├─ Static HTML/CSS/JS
   ├─ Loads CSV + JSON data
   └─ Interactive hierarchical navigation
```

---

## 🔧 Technologies & Tools

### Data Collection
- **CrossRef API**: DOI-based metadata retrieval
- **OpenAlex API**: Citation network + enrichment
  - Batch queries: 50 papers/request
  - Caching: Avoid re-queries
  - Rate limiting: ~1.2 batches/second

### Machine Learning (scikit-learn)
- **TF-IDF**: Term frequency-inverse document frequency
- **TruncatedSVD**: Latent semantic indexing (LSI)
- **AgglomerativeClustering**: Hierarchical L1 clustering
- **NMF**: Non-negative matrix factorization for L2/L3
- **KMeans**: Silhouette score optimization
- **silhouette_score**: Cluster quality metric

### Optimization
- **scipy.sparse**: CSR matrix for 91.3% sparsity
- **Inverted index**: O(n×k) vs O(n²) for citation matrix
- **Batch processing**: Efficient API calls
- **Caching**: JSON-based response storage

### Frontend
- **Vanilla JavaScript**: No frameworks needed
- **CSS Grid/Flexbox**: Responsive layout
- **Fetch API**: CSV/JSON data loading
- **Event delegation**: Efficient DOM handling

---

## 📁 File Structure

```
literature_analyzer_v2/literature/
│
├── data/clean/
│   ├── ais_basket_corpus_enriched.parquet     # Full enriched corpus
│   ├── ais_basket_corpus_enriched.json        # JSON format
│   └── hybrid_streams_full_corpus/            # Clustering results
│       ├── doc_assignments.csv                 # Paper assignments
│       ├── topics_level1.csv                   # 8 streams
│       ├── topics_level2.csv                   # 48 subtopics
│       ├── topics_level3.csv                   # ~200 micro-topics
│       ├── citation_network_stats.json         # Network metrics
│       └── summary.md                          # Quick overview
│
├── literature-explorer.html                    # Main web interface
├── literature-explorer.js                      # Application logic
│
├── enrich_ais_basket_openalex.py              # Citation enrichment
├── stream_extractor_hybrid.py                  # 3-level clustering
│
├── HYBRID_CLUSTERING_RESULTS.md               # Analysis results
├── CITATION_ENRICHMENT_COMPLETE.md            # Data collection
├── QUICK_START_HYBRID_CLUSTERING.md           # Usage guide
└── LITERATURE_EXPLORER_DOCS.md                # This file
```

---

## 🎨 Frontend Features

### 1. Hierarchical Navigation
```
All Streams
  ├─ Stream 0 (1,554 papers)
  │   ├─ Topic 0.0 (638 papers)
  │   │   ├─ Micro-topic 0.0.0
  │   │   ├─ Micro-topic 0.0.1
  │   │   └─ Micro-topic 0.0.2
  │   ├─ Topic 0.1 (150 papers)
  │   └─ ... (6 topics total)
  ├─ Stream 1 (2,021 papers)
  └─ ... (8 streams total)
```

### 2. Search & Filter
- **Full-text search**: Title, keywords, authors
- **Filters**:
  - All papers
  - With citations only
  - Recent (2020+)
  - Classics (pre-2010)

### 3. Multiple Views
- **Topics view**: Browse hierarchy visually
- **Papers view**: List all papers
- **Details on demand**: Expandable metadata

### 4. Methodology Display
- Prominent methodology banner
- Tool explanations
- Technique descriptions
- Performance metrics

---

## 🔬 Algorithms Explained

### 1. TF-IDF (Term Frequency-Inverse Document Frequency)

**Purpose**: Convert text to numerical vectors

**Formula**:
```
TF-IDF(t,d) = TF(t,d) × IDF(t)

TF(t,d) = count(t in d) / total_terms(d)
IDF(t) = log(total_docs / docs_containing(t))
```

**Why**: Common words (like "the") get low scores; distinctive terms get high scores

**Result**: 8,110 × 27,372 sparse matrix

---

### 2. LSI (Latent Semantic Indexing)

**Purpose**: Reduce dimensions while preserving semantic meaning

**Technique**: Truncated SVD (Singular Value Decomposition)

**Formula**:
```
X = U × Σ × V^T
X_reduced = U_k × Σ_k
```

**Parameters**: 200 components (21.95% variance explained)

**Why**: Captures latent topics; removes noise; enables faster clustering

**Result**: 8,110 × 200 dense matrix

---

### 3. Bibliographic Coupling

**Purpose**: Measure paper similarity via shared references

**Technique**: Jaccard similarity of citation sets

**Formula**:
```
Jaccard(A,B) = |A ∩ B| / |A ∪ B|

Where A, B = sets of references cited by papers
```

**Optimization**: Inverted index
```python
# Naive: O(n²) - check all pairs
for i in papers:
    for j in papers:
        compute_similarity(i, j)  # 33M comparisons!

# Optimized: O(n×k) - only check papers citing common refs
inverted_index = {ref: [papers citing it]}
for ref in references:
    for pair in combinations(inverted_index[ref], 2):
        compute_similarity(pair)  # 2.8M comparisons
```

**Result**: Sparse coupling matrix (91.3% zeros)

---

### 4. Hybrid Feature Combination

**Purpose**: Leverage both text and citation information

**Formula**:
```
Combined = α × Text_features + β × Citation_features

Where:
α = 0.6 (text weight)
β = 0.4 (citation weight)
```

**Normalization**: Min-max scaling to [0,1]
```python
normalized = (X - X.min()) / (X.max() - X.min())
```

**Result**: 8,110 × 201 hybrid feature matrix

---

### 5. Agglomerative Clustering (L1)

**Purpose**: Create major research streams

**Algorithm**: Hierarchical bottom-up clustering
```
1. Start: Each paper is its own cluster
2. Repeat: Merge closest clusters
3. Stop: When k clusters remain
```

**Parameters**:
- `n_clusters`: 8 (optimized via silhouette)
- `linkage`: "ward" (minimizes within-cluster variance)
- `metric`: "euclidean"

**Selection**: Test k ∈ {8, 10, 12}, choose best silhouette score

**Result**: 8 balanced streams (silhouette: 0.340)

---

### 6. NMF (Non-negative Matrix Factorization)

**Purpose**: Discover interpretable subtopics

**Formula**:
```
X ≈ W × H

Where:
X = document-term matrix (n_docs × n_terms)
W = document-topic matrix (n_docs × k)
H = topic-term matrix (k × n_terms)

All values ≥ 0 (non-negative constraint)
```

**Initialization**: "nndsvda" (SVD-based, faster convergence)

**Selection**: Test k ∈ {2,3,4,5,6}, minimize reconstruction error
```python
error = ||X - W×H|| + λ×k  # Penalize more topics
```

**Levels**:
- L2: NMF within each L1 (6 topics per stream)
- L3: NMF within each L2 (2-4 topics per subtopic)

**Result**: Hierarchical topic structure with keyword lists

---

## 📈 Performance Metrics

### Clustering Quality

| Metric | Value | Interpretation |
|--------|-------|----------------|
| **Silhouette Score** | 0.340 | Excellent (>0.3 is professional-grade) |
| **Improvement over text-only** | 11.7x | From 0.029 to 0.340 |
| **Papers with citations** | 88% | High coverage enables strong coupling |
| **Citation edges** | 2.8M | Rich network for analysis |

### Computational Efficiency

| Aspect | Naive | Optimized | Speedup |
|--------|-------|-----------|---------|
| **Citation matrix** | O(n²) = 33M | O(n×k) = 2.8M | **12x** |
| **Time** | 30-60 min | ~2 min | **15-30x** |
| **Memory** | Dense | 91.3% sparse | **11x** |

### Data Quality

| Metric | Value | Note |
|--------|-------|------|
| **OpenAlex match** | 99.9% | 12,549/12,564 papers |
| **Citation coverage** | 74.8% | 9,392 papers with refs |
| **Total references** | 545,865 | Average 58.1 per paper |
| **Valid after filtering** | 8,110 | Papers with abstracts |

---

## 🚀 Usage Guide

### Opening the Frontend

1. **Local file** (simple):
   ```
   Open: literature-explorer.html in web browser
   ```

2. **Local server** (recommended):
   ```bash
   # Python
   cd literature_analyzer_v2/literature
   python -m http.server 8000
   
   # Open: http://localhost:8000/literature-explorer.html
   ```

3. **Why local server**: 
   - Avoids CORS issues with file:// protocol
   - Enables proper CSV/JSON loading
   - Matches production environment

### Navigation

1. **Browse streams**: Click any stream in left sidebar
2. **Explore subtopics**: Click topic cards to drill down
3. **View papers**: Click subtopic or toggle Papers view
4. **Search**: Type in search box (updates instantly)
5. **Filter**: Use chips (All/Citations/Recent/Classics)
6. **Details**: Click "Show details" on any paper

### Breadcrumb Navigation

```
All Streams › Stream 1 › Topic 1.3
   ↑           ↑           ↑
  Click     Click       Current
```

---

## 🔄 Updating Data

### Re-run Clustering

```bash
cd data/clean

# 2-level clustering
python stream_extractor_hybrid.py \
  --input ais_basket_corpus_enriched.parquet \
  --outdir hybrid_streams_full_corpus \
  --l1_ks 8 \
  --l2_ks 6 \
  --text_weight 0.6 \
  --citation_weight 0.4

# 3-level clustering
python stream_extractor_hybrid.py \
  --input ais_basket_corpus_enriched.parquet \
  --outdir hybrid_streams_3level \
  --l1_ks 8 \
  --l2_ks 6 \
  --l3_ks 2,3,4 \
  --text_weight 0.6 \
  --citation_weight 0.4
```

### Frontend will auto-load new data from:
```
./data/clean/hybrid_streams_full_corpus/
```

---

## 📊 Data Format Reference

### doc_assignments.csv
```csv
doc_id,title,year,journal,journal_short,L1,L2,L1_label,L2_label
10.2307/...,Paper Title,2020,MIS Quarterly,MISQ,0,2,digital transformation,social media
```

### topics_level1.csv
```csv
L1,size,label,top_terms
0,1554,"digital, transformation, innovation, ...",digital, transformation, ...
```

### topics_level2.csv
```csv
L1,L2,L2_path,size,label,top_terms
0,0,0.0,638,"systems, information, research, ...",systems, information, ...
```

### citation_network_stats.json
```json
{
  "papers_with_refs": 7133,
  "total_refs": 421339,
  "coupling_edges": 2844515,
  "avg_coupling": 0.012,
  "sparsity": 0.9135,
  "combined_silhouette": 0.340
}
```

---

## 🎓 Research Applications

### 1. Literature Reviews
- Start with relevant stream
- Drill down to specific subtopics
- Export paper lists for Zotero/Mendeley
- Track citation patterns

### 2. Gap Analysis
- Identify underexplored areas (small clusters)
- Find emerging topics (recent papers)
- Spot synthesis opportunities (low coupling)

### 3. Course Design
- Map topics to course modules
- Balance breadth vs depth
- Track field evolution over time

### 4. Journal Targeting
- See where topics are published
- Identify journal specializations
- Track publication trends

---

## 🐛 Troubleshooting

### "Failed to load data"
- **Cause**: CORS restrictions on file:// protocol
- **Fix**: Use local server (see Usage Guide)

### "No papers found"
- **Cause**: Too restrictive filters
- **Fix**: Click "All Papers" chip, clear search

### Topics not showing
- **Cause**: JavaScript error loading CSV
- **Fix**: Check browser console (F12), verify file paths

### Slow performance
- **Cause**: Loading 8,110 papers at once
- **Optimization**: Add pagination (see Advanced Customization)

---

## 🔧 Advanced Customization

### Change Color Scheme
Edit CSS variables in `literature-explorer.html`:
```css
:root {
    --primary: #2563eb;      /* Blue */
    --secondary: #10b981;    /* Green */
    --background: #f8fafc;   /* Light gray */
}
```

### Adjust Clustering Parameters
Edit `stream_extractor_hybrid.py`:
```python
# More/fewer streams
--l1_ks 6,8,10,12

# More/fewer subtopics per stream
--l2_ks 4,5,6,7

# Adjust text vs citation balance
--text_weight 0.7
--citation_weight 0.3
```

### Add Pagination
In `literature-explorer.js`:
```javascript
renderPapers() {
    const PAGE_SIZE = 50;
    const start = this.currentPage * PAGE_SIZE;
    const paged = papers.slice(start, start + PAGE_SIZE);
    // ... render paged results
}
```

---

## 📚 Further Reading

### Academic Papers
- Van Eck & Waltman (2014): "Visualizing bibliometric networks"
- Blondel et al. (2008): "Fast unfolding of communities in large networks"
- Lee & Seung (1999): "Learning the parts of objects by NMF"

### Technical Documentation
- [OpenAlex API](https://docs.openalex.org/)
- [scikit-learn Clustering](https://scikit-learn.org/stable/modules/clustering.html)
- [scipy.sparse](https://docs.scipy.org/doc/scipy/reference/sparse.html)

### Related Projects
- VOSviewer: Bibliometric visualization
- CiteSpace: Citation network analysis
- Gephi: Network graph visualization

---

## 🤝 Credits

### Data Sources
- **AIS Basket Journals**: Premier IS research outlets
- **CrossRef**: DOI metadata
- **OpenAlex**: Citation network data

### Technologies
- **Python**: Data processing
- **scikit-learn**: Machine learning
- **pandas**: Data manipulation
- **scipy**: Sparse matrices
- **NumPy**: Numerical computing

### Methodology
- Hybrid clustering: Original contribution
- Inverted index optimization: Algorithm design
- 3-level hierarchy: Hierarchical topic modeling

---

## 📝 License & Citation

### Data
- AIS Basket corpus: Fair use for research
- OpenAlex: CC0 (public domain)
- CrossRef: Metadata API terms of service

### Code
- MIT License (open source)

### Citation
```bibtex
@software{ais_literature_explorer,
  title = {AIS Basket Literature Explorer: Hybrid Clustering with Citations},
  year = {2025},
  note = {Interactive exploration of 8,110 IS papers using text + citation networks}
}
```

---

*Last updated: 2025-10-06*  
*Version: 1.0*  
*Corpus: 8,110 papers from AIS Basket journals*
