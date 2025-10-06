"""
Interactive Hierarchical Cluster Explorer Dashboard
A comprehensive web-based interface for exploring research stream analysis results
"""

import dash
from dash import dcc, html, Input, Output, State, callback_context
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np
import json
from pathlib import Path
from collections import Counter
import base64

# Initialize the Dash app
app = dash.Dash(
    __name__,
    title="Research Stream Explorer",
    update_title="Loading...",
    suppress_callback_exceptions=True
)

# Custom CSS
app.index_string = '''
<!DOCTYPE html>
<html>
    <head>
        {%metas%}
        <title>{%title%}</title>
        {%favicon%}
        {%css%}
        <style>
            body {
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                margin: 0;
                padding: 0;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            }
            .header {
                background: white;
                padding: 20px;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                margin-bottom: 20px;
            }
            .header h1 {
                margin: 0;
                color: #667eea;
                font-size: 32px;
            }
            .header p {
                margin: 5px 0 0 0;
                color: #666;
                font-size: 16px;
            }
            .stats-card {
                background: white;
                border-radius: 8px;
                padding: 20px;
                margin: 10px;
                box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            }
            .stat-number {
                font-size: 36px;
                font-weight: bold;
                color: #667eea;
            }
            .stat-label {
                font-size: 14px;
                color: #666;
                text-transform: uppercase;
            }
            .tab-content {
                background: white;
                border-radius: 8px;
                padding: 20px;
                margin: 10px;
                box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            }
        </style>
    </head>
    <body>
        {%app_entry%}
        <footer>
            {%config%}
            {%scripts%}
            {%renderer%}
        </footer>
    </body>
</html>
'''

# Load data on startup
def load_data():
    """Load all analysis data"""
    global df, hierarchy, enriched_data, keyword_map, cluster_names
    
    print("Loading data...")
    
    # Load clustered papers
    df = pd.read_csv('data/papers_hierarchical_clustered.csv')
    
    # Load hierarchy
    with open('data/hierarchy_leiden.json') as f:
        hierarchy = json.load(f)
    
    # Load enriched data for keywords
    with open('data/clean/ais_basket_corpus_enriched.json', encoding='utf-8') as f:
        enriched_data = json.load(f)
    
    # Load meaningful cluster names
    try:
        with open('data/cluster_names_map.json') as f:
            cluster_names = json.load(f)
        print("Loaded meaningful cluster names")
    except FileNotFoundError:
        cluster_names = {}
        print("Warning: cluster_names_map.json not found, using generic names")
    
    # Create keyword mapping
    keyword_map = {}
    for paper in enriched_data:
        paper_id = paper.get('doi') or paper.get('openalex_id', '')
        if paper_id and 'subject' in paper and isinstance(paper['subject'], list):
            keyword_map[paper_id] = paper['subject']
    
    df['keywords'] = df['doi'].map(keyword_map)
    
    # Add combined citations (OpenAlex + CrossRef)
    openalex_cites = {}
    for paper in enriched_data:
        paper_id = paper.get('doi') or paper.get('openalex_id', '')
        if paper_id and 'openalex_cited_by_count' in paper:
            openalex_cites[paper_id] = paper['openalex_cited_by_count']
    
    df['openalex_citations'] = df['doi'].map(openalex_cites)
    df['citations_combined'] = df['openalex_citations'].fillna(df['Citations'])
    
    print(f"Loaded {len(df):,} papers with {hierarchy.get('total_clusters', 0)} clusters")

# Initialize data on import
load_data()


