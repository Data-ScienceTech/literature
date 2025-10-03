"""
Clustering module for research stream discovery.
Implements Leiden and HDBSCAN clustering on embedding spaces.
"""

import numpy as np
import pandas as pd
from sklearn.neighbors import NearestNeighbors
from sklearn.metrics import silhouette_score, adjusted_rand_score, normalized_mutual_info_score
from typing import Tuple, Optional, List, Dict
import logging

try:
    import igraph as ig
    import leidenalg
    LEIDEN_AVAILABLE = True
except ImportError:
    LEIDEN_AVAILABLE = False
    logging.warning("leidenalg/igraph not available. Leiden clustering will not work.")

try:
    import hdbscan
    HDBSCAN_AVAILABLE = True
except ImportError:
    HDBSCAN_AVAILABLE = False
    logging.warning("hdbscan not available. HDBSCAN clustering will not work.")

try:
    from umap import UMAP
    UMAP_AVAILABLE = True
except ImportError:
    UMAP_AVAILABLE = False
    logging.warning("umap-learn not available. UMAP dimensionality reduction will not work.")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def knn_graph(embeddings: np.ndarray, k: int = 15, metric: str = "cosine") -> 'ig.Graph':
    """
    Build k-nearest neighbors graph from embeddings.
    
    Parameters
    ----------
    embeddings : np.ndarray
        Embedding matrix (n_samples, n_features)
    k : int
        Number of nearest neighbors
    metric : str
        Distance metric ('cosine', 'euclidean', etc.)
        
    Returns
    -------
    ig.Graph
        Undirected graph with edges to k nearest neighbors
    """
    if not LEIDEN_AVAILABLE:
        raise ImportError("igraph is required for knn_graph. Install with: pip install python-igraph")
    
    logger.info(f"Building k-NN graph with k={k}, metric={metric}")
    
    # Fit k-NN
    nbrs = NearestNeighbors(n_neighbors=k+1, metric=metric, n_jobs=-1)
    nbrs.fit(embeddings)
    distances, indices = nbrs.kneighbors(embeddings)
    
    # Build edge set (undirected, so use sorted pairs to avoid duplicates)
    edges = set()
    for i, neighbors in enumerate(indices):
        for j in neighbors[1:]:  # Skip first neighbor (self)
            edge = tuple(sorted((i, int(j))))
            edges.add(edge)
    
    logger.info(f"Created graph with {len(embeddings)} nodes and {len(edges)} edges")
    
    # Create igraph
    g = ig.Graph(n=len(embeddings))
    g.add_edges(list(edges))
    
    return g


def leiden_cluster(
    graph: 'ig.Graph',
    resolution: float = 1.0,
    n_iterations: int = 2,
    seed: Optional[int] = 42
) -> np.ndarray:
    """
    Apply Leiden community detection to a graph.
    
    Parameters
    ----------
    graph : ig.Graph
        Input graph
    resolution : float
        Resolution parameter (higher = more clusters)
    n_iterations : int
        Number of iterations to refine
    seed : int, optional
        Random seed for reproducibility
        
    Returns
    -------
    np.ndarray
        Cluster labels for each node
    """
    if not LEIDEN_AVAILABLE:
        raise ImportError("leidenalg is required. Install with: pip install leidenalg")
    
    logger.info(f"Running Leiden clustering with resolution={resolution}")
    
    # Run Leiden
    partition = leidenalg.find_partition(
        graph,
        leidenalg.RBConfigurationVertexPartition,
        resolution_parameter=resolution,
        n_iterations=n_iterations,
        seed=seed
    )
    
    labels = np.array(partition.membership)
    n_clusters = len(set(labels))
    
    logger.info(f"Found {n_clusters} clusters")
    logger.info(f"Modularity: {partition.modularity:.3f}")
    
    return labels


