# OpenAlex Enrichment Documentation

## Overview

The OpenAlex enrichment script enhances our CrossRef corpus with missing data from OpenAlex, particularly addressing the gaps identified in our coverage analysis:

- **Missing abstracts**: Especially for Taylor & Francis journals (0% coverage)
- **Missing keywords**: CrossRef doesn't provide subject classifications
- **Poor author affiliations**: OpenAlex has better institutional data

## Key Features

### 1. Smart Enrichment Strategy
- Preserves high-quality CrossRef data
- Only adds OpenAlex data where CrossRef is missing or poor quality
- Batch processing for efficiency (50 articles per API call)
- Comprehensive caching to avoid repeat API calls

### 2. Abstract Enhancement
- Reconstructs abstracts from OpenAlex inverted index format
- Only replaces CrossRef abstracts if they're missing or very short (<20 words)
- Handles malformed inverted indices gracefully

### 3. Keyword Addition
- Extracts concepts from OpenAlex semantic classification
- Filters to high-level concepts (level ≤ 2) to avoid noise
- Adds to `subject` field (not available in CrossRef)

### 4. Author Affiliation Enhancement
- Merges CrossRef author names with OpenAlex institutional data
- Only enhances when CrossRef affiliations are missing/poor
- Preserves author name accuracy from CrossRef

## Data Quality Improvements

Based on our coverage analysis, this enrichment should:

- **Abstracts**: Increase from 34.5% to ~75-80% coverage
- **Keywords**: Increase from 0% to ~85-90% coverage  
- **Affiliations**: Improve quality for ~60% of articles

### Specific Journal Impact
- **EJIS**: 0% → ~80% abstract coverage
- **JMIS**: 0% → ~80% abstract coverage  
- **JSIS**: 0% → ~80% abstract coverage
- **All journals**: 0% → ~85% keyword coverage

## Technical Architecture

### Core Classes

#### `OpenAlexEnricher`
- Main enrichment engine
- Handles API communication, caching, and batch processing
- Tracks comprehensive statistics

#### Key Methods
- `batch_find_openalex_works()`: Efficient batch DOI lookups
- `reconstruct_abstract()`: Converts inverted index to text
- `extract_keywords()`: Semantic concept extraction
- `enrich_article()`: Smart merging of CrossRef + OpenAlex data

### Caching System
- Local JSON cache for all API responses
- Caches both positive and negative results
- Persistent across runs for efficiency
- Automatic cache management and periodic saves

### Output Formats
- **JSON**: Full enriched corpus with all metadata
- **Parquet**: Analysis-ready tabular format
- **Reports**: Comprehensive enrichment statistics

## Usage Examples

### Basic Enrichment
```powershell
.\run_ais_basket_enrichment.ps1 -RunEnrichment
```

### Check Dependencies
```powershell
.\run_ais_basket_enrichment.ps1 -CheckDeps
```

### Run Tests
```powershell
python test_ais_basket_enrichment.py
```

## API Considerations

### Rate Limiting
- 0.2 second delay between requests (polite pool)
- Batch processing to minimize API calls
- Retry logic with exponential backoff
- Comprehensive error handling

### OpenAlex Features Used
- Work lookup by DOI
- Abstract inverted index reconstruction
- Concept/subject classification
- Author institutional affiliations
- Citation counts and metadata

## Output Structure

### Enriched Article Schema
```json
{
  "doi": "10.25300/misq/2020/14905",
  "title": "Original CrossRef title",
  "abstract": "Enhanced abstract from OpenAlex if needed",
  "subject": ["Information systems", "Computer science"],
  "authors": [
    {
      "given": "John",
      "family": "Doe", 
      "affiliation": ["University of Testing"]
    }
  ],
  "_enrichment": {
    "source": "openalex",
    "openalex_id": "https://openalex.org/W12345",
    "enriched_fields": ["abstract", "keywords", "affiliations"]
  },
  "openalex_cited_by_count": 25
}
```

## Performance Expectations

### Processing Time
- ~30-45 minutes for full corpus (12,564 articles)
- 95%+ cache hit rate on subsequent runs
- Batch processing reduces API calls by 50x

### Success Rates
- **OpenAlex Match Rate**: ~85-90% (DOI-based matching)
- **Abstract Enhancement**: ~40-50% of articles
- **Keyword Addition**: ~85-90% of articles
- **Affiliation Enhancement**: ~60% of articles

## Quality Assurance

### Data Validation
- DOI normalization and validation
- Abstract quality thresholds (≥20 words)
- Concept filtering (high-level only)
- Author name preservation from authoritative CrossRef

### Error Handling
- Graceful API failure recovery
- Malformed data handling
- Progress preservation through caching
- Comprehensive logging and reporting

## Integration

### Input Requirements
- `data/clean/ais_basket_corpus.json` (from CrossRef fetcher)
- Internet connection for OpenAlex API
- Python 3.8+ with required packages

### Output Files
- `data/clean/ais_basket_corpus_enriched.json`
- `data/clean/ais_basket_corpus_enriched.parquet`
- `output/enrichment_report_*.json`
- `output/enrichment_log_*.log`

## Monitoring and Reporting

### Real-time Progress
- Progress bars for batch processing
- Live statistics updates
- Cache hit rate monitoring
- Error rate tracking

### Final Reports
- Before/after comparison statistics
- Field-by-field improvement metrics
- Journal-specific enhancement rates
- API usage and performance metrics

## Future Enhancements

### Potential Improvements
1. **Semantic Scholar Integration**: Additional abstract source
2. **ORCID Resolution**: Better author disambiguation  
3. **Reference Enhancement**: Full reference metadata
4. **Citation Network**: Citation relationship mapping
5. **Full-text Integration**: PDF/HTML content when available

### Scalability
- Designed for incremental updates
- Cache system supports growing corpus
- Modular architecture for additional sources
- Efficient batch processing scales to larger datasets