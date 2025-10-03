# Implementation Guide for Sample Expansion

**Created:** October 3, 2025  
**Purpose:** Step-by-step guide to expand your literature sample

---

## Quick Decision Matrix

| Scenario | Journals to Add | Time Period | Total Papers | Effort | Benefit |
|----------|----------------|-------------|--------------|--------|---------|
| **Minimal** | None | Extend to 2011 | ~4,600 | Low | Medium |
| **Recommended** | +5 core journals | 2011-2025 | ~8,000 | Medium | High |
| **Aggressive** | +12 journals | 2006-2025 | ~18,000 | High | Very High |
| **Comprehensive** | +20 journals | 2000-2025 | ~35,000 | Very High | Maximum |

---

## Recommended Path: Strategic 9-Journal Expansion

This guide focuses on the **recommended** expansion scenario.

### Target Journals to Add (5 additional)

1. **Academy of Management Journal (AMJ)**
   - ISSN: 0001-4273
   - Type: Empirical management research
   - Complements: AMR (your current sample)
   - Est. papers 2011-2025: ~1,200

2. **Strategic Management Journal (SMJ)**
   - ISSN: 0143-2095
   - Type: Strategic management & competitive advantage
   - Complements: All current journals
   - Est. papers 2011-2025: ~1,500

3. **Administrative Science Quarterly (ASQ)**
   - ISSN: 0001-8392
   - Type: High-theory organizational research
   - Complements: AMR, ORSC
   - Est. papers 2011-2025: ~600

4. **Management Science (MS)**
   - ISSN: 0025-1909
   - Type: Quantitative/analytical management
   - Complements: MISQ, ISR
   - Est. papers 2011-2025: ~2,500

5. **Journal of Business Venturing (JBV)**
   - ISSN: 0883-9026
   - Type: Entrepreneurship & innovation
   - Adds new dimension to current sample
   - Est. papers 2011-2025: ~1,200

**Total addition:** ~7,000 papers  
**New total:** ~10,000 papers (3.2x increase)

---

## Step-by-Step Implementation

### Phase 1: Data Collection (Est. 4-6 hours)

#### Option A: Web of Science (Recommended)

**Prerequisites:**
- Institutional access to Web of Science
- Library login credentials

**Process:**

1. **Access Web of Science**
   - Go to: https://www.webofscience.com/
   - Log in via institutional access

2. **For Each Journal - Run This Query:**

   **Example for AMJ:**
   ```
   Publication Name: "Academy of Management Journal"
   AND
   Publication Year: 2011-2025
   ```

3. **Export Data:**
   - Select all results (or do in batches if >500)
   - Click "Export"
   - Choose format: **BibTeX**
   - Select fields:
     ✓ Author
     ✓ Title  
     ✓ Source
     ✓ Abstract
     ✓ Keywords
     ✓ DOI
     ✓ Cited References
   - Export to file: `AMJ_2011_2025.bib`

4. **Repeat for each journal:**
   - `AMJ_2011_2025.bib`
   - `SMJ_2011_2025.bib`
   - `ASQ_2011_2025.bib`
   - `MS_2011_2025.bib`
   - `JBV_2011_2025.bib`

5. **For existing journals (2011-2015 gap):**
   - `AMR_2011_2015.bib`
   - `MISQ_2011_2015.bib`
   - `ORSC_2011_2015.bib`
   - `ISR_2011_2015.bib`

**Total downloads:** 9 BibTeX files

#### Option B: Scopus

**Access:** https://www.scopus.com/

**Query Structure:**
```
SOURCE-ID("Academy of Management Journal") 
AND PUBYEAR > 2010 AND PUBYEAR < 2026
```

**Export:**
- Select all → Export → BibTeX format
- Include: Abstract, Keywords, References

#### Option C: Publisher Direct (Fallback)

If institutional access unavailable:

1. **SAGE Journals** (AMJ, ASQ):
   - https://journals.sagepub.com/
   - Advanced search → Download citations

2. **Wiley** (SMJ):
   - https://onlinelibrary.wiley.com/journal/10970266
   - Search by date range → Export citations

3. **INFORMS** (MS):
   - https://pubsonline.informs.org/journal/mnsc
   - Browse by year → Export BibTeX

4. **Elsevier** (JBV):
   - https://www.sciencedirect.com/journal/journal-of-business-venturing
   - Advanced search → Export citations

---

### Phase 2: Data Integration (Est. 1-2 hours)

#### Step 2.1: Merge BibTeX Files

Create a Python script to merge all files:

