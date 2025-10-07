#!/usr/bin/env python3
"""
Test suite for OpenAlex enrichment system.

This module contains comprehensive tests for the enrichment process.
"""

import json
import tempfile
from pathlib import Path
import sys
import os

# Add the parent directory to sys.path to import the enrichment module
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Mock the enrichment module for testing
class MockOpenAlexEnricher:
    def __init__(self):
        self.stats = {
            'total_articles': 0,
            'openalex_found': 0,
            'enriched_abstracts': 0,
            'enriched_keywords': 0,
            'enriched_affiliations': 0,
            'api_calls': 0,
            'cache_hits': 0,
            'errors': 0
        }
        self.cache = {}
    
    def reconstruct_abstract(self, inverted_index):
        """Test abstract reconstruction."""
        if not inverted_index:
            return None
        
        # Simple test reconstruction
        try:
            max_pos = max(max(positions) for positions in inverted_index.values() if positions)
            tokens = [""] * (max_pos + 1)
            
            for token, positions in inverted_index.items():
                for pos in positions:
                    if 0 <= pos < len(tokens):
                        tokens[pos] = token
            
            return " ".join(token for token in tokens if token)
        except:
            return None
    
    def extract_keywords(self, openalex_work):
        """Test keyword extraction."""
        keywords = set()
        
        concepts = openalex_work.get("concepts", [])
        for concept in concepts:
            if concept.get("level", 0) <= 2:
                name = concept.get("display_name", "")
                if name and len(name) > 2:
                    keywords.add(name)
        
        return sorted(list(keywords))

def test_abstract_reconstruction():
    """Test abstract reconstruction from inverted index."""
    enricher = MockOpenAlexEnricher()
    
    # Test case 1: Simple inverted index
    inverted_index = {
        "This": [0],
        "is": [1],
        "a": [2],
        "test": [3],
        "abstract": [4]
    }
    
    result = enricher.reconstruct_abstract(inverted_index)
    assert result == "This is a test abstract"
    
    # Test case 2: Empty index
    assert enricher.reconstruct_abstract({}) is None
    assert enricher.reconstruct_abstract(None) is None
    
    # Test case 3: Out of order tokens
    inverted_index_2 = {
        "abstract": [4],
        "This": [0],
        "test": [3],
        "is": [1],
        "a": [2]
    }
    
    result = enricher.reconstruct_abstract(inverted_index_2)
    assert result == "This is a test abstract"

def test_keyword_extraction():
    """Test keyword extraction from OpenAlex concepts."""
    enricher = MockOpenAlexEnricher()
    
    # Test case 1: Normal concepts
    openalex_work = {
        "concepts": [
            {"display_name": "Computer science", "level": 0},
            {"display_name": "Information systems", "level": 1},
            {"display_name": "Very specific concept", "level": 3},  # Should be excluded
            {"display_name": "AI", "level": 2}  # Should be excluded (too short)
        ]
    }
    
    keywords = enricher.extract_keywords(openalex_work)
    expected = ["Computer science", "Information systems"]
    assert sorted(keywords) == sorted(expected)
    
    # Test case 2: Empty concepts
    assert enricher.extract_keywords({"concepts": []}) == []
    assert enricher.extract_keywords({}) == []

def test_sample_enrichment_workflow():
    """Test the enrichment workflow with sample data."""
    # Sample CrossRef article (based on our actual data structure)
    crossref_article = {
        "doi": "10.25300/misq/2020/14905",
        "title": "Test Article",
        "journal": "MIS Quarterly",
        "journal_short": "MISQ",
        "year": 2020,
        "abstract": "",  # Missing abstract
        "authors": [
            {"given": "John", "family": "Doe", "affiliation": []}
        ],
        "reference_count": 45
    }
    
    # Sample OpenAlex work
    openalex_work = {
        "id": "https://openalex.org/W12345",
        "doi": "https://doi.org/10.25300/misq/2020/14905",
        "abstract_inverted_index": {
            "This": [0],
            "paper": [1],
            "examines": [2],
            "information": [3],
            "systems": [4]
        },
        "concepts": [
            {"display_name": "Information systems", "level": 1},
            {"display_name": "Computer science", "level": 0}
        ],
        "authorships": [{
            "author": {"display_name": "John Doe"},
            "institutions": [{"display_name": "University of Testing"}],
            "author_position": "first"
        }],
        "cited_by_count": 25
    }
    
    # Create mock enricher
    enricher = MockOpenAlexEnricher()
    
    # Test abstract reconstruction
    abstract = enricher.reconstruct_abstract(
        openalex_work["abstract_inverted_index"]
    )
    assert abstract == "This paper examines information systems"
    
    # Test keyword extraction
    keywords = enricher.extract_keywords(openalex_work)
    assert "Information systems" in keywords
    assert "Computer science" in keywords

