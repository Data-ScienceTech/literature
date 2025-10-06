#!/usr/bin/env python3
"""
Multilevel Stream Extraction (Research Streams) from Scholarly Corpus

Inputs
------
- A Parquet file (recommended) with columns including at least: 'abstract'.
  Optional helpful columns: 'title', 'journal', 'year', 'doi', 'authors'.
- Alternatively, a CSV file with the same columns.

Outputs (written to --outdir)
-----------------------------
- doc_assignments.csv: one row per document with Level-1 cluster and Level-2 topic, + labels
- topics_level1.csv: topic id, size, top terms, auto-label
- topics_level2.csv: nested topic id (e.g., "3.2"), parent L1 id, size, top terms, auto-label
- summary.md: human-readable summary with counts and labels

Usage
-----
python stream_extractor.py --input /path/to/ais_basket_corpus_enriched.parquet --outdir ./streams_out
# (Optionally) to force CSV input:
python stream_extractor.py --input /path/to/corpus.csv --outdir ./streams_out

Notes
-----
- Requires sklearn and pandas. For Parquet input, install pyarrow OR fastparquet.
- The script will automatically choose the number of Level-1 clusters from a small candidate set via silhouette score,
  and 3-6 Level-2 subtopics per L1 using reconstruction error.
"""

import argparse
import math
import os
from pathlib import Path
import warnings
warnings.filterwarnings("ignore")

import numpy as np
import pandas as pd

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
# Helpers
# ------------------------------

def read_corpus(input_path: Path) -> pd.DataFrame:
    ext = input_path.suffix.lower()
    if ext == ".parquet":
        try:
            return pd.read_parquet(input_path)
        except Exception as e:
            raise RuntimeError("Failed to read Parquet. Install 'pyarrow' or 'fastparquet', "
                               "or convert to CSV.\nOriginal error: %r" % (e,))
    elif ext in [".csv", ".tsv"]:
        sep = "," if ext == ".csv" else "\t"
        return pd.read_csv(input_path, sep=sep)
    else:
        raise ValueError(f"Unsupported input extension: {ext}. Use .parquet, .csv, or .tsv")

def pick_text_column(df: pd.DataFrame) -> str:
    candidates = [c for c in df.columns if c.lower() in ["abstract","summary","text","content","body"]]
    if not candidates:
        # heuristic: longest average length
        textlike = df.select_dtypes(include=["object"]).columns.tolist()
        if not textlike:
            raise ValueError("No text-like columns found for abstracts.")
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

def fit_level1_clusters(X_lsi, candidate_ks=(6,8,10,12)):
    # Use Agglomerative with cosine metric (via pre-normalized LSI space & euclidean ≈ cosine)
    # Evaluate silhouette on KMeans in LSI for speed/robustness, then fit Agglomerative at best k
    best_k, best_score = None, -1
    for k in candidate_ks:
        km = KMeans(n_clusters=k, n_init=10, random_state=42)
        labs = km.fit_predict(X_lsi)
        try:
            sc = silhouette_score(X_lsi, labs, metric="euclidean")
        except Exception:
            sc = -1
        if sc > best_score:
            best_k, best_score = k, sc
    # Final Agglomerative at best_k
    agg = AgglomerativeClustering(n_clusters=best_k, metric="euclidean", linkage="ward")
    l1_labels = agg.fit_predict(X_lsi)
    return l1_labels, best_k, best_score

