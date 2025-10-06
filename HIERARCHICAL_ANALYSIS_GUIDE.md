# 🚀 Enhanced Multi-Level Hierarchical Analysis - Complete Guide

## 📋 Executive Summary

Your literature analysis system has been **completely upgraded** with state-of-the-art multi-level hierarchical clustering and advanced network analysis capabilities. This transforms your analysis from flat, single-level clustering to a sophisticated **3-4 level hierarchical system** that reveals research communities at multiple scales.

## 🎯 What's Been Built

### 1. **Core Hierarchical Clustering Module** (`src/hierarchical_clustering.py`)

Three complementary clustering approaches:

#### **A. Leiden Multi-Resolution** ⭐ RECOMMENDED
- **Method**: Varies resolution parameter from coarse (0.3) to fine (3.0)
- **Innovation**: Auto-detects optimal resolution levels using modularity landscape
- **Output**: 3-4 hierarchical levels with parent-child relationships
- **Based on**: Traag et al. (2019) - Nature Scientific Reports
- **Best for**: Large corpora (1000+ papers), robust results

#### **B. HDBSCAN Hierarchical**
- **Method**: Density-based clustering with recursive subdivision
- **Innovation**: Extracts hierarchy from condensed cluster tree
- **Output**: Variable-depth hierarchy based on density structure
- **Based on**: McInnes et al. (2017) - JOSS
- **Best for**: Datasets with varying density, noise handling

#### **C. Recursive Leiden**
- **Method**: Quality-driven recursive subdivision
- **Innovation**: Splits clusters when silhouette score < threshold
- **Output**: Balanced hierarchy with guaranteed quality
- **Based on**: Combined Leiden + quality metrics
- **Best for**: Ensuring high cohesion at every level

### 2. **Enhanced Network Analysis Module** (`src/networks.py`)

New functions added:

#### **Multi-Resolution Community Detection**
```python
multi_resolution_community_detection(G, resolutions=[0.5, 1.0, 1.5, 2.0])
```
- Detects communities at multiple scales
- Supports Louvain and Leiden
- Returns communities at each resolution

#### **Bridge Paper Detection**
```python
detect_bridge_papers(G, cluster_attr='cluster', centrality_threshold=0.7)
```
- Identifies papers connecting different clusters
- Uses betweenness centrality
- Returns ranked list of knowledge brokers

#### **Hierarchical Backbone Extraction**
```python
extract_hierarchical_backbone(G, levels=3, method='disparity')
```
- Multi-level network backbone
- Progressive edge filtering
- Based on Serrano et al. (2009) disparity filter

#### **Citation Flow Analysis**
```python
analyze_citation_flows_between_clusters(G, cluster_attr='cluster')
```
- Inter-cluster citation matrix
- Internal vs. external citation ratios
- Knowledge flow patterns

#### **Temporal Knowledge Flows**
```python
find_knowledge_flows(G, time_attr='year', time_window=3)
```
- Time-windowed citation flows
- Cluster-to-cluster knowledge transfer
- Citation age analysis

### 3. **Comprehensive Analysis Pipeline** (`run_hierarchical_analysis.py`)

Complete end-to-end workflow:

1. **Data Loading** - Multi-corpus support (recommended, hq_2010+, ais_basket)
2. **Embeddings** - SPECTER2 scientific embeddings (with fallback)
3. **Hierarchical Clustering** - 3-4 levels deep
4. **Structure Analysis** - Quality metrics at each level
5. **Network Analysis** - Citation graphs and flows
6. **Dialog Card Generation** - Nested research stream summaries
7. **Visualization** - Hierarchy tree and distributions

### 4. **Interactive Dashboard** (`hierarchical_dashboard.html`)

Beautiful web interface with:
- Hierarchical tree navigation
- Cluster detail views
- Level-by-level filtering
- Search and sorting
- Responsive design

## 📊 Output Files & Structure

### Generated Files

```
data/
├── papers_hierarchical_clustered.csv          # Main dataset with multi-level labels
├── hierarchy_leiden.json                       # Complete hierarchy structure
├── hierarchical_dialog_cards.json              # Research stream summaries
├── hierarchical_analysis.json                  # Quality & structure metrics
├── hierarchical_network_analysis.json          # Citation network insights
├── embeddings_hierarchical.npy                 # SPECTER2 embeddings
└── visualizations/
    ├── hierarchy_tree.png                      # Visual tree structure
    └── cluster_size_distributions.png          # Size analysis
```

