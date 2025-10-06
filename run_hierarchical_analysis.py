"""
Multi-Level Hierarchical Research Stream Analysis

This script performs state-of-the-art multi-level hierarchical clustering
and network analysis on research corpora, revealing nested research communities
and knowledge flow patterns.

Features:
- Multi-resolution Leiden clustering (3-4 levels deep)
- HDBSCAN hierarchical density-based clustering  
- Recursive quality-driven subdivision
- Cross-level bridge paper detection
- Hierarchical citation flow analysis
- Interactive hierarchical dialog cards

Uses cutting-edge methods:
- Traag et al. (2019) - Leiden algorithm
- McInnes et al. (2017) - HDBSCAN
- Serrano et al. (2009) - Network backbone extraction
"""

import sys
import os
import json
import time
from pathlib import Path
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from typing import Dict, List, Optional

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from src.hierarchical_clustering import (
    LeidenMultiResolution,
    HDBSCANHierarchical,
    RecursiveLeiden,
    HierarchicalClusterTree,
    compare_hierarchies
)
from src.embeddings import ScientificEmbedder
from src.networks import (
    build_direct_citation_graph,
    build_bibliographic_coupling_graph,
    multi_resolution_community_detection,
    detect_bridge_papers,
    extract_hierarchical_backbone,
    analyze_citation_flows_between_clusters,
    find_knowledge_flows
)
from src.bursts import compute_cluster_prevalence, detect_prevalence_bursts
from src.reports import DialogCardGenerator


