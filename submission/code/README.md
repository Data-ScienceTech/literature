# Code Directory - Analysis Scripts

This directory contains the core Python scripts for the literature analysis pipeline.

---

## Quick Start

### 1. Setup Environment

```bash
# Create conda environment from specification
conda env create -f env.yml

# Activate environment
conda activate literature_analyzer

# Verify installation
python -c "import sklearn, scipy, pandas; print('All dependencies installed!')"
```

### 2. Run Full Pipeline

```bash
# Step 1: Enrich corpus with citation data (one-time, ~42 minutes)
python enrich_ais_basket_openalex.py

# Step 2: Run 3-level hybrid clustering (~3 minutes)
python stream_extractor_hybrid.py \
    --input ais_basket_corpus_enriched.parquet \
    --outdir output_3level \
    --l1_ks 8 \
    --l2_ks 4,5,6,7,8 \
    --l3_ks 2,3,4 \
    --text_weight 0.6 \
    --citation_weight 0.4
```

### 3. View Results

```bash
# Check output directory
ls output_3level/

# Expected files:
# - doc_assignments.csv (paper assignments)
# - topics_level1.csv (8 streams)
# - topics_level2.csv (48 subtopics)
# - topics_level3.csv (182 micro-topics)
# - citation_network_stats.json (network metrics)
# - summary.md (analysis summary)
```

---

## Scripts Overview

### `enrich_ais_basket_openalex.py`

**Purpose**: Collect citation data for papers from OpenAlex API

**Input**: 
- Base corpus (CSV or Parquet) with DOI field
- Default: Expects `ais_basket_corpus.parquet` in data directory

**Process**:
1. Load corpus papers
2. For each paper:
   - Query OpenAlex API using DOI
   - Extract `referenced_works` field (list of cited paper IDs)
   - Handle rate limits (respectful API usage)
3. Save enriched corpus with citation data

**Output**:
- `ais_basket_corpus_enriched.parquet`
- Includes all original fields + `referenced_works` column

**Runtime**: ~42 minutes for 8,110 papers
- API rate limit: ~3-5 papers/second
- Includes retry logic for failures

**Configuration**:
```python
# In script, modify these if needed:
INPUT_FILE = 'data/ais_basket_corpus.parquet'
OUTPUT_FILE = 'data/ais_basket_corpus_enriched.parquet'
API_EMAIL = 'your-email@example.com'  # For polite API usage
```

**Requirements**:
- OpenAlex API (free, no key required)
- Internet connection
- Email for API identification (optional but recommended)

---

### `stream_extractor_hybrid.py`

**Purpose**: Perform 3-level hybrid clustering combining text and citations

**Algorithm Overview**:
1. **Load Data**: Read enriched corpus with citations
2. **Text Features**:
   - Concatenate title + abstract
   - TF-IDF vectorization (min_df=5, max_df=0.8)
   - LSI dimensionality reduction (200 components)
3. **Citation Features**:
   - Build bibliographic coupling matrix using inverted index
   - Calculate Jaccard similarity of reference sets
   - Store as sparse matrix (91.3% sparsity)
4. **Hybrid Features**:
   - Normalize text and citation features
   - Combine: `hybrid = text_weight × text + citation_weight × citations`
   - Default: 60% text + 40% citations
5. **Level 1 Clustering**:
   - Agglomerative hierarchical clustering
   - Ward linkage, Euclidean distance
   - Test multiple k values, select best via silhouette score
6. **Level 2 Clustering**:
   - Within each L1 cluster, apply NMF topic modeling
   - Test k ∈ {4,5,6,7,8}, select via reconstruction error
   - Assign papers to highest-weight topic
7. **Level 3 Clustering**:
   - Within each L2 cluster (if ≥10 papers), apply NMF
   - Test k ∈ {2,3,4}, select via reconstruction error
8. **Output**: CSVs with assignments and topic labels

**Command-Line Arguments**:

```bash
python stream_extractor_hybrid.py [OPTIONS]

Required:
  --input PATH          Input Parquet file with corpus + citations
  --outdir PATH         Output directory for results

Optional:
  --l1_ks LIST          L1 cluster candidates (comma-separated)
                        Default: 8
                        Example: --l1_ks 6,8,10,12
  
  --l2_ks LIST          L2 cluster candidates per L1 cluster
                        Default: 4,5,6,7,8
                        Example: --l2_ks 5,6,7
  
  --l3_ks LIST          L3 cluster candidates per L2 cluster
                        Default: 2,3,4
                        Example: --l3_ks 2,3
  
  --text_weight FLOAT   Weight for text features (0-1)
                        Default: 0.6
  
  --citation_weight FLOAT  Weight for citation features (0-1)
                           Default: 0.4
                           Note: text_weight + citation_weight should = 1
```

