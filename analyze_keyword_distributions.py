"""
Analyze Keyword Distributions Per Cluster
Creates keyword-cluster matrices, co-occurrence analysis, and thematic profiles
"""
import json
import pandas as pd
import numpy as np
from pathlib import Path
from collections import Counter, defaultdict
from typing import Dict, List, Tuple
import itertools


def load_data_with_keywords():
    """Load clustered papers with keywords"""
    print("Loading data with keywords...")
    
    # Load clustered papers
    df = pd.read_csv('data/papers_hierarchical_clustered.csv')
    
    # Load enriched data for keywords
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
    
    print(f"Loaded {len(df):,} papers")
    papers_with_keywords = df['keywords'].notna().sum()
    print(f"Papers with keywords: {papers_with_keywords:,} ({100*papers_with_keywords/len(df):.1f}%)")
    
    return df


def analyze_cluster_keywords(df: pd.DataFrame, cluster_id: str, level: int = 0) -> Dict:
    """Analyze keyword distribution for a specific cluster"""
    cluster_col = f'cluster_l{level}'
    cluster_df = df[df[cluster_col] == cluster_id].copy()
    
    if len(cluster_df) == 0:
        return None
    
    # Collect all keywords
    all_keywords = []
    for kw_list in cluster_df['keywords'].dropna():
        if isinstance(kw_list, list):
            all_keywords.extend(kw_list)
    
    if not all_keywords:
        return None
    
    kw_counts = Counter(all_keywords)
    
    return {
        'cluster_id': cluster_id,
        'level': level,
        'size': len(cluster_df),
        'total_keywords': len(all_keywords),
        'unique_keywords': len(kw_counts),
        'top_keywords': dict(kw_counts.most_common(30)),
        'keyword_coverage': len([k for k in cluster_df['keywords'] if k]) / len(cluster_df),
        'avg_keywords_per_paper': len(all_keywords) / len(cluster_df)
    }


def create_keyword_cluster_matrix(df: pd.DataFrame, level: int = 0, top_n_keywords: int = 50):
    """Create matrix of top keywords across clusters"""
    print(f"\nCreating keyword-cluster matrix for Level {level}...")
    
    cluster_col = f'cluster_l{level}'
    if cluster_col not in df.columns:
        return None
    
    # Get top keywords overall
    all_keywords = []
    for kw_list in df['keywords'].dropna():
        if isinstance(kw_list, list):
            all_keywords.extend(kw_list)
    
    top_keywords = [kw for kw, _ in Counter(all_keywords).most_common(top_n_keywords)]
    
    # Create matrix
    clusters = sorted(df[cluster_col].dropna().unique(), key=lambda x: str(x))
    
    matrix_data = []
    for cluster_id in clusters:
        cluster_df = df[df[cluster_col] == cluster_id]
        
        # Count keywords in this cluster
        cluster_keywords = []
        for kw_list in cluster_df['keywords'].dropna():
            if isinstance(kw_list, list):
                cluster_keywords.extend(kw_list)
        
        kw_counter = Counter(cluster_keywords)
        
        row = {
            'cluster': cluster_id,
            'size': len(cluster_df)
        }
        
        # Add keyword frequencies
        for kw in top_keywords:
            row[kw] = kw_counter.get(kw, 0)
        
        matrix_data.append(row)
    
    matrix_df = pd.DataFrame(matrix_data)
    
    # Save matrix
    output_file = Path(f'data/keyword_cluster_matrix_level_{level}.csv')
    matrix_df.to_csv(output_file, index=False)
    print(f"   ✅ Saved to: {output_file}")
    
    return matrix_df


