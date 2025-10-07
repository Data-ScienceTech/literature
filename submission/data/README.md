# Data Directory

This directory contains information about data files and sample datasets for testing.

---

## Data Location

**Full datasets** are located in the parent directory structure:
```
../data/clean/hybrid_streams_3level/
├── doc_assignments.csv           (~100 MB, 8,110 papers)
├── topics_level1.csv              (8 streams)
├── topics_level2.csv              (48 subtopics)
├── topics_level3.csv              (182 micro-topics)
├── citation_network_stats.json    (network metrics)
└── ais_basket_corpus_enriched.parquet  (full corpus with citations)
```

**Note**: Full data files are not copied to submission folder to avoid duplication. Use symbolic links or reference the original location.

---

## Data Files Documentation

### 1. doc_assignments.csv

**Purpose**: Complete paper-level assignments to research streams

**Size**: ~100 MB  
**Rows**: 8,110 papers  
**Format**: CSV (UTF-8 encoding)

**Columns**:
| Column | Type | Description | Example |
|--------|------|-------------|---------|
| `abstract` | text | Paper abstract | "this article draws together..." |
| `title` | text | Paper title | "Essential Principles of IS Development" |
| `journal` | text | Journal name | "MIS Quarterly" |
| `year` | integer | Publication year | 1978 |
| `doi` | text | Digital Object Identifier | "10.2307/248938" |
| `referenced_works` | array | List of cited papers (OpenAlex IDs) | "['https://openalex.org/W...', ...]" |
| `L1` | integer | Level 1 stream ID (0-7) | 5 |
| `L2` | integer | Level 2 subtopic ID (0-47) | 12 |
| `L3` | integer | Level 3 micro-topic ID (0-181) | 47 |
| `L1_label` | text | L1 keywords | "decision, decision support, digital..." |
| `L2_label` | text | L2 keywords | "systems, information, development..." |
| `L3_label` | text | L3 keywords | "security, information security..." |

**Usage**:
```python
import pandas as pd
papers = pd.read_csv('doc_assignments.csv')
print(f"Total papers: {len(papers)}")
print(f"Streams: {papers['L1'].nunique()}")
print(papers.groupby('L1_label').size())
```

### 2. topics_level1.csv

**Purpose**: Definitions of 8 major research streams

**Size**: ~2 KB  
**Rows**: 8  
**Format**: CSV

**Columns**:
| Column | Type | Description |
|--------|------|-------------|
| `L1` | integer | Stream ID (0-7) |
| `size` | integer | Number of papers in stream |
| `label` | text | Top 10 keywords (comma-separated) |
| `top_terms` | text | Same as label (for compatibility) |

**Example**:
```csv
L1,size,label,top_terms
0,1554,"consumers, digital, digital transformation, firm, firms...","consumers, digital..."
1,2021,"auction, auctions, bidders, bidding, consumer...","auction, auctions..."
```

### 3. topics_level2.csv

**Purpose**: Definitions of 48 detailed subtopics

**Size**: ~15 KB  
**Rows**: 48  
**Format**: CSV

**Columns**:
| Column | Type | Description |
|--------|------|-------------|
| `L1` | integer | Parent L1 stream ID |
| `L2` | integer | Subtopic ID (0-47) |
| `L2_path` | text | Hierarchical path (e.g., "0.2") |
| `size` | integer | Number of papers |
| `label` | text | Top keywords |
| `top_terms` | text | Same as label |

### 4. topics_level3.csv

**Purpose**: Definitions of 182 granular micro-topics

**Size**: ~60 KB  
**Rows**: 182  
**Format**: CSV

**Columns**:
| Column | Type | Description |
|--------|------|-------------|
| `L1` | integer | Parent L1 stream ID |
| `L2` | integer | Parent L2 subtopic ID |
| `L3` | integer | Micro-topic ID (0-181) |
| `L2_path` | text | Parent path (e.g., "0.2") |
| `L3_path` | text | Full hierarchical path (e.g., "0.2.1") |
| `size` | integer | Number of papers |
| `label` | text | Top keywords |
| `top_terms` | text | Same as label |