def load_and_prepare_data(corpus_name: str = "ais_basket_enriched") -> pd.DataFrame:
    """
    Load and prepare research corpus.
    
    Parameters
    ----------
    corpus_name : str
        Which corpus to use: 'ais_basket_enriched' (RECOMMENDED), 'recommended', 'hq_2010+', etc.
    
    Returns
    -------
    pd.DataFrame
        Prepared corpus
    """
    print("=" * 80)
    print("STEP 1: LOADING AND PREPARING DATA")
    print("=" * 80)
    
    data_dir = Path('data/clean')
    
    if corpus_name == "ais_basket_enriched":
        # Load enriched corpus with keywords from OpenAlex
        print(f"📚 Loading AIS BASKET ENRICHED corpus (8 journals, OpenAlex enhanced)")
        print(f"   ✨ Includes: abstracts (99.9%), keywords (99.9%), affiliations, citations")
        
        # Try JSON first for full data, fallback to parquet
        json_path = data_dir / 'ais_basket_corpus_enriched.json'
        parquet_path = data_dir / 'ais_basket_corpus_enriched.parquet'
        
        if json_path.exists():
            print(f"   Loading from JSON for complete keyword data...")
            import json
            with open(json_path, encoding='utf-8') as f:
                data = json.load(f)
            df = pd.DataFrame(data)
            corpus_path = None
        elif parquet_path.exists():
            print(f"   Loading from parquet...")
            df = pd.read_parquet(parquet_path)
            corpus_path = None
        else:
            print(f"   ❌ Enriched corpus not found!")
            sys.exit(1)
            
    elif corpus_name == "recommended":
        corpus_path = data_dir / 'is_corpus_recommended.parquet'
        print(f"📚 Loading RECOMMENDED corpus (6 premier IS journals, 2000+)")
        df = None
    elif corpus_name == "hq_2010+":
        corpus_path = data_dir / 'is_corpus_hq_2010+.parquet'
        print(f"📚 Loading HIGH-QUALITY 2010+ corpus")
        df = None
    else:
        corpus_path = data_dir / f'{corpus_name}.parquet'
        print(f"📚 Loading {corpus_name}")
        df = None
    
    if df is None and corpus_path is not None:
        if not corpus_path.exists():
            print(f"❌ Corpus not found: {corpus_path}")
            print(f"\nAvailable corpora:")
            for f in sorted(data_dir.glob('*.parquet')):
                print(f"  - {f.stem}")
            for f in sorted(data_dir.glob('*.json')):
                print(f"  - {f.stem} (JSON)")
            sys.exit(1)
        
        df = pd.read_parquet(corpus_path)
    
    # Ensure df is loaded
    assert df is not None, "Failed to load corpus"
    
    print(f"✅ Loaded {len(df):,} papers")
    print(f"   Date range: {df['year'].min()}-{df['year'].max()}")
    print(f"   Journals: {df['journal'].nunique()}")
    
    # Extract keywords from 'subject' field if available
    has_keywords = False
    if 'subject' in df.columns:
        print(f"\n🔑 Extracting keywords from OpenAlex 'subject' field...")
        
        def extract_keywords_from_subject(subject_data):
            """Extract keywords from OpenAlex subject field"""
            # Handle None/NaN
            if subject_data is None:
                return []
            
            # Already a list
            if isinstance(subject_data, list):
                return subject_data
            
            # String - try to parse as JSON
            if isinstance(subject_data, str):
                try:
                    import json
                    parsed = json.loads(subject_data)
                    if isinstance(parsed, list):
                        return parsed
                except:
                    pass
            
            return []
        
        df['keywords'] = df['subject'].apply(extract_keywords_from_subject)
        df['keyword_count'] = df['keywords'].apply(len)
        
        papers_with_keywords = (df['keyword_count'] > 0).sum()
        pct_with_keywords = 100 * papers_with_keywords / len(df)
        avg_keywords = df['keyword_count'].mean()
        
        print(f"   ✅ Papers with keywords: {papers_with_keywords:,} ({pct_with_keywords:.1f}%)")
        print(f"   ✅ Average keywords per paper: {avg_keywords:.1f}")
        
        if pct_with_keywords > 50:
            has_keywords = True
            # Show sample keywords
            sample_paper = df[df['keyword_count'] > 0].iloc[0]
            print(f"   📋 Sample keywords: {', '.join(sample_paper['keywords'][:5])}")
    
    # Rename columns for consistency
    rename_dict = {
        'openalex_id': 'id',
        'title': 'Title',
        'year': 'Year',
        'journal': 'Journal',
        'abstract': 'Abstract'
    }
    
    # Handle different citation field names
    if 'cited_by_count' in df.columns:
        rename_dict['cited_by_count'] = 'Citations'
    elif 'citation_count' in df.columns:
        rename_dict['citation_count'] = 'Citations'
    elif 'openalex_cited_by_count' in df.columns:
        rename_dict['openalex_cited_by_count'] = 'Citations'
    
    df = df.rename(columns=rename_dict)
    
    # Ensure we have abstracts
    df = df[df['Abstract'].notna() & (df['Abstract'].str.len() > 50)].copy()
    print(f"   With abstracts: {len(df):,} papers")
    
    # Create combined text for embedding
    # ENHANCED: Include keywords for better semantic clustering!
    if has_keywords and 'keywords' in df.columns:
        print(f"\n✨ Creating ENHANCED text embeddings (Title + Abstract + Keywords)")
        
        def format_keywords(kw_list):
            """Format keywords as text"""
            if not isinstance(kw_list, list) or not kw_list:
                return ''
            # Join keywords with semicolons
            return '; '.join(str(k) for k in kw_list if k)
        
        df['keywords_text'] = df['keywords'].apply(format_keywords)
        
        # Enhanced text: title + abstract + keywords
        df['text'] = (
            df['Title'].fillna('') + '. ' + 
            df['Abstract'].fillna('') + '. ' +
            'Keywords: ' + df['keywords_text'].fillna('')
        )
        
        # Show sample
        sample = df[df['keywords_text'].str.len() > 0].iloc[0]
        print(f"   📝 Sample enhanced text length: {len(sample['text'])} chars")
        print(f"   📋 Sample includes {len(sample['keywords'])} keywords")
    else:
        print(f"\n📝 Creating standard text embeddings (Title + Abstract)")
        df['text'] = df['Title'].fillna('') + '. ' + df['Abstract'].fillna('')
    
    # Format authors
    def format_authors(authors_list):
        if not isinstance(authors_list, list) or not authors_list:
            return ''
        return '; '.join([a.get('author', a.get('name', '')) for a in authors_list[:5] if isinstance(a, dict)])
    
    if 'authors' in df.columns:
        df['Author'] = df['authors'].apply(format_authors)
    
    print(f"\n📊 Corpus Statistics:")
    print(f"   Mean citations: {df['Citations'].mean():.1f}")
    print(f"   Median citations: {df['Citations'].median():.0f}")
    print(f"   Total citations: {df['Citations'].sum():,}")
    
    return df