def analyze_keyword_cooccurrence(df: pd.DataFrame, cluster_id: str = None, level: int = 0, 
                                 top_n: int = 100, min_cooccurrence: int = 5):
    """Analyze keyword co-occurrence within papers"""
    if cluster_id:
        cluster_col = f'cluster_l{level}'
        papers = df[df[cluster_col] == cluster_id]
        scope = f"Cluster {cluster_id}"
    else:
        papers = df
        scope = "Entire corpus"
    
    print(f"\nAnalyzing keyword co-occurrence for {scope}...")
    
    # Collect co-occurrences
    cooccurrence = defaultdict(int)
    
    for kw_list in papers['keywords'].dropna():
        if isinstance(kw_list, list) and len(kw_list) >= 2:
            # Get all pairs
            for kw1, kw2 in itertools.combinations(sorted(kw_list), 2):
                cooccurrence[(kw1, kw2)] += 1
    
    # Filter by minimum occurrence
    cooccurrence = {k: v for k, v in cooccurrence.items() if v >= min_cooccurrence}
    
    # Sort by frequency
    sorted_pairs = sorted(cooccurrence.items(), key=lambda x: x[1], reverse=True)[:top_n]
    
    return [
        {
            'keyword1': pair[0],
            'keyword2': pair[1],
            'cooccurrence_count': count
        }
        for (pair, count) in sorted_pairs
    ]


def create_cluster_thematic_profiles(df: pd.DataFrame, level: int = 0):
    """Create thematic profiles based on keyword concentrations"""
    print(f"\n{'='*80}")
    print(f"CLUSTER THEMATIC PROFILES - LEVEL {level}")
    print(f"{'='*80}")
    
    cluster_col = f'cluster_l{level}'
    if cluster_col not in df.columns:
        return None
    
    clusters = sorted(df[cluster_col].dropna().unique(), key=lambda x: str(x))
    profiles = []
    
    for cluster_id in clusters:
        analysis = analyze_cluster_keywords(df, cluster_id, level)
        if analysis:
            profiles.append(analysis)
            
            print(f"\n>> CLUSTER {cluster_id} ({analysis['size']} papers)")
            print(f"   Unique keywords: {analysis['unique_keywords']}")
            print(f"   Avg keywords/paper: {analysis['avg_keywords_per_paper']:.1f}")
            print(f"   Coverage: {100*analysis['keyword_coverage']:.1f}% of papers")
            
            # Show top keywords with percentages
            print(f"   Top keywords:")
            top_kws = list(analysis['top_keywords'].items())[:10]
            for kw, count in top_kws:
                pct = 100 * count / analysis['size']
                print(f"      - {kw}: {count} papers ({pct:.1f}%)")
    
    # Save profiles (convert numpy types to Python native types)
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
    
    profiles_serializable = convert_to_serializable(profiles)
    
    output_file = Path(f'data/keyword_profiles_level_{level}.json')
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(profiles_serializable, f, indent=2, ensure_ascii=False)
    
    print(f"\n✅ Saved keyword profiles to: {output_file}")
    
    return profiles


def identify_distinctive_keywords(df: pd.DataFrame, level: int = 0, top_n: int = 10):
    """Identify keywords that are distinctive to each cluster (TF-IDF style)"""
    print(f"\n{'='*80}")
    print(f"DISTINCTIVE KEYWORDS PER CLUSTER - LEVEL {level}")
    print(f"{'='*80}")
    
    cluster_col = f'cluster_l{level}'
    if cluster_col not in df.columns:
        return None
    
    clusters = sorted(df[cluster_col].dropna().unique(), key=lambda x: str(x))
    
    # Calculate keyword frequencies per cluster
    cluster_keywords = {}
    for cluster_id in clusters:
        cluster_df = df[df[cluster_col] == cluster_id]
        keywords = []
        for kw_list in cluster_df['keywords'].dropna():
            if isinstance(kw_list, list):
                keywords.extend(kw_list)
        cluster_keywords[cluster_id] = Counter(keywords)
    
    # Calculate document frequency (how many clusters contain each keyword)
    doc_freq = defaultdict(int)
    for kw_counter in cluster_keywords.values():
        for kw in kw_counter.keys():
            doc_freq[kw] += 1
    
    num_clusters = len(clusters)
    
    # Calculate TF-IDF scores for each cluster
    distinctive_results = []
    
    for cluster_id in clusters:
        kw_counter = cluster_keywords[cluster_id]
        cluster_size = df[df[cluster_col] == cluster_id].shape[0]
        
        # Calculate TF-IDF
        tfidf_scores = {}
        for kw, count in kw_counter.items():
            tf = count / cluster_size  # Term frequency normalized by cluster size
            idf = np.log(num_clusters / doc_freq[kw])  # Inverse document frequency
            tfidf_scores[kw] = tf * idf
        
        # Get top distinctive keywords
        top_distinctive = sorted(tfidf_scores.items(), key=lambda x: x[1], reverse=True)[:top_n]
        
        distinctive_results.append({
            'cluster_id': cluster_id,
            'size': cluster_size,
            'distinctive_keywords': [
                {
                    'keyword': kw,
                    'tfidf_score': score,
                    'count': kw_counter[kw],
                    'cluster_frequency': kw_counter[kw] / cluster_size
                }
                for kw, score in top_distinctive
            ]
        })
        
        print(f"\n🔹 CLUSTER {cluster_id} - Most Distinctive Keywords:")
        for item in distinctive_results[-1]['distinctive_keywords']:
            print(f"      - {item['keyword']}: "
                  f"TF-IDF={item['tfidf_score']:.3f}, "
                  f"count={item['count']}, "
                  f"freq={100*item['cluster_frequency']:.1f}%")
    
    # Save (convert numpy types)
    def convert_to_serializable(obj):
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
    
    distinctive_serializable = convert_to_serializable(distinctive_results)
    
    output_file = Path(f'data/distinctive_keywords_level_{level}.json')
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(distinctive_serializable, f, indent=2, ensure_ascii=False)
    
    print(f"\n✅ Saved distinctive keywords to: {output_file}")
    
    return distinctive_results


