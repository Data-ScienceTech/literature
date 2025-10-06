"""
Examine Cluster Compositions
Analyzes papers, authors, journals, citations, and temporal patterns within clusters
"""
import json
import pandas as pd
import numpy as np
from pathlib import Path
from collections import Counter
from typing import Dict, List

def load_data():
    """Load clustered papers and hierarchy"""
    print("Loading data...")
    df = pd.read_csv('data/papers_hierarchical_clustered.csv')
    
    with open('data/hierarchy_leiden.json') as f:
        hierarchy = json.load(f)
    
    # Load original enriched data for keywords
    try:
        with open('data/clean/ais_basket_corpus_enriched.json', encoding='utf-8') as f:
            enriched_data = json.load(f)
        
        # Create mapping of DOI to keywords
        keyword_map = {}
        for paper in enriched_data:
            # Try multiple ID fields
            paper_id = paper.get('doi') or paper.get('openalex_id', '')
            if paper_id and 'subject' in paper:
                subjects = paper['subject']
                if isinstance(subjects, list):
                    keyword_map[paper_id] = subjects
        
        # Add keywords to df using doi
        df['keywords'] = df['doi'].map(keyword_map)
    except Exception as e:
        print(f"Warning: Could not load keywords: {e}")
        df['keywords'] = None
    
    return df, hierarchy


def analyze_cluster(df: pd.DataFrame, cluster_id: str, level: int = 0) -> Dict:
    """Analyze composition of a specific cluster"""
    cluster_col = f'cluster_l{level}'
    cluster_df = df[df[cluster_col] == cluster_id].copy()
    
    if len(cluster_df) == 0:
        return None
    
    analysis = {
        'cluster_id': cluster_id,
        'level': level,
        'size': len(cluster_df),
        'journals': {},
        'temporal': {},
        'citations': {},
        'authors': {},
        'top_papers': [],
        'keywords': {}
    }
    
    # Journal distribution
    journal_counts = cluster_df['Journal'].value_counts()
    analysis['journals'] = {
        'distribution': journal_counts.to_dict(),
        'primary': journal_counts.index[0] if len(journal_counts) > 0 else None,
        'diversity': len(journal_counts),
        'top_3': journal_counts.head(3).to_dict()
    }
    
    # Temporal patterns
    if 'Year' in cluster_df.columns:
        years = cluster_df['Year'].dropna()
        if len(years) > 0:
            analysis['temporal'] = {
                'year_range': [int(years.min()), int(years.max())],
                'median_year': int(years.median()),
                'mean_year': float(years.mean()),
                'papers_per_year': cluster_df.groupby('Year').size().to_dict()
            }
    
    # Citation statistics
    if 'Citations' in cluster_df.columns:
        cites = cluster_df['Citations'].dropna()
        if len(cites) > 0:
            analysis['citations'] = {
                'total': int(cites.sum()),
                'mean': float(cites.mean()),
                'median': float(cites.median()),
                'max': int(cites.max()),
                'highly_cited_count': int((cites >= cites.quantile(0.9)).sum())
            }
    
    # Author analysis
    if 'Author' in cluster_df.columns:
        # Extract all authors
        all_authors = []
        for authors_str in cluster_df['Author'].dropna():
            if isinstance(authors_str, str):
                authors = [a.strip() for a in authors_str.split(';')]
                all_authors.extend(authors)
        
        if all_authors:
            author_counts = Counter(all_authors)
            analysis['authors'] = {
                'unique_authors': len(author_counts),
                'total_authorships': len(all_authors),
                'top_10': dict(author_counts.most_common(10)),
                'avg_authors_per_paper': len(all_authors) / len(cluster_df)
            }
    
    # Top cited papers in cluster
    if 'Citations' in cluster_df.columns and 'Title' in cluster_df.columns:
        top_papers = cluster_df.nlargest(5, 'Citations')[['Title', 'Author', 'Year', 'Journal', 'Citations']]
        analysis['top_papers'] = top_papers.to_dict('records')
    
    # Keyword analysis
    if 'keywords' in cluster_df.columns:
        all_keywords = []
        for kw_list in cluster_df['keywords'].dropna():
            if isinstance(kw_list, list):
                all_keywords.extend(kw_list)
        
        if all_keywords:
            kw_counts = Counter(all_keywords)
            analysis['keywords'] = {
                'unique_keywords': len(kw_counts),
                'total_keyword_instances': len(all_keywords),
                'top_20': dict(kw_counts.most_common(20)),
                'avg_keywords_per_paper': len(all_keywords) / len(cluster_df)
            }
    
    return analysis


