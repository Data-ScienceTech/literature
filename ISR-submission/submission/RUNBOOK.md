# Reproduce Results & Generate Submission Artifacts

> Target journal: **Information Systems Research (INFORMS)**  
> Author & corresponding author: **Carlos Denner dos Santos** (carlosdenner@unb.br)

## Environment (choose one)

### Option A — requirements.txt
```bash
python -m venv .venv && source .venv/bin/activate  # on Windows: .venv\Scripts\activate
pip install -r submission/requirements.txt
```

### Option B — environment.yml
```bash
conda env create -f submission/environment.yml
conda activate isr-literature
```

## Exact steps

1. **Build/refresh corpus & citations** (adjust input/output paths to your repo layout):
```bash
python tools/make_corpus.py --source openalex --out data/corpus.parquet
python tools/build_citations.py --in data/corpus.parquet --out data/coupling.parquet
```
2. **Text features & hybrid embedding**:
```bash
python tools/text_features.py --in data/corpus.parquet --out artifacts/tfidf_lsi.pkl
python tools/hybrid.py --text artifacts/tfidf_lsi.pkl --net data/coupling.parquet --w 0.60 --out artifacts/hybrid.npy
```
3. **Cluster (L1/L2/L3) & validate**:
```bash
python tools/cluster_all.py --in artifacts/hybrid.npy --l1 8 --l2 48 --l3 200 --out artifacts/clusters.json --seed 42
python tools/validate.py --in artifacts/clusters.json --out artifacts/validation.json
```
4. **Export submission tables/appendices**:
```bash
python tools/make_table1.py --in artifacts/clusters.json --out submission/table1.csv
python tools/export_l2.py                      # writes submission/appendix_A_L2.md
python tools/export_sensitivity.py             # writes submission/appendix_B_sensitivity.md
```
5. **Complete references from in-text citations**:
```bash
python tools/build_bib.py                      # writes/updates submission/references.bib
```
6. **Render manuscript (Pandoc)**:
```bash
pandoc submission/manuscript.md   --from markdown+smart   --citeproc --bibliography=submission/references.bib   -o submission/manuscript.docx
pandoc submission/manuscript.md   --from markdown+smart   --citeproc --bibliography=submission/references.bib   -o submission/manuscript.pdf
```

## Hardware & timing (baseline)
Commodity laptop (≥4-core 3.0 GHz CPU, 32 GB RAM, SSD). Full pipeline typically completes in minutes for ~8–10k papers when the inverted-index optimization is enabled.