### 5. citation_network_stats.json

**Purpose**: Citation network metrics

**Size**: ~10 KB  
**Format**: JSON

**Contents**:
```json
{
  "total_papers": 8110,
  "papers_with_citations": 7133,
  "coverage_percent": 87.9,
  "total_references": 545865,
  "in_corpus_references": 421339,
  "coupling_edges": 2844515,
  "network_density": 0.087,
  "avg_clustering_coefficient": 0.52,
  "avg_path_length": 2.8
}
```

### 6. ais_basket_corpus_enriched.parquet

**Purpose**: Full corpus with citation data (input for clustering)

**Size**: ~50 MB  
**Rows**: 12,564 (includes papers without abstracts)  
**Format**: Parquet (Apache Arrow columnar format)

**Columns**: All metadata fields + `referenced_works` array

**Usage**:
```python
import pandas as pd
corpus = pd.read_parquet('ais_basket_corpus_enriched.parquet')
print(f"Total papers: {len(corpus)}")
print(f"With citations: {corpus['referenced_works'].notna().sum()}")
```

---

## Sample Data (To Be Added)

For testing and demonstration purposes, we will create:

### `samples/sample_100_papers.parquet`
- 100 papers randomly sampled from corpus
- All fields included
- Can be used to test clustering pipeline quickly (~5 seconds)

### `samples/sample_output/`
- Example clustering output from sample data
- All 6 output files (CSV + JSON)
- Shows expected structure

---

## Data Provenance

### Source
- **Journals**: AIS Basket of Eight (MISQ, ISR, JMIS, JAIS, EJIS, ISJ, JIT, JSIS)
- **Timespan**: 1977-2024 (47 years)
- **Collection**: Journal websites, AIS eLibrary

