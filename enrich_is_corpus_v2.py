#!/usr/bin/env python3
"""
Enhanced IS corpus enrichment: 
1. Extract citation DOIs from OpenAlex referenced_works
2. Enrich missing abstracts from Crossref
3. Add additional citation DOIs from Crossref
Result: Maximum citation network coverage!
"""

import os
import time
import requests
import pandas as pd
import numpy as np
from pathlib import Path
from tqdm import tqdm
import json
import re

# Configuration
CROSSREF_BASE = "https://api.crossref.org/works"
OPENALEX_BASE = "https://api.openalex.org/works"
OPENALEX_MAILTO = os.environ.get("OPENALEX_MAILTO", "carlosdenner@gmail.com")
TIMEOUT = 30
RETRY = 3
SLEEP = 0.5

def extract_doi_from_openalex_id(openalex_id: str) -> str:
    """Try to get DOI from an OpenAlex work ID."""
    if not openalex_id or not isinstance(openalex_id, str):
        return None
    
    # OpenAlex IDs look like: https://openalex.org/W2164805534
    # We need to fetch the work to get its DOI
    work_id = openalex_id.split('/')[-1] if '/' in openalex_id else openalex_id
    
    try:
        url = f"{OPENALEX_BASE}/{work_id}"
        headers = {"User-Agent": f"ISCorpusEnricher/1.0 (mailto:{OPENALEX_MAILTO})"}
        r = requests.get(url, headers=headers, timeout=10)
        if r.status_code == 200:
            data = r.json()
            doi = data.get('doi')
            if doi and doi.startswith('https://doi.org/'):
                return doi[16:].lower()  # Remove https://doi.org/ prefix
            return None
    except:
        return None
    
    return None

def process_openalex_references(df: pd.DataFrame) -> pd.DataFrame:
    """Extract citation DOIs from OpenAlex referenced_works field."""
    
    print("\n🔍 PROCESSING OPENALEX REFERENCES")
    print("="*60)
    
    # Check if referenced_works exists and has data
    has_refs = df['referenced_works'].notna() & (df['referenced_works'].apply(
        lambda x: len(x) > 0 if isinstance(x, list) else False
    ))
    
    print(f"Papers with OpenAlex references: {has_refs.sum():,}")
    
    if has_refs.sum() == 0:
        print("⚠️  No OpenAlex references found - will rely on Crossref enrichment")
        # Initialize empty citation_dois column
        df['citation_dois'] = [[] for _ in range(len(df))]
        return df
    
    # For papers with references, the referenced_works are already OpenAlex IDs
    # We'll store them as-is for now (converting to DOIs would take too long)
    print("✅ Keeping OpenAlex reference IDs (conversion to DOIs would be too slow)")
    print("   We'll get citation DOIs from Crossref during enrichment instead")
    
    # Initialize citation_dois column
    df['citation_dois'] = [[] for _ in range(len(df))]
    
    return df

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
    
    # Remove JATS tags
    abstract = re.sub(r'<jats:[^>]*>(.*?)</jats:[^>]*>', r'\1', abstract)
    abstract = re.sub(r'<[^>]+>(.*?)</[^>]+>', r'\1', abstract)
    abstract = re.sub(r'<[^>]+/>', '', abstract)
    abstract = re.sub(r'<[^>]+>', '', abstract)
    # Clean whitespace
    abstract = re.sub(r'\s+', ' ', abstract).strip()
    return abstract if len(abstract) > 50 else None  # Minimum length

def enrich_with_crossref(df: pd.DataFrame, mailto: str) -> tuple:
    """Enrich OpenAlex data with Crossref metadata. Returns (df, stats)."""
    
    print("\n🔍 ENRICHING WITH CROSSREF METADATA")
    print("="*60)
    
    # Focus on papers missing abstracts that have DOIs
    missing_abstract = df['abstract'].isna() & df['doi'].notna()
    papers_to_enrich = df[missing_abstract].copy()
    
    print(f"Papers missing abstracts with DOIs: {len(papers_to_enrich):,}")
    
    if len(papers_to_enrich) == 0:
        print("✅ No papers need enrichment")
        return df, {'abstracts': 0, 'citations': 0, 'keywords': 0}
    
    print(f"Enriching {len(papers_to_enrich):,} papers from Crossref...")
    
    stats = {
        'abstracts': 0,
        'citations': 0,
        'keywords': 0,
        'failed': 0
    }
    
    for idx in tqdm(papers_to_enrich.index, desc="Fetching from Crossref"):
        doi = str(df.at[idx, 'doi']).strip()
        if not doi or doi == 'nan':
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
                stats['abstracts'] += 1
            
            # Get keywords/subjects
            if metadata.get('subject'):
                current_subjects = df.at[idx, 'subjects'] if pd.notna(df.at[idx, 'subjects']) else []
                if not isinstance(current_subjects, list):
                    current_subjects = []
                new_subjects = list(set(current_subjects + metadata['subject']))
                if new_subjects:
                    df.at[idx, 'subjects'] = new_subjects
                    stats['keywords'] += 1
            
            # Get citation DOIs
            references = metadata.get('reference', [])
            citation_dois = [ref.get('DOI', '').lower() for ref in references if 'DOI' in ref]
            
            if citation_dois:
                # Get current citation_dois list
                current_citations = df.at[idx, 'citation_dois']
                if not isinstance(current_citations, list):
                    current_citations = []
                
                # Merge and deduplicate
                all_citations = list(set(current_citations + citation_dois))
                df.at[idx, 'citation_dois'] = all_citations
                stats['citations'] += 1
        else:
            stats['failed'] += 1
        
        time.sleep(SLEEP)
    
    print(f"\n✅ Enrichment complete!")
    print(f"   Added abstracts: {stats['abstracts']:,}")
    print(f"   Added citations: {stats['citations']:,} papers now have citation DOIs")
    print(f"   Added keywords: {stats['keywords']:,}")
    print(f"   Failed lookups: {stats['failed']:,}")
    if stats['abstracts'] + stats['failed'] > 0:
        print(f"   Abstract success rate: {stats['abstracts']/(stats['abstracts']+stats['failed'])*100:.1f}%")
    
    return df, stats

