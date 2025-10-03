"""
Install advanced packages for full-featured analysis.
"""

import subprocess
import sys
import os

def install_package(package):
    """Install a package with pip."""
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])
        print(f"✅ Successfully installed {package}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install {package}: {e}")
        return False

def main():
    """Install all advanced packages for the best analysis."""
    print("🔧 Installing Advanced Packages for Full Analysis")
    print("=" * 60)
    
    # Essential packages that might be missing
    essential_packages = [
        "umap-learn",
        "hdbscan", 
        "bertopic",
        "python-louvain"
    ]
    
    # Advanced packages (may require compilation)
    advanced_packages = [
        "python-igraph",
        "leidenalg"
    ]
    
    print("📦 Installing essential packages...")
    for package in essential_packages:
        install_package(package)
    
    print("\n🔬 Installing advanced clustering packages...")
    print("Note: These may take longer to compile...")
    
    for package in advanced_packages:
        print(f"\nInstalling {package}...")
        success = install_package(package)
        if not success:
            print(f"⚠️  {package} failed - trying alternative installation...")
            
            if package == "python-igraph":
                # Try conda if available
                try:
                    subprocess.check_call(["conda", "install", "-c", "conda-forge", "python-igraph", "-y"])
                    print(f"✅ Installed {package} via conda")
                except:
                    print(f"❌ Could not install {package} - will use NetworkX fallback")
            
            elif package == "leidenalg":
                try:
                    subprocess.check_call(["conda", "install", "-c", "conda-forge", "leidenalg", "-y"])
                    print(f"✅ Installed {package} via conda")
                except:
                    print(f"❌ Could not install {package} - will use Louvain fallback")
    
    print("\n🧪 Testing installations...")
    
    # Test imports
    test_results = {}
    
    packages_to_test = [
        ("umap", "umap"),
        ("hdbscan", "hdbscan"),
        ("bertopic", "bertopic"),
        ("igraph", "igraph"),
        ("leidenalg", "leidenalg"),
        ("community", "python-louvain")
    ]
    
    for module, package_name in packages_to_test:
        try:
            __import__(module)
            test_results[package_name] = "✅ Available"
        except ImportError:
            test_results[package_name] = "❌ Not available"
    
    print("\n📋 Installation Summary:")
    for package, status in test_results.items():
        print(f"   {package}: {status}")
    
    # Check sentence-transformers and torch
    print("\n🤖 Testing AI/ML packages...")
    try:
        import torch
        print(f"   PyTorch: ✅ Available (version {torch.__version__})")
        print(f"   CUDA available: {'✅ Yes' if torch.cuda.is_available() else '❌ No (CPU only)'}")
    except ImportError:
        print("   PyTorch: ❌ Not available")
    
    try:
        from sentence_transformers import SentenceTransformer
        print("   Sentence Transformers: ✅ Available")
    except ImportError:
        print("   Sentence Transformers: ❌ Not available")
    
    print(f"\n🎯 Ready for high-quality analysis!")
    print("Run: python run_full_analysis.py")

if __name__ == "__main__":
    main()