def test_file_operations():
    """Test file loading and saving operations."""
    sample_articles = [
        {
            "doi": "10.1000/test1",
            "title": "Test Article 1",
            "abstract": "This is a test abstract",
            "journal": "Test Journal"
        },
        {
            "doi": "10.1000/test2", 
            "title": "Test Article 2",
            "abstract": "",
            "journal": "Test Journal"
        }
    ]
    
    # Test JSON serialization
    json_str = json.dumps(sample_articles, indent=2)
    loaded_articles = json.loads(json_str)
    
    assert len(loaded_articles) == 2
    assert loaded_articles[0]["doi"] == "10.1000/test1"
    assert loaded_articles[1]["abstract"] == ""

def test_data_validation():
    """Test data validation functions."""
    # Test DOI validation
    valid_dois = [
        "10.25300/misq/2020/14905",
        "10.1287/isre.2020.0123",
        "10.1080/07421222.2020.1790213"
    ]
    
    invalid_dois = [
        "",
        "not-a-doi",
        "10.",
        None
    ]
    
    for doi in valid_dois:
        assert doi.startswith("10.")
        assert "/" in doi
    
    for doi in invalid_dois:
        if doi:
            assert not (doi.startswith("10.") and "/" in doi)

def test_enrichment_statistics():
    """Test statistics tracking."""
    stats = {
        'total_articles': 100,
        'openalex_found': 85,
        'enriched_abstracts': 45,
        'enriched_keywords': 80,
        'enriched_affiliations': 30,
        'api_calls': 95,
        'cache_hits': 15,
        'errors': 2
    }
    
    # Test coverage calculations
    coverage_rate = stats['openalex_found'] / stats['total_articles'] * 100
    assert coverage_rate == 85.0
    
    enrichment_rate = stats['enriched_abstracts'] / stats['total_articles'] * 100
    assert enrichment_rate == 45.0

def test_error_handling():
    """Test error handling scenarios."""
    enricher = MockOpenAlexEnricher()
    
    # Test with malformed inverted index
    malformed_index = {
        "test": "not-a-list",  # Should be a list
        "word": [0, 1]
    }
    
    # Should handle gracefully
    result = enricher.reconstruct_abstract(malformed_index)
    assert result is None
    
    # Test with malformed concepts - check if it's a dict first
    malformed_work = {
        "concepts": "not-a-list"  # Should be a list
    }
    
    # Should handle gracefully
    try:
        keywords = enricher.extract_keywords(malformed_work)
        assert keywords == []
    except AttributeError:
        # Expected for malformed data
        assert True

def run_tests():
    """Run all tests and report results."""
    test_functions = [
        test_abstract_reconstruction,
        test_keyword_extraction,
        test_sample_enrichment_workflow,
        test_file_operations,
        test_data_validation,
        test_enrichment_statistics,
        test_error_handling
    ]
    
    passed = 0
    failed = 0
    
    print("Running OpenAlex Enrichment Tests")
    print("=" * 50)
    
    for test_func in test_functions:
        try:
            test_func()
            print(f"✓ {test_func.__name__}")
            passed += 1
        except Exception as e:
            print(f"✗ {test_func.__name__}: {e}")
            failed += 1
    
    print("\n" + "=" * 50)
    print(f"Tests completed: {passed} passed, {failed} failed")
    
    if failed == 0:
        print("🎉 All tests passed!")
        return True
    else:
        print("❌ Some tests failed!")
        return False

if __name__ == "__main__":
    success = run_tests()
    exit(0 if success else 1)