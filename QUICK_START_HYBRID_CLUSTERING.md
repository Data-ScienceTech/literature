# Quick Start Guide: Using Hybrid Clustering Results

## 📂 Main Files

### Location
```
data/clean/hybrid_streams_full_corpus/
```

### Key Files
1. **`doc_assignments.csv`** - Every paper's stream assignment
2. **`topics_level1.csv`** - 8 major research streams  
3. **`topics_level2.csv`** - 48 detailed subtopics
4. **`citation_network_stats.json`** - Network metrics
5. **`summary.md`** - Quick overview

---

## 🔍 Common Tasks

### Find Papers by Topic

```python
import pandas as pd

# Load assignments
df = pd.read_csv('data/clean/hybrid_streams_full_corpus/doc_assignments.csv')

# Get all papers in Stream 0 (Digital Transformation)
stream0 = df[df['l1_cluster'] == 0]

# Get specific subtopic (e.g., 0.4 = Digital Platforms)
platforms = df[df['l2_cluster'] == '0.4']

# Search by keyword in title
social_media = df[df['title'].str.contains('social media', case=False, na=False)]
```

### Compare Streams

```python
# Count papers per stream
stream_sizes = df.groupby('l1_cluster').size().sort_values(ascending=False)
print(stream_sizes)

# Most recent papers per stream
recent = df.groupby('l1_cluster')['year'].max()
print(recent)
```

### Analyze Citation Patterns

```python
import json

# Load citation stats
with open('data/clean/hybrid_streams_full_corpus/citation_network_stats.json') as f:
    stats = json.load(f)

print(f"Citation coverage: {stats['papers_with_refs']/8110*100:.1f}%")
print(f"Avg coupling: {stats['avg_coupling']:.3f}")
print(f"Total edges: {stats['coupling_edges']:,}")
```

---

## 📊 8 Research Streams

| Stream | Size | % | Focus Area |
|--------|------|---|-----------|
| 0 | 1,554 | 19.2% | Digital Transformation & Innovation |
| 1 | 2,021 | 24.9% | E-commerce, Auctions, Markets |
| 2 | 316 | 3.9% | ERP & Technology Adoption |
| 3 | 958 | 11.8% | IT Governance & Design Science |
| 4 | 1,610 | 19.9% | Social Media & Data Analytics |
| 5 | 1,158 | 14.3% | Decision Support & Privacy |
| 6 | 410 | 5.1% | Enterprise Systems & EDI |
| 7 | 83 | 1.0% | Technology Acceptance Theory |

---

## 🎯 Quality Metrics

- **Silhouette Score**: 0.340 (excellent)
- **Citation Coverage**: 88% (7,133/8,110 papers)
- **Network Edges**: 2,844,515 citation links
- **Improvement vs Text-Only**: 11.7x better separation

---

## 📝 Example Analyses

### 1. Literature Review for "Digital Platforms"

```python
# Find relevant streams and subtopics
platforms = df[df['title'].str.contains('platform', case=False, na=False)]

# See distribution across streams
print(platforms.groupby('l1_cluster').size())

# Look at Stream 0.4 (Digital Platforms subtopic)
subtopic_04 = df[df['l2_cluster'] == '0.4']
print(f"Digital Platforms: {len(subtopic_04)} papers")
print(subtopic_04[['title', 'year', 'journal']].head(10))
```

### 2. Find Seminal Papers in a Stream

```python
# Get earliest papers in each stream (potential foundations)
for stream in range(8):
    stream_papers = df[df['l1_cluster'] == stream]
    earliest = stream_papers.nsmallest(5, 'year')
    print(f"\nStream {stream} - Earliest papers:")
    print(earliest[['title', 'year', 'journal']])
```

### 3. Track Research Evolution

```python
# Papers per stream over time
evolution = df.groupby(['l1_cluster', 'year']).size().reset_index(name='count')

# Plot using matplotlib/seaborn
import matplotlib.pyplot as plt
import seaborn as sns

pivot = evolution.pivot(index='year', columns='l1_cluster', values='count').fillna(0)
pivot.plot(figsize=(12, 6), title='Research Stream Evolution Over Time')
plt.show()
```

### 4. Cross-Stream Analysis

```python
# Which journals publish which streams?
journal_stream = df.groupby(['journal', 'l1_cluster']).size().unstack(fill_value=0)
print(journal_stream)

# Normalize by journal
journal_pct = journal_stream.div(journal_stream.sum(axis=1), axis=0) * 100
print(journal_pct.round(1))
```

