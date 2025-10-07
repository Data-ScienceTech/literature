"""
Generate searchable papers database page.
"""

import json
import pandas as pd
from pathlib import Path
from datetime import datetime

def generate_papers_database():
    """Generate searchable database of all papers."""
    
    # Load data
    data_dir = Path('data')
    df = pd.read_csv(data_dir / 'papers_clustered_final.csv')
    
    # Sort by year (descending) and title
    df = df.sort_values(['year', 'title'], ascending=[False, True])
    
    # Get statistics
    total_papers = len(df)
    year_range = f"{df['year'].min()}-{df['year'].max()}"
    journals = df['journal'].value_counts().to_dict()
    clusters = df['cluster'].nunique()
    
    html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Searchable Papers Database - {total_papers:,} Papers</title>
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css" rel="stylesheet">
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            color: #333;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
        }}
        
        .container {{
            max-width: 1400px;
            margin: 0 auto;
            padding: 20px;
        }}
        
        .header {{
            background: rgba(255, 255, 255, 0.95);
            backdrop-filter: blur(10px);
            border-radius: 20px;
            padding: 40px;
            margin-bottom: 30px;
            box-shadow: 0 20px 40px rgba(0,0,0,0.1);
            text-align: center;
        }}
        
        .header h1 {{
            font-size: 3em;
            background: linear-gradient(135deg, #667eea, #764ba2);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 20px;
        }}
        
        .search-section {{
            background: rgba(255, 255, 255, 0.95);
            backdrop-filter: blur(10px);
            border-radius: 20px;
            padding: 30px;
            margin-bottom: 30px;
            box-shadow: 0 20px 40px rgba(0,0,0,0.1);
        }}
        
        .search-box {{
            position: relative;
            margin-bottom: 20px;
        }}
        
        .search-input {{
            width: 100%;
            padding: 20px 60px 20px 20px;
            border: 3px solid #667eea;
            border-radius: 15px;
            font-size: 1.2em;
            outline: none;
            transition: all 0.3s ease;
        }}
        
        .search-input:focus {{
            border-color: #764ba2;
            box-shadow: 0 0 20px rgba(102, 126, 234, 0.3);
        }}
        
        .search-icon {{
            position: absolute;
            right: 20px;
            top: 50%;
            transform: translateY(-50%);
            font-size: 1.5em;
            color: #667eea;
        }}
        
        .filters {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin-top: 20px;
        }}
        
        .filter-group {{
            display: flex;
            flex-direction: column;
        }}
        
        .filter-group label {{
            font-weight: bold;
            margin-bottom: 8px;
            color: #667eea;
        }}
        
        .filter-group select {{
            padding: 10px;
            border: 2px solid #667eea;
            border-radius: 8px;
            font-size: 1em;
            outline: none;
            cursor: pointer;
        }}
        
        .stats-bar {{
            background: linear-gradient(135deg, #667eea, #764ba2);
            color: white;
            padding: 15px 25px;
            border-radius: 10px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 20px;
        }}
        
        .results-section {{
            background: rgba(255, 255, 255, 0.95);
            backdrop-filter: blur(10px);
            border-radius: 20px;
            padding: 30px;
            box-shadow: 0 20px 40px rgba(0,0,0,0.1);
        }}
        
        .papers-grid {{
            display: grid;
            gap: 20px;
        }}
        
        .paper-card {{
            background: #f8f9fa;
            border-radius: 12px;
            padding: 25px;
            border-left: 5px solid #667eea;
            transition: all 0.3s ease;
            cursor: pointer;
        }}
        
        .paper-card:hover {{
            transform: translateX(5px);
            box-shadow: 0 8px 25px rgba(0,0,0,0.15);
            border-left-color: #764ba2;
        }}
        
        .paper-title {{
            font-size: 1.3em;
            font-weight: bold;
            margin-bottom: 12px;
            color: #333;
            line-height: 1.4;
        }}
        
        .paper-authors {{
            color: #666;
            margin-bottom: 12px;
            font-style: italic;
        }}
        
        .paper-meta {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            flex-wrap: wrap;
            gap: 10px;
            margin-top: 15px;
        }}
        
        .meta-tags {{
            display: flex;
            gap: 8px;
            flex-wrap: wrap;
        }}
        
        .journal-tag {{
            background: #667eea;
            color: white;
            padding: 5px 12px;
            border-radius: 15px;
            font-size: 0.85em;
        }}
        
        .year-tag {{
            background: #764ba2;
            color: white;
            padding: 5px 10px;
            border-radius: 8px;
            font-size: 0.85em;
        }}
        
        .stream-tag {{
            background: #f093fb;
            color: white;
            padding: 5px 10px;
            border-radius: 8px;
            font-size: 0.85em;
        }}
        
        .doi-link {{
            color: #667eea;
            text-decoration: none;
            font-weight: bold;
            transition: color 0.2s ease;
        }}
        
        .doi-link:hover {{
            color: #764ba2;
        }}
        
        .back-button {{
            background: linear-gradient(135deg, #667eea, #764ba2);
            color: white;
            border: none;
            padding: 12px 25px;
            border-radius: 25px;
            font-size: 1em;
            cursor: pointer;
            text-decoration: none;
            display: inline-block;
            margin-bottom: 20px;
            transition: transform 0.2s ease;
        }}
        
        .back-button:hover {{
            transform: translateY(-2px);
        }}
        
        .no-results {{
            text-align: center;
            padding: 60px 20px;
            color: #666;
        }}
        
        .no-results i {{
            font-size: 4em;
            margin-bottom: 20px;
            color: #667eea;
        }}
        
        .loading {{
            text-align: center;
            padding: 40px;
            color: #667eea;
            font-size: 1.2em;
        }}
        
        @media (max-width: 768px) {{
            .header {{ padding: 25px; }}
            .header h1 {{ font-size: 2em; }}
            .filters {{ grid-template-columns: 1fr; }}
            .stats-bar {{ flex-direction: column; gap: 10px; }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <a href="research_streams_dashboard.html" class="back-button">
            <i class="fas fa-arrow-left"></i> Back to Dashboard
        </a>
        
        <!-- Header -->
        <div class="header">
            <h1><i class="fas fa-database"></i> Searchable Papers Database</h1>
            <p style="font-size: 1.3em; color: #666;">
                Explore all {total_papers:,} papers from {year_range}
            </p>
            <p style="margin-top: 15px; color: #888;">
                Search by title, author, journal, year, or research stream
            </p>
        </div>
        
        <!-- Search Section -->
        <div class="search-section">
            <div class="search-box">
                <input type="text" 
                       class="search-input" 
                       id="searchInput"
                       placeholder="🔍 Search by title, author, keywords..."
                       oninput="filterPapers()">
                <i class="fas fa-search search-icon"></i>
            </div>
            
            <div class="filters">
                <div class="filter-group">
                    <label><i class="fas fa-journal-whills"></i> Journal</label>
                    <select id="journalFilter" onchange="filterPapers()">
                        <option value="">All Journals</option>
"""
    
    # Add journal options
    for journal in sorted(journals.keys()):
        html_content += f'                        <option value="{journal}">{journal} ({journals[journal]})</option>\n'
    
    html_content += """
                    </select>
                </div>
                
                <div class="filter-group">
                    <label><i class="fas fa-calendar"></i> Year</label>
                    <select id="yearFilter" onchange="filterPapers()">
                        <option value="">All Years</option>
"""
    
    # Add year options
    for year in sorted(df['year'].unique(), reverse=True):
        count = len(df[df['year'] == year])
        html_content += f'                        <option value="{year}">{year} ({count})</option>\n'
    
    html_content += f"""
                    </select>
                </div>
                
                <div class="filter-group">
                    <label><i class="fas fa-stream"></i> Research Stream</label>
                    <select id="streamFilter" onchange="filterPapers()">
                        <option value="">All Streams</option>
"""
    
    # Add stream options
    for cluster_id in sorted(df['cluster'].unique()):
        count = len(df[df['cluster'] == cluster_id])
        html_content += f'                        <option value="{cluster_id}">Stream {cluster_id} ({count})</option>\n'
    
    html_content += f"""
                    </select>
                </div>
                
                <div class="filter-group">
                    <label><i class="fas fa-sort"></i> Sort By</label>
                    <select id="sortFilter" onchange="sortPapers()">
                        <option value="year-desc">Year (Newest First)</option>
                        <option value="year-asc">Year (Oldest First)</option>
                        <option value="title-asc">Title (A-Z)</option>
                        <option value="title-desc">Title (Z-A)</option>
                    </select>
                </div>
            </div>
            
            <div class="stats-bar" style="margin-top: 20px;">
                <span id="resultCount">Showing {total_papers:,} papers</span>
                <button onclick="clearFilters()" style="background: rgba(255,255,255,0.2); border: none; color: white; padding: 8px 15px; border-radius: 8px; cursor: pointer;">
                    <i class="fas fa-redo"></i> Clear Filters
                </button>
            </div>
        </div>
        
        <!-- Results Section -->
        <div class="results-section">
            <div class="papers-grid" id="papersContainer">
"""
    
    # Add all papers
    for _, paper in df.iterrows():
        # Create search data (handle NaN values)
        title = str(paper.get('title', '')) if pd.notna(paper.get('title')) else ''
        authors = str(paper.get('authors', '')) if pd.notna(paper.get('authors')) else ''
        journal = str(paper.get('journal', '')) if pd.notna(paper.get('journal')) else ''
        search_data = f"{title.lower()} {authors.lower()} {journal.lower()}"
        
        html_content += f"""
                <div class="paper-card" 
                     data-search="{search_data}"
                     data-journal="{journal}"
                     data-year="{paper.get('year', '')}"
                     data-stream="{paper.get('cluster', '')}"
                     data-title="{title.lower()}">
                    <div class="paper-title">{title if title else 'Untitled'}</div>
                    <div class="paper-authors">{authors if authors else 'Unknown authors'}</div>
                    <div class="paper-meta">
                        <div class="meta-tags">
                            <span class="journal-tag">{paper.get('journal', 'Unknown')}</span>
                            <span class="year-tag">{paper.get('year', 'N/A')}</span>
                            <span class="stream-tag">Stream {paper.get('cluster', 'N/A')}</span>
                        </div>
                        <div>
                            {f'<a href="https://doi.org/{paper.get("doi")}" target="_blank" class="doi-link"><i class="fas fa-external-link-alt"></i> View Paper</a>' if paper.get('doi') else ''}
                        </div>
                    </div>
                </div>
"""
    
    html_content += """
            </div>
            
            <div id="noResults" class="no-results" style="display: none;">
                <i class="fas fa-search"></i>
                <h2>No papers found</h2>
                <p>Try adjusting your search terms or filters</p>
            </div>
        </div>
        
        <!-- Footer -->
        <div style="text-align: center; padding: 40px; color: rgba(255,255,255,0.8);">
            <p><strong>Research Streams Discovery System</strong> | Powered by AI & Network Science</p>
            <p style="margin-top: 10px; font-size: 1.1em;">Developed by <a href="https://datasciencetech.ca" target="_blank" style="color: white; font-weight: bold; text-decoration: none; border-bottom: 2px solid rgba(255,255,255,0.5);">DataScienceTech.ca</a></p>
        </div>
    </div>
    
    <script>
        let allPapers = [];
        
        // Initialize papers array
        document.addEventListener('DOMContentLoaded', function() {
            allPapers = Array.from(document.querySelectorAll('.paper-card'));
        });
        
        function filterPapers() {
            const searchTerm = document.getElementById('searchInput').value.toLowerCase();
            const journalFilter = document.getElementById('journalFilter').value;
            const yearFilter = document.getElementById('yearFilter').value;
            const streamFilter = document.getElementById('streamFilter').value;
            
            let visibleCount = 0;
            
            allPapers.forEach(paper => {
                const searchData = paper.getAttribute('data-search');
                const journal = paper.getAttribute('data-journal');
                const year = paper.getAttribute('data-year');
                const stream = paper.getAttribute('data-stream');
                
                // Check all filters
                const matchesSearch = searchTerm === '' || searchData.includes(searchTerm);
                const matchesJournal = journalFilter === '' || journal === journalFilter;
                const matchesYear = yearFilter === '' || year === yearFilter;
                const matchesStream = streamFilter === '' || stream === streamFilter;
                
                if (matchesSearch && matchesJournal && matchesYear && matchesStream) {
                    paper.style.display = 'block';
                    visibleCount++;
                } else {
                    paper.style.display = 'none';
                }
            });
            
            // Update result count
            document.getElementById('resultCount').textContent = 
                `Showing ${visibleCount.toLocaleString()} of ${allPapers.length.toLocaleString()} papers`;
            
            // Show/hide no results message
            document.getElementById('noResults').style.display = visibleCount === 0 ? 'block' : 'none';
            document.getElementById('papersContainer').style.display = visibleCount === 0 ? 'none' : 'grid';
        }
        
        function sortPapers() {
            const sortBy = document.getElementById('sortFilter').value;
            const container = document.getElementById('papersContainer');
            
            allPapers.sort((a, b) => {
                if (sortBy === 'year-desc') {
                    return parseInt(b.getAttribute('data-year')) - parseInt(a.getAttribute('data-year'));
                } else if (sortBy === 'year-asc') {
                    return parseInt(a.getAttribute('data-year')) - parseInt(b.getAttribute('data-year'));
                } else if (sortBy === 'title-asc') {
                    return a.getAttribute('data-title').localeCompare(b.getAttribute('data-title'));
                } else if (sortBy === 'title-desc') {
                    return b.getAttribute('data-title').localeCompare(a.getAttribute('data-title'));
                }
                return 0;
            });
            
            // Re-append in sorted order
            allPapers.forEach(paper => container.appendChild(paper));
        }
        
        function clearFilters() {
            document.getElementById('searchInput').value = '';
            document.getElementById('journalFilter').value = '';
            document.getElementById('yearFilter').value = '';
            document.getElementById('streamFilter').value = '';
            document.getElementById('sortFilter').value = 'year-desc';
            filterPapers();
        }
    </script>
</body>
</html>
"""
    
    return html_content

def main():
    """Generate the papers database page."""
    print("📚 Generating Searchable Papers Database...")
    
    html_content = generate_papers_database()
    
    with open('papers_database.html', 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print("✅ Papers database generated: papers_database.html")
    print("🔍 Features:")
    print("   • Search by title, author, keywords")
    print("   • Filter by journal, year, research stream")
    print("   • Sort by year or title")
    print("   • Clickable DOI links for all papers")
    print("   • Real-time filtering and sorting")

if __name__ == "__main__":
    main()
