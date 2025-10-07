#!/usr/bin/env python3
"""
Enrich AIS Basket corpus with OpenAlex data.

This script enriches the CrossRef-fetched corpus with:
- Missing abstracts (especially for Taylor & Francis journals)
- Keywords/subjects (CrossRef doesn't provide these)
- Better author affiliations
- Additional metadata

Strategy:
1. Load CrossRef corpus
2. For each article, try to find it in OpenAlex by DOI
3. Merge the best data from both sources
4. Save enriched corpus
"""

import json
import pandas as pd
import numpy as np
import requests
import time
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from collections import defaultdict
import logging
from tqdm import tqdm

# Configuration
OPENALEX_BASE = "https://api.openalex.org"
REQUEST_DELAY = 0.2  # Be polite to OpenAlex
BATCH_SIZE = 50  # OpenAlex supports batch queries
TIMEOUT = 30
RETRY_ATTEMPTS = 3
EMAIL = "carlosdenner@gmail.com"  # For polite pool

# File paths
DATA_DIR = Path("data")
CLEAN_DIR = DATA_DIR / "clean"
CROSSREF_CORPUS = CLEAN_DIR / "ais_basket_corpus.json"
ENRICHED_CORPUS = CLEAN_DIR / "ais_basket_corpus_enriched.json"
ENRICHED_PARQUET = CLEAN_DIR / "ais_basket_corpus_enriched.parquet"
CACHE_DIR = DATA_DIR / "raw" / "openalex_cache"
CACHE_DIR.mkdir(parents=True, exist_ok=True)
OUTPUT_DIR = Path("output")

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(OUTPUT_DIR / f"enrichment_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class OpenAlexEnricher:
    """Enriches CrossRef data with OpenAlex metadata."""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": f"AIS-Basket-Enricher/1.0 (mailto:{EMAIL})"
        })
        self.stats = {
            'total_articles': 0,
            'openalex_found': 0,
            'enriched_abstracts': 0,
            'enriched_keywords': 0,
            'enriched_affiliations': 0,
            'api_calls': 0,
            'cache_hits': 0,
            'errors': 0
        }
        self.cache = {}
        self._load_cache()
    
    def _load_cache(self):
        """Load cached OpenAlex responses."""
        cache_file = CACHE_DIR / "openalex_enrichment.json"
        if cache_file.exists():
            try:
                with open(cache_file, 'r') as f:
                    self.cache = json.load(f)
                logger.info(f"Loaded {len(self.cache)} cached OpenAlex responses")
            except Exception as e:
                logger.warning(f"Could not load cache: {e}")
    
    def _save_cache(self):
        """Save cache to disk."""
        cache_file = CACHE_DIR / "openalex_enrichment.json"
        try:
            with open(cache_file, 'w') as f:
                json.dump(self.cache, f)
            logger.info(f"Saved {len(self.cache)} responses to cache")
        except Exception as e:
            logger.error(f"Could not save cache: {e}")
    
    def _make_request(self, url: str, params: Optional[Dict] = None) -> Optional[Dict]:
        """Make request to OpenAlex API with retries."""
        for attempt in range(RETRY_ATTEMPTS):
            try:
                if EMAIL:
                    if params is None:
                        params = {}
                    params['mailto'] = EMAIL
                
                response = self.session.get(url, params=params, timeout=TIMEOUT)
                response.raise_for_status()
                self.stats['api_calls'] += 1
                return response.json()
                
            except requests.exceptions.RequestException as e:
                if attempt == RETRY_ATTEMPTS - 1:
                    logger.error(f"Request failed after {RETRY_ATTEMPTS} attempts: {e}")
                    self.stats['errors'] += 1
                    return None
                
                wait_time = (attempt + 1) * 2
                logger.warning(f"Request failed (attempt {attempt + 1}), retrying in {wait_time}s...")
                time.sleep(wait_time)
        
        return None
    
    def find_openalex_work(self, doi: str) -> Optional[Dict]:
        """Find work in OpenAlex by DOI."""
        # Check cache first
        cache_key = f"doi:{doi.lower()}"
        if cache_key in self.cache:
            self.stats['cache_hits'] += 1
            return self.cache[cache_key]
        
        # Query OpenAlex
        url = f"{OPENALEX_BASE}/works"
        params = {
            "filter": f"doi:{doi}",
            "select": ",".join([
                "id", "doi", "title", "display_name", "publication_year",
                "authorships", "primary_location", "abstract_inverted_index",
                "concepts", "keywords", "language", "type", "cited_by_count",
                "referenced_works"
            ])
        }
        
        data = self._make_request(url, params)
        if data and data.get("results"):
            work = data["results"][0]
            self.cache[cache_key] = work
            return work
        
        # Cache negative result
        self.cache[cache_key] = None
        return None
    
    def batch_find_openalex_works(self, dois: List[str]) -> Dict[str, Optional[Dict]]:
        """Find multiple works in OpenAlex using batch query."""
        results = {}
        
        # Check cache first
        uncached_dois = []
        for doi in dois:
            cache_key = f"doi:{doi.lower()}"
            if cache_key in self.cache:
                self.stats['cache_hits'] += 1
                results[doi] = self.cache[cache_key]
            else:
                uncached_dois.append(doi)
        
        if not uncached_dois:
            return results
        
        # Query OpenAlex for uncached DOIs
        doi_filter = "|".join(uncached_dois)
        url = f"{OPENALEX_BASE}/works"
        params = {
            "filter": f"doi:{doi_filter}",
            "per-page": min(200, len(uncached_dois)),
            "select": ",".join([
                "id", "doi", "title", "display_name", "publication_year",
                "authorships", "primary_location", "abstract_inverted_index",
                "concepts", "keywords", "language", "type", "cited_by_count",
                "referenced_works"
            ])
        }
        
        data = self._make_request(url, params)
        if data and data.get("results"):
            for work in data["results"]:
                work_doi = work.get("doi", "").replace("https://doi.org/", "").lower()
                if work_doi:
                    results[work_doi] = work
                    self.cache[f"doi:{work_doi}"] = work
        
        # Cache negative results
        for doi in uncached_dois:
            if doi.lower() not in results:
                results[doi] = None
                self.cache[f"doi:{doi.lower()}"] = None
        
        return results
    
    def reconstruct_abstract(self, inverted_index: Dict) -> Optional[str]:
        """Reconstruct abstract from OpenAlex inverted index."""
        if not inverted_index:
            return None
        
        try:
            # Find max position
            max_pos = 0
            for positions in inverted_index.values():
                if positions:
                    max_pos = max(max_pos, max(positions))
            
            # Build token array
            tokens = [""] * (max_pos + 1)
            for token, positions in inverted_index.items():
                for pos in positions:
                    if 0 <= pos < len(tokens):
                        tokens[pos] = token
            
            # Join and clean
            abstract = " ".join(token for token in tokens if token)
            abstract = " ".join(abstract.split())  # Normalize whitespace
            
            return abstract if abstract else None
            
        except Exception as e:
            logger.warning(f"Error reconstructing abstract: {e}")
            return None
    
    def extract_keywords(self, openalex_work: Dict) -> List[str]:
        """Extract keywords/concepts from OpenAlex work."""
        keywords = set()
        
        # From concepts
        concepts = openalex_work.get("concepts", [])
        for concept in concepts:
            if concept.get("level", 0) <= 2:  # Only high-level concepts
                name = concept.get("display_name", "")
                if name and len(name) > 2:
                    keywords.add(name)
        
        # From keywords field (if available)
        work_keywords = openalex_work.get("keywords", [])
        for kw in work_keywords:
            if isinstance(kw, dict):
                name = kw.get("display_name", "")
            else:
                name = str(kw)
            
            if name and len(name) > 2:
                keywords.add(name)
        
        return sorted(list(keywords))
    
    def extract_author_affiliations(self, openalex_work: Dict) -> List[Dict]:
        """Extract author data with better affiliations from OpenAlex."""
        authors = []
        
        authorships = openalex_work.get("authorships", [])
        for authorship in authorships:
            author_info = authorship.get("author", {})
            institutions = authorship.get("institutions", [])
            
            author = {
                "given": author_info.get("display_name", "").split()[-1] if author_info.get("display_name") else "",
                "family": author_info.get("display_name", "").split()[0] if author_info.get("display_name") else "",
                "sequence": "first" if authorship.get("author_position") == "first" else "additional",
                "affiliation": [inst.get("display_name", "") for inst in institutions if inst.get("display_name")]
            }
            
            # Try to split name better
            full_name = author_info.get("display_name", "")
            if full_name:
                parts = full_name.split()
                if len(parts) >= 2:
                    author["given"] = " ".join(parts[:-1])
                    author["family"] = parts[-1]
                elif len(parts) == 1:
                    author["family"] = parts[0]
                    author["given"] = ""
            
            authors.append(author)
        
        return authors
    
    def enrich_article(self, crossref_article: Dict, openalex_work: Optional[Dict]) -> Dict:
        """Enrich CrossRef article with OpenAlex data."""
        enriched = crossref_article.copy()
        
        if not openalex_work:
            return enriched
        
        # Track what we enriched
        enriched["_enrichment"] = {
            "source": "openalex",
            "openalex_id": openalex_work.get("id", ""),
            "enriched_fields": []
        }
        
        # Enrich abstract if missing or poor quality
        crossref_abstract = crossref_article.get("abstract", "")
        if not crossref_abstract or len(crossref_abstract.split()) < 20:
            openalex_abstract = self.reconstruct_abstract(
                openalex_work.get("abstract_inverted_index", {})
            )
            if openalex_abstract and len(openalex_abstract.split()) >= 20:
                enriched["abstract"] = openalex_abstract
                enriched["_enrichment"]["enriched_fields"].append("abstract")
                self.stats['enriched_abstracts'] += 1
        
        # Add keywords (CrossRef doesn't have these)
        keywords = self.extract_keywords(openalex_work)
        if keywords:
            enriched["subject"] = keywords
            enriched["_enrichment"]["enriched_fields"].append("keywords")
            self.stats['enriched_keywords'] += 1
        
        # Enhance author affiliations if poor in CrossRef
        crossref_authors = crossref_article.get("authors", [])
        has_good_affiliations = any(
            auth.get("affiliation") and len(auth["affiliation"]) > 0 
            for auth in crossref_authors
        )
        
        if not has_good_affiliations:
            openalex_authors = self.extract_author_affiliations(openalex_work)
            if openalex_authors:
                # Merge: use CrossRef names but OpenAlex affiliations
                merged_authors = []
                for i, crossref_auth in enumerate(crossref_authors):
                    if i < len(openalex_authors):
                        merged_auth = crossref_auth.copy()
                        if openalex_authors[i]["affiliation"]:
                            merged_auth["affiliation"] = openalex_authors[i]["affiliation"]
                        merged_authors.append(merged_auth)
                    else:
                        merged_authors.append(crossref_auth)
                
                # Add any extra OpenAlex authors
                if len(openalex_authors) > len(crossref_authors):
                    merged_authors.extend(openalex_authors[len(crossref_authors):])
                
                enriched["authors"] = merged_authors
                enriched["_enrichment"]["enriched_fields"].append("affiliations")
                self.stats['enriched_affiliations'] += 1
        
        # Add additional OpenAlex metadata
        enriched["openalex_cited_by_count"] = openalex_work.get("cited_by_count", 0)
        enriched["openalex_type"] = openalex_work.get("type", "")
        
        return enriched
    
    def enrich_corpus(self, articles: List[Dict]) -> List[Dict]:
        """Enrich entire corpus with OpenAlex data."""
        logger.info(f"Starting enrichment of {len(articles)} articles...")
        self.stats['total_articles'] = len(articles)
        
        enriched_articles = []
        
        # Process in batches
        for i in tqdm(range(0, len(articles), BATCH_SIZE), desc="Enriching articles"):
            batch = articles[i:i + BATCH_SIZE]
            batch_dois = [article["doi"] for article in batch]
            
            # Get OpenAlex works for this batch
            openalex_works = self.batch_find_openalex_works(batch_dois)
            
            # Enrich each article in the batch
            for article in batch:
                doi = article["doi"]
                openalex_work = openalex_works.get(doi.lower())
                
                if openalex_work:
                    self.stats['openalex_found'] += 1
                
                enriched_article = self.enrich_article(article, openalex_work)
                enriched_articles.append(enriched_article)
            
            # Be polite
            time.sleep(REQUEST_DELAY)
            
            # Save cache periodically
            if i % (BATCH_SIZE * 10) == 0:
                self._save_cache()
        
        # Final cache save
        self._save_cache()
        
        logger.info("Enrichment complete!")
        self._log_stats()
        
        return enriched_articles
    
    def _log_stats(self):
        """Log enrichment statistics."""
        logger.info("\n" + "="*60)
        logger.info("ENRICHMENT STATISTICS")
        logger.info("="*60)
        logger.info(f"Total articles: {self.stats['total_articles']:,}")
        logger.info(f"Found in OpenAlex: {self.stats['openalex_found']:,} ({self.stats['openalex_found']/self.stats['total_articles']*100:.1f}%)")
        logger.info(f"Enriched abstracts: {self.stats['enriched_abstracts']:,}")
        logger.info(f"Enriched keywords: {self.stats['enriched_keywords']:,}")
        logger.info(f"Enriched affiliations: {self.stats['enriched_affiliations']:,}")
        logger.info(f"API calls made: {self.stats['api_calls']:,}")
        logger.info(f"Cache hits: {self.stats['cache_hits']:,}")
        logger.info(f"Errors: {self.stats['errors']:,}")
        logger.info("="*60)

