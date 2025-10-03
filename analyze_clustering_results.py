#!/usr/bin/env python3
"""
Comprehensive analysis of IS corpus clustering results.
"""

import pandas as pd
import numpy as np
import json
from collections import Counter

print("🔬 ANALYZING IS CORPUS CLUSTERING RESULTS")
print("="*70)

# Load clustered data
df = pd.read_csv('data/papers_clustered_is_corpus.csv')

print(f"\n📊 DATASET OVERVIEW:")
print(f"   Total papers: {len(df):,}")
print(f"   Date range: {df['Year'].min()}-{df['Year'].max()}")
print(f"   Journals: {df['Journal'].nunique()}")
print(f"   Research streams: {df['cluster'].nunique()}")

# Cluster statistics
print(f"\n🎯 CLUSTERING QUALITY:")
cluster_sizes = df['cluster'].value_counts().sort_index()
print(f"   Number of streams: {len(cluster_sizes)}")
print(f"   Largest stream: {cluster_sizes.max():,} papers")
print(f"   Smallest stream: {cluster_sizes.min():,} papers")
print(f"   Mean stream size: {cluster_sizes.mean():.1f} papers")
print(f"   Median stream size: {cluster_sizes.median():.1f} papers")

# Stream size distribution
print(f"\n📊 STREAM SIZE DISTRIBUTION:")
size_bins = [
    (0, 100, "Small (< 100 papers)"),
    (100, 200, "Medium (100-200)"),
    (200, 300, "Large (200-300)"),
    (300, 500, "Very Large (300-500)"),
    (500, 1000, "Mega (500+)")
]

for min_size, max_size, label in size_bins:
    count = ((cluster_sizes >= min_size) & (cluster_sizes < max_size)).sum()
    if count > 0:
        print(f"   {label:25s}: {count:2d} streams")

# Temporal distribution
print(f"\n📅 TEMPORAL DISTRIBUTION:")
year_ranges = [
    (2000, 2004, "2000-2004"),
    (2005, 2009, "2005-2009"),
    (2010, 2014, "2010-2014"),
    (2015, 2019, "2015-2019"),
    (2020, 2025, "2020-2025")
]

for start, end, label in year_ranges:
    subset = df[(df['Year'] >= start) & (df['Year'] <= end)]
    print(f"   {label}: {len(subset):4,} papers ({len(subset)/len(df)*100:4.1f}%)")

# Journal distribution
print(f"\n📚 BY JOURNAL:")
journal_counts = df['Journal'].value_counts()
for journal, count in journal_counts.items():
    print(f"   {journal:50s}: {count:4,} papers ({count/len(df)*100:4.1f}%)")

# Top streams by size
print(f"\n🌟 TOP 10 LARGEST RESEARCH STREAMS:")
for i, (cluster_id, size) in enumerate(cluster_sizes.nlargest(10).items(), 1):
    cluster_papers = df[df['cluster'] == cluster_id]
    years = f"{cluster_papers['Year'].min()}-{cluster_papers['Year'].max()}"
    top_journal = cluster_papers['Journal'].value_counts().index[0]
    print(f"   {i:2d}. Stream {cluster_id:2d}: {size:3,} papers ({years}) - {top_journal}")

# Analyze stream temporal patterns
print(f"\n📈 STREAM TEMPORAL PATTERNS:")
emerging_streams = []
declining_streams = []
stable_streams = []

for cluster_id in sorted(df['cluster'].unique()):
    cluster_papers = df[df['cluster'] == cluster_id]
    
    # Split into early and late periods
    median_year = cluster_papers['Year'].median()
    early = cluster_papers[cluster_papers['Year'] < median_year]
    late = cluster_papers[cluster_papers['Year'] >= median_year]
    
    if len(early) > 0 and len(late) > 0:
        growth_rate = (len(late) - len(early)) / len(early) * 100
        
        if growth_rate > 50:
            emerging_streams.append((cluster_id, growth_rate, len(cluster_papers)))
        elif growth_rate < -50:
            declining_streams.append((cluster_id, growth_rate, len(cluster_papers)))
        else:
            stable_streams.append((cluster_id, growth_rate, len(cluster_papers)))

