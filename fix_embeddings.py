"""
Fix embedding generation issues and test different approaches.
"""

import sys
import pandas as pd
import numpy as np
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

def test_sentence_transformers():
    """Test sentence transformers with different models."""
    print("🧪 Testing Sentence Transformers...")
    
    try:
        from sentence_transformers import SentenceTransformer
        print("✅ Sentence Transformers imported successfully")
        
        # Test with simple model first
        print("📥 Loading simple model...")
        model = SentenceTransformer('all-MiniLM-L6-v2')
        print("✅ Model loaded successfully")
        
        # Test embedding generation
        test_texts = [
            "This is a test sentence about machine learning.",
            "Another sentence about organizational behavior.",
            "A third sentence about information systems research."
        ]
        
        print("🔄 Testing embedding generation...")
        embeddings = model.encode(test_texts, show_progress_bar=True)
        print(f"✅ Generated embeddings: {embeddings.shape}")
        print(f"📊 Embedding norms: {np.linalg.norm(embeddings, axis=1)}")
        
        return True, model
        
    except Exception as e:
        print(f"❌ Sentence Transformers test failed: {e}")
        import traceback
        traceback.print_exc()
        return False, None

def test_specter2():
    """Test SPECTER2 model specifically."""
    print("\n🔬 Testing SPECTER2 model...")
    
    try:
        from sentence_transformers import SentenceTransformer
        
        print("📥 Loading SPECTER2 model...")
        model = SentenceTransformer('allenai/specter2')
        print("✅ SPECTER2 loaded successfully")
        
        # Test with scientific text
        test_texts = [
            "We investigate the impact of artificial intelligence on organizational performance through a comprehensive analysis of 500 firms.",
            "This study examines the role of social networks in knowledge transfer within multinational corporations using network analysis."
        ]
        
        print("🔄 Testing SPECTER2 embedding generation...")
        embeddings = model.encode(test_texts, show_progress_bar=True, batch_size=1)
        print(f"✅ SPECTER2 embeddings: {embeddings.shape}")
        
        return True, model
        
    except Exception as e:
        print(f"❌ SPECTER2 test failed: {e}")
        print("This might be due to model download issues or memory constraints")
        return False, None

def generate_embeddings_robust():
    """Generate embeddings with robust error handling."""
    print("\n🚀 Robust Embedding Generation")
    print("=" * 50)
    
    # Load data
    try:
        df = pd.read_csv('data/parsed_papers_analysis.csv')
        print(f"📊 Loaded {len(df)} papers for analysis")
    except FileNotFoundError:
        print("❌ Analysis dataset not found. Run parsing first.")
        return None
    
    # Test different models in order of preference
    models_to_try = [
        ('allenai/specter2', 'SPECTER2 (Best for scientific papers)'),
        ('sentence-transformers/allenai-specter', 'SPECTER v1'),
        ('sentence-transformers/all-mpnet-base-v2', 'All-MPNet (High quality)'),
        ('sentence-transformers/all-MiniLM-L6-v2', 'MiniLM (Fast and reliable)')
    ]
    
    embeddings = None
    model_used = None
    
    for model_name, description in models_to_try:
        print(f"\n🔄 Trying {description}...")
        
        try:
            from sentence_transformers import SentenceTransformer
            
            model = SentenceTransformer(model_name)
            print(f"✅ Loaded {model_name}")
            
            # Get texts
            texts = df['text'].fillna('').tolist()
            print(f"📝 Processing {len(texts)} texts...")
            
            # Generate embeddings with conservative settings
            embeddings = model.encode(
                texts,
                batch_size=4,  # Very conservative
                show_progress_bar=True,
                convert_to_numpy=True,
                normalize_embeddings=True
            )
            
            print(f"✅ Successfully generated embeddings: {embeddings.shape}")
            model_used = model_name
            break
            
        except Exception as e:
            print(f"❌ Failed with {model_name}: {e}")
            continue
    
    if embeddings is None:
        print("❌ All embedding models failed!")
        return None
    
    # Save embeddings
    data_dir = Path('data')
    data_dir.mkdir(exist_ok=True)
    
    # Save with model name in filename
    model_safe_name = model_used.replace('/', '_').replace('-', '_')
    embeddings_path = data_dir / f'embeddings_{model_safe_name}.npy'
    
    np.save(embeddings_path, embeddings)
    print(f"💾 Saved embeddings to {embeddings_path}")
    
    # Save metadata
    metadata = {
        'model_used': model_used,
        'shape': embeddings.shape,
        'normalized': True,
        'mean_norm': float(np.linalg.norm(embeddings, axis=1).mean()),
        'std_norm': float(np.linalg.norm(embeddings, axis=1).std())
    }
    
    import json
    with open(data_dir / 'embeddings_metadata.json', 'w') as f:
        json.dump(metadata, f, indent=2)
    
    print(f"📊 Embedding quality metrics:")
    print(f"   Model: {model_used}")
    print(f"   Shape: {embeddings.shape}")
    print(f"   Mean norm: {metadata['mean_norm']:.3f}")
    print(f"   Std norm: {metadata['std_norm']:.3f}")
    
    return embeddings, model_used

def main():
    """Main function to fix embedding issues."""
    print("🔧 EMBEDDING GENERATION TROUBLESHOOTER")
    print("=" * 50)
    
    # Test basic functionality
    success, model = test_sentence_transformers()
    if not success:
        print("❌ Basic sentence transformers not working")
        return
    
    # Test SPECTER2 specifically
    specter_success, specter_model = test_specter2()
    
    # Generate embeddings with robust approach
    result = generate_embeddings_robust()
    
    if result:
        embeddings, model_used = result
        print(f"\n🎉 SUCCESS!")
        print(f"Generated {embeddings.shape[0]} embeddings using {model_used}")
        print(f"Ready to proceed with clustering and analysis!")
    else:
        print(f"\n❌ FAILED to generate embeddings")
        print("Please check your internet connection and try again")

if __name__ == "__main__":
    main()
