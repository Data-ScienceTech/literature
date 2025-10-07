# Mapping the Landscape of Information Systems Research# IS Research Streams Analysis# AIS Basket Literature Analyzer v2



[![GitHub Pages](https://img.shields.io/badge/Dashboard-Live-success)](https://data-sciencetech.github.io/literature/)

[![License](https://img.shields.io/badge/License-Academic-blue.svg)](LICENSE)

[![GitHub Pages](https://img.shields.io/badge/Dashboard-Live-success)](https://data-sciencetech.github.io/literature/)🚀 **The Most Comprehensive IS Research Dataset & Analysis System**

> **A Hierarchical Analysis of the AIS Basket of Eight (1977-2026)**  

> Carlos Denner Santos  [![License](https://img.shields.io/badge/License-Academic-blue.svg)](LICENSE)

> Manuscript submitted to *Information Systems Research*

A production-ready system for fetching, enriching, and analyzing Information Systems research from the AIS Basket of 8 journals. This system has successfully created a dataset of **12,564 articles** with unprecedented data quality and coverage.

This repository contains the complete research package including manuscript, appendices, interactive dashboard, data, and reproducibility scripts for our comprehensive analysis of **12,561 research papers** from the AIS Basket of Eight journals spanning nearly five decades (1977-2026).

## 🌐 Interactive Dashboard

## 🌐 Interactive Dashboard

## 🚀 **Quick Start**

**[→ Explore the Live Dashboard](https://data-sciencetech.github.io/literature/)**

**[Explore the Dashboard →](https://data-sciencetech.github.io/literature/)**

An interactive exploration of 12,561 research papers organized into:

### **1. Generate Complete Dataset**

- 🌊 **8 Major Research Streams** (L1)

- 📊 **48 Detailed Subtopics** (L2)An interactive exploration of **12,561 research papers** from the AIS Basket of Eight journals (1977-2026), organized into:```bash

- 🔬 **182 Granular Micro-topics** (L3)

- 📚 **980,661 Citations** analyzed# Install dependencies (if needed)



### Dashboard Features- 🌊 **8 Major Research Streams**pip install requests pandas numpy tqdm pyarrow



- **Hierarchical Navigation**: Browse streams → subtopics → micro-topics → papers- 📊 **48 Detailed Subtopics**

- **Full-Text Search**: Instant search across titles, abstracts, and research streams

- **Advanced Filtering**: Filter by year range, citation count, and journal- 🔬 **182 Granular Micro-topics**# Generate complete dataset (45-50 minutes first time)

- **Export Functions**: Download filtered results as CSV, BibTeX, or JSON

- **Temporal Analysis**: Interactive charts showing research evolution (1977-2026)- 📚 **980,661 Citations** analyzedpython generate_complete_dataset.py

- **Citation Insights**: Identify most impactful papers and emerging topics

- **Interactive Visualizations**: 11 Chart.js visualizations exploring clustering, citations, and trends



## 📂 Repository Structure## 📖 About This Research# Quick regeneration (5 minutes if data exists)



This repository contains **only publication-ready materials** for the ISR submission:python generate_complete_dataset.py --quick



```This repository contains the complete analysis package for our manuscript:```

ISR-submission/

├── dashboard/              # Interactive web dashboard (GitHub Pages)

│   ├── dashboard.html      # Main dashboard application

│   ├── index.html          # Landing page> **Mapping the Landscape of Information Systems Research: A Hierarchical Analysis of the AIS Basket of Eight (1977-2026)**### **2. Load Data for Analysis**

│   ├── data/               # Visualizations and figures

│   └── dashboard-data.js   # Dataset (gitignored - regenerate locally)```python

│

├── submission/             # Manuscript and appendicesPublished in *Information Systems Research* (manuscript under review).import json

│   ├── manuscript.md       # Main manuscript (Pandoc Markdown)

│   ├── appendix_a.md       # Data Collection & Enrichmentimport pandas as pd

│   ├── appendix_b.md       # Topic Modeling & Clustering

│   ├── appendix_c.md       # Validation Results### Key Features

│   ├── appendix_d.md       # Interactive Dashboard Guide

│   └── references.bib      # Complete bibliography# Load enriched corpus (recommended)

│

├── data/                   # Enriched corpus and classifications- **Hierarchical Navigation**: Browse L1 streams → L2 subtopics → L3 micro-topics → individual paperswith open('data/clean/ais_basket_corpus_enriched.json', 'r') as f:

│   ├── ais_basket_corpus_enriched.parquet    # Main dataset (12,561 papers)

│   └── hybrid_streams_3level/- **Temporal Analysis**: Track research evolution across 49 years    articles = json.load(f)

│       └── doc_assignments.csv               # Hierarchical classifications

│- **Citation Insights**: Identify most impactful papers and emerging topics

├── figures/                # Publication-ready figures

│   ├── *.pdf              # Vector graphics for manuscript- **Interactive Visualizations**: Explore clustering, citation networks, and temporal trends# Or load as DataFrame for analysis

│   └── *.png              # Raster versions for web

│- **Comprehensive Data**: All 8 AIS Basket journals with 80.4% citation coveragedf = pd.read_parquet('data/clean/ais_basket_corpus_enriched.parquet')

├── outputs/                # Analysis outputs

│   └── clustering_results/ # Hierarchical clustering results```

│

└── scripts/                # Data processing scripts## 📂 Repository Structure

    ├── generate_dashboard_data.py  # Regenerate dashboard dataset

    └── README.md                   # Script documentation## 🏆 **Dataset Excellence**



.github/workflows/          # Automated deployment```

└── deploy.yml             # GitHub Pages deployment action

```ISR-submission/### **Unprecedented Coverage**



## 🚀 Quick Start├── dashboard/          # Interactive web dashboard (GitHub Pages)- ✅ **12,564 articles** from all 8 AIS Basket journals (1977-2026)



### View the Dashboard│   ├── dashboard.html- ✅ **99.9% OpenAlex match rate** for enrichment



Simply visit: **https://data-sciencetech.github.io/literature/**│   ├── dashboard-data.js- ✅ **64.2% abstract coverage** (improved from 34.1%)



No installation required!│   └── data/          # Visualizations and figures- ✅ **99.9% keyword coverage** (improved from 0%)



### Run Dashboard Locally├── submission/        # Manuscript and appendices- ✅ **42% enhanced author affiliations**



```bash│   ├── manuscript.md- ✅ **Zero data corruption or errors**

# Clone the repository

git clone https://github.com/Data-ScienceTech/literature.git│   └── appendix_*.md

cd literature/ISR-submission/dashboard

├── data/             # Enriched corpus data### **Journal Coverage**

# Regenerate dashboard data (if needed)

cd ../scripts├── figures/          # Publication-ready figures (PDF + PNG)- **MIS Quarterly (MISQ)** - 2,095 articles

python generate_dashboard_data.py \

    --corpus ../data/ais_basket_corpus_enriched.parquet \├── outputs/          # Clustering results and analysis- **Journal of Information Technology (JIT)** - 1,841 articles  

    --clusters ../../data/clean/hybrid_streams_3level/doc_assignments.csv \

    --output ../dashboard/dashboard-data.js└── scripts/          # Data processing and generation scripts- **Information Systems Research (ISR)** - 1,806 articles



# Serve locally```- **Journal of Management Information Systems (JMIS)** - 1,758 articles

cd ../dashboard

python -m http.server 8000- **European Journal of Information Systems (EJIS)** - 1,588 articles



# Open in browser: http://localhost:8000/dashboard.html## 🚀 Quick Start- **Information Systems Journal (ISJ)** - 1,337 articles

```

- **Journal of Strategic Information Systems (JSIS)** - 1,094 articles

### Read the Manuscript

### View the Dashboard- **Journal of the Association for Information Systems (JAIS)** - 1,045 articles

The complete manuscript and appendices are in Pandoc Markdown format in `ISR-submission/submission/`:



- `manuscript.md` - Main paper

- `appendix_a.md` - Data Collection & Enrichment methodologySimply visit: **https://data-sciencetech.github.io/literature/**## 📊 **Quality Transformations**

- `appendix_b.md` - Topic Modeling & Clustering approach  

- `appendix_c.md` - Validation results and expert review

- `appendix_d.md` - Interactive Dashboard user guide

### Run Locally### **Abstract Coverage Revolution**

To compile to PDF, DOCX, or HTML:

| Journal | Before | After | Improvement |

```bash

cd ISR-submission/submission```bash|---------|--------|--------|-------------|



# Generate PDF (requires Pandoc + LaTeX)# Clone the repository| **JMIS** | 0.0% | 85.1% | **+85.1%** 🔥 |

pandoc manuscript.md -o manuscript.pdf --citeproc

git clone https://github.com/Data-ScienceTech/literature.git| **JAIS** | 18.3% | 87.7% | **+69.4%** 🔥 |

# Generate DOCX (requires Pandoc)

pandoc manuscript.md -o manuscript.docx --citeproccd literature/ISR-submission/dashboard| **MISQ** | 38.3% | 80.3% | **+42.1%** 🔥 |

```

| **JIT** | 47.8% | 68.5% | **+20.7%** ✨ |

## 📊 Dataset Overview

# Serve locally (Python 3)| **ISJ** | 62.9% | 75.7% | **+12.8%** ✨ |

### Coverage Statistics

python -m http.server 8000| **ISR** | 87.2% | 87.3% | **+0.1%** ✅ |

- **Journals**: All 8 AIS Basket journals

  - MIS Quarterly (MISQ): 2,095 articles

  - Journal of Information Technology (JIT): 1,841 articles

  - Information Systems Research (ISR): 1,806 articles# Open in browser### **Keyword Coverage Breakthrough**

  - Journal of Management Information Systems (JMIS): 1,758 articles

  - European Journal of Information Systems (EJIS): 1,588 articles# http://localhost:8000/dashboard.html- **Before**: 0 articles (0.0%) had keywords

  - Information Systems Journal (ISJ): 1,337 articles

  - Journal of Strategic Information Systems (JSIS): 1,094 articles```- **After**: 12,548 articles (99.9%) have keywords

  - Journal of the AIS (JAIS): 1,045 articles

- **Result**: Enables semantic analysis across entire IS field

- **Time Period**: 1977-2026 (49 years)

- **Total Papers**: 12,561### Regenerate Dashboard Data

- **Classified Papers**: 8,110 (64.6% of corpus)

- **Citation Data**: 980,661 citations (80.4% coverage)## 🔧 **System Architecture**

- **Abstract Coverage**: 64.2% (up from 34.1% baseline)

- **Keyword Coverage**: 99.9% (enhanced via OpenAlex)```bash



### Data Quality# Navigate to scripts### **Production Pipeline** (`current_pipeline/`)



- **OpenAlex Match Rate**: 99.9%cd ISR-submission/scripts```

- **Data Integrity**: 100% - zero corruption or errors

- **Enhanced Metadata**: Author affiliations improved by 42%current_pipeline/

- **Validation**: Expert-reviewed hierarchical classifications

# Regenerate dashboard data├── fetcher/                    # CrossRef Data Collection

## 🔬 Methodology

python generate_dashboard_data.py \│   ├── fetch_ais_basket_crossref.py    # Main fetcher script

Our analysis employed a rigorous multi-stage approach:

    --corpus ../data/ais_basket_corpus_enriched.parquet \│   ├── run_ais_basket_fetch.ps1        # PowerShell helper

1. **Data Collection**: Comprehensive retrieval from CrossRef and OpenAlex APIs

2. **Enrichment**: Enhanced abstracts, keywords, and citations via OpenAlex    --clusters ../../data/clean/hybrid_streams_3level/doc_assignments.csv \│   └── test_ais_basket.py              # Test suite

3. **Topic Modeling**: BERTopic with MPNet sentence embeddings

4. **Hierarchical Clustering**: 3-level agglomerative clustering (L1→L2→L3)    --output ../dashboard/dashboard-data.js├── enricher/                   # OpenAlex Enhancement

5. **Expert Validation**: Domain expert review and iterative refinement

6. **Interactive Visualization**: Web-based dashboard with Chart.js```│   ├── enrich_ais_basket_openalex.py   # Main enrichment script



**Technologies Used**:│   ├── run_ais_basket_enrichment.ps1   # PowerShell helper

- Python 3.13+ (data processing)

- BERTopic (topic modeling)## 📊 Methodology│   └── test_ais_basket_enrichment.py   # Test suite

- Sentence Transformers (MPNet embeddings)

- Scikit-learn (hierarchical clustering)├── analysis/                   # Quality Assessment

- Pandas, NumPy (data analysis)

- Chart.js 4.4.0 (interactive visualizations)Our analysis employed a rigorous multi-stage approach:│   ├── analyze_ais_basket_coverage.py  # Coverage analysis

- Static HTML/CSS/JavaScript (dashboard)

- GitHub Pages (deployment)│   └── analyze_enrichment_results.py   # Enrichment assessment



## 📚 Citation1. **Data Collection**: Comprehensive retrieval from OpenAlex API└── README.md                   # System documentation



If you use this work in your research, please cite:2. **Topic Modeling**: BERTopic with MPNet embeddings```



```bibtex3. **Hierarchical Clustering**: 3-level agglomerative clustering

@article{santos2025mapping,

  title = {Mapping the Landscape of Information Systems Research: 4. **Expert Validation**: Domain expert review and refinement### **Data Management**

           A Hierarchical Analysis of the AIS Basket of Eight (1977-2026)},

  author = {Santos, Carlos Denner},- **Source Code**: Tracked in git

  journal = {Information Systems Research},

  year = {2025},**Technologies Used**:- **Large Data Files**: Regenerated locally (excluded from git)

  note = {Manuscript submitted for publication},

  url = {https://github.com/Data-ScienceTech/literature}- Python 3.13+- **Caching**: Intelligent caching for efficiency

}

```- BERTopic (topic modeling)- **Incremental Updates**: Daily updates supported



## 📖 Research Contributions- Sentence Transformers (MPNet embeddings)



This work advances IS research infrastructure through:- Scikit-learn (clustering)## 🚀 **Research Capabilities**



### Novel Methodology- Pandas (data processing)

- **Hierarchical Classification**: First 3-level taxonomy of entire AIS Basket corpus

- **Comprehensive Coverage**: Analysis of all 8 journals over 49 years- Static HTML/CSS/JavaScript (dashboard)### **Enabled by 99.9% Keyword Coverage**

- **Data Enhancement**: 99.9% keyword coverage (vs. 0% baseline)

- **Validation Framework**: Expert-reviewed classification system- **Topic Modeling**: Comprehensive semantic analysis



### Practical Impact## 📚 Citation- **Research Stream Identification**: Concept clustering

- **Interactive Dashboard**: Public tool for exploring IS research landscape

- **Open Dataset**: Reproducible analysis with complete data lineage- **Cross-Journal Analysis**: Compare research focus

- **Research Trends**: Temporal analysis revealing field evolution

- **Citation Networks**: Identification of seminal and emerging worksIf you use this work in your research, please cite:- **Temporal Analysis**: Track concept evolution (1977-2026)



### Technical Innovation

- **Automated Pipeline**: Production-ready data collection system

- **Quality Assurance**: 99.9% enrichment success with zero errors```bibtex### **Enhanced by 64.2% Abstract Coverage**

- **Scalable Architecture**: Efficient batch processing and caching

- **Open Science**: Complete code and data transparency@article{santos2025mapping,- **Content Analysis**: Text mining and NLP



## ⚠️ Important Notes  title = {Mapping the Landscape of Information Systems Research: - **Abstract Quality**: Substantial abstracts (≥20 words)



- **Classified Papers**: 8,110 papers (64.6%) assigned to research streams; 4,451 (35.4%) remain unclassified           A Hierarchical Analysis of the AIS Basket of Eight (1977-2026)},- **Full-Text Proxy**: Rich content for analysis

- **Citation Data**: From OpenAlex; may differ from Google Scholar or Web of Science

- **Temporal Range**: Most papers from 1990+; 2026 papers are early online publications  author = {Santos, Carlos Denner},- **Journal Comparison**: Content pattern analysis

- **Dynamic Research**: Classifications reflect dominant themes; papers may bridge multiple streams

- **Large Data File**: `dashboard-data.js` (7.79 MB) is gitignored; regenerate locally using scripts  journal = {Information Systems Research},



## 📜 License  year = {2025},### **Network Analysis Ready**



This work is provided for **academic and research purposes**.  note = {Manuscript submitted for publication}- **Citation Networks**: 57% reference DOI coverage



- ✅ Use for research and education}- **Author Networks**: Enhanced affiliation data

- ✅ Cite in publications

- ✅ Share dashboard URL```- **Institutional Analysis**: Geographic research mapping

- ❌ Do not redistribute raw data without permission

- ❌ Contact authors for commercial usage- **Impact Analysis**: Citation patterns and trends



## 🙏 Acknowledgments## 📖 Dataset Details



- **OpenAlex**: Open access to scholarly metadata## 📈 **System Performance**

- **CrossRef**: DOI registration and metadata services

- **AIS**: Basket of Eight journal curation- **Journals**: EJIS, ISJ, ISR, JAIS, JIT, JMIS, JSIS, MISQ

- **Journal Publishers**: EJIS, ISJ, ISR, JAIS, JIT, JMIS, JSIS, MISQ

- **Open Source Community**: Python, Pandas, BERTopic, Scikit-learn, Chart.js, Sentence Transformers- **Time Period**: 1977-2026 (49 years)### **Production Metrics**



## 📧 Contact- **Total Papers**: 12,561- **Fetch Time**: ~45 minutes (full), ~5 minutes (incremental)



For questions, feedback, or collaboration:- **Classified Papers**: 8,110 (64.6%)- **Enrichment Time**: ~5 minutes (99% cache efficiency)



- 📧 Open an issue on GitHub- **Citation Coverage**: 80.4% (980,661 citations)- **API Efficiency**: 252 batch calls vs 12,564 individual calls

- 📝 See manuscript for author contact information

- 🌐 Visit the [Interactive Dashboard](https://data-sciencetech.github.io/literature/)- **Data Source**: OpenAlex (Crossref, Microsoft Academic Graph)- **Success Rate**: 99.9% with zero errors



---- **Data Integrity**: 100% - no corruption or loss



**Dashboard Version**: 1.0  ## ⚠️ Important Notes

**Last Updated**: October 2025  

**Data Snapshot**: October 2025  ### **Technical Excellence**

**Repository Structure**: ISR-submission only (cleaned for publication)

- **Unclassified Papers**: 4,451 papers (35.4%) not assigned to clusters- **Fault Tolerance**: Recovers from any interruption

- **Citation Data**: From OpenAlex; may differ from Google Scholar/Web of Science- **State Persistence**: Incremental updates from last checkpoint

- **Temporal Range**: Most papers from 1990+; 2026 = early online publications- **Comprehensive Logging**: Full audit trails

- **Dynamic Research**: Classifications reflect dominant themes; papers may bridge streams- **Multiple Formats**: JSON, Parquet, BibTeX outputs



## 📜 License## 📋 **Usage Examples**



This work is provided for **academic and research purposes**. ### **Basic Analysis**

```python

- ✅ Use for research and educationimport pandas as pd

- ✅ Cite in publications

- ✅ Share dashboard URL# Load enriched dataset

- ❌ Do not redistribute raw data without permissiondf = pd.read_parquet('data/clean/ais_basket_corpus_enriched.parquet')

- ❌ Contact for commercial usage

# Basic statistics

## 🙏 Acknowledgmentsprint(f"Total articles: {len(df):,}")

print(f"Year range: {df['year'].min()}-{df['year'].max()}")

- **OpenAlex**: Open access to scholarly metadataprint(f"Journals: {df['journal_short'].nunique()}")

- **AIS**: Basket of Eight journal curationprint(f"With abstracts: {df['abstract'].notna().sum():,}")

- **Journal Publishers**: EJIS, ISJ, ISR, JAIS, JIT, JMIS, JSIS, MISQprint(f"With keywords: {df['has_keywords'].sum():,}")

- **Open Source**: Python, Pandas, Scikit-learn, BERTopic, Sentence Transformers```



## 📧 Contact### **Research Stream Analysis**

```python

For questions, feedback, or collaboration:# Articles with keywords for topic modeling

- Open an issue on GitHubtopic_ready = df[df['has_keywords'] == True]

- Contact the authors (see manuscript)print(f"Articles ready for topic modeling: {len(topic_ready):,}")



---# Get all keywords across corpus

all_keywords = []

**Dashboard Version**: 1.0  for keywords in df['subject'].dropna():

**Last Updated**: October 2025      if isinstance(keywords, list):

**Data Snapshot**: October 2025        all_keywords.extend(keywords)


print(f"Unique concepts: {len(set(all_keywords)):,}")
```

### **Temporal Analysis**
```python
# Annual publication trends
annual_counts = df.groupby(['year', 'journal_short']).size().unstack(fill_value=0)
print(annual_counts.tail())

# Abstract coverage by year
coverage_by_year = df.groupby('year').agg({
    'abstract': lambda x: (x.notna() & (x.str.len() > 50)).sum(),
    'doi': 'count'
}).eval('coverage_rate = abstract / doi * 100')
```

## 🔄 **Maintenance & Updates**

### **Daily Updates**
```bash
# Quick incremental update (5 minutes)
cd current_pipeline/fetcher
python fetch_ais_basket_crossref.py --incremental

# Re-enrich new articles
cd ../enricher  
python enrich_ais_basket_openalex.py
```

### **Quality Monitoring**
```bash
# Generate fresh analysis reports
cd current_pipeline/analysis
python analyze_ais_basket_coverage.py
python analyze_enrichment_results.py
```

## 📁 **File Structure**

### **Generated Data Files** (after running generation script)
- `data/clean/ais_basket_corpus.json` - Original CrossRef data (38MB)
- `data/clean/ais_basket_corpus_enriched.json` - Enhanced dataset (52MB)
- `data/clean/ais_basket_corpus_enriched.parquet` - Analysis-ready (7MB)

### **Analysis Reports**
- `output/coverage_analysis_*.json` - Detailed coverage statistics
- `output/enrichment_report_*.json` - Enrichment improvements
- `output/*_log_*.log` - Processing logs

### **Cache Directories** (auto-generated)
- `data/raw/crossref_cache/` - CrossRef API cache
- `data/raw/openalex_cache/` - OpenAlex API cache

## 🛠️ **Requirements**

- **Python 3.8+**
- **Packages**: `requests`, `pandas`, `numpy`, `tqdm`, `pyarrow`
- **Internet**: Required for initial data generation
- **Storage**: ~200MB for complete dataset + caches

## 📚 **Documentation**

- **System Overview**: `current_pipeline/README.md`
- **Enrichment Guide**: `current_pipeline/OPENALEX_ENRICHMENT_GUIDE.md`
- **Output Documentation**: `output/README.md`
- **Achievement Summary**: `PROJECT_ACHIEVEMENT_SUMMARY.md`

## 🎯 **Research Impact**

This system represents a breakthrough in IS research infrastructure:

### **Before This System**
- ❌ Fragmented data sources
- ❌ Poor abstract coverage (<35%)
- ❌ No keyword standardization
- ❌ Manual, error-prone processes

### **After This System**
- ✅ Unified, comprehensive dataset
- ✅ 64.2% abstract coverage
- ✅ 99.9% semantic concept coverage
- ✅ Automated, production-ready pipeline

---

**Dashboard Version**: 1.0  
**Last Updated**: October 2025  
**Data Snapshot**: October 2025  
**Repository Structure**: ISR-submission only (cleaned for publication)