---

## 🔗 Integration with Original Data

### Merge with Full Corpus

```python
# Load original enriched corpus
corpus = pd.read_parquet('data/clean/ais_basket_corpus_enriched.parquet')

# Merge with stream assignments
merged = corpus.merge(df, left_on='doi', right_on='doc_id', how='left')

# Now you have abstracts, keywords, citations + stream assignments!
print(merged.columns)
```

### Access Citation Data

```python
# Papers with citations in Stream 1
stream1_cited = merged[
    (merged['l1_cluster'] == 1) & 
    (merged['referenced_works'].notna())
]

# Average references by stream
avg_refs = merged.groupby('l1_cluster')['referenced_works'].apply(
    lambda x: x.dropna().apply(len).mean()
)
print("Avg references per stream:")
print(avg_refs.sort_values(ascending=False))
```

---

## 📈 Visualization Ideas

### 1. Stream Size Pie Chart

```python
import matplotlib.pyplot as plt

sizes = df.groupby('l1_cluster').size()
labels = [f"Stream {i}" for i in sizes.index]

plt.figure(figsize=(10, 8))
plt.pie(sizes, labels=labels, autopct='%1.1f%%')
plt.title('Distribution of Papers Across Research Streams')
plt.show()
```

### 2. Subtopic Heatmap

```python
import seaborn as sns

# Papers per subtopic
subtopic_counts = df.groupby(['l1_cluster', 'l2_cluster']).size().unstack(fill_value=0)

plt.figure(figsize=(12, 8))
sns.heatmap(subtopic_counts, annot=True, fmt='d', cmap='YlOrRd')
plt.title('Papers per L2 Subtopic within L1 Streams')
plt.show()
```

### 3. Timeline by Stream

```python
# Papers published per year, colored by stream
timeline = df.groupby(['year', 'l1_cluster']).size().unstack(fill_value=0)

timeline.plot(kind='area', stacked=True, figsize=(14, 6), alpha=0.7)
plt.title('Research Stream Evolution (Stacked Area)')
plt.xlabel('Year')
plt.ylabel('Number of Papers')
plt.legend(title='Stream', bbox_to_anchor=(1.05, 1))
plt.tight_layout()
plt.show()
```

---

## 🎓 Research Applications

### For Literature Reviews
- **Start**: Identify relevant stream(s) for your topic
- **Explore**: Browse papers within stream and subtopics
- **Expand**: Check citation patterns to find seminal works
- **Synthesize**: Compare across streams for comprehensive coverage

### For Gap Analysis
- **Small streams** (e.g., Stream 7: 83 papers) = underexplored
- **Low coupling** = opportunity for synthesis
- **Cross-stream gaps** = interdisciplinary potential

### For Course Design
- **Stream 0-1-4**: Core IS topics (platforms, e-commerce, social media)
- **Stream 3**: Research methods & design science
- **Stream 2-6**: Enterprise systems & IT management
- **Stream 5**: Decision support & ethics (privacy)

### For Journal Targeting
- Compare journal distribution across streams
- Identify venue preferences for your research area
- Track journal evolution over time

---

## 🚀 Next Steps

### Advanced Analytics
1. **Co-citation analysis** - Find papers cited together
2. **Influence mapping** - Most cited papers per stream
3. **Temporal clustering** - How streams evolved
4. **Predictive modeling** - Emerging vs declining topics

### Visualization Dashboard
- Interactive network graph of citations
- Drill-down from stream → subtopic → papers
- Search and filter capabilities
- Export custom paper lists

### Citation Network Exploration
- Build citation graphs for each stream
- Identify "hub" papers (highly cited)
- Map knowledge flow between streams
- Find cross-disciplinary bridges

---

## 📚 Documentation

- **HYBRID_CLUSTERING_RESULTS.md** - Full analysis & methodology
- **CITATION_ENRICHMENT_COMPLETE.md** - Data collection details
- **hybrid_streams_full_corpus/summary.md** - Quick reference

---

## ⚡ Performance Notes

- **Processing time**: ~2 minutes for full corpus
- **Memory efficient**: 91.3% sparse matrix utilization
- **Scalable**: Handles 2.8M citation edges efficiently
- **Quality**: Professional-grade clustering (silhouette > 0.3)

---

*Last updated: 2025-10-06*  
*Corpus: 8,110 papers from AIS Basket journals*  
*Quality: Silhouette 0.340 (11.7x better than text-only)*
