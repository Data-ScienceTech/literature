"""
Network analysis module for citation graphs and bibliometric networks.
Implements direct citation, co-citation, and bibliographic coupling networks.
"""

import numpy as np
import pandas as pd
import networkx as nx
from typing import Dict, List, Tuple, Optional, Set
from collections import defaultdict, Counter
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def build_direct_citation_graph(df: pd.DataFrame) -> nx.DiGraph:
    """
    Build directed citation graph from papers with OpenAlex data.
    
    Parameters
    ----------
    df : pd.DataFrame
        DataFrame with 'openalex_id' and 'referenced_works' columns
        
    Returns
    -------
    nx.DiGraph
        Directed graph where edges represent citations
    """
    logger.info("Building direct citation graph")
    
    # Filter papers with OpenAlex data
    valid_papers = df.dropna(subset=['openalex_id']).copy()
    
    # Create mapping from OpenAlex ID to paper index
    id_to_idx = {row['openalex_id']: idx for idx, row in valid_papers.iterrows()}
    
    # Create graph
    G = nx.DiGraph()
    
    # Add nodes with attributes
    for idx, row in valid_papers.iterrows():
        G.add_node(
            row['openalex_id'],
            title=row.get('title', ''),
            year=row.get('year'),
            journal=row.get('journal', ''),
            cited_by_count=row.get('cited_by_count', 0),
            cluster=row.get('cluster', -1),
            paper_idx=idx
        )
    
    # Add edges (citations)
    edges_added = 0
    for idx, row in valid_papers.iterrows():
        citing_id = row['openalex_id']
        referenced_works = row.get('referenced_works', [])
        
        if isinstance(referenced_works, list):
            for cited_id in referenced_works:
                if cited_id in id_to_idx:
                    G.add_edge(citing_id, cited_id, year=row.get('year'))
                    edges_added += 1
    
    logger.info(f"Created citation graph: {G.number_of_nodes()} nodes, {G.number_of_edges()} edges")
    return G


def build_cocitation_graph(df: pd.DataFrame, min_cocitations: int = 2) -> nx.Graph:
    """
    Build co-citation network (papers cited together).
    
    Parameters
    ----------
    df : pd.DataFrame
        DataFrame with 'openalex_id' and 'referenced_works' columns
    min_cocitations : int
        Minimum number of co-citations to include edge
        
    Returns
    -------
    nx.Graph
        Undirected graph where edge weights represent co-citation counts
    """
    logger.info(f"Building co-citation graph with min_cocitations={min_cocitations}")
    
    # Get all cited works and their citers
    cited_by = defaultdict(set)
    
    valid_papers = df.dropna(subset=['openalex_id']).copy()
    
    for idx, row in valid_papers.iterrows():
        citing_id = row['openalex_id']
        referenced_works = row.get('referenced_works', [])
        
        if isinstance(referenced_works, list):
            for cited_id in referenced_works:
                cited_by[cited_id].add(citing_id)
    
    # Build co-citation pairs
    cocitation_counts = Counter()
    
    for citing_id in valid_papers['openalex_id']:
        referenced_works = df[df['openalex_id'] == citing_id]['referenced_works'].iloc[0]
        
        if isinstance(referenced_works, list) and len(referenced_works) > 1:
            # All pairs of cited works
            for i, cited1 in enumerate(referenced_works):
                for cited2 in referenced_works[i+1:]:
                    pair = tuple(sorted([cited1, cited2]))
                    cocitation_counts[pair] += 1
    
    # Create graph
    G = nx.Graph()
    
    # Add nodes (only cited works that appear in our dataset)
    paper_ids = set(valid_papers['openalex_id'])
    
    for (cited1, cited2), count in cocitation_counts.items():
        if count >= min_cocitations and cited1 in paper_ids and cited2 in paper_ids:
            # Add nodes with attributes if they exist in our dataset
            for cited_id in [cited1, cited2]:
                if cited_id not in G and cited_id in paper_ids:
                    paper_row = df[df['openalex_id'] == cited_id].iloc[0]
                    G.add_node(
                        cited_id,
                        title=paper_row.get('title', ''),
                        year=paper_row.get('year'),
                        journal=paper_row.get('journal', ''),
                        cluster=paper_row.get('cluster', -1)
                    )
            
            G.add_edge(cited1, cited2, weight=count, cocitations=count)
    
    logger.info(f"Created co-citation graph: {G.number_of_nodes()} nodes, {G.number_of_edges()} edges")
    return G


