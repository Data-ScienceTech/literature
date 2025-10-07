#!/usr/bin/env python3
"""
Analyze metadata coverage and quality for AIS Basket of 8 corpus.

This script examines the fetched data to determine:
- How many articles have each metadata field
- Completeness percentages
- Quality metrics (e.g., abstract length, reference counts)
- Missing data patterns by journal and year
"""

import json
import pandas as pd
import numpy as np
from pathlib import Path
from collections import defaultdict
from datetime import datetime

# File paths
DATA_DIR = Path("data")
CLEAN_DIR = DATA_DIR / "clean"
CORPUS_JSON = CLEAN_DIR / "ais_basket_corpus.json"
CORPUS_PARQUET = CLEAN_DIR / "ais_basket_corpus.parquet"
OUTPUT_DIR = Path("output")
OUTPUT_DIR.mkdir(exist_ok=True)

def load_corpus():
    """Load the corpus data."""
    print("Loading corpus data...")
    
    # Load full JSON for detailed metadata
    with open(CORPUS_JSON, 'r', encoding='utf-8') as f:
        articles = json.load(f)
    
    # Load Parquet for easy analysis
    df = pd.read_parquet(CORPUS_PARQUET)
    
    print(f"✓ Loaded {len(articles):,} articles")
    return articles, df

def analyze_field_coverage(articles):
    """Analyze coverage of each metadata field."""
    print("\n" + "="*70)
    print("FIELD COVERAGE ANALYSIS")
    print("="*70)
    
    total = len(articles)
    
    # Define fields to check
    fields = {
        # Core fields
        'doi': 'DOI',
        'title': 'Title',
        'year': 'Publication Year',
        'publication_date': 'Full Publication Date',
        'journal': 'Journal Name',
        
        # Authors
        'authors': 'Authors List',
        'author_count': 'Author Count',
        
        # Content
        'abstract': 'Abstract',
        'type': 'Article Type',
        
        # Bibliographic
        'volume': 'Volume',
        'issue': 'Issue',
        'page': 'Page Numbers',
        
        # Citations & References
        'references': 'Reference DOIs',
        'reference_count': 'Reference Count',
        'citation_count': 'Citation Count',
        
        # Publisher info
        'publisher': 'Publisher',
        'issn': 'ISSN',
        
        # Enhanced metadata
        'subject': 'Subject/Keywords',
        'license': 'License Info',
        'funder': 'Funding Info',
        
        # Dates
        'indexed_date': 'Indexed Date',
        'created_date': 'Created Date',
        'deposited_date': 'Deposited Date',
        'accepted_date': 'Accepted Date',
    }
    
    coverage = {}
    
    for field, label in fields.items():
        count = 0
        non_empty_count = 0
        
        for article in articles:
            value = article.get(field)
            
            if value is not None:
                count += 1
                
                # Check if actually has content (not empty string/list/dict)
                if isinstance(value, str) and value.strip():
                    non_empty_count += 1
                elif isinstance(value, (list, dict)) and len(value) > 0:
                    non_empty_count += 1
                elif isinstance(value, (int, float)) and value != 0:
                    non_empty_count += 1
                elif isinstance(value, (int, float)) and field in ['citation_count', 'reference_count']:
                    # Include 0 citations as valid
                    non_empty_count += 1
        
        coverage[field] = {
            'label': label,
            'present': count,
            'present_pct': (count / total) * 100,
            'non_empty': non_empty_count,
            'non_empty_pct': (non_empty_count / total) * 100
        }
    
    # Display results
    print(f"\nTotal articles: {total:,}\n")
    print(f"{'Field':<30} {'Present':>10} {'%':>7} {'Non-Empty':>10} {'%':>7}")
    print("-" * 70)
    
    # Sort by non-empty percentage descending
    sorted_fields = sorted(coverage.items(), key=lambda x: x[1]['non_empty_pct'], reverse=True)
    
    for field, stats in sorted_fields:
        print(f"{stats['label']:<30} {stats['present']:>10,} {stats['present_pct']:>6.1f}% "
              f"{stats['non_empty']:>10,} {stats['non_empty_pct']:>6.1f}%")
    
    return coverage

