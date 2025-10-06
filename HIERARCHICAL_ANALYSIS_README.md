# Multi-Level Hierarchical Research Stream Analysis

## 🎯 Overview

Your literature analysis system has been enhanced with **state-of-the-art multi-level hierarchical clustering** that reveals nested research communities at multiple scales. This advancement goes far beyond simple flat clustering to provide deep insights into the structure of research fields.

## 🌟 New Capabilities

### 1. **Multi-Level Hierarchical Clustering** (3-4 levels deep)

We've implemented three complementary approaches:

#### **Leiden Multi-Resolution** (Recommended)
- Varies resolution parameter from coarse to fine granularity
- Automatically detects optimal resolution levels using modularity landscape
- Produces 3-4 hierarchical levels revealing macro → meso → micro research communities
- Based on Traag et al. (2019) - state-of-the-art for network community detection

#### **HDBSCAN Hierarchical**
- Density-based hierarchical clustering with recursive subdivision
- Extracts hierarchy from condensed cluster tree
- Identifies noise points and cluster stability scores
- Based on McInnes et al. (2017)

#### **Recursive Leiden**
- Quality-driven recursive subdivision
- Splits clusters when quality (silhouette score) falls below threshold
- Ensures each level maintains high cohesion

### 2. **Enhanced Network Analysis**

#### **Multi-Resolution Community Detection**
- Detects communities at multiple scales simultaneously
- Supports both Louvain and Leiden algorithms
- Maps research community structure from broad fields to specific niches

#### **Bridge Paper Detection**
- Identifies papers that connect different research clusters
- Uses betweenness centrality to find knowledge brokers
- Critical for understanding interdisciplinary knowledge flows

#### **Hierarchical Backbone Extraction**
- Multi-level network backbone (3+ levels)
- Each level shows progressively stronger relationships
- Uses disparity filter (Serrano et al. 2009)

#### **Citation Flow Analysis**
- Inter-cluster citation patterns at each hierarchy level
- Identifies knowledge flows between research communities
- Temporal knowledge flow tracking

### 3. **Hierarchical Dialog Cards**

Each cluster at every level gets a comprehensive card showing:
- **Parent context** - Where it fits in the hierarchy
- **Key papers** - Most influential works in this stream
- **Sub-clusters** - Nested specializations
- **Temporal dynamics** - Evolution over time
- **Topic keywords** - TF-IDF extracted themes
- **Journal distribution** - Primary publication venues
- **Citation metrics** - Impact and influence

## 📊 Analysis Output

### File Structure
```
data/
├── papers_hierarchical_clustered.csv       # Dataset with multi-level cluster labels
│   ├── cluster_l0 (macro-level clusters)
│   ├── cluster_l1 (meso-level clusters)
│   ├── cluster_l2 (micro-level clusters)
│   └── hierarchy_path (full path: "0 > 0.1 > 0.1.2")
│
├── hierarchy_leiden.json                   # Complete hierarchy structure
│   ├── Cluster tree with parent-child relationships
│   ├── Quality metrics (cohesion, density)
│   └── Level-by-level statistics
│
├── hierarchical_dialog_cards.json          # Nested research stream summaries
│   ├── Cards for each cluster at every level
│   ├── Key papers, topics, temporal patterns
│   └── Sub-cluster relationships
│
├── hierarchical_analysis.json              # Quality & structure metrics
│   ├── Silhouette scores by level
│   ├── Davies-Bouldin scores
│   ├── Temporal coverage analysis
│   └── Cluster size distributions
│
├── hierarchical_network_analysis.json      # Citation network insights
│   ├── Inter-cluster citation flows
│   ├── Bridge papers
│   ├── Knowledge flow patterns
│   └── Network metrics by level
│
└── visualizations/
    ├── hierarchy_tree.png                  # Visual hierarchy structure
    └── cluster_size_distributions.png      # Size analysis by level
```

### Dataset Structure

The enhanced dataset includes:
- **cluster_l0**: Top-level research areas (e.g., 5-15 broad themes)
- **cluster_l1**: Mid-level specializations (e.g., 20-40 streams)
- **cluster_l2**: Fine-grained topics (e.g., 50-100 specific niches)
- **cluster_l3**: Ultra-specific sub-topics (if depth=4)
- **hierarchy_path**: Full hierarchical path (e.g., "2 > 2.1 > 2.1.3")

