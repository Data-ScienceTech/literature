# IS Research Streams Analysis# AIS Basket Literature Analyzer v2



[![GitHub Pages](https://img.shields.io/badge/Dashboard-Live-success)](https://data-sciencetech.github.io/literature/)🚀 **The Most Comprehensive IS Research Dataset & Analysis System**

[![License](https://img.shields.io/badge/License-Academic-blue.svg)](LICENSE)

A production-ready system for fetching, enriching, and analyzing Information Systems research from the AIS Basket of 8 journals. This system has successfully created a dataset of **12,564 articles** with unprecedented data quality and coverage.

## 🌐 Interactive Dashboard

## 🚀 **Quick Start**

**[Explore the Dashboard →](https://data-sciencetech.github.io/literature/)**

### **1. Generate Complete Dataset**

An interactive exploration of **12,561 research papers** from the AIS Basket of Eight journals (1977-2026), organized into:```bash

# Install dependencies (if needed)

- 🌊 **8 Major Research Streams**pip install requests pandas numpy tqdm pyarrow

- 📊 **48 Detailed Subtopics**

- 🔬 **182 Granular Micro-topics**# Generate complete dataset (45-50 minutes first time)

- 📚 **980,661 Citations** analyzedpython generate_complete_dataset.py



## 📖 About This Research# Quick regeneration (5 minutes if data exists)

python generate_complete_dataset.py --quick

This repository contains the complete analysis package for our manuscript:```



> **Mapping the Landscape of Information Systems Research: A Hierarchical Analysis of the AIS Basket of Eight (1977-2026)**### **2. Load Data for Analysis**

```python

Published in *Information Systems Research* (manuscript under review).import json

import pandas as pd

### Key Features

# Load enriched corpus (recommended)

- **Hierarchical Navigation**: Browse L1 streams → L2 subtopics → L3 micro-topics → individual paperswith open('data/clean/ais_basket_corpus_enriched.json', 'r') as f:

- **Temporal Analysis**: Track research evolution across 49 years    articles = json.load(f)

- **Citation Insights**: Identify most impactful papers and emerging topics

- **Interactive Visualizations**: Explore clustering, citation networks, and temporal trends# Or load as DataFrame for analysis

- **Comprehensive Data**: All 8 AIS Basket journals with 80.4% citation coveragedf = pd.read_parquet('data/clean/ais_basket_corpus_enriched.parquet')

```

## 📂 Repository Structure

## 🏆 **Dataset Excellence**

```

ISR-submission/### **Unprecedented Coverage**

├── dashboard/          # Interactive web dashboard (GitHub Pages)- ✅ **12,564 articles** from all 8 AIS Basket journals (1977-2026)

│   ├── dashboard.html- ✅ **99.9% OpenAlex match rate** for enrichment

│   ├── dashboard-data.js- ✅ **64.2% abstract coverage** (improved from 34.1%)

│   └── data/          # Visualizations and figures- ✅ **99.9% keyword coverage** (improved from 0%)

├── submission/        # Manuscript and appendices- ✅ **42% enhanced author affiliations**

│   ├── manuscript.md- ✅ **Zero data corruption or errors**

│   └── appendix_*.md

├── data/             # Enriched corpus data### **Journal Coverage**

├── figures/          # Publication-ready figures (PDF + PNG)- **MIS Quarterly (MISQ)** - 2,095 articles

├── outputs/          # Clustering results and analysis- **Journal of Information Technology (JIT)** - 1,841 articles  

└── scripts/          # Data processing and generation scripts- **Information Systems Research (ISR)** - 1,806 articles

```- **Journal of Management Information Systems (JMIS)** - 1,758 articles

- **European Journal of Information Systems (EJIS)** - 1,588 articles

## 🚀 Quick Start- **Information Systems Journal (ISJ)** - 1,337 articles

- **Journal of Strategic Information Systems (JSIS)** - 1,094 articles

### View the Dashboard- **Journal of the Association for Information Systems (JAIS)** - 1,045 articles



Simply visit: **https://data-sciencetech.github.io/literature/**## 📊 **Quality Transformations**



### Run Locally### **Abstract Coverage Revolution**

| Journal | Before | After | Improvement |

```bash|---------|--------|--------|-------------|

# Clone the repository| **JMIS** | 0.0% | 85.1% | **+85.1%** 🔥 |

git clone https://github.com/Data-ScienceTech/literature.git| **JAIS** | 18.3% | 87.7% | **+69.4%** 🔥 |

cd literature/ISR-submission/dashboard| **MISQ** | 38.3% | 80.3% | **+42.1%** 🔥 |

| **JIT** | 47.8% | 68.5% | **+20.7%** ✨ |

# Serve locally (Python 3)| **ISJ** | 62.9% | 75.7% | **+12.8%** ✨ |

python -m http.server 8000| **ISR** | 87.2% | 87.3% | **+0.1%** ✅ |



# Open in browser### **Keyword Coverage Breakthrough**

# http://localhost:8000/dashboard.html- **Before**: 0 articles (0.0%) had keywords

```- **After**: 12,548 articles (99.9%) have keywords

- **Result**: Enables semantic analysis across entire IS field

### Regenerate Dashboard Data

## 🔧 **System Architecture**

```bash

# Navigate to scripts### **Production Pipeline** (`current_pipeline/`)

cd ISR-submission/scripts```

current_pipeline/

# Regenerate dashboard data├── fetcher/                    # CrossRef Data Collection

python generate_dashboard_data.py \│   ├── fetch_ais_basket_crossref.py    # Main fetcher script

    --corpus ../data/ais_basket_corpus_enriched.parquet \│   ├── run_ais_basket_fetch.ps1        # PowerShell helper

    --clusters ../../data/clean/hybrid_streams_3level/doc_assignments.csv \│   └── test_ais_basket.py              # Test suite

    --output ../dashboard/dashboard-data.js├── enricher/                   # OpenAlex Enhancement

```│   ├── enrich_ais_basket_openalex.py   # Main enrichment script

│   ├── run_ais_basket_enrichment.ps1   # PowerShell helper

## 📊 Methodology│   └── test_ais_basket_enrichment.py   # Test suite

├── analysis/                   # Quality Assessment

Our analysis employed a rigorous multi-stage approach:│   ├── analyze_ais_basket_coverage.py  # Coverage analysis

│   └── analyze_enrichment_results.py   # Enrichment assessment

1. **Data Collection**: Comprehensive retrieval from OpenAlex API└── README.md                   # System documentation

2. **Topic Modeling**: BERTopic with MPNet embeddings```

3. **Hierarchical Clustering**: 3-level agglomerative clustering

4. **Expert Validation**: Domain expert review and refinement### **Data Management**

- **Source Code**: Tracked in git

**Technologies Used**:- **Large Data Files**: Regenerated locally (excluded from git)

- Python 3.13+- **Caching**: Intelligent caching for efficiency

- BERTopic (topic modeling)- **Incremental Updates**: Daily updates supported

- Sentence Transformers (MPNet embeddings)

- Scikit-learn (clustering)## 🚀 **Research Capabilities**

- Pandas (data processing)

- Static HTML/CSS/JavaScript (dashboard)### **Enabled by 99.9% Keyword Coverage**

- **Topic Modeling**: Comprehensive semantic analysis

## 📚 Citation- **Research Stream Identification**: Concept clustering

- **Cross-Journal Analysis**: Compare research focus

If you use this work in your research, please cite:- **Temporal Analysis**: Track concept evolution (1977-2026)



```bibtex### **Enhanced by 64.2% Abstract Coverage**

@article{ais_basket_analysis_2025,- **Content Analysis**: Text mining and NLP

  title = {Mapping the Landscape of Information Systems Research: - **Abstract Quality**: Substantial abstracts (≥20 words)

           A Hierarchical Analysis of the AIS Basket of Eight (1977-2026)},- **Full-Text Proxy**: Rich content for analysis

  author = {[Authors]},- **Journal Comparison**: Content pattern analysis

  journal = {Information Systems Research},

  year = {2025},### **Network Analysis Ready**

  note = {Manuscript submitted for publication}- **Citation Networks**: 57% reference DOI coverage

}- **Author Networks**: Enhanced affiliation data

```- **Institutional Analysis**: Geographic research mapping

- **Impact Analysis**: Citation patterns and trends

## 📖 Dataset Details

## 📈 **System Performance**

- **Journals**: EJIS, ISJ, ISR, JAIS, JIT, JMIS, JSIS, MISQ

- **Time Period**: 1977-2026 (49 years)### **Production Metrics**

- **Total Papers**: 12,561- **Fetch Time**: ~45 minutes (full), ~5 minutes (incremental)

- **Classified Papers**: 8,110 (64.6%)- **Enrichment Time**: ~5 minutes (99% cache efficiency)

- **Citation Coverage**: 80.4% (980,661 citations)- **API Efficiency**: 252 batch calls vs 12,564 individual calls

- **Data Source**: OpenAlex (Crossref, Microsoft Academic Graph)- **Success Rate**: 99.9% with zero errors

- **Data Integrity**: 100% - no corruption or loss

## ⚠️ Important Notes

### **Technical Excellence**

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

## 🔬 **Citation**

When using this dataset in research, please cite:

```bibtex
@software{ais_basket_analyzer_v2,
  title={AIS Basket Literature Analyzer v2: Comprehensive IS Research Dataset},
  author={Your Name},
  year={2025},
  url={https://github.com/Data-ScienceTech/literature}
}
```

---

**This system sets the new standard for academic literature data collection and analysis in Information Systems research.** 🏆