# Journal Streams Analysis - Research Discovery Pipeline

A comprehensive system for discovering and analyzing research streams using embeddings, clustering, and citation networks. This implementation follows the methodology outlined in the `journal_streams_playbook.md`.

## Overview

This project analyzes academic literature to identify research streams through:
- **SPECTER2 embeddings** for semantic similarity
- **Leiden/HDBSCAN clustering** for stream discovery
- **OpenAlex enrichment** for citation networks
- **Temporal burst detection** for trend analysis
- **RPYS analysis** for foundational periods
- **Dialog cards** for comprehensive stream summaries

## Dataset

**Input:** `refs_2016_2025_AMR_MISQ_ORSC_ISR.bib`
- **3,098 papers** from four top journals (2016-2025)
- **Academy of Management Review (AMR)**
- **MIS Quarterly (MISQ)**
- **Organization Science (ORSC)**
- **Information Systems Research (ISR)**
- **100% DOI coverage** for citation analysis
- **75% abstract coverage** for text analysis

## Project Structure

```
literature_analyzer/
├── data/                                    # Data files (created during analysis)
│   ├── parsed_papers_full.csv             # Complete parsed dataset
│   ├── parsed_papers_analysis.csv         # Analysis-ready subset
│   ├── papers_clustered.csv               # With research clusters
│   ├── papers_enriched_final.csv          # With OpenAlex citation data
│   ├── embeddings_specter2.npy            # SPECTER2 embeddings
│   ├── embeddings_umap2d.npy              # UMAP visualization
│   └── openalex_cache/                     # Cached API responses
├── src/                                    # Core modules
│   ├── parse_bib.py                       # BibTeX parsing & normalization
│   ├── embeddings.py                      # SPECTER2 embedding generation
│   ├── clustering.py                      # Leiden & HDBSCAN clustering
│   ├── openalex.py                        # Citation data enrichment
│   ├── networks.py                        # Citation network analysis
│   ├── bursts.py                          # Temporal burst detection
│   ├── rpys.py                            # Reference Publication Year Spectroscopy
│   └── reports.py                         # Dialog card generation
├── notebooks/                             # Analysis pipeline
│   ├── 01_parse_bib.ipynb                # Data parsing & exploration
│   ├── 02_embed_cluster.ipynb            # Embedding & clustering
│   ├── 03_openalex_enrichment.ipynb      # Citation enrichment
│   ├── 04_networks_and_backbones.ipynb   # Network analysis
│   └── 05_reports.ipynb                  # Dialog card generation
├── refs_2016_2025_AMR_MISQ_ORSC_ISR.bib  # Input BibTeX file
├── journal_streams_playbook.md            # Methodology documentation
├── env.yml                                # Conda environment
└── README.md                              # This file
```

## Installation

### 1. Create Conda Environment

```bash
conda env create -f env.yml
conda activate journal-streams
```

### 2. Verify Installation

```python
# Test core dependencies
import pandas as pd
import numpy as np
from sentence_transformers import SentenceTransformer
import networkx as nx
import igraph as ig
import leidenalg
import hdbscan
import umap

print("All dependencies installed successfully!")
```

## Usage

### Quick Start

Run the analysis pipeline using the Jupyter notebooks in order:

```bash
jupyter lab
# Open and run notebooks 01-05 in sequence
```

### Command Line Usage

```python
# Parse BibTeX file
from src.parse_bib import load_bib
df = load_bib("refs_2016_2025_AMR_MISQ_ORSC_ISR.bib")

# Generate embeddings
from src.embeddings import embed_texts
embeddings = embed_texts(df['text'])

# Cluster papers
from src.clustering import knn_graph, leiden_cluster
g = knn_graph(embeddings, k=15)
labels = leiden_cluster(g, resolution=1.0)

# Enrich with citations
from src.openalex import enrich_dataframe
enriched_df = enrich_dataframe(df)

# Generate reports
from src.reports import DialogCardGenerator
generator = DialogCardGenerator(enriched_df, embeddings)
card = generator.generate_cluster_card(cluster_id=0)
```

## Key Features

### 1. Robust BibTeX Parsing
- Handles LaTeX formatting and encoding issues
- Normalizes author names and journal titles
- Extracts DOIs and reference counts
- Creates analysis-ready text fields

### 2. Scientific Embeddings
- **SPECTER2** model optimized for scientific papers
- Batch processing with progress tracking
- Automatic caching for reuse
- Cosine similarity for semantic relationships

