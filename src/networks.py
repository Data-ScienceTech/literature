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
