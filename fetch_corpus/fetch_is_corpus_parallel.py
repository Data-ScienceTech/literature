#!/usr/bin/env python3
"""
Fetch the 'whole IS field' (proxy = AIS Senior Scholars' Premier Journals, ~11 titles)
from OpenAlex, all available years, with abstracts & citation links.

PARALLEL VERSION - Fetches multiple journals simultaneously for 3-5x speedup!

Outputs:
  data/raw/openalex_cache/*.jsonl   # per-journal raw API dump (paged)
  data/clean/journal_*.parquet      # tidy per-journal tables
  data/clean/is_corpus_all.parquet  # concatenated corpus across all journals

Requires: Python 3.11+, requests, pandas, pyarrow, tqdm
"""

import os, sys, time, json, pathlib, re
from typing import Dict, List, Optional
from concurrent.futures import ThreadPoolExecutor, as_completed
import requests
import pandas as pd
from tqdm import tqdm

# ---------------------------
# Configuration
# ---------------------------

# AIS Senior Scholars' Premier Journals (11). Source list mirrored in Wikipedia/AIS comms:
# DSS; EJIS; Information & Management; Information and Organization;
# Information Systems Journal; Information Systems Research; Journal of the AIS;
# Journal of Information Technology; Journal of Management Information Systems;
# Journal of Strategic Information Systems; MIS Quarterly.
AIS_11_JOURNALS = [
    "Decision Support Systems",
    "European Journal of Information Systems",
    "Information & Management",
    "Information and Organization",
    "Information Systems Journal",
    "Information Systems Research",
    "Journal of the Association for Information Systems",
    "Journal of Information Technology",
    "Journal of Management Information Systems",
    "Journal of Strategic Information Systems",
    "MIS Quarterly",
]

OPENALEX_BASE = "https://api.openalex.org"
TIMEOUT = 30
RETRY = 5
SLEEP = 1.0          # Keep it polite even with email & parallel
PAGE_SIZE = 200      # OpenAlex max per page is currently 200
MAX_WORKERS = 2      # Parallel journal fetches (reduced to avoid rate limits)
DATA_DIR = pathlib.Path("data")
CACHE_DIR = DATA_DIR / "raw" / "openalex_cache"
CLEAN_DIR = DATA_DIR / "clean"
for p in (CACHE_DIR, CLEAN_DIR):
    p.mkdir(parents=True, exist_ok=True)

# Optional: put your email so OpenAlex can contact you if needed
# (recommended best practice per their docs).
OPENALEX_MAILTO = os.environ.get("OPENALEX_MAILTO", "")

# ---------------------------
# Helpers
# ---------------------------

def _session() -> requests.Session:
    s = requests.Session()
    s.headers.update({"User-Agent": "is-field-fetcher-parallel/1.0"})
    return s

def _get(url: str, params: dict) -> requests.Response:
    if OPENALEX_MAILTO:
        params = {**params, "mailto": OPENALEX_MAILTO}
    for attempt in range(1, RETRY + 1):
        try:
            r = _session().get(url, params=params, timeout=TIMEOUT)
            if r.status_code == 200:
                return r
            # backoff on 429/403/5xx
            if r.status_code in (403, 429, 500, 502, 503, 504):
                wait_time = min(60, attempt * 5)
                print(f"[WARN] Got {r.status_code}, waiting {wait_time}s before retry {attempt}/{RETRY}")
                time.sleep(wait_time)
            else:
                r.raise_for_status()
        except requests.RequestException as e:
            wait_time = min(60, attempt * 5)
            print(f"[WARN] Request exception: {e}, waiting {wait_time}s before retry {attempt}/{RETRY}")
            time.sleep(wait_time)
    raise RuntimeError(f"Failed GET after {RETRY} attempts: {url} {params}")