**Examples**:

```bash
# Basic usage (defaults)
python stream_extractor_hybrid.py \
    --input corpus.parquet \
    --outdir results/

# Custom weights (more emphasis on citations)
python stream_extractor_hybrid.py \
    --input corpus.parquet \
    --outdir results_citation_heavy/ \
    --text_weight 0.5 \
    --citation_weight 0.5

# Test different L1 cluster counts
python stream_extractor_hybrid.py \
    --input corpus.parquet \
    --outdir results_sensitivity/ \
    --l1_ks 6,8,10,12

# Minimal 2-level clustering (skip L3)
python stream_extractor_hybrid.py \
    --input corpus.parquet \
    --outdir results_2level/ \
    --l1_ks 8 \
    --l2_ks 6 \
    --l3_ks ""  # Empty string skips L3
```

**Output Files**:

1. **`doc_assignments.csv`** - Paper-level assignments
   - Columns: abstract, title, journal, year, doi, referenced_works, L1, L2, L3, L1_label, L2_label, L3_label
   - Rows: One per paper (8,110)
   
2. **`topics_level1.csv`** - L1 stream definitions
   - Columns: L1 (ID), size (paper count), label (keywords), top_terms
   - Rows: One per stream (8)
   
3. **`topics_level2.csv`** - L2 subtopic definitions
   - Columns: L1, L2, L2_path, size, label, top_terms
   - Rows: One per subtopic (48)
   
4. **`topics_level3.csv`** - L3 micro-topic definitions
   - Columns: L1, L2, L3, L2_path, L3_path, size, label, top_terms
   - Rows: One per micro-topic (182)
   
5. **`citation_network_stats.json`** - Network metrics
   - Total nodes, edges, density, clustering coefficient, etc.
   
6. **`summary.md`** - Human-readable summary
   - Cluster counts, sizes, silhouette scores, runtime

**Performance**:
- **Runtime**: ~3 minutes total (after enrichment)
  - Text processing: ~20 seconds
  - Citation coupling: ~18 seconds (optimized!)
  - L1 clustering: ~3 seconds
  - L2 clustering: ~31 seconds
  - L3 clustering: ~47 seconds
- **Memory**: ~8GB RAM peak (sparse matrices)
- **Disk**: ~200MB output files

**Algorithm Innovations**:

1. **Inverted Index for Bibliographic Coupling**
   - Naïve approach: O(n²) comparisons = ~33M for 8,110 papers
   - Optimized approach: O(n×k) = ~1.4M operations
   - Speedup: 600× faster (18 sec vs. estimated 3 hours)
   
2. **Sparse Matrix Operations**
   - Citation coupling matrix: 91.3% sparse
   - Only compute non-zero similarities
   - scipy.sparse.csr_matrix for efficiency
   
3. **Recursive NMF for Hierarchy**
   - Apply NMF within parent clusters
   - Allows heterogeneous cluster sizes across levels
   - More flexible than k-means trees

**Key Parameters**:

```python
# Text preprocessing
MIN_DF = 5                 # Min documents for term inclusion
MAX_DF = 0.8               # Max document frequency (ignore common terms)
LSI_COMPONENTS = 200       # Latent dimensions

# Citation coupling
JACCARD_THRESHOLD = 0.0    # Include all non-zero similarities

# Clustering
L1_LINKAGE = 'ward'        # Agglomerative linkage method
L2_L3_METHOD = 'nndsvda'   # NMF initialization
NMF_MAX_ITER = 500         # Convergence iterations

# Validation
METRIC = 'silhouette'      # Cluster quality metric
```

**Troubleshooting**:

**Problem**: Out of memory
- **Solution**: Reduce LSI_COMPONENTS (e.g., 100 instead of 200)
- Or: Process smaller corpus subsets

**Problem**: Slow citation coupling
- **Solution**: Verify inverted index is being used (check console output)
- Ensure scipy.sparse is installed

**Problem**: Poor cluster quality
- **Solution**: Adjust text/citation weights
- Try different L1_ks values
- Ensure citations are properly loaded

**Problem**: Import errors
- **Solution**: Activate conda environment
- Run: `conda env update -f env.yml`