### Dataset Columns

The enhanced `papers_hierarchical_clustered.csv` includes:

| Column | Description | Example |
|--------|-------------|---------|
| `cluster_l0` | Level 0 cluster (macro) | `"2"` |
| `cluster_l1` | Level 1 cluster (meso) | `"2.1"` |
| `cluster_l2` | Level 2 cluster (micro) | `"2.1.3"` |
| `cluster_l3` | Level 3 cluster (ultra-micro) | `"2.1.3.0"` |
| `hierarchy_path` | Full path | `"2 > 2.1 > 2.1.3"` |
| All original columns | Title, Year, Citations, etc. | Preserved |

## 🚀 Quick Start

### Run Complete Analysis

```bash
# 1. Run hierarchical analysis (takes 10-20 minutes)
python run_hierarchical_analysis.py

# 2. Open dashboard
# Open hierarchical_dashboard.html in your browser

# 3. Explore results
# Review data/hierarchical_dialog_cards.json
```

### Configuration

Edit `run_hierarchical_analysis.py`:

```python
# Which corpus
CORPUS_NAME = "recommended"          # "recommended", "hq_2010+", "ais_basket"

# Clustering method  
CLUSTERING_METHOD = "leiden"          # "leiden", "hdbscan", "recursive"

# Hierarchy depth
MAX_LEVELS = 4                        # 3-4 recommended

# Minimum cluster size
MIN_CLUSTER_SIZE = 20                 # Adjust for granularity

# Force re-embedding
FORCE_REGENERATE_EMBEDDINGS = False   # Set True to recompute
```

## 📈 Understanding the Hierarchy

### Typical Structure for IS Research

```
Level 0 (5-12 clusters): MACRO AREAS
├── Digital Innovation & Transformation
├── Data Analytics & AI
├── IS Strategy & Governance
├── User Behavior & Adoption
└── Platform Ecosystems

Level 1 (20-40 clusters): RESEARCH STREAMS
├── Digital Innovation
│   ├── Open Innovation Platforms
│   ├── Digital Business Models
│   ├── Smart Cities & IoT
│   └── Blockchain & DLT

Level 2 (50-100 clusters): SPECIFIC TOPICS
├── Open Innovation Platforms
│   ├── Developer Ecosystems
│   ├── API Design & Management
│   ├── Community Governance
│   └── Innovation Contests

Level 3 (100-200 clusters): NICHE SPECIALIZATIONS
└── Developer Ecosystems
    ├── GitHub collaboration patterns
    ├── Open source sustainability
    └── Platform API evolution
```

### Quality Metrics

At each level, we compute:

- **Silhouette Score** (0-1): Cluster separation
  - \>0.5 = Good
  - \>0.7 = Excellent
  
- **Davies-Bouldin Score** (lower better): Cluster compactness
  - <1.0 = Good
  - <0.5 = Excellent

- **Cohesion**: Within-cluster similarity (cosine)
- **Density**: Pairwise similarity distribution

## 🔬 Research Applications

### 1. Literature Review Strategy

```python
import pandas as pd
import json

# Load data
df = pd.read_csv('data/papers_hierarchical_clustered.csv')
with open('data/hierarchical_dialog_cards.json') as f:
    cards = json.load(f)

# Step 1: Identify broad area (Level 0)
level0_clusters = df['cluster_l0'].value_counts()
print("Macro research areas:")
for cluster, count in level0_clusters.items():
    card = cards.get(str(cluster), {})
    print(f"  {cluster}: {count} papers - {card.get('top_terms', [])[:3]}")

# Step 2: Drill down to research stream (Level 1)
chosen_macro = "2"  # Digital Innovation
streams = df[df['cluster_l0'] == chosen_macro]['cluster_l1'].value_counts()

# Step 3: Focus on specific topic (Level 2)
chosen_stream = "2.1"  # Open Innovation Platforms  
topics = df[df['cluster_l1'] == chosen_stream]['cluster_l2'].value_counts()

# Step 4: Get papers
my_papers = df[df['cluster_l2'] == "2.1.3"]
print(f"\nFocused literature: {len(my_papers)} papers")
print(my_papers.nlargest(10, 'Citations')[['Title', 'Year', 'Citations']])
```

