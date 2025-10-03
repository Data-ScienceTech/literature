#!/usr/bin/env python3
"""
Hybrid IS corpus enrichment: Take OpenAlex data and enrich with Crossref metadata
to maximize abstract coverage and metadata quality.
"""

import os
import time
import requests
import pandas as pd
import numpy as np
from pathlib import Path
from tqdm import tqdm
import json

# Configuration
CROSSREF_BASE = "https://api.crossref.org/works"
OPENALEX_MAILTO = os.environ.get("OPENALEX_MAILTO", "carlosdenner@gmail.com")
TIMEOUT = 30
RETRY = 3
SLEEP = 0.5

def get_crossref_metadata(doi: str, mailto: str) -> dict:
    """Fetch metadata from Crossref for a given DOI."""
    url = f"{CROSSREF_BASE}/{doi}"
    headers = {
        "User-Agent": f"ISCorpusEnricher/1.0 (mailto:{mailto})",
        "Accept": "application/json"
    }
    
    for attempt in range(RETRY):
        try:
            r = requests.get(url, headers=headers, timeout=TIMEOUT)
            if r.status_code == 200:
                return r.json().get("message", {})
            elif r.status_code in (404, 400):
                return {}  # DOI not found
            time.sleep(SLEEP * (attempt + 1))
        except Exception:
            time.sleep(SLEEP * (attempt + 1))
    
    return {}

def clean_abstract(abstract):
    """Clean abstract text from JATS tags."""
    if not abstract or not isinstance(abstract, str):
        return None
    
    import re
    # Remove JATS tags
    abstract = re.sub(r'<jats:[^>]*>(.*?)</jats:[^>]*>', r'\1', abstract)
    abstract = re.sub(r'<[^>]+>(.*?)</[^>]+>', r'\1', abstract)
    abstract = re.sub(r'<[^>]+/>', '', abstract)
    abstract = re.sub(r'<[^>]+>', '', abstract)
    # Clean whitespace
    abstract = re.sub(r'\s+', ' ', abstract).strip()
    return abstract if len(abstract) > 50 else None  # Minimum length

def enrich_with_crossref(df: pd.DataFrame, mailto: str) -> tuple:
    """Enrich OpenAlex data with Crossref metadata. Returns (df, enriched_count)."""
    
    print("\n🔍 ENRICHING WITH CROSSREF METADATA")
    print("="*60)
    
    # Focus on papers missing abstracts that have DOIs
    missing_abstract = df['abstract'].isna() & df['doi'].notna()
    papers_to_enrich = df[missing_abstract].copy()
    
    print(f"Papers missing abstracts with DOIs: {len(papers_to_enrich):,}")
    
    if len(papers_to_enrich) == 0:
        print("✅ No papers need enrichment")
        return df, 0
    
    # Sample for testing
    print(f"Enriching {len(papers_to_enrich):,} papers from Crossref...")
    
    enriched_count = 0
    failed_count = 0
    
    for idx in tqdm(papers_to_enrich.index, desc="Fetching from Crossref"):
        doi = df.at[idx, 'doi']
        if not doi:
            continue
        
        # Fetch Crossref metadata
        metadata = get_crossref_metadata(doi, mailto)
        
        if metadata:
            # Get abstract
            abstract = metadata.get('abstract')
            if isinstance(abstract, dict):
                abstract = abstract.get('value', '')
            
            abstract = clean_abstract(abstract)
            
            if abstract:
                df.at[idx, 'abstract'] = abstract
                enriched_count += 1
            
            # Also enrich other fields
            if metadata.get('subject'):
                df.at[idx, 'subjects'] = metadata['subject']
            
            # Get references/citations
            references = metadata.get('reference', [])
            citation_dois = [ref.get('DOI', '').lower() for ref in references if 'DOI' in ref]
            if citation_dois:
                # Add to existing referenced_works if it's a list, otherwise replace
                current_refs = df.at[idx, 'referenced_works']
                if isinstance(current_refs, list):
                    # Merge with existing references
                    all_refs = list(set(current_refs + citation_dois))
                    df.at[idx, 'referenced_works'] = all_refs
                else:
                    df.at[idx, 'referenced_works'] = citation_dois
        else:
            failed_count += 1
        
        time.sleep(SLEEP)
    
    print(f"\n✅ Enrichment complete!")
    print(f"   Added abstracts: {enriched_count:,}")
    print(f"   Failed lookups: {failed_count:,}")
    print(f"   Success rate: {enriched_count/(enriched_count+failed_count)*100:.1f}%")
    
    return df, enriched_count

