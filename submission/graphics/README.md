# Graphics Directory - Manuscript Figures

This directory will contain the figures for the manuscript. Below are specifications for each required figure.

---

## Figure 1: Analytical Pipeline Diagram

### Purpose
Illustrate the complete data processing and analysis workflow from raw corpus to final taxonomy.

### Content
Show the following stages with arrows:

```
1. Data Collection
   - AIS Basket corpus (12,564 papers)
   - Filter: Papers with abstracts (8,110)
   
2. Citation Enrichment
   - OpenAlex API queries
   - Extract referenced_works
   - Result: 545,865 references, 88% coverage
   
3. Text Feature Extraction
   - Preprocessing (tokenization, stemming)
   - TF-IDF vectorization (8,110 × 12,847)
   - LSI dimensionality reduction (→ 200 dimensions)
   
4. Citation Network Features
   - Bibliographic coupling matrix
   - Inverted index optimization
   - Result: 2.84M coupling edges, 91.3% sparse
   
5. Hybrid Feature Construction
   - Normalize text and citation features
   - Combine: 60% text + 40% citations
   - Optimize weights via silhouette scores
   
6. Three-Level Hierarchical Clustering
   - L1: Agglomerative clustering (k=8)
   - L2: NMF within L1 clusters (→ 48 topics)
   - L3: NMF within L2 clusters (→ 182 topics)
   
7. Validation & Output
   - Silhouette score: 0.340
   - Manual review: 87% accuracy
   - Export: CSVs + interactive explorer
```

### Specifications
- **Format**: Vector (PDF, SVG, or EPS preferred)
- **Size**: Full page width or 2-column width
- **Colors**: Use consistent color scheme (suggest blue/green/orange for stages)
- **Style**: Clean, professional, easily readable
- **Labels**: Clear stage names and metrics

### Tools Recommended
- **Python**: matplotlib, graphviz, or diagrams library
- **Draw.io**: Free online diagramming tool
- **Adobe Illustrator**: Professional vector graphics
- **PowerPoint**: Export as high-res PDF

### Example Code (Python with matplotlib)
```python
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

# Create figure
fig, ax = plt.subplots(figsize=(12, 8))
ax.set_xlim(0, 10)
ax.set_ylim(0, 10)
ax.axis('off')

# Define boxes for each stage
stages = [
    {"name": "Data Collection", "pos": (1, 8), "color": "#3498db"},
    {"name": "Citation Enrichment", "pos": (1, 6.5), "color": "#2ecc71"},
    # ... add more stages
]

# Draw boxes and arrows
# (Implementation details)

plt.savefig('figure1_pipeline.pdf', bbox_inches='tight', dpi=300)
```

---

## Figure 2: Three-Level Hierarchy Sunburst Visualization

### Purpose
Show the hierarchical structure of research streams, subtopics, and micro-topics with proportional sizes.

### Content
- **Inner ring**: 8 L1 research streams (different colors)
- **Middle ring**: 48 L2 subtopics (shaded by parent stream)
- **Outer ring**: 182 L3 micro-topics (further shaded)
- **Size**: Each segment proportional to number of papers
- **Labels**: Stream names (L1 visible, L2/L3 on hover if interactive)

### Specifications
- **Format**: Vector (PDF) or interactive HTML (for supplement)
- **Size**: Full page or 2-column width
- **Colors**: 8 distinct hues for L1, gradients for L2/L3
- **Interactivity** (if HTML): Hover shows details, click to zoom
- **Legend**: L1 stream names with colors

### Tools Recommended
- **Python plotly**: `px.sunburst()` for interactive version
- **D3.js**: Professional interactive visualization
- **R**: ggplot2 with ggtree or sunburstR package
- **Excel/Tableau**: Simple static version

### Example Code (Python with plotly)
```python
import plotly.express as px
import pandas as pd

# Load hierarchy data
df = pd.read_csv('topics_level3.csv')

# Create sunburst
fig = px.sunburst(
    df,
    path=['L1_label', 'L2_label', 'L3_label'],
    values='size',
    color='L1',
    color_discrete_sequence=px.colors.qualitative.Set2
)

fig.update_layout(
    title='Three-Level Research Taxonomy',
    font=dict(size=14)
)

# Export
fig.write_html('figure2_sunburst_interactive.html')
fig.write_image('figure2_sunburst.pdf', width=800, height=800)
```

---

## Figure 3: Temporal Evolution Timeline (1977-2024)

### Purpose
Show how research streams emerged, grew, and evolved over 47 years.

