#!/usr/bin/env python3
"""
Enhanced BibTeX fetcher with parallel processing, progress tracking, and citation DOIs.
"""

import argparse
import time
import sys
import re
import json
import requests
import concurrent.futures
from pathlib import Path
from datetime import datetime
from tqdm import tqdm
import pandas as pd
from urllib.parse import urlencode
from typing import Dict, List, Set, Optional
import logging
from rich.progress import Progress, TextColumn, BarColumn, TimeElapsedColumn, TimeRemainingColumn

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('output/fetch_progress.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

CROSSREF_BASE = "https://api.crossref.org/works"
HEADERS_JSON = {
    "User-Agent": "CarlosDennerBibTool/1.0 (mailto:carlosdenner@gmail.com)",
    "Accept": "application/json"
}
HEADERS_BIB = {**HEADERS_JSON, "Accept": "application/x-bibtex"}

# Journal ISSNs (print + online)
JOURNALS = {
    "Academy of Management Review": ["0363-7425", "1930-3807"],
    "MIS Quarterly": ["0276-7783", "2162-9730"],
    "Organization Science": ["1047-7039", "1526-5455"],
    "Information Systems Research": ["1047-7047", "1526-5536"],
}

# Date window
DATE_FROM = "2016-01-01"
DATE_UNTIL = "2025-12-31"

# Allowed Crossref types
ALLOWED_TYPES = {"journal-article", "journal-editorial", "article-commentary", "editorial", "posted-content"}

# Status to include (including early view/in-press)
INCLUDE_STATUSES = {"complete", "in-press", "ahead-of-print"}

# Simple heuristic to exclude book reviews
EXCLUDE_TITLE_REGEX = re.compile(r"(book review|review of|\[book review\])", re.IGNORECASE)

class CrossrefFetcher:
    def __init__(self, max_workers: int = 4, retry_attempts: int = 3, retry_delay: float = 1.0):
        self.max_workers = max_workers
        self.retry_attempts = retry_attempts
        self.retry_delay = retry_delay
        self.session = requests.Session()
        self.progress = Progress(
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            TimeElapsedColumn(),
            TimeRemainingColumn()
        )
        self.stats = {
            'articles_found': 0,
            'articles_processed': 0,
            'citations_found': 0,
            'errors': 0,
            'by_type': {},
            'by_status': {},
            'by_year': {}
        }

    def validate_metadata(self, metadata: Dict) -> Dict:
        """Validate and clean metadata fields for consistency."""
        if not metadata:
            return metadata
            
        # Ensure all date fields have consistent format
        date_fields = ['published-print', 'published-online', 'accepted', 'content-updated']
        for field in date_fields:
            if metadata.get(field):
                try:
                    date_parts = metadata[field].get('date-parts', [[]])[0]
                    # Ensure date parts are all integers
                    date_parts = [int(p) for p in date_parts if p]
                    if date_parts:
                        metadata[field]['date-parts'] = [date_parts]
                except (ValueError, AttributeError, IndexError):
                    metadata.pop(field, None)
        
        # Clean up author information
        if metadata.get('authors'):
            clean_authors = []
            for author in metadata['authors']:
                if author.get('given') or author.get('family'):
                    # Remove any authors without any name components
                    clean_author = {
                        'given': author.get('given', '').strip(),
                        'family': author.get('family', '').strip(),
                        'sequence': author.get('sequence', ''),
                        'affiliations': [aff.strip() for aff in author.get('affiliations', []) if aff and aff.strip()]
                    }
                    clean_authors.append(clean_author)
            metadata['authors'] = clean_authors
        
        # Ensure all DOIs are lowercase and valid format
        if metadata.get('cited-doi'):
            metadata['cited-doi'] = [
                doi.lower() for doi in metadata['cited-doi']
                if doi and re.match(r'^10\.\d{4,9}/[-._;()/:\w]+$', doi.lower())
            ]
        
        # Clean up subjects/keywords
        if metadata.get('subjects'):
            metadata['subjects'] = [
                subj.strip() for subj in metadata['subjects']
                if subj and subj.strip() and len(subj.strip()) > 1
            ]
        
        # Ensure numerical fields are integers
        int_fields = ['references-count', 'is-referenced-by-count']
        for field in int_fields:
            if metadata.get(field):
                try:
                    metadata[field] = int(metadata[field])
                except (ValueError, TypeError):
                    metadata.pop(field, None)
        
        # Ensure boolean fields are actually booleans
        bool_fields = ['has-full-text']
        for field in bool_fields:
            if field in metadata:
                metadata[field] = bool(metadata[field])
        
        # Clean up URLs in various fields
        url_fields = ['full-text-url', 'license']
        for field in url_fields:
            if metadata.get(field):
                if isinstance(metadata[field], list):
                    metadata[field] = [
                        url for url in metadata[field]
                        if url and re.match(r'^https?://', str(url))
                    ]
                elif isinstance(metadata[field], str):
                    if not re.match(r'^https?://', metadata[field]):
                        metadata.pop(field, None)
        
        return metadata

    def fetch_with_retry(self, url: str, params: Optional[Dict] = None, headers: Optional[Dict] = None) -> requests.Response:
        """Fetch URL with automatic retries on failure."""
        headers = headers or HEADERS_JSON
        for attempt in range(self.retry_attempts):
            try:
                response = self.session.get(url, params=params, headers=headers, timeout=30)
                response.raise_for_status()
                return response
            except requests.exceptions.RequestException as e:
                if attempt == self.retry_attempts - 1:
                    raise
                time.sleep(self.retry_delay * (attempt + 1))
                continue
        raise Exception("All retry attempts failed")

    def get_crossref_metadata(self, doi: str) -> Dict:
        """Fetch detailed metadata including references for a DOI."""
        url = f"{CROSSREF_BASE}/{doi}"
        try:
            resp = self.fetch_with_retry(url)
            data = resp.json()
            return data.get("message", {})
        except Exception as e:
            logging.error(f"Error fetching metadata for DOI {doi}: {str(e)}")
            return {}

    def collect_metadata_batch(self, issns: List[str]) -> List[Dict]:
        """Collect metadata for articles from specified journals in parallel."""
        filters = [
            f"from-pub-date:{DATE_FROM}",
            f"until-pub-date:{DATE_UNTIL}",
        ] + [f"issn:{i}" for i in issns]
        
        params = {
            "filter": ",".join(filters),
            "rows": 1000,
            "cursor": "*"
        }
        
        articles = []
        total_found = None
        
        with self.progress:
            task_id = self.progress.add_task("Fetching articles...", total=None)
            
            while True:
                try:
                    resp = self.fetch_with_retry(CROSSREF_BASE, params=params)
                    data = resp.json()
                    
                    if total_found is None:
                        total_found = data["message"]["total-results"]
                        self.progress.update(task_id, total=total_found)
                    
                    items = data["message"]["items"]
                    if not items:
                        break
                        
                    # Count articles by year
                    year_counts = {}
                    valid_items = []
                    for item in items:
                        if self.is_valid_article(item):
                            valid_items.append(item)
                            year = None
                            for date_field in ['published-print', 'published-online', 'published']:
                                if date_field in item and item[date_field].get('date-parts'):
                                    date_parts = item[date_field]['date-parts'][0]
                                    if len(date_parts) >= 1:
                                        year = date_parts[0]
                                        break
                            if year:
                                year_counts[year] = year_counts.get(year, 0) + 1
                    
                    self.stats['articles_found'] += len(valid_items)
                    if year_counts:
                        logging.info(f"Articles by year: {dict(sorted(year_counts.items()))}")
                        
                    # Process items in parallel
                    with concurrent.futures.ThreadPoolExecutor(max_workers=self.max_workers) as executor:
                        futures = []
                        for item in valid_items:
                            futures.append(executor.submit(self.process_article, item))
                        
                        for future in concurrent.futures.as_completed(futures):
                            try:
                                result = future.result()
                                if result:
                                    articles.append(result)
                                    self.stats['articles_processed'] += 1
                            except Exception as e:
                                self.stats['errors'] += 1
                                logging.error(f"Error processing article: {str(e)}")
                    
                    self.progress.update(task_id, advance=len(items))
                    
                    cursor = data["message"]["next-cursor"]
                    if not cursor:
                        break
                    params["cursor"] = cursor
                    
                except Exception as e:
                    self.stats['errors'] += 1
                    logging.error(f"Error in batch collection: {str(e)}")
                    break
        
        return articles

    def is_valid_article(self, item: Dict) -> bool:
        """Check if an article meets our inclusion criteria."""
        typ = (item.get("type") or "").lower()
        title = " ".join(item.get("title") or [])
        status = item.get("publication-status", "unknown").lower()
        
        # Track article type
        self.stats['by_type'][typ] = self.stats['by_type'].get(typ, 0) + 1
        
        # Track publication status
        self.stats['by_status'][status] = self.stats['by_status'].get(status, 0) + 1
        
        # Check publication date
        pub_date = None
        for date_field in ['published-print', 'published-online', 'published']:
            if date_field in item and item[date_field].get('date-parts'):
                date_parts = item[date_field]['date-parts'][0]
                if len(date_parts) >= 1:
                    year = date_parts[0]
                    if 2016 <= year <= 2025:
                        pub_date = year
                        self.stats['by_year'][year] = self.stats['by_year'].get(year, 0) + 1
                        break
        
        if not pub_date:
            return False
        
        if typ not in ALLOWED_TYPES:
            if typ == "journal-article" and EXCLUDE_TITLE_REGEX.search(title or ""):
                return False
            elif typ != "journal-article":
                return False
        
        return "DOI" in item

    def process_article(self, item: Dict) -> Optional[Dict]:
        """Process a single article, fetching additional metadata and citations."""
        try:
            doi = item["DOI"]
            detailed_metadata = self.get_crossref_metadata(doi)
            
            # Extract citation DOIs and references
            references = detailed_metadata.get("reference", [])
            citation_dois = [ref.get("DOI", "").lower() for ref in references if "DOI" in ref]
            self.stats['citations_found'] += len(citation_dois)
            
            # Extract and clean abstract - handle both string and structured formats
            abstract = detailed_metadata.get("abstract", "")
            if isinstance(abstract, dict):
                # Some publishers return structured abstracts
                abstract = abstract.get("value", "") or next(iter(abstract.values()), "")
            
            # Process authors and their affiliations
            authors = []
            for author in detailed_metadata.get("author", []):
                author_info = {
                    "given": author.get("given", ""),
                    "family": author.get("family", ""),
                    "sequence": author.get("sequence", ""),
                    "affiliations": [aff.get("name", "") for aff in author.get("affiliation", [])]
                }
                authors.append(author_info)
            
            # Prepare enhanced metadata
            enhanced_metadata = {
                "cited-doi": citation_dois,
                "abstract": abstract,
                "authors": authors,
                "publication-status": detailed_metadata.get("publication-status", ""),
                "published-print": detailed_metadata.get("published-print", {}),
                "published-online": detailed_metadata.get("published-online", {}),
                "accepted": detailed_metadata.get("accepted", {}),
                "content-version": detailed_metadata.get("content-version", ""),
                "content-domain": detailed_metadata.get("content-domain", {}),
                "content-updated": detailed_metadata.get("content-updated", {}),
                "published-status": detailed_metadata.get("published-status", ""),
                "published-other": detailed_metadata.get("published-other", {}),
                "publisher-location": detailed_metadata.get("publisher-location", ""),
                "issn-type": detailed_metadata.get("issn-type", []),
                "archive": detailed_metadata.get("archive", []),
                "license": detailed_metadata.get("license", []),
                "link": detailed_metadata.get("link", []),
                "alternative-id": detailed_metadata.get("alternative-id", []),
                "update-to": detailed_metadata.get("update-to", []),
                "update-policy": detailed_metadata.get("update-policy", []),
                "funding": detailed_metadata.get("funder", []),
                "assertion": detailed_metadata.get("assertion", []),
                "references-count": detailed_metadata.get("references-count", 0),
                "is-referenced-by-count": detailed_metadata.get("is-referenced-by-count", 0),
                "has-full-text": detailed_metadata.get("has-full-text", False),
                "full-text-status": detailed_metadata.get("full-text-status", ""),
                "full-text-type": detailed_metadata.get("full-text-type", ""),
                "full-text-url": detailed_metadata.get("full-text-url", ""),
                "source": detailed_metadata.get("source", ""),
                "prefix": detailed_metadata.get("prefix", ""),
                "original-title": detailed_metadata.get("original-title", []),
                "short-title": detailed_metadata.get("short-title", []),
                "container-title": detailed_metadata.get("container-title", []),
                "group-title": detailed_metadata.get("group-title", ""),
                "language": detailed_metadata.get("language", "")
            }
            
            # Collect keywords from multiple sources
            keywords = set()
            keywords.update(detailed_metadata.get("subject", []))
            keywords.update(item.get("subject", []))
            keywords.update(detailed_metadata.get("keywords", []))
            enhanced_metadata["subjects"] = list(keywords)
            
            # Validate and clean the metadata
            enhanced_metadata = self.validate_metadata(enhanced_metadata)
            
            # Update the item with the validated metadata
            item.update(enhanced_metadata)
            return item
            
        except Exception as e:
            logging.error(f"Error processing article {item.get('DOI', 'unknown')}: {str(e)}")
            return None

    def clean_text(self, text: str) -> str:
        """Clean text for BibTeX entry while preserving content between tags."""
        if not text:
            return text
        
        # First, clean any special BibTeX characters
        text = (text.replace('"', "'")
                   .replace("{", "\\{")
                   .replace("}", "\\}")
                   .replace("_", "\\_")
                   .replace("%", "\\%")
                   .replace("$", "\\$")
                   .replace("#", "\\#")
                   .replace("&", "\\&")
                   .replace("~", "\\~")
                   .replace("^", "\\^"))
        
        # Handle JATS and other XML tags while preserving content
        # First remove JATS-specific tags
        pattern = r"<jats:[^>]*>(.*?)</jats:[^>]*>"
        while re.search(pattern, text):
            text = re.sub(pattern, r"\1", text)
            
        # Then handle any remaining XML tags
        pattern = r"<[^>]+>(.*?)</[^>]+>"
        while re.search(pattern, text):
            text = re.sub(pattern, r"\1", text)
        
        # Remove any remaining standalone tags
        text = re.sub(r"<[^>]+/>", "", text)
        text = re.sub(r"<[^>]+>", "", text)
        
        # Clean up newlines, tabs, and extra spaces
        text = re.sub(r"[\n\t\r]+", " ", text)
        text = " ".join(text.split())
        
        return text.strip()

    def enhance_bibtex(self, bib_entry: str, metadata: Dict) -> str:
        """Add enhanced metadata to BibTeX entry."""
        if not bib_entry.strip():
            return bib_entry
        
        # Remove the final newlines and closing brace
        entry = bib_entry.rstrip("\n").rstrip(" ").rstrip("}")
        
        # Add abstract if available
        if metadata.get("abstract"):
            abstract = self.clean_text(metadata["abstract"])
            if abstract:  # Only add if non-empty after cleaning
                entry += f",\n  abstract = {{{abstract}}}"
        
        # Add subjects/keywords if available
        subjects = metadata.get("subjects", [])
        if subjects:
            subjects = [s for s in subjects if s]  # Remove empty strings
            keywords = self.clean_text("; ".join(subjects))
            if keywords:  # Only add if non-empty after cleaning
                entry += f",\n  keywords = {{{keywords}}}"
        
        # Add citation DOIs if available
        if metadata.get("cited-doi"):
            cited_dois = [doi for doi in metadata["cited-doi"] if doi]  # Remove empty DOIs
            if cited_dois:  # Only add if there are valid DOIs
                cited_dois_str = "; ".join(cited_dois)
                entry += f',\n  cited-doi = {{{cited_dois_str}}}'
        
        # Add author affiliations
        if metadata.get("authors"):
            affiliations = []
            for author in metadata["authors"]:
                if author.get("affiliations"):
                    auth_str = f"{author['family']}, {author['given']}"
                    for aff in author["affiliations"]:
                        if aff:
                            affiliations.append(f"{auth_str} ({aff})")
            if affiliations:
                aff_str = self.clean_text("; ".join(affiliations))
                entry += f',\n  author-affiliations = {{{aff_str}}}'
        
        # Add publication dates and status
        for date_type in ['published-print', 'published-online', 'accepted']:
            if metadata.get(date_type, {}).get('date-parts'):
                date_parts = metadata[date_type]['date-parts'][0]
                date_str = '-'.join(str(p) for p in date_parts)
                entry += f',\n  {date_type}-date = {{{date_str}}}'
        
        # Add publication status
        if metadata.get("publication-status"):
            entry += f',\n  publication-status = {{{metadata["publication-status"]}}}'
        
        # Add content information
        if metadata.get("content-version"):
            entry += f',\n  content-version = {{{metadata["content-version"]}}}'
        
        # Add publisher location
        if metadata.get("publisher-location"):
            entry += f',\n  publisher-location = {{{metadata["publisher-location"]}}}'
        
        # Add funding information
        if metadata.get("funding"):
            funders = []
            for funder in metadata["funding"]:
                if funder.get("name"):
                    funders.append(funder["name"])
                    if funder.get("award"):
                        funders[-1] += f" (Award: {funder['award']})"
            if funders:
                funder_str = self.clean_text("; ".join(funders))
                entry += f',\n  funding = {{{funder_str}}}'
        
        # Add citation metrics
        if metadata.get("references-count"):
            entry += f',\n  references-count = {{{metadata["references-count"]}}}'
        if metadata.get("is-referenced-by-count"):
            entry += f',\n  times-cited = {{{metadata["is-referenced-by-count"]}}}'
        
        # Add full text availability info
        if metadata.get("has-full-text"):
            entry += f',\n  has-full-text = {{true}}'
            if metadata.get("full-text-status"):
                entry += f',\n  full-text-status = {{{metadata["full-text-status"]}}}'
        
        # Add language
        if metadata.get("language"):
            entry += f',\n  language = {{{metadata["language"]}}}'
        
        # Add source repository
        if metadata.get("source"):
            entry += f',\n  source = {{{metadata["source"]}}}'
        
        # Add alternative IDs
        if metadata.get("alternative-id"):
            alt_ids = "; ".join(metadata["alternative-id"])
            entry += f',\n  alternative-id = {{{alt_ids}}}'
        
        # Add license information
        if metadata.get("license"):
            licenses = []
            for lic in metadata["license"]:
                if lic.get("URL"):
                    licenses.append(lic["URL"])
            if licenses:
                license_str = "; ".join(licenses)
                entry += f',\n  license = {{{license_str}}}'
        
        # Close the entry
        return entry + "\n}\n"

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="refs_2016_2025.bib", help="Output .bib path")
    ap.add_argument("--workers", type=int, default=4, help="Number of parallel workers")
    ap.add_argument("--pause", type=float, default=0.1, help="Pause (s) between DOI requests")
    ap.add_argument("--max", type=int, default=0, help="Max DOIs overall (0 = no limit)")
    args = ap.parse_args()

    # Initialize fetcher
    fetcher = CrossrefFetcher(max_workers=args.workers)
    start_time = time.time()
    
    # Create output directories
    Path("output").mkdir(exist_ok=True)
    
    # Collect articles from all journals
    all_articles = []
    for jname, issns in JOURNALS.items():
        logging.info(f"Querying Crossref for {jname}...")
        articles = fetcher.collect_metadata_batch(issns)
        logging.info(f"Found {len(articles)} candidate articles for {jname}")
        all_articles.extend(articles)

    # De-duplicate across journals based on DOI
    seen_dois = set()
    unique_articles = []
    for article in all_articles:
        doi = article.get("DOI", "").lower()
        if doi and doi not in seen_dois:
            seen_dois.add(doi)
            unique_articles.append(article)
    
    if args.max > 0:
        unique_articles = unique_articles[:args.max]

    # Sort articles by journal for more predictable output
    unique_articles.sort(key=lambda x: x.get('container-title', [''])[0] if x.get('container-title') else '')

    logging.info(f"Fetching enhanced BibTeX for {len(unique_articles)} articles...")

    # Write BibTeX entries
    with open(args.out, "w", encoding="utf-8") as fh:
        with fetcher.progress as progress:
            task_id = progress.add_task("Generating BibTeX entries...", total=len(unique_articles))
            
            for article in unique_articles:
                try:
                    doi = article["DOI"]
                    # Get base BibTeX entry
                    bib = fetcher.fetch_with_retry(f"https://doi.org/{doi}", headers=HEADERS_BIB).text.strip()
                    
                    # Enhance BibTeX with abstract, keywords, and citations
                    enhanced_bib = fetcher.enhance_bibtex(bib, article)
                    fh.write(enhanced_bib + "\n")
                    
                except Exception as e:
                    fetcher.stats['errors'] += 1
                    logging.error(f"Failed {doi}: {e}")
                
                progress.update(task_id, advance=1)
                time.sleep(args.pause)

    # Generate summary report
    elapsed_time = time.time() - start_time
    summary = {
        'Articles Found': fetcher.stats['articles_found'],
        'Articles Processed': fetcher.stats['articles_processed'],
        'Citations Found': fetcher.stats['citations_found'],
        'Errors': fetcher.stats['errors'],
        'Processing Time': f"{elapsed_time:.1f} seconds",
        'Average Time per Article': f"{elapsed_time/len(unique_articles):.1f} seconds"
    }
    
    with open('output/fetch_summary.json', 'w') as f:
        json.dump(summary, f, indent=2)
    
    logging.info(f"Wrote {args.out}")
    logging.info("\nSummary:")
    logging.info(f"Basic Stats:")
    for key in ['Articles Found', 'Articles Processed', 'Citations Found', 'Errors', 'Processing Time', 'Average Time per Article']:
        logging.info(f"{key}: {summary[key]}")
    
    logging.info("\nArticles by Type:")
    for typ, count in sorted(fetcher.stats['by_type'].items()):
        logging.info(f"{typ}: {count}")
    
    logging.info("\nArticles by Status:")
    for status, count in sorted(fetcher.stats['by_status'].items()):
        logging.info(f"{status}: {count}")
    
    logging.info("\nArticles by Year:")
    for year, count in sorted(fetcher.stats['by_year'].items()):
        logging.info(f"{year}: {count}")

if __name__ == "__main__":
    main()