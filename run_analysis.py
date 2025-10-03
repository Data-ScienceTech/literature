"""
Main analysis runner - executes the complete pipeline without notebooks.
"""

import sys
import os
import json
from pathlib import Path
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# Add src to Python path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

# Import our modules
from src.parse_bib import load_bib, get_corpus_stats
from src.embeddings import embed_texts, ScientificEmbedder
from src.openalex import OpenAlexClient, enrich_dataframe


def step1_parse_bibtex():
    """Step 1: Parse BibTeX file."""
    print("\n" + "="*60)
    print("STEP 1: PARSING BIBTEX FILE")
    print("="*60)
    
    bib_file = "refs_2016_2025_AMR_MISQ_ORSC_ISR.bib"
    
    if not Path(bib_file).exists():
        print(f"❌ BibTeX file not found: {bib_file}")
        return None
    
    print(f"📖 Loading {bib_file}...")
    df = load_bib(bib_file)
    
    # Get statistics
    stats = get_corpus_stats(df)
    
    print(f"\n📊 Dataset Statistics:")
    print(f"   Total papers: {stats['total_papers']}")
    print(f"   Papers with DOI: {stats['papers_with_doi']}")
    print(f"   Papers with abstract: {stats['papers_with_abstract']}")
    print(f"   Year range: {stats['year_min']} - {stats['year_max']}")
    print(f"   Unique journals: {stats['unique_journals']}")
    
    # Save parsed data
    data_dir = Path('data')
    data_dir.mkdir(exist_ok=True)
    
    df.to_csv(data_dir / 'parsed_papers_full.csv', index=False)
    
    # Create analysis subset (papers with sufficient text)
    analysis_df = df[df['text'].notna() & (df['text'].str.len() > 10)].copy()
    analysis_df.to_csv(data_dir / 'parsed_papers_analysis.csv', index=False)
    
    print(f"💾 Saved datasets:")
    print(f"   Full dataset: {len(df)} papers")
    print(f"   Analysis dataset: {len(analysis_df)} papers")
    
    return analysis_df


def step2_generate_embeddings(df):
    """Step 2: Generate SPECTER2 embeddings."""
    print("\n" + "="*60)
    print("STEP 2: GENERATING EMBEDDINGS")
    print("="*60)
    
    data_dir = Path('data')
    embeddings_path = data_dir / 'embeddings_specter2.npy'
    
    if embeddings_path.exists():
        print("📂 Loading existing embeddings...")
        embeddings = np.load(embeddings_path)
        print(f"✅ Loaded embeddings: {embeddings.shape}")
    else:
        print("🤖 Generating SPECTER2 embeddings...")
        print("   This may take several minutes...")
        
        try:
            embedder = ScientificEmbedder(model_name="allenai/specter2")
            texts = df['text'].fillna('').tolist()
            
            embeddings = embedder.embed_texts(
                texts, 
                batch_size=8,  # Conservative batch size
                show_progress=True,
                normalize=True
            )
            
            # Save embeddings
            embedder.save_embeddings(embeddings, embeddings_path)
            print(f"💾 Saved embeddings: {embeddings.shape}")
            
        except Exception as e:
            print(f"❌ Embedding generation failed: {e}")
            print("   Trying with smaller model...")
            
            # Fallback to smaller model
            try:
                embedder = ScientificEmbedder(model_name="sentence-transformers/all-MiniLM-L6-v2")
                embeddings = embedder.embed_texts(texts, batch_size=16, show_progress=True)
                embedder.save_embeddings(embeddings, embeddings_path)
                print(f"💾 Saved fallback embeddings: {embeddings.shape}")
            except Exception as e2:
                print(f"❌ Fallback embedding failed: {e2}")
                return None
    
    return embeddings


