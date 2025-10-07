# Data Directory

This directory contains the corpus data and sample datasets for reproducing the analysis.

---

## Files in This Directory

### 1. `ais_basket_corpus_enriched.parquet` (12.2 MB)
**Purpose**: Complete enriched corpus with citation data (input for clustering)

**Content**:
- **Papers**: 8,110 papers from AIS Basket journals (1990–2024)
- **Citation Data**: 545,865 references from OpenAlex (88.0% coverage)
- **Metadata**: Title, abstract, journal, year, DOI, authors
- **Format**: Apache Parquet (columnar format, optimized for analytics)

**Columns**:
- `abstract`: Paper abstract text (required for text clustering)
- `title`: Paper title
- `journal`: Journal abbreviation (MISQ, ISR, JMIS, JAIS, EJIS, ISJ, JIT, JSIS)
- `year`: Publication year
- `doi`: Digital Object Identifier
- `authors`: Author list (JSON array)
- `referenced_works`: List of cited paper IDs from OpenAlex (JSON array)

**Usage**:
```python
import pandas as pd
corpus = pd.read_parquet('ais_basket_corpus_enriched.parquet')
print(f"Papers: {len(corpus)}")
print(f"With citations: {corpus['referenced_works'].notna().sum()}")
```

**Data Provenance**:
- **Source**: AIS Basket of Eight journals
- **Collection Date**: October 2024
- **Enrichment**: OpenAlex API (https://openalex.org)
- **License**: Metadata CC0 (public domain), abstracts fair use for research

---

### 2. `sample_test.csv` (720 KB)
**Purpose**: Small sample dataset for quick testing (200 papers)

**Content**:
- Stratified sample of 200 papers (25-30 per L1 stream)
- All original columns preserved
- Can be used to test clustering pipeline in ~10 seconds

**Usage**:
```bash
cd ../scripts
python stream_extractor_hybrid.py \
  --input ../data/sample_test.csv \
  --outdir ../outputs/test_run \
  --max_docs 200
```

**Expected Runtime**: ~10-15 seconds on 4-core CPU

---

## Data Statistics

### Corpus Overview

| Metric | Value |
|--------|-------|
| Total papers | 8,110 |
| Date range | 1990–2024 (34 years) |
| Papers with citations | 7,133 (87.9%) |
| Total citations | 545,865 |
| Avg citations per paper | 67.3 |
| Median citations | 42 |

### Journal Distribution

| Journal | Code | Papers | % |
|---------|------|--------|---|
| MIS Quarterly | MISQ | 1,847 | 22.8% |
| Information Systems Research | ISR | 1,523 | 18.8% |
| Journal of MIS | JMIS | 1,289 | 15.9% |
| Journal of AIS | JAIS | 1,134 | 14.0% |
| European J. of IS | EJIS | 1,067 | 13.2% |
| Information Systems Journal | ISJ | 734 | 9.1% |
| Journal of IT | JIT | 298 | 3.7% |
| J. of Strategic IS | JSIS | 218 | 2.7% |

### Temporal Distribution

| Decade | Papers | % |
|--------|--------|---|
| 1990s | 1,156 | 14.3% |
| 2000s | 2,234 | 27.5% |
| 2010s | 2,847 | 35.1% |
| 2020s | 1,873 | 23.1% |

---

## Data Quality

### Citation Coverage Over Time

| Period | Coverage |
|--------|----------|
| 1990–2000 | 73.2% |
| 2001–2010 | 85.1% |
| 2011–2020 | 91.8% |
| 2021–2024 | 88.5% |

**Note**: Coverage improved over time due to better OpenAlex metadata for recent papers.

### Text Quality

- **Abstracts available**: 8,110 / 8,110 (100%)
- **Average abstract length**: 187 words
- **Minimum abstract length**: 25 words
- **Papers with empty abstracts**: 0 (filtered during preprocessing)

---

## Data Collection & Enrichment Process

### 1. Data Collection (Fetching)
**Script**: `current_pipeline/fetcher/fetch_ais_basket_crossref.py`

- Query CrossRef API for AIS Basket journals
- Download metadata: title, abstract, authors, year, DOI
- Filter: Only papers with abstracts
- **Output**: Raw corpus (8,110 papers)
- **Runtime**: ~15 minutes

### 2. Citation Enrichment
**Script**: `current_pipeline/enricher/enrich_ais_basket_openalex.py`

- Match papers to OpenAlex via DOI
- Extract `referenced_works` field (list of cited paper IDs)
- Compute coverage statistics
- **Output**: Enriched corpus with citations
- **Runtime**: ~42 minutes (8,110 API calls)

### 3. Quality Validation
**Scripts**: `current_pipeline/analysis/analyze_ais_basket_coverage.py`

- Check citation coverage by year, journal
- Validate data integrity (no duplicates, valid DOIs)
- Compute network statistics
- **Output**: Coverage reports

---

## File Formats

### Parquet Format
**Why Parquet?**
- ✅ **Fast**: 10× faster to read than CSV
- ✅ **Compact**: 5× smaller file size (12 MB vs 60 MB CSV)
- ✅ **Type-safe**: Preserves data types (lists, dates, integers)
- ✅ **Columnar**: Efficient for analytics (read only needed columns)

**Reading Parquet**:
```python
import pandas as pd
df = pd.read_parquet('ais_basket_corpus_enriched.parquet')
```

**Requirements**: `pip install pyarrow` or `pip install fastparquet`

### CSV Format
**Used for**: Sample data, compatibility

**Encoding**: UTF-8  
**Delimiter**: Comma (`,`)  
**Quoting**: Double quotes for text fields  
**Missing values**: Empty string

---

## Using the Data

### Quick Start: Load Full Corpus
```python
import pandas as pd

# Load enriched corpus
corpus = pd.read_parquet('ais_basket_corpus_enriched.parquet')

print(f"Total papers: {len(corpus)}")
print(f"Columns: {corpus.columns.tolist()}")
print(f"\nSample paper:")
print(corpus.iloc[0][['title', 'year', 'journal']])
```

### Extract Citation Network
```python
import pandas as pd
import json

corpus = pd.read_parquet('ais_basket_corpus_enriched.parquet')

# Parse referenced_works (stored as JSON strings)
corpus['cited_papers'] = corpus['referenced_works'].apply(
    lambda x: json.loads(x) if pd.notna(x) else []
)

# Count citations
corpus['num_citations'] = corpus['cited_papers'].apply(len)

print(f"Average citations per paper: {corpus['num_citations'].mean():.1f}")
print(f"Max citations: {corpus['num_citations'].max()}")
```

### Filter by Journal or Year
```python
# Recent MISQ papers
misq_recent = corpus[
    (corpus['journal'] == 'MIS Quarterly') & 
    (corpus['year'] >= 2020)
]

print(f"MISQ papers 2020+: {len(misq_recent)}")
```

---

## Reproducing the Analysis

### Full Pipeline (45-50 minutes)

```bash
# 1. Activate environment
conda activate isr-literature

# 2. Run clustering on full corpus
cd ../scripts
python stream_extractor_hybrid.py \
  --input ../data/ais_basket_corpus_enriched.parquet \
  --outdir ../outputs/full_run \
  --text_weight 0.6 \
  --citation_weight 0.4 \
  --l1_ks "8"

# 3. Check outputs
ls ../outputs/full_run/
```

**Expected outputs**:
- `doc_assignments.csv`: Paper-level cluster assignments
- `topics_level1.csv`: 8 stream definitions
- `topics_level2.csv`: 48 subtopic definitions
- `citation_network_stats.json`: Network metrics
- `summary.md`: Human-readable results

### Quick Test (10-15 seconds)

```bash
# Use sample data
python stream_extractor_hybrid.py \
  --input ../data/sample_test.csv \
  --outdir ../outputs/test_run \
  --max_docs 200
```

---

## Data Updates

**Current Version**: 1.0 (October 2024)  
**Next Update**: Planned for October 2025  
**Update Process**:
1. Re-fetch from CrossRef (new 2024-2025 papers)
2. Re-enrich via OpenAlex (updated citations)
3. Re-run clustering pipeline
4. Compare results (temporal stability check)

---

## Data Availability

The enriched corpus is available at:

1. **This Repository**: `ISR-submission/data/ais_basket_corpus_enriched.parquet`
2. **GitHub Releases**: https://github.com/Data-ScienceTech/literature/releases
3. **Figshare** (optional): For long-term archival with DOI
4. **Interactive Explorer**: https://data-sciencetech.github.io/literature/

**License**: CC-BY 4.0 (Creative Commons Attribution)

---

## Support

**Questions about data**: carlosdenner@unb.br  
**Data issues**: https://github.com/Data-ScienceTech/literature/issues  
**Citation requests**: See `submission/manuscript.md` for proper citation

---

**Last Updated**: October 7, 2025  
**File Generated**: Via automated data collection pipeline  
**Validated**: Checksums verified, no missing values in required fields
