#!/usr/bin/env python3
"""
Quick test: Add citation data to a sample of the corpus
"""
import sys
import os
sys.path.append("../..")

import pandas as pd
from pathlib import Path
import json

# Create output directory if needed
Path("output").mkdir(exist_ok=True)

# Import the enricher
from enrich_ais_basket_openalex import OpenAlexEnricher, load_crossref_corpus

def test_citation_enrichment(sample_size=100):
    """Test enrichment with citations on a small sample."""
    
    print("="*60)
    print("Testing Citation Data Enrichment")
    print("="*60)
    
    # Load existing corpus
    df = pd.read_parquet("ais_basket_corpus_enriched.parquet")
    print(f"\nLoaded corpus: {len(df):,} documents")
    
    # Take a sample with DOIs
    sample = df[df['doi'].notna()].head(sample_size).copy()
    print(f"Sample size: {len(sample)} documents")
    
    # Convert to list of dicts (CrossRef format)
    articles = []
    for _, row in sample.iterrows():
        article = {
            "doi": row['doi'],
            "title": row.get('title', ''),
            "abstract": row.get('abstract', ''),
            "journal": row.get('journal', ''),
            "year": row.get('year', 2020),
            "authors": []
        }
        articles.append(article)
    
    # Enrich with OpenAlex (including citations)
    enricher = OpenAlexEnricher()
    enriched_articles = enricher.enrich_corpus(articles)
    
    # Convert to DataFrame
    enriched_df = pd.json_normalize(enriched_articles)
    
    # Check citation data
    if 'referenced_works' in enriched_df.columns:
        has_refs = enriched_df['referenced_works'].notna().sum()
        total_refs = enriched_df['referenced_works'].apply(lambda x: len(x) if isinstance(x, list) else 0).sum()
        print(f"\n✓ Citation data retrieved:")
        print(f"  Papers with references: {has_refs}/{len(enriched_df)}")
        print(f"  Total references: {total_refs:,}")
        print(f"  Avg refs per paper: {total_refs/len(enriched_df):.1f}")
    else:
        print("\n✗ No citation data in enriched corpus")
    
    # Save test sample
    outpath = Path("ais_basket_sample_with_citations.parquet")
    enriched_df.to_parquet(outpath)
    print(f"\n✓ Saved enriched sample to: {outpath}")
    
    return enriched_df

if __name__ == "__main__":
    test_citation_enrichment(sample_size=50)