def build_bibliographic_coupling_graph(df: pd.DataFrame, min_shared: int = 2) -> nx.Graph:
    """
    Build bibliographic coupling network (papers sharing references).
    
    Parameters
    ----------
    df : pd.DataFrame
        DataFrame with 'openalex_id' and 'referenced_works' columns
    min_shared : int
        Minimum number of shared references to include edge
        
    Returns
    -------
    nx.Graph
        Undirected graph where edge weights represent shared reference counts
    """
    logger.info(f"Building bibliographic coupling graph with min_shared={min_shared}")
    
    valid_papers = df.dropna(subset=['openalex_id']).copy()
    
    # Create reference sets for each paper
    paper_refs = {}
    for idx, row in valid_papers.iterrows():
        paper_id = row['openalex_id']
        referenced_works = row.get('referenced_works', [])
        
        if isinstance(referenced_works, list):
            paper_refs[paper_id] = set(referenced_works)
        else:
            paper_refs[paper_id] = set()
    
    # Create graph
    G = nx.Graph()
    
    # Add all papers as nodes
    for idx, row in valid_papers.iterrows():
        G.add_node(
            row['openalex_id'],
            title=row.get('title', ''),
            year=row.get('year'),
            journal=row.get('journal', ''),
            cited_by_count=row.get('cited_by_count', 0),
            cluster=row.get('cluster', -1),
            paper_idx=idx
        )
    
    # Calculate bibliographic coupling
    paper_ids = list(paper_refs.keys())
    edges_added = 0
    
    for i, paper1 in enumerate(paper_ids):
        for paper2 in paper_ids[i+1:]:
            shared_refs = paper_refs[paper1] & paper_refs[paper2]
            shared_count = len(shared_refs)
            
            if shared_count >= min_shared:
                G.add_edge(
                    paper1, 
                    paper2, 
                    weight=shared_count,
                    shared_references=shared_count,
                    jaccard=shared_count / len(paper_refs[paper1] | paper_refs[paper2])
                )
                edges_added += 1
    
    logger.info(f"Created bibliographic coupling graph: {G.number_of_nodes()} nodes, {G.number_of_edges()} edges")
    return G


def compute_network_metrics(G: nx.Graph) -> Dict:
    """
    Compute various network metrics.
    
    Parameters
    ----------
    G : nx.Graph or nx.DiGraph
        Input graph
        
    Returns
    -------
    Dict
        Dictionary of network metrics
    """
    logger.info("Computing network metrics")
    
    metrics = {
        'n_nodes': G.number_of_nodes(),
        'n_edges': G.number_of_edges(),
        'density': nx.density(G),
        'is_connected': nx.is_connected(G) if not G.is_directed() else nx.is_weakly_connected(G),
    }
    
    # Connected components
    if G.is_directed():
        components = list(nx.weakly_connected_components(G))
    else:
        components = list(nx.connected_components(G))
    
    metrics['n_components'] = len(components)
    metrics['largest_component_size'] = len(max(components, key=len)) if components else 0
    
    # Centrality measures (on largest component if disconnected)
    if metrics['largest_component_size'] > 1:
        if not metrics['is_connected']:
            # Work with largest component
            largest_cc = max(components, key=len)
            G_main = G.subgraph(largest_cc)
        else:
            G_main = G
        
        # Degree centrality
        if G_main.number_of_nodes() > 0:
            degree_cent = nx.degree_centrality(G_main)
            metrics['avg_degree_centrality'] = np.mean(list(degree_cent.values()))
            
            # Betweenness centrality (sample if large)
            if G_main.number_of_nodes() <= 1000:
                between_cent = nx.betweenness_centrality(G_main)
                metrics['avg_betweenness_centrality'] = np.mean(list(between_cent.values()))
            
            # Closeness centrality (sample if large)
            if G_main.number_of_nodes() <= 500:
                close_cent = nx.closeness_centrality(G_main)
                metrics['avg_closeness_centrality'] = np.mean(list(close_cent.values()))
    
    # Clustering coefficient
    if not G.is_directed() and G.number_of_nodes() > 0:
        metrics['avg_clustering'] = nx.average_clustering(G)
    
    return metrics


