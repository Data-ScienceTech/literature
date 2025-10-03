#!/usr/bin/env python3
"""Quick check of enrichment results."""

import pandas as pd

df = pd.read_parquet('data/clean/is_corpus_enriched.parquet')

print("📊 ENRICHMENT RESULTS CHECK")
print("="*60)
print(f"Total papers: {len(df):,}")
print(f"With abstracts: {df['abstract'].notna().sum():,} ({df['abstract'].notna().sum()/len(df)*100:.1f}%)")
print(f"Papers 2000+: {(df['year'] >= 2000).sum():,}")
print(f"Papers 2000+ with abstract: {((df['year'] >= 2000) & df['abstract'].notna()).sum():,}")

# Check citation_dois
has_citations = df['citation_dois'].apply(lambda x: len(x) > 0 if isinstance(x, list) else False)
print(f"\nWith citation DOIs: {has_citations.sum():,} ({has_citations.sum()/len(df)*100:.1f}%)")

if has_citations.sum() > 0:
    avg_cites = df[has_citations]['citation_dois'].apply(len).mean()
    total_cites = df[has_citations]['citation_dois'].apply(len).sum()
    print(f"Avg citation DOIs per paper: {avg_cites:.1f}")
    print(f"Total unique citation DOIs collected: {total_cites:,}")

# Check what Crossref actually added
print(f"\n🔍 WHAT HAPPENED:")
print(f"According to logs:")
print(f"  - Added abstracts: 25 (only 12.2% success rate!)")
print(f"  - Added citations: 7,035 papers")
print(f"  - Failed lookups: 180")
print(f"\nThis suggests Crossref has very poor abstract coverage for IS journals")
print(f"but good citation/reference coverage!")
