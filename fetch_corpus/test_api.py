import requests
import os

os.environ["OPENALEX_MAILTO"] = "carlosdenner@gmail.com"

url = "https://api.openalex.org/works"
params = {
    "filter": "primary_location.source.id:S11479521",
    "per-page": 200,
    "cursor": "*",
    "mailto": "carlosdenner@gmail.com",
    "select": "id,doi,title,display_name,publication_year,authorships,primary_location,host_venue,abstract_inverted_index,referenced_works,cited_by_count,language,type",
    "sort": "publication_year:asc"
}

print("Testing full API request...")
r = requests.get(url, params=params, timeout=30)
print(f"Status: {r.status_code}")
if r.status_code == 200:
    data = r.json()
    print(f"Total works: {data.get('meta', {}).get('count', 0)}")
    print(f"Results in this page: {len(data.get('results', []))}")
    print("✅ SUCCESS!")
else:
    print(f"Error: {r.text[:300]}")