def generate_or_load_embeddings(
    df: pd.DataFrame,
    force_regenerate: bool = False
) -> np.ndarray:
    """Generate or load SPECTER2 embeddings."""
    print("\n" + "=" * 80)
    print("STEP 2: EMBEDDINGS")
    print("=" * 80)
    
    embeddings_path = Path('data/embeddings_hierarchical.npy')
    
    if embeddings_path.exists() and not force_regenerate:
        print(f"📂 Loading existing embeddings from {embeddings_path}")
        embeddings = np.load(embeddings_path)
        print(f"✅ Loaded embeddings: {embeddings.shape}")
        return embeddings
    
    print("🤖 Generating SPECTER2 embeddings...")
    print(f"   Model: allenai/specter2 (state-of-the-art for scientific papers)")
    print(f"   Papers to embed: {len(df):,}")
    
    try:
        embedder = ScientificEmbedder(
            model_name="allenai/specter2",
            device=None  # Auto-detect
        )
        
        texts = df['text'].tolist()
        
        print(f"   Embedding {len(texts):,} documents...")
        print(f"   This may take 5-15 minutes...")
        
        start_time = time.time()
        embeddings = embedder.embed_texts(
            texts,
            batch_size=32,
            show_progress=True,
            normalize=True
        )
        elapsed = time.time() - start_time
        
        print(f"⏱️  Completed in {elapsed/60:.1f} minutes")
        print(f"📊 Embedding shape: {embeddings.shape}")
        
        # Save
        embedder.save_embeddings(embeddings, str(embeddings_path))
        
        return embeddings
        
    except Exception as e:
        print(f"❌ SPECTER2 failed: {e}")
        print(f"🔄 Falling back to all-MiniLM-L6-v2...")
        
        embedder = ScientificEmbedder(
            model_name="all-MiniLM-L6-v2",
            device=None
        )
        
        embeddings = embedder.embed_texts(
            df['text'].tolist(),
            batch_size=64,
            show_progress=True,
            normalize=True
        )
        
        embedder.save_embeddings(embeddings, str(embeddings_path))
        return embeddings


def perform_hierarchical_clustering(
    embeddings: np.ndarray,
    method: str = "leiden",
    max_levels: int = 4,
    min_cluster_size: int = 20
) -> HierarchicalClusterTree:
    """
    Perform multi-level hierarchical clustering.
    
    Parameters
    ----------
    embeddings : np.ndarray
        Paper embeddings
    method : str
        Clustering method: 'leiden', 'hdbscan', or 'recursive'
    max_levels : int
        Maximum hierarchy depth
    min_cluster_size : int
        Minimum cluster size
    
    Returns
    -------
    HierarchicalClusterTree
        Complete hierarchy
    """
    print("\n" + "=" * 80)
    print(f"STEP 3: MULTI-LEVEL HIERARCHICAL CLUSTERING ({method.upper()})")
    print("=" * 80)
    
    if method == "leiden":
        print("🕸️  Leiden Multi-Resolution Clustering")
        print("   Method: Vary resolution parameter for coarse-to-fine hierarchy")
        
        clusterer = LeidenMultiResolution(
            embeddings=embeddings,
            k=15,
            metric='cosine'
        )
        
        # Auto-detect optimal resolutions
        resolutions = clusterer.find_optimal_resolutions(
            resolution_range=(0.3, 3.0),
            n_resolutions=12
        )
        
        print(f"   Selected {len(resolutions)} resolution levels:")
        for i, res in enumerate(resolutions):
            print(f"      Level {i}: resolution={res:.2f}")
        
        hierarchy = clusterer.build_hierarchy(
            resolutions=resolutions,
            min_cluster_size=min_cluster_size,
            max_levels=max_levels
        )
    
    elif method == "hdbscan":
        print("🎯 HDBSCAN Hierarchical Clustering")
        print("   Method: Density-based with recursive subdivision")
        
        clusterer = HDBSCANHierarchical(
            embeddings=embeddings,
            metric='euclidean'
        )
        
        hierarchy = clusterer.extract_hierarchy(
            min_cluster_size=min_cluster_size,
            max_levels=max_levels
        )
    
    elif method == "recursive":
        print("🔄 Recursive Leiden Clustering")
        print("   Method: Quality-driven recursive subdivision")
        
        clusterer = RecursiveLeiden(
            embeddings=embeddings,
            k=15,
            metric='cosine'
        )
        
        hierarchy = clusterer.build_hierarchy(
            resolution=1.0,
            min_cluster_size=min_cluster_size,
            max_depth=max_levels,
            quality_threshold=0.3
        )
    
    else:
        raise ValueError(f"Unknown method: {method}")
    
    # Print hierarchy summary
    print(f"\n✅ HIERARCHY CONSTRUCTED:")
    print(f"   Total clusters: {len(hierarchy.all_nodes)}")
    print(f"   Maximum depth: {hierarchy.max_depth()}")
    print(f"   Root clusters: {len(hierarchy.root_nodes)}")
    
    for level in range(hierarchy.max_depth() + 1):
        level_clusters = hierarchy.get_level_clusters(level)
        sizes = [c.size for c in level_clusters]
        print(f"   Level {level}: {len(level_clusters)} clusters (mean size: {np.mean(sizes):.0f})")
    
    # Save hierarchy
    output_path = Path('data') / f'hierarchy_{method}.json'
    hierarchy.save_json(str(output_path))
    print(f"\n💾 Saved hierarchy to {output_path}")
    
    return hierarchy