def load_crossref_corpus() -> List[Dict]:
    """Load the CrossRef corpus."""
    logger.info(f"Loading CrossRef corpus from {CROSSREF_CORPUS}...")
    
    with open(CROSSREF_CORPUS, 'r', encoding='utf-8') as f:
        articles = json.load(f)
    
    logger.info(f"✓ Loaded {len(articles):,} articles")
    return articles

def save_enriched_corpus(articles: List[Dict]):
    """Save enriched corpus in multiple formats."""
    logger.info("Saving enriched corpus...")
    
    # Save JSON
    with open(ENRICHED_CORPUS, 'w', encoding='utf-8') as f:
        json.dump(articles, f, indent=2, ensure_ascii=False)
    logger.info(f"✓ Saved JSON: {ENRICHED_CORPUS}")
    
    # Create DataFrame and save Parquet
    df_records = []
    for article in articles:
        record = {
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
            "has_openalex_enrichment": "_enrichment" in article,
            "enriched_fields": ",".join(article.get("_enrichment", {}).get("enriched_fields", [])),
            "openalex_cited_by_count": article.get("openalex_cited_by_count", 0),
            "keyword_count": len(article.get("subject", [])),
            "has_keywords": len(article.get("subject", [])) > 0
        }
        df_records.append(record)
    
    df = pd.DataFrame(df_records)
    df.to_parquet(ENRICHED_PARQUET, index=False, compression="snappy")
    logger.info(f"✓ Saved Parquet: {ENRICHED_PARQUET}")

