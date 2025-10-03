#!/usr/bin/env python3
"""
Extract key topics from each research stream using title and abstract keywords.
"""

import pandas as pd
import numpy as np
from collections import Counter
import re
from sklearn.feature_extraction.text import TfidfVectorizer

def clean_text(text):
    """Clean and tokenize text."""
    if pd.isna(text):
        return ""
    text = str(text).lower()
    # Remove special characters but keep spaces and letters
    text = re.sub(r'[^a-z\s]', ' ', text)
    # Remove common words
    stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
                  'of', 'with', 'by', 'from', 'as', 'is', 'was', 'are', 'were', 'be',
                  'been', 'being', 'have', 'has', 'had', 'do', 'does', 'did', 'will',
                  'would', 'should', 'could', 'may', 'might', 'must', 'can', 'this',
                  'that', 'these', 'those', 'i', 'you', 'he', 'she', 'it', 'we', 'they',
                  'what', 'which', 'who', 'when', 'where', 'why', 'how', 'all', 'each',
                  'every', 'both', 'few', 'more', 'most', 'other', 'some', 'such', 'than',
                  'too', 'very', 'also', 'paper', 'study', 'research', 'abstract', 'using',
                  'based', 'results', 'findings', 'article', 'examines', 'explores', 'we',
                  'our', 'use', 'used', 'between', 'among', 'through', 'into', 'out'}
    words = text.split()
    words = [w for w in words if len(w) > 3 and w not in stop_words]
    return ' '.join(words)

print("🔍 EXTRACTING RESEARCH STREAM TOPICS")
print("="*70)

# Load data
df = pd.read_csv('data/papers_clustered_is_corpus.csv')

print(f"Analyzing {df['cluster'].nunique()} research streams...")

# Analyze each cluster
stream_topics = []

for cluster_id in sorted(df['cluster'].unique()):
    cluster_df = df[df['cluster'] == cluster_id].copy()
    
    # Combine titles and abstracts
    texts = []
    for idx, row in cluster_df.iterrows():
        title = clean_text(row['Title'])
        abstract = clean_text(row['Abstract']) if pd.notna(row['Abstract']) else ""
        texts.append(f"{title} {abstract}")
    
    # TF-IDF to extract key terms
    vectorizer = TfidfVectorizer(max_features=20, ngram_range=(1, 2), min_df=2)
    try:
        tfidf_matrix = vectorizer.fit_transform(texts)
        feature_names = vectorizer.get_feature_names_out()
        
        # Get top terms
        scores = tfidf_matrix.sum(axis=0).A1
        top_indices = scores.argsort()[-10:][::-1]
        top_terms = [feature_names[i] for i in top_indices]
    except:
        top_terms = ["(insufficient data)"]
    
    # Get temporal info
    year_range = f"{cluster_df['Year'].min()}-{cluster_df['Year'].max()}"
    recent_count = len(cluster_df[cluster_df['Year'] >= 2020])
    
    # Get citation info
    total_cites = cluster_df['Citations'].sum()
    avg_cites = cluster_df['Citations'].mean()
    top_paper = cluster_df.nlargest(1, 'Citations').iloc[0]
    
    # Get journal distribution
    top_journal = cluster_df['Journal'].value_counts().index[0]
    
    stream_topics.append({
        'stream_id': cluster_id,
        'size': len(cluster_df),
        'year_range': year_range,
        'recent_papers': recent_count,
        'total_citations': int(total_cites),
        'avg_citations': round(avg_cites, 1),
        'top_terms': top_terms[:10],
        'top_paper_title': top_paper['Title'],
        'top_paper_year': int(top_paper['Year']),
        'top_paper_cites': int(top_paper['Citations']),
        'primary_journal': top_journal
    })

# Sort by size
stream_topics.sort(key=lambda x: x['size'], reverse=True)

print(f"\n📊 RESEARCH STREAM TOPICS (sorted by size):\n")
print("="*70)

for i, stream in enumerate(stream_topics[:15], 1):  # Top 15
    print(f"\n🔬 STREAM #{stream['stream_id']} ({stream['size']} papers, {stream['year_range']})")
    print(f"   Primary Journal: {stream['primary_journal']}")
    print(f"   Citations: {stream['total_citations']:,} total, {stream['avg_citations']} avg")
    print(f"   Recent Activity: {stream['recent_papers']} papers since 2020")
    
    print(f"   📌 Key Topics: {', '.join(stream['top_terms'][:5])}")
    
    title = stream['top_paper_title'][:70] + "..." if len(stream['top_paper_title']) > 70 else stream['top_paper_title']
    print(f"   📚 Most Cited: \"{title}\"")
    print(f"      ({stream['top_paper_year']}, {stream['top_paper_cites']:,} citations)")

# Export full details
output_df = pd.DataFrame(stream_topics)
output_df.to_csv('data/research_stream_topics.csv', index=False)

print(f"\n\n💾 Saved detailed topics to data/research_stream_topics.csv")

# Identify hot emerging topics
print(f"\n\n🔥 HOT EMERGING TOPICS (High recent activity %):")
print("="*70)

emerging = sorted(stream_topics, key=lambda x: x['recent_papers']/x['size'], reverse=True)[:10]
for i, stream in enumerate(emerging, 1):
    recent_pct = stream['recent_papers'] / stream['size'] * 100
    print(f"{i:2d}. Stream #{stream['stream_id']:2d} ({recent_pct:4.1f}% recent): {', '.join(stream['top_terms'][:3])}")

# Identify most impactful streams
print(f"\n\n⭐ MOST IMPACTFUL STREAMS (by average citations):")
print("="*70)

impactful = sorted(stream_topics, key=lambda x: x['avg_citations'], reverse=True)[:10]
for i, stream in enumerate(impactful, 1):
    print(f"{i:2d}. Stream #{stream['stream_id']:2d} ({stream['avg_citations']:5.1f} avg cites, {stream['size']} papers): {', '.join(stream['top_terms'][:3])}")

print(f"\n✨ TOPIC EXTRACTION COMPLETE!")