def flatten_hierarchy_to_df(
    df: pd.DataFrame,
    hierarchy: HierarchicalClusterTree
) -> pd.DataFrame:
    """
    Add hierarchical cluster labels to dataframe.
    
    Adds columns: cluster_l0, cluster_l1, cluster_l2, etc.
    """
    print("\n📋 Flattening hierarchy to DataFrame...")
    
    max_depth = hierarchy.max_depth()
    
    # Initialize cluster columns
    for level in range(max_depth + 1):
        df[f'cluster_l{level}'] = -1
    
    # Assign clusters at each level
    for node in hierarchy.all_nodes.values():
        level = node.level
        cluster_id = node.id
        paper_indices = node.paper_indices
        
        df.loc[df.index[paper_indices], f'cluster_l{level}'] = cluster_id
    
    # Add full hierarchical path
    def get_hierarchy_path(row):
        path_parts = []
        for level in range(max_depth + 1):
            cluster = row.get(f'cluster_l{level}', -1)
            if cluster != -1:
                path_parts.append(str(cluster))
        return ' > '.join(path_parts) if path_parts else 'unclustered'
    
    df['hierarchy_path'] = df.apply(get_hierarchy_path, axis=1)
    
    print(f"✅ Added {max_depth + 1} levels of cluster labels")
    
    return df


def analyze_hierarchical_structure(
    df: pd.DataFrame,
    hierarchy: HierarchicalClusterTree,
    embeddings: np.ndarray
) -> Dict:
    """Comprehensive analysis of hierarchical structure."""
    print("\n" + "=" * 80)
    print("STEP 4: HIERARCHICAL STRUCTURE ANALYSIS")
    print("=" * 80)
    
    analysis = {
        'hierarchy_stats': {},
        'level_analyses': {},
        'quality_metrics': {},
        'temporal_patterns': {}
    }
    
    # Overall hierarchy stats
    analysis['hierarchy_stats'] = {
        'total_clusters': len(hierarchy.all_nodes),
        'max_depth': hierarchy.max_depth(),
        'root_clusters': len(hierarchy.root_nodes),
        'leaf_clusters': len(hierarchy.get_leaf_clusters())
    }
    
    # Analyze each level
    for level in range(hierarchy.max_depth() + 1):
        print(f"\n📊 Analyzing Level {level}...")
        
        level_clusters = hierarchy.get_level_clusters(level)
        level_label_col = f'cluster_l{level}'
        
        if level_label_col not in df.columns:
            continue
        
        # Cluster sizes
        sizes = [c.size for c in level_clusters]
        
        # Temporal coverage
        temporal_stats = []
        for cluster in level_clusters:
            cluster_papers = df.iloc[cluster.paper_indices]
            if len(cluster_papers) > 0:
                temporal_stats.append({
                    'cluster_id': cluster.id,
                    'size': cluster.size,
                    'year_min': int(cluster_papers['Year'].min()),
                    'year_max': int(cluster_papers['Year'].max()),
                    'year_span': int(cluster_papers['Year'].max() - cluster_papers['Year'].min()),
                    'mean_citations': float(cluster_papers['Citations'].mean()),
                    'total_citations': int(cluster_papers['Citations'].sum())
                })
        
        analysis['level_analyses'][level] = {
            'n_clusters': len(level_clusters),
            'sizes': {
                'mean': float(np.mean(sizes)),
                'median': float(np.median(sizes)),
                'min': int(np.min(sizes)),
                'max': int(np.max(sizes)),
                'std': float(np.std(sizes))
            },
            'temporal': temporal_stats
        }
        
        print(f"   Clusters: {len(level_clusters)}")
        print(f"   Size range: {np.min(sizes)}-{np.max(sizes)} (mean: {np.mean(sizes):.0f})")
    
    # Quality metrics per level
    print(f"\n🎯 Computing quality metrics...")
    
    from sklearn.metrics import silhouette_score, davies_bouldin_score
    
    for level in range(hierarchy.max_depth() + 1):
        level_label_col = f'cluster_l{level}'
        
        if level_label_col in df.columns:
            labels = df[level_label_col].values
            
            # Handle both string and numeric labels
            # Filter out noise points (None, NaN, or negative values if numeric)
            if labels.dtype == 'object' or labels.dtype.name.startswith('str'):
                # String labels - filter out None/NaN
                valid_mask = pd.notna(labels) & (labels != '') & (labels != 'None')
            else:
                # Numeric labels - filter out negative (noise points)
                valid_mask = labels >= 0
            
            if valid_mask.sum() > 10 and len(set(labels[valid_mask])) > 1:
                try:
                    # Convert string labels to numeric for sklearn
                    unique_labels = sorted(set(labels[valid_mask]))
                    label_map = {label: i for i, label in enumerate(unique_labels)}
                    numeric_labels = np.array([label_map[label] for label in labels[valid_mask]])
                    
                    sil_score = silhouette_score(
                        embeddings[valid_mask],
                        numeric_labels,
                        metric='cosine',
                        sample_size=min(5000, valid_mask.sum())
                    )
                    
                    db_score = davies_bouldin_score(
                        embeddings[valid_mask],
                        numeric_labels
                    )
                    
                    analysis['quality_metrics'][level] = {
                        'silhouette': float(sil_score),
                        'davies_bouldin': float(db_score),
                        'n_clusters': len(unique_labels),
                        'n_papers': int(valid_mask.sum())
                    }
                    
                    print(f"   Level {level}: Silhouette={sil_score:.3f}, Davies-Bouldin={db_score:.3f} (n={len(unique_labels)} clusters, {valid_mask.sum()} papers)")
                except Exception as e:
                    print(f"   Level {level}: Could not compute metrics ({e})")
    
    return analysis


