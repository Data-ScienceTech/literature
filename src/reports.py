"""
Report generation module for research stream dialog cards.
Creates comprehensive summaries of research clusters with key papers, origins, and trends.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple
import logging
from pathlib import Path
import json
from datetime import datetime
import networkx as nx

# Import our modules
from .embeddings import find_similar_papers
from .bursts import detect_prevalence_bursts, extract_terms_from_text
from .rpys import compute_rpys_spectrum, detect_rpys_peaks
from .networks import compute_network_metrics

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DialogCardGenerator:
    """
    Generator for research stream dialog cards.
    """
    
    def __init__(self, df: pd.DataFrame, embeddings: Optional[np.ndarray] = None):
        """
        Initialize dialog card generator.
        
        Parameters
        ----------
        df : pd.DataFrame
            Main dataset with papers
        embeddings : np.ndarray, optional
            Paper embeddings for similarity analysis
        """
        self.df = df
        self.embeddings = embeddings
        
    def generate_cluster_card(
        self,
        cluster_id: int,
        citation_graph: Optional[nx.Graph] = None,
        prevalence_bursts: Optional[Dict] = None,
        rpys_data: Optional[Dict] = None
    ) -> Dict:
        """
        Generate dialog card for a specific research cluster.
        
        Parameters
        ----------
        cluster_id : int
            Cluster ID to analyze
        citation_graph : nx.Graph, optional
            Citation network for centrality analysis
        prevalence_bursts : Dict, optional
            Burst detection results
        rpys_data : Dict, optional
            RPYS analysis results
            
        Returns
        -------
        Dict
            Dialog card data
        """
        logger.info(f"Generating dialog card for cluster {cluster_id}")
        
        # Get cluster papers
        cluster_papers = self.df[self.df.get('cluster', -1) == cluster_id].copy()
        
        if len(cluster_papers) == 0:
            return {"error": f"No papers found for cluster {cluster_id}"}
        
        # Basic cluster info
        card = {
            "cluster_id": cluster_id,
            "n_papers": len(cluster_papers),
            "year_range": {
                "start": int(cluster_papers['year'].min()) if cluster_papers['year'].notna().any() else None,
                "end": int(cluster_papers['year'].max()) if cluster_papers['year'].notna().any() else None
            },
            "journals": cluster_papers['journal'].value_counts().head(5).to_dict(),
            "generated_at": datetime.now().isoformat()
        }
        
        # Generate cluster name/label
        card["name"] = self._generate_cluster_name(cluster_papers)
        card["description"] = self._generate_cluster_description(cluster_papers)
        
        # Key papers analysis
        card["key_papers"] = self._identify_key_papers(cluster_papers, citation_graph)
        
        # Origins and foundations
        card["origins"] = self._analyze_cluster_origins(cluster_papers, rpys_data)
        
        # Temporal dynamics and bursts
        card["temporal_dynamics"] = self._analyze_temporal_dynamics(cluster_papers, prevalence_bursts)
        
        # Current frontier
        card["current_frontier"] = self._identify_current_frontier(cluster_papers)
        
        # Network properties
        if citation_graph:
            card["network_properties"] = self._analyze_cluster_network(cluster_papers, citation_graph)
        
        # Research themes
        card["themes"] = self._extract_research_themes(cluster_papers)
        
        return card
    
    def _generate_cluster_name(self, cluster_papers: pd.DataFrame) -> str:
        """Generate a descriptive name for the cluster."""
        # Extract common terms from titles and abstracts
        all_text = []
        
        for _, paper in cluster_papers.iterrows():
            title = paper.get('title', '')
            abstract = paper.get('abstract', '')
            text = f"{title} {abstract}".strip()
            if text:
                all_text.append(text)
        
        if not all_text:
            return f"Research Cluster {cluster_papers.iloc[0].get('cluster', 'Unknown')}"
        
        # Extract frequent terms
        all_terms = []
        for text in all_text:
            terms = extract_terms_from_text(text, min_length=4, max_length=15)
            all_terms.extend(terms)
        
        # Get most common meaningful terms
        from collections import Counter
        term_counts = Counter(all_terms)
        
        # Filter out generic terms
        generic_terms = {
            'research', 'study', 'analysis', 'paper', 'article', 'findings', 
            'results', 'conclusion', 'method', 'approach', 'framework',
            'model', 'theory', 'empirical', 'theoretical', 'literature'
        }
        
        meaningful_terms = [
            term for term, count in term_counts.most_common(10)
            if term not in generic_terms and len(term) > 3
        ]
        
        if meaningful_terms:
            # Use top 2-3 terms
            name_terms = meaningful_terms[:3]
            return " & ".join([term.title() for term in name_terms])
        else:
            return f"Research Stream {cluster_papers.iloc[0].get('cluster', 'Unknown')}"
    
    def _generate_cluster_description(self, cluster_papers: pd.DataFrame) -> str:
        """Generate a description of the cluster's scope."""
        n_papers = len(cluster_papers)
        year_range = f"{cluster_papers['year'].min():.0f}-{cluster_papers['year'].max():.0f}"
        
        # Top journals
        top_journals = cluster_papers['journal'].value_counts().head(3)
        journal_text = ", ".join([f"{journal} ({count})" for journal, count in top_journals.items()])
        
        # Basic description
        description = f"Research stream comprising {n_papers} papers published between {year_range}. "
        description += f"Primary publication venues: {journal_text}. "
        
        # Add thematic description if possible
        if 'abstract' in cluster_papers.columns:
            abstracts_available = cluster_papers['abstract'].notna().sum()
            if abstracts_available > 0:
                description += f"Based on analysis of {abstracts_available} abstracts and titles, "
                description += "this stream focuses on interdisciplinary research examining "
                description += "organizational and technological phenomena."
        
        return description
    
    def _identify_key_papers(
        self, 
        cluster_papers: pd.DataFrame, 
        citation_graph: Optional[nx.Graph] = None
    ) -> Dict:
        """Identify key papers in the cluster."""
        key_papers = {
            "most_cited": [],
            "most_recent": [],
            "central_papers": [],
            "foundational": []
        }
        
        # Most cited papers
        if 'cited_by_count' in cluster_papers.columns:
            most_cited = cluster_papers.nlargest(5, 'cited_by_count')
            key_papers["most_cited"] = [
                {
                    "title": row.get('title', ''),
                    "authors": row.get('authors', ''),
                    "year": row.get('year'),
                    "journal": row.get('journal', ''),
                    "citations": row.get('cited_by_count', 0),
                    "doi": row.get('doi', '')
                }
                for _, row in most_cited.iterrows()
            ]
        
        # Most recent papers (last 2 years)
        if 'year' in cluster_papers.columns:
            max_year = cluster_papers['year'].max()
            recent_papers = cluster_papers[cluster_papers['year'] >= max_year - 1]
            if len(recent_papers) > 0:
                # Sort by citations within recent papers
                if 'cited_by_count' in recent_papers.columns:
                    recent_papers = recent_papers.nlargest(3, 'cited_by_count')
                else:
                    recent_papers = recent_papers.head(3)
                
                key_papers["most_recent"] = [
                    {
                        "title": row.get('title', ''),
                        "authors": row.get('authors', ''),
                        "year": row.get('year'),
                        "journal": row.get('journal', ''),
                        "citations": row.get('cited_by_count', 0),
                        "doi": row.get('doi', '')
                    }
                    for _, row in recent_papers.iterrows()
                ]
        
        # Central papers (if citation graph available)
        if citation_graph is not None:
            cluster_nodes = []
            for _, row in cluster_papers.iterrows():
                node_id = row.get('openalex_id')
                if node_id and node_id in citation_graph:
                    cluster_nodes.append(node_id)
            
            if cluster_nodes:
                # Compute centrality for cluster nodes
                subgraph = citation_graph.subgraph(cluster_nodes)
                if len(subgraph) > 1:
                    centrality = nx.betweenness_centrality(subgraph)
                    
                    # Get top central papers
                    top_central = sorted(centrality.items(), key=lambda x: x[1], reverse=True)[:3]
                    
                    for node_id, cent_score in top_central:
                        paper_row = cluster_papers[cluster_papers['openalex_id'] == node_id]
                        if len(paper_row) > 0:
                            row = paper_row.iloc[0]
                            key_papers["central_papers"].append({
                                "title": row.get('title', ''),
                                "authors": row.get('authors', ''),
                                "year": row.get('year'),
                                "journal": row.get('journal', ''),
                                "centrality_score": cent_score,
                                "doi": row.get('doi', '')
                            })
        
        # Foundational papers (earliest with high citations)
        if 'year' in cluster_papers.columns and 'cited_by_count' in cluster_papers.columns:
            min_year = cluster_papers['year'].min()
            early_papers = cluster_papers[cluster_papers['year'] <= min_year + 2]
            if len(early_papers) > 0:
                foundational = early_papers.nlargest(3, 'cited_by_count')
                key_papers["foundational"] = [
                    {
                        "title": row.get('title', ''),
                        "authors": row.get('authors', ''),
                        "year": row.get('year'),
                        "journal": row.get('journal', ''),
                        "citations": row.get('cited_by_count', 0),
                        "doi": row.get('doi', '')
                    }
                    for _, row in foundational.iterrows()
                ]
        
        return key_papers
    
    def _analyze_cluster_origins(
        self, 
        cluster_papers: pd.DataFrame, 
        rpys_data: Optional[Dict] = None
    ) -> Dict:
        """Analyze the origins and foundations of the cluster."""
        origins = {
            "earliest_papers": [],
            "foundational_period": None,
            "rpys_peaks": []
        }
        
        # Earliest papers
        if 'year' in cluster_papers.columns:
            earliest_year = cluster_papers['year'].min()
            earliest_papers = cluster_papers[cluster_papers['year'] == earliest_year]
            
            origins["earliest_papers"] = [
                {
                    "title": row.get('title', ''),
                    "authors": row.get('authors', ''),
                    "year": row.get('year'),
                    "journal": row.get('journal', ''),
                    "doi": row.get('doi', '')
                }
                for _, row in earliest_papers.head(3).iterrows()
            ]
            
            # Foundational period
            year_counts = cluster_papers['year'].value_counts().sort_index()
            if len(year_counts) > 0:
                # Find period with consistent growth
                growth_periods = []
                for i in range(len(year_counts) - 2):
                    years = year_counts.index[i:i+3]
                    counts = year_counts.iloc[i:i+3]
                    if all(counts.iloc[j] <= counts.iloc[j+1] for j in range(2)):
                        growth_periods.append((years[0], years[-1], counts.sum()))
                
                if growth_periods:
                    # Best growth period
                    best_period = max(growth_periods, key=lambda x: x[2])
                    origins["foundational_period"] = {
                        "start_year": int(best_period[0]),
                        "end_year": int(best_period[1]),
                        "total_papers": int(best_period[2])
                    }
        
        # RPYS peaks (if available)
        if rpys_data and 'peaks' in rpys_data:
            origins["rpys_peaks"] = rpys_data['peaks'][:5]  # Top 5 peaks
        
        return origins
    
    def _analyze_temporal_dynamics(
        self, 
        cluster_papers: pd.DataFrame, 
        prevalence_bursts: Optional[Dict] = None
    ) -> Dict:
        """Analyze temporal dynamics and bursts."""
        dynamics = {
            "publication_trend": {},
            "growth_rate": None,
            "bursts": [],
            "peak_years": []
        }
        
        if 'year' in cluster_papers.columns:
            # Publication trend
            year_counts = cluster_papers['year'].value_counts().sort_index()
            dynamics["publication_trend"] = year_counts.to_dict()
            
            # Growth rate (papers per year)
            if len(year_counts) > 1:
                years = year_counts.index.values
                counts = year_counts.values
                
                # Linear regression for growth rate
                from scipy import stats
                slope, intercept, r_value, p_value, std_err = stats.linregress(years, counts)
                dynamics["growth_rate"] = {
                    "slope": slope,
                    "r_squared": r_value ** 2,
                    "p_value": p_value
                }
            
            # Peak years (local maxima)
            peak_years = []
            for i in range(1, len(year_counts) - 1):
                if (year_counts.iloc[i] > year_counts.iloc[i-1] and 
                    year_counts.iloc[i] > year_counts.iloc[i+1]):
                    peak_years.append({
                        "year": int(year_counts.index[i]),
                        "papers": int(year_counts.iloc[i])
                    })
            dynamics["peak_years"] = peak_years
        
        # Bursts (if available)
        if prevalence_bursts:
            cluster_id = cluster_papers.iloc[0].get('cluster')
            if cluster_id in prevalence_bursts:
                dynamics["bursts"] = [
                    {
                        "start_year": start,
                        "end_year": end,
                        "strength": strength
                    }
                    for start, end, strength in prevalence_bursts[cluster_id]
                ]
        
        return dynamics
    
    def _identify_current_frontier(self, cluster_papers: pd.DataFrame) -> Dict:
        """Identify current research frontier."""
        frontier = {
            "recent_papers": [],
            "emerging_themes": [],
            "future_directions": []
        }
        
        # Recent papers (last 2 years)
        if 'year' in cluster_papers.columns:
            max_year = cluster_papers['year'].max()
            recent_papers = cluster_papers[cluster_papers['year'] >= max_year - 1]
            
            frontier["recent_papers"] = [
                {
                    "title": row.get('title', ''),
                    "authors": row.get('authors', ''),
                    "year": row.get('year'),
                    "journal": row.get('journal', ''),
                    "doi": row.get('doi', '')
                }
                for _, row in recent_papers.head(5).iterrows()
            ]
            
            # Emerging themes from recent papers
            if len(recent_papers) > 0:
                recent_text = []
                for _, row in recent_papers.iterrows():
                    title = row.get('title', '')
                    abstract = row.get('abstract', '')
                    text = f"{title} {abstract}".strip()
                    if text:
                        recent_text.append(text)
                
                if recent_text:
                    # Extract terms from recent papers
                    all_terms = []
                    for text in recent_text:
                        terms = extract_terms_from_text(text, min_length=4)
                        all_terms.extend(terms)
                    
                    from collections import Counter
                    term_counts = Counter(all_terms)
                    
                    # Filter for emerging themes
                    emerging_terms = [
                        term for term, count in term_counts.most_common(10)
                        if count >= 2 and len(term) > 4
                    ]
                    
                    frontier["emerging_themes"] = emerging_terms[:5]
        
        return frontier
    
    def _analyze_cluster_network(
        self, 
        cluster_papers: pd.DataFrame, 
        citation_graph: nx.Graph
    ) -> Dict:
        """Analyze network properties of the cluster."""
        # Get cluster nodes
        cluster_nodes = []
        for _, row in cluster_papers.iterrows():
            node_id = row.get('openalex_id')
            if node_id and node_id in citation_graph:
                cluster_nodes.append(node_id)
        
        if not cluster_nodes:
            return {"error": "No cluster papers found in citation graph"}
        
        # Create cluster subgraph
        subgraph = citation_graph.subgraph(cluster_nodes)
        
        # Compute network metrics
        metrics = compute_network_metrics(subgraph)
        
        # Add cluster-specific metrics
        metrics["cluster_size"] = len(cluster_nodes)
        metrics["internal_edges"] = subgraph.number_of_edges()
        
        # External connections
        external_edges = 0
        for node in cluster_nodes:
            for neighbor in citation_graph.neighbors(node):
                if neighbor not in cluster_nodes:
                    external_edges += 1
        
        metrics["external_edges"] = external_edges
        metrics["internal_external_ratio"] = (
            metrics["internal_edges"] / external_edges 
            if external_edges > 0 else float('inf')
        )
        
        return metrics
    
    def _extract_research_themes(self, cluster_papers: pd.DataFrame) -> List[Dict]:
        """Extract main research themes from the cluster."""
        themes = []
        
        # Combine all text
        all_text = []
        for _, row in cluster_papers.iterrows():
            title = row.get('title', '')
            abstract = row.get('abstract', '')
            text = f"{title} {abstract}".strip()
            if text:
                all_text.append(text)
        
        if not all_text:
            return themes
        
        # Extract and count terms
        all_terms = []
        for text in all_text:
            terms = extract_terms_from_text(text, min_length=3, max_length=20)
            all_terms.extend(terms)
        
        from collections import Counter
        term_counts = Counter(all_terms)
        
        # Group related terms into themes
        theme_keywords = {
            "Organizational Behavior": [
                "organizational", "behavior", "management", "leadership", "team", 
                "employee", "workplace", "culture", "performance"
            ],
            "Technology & Innovation": [
                "technology", "innovation", "digital", "artificial intelligence", 
                "machine learning", "automation", "platform", "algorithm"
            ],
            "Strategy & Competition": [
                "strategy", "competitive", "advantage", "market", "business model", 
                "entrepreneurship", "venture", "startup"
            ],
            "Social Networks": [
                "network", "social", "relationship", "collaboration", "partnership", 
                "alliance", "community", "connection"
            ]
        }
        
        # Score themes based on term presence
        theme_scores = {}
        for theme_name, keywords in theme_keywords.items():
            score = 0
            matching_terms = []
            
            for keyword in keywords:
                for term, count in term_counts.items():
                    if keyword in term.lower():
                        score += count
                        matching_terms.append((term, count))
            
            if score > 0:
                theme_scores[theme_name] = {
                    "score": score,
                    "terms": sorted(matching_terms, key=lambda x: x[1], reverse=True)[:5]
                }
        
        # Convert to list format
        for theme_name, data in sorted(theme_scores.items(), key=lambda x: x[1]["score"], reverse=True):
            themes.append({
                "name": theme_name,
                "score": data["score"],
                "key_terms": [term for term, count in data["terms"]]
            })
        
        return themes[:5]  # Top 5 themes


