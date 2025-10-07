#!/usr/bin/env python3
"""
Comprehensive CrossRef Fetcher for AIS Senior Scholars' Basket of 8 Journals

This fetcher builds and maintains a complete dataset of IS research from the official
AIS basket journals. It supports incremental updates, tracking what has already been
downloaded to avoid redundant API calls.

Key Features:
- Fetches from official AIS Basket of 8 journals
- Incremental updates (only fetch new/updated articles)
- State management (tracks last update per journal)
- Comprehensive metadata extraction
- Multiple output formats (Parquet, JSON, BibTeX)
- Deduplication across journals
- Full citation network data
- Progress tracking and error recovery

Official AIS Basket of 8:
1. MIS Quarterly (MISQ)
2. Information Systems Research (ISR)
3. Journal of Management Information Systems (JMIS)
4. Journal of the Association for Information Systems (JAIS)
5. European Journal of Information Systems (EJIS)
6. Information Systems Journal (ISJ)
7. Journal of Information Technology (JIT)
8. Journal of Strategic Information Systems (JSIS)

Author: Carlos Denner
Version: 2.0
Date: October 2025
"""

import os
import sys
import json
import time
import logging
import argparse
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Set, Optional, Tuple
from collections import defaultdict
from urllib.parse import urlencode
import re

import requests
import pandas as pd
from tqdm import tqdm

# ========================================
# Configuration
# ========================================

# Official AIS Senior Scholars' Basket of 8 Journals
# Source: https://aisnet.org/page/SeniorScholarBasket
AIS_BASKET_8 = {
    "MIS Quarterly": {
        "issn": ["0276-7783", "2162-9730"],  # print, online
        "short_name": "MISQ",
        "publisher": "University of Minnesota"
    },
    "Information Systems Research": {
        "issn": ["1047-7047", "1526-5536"],
        "short_name": "ISR",
        "publisher": "INFORMS"
    },
    "Journal of Management Information Systems": {
        "issn": ["0742-1222", "1557-928X"],
        "short_name": "JMIS",
        "publisher": "Taylor & Francis"
    },
    "Journal of the Association for Information Systems": {
        "issn": ["1536-9323"],
        "short_name": "JAIS",
        "publisher": "AIS"
    },
    "European Journal of Information Systems": {
        "issn": ["0960-085X", "1476-9344"],
        "short_name": "EJIS",
        "publisher": "Taylor & Francis"
    },
    "Information Systems Journal": {
        "issn": ["1350-1917", "1365-2575"],
        "short_name": "ISJ",
        "publisher": "Wiley"
    },
    "Journal of Information Technology": {
        "issn": ["0268-3962", "1466-4437"],
        "short_name": "JIT",
        "publisher": "SAGE"
    },
    "Journal of Strategic Information Systems": {
        "issn": ["0963-8687", "1873-1198"],
        "short_name": "JSIS",
        "publisher": "Elsevier"
    }
}

CROSSREF_BASE = "https://api.crossref.org/works"
CROSSREF_EMAIL = "carlosdenner@gmail.com"  # Polite pool access
HEADERS_JSON = {
    "User-Agent": f"AIS-Basket-Fetcher/2.0 (mailto:{CROSSREF_EMAIL})",
    "Accept": "application/json"
}
HEADERS_BIBTEX = {
    "User-Agent": f"AIS-Basket-Fetcher/2.0 (mailto:{CROSSREF_EMAIL})",
    "Accept": "application/x-bibtex"
}

# File paths
DATA_DIR = Path("data")
RAW_DIR = DATA_DIR / "raw" / "crossref_cache"
CLEAN_DIR = DATA_DIR / "clean"
STATE_FILE = DATA_DIR / "crossref_state.json"
OUTPUT_DIR = Path("output")

# Create directories
for directory in [RAW_DIR, CLEAN_DIR, OUTPUT_DIR]:
    directory.mkdir(parents=True, exist_ok=True)

# API settings
ROWS_PER_PAGE = 100  # CrossRef recommends max 100
RETRY_ATTEMPTS = 5
RETRY_DELAY = 2.0
REQUEST_DELAY = 0.5  # Be polite to CrossRef API
TIMEOUT = 30

# Logging setup
LOG_FILE = OUTPUT_DIR / f"fetch_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# ========================================
# State Management
# ========================================