def perform_network_analysis(
    df: pd.DataFrame,
    hierarchy: HierarchicalClusterTree
) -> Dict:
    """
    Perform comprehensive network analysis.
    
    Builds citation networks and analyzes cross-cluster flows.
    """
    print("\n" + "=" * 80)
    print("STEP 5: CITATION NETWORK ANALYSIS")
    print("=" * 80)
    
    network_analysis = {}
    
    # Check if we have OpenAlex data
    has_openalex = 'referenced_works' in df.columns and df['referenced_works'].notna().sum() > 0
    
    if not has_openalex:
        print("⚠️  No citation data available (missing referenced_works)")
        print("   Skipping citation network analysis")
        return {'status': 'no_citation_data'}
    
    # Build citation graph
    print("\n🌐 Building direct citation graph...")
    
    try:
        # Ensure column names match what networks.py expects
        df_network = df.copy()
        if 'id' in df.columns:
            df_network['openalex_id'] = df_network['id']
        
        citation_graph = build_direct_citation_graph(df_network)
        
        print(f"   Nodes: {citation_graph.number_of_nodes()}")
        print(f"   Edges: {citation_graph.number_of_edges()}")
        
        network_analysis['citation_graph'] = {
            'nodes': citation_graph.number_of_nodes(),
            'edges': citation_graph.number_of_edges(),
            'density': float(citation_graph.number_of_edges()) / (citation_graph.number_of_nodes() ** 2) if citation_graph.number_of_nodes() > 0 else 0
        }
        
    except Exception as e:
        print(f"   ❌ Citation graph construction failed: {e}")
        citation_graph = None
    
    # Build bibliographic coupling graph
    print("\n📚 Building bibliographic coupling graph...")
    
    try:
        coupling_graph = build_bibliographic_coupling_graph(df_network, min_shared=2)
        
        print(f"   Nodes: {coupling_graph.number_of_nodes()}")
        print(f"   Edges: {coupling_graph.number_of_edges()}")
        
        network_analysis['coupling_graph'] = {
            'nodes': coupling_graph.number_of_nodes(),
            'edges': coupling_graph.number_of_edges()
        }
        
    except Exception as e:
        print(f"   ❌ Coupling graph construction failed: {e}")
        coupling_graph = None
    
    # Analyze citation flows between clusters (at each level)
    print("\n🔀 Analyzing inter-cluster citation flows...")
    
    flow_analyses = {}
    
    for level in range(min(hierarchy.max_depth() + 1, 3)):  # First 3 levels
        cluster_col = f'cluster_l{level}'
        
        if cluster_col in df.columns and citation_graph is not None:
            try:
                # Add cluster attribute to graph
                for node in citation_graph.nodes():
                    paper_data = df[df.get('id', df.get('openalex_id')) == node]
                    if len(paper_data) > 0:
                        citation_graph.nodes[node][cluster_col] = paper_data.iloc[0][cluster_col]
                
                flow_matrix = analyze_citation_flows_between_clusters(
                    citation_graph,
                    cluster_attr=cluster_col
                )
                
                # Convert to dict for JSON
                flow_analyses[f'level_{level}'] = {
                    'matrix': flow_matrix.to_dict(),
                    'total_flows': int(flow_matrix.values.sum()),
                    'internal_ratio': float(np.diag(flow_matrix.values).sum() / flow_matrix.values.sum()) if flow_matrix.values.sum() > 0 else 0
                }
                
                print(f"   Level {level}: {flow_matrix.values.sum():.0f} total citations")
                
            except Exception as e:
                print(f"   Level {level}: Flow analysis failed ({e})")
    
    network_analysis['citation_flows'] = flow_analyses
    
    # Detect bridge papers
    print("\n🌉 Detecting bridge papers...")
    
    if coupling_graph is not None and coupling_graph.number_of_nodes() > 0:
        try:
            # Use level 0 clusters for bridge detection
            bridges = detect_bridge_papers(
                coupling_graph,
                cluster_attr='cluster_l0',
                centrality_threshold=0.9
            )
            
            network_analysis['bridge_papers'] = [
                {
                    'paper_id': str(b[0]),
                    'centrality': float(b[1]),
                    'home_cluster': str(b[2]),
                    'connected_clusters': [str(c) for c in b[3]],
                    'n_connections': int(b[4])
                }
                for b in bridges[:20]  # Top 20
            ]
            
            print(f"   Found {len(bridges)} bridge papers")
            if len(bridges) > 0:
                print(f"   Top bridge connects {bridges[0][4]} clusters")
            
        except Exception as e:
            print(f"   ❌ Bridge detection failed: {e}")
    
    return network_analysis


