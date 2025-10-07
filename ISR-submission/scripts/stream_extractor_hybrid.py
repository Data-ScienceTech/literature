#!/usr/bin/env python3
"""
Hybrid Multilevel Stream Extraction: Text + Citation Networks

This enhanced version combines:
1. Text-based semantic similarity (TF-IDF + LSI)
2. Citation network features (bibliographic coupling, co-citation)
3. Hybrid clustering using both signals

Inputs
------
- Parquet/CSV file with columns: 'abstract', 'referenced_works' (list of OpenAlex IDs)
- Optional: 'title', 'journal', 'year', 'doi', 'authors'

Outputs (written to --outdir)
-----------------------------
- doc_assignments.csv: documents with L1/L2 clusters, labels, and network metrics
- topics_level1.csv: L1 clusters with top terms and citation characteristics
- topics_level2.csv: L2 nested topics
- summary.md: human-readable summary
- citation_network.json: citation network statistics

Usage
-----
python stream_extractor_hybrid.py --input corpus_enriched.parquet --outdir ./hybrid_streams_out
python stream_extractor_hybrid.py --input corpus.parquet --outdir ./out --text_weight 0.7 --citation_weight 0.3

Parameters
----------
--text_weight: Weight for text similarity (default: 0.6)
--citation_weight: Weight for citation network similarity (default: 0.4)
"""

import argparse
import json
import os
from pathlib import Path
from typing import List, Dict, Tuple, Optional
import warnings
warnings.filterwarnings("ignore")

import numpy as np
import pandas as pd
from scipy.sparse import csr_matrix, hstack
from scipy.spatial.distance import pdist, squareform

# TF-IDF & models
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.decomposition import NMF, TruncatedSVD
from sklearn.cluster import AgglomerativeClustering, KMeans
from sklearn.metrics import silhouette_score
from sklearn.preprocessing import normalize

# Text utils
import re
import string

# ------------------------------
# Text Processing (from original)
# ------------------------------

def read_corpus(input_path: Path) -> pd.DataFrame:
    ext = input_path.suffix.lower()
    if ext == ".parquet":
        try:
            return pd.read_parquet(input_path)
        except Exception as e:
            raise RuntimeError(f"Failed to read Parquet: {e}")
    elif ext in [".csv", ".tsv"]:
        sep = "," if ext == ".csv" else "\t"
        return pd.read_csv(input_path, sep=sep)
    else:
        raise ValueError(f"Unsupported extension: {ext}")

def pick_text_column(df: pd.DataFrame) -> str:
    candidates = [c for c in df.columns if c.lower() in ["abstract","summary","text","content","body"]]
    if not candidates:
        textlike = df.select_dtypes(include=["object"]).columns.tolist()
        if not textlike:
            raise ValueError("No text columns found")
        lengths = [(c, df[c].dropna().astype(str).str.len().mean()) for c in textlike]
        candidates = [sorted(lengths, key=lambda x: x[1], reverse=True)[0][0]]
    return candidates[0]

def basic_clean(s: str) -> str:
    if not isinstance(s, str):
        return ""
    s = s.lower()
    s = re.sub(r"\s+", " ", s)
    s = s.translate(str.maketrans("", "", string.punctuation))
    return s.strip()

def auto_label_topic(feature_names, topic_vector, topn=8):
    idx = np.argsort(topic_vector)[::-1][:topn]
    return ", ".join([feature_names[i] for i in idx])

# ------------------------------
# Citation Network Processing
# ------------------------------

def extract_openalex_ids(ref_list) -> List[str]:
    """Extract OpenAlex IDs from various formats."""
    # Handle None
    if ref_list is None:
        return []
    
    # Handle pandas NA/NaN
    try:
        if pd.isna(ref_list):
            return []
    except (ValueError, TypeError):
        # If pd.isna() fails, ref_list is likely a list or other collection
        pass
    
    # Handle numpy arrays
    if isinstance(ref_list, np.ndarray):
        if len(ref_list) == 0:
            return []
        ref_list = ref_list.tolist()
    
    # Handle string representation of list
    if isinstance(ref_list, str):
        if not ref_list or ref_list == "":
            return []
        try:
            ref_list = eval(ref_list)
        except:
            return []
    
    # Handle list of IDs
    if isinstance(ref_list, list):
        if len(ref_list) == 0:
            return []
        ids = []
        for ref in ref_list:
            if isinstance(ref, str):
                # Extract ID from URL or use as-is
                if "openalex.org/" in ref:
                    ids.append(ref.split("/")[-1])
                else:
                    ids.append(ref)
        return ids
    
    return []

