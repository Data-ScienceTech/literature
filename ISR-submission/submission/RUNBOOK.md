# Reproduce Results & Generate Submission Artifacts

> Target journal: **Information Systems Research (INFORMS)**  
> Author & corresponding author: **Carlos Denner dos Santos** (carlosdenner@unb.br)

## Overview

This repository contains the complete pipeline for reproducing the hybrid clustering analysis of the AIS "Basket of Eight" literature presented in the manuscript. The analysis pipeline is organized in `current_pipeline/` with three main stages: fetching, enrichment, and analysis.

## Environment Setup

### Option A — requirements.txt
```bash
python -m venv .venv && source .venv/bin/activate  # on Windows: .venv\Scripts\activate
pip install -r submission/requirements.txt
```

### Option B — environment.yml
```bash
conda env create -f submission/environment.yml
conda activate isr-literature
```

## Pipeline Execution Steps

### 1. Fetch Papers from AIS Basket Journals
```bash
cd current_pipeline/fetcher
python fetch_ais_basket_crossref.py
# Output: Raw corpus data from CrossRef API
```

### 2. Enrich with Citation Data (OpenAlex)
```bash
cd current_pipeline/enricher
python enrich_ais_basket_openalex.py
# Output: Enriched corpus with citation references (~8,110 papers, 545,865 citations)
# Runtime: ~42 minutes for full corpus
```

### 3. Analyze Coverage and Build Citation Network
```bash
cd current_pipeline/analysis
python analyze_ais_basket_coverage.py
python analyze_enrichment_results.py
# Output: Coverage statistics, citation network construction
```

### 4. Perform Hybrid Clustering (3-Level Hierarchy)
```bash
cd ../scripts
python stream_extractor_hybrid.py \
  --input ../data/ais_basket_enriched.parquet \
  --outdir ../outputs/clustering_results \
  --text_weight 0.6 \
  --citation_weight 0.4 \
  --l1_clusters 8 \
  --seed 42
# - Text feature extraction (TF-IDF + LSI, 200 dimensions)
# - Bibliographic coupling computation (inverted index optimization)
# - Hybrid feature combination (60% text, 40% citation)
# - Level 1: Agglomerative clustering (k=8)
# - Level 2: NMF within L1 clusters (48 topics total)
# - Level 3: Recursive NMF (182 micro-topics)
# Runtime: ~3-5 minutes for clustering
# Output: doc_assignments.csv, topics_level*.csv, summary.md
```

### 5. Generate Submission Artifacts
```bash
cd tools
python export_l2.py                      # Generates submission/appendix_A_L2.md
python export_sensitivity.py             # Generates submission/appendix_B_sensitivity.md
python build_bib.py                      # Updates submission/references.bib
```

### 6. Render Manuscript (Pandoc)
```bash
cd submission
pandoc manuscript.md --from markdown+smart --citeproc --bibliography=references.bib -o manuscript.docx
pandoc manuscript.md --from markdown+smart --citeproc --bibliography=references.bib -o manuscript.pdf
```

## Hardware Requirements & Timing

**Baseline Configuration**:
- Processor: 4-core 3.0 GHz CPU
- Memory: 32 GB RAM
- Storage: SSD (5 GB for corpus + intermediate files)

**Estimated Runtimes**:
- Data fetching: Variable (depends on API rate limits)
- Citation enrichment: ~42 minutes (8,110 OpenAlex API calls)
- Coverage analysis: ~2 minutes
- Clustering pipeline: ~5 minutes total
  - TF-IDF vectorization: ~8 seconds
  - LSI dimensionality reduction: ~12 seconds
  - Bibliographic coupling (optimized): ~18 seconds
  - L1 clustering: ~3 seconds
  - L2 clustering: ~31 seconds
  - L3 clustering: ~47 seconds
- **Total pipeline**: ~45-50 minutes (97% data collection, 3% analysis)

## Key Optimizations

The inverted index algorithm for bibliographic coupling reduces computational complexity from O(n²) to O(n×k), enabling analysis of 8,000+ papers in under 20 seconds (vs. estimated 3 hours for naive implementation).

## File Structure

```
ISR-submission/
├── scripts/              # Core analysis scripts (see scripts/README.md)
│   ├── stream_extractor_hybrid.py  # Main 3-level clustering implementation
│   ├── generate_papers_database.py # Corpus preprocessing
│   └── create_visualizations.py    # Figure generation
├── current_pipeline/
│   ├── fetcher/          # Data collection scripts
│   ├── enricher/         # Citation enrichment
│   └── analysis/         # Coverage and network analysis
├── tools/                # Export and utility scripts
│   ├── export_l2.py      # Generate Appendix A
│   ├── export_sensitivity.py  # Generate Appendix B
│   └── build_bib.py      # Update references.bib
├── submission/
│   ├── manuscript.md     # Main manuscript
│   ├── references.bib    # Bibliography
│   ├── appendix_*.md     # Generated appendices
│   ├── requirements.txt  # Python dependencies
│   ├── environment.yml   # Conda environment
│   └── RUNBOOK.md        # This file
├── data/                 # Corpus data (enriched parquet files)
├── outputs/              # Clustering results
└── figures/              # Publication-quality visualizations
```

## Web-based Explorer

The interactive literature explorer is deployed at:
**https://data-sciencetech.github.io/literature/**

Source code for the dashboard is in the `dashboard/` directory (HTML/CSS/JavaScript, no server required).

## Support

For questions about reproduction, please open an issue at:
https://github.com/Data-ScienceTech/literature/issues
