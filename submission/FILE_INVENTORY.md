# Complete File Inventory - Literature Analysis Submission

**Last Updated**: October 2025  
**Total Files**: 15 core files + data directories

---

## 📁 Directory: manuscript/

### MANUSCRIPT_DRAFT.md
- **Size**: ~12,500 words
- **Purpose**: Complete academic manuscript for journal submission
- **Status**: Draft ready for author finalization
- **Sections**:
  - Abstract (350 words)
  - Introduction (2,800 words) - 5 research objectives
  - Related Work (2,500 words) - Literature review
  - Methodology (4,200 words) - Complete pipeline
  - Results (2,100 words) - Taxonomy + validation
  - Discussion (2,600 words) - Implications + limitations
  - Conclusion (600 words)
  - 4 Appendices
  - 50+ References (skeleton)
- **To Complete**:
  - Author names and affiliations
  - 3 figures
  - Complete references
  - Hardware specifications
  - Appendix tables

### MANUSCRIPT_PREPARATION_GUIDE.md
- **Size**: ~6,000 words
- **Purpose**: Roadmap for journal submission
- **Contents**:
  - What needs completion
  - Target journal recommendations
  - Submission timeline (4-6 weeks)
  - Open peer review options
  - Checklists
  - Data repository suggestions
- **Use**: Follow step-by-step to finalize submission

---

## 📁 Directory: code/

### stream_extractor_hybrid.py
- **Size**: ~800 lines Python
- **Purpose**: Core 3-level hybrid clustering algorithm
- **Key Features**:
  - Hybrid feature combination (60% text + 40% citations)
  - Inverted index for bibliographic coupling (600× speedup)
  - Three-level hierarchical clustering (L1: Agglomerative, L2/L3: NMF)
  - Sparse matrix optimization (91.3% sparsity)
  - Silhouette score optimization
- **Inputs**:
  - `--input`: Parquet file with corpus + citations
  - `--outdir`: Output directory
  - `--l1_ks`: L1 cluster candidates (default: 8)
  - `--l2_ks`: L2 cluster candidates (default: 4,5,6,7,8)
  - `--l3_ks`: L3 cluster candidates (default: 2,3,4)
  - `--text_weight`: Text feature weight (default: 0.6)
  - `--citation_weight`: Citation weight (default: 0.4)
- **Outputs**:
  - `doc_assignments.csv`: Paper-level assignments
  - `topics_level1.csv`: 8 major streams
  - `topics_level2.csv`: 48 subtopics
  - `topics_level3.csv`: 182 micro-topics
  - `citation_network_stats.json`: Network metrics
  - `summary.md`: Analysis summary
- **Runtime**: ~3 minutes (after data enrichment)
- **Dependencies**: See env.yml

### enrich_ais_basket_openalex.py
- **Size**: ~400 lines Python
- **Purpose**: Collect citation data from OpenAlex API
- **Process**:
  1. Load corpus (12,564 papers)
  2. Match papers to OpenAlex via DOI (99.8% success)
  3. Extract referenced_works for each paper
  4. Save enriched corpus with citation data
- **Output**: `ais_basket_corpus_enriched.parquet`
- **Statistics**:
  - Papers enriched: 8,110
  - Papers with citations: 7,133 (88%)
  - Total references: 545,865
  - Average refs/paper: 58.1
- **Runtime**: ~42 minutes (API rate limits)
- **API**: OpenAlex (free, open access)

### env.yml
- **Purpose**: Conda environment specification
- **Python Version**: 3.13
- **Key Dependencies**:
  - scikit-learn 1.3+ (clustering, NMF, metrics)
  - scipy 1.11+ (sparse matrices, optimization)
  - pandas 2.1+ (data manipulation)
  - numpy 1.26+ (numerical operations)
  - requests (API calls)
  - tqdm (progress bars)
- **Installation**: `conda env create -f env.yml`
- **Environment Name**: literature_analyzer

---

## 📁 Directory: frontend/

### literature-explorer.html
- **Size**: ~650 lines (HTML + embedded CSS)
- **Purpose**: Web-based interactive literature explorer
- **Features**:
  - Responsive header with statistics
  - Methodology banner (6 tool/technique cards)
  - Search box (real-time filtering)
  - Filter chips (All/Citations/Recent/Classics)
  - Hierarchical navigation (L1→L2→L3→Papers)
  - Breadcrumb trails
  - Expandable paper details
  - DOI links to original papers
- **Technology**: Pure HTML5/CSS3 (no frameworks)
- **Browser Support**: All modern browsers
- **Server Required**: No (static files only)
- **Data Loading**: Fetch API loads CSV/JSON from data folder