def create_sunburst():
    """Create interactive sunburst chart"""
    labels = []
    parents = []
    values = []
    colors = []
    hover_text = []
    
    # Add root
    labels.append("All Papers")
    parents.append("")
    values.append(len(df))
    colors.append(0)
    hover_text.append(f"Total: {len(df):,} papers")
    
    # Add clusters from hierarchy
    max_depth = min(3, hierarchy.get('max_depth', 0))
    
    for level in range(max_depth + 1):
        cluster_col = f'cluster_l{level}'
        if cluster_col not in df.columns:
            continue
        
        for cluster_id in df[cluster_col].dropna().unique():
            cluster_df = df[df[cluster_col] == cluster_id]
            
            # Determine parent
            if level == 0:
                parent = "All Papers"
            else:
                parent_col = f'cluster_l{level-1}'
                if parent_col in cluster_df.columns:
                    parent_id = cluster_df[parent_col].iloc[0]
                    # Get parent name if available
                    parent_name = None
                    if cluster_names and f'level_{level-1}' in cluster_names:
                        parent_info = cluster_names[f'level_{level-1}'].get(str(parent_id))
                        if parent_info:
                            parent_name = parent_info.get('name', f'Cluster {parent_id}')
                    if not parent_name:
                        parent_name = f'L{level-1}: {parent_id}'
                    # Make parent unique
                    parent = f"{parent_name} [L{level-1}-{parent_id}]"
                else:
                    parent = "All Papers"
            
            # Get meaningful cluster name
            cluster_name = None
            if cluster_names and f'level_{level}' in cluster_names:
                cluster_info = cluster_names[f'level_{level}'].get(str(cluster_id))
                if cluster_info:
                    cluster_name = cluster_info.get('name', f'Cluster {cluster_id}')
            
            if not cluster_name:
                cluster_name = f'L{level}: {cluster_id}'
            
            # Make label unique by adding level and ID
            label = f"{cluster_name} [L{level}-{cluster_id}]"
            
            # Get stats
            mean_cites = cluster_df['citations_combined'].mean()
            total_cites = cluster_df['citations_combined'].sum()
            
            hover = f"<b>{cluster_name}</b><br>"
            hover += f"Level {level}, Cluster {cluster_id}<br>"
            hover += f"Papers: {len(cluster_df):,}<br>"
            hover += f"Total Citations: {total_cites:,.0f}<br>"
            hover += f"Mean Citations: {mean_cites:.1f}"
            
            labels.append(label)
            parents.append(parent)
            values.append(len(cluster_df))
            colors.append(level)
            hover_text.append(hover)
    
    fig = go.Figure(go.Sunburst(
        labels=labels,
        parents=parents,
        values=values,
        branchvalues="total",
        marker=dict(
            colorscale='Viridis',
            cmid=max_depth/2,
            line=dict(width=2, color='white')
        ),
        hovertemplate='%{customdata}<extra></extra>',
        customdata=hover_text
    ))
    
    fig.update_layout(
        height=700,
        margin=dict(t=0, l=0, r=0, b=0),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)'
    )
    
    return fig


