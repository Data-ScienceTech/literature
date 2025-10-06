"""
Generate Meaningful Cluster Names for IS Research Streams
Uses TF-IDF on titles/abstracts + citation analysis to create proper cluster themes
"""

import pandas as pd
import numpy as np
import json
from pathlib import Path
from collections import Counter
from sklearn.feature_extraction.text import TfidfVectorizer
import re

print("="*80)
print("GENERATING MEANINGFUL CLUSTER NAMES")
print("="*80)

# Load data
print("\n>> Loading data...")
df = pd.read_csv('data/papers_hierarchical_clustered.csv')

with open('data/clean/ais_basket_corpus_enriched.json', encoding='utf-8') as f:
    enriched_data = json.load(f)

print(f">> Loaded {len(df):,} papers")

# Create mapping
print("\n>> Creating paper mappings...")
paper_map = {}
for paper in enriched_data:
    paper_id = paper.get('doi') or paper.get('openalex_id', '')
    if paper_id:
        paper_map[paper_id] = paper

df['abstract'] = df['doi'].map(lambda x: paper_map.get(x, {}).get('abstract', ''))
df['openalex_citations'] = df['doi'].map(lambda x: paper_map.get(x, {}).get('openalex_cited_by_count', 0))

# Use openalex citations if available, fallback to crossref
df['citations_combined'] = df['openalex_citations'].fillna(df['Citations'])

print(f">> {(df['abstract'].notna() & (df['abstract'] != '')).sum():,} papers have abstracts")


def clean_text(text):
    """Clean text for TF-IDF analysis"""
    if not isinstance(text, str) or not text:
        return ""
    
    # Remove special characters but keep spaces
    text = re.sub(r'[^\w\s-]', ' ', text.lower())
    
    # Remove common IS stopwords beyond standard English
    is_stopwords = {'information', 'system', 'systems', 'study', 'research', 
                    'paper', 'article', 'using', 'based', 'approach', 'analysis',
                    'model', 'data', 'use', 'used', 'journal', 'quarterly',
                    'management', 'organizational', 'organization', 'jats',
                    'results', 'method', 'findings', 'abstract', 'available',
                    'issue', 'text', 'html', 'full', 'show'}
    
    words = text.split()
    words = [w for w in words if len(w) > 3 and w not in is_stopwords]
    
    return ' '.join(words)


def extract_cluster_themes(cluster_df, top_n_keywords=10, top_n_papers=5):
    """Extract meaningful themes from a cluster using TF-IDF and citation analysis"""
    
    # Combine title + abstract for better context
    texts = []
    for _, row in cluster_df.iterrows():
        title = str(row['Title']) if pd.notna(row['Title']) else ''
        abstract = str(row['abstract']) if pd.notna(row['abstract']) else ''
        # Weight title more heavily (repeat 3 times)
        combined = ' '.join([title] * 3 + [abstract])
        texts.append(clean_text(combined))
    
    if not texts or all(not t for t in texts):
        return {
            'keywords': [],
            'top_papers': [],
            'theme': 'Unknown',
            'description': 'No abstract data available'
        }
    
    # TF-IDF analysis
    try:
        vectorizer = TfidfVectorizer(
            max_features=100,
            ngram_range=(1, 3),  # Unigrams, bigrams, trigrams
            min_df=max(2, int(len(texts) * 0.05)),  # Must appear in at least 5% of docs
            max_df=0.8,  # But not more than 80%
            stop_words='english'
        )
        
        tfidf_matrix = vectorizer.fit_transform(texts)
        feature_names = vectorizer.get_feature_names_out()
        
        # Get mean TF-IDF score for each term across all documents
        mean_tfidf = np.array(tfidf_matrix.mean(axis=0)).ravel()
        top_indices = mean_tfidf.argsort()[-top_n_keywords:][::-1]
        
        keywords = [(str(feature_names[i]), float(mean_tfidf[i])) for i in top_indices]
        
    except Exception as e:
        print(f"  WARNING: TF-IDF failed: {e}")
        keywords = []
    
    # Get most cited papers (using combined citation data)
    top_papers = cluster_df.nlargest(top_n_papers, 'citations_combined')[
        ['Title', 'Author', 'Year', 'citations_combined', 'Journal']
    ].to_dict('records')
    
    # Generate theme name from top keywords
    if keywords:
        # Take top 3-4 keywords and create a theme name
        theme_keywords = [kw for kw, _ in keywords[:4]]
        theme = ' / '.join(theme_keywords[:3]).title()
        
        # Create description from top paper titles
        top_titles = [p['Title'][:60] for p in top_papers[:3]]
        description = f"Key papers: {'; '.join(top_titles)}"
    else:
        theme = "Undefined Theme"
        description = "Insufficient data for theme extraction"
    
    return {
        'keywords': keywords,
        'top_papers': top_papers,
        'theme': theme,
        'description': description,
        'paper_count': len(cluster_df),
        'total_citations': int(cluster_df['citations_combined'].sum()),
        'mean_citations': float(cluster_df['citations_combined'].mean()),
        'median_citations': float(cluster_df['citations_combined'].median())
    }


