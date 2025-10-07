# Literature Analysis Submission Package

**Title**: Mapping the Information Systems Literature: A Three-Level Hybrid Clustering Approach Combining Text Similarity and Citation Networks

**Date**: October 2025  
**Status**: Ready for Open Peer Review Submission

---

## 📁 Folder Structure

```
submission/
├── README.md                    (This file - Overview and navigation)
├── FILE_INVENTORY.md            (Complete file listing with descriptions)
│
├── manuscript/                  (Publication-ready materials)
│   ├── MANUSCRIPT_DRAFT.md      (Main manuscript ~12,500 words)
│   └── MANUSCRIPT_PREPARATION_GUIDE.md (Submission checklist & instructions)
│
├── code/                        (Analysis scripts)
│   ├── stream_extractor_hybrid.py    (3-level hybrid clustering algorithm)
│   ├── enrich_ais_basket_openalex.py (Citation data collection)
│   └── env.yml                       (Python environment specification)
│
├── frontend/                    (Interactive web explorer)
│   ├── literature-explorer.html (Web interface)
│   ├── literature-explorer.js   (Application logic)
│   └── data/                    (Data files - link to main data folder)
│
├── graphics/                    (Figures for manuscript)
│   └── README.md                (Instructions for creating figures)
│
├── data/                        (Analysis outputs & sample data)
│   ├── README.md                (Data documentation)
│   └── samples/                 (Sample datasets for testing)
│
└── documentation/               (Technical documentation)
    ├── LITERATURE_EXPLORER_DOCS.md      (Complete technical guide)
    ├── LITERATURE_EXPLORER_README.md    (Quick start)
    ├── PROJECT_COMPLETE.md              (Project summary)
    ├── FRONTEND_FIXES.md                (Implementation notes)
    ├── HYBRID_CLUSTERING_RESULTS.md     (Analysis results)
    └── CITATION_ENRICHMENT_COMPLETE.md  (Data collection details)
```

---

## 🎯 Quick Start Guide

### For Reviewers

1. **Read the manuscript**: `manuscript/MANUSCRIPT_DRAFT.md`
2. **View the interactive results**: Open `frontend/literature-explorer.html` in a browser
3. **Review methodology**: `documentation/LITERATURE_EXPLORER_DOCS.md`
4. **Examine code**: `code/stream_extractor_hybrid.py`

### For Replication

1. **Install dependencies**: `conda env create -f code/env.yml`
2. **Run analysis**: See instructions in `code/README.md`
3. **Launch explorer**: Open `frontend/literature-explorer.html`

### For Journal Submission

1. **Follow checklist**: `manuscript/MANUSCRIPT_PREPARATION_GUIDE.md`
2. **Create figures**: Instructions in `graphics/README.md`
3. **Format manuscript**: Apply journal-specific template
4. **Package supplementary materials**: Use files from `code/` and `documentation/`

---

## 📊 Key Results Summary

### Methodology Innovation
- **Hybrid Clustering**: Combines 60% text similarity + 40% citation networks
- **Performance**: 11.7× better than text-only clustering (silhouette: 0.340 vs 0.029)
- **Efficiency**: 600× speedup via inverted index algorithm
- **Coverage**: 88% citation coverage (vs. typical 30-50%)

### Three-Level Taxonomy
- **Level 1**: 8 major research streams
- **Level 2**: 48 detailed subtopics
- **Level 3**: 182 granular micro-topics
- **Corpus**: 8,110 papers from AIS Basket journals (1977-2024)

### Validation Metrics
- **Silhouette Score**: 0.340 (professional-grade)
- **Manual Validation**: 87% appropriate assignments
- **Keyword Coherence**: 90%+ across all levels
- **Network**: 2.84M citation coupling edges

---

## 📝 Manuscript Status

### Complete ✅
- Abstract (350 words)
- Introduction with 5 research objectives
- Related Work (comprehensive literature review)
- Methodology (complete pipeline with formulas)
- Results (full taxonomy + validation)
- Discussion (implications, limitations, future work)
- Conclusion
- Reference skeleton (50+ citations)

### To Complete 📋
- [ ] Add author names and affiliations
- [ ] Create 3 figures (pipeline, sunburst, timeline)
- [ ] Complete reference list
- [ ] Fill hardware specifications
- [ ] Generate appendix tables
- [ ] Format for target journal template

**Estimated time to submission**: 2-4 weeks

---

## 🎨 Graphics Needed

See `graphics/README.md` for detailed specifications. Required figures:

1. **Figure 1**: Analytical pipeline diagram
   - Data collection → Feature engineering → Clustering → Validation
   
2. **Figure 2**: Three-level hierarchy sunburst visualization
   - Interactive or static showing 8→48→182 structure
   
3. **Figure 3**: Temporal evolution timeline (1977-2024)
   - Stream emergence and growth patterns

**Tools suggested**: Python (matplotlib/plotly), D3.js, Adobe Illustrator

---

## 💻 Code Overview

### Main Analysis Pipeline

**`stream_extractor_hybrid.py`** - Core clustering algorithm
- Input: Corpus with citation data (Parquet format)
- Output: 3-level topic assignments (CSV)
- Key innovations:
  - Hybrid feature combination (text + citations)
  - Inverted index for bibliographic coupling
  - Recursive NMF for hierarchical clustering
  - Sparse matrix optimization