def main():
    """Main enrichment pipeline."""
    print("🚀 IS CORPUS ENRICHMENT WITH CROSSREF")
    print("="*60)
    
    # Load OpenAlex corpus
    input_file = 'data/clean/is_corpus_all.parquet'
    output_file = 'data/clean/is_corpus_enriched.parquet'
    
    print(f"Loading {input_file}...")
    df = pd.read_parquet(input_file)
    
    print(f"\n📊 INITIAL STATS:")
    print(f"   Total papers: {len(df):,}")
    print(f"   With abstracts: {df['abstract'].notna().sum():,} ({df['abstract'].notna().sum()/len(df)*100:.1f}%)")
    print(f"   With DOIs: {df['doi'].notna().sum():,} ({df['doi'].notna().sum()/len(df)*100:.1f}%)")
    print(f"   Missing abstract but have DOI: {(df['abstract'].isna() & df['doi'].notna()).sum():,}")
    
    # Filter to recent papers (2000+) for more efficient enrichment
    df_recent = df[df['year'] >= 2000].copy()
    print(f"\n🔍 Focusing on papers from 2000+ for enrichment")
    print(f"   Papers 2000+: {len(df_recent):,}")
    print(f"   Need enrichment: {(df_recent['abstract'].isna() & df_recent['doi'].notna()).sum():,}")
    
    # Enrich with Crossref
    df_enriched, enriched_count = enrich_with_crossref(df_recent, OPENALEX_MAILTO)
    
    # Combine with older papers (keep as-is)
    df_old = df[df['year'] < 2000]
    df_final = pd.concat([df_old, df_enriched], ignore_index=True)
    
    print(f"\n📊 FINAL STATS:")
    print(f"   Total papers: {len(df_final):,}")
    print(f"   With abstracts: {df_final['abstract'].notna().sum():,} ({df_final['abstract'].notna().sum()/len(df_final)*100:.1f}%)")
    
    # Show improvement for 2000+
    df_final_recent = df_final[df_final['year'] >= 2000]
    print(f"\n   Papers 2000+ with abstracts:")
    print(f"   Before: {df_recent['abstract'].notna().sum():,} ({df_recent['abstract'].notna().sum()/len(df_recent)*100:.1f}%)")
    print(f"   After: {df_final_recent['abstract'].notna().sum():,} ({df_final_recent['abstract'].notna().sum()/len(df_final_recent)*100:.1f}%)")
    print(f"   Improvement: +{df_final_recent['abstract'].notna().sum() - df_recent['abstract'].notna().sum():,} abstracts")
    
    # Show by journal
    print(f"\n📚 By journal (2016+, with abstract):")
    df_2016 = df_final[df_final['year'] >= 2016]
    summary = df_2016[df_2016['abstract'].notna()].groupby('journal').size().sort_values(ascending=False)
    print(summary.to_string())
    
    # Save enriched corpus
    df_final.to_parquet(output_file, index=False)
    print(f"\n💾 Saved enriched corpus to {output_file}")
    
    # Save metadata
    metadata = {
        'total_papers': len(df_final),
        'papers_with_abstracts': int(df_final['abstract'].notna().sum()),
        'abstract_coverage_pct': float(df_final['abstract'].notna().sum()/len(df_final)*100),
        'enriched_from_crossref': enriched_count,
        'date_range': f"{df_final['year'].min()}-{df_final['year'].max()}",
        'timestamp': pd.Timestamp.now().isoformat()
    }
    
    with open('data/clean/enrichment_metadata.json', 'w') as f:
        json.dump(metadata, f, indent=2)
    
    print(f"\n🎯 NEXT STEPS:")
    print(f"   1. Run analysis on enriched corpus: python run_is_corpus_analysis.py")
    print(f"   2. Update script to use 'data/clean/is_corpus_enriched.parquet'")
    print(f"   3. Enjoy higher quality analysis with more abstracts!")

if __name__ == "__main__":
    main()
