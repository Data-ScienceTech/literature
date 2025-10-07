import pandas as pd

df = pd.read_csv('../outputs/clustering_results/doc_assignments.csv')

print('Year distribution (earliest years):')
print(df['year'].value_counts().sort_index().head(30))

print(f'\nTotal papers before 1990: {len(df[df["year"] < 1990])}')
print(f'Total papers 1990+: {len(df[df["year"] >= 1990])}')
print(f'Percentage before 1990: {len(df[df["year"] < 1990])/len(df)*100:.1f}%')

print('\nPapers by decade:')
df['decade'] = (df['year'] // 10) * 10
print(df['decade'].value_counts().sort_index())