def choose_k_nmf(X_tfidf, ks=(3,4,5,6)):
    # Pick k minimizing reconstruction error; small preference for smaller k
    best_k, best_err = None, float("inf")
    best_model: NMF | None = None
    for k in ks:
        nmf = NMF(n_components=k, init="nndsvda", random_state=42, max_iter=400)
        W = nmf.fit_transform(X_tfidf)
        H = nmf.components_
        recon = W @ H
        # Frobenius norm of residual
        err = np.linalg.norm(X_tfidf.toarray() - recon) if hasattr(X_tfidf, 'toarray') else np.linalg.norm(X_tfidf - recon)
        # small penalty to avoid always picking largest k
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
# Main pipeline
# ------------------------------

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", required=True, help="Path to .parquet (preferred) or .csv/.tsv")
    ap.add_argument("--outdir", required=True, help="Output directory")
    ap.add_argument("--max_docs", type=int, default=None, help="Optional cap for faster prototyping")
    ap.add_argument("--l1_ks", type=str, default="6,8,10,12", help="Candidate ks for Level-1 (comma-separated)")
    ap.add_argument("--l2_ks", type=str, default="3,4,5,6", help="Candidate ks for Level-2 (comma-separated)")
    args = ap.parse_args()

    inp = Path(args.input)
    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)

    df = read_corpus(inp)
    text_col = pick_text_column(df)

    # Keep useful metadata if present
    meta_cols = [c for c in ["title","journal","year","doi","authors"] if c in df.columns]
    work = df[[text_col] + meta_cols].copy()
    work[text_col] = work[text_col].astype(str).map(basic_clean)
    work = work[work[text_col].str.len() > 20].reset_index(drop=True)

    if args.max_docs:
        work = work.iloc[:args.max_docs].copy()

    # TF-IDF vectorization
    tfidf = TfidfVectorizer(
        max_features=50000,
        min_df=5,
        max_df=0.8,
        ngram_range=(1,2),
        stop_words="english"
    )
    X = tfidf.fit_transform(work[text_col].values)
    feat_names = np.array(tfidf.get_feature_names_out())

    # LSI (SVD) for clustering space
    svd = TruncatedSVD(n_components=200, random_state=42)
    X_lsi = svd.fit_transform(X)
    X_lsi = normalize(X_lsi)  # cosine-friendly

    # Level-1 clusters
    cand_ks = tuple(int(x) for x in args.l1_ks.split(","))
    l1_labels, l1_k, l1_sil = fit_level1_clusters(X_lsi, candidate_ks=cand_ks)
    work["L1"] = l1_labels

    # Summarize Level-1 with NMF topics (optional labeling aid on whole corpus)
    # Label each L1 by NMF on its subset to get better descriptors
    l2_candidate_ks = tuple(int(x) for x in args.l2_ks.split(","))
    l1_rows = []
    l2_rows = []
    doc_L2 = np.full(len(work), fill_value=-1, dtype=int)
    doc_L2_label = np.array([""]*len(work), dtype=object)
    doc_L1_label = np.array([""]*len(work), dtype=object)

    for l1 in sorted(work["L1"].unique()):
        mask = work["L1"] == l1
        X_sub = X[mask.values]  # type: ignore[index] # sparse matrices support indexing - convert Series to numpy array
        if X_sub.shape[0] < 20:
            # too small; label by top corpus terms
            centroid = np.asarray(X_sub.mean(axis=0)).ravel()
            l1_label = auto_label_topic(feat_names, centroid, topn=8)
            l1_rows.append({"L1": l1, "size": int(mask.sum()), "label": l1_label, "top_terms": l1_label})
            doc_L1_label[mask.values] = l1_label
            continue

        # Choose k and fit NMF for Level-2 inside this L1
        k_best, nmf = choose_k_nmf(X_sub, ks=l2_candidate_ks)
        if nmf is None:
            continue
        W = nmf.transform(X_sub)
        H = nmf.components_
        terms = top_terms_per_topic(nmf, feat_names, topn=12)
        # Level-1 label as the union of top terms across its Level-2
        flat_terms = [t for lst in terms for t in lst[:4]]
        l1_label = ", ".join(sorted(set(flat_terms))[:10])

        l1_rows.append({"L1": l1, "size": int(mask.sum()), "label": l1_label, "top_terms": l1_label})

        # Assign L2 as argmax over W
        l2_local = W.argmax(axis=1)
        doc_L2[np.where(mask)[0]] = l2_local
        # Build per L2 topic rows
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
            # Write labels back to docs
            doc_L2_label[np.where(mask)[0][tmask]] = label
        # Assign L1 label to docs
        doc_L1_label[mask.values] = l1_label

    # Build doc assignment table
    out_docs = work.copy()
    out_docs["L2"] = doc_L2
    out_docs["L1_label"] = doc_L1_label
    out_docs["L2_label"] = doc_L2_label

    # Save outputs
    pd.DataFrame(l1_rows).sort_values("L1").to_csv(outdir / "topics_level1.csv", index=False)
    pd.DataFrame(l2_rows).sort_values(["L1","L2"]).to_csv(outdir / "topics_level2.csv", index=False)
    out_docs.to_csv(outdir / "doc_assignments.csv", index=False)

    # Summary markdown
    lines = []
    lines.append(f"# Stream Extraction Summary")
    lines.append("")
    lines.append(f"- Documents: {len(work)}")
    lines.append(f"- L1 clusters: {len(set(work['L1']))} (selected k={l1_k}, silhouette≈{l1_sil:.3f})")
    lines.append("")
    lines.append("## Level-1 Streams")
    l1_df = pd.DataFrame(l1_rows).sort_values("L1")
    for _, r in l1_df.iterrows():
        lines.append(f"- **L1 {int(r['L1'])}** (n={int(r['size'])}): {r['label']}")
    lines.append("")
    lines.append("## Level-2 Substreams (per L1)")
    l2_df = pd.DataFrame(l2_rows).sort_values(["L1","L2"])
    for l1_val, grp in l2_df.groupby("L1"):
        # Convert to Python int - handle numpy/pandas scalars safely
        try:
            l1_display = int(l1_val)  # type: ignore
        except (TypeError, ValueError):
            l1_display = l1_val
        lines.append(f"### L1 {l1_display}")
        for _, r in grp.iterrows():
            lines.append(f"  - **{int(r['L1'])}.{int(r['L2'])}** (n={int(r['size'])}): {r['label']}")
    (outdir / "summary.md").write_text("\n".join(lines), encoding="utf-8")

    print("Done. Outputs in:", outdir.resolve())

if __name__ == "__main__":
    main()
