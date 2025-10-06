"""
Comprehensive Summary of Cluster Analysis Results
Shows composition, keywords, and visualizations
"""
import json
import pandas as pd
from pathlib import Path
from collections import Counter

print("="*80)
print("COMPREHENSIVE CLUSTER ANALYSIS SUMMARY")
print("="*80)
print("\nGenerated from enhanced hierarchical analysis with OpenAlex keywords")
print(f"Date: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M')}")

# Load main data
print("\n" + "-"*80)
print("LOADING DATA")
print("-"*80)

df = pd.read_csv('data/papers_hierarchical_clustered.csv')
print(f"Total papers: {len(df):,}")

with open('data/hierarchy_leiden.json') as f:
    hierarchy = json.load(f)

print(f"Hierarchy depth: {hierarchy.get('max_depth', 0)} levels")
print(f"Total clusters: {hierarchy.get('total_clusters', 0)}")

# Load keywords
with open('data/clean/ais_basket_corpus_enriched.json', encoding='utf-8') as f:
    enriched_data = json.load(f)

keyword_map = {}
for paper in enriched_data:
    paper_id = paper.get('doi') or paper.get('openalex_id', '')
    if paper_id and 'subject' in paper and isinstance(paper['subject'], list):
        keyword_map[paper_id] = paper['subject']

df['keywords'] = df['doi'].map(keyword_map)
papers_with_kw = df['keywords'].notna().sum()
print(f"Papers with keywords: {papers_with_kw:,} ({100*papers_with_kw/len(df):.1f}%)")

# Analyze each level
for level in range(hierarchy.get('max_depth', 0) + 1):
    print(f"\n{'='*80}")
    print(f"LEVEL {level} ANALYSIS")
    print(f"{'='*80}")
    
    cluster_col = f'cluster_l{level}'
    if cluster_col not in df.columns:
        print(f"Level {level} not found")
        continue
    
    clusters = sorted(df[cluster_col].dropna().unique(), key=lambda x: str(x))
    print(f"\nNumber of clusters: {len(clusters)}")
    
    # Cluster sizes
    sizes = df[cluster_col].value_counts().sort_values(ascending=False)
    print(f"\nCluster size distribution:")
    print(f"  Range: {sizes.min()}-{sizes.max()} papers")
    print(f"  Mean: {sizes.mean():.0f} papers")
    print(f"  Median: {sizes.median():.0f} papers")
    
    # Top 5 clusters by size
    print(f"\n  Top 5 largest clusters:")
    for cluster_id, size in sizes.head(5).items():
        pct = 100 * size / len(df)
        print(f"    Cluster {cluster_id}: {size:,} papers ({pct:.1f}%)")
    
    # Journal distribution across clusters
    if 'Journal' in df.columns:
        print(f"\n  Journal diversity:")
        journal_diversity = df.groupby(cluster_col)['Journal'].nunique().sort_values(ascending=False)
        print(f"    Most diverse: Cluster {journal_diversity.index[0]} ({journal_diversity.iloc[0]} journals)")
        print(f"    Least diverse: Cluster {journal_diversity.index[-1]} ({journal_diversity.iloc[-1]} journals)")
    
    # Citation patterns
    if 'Citations' in df.columns:
        print(f"\n  Citation statistics:")
        cite_means = df.groupby(cluster_col)['Citations'].agg(['mean', 'median', 'sum']).sort_values('mean', ascending=False)
        print(f"    Highest mean: Cluster {cite_means.index[0]} ({cite_means.iloc[0]['mean']:.1f} cites/paper)")
        print(f"    Lowest mean: Cluster {cite_means.index[-1]} ({cite_means.iloc[-1]['mean']:.1f} cites/paper)")
    
    # Keyword analysis per cluster
    print(f"\n  Keyword analysis (top 3 clusters):")
    for cluster_id in list(clusters)[:3]:
        cluster_df = df[df[cluster_col] == cluster_id]
        all_kw = []
        for kw_list in cluster_df['keywords'].dropna():
            if isinstance(kw_list, list):
                all_kw.extend(kw_list)
        
        if all_kw:
            kw_counter = Counter(all_kw)
            top_kw = kw_counter.most_common(5)
            kw_str = ', '.join([f"{kw} ({cnt})" for kw, cnt in top_kw])
            print(f"\n    Cluster {cluster_id} ({len(cluster_df)} papers):")
            print(f"      Top keywords: {kw_str}")
            print(f"      Unique keywords: {len(kw_counter)}")
            print(f"      Avg keywords/paper: {len(all_kw)/len(cluster_df):.1f}")

# Summary of generated files
print(f"\n{'='*80}")
print(f"GENERATED OUTPUT FILES")
print(f"{'='*80}")

output_files = {
    'Hierarchy & Analysis': [
        'data/hierarchy_leiden.json',
        'data/hierarchical_analysis.json',
        'data/papers_hierarchical_clustered.csv',
        'data/embeddings_hierarchical.npy'
    ],
    'Composition Analysis': [
        'data/cluster_composition_level_0.json',
        'data/cluster_composition_level_1.json',
        'data/cluster_composition_level_2.json',
        'data/cluster_composition_level_3.json',
    ],
    'Keyword Analysis': [
        'data/keyword_profiles_level_0.json',
        'data/keyword_profiles_level_1.json',
        'data/keyword_profiles_level_2.json',
        'data/keyword_profiles_level_3.json',
        'data/distinctive_keywords_level_0.json',
        'data/keyword_cluster_matrix_level_0.csv',
        'data/keyword_cooccurrence.json'
    ],
    'Visualizations': [
        'data/visualizations/sunburst_hierarchy.html',
        'data/visualizations/dendrogram_hierarchy.png',
        'data/visualizations/cluster_sizes_heatmap.png',
        'data/visualizations/keyword_wordclouds_level_0.png',
        'data/visualizations/temporal_evolution.png'
    ]
}

for category, files in output_files.items():
    print(f"\n{category}:")
    for filepath in files:
        path = Path(filepath)
        if path.exists():
            size_mb = path.stat().st_size / (1024 * 1024)
            print(f"  [OK] {filepath} ({size_mb:.2f} MB)")
        else:
            print(f"  [ ] {filepath} (not yet generated)")

print(f"\n{'='*80}")
print(f"ANALYSIS SUMMARY COMPLETE")
print(f"{'='*80}")
print(f"\nNext steps:")
print(f"  1. Examine cluster compositions: python analyze_cluster_composition.py")
print(f"  2. Analyze keyword distributions: python analyze_keyword_distributions.py")  
print(f"  3. Create visualizations: python create_visualizations.py")
print(f"  4. Review output files in data/ and data/visualizations/")
print(f"\n")
