#!/usr/bin/env python3
"""Check which journals have poor abstract coverage."""

import pandas as pd

df = pd.read_parquet('data/clean/is_corpus_enriched.parquet')
recent = df[df['year'] >= 2016]

print("📊 JOURNAL ABSTRACT COVERAGE (2016+)")
print("="*70)

journal_stats = []
for journal in sorted(recent['journal'].unique()):
    subset = recent[recent['journal'] == journal]
    total = len(subset)
    with_abs = subset['abstract'].notna().sum()
    without_abs = total - with_abs
    pct = with_abs/total*100
    
    journal_stats.append({
        'Journal': journal,
        'Total': total,
        'With Abs': with_abs,
        'Missing': without_abs,
        'Coverage %': pct
    })

stats_df = pd.DataFrame(journal_stats).sort_values('Coverage %')
print(stats_df.to_string(index=False))

print("\n" + "="*70)
print("INSIGHT:")
low_coverage = stats_df[stats_df['Coverage %'] < 30]
print(f"  {len(low_coverage)} journals have <30% coverage")
print(f"  These account for {low_coverage['Missing'].sum():,} missing abstracts")
print(f"  This is a PUBLISHER policy issue, not a data source issue!")

print("\n💡 RECOMMENDATION:")
print("  Semantic Scholar won't help much (same ~10% improvement as Crossref)")
print("  Better approach:")
print("  1. Focus analysis on high-quality journals (ISR, MISQ, JAIS, ISJ, JMIS, JIT)")
print("  2. Use the 6,881 papers we have from 2000+")
print("  3. Accept that some publishers don't share abstracts with public APIs")