**`enrich_ais_basket_openalex.py`** - Citation data collection
- Queries OpenAlex API for reference data
- Matches papers via DOI
- Extracts citation networks
- Output: Enriched corpus with 545K references

### Environment

**`env.yml`** - Python dependencies
- Python 3.13
- scikit-learn, scipy, pandas, numpy
- OpenAlex API client
- See file for complete list

---

## 🌐 Interactive Explorer

The web-based literature explorer provides:

- **Hierarchical Navigation**: Browse L1→L2→L3→Papers
- **Search**: Real-time filtering by title, keywords
- **Filters**: By citations, publication year
- **Paper Details**: Full metadata with DOI links
- **Methodology Docs**: Embedded explanations of tools/techniques

**How to use**:
1. Open `frontend/literature-explorer.html` in any modern browser
2. No server required (pure client-side JavaScript)
3. Data automatically loaded from `data/clean/hybrid_streams_3level/`

**Technology**: HTML5, CSS3, Vanilla JavaScript (no frameworks)

---

## 📚 Documentation Overview

### Technical Documentation

**`LITERATURE_EXPLORER_DOCS.md`** (15,000+ words)
- Complete algorithm explanations with formulas
- All 7 tools documented (OpenAlex, TF-IDF, LSI, etc.)
- Performance metrics and optimization details
- Usage guide and troubleshooting

**`LITERATURE_EXPLORER_README.md`**
- Quick start guide (3 launch methods)
- Key features and metrics
- 5-minute introduction

### Project Summaries

**`PROJECT_COMPLETE.md`**
- Final project summary
- Achievements and deliverables
- Usage instructions

**`FRONTEND_FIXES.md`**
- Implementation details for 3-level support
- Debugging notes

### Analysis Results

**`HYBRID_CLUSTERING_RESULTS.md`**
- Complete analysis of 2-level clustering
- Comparison to text-only methods
- Stream descriptions

**`CITATION_ENRICHMENT_COMPLETE.md`**
- Data collection process
- Coverage statistics
- OpenAlex integration details

---

## 🎯 Target Journals

### Primary Recommendation
**Journal of the Association for Information Systems (JAIS)**
- Excellent fit for IS bibliometric research
- Published similar studies (Sidorova et al. 2008)
- Moderate review timeline (2-4 months)
- High impact in IS community

### Alternative Venues

**Tier 1 IS Journals**:
- MIS Quarterly (MISQ) - Methodological innovation focus
- Information Systems Research (ISR) - Analytical studies

**Open Access Options**:
- PLOS ONE - Computational methods track
- F1000Research - Publish-then-review model

**Bibliometrics Journals**:
- Scientometrics - Core venue for this methodology
- Journal of Informetrics - Quantitative information studies

---

## 📦 Data Availability

### Included in Submission
- Sample datasets for testing
- Complete topic assignments (8,110 papers)
- Citation network statistics
- All output CSVs from 3-level clustering

### Full Dataset
- Available via institutional data repository (to be determined)
- DOI will be assigned upon deposit
- Includes complete corpus metadata and enriched citations

### Repository Locations
- **Code**: GitHub (https://github.com/Data-ScienceTech/literature)
- **Interactive Explorer**: GitHub Pages (to be deployed)
- **Data Archive**: Harvard Dataverse or Figshare (recommended)

---

## 🔬 Reproducibility

All analysis is fully reproducible:

1. **Environment**: Specified in `code/env.yml`
2. **Data**: Available via OpenAlex (open API) and AIS eLibrary
3. **Code**: Complete pipeline provided
4. **Parameters**: All hyperparameters documented
5. **Random Seeds**: Can be specified for exact replication

**Expected runtime**: ~45 minutes total
- Citation enrichment: ~42 minutes (API calls)
- Analysis: ~3 minutes (computation)

**Hardware requirements**: Modest (16GB RAM, standard CPU)

---

## 📄 License Information

### Code
- **License**: MIT License
- **Permissions**: Free to use, modify, distribute

### Documentation & Data
- **License**: Creative Commons Attribution 4.0 (CC-BY 4.0)
- **Requirements**: Cite this work when used

### Manuscript
- **Copyright**: Authors retain copyright
- **Journal Rights**: To be determined upon submission
- **Preprint**: Can be posted to arXiv or SocArXiv

---

## 🙏 Acknowledgments

- **Data Source**: OpenAlex (open bibliographic database)
- **Journals**: AIS Basket of Eight publishers
- **Tools**: Python scientific stack (NumPy, SciPy, scikit-learn)

---

## 📧 Contact

For questions about this submission package:
- **GitHub Issues**: [Repository URL]
- **Email**: [To be added]
- **ORCID**: [To be added]

---

## ✅ Pre-Submission Checklist

Use this before journal submission:

### Manuscript
- [ ] Author details added
- [ ] Figures created and embedded
- [ ] References completed
- [ ] Appendices finalized
- [ ] Journal template applied
- [ ] Word count verified
- [ ] All placeholders filled

### Code
- [ ] Scripts tested and working
- [ ] Dependencies documented
- [ ] README files complete
- [ ] Comments added
- [ ] Examples provided

### Data
- [ ] Deposited in repository
- [ ] DOI obtained
- [ ] Data dictionary provided
- [ ] Access instructions clear

### Supplementary Materials
- [ ] All files organized
- [ ] Licenses specified
- [ ] Replication guide complete
- [ ] Interactive demo accessible

---

**Version**: 1.0  
**Last Updated**: October 2025  
**Status**: Ready for final author review before submission

