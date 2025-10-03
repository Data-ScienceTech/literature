"""
Check what citation/reference data we have in the IS corpus.
"""
import pandas as pd
import json

print("="*70)
print("CITATION DATA ANALYSIS - IS CORPUS")
print("="*70)

# Load the corpus
df = pd.read_parquet('data/clean/is_corpus_all.parquet')

print(f"\n📊 CITATION DATA COVERAGE:")
print(f"   Total papers: {len(df):,}")

# Check referenced_works field
has_refs = df['referenced_works'].notna() & (df['referenced_works'].apply(lambda x: len(x) > 0 if isinstance(x, list) else False))
print(f"\n   Papers with reference lists: {has_refs.sum():,} ({has_refs.sum()/len(df)*100:.1f}%)")

if has_refs.sum() > 0:
    # Sample some papers with references
    sample = df[has_refs].head(5)
    
    print(f"\n📋 SAMPLE PAPERS WITH REFERENCES:")
    for idx, row in sample.iterrows():
        refs = row['referenced_works']
        if isinstance(refs, list):
            print(f"\n   Paper: {row['title'][:60]}...")
            print(f"   Year: {row['year']}")
            print(f"   References: {len(refs)} cited works")
            print(f"   Sample refs: {refs[:3]}")

# Check cited_by_count
print(f"\n📈 CITATION COUNTS (from OpenAlex):")
print(f"   Papers with citation counts: {df['cited_by_count'].notna().sum():,}")
print(f"   Mean citations: {df['cited_by_count'].mean():.1f}")
print(f"   Median citations: {df['cited_by_count'].median():.1f}")
print(f"   Max citations: {df['cited_by_count'].max():.0f}")

# Most cited papers
print(f"\n🏆 TOP 5 MOST CITED PAPERS:")
top_cited = df.nlargest(5, 'cited_by_count')[['title', 'year', 'journal', 'cited_by_count']]
for idx, row in top_cited.iterrows():
    print(f"   {row['cited_by_count']:.0f} citations: {row['title'][:50]}... ({row['year']})")

print("\n" + "="*70)
print("WHAT DATA WE COLLECT:")
print("="*70)

print("""
✅ FROM OPENALEX (Already Have):
   1. cited_by_count - How many times each paper has been cited
   2. referenced_works - List of OpenAlex work IDs that this paper cites
      Example: ['https://openalex.org/W2164805534', ...]
   
✅ FROM CROSSREF (What We're Adding via Enrichment):
   1. abstract - Full text abstract (if missing)
   2. subjects/keywords - Topic classifications
   3. referenced_works - Citation DOIs merged with OpenAlex refs
      Example: ['10.1287/isre.2018.0802', '10.2307/41410412', ...]
   
🎯 CITATION NETWORK CAPABILITIES:

After enrichment, for EACH paper you'll have:
- Who cited it (cited_by_count)
- What it cites (referenced_works with DOIs)
- This enables:
  ✓ Citation network analysis
  ✓ Co-citation analysis
  ✓ Bibliographic coupling
  ✓ Reference Publication Year Spectroscopy (RPYS)
  ✓ Identify influential papers
  ✓ Track knowledge flows between research streams

📊 EXAMPLE USE CASES:
1. Build citation network for each research stream
2. Find "bridge papers" connecting different streams
3. Identify foundational papers (heavily cited, older)
4. Track how streams cite each other over time
5. Find emerging papers (recent, gaining citations)
""")

print("\n🔍 ENRICHMENT IMPACT:")
print("""
The enrichment script will:
1. Keep all OpenAlex citation data (cited_by_count, referenced_works)
2. Add Crossref citation DOIs to referenced_works
3. Merge and deduplicate citations from both sources
4. Result: More complete citation network

For papers missing abstracts, we get:
- Abstract text ✓
- Citation DOIs ✓  
- Keywords ✓
- Better metadata overall ✓
""")

print(f"\n💡 TIP: After enrichment completes, you can:")
print(f"   - Build co-citation networks")
print(f"   - Analyze citation patterns across research streams")
print(f"   - Track knowledge diffusion over time")
print(f"   - Identify seminal papers and emerging trends")

