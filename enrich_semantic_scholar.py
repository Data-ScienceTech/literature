#!/usr/bin/env python3
"""
Enrich IS corpus using Semantic Scholar API.
Semantic Scholar often has better abstract coverage than OpenAlex/Crossref.

API Docs: https://api.semanticscholar.org/api-docs/
Rate limit: 100 requests/second (with API key), 1/second without
"""

import os
import time
import requests
import pandas as pd
import numpy as np
from pathlib import Path
from tqdm import tqdm
import json
from typing import Optional, Dict, List

# Configuration
S2_BASE = "https://api.semanticscholar.org/graph/v1"
S2_API_KEY = os.environ.get("S2_API_KEY", None)  # Optional but recommended
TIMEOUT = 30
RETRY = 3
SLEEP = 1.0 if not S2_API_KEY else 0.01  # 1/sec without key, 100/sec with key

# Fields to request from Semantic Scholar
S2_FIELDS = [
    "paperId",
    "externalIds", 
    "title",
    "abstract",
    "year",
    "authors",
    "citationCount",
    "referenceCount",
    "influentialCitationCount",
    "fieldsOfStudy",
    "s2FieldsOfStudy",
    "publicationTypes",
    "journal",
    "references",  # Get citation DOIs
    "citations"    # Get papers that cite this one
]

def get_s2_paper_by_doi(doi: str) -> Optional[Dict]:
    """Fetch paper metadata from Semantic Scholar using DOI."""
    if not doi or pd.isna(doi):
        return None
    
    # Clean DOI
    doi = str(doi).strip().lower()
    if doi.startswith('https://doi.org/'):
        doi = doi[16:]
    
    url = f"{S2_BASE}/paper/DOI:{doi}"
    params = {"fields": ",".join(S2_FIELDS)}
    headers = {}
    if S2_API_KEY:
        headers["x-api-key"] = S2_API_KEY
    
    for attempt in range(RETRY):
        try:
            r = requests.get(url, params=params, headers=headers, timeout=TIMEOUT)
            
            if r.status_code == 200:
                return r.json()
            elif r.status_code == 404:
                return None  # Paper not found in S2
            elif r.status_code == 429:
                # Rate limited - wait longer
                wait_time = SLEEP * (2 ** attempt) * 5
                print(f"\n⚠️  Rate limited, waiting {wait_time:.1f}s...")
                time.sleep(wait_time)
            else:
                time.sleep(SLEEP * (attempt + 1))
                
        except Exception as e:
            if attempt == RETRY - 1:
                print(f"\n❌ Error fetching {doi}: {e}")
            time.sleep(SLEEP * (attempt + 1))
    
    return None

def extract_citation_info(s2_data: Dict) -> Dict:
    """Extract citation and reference information from S2 data."""
    info = {
        'reference_count': s2_data.get('referenceCount', 0),
        'citation_count': s2_data.get('citationCount', 0),
        'influential_citation_count': s2_data.get('influentialCitationCount', 0),
        'reference_dois': [],
        'citing_dois': []
    }
    
    # Extract DOIs from references (what this paper cites)
    references = s2_data.get('references', [])
    if references:
        for ref in references[:100]:  # Limit to first 100 to avoid huge lists
            if ref and isinstance(ref, dict):
                ext_ids = ref.get('externalIds', {})
                if ext_ids and isinstance(ext_ids, dict):
                    doi = ext_ids.get('DOI')
                    if doi:
                        info['reference_dois'].append(doi.lower())
    
    # Extract DOIs from citations (papers that cite this one)
    citations = s2_data.get('citations', [])
    if citations:
        for cit in citations[:100]:  # Limit to first 100
            if cit and isinstance(cit, dict):
                ext_ids = cit.get('externalIds', {})
                if ext_ids and isinstance(ext_ids, dict):
                    doi = ext_ids.get('DOI')
                    if doi:
                        info['citing_dois'].append(doi.lower())
    
    return info

