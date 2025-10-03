"""
Test script to verify installation and run a quick analysis.
"""

import sys
import os
from pathlib import Path

# Add src to Python path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

def test_imports():
    """Test that all required packages can be imported."""
    print("Testing imports...")
    
    try:
        import pandas as pd
        import numpy as np
        import matplotlib.pyplot as plt
        import seaborn as sns
        print("✓ Core data science libraries")
    except ImportError as e:
        print(f"✗ Core libraries failed: {e}")
        return False
    
    try:
        from src.parse_bib import load_bib, get_corpus_stats
        print("✓ BibTeX parsing module")
    except ImportError as e:
        print(f"✗ BibTeX parsing failed: {e}")
        return False
    
    try:
        from sentence_transformers import SentenceTransformer
        print("✓ Sentence transformers")
    except ImportError as e:
        print(f"✗ Sentence transformers failed: {e}")
        return False
    
    try:
        import networkx as nx
        print("✓ NetworkX")
    except ImportError as e:
        print(f"✗ NetworkX failed: {e}")
        return False
    
    # Optional imports (clustering)
    try:
        import igraph as ig
        import leidenalg
        print("✓ Leiden clustering (igraph + leidenalg)")
    except ImportError as e:
        print(f"⚠ Leiden clustering not available: {e}")
    
    try:
        import hdbscan
        print("✓ HDBSCAN clustering")
    except ImportError as e:
        print(f"⚠ HDBSCAN not available: {e}")
    
    try:
        import umap
        print("✓ UMAP dimensionality reduction")
    except ImportError as e:
        print(f"⚠ UMAP not available: {e}")
    
    return True


def quick_analysis():
    """Run a quick analysis on the BibTeX file."""
    print("\n" + "="*50)
    print("Running Quick Analysis")
    print("="*50)
    
    # Check if BibTeX file exists
    bib_file = Path("refs_2016_2025_AMR_MISQ_ORSC_ISR.bib")
    if not bib_file.exists():
        print(f"✗ BibTeX file not found: {bib_file}")
        print("Please ensure the BibTeX file is in the current directory")
        return False
    
    print(f"✓ Found BibTeX file: {bib_file}")
    
    try:
        # Load and parse BibTeX
        from src.parse_bib import load_bib, get_corpus_stats
        
        print("Loading BibTeX file...")
        df = load_bib(str(bib_file))
        
        print(f"✓ Loaded {len(df)} papers")
        
        # Get statistics
        stats = get_corpus_stats(df)
        
        print("\n--- Dataset Statistics ---")
        print(f"Total papers: {stats['total_papers']}")
        print(f"Papers with DOI: {stats['papers_with_doi']}")
        print(f"Papers with abstract: {stats['papers_with_abstract']}")
        print(f"Year range: {stats['year_min']} - {stats['year_max']}")
        print(f"Unique journals: {stats['unique_journals']}")
        
        # Show top journals
        print(f"\n--- Top Journals ---")
        for journal, count in list(stats['journals'].items())[:5]:
            print(f"{journal}: {count} papers")
        
        # Test embeddings (small sample)
        print(f"\n--- Testing Embeddings ---")
        try:
            from src.embeddings import embed_texts
            
            # Test with just 3 papers
            sample_texts = df['text'].dropna().head(3).tolist()
            print(f"Testing embeddings on {len(sample_texts)} papers...")
            
            embeddings = embed_texts(sample_texts, batch_size=2, show_progress=True)
            print(f"✓ Generated embeddings: {embeddings.shape}")
            print(f"Embedding norms: {np.linalg.norm(embeddings, axis=1)}")
            
        except Exception as e:
            print(f"⚠ Embedding test failed: {e}")
        
        # Test clustering (if available)
        print(f"\n--- Testing Clustering ---")
        try:
            from src.clustering import knn_graph, leiden_cluster
            
            # Create small k-NN graph
            if 'embeddings' in locals():
                print("Building k-NN graph...")
                g = knn_graph(embeddings, k=2, metric='cosine')
                print(f"✓ Created graph: {g.vcount()} nodes, {g.ecount()} edges")
                
                # Test clustering
                labels = leiden_cluster(g, resolution=1.0)
                print(f"✓ Leiden clustering: {len(set(labels))} clusters")
            
        except Exception as e:
            print(f"⚠ Clustering test failed: {e}")
        
        print(f"\n✓ Quick analysis completed successfully!")
        return True
        
    except Exception as e:
        print(f"✗ Analysis failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Main test function."""
    print("Journal Streams Analysis - Setup Test")
    print("="*50)
    
    # Test imports
    if not test_imports():
        print("\n❌ Import tests failed. Please install missing packages:")
        print("pip install -r requirements.txt")
        return
    
    print("\n✅ All imports successful!")
    
    # Run quick analysis
    if quick_analysis():
        print("\n🎉 Setup test completed successfully!")
        print("\nNext steps:")
        print("1. Run: jupyter lab")
        print("2. Open and execute notebooks in order: 01, 02, 03...")
    else:
        print("\n❌ Quick analysis failed. Check error messages above.")


if __name__ == "__main__":
    main()
