#!/usr/bin/env python3
"""
Create a visual summary of the clustering results.
"""

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

# Set style
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (16, 10)

# Load data
df = pd.read_csv('data/papers_clustered_is_corpus.csv')

print("📊 Creating visualization summary...")

# Create figure with subplots
fig = plt.figure(figsize=(20, 12))

# 1. Papers per year
ax1 = plt.subplot(2, 3, 1)
year_counts = df['Year'].value_counts().sort_index()
ax1.bar(year_counts.index, year_counts.values, color='steelblue', alpha=0.7)
ax1.set_xlabel('Year', fontsize=12)
ax1.set_ylabel('Number of Papers', fontsize=12)
ax1.set_title('Publication Trend (2000-2025)', fontsize=14, fontweight='bold')
ax1.grid(axis='y', alpha=0.3)

# 2. Stream size distribution
ax2 = plt.subplot(2, 3, 2)
stream_sizes = df['cluster'].value_counts().values
ax2.hist(stream_sizes, bins=15, color='coral', alpha=0.7, edgecolor='black')
ax2.set_xlabel('Stream Size (papers)', fontsize=12)
ax2.set_ylabel('Number of Streams', fontsize=12)
ax2.set_title('Research Stream Size Distribution', fontsize=14, fontweight='bold')
ax2.axvline(stream_sizes.mean(), color='red', linestyle='--', linewidth=2, label=f'Mean: {stream_sizes.mean():.0f}')
ax2.legend()
ax2.grid(axis='y', alpha=0.3)

# 3. Journal distribution
ax3 = plt.subplot(2, 3, 3)
journal_counts = df['Journal'].value_counts()
colors = sns.color_palette("husl", len(journal_counts))
ax3.pie(journal_counts.values, labels=[j[:25] + '...' if len(j) > 25 else j for j in journal_counts.index],
        autopct='%1.1f%%', colors=colors, startangle=90)
ax3.set_title('Papers by Journal', fontsize=14, fontweight='bold')

# 4. Top 10 streams by size
ax4 = plt.subplot(2, 3, 4)
top_streams = df['cluster'].value_counts().head(10)
ax4.barh(range(len(top_streams)), top_streams.values, color='teal', alpha=0.7)
ax4.set_yticks(range(len(top_streams)))
ax4.set_yticklabels([f'Stream {i}' for i in top_streams.index])
ax4.set_xlabel('Number of Papers', fontsize=12)
ax4.set_title('Top 10 Largest Research Streams', fontsize=14, fontweight='bold')
ax4.grid(axis='x', alpha=0.3)

# 5. Citation distribution (log scale)
ax5 = plt.subplot(2, 3, 5)
citations = df['Citations'].values
citations_log = np.log10(citations + 1)  # +1 to avoid log(0)
ax5.hist(citations_log, bins=50, color='purple', alpha=0.7, edgecolor='black')
ax5.set_xlabel('Citations (log10 scale)', fontsize=12)
ax5.set_ylabel('Number of Papers', fontsize=12)
ax5.set_title('Citation Distribution (Log Scale)', fontsize=14, fontweight='bold')
ax5.axvline(np.log10(df['Citations'].median() + 1), color='red', linestyle='--', 
            linewidth=2, label=f'Median: {df["Citations"].median():.0f}')
ax5.legend()
ax5.grid(axis='y', alpha=0.3)

# 6. Recent activity heatmap (papers per stream per period)
ax6 = plt.subplot(2, 3, 6)
periods = {
    '2000-2004': (2000, 2004),
    '2005-2009': (2005, 2009),
    '2010-2014': (2010, 2014),
    '2015-2019': (2015, 2019),
    '2020-2025': (2020, 2025)
}

# Get top 15 streams
top_15_streams = df['cluster'].value_counts().head(15).index

heatmap_data = []
for stream_id in top_15_streams:
    stream_df = df[df['cluster'] == stream_id]
    row = []
    for period, (start, end) in periods.items():
        count = len(stream_df[(stream_df['Year'] >= start) & (stream_df['Year'] <= end)])
        row.append(count)
    heatmap_data.append(row)

