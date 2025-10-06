import subprocess
import sys
from pathlib import Path

def check_dependencies():
    required = ["dash", "plotly", "pandas", "numpy"]
    missing = []
    for package in required:
        try:
            __import__(package)
        except ImportError:
            missing.append(package)
    return missing

def main():
    print("="*80)
    print("Research Stream Explorer - Dashboard Launcher")
    print("="*80)
    
    required_files = [
        "data/papers_hierarchical_clustered.csv",
        "data/hierarchy_leiden.json",
        "data/clean/ais_basket_corpus_enriched.json"
    ]
    
    missing_files = [f for f in required_files if not Path(f).exists()]
    
    if missing_files:
        print("\nERROR: Missing required data files:")
        for f in missing_files:
            print(f"   - {f}")
        print("\nPlease run: python run_hierarchical_analysis.py")
        return
    
    print("\nChecking dependencies...")
    missing = check_dependencies()
    
    if missing:
        print(f"\nMissing packages: {', '.join(missing)}")
        response = input("\nInstall missing packages? (y/n): ")
        
        if response.lower() == "y":
            try:
                subprocess.check_call([sys.executable, "-m", "pip", "install"] + missing)
                print("\nDependencies installed successfully!")
            except Exception as e:
                print(f"\nError: {e}")
                print("\nTry: pip install -r requirements_dashboard.txt")
                return
        else:
            print("\nCannot start dashboard without required packages")
            return
    
    print("\nAll dependencies ready!")
    print("\nStarting dashboard server...")
    print("="*80)
    
    try:
        subprocess.run([sys.executable, "dashboard_app.py"])
    except KeyboardInterrupt:
        print("\n\nDashboard stopped by user")
    except Exception as e:
        print(f"\nError running dashboard: {e}")

if __name__ == "__main__":
    main()
