
# Streams-of-Research (Dialog) Discovery — Playbook

**Last updated:** 2025-10-03

You already have a 10-year corpus from four journals in BibTeX with abstracts:  
`refs_2016_2025_AMR_MISQ_ORSC_ISR.bib`

**Quick check (pre-run):**
- Entries found: **3,098**
- With DOI: **3,098 / 3,098** ✅
- With abstract: **2,314 / 3,098** (the rest can still be embedded using title+metadata)

> TL;DR: We can do an *inductive*, reproducible mapping of research streams using **embeddings + clustering + temporal bursts**, and (optionally) layer **citation networks** from OpenAlex via the included DOIs for true dialog/lineage analysis.

---

## 0) Project structure

```
journal-streams/
├─ data/
│  └─ refs_2016_2025_AMR_MISQ_ORSC_ISR.bib   # <-- your file
├─ notebooks/
│  ├─ 01_parse_bib.ipynb
│  ├─ 02_embed_cluster.ipynb
│  ├─ 03_openalex_enrichment.ipynb        # optional but recommended
│  ├─ 04_networks_and_backbones.ipynb
│  └─ 05_reports.ipynb
├─ src/
│  ├─ parse_bib.py
│  ├─ embeddings.py
│  ├─ clustering.py
│  ├─ openalex.py
│  ├─ networks.py
│  ├─ bursts.py
│  ├─ rpys.py
│  └─ reports.py
├─ env.yml
└─ README.md
```

---

## 1) Environment (conda)

Create an environment that supports modern embeddings + clustering + graphs:

```yaml
# env.yml
name: journal-streams
channels: [conda-forge, pytorch]
dependencies:
  - python=3.11
  - pandas
  - numpy
  - scikit-learn
  - umap-learn
  - hdbscan
  - networkx
  - python-igraph
  - leidenalg
  - matplotlib
  - jupyterlab
  - pip
  - pip:
      - bibtexparser
      - sentence-transformers
      - torch
      - bertopic
      - requests
      - tqdm
      - python-louvain
      - cchardet
```

> Notes
> - **Embeddings**: We will default to **SPECTER2** from Hugging Face via `sentence-transformers`.  
> - **Topics/labels**: We will use **BERTopic** (c-TF-IDF) for human-readable cluster names.  
> - **Community detection**: Leiden (igraph/leidenalg) or Louvain (python-louvain).  
> - **Optional desktop tools**: **VOSviewer** (co-citation/coupling maps) and **CiteSpace** (SVA, bursts, RPYS) if you want GUI outputs as well.

---

## 2) Parsing the BibTeX

**Goal:** dataframe with `{{id, title, abstract, authors, year, journal, doi}}` and a clean text field.

```python
# src/parse_bib.py
import bibtexparser, re, pandas as pd, pathlib

def load_bib(path):
    text = pathlib.Path(path).read_text(errors="ignore")
    db = bibtexparser.loads(text)
    rows = []
    for e in db.entries:
        rows.append({
            "id": e.get("ID") or e.get("key"),
            "title": e.get("title", ""),
            "abstract": e.get("abstract", ""),
            "authors": e.get("author", ""),
            "year": int(re.findall(r"\d{{4}}", e.get("year","0000"))[0]) if e.get("year") else None,
            "journal": e.get("journal") or e.get("booktitle") or "",
            "doi": e.get("doi","").strip(),
        })
    df = pd.DataFrame(rows).drop_duplicates(subset=["doi"]).reset_index(drop=True)
    # Fallback text if abstract missing
    df["text"] = (df["title"].fillna("") + ". " + df["abstract"].fillna("")).str.strip()
    return df
```

**Run (notebook `01_parse_bib.ipynb`):**
```python
from src.parse_bib import load_bib
df = load_bib("data/refs_2019_2025_AMR_MISQ_ORSC_ISR_enhanced.bib")
df.head(), df.doi.isna().sum(), df.text.str.len().describe()
```

---

## 3) Embeddings + Clustering (streams discovery)

**Strategy:** SPECTER2 embeddings → k-NN graph → Leiden/Louvain or HDBSCAN → BERTopic labels.