```python
# merge_bibtex.py
import glob
from pathlib import Path

def merge_bib_files(input_pattern, output_file):
    """Merge multiple BibTeX files into one."""
    
    all_content = []
    files = glob.glob(input_pattern)
    
    print(f"Found {len(files)} BibTeX files to merge")
    
    for file in files:
        print(f"Reading: {file}")
        with open(file, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
            all_content.append(content)
    
    # Write merged file
    merged = '\n\n'.join(all_content)
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(merged)
    
    print(f"\nMerged {len(files)} files into: {output_file}")
    return output_file

if __name__ == "__main__":
    # Merge all new journal exports
    merge_bib_files(
        "data/exports/*.bib",
        "data/refs_2011_2025_expanded.bib"
    )
```

**Run:**
```powershell
cd c:\Users\carlo\Dropbox\literature_analyzer_v2\literature
python merge_bibtex.py
```

#### Step 2.2: Validate Merged File

```python
# validate_merged.py
from src.parse_bib import load_bib
import pandas as pd

# Load merged file
df = load_bib("data/refs_2011_2025_expanded.bib")

# Print statistics
print(f"Total papers: {len(df)}")
print(f"Papers with DOI: {df.doi.notna().sum()} ({df.doi.notna().sum()/len(df)*100:.1f}%)")
print(f"Papers with abstract: {df.abstract.notna().sum()} ({df.abstract.notna().sum()/len(df)*100:.1f}%)")
print(f"\nYear range: {df.year.min()} - {df.year.max()}")
print(f"\nJournals:")
print(df.journal.value_counts())

# Check for duplicates
duplicates = df[df.duplicated(subset=['doi'], keep=False)]
print(f"\nDuplicate DOIs found: {len(duplicates)}")

# Save validation report
with open("data/validation_report.txt", "w") as f:
    f.write(f"Validation Report\n")
    f.write(f"================\n\n")
    f.write(f"Total papers: {len(df)}\n")
    f.write(f"DOI coverage: {df.doi.notna().sum()/len(df)*100:.1f}%\n")
    f.write(f"Abstract coverage: {df.abstract.notna().sum()/len(df)*100:.1f}%\n")
    f.write(f"\nJournals:\n{df.journal.value_counts()}\n")
    f.write(f"\nPapers by year:\n{df.year.value_counts().sort_index()}\n")
```

**Expected Output:**
```
Total papers: ~10,000
DOI coverage: >90%
Abstract coverage: >70%
Year range: 2011-2025
Journals: 9 unique
```

#### Step 2.3: Remove Duplicates

```python
# deduplicate.py
from src.parse_bib import load_bib

df = load_bib("data/refs_2011_2025_expanded.bib")

print(f"Before deduplication: {len(df)} papers")

# Remove duplicates by DOI
df_clean = df.drop_duplicates(subset=['doi'], keep='first')

print(f"After deduplication: {len(df_clean)} papers")
print(f"Removed: {len(df) - len(df_clean)} duplicates")

# Save cleaned version
# Re-create BibTeX format or save as CSV for pipeline
df_clean.to_csv("data/papers_expanded_clean.csv", index=False)
```

---

### Phase 3: Update Analysis Scripts (Est. 30 min)

Update your existing scripts to use the new file:

#### 3.1 Update `run_full_analysis.py`

```python
# Change line 99 from:
bib_file = "refs_2016_2025_AMR_MISQ_ORSC_ISR.bib"

# To:
bib_file = "refs_2011_2025_expanded.bib"
```

#### 3.2 Update Other Scripts

```powershell
# Find all references to old filename
Get-ChildItem -Path . -Recurse -Include *.py | Select-String "refs_2016_2025"

# Update each file found
```

#### 3.3 Adjust Computational Parameters

For larger corpus, update clustering parameters:

```python
# In src/clustering.py or your main analysis script

# For ~10,000 papers, adjust:
k_neighbors = 20  # Increase from 15
resolution = 0.8  # Decrease slightly for fewer, larger clusters
min_cluster_size = 25  # Increase from 10-15
```

---

### Phase 4: Re-run Analysis Pipeline (Est. 4-5 hours)

#### 4.1 Test Run First

Start with a subset to verify everything works:

```python
# test_expanded_sample.py
from src.parse_bib import load_bib
import pandas as pd

# Load full file
df = load_bib("data/refs_2011_2025_expanded.bib")

# Create small test sample (1000 random papers)
df_test = df.sample(n=1000, random_state=42)

# Save test sample
df_test.to_csv("data/test_sample_1000.csv", index=False)

print("Test sample created: 1000 papers")
print(f"Journals: {df_test.journal.value_counts()}")
print(f"Year range: {df_test.year.min()}-{df_test.year.max()}")
```

