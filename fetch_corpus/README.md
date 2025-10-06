# IS Corpus Fetchers

This directory contains multiple fetchers for building comprehensive IS research datasets.

## 🆕 NEW: AIS Basket of 8 - CrossRef Fetcher (RECOMMENDED)

**The new production-ready fetcher with incremental update support!**

### Quick Start
```powershell
# Test your setup
python test_ais_basket.py

# Run your first fetch
.\run_ais_basket_fetch.ps1
```

### Why Use This?
- ✅ **Incremental updates** - Only fetch new articles (1-2 min daily)
- ✅ **State tracking** - Never re-download existing data
- ✅ **Official AIS Basket** - All 8 premier journals
- ✅ **Authoritative data** - Direct from CrossRef
- ✅ **Citation network** - Full reference DOIs
- ✅ **Multiple formats** - Parquet, JSON, BibTeX

### Documentation
- **`NEW_FETCHER_SUMMARY.md`** - Overview and test results
- **`QUICKSTART_AIS_BASKET.md`** - 5-minute setup guide
- **`README_AIS_BASKET.md`** - Complete documentation
- **`FETCHER_COMPARISON.md`** - Compare with other fetchers

---

## Available Fetchers

### 1. CrossRef Fetcher (NEW) ⭐ RECOMMENDED
- **File**: `fetch_ais_basket_crossref.py`
- **Source**: CrossRef API
- **Journals**: AIS Basket of 8 (~12,500 articles)
- **Updates**: Incremental (fast!)
- **Best for**: Core dataset, daily updates, citations

### 2. OpenAlex Fetcher (EXISTING)
- **File**: `fetch_is_corpus.py`
- **Source**: OpenAlex API
- **Journals**: AIS 11 journals (~15,000 articles)
- **Updates**: Full refetch
- **Best for**: Abstracts, author affiliations, enrichment

### 3. BibTeX Fetcher (EXISTING)
- **File**: `fetch_journals_bibtex.py`
- **Source**: CrossRef + enrichment
- **Journals**: Custom set (4 journals)
- **Updates**: Full refetch
- **Best for**: Deep metadata extraction

See **`FETCHER_COMPARISON.md`** for detailed comparison.

---

# Original OpenAlex Fetcher Documentation

This script fetches academic literature from OpenAlex for the 11 AIS Senior Scholars' Premier Journals.

## Quick Start

### Option 1: Using the PowerShell Helper Script (Recommended)

1. **Edit `run_fetch.ps1`** and replace `your.email@example.com` with your actual email
2. **Run the script**:
   ```powershell
   .\fetch_corpus\run_fetch.ps1
   ```

### Option 2: Manual Run with Environment Variable

```powershell
$env:OPENALEX_MAILTO = "your.email@example.com"
python fetch_corpus/fetch_is_corpus.py
```

### Option 3: Direct Python Run (Limited Rate)

```powershell
python fetch_corpus/fetch_is_corpus.py
```
⚠️ **Warning:** Without an email, you're limited to ~100 requests per 5 minutes and will likely get 403 errors.

## Why Provide an Email?

OpenAlex offers a "polite pool" for users who provide contact information:
- **With email**: 100,000 requests per day
- **Without email**: ~100 requests per 5 minutes

Since this script needs to fetch thousands of papers from 11 journals, the email is essential for reliable operation.

## Output Files

### Cache Files (Raw API Data)
- `data/raw/openalex_cache/*.jsonl` - One JSONL file per journal with raw OpenAlex API responses

### Clean Data Files
- `data/clean/journal_*.parquet` - Individual parquet files for each journal
- `data/clean/is_corpus_all.parquet` - **Combined corpus file with all journals**

## Journals Included

The 11 AIS Senior Scholars' Premier Journals:
1. Decision Support Systems
2. European Journal of Information Systems
3. Information & Management
4. Information and Organization
5. Information Systems Journal
6. Information Systems Research
7. Journal of the Association for Information Systems
8. Journal of Information Technology
9. Journal of Management Information Systems
10. Journal of Strategic Information Systems
11. MIS Quarterly

## Data Fields

Each record includes:
- `openalex_id` - OpenAlex unique identifier
- `doi` - Digital Object Identifier
- `title` - Article title
- `year` - Publication year
- `journal` - Source journal name
- `authors` - List of authors with affiliations
- `abstract` - Full text abstract
- `referenced_works` - List of cited work IDs
- `cited_by_count` - Citation count
- `language` - Language code
- `type` - Publication type

## Estimated Runtime

- With polite pool access: ~30-60 minutes (depending on network speed)
- Without polite pool: Will likely fail due to rate limiting

## Troubleshooting

### 403 Forbidden Errors
- **Solution**: Provide your email via `OPENALEX_MAILTO` environment variable

### No Records for a Journal
- The script will continue and skip journals with no data
- Check if the journal name resolution was successful in the initial output

### Resuming After Interruption
- The script uses caching - already downloaded journals won't be re-fetched
- Delete specific `.jsonl` files in `data/raw/openalex_cache/` to re-fetch individual journals
- Delete all cache files to start completely fresh

## Requirements

- Python 3.11+
- Dependencies: `requests`, `pandas`, `pyarrow`, `tqdm`
- Internet connection

## More Information

- OpenAlex Documentation: https://docs.openalex.org/
- OpenAlex Polite Pool: https://docs.openalex.org/how-to-use-the-api/rate-limits-and-authentication
