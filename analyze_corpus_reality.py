#!/usr/bin/env python3
"""
Realistic assessment of IS corpus data quality.
"""

import pandas as pd

# Load both versions
df_orig = pd.read_parquet('data/clean/is_corpus_all.parquet')
df_enrich = pd.read_parquet('data/clean/is_corpus_enriched.parquet')

print("📊 IS CORPUS DATA REALITY CHECK")
print("="*70)

print("\n🔍 OVERALL STATS:")
print(f"Total papers collected: {len(df_orig):,}")
print(f"Date range: {df_orig['year'].min()}-{df_orig['year'].max()}")

print("\n📝 ABSTRACT COVERAGE:")
orig_abstracts = df_orig['abstract'].notna().sum()
enrich_abstracts = df_enrich['abstract'].notna().sum()
print(f"Before enrichment: {orig_abstracts:,} ({orig_abstracts/len(df_orig)*100:.1f}%)")
print(f"After enrichment:  {enrich_abstracts:,} ({enrich_abstracts/len(df_enrich)*100:.1f}%)")
print(f"Improvement: +{enrich_abstracts - orig_abstracts} abstracts (disappointing!)")

print("\n📅 BY TIME PERIOD:")
periods = [
    (1800, 1999, "Pre-2000 (historical)"),
    (2000, 2009, "2000-2009"),
    (2010, 2015, "2010-2015"),
    (2016, 2020, "2016-2020"),
    (2021, 2025, "2021-2025")
]

for start, end, label in periods:
    subset = df_enrich[(df_enrich['year'] >= start) & (df_enrich['year'] <= end)]
    if len(subset) > 0:
        with_abs = subset['abstract'].notna().sum()
        print(f"{label:20s}: {len(subset):5,} papers, {with_abs:5,} abstracts ({with_abs/len(subset)*100:4.1f}%)")

print("\n📚 BY JOURNAL (2016+):")
df_recent = df_enrich[df_enrich['year'] >= 2016]
journal_stats = []
for journal in sorted(df_recent['journal'].unique()):
    subset = df_recent[df_recent['journal'] == journal]
    with_abs = subset['abstract'].notna().sum()
    journal_stats.append({
        'Journal': journal,
        'Papers': len(subset),
        'With Abstract': with_abs,
        'Coverage %': with_abs/len(subset)*100
    })

stats_df = pd.DataFrame(journal_stats).sort_values('Papers', ascending=False)
print(stats_df.to_string(index=False))

print("\n📊 CITATION DATA:")
print(f"Papers with cited_by_count (OpenAlex): {(df_enrich['cited_by_count'] > 0).sum():,} ({(df_enrich['cited_by_count'] > 0).sum()/len(df_enrich)*100:.1f}%)")
print(f"Papers with referenced_works (OpenAlex): {df_enrich['referenced_works'].apply(lambda x: len(x) > 0 if isinstance(x, list) else False).sum():,}")

# Check citation_dois
has_cites = df_enrich['citation_dois'].apply(lambda x: len(x) > 0 if isinstance(x, list) or isinstance(x, tuple) else False)
print(f"Papers with citation_dois (from enrichment): {has_cites.sum():,}")

print("\n🎯 USABLE CORPUS FOR ANALYSIS:")
df_2000 = df_enrich[df_enrich['year'] >= 2000]
df_2000_abs = df_2000[df_2000['abstract'].notna()]
print(f"Papers from 2000+: {len(df_2000):,}")
print(f"Papers from 2000+ with abstracts: {len(df_2000_abs):,} ({len(df_2000_abs)/len(df_2000)*100:.1f}%)")

df_2010 = df_enrich[df_enrich['year'] >= 2010]
df_2010_abs = df_2010[df_2010['abstract'].notna()]
print(f"\nPapers from 2010+: {len(df_2010):,}")
print(f"Papers from 2010+ with abstracts: {len(df_2010_abs):,} ({len(df_2010_abs)/len(df_2010)*100:.1f}%)")

df_2016 = df_enrich[df_enrich['year'] >= 2016]
df_2016_abs = df_2016[df_2016['abstract'].notna()]
print(f"\nPapers from 2016+: {len(df_2016):,}")
print(f"Papers from 2016+ with abstracts: {len(df_2016_abs):,} ({len(df_2016_abs)/len(df_2016)*100:.1f}%)")

print("\n💡 RECOMMENDATION:")
print("The enrichment didn't help much with abstracts (only +25).")
print("Crossref has very poor coverage for IS journals.")
print("\nBest approach:")
print("1. Use all 6,881 papers from 2000+ with abstracts (40.5% coverage)")
print("2. OR focus on 2010+ for better coverage")
print("3. Use OpenAlex cited_by_count for citation analysis")
print("4. Accept that ~60% of papers lack abstracts - this is the reality of the data")