Run analysis on test sample:
```powershell
# Modify run_full_analysis.py to use test_sample_1000.csv
python run_full_analysis.py
```

#### 4.2 Full Analysis Run

Once test succeeds:

```powershell
# Run complete analysis on expanded corpus
python run_full_analysis.py

# Expected runtime: 4-5 hours
# Monitor progress in console output
```

#### 4.3 Compare Results

```python
# compare_samples.py
import pandas as pd
import json

# Load original results
with open("data/original_summary_report.json") as f:
    original = json.load(f)

# Load expanded results  
with open("data/summary_report_complete.json") as f:
    expanded = json.load(f)

# Compare
print("Comparison: Original vs Expanded")
print("="*50)
print(f"Papers: {original.get('total_papers')} → {expanded.get('total_papers')}")
print(f"Clusters: {original.get('n_clusters')} → {expanded.get('n_clusters')}")
print(f"Years: {original.get('year_range')} → {expanded.get('year_range')}")
print(f"Journals: {original.get('n_journals')} → {expanded.get('n_journals')}")
```

---

### Phase 5: Quality Checks (Est. 1 hour)

#### 5.1 Verify Data Quality

```python
# quality_checks.py
from src.parse_bib import load_bib
import pandas as pd

df = load_bib("data/refs_2011_2025_expanded.bib")

print("Quality Check Report")
print("="*50)

# 1. DOI coverage by journal
print("\nDOI Coverage by Journal:")
doi_by_journal = df.groupby('journal')['doi'].apply(
    lambda x: f"{x.notna().sum()}/{len(x)} ({x.notna().sum()/len(x)*100:.1f}%)"
)
print(doi_by_journal)

# 2. Abstract coverage by year
print("\nAbstract Coverage by Year:")
abstract_by_year = df.groupby('year')['abstract'].apply(
    lambda x: f"{x.notna().sum()}/{len(x)} ({x.notna().sum()/len(x)*100:.1f}%)"
)
print(abstract_by_year)

# 3. Text length distribution
print("\nText Length Statistics:")
text_lengths = df.text.str.len()
print(text_lengths.describe())

# 4. Check for anomalies
print("\nAnomalies:")
print(f"- Papers with empty title: {df.title.isna().sum()}")
print(f"- Papers with year < 2011: {(df.year < 2011).sum()}")
print(f"- Papers with year > 2025: {(df.year > 2025).sum()}")
print(f"- Papers with text < 50 chars: {(text_lengths < 50).sum()}")

# Save quality report
with open("data/quality_report.txt", "w") as f:
    f.write("Quality Check Report\n")
    f.write("="*50 + "\n\n")
    f.write(f"DOI Coverage by Journal:\n{doi_by_journal}\n\n")
    f.write(f"Abstract Coverage by Year:\n{abstract_by_year}\n\n")
    f.write(f"Text Length Statistics:\n{text_lengths.describe()}\n")
```

#### 5.2 Verify Clustering Quality

```python
# Check if clusters make sense
import pandas as pd

# Load clustered papers
df_clustered = pd.read_csv("data/papers_clustered_final.csv")

# Examine cluster sizes
print("\nCluster Size Distribution:")
print(df_clustered.cluster.value_counts().sort_index())

# Check for noise cluster
noise_papers = df_clustered[df_clustered.cluster == -1]
print(f"\nNoise cluster (unclustered papers): {len(noise_papers)} ({len(noise_papers)/len(df_clustered)*100:.1f}%)")

# Sample papers from each cluster
for cluster_id in range(5):  # First 5 clusters
    print(f"\nCluster {cluster_id} - Sample Titles:")
    sample = df_clustered[df_clustered.cluster == cluster_id].sample(min(5, len(df_clustered[df_clustered.cluster == cluster_id])))
    for title in sample.title:
        print(f"  - {title[:80]}...")
```

---

## Computational Requirements

### Updated System Requirements

For ~10,000 paper corpus:

| Component | Minimum | Recommended | Optimal |
|-----------|---------|-------------|---------|
| **RAM** | 12 GB | 16 GB | 32 GB |
| **CPU** | 4 cores | 8 cores | 16 cores |
| **Storage** | 5 GB | 10 GB | 20 GB |
| **GPU** | None | GTX 1060 | RTX 3060+ |

### Processing Time Estimates