def create_cluster_details_table(level=0, cluster_id=None):
    """Create detailed table for a specific cluster"""
    if cluster_id is None:
        cluster_col = f'cluster_l{level}'
        cluster_id = df[cluster_col].value_counts().index[0]
    
    cluster_col = f'cluster_l{level}'
    cluster_df = df[df[cluster_col] == str(cluster_id)]
    
    if len(cluster_df) == 0:
        return html.Div("No data available")
    
    # Get meaningful cluster name
    cluster_name = f"Cluster {cluster_id}"
    if cluster_names and f'level_{level}' in cluster_names:
        cluster_info = cluster_names[f'level_{level}'].get(str(cluster_id))
        if cluster_info:
            cluster_name = cluster_info.get('name', cluster_name)
    
    # Get top papers by combined citations
    top_papers = cluster_df.nlargest(10, 'citations_combined')[
        ['Title', 'Author', 'Year', 'Journal', 'citations_combined']
    ]
    
    # Get top keywords from meaningful cluster themes if available
    top_keywords = []
    if cluster_names and f'level_{level}' in cluster_names:
        cluster_info = cluster_names[f'level_{level}'].get(str(cluster_id))
        if cluster_info and 'top_keywords' in cluster_info:
            top_keywords = cluster_info['top_keywords'][:15]
    
    # Create stats
    stats = html.Div([
        html.H2(cluster_name, style={'color': '#667eea', 'margin-bottom': '20px'}),
        
        html.Div([
            html.Div([
                html.Div(f"{len(cluster_df):,}", className="stat-number"),
                html.Div("Papers", className="stat-label")
            ], style={'flex': '1', 'text-align': 'center'}),
            html.Div([
                html.Div(f"{cluster_df['citations_combined'].sum():,.0f}", className="stat-number"),
                html.Div("Total Citations", className="stat-label")
            ], style={'flex': '1', 'text-align': 'center'}),
            html.Div([
                html.Div(f"{cluster_df['citations_combined'].mean():.1f}", className="stat-number"),
                html.Div("Mean Citations", className="stat-label")
            ], style={'flex': '1', 'text-align': 'center'}),
            html.Div([
                html.Div(f"{cluster_df['citations_combined'].median():.0f}", className="stat-number"),
                html.Div("Median Citations", className="stat-label")
            ], style={'flex': '1', 'text-align': 'center'}),
        ], style={'display': 'flex', 'margin-bottom': '20px'}),
        
        html.H3("Top Keywords from Theme Analysis"),
        html.Div([
            html.Span(
                kw,
                style={
                    'display': 'inline-block',
                    'margin': '5px',
                    'padding': '8px 15px',
                    'background': f'rgba(102, 126, 234, {min((idx + 1) / len(top_keywords), 1) * 0.8 + 0.2})',
                    'color': 'white',
                    'border-radius': '20px',
                    'font-size': '14px'
                }
            ) for idx, kw in enumerate(top_keywords)
        ]) if top_keywords else html.Div("No thematic keywords available"),
        
        html.H3("Most Cited Papers", style={'margin-top': '30px'}),
        html.Table([
            html.Thead(html.Tr([
                html.Th("Title"),
                html.Th("Author"),
                html.Th("Year"),
                html.Th("Journal"),
                html.Th("Citations")
            ])),
            html.Tbody([
                html.Tr([
                    html.Td(row['Title'][:80] + "..." if len(str(row['Title'])) > 80 else row['Title']),
                    html.Td(str(row['Author'])[:40] if pd.notna(row['Author']) else ""),
                    html.Td(int(row['Year']) if pd.notna(row['Year']) else ""),
                    html.Td(row['Journal']),
                    html.Td(f"{int(row['citations_combined']):,}" if pd.notna(row['citations_combined']) else "0")
                ]) for _, row in top_papers.iterrows()
            ])
        ], style={'width': '100%', 'border-collapse': 'collapse', 'font-size': '12px'})
    ])
    
    return stats


