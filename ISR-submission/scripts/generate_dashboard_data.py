"""
Generate Interactive Dashboard Data

Transforms clustering results and enriched corpus into dashboard-compatible JSON
for the Interactive Literature Explorer web application.

Usage:
    python generate_dashboard_data.py --corpus ../data/ais_basket_corpus_enriched.parquet \
                                       --clusters ../data/doc_assignments.csv \
                                       --output ../dashboard-data.js

Output:
    JavaScript file containing complete dataset for web dashboard
    - 8 L1 streams with metadata
    - 48 L2 subtopics with paper assignments
    - Full paper metadata (title, authors, year, journal, citations, keywords)
    - Optimized for ~2.5 MB file size

Author: Carlos Denner dos Santos
Date: October 2025
"""

import pandas as pd
import json
import argparse
from pathlib import Path
from datetime import datetime
from collections import defaultdict
import numpy as np


# Stream labels (from manuscript Table 1)
L1_LABELS = {
    0: "Digital Transformation & Innovation",
    1: "Systems Development & Decision Support",
    2: "Enterprise Systems & Alignment",
    3: "IT Governance & Strategy",
    4: "Social Media & Digital Platforms",
    5: "Information Privacy & Analytics",
    6: "E-Commerce & Electronic Markets",
    7: "Emerging Technologies"
}

# L2 labels (simplified - full list would be longer)
L2_LABELS = {
    "0.0": "Innovation Systems & Knowledge Management",
    "0.1": "E-Commerce Consumer Behavior",
    "0.2": "Social Networks & Collaboration",
    "0.3": "Strategic IT Investments",
    "0.4": "Digital Platforms & Ecosystems",
    "0.5": "Knowledge Management Processes",
    "1.0": "Systems Development Methods",
    "1.1": "Consumer Behavior & Reviews",
    "1.2": "Decision Support Systems",
    "1.3": "Software Development Practices",
    "1.4": "Information Systems Design",
    "1.5": "IT Project Management",
    "4.0": "Social Media Analytics",
    "4.1": "Online Communities",
    "4.2": "User-Generated Content",
    "4.3": "Social Commerce",
    "4.4": "Crowdsourcing",
    "4.5": "Digital Influence"
    # Add more as needed
}


def load_data(corpus_path, clusters_path):
    """Load enriched corpus and clustering assignments."""
    print(f"Loading corpus from {corpus_path}...")
    corpus = pd.read_parquet(corpus_path)
    
    print(f"Loading cluster assignments from {clusters_path}...")
    clusters = pd.read_csv(clusters_path)
    
    # Merge on DOI - use LEFT join from corpus to keep all papers
    print("Merging datasets...")
    merged = corpus.merge(clusters, on='doi', how='left', suffixes=('', '_cluster'))
    
    # Handle duplicate columns - prefer corpus data
    for col in ['title', 'journal', 'year', 'abstract', 'referenced_works']:
        if f'{col}_cluster' in merged.columns:
            # Fill missing corpus values with cluster values
            merged[col] = merged[col].fillna(merged[f'{col}_cluster'])
            merged.drop(f'{col}_cluster', axis=1, inplace=True)
    
    # Mark unclustered papers
    merged['L1'] = merged['L1'].fillna(-1).astype(int)
    merged['L2'] = merged['L2'].fillna(-1).astype(int)
    merged['L1_label'] = merged['L1_label'].fillna('Unclassified')
    merged['L2_label'] = merged['L2_label'].fillna('Unclassified')
    
    print(f"Loaded {len(merged)} papers total")
    print(f"  - With cluster assignments: {len(merged[merged['L1'] >= 0])}")
    print(f"  - Unclassified: {len(merged[merged['L1'] < 0])}")
    print(f"Columns: {merged.columns.tolist()[:10]}...")
    return merged


def extract_top_keywords(papers, n=10):
    """Extract top N keywords from papers in a cluster."""
    # Since we don't have explicit keywords, extract from titles
    from collections import Counter
    import re
    
    all_words = []
    
    # Common stopwords to exclude
    stopwords = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
                 'of', 'with', 'by', 'from', 'as', 'is', 'was', 'are', 'were', 'been',
                 'be', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 
                 'could', 'should', 'may', 'might', 'must', 'can', 'this', 'that',
                 'these', 'those', 'i', 'you', 'he', 'she', 'it', 'we', 'they',
                 'what', 'which', 'who', 'when', 'where', 'why', 'how', 'all', 'each',
                 'every', 'both', 'few', 'more', 'most', 'other', 'some', 'such',
                 'no', 'nor', 'not', 'only', 'own', 'same', 'so', 'than', 'too',
                 'very', 'using', 'based', 'study', 'paper', 'research', 'analysis'}
    
    # Extract words from titles
    for title in papers['title'].dropna():
        # Convert to lowercase and extract words
        words = re.findall(r'\b[a-z]{3,}\b', title.lower())
        all_words.extend([w for w in words if w not in stopwords])
    
    # Count frequencies
    word_counts = Counter(all_words)
    return [word for word, count in word_counts.most_common(n)]