def step3_clustering(df, embeddings):
    """Step 3: Cluster papers into research streams."""
    print("\n" + "="*60)
    print("STEP 3: CLUSTERING INTO RESEARCH STREAMS")
    print("="*60)
    
    try:
        from src.clustering import knn_graph, leiden_cluster, evaluate_clustering
        
        print("🕸️ Building k-NN graph...")
        k = min(15, len(embeddings) // 10)  # Adaptive k
        g = knn_graph(embeddings, k=k, metric='cosine')
        print(f"   Graph: {g.vcount()} nodes, {g.ecount()} edges")
        
        print("🎯 Running Leiden clustering...")
        labels = leiden_cluster(g, resolution=1.0, seed=42)
        
        n_clusters = len(set(labels))
        print(f"   Found {n_clusters} clusters")
        
        # Evaluate clustering
        metrics = evaluate_clustering(embeddings, labels, metric='cosine')
        print(f"   Silhouette score: {metrics.get('silhouette', 'N/A')}")
        
        # Add clusters to dataframe
        df['cluster'] = labels
        
        # Save clustered data
        data_dir = Path('data')
        df.to_csv(data_dir / 'papers_clustered.csv', index=False)
        
        # Cluster statistics
        cluster_sizes = pd.Series(labels).value_counts().sort_values(ascending=False)
        print(f"   Largest cluster: {cluster_sizes.iloc[0]} papers")
        print(f"   Smallest cluster: {cluster_sizes.iloc[-1]} papers")
        
        return df, labels
        
    except ImportError as e:
        print(f"⚠️ Advanced clustering not available: {e}")
        print("   Using simple k-means clustering...")
        
        # Fallback to k-means
        from sklearn.cluster import KMeans
        
        n_clusters = min(20, len(embeddings) // 50)  # Adaptive number of clusters
        kmeans = KMeans(n_clusters=n_clusters, random_state=42)
        labels = kmeans.fit_predict(embeddings)
        
        df['cluster'] = labels
        print(f"   K-means clustering: {n_clusters} clusters")
        
        return df, labels


def step4_enrich_citations(df, sample_only=True):
    """Step 4: Enrich with OpenAlex citation data."""
    print("\n" + "="*60)
    print("STEP 4: ENRICHING WITH CITATION DATA")
    print("="*60)
    
    data_dir = Path('data')
    enriched_path = data_dir / 'papers_enriched.csv'
    
    if enriched_path.exists():
        print("📂 Loading existing enriched data...")
        enriched_df = pd.read_csv(enriched_path)
        print(f"✅ Loaded {len(enriched_df)} enriched papers")
        return enriched_df
    
    # Initialize OpenAlex client
    client = OpenAlexClient(
        cache_dir=str(data_dir / 'openalex_cache'),
        rate_limit=0.2,  # Be conservative
        timeout=30
    )
    
    if sample_only:
        print("🔬 Running on sample (first 50 papers with DOIs)...")
        sample_df = df[df['doi'].notna()].head(50).copy()
        enriched_df = enrich_dataframe(sample_df, client=client, max_workers=2)
        
        # Merge back with full dataset
        full_enriched = df.merge(
            enriched_df[['doi', 'openalex_id', 'cited_by_count', 'referenced_works']], 
            on='doi', 
            how='left'
        )
    else:
        print("🌐 Enriching full dataset...")
        print(f"   This will make ~{df['doi'].notna().sum()} API calls")
        print("   Estimated time: 5-10 minutes")
        
        full_enriched = enrich_dataframe(df, client=client, max_workers=3)
    
    # Save enriched data
    full_enriched.to_csv(enriched_path, index=False)
    
    enriched_count = full_enriched['openalex_id'].notna().sum()
    print(f"💾 Saved enriched dataset: {enriched_count} papers with citation data")
    
    return full_enriched


def step5_generate_reports(df):
    """Step 5: Generate research stream reports."""
    print("\n" + "="*60)
    print("STEP 5: GENERATING RESEARCH STREAM REPORTS")
    print("="*60)
    
    try:
        from src.reports import DialogCardGenerator, generate_summary_report
        
        print("📋 Generating dialog cards...")
        generator = DialogCardGenerator(df)
        
        # Generate cards for top clusters
        cluster_sizes = df['cluster'].value_counts()
        top_clusters = cluster_sizes.head(5).index  # Top 5 clusters
        
        cluster_cards = {}
        for cluster_id in top_clusters:
            print(f"   Generating card for cluster {cluster_id}...")
            card = generator.generate_cluster_card(cluster_id)
            cluster_cards[cluster_id] = card
            
            print(f"     Name: {card.get('name', 'Unknown')}")
            print(f"     Papers: {card.get('n_papers', 0)}")
        
        # Generate summary report
        summary = generate_summary_report(df, cluster_cards)
        
        # Save reports
        data_dir = Path('data')
        
        with open(data_dir / 'dialog_cards.json', 'w') as f:
            json.dump(cluster_cards, f, indent=2, default=str)
        
        with open(data_dir / 'summary_report.json', 'w') as f:
            json.dump(summary, f, indent=2, default=str)
        
        print(f"💾 Saved reports for {len(cluster_cards)} research streams")
        
        return cluster_cards, summary
        
    except Exception as e:
        print(f"⚠️ Report generation failed: {e}")
        return None, None


def main():
    """Run the complete analysis pipeline."""
    print("🚀 JOURNAL STREAMS ANALYSIS PIPELINE")
    print("="*60)
    print("This will run the complete research discovery pipeline.")
    print("Estimated time: 10-30 minutes depending on dataset size.")
    
    # Step 1: Parse BibTeX
    df = step1_parse_bibtex()
    if df is None:
        return
    
    # Step 2: Generate embeddings
    embeddings = step2_generate_embeddings(df)
    if embeddings is None:
        return
    
    # Step 3: Clustering
    df, labels = step3_clustering(df, embeddings)
    if df is None:
        return
    
    # Step 4: Citation enrichment (sample only for quick test)
    enriched_df = step4_enrich_citations(df, sample_only=True)
    
    # Step 5: Generate reports
    cards, summary = step5_generate_reports(enriched_df)
    
    # Final summary
    print("\n" + "🎉" + "="*58 + "🎉")
    print("ANALYSIS COMPLETE!")
    print("="*60)
    
    if summary:
        print(f"📊 Results Summary:")
        print(f"   Total papers analyzed: {summary['dataset_overview']['total_papers']}")
        print(f"   Research streams found: {summary['clustering_overview']['total_clusters']}")
        print(f"   Largest stream: {summary['clustering_overview']['largest_cluster_size']} papers")
        print(f"   Year range: {summary['dataset_overview']['year_range']['start']}-{summary['dataset_overview']['year_range']['end']}")
    
    print(f"\n📁 Output files saved in 'data/' directory:")
    print(f"   - papers_clustered.csv (clustered papers)")
    print(f"   - papers_enriched.csv (with citations)")
    print(f"   - dialog_cards.json (research stream summaries)")
    print(f"   - summary_report.json (overall analysis)")
    
    print(f"\n🔬 Next steps:")
    print(f"   - Review dialog_cards.json for research stream insights")
    print(f"   - Run with sample_only=False for full citation enrichment")
    print(f"   - Use Jupyter notebooks for detailed visualization")


if __name__ == "__main__":
    main()