| Task | Current (3K) | Expanded (10K) | Multiplier |
|------|-------------|----------------|------------|
| Parsing BibTeX | 2 min | 5 min | 2.5x |
| SPECTER2 Embeddings | 15 min | 45 min | 3x |
| Clustering | 5 min | 20 min | 4x |
| OpenAlex Enrichment | 45 min | 150 min | 3.3x |
| Citation Networks | 30 min | 120 min | 4x |
| Report Generation | 10 min | 30 min | 3x |
| **Total** | **~2 hours** | **~6 hours** | **3x** |

*With GPU: Embeddings can be 3-5x faster*

---

## Troubleshooting Common Issues

### Issue 1: BibTeX Parsing Errors

**Problem:** `bibtexparser` fails on some entries

**Solution:**
```python
# Add error handling to parse_bib.py
def load_bib(path):
    try:
        text = pathlib.Path(path).read_text(errors="ignore")
        db = bibtexparser.loads(text)
    except Exception as e:
        print(f"Error parsing {path}: {e}")
        # Try alternative parser
        import bibtexparser
        parser = bibtexparser.bparser.BibTexParser(common_strings=True)
        parser.ignore_nonstandard_types = False
        db = bibtexparser.loads(text, parser=parser)
    # ... rest of function
```

### Issue 2: Memory Errors During Embeddings

**Problem:** Out of memory error with SPECTER2

**Solution:**
```python
# Process in batches
def embed_texts_batched(texts, batch_size=100, model_name="allenai/specter2"):
    model = SentenceTransformer(model_name)
    all_embeddings = []
    
    for i in range(0, len(texts), batch_size):
        batch = texts[i:i+batch_size]
        embs = model.encode(batch, show_progress_bar=True)
        all_embeddings.append(embs)
        
    return np.vstack(all_embeddings)
```

### Issue 3: OpenAlex API Rate Limiting

**Problem:** Too many API calls cause rate limiting

**Solution:**
```python
# Add delays and better caching
import time

def enrich_with_openalex(df, delay=0.2):
    for idx, row in df.iterrows():
        # Check cache first
        if row['doi'] in cache:
            continue
        
        # Make API call
        result = query_openalex(row['doi'])
        
        # Add delay
        time.sleep(delay)  # Increased from 0.1 to 0.2
        
        # Save to cache every 100 requests
        if idx % 100 == 0:
            save_cache()
```

### Issue 4: Clustering Takes Too Long

**Problem:** Leiden clustering is very slow on 10K papers

**Solution:**
```python
# Use faster approximations
from sklearn.cluster import MiniBatchKMeans

# Pre-cluster with k-means, then refine with Leiden
kmeans = MiniBatchKMeans(n_clusters=50, random_state=42)
rough_labels = kmeans.fit_predict(embeddings)

# Apply Leiden within each k-means cluster
# This dramatically speeds up computation
```

---

## Alternative: Incremental Expansion

If full expansion seems overwhelming, do it incrementally:

### Year 1: Add 2 journals
- AMJ (most important complement to AMR)
- SMJ (strategy focus)
- **Total:** ~6,500 papers

### Year 2: Add 2 more journals
- ASQ (theory depth)
- MS (quantitative methods)
- **Total:** ~8,500 papers

### Year 3: Add final journal + extend years
- JBV (entrepreneurship)
- Extend backward to 2011
- **Total:** ~10,000 papers

This spreads out the work and allows you to validate each expansion step.

---

## Summary Checklist

- [ ] Decide on expansion scope (journals + years)
- [ ] Verify institutional access to Web of Science/Scopus
- [ ] Export BibTeX files for new journals
- [ ] Merge and validate data files
- [ ] Remove duplicates
- [ ] Update analysis scripts
- [ ] Test with small sample first
- [ ] Run full analysis pipeline
- [ ] Validate results quality
- [ ] Compare with original analysis
- [ ] Document new methodology
- [ ] Update README and documentation

---

## Next Steps After Expansion

Once expansion is complete:

1. **Validate Stream Quality**
   - Review cluster compositions
   - Check if new journals added meaningful streams
   - Verify temporal patterns make sense

2. **Update Visualizations**
   - Re-generate dashboard with new data
   - Update stream pages
   - Recreate network visualizations

3. **Compare Findings**
   - Document what changed with expansion
   - Identify new research streams discovered
   - Note any streams that merged or split

4. **Update Documentation**
   - Revise README with new corpus details
   - Update methodology documentation
   - Note any parameter changes needed

5. **Consider Publication**
   - Expanded corpus may warrant full paper
   - Document methodology carefully
   - Consider methodological contribution

---

**Questions?** Review the main `EXPANSION_ANALYSIS.md` file for detailed rationale and feasibility assessment.