def hdbscan_cluster(
    embeddings: np.ndarray,
    min_cluster_size: int = 15,
    min_samples: int = 5,
    metric: str = "euclidean",
    cluster_selection_epsilon: float = 0.0
) -> np.ndarray:
    """
    Apply HDBSCAN clustering to embeddings.
    
    Parameters
    ----------
    embeddings : np.ndarray
        Embedding matrix
    min_cluster_size : int
        Minimum cluster size
    min_samples : int
        Minimum samples in neighborhood
    metric : str
        Distance metric
    cluster_selection_epsilon : float
        Distance threshold for cluster merging
        
    Returns
    -------
    np.ndarray
        Cluster labels (-1 for noise)
    """
    if not HDBSCAN_AVAILABLE:
        raise ImportError("hdbscan is required. Install with: pip install hdbscan")
    
    logger.info(f"Running HDBSCAN with min_cluster_size={min_cluster_size}")
    
    clusterer = hdbscan.HDBSCAN(
        min_cluster_size=min_cluster_size,
        min_samples=min_samples,
        metric=metric,
        cluster_selection_epsilon=cluster_selection_epsilon,
        core_dist_n_jobs=-1
    )
    
    labels = clusterer.fit_predict(embeddings)
    
    n_clusters = len(set(labels)) - (1 if -1 in labels else 0)
    n_noise = np.sum(labels == -1)
    
    logger.info(f"Found {n_clusters} clusters")
    logger.info(f"Noise points: {n_noise} ({n_noise/len(labels)*100:.1f}%)")
    
    return labels


def umap_reduce(
    embeddings: np.ndarray,
    n_components: int = 2,
    n_neighbors: int = 15,
    min_dist: float = 0.1,
    metric: str = "cosine",
    random_state: int = 42
) -> np.ndarray:
    """
    Reduce dimensionality using UMAP for visualization.
    
    Parameters
    ----------
    embeddings : np.ndarray
        High-dimensional embeddings
    n_components : int
        Target dimensionality
    n_neighbors : int
        Number of neighbors for UMAP
    min_dist : float
        Minimum distance between points
    metric : str
        Distance metric
    random_state : int
        Random seed
        
    Returns
    -------
    np.ndarray
        Low-dimensional embeddings
    """
    if not UMAP_AVAILABLE:
        raise ImportError("umap-learn is required. Install with: pip install umap-learn")
    
    logger.info(f"Running UMAP reduction to {n_components} dimensions")
    
    reducer = UMAP(
        n_components=n_components,
        n_neighbors=n_neighbors,
        min_dist=min_dist,
        metric=metric,
        random_state=random_state
    )
    
    reduced = reducer.fit_transform(embeddings)
    
    logger.info(f"Reduced from {embeddings.shape[1]} to {reduced.shape[1]} dimensions")
    
    return reduced


def evaluate_clustering(
    embeddings: np.ndarray,
    labels: np.ndarray,
    metric: str = "cosine"
) -> Dict[str, float]:
    """
    Evaluate clustering quality.
    
    Parameters
    ----------
    embeddings : np.ndarray
        Original embeddings
    labels : np.ndarray
        Cluster labels
    metric : str
        Distance metric for silhouette score
        
    Returns
    -------
    Dict[str, float]
        Dictionary with evaluation metrics
    """
    # Filter out noise points for silhouette score
    mask = labels >= 0
    
    if mask.sum() < 2:
        logger.warning("Not enough clustered points for evaluation")
        return {
            "n_clusters": len(set(labels)) - (1 if -1 in labels else 0),
            "n_noise": np.sum(labels == -1),
            "silhouette": None,
            "cluster_sizes_mean": None,
            "cluster_sizes_std": None
        }
    
    # Silhouette score
    try:
        sil_score = silhouette_score(
            embeddings[mask],
            labels[mask],
            metric=metric,
            sample_size=min(10000, mask.sum())
        )
    except Exception as e:
        logger.warning(f"Could not compute silhouette score: {e}")
        sil_score = None
    
    # Cluster size statistics
    unique_labels = [l for l in set(labels) if l >= 0]
    cluster_sizes = [np.sum(labels == l) for l in unique_labels]
    
    metrics = {
        "n_clusters": len(unique_labels),
        "n_noise": np.sum(labels == -1),
        "noise_ratio": np.sum(labels == -1) / len(labels),
        "silhouette": sil_score,
        "cluster_sizes_mean": np.mean(cluster_sizes) if cluster_sizes else 0,
        "cluster_sizes_std": np.std(cluster_sizes) if cluster_sizes else 0,
        "cluster_sizes_min": np.min(cluster_sizes) if cluster_sizes else 0,
        "cluster_sizes_max": np.max(cluster_sizes) if cluster_sizes else 0,
    }
    
    return metrics