### 2. Gap Analysis

```python
# Find under-researched areas
for cluster_id, card in cards.items():
    if card['level'] == 2:  # Level 2 topics
        size = card['size']
        recent = sum(1 for p in card.get('papers', []) if p.get('year', 0) >= 2020)
        
        # Small but growing = potential gap
        if size < 30 and recent > size * 0.5:
            print(f"Emerging niche: {cluster_id}")
            print(f"  Size: {size}, Recent: {recent}")
            print(f"  Topics: {card.get('top_terms', [])[:5]}")
```

### 3. Bridge Paper Analysis

```python
with open('data/hierarchical_network_analysis.json') as f:
    network = json.load(f)

bridges = network.get('bridge_papers', [])

print("Top knowledge brokers:")
for bridge in bridges[:10]:
    paper_id = bridge['paper_id']
    paper = df[df['id'] == paper_id].iloc[0]
    
    print(f"\nTitle: {paper['Title'][:80]}...")
    print(f"Connects: {bridge['n_connections']} clusters")
    print(f"Centrality: {bridge['centrality']:.3f}")
    print(f"Bridges: {', '.join(bridge['connected_clusters'])}")
```

### 4. Temporal Evolution

```python
# Track how clusters evolve over time
import matplotlib.pyplot as plt

for cluster_id in ['0', '1', '2', '3']:  # Level 0 clusters
    cluster_papers = df[df['cluster_l0'] == cluster_id]
    yearly = cluster_papers.groupby('Year').size()
    
    plt.plot(yearly.index, yearly.values, label=f'Cluster {cluster_id}')

plt.xlabel('Year')
plt.ylabel('Papers')
plt.title('Research Stream Evolution')
plt.legend()
plt.savefig('data/visualizations/temporal_evolution.png')
```

## 🎯 Advanced Usage

### Compare Multiple Methods

```bash
# Run all three methods
python run_hierarchical_analysis.py  # leiden (default)

# Edit config: CLUSTERING_METHOD = "hdbscan"
python run_hierarchical_analysis.py

# Edit config: CLUSTERING_METHOD = "recursive"
python run_hierarchical_analysis.py

# Compare results
```

### Custom Analysis

```python
from src.hierarchical_clustering import LeidenMultiResolution
from src.embeddings import ScientificEmbedder
import pandas as pd
import numpy as np

# Load your data
df = pd.read_parquet('data/clean/is_corpus_recommended.parquet')

# Generate embeddings
embedder = ScientificEmbedder(model_name="allenai/specter2")
texts = (df['title'] + '. ' + df['abstract']).tolist()
embeddings = embedder.embed_texts(texts, batch_size=32)

# Custom hierarchical clustering
clusterer = LeidenMultiResolution(
    embeddings=embeddings,
    k=20,  # More neighbors = tighter clusters
    metric='cosine'
)

# Build hierarchy with custom resolutions
hierarchy = clusterer.build_hierarchy(
    resolutions=[0.4, 0.8, 1.5, 2.5],  # Custom levels
    min_cluster_size=15,
    max_levels=4
)

# Analyze
print(f"Root clusters: {len(hierarchy.root_nodes)}")
for level in range(hierarchy.max_depth() + 1):
    clusters = hierarchy.get_level_clusters(level)
    sizes = [c.size for c in clusters]
    print(f"Level {level}: {len(clusters)} clusters (avg size: {np.mean(sizes):.0f})")
```

## 🔧 Troubleshooting

### Issue: "ImportError: leidenalg not available"

```bash
# Install required packages
pip install leidenalg python-igraph

# Or use conda
conda install -c conda-forge leidenalg python-igraph
```

### Issue: "Out of memory during embedding"

```python
# In run_hierarchical_analysis.py, reduce batch size
embeddings = embedder.embed_texts(
    texts,
    batch_size=16,  # Reduce from 32
    show_progress=True
)
```

### Issue: "Too many small clusters"

```python
# Increase minimum cluster size
hierarchy = clusterer.build_hierarchy(
    min_cluster_size=30,  # Increase from 20
    max_levels=3  # Or reduce levels
)
```

### Issue: "Clustering takes too long"

```python
# Use smaller corpus or HDBSCAN
CORPUS_NAME = "hq_2010+"  # Smaller than "recommended"
CLUSTERING_METHOD = "hdbscan"  # Faster than leiden
```

