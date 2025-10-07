# Appendix D — Interactive Literature Explorer Guide

This appendix provides guidance for using the web-based Interactive Literature Explorer, which offers dynamic visualization and exploration of the research streams identified in our analysis.

## Overview

**URL**: https://data-sciencetech.github.io/literature/  
**Technology**: Client-side web application (HTML/CSS/JavaScript)  
**Data**: Complete corpus of 8,110 papers with cluster assignments  
**No installation required**: Works in any modern web browser

The Interactive Explorer complements the static analysis presented in the manuscript by enabling:

1. **Dynamic filtering** by year, journal, and research stream
2. **Full-text search** across titles, abstracts, and keywords
3. **Citation network visualization** with interactive graph exploration
4. **Temporal trend analysis** with customizable time windows
5. **Export functionality** for creating custom datasets

---

## Getting Started

### Accessing the Explorer

1. Navigate to **https://data-sciencetech.github.io/literature/** in your web browser
2. The homepage displays the **Stream Overview** with 8 major research streams
3. Each stream shows:
   - Stream name and description
   - Paper count and percentage of corpus
   - Top 10 distinctive keywords
   - Temporal distribution (sparkline chart)
   - Representative papers (top 3 by citation count)

### System Requirements

- **Browser**: Chrome 90+, Firefox 88+, Safari 14+, or Edge 90+
- **Internet**: Broadband connection recommended (initial load: ~2.5 MB)
- **Screen**: Minimum 1024×768 resolution (1920×1080 recommended)
- **JavaScript**: Must be enabled

---

## Navigation Guide

### 1. Homepage — Stream Overview

The landing page presents a high-level overview of all 8 research streams. Click any stream card to drill down into Level 2 subtopics. Use the dropdown menu to sort streams by paper count, average publication year, or alphabetical order.

**Example Use Case**: "I want to see which research streams are most active"
→ Sort by paper count to see "User Adoption & Behavior" (1,847 papers, 22.8%) is the largest stream.

### 2. Stream Detail View — Level 2 Subtopics

Clicking a stream card navigates to the Stream Detail page showing 4–8 Level 2 subtopics. Each subtopic card displays the subtopic name, paper count, top keywords, temporal trend indicator, and average publication year.

**Interactive Features**:
- **Temporal filter**: Slider to show only papers from selected year range
- **Journal filter**: Checkboxes to include/exclude specific journals
- **Citation threshold**: Slider to show only highly-cited papers

**Example Use Case**: "I want to find recent papers on Technology Acceptance"
→ Navigate to "User Adoption & Behavior" stream → Click "Technology Acceptance Model (TAM)" subtopic → Set temporal filter to 2020–2024 → Shows 47 recent TAM papers.

### 3. Subtopic Detail View — Paper List

Clicking a subtopic card shows the complete list of papers in that cluster with columns for Title, Authors, Year, Journal, Citations, and Keywords.

**Sorting & Filtering**:
- **Sort by**: Title (A-Z), Year (newest/oldest), Citations (most/least)
- **Search bar**: Full-text search across title, authors, abstract, keywords
- **Advanced filters**: Publication year range, citation count range, specific journals, author name

**Export Options**:
- **CSV**: Download filtered paper list with all metadata
- **BibTeX**: Export citations for reference management software
- **JSON**: Download raw data for custom analysis

**Example Use Case**: "I want to export all blockchain papers published in MISQ after 2018"
→ Navigate to "Emerging Technologies" stream → "Blockchain & Distributed Ledger" subtopic → Filter: Year ≥ 2019, Journal = MISQ → Export as BibTeX → Import to Zotero.

### 4. Citation Network Visualization

Accessible from any subtopic view via the "View Citation Network" button. The visualization shows papers as nodes (sized by citation count, colored by L2 cluster) and bibliographic coupling links as edges.