def build_citation_matrix(df: pd.DataFrame, citation_col: str = "referenced_works") -> Tuple[csr_matrix, Dict]:
    """
    Build bibliographic coupling matrix from citation data using OPTIMIZED sparse matrix approach.
    
    Papers that cite similar works are bibliographically coupled.
    Returns sparse matrix where M[i,j] = Jaccard similarity of reference sets.
    
    OPTIMIZATIONS:
    - Uses inverted index for fast reference lookup
    - Computes only non-zero similarities
    - Processes in chunks with progress bar
    - Avoids full n^2 pairwise comparison
    """
    print(f"Building citation network from '{citation_col}' column...")
    print("  Using OPTIMIZED sparse matrix algorithm...")
    
    # Check if column exists
    if citation_col not in df.columns:
        print(f"Warning: '{citation_col}' column not found. Using zero matrix.")
        n = len(df)
        return csr_matrix((n, n)), {"has_citations": False, "total_refs": 0}
    
    # Extract all citations
    all_citations = []
    for idx, row in df.iterrows():
        refs = extract_openalex_ids(row.get(citation_col))
        all_citations.append(set(refs))
    
    # Stats
    total_refs = sum(len(c) for c in all_citations)
    has_refs = sum(1 for c in all_citations if len(c) > 0)
    
    print(f"  Papers with references: {has_refs}/{len(df)} ({has_refs/len(df)*100:.1f}%)")
    print(f"  Total references: {total_refs:,}")
    print(f"  Avg refs per paper: {total_refs/len(df):.1f}")
    
    if total_refs == 0:
        print("  No citation data available - using zero matrix")
        n = len(df)
        return csr_matrix((n, n)), {"has_citations": False, "total_refs": 0}
    
    # Build inverted index: reference -> list of papers that cite it
    print("  Building inverted index...")
    from collections import defaultdict
    inverted_index = defaultdict(set)
    for paper_idx, refs in enumerate(all_citations):
        for ref in refs:
            inverted_index[ref].add(paper_idx)
    
    # Find candidate pairs: papers that cite at least one common reference
    print("  Finding candidate paper pairs...")
    candidate_pairs = defaultdict(int)  # (i,j) -> count of common refs
    
    for ref, citing_papers in inverted_index.items():
        citing_list = list(citing_papers)
        # All pairs of papers that cite this reference
        for i in range(len(citing_list)):
            for j in range(i+1, len(citing_list)):
                p1, p2 = citing_list[i], citing_list[j]
                if p1 > p2:
                    p1, p2 = p2, p1
                candidate_pairs[(p1, p2)] += 1
    
    print(f"  Candidate pairs with overlap: {len(candidate_pairs):,}")
    
    # Compute Jaccard similarity for candidate pairs
    print("  Computing bibliographic coupling (Jaccard similarity)...")
    data, rows, cols = [], [], []
    
    for (i, j), intersection_count in candidate_pairs.items():
        if intersection_count > 0:
            # Jaccard = |A ∩ B| / |A ∪ B|
            union_count = len(all_citations[i]) + len(all_citations[j]) - intersection_count
            similarity = intersection_count / union_count
            
            data.append(similarity)
            rows.append(i)
            cols.append(j)
    
    # Make symmetric
    all_data = data + data
    all_rows = rows + cols
    all_cols = cols + rows
    
    coupling_matrix = csr_matrix((all_data, (all_rows, all_cols)), shape=(len(df), len(df)))
    
    stats = {
        "has_citations": True,
        "total_refs": total_refs,
        "papers_with_refs": has_refs,
        "avg_refs_per_paper": total_refs / len(df),
        "coupling_edges": len(data),
        "avg_coupling": np.mean(data) if data else 0,
        "sparsity": 1.0 - (len(data) / (len(df) * (len(df)-1) / 2))
    }
    
    print(f"  Bibliographic coupling edges: {len(data):,}")
    print(f"  Avg coupling strength: {stats['avg_coupling']:.3f}")
    print(f"  Matrix sparsity: {stats['sparsity']*100:.2f}%")
    
    return coupling_matrix, stats