def generate_hierarchical_dialog_cards(
    df: pd.DataFrame,
    hierarchy: HierarchicalClusterTree,
    analysis: Dict
) -> Dict:
    """
    Generate nested dialog cards for hierarchical clusters.
    
    Each cluster gets a card showing:
    - Parent context
    - Key papers
    - Sub-clusters
    - Temporal dynamics
    """
    print("\n" + "=" * 80)
    print("STEP 6: GENERATING HIERARCHICAL DIALOG CARDS")
    print("=" * 80)
    
    dialog_cards = {}
    
    # Generate card for each cluster node
    for cluster_id, node in hierarchy.all_nodes.items():
        print(f"   Processing {cluster_id} (level {node.level}, {node.size} papers)...")
        
        # Get papers in this cluster
        cluster_papers = df.iloc[node.paper_indices].copy()
        
        if len(cluster_papers) == 0:
            continue
        
        # Basic info
        card = {
            'id': cluster_id,
            'level': node.level,
            'parent_id': node.parent_id,
            'size': node.size,
            'metadata': node.metadata,
            
            # Temporal
            'year_range': {
                'start': int(cluster_papers['Year'].min()),
                'end': int(cluster_papers['Year'].max()),
                'span': int(cluster_papers['Year'].max() - cluster_papers['Year'].min())
            },
            
            # Citations
            'citations': {
                'total': int(cluster_papers['Citations'].sum()),
                'mean': float(cluster_papers['Citations'].mean()),
                'median': float(cluster_papers['Citations'].median())
            },
            
            # Journals
            'journals': cluster_papers['Journal'].value_counts().head(5).to_dict(),
            
            # Children
            'children': [c.id for c in node.children],
            'n_children': len(node.children)
        }
        
        # Key papers
        top_papers = cluster_papers.nlargest(5, 'Citations')
        card['key_papers'] = []
        
        for _, paper in top_papers.iterrows():
            card['key_papers'].append({
                'title': paper['Title'],
                'year': int(paper['Year']),
                'citations': int(paper['Citations']),
                'journal': paper['Journal'],
                'authors': paper.get('Author', '')[:100]
            })
        
        # Topic keywords (simple TF-IDF on titles+abstracts)
        try:
            from sklearn.feature_extraction.text import TfidfVectorizer
            
            texts = cluster_papers['text'].fillna('').tolist()
            
            if len(texts) >= 5:
                vectorizer = TfidfVectorizer(
                    max_features=10,
                    ngram_range=(1, 2),
                    min_df=2,
                    stop_words='english'
                )
                
                tfidf_matrix = vectorizer.fit_transform(texts)
                feature_names = vectorizer.get_feature_names_out()
                
                scores = tfidf_matrix.sum(axis=0).A1
                top_indices = scores.argsort()[-10:][::-1]
                top_terms = [feature_names[i] for i in top_indices]
                
                card['top_terms'] = top_terms
        except:
            card['top_terms'] = []
        
        dialog_cards[cluster_id] = card
    
    # Save dialog cards
    output_path = Path('data') / 'hierarchical_dialog_cards.json'
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(dialog_cards, f, indent=2, ensure_ascii=False)
    
    print(f"\n💾 Saved {len(dialog_cards)} dialog cards to {output_path}")
    
    return dialog_cards


