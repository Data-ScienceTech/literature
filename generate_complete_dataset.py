#!/usr/bin/env python3
"""
Data Generation Script - Recreate the complete AIS Basket dataset

This script regenerates all the data files that were removed from git
due to their large size. Run this after cloning the repository to
recreate the complete dataset.

Usage:
    python generate_complete_dataset.py [--quick]

Options:
    --quick     Skip full fetching, only run enrichment and analysis
"""

import sys
import subprocess
import argparse
from pathlib import Path
import time

def run_command(cmd, description, cwd=None):
    """Run a command and handle errors."""
    print(f"\n{'='*60}")
    print(f"STEP: {description}")
    print(f"{'='*60}")
    print(f"Running: {cmd}")
    
    try:
        if cwd:
            result = subprocess.run(cmd, shell=True, check=True, cwd=cwd, 
                                  capture_output=False, text=True)
        else:
            result = subprocess.run(cmd, shell=True, check=True, 
                                  capture_output=False, text=True)
        print(f"✓ {description} completed successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ {description} failed with error code {e.returncode}")
        print(f"Error: {e}")
        return False

def check_requirements():
    """Check if required packages are installed."""
    required_packages = ['requests', 'pandas', 'numpy', 'tqdm', 'pyarrow']
    missing = []
    
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing.append(package)
    
    if missing:
        print(f"Missing required packages: {', '.join(missing)}")
        response = input("Install missing packages? (y/n): ")
        if response.lower() == 'y':
            cmd = f"pip install {' '.join(missing)}"
            if not run_command(cmd, "Installing missing packages"):
                return False
        else:
            print("Cannot continue without required packages.")
            return False
    
    return True

def main():
    parser = argparse.ArgumentParser(description='Generate complete AIS Basket dataset')
    parser.add_argument('--quick', action='store_true', 
                       help='Skip full fetching, only run enrichment and analysis')
    args = parser.parse_args()
    
    print("AIS Basket Dataset Generation")
    print("=" * 40)
    print("\nThis script will recreate the complete dataset that was")
    print("removed from git due to file size constraints.")
    
    if not args.quick:
        print("\nFull generation includes:")
        print("1. Fetch complete corpus from CrossRef (~45 minutes)")
        print("2. Enrich with OpenAlex data (~5 minutes)")
        print("3. Generate analysis reports (~1 minute)")
        print("\nEstimated total time: 45-50 minutes")
    else:
        print("\nQuick generation includes:")
        print("1. Use existing corpus (if available)")
        print("2. Enrich with OpenAlex data (~5 minutes)")
        print("3. Generate analysis reports (~1 minute)")
        print("\nEstimated total time: 5-10 minutes")
    
    response = input("\nContinue? (y/n): ")
    if response.lower() != 'y':
        print("Aborted.")
        return
    
    # Check requirements
    print("\nChecking requirements...")
    if not check_requirements():
        return
    
    # Create directories
    print("\nCreating directories...")
    dirs = [
        "data/clean",
        "data/raw/crossref_cache", 
        "data/raw/openalex_cache",
        "output"
    ]
    for d in dirs:
        Path(d).mkdir(parents=True, exist_ok=True)
    print("✓ Directories created")
    
    # Step 1: Fetch data (if not quick mode)
    if not args.quick:
        success = run_command(
            "python current_pipeline/fetcher/fetch_ais_basket_crossref.py --full",
            "Fetching complete corpus from CrossRef (this may take 45+ minutes)"
        )
        if not success:
            print("\n❌ Failed to fetch corpus. Try --quick mode if corpus already exists.")
            return
    else:
        # Check if corpus exists
        corpus_path = Path("data/clean/ais_basket_corpus.json")
        if not corpus_path.exists():
            print("\n❌ No existing corpus found. Run without --quick to fetch data.")
            return
        print("✓ Using existing corpus")
    
    # Step 2: Enrich data
    success = run_command(
        "python current_pipeline/enricher/enrich_ais_basket_openalex.py",
        "Enriching corpus with OpenAlex data"
    )
    if not success:
        print("\n❌ Failed to enrich corpus.")
        return
    
    # Step 3: Generate analysis
    success = run_command(
        "python current_pipeline/analysis/analyze_ais_basket_coverage.py",
        "Generating coverage analysis"
    )
    if not success:
        print("\n❌ Failed to generate coverage analysis.")
        return
    
    success = run_command(
        "python current_pipeline/analysis/analyze_enrichment_results.py", 
        "Generating enrichment analysis"
    )
    if not success:
        print("\n❌ Failed to generate enrichment analysis.")
        return
    
    # Success!
    print("\n" + "=" * 60)
    print("🎉 DATASET GENERATION COMPLETE!")
    print("=" * 60)
    print("\nGenerated files:")
    print("📊 Core Datasets:")
    print("   - data/clean/ais_basket_corpus.json (original CrossRef data)")
    print("   - data/clean/ais_basket_corpus_enriched.json (enhanced with OpenAlex)")
    print("   - data/clean/ais_basket_corpus_enriched.parquet (analysis-ready)")
    
    print("\n📈 Analysis Reports:")
    print("   - output/coverage_analysis_*.json (detailed coverage statistics)")
    print("   - output/enrichment_report_*.json (enrichment improvements)")
    print("   - output/*_log_*.log (processing logs)")
    
    print("\n📚 Usage:")
    print("   Load JSON: with open('data/clean/ais_basket_corpus_enriched.json') as f:")
    print("   Load Parquet: df = pd.read_parquet('data/clean/ais_basket_corpus_enriched.parquet')")
    
    print("\n🔄 Future Updates:")
    print("   Run with --quick for incremental updates")
    print("   See current_pipeline/README.md for detailed usage")
    
    print("\n✅ Ready for analysis!")

if __name__ == "__main__":
    main()