def create_composition_report(df: pd.DataFrame, hierarchy: Dict, level: int = 0, max_clusters: int = 20):
    """Create comprehensive composition report for a hierarchy level"""
    print(f"\n{'='*80}")
    print(f"CLUSTER COMPOSITION ANALYSIS - LEVEL {level}")
    print(f"{'='*80}")
    
    cluster_col = f'cluster_l{level}'
    if cluster_col not in df.columns:
        print(f"Level {level} not found in data")
        return
    
    unique_clusters = df[cluster_col].dropna().unique()
    print(f"\nAnalyzing {len(unique_clusters)} clusters at Level {level}")
    print(f"Total papers: {len(df)}")
    
    # Analyze each cluster
    results = []
    for cluster_id in sorted(unique_clusters, key=lambda x: str(x))[:max_clusters]:
        analysis = analyze_cluster(df, cluster_id, level)
        if analysis:
            results.append(analysis)
    
    # Display summary
    print(f"\n{'-'*80}")
    print(f"CLUSTER SUMMARIES")
    print(f"{'-'*80}")
    
    for i, result in enumerate(results, 1):
        print(f"\n>> CLUSTER {result['cluster_id']} ({result['size']} papers)")
        print(f"   Primary Journal: {result['journals']['primary']}")
        
        if result['temporal']:
            print(f"   Time Period: {result['temporal']['year_range'][0]}-{result['temporal']['year_range'][1]} "
                  f"(median: {result['temporal']['median_year']})")
        
        if result['citations']:
            print(f"   Citations: Total={result['citations']['total']:,}, "
                  f"Mean={result['citations']['mean']:.1f}, "
                  f"Median={result['citations']['median']:.0f}")
        
        if result['authors']:
            print(f"   Authors: {result['authors']['unique_authors']} unique, "
                  f"avg {result['authors']['avg_authors_per_paper']:.1f} per paper")
        
        if result['keywords'] and result['keywords'].get('top_20'):
            top_kw = list(result['keywords']['top_20'].items())[:5]
            kw_str = ', '.join([f"{kw} ({cnt})" for kw, cnt in top_kw])
            print(f"   Top Keywords: {kw_str}")
        
        # Show top papers
        if result['top_papers']:
            print(f"   >> Most Cited Paper:")
            top = result['top_papers'][0]
            title = str(top.get('Title', 'Unknown'))[:80]
            author = str(top.get('Author', 'Unknown'))[:60] if top.get('Author') else 'Unknown'
            year = top.get('Year', '?')
            citations = top.get('Citations', 0)
            print(f"      {title}...")
            print(f"      {author} ({year}), {citations} citations")
    
    # Save detailed results (convert numpy types to Python native types)
    def convert_to_serializable(obj):
        """Convert numpy types to native Python types"""
        if isinstance(obj, dict):
            return {k: convert_to_serializable(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [convert_to_serializable(item) for item in obj]
        elif isinstance(obj, np.integer):
            return int(obj)
        elif isinstance(obj, np.floating):
            return float(obj)
        elif pd.isna(obj):
            return None
        else:
            return obj
    
    results_serializable = convert_to_serializable(results)
    
    output_file = Path(f'data/cluster_composition_level_{level}.json')
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results_serializable, f, indent=2, ensure_ascii=False)
    
    print(f"\n{'='*80}")
    print(f"✅ Detailed composition saved to: {output_file}")
    print(f"{'='*80}")
    
    return results


def compare_clusters(df: pd.DataFrame, level: int = 0):
    """Create comparative statistics across clusters"""
    print(f"\n{'='*80}")
    print(f"COMPARATIVE CLUSTER ANALYSIS - LEVEL {level}")
    print(f"{'='*80}")
    
    cluster_col = f'cluster_l{level}'
    if cluster_col not in df.columns:
        return
    
    # Group by cluster
    grouped = df.groupby(cluster_col)
    
    # Size distribution
    sizes = grouped.size().sort_values(ascending=False)
    print(f"\n📊 Cluster Size Distribution:")
    print(f"   Total clusters: {len(sizes)}")
    print(f"   Size range: {sizes.min()}-{sizes.max()} papers")
    print(f"   Mean size: {sizes.mean():.0f} papers")
    print(f"   Median size: {sizes.median():.0f} papers")
    print(f"\n   Top 5 largest clusters:")
    for cluster_id, size in sizes.head(5).items():
        print(f"      Cluster {cluster_id}: {size} papers ({100*size/len(df):.1f}%)")
    
    # Journal diversity
    if 'Journal' in df.columns:
        print(f"\n📚 Journal Distribution:")
        journal_diversity = grouped['Journal'].nunique().sort_values(ascending=False)
        print(f"   Most diverse cluster: {journal_diversity.index[0]} ({journal_diversity.iloc[0]} journals)")
        print(f"   Least diverse cluster: {journal_diversity.index[-1]} ({journal_diversity.iloc[-1]} journals)")
    
    # Citation statistics
    if 'Citations' in df.columns:
        print(f"\n📈 Citation Patterns:")
        citation_means = grouped['Citations'].mean().sort_values(ascending=False)
        print(f"   Highest mean citations: Cluster {citation_means.index[0]} ({citation_means.iloc[0]:.1f} cites/paper)")
        print(f"   Top 5 by mean citations:")
        for cluster_id, mean_cites in citation_means.head(5).items():
            total = grouped.get_group(cluster_id)['Citations'].sum()
            print(f"      Cluster {cluster_id}: {mean_cites:.1f} mean, {total:,} total")
    
    # Temporal patterns
    if 'Year' in df.columns:
        print(f"\n📅 Temporal Distribution:")
        median_years = grouped['Year'].median().sort_values()
        print(f"   Oldest cluster (by median): {median_years.index[0]} (median year: {median_years.iloc[0]:.0f})")
        print(f"   Newest cluster (by median): {median_years.index[-1]} (median year: {median_years.iloc[-1]:.0f})")


def main():
    """Run cluster composition analysis"""
    # Load data
    df, hierarchy = load_data()
    
    print(f"\n{'='*80}")
    print(f"HIERARCHICAL CLUSTER COMPOSITION ANALYZER")
    print(f"{'='*80}")
    print(f"Total papers: {len(df):,}")
    print(f"Hierarchy depth: {hierarchy.get('max_depth', 0)} levels")
    
    # Analyze each level
    for level in range(hierarchy.get('max_depth', 0) + 1):
        # Detailed composition
        create_composition_report(df, hierarchy, level=level, max_clusters=15)
        
        # Comparative analysis
        compare_clusters(df, level=level)
        
        print("\n")
    
    print(f"\n{'='*80}")
    print(f"✅ COMPOSITION ANALYSIS COMPLETE!")
    print(f"{'='*80}")
    print(f"\nGenerated files:")
    for level in range(hierarchy.get('max_depth', 0) + 1):
        filepath = f'data/cluster_composition_level_{level}.json'
        if Path(filepath).exists():
            print(f"  ✅ {filepath}")


if __name__ == '__main__':
    main()