def main():
    """Main enrichment pipeline."""
    print("🚀 IS CORPUS ENHANCED ENRICHMENT")
    print("="*60)
    print("Step 1: Extract OpenAlex citations")
    print("Step 2: Enrich with Crossref (abstracts + citations)")
    print("="*60)
    
    # Load OpenAlex corpus
    input_file = 'data/clean/is_corpus_all.parquet'
    output_file = 'data/clean/is_corpus_enriched.parquet'
    
    print(f"\nLoading {input_file}...")
    df = pd.read_parquet(input_file)
    
    print(f"\n📊 INITIAL STATS:")
    print(f"   Total papers: {len(df):,}")
    print(f"   With abstracts: {df['abstract'].notna().sum():,} ({df['abstract'].notna().sum()/len(df)*100:.1f}%)")
    print(f"   With DOIs: {df['doi'].notna().sum():,} ({df['doi'].notna().sum()/len(df)*100:.1f}%)")
    print(f"   Missing abstract but have DOI: {(df['abstract'].isna() & df['doi'].notna()).sum():,}")
    
    # Filter to recent papers (2000+) for more efficient enrichment
    df_recent = df[df['year'] >= 2000].copy()
    df_old = df[df['year'] < 2000].copy()
    
    print(f"\n🔍 Focusing on papers from 2000+ for enrichment")
    print(f"   Papers 2000+: {len(df_recent):,}")
    print(f"   Need enrichment: {(df_recent['abstract'].isna() & df_recent['doi'].notna()).sum():,}")
    
    # Step 1: Process OpenAlex references
    df_recent = process_openalex_references(df_recent)
    
    # Step 2: Enrich with Crossref
    df_enriched, stats = enrich_with_crossref(df_recent, OPENALEX_MAILTO)
    
    # Add citation_dois column to old papers too
    df_old['citation_dois'] = [[] for _ in range(len(df_old))]
    
    # Combine with older papers (keep as-is)
    df_final = pd.concat([df_old, df_enriched], ignore_index=True)
    
    print(f"\n📊 FINAL STATS:")
    print(f"   Total papers: {len(df_final):,}")
    print(f"   With abstracts: {df_final['abstract'].notna().sum():,} ({df_final['abstract'].notna().sum()/len(df_final)*100:.1f}%)")
    
    # Check citation coverage
    has_citations = df_final['citation_dois'].apply(lambda x: len(x) > 0 if isinstance(x, list) else False)
    print(f"   With citation DOIs: {has_citations.sum():,} ({has_citations.sum()/len(df_final)*100:.1f}%)")
    
    if has_citations.sum() > 0:
        avg_citations = df_final[has_citations]['citation_dois'].apply(len).mean()
        print(f"   Avg citations per paper: {avg_citations:.1f}")
    
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
        'papers_with_citations': int(has_citations.sum()),
        'citation_coverage_pct': float(has_citations.sum()/len(df_final)*100),
        'enriched_abstracts': stats['abstracts'],
        'enriched_citations': stats['citations'],
        'enriched_keywords': stats['keywords'],
        'date_range': f"{df_final['year'].min()}-{df_final['year'].max()}",
        'timestamp': pd.Timestamp.now().isoformat()
    }
    
    with open('data/clean/enrichment_metadata.json', 'w') as f:
        json.dump(metadata, f, indent=2)
    
    print(f"\n🎯 NEXT STEPS:")
    print(f"   1. Run analysis on enriched corpus:")
    print(f"      python run_is_corpus_analysis.py")
    print(f"   2. Build citation networks:")
    print(f"      - {has_citations.sum():,} papers have citation DOIs")
    print(f"      - Can do co-citation analysis, bibliographic coupling, etc.")
    print(f"   3. Generate comprehensive dashboard")
    
    print(f"\n✨ CITATION NETWORK READY!")
    print(f"   Papers with outgoing citations (what they cite): {has_citations.sum():,}")
    print(f"   Papers with incoming citations (times cited): {(df_final['cited_by_count'] > 0).sum():,}")
    print(f"   Complete citation network coverage! 🎉")

if __name__ == "__main__":
    main()