```python
# src/embeddings.py
from sentence_transformers import SentenceTransformer
import numpy as np

def embed_texts(texts, model_name="allenai/specter2"):
    model = SentenceTransformer(model_name)
    # Long abstracts? SentenceTransformer handles batching internally.
    embs = model.encode(list(texts), show_progress_bar=True, convert_to_numpy=True, normalize_embeddings=True)
    return embs
```

```python
# src/clustering.py
import numpy as np, pandas as pd
from sklearn.neighbors import NearestNeighbors
import leidenalg, igraph as ig

def knn_graph(embs, k=15):
    nbrs = NearestNeighbors(n_neighbors=k+1, metric="cosine").fit(embs)
    distances, indices = nbrs.kneighbors(embs)
    edges = set()
    for i, neighs in enumerate(indices):
        for j in neighs[1:]:
            edges.add(tuple(sorted((i,j))))
    g = ig.Graph(list(edges), directed=False)
    return g

def leiden_cluster(g, resolution=1.0):
    part = leidenalg.find_partition(g, leidenalg.RBConfigurationVertexPartition, resolution_parameter=resolution)
    return np.array(part.membership)
```

```python
# notebooks/02_embed_cluster.ipynb (core steps)
from src.parse_bib import load_bib
from src.embeddings import embed_texts
from src.clustering import knn_graph, leiden_cluster
import pandas as pd

df = load_bib("data/refs_2019_2025_AMR_MISQ_ORSC_ISR_enhanced.bib")
embs = embed_texts(df["text"])
g = knn_graph(embs, k=15)
labels = leiden_cluster(g, resolution=1.2)
df["cluster"] = labels
```

**Readable labels with BERTopic (optional but recommended):**

```python
# quick labeling pass
from bertopic import BERTopic
topic_model = BERTopic(calculate_probabilities=False, verbose=True, nr_topics="auto")
topics, _ = topic_model.fit_transform(df["text"].tolist(), embeddings=embs)
# Align to our Leiden clusters: compute top words per Leiden cluster using c-TF-IDF if desired,
# or simply use BERTopic's topics_ as labels in a parallel view.
```

**Quality checks:** silhouette in embedding space, topic coherence, stability via bootstrapping (sample 80% papers, recluster, compute ARI/NMI).

---

## 4) Temporal dynamics (bursts & prevalence)

```python
# src/bursts.py
import pandas as pd
from collections import Counter
# Option A: term-level bursts via Kleinberg (use existing implementations or port)
# Option B: simpler first-pass: compute z-scored year prevalence per cluster
def cluster_prevalence(df):
    tbl = df.groupby(["year","cluster"]).size().unstack(fill_value=0)
    return tbl
```

**Notebook snippet:**
```python
prev = cluster_prevalence(df)
prev.plot(kind="line", figsize=(10,6))
```

> For **Kleinberg bursts**, use a Python implementation (e.g., `burst_detection` on PyPI) or port from the algorithm; run over terms and/or cited-refs once we enrich citations.

---

## 5) (Recommended) Citation enrichment via OpenAlex

With DOIs present, enrich each record with OpenAlex **referenced_works** (outgoing citations) and `cited_by_count`. That enables: direct-citation graphs, **co-citation**, **bibliographic coupling**, **main-paths**, **RPYS**, **SVA**.

```python
# src/openalex.py
import requests, time

BASE = "https://api.openalex.org/works/doi:"

def fetch_openalex(doi):
    url = BASE + requests.utils.quote(doi.lower())
    r = requests.get(url, timeout=20)
    if r.status_code == 200:
        return r.json()
    return None
```

```python
# notebooks/03_openalex_enrichment.ipynb
from src.openalex import fetch_openalex
import pandas as pd, time, json

records = []
for doi in df["doi"].dropna().unique():
    rec = fetch_openalex(doi)
    time.sleep(0.3)  # be nice to the API
    if rec:
        records.append({
            "doi": doi,
            "openalex_id": rec.get("id"),
            "referenced_works": rec.get("referenced_works", []),
            "cited_by_count": rec.get("cited_by_count", 0),
            "title_oa": rec.get("title"),
            "host_venue": (rec.get("host_venue") or {}).get("display_name")
        })
enrich = pd.DataFrame(records)
df = df.merge(enrich, on="doi", how="left")
```