def find_main_path(G: nx.DiGraph, method: str = "spc") -> List:
    """
    Find main path in citation network using search path count.
    
    Parameters
    ----------
    G : nx.DiGraph
        Directed citation graph
    method : str
        Method for path finding ('spc' for search path count)
        
    Returns
    -------
    List
        List of nodes in main path
    """
    logger.info(f"Finding main path using {method} method")
    
    if G.number_of_nodes() == 0:
        return []
    
    # Ensure DAG (remove cycles if any)
    if not nx.is_directed_acyclic_graph(G):
        logger.warning("Graph has cycles, removing back edges")
        G = nx.DiGraph(G)
        back_edges = [(u, v) for u, v in G.edges() if not nx.is_directed_acyclic_graph(G)]
        G.remove_edges_from(back_edges)
    
    # Compute search path counts
    spc = {}
    
    # Topological sort
    topo_order = list(nx.topological_sort(G))
    
    # Initialize
    for node in G.nodes():
        spc[node] = 0
    
    # Forward pass
    for node in topo_order:
        if G.in_degree(node) == 0:  # Source node
            spc[node] = 1
        else:
            spc[node] = sum(spc[pred] for pred in G.predecessors(node))
    
    # Backward pass to get traversal weights
    traversal_weights = {}
    
    for node in reversed(topo_order):
        if G.out_degree(node) == 0:  # Sink node
            traversal_weights[node] = spc[node]
        else:
            traversal_weights[node] = sum(traversal_weights[succ] for succ in G.successors(node))
    
    # Find path with highest traversal weights
    # Start from source with highest weight
    sources = [n for n in G.nodes() if G.in_degree(n) == 0]
    if not sources:
        return []
    
    start_node = max(sources, key=lambda x: traversal_weights.get(x, 0))
    
    # Trace path
    path = [start_node]
    current = start_node
    
    while G.out_degree(current) > 0:
        # Choose successor with highest traversal weight
        successors = list(G.successors(current))
        next_node = max(successors, key=lambda x: traversal_weights.get(x, 0))
        path.append(next_node)
        current = next_node
    
    logger.info(f"Found main path with {len(path)} nodes")
    return path


def extract_backbone(G: nx.Graph, method: str = "disparity", alpha: float = 0.05) -> nx.Graph:
    """
    Extract network backbone using disparity filter.
    
    Parameters
    ----------
    G : nx.Graph
        Weighted graph
    method : str
        Backbone extraction method
    alpha : float
        Significance level for disparity filter
        
    Returns
    -------
    nx.Graph
        Backbone network
    """
    logger.info(f"Extracting backbone using {method} filter with alpha={alpha}")
    
    if method != "disparity":
        raise ValueError("Only disparity filter is currently implemented")
    
    # Create backbone graph
    backbone = nx.Graph()
    backbone.add_nodes_from(G.nodes(data=True))
    
    # Disparity filter
    for node in G.nodes():
        neighbors = list(G.neighbors(node))
        if len(neighbors) <= 1:
            continue
        
        # Get edge weights
        weights = [G[node][neighbor].get('weight', 1) for neighbor in neighbors]
        total_weight = sum(weights)
        
        if total_weight == 0:
            continue
        
        # Compute p-values
        k = len(neighbors)
        for i, neighbor in enumerate(neighbors):
            w = weights[i]
            p_ij = w / total_weight
            
            # Disparity measure
            if k > 1:
                p_value = (1 - p_ij) ** (k - 1)
                
                # Keep edge if significant
                if p_value < alpha:
                    backbone.add_edge(node, neighbor, **G[node][neighbor])
    
    logger.info(f"Backbone: {backbone.number_of_nodes()} nodes, {backbone.number_of_edges()} edges")
    return backbone


