# 📋 QUICK REFERENCE GUIDE - IS CORPUS ANALYSIS

## 🎯 What We Did

Analyzed **6,556 Information Systems research papers** from 6 premier journals (2000-2025), identifying **28 distinct research streams** using machine learning clustering.

---

## 📊 Key Numbers to Remember

- **6,556** papers analyzed
- **28** research streams identified  
- **907,900** total citations
- **100%** abstract coverage
- **25 years** of research (2000-2025)

---

## 🌟 Top 5 Research Streams (by size)

1. **Social Media & Online Communities** - 549 papers
2. **IT Business Value** - 516 papers  
3. **IS Theory & Methodology** - 508 papers
4. **Technology Acceptance (TAM/UTAUT)** - 434 papers (HIGHEST IMPACT: 406 avg cites)
5. **E-Commerce & Trust** - 393 papers

---

## 🔥 Top 5 Emerging Topics (2020-2025)

1. **AI & Machine Learning** - 79% recent papers
2. **Blockchain & Fintech** - 66% recent
3. **Crowdfunding** - 65% recent
4. **Digital Platforms** - 61% recent
5. **Online Reviews** - 47% recent

---

## 📚 Most Cited Papers (Top 5)

1. **37,372 cites** - "User Acceptance of Information Technology: Toward a Unified View" (UTAUT, 2003)
2. **12,327 cites** - "Consumer Acceptance and Use of Information Technology" (2012)
3. **10,732 cites** - "The DeLone and McLean Model of Information Systems Success" (2003)
4. **9,833 cites** - "Knowledge Management and Knowledge Management Systems" (2001)
5. **7,923 cites** - "Design science in information systems research" (2004)

---

## 📁 Key Files to Check

### For Analysis:
- `EXECUTIVE_SUMMARY.md` - Full results overview
- `ANALYSIS_RESULTS.md` - Comprehensive detailed analysis
- `data/papers_clustered_is_corpus.csv` - Full dataset with clusters
- `data/research_stream_topics.csv` - Stream characteristics

### For Visualizations:
- `data/clustering_visualization.png` - Overview charts
- `data/clustering_details.png` - Detailed analysis

### For Raw Data:
- `data/clean/is_corpus_recommended.parquet` - Clean corpus (6,556 papers)
- `data/embeddings_is_corpus.npy` - Semantic embeddings

---

## 🎯 How to Explore Specific Topics

### Find papers in a specific stream:
```python
import pandas as pd
df = pd.read_csv('data/papers_clustered_is_corpus.csv')

# Example: Get all papers in Stream 4 (Technology Acceptance)
stream_4 = df[df['cluster'] == 4]
print(stream_4[['Title', 'Year', 'Citations']].head(10))
```

### Find recent papers on a topic:
```python
# Example: AI/ML papers from 2020+
stream_14 = df[(df['cluster'] == 14) & (df['Year'] >= 2020)]
print(f"Found {len(stream_14)} recent AI/ML papers")
```

### Find most cited papers in each stream:
```python
for stream_id in range(28):
    stream_papers = df[df['cluster'] == stream_id]
    top_paper = stream_papers.nlargest(1, 'Citations').iloc[0]
    print(f"Stream {stream_id}: {top_paper['Title'][:50]}... ({top_paper['Citations']} cites)")
```

---

## 🔍 Research Stream Cheat Sheet

| Stream # | Topic | Size | Recent % | Avg Cites |
|----------|-------|------|----------|-----------|
| 0 | Social Media & Communities | 549 | 44% | 85 |
| 1 | IT Business Value | 516 | 16% | 144 |
| 2 | IS Theory | 508 | 21% | 108 |
| 3 | Online Markets | 507 | 34% | 49 |
| 4 | **Technology Acceptance** | 434 | 21% | **406** ⭐ |
| 5 | E-Commerce Trust | 393 | 26% | 204 |
| 6 | Digital Platforms | 322 | **61%** 🔥 | 143 |
| 7 | Virtual Teams | 310 | 14% | 126 |
| 8 | Design Science | 303 | 17% | 170 |
| 9 | Information Security | 268 | 37% | 104 |
| 10 | **Crowdfunding** | 211 | **65%** 🔥 | 56 |
| 13 | Business Analytics | 202 | 36% | 186 |
| 14 | **AI & Machine Learning** | 188 | **79%** 🔥🔥 | 52 |
| 15 | Knowledge Management | 164 | 20% | **304** ⭐ |

*⭐ = High Impact | 🔥 = Emerging Topic*

---

## 💡 Quick Insights

### What's Hot Right Now?
- **AI/Machine Learning** (Stream 14) - Nearly 80% of papers from 2020+
- **Blockchain/Fintech** (Stream 26) - 66% recent
- **Digital Platforms** (Stream 6) - 61% recent, high citations

### What's Most Impactful?
- **Technology Acceptance** (Stream 4) - 406 avg citations per paper!
- **Knowledge Management** (Stream 15) - 304 avg citations
- **E-Commerce Trust** (Stream 5) - 204 avg citations

### What's Established & Stable?
- **IT Business Value** (Stream 1) - Large, steady stream
- **IS Theory** (Stream 2) - Foundational research
- **Social Media** (Stream 0) - Biggest stream, consistent growth

---

## 🚀 Next Steps

1. ✅ **Review visualizations** - Check the PNG files in data/
2. ✅ **Explore specific streams** - Use the CSV files
3. ✅ **Read full analysis** - Check ANALYSIS_RESULTS.md
4. 📊 **Build dashboard** - Create interactive visualization
5. 🔗 **Citation networks** - Map connections between streams
6. 👥 **Author analysis** - Identify key researchers

---

## 📞 Technical Details

**Embedding Model:** all-MiniLM-L6-v2 (384 dimensions)  
**Clustering:** Leiden algorithm (resolution=1.5)  
**Quality Metrics:** Modularity=0.669, Silhouette=0.053  
**Data Source:** OpenAlex API  
**Journals:** ISR, MISQ, JAIS, ISJ, JMIS, JIT  

---

## ⚡ One-Line Summary

**"28 research streams identified from 6,556 high-quality IS papers (2000-2025), with Technology Acceptance, AI/ML, and Digital Platforms showing highest impact and growth."**

---

*Last updated: October 3, 2025*