def main():
    """Run keyword distribution analysis"""
    df = load_data_with_keywords()
    
    # Load hierarchy to get max depth
    with open('data/hierarchy_leiden.json') as f:
        hierarchy = json.load(f)
    
    max_depth = hierarchy.get('max_depth', 0)
    
    print(f"\n{'='*80}")
    print(f"KEYWORD DISTRIBUTION ANALYSIS")
    print(f"{'='*80}")
    print(f"Analyzing {max_depth + 1} hierarchy levels")
    
    # Analyze each level
    for level in range(max_depth + 1):
        # Thematic profiles
        create_cluster_thematic_profiles(df, level=level)
        
        # Distinctive keywords
        identify_distinctive_keywords(df, level=level, top_n=15)
        
        # Keyword-cluster matrix
        create_keyword_cluster_matrix(df, level=level, top_n_keywords=100)
        
        # Co-occurrence analysis (for level 0 only to keep it manageable)
        if level == 0:
            print(f"\n{'='*80}")
            print(f"KEYWORD CO-OCCURRENCE ANALYSIS")
            print(f"{'='*80}")
            
            cooccurrence = analyze_keyword_cooccurrence(df, cluster_id=None, level=level, 
                                                       top_n=100, min_cooccurrence=10)
            
            print(f"\nTop 20 keyword pairs (corpus-wide):")
            for i, pair in enumerate(cooccurrence[:20], 1):
                print(f"{i:2d}. {pair['keyword1']} + {pair['keyword2']}: "
                      f"{pair['cooccurrence_count']} papers")
            
            # Save (convert numpy types)
            def convert_to_serializable(obj):
                if isinstance(obj, dict):
                    return {k: convert_to_serializable(v) for k, v in obj.items()}
                elif isinstance(obj, list):
                    return [convert_to_serializable(item) for item in obj]
                elif isinstance(obj, np.integer):
                    return int(obj)
                elif isinstance(obj, np.floating):
                    return float(obj)
                else:
                    return obj
            
            cooccurrence_serializable = convert_to_serializable(cooccurrence)
            
            with open('data/keyword_cooccurrence.json', 'w', encoding='utf-8') as f:
                json.dump(cooccurrence_serializable, f, indent=2, ensure_ascii=False)
            print(f"\n✅ Saved co-occurrence data to: data/keyword_cooccurrence.json")
    
    print(f"\n{'='*80}")
    print(f"✅ KEYWORD ANALYSIS COMPLETE!")
    print(f"{'='*80}")
    print(f"\nGenerated files:")
    for level in range(max_depth + 1):
        files = [
            f'data/keyword_profiles_level_{level}.json',
            f'data/distinctive_keywords_level_{level}.json',
            f'data/keyword_cluster_matrix_level_{level}.csv'
        ]
        for filepath in files:
            if Path(filepath).exists():
                print(f"  ✅ {filepath}")
    
    if Path('data/keyword_cooccurrence.json').exists():
        print(f"  ✅ data/keyword_cooccurrence.json")


if __name__ == '__main__':
    main()