## 📚 Methodological References

### Core Algorithms
1. **Traag, V. A., Waltman, L., & Van Eck, N. J. (2019).** From Louvain to Leiden: guaranteeing well-connected communities. *Scientific Reports*, 9(1), 1-12.

2. **McInnes, L., Healy, J., & Astels, S. (2017).** HDBSCAN: Hierarchical density based clustering. *Journal of Open Source Software*, 2(11), 205.

3. **Cohan, A., et al. (2020).** SPECTER: Document-level Representation Learning using Citation-informed Transformers. *ACL 2020*.

### Network Methods
4. **Serrano, M. Á., Boguná, M., & Vespignani, A. (2009).** Extracting the multiscale backbone of complex weighted networks. *PNAS*, 106(16), 6483-6488.

5. **Newman, M. E. (2006).** Modularity and community structure in networks. *PNAS*, 103(23), 8577-8582.

### Quality Metrics
6. **Rousseeuw, P. J. (1987).** Silhouettes: a graphical aid to the interpretation and validation of cluster analysis. *Journal of Computational and Applied Mathematics*, 20, 53-65.

7. **Davies, D. L., & Bouldin, D. W. (1979).** A cluster separation measure. *IEEE Transactions on Pattern Analysis and Machine Intelligence*, (2), 224-227.

## 🎉 What Makes This State-of-the-Art

### 1. Multi-Resolution Approach
- Goes beyond fixed-resolution clustering
- Captures structure at natural scales
- Automatic resolution detection

### 2. Quality-Driven Subdivision
- Ensures interpretable clusters
- Quality metrics at every level
- Prevents over/under-splitting

### 3. Network-Aware Analysis
- Citation flows between clusters
- Bridge paper detection
- Hierarchical backbone extraction

### 4. Comprehensive Validation
- Multiple quality metrics
- Cross-level coherence
- Bootstrap stability (available)

### 5. Practical Usability
- One-command execution
- Interactive visualization
- Detailed documentation

## 💡 Best Practices

1. **Start with Leiden**: Most robust for large corpora
2. **Use 3-4 levels**: Balance between granularity and interpretability
3. **Min cluster size 20**: Prevents noise clusters
4. **Review quality metrics**: Ensure silhouette >0.3 at each level
5. **Validate with domain knowledge**: Use dialog cards for expert review
6. **Explore bridge papers**: Key for cross-cutting insights
7. **Track temporal patterns**: Identify emerging vs. established streams

## 🚀 Future Enhancements

The hierarchical framework enables:

1. **Dynamic Dashboard**: Full JavaScript implementation with data loading
2. **Temporal Tracking**: How hierarchy evolves year-over-year
3. **Predictive Models**: Forecast emerging research areas
4. **Recommendation Engine**: Find relevant papers across levels
5. **Collaboration Networks**: Co-author analysis at each level
6. **Full-Text Integration**: When available from publishers

## 📞 Getting Help

### Check Outputs

```bash
# Verify all output files were generated
ls data/hierarchy*.json
ls data/hierarchical*.json
ls data/hierarchical*.csv
ls data/visualizations/
```

### Debug Mode

```python
# In run_hierarchical_analysis.py, add debugging
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Review Quality

```python
import json

with open('data/hierarchical_analysis.json') as f:
    analysis = json.load(f)

# Check silhouette scores
for level, metrics in analysis.get('quality_metrics', {}).items():
    print(f"Level {level}: Silhouette = {metrics['silhouette']:.3f}")
```

---

## 🎯 Summary

You now have a **state-of-the-art hierarchical research stream analysis system** that:

✅ Reveals research communities at 3-4 nested levels  
✅ Uses cutting-edge Leiden multi-resolution clustering  
✅ Analyzes citation networks and knowledge flows  
✅ Detects bridge papers connecting different streams  
✅ Generates comprehensive dialog cards for each cluster  
✅ Provides quality metrics and validation  
✅ Creates beautiful visualizations  
✅ Supports multiple corpora and methods  

**Next step**: Run `python run_hierarchical_analysis.py` and explore your multi-level research hierarchy! 🚀

---

**Created**: 2025-01-06  
**Version**: 1.0  
**Methods**: Leiden Multi-Resolution, HDBSCAN, SPECTER2  
**Status**: Production Ready ✨
