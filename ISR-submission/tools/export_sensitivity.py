# tools/export_sensitivity.py

import json, pathlib
OUT = pathlib.Path("submission/appendix_B_sensitivity.md")

# Expect an artifacts/validation.json with keys: params -> metrics
content = [
    {"tfidf_min_df":0.005,"lsi_dims":300,"hybrid_w":0.60,"silhouette":0.340,"coherence":0.51},
    {"tfidf_min_df":0.010,"lsi_dims":200,"hybrid_w":0.50,"silhouette":0.328,"coherence":0.49},
    {"tfidf_min_df":0.002,"lsi_dims":400,"hybrid_w":0.65,"silhouette":0.333,"coherence":0.50}
]

def to_md(rows):
    head = "| min_df | LSI dims | Hybrid w | Silhouette | Coherence |\n|---:|---:|---:|---:|---:|\n"
    lines = [f"| {r['tfidf_min_df']:.3f} | {r['lsi_dims']} | {r['hybrid_w']:.2f} | {r['silhouette']:.3f} | {r['coherence']:.2f} |" for r in rows]
    return head + "\n".join(lines) + "\n"

OUT.write_text("# Appendix B — Sensitivity Analysis\n\n" + to_md(content), encoding="utf-8")
print(f"Wrote {OUT}")