### literature-explorer.js
- **Size**: ~405 lines JavaScript
- **Purpose**: Application logic for explorer
- **Key Components**:
  - `LiteratureExplorer` class (main application)
  - CSV parser (handles quoted fields)
  - Data loading (4 CSV files + 1 JSON)
  - Navigation logic (selectStream, selectL2, selectL3)
  - Rendering functions (streams, topics, papers)
  - Search and filter implementation
  - Real-time updates
- **Data Files Expected**:
  - `data/clean/hybrid_streams_3level/doc_assignments.csv`
  - `data/clean/hybrid_streams_3level/topics_level1.csv`
  - `data/clean/hybrid_streams_3level/topics_level2.csv`
  - `data/clean/hybrid_streams_3level/topics_level3.csv`
  - `data/clean/hybrid_streams_3level/citation_network_stats.json`
- **No Dependencies**: Vanilla JavaScript (no libraries)

---

## 📁 Directory: documentation/

### LITERATURE_EXPLORER_DOCS.md
- **Size**: ~15,000 words
- **Purpose**: Complete technical documentation
- **Contents**:
  1. **Overview** - System architecture
  2. **Algorithms Explained**:
     - TF-IDF: Formula and implementation
     - LSI (Truncated SVD): Dimensionality reduction
     - Bibliographic Coupling: Jaccard similarity
     - Inverted Index: O(n²) → O(n×k) optimization
     - Hybrid Features: Weighted combination
     - NMF: Matrix factorization for topics
     - Agglomerative Clustering: Ward linkage
  3. **Data Pipeline**: Flowchart and stages
  4. **Tools Documentation**: All 7 tools explained
  5. **Performance Metrics**: Runtime, memory, quality
  6. **Usage Guide**: Step-by-step instructions
  7. **Troubleshooting**: Common issues and solutions
  8. **Customization**: Parameter tuning guide
- **Audience**: Technical readers, reproducibility

### LITERATURE_EXPLORER_README.md
- **Size**: ~2,000 words
- **Purpose**: Quick start guide
- **Contents**:
  - 3 launch methods (Python server, VS Code Live Server, direct open)
  - Key features overview
  - System requirements
  - Quick metrics summary
  - Links to detailed docs
- **Audience**: General users, quick introduction

### PROJECT_COMPLETE.md
- **Size**: ~5,000 words
- **Purpose**: Final project summary
- **Contents**:
  - Complete achievement list
  - Deliverables (code, frontend, docs)
  - Methodology overview
  - Results summary (8→48→182 taxonomy)
  - Quality metrics
  - Deployment instructions
  - Next steps
- **Audience**: Project stakeholders, overview

### FRONTEND_FIXES.md
- **Size**: ~1,500 words
- **Purpose**: Implementation notes for 3-level support
- **Contents**:
  - Problem description (papers not loading)
  - Root causes identified
  - Fixes applied (data paths, L3 loading, stats update)
  - Testing results
  - File changes summary
- **Audience**: Developers, debugging reference

### HYBRID_CLUSTERING_RESULTS.md
- **Size**: ~4,000 words (estimated)
- **Purpose**: Detailed analysis results
- **Contents**:
  - Performance comparison (hybrid vs. text-only)
  - 8 research streams described
  - 48 subtopics overview
  - Citation network statistics
  - Silhouette scores
  - Cluster size distributions
  - Top keywords per cluster
- **Audience**: Researchers, results validation

### CITATION_ENRICHMENT_COMPLETE.md
- **Size**: ~2,000 words (estimated)
- **Purpose**: Data collection documentation
- **Contents**:
  - OpenAlex integration process
  - API usage and rate limits
  - Coverage statistics (88% success)
  - Reference extraction methods
  - Data quality checks
  - Enrichment results summary
- **Audience**: Data provenance, reproducibility

---

## 📁 Directory: graphics/

### README.md
- **Purpose**: Instructions for creating manuscript figures
- **Contents**:
  - Figure 1 specification: Analytical pipeline diagram
  - Figure 2 specification: Sunburst hierarchy visualization
  - Figure 3 specification: Temporal evolution timeline
  - Recommended tools (Python, D3.js, Illustrator)
  - Size requirements (journal-specific)
  - Format guidelines (vector preferred)
  - Color palette suggestions
- **Status**: Instructions ready, figures to be created

### (Figures to be added)
- `figure1_pipeline.pdf` - To be created
- `figure2_sunburst.pdf` - To be created
- `figure3_timeline.pdf` - To be created

---

## 📁 Directory: data/

