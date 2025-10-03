"""
Reference Publication Year Spectroscopy (RPYS) analysis.
Analyzes the temporal distribution of cited references to identify foundational periods.
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional
from collections import Counter, defaultdict
import logging
import re
from scipy import signal
from scipy.stats import zscore

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def extract_cited_years(cited_doi_string: str, openalex_data: Optional[Dict] = None) -> List[int]:
    """
    Extract publication years from cited references.
    
    Parameters
    ----------
    cited_doi_string : str
        String containing cited DOIs (semicolon separated)
    openalex_data : Dict, optional
        OpenAlex data mapping DOIs to metadata
        
    Returns
    -------
    List[int]
        List of publication years of cited references
    """
    years = []
    
    if not cited_doi_string or pd.isna(cited_doi_string):
        return years
    
    # Parse DOIs
    dois = [doi.strip() for doi in str(cited_doi_string).split(';') if doi.strip()]
    
    for doi in dois:
        year = None
        
        # Try to get year from OpenAlex data if available
        if openalex_data and doi in openalex_data:
            work_data = openalex_data[doi]
            if isinstance(work_data, dict):
                year = work_data.get('publication_year')
        
        # If no OpenAlex data, try to extract from DOI patterns (limited success)
        if year is None:
            # Some DOIs contain year information
            year_match = re.search(r'(19|20)\d{2}', doi)
            if year_match:
                potential_year = int(year_match.group(0))
                if 1900 <= potential_year <= 2030:
                    year = potential_year
        
        if year and isinstance(year, (int, float)) and 1900 <= year <= 2030:
            years.append(int(year))
    
    return years


def compute_rpys_spectrum(
    df: pd.DataFrame,
    cited_col: str = 'cited_doi',
    openalex_data: Optional[Dict] = None,
    min_year: int = 1900,
    max_year: Optional[int] = None
) -> pd.Series:
    """
    Compute RPYS spectrum from cited references.
    
    Parameters
    ----------
    df : pd.DataFrame
        DataFrame with cited references
    cited_col : str
        Column name containing cited DOIs
    openalex_data : Dict, optional
        OpenAlex metadata for cited works
    min_year : int
        Minimum year to include
    max_year : int, optional
        Maximum year to include (default: current year)
        
    Returns
    -------
    pd.Series
        RPYS spectrum with years as index and citation counts as values
    """
    logger.info("Computing RPYS spectrum from cited references")
    
    if max_year is None:
        max_year = pd.Timestamp.now().year
    
    # Collect all cited years
    all_cited_years = []
    
    valid_df = df.dropna(subset=[cited_col])
    logger.info(f"Processing {len(valid_df)} papers with cited references")
    
    for _, row in valid_df.iterrows():
        cited_string = row[cited_col]
        cited_years = extract_cited_years(cited_string, openalex_data)
        all_cited_years.extend(cited_years)
    
    # Filter years
    filtered_years = [y for y in all_cited_years if min_year <= y <= max_year]
    
    logger.info(f"Extracted {len(filtered_years)} cited references from {len(all_cited_years)} total")
    
    # Count citations per year
    year_counts = Counter(filtered_years)
    
    # Create complete year range
    if year_counts:
        year_range = range(min(year_counts.keys()), max(year_counts.keys()) + 1)
    else:
        year_range = range(min_year, max_year + 1)
    
    # Create spectrum
    spectrum = pd.Series(
        [year_counts.get(year, 0) for year in year_range],
        index=list(year_range),
        name='citations'
    )
    
    logger.info(f"RPYS spectrum covers {len(spectrum)} years ({spectrum.index.min()}-{spectrum.index.max()})")
    logger.info(f"Total citations: {spectrum.sum()}, Non-zero years: {(spectrum > 0).sum()}")
    
    return spectrum


def detect_rpys_peaks(
    spectrum: pd.Series,
    method: str = 'prominence',
    prominence_threshold: float = None,
    z_threshold: float = 2.0,
    min_distance: int = 5
) -> List[Tuple[int, int, float]]:
    """
    Detect peaks in RPYS spectrum.
    
    Parameters
    ----------
    spectrum : pd.Series
        RPYS spectrum from compute_rpys_spectrum
    method : str
        Peak detection method ('prominence', 'zscore', 'percentile')
    prominence_threshold : float, optional
        Prominence threshold for peak detection
    z_threshold : float
        Z-score threshold for peak detection
    min_distance : int
        Minimum distance between peaks
        
    Returns
    -------
    List[Tuple[int, int, float]]
        List of (year, citation_count, prominence/z_score) for each peak
    """
    logger.info(f"Detecting RPYS peaks using {method} method")
    
    if len(spectrum) == 0 or spectrum.sum() == 0:
        logger.warning("Empty or zero spectrum, no peaks to detect")
        return []
    
    years = spectrum.index.values
    counts = spectrum.values
    
    peaks = []
    
    if method == 'prominence':
        # Use scipy's find_peaks with prominence
        if prominence_threshold is None:
            prominence_threshold = np.std(counts)
        
        peak_indices, properties = signal.find_peaks(
            counts,
            prominence=prominence_threshold,
            distance=min_distance
        )
        
        for i, peak_idx in enumerate(peak_indices):
            year = years[peak_idx]
            count = counts[peak_idx]
            prominence = properties['prominences'][i]
            peaks.append((year, count, prominence))
    
    elif method == 'zscore':
        # Z-score based peak detection
        z_scores = zscore(counts)
        
        # Find peaks above threshold
        for i, (year, count, z_score) in enumerate(zip(years, counts, z_scores)):
            if z_score >= z_threshold:
                # Check if it's a local maximum
                is_peak = True
                for j in range(max(0, i - min_distance), min(len(counts), i + min_distance + 1)):
                    if j != i and counts[j] > count:
                        is_peak = False
                        break
                
                if is_peak:
                    peaks.append((year, count, z_score))
    
    elif method == 'percentile':
        # Percentile-based peak detection
        threshold = np.percentile(counts[counts > 0], 90)  # 90th percentile of non-zero values
        
        for i, (year, count) in enumerate(zip(years, counts)):
            if count >= threshold:
                # Check if it's a local maximum
                is_peak = True
                for j in range(max(0, i - min_distance), min(len(counts), i + min_distance + 1)):
                    if j != i and counts[j] > count:
                        is_peak = False
                        break
                
                if is_peak:
                    percentile_score = (count - np.min(counts)) / (np.max(counts) - np.min(counts))
                    peaks.append((year, count, percentile_score))
    
    # Sort peaks by strength (descending)
    peaks.sort(key=lambda x: x[2], reverse=True)
    
    logger.info(f"Detected {len(peaks)} peaks")
    return peaks


def analyze_rpys_periods(
    spectrum: pd.Series,
    peaks: List[Tuple[int, int, float]],
    window_size: int = 10
) -> Dict:
    """
    Analyze foundational periods around RPYS peaks.
    
    Parameters
    ----------
    spectrum : pd.Series
        RPYS spectrum
    peaks : List[Tuple[int, int, float]]
        Detected peaks
    window_size : int
        Window size around peaks for analysis
        
    Returns
    -------
    Dict
        Analysis of foundational periods
    """
    logger.info("Analyzing RPYS foundational periods")
    
    periods = {}
    
    for i, (peak_year, peak_count, peak_strength) in enumerate(peaks):
        # Define window around peak
        start_year = peak_year - window_size // 2
        end_year = peak_year + window_size // 2
        
        # Get spectrum window
        window_spectrum = spectrum[(spectrum.index >= start_year) & (spectrum.index <= end_year)]
        
        if len(window_spectrum) == 0:
            continue
        
        # Analyze period
        period_analysis = {
            'peak_year': peak_year,
            'peak_count': peak_count,
            'peak_strength': peak_strength,
            'window_start': start_year,
            'window_end': end_year,
            'window_total_citations': window_spectrum.sum(),
            'window_mean_citations': window_spectrum.mean(),
            'window_std_citations': window_spectrum.std(),
            'window_peak_ratio': peak_count / window_spectrum.sum() if window_spectrum.sum() > 0 else 0,
            'years_with_citations': (window_spectrum > 0).sum(),
            'concentration_index': window_spectrum.std() / window_spectrum.mean() if window_spectrum.mean() > 0 else 0
        }
        
        # Find secondary peaks in window
        window_peaks = []
        for year, count in window_spectrum.items():
            if year != peak_year and count > window_spectrum.mean() + window_spectrum.std():
                window_peaks.append((year, count))
        
        period_analysis['secondary_peaks'] = window_peaks
        
        periods[f'period_{i+1}'] = period_analysis
    
    return periods


def compute_rpys_metrics(spectrum: pd.Series) -> Dict:
    """
    Compute various RPYS metrics.
    
    Parameters
    ----------
    spectrum : pd.Series
        RPYS spectrum
        
    Returns
    -------
    Dict
        Dictionary of RPYS metrics
    """
    logger.info("Computing RPYS metrics")
    
    if len(spectrum) == 0 or spectrum.sum() == 0:
        return {"error": "Empty spectrum"}
    
    # Basic statistics
    total_citations = spectrum.sum()
    non_zero_years = (spectrum > 0).sum()
    
    # Temporal metrics
    weighted_mean_year = (spectrum * spectrum.index).sum() / total_citations
    
    # Variance and standard deviation of years
    year_variance = ((spectrum.index - weighted_mean_year) ** 2 * spectrum).sum() / total_citations
    year_std = np.sqrt(year_variance)
    
    # Concentration metrics
    # Gini coefficient for citation distribution
    sorted_counts = np.sort(spectrum.values)
    n = len(sorted_counts)
    cumsum = np.cumsum(sorted_counts)
    gini = (2 * np.sum((np.arange(1, n + 1) * sorted_counts))) / (n * cumsum[-1]) - (n + 1) / n
    
    # Median year (weighted)
    cumulative_citations = spectrum.cumsum()
    median_citation_idx = total_citations / 2
    median_year = spectrum.index[cumulative_citations >= median_citation_idx].iloc[0]
    
    # Age distribution
    current_year = pd.Timestamp.now().year
    ages = current_year - spectrum.index
    weighted_mean_age = (spectrum * ages).sum() / total_citations
    
    # Peak analysis
    max_citations_year = spectrum.idxmax()
    max_citations_count = spectrum.max()
    
    metrics = {
        'total_citations': int(total_citations),
        'years_with_citations': int(non_zero_years),
        'year_span': int(spectrum.index.max() - spectrum.index.min()),
        'weighted_mean_year': float(weighted_mean_year),
        'weighted_std_year': float(year_std),
        'median_year': int(median_year),
        'weighted_mean_age': float(weighted_mean_age),
        'max_citations_year': int(max_citations_year),
        'max_citations_count': int(max_citations_count),
        'gini_coefficient': float(gini),
        'concentration_ratio_top10': float(spectrum.nlargest(10).sum() / total_citations),
        'concentration_ratio_top5': float(spectrum.nlargest(5).sum() / total_citations),
    }
    
    return metrics


def compare_rpys_spectra(
    spectra: Dict[str, pd.Series],
    method: str = 'correlation'
) -> pd.DataFrame:
    """
    Compare multiple RPYS spectra.
    
    Parameters
    ----------
    spectra : Dict[str, pd.Series]
        Dictionary mapping names to RPYS spectra
    method : str
        Comparison method ('correlation', 'distance')
        
    Returns
    -------
    pd.DataFrame
        Comparison matrix
    """
    logger.info(f"Comparing {len(spectra)} RPYS spectra using {method}")
    
    names = list(spectra.keys())
    n = len(names)
    
    # Align all spectra to same year range
    all_years = set()
    for spectrum in spectra.values():
        all_years.update(spectrum.index)
    
    year_range = sorted(all_years)
    
    # Align spectra
    aligned_spectra = {}
    for name, spectrum in spectra.items():
        aligned = pd.Series(0, index=year_range)
        aligned.update(spectrum)
        aligned_spectra[name] = aligned
    
    # Compute comparison matrix
    comparison_matrix = np.zeros((n, n))
    
    for i, name1 in enumerate(names):
        for j, name2 in enumerate(names):
            if i == j:
                comparison_matrix[i, j] = 1.0
            else:
                spec1 = aligned_spectra[name1]
                spec2 = aligned_spectra[name2]
                
                if method == 'correlation':
                    corr = spec1.corr(spec2)
                    comparison_matrix[i, j] = corr if not pd.isna(corr) else 0
                
                elif method == 'distance':
                    # Euclidean distance (normalized)
                    dist = np.sqrt(((spec1 - spec2) ** 2).sum())
                    max_dist = np.sqrt((spec1 ** 2).sum() + (spec2 ** 2).sum())
                    comparison_matrix[i, j] = 1 - (dist / max_dist) if max_dist > 0 else 0
    
    return pd.DataFrame(comparison_matrix, index=names, columns=names)


if __name__ == "__main__":
    # Test RPYS analysis with synthetic data
    logger.info("Testing RPYS analysis with synthetic data")
    
    # Create test data with cited DOIs
    np.random.seed(42)
    
    test_data = []
    for i in range(100):
        # Simulate cited DOIs with years embedded (simplified)
        cited_dois = []
        n_refs = np.random.poisson(20)
        
        for _ in range(n_refs):
            # Simulate foundational period around 1990s and 2000s
            if np.random.random() < 0.3:
                year = np.random.randint(1990, 2000)  # Foundational period 1
            elif np.random.random() < 0.5:
                year = np.random.randint(2000, 2010)  # Foundational period 2
            else:
                year = np.random.randint(1980, 2020)  # Random
            
            # Create fake DOI with year
            doi = f"10.1000/journal.{year}.{np.random.randint(1000, 9999)}"
            cited_dois.append(doi)
        
        test_data.append({
            'id': i,
            'cited_doi': '; '.join(cited_dois)
        })
    
    df = pd.DataFrame(test_data)
    
    # Test RPYS spectrum computation
    spectrum = compute_rpys_spectrum(df, min_year=1980, max_year=2020)
    print(f"\nRPYS spectrum shape: {len(spectrum)}")
    print(f"Total citations: {spectrum.sum()}")
    print(f"Peak year: {spectrum.idxmax()} ({spectrum.max()} citations)")
    
    # Test peak detection
    peaks = detect_rpys_peaks(spectrum, method='prominence')
    print(f"\nDetected {len(peaks)} peaks:")
    for year, count, strength in peaks[:5]:
        print(f"  {year}: {count} citations (strength: {strength:.2f})")
    
    # Test period analysis
    periods = analyze_rpys_periods(spectrum, peaks)
    print(f"\nFoundational periods: {len(periods)}")
    
    # Test metrics
    metrics = compute_rpys_metrics(spectrum)
    print(f"\nRPYS metrics:")
    for key, value in metrics.items():
        if isinstance(value, float):
            print(f"  {key}: {value:.2f}")
        else:
            print(f"  {key}: {value}")
