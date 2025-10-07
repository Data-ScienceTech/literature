# AIS Basket Literature Analyzer v2

🚀 **The Most Comprehensive IS Research Dataset & Analysis System**

A production-ready system for fetching, enriching, and analyzing Information Systems research from the AIS Basket of 8 journals. This system has successfully created a dataset of **12,564 articles** with unprecedented data quality and coverage.

## 🚀 **Quick Start**

### **1. Generate Complete Dataset**
```bash
# Install dependencies (if needed)
pip install requests pandas numpy tqdm pyarrow

# Generate complete dataset (45-50 minutes first time)
python generate_complete_dataset.py

# Quick regeneration (5 minutes if data exists)
python generate_complete_dataset.py --quick
```

### **2. Load Data for Analysis**
```python
import json
import pandas as pd

# Load enriched corpus (recommended)
with open('data/clean/ais_basket_corpus_enriched.json', 'r') as f:
    articles = json.load(f)

# Or load as DataFrame for analysis
df = pd.read_parquet('data/clean/ais_basket_corpus_enriched.parquet')
```

## 🏆 **Dataset Excellence**

### **Unprecedented Coverage**
- ✅ **12,564 articles** from all 8 AIS Basket journals (1977-2026)
- ✅ **99.9% OpenAlex match rate** for enrichment
- ✅ **64.2% abstract coverage** (improved from 34.1%)
- ✅ **99.9% keyword coverage** (improved from 0%)
- ✅ **42% enhanced author affiliations**
- ✅ **Zero data corruption or errors**

### **Journal Coverage**
- **MIS Quarterly (MISQ)** - 2,095 articles
- **Journal of Information Technology (JIT)** - 1,841 articles  
- **Information Systems Research (ISR)** - 1,806 articles
- **Journal of Management Information Systems (JMIS)** - 1,758 articles
- **European Journal of Information Systems (EJIS)** - 1,588 articles
- **Information Systems Journal (ISJ)** - 1,337 articles
- **Journal of Strategic Information Systems (JSIS)** - 1,094 articles
- **Journal of the Association for Information Systems (JAIS)** - 1,045 articles

## 📊 **Quality Transformations**

### **Abstract Coverage Revolution**
| Journal | Before | After | Improvement |
|---------|--------|--------|-------------|
| **JMIS** | 0.0% | 85.1% | **+85.1%** 🔥 |
| **JAIS** | 18.3% | 87.7% | **+69.4%** 🔥 |
| **MISQ** | 38.3% | 80.3% | **+42.1%** 🔥 |
| **JIT** | 47.8% | 68.5% | **+20.7%** ✨ |
| **ISJ** | 62.9% | 75.7% | **+12.8%** ✨ |
| **ISR** | 87.2% | 87.3% | **+0.1%** ✅ |

### **Keyword Coverage Breakthrough**
- **Before**: 0 articles (0.0%) had keywords
- **After**: 12,548 articles (99.9%) have keywords
- **Result**: Enables semantic analysis across entire IS field

## 🔧 **System Architecture**

### **Production Pipeline** (`current_pipeline/`)
```
current_pipeline/
├── fetcher/                    # CrossRef Data Collection
│   ├── fetch_ais_basket_crossref.py    # Main fetcher script
│   ├── run_ais_basket_fetch.ps1        # PowerShell helper
│   └── test_ais_basket.py              # Test suite
├── enricher/                   # OpenAlex Enhancement
│   ├── enrich_ais_basket_openalex.py   # Main enrichment script
│   ├── run_ais_basket_enrichment.ps1   # PowerShell helper
│   └── test_ais_basket_enrichment.py   # Test suite
├── analysis/                   # Quality Assessment
│   ├── analyze_ais_basket_coverage.py  # Coverage analysis
│   └── analyze_enrichment_results.py   # Enrichment assessment
└── README.md                   # System documentation
```

### **Data Management**
- **Source Code**: Tracked in git
- **Large Data Files**: Regenerated locally (excluded from git)
- **Caching**: Intelligent caching for efficiency
- **Incremental Updates**: Daily updates supported

## 🚀 **Research Capabilities**

### **Enabled by 99.9% Keyword Coverage**
- **Topic Modeling**: Comprehensive semantic analysis
- **Research Stream Identification**: Concept clustering
- **Cross-Journal Analysis**: Compare research focus
- **Temporal Analysis**: Track concept evolution (1977-2026)

### **Enhanced by 64.2% Abstract Coverage**
- **Content Analysis**: Text mining and NLP
- **Abstract Quality**: Substantial abstracts (≥20 words)
- **Full-Text Proxy**: Rich content for analysis
- **Journal Comparison**: Content pattern analysis

### **Network Analysis Ready**
- **Citation Networks**: 57% reference DOI coverage
- **Author Networks**: Enhanced affiliation data
- **Institutional Analysis**: Geographic research mapping
- **Impact Analysis**: Citation patterns and trends

## 📈 **System Performance**

### **Production Metrics**
- **Fetch Time**: ~45 minutes (full), ~5 minutes (incremental)
- **Enrichment Time**: ~5 minutes (99% cache efficiency)
- **API Efficiency**: 252 batch calls vs 12,564 individual calls
- **Success Rate**: 99.9% with zero errors
- **Data Integrity**: 100% - no corruption or loss

### **Technical Excellence**
- **Fault Tolerance**: Recovers from any interruption
- **State Persistence**: Incremental updates from last checkpoint
- **Comprehensive Logging**: Full audit trails
- **Multiple Formats**: JSON, Parquet, BibTeX outputs

## 📋 **Usage Examples**

### **Basic Analysis**
```python
import pandas as pd

# Load enriched dataset
df = pd.read_parquet('data/clean/ais_basket_corpus_enriched.parquet')

# Basic statistics
print(f"Total articles: {len(df):,}")
print(f"Year range: {df['year'].min()}-{df['year'].max()}")
print(f"Journals: {df['journal_short'].nunique()}")
print(f"With abstracts: {df['abstract'].notna().sum():,}")
print(f"With keywords: {df['has_keywords'].sum():,}")
```

### **Research Stream Analysis**
```python
# Articles with keywords for topic modeling
topic_ready = df[df['has_keywords'] == True]
print(f"Articles ready for topic modeling: {len(topic_ready):,}")

# Get all keywords across corpus
all_keywords = []
for keywords in df['subject'].dropna():
    if isinstance(keywords, list):
        all_keywords.extend(keywords)

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