def calculate_temporal_trend(papers):
    """Calculate publication trend over time."""
    years = papers['year'].dropna()
    if len(years) == 0:
        return []
    
    # Get counts per year
    year_counts = years.value_counts().sort_index()
    
    # Convert to list of [year, count] pairs
    return [[int(year), int(count)] for year, count in year_counts.items()]


def format_authors(author_data):
    """Format author information for display."""
    if pd.isna(author_data):
        return "Unknown"
    
    if isinstance(author_data, str):
        # Try to parse if it's a string representation
        try:
            import ast
            authors = ast.literal_eval(author_data)
        except:
            return author_data
    elif isinstance(author_data, list):
        authors = author_data
    else:
        return str(author_data)
    
    # Extract author names
    if isinstance(authors, list):
        names = []
        for a in authors[:3]:  # First 3 authors
            if isinstance(a, dict) and 'author' in a:
                names.append(a['author'])
            elif isinstance(a, str):
                names.append(a)
        
        result = ", ".join(names)
        if len(authors) > 3:
            result += " et al."
        return result
    
    return str(authors)


def generate_stream_data(df, stream_id):
    """Generate metadata for a single L1 stream."""
    stream_papers = df[df['L1'] == stream_id]
    
    if len(stream_papers) == 0:
        return None
    
    # Handle unclassified papers specially
    if stream_id == -1:
        stream_label = "Unclassified"
        stream_desc = "Papers not included in clustering analysis (may be too recent, lack citations, or fall outside main research streams)"
    else:
        stream_label = L1_LABELS.get(stream_id, f"Stream {stream_id}")
        stream_desc = L1_LABELS.get(stream_id, f"Stream {stream_id}")
    
    # Get top papers by citations
    top_papers = stream_papers.nlargest(5, 'citation_count', keep='all')
    
    stream_data = {
        "id": int(stream_id),
        "title": stream_label,
        "size": len(stream_papers),
        "percentage": round(len(stream_papers) / len(df) * 100, 1),
        "avgCitations": round(stream_papers['citation_count'].mean(), 1),
        "totalCitations": int(stream_papers['citation_count'].sum()),
        "topKeywords": extract_top_keywords(stream_papers, n=10),
        "yearRange": f"{int(stream_papers['year'].min())}-{int(stream_papers['year'].max())}",
        "avgYear": round(stream_papers['year'].mean(), 1),
        "temporalTrend": calculate_temporal_trend(stream_papers),
        "recentActivity": round(len(stream_papers[stream_papers['year'] >= 2020]) / len(stream_papers), 2),
        "description": stream_desc,
        "samplePapers": [
            {
                "title": row['title'],
                "authors": format_authors(row.get('authors', 'Unknown')),
                "year": int(row['year']) if pd.notna(row['year']) else None,
                "journal": row.get('journal', 'Unknown'),
                "citations": int(row['citation_count']) if pd.notna(row['citation_count']) else 0,
                "doi": row['doi']
            }
            for _, row in top_papers.iterrows()
        ],
        "l2Subtopics": []
    }
    
    # Add L2 subtopics (only for classified streams)
    if stream_id >= 0:
        for l2 in sorted(stream_papers['L2'].unique()):
            if l2 < 0:  # Skip unclassified L2
                continue
            l2_papers = stream_papers[stream_papers['L2'] == l2]
            l2_key = f"{stream_id}.{l2}"
            
            l2_data = {
                "id": l2_key,
                "title": L2_LABELS.get(l2_key, f"Subtopic {l2_key}"),
                "size": len(l2_papers),
                "avgYear": round(l2_papers['year'].mean(), 1),
                "topKeywords": extract_top_keywords(l2_papers, n=5),
                "paperCount": len(l2_papers),
                "l3Microtopics": []
            }
            
            # Add L3 micro-topics if they exist
            if 'L3' in l2_papers.columns:
                for l3 in sorted(l2_papers['L3'].dropna().unique()):
                    if l3 < 0:  # Skip unclassified L3
                        continue
                    l3_papers = l2_papers[l2_papers['L3'] == l3]
                    l3_key = f"{stream_id}.{l2}.{int(l3)}"
                    
                    # Get L3 label if available
                    l3_label = None
                    if 'L3_label' in l3_papers.columns:
                        l3_label_values = l3_papers['L3_label'].dropna().unique()
                        if len(l3_label_values) > 0:
                            l3_label = l3_label_values[0]
                    
                    l2_data["l3Microtopics"].append({
                        "id": l3_key,
                        "title": l3_label if l3_label else f"Micro-topic {l3_key}",
                        "size": len(l3_papers),
                        "avgYear": round(l3_papers['year'].mean(), 1),
                        "topKeywords": extract_top_keywords(l3_papers, n=4),
                        "paperCount": len(l3_papers)
                    })
            
            stream_data["l2Subtopics"].append(l2_data)
    
    return stream_data


