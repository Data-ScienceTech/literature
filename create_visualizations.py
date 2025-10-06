"""
Create Hierarchical Visualizations
Generates sunburst charts, dendrograms, network graphs, and keyword clouds
"""
import json
import pandas as pd
import numpy as np
from pathlib import Path
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from collections import Counter
import warnings
warnings.filterwarnings('ignore')

# Try to import plotly for interactive visualizations
try:
    import plotly.graph_objects as go
    import plotly.express as px
    HAS_PLOTLY = True
except ImportError:
    HAS_PLOTLY = False
    print("⚠️  Plotly not installed. Interactive visualizations will be skipped.")
    print("   Install with: pip install plotly")


def load_data():
    """Load all necessary data"""
    print("Loading data...")
    
    # Clustered papers
    df = pd.read_csv('data/papers_hierarchical_clustered.csv')
    
    # Hierarchy
    with open('data/hierarchy_leiden.json') as f:
        hierarchy = json.load(f)
    
    # Keywords
    try:
        with open('data/clean/ais_basket_corpus_enriched.json', encoding='utf-8') as f:
            enriched_data = json.load(f)
        
        keyword_map = {}
        for paper in enriched_data:
            # Try multiple ID fields
            paper_id = paper.get('doi') or paper.get('openalex_id', '')
            if paper_id and 'subject' in paper:
                subjects = paper['subject']
                if isinstance(subjects, list):
                    keyword_map[paper_id] = subjects
        
        df['keywords'] = df['doi'].map(keyword_map)
    except Exception as e:
        print(f"Warning: Could not load keywords: {e}")
        df['keywords'] = None
    
    return df, hierarchy


def create_sunburst_chart(df: pd.DataFrame, hierarchy: dict, max_depth: int = 3):
    """Create interactive sunburst chart of the hierarchy"""
    if not HAS_PLOTLY:
        print("⚠️  Skipping sunburst chart (plotly not available)")
        return
    
    print("\nCreating sunburst chart...")
    
    # Prepare data for sunburst
    labels = []
    parents = []
    values = []
    colors_list = []
    
    # Add root
    labels.append("All Papers")
    parents.append("")
    values.append(len(df))
    colors_list.append(0)
    
    # Process hierarchy levels
    for level in range(min(max_depth + 1, hierarchy.get('max_depth', 0) + 1)):
        cluster_col = f'cluster_l{level}'
        if cluster_col not in df.columns:
            continue
        
        # Get clusters at this level
        for cluster_id in df[cluster_col].dropna().unique():
            cluster_df = df[df[cluster_col] == cluster_id]
            
            # Determine parent
            if level == 0:
                parent = "All Papers"
            else:
                # Find parent cluster
                parent_col = f'cluster_l{level-1}'
                if parent_col in cluster_df.columns:
                    parent_id = cluster_df[parent_col].iloc[0]
                    parent = f"L{level-1}:{parent_id}"
                else:
                    parent = "All Papers"
            
            label = f"L{level}:{cluster_id}"
            labels.append(label)
            parents.append(parent)
            values.append(len(cluster_df))
            colors_list.append(level)
    
    # Create sunburst
    fig = go.Figure(go.Sunburst(
        labels=labels,
        parents=parents,
        values=values,
        branchvalues="total",
        marker=dict(
            colorscale='Viridis',
            cmid=max_depth/2,
            line=dict(width=2)
        ),
        hovertemplate='<b>%{label}</b><br>Papers: %{value}<br><extra></extra>'
    ))
    
    fig.update_layout(
        title=dict(
            text="Hierarchical Research Stream Structure<br><sub>Enhanced with OpenAlex Keywords</sub>",
            x=0.5,
            xanchor='center'
        ),
        width=1000,
        height=1000,
        font=dict(size=12)
    )
    
    output_file = 'data/visualizations/sunburst_hierarchy.html'
    Path('data/visualizations').mkdir(exist_ok=True)
    fig.write_html(output_file)
    print(f"   ✅ Saved to: {output_file}")
    
    return fig