def resolve_source_id_by_name(journal_name: str) -> Optional[str]:
    """
    Resolve OpenAlex Source ID for a given journal name.
    Uses /sources?search=... and picks the best exact (case-insensitive) match of type=journal.
    """
    url = f"{OPENALEX_BASE}/sources"
    params = {
        "search": journal_name,
        "filter": "type:journal,has_issn:true",
        "per-page": 25,
    }
    r = _get(url, params)
    data = r.json()
    results = data.get("results", [])
    # Try exact match on display_name (case-insensitive)
    for src in results:
        if (src.get("display_name") or "").lower().strip() == journal_name.lower().strip():
            return src.get("id")
    # Fallback: startswith/contains heuristic
    for src in results:
        dn = (src.get("display_name") or "").lower()
        if journal_name.lower() in dn:
            return src.get("id")
    return None

def reconstruct_abstract_from_inverted_index(inv: dict) -> Optional[str]:
    """OpenAlex returns abstracts as an inverted index dict {token: [positions...]}. Rebuild text."""
    if not inv:
        return None
    max_pos = 0
    for positions in inv.values():
        if positions:
            max_pos = max(max_pos, max(positions))
    tokens = [""] * (max_pos + 1)
    for token, positions in inv.items():
        for p in positions:
            if 0 <= p < len(tokens):
                tokens[p] = token
    # join and clean spacing
    txt = " ".join(tokens)
    txt = re.sub(r"\s+", " ", txt).strip()
    return txt or None

def fetch_all_works_for_source(source_id: str, journal_name: str, outfile: pathlib.Path) -> int:
    """
    Page through /works filtered by primary_location.source.id == source_id
    Store raw JSONL for reproducibility.
    Returns the number of works fetched.
    """
    url = f"{OPENALEX_BASE}/works"
    cursor = "*"
    total = None
    count = 0
    # Extract just the ID code from the full URL (e.g., S11479521 from https://openalex.org/S11479521)
    source_code = source_id.split('/')[-1] if '/' in source_id else source_id
    
    with outfile.open("w", encoding="utf-8") as f:
        pbar = None
        while True:
            params = {
                "filter": f"primary_location.source.id:{source_code}",
                "per-page": PAGE_SIZE,
                "cursor": cursor,
                "select": ",".join([
                    "id", "doi", "title", "display_name", "publication_year",
                    "authorships", "primary_location",
                    "abstract_inverted_index", "referenced_works", "cited_by_count",
                    "language", "type"
                ]),
                "sort": "publication_year:asc"
            }
            r = _get(url, params)
            data = r.json()
            if total is None:
                total = data.get("meta", {}).get("count", 0)
                pbar = tqdm(total=total, desc=f"{journal_name[:30]:30}", unit="w", position=None, leave=True)
            results = data.get("results", [])
            for rec in results:
                f.write(json.dumps(rec, ensure_ascii=False) + "\n")
                count += 1
                if pbar: pbar.update(1)
            cursor = data.get("meta", {}).get("next_cursor")
            if not cursor:
                if pbar: pbar.close()
                break
            time.sleep(SLEEP)
    
    return count

def load_jsonl(path: pathlib.Path) -> List[dict]:
    rows = []
    if not path.exists():
        return rows
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                rows.append(json.loads(line))
    return rows

def normalize_records(raw: List[dict], source_display_name: str) -> pd.DataFrame:
    """Flatten OpenAlex works into a tidy table."""
    def get_doi(x):
        doi = x.get("doi")
        if isinstance(doi, str) and doi.lower().startswith("https://doi.org/"):
            return doi[16:]
        return doi

    def authors(x):
        out = []
        for a in (x.get("authorships") or []):
            author = (a.get("author") or {}).get("display_name")
            insts = [ (i.get("institution") or {}).get("display_name") for i in (a.get("institutions") or []) ]
            out.append({"author": author, "institutions": [i for i in insts if i]})
        return out

    recs = []
    for x in raw:
        abstract = reconstruct_abstract_from_inverted_index(x.get("abstract_inverted_index"))
        recs.append({
            "openalex_id": x.get("id"),
            "doi": get_doi(x),
            "title": x.get("display_name") or x.get("title"),
            "year": x.get("publication_year"),
            "language": x.get("language"),
            "type": x.get("type"),
            "journal": source_display_name,
            "host_venue": (x.get("host_venue") or {}).get("display_name"),
            "referenced_works": x.get("referenced_works") or [],
            "cited_by_count": x.get("cited_by_count") or 0,
            "authors": authors(x),
            "abstract": abstract,
        })
    df = pd.DataFrame.from_records(recs)
    # clean
    df["year"] = pd.to_numeric(df["year"], errors="coerce").astype("Int64")
    df = df.drop_duplicates(subset=["openalex_id"]).reset_index(drop=True)
    return df

