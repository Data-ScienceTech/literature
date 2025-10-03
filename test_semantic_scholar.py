#!/usr/bin/env python3
"""
Test Semantic Scholar API on a small sample to check coverage.
"""

import requests
import pandas as pd

# Test with 10 papers that are missing abstracts
df = pd.read_parquet('data/clean/is_corpus_enriched.parquet')
missing_abs = df[(df['abstract'].isna()) & (df['doi'].notna()) & (df['year'] >= 2016)]

print("🧪 TESTING SEMANTIC SCHOLAR COVERAGE")
print("="*60)
print(f"Total papers missing abstracts (2016+): {len(missing_abs):,}")

# Sample 10 random papers
sample = missing_abs.sample(min(10, len(missing_abs)))

print(f"\nTesting with {len(sample)} random papers...")
print("\nResults:")
print("-"*60)

found_count = 0
abstract_count = 0

for idx, row in sample.iterrows():
    doi = row['doi']
    title = row['title'][:50] + "..." if len(row['title']) > 50 else row['title']
    
    url = f"https://api.semanticscholar.org/graph/v1/paper/DOI:{doi}"
    params = {"fields": "paperId,title,abstract,year"}
    
    try:
        r = requests.get(url, params=params, timeout=10)
        if r.status_code == 200:
            data = r.json()
            found_count += 1
            
            has_abstract = bool(data.get('abstract'))
            if has_abstract:
                abstract_count += 1
                status = "✅ HAS ABSTRACT"
            else:
                status = "❌ NO ABSTRACT"
            
            print(f"{status}: {title}")
            print(f"   Year: {row['year']}, Journal: {row['journal']}")
        else:
            print(f"❌ NOT IN S2: {title}")
            print(f"   Status: {r.status_code}")
    except Exception as e:
        print(f"❌ ERROR: {title}")
        print(f"   {e}")
    
    print()

print("="*60)
print(f"RESULTS:")
print(f"  Found in S2: {found_count}/{len(sample)} ({found_count/len(sample)*100:.1f}%)")
print(f"  Have abstracts: {abstract_count}/{len(sample)} ({abstract_count/len(sample)*100:.1f}%)")

if abstract_count > 0:
    print(f"\n✨ Semantic Scholar looks promising!")
    print(f"   {abstract_count/len(sample)*100:.1f}% success rate on this sample")
    print(f"\n🚀 Ready to run full enrichment:")
    print(f"   python enrich_semantic_scholar.py")
    print(f"\n💡 OPTIONAL: Get free API key for faster processing (100 req/sec vs 1 req/sec)")
    print(f"   1. Go to: https://www.semanticscholar.org/product/api#api-key")
    print(f"   2. Sign up and get API key")
    print(f"   3. Set env var: $env:S2_API_KEY = 'your-key-here'")
else:
    print(f"\n⚠️  Semantic Scholar doesn't have better coverage for this sample")
    print(f"   May not be worth the full enrichment")