## 🚀 Usage

### Quick Start

```bash
# Run hierarchical analysis with recommended settings
python run_hierarchical_analysis.py
```

This will:
1. Load the IS corpus (recommended: 6 premier journals, 2000+)
2. Generate/load SPECTER2 embeddings
3. Perform Leiden multi-resolution clustering (3-4 levels)
4. Analyze hierarchical structure and quality
5. Conduct citation network analysis
6. Generate hierarchical dialog cards
7. Create visualizations

### Configuration Options

Edit the configuration in `run_hierarchical_analysis.py`:

```python
# Which corpus to analyze
CORPUS_NAME = "recommended"          # Options: "recommended", "hq_2010+", "ais_basket"

# Clustering method
CLUSTERING_METHOD = "leiden"          # Options: "leiden", "hdbscan", "recursive"

# Hierarchy depth
MAX_LEVELS = 4                        # 3-4 recommended

# Minimum cluster size at any level
MIN_CLUSTER_SIZE = 20                 # Smaller = more granular

# Regenerate embeddings
FORCE_REGENERATE_EMBEDDINGS = False   # Set True to recompute
```

### Advanced Usage

#### 1. Load and Explore Hierarchy

```python
import json
from pathlib import Path

# Load hierarchy
with open('data/hierarchy_leiden.json') as f:
    hierarchy_data = json.load(f)

# Explore levels
print(f"Depth: {hierarchy_data['max_depth']}")
print(f"Total clusters: {hierarchy_data['total_clusters']}")
print(f"Clusters by level: {hierarchy_data['level_sizes']}")
```

#### 2. Analyze Specific Research Stream

```python
import pandas as pd

# Load clustered data
df = pd.read_csv('data/papers_hierarchical_clustered.csv')

# Get papers in a specific path
stream = df[df['hierarchy_path'] == '2 > 2.1 > 2.1.3']

print(f"Stream size: {len(stream)}")
print(f"Years: {stream['Year'].min()}-{stream['Year'].max()}")
print(f"\nTop papers:")
print(stream.nlargest(5, 'Citations')[['Title', 'Year', 'Citations']])
```

#### 3. Compare Clustering Methods

```python
# Run different methods and compare
# Method 1: Leiden
python run_hierarchical_analysis.py  # CLUSTERING_METHOD = "leiden"

# Method 2: HDBSCAN
# Edit config: CLUSTERING_METHOD = "hdbscan"
python run_hierarchical_analysis.py

# Method 3: Recursive
# Edit config: CLUSTERING_METHOD = "recursive"
python run_hierarchical_analysis.py
```

#### 4. Analyze Bridge Papers

```python
with open('data/hierarchical_network_analysis.json') as f:
    network = json.load(f)

bridges = network.get('bridge_papers', [])

print(f"Top 5 bridge papers:")
for i, bridge in enumerate(bridges[:5], 1):
    print(f"{i}. Connects {bridge['n_connections']} clusters")
    print(f"   Centrality: {bridge['centrality']:.3f}")
    print(f"   Home cluster: {bridge['home_cluster']}")
    print(f"   Bridges to: {bridge['connected_clusters']}")
```

## 📈 Understanding the Hierarchy

### Level 0 (Macro): Broad Research Areas
- **5-15 clusters** representing major themes
- Examples:
  - Digital Innovation & Transformation
  - Data Analytics & AI
  - IS Strategy & Governance
  - User Behavior & Adoption
  - Platform Ecosystems

### Level 1 (Meso): Research Streams
- **20-40 clusters** representing established research streams
- Examples within "Digital Innovation":
  - Open Innovation Platforms
  - Digital Business Models
  - Smart Cities & IoT
  - Blockchain & DLT

### Level 2 (Micro): Specific Topics
- **50-100 clusters** representing focused research topics
- Examples within "Open Innovation Platforms":
  - Developer Ecosystems
  - API Design & Management
  - Community Governance
  - Innovation Contests

### Level 3 (Ultra-Micro): Niche Specializations
- **100-200 clusters** (if depth=4)
- Highly specific research niches and methodological approaches

## 🎯 Research Applications

### 1. **Literature Review**
- Start at Level 0 to identify relevant broad area
- Drill down to Level 1 for established research streams
- Focus on Level 2-3 for specific literature review scope