def process_journal(jname: str, sid: str) -> Optional[pd.DataFrame]:
    """Fetch and process a single journal. Returns DataFrame or None if failed."""
    try:
        cache_file = CACHE_DIR / f"{jname.replace(' ', '_')}.jsonl"
        
        # Fetch if not cached
        if not cache_file.exists():
            count = fetch_all_works_for_source(sid, jname, cache_file)
            if count == 0:
                print(f"[WARN] No records for {jname}")
                return None
        
        # Load and normalize
        raw = load_jsonl(cache_file)
        if not raw:
            print(f"[WARN] No records in cache for {jname}")
            return None
        
        df = normalize_records(raw, jname)
        
        # Write per-journal parquet
        out_parquet = CLEAN_DIR / f"journal_{jname.replace(' ', '_')}.parquet"
        df.to_parquet(out_parquet, index=False)
        print(f"[SAVE] {jname}: {len(df):,} rows -> {out_parquet.name}")
        
        return df
    except Exception as e:
        print(f"[ERROR] Failed to process {jname}: {e}")
        return None

# ---------------------------
# Main
# ---------------------------

def main():
    if not OPENALEX_MAILTO:
        print("[WARN] No OPENALEX_MAILTO set! You may hit rate limits.")
        print("[WARN] Set the environment variable with your email for polite pool access.")
        print()
    
    # 1) Resolve Source IDs for the 11 journals
    print("Resolving OpenAlex Source IDs…")
    name_to_source: Dict[str, str] = {}
    for j in AIS_11_JOURNALS:
        sid = resolve_source_id_by_name(j)
        if not sid:
            print(f"[WARN] Could not resolve Source ID for: {j}")
        else:
            name_to_source[j] = sid
            print(f"[OK] {j} -> {sid}")

    if not name_to_source:
        print("No journals resolved. Exiting.")
        sys.exit(1)

    print(f"\n🚀 Fetching {len(name_to_source)} journals in parallel with {MAX_WORKERS} workers...\n")
    
    # 2) Fetch all works for each Source ID in parallel
    all_frames = []
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        # Submit all journal fetch tasks
        future_to_journal = {
            executor.submit(process_journal, jname, sid): jname 
            for jname, sid in name_to_source.items()
        }
        
        # Process results as they complete
        for future in as_completed(future_to_journal):
            jname = future_to_journal[future]
            try:
                df = future.result()
                if df is not None:
                    all_frames.append(df)
            except Exception as e:
                print(f"[ERROR] {jname} generated an exception: {e}")

    if not all_frames:
        print("No data frames produced. Exiting.")
        sys.exit(1)

    # 3) Concatenate full corpus
    print("\n📊 Combining all journals into single corpus...")
    corpus = pd.concat(all_frames, ignore_index=True)
    corpus = corpus.drop_duplicates(subset=["openalex_id"]).reset_index(drop=True)
    corpus_file = CLEAN_DIR / "is_corpus_all.parquet"
    corpus.to_parquet(corpus_file, index=False)
    print(f"[SAVE] ALL: {len(corpus):,} rows -> {corpus_file}")

    # 4) Little summary
    print("\n" + "="*60)
    print("📈 Per-journal counts:")
    print("="*60)
    summary = (
        corpus.groupby("journal")["openalex_id"].count().sort_values(ascending=False)
        .rename("works").to_frame()
    )
    print(summary.to_string())
    print("="*60)
    print(f"\n✅ Total papers in corpus: {len(corpus):,}")
    print(f"✅ Output file: {corpus_file}")
    print("\n🎉 All done!")

if __name__ == "__main__":
    main()