def enrich_with_semantic_scholar(df: pd.DataFrame) -> tuple:
    """Enrich corpus with Semantic Scholar data. Returns (df, stats)."""
    
    print("\n🔍 ENRICHING WITH SEMANTIC SCHOLAR API")
    print("="*70)
    
    # Focus on papers missing abstracts that have DOIs
    missing_abstract = df['abstract'].isna() & df['doi'].notna()
    papers_to_enrich = df[missing_abstract].copy()
    
    print(f"Papers missing abstracts with DOIs: {len(papers_to_enrich):,}")
    
    if len(papers_to_enrich) == 0:
        print("✅ No papers need enrichment")
        return df, {'abstracts': 0, 'citations': 0, 'fields': 0}
    
    # Check API key status
    if S2_API_KEY:
        print(f"✅ Using S2 API key (100 requests/sec)")
    else:
        print(f"⚠️  No S2_API_KEY - limited to 1 request/sec")
        print(f"   Set env var S2_API_KEY to speed up (get free key at semanticscholar.org)")
    
    print(f"\nEnriching {len(papers_to_enrich):,} papers from Semantic Scholar...")
    estimated_time = len(papers_to_enrich) * SLEEP
    print(f"Estimated time: {estimated_time/60:.1f} minutes")
    
    stats = {
        'abstracts': 0,
        'citations': 0,
        'references': 0,
        'fields': 0,
        'not_found': 0,
        'failed': 0
    }
    
    # Initialize new columns if they don't exist
    if 's2_paper_id' not in df.columns:
        df['s2_paper_id'] = None
    if 's2_citation_count' not in df.columns:
        df['s2_citation_count'] = 0
    if 's2_reference_count' not in df.columns:
        df['s2_reference_count'] = 0
    if 's2_influential_citations' not in df.columns:
        df['s2_influential_citations'] = 0
    if 's2_fields' not in df.columns:
        df['s2_fields'] = [[] for _ in range(len(df))]
    if 'reference_dois' not in df.columns:
        df['reference_dois'] = [[] for _ in range(len(df))]
    if 'citing_dois' not in df.columns:
        df['citing_dois'] = [[] for _ in range(len(df))]
    
    for idx in tqdm(papers_to_enrich.index, desc="Fetching from Semantic Scholar"):
        doi = df.at[idx, 'doi']
        
        s2_data = get_s2_paper_by_doi(doi)
        
        if s2_data:
            # Store S2 paper ID
            if s2_data.get('paperId'):
                df.at[idx, 's2_paper_id'] = s2_data['paperId']
            
            # Get abstract
            abstract = s2_data.get('abstract')
            if abstract and isinstance(abstract, str) and len(abstract) > 50:
                df.at[idx, 'abstract'] = abstract
                stats['abstracts'] += 1
            
            # Get citation metrics
            if s2_data.get('citationCount'):
                df.at[idx, 's2_citation_count'] = s2_data['citationCount']
                stats['citations'] += 1
            
            if s2_data.get('referenceCount'):
                df.at[idx, 's2_reference_count'] = s2_data['referenceCount']
            
            if s2_data.get('influentialCitationCount'):
                df.at[idx, 's2_influential_citations'] = s2_data['influentialCitationCount']
            
            # Get fields of study
            fields = []
            if s2_data.get('s2FieldsOfStudy'):
                fields = [f.get('category', '') for f in s2_data['s2FieldsOfStudy'] if f]
            elif s2_data.get('fieldsOfStudy'):
                fields = s2_data['fieldsOfStudy']
            
            if fields:
                df.at[idx, 's2_fields'] = fields
                stats['fields'] += 1
            
            # Get citation network data
            cit_info = extract_citation_info(s2_data)
            if cit_info['reference_dois']:
                df.at[idx, 'reference_dois'] = cit_info['reference_dois']
                stats['references'] += 1
            if cit_info['citing_dois']:
                df.at[idx, 'citing_dois'] = cit_info['citing_dois']
        
        elif s2_data is None:
            stats['not_found'] += 1
        else:
            stats['failed'] += 1
        
        time.sleep(SLEEP)
    
    print(f"\n✅ Semantic Scholar enrichment complete!")
    print(f"   Added abstracts: {stats['abstracts']:,}")
    print(f"   Added citation counts: {stats['citations']:,}")
    print(f"   Added reference DOIs: {stats['references']:,}")
    print(f"   Added fields of study: {stats['fields']:,}")
    print(f"   Not found in S2: {stats['not_found']:,}")
    print(f"   Failed lookups: {stats['failed']:,}")
    
    if stats['abstracts'] + stats['not_found'] + stats['failed'] > 0:
        total_attempted = stats['abstracts'] + stats['not_found'] + stats['failed']
        success_rate = stats['abstracts'] / total_attempted * 100
        print(f"   Abstract success rate: {success_rate:.1f}%")
    
    return df, stats