def analyze_temporal_patterns(G: nx.DiGraph) -> Dict:
    """
    Analyze temporal patterns in citation network.
    
    Parameters
    ----------
    G : nx.DiGraph
        Citation graph with 'year' node attributes
        
    Returns
    -------
    Dict
        Temporal analysis results
    """
    logger.info("Analyzing temporal citation patterns")
    
    # Get years
    years = {}
    for node, data in G.nodes(data=True):
        year = data.get('year')
        if year is not None:
            years[node] = year
    
    if not years:
        return {"error": "No year information available"}
    
    # Citation age distribution
    citation_ages = []
    
    for citing, cited in G.edges():
        citing_year = years.get(citing)
        cited_year = years.get(cited)
        
        if citing_year is not None and cited_year is not None:
            age = citing_year - cited_year
            if age >= 0:  # Only forward citations
                citation_ages.append(age)
    
    results = {
        'n_temporal_citations': len(citation_ages),
        'mean_citation_age': np.mean(citation_ages) if citation_ages else 0,
        'median_citation_age': np.median(citation_ages) if citation_ages else 0,
        'max_citation_age': np.max(citation_ages) if citation_ages else 0,
    }
    
    # Citation age distribution
    if citation_ages:
        age_counts = Counter(citation_ages)
        results['citation_age_distribution'] = dict(age_counts)
    
    return results


def multi_resolution_community_detection(
    G: nx.Graph,
    resolutions: List[float] = None,
    method: str = 'louvain'
) -> Dict[float, List[Set]]:
    """
    Detect communities at multiple resolution scales.
    
    Parameters
    ----------
    G : nx.Graph
        Input graph
    resolutions : list of float
        Resolution parameters to test
    method : str
        Community detection method ('louvain' or 'leiden')
    
    Returns
    -------
    Dict[float, List[Set]]
        Communities at each resolution level
    """
    logger.info(f"Multi-resolution community detection using {method}")
    
    if resolutions is None:
        resolutions = [0.5, 1.0, 1.5, 2.0]
    
    communities_by_resolution = {}
    
    try:
        if method == 'louvain':
            import community as community_louvain
            
            for res in resolutions:
                partition = community_louvain.best_partition(G, resolution=res)
                
                # Convert to list of sets
                communities = defaultdict(set)
                for node, comm_id in partition.items():
                    communities[comm_id].add(node)
                
                communities_by_resolution[res] = list(communities.values())
                logger.info(f"  Resolution {res}: {len(communities)} communities")
        
        elif method == 'leiden':
            try:
                import igraph as ig
                import leidenalg
                
                # Convert to igraph
                ig_graph = ig.Graph.from_networkx(G)
                
                for res in resolutions:
                    partition = leidenalg.find_partition(
                        ig_graph,
                        leidenalg.RBConfigurationVertexPartition,
                        resolution_parameter=res
                    )
                    
                    # Convert back to node sets
                    communities = []
                    for comm in partition:
                        node_names = [G.nodes()[i] for i in comm]
                        communities.append(set(node_names))
                    
                    communities_by_resolution[res] = communities
                    logger.info(f"  Resolution {res}: {len(communities)} communities")
            
            except ImportError:
                logger.warning("Leiden not available, falling back to Louvain")
                return multi_resolution_community_detection(G, resolutions, method='louvain')
        
        else:
            raise ValueError(f"Unknown method: {method}")
    
    except Exception as e:
        logger.error(f"Community detection failed: {e}")
        return {}
    
    return communities_by_resolution


