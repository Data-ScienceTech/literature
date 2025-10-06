#!/usr/bin/env python3
"""
Test script for AIS Basket CrossRef Fetcher
Tests basic functionality and API connectivity
"""

import sys
import json
import requests
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

def test_crossref_api():
    """Test basic CrossRef API connectivity."""
    print("Testing CrossRef API connectivity...")
    
    url = "https://api.crossref.org/works"
    params = {
        "filter": "issn:0276-7783",  # MISQ
        "rows": 1
    }
    headers = {
        "User-Agent": "AIS-Basket-Test/1.0 (mailto:carlosdenner@gmail.com)"
    }
    
    try:
        response = requests.get(url, params=params, headers=headers, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        total = data.get("message", {}).get("total-results", 0)
        print(f"✓ CrossRef API is accessible")
        print(f"  Found {total:,} articles for MISQ")
        
        if total > 0:
            item = data["message"]["items"][0]
            print(f"  Sample article: {item.get('title', ['No title'])[0][:60]}...")
            return True
    except Exception as e:
        print(f"✗ CrossRef API test failed: {e}")
        return False

def test_dependencies():
    """Test required Python packages."""
    print("\nTesting required packages...")
    
    packages = {
        "requests": "HTTP requests",
        "pandas": "Data processing",
        "tqdm": "Progress bars",
        "pyarrow": "Parquet file support"
    }
    
    all_ok = True
    for package, description in packages.items():
        try:
            __import__(package)
            print(f"✓ {package:12s} - {description}")
        except ImportError:
            print(f"✗ {package:12s} - NOT INSTALLED")
            all_ok = False
    
    return all_ok

def test_directories():
    """Test that required directories can be created."""
    print("\nTesting directory structure...")
    
    dirs = [
        Path("data"),
        Path("data/raw/crossref_cache"),
        Path("data/clean"),
        Path("output")
    ]
    
    all_ok = True
    for directory in dirs:
        try:
            directory.mkdir(parents=True, exist_ok=True)
            print(f"✓ {str(directory):30s} - exists")
        except Exception as e:
            print(f"✗ {str(directory):30s} - ERROR: {e}")
            all_ok = False
    
    return all_ok

def test_journal_issns():
    """Test that all journal ISSNs are valid in CrossRef."""
    print("\nTesting journal ISSNs...")
    
    journals = {
        "MIS Quarterly": ["0276-7783", "2162-9730"],
        "Information Systems Research": ["1047-7047", "1526-5536"],
        "Journal of Management Information Systems": ["0742-1222", "1557-928X"],
        "Journal of the Association for Information Systems": ["1536-9323"],
        "European Journal of Information Systems": ["0960-085X", "1476-9344"],
        "Information Systems Journal": ["1350-1917", "1365-2575"],
        "Journal of Information Technology": ["0268-3962", "1466-4437"],
        "Journal of Strategic Information Systems": ["0963-8687", "1873-1198"]
    }
    
    url = "https://api.crossref.org/works"
    headers = {
        "User-Agent": "AIS-Basket-Test/1.0 (mailto:carlosdenner@gmail.com)"
    }
    
    all_ok = True
    total_articles = 0
    
    for journal, issns in journals.items():
        try:
            # Test first ISSN
            params = {
                "filter": f"issn:{issns[0]}",
                "rows": 1
            }
            response = requests.get(url, params=params, headers=headers, timeout=10)
            response.raise_for_status()
            data = response.json()
            count = data.get("message", {}).get("total-results", 0)
            total_articles += count
            
            if count > 0:
                print(f"✓ {journal:50s} - {count:,} articles")
            else:
                print(f"⚠ {journal:50s} - 0 articles (may need verification)")
                
        except Exception as e:
            print(f"✗ {journal:50s} - ERROR: {e}")
            all_ok = False
    
    print(f"\n  Total articles across all journals: {total_articles:,}")
    return all_ok

def main():
    """Run all tests."""
    print("="*60)
    print("AIS Basket CrossRef Fetcher - Test Suite")
    print("="*60)
    print()
    
    results = {
        "Dependencies": test_dependencies(),
        "Directories": test_directories(),
        "CrossRef API": test_crossref_api(),
        "Journal ISSNs": test_journal_issns()
    }
    
    print()
    print("="*60)
    print("Test Results Summary")
    print("="*60)
    
    all_passed = True
    for test_name, result in results.items():
        status = "✓ PASSED" if result else "✗ FAILED"
        print(f"{test_name:20s} - {status}")
        if not result:
            all_passed = False
    
    print("="*60)
    
    if all_passed:
        print("\n✓ All tests passed! Ready to fetch articles.")
        print("\nNext steps:")
        print("  1. Run: .\\fetch_corpus\\run_ais_basket_fetch.ps1")
        print("  2. Or:  python fetch_corpus/fetch_ais_basket_crossref.py")
        return 0
    else:
        print("\n✗ Some tests failed. Please fix issues before running the fetcher.")
        print("\nCommon fixes:")
        print("  - Install missing packages: pip install requests pandas tqdm pyarrow")
        print("  - Check network connectivity")
        print("  - Verify CrossRef API is accessible")
        return 1

if __name__ == "__main__":
    sys.exit(main())