def create_dendrogram_visualization(hierarchy: dict):
    """Create dendrogram visualization of cluster hierarchy"""
    print("\nCreating dendrogram...")
    
    root_nodes = hierarchy.get('root_nodes', [])
    if not root_nodes:
        print("   ⚠️  No root nodes found")
        return
    
    fig, ax = plt.subplots(figsize=(16, 10))
    
    # Recursive function to draw tree
    def draw_node(node, x, y, x_span, level, ax):
        """Recursively draw hierarchy tree"""
        node_id = node.get('id', '?')
        size = node.get('size', 0)
        children = node.get('children', [])
        
        # Draw node
        node_color = plt.cm.tab10(level % 10)
        circle = plt.Circle((x, y), 0.3, color=node_color, alpha=0.7, ec='black', linewidth=2)
        ax.add_patch(circle)
        
        # Label
        ax.text(x, y, f"{node_id}\n{size}", ha='center', va='center', 
                fontsize=8, fontweight='bold')
        
        # Draw children
        if children:
            n_children = len(children)
            child_y = y - 2
            child_x_span = x_span / max(n_children, 1)
            
            for i, child in enumerate(children):
                child_x = x - x_span/2 + child_x_span * (i + 0.5)
                
                # Draw line to child
                ax.plot([x, child_x], [y-0.3, child_y+0.3], 'k-', alpha=0.3, linewidth=1.5)
                
                # Recursively draw child
                draw_node(child, child_x, child_y, child_x_span, level + 1, ax)
    
    # Draw each root node
    n_roots = len(root_nodes)
    root_span = 20
    
    for i, root in enumerate(root_nodes[:10]):  # Limit to 10 for clarity
        root_x = -root_span/2 + root_span * (i / max(n_roots-1, 1))
        draw_node(root, root_x, 0, root_span/n_roots, 0, ax)
    
    ax.set_xlim(-root_span/2 - 1, root_span/2 + 1)
    ax.set_ylim(-10, 1)
    ax.set_aspect('equal')
    ax.axis('off')
    ax.set_title('Hierarchical Cluster Dendrogram\n(Enhanced with OpenAlex Keywords)', 
                 fontsize=16, fontweight='bold', pad=20)
    
    # Legend
    legend_elements = [
        mpatches.Patch(color=plt.cm.tab10(i), label=f'Level {i}', alpha=0.7)
        for i in range(4)
    ]
    ax.legend(handles=legend_elements, loc='upper right', fontsize=10)
    
    plt.tight_layout()
    output_file = 'data/visualizations/dendrogram_hierarchy.png'
    Path('data/visualizations').mkdir(exist_ok=True)
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"   ✅ Saved to: {output_file}")
    plt.close()


def create_cluster_size_heatmap(df: pd.DataFrame, hierarchy: dict):
    """Create heatmap of cluster sizes across levels"""
    print("\nCreating cluster size heatmap...")
    
    max_depth = hierarchy.get('max_depth', 0)
    
    # Collect sizes for each level
    level_data = []
    for level in range(max_depth + 1):
        cluster_col = f'cluster_l{level}'
        if cluster_col in df.columns:
            sizes = df[cluster_col].value_counts().sort_index()
            level_data.append(sizes)
    
    if not level_data:
        print("   ⚠️  No cluster data found")
        return
    
    # Create figure
    fig, axes = plt.subplots(len(level_data), 1, figsize=(14, 3*len(level_data)))
    if len(level_data) == 1:
        axes = [axes]
    
    for level, (ax, sizes) in enumerate(zip(axes, level_data)):
        colors = plt.cm.viridis(sizes.values / sizes.max())
        bars = ax.bar(range(len(sizes)), sizes.values, color=colors, edgecolor='black', linewidth=0.5)
        
        ax.set_xlabel('Cluster ID', fontsize=12)
        ax.set_ylabel('Number of Papers', fontsize=12)
        ax.set_title(f'Level {level} - Cluster Sizes ({len(sizes)} clusters)', 
                    fontsize=14, fontweight='bold')
        ax.set_xticks(range(len(sizes)))
        ax.set_xticklabels([str(x) for x in sizes.index], rotation=45, ha='right')
        ax.grid(axis='y', alpha=0.3)
        
        # Add value labels on bars
        for i, (bar, val) in enumerate(zip(bars, sizes.values)):
            if val > 30:  # Only label larger clusters
                ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 10, 
                       str(val), ha='center', va='bottom', fontsize=8)
    
    plt.suptitle('Cluster Size Distribution Across Hierarchy Levels', 
                fontsize=16, fontweight='bold', y=1.002)
    plt.tight_layout()
    
    output_file = 'data/visualizations/cluster_sizes_heatmap.png'
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"   ✅ Saved to: {output_file}")
    plt.close()


