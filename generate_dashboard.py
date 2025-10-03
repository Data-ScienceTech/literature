"""
Generate beautiful interactive HTML dashboard for research stream analysis.
"""

import json
import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime
import base64

def load_analysis_data():
    """Load all analysis results."""
    data_dir = Path('data')
    
    # Load main datasets
    df = pd.read_csv(data_dir / 'papers_clustered_final.csv')
    
    with open(data_dir / 'dialog_cards_complete.json', 'r', encoding='utf-8') as f:
        dialog_cards = json.load(f)
    
    with open(data_dir / 'summary_report_complete.json', 'r', encoding='utf-8') as f:
        summary = json.load(f)
    
    with open(data_dir / 'corpus_stats.json', 'r', encoding='utf-8') as f:
        corpus_stats = json.load(f)
    
    return df, dialog_cards, summary, corpus_stats

def generate_main_dashboard(df, dialog_cards, summary, corpus_stats):
    """Generate the main dashboard HTML."""
    
    # Calculate additional statistics
    cluster_sizes = df['cluster'].value_counts().sort_values(ascending=False)
    journal_distribution = df['journal'].value_counts()
    yearly_distribution = df['year'].value_counts().sort_index()
    
    html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Research Streams Discovery Dashboard</title>
    <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/d3/7.8.5/d3.min.js"></script>
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
            font-size: 3.5em;
            background: linear-gradient(135deg, #667eea, #764ba2);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 20px;
        }}
        
        .header .subtitle {{
            font-size: 1.3em;
            color: #666;
            margin-bottom: 30px;
        }}
        
        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-bottom: 40px;
        }}
        
        .stat-card {{
            background: rgba(255, 255, 255, 0.95);
            backdrop-filter: blur(10px);
            border-radius: 15px;
            padding: 30px;
            text-align: center;
            box-shadow: 0 10px 30px rgba(0,0,0,0.1);
            transition: transform 0.3s ease;
        }}
        
        .stat-card:hover {{
            transform: translateY(-5px);
        }}
        
        .stat-card .icon {{
            font-size: 3em;
            margin-bottom: 15px;
            background: linear-gradient(135deg, #667eea, #764ba2);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }}
        
        .stat-card .number {{
            font-size: 2.5em;
            font-weight: bold;
            color: #333;
            margin-bottom: 10px;
        }}
        
        .stat-card .label {{
            font-size: 1.1em;
            color: #666;
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
            font-size: 2.5em;
            margin-bottom: 30px;
            color: #333;
            border-bottom: 3px solid #667eea;
            padding-bottom: 15px;
        }}
        
        .methodology {{
            background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
            color: white;
        }}
        
        .methodology h2 {{
            color: white;
            border-bottom-color: rgba(255,255,255,0.3);
        }}
        
        .method-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 25px;
            margin-top: 30px;
        }}
        
        .method-card {{
            background: rgba(255, 255, 255, 0.1);
            backdrop-filter: blur(10px);
            border-radius: 15px;
            padding: 25px;
            border: 1px solid rgba(255,255,255,0.2);
        }}
        
        .method-card h3 {{
            font-size: 1.4em;
            margin-bottom: 15px;
            color: #fff;
        }}
        
        .method-card .tech {{
            background: rgba(255,255,255,0.2);
            padding: 5px 12px;
            border-radius: 20px;
            font-size: 0.9em;
            display: inline-block;
            margin: 5px 5px 5px 0;
        }}
        
        .streams-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
            gap: 25px;
            margin-top: 30px;
        }}
        
        .stream-card {{
            background: linear-gradient(135deg, #667eea, #764ba2);
            color: white;
            border-radius: 15px;
            padding: 30px;
            box-shadow: 0 15px 35px rgba(0,0,0,0.1);
            transition: transform 0.3s ease;
            cursor: pointer;
        }}
        
        .stream-card:hover {{
            transform: translateY(-8px);
        }}
        
        .stream-card h3 {{
            font-size: 1.6em;
            margin-bottom: 15px;
        }}
        
        .stream-meta {{
            display: flex;
            justify-content: space-between;
            margin-bottom: 15px;
            font-size: 0.9em;
            opacity: 0.9;
        }}
        
        .chart-container {{
            background: white;
            border-radius: 15px;
            padding: 20px;
            margin: 20px 0;
            box-shadow: 0 10px 30px rgba(0,0,0,0.1);
        }}
        
        .nav-tabs {{
            display: flex;
            margin-bottom: 30px;
            background: rgba(255,255,255,0.1);
            border-radius: 15px;
            padding: 5px;
        }}
        
        .nav-tab {{
            flex: 1;
            padding: 15px 25px;
            text-align: center;
            border-radius: 10px;
            cursor: pointer;
            transition: all 0.3s ease;
            color: rgba(255,255,255,0.7);
        }}
        
        .nav-tab.active {{
            background: rgba(255,255,255,0.2);
            color: white;
        }}
        
        .tab-content {{
            display: none;
        }}
        
        .tab-content.active {{
            display: block;
        }}
        
        .footer {{
            text-align: center;
            padding: 40px;
            color: rgba(255,255,255,0.8);
        }}
        
        .footer a {{
            color: rgba(255,255,255,0.9);
            text-decoration: none;
        }}
        
        .tooltip {{
            position: relative;
            cursor: help;
        }}
        
        .tooltip:hover::after {{
            content: attr(data-tooltip);
            position: absolute;
            bottom: 100%;
            left: 50%;
            transform: translateX(-50%);
            background: rgba(0,0,0,0.9);
            color: white;
            padding: 8px 12px;
            border-radius: 5px;
            font-size: 0.8em;
            white-space: nowrap;
            z-index: 1000;
        }}
        
        @media (max-width: 768px) {{
            .header h1 {{ font-size: 2.5em; }}
            .section {{ padding: 25px; }}
            .stats-grid {{ grid-template-columns: 1fr; }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <!-- Header -->
        <div class="header">
            <h1><i class="fas fa-network-wired"></i> Research Streams Discovery</h1>
            <p class="subtitle">AI-Powered Analysis of {summary['dataset_overview']['total_papers']:,} Academic Papers from Top Management & IS Journals</p>
            <p><strong>Analysis Period:</strong> {summary['dataset_overview']['year_range']['start']}-{summary['dataset_overview']['year_range']['end']} | 
               <strong>Generated:</strong> {datetime.now().strftime('%B %d, %Y')}</p>
        </div>
        
        <!-- Key Statistics -->
        <div class="stats-grid">
            <div class="stat-card">
                <div class="icon"><i class="fas fa-file-alt"></i></div>
                <div class="number">{summary['dataset_overview']['total_papers']:,}</div>
                <div class="label">Research Papers</div>
            </div>
            <div class="stat-card">
                <div class="icon"><i class="fas fa-project-diagram"></i></div>
                <div class="number">{summary['clustering_overview']['total_clusters']}</div>
                <div class="label">Research Streams</div>
            </div>
            <div class="stat-card">
                <div class="icon"><i class="fas fa-journal-whills"></i></div>
                <div class="number">{summary['dataset_overview']['unique_journals']}</div>
                <div class="label">Top Journals</div>
            </div>
            <div class="stat-card">
                <div class="icon"><i class="fas fa-calendar-alt"></i></div>
                <div class="number">{summary['dataset_overview']['year_range']['end'] - summary['dataset_overview']['year_range']['start'] + 1}</div>
                <div class="label">Years Analyzed</div>
            </div>
        </div>
        
        <!-- Methodology Section -->
        <div class="section methodology">
            <h2><i class="fas fa-cogs"></i> World-Class Methodology</h2>
            <p style="font-size: 1.2em; margin-bottom: 30px; opacity: 0.9;">
                Our analysis employs state-of-the-art AI and network science methods, following best practices 
                from computational social science and bibliometrics research.
            </p>
            
            <div class="method-grid">
                <div class="method-card">
                    <h3><i class="fas fa-brain"></i> SPECTER2 Embeddings</h3>
                    <p>State-of-the-art transformer model specifically trained on scientific literature for semantic understanding.</p>
                    <div style="margin-top: 15px;">
                        <span class="tech">768-dimensional vectors</span>
                        <span class="tech">Cosine similarity</span>
                        <span class="tech">AllenAI</span>
                    </div>
                    <p style="margin-top: 15px; font-size: 0.9em; opacity: 0.8;">
                        <a href="https://github.com/allenai/specter2" style="color: rgba(255,255,255,0.9);">
                            <i class="fas fa-external-link-alt"></i> Learn more about SPECTER2
                        </a>
                    </p>
                </div>
                
                <div class="method-card">
                    <h3><i class="fas fa-network-wired"></i> Leiden Clustering</h3>
                    <p>Advanced community detection on k-NN graphs, superior to traditional clustering methods.</p>
                    <div style="margin-top: 15px;">
                        <span class="tech">k-NN graphs</span>
                        <span class="tech">Modularity optimization</span>
                        <span class="tech">Resolution tuning</span>
                    </div>
                    <p style="margin-top: 15px; font-size: 0.9em; opacity: 0.8;">
                        <a href="https://www.nature.com/articles/s41598-019-41695-z" style="color: rgba(255,255,255,0.9);">
                            <i class="fas fa-external-link-alt"></i> Leiden algorithm paper
                        </a>
                    </p>
                </div>
                
                <div class="method-card">
                    <h3><i class="fas fa-chart-line"></i> Temporal Analysis</h3>
                    <p>Burst detection and trend analysis to identify emerging research directions and foundational periods.</p>
                    <div style="margin-top: 15px;">
                        <span class="tech">Kleinberg bursts</span>
                        <span class="tech">Z-score analysis</span>
                        <span class="tech">RPYS</span>
                    </div>
                    <p style="margin-top: 15px; font-size: 0.9em; opacity: 0.8;">
                        <a href="https://dl.acm.org/doi/10.1145/775047.775061" style="color: rgba(255,255,255,0.9);">
                            <i class="fas fa-external-link-alt"></i> Kleinberg burst detection
                        </a>
                    </p>
                </div>
                
                <div class="method-card">
                    <h3><i class="fas fa-robot"></i> Dialog Cards</h3>
                    <p>AI-generated comprehensive summaries combining bibliometric analysis with natural language processing.</p>
                    <div style="margin-top: 15px;">
                        <span class="tech">BERTopic</span>
                        <span class="tech">TF-IDF</span>
                        <span class="tech">Automated labeling</span>
                    </div>
                    <p style="margin-top: 15px; font-size: 0.9em; opacity: 0.8;">
                        <a href="https://github.com/MaartenGr/BERTopic" style="color: rgba(255,255,255,0.9);">
                            <i class="fas fa-external-link-alt"></i> BERTopic documentation
                        </a>
                    </p>
                </div>
            </div>
        </div>
        
        <!-- Visualizations Section -->
        <div class="section">
            <h2><i class="fas fa-chart-bar"></i> Interactive Analytics</h2>
            
            <div class="nav-tabs">
                <div class="nav-tab active" onclick="showTab('overview')">Overview</div>
                <div class="nav-tab" onclick="showTab('temporal')">Temporal Trends</div>
                <div class="nav-tab" onclick="showTab('journals')">Journal Analysis</div>
                <div class="nav-tab" onclick="showTab('clusters')">Cluster Distribution</div>
            </div>
            
            <div id="overview" class="tab-content active">
                <div class="chart-container">
                    <div id="overview-chart"></div>
                </div>
            </div>
            
            <div id="temporal" class="tab-content">
                <div class="chart-container">
                    <div id="temporal-chart"></div>
                </div>
            </div>
            
            <div id="journals" class="tab-content">
                <div class="chart-container">
                    <div id="journals-chart"></div>
                </div>
            </div>
            
            <div id="clusters" class="tab-content">
                <div class="chart-container">
                    <div id="clusters-chart"></div>
                </div>
            </div>
        </div>
        
        <!-- Research Streams -->
        <div class="section">
            <h2><i class="fas fa-stream"></i> Discovered Research Streams</h2>
            <p style="font-size: 1.1em; margin-bottom: 30px; color: #666;">
                Each research stream represents a coherent dialog of papers identified through semantic similarity and citation patterns.
                Click on any stream to explore detailed insights.
            </p>
            
            <div class="streams-grid">
"""
    
    # Add top research streams
    for i, (cluster_id, card) in enumerate(list(dialog_cards.items())[:8]):
        journals_text = " • ".join([f"{j} ({c})" for j, c in list(card.get('journals', {}).items())[:2]])
        
        html_content += f"""
                <div class="stream-card" onclick="showStreamDetails('{cluster_id}')">
                    <h3><i class="fas fa-lightbulb"></i> {card.get('name', f'Stream {cluster_id}')}</h3>
                    <div class="stream-meta">
                        <span><i class="fas fa-file-alt"></i> {card.get('n_papers', 0)} papers</span>
                        <span><i class="fas fa-calendar"></i> {card.get('year_range', {}).get('start', 'N/A')}-{card.get('year_range', {}).get('end', 'N/A')}</span>
                    </div>
                    <p style="margin-bottom: 15px; opacity: 0.9;">{card.get('description', 'Research stream analysis')[:150]}...</p>
                    <p style="font-size: 0.9em; opacity: 0.8;"><i class="fas fa-journal-whills"></i> {journals_text}</p>
                </div>
"""
    
    html_content += f"""
            </div>
            
            <div style="text-align: center; margin-top: 40px;">
                <button onclick="showAllStreams()" style="background: linear-gradient(135deg, #667eea, #764ba2); color: white; border: none; padding: 15px 30px; border-radius: 25px; font-size: 1.1em; cursor: pointer; box-shadow: 0 10px 30px rgba(0,0,0,0.2);">
                    <i class="fas fa-expand-arrows-alt"></i> View All {len(dialog_cards)} Research Streams
                </button>
            </div>
        </div>
        
        <!-- Footer -->
        <div class="footer">
            <p><strong>Research Streams Discovery System</strong> | Powered by AI & Network Science</p>
            <p>Built with <i class="fas fa-heart" style="color: #e74c3c;"></i> using Python, SPECTER2, Leiden Algorithm, and Modern Web Technologies</p>
            <p style="margin-top: 20px;">
                <a href="https://github.com/allenai/specter2"><i class="fab fa-github"></i> SPECTER2</a> • 
                <a href="https://leidenalg.readthedocs.io/"><i class="fas fa-book"></i> Leiden Algorithm</a> • 
                <a href="https://plotly.com/"><i class="fas fa-chart-line"></i> Plotly</a> • 
                <a href="https://networkx.org/"><i class="fas fa-project-diagram"></i> NetworkX</a>
            </p>
        </div>
    </div>
    
    <script>
        // Tab switching functionality
        function showTab(tabName) {{
            // Hide all tab contents
            document.querySelectorAll('.tab-content').forEach(tab => {{
                tab.classList.remove('active');
            }});
            
            // Remove active class from all tabs
            document.querySelectorAll('.nav-tab').forEach(tab => {{
                tab.classList.remove('active');
            }});
            
            // Show selected tab and mark as active
            document.getElementById(tabName).classList.add('active');
            event.target.classList.add('active');
            
            // Generate chart for the selected tab
            generateChart(tabName);
        }}
        
        function generateChart(chartType) {{
            const data = {json.dumps({
                'yearly_distribution': yearly_distribution.to_dict(),
                'journal_distribution': journal_distribution.to_dict(),
                'cluster_sizes': cluster_sizes.head(10).to_dict(),
                'summary': summary
            })};
            
            switch(chartType) {{
                case 'overview':
                    createOverviewChart(data);
                    break;
                case 'temporal':
                    createTemporalChart(data);
                    break;
                case 'journals':
                    createJournalsChart(data);
                    break;
                case 'clusters':
                    createClustersChart(data);
                    break;
            }}
        }}
        
        function createOverviewChart(data) {{
            const trace = {{
                x: Object.keys(data.yearly_distribution),
                y: Object.values(data.yearly_distribution),
                type: 'scatter',
                mode: 'lines+markers',
                fill: 'tonexty',
                line: {{color: '#667eea', width: 3}},
                marker: {{color: '#764ba2', size: 8}},
                name: 'Papers per Year'
            }};
            
            const layout = {{
                title: {{
                    text: 'Research Output Growth Over Time',
                    font: {{size: 20, color: '#333'}}
                }},
                xaxis: {{title: 'Year', gridcolor: '#f0f0f0'}},
                yaxis: {{title: 'Number of Papers', gridcolor: '#f0f0f0'}},
                plot_bgcolor: 'rgba(0,0,0,0)',
                paper_bgcolor: 'rgba(0,0,0,0)',
                font: {{family: 'Segoe UI, sans-serif'}}
            }};
            
            Plotly.newPlot('overview-chart', [trace], layout, {{responsive: true}});
        }}
        
        function createTemporalChart(data) {{
            const years = Object.keys(data.yearly_distribution);
            const counts = Object.values(data.yearly_distribution);
            
            const trace = {{
                x: years,
                y: counts,
                type: 'bar',
                marker: {{
                    color: counts,
                    colorscale: 'Viridis',
                    showscale: true,
                    colorbar: {{title: 'Papers'}}
                }},
                text: counts.map(c => c.toString()),
                textposition: 'auto'
            }};
            
            const layout = {{
                title: {{
                    text: 'Annual Publication Distribution',
                    font: {{size: 20, color: '#333'}}
                }},
                xaxis: {{title: 'Publication Year'}},
                yaxis: {{title: 'Number of Papers'}},
                plot_bgcolor: 'rgba(0,0,0,0)',
                paper_bgcolor: 'rgba(0,0,0,0)'
            }};
            
            Plotly.newPlot('temporal-chart', [trace], layout, {{responsive: true}});
        }}
        
        function createJournalsChart(data) {{
            const journals = Object.keys(data.journal_distribution);
            const counts = Object.values(data.journal_distribution);
            
            const trace = {{
                labels: journals,
                values: counts,
                type: 'pie',
                hole: 0.4,
                marker: {{
                    colors: ['#667eea', '#764ba2', '#f093fb', '#f5576c']
                }},
                textinfo: 'label+percent+value',
                textposition: 'auto'
            }};
            
            const layout = {{
                title: {{
                    text: 'Distribution Across Journals',
                    font: {{size: 20, color: '#333'}}
                }},
                plot_bgcolor: 'rgba(0,0,0,0)',
                paper_bgcolor: 'rgba(0,0,0,0)',
                showlegend: true
            }};
            
            Plotly.newPlot('journals-chart', [trace], layout, {{responsive: true}});
        }}
        
        function createClustersChart(data) {{
            const clusters = Object.keys(data.cluster_sizes).map(c => `Stream ${{c}}`);
            const sizes = Object.values(data.cluster_sizes);
            
            const trace = {{
                x: clusters,
                y: sizes,
                type: 'bar',
                marker: {{
                    color: '#667eea',
                    opacity: 0.8
                }},
                text: sizes.map(s => s.toString()),
                textposition: 'auto'
            }};
            
            const layout = {{
                title: {{
                    text: 'Research Stream Sizes (Top 10)',
                    font: {{size: 20, color: '#333'}}
                }},
                xaxis: {{title: 'Research Stream', tickangle: -45}},
                yaxis: {{title: 'Number of Papers'}},
                plot_bgcolor: 'rgba(0,0,0,0)',
                paper_bgcolor: 'rgba(0,0,0,0)'
            }};
            
            Plotly.newPlot('clusters-chart', [trace], layout, {{responsive: true}});
        }}
        
        function showStreamDetails(clusterId) {{
            window.open(`stream_${{clusterId}}.html`, '_blank');
        }}
        
        function showAllStreams() {{
            window.open('all_streams.html', '_blank');
        }}
        
        // Initialize with overview chart
        document.addEventListener('DOMContentLoaded', function() {{
            generateChart('overview');
        }});
    </script>
</body>
</html>
"""
    
    return html_content

def main():
    """Generate the complete dashboard."""
    print("🎨 Generating Beautiful Interactive Dashboard...")
    
    # Load data
    df, dialog_cards, summary, corpus_stats = load_analysis_data()
    
    # Generate main dashboard
    dashboard_html = generate_main_dashboard(df, dialog_cards, summary, corpus_stats)
    
    # Save dashboard
    with open('research_streams_dashboard.html', 'w', encoding='utf-8') as f:
        f.write(dashboard_html)
    
    print("✅ Dashboard generated: research_streams_dashboard.html")
    print("🌐 Open in browser to explore your research streams!")

if __name__ == "__main__":
    main()
