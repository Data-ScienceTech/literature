"""
Temporal burst detection for research streams analysis.
Implements Kleinberg burst detection and simpler prevalence-based methods.
"""

import numpy as np
import pandas as pd
from typing import List, Dict, Tuple, Optional
from collections import Counter, defaultdict
import logging
from scipy import stats
import re

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def extract_terms_from_text(text: str, min_length: int = 3, max_length: int = 20) -> List[str]:
    """
    Extract terms from text for burst analysis.
    
    Parameters
    ----------
    text : str
        Input text
    min_length : int
        Minimum term length
    max_length : int
        Maximum term length
        
    Returns
    -------
    List[str]
        List of extracted terms
    """
    if not text or pd.isna(text):
        return []
    
    # Simple term extraction (can be enhanced with NLP)
    text = text.lower()
    
    # Remove common patterns
    text = re.sub(r'[^\w\s]', ' ', text)
    text = re.sub(r'\s+', ' ', text).strip()
    
    # Extract words
    words = text.split()
    
    # Filter by length and remove common stopwords
    stopwords = {
        'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with',
        'by', 'from', 'up', 'about', 'into', 'through', 'during', 'before', 'after',
        'above', 'below', 'between', 'among', 'this', 'that', 'these', 'those', 'is',
        'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'do', 'does',
        'did', 'will', 'would', 'could', 'should', 'may', 'might', 'must', 'can', 'cannot'
    }
    
    terms = []
    for word in words:
        if (min_length <= len(word) <= max_length and 
            word not in stopwords and 
            word.isalpha()):
            terms.append(word)
    
    # Also extract bigrams
    for i in range(len(words) - 1):
        bigram = f"{words[i]} {words[i+1]}"
        if (min_length <= len(bigram) <= max_length and 
            words[i] not in stopwords and 
            words[i+1] not in stopwords):
            terms.append(bigram)
    
    return terms


def compute_cluster_prevalence(df: pd.DataFrame, time_col: str = 'year', cluster_col: str = 'cluster') -> pd.DataFrame:
    """
    Compute cluster prevalence over time.
    
    Parameters
    ----------
    df : pd.DataFrame
        Input dataframe with time and cluster columns
    time_col : str
        Name of time column
    cluster_col : str
        Name of cluster column
        
    Returns
    -------
    pd.DataFrame
        Prevalence table with time as index and clusters as columns
    """
    logger.info(f"Computing cluster prevalence over {time_col}")
    
    # Filter valid data
    valid_df = df.dropna(subset=[time_col, cluster_col]).copy()
    
    # Create prevalence table
    prevalence = valid_df.groupby([time_col, cluster_col]).size().unstack(fill_value=0)
    
    # Ensure all years are present
    if len(prevalence) > 1:
        year_range = range(int(prevalence.index.min()), int(prevalence.index.max()) + 1)
        prevalence = prevalence.reindex(year_range, fill_value=0)
    
    logger.info(f"Prevalence table shape: {prevalence.shape}")
    return prevalence


def detect_prevalence_bursts(
    prevalence_df: pd.DataFrame, 
    z_threshold: float = 2.0,
    min_duration: int = 2
) -> Dict[int, List[Tuple[int, int, float]]]:
    """
    Detect bursts in cluster prevalence using z-score method.
    
    Parameters
    ----------
    prevalence_df : pd.DataFrame
        Prevalence table from compute_cluster_prevalence
    z_threshold : float
        Z-score threshold for burst detection
    min_duration : int
        Minimum burst duration in time periods
        
    Returns
    -------
    Dict[int, List[Tuple[int, int, float]]]
        Dictionary mapping cluster_id to list of (start_year, end_year, max_z_score)
    """
    logger.info(f"Detecting prevalence bursts with z_threshold={z_threshold}")
    
    bursts = {}
    
    for cluster in prevalence_df.columns:
        cluster_counts = prevalence_df[cluster]
        
        # Skip if not enough data
        if len(cluster_counts) < 3 or cluster_counts.sum() < 5:
            continue
        
        # Compute rolling statistics
        mean_count = cluster_counts.mean()
        std_count = cluster_counts.std()
        
        if std_count == 0:
            continue
        
        # Z-scores
        z_scores = (cluster_counts - mean_count) / std_count
        
        # Find burst periods
        cluster_bursts = []
        in_burst = False
        burst_start = None
        burst_max_z = 0
        
        for year, z_score in z_scores.items():
            if z_score >= z_threshold:
                if not in_burst:
                    # Start new burst
                    in_burst = True
                    burst_start = year
                    burst_max_z = z_score
                else:
                    # Continue burst
                    burst_max_z = max(burst_max_z, z_score)
            else:
                if in_burst:
                    # End burst
                    burst_duration = year - burst_start
                    if burst_duration >= min_duration:
                        cluster_bursts.append((burst_start, year - 1, burst_max_z))
                    in_burst = False
        
        # Handle burst that continues to end
        if in_burst:
            burst_duration = z_scores.index[-1] - burst_start + 1
            if burst_duration >= min_duration:
                cluster_bursts.append((burst_start, z_scores.index[-1], burst_max_z))
        
        if cluster_bursts:
            bursts[cluster] = cluster_bursts
    
    logger.info(f"Found bursts in {len(bursts)} clusters")
    return bursts


