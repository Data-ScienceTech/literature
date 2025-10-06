"""Show top clusters from the hierarchy"""
import json
from pathlib import Path

# Load hierarchy
with open('data/hierarchy_leiden.json') as f:
    hierarchy = json.load(f)

print("\n" + "="*80)
print("🌳 HIERARCHICAL CLUSTER STRUCTURE")
print("="*80)

# Get root nodes
root_nodes = hierarchy.get('root_nodes', [])
print(f"\nMax depth: {hierarchy.get('max_depth', 0)} levels")
print(f"Total clusters: {hierarchy.get('total_clusters', 0)}")
print(f"Level sizes: {hierarchy.get('level_sizes', {})}")

print(f"\n📊 Root level (Level 0): {len(root_nodes)} clusters")
print("-"*80)

for i, node in enumerate(root_nodes[:10]):  # Show first 10
    cluster_id = node.get('id', f'cluster_{i}')
    size = node.get('size', 0)
    print(f"\n{i+1}. Cluster {cluster_id}")
    print(f"   Size: {size} papers")
    
    # Show metadata if available
    metadata = node.get('metadata', {})
    if 'top_terms' in metadata and metadata['top_terms']:
        terms = ', '.join(metadata['top_terms'][:10])
        print(f"   Top terms: {terms}")
    
    if 'temporal' in metadata:
        temp = metadata['temporal']
        print(f"   Years: {temp.get('year_range', ['?', '?'])[0]}-{temp.get('year_range', ['?', '?'])[1]}")
    
    # Show children count
    children = node.get('children', [])
    if children:
        print(f"   Sub-clusters: {len(children)}")
        # Show first few child sizes
        child_sizes = [c.get('size', 0) for c in children[:3]]
        if child_sizes:
            print(f"   Largest sub-clusters: {', '.join(map(str, child_sizes))} papers")

print("\n" + "="*80)