---

## Environment Specification (`env.yml`)

### Python Version
- **Required**: Python 3.13 or 3.12
- **Recommended**: 3.13 (latest features)

### Core Dependencies

**Machine Learning & Clustering**:
- `scikit-learn >= 1.3`: TF-IDF, LSI, NMF, Agglomerative clustering, metrics
- `scipy >= 1.11`: Sparse matrices, optimization, distance metrics

**Data Manipulation**:
- `pandas >= 2.1`: DataFrame operations, CSV/Parquet I/O
- `numpy >= 1.26`: Numerical arrays, linear algebra

**API & Utilities**:
- `requests`: HTTP client for OpenAlex API
- `tqdm`: Progress bars
- `pyarrow`: Parquet file format (fast columnar storage)

**Optional but Recommended**:
- `jupyter`: Interactive notebooks for exploration
- `matplotlib`: Basic plotting
- `seaborn`: Statistical visualizations

### Installation

```bash
# Method 1: From env.yml (recommended)
conda env create -f env.yml
conda activate literature_analyzer

# Method 2: Manual installation
conda create -n literature_analyzer python=3.13
conda activate literature_analyzer
pip install scikit-learn scipy pandas numpy requests tqdm pyarrow

# Verify
python -c "import sklearn, scipy, pandas, numpy; print('Ready!')"
```

---

## Testing & Validation

### Unit Tests (To be added)
```bash
# Run tests
pytest tests/

# Expected tests:
# - test_text_preprocessing.py
# - test_citation_coupling.py
# - test_hybrid_features.py
# - test_clustering.py
```

### Integration Test
```bash
# Run on small sample (100 papers)
python stream_extractor_hybrid.py \
    --input sample_corpus.parquet \
    --outdir test_output/ \
    --l1_ks 3 \
    --l2_ks 3 \
    --l3_ks 2

# Should complete in <10 seconds
# Check test_output/ for correct file structure
```

### Reproduce Published Results
```bash
# Exact parameters from manuscript
python stream_extractor_hybrid.py \
    --input ais_basket_corpus_enriched.parquet \
    --outdir reproduction/ \
    --l1_ks 8 \
    --l2_ks 4,5,6,7,8 \
    --l3_ks 2,3,4 \
    --text_weight 0.6 \
    --citation_weight 0.4

# Compare output to published results
# Expected: 8 streams, 48 subtopics, 182 micro-topics
# Silhouette score: ~0.340 (±0.01 due to numerical precision)
```

---

## Extending the Code

### Add New Feature Types
```python
# In stream_extractor_hybrid.py, add new feature extraction

def extract_author_features(corpus):
    """Extract author collaboration features."""
    # Your implementation
    return author_matrix

# In main pipeline, combine with existing features
hybrid_features = (
    text_weight * text_features +
    citation_weight * citation_features +
    author_weight * author_features
)
```

### Custom Clustering Algorithms
```python
# Replace Agglomerative with your algorithm

from sklearn.cluster import DBSCAN

# Level 1 clustering
l1_clusterer = DBSCAN(eps=0.3, min_samples=10)
l1_labels = l1_clusterer.fit_predict(hybrid_features)
```

### Alternative Topic Models
```python
# Replace NMF with LDA for L2/L3

from sklearn.decomposition import LatentDirichletAllocation

lda = LatentDirichletAllocation(n_components=k, random_state=42)
topics = lda.fit_transform(tfidf_matrix)
```

---

## Performance Optimization Tips

1. **Use Parquet format**: 5-10× faster than CSV for large datasets
2. **Sparse matrices**: Essential for citation coupling (91% savings)
3. **Batch processing**: Process papers in chunks if memory-limited
4. **Parallel execution**: Use `n_jobs=-1` in scikit-learn functions
5. **Caching**: Save intermediate results (TF-IDF, LSI) for reuse

---

## Citation

If you use this code, please cite:

```
[Authors] (2025). Mapping the Information Systems Literature: A Three-Level
Hybrid Clustering Approach Combining Text Similarity and Citation Networks.
[Journal], [Volume]([Issue]), [Pages].

Code: https://github.com/Data-ScienceTech/literature
```

---

## License

**MIT License** - Free to use, modify, and distribute with attribution.

---

## Support

- **Issues**: GitHub repository issues page
- **Email**: [To be added]
- **Documentation**: See ../documentation/ folder

---

**Last Updated**: October 2025  
**Version**: 1.0  
**Status**: Production-ready