def detect_bridge_papers(
    G: nx.Graph,
    cluster_attr: str = 'cluster',
    centrality_threshold: float = 0.7
) -> List[Tuple]:
    """
    Detect papers that bridge different research clusters.
    
    Parameters
    ----------
    G : nx.Graph
        Graph with cluster annotations
    cluster_attr : str
        Node attribute containing cluster ID
    centrality_threshold : float
        Percentile threshold for betweenness centrality
    
    Returns
    -------
    List[Tuple]
        List of (node, betweenness, cluster_connections)
    """
    logger.info("Detecting bridge papers between clusters")
    
    # Compute betweenness centrality
    betweenness = nx.betweenness_centrality(G, weight='weight' if G.is_weighted() else None)
    
    # Threshold
    threshold_value = np.percentile(list(betweenness.values()), centrality_threshold * 100)
    
    bridges = []
    
    for node, centrality in betweenness.items():
        if centrality < threshold_value:
            continue
        
        # Get neighbor clusters
        node_data = G.nodes[node]
        node_cluster = node_data.get(cluster_attr, -1)
        
        neighbor_clusters = set()
        for neighbor in G.neighbors(node):
            neighbor_cluster = G.nodes[neighbor].get(cluster_attr, -1)
            if neighbor_cluster != node_cluster and neighbor_cluster >= 0:
                neighbor_clusters.add(neighbor_cluster)
        
        if len(neighbor_clusters) >= 2:  # Connects multiple clusters
            bridges.append((
                node,
                centrality,
                node_cluster,
                list(neighbor_clusters),
                len(neighbor_clusters)
            ))
    
    # Sort by number of cluster connections
    bridges.sort(key=lambda x: (x[4], x[1]), reverse=True)
    
    logger.info(f"Found {len(bridges)} bridge papers")
    return bridges


def extract_hierarchical_backbone(
    G: nx.Graph,
    levels: int = 3,
    method: str = 'disparity',
    alpha: float = 0.05
) -> Dict[int, nx.Graph]:
    """
    Extract multi-level backbone hierarchy.
    
    Each level contains progressively stronger edges.
    
    Parameters
    ----------
    G : nx.Graph
        Weighted input graph
    levels : int
        Number of hierarchy levels
    method : str
        Backbone extraction method
    alpha : float
        Base significance level
    
    Returns
    -------
    Dict[int, nx.Graph]
        Backbone graphs at each level
    """
    logger.info(f"Extracting {levels}-level hierarchical backbone")
    
    backbones = {}
    
    # Level 0: Full graph
    backbones[0] = G.copy()
    
    # Extract increasingly strict backbones
    for level in range(1, levels):
        # Adjust alpha for this level (more strict)
        level_alpha = alpha / (2 ** level)
        
        logger.info(f"  Level {level}: alpha={level_alpha:.4f}")
        
        # Extract backbone from previous level
        prev_backbone = backbones[level - 1]
        
        if method == 'disparity':
            level_backbone = _disparity_filter(prev_backbone, level_alpha)
        elif method == 'weight_threshold':
            # Use percentile threshold
            threshold_pct = 50 + (level * 15)  # 50th, 65th, 80th percentiles
            level_backbone = _threshold_filter(prev_backbone, threshold_pct)
        else:
            raise ValueError(f"Unknown method: {method}")
        
        backbones[level] = level_backbone
        
        logger.info(f"    Nodes: {level_backbone.number_of_nodes()}, Edges: {level_backbone.number_of_edges()}")
    
    return backbones


def _disparity_filter(G: nx.Graph, alpha: float) -> nx.Graph:
    """Apply disparity filter to extract backbone."""
    backbone = nx.Graph()
    backbone.add_nodes_from(G.nodes(data=True))
    
    for node in G.nodes():
        neighbors = list(G.neighbors(node))
        if len(neighbors) <= 1:
            continue
        
        weights = [G[node][neighbor].get('weight', 1) for neighbor in neighbors]
        total_weight = sum(weights)
        
        if total_weight == 0:
            continue
        
        k = len(neighbors)
        
        for i, neighbor in enumerate(neighbors):
            w = weights[i]
            p_ij = w / total_weight
            
            if k > 1:
                p_value = (1 - p_ij) ** (k - 1)
                
                if p_value < alpha:
                    backbone.add_edge(node, neighbor, **G[node][neighbor])
    
    return backbone


