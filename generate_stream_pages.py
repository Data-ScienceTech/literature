"""
Generate individual research stream detail pages.
"""

import json
import pandas as pd
from pathlib import Path
from datetime import datetime

def load_data():
    """Load analysis data."""
    data_dir = Path('data')
    
    df = pd.read_csv(data_dir / 'papers_clustered_final.csv')
    
    with open(data_dir / 'dialog_cards_complete.json', 'r', encoding='utf-8') as f:
        dialog_cards = json.load(f)
    
    return df, dialog_cards

def generate_stream_page(cluster_id, card, df):
    """Generate detailed page for a specific research stream."""
    
    # Get papers in this cluster
    cluster_papers = df[df['cluster'] == int(cluster_id)].copy()
    
    # Sort by year and citations
    cluster_papers = cluster_papers.sort_values(['year', 'title'], ascending=[False, True])
    
    # Get key statistics
    total_papers = len(cluster_papers)
    year_range = f"{cluster_papers['year'].min()}-{cluster_papers['year'].max()}"
    journals = cluster_papers['journal'].value_counts().to_dict()
    yearly_dist = cluster_papers['year'].value_counts().sort_index().to_dict()
    
    html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Research Stream: {card.get('name', f'Stream {cluster_id}')}</title>
    <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
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
            max-width: 1200px;
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
        }}
        
        .header h1 {{
            font-size: 2.8em;
            background: linear-gradient(135deg, #667eea, #764ba2);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 20px;
        }}
        
        .meta-info {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-top: 30px;
        }}
        
        .meta-card {{
            background: rgba(102, 126, 234, 0.1);
            border-radius: 10px;
            padding: 20px;
            text-align: center;
        }}
        
        .meta-card .number {{
            font-size: 2em;
            font-weight: bold;
            color: #667eea;
        }}
        
        .section {{
            background: rgba(255, 255, 255, 0.95);
            backdrop-filter: blur(10px);
            border-radius: 20px;
            padding: 40px;
            margin-bottom: 30px;
            box-shadow: 0 20px 40px rgba(0,0,0,0.1);
        }}
        
        .section h2 {{
            font-size: 2em;
            margin-bottom: 25px;
            color: #333;
            border-bottom: 3px solid #667eea;
            padding-bottom: 10px;
        }}
        
        .papers-grid {{
            display: grid;
            gap: 20px;
        }}
        
        .paper-card {{
            background: #f8f9fa;
            border-radius: 10px;
            padding: 25px;
            border-left: 4px solid #667eea;
            transition: transform 0.2s ease;
        }}
        
        .paper-card:hover {{
            transform: translateX(5px);
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
        }}
        
        .paper-title {{
            font-size: 1.3em;
            font-weight: bold;
            margin-bottom: 10px;
            color: #333;
        }}
        
        .paper-authors {{
            color: #666;
            margin-bottom: 10px;
            font-style: italic;
        }}
        
        .paper-meta {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-top: 15px;
            font-size: 0.9em;
        }}
        
        .journal-tag {{
            background: #667eea;
            color: white;
            padding: 4px 12px;
            border-radius: 15px;
            font-size: 0.8em;
        }}
        
        .year-tag {{
            background: #764ba2;
            color: white;
            padding: 4px 8px;
            border-radius: 5px;
        }}
        
        .chart-container {{
            background: white;
            border-radius: 15px;
            padding: 20px;
            margin: 20px 0;
            box-shadow: 0 10px 30px rgba(0,0,0,0.1);
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
        
        .methodology-box {{
            background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
            color: white;
            border-radius: 15px;
            padding: 25px;
            margin: 20px 0;
        }}
        
        .methodology-box h3 {{
            margin-bottom: 15px;
            font-size: 1.4em;
        }}
        
        .key-insights {{
            background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
            color: white;
            border-radius: 15px;
            padding: 25px;
            margin: 20px 0;
        }}
        
        .insight-item {{
            margin-bottom: 15px;
            padding-left: 25px;
            position: relative;
        }}
        
        .insight-item::before {{
            content: "💡";
            position: absolute;
            left: 0;
            top: 0;
        }}
        
        @media (max-width: 768px) {{
            .header {{ padding: 25px; }}
            .section {{ padding: 25px; }}
            .meta-info {{ grid-template-columns: 1fr; }}
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
            <h1><i class="fas fa-lightbulb"></i> {card.get('name', f'Research Stream {cluster_id}')}</h1>
            <p style="font-size: 1.2em; color: #666; margin-bottom: 20px;">
                {card.get('description', 'Detailed analysis of this research stream')}
            </p>
            
            <div class="meta-info">
                <div class="meta-card">
                    <div class="number">{total_papers}</div>
                    <div>Papers</div>
                </div>
                <div class="meta-card">
                    <div class="number">{year_range}</div>
                    <div>Time Span</div>
                </div>
                <div class="meta-card">
                    <div class="number">{len(journals)}</div>
                    <div>Journals</div>
                </div>
                <div class="meta-card">
                    <div class="number">{cluster_papers['year'].mode().iloc[0] if not cluster_papers['year'].mode().empty else 'N/A'}</div>
                    <div>Peak Year</div>
                </div>
            </div>
        </div>
        
        <!-- Key Insights -->
        <div class="key-insights">
            <h3><i class="fas fa-star"></i> Key Research Insights</h3>
            <div class="insight-item">
                <strong>Temporal Evolution:</strong> This stream spans {cluster_papers['year'].max() - cluster_papers['year'].min() + 1} years, 
                showing {'steady growth' if len(yearly_dist) > 5 else 'focused activity'} in research attention.
            </div>
            <div class="insight-item">
                <strong>Journal Distribution:</strong> Primary publication venue is {list(journals.keys())[0]} 
                ({list(journals.values())[0]} papers, {list(journals.values())[0]/total_papers*100:.1f}%).
            </div>
            <div class="insight-item">
                <strong>Research Maturity:</strong> {'Established field' if total_papers > 150 else 'Emerging area'} with 
                {total_papers} papers contributing to the scholarly dialog.
            </div>
        </div>
        
        <!-- Methodology -->
        <div class="methodology-box">
            <h3><i class="fas fa-microscope"></i> How This Stream Was Discovered</h3>
            <p>This research stream was identified using advanced AI and network science methods:</p>
            <ul style="margin-top: 15px; padding-left: 20px;">
                <li><strong>SPECTER2 Embeddings:</strong> Papers were encoded into 768-dimensional semantic vectors using a transformer model trained on scientific literature</li>
                <li><strong>Leiden Clustering:</strong> Community detection on k-nearest neighbor graphs revealed papers with high semantic similarity</li>
                <li><strong>Temporal Analysis:</strong> Burst detection identified periods of increased research activity</li>
                <li><strong>Quality Validation:</strong> Clustering quality assessed using silhouette scores and manual inspection</li>
            </ul>
        </div>
        
        <!-- Temporal Trends -->
        <div class="section">
            <h2><i class="fas fa-chart-line"></i> Temporal Evolution</h2>
            <div class="chart-container">
                <div id="temporal-chart"></div>
            </div>
        </div>
        
        <!-- Journal Distribution -->
        <div class="section">
            <h2><i class="fas fa-journal-whills"></i> Journal Distribution</h2>
            <div class="chart-container">
                <div id="journal-chart"></div>
            </div>
        </div>
        
        <!-- All Papers -->
        <div class="section">
            <h2><i class="fas fa-file-alt"></i> All Papers in This Stream</h2>
            <p style="margin-bottom: 30px; color: #666;">
                Papers are ordered by publication year (most recent first). Each paper contributes to the coherent 
                research dialog that defines this stream.
            </p>
            
            <div class="papers-grid">
"""
    
    # Add all papers
    for _, paper in cluster_papers.iterrows():
        html_content += f"""
                <div class="paper-card">
                    <div class="paper-title">{paper.get('title', 'Untitled')}</div>
                    <div class="paper-authors">{paper.get('authors', 'Unknown authors')}</div>
                    <div class="paper-meta">
                        <div>
                            <span class="journal-tag">{paper.get('journal', 'Unknown')}</span>
                            <span class="year-tag">{paper.get('year', 'N/A')}</span>
                        </div>
                        <div>
                            {f'<a href="https://doi.org/{paper.get("doi")}" target="_blank" style="color: #667eea; text-decoration: none;"><i class="fas fa-external-link-alt"></i> View Paper</a>' if paper.get('doi') else ''}
                        </div>
                    </div>
                </div>
"""
    
    html_content += f"""
            </div>
        </div>
        
        <!-- Footer -->
        <div style="text-align: center; padding: 40px; color: rgba(255,255,255,0.8);">
            <p><strong>Research Streams Discovery System</strong> | Powered by AI & Network Science</p>
            <p style="margin-top: 10px; font-size: 1.1em;">Developed by <a href="https://datasciencetech.ca" target="_blank" style="color: white; font-weight: bold; text-decoration: none; border-bottom: 2px solid rgba(255,255,255,0.5);">DataScienceTech.ca</a></p>
        </div>
    </div>
    
    <script>
        // Generate temporal chart
        const yearlyData = {json.dumps(yearly_dist)};
        const years = Object.keys(yearlyData).map(y => parseInt(y)).sort();
        const counts = years.map(y => yearlyData[y.toString()]);
        
        const temporalTrace = {{
            x: years,
            y: counts,
            type: 'scatter',
            mode: 'lines+markers',
            fill: 'tonexty',
            line: {{color: '#667eea', width: 3}},
            marker: {{color: '#764ba2', size: 8}},
            name: 'Papers per Year'
        }};
        
        const temporalLayout = {{
            title: {{
                text: 'Research Activity Over Time',
                font: {{size: 18, color: '#333'}}
            }},
            xaxis: {{title: 'Year'}},
            yaxis: {{title: 'Number of Papers'}},
            plot_bgcolor: 'rgba(0,0,0,0)',
            paper_bgcolor: 'rgba(0,0,0,0)'
        }};
        
        Plotly.newPlot('temporal-chart', [temporalTrace], temporalLayout, {{responsive: true}});
        
        // Generate journal chart
        const journalData = {json.dumps(journals)};
        const journalTrace = {{
            labels: Object.keys(journalData),
            values: Object.values(journalData),
            type: 'pie',
            hole: 0.4,
            marker: {{
                colors: ['#667eea', '#764ba2', '#f093fb', '#f5576c']
            }},
            textinfo: 'label+percent+value'
        }};
        
        const journalLayout = {{
            title: {{
                text: 'Distribution Across Journals',
                font: {{size: 18, color: '#333'}}
            }},
            plot_bgcolor: 'rgba(0,0,0,0)',
            paper_bgcolor: 'rgba(0,0,0,0)'
        }};
        
        Plotly.newPlot('journal-chart', [journalTrace], journalLayout, {{responsive: true}});
    </script>
</body>
</html>
"""
    
    return html_content

def generate_all_streams_page(dialog_cards, df):
    """Generate overview page of all research streams."""
    
    html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>All Research Streams - Comprehensive Overview</title>
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
        
        .streams-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
            gap: 25px;
            margin-top: 30px;
        }}
        
        .stream-card {{
            background: rgba(255, 255, 255, 0.95);
            backdrop-filter: blur(10px);
            border-radius: 15px;
            padding: 30px;
            box-shadow: 0 15px 35px rgba(0,0,0,0.1);
            transition: transform 0.3s ease;
            cursor: pointer;
            border-left: 5px solid #667eea;
        }}
        
        .stream-card:hover {{
            transform: translateY(-8px);
        }}
        
        .stream-card h3 {{
            font-size: 1.5em;
            margin-bottom: 15px;
            color: #333;
        }}
        
        .stream-meta {{
            display: flex;
            justify-content: space-between;
            margin-bottom: 15px;
            font-size: 0.9em;
            color: #666;
        }}
        
        .stream-description {{
            color: #555;
            margin-bottom: 20px;
            line-height: 1.5;
        }}
        
        .journal-tags {{
            display: flex;
            flex-wrap: wrap;
            gap: 8px;
        }}
        
        .journal-tag {{
            background: #667eea;
            color: white;
            padding: 4px 10px;
            border-radius: 12px;
            font-size: 0.8em;
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
        }}
        
        .search-box {{
            background: rgba(255, 255, 255, 0.95);
            border-radius: 15px;
            padding: 20px;
            margin-bottom: 30px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.1);
        }}
        
        .search-input {{
            width: 100%;
            padding: 15px;
            border: 2px solid #667eea;
            border-radius: 10px;
            font-size: 1.1em;
            outline: none;
        }}
        
        .stats-summary {{
            background: rgba(255, 255, 255, 0.95);
            border-radius: 15px;
            padding: 30px;
            margin-bottom: 30px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.1);
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            text-align: center;
        }}
        
        .stat-item {{
            padding: 20px;
            background: linear-gradient(135deg, #667eea, #764ba2);
            color: white;
            border-radius: 10px;
        }}
        
        .stat-number {{
            font-size: 2.5em;
            font-weight: bold;
            margin-bottom: 10px;
        }}
        
        @media (max-width: 768px) {{
            .streams-grid {{ grid-template-columns: 1fr; }}
            .stats-summary {{ grid-template-columns: repeat(2, 1fr); }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <a href="research_streams_dashboard.html" class="back-button">
            <i class="fas fa-arrow-left"></i> Back to Dashboard
        </a>
        
        <div class="header">
            <h1><i class="fas fa-stream"></i> All Research Streams</h1>
            <p style="font-size: 1.2em; color: #666;">
                Comprehensive overview of all {len(dialog_cards)} discovered research streams
            </p>
        </div>
        
        <div class="stats-summary">
            <div class="stat-item">
                <div class="stat-number">{len(dialog_cards)}</div>
                <div>Research Streams</div>
            </div>
            <div class="stat-item">
                <div class="stat-number">{len(df):,}</div>
                <div>Total Papers</div>
            </div>
            <div class="stat-item">
                <div class="stat-number">{df['year'].max() - df['year'].min() + 1}</div>
                <div>Years Covered</div>
            </div>
            <div class="stat-item">
                <div class="stat-number">{df['journal'].nunique()}</div>
                <div>Journals</div>
            </div>
        </div>
        
        <div class="search-box">
            <input type="text" class="search-input" placeholder="🔍 Search research streams by name, description, or journal..." 
                   onkeyup="filterStreams(this.value)">
        </div>
        
        <div class="streams-grid" id="streams-container">
"""
    
    # Add all streams
    for cluster_id, card in dialog_cards.items():
        journals = card.get('journals', {})
        top_journals = list(journals.keys())[:3]
        
        html_content += f"""
            <div class="stream-card" onclick="window.open('stream_{cluster_id}.html', '_blank')" 
                 data-search="{card.get('name', '').lower()} {card.get('description', '').lower()} {' '.join(top_journals).lower()}">
                <h3><i class="fas fa-lightbulb"></i> {card.get('name', f'Stream {cluster_id}')}</h3>
                <div class="stream-meta">
                    <span><i class="fas fa-file-alt"></i> {card.get('n_papers', 0)} papers</span>
                    <span><i class="fas fa-calendar"></i> {card.get('year_range', {}).get('start', 'N/A')}-{card.get('year_range', {}).get('end', 'N/A')}</span>
                </div>
                <div class="stream-description">
                    {card.get('description', 'Research stream analysis')[:200]}...
                </div>
                <div class="journal-tags">
"""
        
        for journal in top_journals:
            html_content += f'<span class="journal-tag">{journal}</span>'
        
        html_content += """
                </div>
            </div>
"""
    
    html_content += """
        </div>
        
        <!-- Footer -->
        <div style="text-align: center; padding: 40px; color: rgba(255,255,255,0.8);">
            <p><strong>Research Streams Discovery System</strong> | Powered by AI & Network Science</p>
            <p style="margin-top: 10px; font-size: 1.1em;">Developed by <a href="https://datasciencetech.ca" target="_blank" style="color: white; font-weight: bold; text-decoration: none; border-bottom: 2px solid rgba(255,255,255,0.5);">DataScienceTech.ca</a></p>
        </div>
    </div>
    
    <script>
        function filterStreams(searchTerm) {
            const cards = document.querySelectorAll('.stream-card');
            const term = searchTerm.toLowerCase();
            
            cards.forEach(card => {
                const searchData = card.getAttribute('data-search');
                if (searchData.includes(term)) {
                    card.style.display = 'block';
                } else {
                    card.style.display = 'none';
                }
            });
        }
    </script>
</body>
</html>
"""
    
    return html_content

def main():
    """Generate all stream pages."""
    print("🎨 Generating Individual Stream Pages...")
    
    # Load data
    df, dialog_cards = load_data()
    
    # Generate individual stream pages
    for cluster_id, card in dialog_cards.items():
        print(f"   Generating stream_{cluster_id}.html...")
        stream_html = generate_stream_page(cluster_id, card, df)
        
        with open(f'stream_{cluster_id}.html', 'w', encoding='utf-8') as f:
            f.write(stream_html)
    
    # Generate all streams overview
    print("   Generating all_streams.html...")
    all_streams_html = generate_all_streams_page(dialog_cards, df)
    
    with open('all_streams.html', 'w', encoding='utf-8') as f:
        f.write(all_streams_html)
    
    print(f"✅ Generated {len(dialog_cards)} individual stream pages + overview")
    print("🌐 Complete interactive dashboard ready!")

if __name__ == "__main__":
    main()
