"""
Multi-level hierarchical clustering for research stream discovery.

Implements state-of-the-art hierarchical clustering methods:
- Leiden multi-resolution (varying resolution parameter)
- HDBSCAN hierarchical condensed tree
- Recursive clustering with quality thresholds
- Cross-level coherence analysis
- Hierarchical stability metrics

References:
- Traag et al. (2019) - Leiden algorithm
- McInnes et al. (2017) - HDBSCAN
- Schaub et al. (2017) - Multi-scale community detection
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional, Set
from collections import defaultdict
import logging
from dataclasses import dataclass
import json

try:
    import igraph as ig
    import leidenalg
    LEIDEN_AVAILABLE = True
except ImportError:
    LEIDEN_AVAILABLE = False
    logging.warning("leidenalg/igraph not available")

try:
    import hdbscan
    HDBSCAN_AVAILABLE = True
except ImportError:
    HDBSCAN_AVAILABLE = False
    logging.warning("hdbscan not available")

from sklearn.metrics import silhouette_score, davies_bouldin_score, calinski_harabasz_score
from sklearn.neighbors import NearestNeighbors

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class ClusterNode:
    """Hierarchical cluster node with metadata."""
    id: str  # Unique hierarchical ID like "0", "0.1", "0.1.2"
    level: int  # Depth in hierarchy (0 = root)
    parent_id: Optional[str]  # Parent cluster ID
    paper_indices: np.ndarray  # Papers in this cluster
    size: int  # Number of papers
    children: List['ClusterNode']  # Sub-clusters
    metadata: Dict  # Quality metrics, temporal info, etc.
    
    def __post_init__(self):
        self.size = len(self.paper_indices)
    
    def to_dict(self) -> Dict:
        """Convert to JSON-serializable dict."""
        return {
            'id': self.id,
            'level': self.level,
            'parent_id': self.parent_id,
            'size': self.size,
            'paper_indices': self.paper_indices.tolist(),
            'children': [c.to_dict() for c in self.children],
            'metadata': self.metadata
        }


class HierarchicalClusterTree:
    """Container for multi-level cluster hierarchy."""
    
    def __init__(self, root_nodes: List[ClusterNode]):
        self.root_nodes = root_nodes
        self.all_nodes = {}  # Map cluster_id -> ClusterNode
        self._index_nodes()
    
    def _index_nodes(self):
        """Build index of all nodes."""
        def index_recursive(node):
            self.all_nodes[node.id] = node
            for child in node.children:
                index_recursive(child)
        
        for root in self.root_nodes:
            index_recursive(root)
    
    def get_node(self, cluster_id: str) -> Optional[ClusterNode]:
        """Get node by ID."""
        return self.all_nodes.get(cluster_id)
    
    def get_level_clusters(self, level: int) -> List[ClusterNode]:
        """Get all clusters at a specific level."""
        return [node for node in self.all_nodes.values() if node.level == level]
    
    def max_depth(self) -> int:
        """Get maximum depth of hierarchy."""
        return max(node.level for node in self.all_nodes.values())
    
    def get_leaf_clusters(self) -> List[ClusterNode]:
        """Get all leaf clusters (no children)."""
        return [node for node in self.all_nodes.values() if len(node.children) == 0]
    
    def to_dict(self) -> Dict:
        """Export to JSON-serializable dict."""
        return {
            'root_nodes': [r.to_dict() for r in self.root_nodes],
            'max_depth': self.max_depth(),
            'total_clusters': len(self.all_nodes),
            'level_sizes': {
                level: len(self.get_level_clusters(level))
                for level in range(self.max_depth() + 1)
            }
        }
    
    def save_json(self, path: str):
        """Save hierarchy to JSON."""
        import json
        with open(path, 'w') as f:
            json.dump(self.to_dict(), f, indent=2)
        logger.info(f"Saved hierarchy to {path}")


class LeidenMultiResolution:
    """
    Multi-resolution Leiden clustering.
    
    Creates hierarchy by varying resolution parameter from coarse to fine.
    Uses modularity optimization to find natural scales.
    """
    
    def __init__(
        self,
        embeddings: np.ndarray,
        k: int = 15,
        metric: str = 'cosine'
    ):
        """Initialize with embeddings."""
        if not LEIDEN_AVAILABLE:
            raise ImportError("leidenalg required for Leiden multi-resolution")
        
        self.embeddings = embeddings
        self.k = k
        self.metric = metric
        self.graph = None
        
        logger.info(f"Initializing Leiden multi-resolution on {len(embeddings)} papers")
    
    def build_graph(self) -> ig.Graph:
        """Build k-NN graph."""
        logger.info(f"Building k-NN graph (k={self.k}, metric={self.metric})")
        
        nbrs = NearestNeighbors(n_neighbors=self.k+1, metric=self.metric, n_jobs=-1)
        nbrs.fit(self.embeddings)
        distances, indices = nbrs.kneighbors(self.embeddings)
        
        edges = set()
        for i, neighbors in enumerate(indices):
            for j in neighbors[1:]:
                edge = tuple(sorted((i, int(j))))
                edges.add(edge)
        
        g = ig.Graph(n=len(self.embeddings))
        g.add_edges(list(edges))
        
        logger.info(f"Graph: {g.vcount()} nodes, {g.ecount()} edges")
        self.graph = g
        return g
    
    def find_optimal_resolutions(
        self,
        resolution_range: Tuple[float, float] = (0.3, 3.0),
        n_resolutions: int = 10
    ) -> List[float]:
        """
        Find optimal resolution values using modularity landscape.
        
        Returns resolutions that produce distinct, high-quality partitions.
        """
        if self.graph is None:
            self.build_graph()
        
        logger.info(f"Finding optimal resolutions in range {resolution_range}")
        
        # Sample resolution values
        resolutions = np.linspace(resolution_range[0], resolution_range[1], n_resolutions)
        
        results = []
        prev_partition = None
        
        for res in resolutions:
            partition = leidenalg.find_partition(
                self.graph,
                leidenalg.RBConfigurationVertexPartition,
                resolution_parameter=res,
                seed=42
            )
            
            n_clusters = len(set(partition.membership))
            modularity = partition.modularity
            
            # Check if this is sufficiently different from previous
            is_different = True
            if prev_partition is not None:
                from sklearn.metrics import adjusted_rand_score
                ari = adjusted_rand_score(prev_partition.membership, partition.membership)
                is_different = ari < 0.95  # Not too similar
            
            results.append({
                'resolution': res,
                'n_clusters': n_clusters,
                'modularity': modularity,
                'is_different': is_different
            })
            
            prev_partition = partition
        
        # Select resolutions with high modularity and distinct partitions
        results_df = pd.DataFrame(results)
        
        # Filter for different partitions
        distinct_results = results_df[results_df['is_different']].copy()
        
        # Sort by modularity and select diverse resolutions
        distinct_results = distinct_results.sort_values('modularity', ascending=False)
        
        # Select top resolutions ensuring coverage of cluster counts
        selected_resolutions = []
        seen_n_clusters = set()
        
        for _, row in distinct_results.iterrows():
            if row['n_clusters'] not in seen_n_clusters:
                selected_resolutions.append(row['resolution'])
                seen_n_clusters.add(row['n_clusters'])
                
                if len(selected_resolutions) >= 5:  # Max 5 levels
                    break
        
        logger.info(f"Selected {len(selected_resolutions)} optimal resolutions")
        return sorted(selected_resolutions)
    
    def cluster_at_resolution(
        self,
        resolution: float,
        seed: int = 42
    ) -> np.ndarray:
        """Run Leiden at specific resolution."""
        if self.graph is None:
            self.build_graph()
        
        partition = leidenalg.find_partition(
            self.graph,
            leidenalg.RBConfigurationVertexPartition,
            resolution_parameter=resolution,
            seed=seed,
            n_iterations=2
        )
        
        return np.array(partition.membership)
    
    def build_hierarchy(
        self,
        resolutions: Optional[List[float]] = None,
        min_cluster_size: int = 20,
        max_levels: int = 4
    ) -> HierarchicalClusterTree:
        """
        Build multi-level hierarchy using multiple resolutions.
        
        Parameters
        ----------
        resolutions : list, optional
            Resolution values (coarse to fine). Auto-detected if None.
        min_cluster_size : int
            Minimum cluster size at any level
        max_levels : int
            Maximum depth of hierarchy
        
        Returns
        -------
        HierarchicalClusterTree
            Complete hierarchy
        """
        logger.info("Building Leiden multi-resolution hierarchy")
        
        if resolutions is None:
            resolutions = self.find_optimal_resolutions()
        
        # Sort from coarse to fine (lower resolution = fewer clusters)
        resolutions = sorted(resolutions)[:max_levels]
        
        logger.info(f"Using {len(resolutions)} resolutions: {resolutions}")
        
        # Cluster at each resolution
        level_labels = []
        for res in resolutions:
            labels = self.cluster_at_resolution(res)
            level_labels.append(labels)
            n_clusters = len(set(labels))
            logger.info(f"  Resolution {res:.2f}: {n_clusters} clusters")
        
        # Build hierarchy from coarse to fine
        hierarchy = self._construct_hierarchy_from_levels(
            level_labels,
            min_cluster_size=min_cluster_size
        )
        
        return hierarchy
    
    def _construct_hierarchy_from_levels(
        self,
        level_labels: List[np.ndarray],
        min_cluster_size: int = 20
    ) -> HierarchicalClusterTree:
        """Construct hierarchy from multi-resolution clusterings."""
        
        # Level 0: Coarsest clustering
        level0_labels = level_labels[0]
        unique_labels = sorted(set(level0_labels))
        
        root_nodes = []
        
        for cluster_id in unique_labels:
            paper_idx = np.where(level0_labels == cluster_id)[0]
            
            if len(paper_idx) < min_cluster_size:
                continue
            
            # Compute quality metrics for this cluster
            metadata = self._compute_cluster_quality(paper_idx, level=0)
            
            node = ClusterNode(
                id=str(cluster_id),
                level=0,
                parent_id=None,
                paper_indices=paper_idx,
                size=len(paper_idx),
                children=[],
                metadata=metadata
            )
            
            # Recursively build sub-clusters
            if len(level_labels) > 1:
                self._build_subclusters(
                    node,
                    paper_idx,
                    level_labels[1:],
                    min_cluster_size=min_cluster_size
                )
            
            root_nodes.append(node)
        
        return HierarchicalClusterTree(root_nodes)
    
    def _build_subclusters(
        self,
        parent_node: ClusterNode,
        parent_papers: np.ndarray,
        remaining_levels: List[np.ndarray],
        min_cluster_size: int
    ):
        """Recursively build sub-clusters."""
        if len(remaining_levels) == 0:
            return
        
        # Get next level labels for parent's papers
        next_level_labels = remaining_levels[0][parent_papers]
        unique_sublabels = sorted(set(next_level_labels))
        
        # Only split if we get multiple sub-clusters
        if len(unique_sublabels) <= 1:
            return
        
        child_level = parent_node.level + 1
        
        for i, sublabel in enumerate(unique_sublabels):
            # Get papers in this sub-cluster
            local_mask = next_level_labels == sublabel
            subcluster_papers = parent_papers[local_mask]
            
            if len(subcluster_papers) < min_cluster_size:
                continue
            
            # Create child node
            child_id = f"{parent_node.id}.{i}"
            metadata = self._compute_cluster_quality(subcluster_papers, level=child_level)
            
            child_node = ClusterNode(
                id=child_id,
                level=child_level,
                parent_id=parent_node.id,
                paper_indices=subcluster_papers,
                size=len(subcluster_papers),
                children=[],
                metadata=metadata
            )
            
            # Recurse
            if len(remaining_levels) > 1:
                self._build_subclusters(
                    child_node,
                    subcluster_papers,
                    remaining_levels[1:],
                    min_cluster_size=min_cluster_size
                )
            
            parent_node.children.append(child_node)
    
    def _compute_cluster_quality(
        self,
        paper_indices: np.ndarray,
        level: int
    ) -> Dict:
        """Compute quality metrics for a cluster."""
        cluster_embeddings = self.embeddings[paper_indices]
        
        # Cohesion: average internal similarity
        if len(cluster_embeddings) > 1:
            centroid = cluster_embeddings.mean(axis=0)
            centroid = centroid / np.linalg.norm(centroid)
            similarities = cluster_embeddings @ centroid
            cohesion = float(similarities.mean())
        else:
            cohesion = 1.0
        
        # Density
        if len(cluster_embeddings) > 1:
            pairwise_sim = cluster_embeddings @ cluster_embeddings.T
            density = float(pairwise_sim[np.triu_indices_from(pairwise_sim, k=1)].mean())
        else:
            density = 1.0
        
        return {
            'level': level,
            'cohesion': cohesion,
            'density': density,
            'size': len(paper_indices)
        }


class HDBSCANHierarchical:
    """
    Hierarchical clustering using HDBSCAN's condensed tree.
    
    Extracts multi-level hierarchy from density-based clustering.
    """
    
    def __init__(self, embeddings: np.ndarray, metric: str = 'euclidean'):
        """Initialize with embeddings."""
        if not HDBSCAN_AVAILABLE:
            raise ImportError("hdbscan required for HDBSCAN hierarchical")
        
        self.embeddings = embeddings
        self.metric = metric
        self.clusterer = None
        
        logger.info(f"Initializing HDBSCAN hierarchical on {len(embeddings)} papers")
    
    def fit(
        self,
        min_cluster_size: int = 20,
        min_samples: int = 5,
        cluster_selection_method: str = 'eom'
    ):
        """Fit HDBSCAN clusterer."""
        logger.info(f"Fitting HDBSCAN (min_cluster_size={min_cluster_size})")
        
        self.clusterer = hdbscan.HDBSCAN(
            min_cluster_size=min_cluster_size,
            min_samples=min_samples,
            metric=self.metric,
            cluster_selection_method=cluster_selection_method,
            core_dist_n_jobs=-1
        )
        
        self.clusterer.fit(self.embeddings)
        
        n_clusters = len(set(self.clusterer.labels_)) - (1 if -1 in self.clusterer.labels_ else 0)
        n_noise = np.sum(self.clusterer.labels_ == -1)
        
        logger.info(f"Found {n_clusters} clusters, {n_noise} noise points")
    
    def extract_hierarchy(
        self,
        min_cluster_size: int = 20,
        max_levels: int = 4
    ) -> HierarchicalClusterTree:
        """
        Extract hierarchy from HDBSCAN condensed tree.
        
        Parameters
        ----------
        min_cluster_size : int
            Minimum cluster size
        max_levels : int
            Maximum depth
        
        Returns
        -------
        HierarchicalClusterTree
            Multi-level hierarchy
        """
        if self.clusterer is None:
            self.fit(min_cluster_size=min_cluster_size)
        
        logger.info("Extracting hierarchy from condensed tree")
        
        # Get condensed tree
        tree = self.clusterer.condensed_tree_
        
        # Extract cluster hierarchy
        # HDBSCAN provides parent-child relationships in condensed tree
        
        # Start with top-level clusters
        top_level_labels = self.clusterer.labels_
        unique_labels = sorted([l for l in set(top_level_labels) if l >= 0])
        
        root_nodes = []
        
        for cluster_id in unique_labels:
            paper_idx = np.where(top_level_labels == cluster_id)[0]
            
            if len(paper_idx) < min_cluster_size:
                continue
            
            metadata = {
                'level': 0,
                'size': len(paper_idx),
                'stability': self._get_cluster_stability(cluster_id),
                'persistence': self._get_cluster_persistence(cluster_id)
            }
            
            node = ClusterNode(
                id=str(cluster_id),
                level=0,
                parent_id=None,
                paper_indices=paper_idx,
                size=len(paper_idx),
                children=[],
                metadata=metadata
            )
            
            # Subdivide using recursive HDBSCAN if cluster is large
            if len(paper_idx) >= min_cluster_size * 3 and max_levels > 1:
                self._recursive_subdivide(
                    node,
                    paper_idx,
                    min_cluster_size=min_cluster_size,
                    remaining_levels=max_levels - 1
                )
            
            root_nodes.append(node)
        
        return HierarchicalClusterTree(root_nodes)
    
    def _recursive_subdivide(
        self,
        parent_node: ClusterNode,
        paper_indices: np.ndarray,
        min_cluster_size: int,
        remaining_levels: int
    ):
        """Recursively subdivide a cluster."""
        if remaining_levels <= 0 or len(paper_indices) < min_cluster_size * 2:
            return
        
        # Cluster the subset
        sub_embeddings = self.embeddings[paper_indices]
        
        sub_clusterer = hdbscan.HDBSCAN(
            min_cluster_size=min_cluster_size,
            min_samples=5,
            metric=self.metric,
            cluster_selection_method='eom',
            core_dist_n_jobs=-1
        )
        
        sub_labels = sub_clusterer.fit_predict(sub_embeddings)
        unique_sublabels = sorted([l for l in set(sub_labels) if l >= 0])
        
        # Only split if we found multiple clusters
        if len(unique_sublabels) <= 1:
            return
        
        child_level = parent_node.level + 1
        
        for i, sublabel in enumerate(unique_sublabels):
            subcluster_mask = sub_labels == sublabel
            subcluster_papers = paper_indices[subcluster_mask]
            
            if len(subcluster_papers) < min_cluster_size:
                continue
            
            child_id = f"{parent_node.id}.{i}"
            
            metadata = {
                'level': child_level,
                'size': len(subcluster_papers)
            }
            
            child_node = ClusterNode(
                id=child_id,
                level=child_level,
                parent_id=parent_node.id,
                paper_indices=subcluster_papers,
                size=len(subcluster_papers),
                children=[],
                metadata=metadata
            )
            
            # Recurse
            self._recursive_subdivide(
                child_node,
                subcluster_papers,
                min_cluster_size=min_cluster_size,
                remaining_levels=remaining_levels - 1
            )
            
            parent_node.children.append(child_node)
    
    def _get_cluster_stability(self, cluster_id: int) -> float:
        """Get cluster stability score from HDBSCAN."""
        if self.clusterer is None or not hasattr(self.clusterer, 'cluster_persistence_'):
            return 0.0
        
        # Cluster persistence is a measure of stability
        try:
            persistence = self.clusterer.cluster_persistence_
            if cluster_id < len(persistence):
                return float(persistence[cluster_id])
        except:
            pass
        
        return 0.0
    
    def _get_cluster_persistence(self, cluster_id: int) -> float:
        """Get cluster persistence (lifetime in dendrogram)."""
        return self._get_cluster_stability(cluster_id)


class RecursiveLeiden:
    """
    Recursive Leiden clustering with quality-based subdivision.
    
    Recursively subdivides clusters until quality threshold is met.
    """
    
    def __init__(
        self,
        embeddings: np.ndarray,
        k: int = 15,
        metric: str = 'cosine'
    ):
        """Initialize with embeddings."""
        if not LEIDEN_AVAILABLE:
            raise ImportError("leidenalg required for recursive Leiden")
        
        self.embeddings = embeddings
        self.k = k
        self.metric = metric
        
        logger.info(f"Initializing recursive Leiden on {len(embeddings)} papers")
    
    def build_hierarchy(
        self,
        resolution: float = 1.0,
        min_cluster_size: int = 20,
        max_depth: int = 4,
        quality_threshold: float = 0.3
    ) -> HierarchicalClusterTree:
        """
        Build hierarchy recursively.
        
        Parameters
        ----------
        resolution : float
            Leiden resolution parameter
        min_cluster_size : int
            Minimum cluster size
        max_depth : int
            Maximum depth
        quality_threshold : float
            Silhouette threshold for subdivision (0-1)
        
        Returns
        -------
        HierarchicalClusterTree
            Multi-level hierarchy
        """
        logger.info(f"Building recursive Leiden hierarchy (max_depth={max_depth})")
        
        # Initial clustering
        all_indices = np.arange(len(self.embeddings))
        
        root_labels = self._cluster_subset(all_indices, resolution=resolution)
        unique_labels = sorted(set(root_labels))
        
        logger.info(f"Level 0: {len(unique_labels)} clusters")
        
        root_nodes = []
        
        for cluster_id in unique_labels:
            local_mask = root_labels == cluster_id
            paper_idx = all_indices[local_mask]
            
            if len(paper_idx) < min_cluster_size:
                continue
            
            # Compute quality
            silhouette = self._compute_silhouette(paper_idx, root_labels[local_mask])
            
            metadata = {
                'level': 0,
                'size': len(paper_idx),
                'silhouette': silhouette,
                'should_subdivide': silhouette < quality_threshold and len(paper_idx) >= min_cluster_size * 3
            }
            
            node = ClusterNode(
                id=str(cluster_id),
                level=0,
                parent_id=None,
                paper_indices=paper_idx,
                size=len(paper_idx),
                children=[],
                metadata=metadata
            )
            
            # Recursively subdivide if needed
            if metadata['should_subdivide'] and max_depth > 1:
                self._recursive_cluster(
                    node,
                    resolution=resolution,
                    min_cluster_size=min_cluster_size,
                    remaining_depth=max_depth - 1,
                    quality_threshold=quality_threshold
                )
            
            root_nodes.append(node)
        
        return HierarchicalClusterTree(root_nodes)
    
    def _cluster_subset(
        self,
        paper_indices: np.ndarray,
        resolution: float
    ) -> np.ndarray:
        """Cluster a subset of papers."""
        subset_embeddings = self.embeddings[paper_indices]
        
        # Build k-NN graph for subset
        nbrs = NearestNeighbors(n_neighbors=min(self.k+1, len(subset_embeddings)), metric=self.metric, n_jobs=-1)
        nbrs.fit(subset_embeddings)
        distances, indices = nbrs.kneighbors(subset_embeddings)
        
        edges = set()
        for i, neighbors in enumerate(indices):
            for j in neighbors[1:]:
                edge = tuple(sorted((i, int(j))))
                edges.add(edge)
        
        g = ig.Graph(n=len(subset_embeddings))
        g.add_edges(list(edges))
        
        # Leiden clustering
        partition = leidenalg.find_partition(
            g,
            leidenalg.RBConfigurationVertexPartition,
            resolution_parameter=resolution,
            seed=42
        )
        
        return np.array(partition.membership)
    
    def _recursive_cluster(
        self,
        parent_node: ClusterNode,
        resolution: float,
        min_cluster_size: int,
        remaining_depth: int,
        quality_threshold: float
    ):
        """Recursively subdivide cluster."""
        if remaining_depth <= 0:
            return
        
        paper_indices = parent_node.paper_indices
        
        if len(paper_indices) < min_cluster_size * 2:
            return
        
        # Cluster the subset
        sub_labels = self._cluster_subset(paper_indices, resolution=resolution)
        unique_sublabels = sorted(set(sub_labels))
        
        # Only split if we found multiple clusters
        if len(unique_sublabels) <= 1:
            return
        
        child_level = parent_node.level + 1
        
        for i, sublabel in enumerate(unique_sublabels):
            subcluster_mask = sub_labels == sublabel
            subcluster_papers = paper_indices[subcluster_mask]
            
            if len(subcluster_papers) < min_cluster_size:
                continue
            
            # Quality check
            silhouette = self._compute_silhouette(
                subcluster_papers,
                sub_labels[subcluster_mask]
            )
            
            child_id = f"{parent_node.id}.{i}"
            
            metadata = {
                'level': child_level,
                'size': len(subcluster_papers),
                'silhouette': silhouette,
                'should_subdivide': silhouette < quality_threshold and len(subcluster_papers) >= min_cluster_size * 3
            }
            
            child_node = ClusterNode(
                id=child_id,
                level=child_level,
                parent_id=parent_node.id,
                paper_indices=subcluster_papers,
                size=len(subcluster_papers),
                children=[],
                metadata=metadata
            )
            
            # Recurse if quality is poor
            if metadata['should_subdivide'] and remaining_depth > 1:
                self._recursive_cluster(
                    child_node,
                    resolution=resolution,
                    min_cluster_size=min_cluster_size,
                    remaining_depth=remaining_depth - 1,
                    quality_threshold=quality_threshold
                )
            
            parent_node.children.append(child_node)
    
    def _compute_silhouette(
        self,
        paper_indices: np.ndarray,
        labels: np.ndarray
    ) -> float:
        """Compute silhouette score for cluster."""
        if len(set(labels)) <= 1 or len(paper_indices) < 2:
            return 1.0
        
        cluster_embeddings = self.embeddings[paper_indices]
        
        try:
            score = silhouette_score(
                cluster_embeddings,
                labels,
                metric=self.metric,
                sample_size=min(1000, len(paper_indices))
            )
            return float(score)
        except:
            return 0.0


def compare_hierarchies(
    hierarchy1: HierarchicalClusterTree,
    hierarchy2: HierarchicalClusterTree,
    embeddings: np.ndarray
) -> Dict:
    """
    Compare two hierarchical clusterings.
    
    Computes agreement at each level and overall quality.
    """
    logger.info("Comparing two hierarchies")
    
    max_depth = min(hierarchy1.max_depth(), hierarchy2.max_depth())
    
    level_comparisons = []
    
    for level in range(max_depth + 1):
        clusters1 = hierarchy1.get_level_clusters(level)
        clusters2 = hierarchy2.get_level_clusters(level)
        
        # Build label arrays
        labels1 = np.full(len(embeddings), -1)
        labels2 = np.full(len(embeddings), -1)
        
        for i, cluster in enumerate(clusters1):
            labels1[cluster.paper_indices] = i
        
        for i, cluster in enumerate(clusters2):
            labels2[cluster.paper_indices] = i
        
        # Compute agreement on non-noise points
        mask = (labels1 >= 0) & (labels2 >= 0)
        
        if mask.sum() > 0:
            from sklearn.metrics import adjusted_rand_score, normalized_mutual_info_score
            
            ari = adjusted_rand_score(labels1[mask], labels2[mask])
            nmi = normalized_mutual_info_score(labels1[mask], labels2[mask])
        else:
            ari = 0.0
            nmi = 0.0
        
        level_comparisons.append({
            'level': level,
            'n_clusters_h1': len(clusters1),
            'n_clusters_h2': len(clusters2),
            'ari': ari,
            'nmi': nmi
        })
    
    return {
        'level_comparisons': level_comparisons,
        'mean_ari': np.mean([lc['ari'] for lc in level_comparisons]),
        'mean_nmi': np.mean([lc['nmi'] for lc in level_comparisons])
    }


if __name__ == "__main__":
    # Test with synthetic data
    logger.info("Testing hierarchical clustering on synthetic data")
    
    np.random.seed(42)
    
    # Generate hierarchical clusters
    # Super-cluster 1: 2 sub-clusters
    cluster_1a = np.random.randn(50, 10) + np.array([5, 0, 0, 0, 0, 0, 0, 0, 0, 0])
    cluster_1b = np.random.randn(50, 10) + np.array([6, 1, 0, 0, 0, 0, 0, 0, 0, 0])
    
    # Super-cluster 2: 2 sub-clusters
    cluster_2a = np.random.randn(50, 10) + np.array([0, 5, 0, 0, 0, 0, 0, 0, 0, 0])
    cluster_2b = np.random.randn(50, 10) + np.array([1, 6, 0, 0, 0, 0, 0, 0, 0, 0])
    
    embeddings = np.vstack([cluster_1a, cluster_1b, cluster_2a, cluster_2b])
    
    print(f"\nTest dataset: {len(embeddings)} papers")
    
    # Test Leiden multi-resolution
    if LEIDEN_AVAILABLE:
        print("\n" + "="*60)
        print("TESTING LEIDEN MULTI-RESOLUTION")
        print("="*60)
        
        leiden_mr = LeidenMultiResolution(embeddings, k=10, metric='euclidean')
        hierarchy = leiden_mr.build_hierarchy(
            resolutions=[0.5, 1.0, 2.0],
            min_cluster_size=10,
            max_levels=3
        )
        
        print(f"\nHierarchy: {len(hierarchy.root_nodes)} root clusters")
        print(f"Max depth: {hierarchy.max_depth()}")
        print(f"Total clusters: {len(hierarchy.all_nodes)}")
        
        for level in range(hierarchy.max_depth() + 1):
            level_clusters = hierarchy.get_level_clusters(level)
            print(f"Level {level}: {len(level_clusters)} clusters")
    
    # Test HDBSCAN hierarchical
    if HDBSCAN_AVAILABLE:
        print("\n" + "="*60)
        print("TESTING HDBSCAN HIERARCHICAL")
        print("="*60)
        
        hdbscan_h = HDBSCANHierarchical(embeddings, metric='euclidean')
        hierarchy = hdbscan_h.extract_hierarchy(min_cluster_size=10, max_levels=3)
        
        print(f"\nHierarchy: {len(hierarchy.root_nodes)} root clusters")
        print(f"Max depth: {hierarchy.max_depth()}")
        print(f"Total clusters: {len(hierarchy.all_nodes)}")
        
        for level in range(hierarchy.max_depth() + 1):
            level_clusters = hierarchy.get_level_clusters(level)
            print(f"Level {level}: {len(level_clusters)} clusters")
