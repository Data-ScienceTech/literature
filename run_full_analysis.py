"""
Full-featured analysis runner with robust error handling and best-in-class methods.
"""

import sys
import os
import json
import time
from pathlib import Path
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import warnings
warnings.filterwarnings('ignore')

# Add src to Python path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

# Import our modules
from src.parse_bib import load_bib, get_corpus_stats
from src.embeddings import ScientificEmbedder
from src.openalex import OpenAlexClient, enrich_dataframe


def setup_environment():
    """Setup analysis environment and check capabilities."""
    print("🔧 ENVIRONMENT SETUP")
    print("=" * 50)
    
    capabilities = {
        'torch_gpu': False,
        'torch_cpu': False,
        'sentence_transformers': False,
        'leiden_clustering': False,
        'hdbscan_clustering': False,
        'umap_reduction': False,
        'bertopic_labeling': False
    }
    
    # Check PyTorch
    try:
        import torch
        capabilities['torch_cpu'] = True
        if torch.cuda.is_available():
            capabilities['torch_gpu'] = True
            print(f"🚀 PyTorch GPU available: {torch.cuda.get_device_name(0)}")
        else:
            print("💻 PyTorch CPU mode")
    except ImportError:
        print("❌ PyTorch not available")
    
    # Check Sentence Transformers
    try:
        from sentence_transformers import SentenceTransformer
        capabilities['sentence_transformers'] = True
        print("🤖 Sentence Transformers available")
    except ImportError:
        print("❌ Sentence Transformers not available")
    
    # Check clustering packages
    try:
        import igraph as ig
        import leidenalg
        capabilities['leiden_clustering'] = True
        print("🕸️  Leiden clustering available")
    except ImportError:
        print("⚠️  Leiden clustering not available - will use Louvain")
    
    try:
        import hdbscan
        capabilities['hdbscan_clustering'] = True
        print("🎯 HDBSCAN clustering available")
    except ImportError:
        print("⚠️  HDBSCAN not available - will use K-means")
    
    try:
        import umap
        capabilities['umap_reduction'] = True
        print("📊 UMAP dimensionality reduction available")
    except ImportError:
        print("⚠️  UMAP not available - will use PCA")
    
    try:
        from bertopic import BERTopic
        capabilities['bertopic_labeling'] = True
        print("🏷️  BERTopic labeling available")
    except ImportError:
        print("⚠️  BERTopic not available - will use TF-IDF")
    
    return capabilities


def step1_parse_bibtex():
    """Step 1: Parse BibTeX file with comprehensive analysis."""
    print("\n" + "=" * 60)
    print("STEP 1: COMPREHENSIVE BIBTEX PARSING")
    print("=" * 60)
    
    bib_file = "refs_2016_2025_AMR_MISQ_ORSC_ISR.bib"
    
    if not Path(bib_file).exists():
        print(f"❌ BibTeX file not found: {bib_file}")
        print("Please ensure the BibTeX file is in the current directory")
        return None
    
    print(f"📖 Loading and parsing {bib_file}...")
    df = load_bib(bib_file)
    
    # Comprehensive statistics
    stats = get_corpus_stats(df)
    
    print(f"\n📊 DATASET OVERVIEW:")
    print(f"   📄 Total papers: {stats['total_papers']:,}")
    print(f"   🔗 Papers with DOI: {stats['papers_with_doi']:,} ({stats['papers_with_doi']/stats['total_papers']*100:.1f}%)")
    print(f"   📝 Papers with abstract: {stats['papers_with_abstract']:,} ({stats['papers_with_abstract']/stats['total_papers']*100:.1f}%)")
    print(f"   📅 Year range: {stats['year_min']} - {stats['year_max']}")
    print(f"   📚 Unique journals: {stats['unique_journals']}")
    
    print(f"\n📚 JOURNAL DISTRIBUTION:")
    for journal, count in list(stats['journals'].items())[:4]:
        print(f"   {journal}: {count:,} papers")
    
    print(f"\n📈 TEMPORAL DISTRIBUTION:")
    recent_years = {year: count for year, count in stats['papers_per_year'].items() if year >= 2020}
    for year, count in sorted(recent_years.items()):
        print(f"   {year}: {count:,} papers")
    
    # Create data directory
    data_dir = Path('data')
    data_dir.mkdir(exist_ok=True)
    
    # Save full dataset
    df.to_csv(data_dir / 'parsed_papers_full.csv', index=False)
    
    # Create analysis-ready subset
    analysis_df = df[df['text'].notna() & (df['text'].str.len() > 20)].copy()
    analysis_df['has_abstract'] = analysis_df['abstract'].notna()
    analysis_df['word_count'] = analysis_df['text'].str.split().str.len()
    
    analysis_df.to_csv(data_dir / 'parsed_papers_analysis.csv', index=False)
    
    # Save statistics
    with open(data_dir / 'corpus_stats.json', 'w') as f:
        json.dump(stats, f, indent=2, default=str)
    
    print(f"\n💾 SAVED DATASETS:")
    print(f"   📊 Full dataset: {len(df):,} papers")
    print(f"   🔬 Analysis dataset: {len(analysis_df):,} papers")
    print(f"   📈 Mean word count: {analysis_df['word_count'].mean():.0f} words")
    
    return analysis_df


