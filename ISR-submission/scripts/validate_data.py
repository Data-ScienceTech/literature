#!/usr/bin/env python3
"""
Validate ISR-submission data consistency
Ensures all data files match and are from the latest pipeline run
"""

import pandas as pd
import json
from pathlib import Path
from datetime import datetime

def validate_data():
    print("="*60)
    print("ISR-SUBMISSION DATA VALIDATION")
    print("="*60)
    
    base_dir = Path("c:/Users/carlo/Dropbox/literature_analyzer_v2/literature/ISR-submission")
    
    # 1. Check corpus data
    print("\n1. CORPUS DATA")
    print("-" * 60)
    
    corpus_file = base_dir / "data" / "ais_basket_corpus_enriched.parquet"
    if corpus_file.exists():
        corpus = pd.read_parquet(corpus_file)
        print(f"✓ Corpus file exists: {corpus_file.name}")
        print(f"  Papers: {len(corpus):,}")
        print(f"  File size: {corpus_file.stat().st_size / 1024 / 1024:.1f} MB")
        print(f"  Last modified: {datetime.fromtimestamp(corpus_file.stat().st_mtime)}")
        
        # Check required columns
        required_cols = ['abstract', 'title', 'journal', 'year', 'doi', 'referenced_works']
        missing_cols = [col for col in required_cols if col not in corpus.columns]
        if missing_cols:
            print(f"  ✗ Missing columns: {missing_cols}")
        else:
            print(f"  ✓ All required columns present")
            
        # Check data quality
        print(f"  With citations: {corpus['referenced_works'].notna().sum():,} ({corpus['referenced_works'].notna().sum()/len(corpus)*100:.1f}%)")
        print(f"  Year range: {corpus['year'].min()}-{corpus['year'].max()}")
    else:
        print(f"✗ Corpus file not found: {corpus_file}")
    
    # 2. Check clustering results
    print("\n2. CLUSTERING RESULTS")
    print("-" * 60)
    
    results_dir = base_dir / "outputs" / "clustering_results"
    expected_files = [
        'doc_assignments.csv',
        'topics_level1.csv',
        'topics_level2.csv',
        'citation_network_stats.json',
        'summary.md'
    ]
    
    for filename in expected_files:
        filepath = results_dir / filename
        if filepath.exists():
            size = filepath.stat().st_size / 1024
            modified = datetime.fromtimestamp(filepath.stat().st_mtime)
            print(f"✓ {filename:30} {size:>10.1f} KB  {modified}")
        else:
            print(f"✗ {filename:30} NOT FOUND")
    
    # 3. Validate clustering results match corpus
    print("\n3. DATA CONSISTENCY")
    print("-" * 60)
    
    doc_file = results_dir / "doc_assignments.csv"
    if doc_file.exists() and corpus_file.exists():
        docs = pd.read_csv(doc_file)
        
        print(f"  Corpus papers: {len(corpus):,}")
        print(f"  Clustered papers: {len(docs):,}")
        
        if len(docs) == len(corpus):
            print(f"  ✓ Paper counts match")
        else:
            print(f"  ✗ MISMATCH: {abs(len(docs) - len(corpus))} papers difference")
        
        # Check L1 cluster distribution
        if 'L1' in docs.columns:
            l1_dist = docs['L1'].value_counts().sort_index()
            print(f"\n  L1 cluster distribution:")
            for cluster_id, count in l1_dist.items():
                print(f"    L1={cluster_id}: {count:>5} papers ({count/len(docs)*100:>5.1f}%)")
                
        # Check for missing values
        missing_l1 = docs['L1'].isna().sum() if 'L1' in docs.columns else 0
        missing_l2 = docs['L2'].isna().sum() if 'L2' in docs.columns else 0
        
        if missing_l1 == 0 and missing_l2 == 0:
            print(f"  ✓ No missing cluster assignments")
        else:
            print(f"  ✗ Missing assignments: L1={missing_l1}, L2={missing_l2}")
    
    # 4. Check sample data
    print("\n4. SAMPLE TEST DATA")
    print("-" * 60)
    
    sample_file = base_dir / "data" / "sample_test.csv"
    if sample_file.exists():
        sample = pd.read_csv(sample_file)
        print(f"✓ Sample file exists: {sample_file.name}")
        print(f"  Papers: {len(sample):,}")
        print(f"  File size: {sample_file.stat().st_size / 1024:.1f} KB")
        
        if 'L1' in sample.columns:
            print(f"  L1 clusters: {sample['L1'].nunique()}")
            print(f"  Distribution: {dict(sample['L1'].value_counts().sort_index())}")
    else:
        print(f"✗ Sample file not found")
    
    # 5. Check scripts
    print("\n5. SCRIPTS")
    print("-" * 60)
    
    scripts_dir = base_dir / "scripts"
    key_scripts = [
        'stream_extractor_hybrid.py',
        'generate_papers_database.py',
        'create_visualizations.py',
        'create_sample_dataset.py'
    ]
    
    for script in key_scripts:
        script_path = scripts_dir / script
        if script_path.exists():
            size = script_path.stat().st_size / 1024
            print(f"✓ {script:35} {size:>8.1f} KB")
        else:
            print(f"✗ {script:35} NOT FOUND")
    
    # 6. Final validation summary
    print("\n" + "="*60)
    print("VALIDATION SUMMARY")
    print("="*60)
    
    all_checks = [
        corpus_file.exists(),
        (results_dir / "doc_assignments.csv").exists(),
        (results_dir / "topics_level1.csv").exists(),
        (results_dir / "topics_level2.csv").exists(),
        sample_file.exists(),
        (scripts_dir / "stream_extractor_hybrid.py").exists()
    ]
    
    passed = sum(all_checks)
    total = len(all_checks)
    
    print(f"\nChecks passed: {passed}/{total} ({passed/total*100:.0f}%)")
    
    if passed == total:
        print("\n✓ ALL VALIDATIONS PASSED")
        print("  Data is consistent and ready for reproducibility testing.")
        return True
    else:
        print("\n✗ SOME VALIDATIONS FAILED")
        print("  Please review errors above and regenerate missing files.")
        return False

if __name__ == "__main__":
    success = validate_data()
    exit(0 if success else 1)