def visualize_hierarchy(
    hierarchy: HierarchicalClusterTree,
    dialog_cards: Dict,
    output_dir: Path
):
    """Create visualizations of the hierarchy."""
    print("\n" + "=" * 80)
    print("STEP 7: GENERATING VISUALIZATIONS")
    print("=" * 80)
    
    output_dir = Path(output_dir)
    output_dir.mkdir(exist_ok=True, parents=True)
    
    # 1. Hierarchy tree visualization
    print("🌳 Creating hierarchy tree diagram...")
    
    fig, ax = plt.subplots(figsize=(20, 12))
    
    # Draw tree level by level
    max_depth = hierarchy.max_depth()
    
    # Position nodes
    node_positions = {}
    level_counts = {level: len(hierarchy.get_level_clusters(level)) for level in range(max_depth + 1)}
    
    for level in range(max_depth + 1):
        clusters = hierarchy.get_level_clusters(level)
        n_clusters = len(clusters)
        
        y = max_depth - level
        
        for i, cluster in enumerate(sorted(clusters, key=lambda c: c.id)):
            x = (i + 0.5) / n_clusters if n_clusters > 0 else 0.5
            node_positions[cluster.id] = (x, y)
    
    # Draw edges
    for node in hierarchy.all_nodes.values():
        if node.parent_id and node.parent_id in node_positions:
            x1, y1 = node_positions[node.parent_id]
            x2, y2 = node_positions[node.id]
            ax.plot([x1, x2], [y1, y2], 'k-', alpha=0.3, linewidth=1)
    
    # Draw nodes
    for cluster_id, (x, y) in node_positions.items():
        node = hierarchy.get_node(cluster_id)
        size = node.size
        
        # Size proportional to cluster size
        markersize = np.sqrt(size) * 2
        
        ax.scatter(x, y, s=markersize, alpha=0.6, c=f'C{node.level}')
        
        # Label for large clusters
        if size > 50:
            ax.text(x, y, f"{size}", ha='center', va='center', fontsize=8)
    
    ax.set_ylim(-0.5, max_depth + 0.5)
    ax.set_xlim(-0.05, 1.05)
    ax.set_yticks(range(max_depth + 1))
    ax.set_yticklabels([f'Level {i}' for i in range(max_depth + 1)])
    ax.set_xlabel('Cluster Distribution')
    ax.set_title('Hierarchical Research Stream Structure', fontsize=16, fontweight='bold')
    ax.grid(True, alpha=0.2)
    
    plt.tight_layout()
    tree_path = output_dir / 'hierarchy_tree.png'
    plt.savefig(tree_path, dpi=300, bbox_inches='tight')
    print(f"   ✅ Saved to {tree_path}")
    plt.close()
    
    # 2. Cluster size distributions by level
    print("📊 Creating cluster size distributions...")
    
    fig, axes = plt.subplots(1, min(4, max_depth + 1), figsize=(16, 4))
    if max_depth == 0:
        axes = [axes]
    
    for level in range(min(4, max_depth + 1)):
        ax = axes[level] if max_depth > 0 else axes[0]
        
        clusters = hierarchy.get_level_clusters(level)
        sizes = [c.size for c in clusters]
        
        ax.hist(sizes, bins=20, edgecolor='black', alpha=0.7)
        ax.set_xlabel('Cluster Size')
        ax.set_ylabel('Frequency')
        ax.set_title(f'Level {level}\n({len(clusters)} clusters)')
        ax.grid(True, alpha=0.2)
    
    plt.suptitle('Cluster Size Distributions by Level', fontsize=14, fontweight='bold')
    plt.tight_layout()
    
    dist_path = output_dir / 'cluster_size_distributions.png'
    plt.savefig(dist_path, dpi=300, bbox_inches='tight')
    print(f"   ✅ Saved to {dist_path}")
    plt.close()
    
    print(f"\n✅ Visualizations saved to {output_dir}/")