def generate_summary_report(
    df: pd.DataFrame,
    cluster_cards: Dict[int, Dict],
    output_path: Optional[str] = None
) -> Dict:
    """
    Generate overall summary report of all clusters.
    
    Parameters
    ----------
    df : pd.DataFrame
        Main dataset
    cluster_cards : Dict[int, Dict]
        Dialog cards for all clusters
    output_path : str, optional
        Path to save the report
        
    Returns
    -------
    Dict
        Summary report
    """
    logger.info("Generating summary report")
    
    summary = {
        "dataset_overview": {
            "total_papers": len(df),
            "year_range": {
                "start": int(df['year'].min()) if df['year'].notna().any() else None,
                "end": int(df['year'].max()) if df['year'].notna().any() else None
            },
            "unique_journals": df['journal'].nunique() if 'journal' in df.columns else 0,
            "papers_with_abstracts": df['abstract'].notna().sum() if 'abstract' in df.columns else 0
        },
        "clustering_overview": {
            "total_clusters": len(cluster_cards),
            "largest_cluster_size": max([card.get("n_papers", 0) for card in cluster_cards.values()]) if cluster_cards else 0,
            "smallest_cluster_size": min([card.get("n_papers", 0) for card in cluster_cards.values()]) if cluster_cards else 0,
            "mean_cluster_size": np.mean([card.get("n_papers", 0) for card in cluster_cards.values()]) if cluster_cards else 0
        },
        "temporal_patterns": {},
        "top_clusters": [],
        "generated_at": datetime.now().isoformat()
    }
    
    # Temporal patterns
    if 'year' in df.columns:
        year_counts = df['year'].value_counts().sort_index()
        summary["temporal_patterns"] = {
            "papers_per_year": year_counts.to_dict(),
            "peak_year": int(year_counts.idxmax()),
            "peak_count": int(year_counts.max())
        }
    
    # Top clusters by size
    cluster_sizes = [(cid, card.get("n_papers", 0)) for cid, card in cluster_cards.items()]
    cluster_sizes.sort(key=lambda x: x[1], reverse=True)
    
    for cid, size in cluster_sizes[:10]:
        card = cluster_cards[cid]
        summary["top_clusters"].append({
            "cluster_id": cid,
            "name": card.get("name", f"Cluster {cid}"),
            "size": size,
            "year_range": card.get("year_range", {}),
            "description": card.get("description", "")[:200] + "..." if len(card.get("description", "")) > 200 else card.get("description", "")
        })
    
    # Save report if path provided
    if output_path:
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(summary, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Summary report saved to {output_path}")
    
    return summary


if __name__ == "__main__":
    # Test dialog card generation with synthetic data
    logger.info("Testing dialog card generation")
    
    # Create test data
    test_data = {
        'cluster': [0, 0, 0, 1, 1, 2, 2, 2, 2],
        'title': [
            'Organizational Learning in Digital Transformation',
            'Leadership Styles in Remote Work Environments', 
            'Team Performance and Collaboration Technologies',
            'Machine Learning Applications in Business Strategy',
            'Artificial Intelligence and Competitive Advantage',
            'Social Networks and Innovation Diffusion',
            'Network Effects in Platform Ecosystems',
            'Community Building in Digital Platforms',
            'Relationship Management in Virtual Organizations'
        ],
        'authors': ['Author A', 'Author B', 'Author C', 'Author D', 'Author E', 'Author F', 'Author G', 'Author H', 'Author I'],
        'year': [2020, 2021, 2022, 2019, 2021, 2018, 2020, 2021, 2022],
        'journal': ['Journal A', 'Journal A', 'Journal B', 'Journal C', 'Journal C', 'Journal D', 'Journal D', 'Journal D', 'Journal B'],
        'cited_by_count': [45, 32, 18, 67, 89, 23, 34, 41, 29],
        'doi': [f'10.1000/test.{i}' for i in range(9)],
        'abstract': [
            'This study examines organizational learning processes during digital transformation initiatives.',
            'We investigate different leadership approaches in distributed work settings.',
            'Analysis of team dynamics and technology adoption in collaborative environments.',
            'Machine learning techniques applied to strategic decision making processes.',
            'Exploring how AI technologies create sustainable competitive advantages.',
            'Social network analysis of innovation adoption and diffusion patterns.',
            'Network effects and their impact on platform-based business models.',
            'Community formation and engagement in digital platform ecosystems.',
            'Managing relationships and trust in virtual organizational structures.'
        ]
    }
    
    df = pd.DataFrame(test_data)
    
    # Test dialog card generation
    generator = DialogCardGenerator(df)
    
    # Generate cards for each cluster
    cluster_cards = {}
    for cluster_id in df['cluster'].unique():
        card = generator.generate_cluster_card(cluster_id)
        cluster_cards[cluster_id] = card
        print(f"\nCluster {cluster_id} - {card.get('name', 'Unknown')}")
        print(f"Papers: {card.get('n_papers', 0)}")
        print(f"Description: {card.get('description', 'N/A')[:100]}...")
    
    # Generate summary report
    summary = generate_summary_report(df, cluster_cards)
    print(f"\nSummary Report:")
    print(f"Total papers: {summary['dataset_overview']['total_papers']}")
    print(f"Total clusters: {summary['clustering_overview']['total_clusters']}")
    print(f"Largest cluster: {summary['clustering_overview']['largest_cluster_size']} papers")