def _threshold_filter(G: nx.Graph, percentile: float) -> nx.Graph:
    """Extract backbone by weight threshold."""
    weights = [data.get('weight', 1) for u, v, data in G.edges(data=True)]
    threshold = np.percentile(weights, percentile)
    
    backbone = nx.Graph()
    backbone.add_nodes_from(G.nodes(data=True))
    
    for u, v, data in G.edges(data=True):
        if data.get('weight', 1) >= threshold:
            backbone.add_edge(u, v, **data)
    
    logger.debug(f"Threshold filter: {backbone.number_of_edges()} edges above {threshold:.2f}")
    return backbone


def analyze_citation_flows_between_clusters(
    G: nx.DiGraph,
    cluster_attr: str = 'cluster'
) -> pd.DataFrame:
    """
    Analyze citation flows between research clusters.
    
    Parameters
    ----------
    G : nx.DiGraph
        Directed citation graph
    cluster_attr : str
        Node attribute containing cluster ID
    
    Returns
    -------
    pd.DataFrame
        Citation flow matrix (from_cluster -> to_cluster)
    """
    logger.info("Analyzing inter-cluster citation flows")
    
    # Get clusters
    clusters = set()
    for node, data in G.nodes(data=True):
        cluster = data.get(cluster_attr, -1)
        if cluster >= 0:
            clusters.add(cluster)
    
    clusters = sorted(clusters)
    
    # Build flow matrix
    flow_matrix = np.zeros((len(clusters), len(clusters)))
    cluster_to_idx = {c: i for i, c in enumerate(clusters)}
    
    for citing, cited in G.edges():
        citing_cluster = G.nodes[citing].get(cluster_attr, -1)
        cited_cluster = G.nodes[cited].get(cluster_attr, -1)
        
        if citing_cluster >= 0 and cited_cluster >= 0:
            i = cluster_to_idx[citing_cluster]
            j = cluster_to_idx[cited_cluster]
            flow_matrix[i, j] += 1
    
    # Convert to DataFrame
    flow_df = pd.DataFrame(
        flow_matrix,
        index=[f"Cluster_{c}" for c in clusters],
        columns=[f"Cluster_{c}" for c in clusters]
    )
    
    # Summary statistics
    total_citations = flow_matrix.sum()
    internal_citations = np.diag(flow_matrix).sum()
    external_citations = total_citations - internal_citations
    
    logger.info(f"Total citations: {int(total_citations)}")
    logger.info(f"Internal citations: {int(internal_citations)} ({internal_citations/total_citations*100:.1f}%)")
    logger.info(f"External citations: {int(external_citations)} ({external_citations/total_citations*100:.1f}%)")
    
    return flow_df


