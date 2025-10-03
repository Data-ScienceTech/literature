"""
Sample Expansion Toolkit
=========================

Helper scripts to expand the literature sample by:
1. Merging multiple BibTeX files
2. Validating data quality
3. Removing duplicates
4. Generating statistics

Usage:
    python expand_sample.py --merge          # Merge BibTeX files
    python expand_sample.py --validate       # Validate merged file
    python expand_sample.py --deduplicate    # Remove duplicates
    python expand_sample.py --stats          # Generate statistics
    python expand_sample.py --all            # Run all steps

Author: Literature Analyzer
Date: October 2025
"""

import argparse
import glob
import json
from pathlib import Path
from typing import List, Dict
import pandas as pd
from src.parse_bib import load_bib


def merge_bib_files(input_pattern: str, output_file: str) -> str:
    """
    Merge multiple BibTeX files into one.
    
    Args:
        input_pattern: Glob pattern for input files (e.g., "data/exports/*.bib")
        output_file: Path to output merged file
        
    Returns:
        Path to merged file
    """
    print("=" * 70)
    print("STEP 1: MERGING BIBTEX FILES")
    print("=" * 70)
    
    files = sorted(glob.glob(input_pattern))
    
    if not files:
        print(f"⚠️  No files found matching pattern: {input_pattern}")
        print(f"   Please ensure BibTeX files are in the correct location")
        return None
    
    print(f"\n📁 Found {len(files)} BibTeX files to merge:")
    for i, file in enumerate(files, 1):
        size_kb = Path(file).stat().st_size / 1024
        print(f"   {i}. {Path(file).name} ({size_kb:.1f} KB)")
    
    all_content = []
    total_chars = 0
    
    for file in files:
        with open(file, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
            all_content.append(content)
            total_chars += len(content)
    
    # Write merged file
    merged = '\n\n'.join(all_content)
    
    # Create output directory if needed
    output_path = Path(output_file)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(merged)
    
    size_mb = total_chars / (1024 * 1024)
    print(f"\n✅ Successfully merged {len(files)} files into:")
    print(f"   📄 {output_file}")
    print(f"   💾 Size: {size_mb:.2f} MB")
    
    return output_file


def validate_merged_file(bib_file: str) -> Dict:
    """
    Validate merged BibTeX file and generate quality report.
    
    Args:
        bib_file: Path to BibTeX file to validate
        
    Returns:
        Dictionary with validation statistics
    """
    print("\n" + "=" * 70)
    print("STEP 2: VALIDATING MERGED FILE")
    print("=" * 70)
    
    if not Path(bib_file).exists():
        print(f"⚠️  File not found: {bib_file}")
        return None
    
    print(f"\n📖 Loading: {bib_file}")
    df = load_bib(bib_file)
    
    # Calculate statistics
    total = len(df)
    doi_count = df.doi.notna().sum()
    doi_pct = (doi_count / total * 100) if total > 0 else 0
    abstract_count = df.abstract.notna().sum()
    abstract_pct = (abstract_count / total * 100) if total > 0 else 0
    
    stats = {
        'total_papers': total,
        'papers_with_doi': doi_count,
        'doi_percentage': doi_pct,
        'papers_with_abstract': abstract_count,
        'abstract_percentage': abstract_pct,
        'year_min': int(df.year.min()) if df.year.notna().any() else None,
        'year_max': int(df.year.max()) if df.year.notna().any() else None,
        'unique_journals': df.journal.nunique(),
        'journals': df.journal.value_counts().to_dict(),
        'papers_per_year': df.year.value_counts().sort_index().to_dict(),
    }
    
    # Print report
    print(f"\n📊 VALIDATION REPORT")
    print(f"   {'─' * 50}")
    print(f"   Total papers: {stats['total_papers']:,}")
    print(f"   Papers with DOI: {stats['papers_with_doi']:,} ({stats['doi_percentage']:.1f}%)")
    print(f"   Papers with abstract: {stats['papers_with_abstract']:,} ({stats['abstract_percentage']:.1f}%)")
    print(f"   Year range: {stats['year_min']} - {stats['year_max']}")
    print(f"   Unique journals: {stats['unique_journals']}")
    
    print(f"\n📚 JOURNALS:")
    for journal, count in sorted(stats['journals'].items(), key=lambda x: x[1], reverse=True):
        print(f"   • {journal}: {count:,} papers")
    
    print(f"\n📅 PAPERS PER YEAR:")
    for year, count in sorted(stats['papers_per_year'].items()):
        if year and not pd.isna(year):
            bar = '█' * int(count / 20)
            print(f"   {int(year)}: {bar} {count:,}")
    
    # Check for issues
    print(f"\n⚠️  POTENTIAL ISSUES:")
    issues_found = False
    
    if doi_pct < 90:
        print(f"   ⚠️  DOI coverage below 90% ({doi_pct:.1f}%)")
        issues_found = True
    
    if abstract_pct < 70:
        print(f"   ⚠️  Abstract coverage below 70% ({abstract_pct:.1f}%)")
        issues_found = True
    
    duplicates = df[df.duplicated(subset=['doi'], keep=False)]
    if len(duplicates) > 0:
        print(f"   ⚠️  Found {len(duplicates)} duplicate DOIs")
        issues_found = True
    
    empty_titles = df.title.isna().sum()
    if empty_titles > 0:
        print(f"   ⚠️  Found {empty_titles} papers with missing titles")
        issues_found = True
    
    if not issues_found:
        print(f"   ✅ No major issues detected!")
    
    # Save validation report
    report_path = Path(bib_file).parent / "validation_report.json"
    with open(report_path, 'w') as f:
        json.dump(stats, f, indent=2)
    
    print(f"\n💾 Validation report saved to: {report_path}")
    
    return stats


def deduplicate_file(bib_file: str, output_file: str = None) -> str:
    """
    Remove duplicate entries from BibTeX file.
    
    Args:
        bib_file: Path to input BibTeX file
        output_file: Path to output deduplicated file (optional)
        
    Returns:
        Path to deduplicated file
    """
    print("\n" + "=" * 70)
    print("STEP 3: REMOVING DUPLICATES")
    print("=" * 70)
    
    if not Path(bib_file).exists():
        print(f"⚠️  File not found: {bib_file}")
        return None
    
    print(f"\n📖 Loading: {bib_file}")
    df = load_bib(bib_file)
    
    initial_count = len(df)
    print(f"   Initial papers: {initial_count:,}")
    
    # Remove duplicates by DOI
    df_clean = df.drop_duplicates(subset=['doi'], keep='first')
    
    final_count = len(df_clean)
    removed = initial_count - final_count
    
    print(f"   Duplicates removed: {removed:,}")
    print(f"   Final papers: {final_count:,}")
    
    if removed > 0:
        print(f"   📉 Reduction: {(removed/initial_count*100):.1f}%")
    else:
        print(f"   ✅ No duplicates found!")
    
    # Save deduplicated version
    if output_file is None:
        output_file = Path(bib_file).parent / f"{Path(bib_file).stem}_clean.csv"
    
    df_clean.to_csv(output_file, index=False)
    print(f"\n💾 Deduplicated data saved to: {output_file}")
    
    return output_file


def generate_statistics(df_or_file, output_dir: str = "data") -> Dict:
    """
    Generate comprehensive statistics about the corpus.
    
    Args:
        df_or_file: Either DataFrame or path to BibTeX/CSV file
        output_dir: Directory to save statistics
        
    Returns:
        Dictionary with statistics
    """
    print("\n" + "=" * 70)
    print("STEP 4: GENERATING STATISTICS")
    print("=" * 70)
    
    # Load data if file path provided
    if isinstance(df_or_file, str):
        if df_or_file.endswith('.bib'):
            df = load_bib(df_or_file)
        else:
            df = pd.read_csv(df_or_file)
    else:
        df = df_or_file
    
    # Calculate comprehensive statistics
    stats = {
        'corpus_overview': {
            'total_papers': len(df),
            'unique_journals': df.journal.nunique(),
            'year_range': f"{int(df.year.min())}-{int(df.year.max())}",
            'total_years': int(df.year.max() - df.year.min() + 1),
        },
        'data_quality': {
            'doi_coverage': f"{df.doi.notna().sum()}/{len(df)} ({df.doi.notna().sum()/len(df)*100:.1f}%)",
            'abstract_coverage': f"{df.abstract.notna().sum()}/{len(df)} ({df.abstract.notna().sum()/len(df)*100:.1f}%)",
            'title_coverage': f"{df.title.notna().sum()}/{len(df)} ({df.title.notna().sum()/len(df)*100:.1f}%)",
            'text_available': f"{df.text.notna().sum()}/{len(df)} ({df.text.notna().sum()/len(df)*100:.1f}%)",
        },
        'journals': df.journal.value_counts().to_dict(),
        'papers_per_year': df.year.value_counts().sort_index().to_dict(),
        'text_statistics': {
            'mean_length': int(df.text.str.len().mean()) if df.text.notna().any() else 0,
            'median_length': int(df.text.str.len().median()) if df.text.notna().any() else 0,
            'min_length': int(df.text.str.len().min()) if df.text.notna().any() else 0,
            'max_length': int(df.text.str.len().max()) if df.text.notna().any() else 0,
        }
    }
    
    # Print statistics
    print("\n📊 CORPUS OVERVIEW")
    print(f"   {'─' * 50}")
    for key, value in stats['corpus_overview'].items():
        print(f"   {key.replace('_', ' ').title()}: {value}")
    
    print("\n✅ DATA QUALITY")
    print(f"   {'─' * 50}")
    for key, value in stats['data_quality'].items():
        print(f"   {key.replace('_', ' ').title()}: {value}")
    
    print("\n📚 DISTRIBUTION BY JOURNAL")
    print(f"   {'─' * 50}")
    for journal, count in sorted(stats['journals'].items(), key=lambda x: x[1], reverse=True):
        pct = count / len(df) * 100
        bar = '█' * int(pct / 2)
        print(f"   {journal[:30]:30} {bar} {count:5,} ({pct:5.1f}%)")
    
    print("\n📅 DISTRIBUTION BY YEAR")
    print(f"   {'─' * 50}")
    for year, count in sorted(stats['papers_per_year'].items()):
        if year and not pd.isna(year):
            bar = '█' * int(count / 20)
            print(f"   {int(year)}: {bar} {count:,}")
    
    print("\n📝 TEXT LENGTH STATISTICS")
    print(f"   {'─' * 50}")
    for key, value in stats['text_statistics'].items():
        print(f"   {key.replace('_', ' ').title()}: {value:,} chars")
    
    # Save statistics
    stats_path = Path(output_dir) / "corpus_stats_expanded.json"
    stats_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(stats_path, 'w') as f:
        json.dump(stats, f, indent=2)
    
    print(f"\n💾 Statistics saved to: {stats_path}")
    
    return stats


def run_all_steps(input_pattern: str = "data/exports/*.bib", 
                  merged_file: str = "data/refs_expanded.bib",
                  clean_file: str = "data/refs_expanded_clean.csv"):
    """
    Run all expansion steps in sequence.
    
    Args:
        input_pattern: Glob pattern for input BibTeX files
        merged_file: Path to save merged file
        clean_file: Path to save cleaned file
    """
    print("\n" + "=" * 70)
    print("RUNNING COMPLETE SAMPLE EXPANSION WORKFLOW")
    print("=" * 70)
    
    # Step 1: Merge
    merged_path = merge_bib_files(input_pattern, merged_file)
    if not merged_path:
        print("\n❌ Merging failed. Aborting.")
        return
    
    # Step 2: Validate
    stats = validate_merged_file(merged_path)
    if not stats:
        print("\n❌ Validation failed. Aborting.")
        return
    
    # Step 3: Deduplicate
    clean_path = deduplicate_file(merged_path, clean_file)
    if not clean_path:
        print("\n❌ Deduplication failed. Aborting.")
        return
    
    # Step 4: Generate statistics on clean data
    final_stats = generate_statistics(clean_path)
    
    print("\n" + "=" * 70)
    print("✅ EXPANSION WORKFLOW COMPLETE!")
    print("=" * 70)
    print(f"\n📄 Output files:")
    print(f"   • Merged BibTeX: {merged_path}")
    print(f"   • Clean CSV: {clean_path}")
    print(f"   • Validation report: data/validation_report.json")
    print(f"   • Statistics: data/corpus_stats_expanded.json")
    
    print(f"\n📊 Final corpus:")
    print(f"   • Total papers: {final_stats['corpus_overview']['total_papers']:,}")
    print(f"   • Journals: {final_stats['corpus_overview']['unique_journals']}")
    print(f"   • Year range: {final_stats['corpus_overview']['year_range']}")
    
    print(f"\n🚀 Next steps:")
    print(f"   1. Review validation report and statistics")
    print(f"   2. Update run_full_analysis.py to use new file")
    print(f"   3. Run analysis pipeline: python run_full_analysis.py")
    print(f"   4. Compare results with original sample")


def main():
    parser = argparse.ArgumentParser(
        description="Sample Expansion Toolkit for Literature Analyzer",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Merge all BibTeX files in data/exports/
  python expand_sample.py --merge
  
  # Validate the merged file
  python expand_sample.py --validate
  
  # Remove duplicates
  python expand_sample.py --deduplicate
  
  # Generate statistics
  python expand_sample.py --stats
  
  # Run complete workflow
  python expand_sample.py --all
  
  # Custom input pattern
  python expand_sample.py --merge --input "exports/*.bib" --output "data/custom.bib"
        """
    )
    
    parser.add_argument('--merge', action='store_true',
                       help='Merge BibTeX files')
    parser.add_argument('--validate', action='store_true',
                       help='Validate merged file')
    parser.add_argument('--deduplicate', action='store_true',
                       help='Remove duplicates')
    parser.add_argument('--stats', action='store_true',
                       help='Generate statistics')
    parser.add_argument('--all', action='store_true',
                       help='Run all steps')
    
    parser.add_argument('--input', type=str, default="data/exports/*.bib",
                       help='Input pattern for BibTeX files (default: data/exports/*.bib)')
    parser.add_argument('--output', type=str, default="data/refs_expanded.bib",
                       help='Output merged file (default: data/refs_expanded.bib)')
    parser.add_argument('--clean', type=str, default="data/refs_expanded_clean.csv",
                       help='Output clean file (default: data/refs_expanded_clean.csv)')
    
    args = parser.parse_args()
    
    # If no arguments, show help
    if not any([args.merge, args.validate, args.deduplicate, args.stats, args.all]):
        parser.print_help()
        return
    
    # Run requested operations
    if args.all:
        run_all_steps(args.input, args.output, args.clean)
    else:
        if args.merge:
            merge_bib_files(args.input, args.output)
        
        if args.validate:
            validate_merged_file(args.output)
        
        if args.deduplicate:
            deduplicate_file(args.output, args.clean)
        
        if args.stats:
            generate_statistics(args.clean if Path(args.clean).exists() else args.output)


if __name__ == "__main__":
    main()