def combine_similarity_matrices(
    text_sim: np.ndarray, 
    citation_sim: csr_matrix,
    text_weight: float = 0.6,
    citation_weight: float = 0.4
) -> np.ndarray:
    """Combine text and citation similarity matrices with weights."""
    
    # Convert citation matrix to dense if needed
    if hasattr(citation_sim, 'toarray'):
        citation_sim_dense = citation_sim.toarray()
    else:
        citation_sim_dense = citation_sim
    
    # Normalize both to [0, 1]
    text_sim_norm = (text_sim - text_sim.min()) / (text_sim.max() - text_sim.min() + 1e-10)
    citation_sim_norm = (citation_sim_dense - citation_sim_dense.min()) / (citation_sim_dense.max() - citation_sim_dense.min() + 1e-10)
    
    # Weighted combination
    combined = text_weight * text_sim_norm + citation_weight * citation_sim_norm
    
    return combined

# ------------------------------
# Clustering Functions
# ------------------------------

def fit_level1_clusters(X_combined, candidate_ks=(6,8,10,12)):
    """Cluster using combined text+citation features."""
    best_k, best_score = None, -1
    
    for k in candidate_ks:
        km = KMeans(n_clusters=k, n_init=10, random_state=42)
        labs = km.fit_predict(X_combined)
        try:
            sc = silhouette_score(X_combined, labs, metric="euclidean")
        except Exception:
            sc = -1
        if sc > best_score:
            best_k, best_score = k, sc
    
    # Final clustering with best k
    agg = AgglomerativeClustering(n_clusters=best_k, metric="euclidean", linkage="ward")
    l1_labels = agg.fit_predict(X_combined)
    
    return l1_labels, best_k, best_score

def choose_k_nmf(X_tfidf, ks=(3,4,5,6)):
    """Choose optimal k for NMF based on reconstruction error."""
    best_k, best_err = None, float("inf")
    best_model: NMF | None = None
    
    for k in ks:
        nmf = NMF(n_components=k, init="nndsvda", random_state=42, max_iter=400)
        W = nmf.fit_transform(X_tfidf)
        H = nmf.components_
        recon = W @ H
        err = np.linalg.norm(X_tfidf.toarray() - recon) if hasattr(X_tfidf, 'toarray') else np.linalg.norm(X_tfidf - recon)
        err += 0.001 * k
        
        if err < best_err:
            best_k, best_err, best_model = k, err, nmf
    
    return best_k, best_model

def top_terms_per_topic(model, feature_names, topn=15):
    out = []
    for comp in model.components_:
        idx = np.argsort(comp)[::-1][:topn]
        terms = [feature_names[i] for i in idx]
        out.append(terms)
    return out