### Enrichment
- **Citation Data**: OpenAlex (https://openalex.org)
- **API Queries**: 8,110 papers matched via DOI
- **Success Rate**: 99.8% match rate
- **Date Collected**: October 2025

### Processing
- **Text Cleaning**: Remove special characters, normalize whitespace
- **Citation Extraction**: Parse `referenced_works` field from OpenAlex
- **Filtering**: Remove papers without abstracts (analysis requires text)
- **Final Corpus**: 8,110 papers with both text and citations

---

## Data Format Specifications

### CSV Files
- **Encoding**: UTF-8
- **Delimiter**: Comma (`,`)
- **Quote Character**: Double quote (`"`)
- **Escaping**: Doubled quotes (`""` for literal `"`)
- **Line Endings**: Unix style (`\n`)
- **Missing Values**: Empty string or `NaN`

### Parquet Files
- **Compression**: Snappy (default)
- **Version**: Parquet format version 2.0
- **Schema**: Embedded (self-describing)
- **Benefits**: 
  - 10× faster to read than CSV
  - 5× smaller file size
  - Preserves data types (no string conversion)

### JSON Files
- **Format**: Pretty-printed (indented)
- **Encoding**: UTF-8
- **Number Format**: Standard JSON numbers (no special encoding)

---

## Data Statistics

### Corpus Coverage

| Metric | Value |
|--------|-------|
| Total AIS Basket papers | 12,564 |
| Papers with abstracts | 8,110 (64.5%) |
| Papers with citations | 7,133 (87.9% of analyzed) |
| Average citations per paper | 58.1 |
| Total citation references | 545,865 |
| In-corpus citations | 421,339 |
| Citation network edges | 2,844,515 |

### Temporal Distribution

| Decade | Papers | Percentage |
|--------|--------|------------|
| 1970s | 89 | 1.1% |
| 1980s | 247 | 3.0% |
| 1990s | 1,156 | 14.3% |
| 2000s | 2,234 | 27.5% |
| 2010s | 2,847 | 35.1% |
| 2020s | 1,537 | 19.0% |

### Journal Distribution

| Journal | Code | Papers | Percentage |
|---------|------|--------|------------|
| MIS Quarterly | MISQ | 1,847 | 22.8% |
| Information Systems Research | ISR | 1,523 | 18.8% |
| Journal of MIS | JMIS | 1,289 | 15.9% |
| Journal of AIS | JAIS | 1,134 | 14.0% |
| European J. of IS | EJIS | 1,067 | 13.2% |
| Information Systems Journal | ISJ | 734 | 9.1% |
| Journal of IT | JIT | 298 | 3.7% |
| J. of Strategic IS | JSIS | 218 | 2.7% |

---

## Data Access & Privacy

### Public Data
All metadata (titles, abstracts, authors, journals, years, DOIs) is publicly available:
- Journal websites
- AIS eLibrary
- OpenAlex database

### No Personal Data
- No email addresses, affiliations, or contact information
- Only published scholarly information
- All papers are public domain or openly accessible

### Ethical Considerations
- Data collection follows robots.txt and API terms of service
- OpenAlex data is CC0 (public domain)
- Journal metadata is factual (not copyrightable)
- Abstracts used under fair use for research purposes

### Reuse
- Citation network data: CC0 (from OpenAlex)
- Clustering assignments: Our creation, CC-BY 4.0
- Original papers: Subject to publisher copyright (not redistributed)

---

## Data Availability Statement (For Manuscript)

```
Data Availability

The complete dataset including paper assignments, topic definitions, and 
citation network statistics is available at:

- Harvard Dataverse: https://doi.org/[DOI] (recommended)
- GitHub Repository: https://github.com/Data-ScienceTech/literature
- Interactive Explorer: https://data-sciencetech.github.io/literature/

Original corpus metadata can be reconstructed using:
- AIS eLibrary (https://aisel.aisnet.org/)
- OpenAlex API (https://openalex.org/)

All data is released under CC-BY 4.0 license. Citation requests:
[Standard citation format]
```

---

## Using the Data

### Load in Python
```python
import pandas as pd

# Load paper assignments
papers = pd.read_csv('doc_assignments.csv')

# Load topic definitions
l1 = pd.read_csv('topics_level1.csv')
l2 = pd.read_csv('topics_level2.csv')
l3 = pd.read_csv('topics_level3.csv')

# Load network stats
import json
with open('citation_network_stats.json') as f:
    stats = json.load(f)

# Example analysis: Papers per stream
print(papers.groupby('L1_label').size().sort_values(ascending=False))

# Example: Evolution over time
temporal = papers.groupby(['year', 'L1_label']).size()
print(temporal.unstack(fill_value=0))
```

### Load in R
```r
library(tidyverse)

# Load paper assignments
papers <- read_csv('doc_assignments.csv')

# Load topic definitions
l1 <- read_csv('topics_level1.csv')
l2 <- read_csv('topics_level2.csv')
l3 <- read_csv('topics_level3.csv')

# Example analysis
papers %>%
  group_by(L1_label) %>%
  summarise(count = n()) %>%
  arrange(desc(count))
```

### Load in Excel
- Open CSV files directly
- Use "Text to Columns" if needed
- Large files (doc_assignments.csv) may be slow - consider filtering first

---

## Troubleshooting

**Problem**: CSV not loading correctly (encoding issues)
- **Solution**: Specify UTF-8 encoding explicitly
  ```python
  pd.read_csv('file.csv', encoding='utf-8')
  ```

**Problem**: Parquet file not readable
- **Solution**: Install pyarrow or fastparquet
  ```bash
  pip install pyarrow
  ```

**Problem**: Memory error loading large CSV
- **Solution**: Load in chunks
  ```python
  chunks = pd.read_csv('file.csv', chunksize=1000)
  for chunk in chunks:
      process(chunk)
  ```

---

**Last Updated**: October 2025  
**Data Version**: 1.0  
**Status**: Production dataset ready for publication

