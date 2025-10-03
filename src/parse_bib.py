"""
BibTeX parsing module for journal streams analysis.
Robustly parses BibTeX files and normalizes metadata.
"""

import bibtexparser
import re
import pandas as pd
import pathlib
from typing import Dict, List, Optional
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def clean_latex_accents(text: str) -> str:
    """Remove common LaTeX accents and special characters."""
    if not text:
        return ""
    
    # Common LaTeX accent commands
    replacements = {
        r"\'": "'",
        r"\`": "`",
        r'\\"': '"',
        r"\^": "^",
        r"\~": "~",
        r"\\c{": "",
        r"{": "",
        r"}": "",
        r"\\": ""
    }
    
    result = text
    for pattern, replacement in replacements.items():
        result = result.replace(pattern, replacement)
    
    return result.strip()


def parse_authors(author_string: str) -> List[str]:
    """Parse author string and return list of normalized author names."""
    if not author_string:
        return []
    
    # Split by 'and' for BibTeX format
    authors = re.split(r'\s+and\s+', author_string, flags=re.IGNORECASE)
    
    # Clean each author
    cleaned_authors = []
    for author in authors:
        author = clean_latex_accents(author)
        author = re.sub(r'\s+', ' ', author).strip()
        if author:
            cleaned_authors.append(author)
    
    return cleaned_authors


def extract_year(year_string: str) -> Optional[int]:
    """Extract 4-digit year from year string."""
    if not year_string:
        return None
    
    # Find first 4-digit number
    match = re.search(r'\b(19|20)\d{2}\b', str(year_string))
    if match:
        return int(match.group(0))
    
    return None


def normalize_journal(journal_string: str) -> str:
    """Normalize journal names."""
    if not journal_string:
        return ""
    
    journal = clean_latex_accents(journal_string)
    journal = re.sub(r'\s+', ' ', journal).strip()
    
    return journal


def load_bib(path: str) -> pd.DataFrame:
    """
    Load and parse BibTeX file into a pandas DataFrame.
    
    Parameters
    ----------
    path : str
        Path to the BibTeX file
        
    Returns
    -------
    pd.DataFrame
        DataFrame with columns: id, title, abstract, authors, author_list, 
        year, journal, doi, text, cited_doi, references_count
    """
    logger.info(f"Loading BibTeX file: {path}")
    
    # Read file with error handling for encoding issues
    file_path = pathlib.Path(path)
    try:
        text = file_path.read_text(encoding='utf-8', errors='ignore')
    except Exception as e:
        logger.warning(f"UTF-8 encoding failed, trying latin-1: {e}")
        text = file_path.read_text(encoding='latin-1', errors='ignore')
    
    # Parse BibTeX
    try:
        db = bibtexparser.loads(text)
    except Exception as e:
        logger.error(f"Failed to parse BibTeX: {e}")
        raise
    
    logger.info(f"Parsed {len(db.entries)} entries from BibTeX file")
    
    # Extract data from entries
    rows = []
    for e in db.entries:
        # Get entry ID
        entry_id = e.get("ID") or e.get("key", "")
        
        # Extract fields
        title = clean_latex_accents(e.get("title", ""))
        abstract = clean_latex_accents(e.get("abstract", ""))
        
        # Parse authors
        author_string = e.get("author", "")
        author_list = parse_authors(author_string)
        authors = "; ".join(author_list) if author_list else ""
        
        # Extract year
        year = extract_year(e.get("year", ""))
        
        # Normalize journal
        journal = normalize_journal(e.get("journal") or e.get("booktitle", ""))
        
        # DOI
        doi = e.get("doi", "").strip().lower()
        
        # Cited DOIs
        cited_doi = e.get("cited-doi", "").strip()
        
        # Reference count
        ref_count = e.get("references-count", "")
        try:
            references_count = int(ref_count) if ref_count else None
        except (ValueError, TypeError):
            references_count = None
        
        rows.append({
            "id": entry_id,
            "title": title,
            "abstract": abstract,
            "authors": authors,
            "author_list": author_list,
            "year": year,
            "journal": journal,
            "doi": doi,
            "cited_doi": cited_doi,
            "references_count": references_count,
        })
    
    # Create DataFrame
    df = pd.DataFrame(rows)
    
    # Remove duplicates based on DOI (keep first occurrence)
    initial_count = len(df)
    df = df.drop_duplicates(subset=["doi"], keep='first').reset_index(drop=True)
    if len(df) < initial_count:
        logger.info(f"Removed {initial_count - len(df)} duplicate DOIs")
    
    # Create text field for embedding (title + abstract, or just title if no abstract)
    df["text"] = (
        df["title"].fillna("") + ". " + df["abstract"].fillna("")
    ).str.strip()
    
    # Replace empty strings with NaN for better data handling
    df["text"] = df["text"].replace("", pd.NA)
    df["abstract"] = df["abstract"].replace("", pd.NA)
    
    # Log statistics
    logger.info(f"Final dataset: {len(df)} papers")
    logger.info(f"Papers with DOI: {df['doi'].notna().sum()} ({df['doi'].notna().sum()/len(df)*100:.1f}%)")
    logger.info(f"Papers with abstract: {df['abstract'].notna().sum()} ({df['abstract'].notna().sum()/len(df)*100:.1f}%)")
    logger.info(f"Year range: {df['year'].min()} - {df['year'].max()}")
    logger.info(f"Unique journals: {df['journal'].nunique()}")
    
    return df


def get_corpus_stats(df: pd.DataFrame) -> Dict:
    """
    Calculate corpus statistics.
    
    Parameters
    ----------
    df : pd.DataFrame
        DataFrame from load_bib
        
    Returns
    -------
    Dict
        Dictionary with corpus statistics
    """
    stats = {
        "total_papers": len(df),
        "papers_with_doi": df["doi"].notna().sum(),
        "papers_with_abstract": df["abstract"].notna().sum(),
        "papers_with_text": df["text"].notna().sum(),
        "year_min": int(df["year"].min()) if df["year"].notna().any() else None,
        "year_max": int(df["year"].max()) if df["year"].notna().any() else None,
        "unique_journals": df["journal"].nunique(),
        "journals": df["journal"].value_counts().to_dict(),
        "papers_per_year": df["year"].value_counts().sort_index().to_dict(),
    }
    
    return stats


if __name__ == "__main__":
    # Test the parser
    import sys
    
    if len(sys.argv) > 1:
        bib_path = sys.argv[1]
    else:
        bib_path = "data/refs_2016_2025_AMR_MISQ_ORSC_ISR.bib"
    
    df = load_bib(bib_path)
    print("\n=== Corpus Statistics ===")
    stats = get_corpus_stats(df)
    for key, value in stats.items():
        if key not in ["journals", "papers_per_year"]:
            print(f"{key}: {value}")
    
    print("\n=== Sample Records ===")
    print(df.head())