class FetchState:
    """Manages fetcher state to enable incremental updates."""
    
    def __init__(self, state_file: Path):
        self.state_file = state_file
        self.state = self._load_state()
    
    def _load_state(self) -> Dict:
        """Load state from JSON file."""
        if self.state_file.exists():
            try:
                with open(self.state_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                logger.warning(f"Could not load state file: {e}. Starting fresh.")
                return self._init_state()
        return self._init_state()
    
    def _init_state(self) -> Dict:
        """Initialize empty state."""
        return {
            "version": "2.0",
            "created": datetime.now().isoformat(),
            "last_updated": None,
            "journals": {},
            "total_articles": 0,
            "runs": []
        }
    
    def save(self):
        """Save state to JSON file."""
        self.state["last_updated"] = datetime.now().isoformat()
        with open(self.state_file, 'w') as f:
            json.dump(self.state, f, indent=2)
        logger.info(f"State saved to {self.state_file}")
    
    def get_last_update(self, journal_name: str) -> Optional[str]:
        """Get last update date for a journal."""
        return self.state["journals"].get(journal_name, {}).get("last_update")
    
    def update_journal(self, journal_name: str, article_count: int, last_date: str):
        """Update journal state."""
        if journal_name not in self.state["journals"]:
            self.state["journals"][journal_name] = {
                "first_fetch": datetime.now().isoformat(),
                "article_count": 0,
                "fetch_count": 0
            }
        
        self.state["journals"][journal_name].update({
            "last_update": datetime.now().isoformat(),
            "last_indexed_date": last_date,
            "article_count": article_count,
            "fetch_count": self.state["journals"][journal_name].get("fetch_count", 0) + 1
        })
    
    def add_run_summary(self, summary: Dict):
        """Add run summary to state."""
        self.state["runs"].append({
            "timestamp": datetime.now().isoformat(),
            **summary
        })
        # Keep only last 50 runs
        if len(self.state["runs"]) > 50:
            self.state["runs"] = self.state["runs"][-50:]

# ========================================
# CrossRef Fetcher
# ========================================

class CrossRefFetcher:
    """Fetches articles from CrossRef API with incremental update capability."""
    
    def __init__(self, state: FetchState):
        self.state = state
        self.session = requests.Session()
        self.session.headers.update(HEADERS_JSON)
        self.stats = {
            'articles_fetched': 0,
            'articles_new': 0,
            'articles_updated': 0,
            'citations_extracted': 0,
            'errors': 0,
            'by_journal': defaultdict(int),
            'by_year': defaultdict(int),
            'by_type': defaultdict(int)
        }
    
    def _make_request(self, url: str, params: Optional[Dict] = None) -> requests.Response:
        """Make HTTP request with retries."""
        for attempt in range(RETRY_ATTEMPTS):
            try:
                response = self.session.get(url, params=params, timeout=TIMEOUT)
                response.raise_for_status()
                return response
            except requests.exceptions.RequestException as e:
                if attempt == RETRY_ATTEMPTS - 1:
                    logger.error(f"Request failed after {RETRY_ATTEMPTS} attempts: {e}")
                    raise
                wait_time = RETRY_DELAY * (attempt + 1)
                logger.warning(f"Request failed (attempt {attempt + 1}/{RETRY_ATTEMPTS}): {e}. Retrying in {wait_time}s...")
                time.sleep(wait_time)
        raise RuntimeError(f"Failed to make request after {RETRY_ATTEMPTS} attempts")
    
    def fetch_journal_articles(
        self, 
        journal_name: str, 
        issns: List[str],
        from_indexed_date: Optional[str] = None,
        full_fetch: bool = False
    ) -> List[Dict]:
        """
        Fetch all articles for a journal from CrossRef.
        
        Args:
            journal_name: Name of the journal
            issns: List of ISSNs (print and online)
            from_indexed_date: Only fetch articles indexed after this date (YYYY-MM-DD)
            full_fetch: If True, fetch all articles regardless of state
        
        Returns:
            List of article metadata dictionaries
        """
        logger.info(f"\n{'='*60}")
        logger.info(f"Fetching: {journal_name}")
        logger.info(f"ISSNs: {', '.join(issns)}")
        
        # Determine date filter
        if not full_fetch and from_indexed_date is None:
            from_indexed_date = self.state.get_last_update(journal_name)
        
        if from_indexed_date:
            logger.info(f"Incremental update since: {from_indexed_date}")
        else:
            logger.info(f"Full fetch (no previous data)")
        
        # Build filter string
        filters = [f"issn:{issn}" for issn in issns]
        if from_indexed_date:
            # Use indexed date for incremental updates
            filters.append(f"from-indexed-date:{from_indexed_date}")
        
        filter_str = ",".join(filters)
        
        # Fetch with cursor pagination
        articles = []
        cursor = "*"
        total_results = None
        page_num = 0
        
        while cursor:
            page_num += 1
            params = {
                "filter": filter_str,
                "rows": ROWS_PER_PAGE,
                "cursor": cursor,
                "select": ",".join([
                    "DOI", "title", "author", "published", "published-print", 
                    "published-online", "container-title", "volume", "issue",
                    "page", "type", "abstract", "reference", "is-referenced-by-count",
                    "indexed", "created", "deposited", "subject", "ISSN",
                    "publisher", "license", "funder", "accepted"
                ])
            }
            
            try:
                response = self._make_request(CROSSREF_BASE, params)
                data = response.json()
                
                if total_results is None:
                    total_results = data.get("message", {}).get("total-results", 0)
                    logger.info(f"Total results: {total_results:,}")
                
                items = data.get("message", {}).get("items", [])
                
                # Break if no more items
                if not items:
                    logger.info(f"No more items, stopping pagination")
                    break
                
                for item in items:
                    processed = self._process_article(item, journal_name)
                    if processed:
                        articles.append(processed)
                        self.stats['articles_fetched'] += 1
                        self.stats['by_journal'][journal_name] += 1
                
                # Log progress
                if page_num % 5 == 0:
                    logger.info(f"  Page {page_num}: {len(articles)}/{total_results} articles")
                
                # Get next cursor
                cursor = data.get("message", {}).get("next-cursor")
                
                # Stop if we've collected all expected articles
                if total_results and len(articles) >= total_results:
                    logger.info(f"Collected all {total_results} articles, stopping")
                    break
                
                # Be polite (only if we have more pages)
                if cursor:
                    try:
                        time.sleep(REQUEST_DELAY)
                    except KeyboardInterrupt:
                        logger.warning("Sleep interrupted, continuing...")
                        pass
                
            except Exception as e:
                logger.error(f"Error fetching page for {journal_name}: {e}")
                self.stats['errors'] += 1
                cursor = None  # Stop pagination on error
        
        logger.info(f"Fetched {len(articles):,} articles for {journal_name}")
        
        # Cache raw data
        logger.info(f"Saving cache for {journal_name}...")
        cache_file = RAW_DIR / f"{journal_name.replace(' ', '_')}.jsonl"
        self._save_cache(articles, cache_file)
        logger.info(f"Cache saved successfully for {journal_name}")
        
        return articles
    
    def _process_article(self, item: Dict, journal_name: str) -> Optional[Dict]:
        """Process and validate a single article."""
        try:
            # Extract DOI
            doi = item.get("DOI", "").lower()
            if not doi:
                return None
            
            # Extract title
            title = item.get("title", [])
            if isinstance(title, list):
                title = " ".join(title)
            
            # Extract publication date
            pub_year = None
            pub_date = None
            for date_field in ["published-print", "published-online", "published"]:
                if date_field in item and item[date_field].get("date-parts"):
                    date_parts = item[date_field]["date-parts"][0]
                    if len(date_parts) >= 1:
                        pub_year = date_parts[0]
                        pub_date = "-".join(str(p) for p in date_parts)
                        break
            
            # Track by year
            if pub_year:
                self.stats['by_year'][pub_year] += 1
            
            # Track by type
            article_type = item.get("type", "unknown")
            self.stats['by_type'][article_type] += 1
            
            # Extract authors
            authors = []
            for author in item.get("author", []):
                author_data = {
                    "given": author.get("given", ""),
                    "family": author.get("family", ""),
                    "sequence": author.get("sequence", ""),
                    "affiliation": [
                        aff.get("name", "") 
                        for aff in author.get("affiliation", [])
                    ]
                }
                authors.append(author_data)
            
            # Extract abstract
            abstract = item.get("abstract", "")
            
            # Extract references/citations
            references = item.get("reference", [])
            cited_dois = []
            for ref in references:
                ref_doi = ref.get("DOI", "").lower()
                if ref_doi:
                    cited_dois.append(ref_doi)
            
            if cited_dois:
                self.stats['citations_extracted'] += len(cited_dois)
            
            # Extract indexed date (for tracking updates)
            indexed = item.get("indexed", {}).get("date-time", "")
            
            # Build comprehensive record
            record = {
                "doi": doi,
                "title": title,
                "journal": journal_name,
                "journal_short": AIS_BASKET_8[journal_name]["short_name"],
                "year": pub_year,
                "publication_date": pub_date,
                "container_title": item.get("container-title", []),
                "volume": item.get("volume", ""),
                "issue": item.get("issue", ""),
                "page": item.get("page", ""),
                "type": article_type,
                "authors": authors,
                "author_count": len(authors),
                "abstract": abstract,
                "references": cited_dois,
                "reference_count": len(cited_dois),
                "citation_count": item.get("is-referenced-by-count", 0),
                "publisher": item.get("publisher", ""),
                "issn": item.get("ISSN", []),
                "subject": item.get("subject", []),
                "license": item.get("license", []),
                "funder": item.get("funder", []),
                "indexed_date": indexed,
                "created_date": item.get("created", {}).get("date-time", ""),
                "deposited_date": item.get("deposited", {}).get("date-time", ""),
                "accepted_date": item.get("accepted", {}).get("date-parts", [[]])[0] if item.get("accepted") else None,
            }
            
            return record
            
        except Exception as e:
            logger.error(f"Error processing article: {e}")
            self.stats['errors'] += 1
            return None
    
    def _save_cache(self, articles: List[Dict], cache_file: Path):
        """Save articles to JSONL cache file."""
        try:
            logger.info(f"Writing {len(articles)} articles to {cache_file}...")
            sys.stdout.flush()
            with open(cache_file, 'w', encoding='utf-8') as f:
                for i, article in enumerate(articles):
                    f.write(json.dumps(article, ensure_ascii=False) + '\n')
                    if (i + 1) % 500 == 0:
                        logger.info(f"  Wrote {i+1}/{len(articles)} articles...")
                        sys.stdout.flush()
            logger.info(f"Cached {len(articles)} articles to {cache_file}")
            sys.stdout.flush()
        except Exception as e:
            logger.error(f"Error saving cache: {e}")
            sys.stdout.flush()
    
    def load_cache(self, cache_file: Path) -> List[Dict]:
        """Load articles from JSONL cache file."""
        articles = []
        if cache_file.exists():
            try:
                with open(cache_file, 'r', encoding='utf-8') as f:
                    for line in f:
                        if line.strip():
                            articles.append(json.loads(line))
                logger.info(f"Loaded {len(articles)} articles from cache {cache_file}")
            except Exception as e:
                logger.error(f"Error loading cache: {e}")
        return articles

# ========================================
# Data Processing
# ========================================

class DataProcessor:
    """Process and deduplicate fetched articles."""
    
    def __init__(self):
        self.stats = {
            'total_articles': 0,
            'unique_articles': 0,
            'duplicates_removed': 0
        }
    
    def deduplicate(self, articles: List[Dict]) -> List[Dict]:
        """Remove duplicate articles based on DOI."""
        seen_dois = set()
        unique_articles = []
        
        for article in articles:
            doi = article.get("doi", "").lower()
            if doi and doi not in seen_dois:
                seen_dois.add(doi)
                unique_articles.append(article)
            else:
                self.stats['duplicates_removed'] += 1
        
        self.stats['total_articles'] = len(articles)
        self.stats['unique_articles'] = len(unique_articles)
        
        logger.info(f"Deduplication: {len(articles)} -> {len(unique_articles)} articles")
        logger.info(f"Removed {self.stats['duplicates_removed']} duplicates")
        
        return unique_articles
    
    def to_dataframe(self, articles: List[Dict]) -> pd.DataFrame:
        """Convert articles to pandas DataFrame."""
        # Flatten for DataFrame
        flattened = []
        for article in articles:
            flat = {
                "doi": article["doi"],
                "title": article["title"],
                "journal": article["journal"],
                "journal_short": article["journal_short"],
                "year": article["year"],
                "publication_date": article["publication_date"],
                "volume": article["volume"],
                "issue": article["issue"],
                "page": article["page"],
                "type": article["type"],
                "author_count": article["author_count"],
                "abstract": article["abstract"],
                "reference_count": article["reference_count"],
                "citation_count": article["citation_count"],
                "publisher": article["publisher"],
                "indexed_date": article["indexed_date"],
            }
            flattened.append(flat)
        
        df = pd.DataFrame(flattened)
        
        # Convert types
        df["year"] = pd.to_numeric(df["year"], errors="coerce").astype("Int64")
        df["author_count"] = pd.to_numeric(df["author_count"], errors="coerce").astype("Int64")
        df["reference_count"] = pd.to_numeric(df["reference_count"], errors="coerce").astype("Int64")
        df["citation_count"] = pd.to_numeric(df["citation_count"], errors="coerce").astype("Int64")
        
        # Sort by year and journal
        df = df.sort_values(["year", "journal", "title"])
        df = df.reset_index(drop=True)
        
        return df

# ========================================
# Output Generation
# ========================================

class OutputGenerator:
    """Generate various output formats."""
    
    @staticmethod
    def save_parquet(df: pd.DataFrame, output_file: Path):
        """Save DataFrame as Parquet."""
        df.to_parquet(output_file, index=False, compression="snappy")
        logger.info(f"Saved Parquet: {output_file} ({len(df):,} articles)")
    
    @staticmethod
    def save_json(articles: List[Dict], output_file: Path):
        """Save articles as JSON."""
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(articles, f, indent=2, ensure_ascii=False)
        logger.info(f"Saved JSON: {output_file} ({len(articles):,} articles)")
    
    @staticmethod
    def save_bibtex(articles: List[Dict], output_file: Path):
        """Save articles as BibTeX."""
        with open(output_file, 'w', encoding='utf-8') as f:
            for article in articles:
                bibtex_entry = OutputGenerator._create_bibtex_entry(article)
                f.write(bibtex_entry + "\n\n")
        logger.info(f"Saved BibTeX: {output_file} ({len(articles):,} articles)")
    
    @staticmethod
    def _create_bibtex_entry(article: Dict) -> str:
        """Create BibTeX entry from article metadata."""
        # Create citation key
        first_author = ""
        if article.get("authors"):
            first_author = article["authors"][0].get("family", "Unknown")
        year = article.get("year", "")
        key = f"{first_author}{year}".replace(" ", "")
        
        # Build entry
        lines = [f"@article{{{key},"]
        
        # Required fields
        if article.get("doi"):
            lines.append(f"  doi = {{{article['doi']}}},")
        if article.get("title"):
            title = article['title'].replace('{', '').replace('}', '')
            lines.append(f"  title = {{{title}}},")
        
        # Authors
        if article.get("authors"):
            author_str = " and ".join([
                f"{a.get('given', '')} {a.get('family', '')}".strip()
                for a in article["authors"]
            ])
            lines.append(f"  author = {{{author_str}}},")
        
        # Journal
        if article.get("journal"):
            lines.append(f"  journal = {{{article['journal']}}},")
        
        # Year
        if year:
            lines.append(f"  year = {{{year}}},")
        
        # Optional fields
        if article.get("volume"):
            lines.append(f"  volume = {{{article['volume']}}},")
        if article.get("issue"):
            lines.append(f"  number = {{{article['issue']}}},")
        if article.get("page"):
            lines.append(f"  pages = {{{article['page']}}},")
        if article.get("abstract"):
            abstract = article['abstract'].replace('{', '').replace('}', '').replace('\n', ' ')
            lines.append(f"  abstract = {{{abstract}}},")
        if article.get("publisher"):
            lines.append(f"  publisher = {{{article['publisher']}}},")
        
        # Remove trailing comma from last line
        lines[-1] = lines[-1].rstrip(',')
        lines.append("}")
        
        return "\n".join(lines)
    
    @staticmethod
    def generate_summary_report(
        articles: List[Dict],
        fetcher_stats: Dict,
        processor_stats: Dict,
        output_file: Path
    ):
        """Generate summary report."""
        # Analyze articles
        df = pd.DataFrame([{
            "journal": a["journal"],
            "year": a["year"],
            "type": a["type"]
        } for a in articles])
        
        summary = {
            "generated_at": datetime.now().isoformat(),
            "total_articles": len(articles),
            "date_range": {
                "earliest": int(df["year"].min()) if not df.empty else None,
                "latest": int(df["year"].max()) if not df.empty else None
            },
            "by_journal": df.groupby("journal").size().to_dict(),
            "by_year": df.groupby("year").size().to_dict(),
            "by_type": df.groupby("type").size().to_dict(),
            "fetcher_stats": fetcher_stats,
            "processor_stats": processor_stats
        }
        
        with open(output_file, 'w') as f:
            json.dump(summary, f, indent=2)
        
        logger.info(f"Saved summary report: {output_file}")
        
        # Print summary
        print("\n" + "="*60)
        print("FETCH SUMMARY")
        print("="*60)
        print(f"Total articles: {summary['total_articles']:,}")
        print(f"Date range: {summary['date_range']['earliest']} - {summary['date_range']['latest']}")
        print(f"\nBy Journal:")
        for journal, count in sorted(summary['by_journal'].items(), key=lambda x: x[1], reverse=True):
            print(f"  {journal}: {count:,}")
        print(f"\nBy Year (last 5):")
        years = sorted(summary['by_year'].items(), key=lambda x: x[0], reverse=True)[:5]
        for year, count in years:
            print(f"  {year}: {count:,}")
        print("="*60)

# ========================================
# Main Execution
# ========================================

def main():
    parser = argparse.ArgumentParser(
        description="Fetch AIS Basket of 8 journals from CrossRef",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument(
        "--full",
        action="store_true",
        help="Perform full fetch (ignore state, fetch everything)"
    )
    parser.add_argument(
        "--journal",
        type=str,
        help="Fetch only specified journal (use full name)"
    )
    parser.add_argument(
        "--from-date",
        type=str,
        help="Fetch articles indexed from this date (YYYY-MM-DD)"
    )
    parser.add_argument(
        "--no-bibtex",
        action="store_true",
        help="Skip BibTeX output generation"
    )
    
    args = parser.parse_args()
    
    logger.info("="*60)
    logger.info("AIS Basket of 8 - CrossRef Fetcher v2.0")
    logger.info("="*60)
    logger.info(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Initialize components
    state = FetchState(STATE_FILE)
    fetcher = CrossRefFetcher(state)
    processor = DataProcessor()
    
    # Determine journals to fetch
    journals_to_fetch = AIS_BASKET_8
    if args.journal:
        if args.journal in AIS_BASKET_8:
            journals_to_fetch = {args.journal: AIS_BASKET_8[args.journal]}
        else:
            logger.error(f"Journal '{args.journal}' not found in AIS Basket of 8")
            logger.info(f"Available journals: {', '.join(AIS_BASKET_8.keys())}")
            return
    
    # Fetch articles
    all_articles = []
    for journal_name, journal_info in journals_to_fetch.items():
        articles = fetcher.fetch_journal_articles(
            journal_name,
            journal_info["issn"],
            from_indexed_date=args.from_date,
            full_fetch=args.full
        )
        all_articles.extend(articles)
        
        # Update state
        if articles:
            last_indexed = max(a.get("indexed_date", "") for a in articles)
            state.update_journal(journal_name, len(articles), last_indexed)
    
    # Process and deduplicate
    logger.info("\n" + "="*60)
    logger.info("Processing and deduplicating...")
    unique_articles = processor.deduplicate(all_articles)
    
    # Convert to DataFrame
    df = processor.to_dataframe(unique_articles)
    
    # Generate outputs
    logger.info("\n" + "="*60)
    logger.info("Generating outputs...")
    
    timestamp = datetime.now().strftime("%Y%m%d")
    
    # Save Parquet (main format)
    OutputGenerator.save_parquet(
        df,
        CLEAN_DIR / "ais_basket_corpus.parquet"
    )
    
    # Save JSON (with full metadata)
    OutputGenerator.save_json(
        unique_articles,
        CLEAN_DIR / "ais_basket_corpus.json"
    )
    
    # Save BibTeX (optional)
    if not args.no_bibtex:
        OutputGenerator.save_bibtex(
            unique_articles,
            OUTPUT_DIR / f"ais_basket_{timestamp}.bib"
        )
    
    # Generate summary report
    OutputGenerator.generate_summary_report(
        unique_articles,
        fetcher.stats,
        processor.stats,
        OUTPUT_DIR / f"fetch_summary_{timestamp}.json"
    )
    
    # Save state
    state.add_run_summary({
        "articles_fetched": len(all_articles),
        "unique_articles": len(unique_articles),
        "journals_updated": len(journals_to_fetch),
        "full_fetch": args.full
    })
    state.save()
    
    logger.info("\n" + "="*60)
    logger.info("Fetch complete!")
    logger.info(f"Log saved to: {LOG_FILE}")
    logger.info("="*60)

if __name__ == "__main__":
    main()
