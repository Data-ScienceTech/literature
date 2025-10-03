#!/usr/bin/env python3
"""
Create a focused IS corpus with high-quality journals only.
These journals have good abstract coverage (78-89%).
"""

import pandas as pd
import json

# Load full corpus
df = pd.read_parquet('data/clean/is_corpus_enriched.parquet')

print("🎯 CREATING FOCUSED HIGH-QUALITY CORPUS")
print("="*70)

# Define high-quality journals (with good abstract coverage >75%)
HIGH_QUALITY_JOURNALS = [
    'Information Systems Research',
    'MIS Quarterly',
    'Journal of the Association for Information Systems',
    'Information Systems Journal',
    'Journal of Management Information Systems',
    'Journal of Information Technology'
]

print("\n📚 Selected journals (top tier with >75% abstract coverage):")
for j in HIGH_QUALITY_JOURNALS:
    print(f"  • {j}")

# Filter to high-quality journals
df_hq = df[df['journal'].isin(HIGH_QUALITY_JOURNALS)].copy()

print(f"\n📊 FILTERING RESULTS:")
print(f"  Original corpus: {len(df):,} papers")
print(f"  High-quality subset: {len(df_hq):,} papers ({len(df_hq)/len(df)*100:.1f}%)")

# Show stats by time period
print(f"\n📅 BY TIME PERIOD (High-Quality Journals):")
periods = [
    (1800, 1999, "Pre-2000"),
    (2000, 2009, "2000-2009"),
    (2010, 2015, "2010-2015"),
    (2016, 2020, "2016-2020"),
    (2021, 2025, "2021-2025")
]

for start, end, label in periods:
    subset = df_hq[(df_hq['year'] >= start) & (df_hq['year'] <= end)]
    if len(subset) > 0:
        with_abs = subset['abstract'].notna().sum()
        print(f"  {label:12s}: {len(subset):5,} papers, {with_abs:5,} abstracts ({with_abs/len(subset)*100:5.1f}%)")

# Create focused datasets for different time ranges
datasets = {
    'is_corpus_hq_all.parquet': (df_hq, "All years"),
    'is_corpus_hq_2000+.parquet': (df_hq[df_hq['year'] >= 2000], "2000+"),
    'is_corpus_hq_2010+.parquet': (df_hq[df_hq['year'] >= 2010], "2010+"),
    'is_corpus_hq_2016+.parquet': (df_hq[df_hq['year'] >= 2016], "2016+")
}

print(f"\n💾 SAVING FOCUSED DATASETS:")
for filename, (data, label) in datasets.items():
    if len(data) > 0:
        with_abs = data['abstract'].notna().sum()
        output_path = f'data/clean/{filename}'
        data.to_parquet(output_path, index=False)
        print(f"  ✅ {filename:30s} {len(data):5,} papers, {with_abs:5,} abs ({with_abs/len(data)*100:5.1f}%)")

# Recommended dataset: 2000+ with abstracts
df_recommended = df_hq[(df_hq['year'] >= 2000) & df_hq['abstract'].notna()].copy()

print(f"\n🌟 RECOMMENDED DATASET FOR ANALYSIS:")
print(f"  File: is_corpus_hq_2000+.parquet (filtered to papers WITH abstracts)")
print(f"  Papers: {len(df_recommended):,}")
print(f"  Date range: {df_recommended['year'].min()}-{df_recommended['year'].max()}")
print(f"  Abstract coverage: 100% (by definition)")
print(f"  Citation coverage: {(df_recommended['cited_by_count'] > 0).sum():,} ({(df_recommended['cited_by_count'] > 0).sum()/len(df_recommended)*100:.1f}%)")

# Show journal distribution
print(f"\n📚 BY JOURNAL (2000+, with abstracts):")
summary = df_recommended.groupby('journal').size().sort_values(ascending=False)
print(summary.to_string())

# Save recommended dataset
df_recommended.to_parquet('data/clean/is_corpus_recommended.parquet', index=False)
print(f"\n💾 Saved recommended dataset: data/clean/is_corpus_recommended.parquet")

# Save metadata
metadata = {
    'total_papers': len(df_recommended),
    'papers_with_abstracts': len(df_recommended),
    'abstract_coverage_pct': 100.0,
    'papers_with_citations': int((df_recommended['cited_by_count'] > 0).sum()),
    'citation_coverage_pct': float((df_recommended['cited_by_count'] > 0).sum()/len(df_recommended)*100),
    'journals': HIGH_QUALITY_JOURNALS,
    'date_range': f"{df_recommended['year'].min()}-{df_recommended['year'].max()}",
    'timestamp': pd.Timestamp.now().isoformat(),
    'description': 'High-quality IS journals (>75% abstract coverage), 2000+, abstracts only'
}

with open('data/clean/recommended_corpus_metadata.json', 'w') as f:
    json.dump(metadata, f, indent=2)

print(f"\n🎯 NEXT STEPS:")
print(f"  1. Use is_corpus_recommended.parquet for analysis")
print(f"  2. Run: python run_is_corpus_analysis.py")
print(f"  3. This gives you {len(df_recommended):,} high-quality papers from top IS journals")
print(f"  4. 100% abstract coverage = better embedding quality!")

print(f"\n✨ QUALITY > QUANTITY")
print(f"  Better to analyze {len(df_recommended):,} papers with 100% abstracts")
print(f"  than {len(df):,} papers with only 38% abstracts")
