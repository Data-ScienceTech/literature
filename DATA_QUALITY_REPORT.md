# IS Corpus Data Collection: Quality Analysis & Recommendations

## 📊 Current Status

### OpenAlex Corpus (Completed ✅)
- **Total papers**: 23,266 from 11 premier IS journals  
- **Date range**: 1800-2025
- **Abstract coverage**: 38.3% overall, 46.8% for 2016+
- **Papers analyzed**: 6,856 (2000+, with abstracts)
- **Clustering**: 29 research streams identified

### Key Findings
| Metric | All Years | 2000+ | 2016+ |
|--------|-----------|-------|-------|
| Total Papers | 23,266 | 17,010 | 7,122 |
| With Abstracts | 8,900 (38.3%) | 6,856 (40.3%) | 3,331 (46.8%) |
| **Data Loss** | **61.7%** | **59.7%** | **53.2%** |

## ❌ Problem: Significant Data Loss

**Only 46.8% of recent papers (2016+) have abstracts in OpenAlex!**

This means we're losing more than half of the available research for analysis.

---

## 💡 Solutions: Three Approaches

### Option A: Crossref-Only (High Quality, Limited Scope) ⭐
**Use the existing `fetch_journals_bibtex.py` script**

**Pros:**
- ✅ 80-90% abstract coverage (Crossref is better)
- ✅ Rich metadata (funding, licenses, author affiliations)
- ✅ Direct citation DOIs
- ✅ Already configured and tested
- ✅ Clean, validated data

**Cons:**
- ❌ Only 4 journals (AMR, MISQ, ORSC, ISR)
- ❌ Missing 7 other IS journals
- ❌ ~2,000-3,000 papers vs 23,266

**Best for:** Deep, high-quality analysis of top-tier IS research

**Command:**
```powershell
cd fetch_corpus
python fetch_journals_bibtex.py --out ../refs_is_2016_2025.bib
```

---

### Option B: Hybrid Enrichment (Best of Both Worlds) 🌟 **RECOMMENDED**
**Use OpenAlex + Crossref enrichment**

**Approach:**
1. Keep all 23,266 papers from OpenAlex (11 journals)
2. Enrich missing abstracts from Crossref using DOI lookups
3. Expected improvement: 46.8% → 70-80% abstract coverage

**Pros:**
- ✅ Comprehensive coverage (all 11 journals)
- ✅ Improved abstract coverage (+20-30%)
- ✅ Retains historical data
- ✅ Best of both APIs

**Cons:**
- ⚠️ Requires ~10,000 Crossref API calls (2-3 hours)
- ⚠️ Some papers still won't have abstracts

**Best for:** Comprehensive IS field analysis with maximum coverage

**Command:**
```powershell
$env:OPENALEX_MAILTO = "your.email@example.com"
python enrich_is_corpus.py
```

---

### Option C: Expand Crossref Coverage (Middle Ground)
**Modify `fetch_journals_bibtex.py` to include all 11 IS journals**

**Approach:**
1. Add the 7 missing journals to the JOURNALS dict
2. Find their ISSNs
3. Run the Crossref fetcher

**Pros:**
- ✅ All 11 journals
- ✅ High abstract coverage (80-90%)
- ✅ Rich Crossref metadata

**Cons:**
- ⚠️ Need to find ISSNs for 7 journals
- ⚠️ Longer fetch time (6-8 hours for all journals)
- ❌ May miss some papers that only OpenAlex has

**Best for:** Comprehensive analysis with Crossref's superior metadata

---

## 🎯 Recommended Strategy: **Option B (Hybrid)**

### Why Hybrid is Best:
1. **Maximum Coverage**: 23,266 papers from all 11 journals
2. **Improved Quality**: Enrich ~3,800 missing abstracts from Crossref  
3. **Fast Enrichment**: Only fetch what's missing (~10K lookups vs 20K full fetch)
4. **Future-Proof**: Can re-enrich as Crossref adds more data

### Implementation Steps:

#### Step 1: Run the Enrichment Script
```powershell
$env:OPENALEX_MAILTO = "carlosdenner@gmail.com"
python enrich_is_corpus.py
```

**Expected Output:**
- Input: 23,266 papers (46.8% with abstracts)
- Output: 23,266 papers (70-80% with abstracts)
- Time: 2-3 hours
- File: `data/clean/is_corpus_enriched.parquet`

#### Step 2: Re-run Analysis on Enriched Data
Update `run_is_corpus_analysis.py` line 25:
```python
# Change from:
corpus = pd.read_parquet('data/clean/is_corpus_all.parquet')

# To:
corpus = pd.read_parquet('data/clean/is_corpus_enriched.parquet')
```

Then run:
```powershell
python run_is_corpus_analysis.py
```

**Expected Results:**
- ~12,000-14,000 papers analyzed (vs current 6,856)
- **100% more data for analysis!**
- Better research stream identification
- More comprehensive coverage

---

## 📈 Expected Impact

### Before Enrichment (Current):
- Papers analyzed: 6,856
- Research streams: 29
- Coverage: 46.8% of 2016+ papers

### After Enrichment (Projected):
- Papers analyzed: ~13,000-15,000
- Research streams: 40-50 (more granular)
- Coverage: 70-80% of 2016+ papers
- **Impact: ~2x more research analyzed!**

---

## 🚀 Quick Start (Recommended Path)

```powershell
# 1. Set your email for Crossref polite pool
$env:OPENALEX_MAILTO = "carlosdenner@gmail.com"

# 2. Run enrichment (2-3 hours, be patient!)
python enrich_is_corpus.py

# 3. Update analysis script to use enriched data
# (Manual edit: change line 25 in run_is_corpus_analysis.py)

# 4. Re-run analysis
python run_is_corpus_analysis.py

# 5. Generate dashboard with better data
python generate_dashboard.py
```

---

## 📝 Alternative: Quick Test with Crossref-Only

If you want to see Crossref quality immediately:

```powershell
cd fetch_corpus

# Modify fetch_journals_bibtex.py to add more IS journals, or run as-is for 4 journals
python fetch_journals_bibtex.py --out ../refs_is_subset.bib

# Then parse and analyze
cd ..
# Use your existing BibTeX analysis pipeline
```

---

## ✅ My Recommendation

**Go with Option B (Hybrid Enrichment)**

1. **Run the enrichment now** (it's automated, just takes time)
2. **While it runs**, review the clustering results we already have
3. **After enrichment**, re-run for comprehensive analysis
4. **Result**: Best possible IS corpus with maximum coverage

The clustering we already did shows the pipeline works! Now let's give it better data to work with.

**Want me to start the enrichment process?**