# Analyze all clusters at each level
print("\n>> Analyzing clusters and generating themes...")
cluster_themes = {}

for level in range(4):
    cluster_col = f'cluster_l{level}'
    if cluster_col not in df.columns:
        continue
    
    print(f"\n{'='*80}")
    print(f"LEVEL {level} - {df[cluster_col].nunique()} clusters")
    print('='*80)
    
    cluster_themes[f'level_{level}'] = {}
    
    for cluster_id in sorted(df[cluster_col].dropna().unique(), key=lambda x: str(x)):
        cluster_df = df[df[cluster_col] == cluster_id]
        
        print(f"\nCluster {cluster_id} ({len(cluster_df):,} papers)...")
        
        themes = extract_cluster_themes(cluster_df)
        cluster_themes[f'level_{level}'][str(cluster_id)] = themes
        
        # Print summary
        print(f"   Theme: {themes['theme']}")
        print(f"   Citations: {themes['total_citations']:,} total, {themes['mean_citations']:.1f} mean")
        
        if themes['keywords']:
            top_3_kw = ', '.join([kw for kw, _ in themes['keywords'][:3]])
            print(f"   Top Keywords: {top_3_kw}")
        
        if themes['top_papers']:
            top_paper = themes['top_papers'][0]
            cites = int(top_paper['citations_combined']) if not pd.isna(top_paper['citations_combined']) else 0
            print(f"   Most Cited: {top_paper['Title'][:60]}... ({cites} cites)")


# Save results
print("\n\n>> Saving cluster themes...")
output_file = 'data/cluster_themes.json'

with open(output_file, 'w', encoding='utf-8') as f:
    json.dump(cluster_themes, f, indent=2, ensure_ascii=False)

print(f">> Saved to: {output_file}")


# Generate summary report
print("\n\n" + "="*80)
print("CLUSTER THEMES SUMMARY")
print("="*80)

for level in range(4):
    level_key = f'level_{level}'
    if level_key not in cluster_themes:
        continue
    
    print(f"\n{'='*80}")
    print(f"LEVEL {level}")
    print('='*80)
    
    clusters = cluster_themes[level_key]
    
    for cluster_id, themes in sorted(clusters.items(), key=lambda x: x[1]['paper_count'], reverse=True):
        print(f"\nCluster {cluster_id}: {themes['theme']}")
        print(f"  Papers: {themes['paper_count']:,} | "
              f"Total Cites: {themes['total_citations']:,} | "
              f"Mean: {themes['mean_citations']:.1f}")
        
        if themes['keywords']:
            kw_str = ', '.join([f"{kw} ({score:.3f})" for kw, score in themes['keywords'][:5]])
            print(f"  Keywords: {kw_str}")


# Create human-readable mapping
print("\n\n" + "="*80)
print("CREATING HUMAN-READABLE CLUSTER MAP")
print("="*80)

cluster_map = {}

for level in range(4):
    level_key = f'level_{level}'
    if level_key not in cluster_themes:
        continue
    
    cluster_map[f'level_{level}'] = {}
    
    for cluster_id, themes in cluster_themes[level_key].items():
        cluster_map[f'level_{level}'][cluster_id] = {
            'name': themes['theme'],
            'paper_count': themes['paper_count'],
            'mean_citations': round(themes['mean_citations'], 1),
            'top_keywords': [kw for kw, _ in themes['keywords'][:5]]
        }

# Save simplified map
map_file = 'data/cluster_names_map.json'
with open(map_file, 'w', encoding='utf-8') as f:
    json.dump(cluster_map, f, indent=2, ensure_ascii=False)

print(f">> Saved cluster name mapping to: {map_file}")

print("\n\n" + "="*80)
print("CLUSTER THEME GENERATION COMPLETE!")
print("="*80)
print(f"\nAnalyzed {sum(len(clusters) for clusters in cluster_themes.values())} clusters")
print(f"Results saved to:")
print(f"   - {output_file} (detailed themes)")
print(f"   - {map_file} (simplified mapping)")
print("\nUse these meaningful themes instead of generic OpenAlex keywords!")
print("="*80)
