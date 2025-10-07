# AIS Basket of 8 - Comprehensive CrossRef Fetcher

A robust, incremental fetcher for building and maintaining a complete dataset of IS research from the official AIS Senior Scholars' Basket of 8 journals.

## 🎯 Overview

This fetcher is designed to:
- **Build** a comprehensive dataset of IS research from CrossRef
- **Update** incrementally (only fetch new/updated articles)
- **Track state** to avoid redundant downloads
- **Extract** full metadata including abstracts and citations
- **Output** multiple formats (Parquet, JSON, BibTeX)
- **Scale** to handle thousands of articles efficiently

## 📚 AIS Basket of 8 Journals

The official AIS Senior Scholars' Basket of Journals:

1. **MIS Quarterly (MISQ)** - University of Minnesota
2. **Information Systems Research (ISR)** - INFORMS  
3. **Journal of Management Information Systems (JMIS)** - Taylor & Francis
4. **Journal of the Association for Information Systems (JAIS)** - AIS
5. **European Journal of Information Systems (EJIS)** - Taylor & Francis
6. **Information Systems Journal (ISJ)** - Wiley
7. **Journal of Information Technology (JIT)** - SAGE
8. **Journal of Strategic Information Systems (JSIS)** - Elsevier

Source: [AIS Senior Scholars](https://aisnet.org/page/SeniorScholarBasket)

## 🚀 Quick Start

### Option 1: PowerShell Script (Recommended)

```powershell
# Incremental update (run daily/weekly to get latest articles)
.\fetch_corpus\run_ais_basket_fetch.ps1

# Full fetch from scratch
.\fetch_corpus\run_ais_basket_fetch.ps1 -Full

# Fetch specific journal only
.\fetch_corpus\run_ais_basket_fetch.ps1 -Journal "MIS Quarterly"
```

### Option 2: Direct Python

```powershell
# Incremental update
python fetch_corpus/fetch_ais_basket_crossref.py

# Full fetch
python fetch_corpus/fetch_ais_basket_crossref.py --full

# Fetch from specific date
python fetch_corpus/fetch_ais_basket_crossref.py --from-date 2024-01-01

# Fetch specific journal
python fetch_corpus/fetch_ais_basket_crossref.py --journal "Information Systems Research"
```

## 📋 Requirements

### Python Packages

```bash
pip install requests pandas tqdm pyarrow
```

Or use the existing requirements:

```powershell
pip install -r requirements_minimal.txt
```

### API Access

- **CrossRef API**: Free, no authentication required
- **Polite Pool**: Email is included in user-agent for better rate limits
- **Rate Limits**: ~50 requests/second (polite pool)

## 📁 Output Files

### Main Dataset
- `data/clean/ais_basket_corpus.parquet` - **Main dataset** (recommended for analysis)
  - Optimized columnar format
  - Fast loading with pandas
  - Compressed storage

### Full Metadata
- `data/clean/ais_basket_corpus.json` - Complete metadata including:
  - Full author affiliations
  - All references (DOIs)
  - Funding information
  - License details
  - Subject classifications

### Citations
- `output/ais_basket_YYYYMMDD.bib` - BibTeX format
  - Ready for citation management
  - Compatible with LaTeX, Mendeley, Zotero

### Tracking & Reports
- `data/crossref_state.json` - State tracking file
  - Last update dates per journal
  - Incremental update metadata
  - Run history
  
- `output/fetch_summary_YYYYMMDD.json` - Summary report
  - Article counts by journal/year/type
  - Fetcher statistics
  - Processing metrics

- `output/fetch_log_YYYYMMDD_HHMMSS.log` - Detailed execution log

### Cache
- `data/raw/crossref_cache/*.jsonl` - Raw API responses
  - One file per journal
  - For debugging and recovery

## 🔄 Incremental Updates

The fetcher is designed to be run regularly (daily/weekly) to stay current:

### How It Works

1. **First Run**: Fetches all articles from each journal
   - Saves state with last indexed date
   - Caches raw data for recovery

2. **Subsequent Runs**: Only fetches new/updated articles
   - Uses CrossRef's `from-indexed-date` filter
   - Merges with existing dataset
   - Deduplicates based on DOI

3. **State Tracking**: Maintains `crossref_state.json`
   - Last update timestamp per journal
   - Article counts
   - Run history

### Best Practices

```powershell
# Daily update (recommended for active projects)
.\fetch_corpus\run_ais_basket_fetch.ps1

# Weekly update (sufficient for most research)
.\fetch_corpus\run_ais_basket_fetch.ps1

# Monthly deep check (occasionally do a full fetch to ensure completeness)
.\fetch_corpus\run_ais_basket_fetch.ps1 -Full
```

## 📊 Data Schema

### Parquet/DataFrame Columns

| Column | Type | Description |
|--------|------|-------------|
| `doi` | string | Digital Object Identifier (unique) |
| `title` | string | Article title |
| `journal` | string | Full journal name |
| `journal_short` | string | Journal abbreviation (MISQ, ISR, etc.) |
| `year` | int | Publication year |
| `publication_date` | string | Full publication date |
| `volume` | string | Volume number |
| `issue` | string | Issue number |
| `page` | string | Page range |
| `type` | string | Article type (journal-article, etc.) |
| `author_count` | int | Number of authors |
| `abstract` | string | Full abstract text |
| `reference_count` | int | Number of references |
| `citation_count` | int | Times cited (CrossRef count) |
| `publisher` | string | Publisher name |
| `indexed_date` | string | Last indexed by CrossRef |

### JSON Full Metadata

Additional fields in JSON output:
- `authors`: List of author objects with affiliations
- `references`: List of cited DOIs
- `subject`: Subject classifications
- `license`: License information
- `funder`: Funding sources
- `issn`: Journal ISSNs

## 🎛️ Command-Line Options

```
python fetch_corpus/fetch_ais_basket_crossref.py [OPTIONS]

Options:
  --full              Perform full fetch (ignore state)
  --journal NAME      Fetch only specified journal
  --from-date DATE    Fetch articles indexed from date (YYYY-MM-DD)
  --no-bibtex         Skip BibTeX output generation
  -h, --help          Show help message
```

### Examples

```powershell
# Incremental update (default, recommended)
python fetch_corpus/fetch_ais_basket_crossref.py

# Full fetch from scratch
python fetch_corpus/fetch_ais_basket_crossref.py --full

# Fetch only MIS Quarterly
python fetch_corpus/fetch_ais_basket_crossref.py --journal "MIS Quarterly"

# Fetch articles indexed since January 1, 2024
python fetch_corpus/fetch_ais_basket_crossref.py --from-date 2024-01-01

# Update without generating BibTeX (faster)
python fetch_corpus/fetch_ais_basket_crossref.py --no-bibtex

# Fetch specific journal from specific date
python fetch_corpus/fetch_ais_basket_crossref.py --journal "Information Systems Research" --from-date 2024-01-01
```

## 📈 Performance

### Timing Estimates

| Operation | Duration | Articles |
|-----------|----------|----------|
| Full fetch (all 8 journals) | 15-30 min | ~15,000+ |
| Incremental (daily) | 1-2 min | ~10-50 |
| Incremental (weekly) | 2-5 min | ~50-200 |
| Single journal (full) | 2-5 min | ~1,500-3,000 |

*Times vary based on network speed and CrossRef API performance*

### API Usage

- **Request rate**: ~2 requests/second (polite)
- **Rows per page**: 100 items
- **Retries**: 5 attempts with exponential backoff
- **Timeout**: 30 seconds per request

## 🔍 Data Quality

### Validation

- **Deduplication**: Articles deduplicated by DOI across journals
- **Type filtering**: Only includes valid article types
- **Date validation**: Checks publication date fields
- **Author extraction**: Handles missing/malformed author data
- **Abstract cleaning**: Removes JATS/XML tags

### Coverage

Expected coverage per journal (approximate):
- MISQ: ~3,000+ articles
- ISR: ~2,500+ articles  
- JMIS: ~2,000+ articles
- JAIS: ~1,000+ articles
- EJIS: ~2,000+ articles
- ISJ: ~1,500+ articles
- JIT: ~1,500+ articles
- JSIS: ~1,500+ articles

**Total: ~15,000-20,000 articles** (depending on CrossRef coverage)

## 🛠️ Troubleshooting

### No articles found for a journal

**Possible causes:**
- Journal not yet indexed in CrossRef
- ISSN mismatch
- Network issues

**Solutions:**
```powershell
# Try full fetch
python fetch_corpus/fetch_ais_basket_crossref.py --full --journal "Journal Name"

# Check log file for errors
Get-Content output\fetch_log_*.log | Select-String -Pattern "ERROR"
```

### State file corruption

**Solution:**
```powershell
# Delete state file and start fresh
Remove-Item data\crossref_state.json
python fetch_corpus/fetch_ais_basket_crossref.py --full
```

### Missing packages

**Solution:**
```powershell
# Install required packages
pip install requests pandas tqdm pyarrow

# Or use requirements file
pip install -r requirements_minimal.txt
```

### Rate limiting errors

**Symptoms:** 429 or 403 errors in log

**Solution:**
- Wait a few minutes
- The fetcher automatically retries with backoff
- CrossRef polite pool should handle ~50 req/s

### Partial fetch completion

The fetcher is resumable:
- Cache files are saved per journal
- Already-fetched journals are skipped
- Delete specific cache files to re-fetch individual journals

## 📚 Usage in Analysis Pipeline

### Load Dataset

```python
import pandas as pd

# Load main dataset
df = pd.read_parquet('data/clean/ais_basket_corpus.parquet')

# Filter by journal
misq = df[df['journal_short'] == 'MISQ']

# Filter by year range
recent = df[df['year'] >= 2020]

# Filter by citation count
highly_cited = df[df['citation_count'] >= 100]
```

### Load Full Metadata

```python
import json

# Load complete metadata
with open('data/clean/ais_basket_corpus.json', 'r') as f:
    articles = json.load(f)

# Access full details
for article in articles:
    print(f"DOI: {article['doi']}")
    print(f"Authors: {article['authors']}")
    print(f"References: {article['references'][:5]}...")  # First 5 refs
```

### Integration with Existing Pipeline

The output format is compatible with your existing analysis scripts:

```python
# Your existing analysis can use the new dataset
df = pd.read_parquet('data/clean/ais_basket_corpus.parquet')

# Continue with existing pipeline
# - generate_papers_database.py
# - run_analysis.py
# - visualize_results.py
```

## 🔮 Future Enhancements

Potential additions:
- [ ] Semantic Scholar enrichment (abstracts, citations)
- [ ] OpenAlex cross-referencing
- [ ] Author disambiguation
- [ ] Institution mapping
- [ ] Citation network extraction
- [ ] Altmetrics integration
- [ ] Parallel journal fetching
- [ ] Docker containerization

## 📝 Notes

### CrossRef vs OpenAlex

**CrossRef (this fetcher):**
- ✅ Official DOI registration agency
- ✅ Most authoritative metadata
- ✅ Best citation data (DOIs)
- ✅ Better coverage of recent articles
- ⚠️ Abstracts sometimes missing
- ⚠️ Author affiliations incomplete

**OpenAlex (existing fetcher):**
- ✅ Better abstract coverage
- ✅ Better author/institution data
- ✅ Free & open API
- ⚠️ Occasional indexing delays
- ⚠️ Some metadata inconsistencies

**Recommendation:** Use both! CrossRef for authoritative core dataset, OpenAlex for enrichment.

### Why 8 journals (not 11)?

The **official** AIS Senior Scholars' Basket contains 8 journals. Some sources cite 11, but the authoritative list from AIS includes only these 8 premier IS journals.

## 📧 Support

For issues or questions:
- Check the log files in `output/`
- Review the state file: `data/crossref_state.json`
- Examine cache files: `data/raw/crossref_cache/`

## 📄 License

This fetcher is open source. The data fetched from CrossRef is subject to CrossRef's terms of service and the publishers' copyright policies.

---

**Happy researching! 🎓**

*Build backwards, run forward - Start from today, update for tomorrow*
