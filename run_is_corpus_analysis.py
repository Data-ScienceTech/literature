"""
Complete analysis of the IS corpus (OpenAlex data).
Runs embedding, clustering, and report generation on the 23K+ IS papers.
"""

import sys
import os
import json
import time
from pathlib import Path
import pandas as pd
import numpy as np

# Add src to Python path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

def prepare_is_corpus():
    """Load and prepare the IS corpus for analysis."""
    print("📚 LOADING IS CORPUS (HIGH-QUALITY FOCUSED)")
    print("=" * 60)
    
    # Load the RECOMMENDED corpus (high-quality journals, 2000+, 100% abstracts)
    corpus = pd.read_parquet('data/clean/is_corpus_recommended.parquet')
    
    print(f"✅ Loaded {len(corpus):,} papers from 6 premier IS journals")
    print(f"   Journals: ISR, MISQ, JAIS, ISJ, JMIS, JIT")
    print(f"   Date range: {corpus['year'].min()} - {corpus['year'].max()}")
    print(f"   With abstracts: {corpus['abstract'].notna().sum():,} (100% by design)")
    
    # All papers already have abstracts, no filtering needed
    df = corpus.copy()
    
    # Filter to recent papers (e.g., 2000+) for manageable size
    df = df[df['year'] >= 2000].copy()
    
    print(f"\n🔍 Filtered to {len(df):,} papers (2000+, with abstracts)")
    
    # Prepare the dataframe in expected format
    df = df.rename(columns={
        'openalex_id': 'id',
        'title': 'Title',
        'year': 'Year',
        'journal': 'Journal',
        'abstract': 'Abstract',
        'cited_by_count': 'Citations'
    })
    
    # Create Author field from authors list
    def format_authors(authors_list):
        if not isinstance(authors_list, list) or not authors_list:
            return ''
        return '; '.join([a.get('author', '') for a in authors_list if a.get('author')])
    
    df['Author'] = df['authors'].apply(format_authors)
    
    # Save for analysis
    df.to_csv('data/parsed_papers_is_corpus.csv', index=False)
    print(f"💾 Saved to data/parsed_papers_is_corpus.csv")
    
    return df


def generate_embeddings(df):
    """Generate SPECTER2 embeddings for the corpus."""
    print("\n🧠 GENERATING EMBEDDINGS")
    print("=" * 60)
    
    try:
        from src.embeddings import embed_texts
        
        # Combine title and abstract for better embeddings
        texts = []
        for _, row in df.iterrows():
            title = str(row.get('Title', ''))
            abstract = str(row.get('Abstract', ''))
            texts.append(f"{title}. {abstract}")
        
        print(f"📄 Processing {len(texts):,} documents...")
        print("Using all-MiniLM-L6-v2 model (fast, reliable)")
        
        embeddings = embed_texts(
            texts,
            model_name="all-MiniLM-L6-v2",  # Fast and reliable alternative
            batch_size=64,
            show_progress=True
        )
        
        # Save embeddings
        embeddings_path = 'data/embeddings_is_corpus.npy'
        np.save(embeddings_path, embeddings)
        
        print(f"✅ Generated {embeddings.shape} embeddings")
        print(f"💾 Saved to {embeddings_path}")
        
        # Save metadata
        metadata = {
            'n_papers': len(df),
            'embedding_dim': embeddings.shape[1],
            'model': 'specter2',
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
            'corpus': 'IS Premier Journals (OpenAlex)'
        }
        
        with open('data/embeddings_metadata_is.json', 'w') as f:
            json.dump(metadata, f, indent=2)
        
        return embeddings
        
    except Exception as e:
        print(f"❌ Embedding generation failed: {e}")
        import traceback
        traceback.print_exc()
        return None