def create_keyword_wordclouds(df: pd.DataFrame, level: int = 0, max_clusters: int = 9):
    """Create word clouds for top clusters based on keywords"""
    try:
        from wordcloud import WordCloud
    except ImportError:
        print("⚠️  Skipping word clouds (wordcloud not installed)")
        print("   Install with: pip install wordcloud")
        return
    
    print(f"\nCreating keyword word clouds for Level {level}...")
    
    cluster_col = f'cluster_l{level}'
    if cluster_col not in df.columns:
        print(f"   ⚠️  Level {level} not found")
        return
    
    # Get top clusters by size
    top_clusters = df[cluster_col].value_counts().head(max_clusters).index
    
    n_cols = 3
    n_rows = (len(top_clusters) + n_cols - 1) // n_cols
    
    fig, axes = plt.subplots(n_rows, n_cols, figsize=(18, 6*n_rows))
    axes = axes.flatten() if n_rows > 1 else [axes] if n_cols == 1 else axes
    
    for idx, cluster_id in enumerate(top_clusters):
        cluster_df = df[df[cluster_col] == cluster_id]
        
        # Collect keywords
        all_keywords = []
        for kw_list in cluster_df['keywords'].dropna():
            if isinstance(kw_list, list):
                all_keywords.extend(kw_list)
        
        if not all_keywords:
            axes[idx].text(0.5, 0.5, 'No keywords', ha='center', va='center')
            axes[idx].set_title(f'Cluster {cluster_id} ({len(cluster_df)} papers)')
            axes[idx].axis('off')
            continue
        
        # Create word cloud
        keyword_freq = Counter(all_keywords)
        
        wc = WordCloud(
            width=600,
            height=400,
            background_color='white',
            colormap='viridis',
            relative_scaling=0.5,
            min_font_size=8
        ).generate_from_frequencies(keyword_freq)
        
        axes[idx].imshow(wc, interpolation='bilinear')
        axes[idx].set_title(f'Cluster {cluster_id}\n({len(cluster_df)} papers, {len(keyword_freq)} unique keywords)', 
                          fontsize=12, fontweight='bold')
        axes[idx].axis('off')
    
    # Hide empty subplots
    for idx in range(len(top_clusters), len(axes)):
        axes[idx].axis('off')
    
    plt.suptitle(f'Keyword Distributions - Level {level} Top Clusters\n(Enhanced with OpenAlex)', 
                fontsize=16, fontweight='bold')
    plt.tight_layout()
    
    output_file = f'data/visualizations/keyword_wordclouds_level_{level}.png'
    Path('data/visualizations').mkdir(exist_ok=True)
    plt.savefig(output_file, dpi=200, bbox_inches='tight')
    print(f"   ✅ Saved to: {output_file}")
    plt.close()


def create_temporal_evolution_plot(df: pd.DataFrame, hierarchy: dict):
    """Create temporal evolution plot showing when clusters were active"""
    print("\nCreating temporal evolution visualization...")
    
    if 'Year' not in df.columns:
        print("   ⚠️  No year information available")
        return
    
    fig, axes = plt.subplots(hierarchy.get('max_depth', 0) + 1, 1, 
                            figsize=(16, 4 * (hierarchy.get('max_depth', 0) + 1)))
    
    if not isinstance(axes, np.ndarray):
        axes = [axes]
    
    for level, ax in enumerate(axes):
        cluster_col = f'cluster_l{level}'
        if cluster_col not in df.columns:
            continue
        
        clusters = sorted(df[cluster_col].dropna().unique(), key=lambda x: str(x))
        
        for i, cluster_id in enumerate(clusters[:20]):  # Limit to 20 clusters
            cluster_df = df[df[cluster_col] == cluster_id]
            years = cluster_df['Year'].dropna()
            
            if len(years) == 0:
                continue
            
            # Create histogram
            year_counts = years.value_counts().sort_index()
            
            # Plot as area
            ax.fill_between(year_counts.index, i, i + year_counts.values/year_counts.max(), 
                           alpha=0.6, label=f'C{cluster_id}')
        
        ax.set_xlabel('Year', fontsize=12)
        ax.set_ylabel('Clusters', fontsize=12)
        ax.set_title(f'Level {level} - Temporal Evolution', fontsize=14, fontweight='bold')
        ax.grid(axis='x', alpha=0.3)
        
        if len(clusters) <= 15:
            ax.legend(loc='center left', bbox_to_anchor=(1, 0.5), ncol=1, fontsize=8)
    
    plt.suptitle('Research Stream Temporal Evolution\n(Enhanced with OpenAlex Keywords)', 
                fontsize=16, fontweight='bold')
    plt.tight_layout()
    
    output_file = 'data/visualizations/temporal_evolution.png'
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"   ✅ Saved to: {output_file}")
    plt.close()


def main():
    """Create all visualizations"""
    print(f"\n{'='*80}")
    print(f"CREATING HIERARCHICAL VISUALIZATIONS")
    print(f"{'='*80}")
    
    # Load data
    df, hierarchy = load_data()
    
    print(f"\nTotal papers: {len(df):,}")
    print(f"Hierarchy depth: {hierarchy.get('max_depth', 0)} levels")
    print(f"Total clusters: {hierarchy.get('total_clusters', 0)}")
    
    # Create visualizations directory
    Path('data/visualizations').mkdir(exist_ok=True)
    
    # Generate visualizations
    create_sunburst_chart(df, hierarchy, max_depth=3)
    create_dendrogram_visualization(hierarchy)
    create_cluster_size_heatmap(df, hierarchy)
    create_temporal_evolution_plot(df, hierarchy)
    
    # Word clouds for each level
    for level in range(min(3, hierarchy.get('max_depth', 0) + 1)):
        create_keyword_wordclouds(df, level=level, max_clusters=9)
    
    print(f"\n{'='*80}")
    print(f"✅ VISUALIZATION COMPLETE!")
    print(f"{'='*80}")
    print(f"\nGenerated files in data/visualizations/:")
    viz_dir = Path('data/visualizations')
    if viz_dir.exists():
        for file in sorted(viz_dir.glob('*')):
            size_mb = file.stat().st_size / (1024 * 1024)
            print(f"  ✅ {file.name} ({size_mb:.2f} MB)")


if __name__ == '__main__':
    main()