def generate_enrichment_report(articles: List[Dict], enricher: OpenAlexEnricher):
    """Generate enrichment report."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_file = OUTPUT_DIR / f"enrichment_report_{timestamp}.json"
    
    # Calculate improvements
    total = len(articles)
    enriched_count = sum(1 for a in articles if "_enrichment" in a)
    
    before_abstracts = sum(1 for a in articles if a.get("abstract") and len(a["abstract"].split()) >= 20)
    before_keywords = sum(1 for a in articles if a.get("subject") and len(a["subject"]) > 0)
    
    # Count final state
    final_abstracts = sum(1 for a in articles if a.get("abstract") and len(a["abstract"].split()) >= 20)
    final_keywords = sum(1 for a in articles if a.get("subject") and len(a["subject"]) > 0)
    
    report = {
        "timestamp": datetime.now().isoformat(),
        "total_articles": total,
        "enriched_articles": enriched_count,
        "enrichment_rate": enriched_count / total * 100,
        "improvements": {
            "abstracts": {
                "before": before_abstracts,
                "after": final_abstracts,
                "improvement": final_abstracts - before_abstracts
            },
            "keywords": {
                "before": before_keywords,
                "after": final_keywords,
                "improvement": final_keywords - before_keywords
            }
        },
        "stats": enricher.stats
    }
    
    with open(report_file, 'w') as f:
        json.dump(report, f, indent=2)
    
    logger.info(f"✓ Enrichment report saved: {report_file}")
    
    # Print summary
    print("\n" + "="*70)
    print("ENRICHMENT SUMMARY")
    print("="*70)
    print(f"Total articles: {total:,}")
    print(f"Articles enriched: {enriched_count:,} ({enriched_count/total*100:.1f}%)")
    print(f"\nImprovements:")
    print(f"  Abstracts: {before_abstracts:,} → {final_abstracts:,} (+{final_abstracts-before_abstracts:,})")
    print(f"  Keywords:  {before_keywords:,} → {final_keywords:,} (+{final_keywords-before_keywords:,})")
    print("="*70)

def main():
    """Main enrichment function."""
    logger.info("\n" + "="*70)
    logger.info("AIS BASKET CORPUS ENRICHMENT")
    logger.info("="*70)
    logger.info(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    # Load CrossRef corpus
    articles = load_crossref_corpus()
    
    # Initialize enricher
    enricher = OpenAlexEnricher()
    
    # Enrich corpus
    enriched_articles = enricher.enrich_corpus(articles)
    
    # Save enriched corpus
    save_enriched_corpus(enriched_articles)
    
    # Generate report
    generate_enrichment_report(enriched_articles, enricher)
    
    logger.info("\n✓ Enrichment complete!")

if __name__ == "__main__":
    main()