### Content
- **X-axis**: Years (1977-2024)
- **Y-axis**: Number of papers or percentage of corpus
- **Lines/Areas**: One per L1 stream (8 total)
- **Colors**: Match sunburst figure colors
- **Annotations**: Mark key periods (e.g., "Web 2.0 Era", "Digital Transformation")

### Specifications
- **Format**: Vector (PDF, EPS)
- **Size**: Full page width
- **Style**: Stacked area chart or line chart
- **Colors**: Same as Figure 2 for consistency
- **Legend**: L1 stream names
- **Grid**: Light gridlines for readability

### Tools Recommended
- **Python matplotlib/seaborn**: Professional quality
- **Python plotly**: Interactive version
- **R ggplot2**: Publication-quality plots
- **Excel**: Simple version

### Example Code (Python with matplotlib)
```python
import matplotlib.pyplot as plt
import pandas as pd

# Load data
df = pd.read_csv('doc_assignments.csv')

# Aggregate by year and stream
temporal = df.groupby(['year', 'L1_label']).size().unstack(fill_value=0)

# Create stacked area plot
fig, ax = plt.subplots(figsize=(12, 6))
temporal.plot.area(
    ax=ax,
    stacked=True,
    colormap='tab10',
    alpha=0.8
)

ax.set_xlabel('Year', fontsize=12)
ax.set_ylabel('Number of Papers', fontsize=12)
ax.set_title('Evolution of IS Research Streams (1977-2024)', fontsize=14)
ax.legend(title='Research Stream', bbox_to_anchor=(1.05, 1), loc='upper left')
ax.grid(alpha=0.3)

plt.tight_layout()
plt.savefig('figure3_timeline.pdf', dpi=300, bbox_inches='tight')
```

---

## Additional Figures (Optional)

### Figure 4: Citation Network Visualization
- Sample of highly coupled papers
- Network graph showing connections
- Node size = paper influence
- Edge thickness = coupling strength

### Figure 5: Silhouette Score Comparison
- Bar chart comparing text-only vs. hybrid
- Show improvement (0.029 → 0.340)
- Include confidence intervals

### Figure 6: Cluster Size Distribution
- Histogram or box plot
- Show balanced cluster sizes
- L1, L2, L3 distributions

---

## General Guidelines

### Resolution
- **Vector graphics**: Preferred (scalable)
- **Raster graphics**: Minimum 300 DPI
- **Screen resolution**: 600 DPI for print journals

### Colors
- Use colorblind-friendly palettes
- Maintain consistency across figures
- Suggested palettes:
  - ColorBrewer Set2 or Paired
  - Matplotlib tab10
  - Seaborn deep or muted

### Fonts
- Sans-serif (Arial, Helvetica, Open Sans)
- Minimum 8pt for labels
- 10-12pt for axis labels
- 12-14pt for titles

### File Formats
- **Primary**: PDF (vector, widely accepted)
- **Alternative**: EPS (older journals), SVG (modern)
- **Supplementary**: PNG (300+ DPI) for web

### Journal-Specific Requirements
Check target journal's figure guidelines:
- MIS Quarterly: PDF, 300 DPI minimum
- JAIS: PDF or EPS, specific size limits
- PLOS ONE: TIFF or PNG, 300-600 DPI

---

## Files to Create

Place completed figures in this directory:

- [ ] `figure1_pipeline.pdf` - Analytical pipeline
- [ ] `figure2_sunburst.pdf` - Hierarchy visualization
- [ ] `figure3_timeline.pdf` - Temporal evolution
- [ ] `figure2_sunburst_interactive.html` - Interactive sunburst (supplementary)
- [ ] `figureX_network.pdf` - Citation network (optional)
- [ ] `figureX_validation.pdf` - Validation metrics (optional)

---

## Data Sources

All data needed for figures is in:
```
../data/clean/hybrid_streams_3level/
├── doc_assignments.csv        (for temporal analysis)
├── topics_level1.csv           (for L1 labels)
├── topics_level2.csv           (for L2 labels)
├── topics_level3.csv           (for hierarchy sunburst)
└── citation_network_stats.json (for network metrics)
```

---

## Testing Figures

Before finalizing:
1. **Readability**: Can labels be read at publication size?
2. **Color**: Test with colorblindness simulator
3. **Consistency**: Colors/fonts match across figures?
4. **File size**: <10MB per figure (journals have limits)
5. **Quality**: Zoom to 200% - still crisp?

---

**Status**: Ready for figure creation  
**Estimated Time**: 2-4 hours for all figures  
**Tools Needed**: Python (recommended) or alternative design tools