def main():
    """Run complete hierarchical analysis pipeline."""
    print("=" * 80)
    print("MULTI-LEVEL HIERARCHICAL RESEARCH STREAM ANALYSIS")
    print("=" * 80)
    print("State-of-the-art multi-resolution clustering with:")
    print("  • Leiden multi-resolution")
    print("  • HDBSCAN hierarchical density")
    print("  • Recursive quality-driven subdivision")
    print("  • Citation network analysis")
    print("  • Hierarchical dialog cards")
    print("=" * 80)
    
    start_time = time.time()
    
    # Configuration
    CORPUS_NAME = "ais_basket_enriched"  # ⭐ RECOMMENDED: OpenAlex-enriched with keywords!
    # Other options: "recommended", "hq_2010+", "ais_basket"
    
    CLUSTERING_METHOD = "leiden"  # or "hdbscan", "recursive"
    MAX_LEVELS = 4
    MIN_CLUSTER_SIZE = 20
    FORCE_REGENERATE_EMBEDDINGS = False
    
    # Step 1: Load data
    df = load_and_prepare_data(corpus_name=CORPUS_NAME)
    
    # Step 2: Embeddings
    embeddings = generate_or_load_embeddings(df, force_regenerate=FORCE_REGENERATE_EMBEDDINGS)
    
    # Step 3: Hierarchical clustering
    hierarchy = perform_hierarchical_clustering(
        embeddings=embeddings,
        method=CLUSTERING_METHOD,
        max_levels=MAX_LEVELS,
        min_cluster_size=MIN_CLUSTER_SIZE
    )
    
    # Step 4: Flatten hierarchy to DataFrame
    df = flatten_hierarchy_to_df(df, hierarchy)
    
    # Save clustered data
    output_path = Path('data') / 'papers_hierarchical_clustered.csv'
    df.to_csv(output_path, index=False)
    print(f"\n💾 Saved clustered dataset to {output_path}")
    
    # Step 5: Analyze structure
    analysis = analyze_hierarchical_structure(df, hierarchy, embeddings)
    
    # Save analysis
    analysis_path = Path('data') / 'hierarchical_analysis.json'
    with open(analysis_path, 'w') as f:
        json.dump(analysis, f, indent=2, default=str)
    print(f"💾 Saved analysis to {analysis_path}")
    
    # Step 6: Network analysis
    network_analysis = perform_network_analysis(df, hierarchy)
    
    # Save network analysis
    network_path = Path('data') / 'hierarchical_network_analysis.json'
    with open(network_path, 'w') as f:
        json.dump(network_analysis, f, indent=2, default=str)
    print(f"💾 Saved network analysis to {network_path}")
    
    # Step 7: Generate dialog cards
    dialog_cards = generate_hierarchical_dialog_cards(df, hierarchy, analysis)
    
    # Step 8: Visualizations
    visualize_hierarchy(hierarchy, dialog_cards, Path('data/visualizations'))
    
    # Final summary
    elapsed = time.time() - start_time
    
    print("\n" + "=" * 80)
    print("🎉 HIERARCHICAL ANALYSIS COMPLETE!")
    print("=" * 80)
    print(f"⏱️  Total time: {elapsed/60:.1f} minutes")
    print(f"\n📊 RESULTS:")
    print(f"   Papers analyzed: {len(df):,}")
    print(f"   Hierarchy depth: {hierarchy.max_depth()}")
    print(f"   Total clusters: {len(hierarchy.all_nodes)}")
    print(f"   Root clusters: {len(hierarchy.root_nodes)}")
    print(f"   Leaf clusters: {len(hierarchy.get_leaf_clusters())}")
    
    for level in range(hierarchy.max_depth() + 1):
        level_clusters = hierarchy.get_level_clusters(level)
        print(f"   Level {level}: {len(level_clusters)} clusters")
    
    print(f"\n📁 OUTPUT FILES:")
    print(f"   data/papers_hierarchical_clustered.csv - Clustered dataset")
    print(f"   data/hierarchy_{CLUSTERING_METHOD}.json - Hierarchy structure")
    print(f"   data/hierarchical_dialog_cards.json - Research stream cards")
    print(f"   data/hierarchical_analysis.json - Quality metrics")
    print(f"   data/hierarchical_network_analysis.json - Citation flows")
    print(f"   data/visualizations/ - Hierarchy visualizations")
    
    print(f"\n🎯 NEXT STEPS:")
    print(f"   1. Review hierarchical_dialog_cards.json for insights")
    print(f"   2. Explore hierarchy tree in visualizations/")
    print(f"   3. Generate interactive dashboard")
    print(f"   4. Drill down into specific research streams")


if __name__ == "__main__":
    main()
