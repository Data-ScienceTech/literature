# tools/build_bib.py

import re, pathlib
from collections import OrderedDict
from habanero import Crossref
import bibtexparser

MANUSCRIPT = pathlib.Path("submission/manuscript.md")  # adjust if needed
BIB_OUT = pathlib.Path("submission/references.bib")

text = MANUSCRIPT.read_text(encoding="utf-8")

# simple (Author, YEAR) extraction
candidates = set(re.findall(r"\(([A-Z][A-Za-z\-\s]+?)[^)]*?,\s*(\d{4})\)", text))

cr = Crossref()
entries = OrderedDict()

def add_entry(item):
    doi = item.get("DOI") or item.get("URL")
    if not doi: 
        return
    year = item.get("issued",{}).get("date-parts",[[None]])[0][0]
    fam = item.get("author",[{"family":"Anon"}])[0].get("family","Anon")
    key = (fam + str(year)).lower()
    if key in entries:
        return
    typ = item.get("type","article-journal")
    title = item.get("title",[None])[0]
    container = item.get("container-title",[None])[0]
    volume = item.get("volume"); issue = item.get("issue"); page = item.get("page")
    entries[key] = {
        "ENTRYTYPE": "article" if "journal" in typ else "misc",
        "ID": key,
        "title": title or "",
        "author": " and ".join([f"{au.get('family','')} {au.get('given','')}" for au in item.get("author",[])]),
        "year": str(year) if year else "",
        "journal": container or "",
        "volume": volume or "",
        "number": issue or "",
        "pages": page or "",
        "doi": item.get("DOI") or "",
        "url": item.get("URL") or ""
    }

for a,y in candidates:
    try:
        res = cr.works(query_author=a.strip(), filter={"from-pub-date":f"{y}-01-01","until-pub-date":f"{y}-12-31"}, limit=5)
        items = res.get("message",{}).get("items",[])
        for it in items:
            add_entry(it)
    except Exception:
        continue

db = bibtexparser.bibdatabase.BibDatabase()
db.entries = list(entries.values())
with open(BIB_OUT, "w", encoding="utf-8") as f:
    f.write(bibtexparser.dumps(db))
print(f"Wrote {len(entries)} entries to {BIB_OUT}")