def analyze_abstracts(articles):
    """Analyze abstract coverage and quality."""
    print("\n" + "="*70)
    print("ABSTRACT ANALYSIS")
    print("="*70)
    
    total = len(articles)
    with_abstract = [a for a in articles if a.get('abstract') and a['abstract'].strip()]
    
    print(f"\nArticles with abstract: {len(with_abstract):,} / {total:,} ({len(with_abstract)/total*100:.1f}%)")
    
    if with_abstract:
        lengths = [len(a['abstract']) for a in with_abstract]
        word_counts = [len(a['abstract'].split()) for a in with_abstract]
        
        print(f"\nAbstract Length (characters):")
        print(f"  Min:     {min(lengths):,}")
        print(f"  Max:     {max(lengths):,}")
        print(f"  Mean:    {np.mean(lengths):,.0f}")
        print(f"  Median:  {np.median(lengths):,.0f}")
        
        print(f"\nAbstract Length (words):")
        print(f"  Min:     {min(word_counts):,}")
        print(f"  Max:     {max(word_counts):,}")
        print(f"  Mean:    {np.mean(word_counts):,.0f}")
        print(f"  Median:  {np.median(word_counts):,.0f}")
        
        # Check for suspiciously short abstracts
        short_abstracts = [a for a in with_abstract if len(a['abstract'].split()) < 50]
        if short_abstracts:
            print(f"\nSuspiciously short abstracts (<50 words): {len(short_abstracts):,}")
    
    return {
        'total': total,
        'with_abstract': len(with_abstract),
        'coverage_pct': len(with_abstract)/total*100 if total > 0 else 0,
        'avg_length_chars': np.mean(lengths) if with_abstract else 0,
        'avg_length_words': np.mean(word_counts) if with_abstract else 0
    }

def analyze_references(articles):
    """Analyze reference/citation data."""
    print("\n" + "="*70)
    print("REFERENCE & CITATION ANALYSIS")
    print("="*70)
    
    total = len(articles)
    with_refs = [a for a in articles if a.get('references') and len(a['references']) > 0]
    
    print(f"\nArticles with reference DOIs: {len(with_refs):,} / {total:,} ({len(with_refs)/total*100:.1f}%)")
    
    if with_refs:
        ref_counts = [len(a['references']) for a in with_refs]
        
        print(f"\nReferences per article:")
        print(f"  Min:     {min(ref_counts):,}")
        print(f"  Max:     {max(ref_counts):,}")
        print(f"  Mean:    {np.mean(ref_counts):,.1f}")
        print(f"  Median:  {np.median(ref_counts):,.0f}")
        
        # Total unique DOIs referenced
        all_refs = set()
        for a in with_refs:
            all_refs.update(a['references'])
        print(f"\nUnique DOIs referenced: {len(all_refs):,}")
    
    # Citation counts
    citation_counts = [a.get('citation_count', 0) for a in articles]
    cited_articles = [a for a in articles if a.get('citation_count', 0) > 0]
    
    print(f"\nCitation Counts:")
    print(f"  Articles cited (>0):  {len(cited_articles):,} / {total:,} ({len(cited_articles)/total*100:.1f}%)")
    if citation_counts:
        print(f"  Min:     {min(citation_counts):,}")
        print(f"  Max:     {max(citation_counts):,}")
        print(f"  Mean:    {np.mean(citation_counts):,.1f}")
        print(f"  Median:  {np.median(citation_counts):,.0f}")
        
        # Highly cited papers
        highly_cited = [a for a in articles if a.get('citation_count', 0) >= 100]
        print(f"\nHighly cited papers (≥100 citations): {len(highly_cited):,}")
        
        very_highly_cited = [a for a in articles if a.get('citation_count', 0) >= 500]
        print(f"Very highly cited papers (≥500 citations): {len(very_highly_cited):,}")
    
    return {
        'articles_with_refs': len(with_refs),
        'avg_refs_per_article': np.mean(ref_counts) if with_refs else 0,
        'unique_dois_referenced': len(all_refs) if with_refs else 0,
        'articles_cited': len(cited_articles),
        'avg_citations': np.mean(citation_counts) if citation_counts else 0
    }

def analyze_by_journal(articles, df):
    """Analyze coverage by journal."""
    print("\n" + "="*70)
    print("COVERAGE BY JOURNAL")
    print("="*70)
    
    journal_stats = []
    
    for journal in sorted(df['journal'].unique()):
        journal_articles = [a for a in articles if a['journal'] == journal]
        journal_df = df[df['journal'] == journal]
        
        stats = {
            'journal': journal,
            'count': len(journal_articles),
            'abstract_pct': sum(1 for a in journal_articles if a.get('abstract') and a['abstract'].strip()) / len(journal_articles) * 100,
            'refs_pct': sum(1 for a in journal_articles if a.get('references') and len(a['references']) > 0) / len(journal_articles) * 100,
            'keywords_pct': sum(1 for a in journal_articles if a.get('subject') and len(a['subject']) > 0) / len(journal_articles) * 100,
            'avg_citations': journal_df['citation_count'].mean(),
            'year_range': f"{journal_df['year'].min()}-{journal_df['year'].max()}"
        }
        journal_stats.append(stats)
    
    # Display
    print(f"\n{'Journal':<50} {'Articles':>8} {'Abstract':>9} {'Refs':>9} {'Keywords':>9}")
    print("-" * 95)
    
    for stats in sorted(journal_stats, key=lambda x: x['count'], reverse=True):
        print(f"{stats['journal']:<50} {stats['count']:>8,} "
              f"{stats['abstract_pct']:>8.1f}% {stats['refs_pct']:>8.1f}% {stats['keywords_pct']:>8.1f}%")
    
    return journal_stats