print(f"   Emerging streams (>50% growth): {len(emerging_streams)}")
if emerging_streams:
    for cid, growth, size in sorted(emerging_streams, key=lambda x: x[1], reverse=True)[:5]:
        print(f"      Stream {cid:2d}: +{growth:5.1f}% growth ({size} papers)")

print(f"   Declining streams (>50% decline): {len(declining_streams)}")
if declining_streams:
    for cid, growth, size in sorted(declining_streams, key=lambda x: x[1])[:5]:
        print(f"      Stream {cid:2d}: {growth:5.1f}% decline ({size} papers)")

print(f"   Stable streams: {len(stable_streams)}")

# Citation analysis
if 'Citations' in df.columns:
    print(f"\n📊 CITATION ANALYSIS:")
    total_citations = df['Citations'].sum()
    mean_citations = df['Citations'].mean()
    median_citations = df['Citations'].median()
    
    print(f"   Total citations: {total_citations:,}")
    print(f"   Mean citations/paper: {mean_citations:.1f}")
    print(f"   Median citations/paper: {median_citations:.1f}")
    
    # Most cited papers
    print(f"\n   📚 Most cited papers:")
    top_cited = df.nlargest(5, 'Citations')[['Title', 'Year', 'Citations', 'cluster']]
    for idx, row in top_cited.iterrows():
        title = row['Title'][:60] + "..." if len(row['Title']) > 60 else row['Title']
        print(f"      {row['Citations']:5,} cites: {title} ({row['Year']}, Stream {row['cluster']})")
    
    # Most cited streams
    print(f"\n   🌟 Most cited research streams:")
    stream_citations = df.groupby('cluster').agg({
        'Citations': ['sum', 'mean', 'count']
    }).round(1)
    stream_citations.columns = ['total_cites', 'avg_cites', 'papers']
    stream_citations = stream_citations.sort_values('total_cites', ascending=False)
    
    for i, (cluster_id, row) in enumerate(stream_citations.head(10).iterrows(), 1):
        print(f"      {i:2d}. Stream {cluster_id:2d}: {int(row['total_cites']):6,} total ({row['avg_cites']:5.1f} avg, {int(row['papers'])} papers)")

# Recent trends (2020-2025)
print(f"\n🔥 HOT TOPICS (2020-2025):")
recent = df[df['Year'] >= 2020]
recent_streams = recent['cluster'].value_counts().head(10)
for i, (cluster_id, count) in enumerate(recent_streams.items(), 1):
    pct = count / len(recent) * 100
    total_in_stream = len(df[df['cluster'] == cluster_id])
    recent_pct = count / total_in_stream * 100
    print(f"   {i:2d}. Stream {cluster_id:2d}: {count:3,} recent papers ({pct:4.1f}% of recent, {recent_pct:4.1f}% of stream)")

# Save summary statistics
summary = {
    'total_papers': len(df),
    'num_streams': int(df['cluster'].nunique()),
    'date_range': f"{df['Year'].min()}-{df['Year'].max()}",
    'largest_stream': int(cluster_sizes.max()),
    'smallest_stream': int(cluster_sizes.min()),
    'mean_stream_size': float(cluster_sizes.mean()),
    'emerging_streams': len(emerging_streams),
    'declining_streams': len(declining_streams),
    'stable_streams': len(stable_streams),
    'journals': df['Journal'].unique().tolist()
}

if 'Citations' in df.columns:
    summary['total_citations'] = int(df['Citations'].sum())
    summary['mean_citations'] = float(df['Citations'].mean())

with open('data/clustering_analysis.json', 'w') as f:
    json.dump(summary, f, indent=2)

print(f"\n💾 Saved analysis summary to data/clustering_analysis.json")

print(f"\n✨ ANALYSIS COMPLETE!")
print(f"\n🎯 KEY INSIGHTS:")
print(f"   • Successfully identified {df['cluster'].nunique()} research streams")
print(f"   • Corpus spans {df['Year'].max() - df['Year'].min()} years ({df['Year'].min()}-{df['Year'].max()})")
print(f"   • {len(emerging_streams)} emerging streams show >50% growth")
print(f"   • {len(declining_streams)} streams showing decline")
if 'Citations' in df.columns:
    print(f"   • {int(df['Citations'].sum()):,} total citations across corpus")