heatmap_df = pd.DataFrame(heatmap_data, 
                          columns=list(periods.keys()),
                          index=[f'Stream {i}' for i in top_15_streams])

sns.heatmap(heatmap_df, annot=True, fmt='d', cmap='YlOrRd', ax=ax6, cbar_kws={'label': 'Papers'})
ax6.set_title('Temporal Evolution (Top 15 Streams)', fontsize=14, fontweight='bold')
ax6.set_xlabel('Time Period', fontsize=12)
ax6.set_ylabel('Research Stream', fontsize=12)

plt.tight_layout()
plt.savefig('data/clustering_visualization.png', dpi=300, bbox_inches='tight')
print("✅ Saved visualization to data/clustering_visualization.png")

# Create additional focused plots
fig2, axes = plt.subplots(2, 2, figsize=(16, 12))

# Top cited papers
ax = axes[0, 0]
top_cited = df.nlargest(20, 'Citations')
ax.barh(range(len(top_cited)), top_cited['Citations'].values, color='gold', alpha=0.7)
ax.set_yticks(range(len(top_cited)))
ax.set_yticklabels([title[:40] + '...' if len(title) > 40 else title for title in top_cited['Title']], fontsize=8)
ax.set_xlabel('Citations', fontsize=12)
ax.set_title('Top 20 Most Cited Papers', fontsize=14, fontweight='bold')
ax.grid(axis='x', alpha=0.3)

# Citations by stream
ax = axes[0, 1]
stream_citations = df.groupby('cluster')['Citations'].sum().sort_values(ascending=False).head(15)
ax.barh(range(len(stream_citations)), stream_citations.values, color='darkgreen', alpha=0.7)
ax.set_yticks(range(len(stream_citations)))
ax.set_yticklabels([f'Stream {i}' for i in stream_citations.index])
ax.set_xlabel('Total Citations', fontsize=12)
ax.set_title('Top 15 Most Cited Streams', fontsize=14, fontweight='bold')
ax.grid(axis='x', alpha=0.3)

# Recent activity (2020+)
ax = axes[1, 0]
recent_df = df[df['Year'] >= 2020]
recent_streams = recent_df['cluster'].value_counts().head(15)
ax.bar(range(len(recent_streams)), recent_streams.values, color='dodgerblue', alpha=0.7)
ax.set_xticks(range(len(recent_streams)))
ax.set_xticklabels([f'S{i}' for i in recent_streams.index], rotation=0)
ax.set_ylabel('Papers (2020-2025)', fontsize=12)
ax.set_xlabel('Stream ID', fontsize=12)
ax.set_title('Hottest Topics (2020-2025)', fontsize=14, fontweight='bold')
ax.grid(axis='y', alpha=0.3)

# Average citations by stream
ax = axes[1, 1]
stream_avg_cites = df.groupby('cluster')['Citations'].mean().sort_values(ascending=False).head(15)
ax.barh(range(len(stream_avg_cites)), stream_avg_cites.values, color='crimson', alpha=0.7)
ax.set_yticks(range(len(stream_avg_cites)))
ax.set_yticklabels([f'Stream {i}' for i in stream_avg_cites.index])
ax.set_xlabel('Average Citations', fontsize=12)
ax.set_title('Most Impactful Streams (Avg Citations)', fontsize=14, fontweight='bold')
ax.grid(axis='x', alpha=0.3)

plt.tight_layout()
plt.savefig('data/clustering_details.png', dpi=300, bbox_inches='tight')
print("✅ Saved detailed visualization to data/clustering_details.png")

# Summary statistics
print("\n📊 VISUALIZATION SUMMARY STATISTICS:")
print(f"   Total plots created: 10")
print(f"   Papers visualized: {len(df):,}")
print(f"   Streams analyzed: {df['cluster'].nunique()}")
print(f"   Date range: {df['Year'].min()}-{df['Year'].max()}")
print(f"   Total citations: {df['Citations'].sum():,}")

print("\n✨ Visualizations complete!")
print("   📁 clustering_visualization.png - Overview (6 panels)")
print("   📁 clustering_details.png - Detailed analysis (4 panels)")