def analyze_by_year(articles, df):
    """Analyze coverage by publication year."""
    print("\n" + "="*70)
    print("COVERAGE BY YEAR (Last 10 Years)")
    print("="*70)
    
    # Get last 10 years
    recent_years = sorted(df['year'].dropna().unique(), reverse=True)[:10]
    
    year_stats = []
    
    for year in sorted(recent_years):
        year_articles = [a for a in articles if a.get('year') == year]
        
        if year_articles:
            stats = {
                'year': int(year),
                'count': len(year_articles),
                'abstract_pct': sum(1 for a in year_articles if a.get('abstract') and a['abstract'].strip()) / len(year_articles) * 100,
                'refs_pct': sum(1 for a in year_articles if a.get('references') and len(a['references']) > 0) / len(year_articles) * 100,
                'keywords_pct': sum(1 for a in year_articles if a.get('subject') and len(a['subject']) > 0) / len(year_articles) * 100
            }
            year_stats.append(stats)
    
    # Display
    print(f"\n{'Year':>6} {'Articles':>8} {'Abstract':>9} {'Refs':>9} {'Keywords':>9}")
    print("-" * 50)
    
    for stats in sorted(year_stats, key=lambda x: x['year'], reverse=True):
        print(f"{stats['year']:>6} {stats['count']:>8,} "
              f"{stats['abstract_pct']:>8.1f}% {stats['refs_pct']:>8.1f}% {stats['keywords_pct']:>8.1f}%")
    
    return year_stats

def analyze_author_affiliations(articles):
    """Analyze author affiliation data."""
    print("\n" + "="*70)
    print("AUTHOR & AFFILIATION ANALYSIS")
    print("="*70)
    
    total = len(articles)
    
    # Articles with authors
    with_authors = [a for a in articles if a.get('authors') and len(a['authors']) > 0]
    print(f"\nArticles with authors: {len(with_authors):,} / {total:,} ({len(with_authors)/total*100:.1f}%)")
    
    author_counts = []
    affiliation_pct = 0.0
    
    if with_authors:
        author_counts = [len(a['authors']) for a in with_authors]
        print(f"\nAuthors per article:")
        print(f"  Min:     {min(author_counts)}")
        print(f"  Max:     {max(author_counts)}")
        print(f"  Mean:    {np.mean(author_counts):.1f}")
        print(f"  Median:  {np.median(author_counts):.0f}")
        
        # Check affiliation coverage
        articles_with_affiliations = 0
        total_authors_with_affiliation = 0
        total_authors = 0
        
        for article in with_authors:
            has_any_affiliation = False
            for author in article['authors']:
                total_authors += 1
                affiliations = author.get('affiliation', [])
                if affiliations and any(aff for aff in affiliations if aff.strip()):
                    total_authors_with_affiliation += 1
                    has_any_affiliation = True
            
            if has_any_affiliation:
                articles_with_affiliations += 1
        
        print(f"\nAffiliation Coverage:")
        print(f"  Articles with at least one affiliation: {articles_with_affiliations:,} / {len(with_authors):,} "
              f"({articles_with_affiliations/len(with_authors)*100:.1f}%)")
        if total_authors > 0:
            print(f"  Authors with affiliation: {total_authors_with_affiliation:,} / {total_authors:,} "
                  f"({total_authors_with_affiliation/total_authors*100:.1f}%)")
            affiliation_pct = total_authors_with_affiliation/total_authors*100
    
    return {
        'articles_with_authors': len(with_authors),
        'avg_authors_per_article': float(np.mean(author_counts)) if author_counts else 0.0,
        'affiliation_coverage_pct': float(affiliation_pct)
    }

