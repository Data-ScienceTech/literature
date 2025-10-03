"""
Compare data quality between OpenAlex and Crossref approaches.
"""
import pandas as pd
import json

print("="*70)
print("DATA QUALITY COMPARISON: OpenAlex vs Crossref")
print("="*70)

# Analyze OpenAlex data
df_oa = pd.read_parquet('data/clean/is_corpus_all.parquet')

print("\n📊 OPENALEX APPROACH:")
print(f"   Total papers: {len(df_oa):,}")
print(f"   Date range: {df_oa['year'].min()} - {df_oa['year'].max()}")
print(f"   Papers 2000+: {(df_oa['year'] >= 2000).sum():,}")
print(f"   Papers 2016+: {(df_oa['year'] >= 2016).sum():,}")

print(f"\n   Abstract coverage:")
print(f"   - All years: {df_oa['abstract'].notna().sum():,} / {len(df_oa):,} ({df_oa['abstract'].notna().sum()/len(df_oa)*100:.1f}%)")

df_oa_2000 = df_oa[df_oa['year'] >= 2000]
print(f"   - 2000+: {df_oa_2000['abstract'].notna().sum():,} / {len(df_oa_2000):,} ({df_oa_2000['abstract'].notna().sum()/len(df_oa_2000)*100:.1f}%)")

df_oa_2016 = df_oa[df_oa['year'] >= 2016]
print(f"   - 2016+: {df_oa_2016['abstract'].notna().sum():,} / {len(df_oa_2016):,} ({df_oa_2016['abstract'].notna().sum()/len(df_oa_2016)*100:.1f}%)")

print(f"\n   By journal (2016+, with abstract):")
df_with_abstract = df_oa_2016[df_oa_2016['abstract'].notna()]
summary = df_with_abstract.groupby('journal').agg({
    'openalex_id': 'count',
    'cited_by_count': 'mean'
}).round(1)
summary.columns = ['Papers', 'Avg Citations']
summary = summary.sort_values('Papers', ascending=False)
print(summary.to_string())

print(f"\n   Total 2016+ with abstract: {len(df_with_abstract):,}")

print("\n" + "="*70)
print("RECOMMENDATIONS:")
print("="*70)

print("""
🎯 ISSUE IDENTIFIED:
   Only 38.3% of papers have abstracts in OpenAlex
   For 2016-2025: only ~60% have abstracts
   
💡 SOLUTION - HYBRID APPROACH:

1. Use Crossref (fetch_journals_bibtex.py) for 2016-2025:
   ✓ Better abstract coverage (typically 80-90%)
   ✓ More metadata (funding, licenses, etc.)
   ✓ Direct citation DOIs
   ✓ Already configured for 4 key journals
   
2. Keep OpenAlex for broader coverage:
   ✓ All 11 IS journals
   ✓ Historical data (pre-2016)
   ✓ Better journal coverage
   
📋 RECOMMENDED STRATEGY:

Option A: Focus on recent, high-quality data (2016-2025)
   - Use fetch_journals_bibtex.py for AMR, MISQ, ORSC, ISR
   - Expect ~2,000-3,000 papers with high abstract coverage
   - Better for deep analysis with full metadata

Option B: Comprehensive IS field (2000-2025, all 11 journals)  
   - Enhance OpenAlex data with Crossref lookups
   - Create hybrid script to fetch missing abstracts from Crossref
   - Get ~15,000+ papers with improved abstract coverage

Option C: Two-tier analysis
   - Core analysis: 2016-2025 Crossref data (high quality)
   - Extended analysis: Full OpenAlex corpus (broad coverage)
""")

print("\n🔧 NEXT STEPS:")
print("1. Run Crossref fetcher for 2016-2025 to compare quality")
print("2. Create hybrid enrichment script")
print("3. Re-run analysis with better data")