def main():
    """Main enrichment pipeline."""
    print("🚀 SEMANTIC SCHOLAR ENRICHMENT")
    print("="*70)
    
    # Load current corpus
    input_file = 'data/clean/is_corpus_enriched.parquet'
    output_file = 'data/clean/is_corpus_semantic_scholar.parquet'
    
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
    
    # Enrich with Semantic Scholar
    df_enriched, stats = enrich_with_semantic_scholar(df_recent)
    
    # Initialize columns for old papers
    for col in ['s2_paper_id', 's2_citation_count', 's2_reference_count', 
                's2_influential_citations', 's2_fields', 'reference_dois', 'citing_dois']:
        if col not in df_old.columns:
            if col.endswith('_count') or col == 's2_influential_citations':
                df_old[col] = 0
            elif col.endswith('s') and col != 's2_paper_id':
                df_old[col] = [[] for _ in range(len(df_old))]
            else:
                df_old[col] = None
    
    # Combine with older papers
    df_final = pd.concat([df_old, df_enriched], ignore_index=True)
    
    print(f"\n📊 FINAL STATS:")
    print(f"   Total papers: {len(df_final):,}")
    print(f"   With abstracts: {df_final['abstract'].notna().sum():,} ({df_final['abstract'].notna().sum()/len(df_final)*100:.1f}%)")
    
    # Check citation network coverage
    has_refs = df_final['reference_dois'].apply(lambda x: len(x) > 0 if isinstance(x, list) else False)
    has_citing = df_final['citing_dois'].apply(lambda x: len(x) > 0 if isinstance(x, list) else False)
    
    print(f"\n📊 CITATION NETWORK:")
    print(f"   Papers with reference DOIs: {has_refs.sum():,} ({has_refs.sum()/len(df_final)*100:.1f}%)")
    print(f"   Papers with citing DOIs: {has_citing.sum():,} ({has_citing.sum()/len(df_final)*100:.1f}%)")
    
    if has_refs.sum() > 0:
        avg_refs = df_final[has_refs]['reference_dois'].apply(len).mean()
        total_refs = df_final[has_refs]['reference_dois'].apply(len).sum()
        print(f"   Avg references per paper: {avg_refs:.1f}")
        print(f"   Total reference DOIs: {total_refs:,}")
    
    # Show improvement for 2000+
    df_final_recent = df_final[df_final['year'] >= 2000]
    before_count = df_recent['abstract'].notna().sum()
    after_count = df_final_recent['abstract'].notna().sum()
    
    print(f"\n   Papers 2000+ with abstracts:")
    print(f"   Before: {before_count:,} ({before_count/len(df_recent)*100:.1f}%)")
    print(f"   After: {after_count:,} ({after_count/len(df_final_recent)*100:.1f}%)")
    print(f"   Improvement: +{after_count - before_count:,} abstracts")
    
    # Show by journal (2016+)
    print(f"\n📚 By journal (2016+, with abstract):")
    df_2016 = df_final[df_final['year'] >= 2016]
    summary = df_2016[df_2016['abstract'].notna()].groupby('journal').size().sort_values(ascending=False)
    print(summary.to_string())
    
    # Save enriched corpus
    df_final.to_parquet(output_file, index=False)
    print(f"\n💾 Saved S2-enriched corpus to {output_file}")
    
    # Save metadata
    metadata = {
        'total_papers': len(df_final),
        'papers_with_abstracts': int(df_final['abstract'].notna().sum()),
        'abstract_coverage_pct': float(df_final['abstract'].notna().sum()/len(df_final)*100),
        'papers_with_references': int(has_refs.sum()),
        'papers_with_citations': int(has_citing.sum()),
        'enriched_abstracts': stats['abstracts'],
        'enriched_references': stats['references'],
        'enriched_fields': stats['fields'],
        'date_range': f"{df_final['year'].min()}-{df_final['year'].max()}",
        'timestamp': pd.Timestamp.now().isoformat(),
        'source': 'Semantic Scholar API'
    }
    
    with open('data/clean/s2_enrichment_metadata.json', 'w') as f:
        json.dump(metadata, f, indent=2)
    
    print(f"\n🎯 NEXT STEPS:")
    print(f"   1. Check if we got significant improvement")
    print(f"   2. If yes, run analysis: python run_is_corpus_analysis.py")
    print(f"   3. Build citation networks with reference_dois and citing_dois")
    print(f"   4. Analyze research fields with s2_fields")
    
    print(f"\n✨ ENRICHMENT COMPLETE!")

if __name__ == "__main__":
    main()