def identify_missing_data_patterns(articles):
    """Identify patterns in missing data."""
    print("\n" + "="*70)
    print("MISSING DATA PATTERNS")
    print("="*70)
    
    # Articles missing critical fields
    missing_abstract = [a for a in articles if not (a.get('abstract') and a['abstract'].strip())]
    missing_refs = [a for a in articles if not (a.get('references') and len(a['references']) > 0)]
    missing_keywords = [a for a in articles if not (a.get('subject') and len(a['subject']) > 0)]
    
    print(f"\nArticles missing critical fields:")
    print(f"  Missing abstract:  {len(missing_abstract):>6,} ({len(missing_abstract)/len(articles)*100:>5.1f}%)")
    print(f"  Missing refs:      {len(missing_refs):>6,} ({len(missing_refs)/len(articles)*100:>5.1f}%)")
    print(f"  Missing keywords:  {len(missing_keywords):>6,} ({len(missing_keywords)/len(articles)*100:>5.1f}%)")
    
    # Articles missing all three
    missing_all_three = [a for a in articles 
                        if a in missing_abstract and a in missing_refs and a in missing_keywords]
    
    print(f"\n  Missing all three: {len(missing_all_three):>6,} ({len(missing_all_three)/len(articles)*100:>5.1f}%)")
    
    # Most complete articles
    complete_articles = [a for a in articles
                        if (a.get('abstract') and a['abstract'].strip())
                        and (a.get('references') and len(a['references']) > 0)
                        and (a.get('subject') and len(a['subject']) > 0)]
    
    print(f"\n  Complete (all three): {len(complete_articles):>6,} ({len(complete_articles)/len(articles)*100:>5.1f}%)")
    
    return {
        'missing_abstract': len(missing_abstract),
        'missing_refs': len(missing_refs),
        'missing_keywords': len(missing_keywords),
        'missing_all_three': len(missing_all_three),
        'complete_articles': len(complete_articles)
    }

def generate_summary_report(all_stats):
    """Generate comprehensive summary report."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_file = OUTPUT_DIR / f"coverage_analysis_{timestamp}.json"
    
    with open(report_file, 'w') as f:
        json.dump(all_stats, f, indent=2)
    
    print(f"\n✓ Detailed report saved to: {report_file}")
    
    # Also create a markdown summary
    md_file = OUTPUT_DIR / f"coverage_summary_{timestamp}.md"
    with open(md_file, 'w') as f:
        f.write("# AIS Basket of 8 - Data Coverage Analysis\n\n")
        f.write(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        f.write(f"**Total Articles:** {all_stats['total_articles']:,}\n\n")
        
        f.write("## Key Metrics\n\n")
        f.write(f"- **Abstract Coverage:** {all_stats['abstract']['coverage_pct']:.1f}%\n")
        f.write(f"- **Reference DOIs:** {all_stats['references']['articles_with_refs']:,} articles ({all_stats['references']['articles_with_refs']/all_stats['total_articles']*100:.1f}%)\n")
        f.write(f"- **Average References per Article:** {all_stats['references']['avg_refs_per_article']:.1f}\n")
        f.write(f"- **Unique DOIs Referenced:** {all_stats['references']['unique_dois_referenced']:,}\n")
        f.write(f"- **Author Affiliation Coverage:** {all_stats['authors']['affiliation_coverage_pct']:.1f}%\n")
        
        f.write("\n## Completeness\n\n")
        f.write(f"- Articles with abstract + references + keywords: {all_stats['missing_patterns']['complete_articles']:,} ({all_stats['missing_patterns']['complete_articles']/all_stats['total_articles']*100:.1f}%)\n")
        
    print(f"✓ Summary report saved to: {md_file}")

def main():
    """Main analysis function."""
    print("\n" + "="*70)
    print("AIS BASKET OF 8 - DATA COVERAGE ANALYSIS")
    print("="*70)
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    # Load data
    articles, df = load_corpus()
    
    # Run analyses
    all_stats = {
        'total_articles': len(articles),
        'analysis_date': datetime.now().isoformat()
    }
    
    # Field coverage
    all_stats['field_coverage'] = analyze_field_coverage(articles)
    
    # Abstract analysis
    all_stats['abstract'] = analyze_abstracts(articles)
    
    # Reference analysis
    all_stats['references'] = analyze_references(articles)
    
    # Author analysis
    all_stats['authors'] = analyze_author_affiliations(articles)
    
    # By journal
    all_stats['by_journal'] = analyze_by_journal(articles, df)
    
    # By year
    all_stats['by_year'] = analyze_by_year(articles, df)
    
    # Missing data patterns
    all_stats['missing_patterns'] = identify_missing_data_patterns(articles)
    
    # Generate summary report
    generate_summary_report(all_stats)
    
    print("\n" + "="*70)
    print("ANALYSIS COMPLETE")
    print("="*70)
    print(f"\n✓ Analyzed {len(articles):,} articles from {len(df['journal'].unique())} journals")
    print(f"✓ Date range: {int(df['year'].min())} - {int(df['year'].max())}")
    print("\n")

if __name__ == "__main__":
    main()