def run_clustering_analysis(df, embeddings):
    """Run clustering analysis with the generated embeddings."""
    print("\n🎯 RESEARCH STREAM CLUSTERING")
    print("=" * 60)
    
    print(f"📊 Analyzing {len(df):,} papers with {embeddings.shape[1]}-dim embeddings")
    
    # Try Leiden clustering first
    try:
        from src.clustering import knn_graph, leiden_cluster, evaluate_clustering
        
        print("🕸️  Building k-NN graph for Leiden clustering...")
        k = min(15, len(embeddings) // 20)
        g = knn_graph(embeddings, k=k, metric='cosine')
        print(f"   Graph: {g.vcount():,} nodes, {g.ecount():,} edges")
        
        print("🎯 Running Leiden clustering...")
        best_labels = None
        best_score = -1
        best_resolution = None
        
        for resolution in [0.5, 1.0, 1.5, 2.0]:
            labels = leiden_cluster(g, resolution=resolution, seed=42)
            metrics = evaluate_clustering(embeddings, labels, metric='cosine')
            
            n_clusters = len(set(labels))
            silhouette = metrics.get('silhouette', 0)
            
            if silhouette is not None and 5 <= n_clusters <= 80:
                score = silhouette - abs(n_clusters - 30) * 0.01
                print(f"   Resolution {resolution}: {n_clusters} clusters, silhouette={silhouette:.3f}")
                
                if score > best_score:
                    best_score = score
                    best_labels = labels
                    best_resolution = resolution
        
        if best_labels is not None:
            print(f"✅ Best Leiden clustering: resolution={best_resolution}, {len(set(best_labels))} clusters")
            method = "leiden"
        else:
            raise Exception("No good Leiden clustering found")
            
    except Exception as e:
        print(f"⚠️  Leiden failed: {e}")
        print("🔄 Falling back to HDBSCAN...")
        
        try:
            from src.clustering import hdbscan_cluster, evaluate_clustering
            
            best_labels = hdbscan_cluster(
                embeddings,
                min_cluster_size=max(20, len(embeddings) // 100),
                min_samples=5,
                metric='cosine'
            )
            
            metrics = evaluate_clustering(embeddings, best_labels, metric='cosine')
            print(f"✅ HDBSCAN: {metrics['n_clusters']} clusters, {metrics['n_noise']} noise points")
            method = "hdbscan"
            
        except Exception as e2:
            print(f"⚠️  HDBSCAN failed: {e2}")
            print("🔄 Using K-means fallback...")
            
            from sklearn.cluster import KMeans
            from sklearn.metrics import silhouette_score
            
            # Find optimal K
            best_k = 30
            best_silhouette = -1
            
            for k in range(15, min(61, len(embeddings) // 30)):
                kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
                labels = kmeans.fit_predict(embeddings)
                
                silhouette = silhouette_score(embeddings, labels, metric='cosine', sample_size=min(1000, len(embeddings)))
                
                if silhouette > best_silhouette:
                    best_silhouette = silhouette
                    best_k = k
                    best_labels = labels
            
            print(f"✅ K-means: {best_k} clusters, silhouette={best_silhouette:.3f}")
            method = "kmeans"
    
    # Add clusters to dataframe
    df['cluster'] = best_labels
    df['clustering_method'] = method
    
    # Analyze clusters
    cluster_sizes = pd.Series(best_labels).value_counts().sort_values(ascending=False)
    
    print(f"\n📊 CLUSTER ANALYSIS:")
    print(f"   Method used: {method}")
    print(f"   Total clusters: {len(cluster_sizes)}")
    print(f"   Largest cluster: {cluster_sizes.iloc[0]} papers")
    print(f"   Smallest cluster: {cluster_sizes.iloc[-1]} papers")
    print(f"   Mean cluster size: {cluster_sizes.mean():.1f} papers")
    
    # Save results
    df.to_csv('data/papers_clustered_is_corpus.csv', index=False)
    print(f"💾 Saved clustered dataset to data/papers_clustered_is_corpus.csv")
    
    return df, best_labels


def generate_research_reports(df):
    """Generate comprehensive research stream reports."""
    print("\n📋 GENERATING RESEARCH STREAM REPORTS")
    print("=" * 60)
    
    try:
        from src.reports import DialogCardGenerator, generate_summary_report
        from src.bursts import compute_cluster_prevalence, detect_prevalence_bursts
        
        # Initialize generator
        generator = DialogCardGenerator(df)
        
        # Compute temporal dynamics
        print("🔥 Analyzing temporal bursts...")
        prevalence = compute_cluster_prevalence(df)
        bursts = detect_prevalence_bursts(prevalence, z_threshold=1.5)
        
        # Generate dialog cards for significant clusters
        cluster_sizes = df['cluster'].value_counts()
        significant_clusters = cluster_sizes[cluster_sizes >= 15].index
        
        print(f"📋 Generating dialog cards for {len(significant_clusters)} research streams...")
        
        cluster_cards = {}
        for i, cluster_id in enumerate(significant_clusters[:20]):  # Top 20 clusters
            print(f"   Processing cluster {cluster_id} ({i+1}/{min(20, len(significant_clusters))})...")
            
            card = generator.generate_cluster_card(
                cluster_id,
                prevalence_bursts=bursts
            )
            
            cluster_cards[cluster_id] = card
            
            print(f"     📛 {card.get('name', 'Unknown')}")
            print(f"     📄 {card.get('n_papers', 0)} papers")
            
            # Show key papers
            key_papers = card.get('key_papers', {})
            if key_papers.get('most_cited'):
                top_paper = key_papers['most_cited'][0]
                print(f"     🏆 Top paper: {top_paper.get('title', 'N/A')[:50]}...")
        
        # Generate summary report
        print("\n📊 Generating summary report...")
        summary = generate_summary_report(df, cluster_cards)
        
        # Save results
        with open('data/dialog_cards_is_corpus.json', 'w', encoding='utf-8') as f:
            json.dump(cluster_cards, f, indent=2, default=str, ensure_ascii=False)
        
        with open('data/summary_report_is_corpus.json', 'w', encoding='utf-8') as f:
            json.dump(summary, f, indent=2, default=str, ensure_ascii=False)
        
        print(f"💾 Saved comprehensive reports:")
        print(f"   📋 {len(cluster_cards)} research stream dialog cards")
        print(f"   📊 Complete summary report")
        
        return cluster_cards, summary
        
    except Exception as e:
        print(f"❌ Report generation failed: {e}")
        import traceback
        traceback.print_exc()
        return None, None


def display_results(df, cluster_cards, summary):
    """Display key results."""
    print("\n" + "🎉" + "=" * 58 + "🎉")
    print("IS CORPUS RESEARCH STREAM ANALYSIS COMPLETE!")
    print("=" * 60)
    
    if summary:
        print(f"📊 ANALYSIS RESULTS:")
        print(f"   📄 Papers analyzed: {summary['dataset_overview']['total_papers']:,}")
        print(f"   🔬 Research streams found: {summary['clustering_overview']['total_clusters']}")
        print(f"   🏆 Largest stream: {summary['clustering_overview']['largest_cluster_size']} papers")
        print(f"   📅 Time span: {summary['dataset_overview']['year_range']['start']}-{summary['dataset_overview']['year_range']['end']}")
    
    print(f"\n🔬 TOP RESEARCH STREAMS:")
    if cluster_cards:
        for i, (cluster_id, card) in enumerate(list(cluster_cards.items())[:5]):
            print(f"   {i+1}. {card.get('name', f'Stream {cluster_id}')} ({card.get('n_papers', 0)} papers)")
            
            # Show temporal span
            year_range = card.get('year_range', {})
            if year_range:
                print(f"      📅 {year_range.get('start', 'N/A')}-{year_range.get('end', 'N/A')}")
            
            # Show top journal
            journals = card.get('journals', {})
            if journals:
                top_journal = list(journals.keys())[0]
                print(f"      📚 Primary journal: {top_journal}")
    
    print(f"\n📁 OUTPUT FILES:")
    print(f"   📊 papers_clustered_is_corpus.csv - Final clustered dataset")
    print(f"   📋 dialog_cards_is_corpus.json - Research stream summaries")
    print(f"   📈 summary_report_is_corpus.json - Overall analysis")
    print(f"   🧠 embeddings_is_corpus.npy - Semantic embeddings")
    
    print(f"\n🎯 NEXT STEPS:")
    print(f"   📖 Review dialog_cards_is_corpus.json for detailed insights")
    print(f"   📊 Generate dashboard with generate_dashboard.py")
    print(f"   🌐 Create visualizations with the notebooks")
    print(f"   📈 Analyze trends over time")


def main():
    """Run the complete IS corpus analysis pipeline."""
    print("🚀 IS CORPUS - COMPLETE RESEARCH STREAM ANALYSIS")
    print("=" * 60)
    print("Analyzing 23K+ papers from 11 premier IS journals")
    print("Source: OpenAlex (AIS Senior Scholars' list)")
    print()
    
    start_time = time.time()
    
    # Step 1: Prepare corpus
    df = prepare_is_corpus()
    if df is None or len(df) == 0:
        print("❌ Failed to load corpus")
        return
    
    # Step 2: Generate embeddings
    embeddings = generate_embeddings(df)
    if embeddings is None:
        print("❌ Failed to generate embeddings")
        return
    
    # Step 3: Clustering analysis
    df, labels = run_clustering_analysis(df, embeddings)
    if df is None:
        print("❌ Clustering failed")
        return
    
    # Step 4: Generate reports
    cluster_cards, summary = generate_research_reports(df)
    
    # Step 5: Display results
    total_time = time.time() - start_time
    print(f"\n⏱️  Analysis completed in {total_time/60:.1f} minutes")
    
    display_results(df, cluster_cards, summary)


if __name__ == "__main__":
    main()