def bootstrap_clustering_stability(
    embeddings: np.ndarray,
    clustering_func,
    n_bootstraps: int = 10,
    sample_ratio: float = 0.8,
    random_state: int = 42,
    **clustering_kwargs
) -> Dict[str, float]:
    """
    Evaluate clustering stability via bootstrapping.
    
    Parameters
    ----------
    embeddings : np.ndarray
        Embedding matrix
    clustering_func : callable
        Clustering function that returns labels
    n_bootstraps : int
        Number of bootstrap samples
    sample_ratio : float
        Fraction of data to sample
    random_state : int
        Random seed
    **clustering_kwargs
        Arguments to pass to clustering_func
        
    Returns
    -------
    Dict[str, float]
        Stability metrics (mean and std of ARI/NMI)
    """
    logger.info(f"Running bootstrap stability analysis with {n_bootstraps} iterations")
    
    np.random.seed(random_state)
    n_samples = len(embeddings)
    sample_size = int(n_samples * sample_ratio)
    
    ari_scores = []
    nmi_scores = []
    
    # Reference clustering on full data
    ref_labels = clustering_func(embeddings, **clustering_kwargs)
    
    for i in range(n_bootstraps):
        # Sample indices
        sample_idx = np.random.choice(n_samples, size=sample_size, replace=False)
        
        # Cluster sample
        sample_labels = clustering_func(embeddings[sample_idx], **clustering_kwargs)
        
        # Map back to full space (unsampled points get -1)
        full_labels = np.full(n_samples, -1)
        full_labels[sample_idx] = sample_labels
        
        # Compute agreement on sampled points
        mask = full_labels >= 0
        if mask.sum() > 1:
            ari = adjusted_rand_score(ref_labels[mask], full_labels[mask])
            nmi = normalized_mutual_info_score(ref_labels[mask], full_labels[mask])
            ari_scores.append(ari)
            nmi_scores.append(nmi)
    
    stability = {
        "ari_mean": np.mean(ari_scores),
        "ari_std": np.std(ari_scores),
        "nmi_mean": np.mean(nmi_scores),
        "nmi_std": np.std(nmi_scores),
    }
    
    logger.info(f"Stability - ARI: {stability['ari_mean']:.3f} ± {stability['ari_std']:.3f}")
    logger.info(f"Stability - NMI: {stability['nmi_mean']:.3f} ± {stability['nmi_std']:.3f}")
    
    return stability


if __name__ == "__main__":
    # Test clustering on synthetic data
    logger.info("Testing clustering on synthetic data...")
    
    np.random.seed(42)
    
    # Generate 3 clusters
    n_per_cluster = 50
    cluster1 = np.random.randn(n_per_cluster, 10) + np.array([5, 0, 0, 0, 0, 0, 0, 0, 0, 0])
    cluster2 = np.random.randn(n_per_cluster, 10) + np.array([0, 5, 0, 0, 0, 0, 0, 0, 0, 0])
    cluster3 = np.random.randn(n_per_cluster, 10) + np.array([0, 0, 5, 0, 0, 0, 0, 0, 0, 0])
    
    embeddings = np.vstack([cluster1, cluster2, cluster3])
    true_labels = np.array([0]*n_per_cluster + [1]*n_per_cluster + [2]*n_per_cluster)
    
    # Test Leiden if available
    if LEIDEN_AVAILABLE:
        g = knn_graph(embeddings, k=10, metric="euclidean")
        leiden_labels = leiden_cluster(g, resolution=1.0)
        print(f"\nLeiden clustering: {len(set(leiden_labels))} clusters")
        print(f"ARI vs true labels: {adjusted_rand_score(true_labels, leiden_labels):.3f}")
    
    # Test HDBSCAN if available
    if HDBSCAN_AVAILABLE:
        hdbscan_labels = hdbscan_cluster(embeddings, min_cluster_size=10)
        print(f"\nHDBSCAN clustering: {len(set(hdbscan_labels))-1} clusters")
        mask = hdbscan_labels >= 0
        if mask.sum() > 0:
            print(f"ARI vs true labels: {adjusted_rand_score(true_labels[mask], hdbscan_labels[mask]):.3f}")