### 3. Advanced Clustering
- **Leiden algorithm** on k-NN graphs for high-quality clusters
- **HDBSCAN** alternative with noise detection
- Multiple resolution testing and evaluation
- Stability analysis via bootstrapping

### 4. Citation Network Analysis
- **OpenAlex API** integration with intelligent caching
- Direct citation, co-citation, and bibliographic coupling networks
- Main path analysis for research lineages
- Network backbone extraction

### 5. Temporal Analysis
- **Burst detection** using Kleinberg algorithm and z-score methods
- **RPYS** (Reference Publication Year Spectroscopy) for foundational periods
- Cluster prevalence tracking over time
- Growth rate and trend analysis

### 6. Comprehensive Reporting
- **Dialog cards** for each research stream
- Key papers identification (most cited, central, foundational)
- Research themes extraction
- Current frontier analysis

## Analysis Pipeline

### Stage 1: Data Preparation
1. **Parse BibTeX** → Clean, normalized dataset
2. **Quality analysis** → Missing data, text lengths, temporal coverage
3. **Filter for analysis** → Papers with sufficient text content

### Stage 2: Stream Discovery
1. **Generate embeddings** → SPECTER2 semantic vectors
2. **Build k-NN graph** → Cosine similarity connections
3. **Apply clustering** → Leiden community detection
4. **Evaluate quality** → Silhouette scores, stability analysis

### Stage 3: Citation Enrichment
1. **Query OpenAlex** → Citation counts, referenced works
2. **Build networks** → Direct citations, co-citations, coupling
3. **Analyze patterns** → Temporal citation dynamics
4. **Extract backbones** → Core network structures

### Stage 4: Temporal Analysis
1. **Detect bursts** → Cluster and term prevalence spikes
2. **RPYS analysis** → Foundational reference periods
3. **Main paths** → Key research lineages
4. **Growth patterns** → Stream evolution over time

### Stage 5: Report Generation
1. **Generate cards** → Comprehensive stream summaries
2. **Identify key papers** → Central, foundational, recent works
3. **Extract themes** → Research focus areas
4. **Current frontier** → Emerging directions

## Output Files

### Core Datasets
- `papers_clustered.csv` - Papers with research stream assignments
- `papers_enriched_final.csv` - Full dataset with citation data
- `embeddings_specter2.npy` - High-dimensional semantic embeddings
- `cluster_stats.csv` - Summary statistics for each stream

### Analysis Results
- `clustering_summary.json` - Algorithm performance metrics
- `enrichment_summary.json` - Citation enrichment statistics
- `burst_analysis.json` - Temporal burst detection results
- `dialog_cards.json` - Comprehensive stream summaries

### Visualizations
- Cluster visualizations in UMAP space
- Temporal prevalence trends
- Citation network diagrams
- RPYS spectroscopy plots

## Performance Notes

### Computational Requirements
- **Memory:** 8GB+ RAM recommended for full dataset
- **GPU:** Optional but recommended for SPECTER2 embeddings
- **Storage:** ~2GB for full pipeline with caching
- **Time:** 30-60 minutes for complete analysis

### API Usage
- **OpenAlex:** ~3,000 API calls for full enrichment
- **Rate limiting:** 100ms between requests (respectful usage)
- **Caching:** Automatic to avoid redundant calls
- **Offline mode:** Works with cached data after initial run

## Methodology

This implementation follows established bibliometric practices:

- **Embeddings:** SPECTER2 for scientific document similarity
- **Clustering:** Leiden algorithm for high-quality communities
- **Networks:** Multiple citation network types for comprehensive analysis
- **Temporal:** Kleinberg burst detection and RPYS for historical analysis
- **Validation:** Silhouette scores, stability analysis, and expert review

## Citation

If you use this system in your research, please cite:

```bibtex
@software{journal_streams_analyzer,
  title={Journal Streams Analysis: Research Discovery Pipeline},
  author={[Your Name]},
  year={2024},
  url={https://github.com/[your-repo]/literature_analyzer}
}
```

## License

This project is licensed under the MIT License. See LICENSE file for details.

## Contributing

Contributions welcome! Please see CONTRIBUTING.md for guidelines.

## Support

For questions or issues:
1. Check the documentation in `journal_streams_playbook.md`
2. Review notebook outputs for debugging
3. Open an issue on GitHub with error details

---

**Note:** This system is designed for academic research purposes. Please respect API rate limits and terms of service when using external data sources.