def create_keyword_network(level=0, top_n=30):
    """Create keyword co-occurrence network with cluster context"""
    cluster_col = f'cluster_l{level}'
    
    # Collect all keywords with cluster information
    all_keywords = []
    keyword_clusters = {}  # Track which clusters each keyword appears in
    
    for idx, row in df.iterrows():
        keywords = row.get('keywords')
        if keywords is not None and isinstance(keywords, list):
            cluster_id = row.get(cluster_col)
            if cluster_id is not None:
                for kw in keywords:
                    all_keywords.append(kw)
                    if kw not in keyword_clusters:
                        keyword_clusters[kw] = set()
                    keyword_clusters[kw].add(str(cluster_id))
    
    # Get top keywords
    kw_counter = Counter(all_keywords)
    top_kws = [kw for kw, _ in kw_counter.most_common(top_n)]
    
    # Build co-occurrence matrix
    from itertools import combinations
    cooccurrence = Counter()
    
    for kw_list in df['keywords'].dropna():
        if isinstance(kw_list, list):
            filtered_kws = [kw for kw in kw_list if kw in top_kws]
            for kw1, kw2 in combinations(sorted(filtered_kws), 2):
                cooccurrence[(kw1, kw2)] += 1
    
    # Create network edges
    edge_x = []
    edge_y = []
    edge_weights = []
    
    # Position keywords in circle
    import math
    n = len(top_kws)
    positions = {}
    for i, kw in enumerate(top_kws):
        angle = 2 * math.pi * i / n
        positions[kw] = (math.cos(angle), math.sin(angle))
    
    for (kw1, kw2), weight in cooccurrence.most_common(100):
        if weight > 5:  # Threshold
            x0, y0 = positions[kw1]
            x1, y1 = positions[kw2]
            edge_x.extend([x0, x1, None])
            edge_y.extend([y0, y1, None])
            edge_weights.append(weight)
    
    # Create edges trace
    edge_trace = go.Scatter(
        x=edge_x, y=edge_y,
        line=dict(width=0.5, color='#888'),
        hoverinfo='none',
        mode='lines')
    
    # Create nodes trace with cluster information
    node_x = [positions[kw][0] for kw in top_kws]
    node_y = [positions[kw][1] for kw in top_kws]
    node_text = top_kws
    node_size = [kw_counter[kw] for kw in top_kws]
    
    # Create hover text with cluster names
    hover_texts = []
    for kw in top_kws:
        cluster_ids = keyword_clusters.get(kw, set())
        cluster_info = []
        
        # Get meaningful cluster names
        for cid in sorted(cluster_ids, key=str)[:5]:  # Top 5 clusters
            if cluster_names and f'level_{level}' in cluster_names:
                c_info = cluster_names[f'level_{level}'].get(str(cid))
                if c_info:
                    name = c_info.get('name', f'Cluster {cid}')
                    if len(name) > 40:
                        name = name[:37] + '...'
                    cluster_info.append(name)
                else:
                    cluster_info.append(f'Cluster {cid}')
            else:
                cluster_info.append(f'Cluster {cid}')
        
        clusters_text = '<br>  • ' + '<br>  • '.join(cluster_info) if cluster_info else ''
        hover_text = f"<b>{kw}</b><br>{kw_counter[kw]} papers<br>Top clusters:{clusters_text}"
        hover_texts.append(hover_text)
    
    node_trace = go.Scatter(
        x=node_x, y=node_y,
        mode='markers+text',
        text=node_text,
        textposition="top center",
        hoverinfo='text',
        hovertext=hover_texts,
        marker=dict(
            size=[s/50 for s in node_size],
            color=node_size,
            colorscale='Viridis',
            line_width=2,
            line_color='white'))
    
    fig = go.Figure(data=[edge_trace, node_trace])
    fig.update_layout(
        showlegend=False,
        hovermode='closest',
        margin=dict(b=0, l=0, r=0, t=0),
        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        height=600,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)'
    )
    
    return fig


def create_temporal_evolution():
    """Create temporal evolution visualization"""
    fig = go.Figure()
    
    cluster_col = 'cluster_l0'
    clusters = sorted(df[cluster_col].dropna().unique(), key=lambda x: str(x))[:10]
    
    for cluster_id in clusters:
        cluster_df = df[df[cluster_col] == cluster_id]
        years = cluster_df.groupby('Year').size()
        
        fig.add_trace(go.Scatter(
            x=years.index,
            y=years.values,
            mode='lines+markers',
            name=f'Cluster {cluster_id}',
            line=dict(width=2),
            marker=dict(size=6)
        ))
    
    fig.update_layout(
        title="Research Stream Evolution Over Time",
        xaxis_title="Year",
        yaxis_title="Number of Papers",
        height=500,
        hovermode='x unified',
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='white',
        legend=dict(
            orientation="v",
            yanchor="top",
            y=1,
            xanchor="left",
            x=1.05
        )
    )
    
    return fig