def find_knowledge_flows(
    G: nx.DiGraph,
    time_attr: str = 'year',
    cluster_attr: str = 'cluster',
    time_window: int = 3
) -> List[Dict]:
    """
    Identify knowledge flow patterns between clusters over time.
    
    Parameters
    ----------
    G : nx.DiGraph
        Citation graph
    time_attr : str
        Node attribute for time
    cluster_attr : str
        Node attribute for cluster
    time_window : int
        Years to aggregate
    
    Returns
    -------
    List[Dict]
        Knowledge flow events
    """
    logger.info("Identifying knowledge flow patterns")
    
    # Get temporal citation edges
    temporal_flows = []
    
    for citing, cited in G.edges():
        citing_data = G.nodes[citing]
        cited_data = G.nodes[cited]
        
        citing_year = citing_data.get(time_attr)
        cited_year = cited_data.get(time_attr)
        citing_cluster = citing_data.get(cluster_attr, -1)
        cited_cluster = cited_data.get(cluster_attr, -1)
        
        if all([citing_year, cited_year, citing_cluster >= 0, cited_cluster >= 0]):
            temporal_flows.append({
                'citing': citing,
                'cited': cited,
                'citing_year': citing_year,
                'cited_year': cited_year,
                'citing_cluster': citing_cluster,
                'cited_cluster': cited_cluster,
                'citation_age': citing_year - cited_year
            })
    
    # Aggregate into time windows
    flows_df = pd.DataFrame(temporal_flows)
    
    if len(flows_df) == 0:
        return []
    
    # Group by time window and cluster pairs
    flows_df['time_window'] = flows_df['citing_year'] // time_window * time_window
    
    flow_patterns = flows_df.groupby(
        ['time_window', 'citing_cluster', 'cited_cluster']
    ).agg({
        'citing': 'count',
        'citation_age': 'mean'
    }).reset_index()
    
    flow_patterns.columns = ['time_window', 'from_cluster', 'to_cluster', 'citation_count', 'avg_age']
    
    # Filter for significant flows (cross-cluster only)
    significant_flows = flow_patterns[
        (flow_patterns['from_cluster'] != flow_patterns['to_cluster']) &
        (flow_patterns['citation_count'] >= 3)
    ].copy()
    
    logger.info(f"Found {len(significant_flows)} significant knowledge flows")
    
    return significant_flows.to_dict('records')


if __name__ == "__main__":
    # Test with synthetic data
    logger.info("Testing network analysis with synthetic data")
    
    # Create test DataFrame
    test_data = {
        'openalex_id': ['A1', 'A2', 'A3', 'A4', 'A5'],
        'title': ['Paper 1', 'Paper 2', 'Paper 3', 'Paper 4', 'Paper 5'],
        'year': [2020, 2021, 2021, 2022, 2022],
        'journal': ['Journal A', 'Journal B', 'Journal A', 'Journal C', 'Journal B'],
        'referenced_works': [
            [],
            ['A1'],
            ['A1', 'A2'],
            ['A2', 'A3'],
            ['A1', 'A3', 'A4']
        ],
        'cluster': [0, 0, 1, 1, 0]
    }
    
    df = pd.DataFrame(test_data)
    
    # Test direct citation graph
    citation_graph = build_direct_citation_graph(df)
    print(f"\nCitation graph: {citation_graph.number_of_nodes()} nodes, {citation_graph.number_of_edges()} edges")
    
    # Test co-citation graph
    cocitation_graph = build_cocitation_graph(df, min_cocitations=1)
    print(f"Co-citation graph: {cocitation_graph.number_of_nodes()} nodes, {cocitation_graph.number_of_edges()} edges")
    
    # Test bibliographic coupling
    coupling_graph = build_bibliographic_coupling_graph(df, min_shared=1)
    print(f"Bibliographic coupling graph: {coupling_graph.number_of_nodes()} nodes, {coupling_graph.number_of_edges()} edges")
    
    # Test metrics
    metrics = compute_network_metrics(citation_graph)
    print(f"\nNetwork metrics: {metrics}")
    
    # Test main path
    main_path = find_main_path(citation_graph)
    print(f"Main path: {main_path}")
    
    # Test temporal analysis
    temporal = analyze_temporal_patterns(citation_graph)
    print(f"Temporal analysis: {temporal}")
    
    # Test multi-resolution communities
    if coupling_graph.number_of_edges() > 0:
        try:
            communities = multi_resolution_community_detection(coupling_graph, resolutions=[0.5, 1.0])
            print(f"\nMulti-resolution communities: {len(communities)} resolutions tested")
        except Exception as e:
            print(f"Community detection test skipped: {e}")
    
    # Test bridge detection
    bridges = detect_bridge_papers(coupling_graph, cluster_attr='cluster')
    print(f"Bridge papers: {len(bridges)}")
    
    # Test citation flows
    flows = analyze_citation_flows_between_clusters(citation_graph, cluster_attr='cluster')
    print(f"\nCitation flow matrix:\n{flows}")