def compute_term_frequencies(df: pd.DataFrame, text_col: str = 'text', time_col: str = 'year') -> pd.DataFrame:
    """
    Compute term frequencies over time.
    
    Parameters
    ----------
    df : pd.DataFrame
        Input dataframe
    text_col : str
        Name of text column
    time_col : str
        Name of time column
        
    Returns
    -------
    pd.DataFrame
        Term frequency table with time as index and terms as columns
    """
    logger.info("Computing term frequencies over time")
    
    # Extract terms from all texts
    all_terms = Counter()
    term_by_year = defaultdict(Counter)
    
    valid_df = df.dropna(subset=[text_col, time_col]).copy()
    
    for _, row in valid_df.iterrows():
        year = row[time_col]
        text = row[text_col]
        
        terms = extract_terms_from_text(str(text))
        
        for term in terms:
            all_terms[term] += 1
            term_by_year[year][term] += 1
    
    # Keep only terms that appear multiple times
    min_frequency = max(3, len(valid_df) // 100)  # At least 3 or 1% of documents
    frequent_terms = [term for term, count in all_terms.items() if count >= min_frequency]
    
    logger.info(f"Found {len(frequent_terms)} frequent terms (min_freq={min_frequency})")
    
    # Create frequency matrix
    years = sorted(term_by_year.keys())
    freq_matrix = []
    
    for year in years:
        year_counts = [term_by_year[year][term] for term in frequent_terms]
        freq_matrix.append(year_counts)
    
    freq_df = pd.DataFrame(freq_matrix, index=years, columns=frequent_terms)
    freq_df = freq_df.fillna(0)
    
    return freq_df


def detect_term_bursts(
    freq_df: pd.DataFrame,
    method: str = 'zscore',
    z_threshold: float = 2.0,
    min_duration: int = 2
) -> Dict[str, List[Tuple[int, int, float]]]:
    """
    Detect term bursts using various methods.
    
    Parameters
    ----------
    freq_df : pd.DataFrame
        Term frequency table from compute_term_frequencies
    method : str
        Burst detection method ('zscore', 'relative_growth')
    z_threshold : float
        Threshold for burst detection
    min_duration : int
        Minimum burst duration
        
    Returns
    -------
    Dict[str, List[Tuple[int, int, float]]]
        Dictionary mapping term to list of (start_year, end_year, strength)
    """
    logger.info(f"Detecting term bursts using {method} method")
    
    bursts = {}
    
    for term in freq_df.columns:
        term_counts = freq_df[term]
        
        # Skip terms with insufficient data
        if term_counts.sum() < 5 or len(term_counts.nonzero()[0]) < 3:
            continue
        
        if method == 'zscore':
            # Z-score method
            mean_count = term_counts.mean()
            std_count = term_counts.std()
            
            if std_count == 0:
                continue
            
            z_scores = (term_counts - mean_count) / std_count
            
            # Find bursts
            term_bursts = []
            in_burst = False
            burst_start = None
            burst_max_z = 0
            
            for year, z_score in z_scores.items():
                if z_score >= z_threshold:
                    if not in_burst:
                        in_burst = True
                        burst_start = year
                        burst_max_z = z_score
                    else:
                        burst_max_z = max(burst_max_z, z_score)
                else:
                    if in_burst:
                        burst_duration = year - burst_start
                        if burst_duration >= min_duration:
                            term_bursts.append((burst_start, year - 1, burst_max_z))
                        in_burst = False
            
            # Handle ongoing burst
            if in_burst:
                burst_duration = z_scores.index[-1] - burst_start + 1
                if burst_duration >= min_duration:
                    term_bursts.append((burst_start, z_scores.index[-1], burst_max_z))
            
        elif method == 'relative_growth':
            # Relative growth method
            term_bursts = []
            
            for i in range(1, len(term_counts)):
                current_year = term_counts.index[i]
                prev_count = term_counts.iloc[i-1]
                curr_count = term_counts.iloc[i]
                
                if prev_count > 0 and curr_count > 0:
                    growth_rate = (curr_count - prev_count) / prev_count
                    if growth_rate >= z_threshold:  # Use threshold as growth rate
                        term_bursts.append((current_year, current_year, growth_rate))
        
        if term_bursts:
            bursts[term] = term_bursts
    
    logger.info(f"Found bursts for {len(bursts)} terms")
    return bursts


def analyze_citation_bursts(df: pd.DataFrame) -> Dict:
    """
    Analyze bursts in citation patterns.
    
    Parameters
    ----------
    df : pd.DataFrame
        DataFrame with citation data
        
    Returns
    -------
    Dict
        Citation burst analysis results
    """
    logger.info("Analyzing citation bursts")
    
    results = {}
    
    # Analyze cited works bursts (if available)
    if 'cited_doi' in df.columns:
        # Extract individual DOIs from cited_doi field
        cited_counts_by_year = defaultdict(Counter)
        
        for _, row in df.iterrows():
            year = row.get('year')
            cited_dois = row.get('cited_doi', '')
            
            if year and cited_dois:
                # Parse cited DOIs (assuming semicolon separated)
                dois = [doi.strip() for doi in str(cited_dois).split(';') if doi.strip()]
                
                for doi in dois:
                    cited_counts_by_year[year][doi] += 1
        
        # Find most cited works per year
        top_cited_by_year = {}
        for year, doi_counts in cited_counts_by_year.items():
            if doi_counts:
                top_cited = doi_counts.most_common(10)
                top_cited_by_year[year] = top_cited
        
        results['top_cited_by_year'] = top_cited_by_year
    
    # Analyze journal publication bursts
    if 'journal' in df.columns and 'year' in df.columns:
        journal_by_year = df.groupby(['year', 'journal']).size().unstack(fill_value=0)
        
        # Find journals with significant year-over-year growth
        journal_bursts = {}
        for journal in journal_by_year.columns:
            journal_counts = journal_by_year[journal]
            
            # Calculate year-over-year growth rates
            growth_rates = journal_counts.pct_change().fillna(0)
            
            # Find significant growth periods
            high_growth_years = growth_rates[growth_rates > 1.0]  # 100% growth
            
            if len(high_growth_years) > 0:
                journal_bursts[journal] = high_growth_years.to_dict()
        
        results['journal_bursts'] = journal_bursts
    
    return results


def summarize_bursts(
    cluster_bursts: Dict,
    term_bursts: Dict,
    df: pd.DataFrame
) -> pd.DataFrame:
    """
    Create summary table of all detected bursts.
    
    Parameters
    ----------
    cluster_bursts : Dict
        Cluster burst results
    term_bursts : Dict
        Term burst results
    df : pd.DataFrame
        Original dataframe for context
        
    Returns
    -------
    pd.DataFrame
        Summary table of bursts
    """
    logger.info("Creating burst summary")
    
    burst_records = []
    
    # Add cluster bursts
    for cluster_id, bursts in cluster_bursts.items():
        for start_year, end_year, strength in bursts:
            # Get cluster info
            cluster_papers = df[df.get('cluster', -1) == cluster_id]
            n_papers = len(cluster_papers)
            
            burst_records.append({
                'type': 'cluster',
                'item': f'Cluster {cluster_id}',
                'start_year': start_year,
                'end_year': end_year,
                'duration': end_year - start_year + 1,
                'strength': strength,
                'n_papers': n_papers,
                'description': f'Research cluster with {n_papers} papers'
            })
    
    # Add term bursts
    for term, bursts in term_bursts.items():
        for start_year, end_year, strength in bursts:
            burst_records.append({
                'type': 'term',
                'item': term,
                'start_year': start_year,
                'end_year': end_year,
                'duration': end_year - start_year + 1,
                'strength': strength,
                'n_papers': None,
                'description': f'Term: "{term}"'
            })
    
    # Create summary dataframe
    summary_df = pd.DataFrame(burst_records)
    
    if len(summary_df) > 0:
        # Sort by strength
        summary_df = summary_df.sort_values('strength', ascending=False).reset_index(drop=True)
    
    logger.info(f"Created burst summary with {len(summary_df)} bursts")
    return summary_df


if __name__ == "__main__":
    # Test burst detection with synthetic data
    logger.info("Testing burst detection with synthetic data")
    
    np.random.seed(42)
    
    # Create test data
    years = list(range(2015, 2025))
    clusters = [0, 1, 2]
    
    test_data = []
    for year in years:
        for cluster in clusters:
            # Simulate burst in cluster 1 around 2020-2022
            if cluster == 1 and 2020 <= year <= 2022:
                n_papers = np.random.poisson(15)  # Burst
            else:
                n_papers = np.random.poisson(5)   # Normal
            
            for _ in range(n_papers):
                test_data.append({
                    'year': year,
                    'cluster': cluster,
                    'text': f'research paper about topic {cluster} in year {year} with some random text'
                })
    
    df = pd.DataFrame(test_data)
    
    # Test cluster prevalence
    prevalence = compute_cluster_prevalence(df)
    print(f"\nPrevalence table shape: {prevalence.shape}")
    print(prevalence)
    
    # Test prevalence bursts
    cluster_bursts = detect_prevalence_bursts(prevalence, z_threshold=1.5)
    print(f"\nCluster bursts: {cluster_bursts}")
    
    # Test term frequencies
    term_freq = compute_term_frequencies(df)
    print(f"\nTerm frequency table shape: {term_freq.shape}")
    
    # Test term bursts
    term_bursts = detect_term_bursts(term_freq, z_threshold=1.5)
    print(f"\nTerm bursts: {len(term_bursts)} terms with bursts")
    
    # Test summary
    summary = summarize_bursts(cluster_bursts, term_bursts, df)
    print(f"\nBurst summary:")
    print(summary.head())
