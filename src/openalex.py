"""
OpenAlex API integration for citation enrichment.
Fetches citation data and referenced works for papers with DOIs.
"""

import requests
import time
import json
import pandas as pd
import pathlib
from typing import Dict, List, Optional, Union
import logging
from urllib.parse import quote
from concurrent.futures import ThreadPoolExecutor, as_completed
import pickle

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

BASE_URL = "https://api.openalex.org/works/doi:"
CACHE_DIR = pathlib.Path("data/openalex_cache")


class OpenAlexClient:
    """Client for OpenAlex API with caching and rate limiting."""
    
    def __init__(
        self,
        cache_dir: str = "data/openalex_cache",
        rate_limit: float = 0.1,
        timeout: int = 30,
        max_retries: int = 3
    ):
        """
        Initialize OpenAlex client.
        
        Parameters
        ----------
        cache_dir : str
            Directory for caching responses
        rate_limit : float
            Seconds to wait between requests
        timeout : int
            Request timeout in seconds
        max_retries : int
            Maximum number of retries for failed requests
        """
        self.cache_dir = pathlib.Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.rate_limit = rate_limit
        self.timeout = timeout
        self.max_retries = max_retries
        
        # Session for connection pooling
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Literature-Analyzer/1.0 (mailto:research@example.com)'
        })
        
    def _get_cache_path(self, doi: str) -> pathlib.Path:
        """Get cache file path for a DOI."""
        # Clean DOI for filename
        clean_doi = doi.replace("/", "_").replace(":", "_")
        return self.cache_dir / f"{clean_doi}.json"
    
    def _load_from_cache(self, doi: str) -> Optional[Dict]:
        """Load cached response for a DOI."""
        cache_path = self._get_cache_path(doi)
        if cache_path.exists():
            try:
                with open(cache_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                logger.warning(f"Failed to load cache for {doi}: {e}")
        return None
    
    def _save_to_cache(self, doi: str, data: Dict):
        """Save response to cache."""
        cache_path = self._get_cache_path(doi)
        try:
            with open(cache_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            logger.warning(f"Failed to save cache for {doi}: {e}")
    
    def fetch_work(self, doi: str) -> Optional[Dict]:
        """
        Fetch work data from OpenAlex API.
        
        Parameters
        ----------
        doi : str
            DOI of the work
            
        Returns
        -------
        Dict or None
            Work data from OpenAlex, or None if not found
        """
        # Check cache first
        cached = self._load_from_cache(doi)
        if cached is not None:
            return cached
        
        # Clean DOI
        clean_doi = doi.strip().lower()
        if not clean_doi:
            return None
        
        # Build URL
        url = BASE_URL + quote(clean_doi)
        
        # Retry loop
        for attempt in range(self.max_retries):
            try:
                # Rate limiting
                time.sleep(self.rate_limit)
                
                # Make request
                response = self.session.get(url, timeout=self.timeout)
                
                if response.status_code == 200:
                    data = response.json()
                    self._save_to_cache(doi, data)
                    return data
                elif response.status_code == 404:
                    logger.debug(f"Work not found in OpenAlex: {doi}")
                    # Cache negative result
                    self._save_to_cache(doi, {"error": "not_found"})
                    return None
                else:
                    logger.warning(f"HTTP {response.status_code} for {doi}")
                    
            except requests.exceptions.RequestException as e:
                logger.warning(f"Request failed for {doi} (attempt {attempt+1}): {e}")
                if attempt < self.max_retries - 1:
                    time.sleep(2 ** attempt)  # Exponential backoff
        
        logger.error(f"Failed to fetch {doi} after {self.max_retries} attempts")
        return None
    
    def fetch_multiple(
        self,
        dois: List[str],
        max_workers: int = 5,
        progress_callback: Optional[callable] = None
    ) -> Dict[str, Optional[Dict]]:
        """
        Fetch multiple works in parallel.
        
        Parameters
        ----------
        dois : List[str]
            List of DOIs to fetch
        max_workers : int
            Maximum number of concurrent requests
        progress_callback : callable, optional
            Function to call with progress updates
            
        Returns
        -------
        Dict[str, Dict]
            Mapping from DOI to work data
        """
        logger.info(f"Fetching {len(dois)} works from OpenAlex with {max_workers} workers")
        
        results = {}
        completed = 0
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Submit all tasks
            future_to_doi = {
                executor.submit(self.fetch_work, doi): doi
                for doi in dois
            }
            
            # Collect results
            for future in as_completed(future_to_doi):
                doi = future_to_doi[future]
                try:
                    result = future.result()
                    results[doi] = result
                except Exception as e:
                    logger.error(f"Error fetching {doi}: {e}")
                    results[doi] = None
                
                completed += 1
                if progress_callback:
                    progress_callback(completed, len(dois))
                
                if completed % 100 == 0:
                    logger.info(f"Completed {completed}/{len(dois)} requests")
        
        logger.info(f"Fetched {sum(1 for v in results.values() if v is not None)}/{len(dois)} works successfully")
        return results


def extract_work_metadata(work_data: Dict) -> Dict:
    """
    Extract relevant metadata from OpenAlex work data.
    
    Parameters
    ----------
    work_data : Dict
        Raw work data from OpenAlex
        
    Returns
    -------
    Dict
        Extracted metadata
    """
    if not work_data or "error" in work_data:
        return {}
    
    # Extract basic info
    metadata = {
        "openalex_id": work_data.get("id", ""),
        "title_oa": work_data.get("title", ""),
        "publication_year": work_data.get("publication_year"),
        "cited_by_count": work_data.get("cited_by_count", 0),
        "is_retracted": work_data.get("is_retracted", False),
        "is_paratext": work_data.get("is_paratext", False),
    }
    
    # Host venue
    host_venue = work_data.get("host_venue", {})
    if host_venue:
        metadata.update({
            "host_venue_name": host_venue.get("display_name", ""),
            "host_venue_type": host_venue.get("type", ""),
            "host_venue_issn": host_venue.get("issn_l", ""),
        })
    
    # Referenced works (outgoing citations)
    referenced_works = work_data.get("referenced_works", [])
    metadata["referenced_works"] = referenced_works
    metadata["references_count_oa"] = len(referenced_works)
    
    # Concepts/topics
    concepts = work_data.get("concepts", [])
    if concepts:
        # Top 3 concepts
        top_concepts = sorted(concepts, key=lambda x: x.get("score", 0), reverse=True)[:3]
        metadata["concepts"] = [c.get("display_name", "") for c in top_concepts]
        metadata["concept_scores"] = [c.get("score", 0) for c in top_concepts]
    
    # Authors
    authorships = work_data.get("authorships", [])
    if authorships:
        authors_oa = []
        institutions = []
        for auth in authorships:
            author = auth.get("author", {})
            if author:
                authors_oa.append(author.get("display_name", ""))
            
            # Institutions
            for inst in auth.get("institutions", []):
                institutions.append(inst.get("display_name", ""))
        
        metadata["authors_oa"] = authors_oa
        metadata["institutions"] = list(set(institutions))  # Unique institutions
    
    # Open access info
    open_access = work_data.get("open_access", {})
    if open_access:
        metadata.update({
            "is_oa": open_access.get("is_oa", False),
            "oa_status": open_access.get("oa_status", ""),
            "oa_url": open_access.get("oa_url", ""),
        })
    
    return metadata


def enrich_dataframe(
    df: pd.DataFrame,
    doi_column: str = "doi",
    client: Optional[OpenAlexClient] = None,
    max_workers: int = 5
) -> pd.DataFrame:
    """
    Enrich dataframe with OpenAlex metadata.
    
    Parameters
    ----------
    df : pd.DataFrame
        Input dataframe with DOIs
    doi_column : str
        Name of DOI column
    client : OpenAlexClient, optional
        OpenAlex client (will create default if None)
    max_workers : int
        Number of parallel workers
        
    Returns
    -------
    pd.DataFrame
        Enriched dataframe with OpenAlex metadata
    """
    if client is None:
        client = OpenAlexClient()
    
    # Get unique DOIs
    dois = df[doi_column].dropna().unique().tolist()
    logger.info(f"Enriching {len(dois)} unique DOIs")
    
    # Progress callback
    def progress(completed, total):
        if completed % 50 == 0 or completed == total:
            logger.info(f"Progress: {completed}/{total} ({completed/total*100:.1f}%)")
    
    # Fetch data
    results = client.fetch_multiple(dois, max_workers=max_workers, progress_callback=progress)
    
    # Extract metadata
    metadata_records = []
    for doi, work_data in results.items():
        metadata = extract_work_metadata(work_data or {})
        metadata["doi"] = doi
        metadata_records.append(metadata)
    
    # Create metadata dataframe
    metadata_df = pd.DataFrame(metadata_records)
    
    # Merge with original dataframe
    enriched_df = df.merge(metadata_df, on=doi_column, how="left")
    
    # Log statistics
    n_enriched = enriched_df["openalex_id"].notna().sum()
    logger.info(f"Successfully enriched {n_enriched}/{len(df)} papers ({n_enriched/len(df)*100:.1f}%)")
    
    return enriched_df


def save_cache_summary(cache_dir: str = "data/openalex_cache") -> Dict:
    """
    Generate summary of cached OpenAlex data.
    
    Parameters
    ----------
    cache_dir : str
        Cache directory path
        
    Returns
    -------
    Dict
        Cache summary statistics
    """
    cache_path = pathlib.Path(cache_dir)
    
    if not cache_path.exists():
        return {"total_files": 0, "successful": 0, "errors": 0}
    
    cache_files = list(cache_path.glob("*.json"))
    successful = 0
    errors = 0
    
    for file_path in cache_files:
        try:
            with open(file_path, 'r') as f:
                data = json.load(f)
                if "error" in data:
                    errors += 1
                else:
                    successful += 1
        except Exception:
            errors += 1
    
    summary = {
        "total_files": len(cache_files),
        "successful": successful,
        "errors": errors,
        "cache_dir": str(cache_path)
    }
    
    logger.info(f"Cache summary: {successful} successful, {errors} errors, {len(cache_files)} total")
    return summary


if __name__ == "__main__":
    # Test the OpenAlex client
    test_dois = [
        "10.5465/amr.2024.0210",
        "10.5465/amr.2016.0264",
        "10.1234/invalid.doi"  # This should fail
    ]
    
    client = OpenAlexClient(rate_limit=0.1)
    
    logger.info("Testing individual fetches...")
    for doi in test_dois:
        result = client.fetch_work(doi)
        if result:
            metadata = extract_work_metadata(result)
            print(f"\n{doi}:")
            print(f"  Title: {metadata.get('title_oa', 'N/A')}")
            print(f"  Citations: {metadata.get('cited_by_count', 0)}")
            print(f"  References: {metadata.get('references_count_oa', 0)}")
        else:
            print(f"\n{doi}: Not found")
    
    logger.info("\nTesting batch fetch...")
    results = client.fetch_multiple(test_dois[:2], max_workers=2)
    print(f"Batch results: {len(results)} items")
    
    # Cache summary
    summary = save_cache_summary()
    print(f"\nCache summary: {summary}")