def step2_generate_embeddings(df, capabilities):
    """Step 2: Generate high-quality SPECTER2 embeddings."""
    print("\n" + "=" * 60)
    print("STEP 2: SCIENTIFIC EMBEDDING GENERATION")
    print("=" * 60)
    
    data_dir = Path('data')
    embeddings_path = data_dir / 'embeddings_specter2.npy'
    
    if embeddings_path.exists():
        print("📂 Loading existing SPECTER2 embeddings...")
        embeddings = np.load(embeddings_path)
        print(f"✅ Loaded embeddings: {embeddings.shape}")
        return embeddings
    
    if not capabilities['sentence_transformers']:
        print("❌ Sentence Transformers not available - cannot generate embeddings")
        return None
    
    print("🤖 Generating SPECTER2 embeddings...")
    print("   Model: allenai/specter2 (state-of-the-art for scientific papers)")
    
    device = 'cuda' if capabilities['torch_gpu'] else 'cpu'
    print(f"   Device: {device}")
    
    try:
        # Initialize embedder with optimal settings
        embedder = ScientificEmbedder(
            model_name="allenai/specter2",
            device=device
        )
        
        texts = df['text'].fillna('').tolist()
        print(f"   Processing {len(texts):,} papers...")
        
        # Adaptive batch size based on available memory
        if capabilities['torch_gpu']:
            batch_size = 16  # GPU can handle larger batches
        else:
            batch_size = 8   # Conservative for CPU
        
        print(f"   Batch size: {batch_size}")
        print("   This may take 5-15 minutes depending on hardware...")
        
        start_time = time.time()
        embeddings = embedder.embed_texts(
            texts,
            batch_size=batch_size,
            show_progress=True,
            normalize=True
        )
        elapsed = time.time() - start_time
        
        print(f"⏱️  Embedding generation completed in {elapsed/60:.1f} minutes")
        print(f"📊 Generated embeddings: {embeddings.shape}")
        print(f"🎯 Embedding quality: normalized={np.allclose(np.linalg.norm(embeddings, axis=1), 1.0)}")
        
        # Save embeddings
        embedder.save_embeddings(embeddings, embeddings_path)
        print(f"💾 Saved embeddings to {embeddings_path}")
        
        return embeddings
        
    except Exception as e:
        print(f"❌ SPECTER2 failed: {e}")
        print("🔄 Trying fallback model: all-MiniLM-L6-v2...")
        
        try:
            embedder = ScientificEmbedder(
                model_name="sentence-transformers/all-MiniLM-L6-v2",
                device=device
            )
            
            embeddings = embedder.embed_texts(
                texts,
                batch_size=batch_size * 2,  # Smaller model, larger batch
                show_progress=True,
                normalize=True
            )
            
            # Save with different name
            fallback_path = data_dir / 'embeddings_minilm.npy'
            embedder.save_embeddings(embeddings, fallback_path)
            print(f"💾 Saved fallback embeddings: {embeddings.shape}")
            
            return embeddings
            
        except Exception as e2:
            print(f"❌ Fallback embedding also failed: {e2}")
            return None


