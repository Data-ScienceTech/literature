import pandas as pd

# Load the IS corpus
corpus = pd.read_parquet("data/clean/is_corpus_all.parquet")

print("="*70)
print("IS CORPUS SUMMARY")
print("="*70)
print(f"Total papers: {len(corpus):,}")
print(f"Date range: {corpus['year'].min()} - {corpus['year'].max()}")
print(f"\nPapers by journal:")
print(corpus['journal'].value_counts().to_string())
print(f"\nColumns available: {', '.join(corpus.columns)}")
print(f"\nWith abstracts: {corpus['abstract'].notna().sum():,} ({corpus['abstract'].notna().sum()/len(corpus)*100:.1f}%)")
print("="*70)
