# tools/export_l2.py

import pandas as pd, pathlib, sys

# Adjust input path to your artifact
IN = pathlib.Path("artifacts/level2_topics.csv")
OUT = pathlib.Path("submission/appendix_A_L2.md")

df = pd.read_csv(IN)
keep = [c for c in df.columns if c.lower() in {"stream","topic","label","keywords","n_papers"} or c.lower().startswith("topic")]
df = df[keep] if keep else df
df = df.sort_values(["stream","topic"]) if "stream" in df and "topic" in df else df
df.to_markdown(OUT, index=False)
print(f"Wrote {OUT}")