def create_citation_distribution():
    """Create citation distribution by cluster"""
    cluster_col = 'cluster_l0'
    
    cluster_stats = []
    for cluster_id in sorted(df[cluster_col].dropna().unique(), key=lambda x: str(x)):
        cluster_df = df[df[cluster_col] == cluster_id]
        
        # Get cluster name
        cluster_name = f"C{cluster_id}"
        if cluster_names and 'level_0' in cluster_names:
            cluster_info = cluster_names['level_0'].get(str(cluster_id))
            if cluster_info:
                name = cluster_info.get('name', f'Cluster {cluster_id}')
                # Shorten name for chart
                cluster_name = name.split(' / ')[0] if ' / ' in name else name[:20]
        
        cluster_stats.append({
            'Cluster': cluster_name,
            'ID': str(cluster_id),
            'Mean Citations': cluster_df['citations_combined'].mean(),
            'Median Citations': cluster_df['citations_combined'].median(),
            'Total Citations': cluster_df['citations_combined'].sum(),
            'Papers': len(cluster_df)
        })
    
    stats_df = pd.DataFrame(cluster_stats)
    stats_df = stats_df.nlargest(15, 'Mean Citations')  # Show top 15 by impact
    
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        x=stats_df['Cluster'],
        y=stats_df['Mean Citations'],
        name='Mean Citations',
        marker_color='#667eea',
        hovertemplate='<b>%{x}</b><br>Mean: %{y:.1f} citations<extra></extra>'
    ))
    
    fig.update_layout(
        title="Top 15 Most Impactful Research Streams (by Mean Citations)",
        xaxis_title="Research Stream",
        yaxis_title="Mean Citations per Paper",
        height=400,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='white',
        xaxis={'tickangle': -45}
    )
    
    return fig


# Layout
app.layout = html.Div([
    # Header
    html.Div([
        html.H1("🔬 Research Stream Explorer"),
        html.P("Interactive Hierarchical Analysis of IS Research (8 AIS Basket Journals, 2025)")
    ], className='header'),
    
    # Overview Stats
    html.Div([
        html.Div([
            html.Div(f"{len(df):,}", className="stat-number"),
            html.Div("Total Papers", className="stat-label")
        ], className='stats-card', style={'flex': '1'}),
        html.Div([
            html.Div(f"{hierarchy.get('total_clusters', 0)}", className="stat-number"),
            html.Div("Total Clusters", className="stat-label")
        ], className='stats-card', style={'flex': '1'}),
        html.Div([
            html.Div(f"{len(df[df['keywords'].notna()]):,}", className="stat-number"),
            html.Div("With Keywords", className="stat-label")
        ], className='stats-card', style={'flex': '1'}),
        html.Div([
            html.Div(f"{df['Citations'].sum():,}", className="stat-number"),
            html.Div("Total Citations", className="stat-label")
        ], className='stats-card', style={'flex': '1'}),
    ], style={'display': 'flex', 'padding': '10px'}),
    
    # Main Content with Tabs
    dcc.Tabs(id='tabs', value='overview', children=[
        dcc.Tab(label='📊 Overview', value='overview', children=[
            html.Div([
                html.H2("Hierarchical Structure"),
                dcc.Graph(figure=create_sunburst(), id='sunburst-chart'),
                
                html.Div([
                    html.Div([
                        html.H3("Temporal Evolution"),
                        dcc.Graph(figure=create_temporal_evolution())
                    ], style={'flex': '1', 'padding': '10px'}),
                    html.Div([
                        html.H3("Citation Impact"),
                        dcc.Graph(figure=create_citation_distribution())
                    ], style={'flex': '1', 'padding': '10px'}),
                ], style={'display': 'flex'})
            ], className='tab-content')
        ]),
        
        dcc.Tab(label='🔍 Cluster Explorer', value='clusters', children=[
            html.Div([
                html.H2("Explore Clusters"),
                html.Div([
                    html.Label("Select Level:"),
                    dcc.Dropdown(
                        id='level-selector',
                        options=[{'label': f'Level {i}', 'value': i} for i in range(4)],
                        value=0,
                        style={'width': '200px', 'display': 'inline-block', 'margin': '10px'}
                    ),
                    html.Label("Select Cluster:"),
                    dcc.Dropdown(
                        id='cluster-selector',
                        style={'width': '200px', 'display': 'inline-block', 'margin': '10px'}
                    ),
                ]),
                html.Div(id='cluster-details')
            ], className='tab-content')
        ]),
        
        dcc.Tab(label='🏷️ Keywords', value='keywords', children=[
            html.Div([
                html.H2("Keyword Analysis"),
                html.P("Co-occurrence network of top keywords across the corpus"),
                dcc.Graph(figure=create_keyword_network(), id='keyword-network')
            ], className='tab-content')
        ]),
        
        dcc.Tab(label='📈 Statistics', value='stats', children=[
            html.Div([
                html.H2("Detailed Statistics"),
                html.Div(id='stats-content')
            ], className='tab-content')
        ]),
    ], style={'margin': '10px'})
], style={'maxWidth': '1400px', 'margin': '0 auto', 'padding': '20px'})