### README.md
- **Purpose**: Data documentation and access instructions
- **Contents**:
  - Data structure overview
  - File format specifications (CSV, JSON, Parquet)
  - Field definitions (data dictionary)
  - Sample data availability
  - Full dataset access (repository links)
  - Citation requirements
  - Privacy and ethics notes
- **Status**: To be created

### samples/ (To be populated)
- Sample datasets for testing (100 papers subset)
- Example outputs from each analysis stage
- Small enough for GitHub, representative of full data

---

## 📊 Data Files (Referenced, not copied)

These files remain in `../data/clean/hybrid_streams_3level/`:

### doc_assignments.csv
- **Size**: ~100 MB (8,110 rows)
- **Columns**: abstract, title, journal, year, doi, referenced_works, L1, L2, L3, L1_label, L2_label, L3_label
- **Purpose**: Complete paper-level assignments
- **Use**: Primary data for frontend explorer

### topics_level1.csv
- **Size**: ~2 KB (8 rows)
- **Columns**: L1, size, label, top_terms
- **Purpose**: Major research stream definitions
- **Use**: L1 navigation and display

### topics_level2.csv
- **Size**: ~15 KB (48 rows)
- **Columns**: L1, L2, L2_path, size, label, top_terms
- **Purpose**: Detailed subtopic definitions
- **Use**: L2 navigation and display

### topics_level3.csv
- **Size**: ~60 KB (182 rows)
- **Columns**: L1, L2, L3, L2_path, L3_path, size, label, top_terms
- **Purpose**: Granular micro-topic definitions
- **Use**: L3 navigation and display

### citation_network_stats.json
- **Size**: ~10 KB
- **Contents**: Network metrics (nodes, edges, density, clustering coefficient)
- **Purpose**: Network analysis summary
- **Use**: Frontend statistics display

### ais_basket_corpus_enriched.parquet
- **Size**: ~50 MB
- **Rows**: 12,564 papers (full corpus)
- **Columns**: All metadata + referenced_works
- **Purpose**: Input for clustering analysis
- **Use**: Replication of full analysis

---

## 📝 Summary Statistics

### File Counts by Type
- **Markdown Documentation**: 11 files
- **Python Scripts**: 2 files
- **Configuration**: 1 file (env.yml)
- **Web Frontend**: 2 files (HTML + JS)
- **Data Files**: 6 files (CSV, JSON, Parquet)
- **Total**: 22 core files

### Size Summary
- **Code**: ~1,200 lines Python
- **Frontend**: ~1,055 lines (HTML/CSS/JS)
- **Documentation**: ~45,000 words
- **Manuscript**: ~12,500 words
- **Data**: ~160 MB (all outputs)

### Creation Timeline
- **Data Collection**: 42 minutes (OpenAlex API)
- **Analysis**: 3 minutes (clustering pipeline)
- **Frontend Development**: ~4 hours (HTML/CSS/JS)
- **Documentation**: ~6 hours (all markdown files)
- **Manuscript**: ~8 hours (draft writing)
- **Total Project**: ~20 hours (concentrated work)

---

## 🔗 File Dependencies

```
Manuscript
└── References: All documentation + code + results

Code
├── stream_extractor_hybrid.py
│   └── Requires: env.yml, enriched corpus
│   └── Produces: 5 output files (CSV + JSON)
└── enrich_ais_basket_openalex.py
    └── Requires: env.yml, base corpus
    └── Produces: enriched corpus (Parquet)

Frontend
├── literature-explorer.html
│   └── Requires: literature-explorer.js
├── literature-explorer.js
│   └── Requires: 5 data files (CSV + JSON)
└── Data files
    └── Produced by: stream_extractor_hybrid.py

Documentation
└── Supports: All components (standalone)
```

---

## ✅ Completeness Check

### Ready for Use ✅
- [x] Complete analysis pipeline (code)
- [x] Working frontend (web explorer)
- [x] Comprehensive documentation
- [x] Manuscript draft
- [x] Submission guide

### Needs Finalization 📋
- [ ] Manuscript: Author details, figures, references
- [ ] Graphics: Create 3 figures
- [ ] Data: Package sample datasets
- [ ] Code: Add example notebooks
- [ ] Testing: End-to-end replication test

### Optional Enhancements 💡
- [ ] Video tutorial for explorer
- [ ] Jupyter notebooks with analysis examples
- [ ] Automated tests for code
- [ ] Docker container for reproducibility
- [ ] Online hosted version of explorer

---

**Version**: 1.0  
**Completeness**: 85% (core complete, finalization pending)  
**Next Action**: Create figures, complete manuscript author details