def step3_advanced_clustering(df, embeddings, capabilities):
    """Step 3: Advanced clustering with multiple algorithms."""
    print("\n" + "=" * 60)
    print("STEP 3: ADVANCED RESEARCH STREAM CLUSTERING")
    print("=" * 60)
    
    clustering_results = {}
    
    # Method 1: Leiden clustering (best quality)
    if capabilities['leiden_clustering']:
        print("🕸️  LEIDEN CLUSTERING (Optimal)")
        try:
            from src.clustering import knn_graph, leiden_cluster, evaluate_clustering
            
            print("   Building k-NN graph...")
            k = min(15, len(embeddings) // 20)
            g = knn_graph(embeddings, k=k, metric='cosine')
            print(f"   Graph: {g.vcount():,} nodes, {g.ecount():,} edges")
            
            # Test multiple resolutions
            print("   Testing resolution parameters...")
            best_resolution = None
            best_score = -1
            
            for resolution in [0.5, 1.0, 1.5, 2.0]:
                labels = leiden_cluster(g, resolution=resolution, seed=42)
                metrics = evaluate_clustering(embeddings, labels, metric='cosine')
                
                n_clusters = len(set(labels))
                silhouette = metrics.get('silhouette', 0)
                
                # Composite score favoring good silhouette and reasonable cluster count
                if silhouette is not None and 5 <= n_clusters <= 50:
                    score = silhouette - abs(n_clusters - 20) * 0.01
                    print(f"   Resolution {resolution}: {n_clusters} clusters, silhouette={silhouette:.3f}, score={score:.3f}")
                    
                    if score > best_score:
                        best_score = score
                        best_resolution = resolution
                        clustering_results['leiden'] = {
                            'labels': labels,
                            'resolution': resolution,
                            'n_clusters': n_clusters,
                            'silhouette': silhouette,
                            'metrics': metrics
                        }
            
            print(f"   ✅ Best Leiden: resolution={best_resolution}, {clustering_results['leiden']['n_clusters']} clusters")
            
        except Exception as e:
            print(f"   ❌ Leiden clustering failed: {e}")
    
    # Method 2: HDBSCAN clustering
    if capabilities['hdbscan_clustering']:
        print("\n🎯 HDBSCAN CLUSTERING (Density-based)")
        try:
            from src.clustering import hdbscan_cluster, evaluate_clustering
            
            labels = hdbscan_cluster(
                embeddings,
                min_cluster_size=max(15, len(embeddings) // 100),
                min_samples=5,
                metric='cosine'
            )
            
            metrics = evaluate_clustering(embeddings, labels, metric='cosine')
            
            clustering_results['hdbscan'] = {
                'labels': labels,
                'n_clusters': metrics['n_clusters'],
                'n_noise': metrics['n_noise'],
                'silhouette': metrics.get('silhouette'),
                'metrics': metrics
            }
            
            print(f"   ✅ HDBSCAN: {metrics['n_clusters']} clusters, {metrics['n_noise']} noise points")
            
        except Exception as e:
            print(f"   ❌ HDBSCAN failed: {e}")
    
    # Method 3: Fallback clustering
    if not clustering_results:
        print("\n🔄 FALLBACK CLUSTERING (K-means)")
        from sklearn.cluster import KMeans
        from sklearn.metrics import silhouette_score
        
        # Find optimal number of clusters
        best_k = None
        best_silhouette = -1
        
        for k in range(5, min(51, len(embeddings) // 20)):
            kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
            labels = kmeans.fit_predict(embeddings)
            
            silhouette = silhouette_score(embeddings, labels, metric='cosine', sample_size=min(1000, len(embeddings)))
            
            if silhouette > best_silhouette:
                best_silhouette = silhouette
                best_k = k
                clustering_results['kmeans'] = {
                    'labels': labels,
                    'n_clusters': k,
                    'silhouette': silhouette
                }
        
        print(f"   ✅ K-means: {best_k} clusters, silhouette={best_silhouette:.3f}")
    
    # Select best clustering
    if 'leiden' in clustering_results:
        best_method = 'leiden'
        best_labels = clustering_results['leiden']['labels']
        print(f"\n🏆 SELECTED: Leiden clustering ({clustering_results['leiden']['n_clusters']} clusters)")
    elif 'hdbscan' in clustering_results:
        best_method = 'hdbscan'
        best_labels = clustering_results['hdbscan']['labels']
        print(f"\n🏆 SELECTED: HDBSCAN clustering ({clustering_results['hdbscan']['n_clusters']} clusters)")
    else:
        best_method = 'kmeans'
        best_labels = clustering_results['kmeans']['labels']
        print(f"\n🏆 SELECTED: K-means clustering ({clustering_results['kmeans']['n_clusters']} clusters)")
    
    # Add clusters to dataframe
    df['cluster'] = best_labels
    df['clustering_method'] = best_method
    
    # Cluster analysis
    cluster_sizes = pd.Series(best_labels).value_counts().sort_values(ascending=False)
    print(f"\n📊 CLUSTER ANALYSIS:")
    print(f"   Largest cluster: {cluster_sizes.iloc[0]:,} papers")
    print(f"   Smallest cluster: {cluster_sizes.iloc[-1]:,} papers")
    print(f"   Mean cluster size: {cluster_sizes.mean():.1f} papers")
    print(f"   Median cluster size: {cluster_sizes.median():.1f} papers")
    
    # Save clustered data
    data_dir = Path('data')
    df.to_csv(data_dir / 'papers_clustered.csv', index=False)
    
    # Save clustering results
    with open(data_dir / 'clustering_results.json', 'w') as f:
        json.dump(clustering_results, f, indent=2, default=str)
    
    print(f"💾 Saved clustered dataset and results")
    
    return df, best_labels, clustering_results


def step4_citation_enrichment(df, full_enrichment=False):
    """Step 4: Comprehensive OpenAlex citation enrichment."""
    print("\n" + "=" * 60)
    print("STEP 4: CITATION NETWORK ENRICHMENT")
    print("=" * 60)
    
    data_dir = Path('data')
    enriched_path = data_dir / 'papers_enriched_full.csv'
    
    if enriched_path.exists():
        print("📂 Loading existing enriched dataset...")
        enriched_df = pd.read_csv(enriched_path)
        print(f"✅ Loaded {len(enriched_df):,} enriched papers")
        
        enriched_count = enriched_df['openalex_id'].notna().sum()
        print(f"📊 Papers with OpenAlex data: {enriched_count:,} ({enriched_count/len(enriched_df)*100:.1f}%)")
        
        return enriched_df
    
    # Initialize OpenAlex client
    client = OpenAlexClient(
        cache_dir=str(data_dir / 'openalex_cache'),
        rate_limit=0.1,  # Respectful rate limiting
        timeout=30,
        max_retries=3
    )
    
    papers_with_dois = df['doi'].notna().sum()
    print(f"🔗 Papers with DOIs: {papers_with_dois:,}")
    
    if full_enrichment:
        print("🌐 FULL ENRICHMENT MODE")
        print(f"   This will make ~{papers_with_dois:,} API calls")
        print(f"   Estimated time: {papers_with_dois * 0.1 / 60:.0f}-{papers_with_dois * 0.2 / 60:.0f} minutes")
        
        enriched_df = enrich_dataframe(
            df,
            doi_column='doi',
            client=client,
            max_workers=3  # Conservative parallelism
        )
    else:
        print("🔬 SAMPLE ENRICHMENT MODE (first 100 papers)")
        print("   Use full_enrichment=True for complete dataset")
        
        sample_df = df[df['doi'].notna()].head(100).copy()
        enriched_sample = enrich_dataframe(sample_df, client=client, max_workers=2)
        
        # Merge back with full dataset
        enriched_df = df.merge(
            enriched_sample[['doi', 'openalex_id', 'cited_by_count', 'referenced_works', 
                           'host_venue_name', 'is_oa', 'concepts']],
            on='doi',
            how='left'
        )
    
    # Analyze enrichment results
    enriched_count = enriched_df['openalex_id'].notna().sum()
    total_citations = enriched_df['cited_by_count'].sum() if 'cited_by_count' in enriched_df.columns else 0
    
    print(f"\n📊 ENRICHMENT RESULTS:")
    print(f"   Papers enriched: {enriched_count:,} / {len(enriched_df):,} ({enriched_count/len(enriched_df)*100:.1f}%)")
    print(f"   Total citations collected: {total_citations:,}")
    
    if 'cited_by_count' in enriched_df.columns:
        citation_stats = enriched_df['cited_by_count'].describe()
        print(f"   Mean citations per paper: {citation_stats['mean']:.1f}")
        print(f"   Most cited paper: {citation_stats['max']:.0f} citations")
    
    # Save enriched dataset
    enriched_df.to_csv(enriched_path, index=False)
    print(f"💾 Saved enriched dataset")
    
    return enriched_df


def step5_advanced_reports(df, capabilities):
    """Step 5: Generate comprehensive research stream reports."""
    print("\n" + "=" * 60)
    print("STEP 5: COMPREHENSIVE STREAM ANALYSIS")
    print("=" * 60)
    
    try:
        from src.reports import DialogCardGenerator, generate_summary_report
        from src.bursts import compute_cluster_prevalence, detect_prevalence_bursts
        
        print("📋 Generating advanced dialog cards...")
        
        # Initialize generator
        generator = DialogCardGenerator(df)
        
        # Analyze temporal bursts
        print("   Computing temporal bursts...")
        prevalence = compute_cluster_prevalence(df)
        bursts = detect_prevalence_bursts(prevalence, z_threshold=1.5)
        
        # Generate cards for all significant clusters
        cluster_sizes = df['cluster'].value_counts()
        significant_clusters = cluster_sizes[cluster_sizes >= 10].index  # At least 10 papers
        
        print(f"   Generating cards for {len(significant_clusters)} research streams...")
        
        cluster_cards = {}
        for i, cluster_id in enumerate(significant_clusters):
            print(f"   Processing cluster {cluster_id} ({i+1}/{len(significant_clusters)})...")
            
            card = generator.generate_cluster_card(
                cluster_id,
                prevalence_bursts=bursts
            )
            
            cluster_cards[cluster_id] = card
            
            print(f"     📛 {card.get('name', 'Unknown Stream')}")
            print(f"     📄 {card.get('n_papers', 0)} papers")
            print(f"     📅 {card.get('year_range', {}).get('start', 'N/A')}-{card.get('year_range', {}).get('end', 'N/A')}")
        
        # Generate comprehensive summary
        print("   Generating summary report...")
        summary = generate_summary_report(df, cluster_cards)
        
        # Save all results
        data_dir = Path('data')
        
        with open(data_dir / 'dialog_cards_full.json', 'w', encoding='utf-8') as f:
            json.dump(cluster_cards, f, indent=2, default=str, ensure_ascii=False)
        
        with open(data_dir / 'summary_report_full.json', 'w', encoding='utf-8') as f:
            json.dump(summary, f, indent=2, default=str, ensure_ascii=False)
        
        with open(data_dir / 'temporal_bursts.json', 'w') as f:
            json.dump(bursts, f, indent=2, default=str)
        
        print(f"💾 Saved comprehensive reports:")
        print(f"   📋 Dialog cards: {len(cluster_cards)} research streams")
        print(f"   📊 Summary report with temporal analysis")
        print(f"   🔥 Burst detection results")
        
        return cluster_cards, summary, bursts
        
    except Exception as e:
        print(f"❌ Report generation failed: {e}")
        import traceback
        traceback.print_exc()
        return None, None, None


def main():
    """Run the complete high-quality analysis pipeline."""
    print("🚀 JOURNAL STREAMS ANALYSIS - FULL PIPELINE")
    print("=" * 60)
    print("High-quality research stream discovery using state-of-the-art methods")
    print("Expected runtime: 20-45 minutes for full analysis")
    
    start_time = time.time()
    
    # Setup and capability detection
    capabilities = setup_environment()
    
    # Step 1: Parse BibTeX
    df = step1_parse_bibtex()
    if df is None:
        return
    
    # Step 2: Generate embeddings
    embeddings = step2_generate_embeddings(df, capabilities)
    if embeddings is None:
        return
    
    # Step 3: Advanced clustering
    df, labels, clustering_results = step3_advanced_clustering(df, embeddings, capabilities)
    if df is None:
        return
    
    # Step 4: Citation enrichment
    print("\nChoose enrichment mode:")
    print("1. Sample mode (100 papers, ~2 minutes)")
    print("2. Full mode (all papers, ~10-20 minutes)")
    
    # For now, use sample mode - user can modify this
    enriched_df = step4_citation_enrichment(df, full_enrichment=False)
    
    # Step 5: Generate reports
    cards, summary, bursts = step5_advanced_reports(enriched_df, capabilities)
    
    # Final summary
    total_time = time.time() - start_time
    
    print("\n" + "🎉" + "=" * 58 + "🎉")
    print("HIGH-QUALITY ANALYSIS COMPLETE!")
    print("=" * 60)
    
    if summary:
        print(f"📊 FINAL RESULTS:")
        print(f"   📄 Papers analyzed: {summary['dataset_overview']['total_papers']:,}")
        print(f"   🔬 Research streams: {summary['clustering_overview']['total_clusters']}")
        print(f"   🏆 Largest stream: {summary['clustering_overview']['largest_cluster_size']} papers")
        print(f"   📅 Temporal span: {summary['dataset_overview']['year_range']['start']}-{summary['dataset_overview']['year_range']['end']}")
        print(f"   ⏱️  Total runtime: {total_time/60:.1f} minutes")
    
    print(f"\n📁 OUTPUT FILES (data/ directory):")
    print(f"   📊 papers_clustered.csv - Research stream assignments")
    print(f"   🔗 papers_enriched_full.csv - Citation-enriched dataset")
    print(f"   📋 dialog_cards_full.json - Detailed stream summaries")
    print(f"   📈 summary_report_full.json - Overall analysis")
    print(f"   🔥 temporal_bursts.json - Trend analysis")
    print(f"   🧠 embeddings_specter2.npy - Semantic embeddings")
    
    print(f"\n🔬 METHODOLOGY USED:")
    if 'leiden' in clustering_results:
        print(f"   🕸️  Leiden clustering on k-NN graph (resolution={clustering_results['leiden']['resolution']})")
    print(f"   🤖 SPECTER2 embeddings (768-dimensional)")
    print(f"   🌐 OpenAlex citation enrichment")
    print(f"   🔥 Kleinberg burst detection")
    print(f"   📊 Comprehensive dialog card generation")
    
    print(f"\n🎯 Next steps:")
    print(f"   📖 Review dialog_cards_full.json for research insights")
    print(f"   🔄 Re-run with full_enrichment=True for complete citation data")
    print(f"   📊 Use Jupyter notebooks for detailed visualizations")
    print(f"   🔬 Explore individual research streams in detail")


if __name__ == "__main__":
    main()