def generate_paper_list(df):
    """Generate simplified paper list for dashboard."""
    papers = []
    
    for _, row in df.iterrows():
        paper = {
            "doi": row['doi'],
            "title": row['title'],
            "authors": format_authors(row.get('authors', 'Unknown')),
            "year": int(row['year']) if pd.notna(row['year']) else None,
            "journal": row.get('journal', 'Unknown'),
            "citations": int(row['citation_count']) if pd.notna(row['citation_count']) else 0,
            "l1": int(row['L1']),
            "l2": int(row['L2']),
            "l1Label": L1_LABELS.get(row['L1'], 'Unclassified' if row['L1'] < 0 else f"Stream {row['L1']}"),
            "abstract": row.get('abstract', '')[:300] if pd.notna(row.get('abstract')) else ""  # Truncate
        }
        
        # Add L3 if it exists in the data
        if 'L3' in row.index and pd.notna(row['L3']):
            paper["l3"] = int(row['L3'])
        
        if 'L3_label' in row.index and pd.notna(row['L3_label']):
            paper["l3Label"] = row['L3_label']
        
        papers.append(paper)
    
    return papers


def main():
    parser = argparse.ArgumentParser(description="Generate dashboard data from clustering results")
    parser.add_argument('--corpus', required=True, help='Path to enriched corpus parquet file')
    parser.add_argument('--clusters', required=True, help='Path to doc_assignments.csv')
    parser.add_argument('--output', required=True, help='Output JavaScript file path')
    
    args = parser.parse_args()
    
    # Load data
    df = load_data(args.corpus, args.clusters)
    
    # Ensure required columns exist
    df['citation_count'] = df['citation_count'].fillna(0)
    df['year'] = pd.to_numeric(df['year'], errors='coerce')
    
    # Filter to papers with valid year (1977-2026 to include some future pubs)
    df = df[(df['year'] >= 1977) & (df['year'] <= 2026)]
    
    print(f"\nGenerating dashboard data for {len(df)} papers...")
    print(f"  Clustered: {len(df[df['L1'] >= 0])}")
    print(f"  Unclassified: {len(df[df['L1'] < 0])}")
    
    # Generate stream data (includes -1 for unclassified)
    streams = []
    for stream_id in sorted(df['L1'].unique()):
        if stream_id < 0:
            stream_name = "Unclassified"
        else:
            stream_name = L1_LABELS.get(stream_id, f"Stream {stream_id}")
        print(f"  Processing Stream {stream_id}: {stream_name}...")
        stream_data = generate_stream_data(df, stream_id)
        if stream_data:
            streams.append(stream_data)
    
    # Generate paper list
    print("\nGenerating paper list...")
    papers = generate_paper_list(df)
    
    # Create final data structure
    dashboard_data = {
        "metadata": {
            "generated": datetime.now().isoformat(),
            "totalPapers": len(df),
            "clusteredPapers": len(df[df['L1'] >= 0]),
            "unclassifiedPapers": len(df[df['L1'] < 0]),
            "streams": len([s for s in streams if s['id'] >= 0]),
            "yearRange": f"{int(df['year'].min())}-{int(df['year'].max())}",
            "citationCoverage": round(len(df[df['citation_count'] > 0]) / len(df) * 100, 1),
            "totalCitations": int(df['citation_count'].sum())
        },
        "streams": streams,
        "papers": papers
    }
    
    # Write to JavaScript file
    print(f"\nWriting to {args.output}...")
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write("// Interactive Literature Explorer Data\n")
        f.write(f"// Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"// Total papers: {len(df)}\n")
        f.write(f"// Streams: {len(streams)}\n\n")
        f.write("const dashboardData = ")
        json.dump(dashboard_data, f, indent=2, ensure_ascii=False)
        f.write(";\n\n")
        f.write("// Make available globally\n")
        f.write("if (typeof module !== 'undefined' && module.exports) {\n")
        f.write("    module.exports = dashboardData;\n")
        f.write("}\n")
    
    # Print statistics
    file_size = output_path.stat().st_size / (1024 * 1024)  # MB
    print(f"\n✅ Dashboard data generated successfully!")
    print(f"   File: {output_path}")
    print(f"   Size: {file_size:.2f} MB")
    print(f"   Papers: {len(papers):,}")
    print(f"   Streams: {len(streams)}")
    print(f"   Year range: {dashboard_data['metadata']['yearRange']}")
    
    if file_size > 3.0:
        print(f"\n⚠️  Warning: File size ({file_size:.2f} MB) exceeds target of 2.5 MB")
        print("   Consider truncating abstracts or removing low-value fields")


if __name__ == "__main__":
    main()