**Interactive Controls**:
- **Edge threshold**: Slider to show only strong connections
- **Node filter**: Hide papers with fewer than N citations
- **Cluster highlighting**: Click legend to highlight/isolate specific L2 clusters
- **Shortest path**: Click two nodes to highlight citation path between them

**Example Use Case**: "I want to see how TAM papers connect to trust research"
→ View citation network for "User Adoption & Behavior" stream → Click "Technology Acceptance Model" node → Click "Trust in E-Commerce" node → Shortest path highlighted.

### 5. Temporal Evolution Dashboard

Accessible via the "Trends" tab in main navigation:

**Components**:
1. **Stream Timeline**: Line chart showing paper count per stream over time (1990–2024)
2. **Cumulative Growth**: Area chart showing total papers over time
3. **Journal Distribution**: Stacked bar chart showing contribution by journal per year
4. **Emerging Topics**: Bubble chart showing L2 subtopics by average year and growth rate

**Example Use Case**: "When did blockchain research emerge in IS?"
→ Trends tab → Emerging Topics chart → Locate "Blockchain & Distributed Ledger" bubble → Avg year: 2019.3, growth rate: 12 papers/year.

---

## Advanced Features

### Keyword Co-occurrence Network
Shows relationships between research concepts with nodes (keywords sized by frequency) and edges (co-occurrence weighted by PMI). Use this to discover concept associations.

**Use Case**: "What concepts are associated with 'artificial intelligence'?"
→ Keyword Network → Search "artificial intelligence" → Highlights connected nodes: "machine learning", "decision making", "automation", "trust".

### Author Collaboration Network
Shows co-authorship patterns with nodes (authors sized by paper count) and edges (co-authorship relationships).

**Use Case**: "Who are the most prolific TAM researchers?"
→ Filter to "TAM" subtopic → Author Network → Largest nodes: Venkatesh (32 papers), Davis (18 papers), Gefen (15 papers).

### Cross-Stream Analysis
Compare multiple streams simultaneously using Venn diagrams, side-by-side keyword clouds, and Sankey diagrams showing inter-stream citations.

**Use Case**: "How much overlap exists between 'AI/ML' and 'Decision Support'?"
→ Cross-Stream tab → Select both streams → Venn diagram shows overlap.

---

## Tips for Effective Exploration

### For Literature Review Authors
1. Start broad with Stream Overview to understand the landscape
2. Narrow down using temporal and journal filters
3. Export BibTeX for each subtopic of interest
4. Use Temporal Evolution to identify emerging vs. declining topics

### For Researchers Situating Their Work
1. Search for your keywords to find matching stream/subtopic
2. Use keyword co-occurrence to find under-researched concept combinations
3. Sort by citations to find seminal works in your subtopic
4. Filter to last 3 years to build on recent work

---

## Data Freshness & Updates

**Current version**: Based on data collected October 2024  
**Coverage**: 8,110 papers from AIS Basket journals (1990–2024)  
**Citation data**: From OpenAlex API (88.0% coverage, 545,865 citations)  
**Update schedule**: Annual refresh every October

**Feedback**: Report issues or suggest features at https://github.com/Data-ScienceTech/literature/issues

---

## Technical Notes

**Performance**: ~2.5 MB initial load, instant subsequent pages (client-side rendering)  
**Browser Compatibility**: Tested on Chrome 120+, Firefox 115+, Safari 17+, Edge 120+  
**Data Privacy**: No tracking, no cookies, no data collection — all computation client-side

---

## Citing the Explorer

If you use the Interactive Explorer in your research, please cite:

```
Santos, C. D. (2025). Interactive Literature Explorer for Information Systems
Research: A Web-based Tool for Exploring the AIS Basket of Eight.
Available at: https://data-sciencetech.github.io/literature/
```

---

## Support & Contact

**Questions**: carlosdenner@unb.br  
**GitHub Issues**: https://github.com/Data-ScienceTech/literature/issues  
**Code Repository**: https://github.com/Data-ScienceTech/literature