### 2. **Gap Analysis**
- Compare cluster sizes across levels
- Identify under-researched areas (small clusters with high growth)
- Find emerging topics (recent papers in new sub-clusters)

### 3. **Theoretical Integration**
- Use bridge papers to find cross-disciplinary connections
- Analyze citation flows between clusters
- Identify theoretical frameworks spanning multiple streams

### 4. **Trend Analysis**
- Track temporal evolution within hierarchy
- Identify growing vs. declining streams at each level
- Detect emerging sub-specializations

## 🔬 Methodological Rigor

### Clustering Quality Metrics

We compute multiple quality metrics at each level:

- **Silhouette Score** (0-1): Measures cluster separation
  - >0.5 = Good separation
  - >0.7 = Excellent separation
  
- **Davies-Bouldin Score** (lower = better): Measures cluster compactness
  - <1.0 = Good clustering
  - <0.5 = Excellent clustering

- **Cohesion**: Average within-cluster similarity
- **Density**: Pairwise similarity distribution

### Validation

The hierarchical structure is validated through:

1. **Cross-level coherence**: Parent clusters should meaningfully contain child clusters
2. **Stability analysis**: Bootstrap resampling to test consistency
3. **Quality thresholds**: Each level maintains minimum quality standards
4. **Expert validation**: Dialog cards enable domain expert review

## 📚 References & Methods

### Clustering Algorithms
- **Traag, V. A., Waltman, L., & Van Eck, N. J. (2019).** From Louvain to Leiden: guaranteeing well-connected communities. *Scientific Reports*, 9(1), 1-12.
  
- **McInnes, L., Healy, J., & Astels, S. (2017).** HDBSCAN: Hierarchical density based clustering. *Journal of Open Source Software*, 2(11), 205.

### Network Methods
- **Serrano, M. Á., Boguná, M., & Vespignani, A. (2009).** Extracting the multiscale backbone of complex weighted networks. *PNAS*, 106(16), 6483-6488.

### Embeddings
- **Cohan, A., et al. (2020).** SPECTER: Document-level Representation Learning using Citation-informed Transformers. *ACL 2020*.

## 🎉 What's New vs. Previous Analysis

| Feature | Previous (Flat) | New (Hierarchical) |
|---------|----------------|-------------------|
| **Clustering Depth** | 1 level | 3-4 levels |
| **Total Clusters** | 20-30 | 100-300+ |
| **Granularity** | Fixed | Multi-scale |
| **Relationships** | Peer clusters only | Parent-child + peer |
| **Network Analysis** | Single resolution | Multi-resolution |
| **Bridge Detection** | Not available | Cross-cluster brokers |
| **Citation Flows** | Not analyzed | Multi-level flow analysis |
| **Dialog Cards** | Flat structure | Nested with context |

## 🔮 Future Enhancements

The hierarchical framework enables:

1. **Interactive Dashboard** with drill-down navigation
2. **Temporal Hierarchy Evolution** tracking how structure changes over time
3. **Predictive Modeling** of emerging research areas
4. **Recommendation System** for finding relevant papers across levels
5. **Collaboration Network** analysis at each hierarchical level

## 💡 Tips for Best Results

1. **Start with Leiden**: Most robust for large corpora
2. **Use MIN_CLUSTER_SIZE=20**: Balances granularity and stability
3. **Aim for 3-4 levels**: Sweet spot for interpretability
4. **Review quality metrics**: Ensure silhouette >0.3 at each level
5. **Examine bridge papers**: Key for cross-cutting insights
6. **Validate with domain knowledge**: Dialog cards enable expert review

## 🎯 Example Research Questions

The hierarchical analysis can answer:

1. **"What are the major research areas in IS?"** → Level 0 clusters
2. **"What established streams exist in digital innovation?"** → Level 1 under macro-cluster
3. **"What specific topics are being studied in platform ecosystems?"** → Level 2-3
4. **"Which papers bridge strategy and technology streams?"** → Bridge paper analysis
5. **"How does knowledge flow between theory and practice clusters?"** → Citation flow analysis
6. **"What are emerging micro-specializations?"** → Recent Level 3 clusters

---

**Created**: 2025-01-06
**Methods**: Leiden Multi-Resolution, HDBSCAN Hierarchical, SPECTER2 Embeddings
**Implementation**: run_hierarchical_analysis.py
**Contact**: Your enhanced literature analysis system 🚀