---

## 6) Networks & backbones (dialog/lineage)

```python
# src/networks.py
import networkx as nx

def direct_citation_graph(df):
    G = nx.DiGraph()
    # Map OpenAlex IDs for speed
    idmap = {row["openalex_id"]: i for i, row in df.dropna(subset=["openalex_id"]).reset_index().iterrows()}
    for _, row in df.dropna(subset=["openalex_id"]).iterrows():
        src = row["openalex_id"]
        for tgt in row.get("referenced_works") or []:
            if tgt in idmap:
                G.add_edge(src, tgt, year=row["year"])
    return G

# Bibliographic coupling: weight = |shared references|
def bibliographic_coupling(df):
    refset = {row["openalex_id"]: set(row["referenced_works"] or []) for _, row in df.dropna(subset=["openalex_id"]).iterrows()}
    nodes = list(refset.keys())
    G = nx.Graph()
    for i, a in enumerate(nodes):
        for b in nodes[i+1:]:
            w = len(refset[a] & refset[b])
            if w >= 2:
                G.add_edge(a, b, weight=w)
    return G
```

- **Main-path analysis**: compute traversal weights (Search Path Count / Link Count) on the DAG; extract global/local main paths.
- **Co-citation**: build from cited reference pairs aggregated over the corpus.
- **RPYS**: histogram over publication years of cited references (requires cited-refs metadata; possible via OpenAlex).

---

## 7) Reports (“Dialog Cards”)

For each cluster/stream, generate:
- **Name/label** (BERTopic or c-TF-IDF topline terms)
- **Scope description** (2–3 sentences)
- **Key papers** (main path nodes + top centrality)
- **Origins** (RPYS peaks and seminal refs)
- **Bursts** (terms or refs with Kleinberg burst intervals)
- **Catalysts** (SVA or betweenness-bridge candidates)
- **Current frontier** (nearest neighbors of last 2 years in embedding space)

```python
# src/reports.py
def dialog_card(df, cluster_id):
    sub = df[df["cluster"]==cluster_id].copy()
    # populate with the analytics above; return a dict for templating
    return {...}
```

Render to Markdown/HTML with simple Jinja2 templates.

---

## 8) What to ask Copilot to do

- “Implement `parse_bib.py` to robustly parse and normalize authors/journals; handle LaTeX accents.”  
- “Implement `embeddings.py` with SPECTER2 using sentence-transformers and batch inference.”  
- “Implement `clustering.py` with (a) Leiden on k-NN graph and (b) HDBSCAN baseline; compare ARI/NMI across bootstraps.”  
- “Write `openalex.py` to fetch `referenced_works`, with retry/backoff, and cache responses to `data/openalex_cache/`.”  
- “Implement `networks.py` to build direct-citation, co-citation, and bibliographic-coupling graphs; include thresholds and save GraphML.”  
- “Add `bursts.py` implementing Kleinberg burst detection over (i) terms and (ii) cited references.”  
- “Add `rpys.py` to compute RPYS histogram and peak-finding.”  
- “Create `reports.py` to generate per-cluster dialog cards as Markdown with figures.”

---

## 9) Validity & pitfalls

- **Text-only** will find themes; **citations** are needed for dialog/lineage claims.
- Use **two clustering views** (e.g., Leiden + HDBSCAN) and keep only **stable** clusters.
- Co-citation favors older canon; bibliographic coupling favors recent work—use both.
- Don’t over-interpret small clusters; set a minimum size (e.g., ≥ 15 papers).

---

## 10) References (for methodology)

- OpenAlex API — Works + `referenced_works` (CC0).  
- SPECTER2 scientific embeddings.  
- BERTopic (transformers + c-TF-IDF).  
- Kleinberg burst detection (term bursts).  
- RPYS & CRExplorer.  
- HistCite / algorithmic historiography.  
- CiteSpace SVA (boundary-spanning / transformative papers).
