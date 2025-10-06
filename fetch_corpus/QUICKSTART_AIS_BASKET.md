# 🚀 Quick Start Guide - AIS Basket Fetcher

## 5-Minute Setup

### Step 1: Test Your Setup
```powershell
python fetch_corpus/test_ais_basket.py
```

This will verify:
- ✅ Python packages installed
- ✅ CrossRef API accessible  
- ✅ All 8 journal ISSNs valid
- ✅ Directory structure ready

### Step 2: Run Your First Fetch
```powershell
# Option A: PowerShell helper (recommended)
.\fetch_corpus\run_ais_basket_fetch.ps1

# Option B: Direct Python
python fetch_corpus/fetch_ais_basket_crossref.py
```

**First run takes 15-30 minutes** to fetch ~15,000+ articles from all 8 journals.

### Step 3: Check Your Data
```powershell
# View summary
Get-Content output\fetch_summary_*.json | ConvertFrom-Json

# Load in Python
python -c "import pandas as pd; df = pd.read_parquet('data/clean/ais_basket_corpus.parquet'); print(df.info())"
```

## Daily/Weekly Updates

After the first fetch, subsequent runs are **FAST** (1-5 minutes):

```powershell
# Just run the same command
.\fetch_corpus\run_ais_basket_fetch.ps1
```

The fetcher automatically:
1. Checks state file for last update
2. Fetches only new/updated articles
3. Merges with existing data
4. Deduplicates by DOI

## Common Commands

```powershell
# Full fetch (start from scratch)
.\fetch_corpus\run_ais_basket_fetch.ps1 -Full

# Fetch specific journal
.\fetch_corpus\run_ais_basket_fetch.ps1 -Journal "MIS Quarterly"

# Fetch since specific date
.\fetch_corpus\run_ais_basket_fetch.ps1 -FromDate "2024-01-01"

# Quick update without BibTeX
.\fetch_corpus\run_ais_basket_fetch.ps1 -NoBibTeX

# Get help
.\fetch_corpus\run_ais_basket_fetch.ps1 -Help
```

## What You Get

```
data/
  clean/
    ais_basket_corpus.parquet   ← Main dataset (USE THIS!)
    ais_basket_corpus.json      ← Full metadata
  crossref_state.json           ← Tracks updates
  raw/
    crossref_cache/             ← Raw API responses

output/
  fetch_summary_YYYYMMDD.json  ← Summary report
  fetch_log_YYYYMMDD_HHMMSS.log ← Detailed log
  ais_basket_YYYYMMDD.bib      ← BibTeX citations
```

## Load Data in Python

```python
import pandas as pd

# Load the dataset
df = pd.read_parquet('data/clean/ais_basket_corpus.parquet')

print(f"Total articles: {len(df):,}")
print(f"\nBy journal:")
print(df['journal_short'].value_counts())

print(f"\nRecent articles (2024):")
recent = df[df['year'] == 2024]
print(f"  {len(recent)} articles published in 2024")

# Filter by journal
misq = df[df['journal_short'] == 'MISQ']
print(f"\nMISQ: {len(misq)} articles")

# High-impact articles
highly_cited = df[df['citation_count'] >= 100]
print(f"\nHighly cited (100+): {len(highly_cited)} articles")
```

## Troubleshooting

### "Module not found" error
```powershell
pip install requests pandas tqdm pyarrow
```

### "No articles found"
- Check network connection
- Review log: `Get-Content output\fetch_log_*.log`
- Try: `.\fetch_corpus\run_ais_basket_fetch.ps1 -Full`

### Want to start fresh?
```powershell
# Delete state and cache
Remove-Item data\crossref_state.json
Remove-Item data\raw\crossref_cache\*.jsonl

# Run full fetch
.\fetch_corpus\run_ais_basket_fetch.ps1 -Full
```

## Next Steps

1. **Daily updates**: Add to task scheduler or cron
2. **Analysis**: Use with your existing pipeline
3. **Enrichment**: Consider adding Semantic Scholar data
4. **Exploration**: Check out the dashboard generators

## Support

- 📖 Full docs: `README_AIS_BASKET.md`
- 🧪 Test suite: `python fetch_corpus/test_ais_basket.py`
- 📊 View logs: `output/fetch_log_*.log`

---

**Build backwards, run forward!** 🚀
