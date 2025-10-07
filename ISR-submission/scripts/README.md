# Analysis Scripts

This directory contains the core analysis scripts for reproducing the hybrid clustering results presented in the manuscript.

## Scripts Overview

### 1. `stream_extractor_hybrid.py` ⭐ **Main Clustering Script**
**Purpose**: Performs 3-level hybrid clustering combining text similarity (TF-IDF + LSI) with citation network features (bibliographic coupling).

**Key Features**:
- Level 1: Agglomerative clustering (k=8 major streams)
- Level 2: NMF within each L1 cluster (48 total subtopics)
- Level 3: Recursive NMF for micro-topics (182 total)
- Hybrid weighting: 60% text, 40% citations (optimized via grid search)
- Inverted index optimization for O(n×k) citation coupling computation

**Usage**:
```bash
python stream_extractor_hybrid.py \
  --input ../data/ais_basket_enriched.parquet \
  --outdir ../outputs/clustering_results \
  --text_weight 0.6 \
  --citation_weight 0.4 \
  --l1_clusters 8 \
  --l2_clusters 6 \
  --seed 42
```

**Inputs**:
- Parquet/CSV file with columns: `abstract`, `referenced_works` (list of OpenAlex IDs)
- Optional: `title`, `journal`, `year`, `doi`, `authors`

**Outputs** (written to `--outdir`):
- `doc_assignments.csv`: Paper-level cluster assignments (L1/L2/L3)
- `topics_level1.csv`: L1 stream characteristics (keywords, sizes, silhouette)
- `topics_level2.csv`: L2 subtopic characteristics
- `topics_level3.csv`: L3 micro-topic characteristics
- `citation_network.json`: Network statistics
- `summary.md`: Human-readable summary

**Runtime**: ~3-5 minutes for 8,110 papers on 4-core CPU

---

### 2. `generate_papers_database.py`
**Purpose**: Preprocesses raw corpus data and generates the enriched database for clustering.

**Key Features**:
- Text preprocessing (tokenization, stemming, stop word removal)
- TF-IDF feature extraction
- Citation metadata integration
- Quality filtering

**Usage**:
```bash
python generate_papers_database.py \
  --input ../data/raw_corpus.csv \
  --output ../data/ais_basket_enriched.parquet
```

---

### 3. `create_visualizations.py`
**Purpose**: Generates publication-quality figures for the manuscript.

**Key Features**:
- Temporal evolution plots (Figure 3)
- Citation network visualizations
- Silhouette score comparisons
- Stream size distributions

**Usage**:
```bash
python create_visualizations.py \
  --clusters ../outputs/clustering_results/doc_assignments.csv \
  --outdir ../figures/
```

---

## Dependencies

All scripts require Python 3.8+ and the following packages (see `../submission/requirements.txt`):

**Core**:
- numpy >= 1.24
- pandas >= 2.0
- scipy >= 1.11

**Machine Learning**:
- scikit-learn >= 1.3
- nltk >= 3.8

**Visualization**:
- matplotlib >= 3.7
- seaborn >= 0.12

**Data**:
- pyarrow >= 12.0 (for Parquet support)

## Quick Start

To reproduce the complete analysis pipeline:

```bash
# 1. Set up environment
cd ISR-submission
conda env create -f submission/environment.yml
conda activate isr-literature

# 2. Run fetching (if needed - requires data files)
cd current_pipeline/fetcher
python fetch_ais_basket_crossref.py

# 3. Run enrichment (requires OpenAlex API access)
cd ../enricher
python enrich_ais_basket_openalex.py

# 4. Run clustering
cd ../../scripts
python stream_extractor_hybrid.py \
  --input ../data/ais_basket_enriched.parquet \
  --outdir ../outputs/clustering_results

# 5. Generate visualizations
python create_visualizations.py \
  --clusters ../outputs/clustering_results/doc_assignments.csv \
  --outdir ../figures/
```

## Algorithm Details

### Hybrid Feature Construction

The hybrid similarity matrix combines normalized text and citation features:

```
F_hybrid = w_text × F_text + w_citation × F_citation
```

Where:
- `F_text`: 8,110 × 200 LSI matrix (L2-normalized rows)
- `F_citation`: 8,110 × 8,110 bibliographic coupling matrix (Jaccard-normalized)
- `w_text = 0.60`, `w_citation = 0.40` (optimized via silhouette score)

### Bibliographic Coupling Optimization

**Naive approach**: O(n²) comparisons × O(r²) set intersections = O(n²r²) ≈ 90B operations

**Inverted index approach**:
1. Build inverted index: `reference_id → [papers citing it]`
2. For each paper, iterate through its references and increment co-citation counts
3. Compute Jaccard only for papers with non-zero co-citations

**Complexity**: O(n×r) index + O(n×k×r) coupling ≈ 145M operations (600× faster)

### Clustering Parameters

**Level 1** (Agglomerative):
- Algorithm: Ward linkage
- Distance: Euclidean on hybrid features
- k: 8 (selected via silhouette score grid search over {6, 8, 10, 12})

**Level 2** (NMF):
- Applied within each L1 cluster
- k: Variable (4-8, selected via reconstruction error minimization)
- Result: 48 total subtopics (avg 6 per L1 stream)

**Level 3** (Recursive NMF):
- Applied within each L2 subtopic (only if ≥10 papers)
- k: {2, 3, 4} (selected via reconstruction error)
- Result: 182 total micro-topics

## Validation

Clustering quality is assessed via:

1. **Silhouette Score**: 0.340 (hybrid) vs 0.029 (text-only) = 11.7× improvement
2. **Manual Validation**: 87% agreement on 100 random papers
3. **Keyword Coherence**: 91% of topics have semantically related terms
4. **Comparison to Expert Classifications**: 73% agreement with AIS eLibrary tags

## Support

For questions about these scripts:
- GitHub Issues: https://github.com/Data-ScienceTech/literature/issues
- Corresponding author: carlosdenner@unb.br
