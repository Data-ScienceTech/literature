#!/usr/bin/env python3
"""
Quick analysis of enrichment results.
"""

import json
import pandas as pd

# Load both original and enriched corpora
print("Loading original CrossRef corpus...")
with open("data/clean/ais_basket_corpus.json", 'r', encoding='utf-8') as f:
    original_articles = json.load(f)

print("Loading enriched corpus...")
with open("data/clean/ais_basket_corpus_enriched.json", 'r', encoding='utf-8') as f:
    enriched_articles = json.load(f)

print(f"\nOriginal articles: {len(original_articles):,}")
print(f"Enriched articles: {len(enriched_articles):,}")

# Analyze abstract improvements
original_abstracts = sum(1 for a in original_articles if a.get("abstract") and len(a["abstract"].split()) >= 20)
enriched_abstracts = sum(1 for a in enriched_articles if a.get("abstract") and len(a["abstract"].split()) >= 20)

# Analyze keyword improvements  
original_keywords = sum(1 for a in original_articles if a.get("subject") and len(a["subject"]) > 0)
enriched_keywords = sum(1 for a in enriched_articles if a.get("subject") and len(a["subject"]) > 0)

# Count enrichment metadata
enriched_count = sum(1 for a in enriched_articles if "_enrichment" in a)
abstract_enrichments = sum(1 for a in enriched_articles if "_enrichment" in a and "abstract" in a["_enrichment"].get("enriched_fields", []))
keyword_enrichments = sum(1 for a in enriched_articles if "_enrichment" in a and "keywords" in a["_enrichment"].get("enriched_fields", []))
affiliation_enrichments = sum(1 for a in enriched_articles if "_enrichment" in a and "affiliations" in a["_enrichment"].get("enriched_fields", []))

print("\n" + "="*60)
print("ENRICHMENT ANALYSIS")
print("="*60)
print(f"Articles with enrichment data: {enriched_count:,} ({enriched_count/len(enriched_articles)*100:.1f}%)")
print(f"\nAbstracts (≥20 words):")
print(f"  Before: {original_abstracts:,} ({original_abstracts/len(original_articles)*100:.1f}%)")
print(f"  After:  {enriched_abstracts:,} ({enriched_abstracts/len(enriched_articles)*100:.1f}%)")
print(f"  Improvement: +{enriched_abstracts - original_abstracts:,}")
print(f"  Abstract enrichments applied: {abstract_enrichments:,}")

print(f"\nKeywords/subjects:")
print(f"  Before: {original_keywords:,} ({original_keywords/len(original_articles)*100:.1f}%)")
print(f"  After:  {enriched_keywords:,} ({enriched_keywords/len(enriched_articles)*100:.1f}%)")
print(f"  Improvement: +{enriched_keywords - original_keywords:,}")
print(f"  Keyword enrichments applied: {keyword_enrichments:,}")

print(f"\nAffiliation enrichments applied: {affiliation_enrichments:,}")

# Journal-specific analysis
print(f"\n{'Journal':<20} {'Original Abs':<12} {'Enriched Abs':<12} {'Improvement':<12}")
print("-" * 60)

journal_stats = {}
for article in original_articles:
    journal = article.get("journal_short", "Unknown")
    if journal not in journal_stats:
        journal_stats[journal] = {"original_abs": 0, "enriched_abs": 0, "total": 0}
    journal_stats[journal]["total"] += 1
    if article.get("abstract") and len(article["abstract"].split()) >= 20:
        journal_stats[journal]["original_abs"] += 1

for article in enriched_articles:
    journal = article.get("journal_short", "Unknown")
    if journal in journal_stats:
        if article.get("abstract") and len(article["abstract"].split()) >= 20:
            journal_stats[journal]["enriched_abs"] += 1

for journal, stats in sorted(journal_stats.items()):
    orig_pct = stats["original_abs"] / stats["total"] * 100 if stats["total"] > 0 else 0
    enrich_pct = stats["enriched_abs"] / stats["total"] * 100 if stats["total"] > 0 else 0
    improvement = enrich_pct - orig_pct
    print(f"{journal:<20} {orig_pct:>8.1f}%    {enrich_pct:>8.1f}%    {improvement:>+8.1f}%")

print("="*60)