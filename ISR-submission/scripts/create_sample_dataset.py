#!/usr/bin/env python3
"""
Create a sample test dataset for validating the clustering pipeline.
Extracts 200 random papers from the full corpus for quick testing.
"""

import pandas as pd
import sys
from pathlib import Path

def create_sample():
    # Read the full clustering results
    full_corpus_dir = Path("c:/Users/carlo/Dropbox/literature_analyzer_v2/literature/data/clean/hybrid_streams_full_corpus")
    
    if not full_corpus_dir.exists():
        print(f"Error: {full_corpus_dir} not found")
        sys.exit(1)
    
    # Load doc assignments
    doc_file = full_corpus_dir / "doc_assignments.csv"
    if not doc_file.exists():
        print(f"Error: {doc_file} not found")
        sys.exit(1)
        
    print(f"Loading {doc_file}...")
    df = pd.read_csv(doc_file)
    print(f"Loaded {len(df)} papers")
    
    # Sample 200 papers (stratified by L1 cluster to maintain diversity)
    sample_size = 200
    sample_df = df.groupby('L1', group_keys=False).apply(
        lambda x: x.sample(n=min(len(x), sample_size // df['L1'].nunique() + 5), random_state=42)
    ).reset_index(drop=True)
    
    # Trim to exactly 200
    sample_df = sample_df.head(sample_size)
    
    print(f"\nCreated sample with {len(sample_df)} papers")
    print(f"L1 cluster distribution:\n{sample_df['L1'].value_counts().sort_index()}")
    
    # Save to ISR-submission/data
    output_dir = Path("c:/Users/carlo/Dropbox/literature_analyzer_v2/literature/ISR-submission/data")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    output_file = output_dir / "sample_test.csv"
    sample_df.to_csv(output_file, index=False)
    print(f"\nSaved sample to: {output_file}")
    print(f"File size: {output_file.stat().st_size / 1024:.1f} KB")
    
    return sample_df

if __name__ == "__main__":
    create_sample()