# Callbacks
@app.callback(
    Output('cluster-selector', 'options'),
    Output('cluster-selector', 'value'),
    Input('level-selector', 'value')
)
def update_cluster_options(level):
    cluster_col = f'cluster_l{level}'
    if cluster_col not in df.columns:
        return [], None
    
    clusters = sorted(df[cluster_col].dropna().unique(), key=lambda x: str(x))
    
    # Create options with meaningful names
    options = []
    for c in clusters:
        # Get meaningful cluster name
        cluster_name = f'Cluster {c}'
        if cluster_names and f'level_{level}' in cluster_names:
            cluster_info = cluster_names[f'level_{level}'].get(str(c))
            if cluster_info:
                name = cluster_info.get('name', f'Cluster {c}')
                # Shorten for dropdown
                if len(name) > 50:
                    name = name[:47] + '...'
                cluster_name = f'{c}: {name}'
        
        options.append({'label': cluster_name, 'value': str(c)})
    
    return options, str(clusters[0]) if clusters else None


@app.callback(
    Output('cluster-details', 'children'),
    Input('level-selector', 'value'),
    Input('cluster-selector', 'value')
)
def update_cluster_details(level, cluster_id):
    if cluster_id is None:
        return html.Div("Select a cluster to view details")
    
    return create_cluster_details_table(level, cluster_id)


@app.callback(
    Output('stats-content', 'children'),
    Input('tabs', 'value')
)
def update_stats(tab):
    if tab != 'stats':
        return html.Div()
    
    # Generate comprehensive stats with cluster names
    stats_content = []
    
    for level in range(hierarchy.get('max_depth', 0) + 1):
        cluster_col = f'cluster_l{level}'
        if cluster_col not in df.columns:
            continue
        
        sizes = df[cluster_col].value_counts()
        
        # Get top 10 clusters by size with meaningful names
        top_clusters = []
        for cluster_id in sizes.head(10).index:
            cluster_df = df[df[cluster_col] == cluster_id]
            
            # Get meaningful name
            cluster_name = f'Cluster {cluster_id}'
            if cluster_names and f'level_{level}' in cluster_names:
                cluster_info = cluster_names[f'level_{level}'].get(str(cluster_id))
                if cluster_info:
                    cluster_name = cluster_info.get('name', cluster_name)
            
            mean_cites = cluster_df['citations_combined'].mean()
            
            top_clusters.append(html.Div([
                html.Strong(f"{cluster_name}"),
                html.Span(f": {len(cluster_df)} papers, {mean_cites:.1f} mean citations",
                         style={'marginLeft': '10px', 'color': '#666'})
            ], style={'marginBottom': '8px'}))
        
        stats_content.append(html.Div([
            html.H3(f"Level {level} Statistics"),
            html.P(f"Number of clusters: {len(sizes)}"),
            html.P(f"Size range: {sizes.min()}-{sizes.max()} papers"),
            html.P(f"Mean size: {sizes.mean():.0f} papers"),
            html.P(f"Median size: {sizes.median():.0f} papers"),
            html.H4("Top 10 Largest Clusters:", style={'marginTop': '20px'}),
            html.Div(top_clusters),
            html.Hr()
        ]))
    
    return stats_content


if __name__ == '__main__':
    print("="*80)
    print("Starting Research Stream Explorer Dashboard...")
    print("="*80)
    print("\n📊 Loading data and initializing visualizations...")
    print(f"\n🌐 Dashboard will be available at: http://127.0.0.1:8050")
    print("\n💡 Press Ctrl+C to stop the server\n")
    print("="*80)
    
    app.run(debug=True, port=8050)