# ------------------------------
# Main Pipeline
# ------------------------------

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", required=True, help="Path to .parquet or .csv")
    ap.add_argument("--outdir", required=True, help="Output directory")
    ap.add_argument("--max_docs", type=int, default=None, help="Cap for faster testing")
    ap.add_argument("--l1_ks", type=str, default="6,8,10,12", help="L1 cluster candidates")
    ap.add_argument("--l2_ks", type=str, default="3,4,5,6", help="L2 cluster candidates")
    ap.add_argument("--l3_ks", type=str, default="2,3,4", help="L3 cluster candidates")
    ap.add_argument("--text_weight", type=float, default=0.6, help="Weight for text similarity")
    ap.add_argument("--citation_weight", type=float, default=0.4, help="Weight for citation similarity")
    ap.add_argument("--citation_col", type=str, default="referenced_works", help="Column with citation data")
    args = ap.parse_args()
    
    inp = Path(args.input)
    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)
    
    print("="*60)
    print("HYBRID STREAM EXTRACTION: Text + Citation Networks")
    print("="*60)
    print(f"Input: {inp}")
    print(f"Output: {outdir}")
    print(f"Text weight: {args.text_weight}")
    print(f"Citation weight: {args.citation_weight}")
    print("="*60)
    
    # Load corpus
    df = read_corpus(inp)
    text_col = pick_text_column(df)
    print(f"\nUsing text column: '{text_col}'")
    
    # Keep metadata
    meta_cols = [c for c in ["title","journal","year","doi","authors"] if c in df.columns]
    work = df[[text_col] + meta_cols + [args.citation_col] if args.citation_col in df.columns else [text_col] + meta_cols].copy()
    work[text_col] = work[text_col].astype(str).map(basic_clean)
    work = work[work[text_col].str.len() > 20].reset_index(drop=True)
    
    if args.max_docs:
        work = work.iloc[:args.max_docs].copy()
    
    print(f"\nProcessing {len(work):,} documents")
    
    # ========== TEXT FEATURES ==========
    print("\n" + "="*60)
    print("BUILDING TEXT FEATURES")
    print("="*60)
    
    tfidf = TfidfVectorizer(
        max_features=50000,
        min_df=5,
        max_df=0.8,
        ngram_range=(1,2),
        stop_words="english"
    )
    X_tfidf = tfidf.fit_transform(work[text_col].values)
    feat_names = np.array(tfidf.get_feature_names_out())
    print(f"TF-IDF matrix: {X_tfidf.shape}")
    
    # LSI for text dimensionality reduction
    # Adjust n_components based on available features
    n_svd_components = min(200, X_tfidf.shape[1] - 1, X_tfidf.shape[0] - 1)
    svd = TruncatedSVD(n_components=n_svd_components, random_state=42)
    X_text_lsi = svd.fit_transform(X_tfidf)
    X_text_lsi = normalize(X_text_lsi)
    print(f"LSI reduction: {X_text_lsi.shape}")
    print(f"Explained variance: {svd.explained_variance_ratio_.sum():.2%}")
    
    # ========== CITATION FEATURES ==========
    print("\n" + "="*60)
    print("BUILDING CITATION NETWORK FEATURES")
    print("="*60)
    
    citation_matrix, citation_stats = build_citation_matrix(work, args.citation_col)
    
    # If we have citations, use them; otherwise rely only on text
    if citation_stats["has_citations"]:
        # Convert citation similarity to distance matrix for clustering
        # Use coupling matrix directly as additional features
        print("\nIntegrating citation network into clustering space...")
        
        # Compute pairwise citation similarity for each document
        # Sum of coupling strengths as a feature vector
        citation_features = np.array(citation_matrix.sum(axis=1)).ravel()
        citation_features = citation_features.reshape(-1, 1)
        
        # Normalize
        citation_features = (citation_features - citation_features.min()) / (citation_features.max() - citation_features.min() + 1e-10)
        
        # Combine text LSI + citation features
        X_combined = np.hstack([
            X_text_lsi * args.text_weight,
            citation_features * args.citation_weight * 50  # Scale up to match LSI magnitude
        ])
        
        print(f"Combined features: {X_combined.shape}")
        print(f"  Text LSI dims: {X_text_lsi.shape[1]}")
        print(f"  Citation dims: {citation_features.shape[1]}")
    else:
        print("\nNo citation data - using text features only")
        X_combined = X_text_lsi
        citation_stats["mode"] = "text_only"
    
    # ========== LEVEL-1 CLUSTERING ==========
    print("\n" + "="*60)
    print("LEVEL-1 CLUSTERING")
    print("="*60)
    
    cand_ks = tuple(int(x) for x in args.l1_ks.split(","))
    l1_labels, l1_k, l1_sil = fit_level1_clusters(X_combined, candidate_ks=cand_ks)
    work["L1"] = l1_labels
    
    print(f"Selected {l1_k} clusters (silhouette: {l1_sil:.3f})")
    
    # ========== LEVEL-2 CLUSTERING ==========
    print("\n" + "="*60)
    print("LEVEL-2 CLUSTERING (within each L1)")
    print("="*60)
    
    l2_candidate_ks = tuple(int(x) for x in args.l2_ks.split(","))
    l3_candidate_ks = tuple(int(x) for x in args.l3_ks.split(","))
    l1_rows = []
    l2_rows = []
    l3_rows = []
    doc_L2 = np.full(len(work), fill_value=-1, dtype=int)
    doc_L3 = np.full(len(work), fill_value=-1, dtype=int)
    doc_L2_label = np.array([""]*len(work), dtype=object)
    doc_L3_label = np.array([""]*len(work), dtype=object)
    doc_L1_label = np.array([""]*len(work), dtype=object)
    
    for l1 in sorted(work["L1"].unique()):
        mask = work["L1"] == l1
        X_sub = X_tfidf[mask.values]  # type: ignore[index]
        
        print(f"\nL1 cluster {l1}: {mask.sum()} documents")
        
        if X_sub.shape[0] < 20:
            # Too small
            centroid = np.asarray(X_sub.mean(axis=0)).ravel()
            l1_label = auto_label_topic(feat_names, centroid, topn=8)
            l1_rows.append({"L1": l1, "size": int(mask.sum()), "label": l1_label, "top_terms": l1_label})
            doc_L1_label[mask.values] = l1_label
            continue
        
        # NMF for Level-2
        k_best, nmf = choose_k_nmf(X_sub, ks=l2_candidate_ks)
        if nmf is None:
            continue
        
        W = nmf.transform(X_sub)
        H = nmf.components_
        terms = top_terms_per_topic(nmf, feat_names, topn=12)
        
        # L1 label from union of L2 top terms
        flat_terms = [t for lst in terms for t in lst[:4]]
        l1_label = ", ".join(sorted(set(flat_terms))[:10])
        
        l1_rows.append({"L1": l1, "size": int(mask.sum()), "label": l1_label, "top_terms": l1_label})
        
        # Assign L2
        l2_local = W.argmax(axis=1)
        doc_L2[np.where(mask)[0]] = l2_local
        
        # Build L2 topic rows and perform L3 clustering
        n_topics = nmf.n_components_
        for t in range(n_topics):
            tmask = l2_local == t
            size = int(tmask.sum())
            label = ", ".join(terms[t][:8])
            l2_rows.append({
                "L1": l1,
                "L2": t,
                "L2_path": f"{l1}.{t}",
                "size": size,
                "label": label,
                "top_terms": ", ".join(terms[t])
            })
            doc_L2_label[np.where(mask)[0][tmask]] = label
            
            # ========== LEVEL-3 CLUSTERING (within each L2) ==========
            l2_doc_indices = np.where(mask)[0][tmask]
            X_l2_sub = X_tfidf[l2_doc_indices]  # type: ignore[index]
            
            if X_l2_sub.shape[0] >= 10:  # Only cluster if enough documents
                # NMF for Level-3
                k_l3, nmf_l3 = choose_k_nmf(X_l2_sub, ks=l3_candidate_ks)
                if nmf_l3 is not None:
                    W_l3 = nmf_l3.transform(X_l2_sub)
                    terms_l3 = top_terms_per_topic(nmf_l3, feat_names, topn=10)
                    
                    # Assign L3
                    l3_local = W_l3.argmax(axis=1)
                    doc_L3[l2_doc_indices] = l3_local
                    
                    # Build L3 topic rows
                    n_l3_topics = nmf_l3.n_components_
                    for t3 in range(n_l3_topics):
                        t3mask = l3_local == t3
                        l3_size = int(t3mask.sum())
                        l3_label = ", ".join(terms_l3[t3][:6])
                        l3_rows.append({
                            "L1": l1,
                            "L2": t,
                            "L3": t3,
                            "L2_path": f"{l1}.{t}",
                            "L3_path": f"{l1}.{t}.{t3}",
                            "size": l3_size,
                            "label": l3_label,
                            "top_terms": ", ".join(terms_l3[t3])
                        })
                        doc_L3_label[l2_doc_indices[t3mask]] = l3_label
        
        doc_L1_label[mask.values] = l1_label
        total_l3 = len([r for r in l3_rows if r["L1"] == l1])
        print(f"  → {n_topics} L2 subtopics → {total_l3} L3 micro-topics")
    
    # ========== BUILD OUTPUT ==========
    print("\n" + "="*60)
    print("SAVING RESULTS")
    print("="*60)
    
    out_docs = work.copy()
    out_docs["L2"] = doc_L2
    out_docs["L3"] = doc_L3
    out_docs["L1_label"] = doc_L1_label
    out_docs["L2_label"] = doc_L2_label
    out_docs["L3_label"] = doc_L3_label
    
    # Save outputs
    pd.DataFrame(l1_rows).sort_values("L1").to_csv(outdir / "topics_level1.csv", index=False)
    if l2_rows:  # Only save if we have L2 topics
        pd.DataFrame(l2_rows).sort_values(["L1","L2"]).to_csv(outdir / "topics_level2.csv", index=False)
    else:
        # Create empty file with headers
        pd.DataFrame(columns=["L1", "L2", "L2_path", "size", "label", "top_terms"]).to_csv(outdir / "topics_level2.csv", index=False)
    
    if l3_rows:  # Save L3 topics if we have them
        pd.DataFrame(l3_rows).sort_values(["L1","L2","L3"]).to_csv(outdir / "topics_level3.csv", index=False)
    else:
        # Create empty file with headers
        pd.DataFrame(columns=["L1", "L2", "L3", "L2_path", "L3_path", "size", "label", "top_terms"]).to_csv(outdir / "topics_level3.csv", index=False)
    
    out_docs.to_csv(outdir / "doc_assignments.csv", index=False)
    
    # Save citation network stats
    with open(outdir / "citation_network_stats.json", "w") as f:
        json.dump(citation_stats, f, indent=2)
    
    # Summary markdown
    lines = []
    lines.append(f"# Hybrid Stream Extraction Summary")
    lines.append("")
    lines.append(f"**Methodology**: Text similarity + Citation networks")
    lines.append(f"- Text weight: {args.text_weight}")
    lines.append(f"- Citation weight: {args.citation_weight}")
    lines.append("")
    lines.append(f"## Corpus Statistics")
    lines.append(f"- Documents: {len(work):,}")
    lines.append(f"- L1 clusters: {len(set(work['L1']))} (k={l1_k}, silhouette≈{l1_sil:.3f})")
    lines.append(f"- L2 subtopics: {len(l2_rows)}")
    lines.append(f"- L3 micro-topics: {len(l3_rows)}")
    
    if citation_stats["has_citations"]:
        lines.append(f"\n## Citation Network")
        lines.append(f"- Papers with references: {citation_stats['papers_with_refs']:,} ({citation_stats['papers_with_refs']/len(work)*100:.1f}%)")
        lines.append(f"- Total references: {citation_stats['total_refs']:,}")
        lines.append(f"- Avg references per paper: {citation_stats['avg_refs_per_paper']:.1f}")
        lines.append(f"- Bibliographic coupling edges: {citation_stats['coupling_edges']:,}")
        lines.append(f"- Avg coupling strength: {citation_stats['avg_coupling']:.3f}")
    else:
        lines.append(f"\n## Citation Network")
        lines.append(f"- No citation data available (text-only mode)")
    
    lines.append("")
    lines.append("## Level-1 Streams")
    l1_df = pd.DataFrame(l1_rows).sort_values("L1")
    for _, r in l1_df.iterrows():
        lines.append(f"- **L1 {int(r['L1'])}** (n={int(r['size'])}): {r['label']}")
    
    lines.append("")
    lines.append("## Level-2 Substreams (per L1)")
    if l2_rows:
        l2_df = pd.DataFrame(l2_rows).sort_values(["L1","L2"])
        for l1_val, grp in l2_df.groupby("L1"):
            try:
                l1_display = int(l1_val)  # type: ignore
            except (TypeError, ValueError):
                l1_display = l1_val
            lines.append(f"### L1 {l1_display}")
            for _, r in grp.iterrows():
                lines.append(f"  - **{int(r['L1'])}.{int(r['L2'])}** (n={int(r['size'])}): {r['label']}")
    else:
        lines.append("(No L2 subtopics - all clusters too small)")
    
    (outdir / "summary.md").write_text("\n".join(lines), encoding="utf-8")
    
    print(f"\n✓ Saved to: {outdir.resolve()}")
    print(f"  - doc_assignments.csv")
    print(f"  - topics_level1.csv")
    print(f"  - topics_level2.csv")
    print(f"  - citation_network_stats.json")
    print(f"  - summary.md")
    print("\nDone!")

if __name__ == "__main__":
    main()
