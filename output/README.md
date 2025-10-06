# Output Files Documentation

This directory contains all analysis results, reports, and logs from the AIS Basket Literature project.

## 📊 **Current Analysis Results** (October 6, 2025)

### **Core Dataset Outputs**
- `ais_basket_20251006.bib` - Complete BibTeX export of all 12,564 articles
  - Format: Standard BibTeX for citation management
  - Size: ~15MB
  - Contains: DOI, title, authors, journal, year, volume, issue, pages

### **Coverage Analysis**
- `coverage_analysis_20251006_125328.json` - Detailed coverage statistics
  - Complete field-by-field analysis
  - Journal-specific breakdowns
  - Temporal coverage patterns
  - Missing data identification

- `coverage_summary_20251006_125328.md` - Human-readable coverage report
  - Executive summary of data quality
  - Recommendations for improvement
  - Visualization-ready statistics

### **Enrichment Results**
- `enrichment_report_20251006_130647.json` - OpenAlex enrichment outcomes
  - Before/after comparison statistics
  - Field-specific improvement metrics
  - API usage and performance data
  - Quality assessment results

### **Processing Logs**
- `enrichment_log_20251006_130141.log` - Complete enrichment process log
  - Real-time progress tracking
  - Error handling and recovery
  - API call details and timing
  - Cache performance metrics

### **Fetching History**
- `fetch_log_*.log` - Historical fetch operation logs
  - `fetch_log_20251006_124846.log` - Final successful full fetch
  - Earlier logs show incremental development and testing
  - Complete audit trail of data collection

- `fetch_summary_20251006.json` - Fetch operation summary
  - Articles collected per journal
  - Processing time and performance
  - Error rates and recovery

## 📈 **Key Metrics from Latest Run**

### **Dataset Completeness**
- **Total Articles**: 12,564
- **Date Range**: 1977-2026 (49 years)
- **Journals Covered**: 8/8 AIS Basket journals (100%)
- **Processing Success Rate**: 100%

### **Data Quality Achievements**
- **Abstract Coverage**: 64.2% (up from 34.1%)
- **Keyword Coverage**: 99.9% (up from 0%)
- **Reference Coverage**: 57% (maintained)
- **Author Coverage**: 90.1% (enhanced affiliations for 42%)

### **Processing Performance**
- **Fetch Time**: ~45 minutes (full corpus)
- **Enrichment Time**: ~5 minutes (252 API calls)
- **API Efficiency**: 50 articles per call (vs 1:1)
- **Cache Hit Rate**: 99%+ on subsequent runs
- **Error Rate**: 0%

## 🗂️ **File Usage Guide**

### **For Citation Management**
```bash
# Import into reference manager
cp output/ais_basket_20251006.bib ~/Documents/References/
```

### **For Statistical Analysis**
```python
import json
import pandas as pd

# Load coverage analysis
with open('output/coverage_analysis_20251006_125328.json', 'r') as f:
    coverage = json.load(f)
    
# Load enrichment results
with open('output/enrichment_report_20251006_130647.json', 'r') as f:
    enrichment = json.load(f)
```

### **For Quality Assessment**
```bash
# View human-readable summary
cat output/coverage_summary_20251006_125328.md

# Check processing logs for any issues
tail -n 50 output/enrichment_log_20251006_130141.log
```

## 🔍 **Log File Analysis**

### **Understanding Fetch Logs**
- Multiple fetch logs show iterative development
- Final successful log: `fetch_log_20251006_124846.log`
- Shows progress through all 8 journals
- Documents API rate limiting and error handling

### **Understanding Enrichment Logs**
- Real-time progress through 252 batches
- Cache saving at regular intervals
- No errors encountered during enrichment
- Complete statistics summary at end

## 📅 **File Retention Policy**

### **Keep Permanently**
- Latest coverage analysis and enrichment reports
- Final BibTeX export
- Final fetch summary

### **Archive After 30 Days**
- Processing logs (keep for debugging)
- Intermediate analysis files
- Development iteration logs

### **Update on Next Run**
- All files will have new timestamps
- Previous versions should be archived
- Compare reports to track improvements

## 🔄 **Regenerating Reports**

To regenerate these reports with fresh data:

```bash
# Update dataset (incremental)
cd current_pipeline/fetcher
python fetch_ais_basket_crossref.py --incremental

# Re-enrich if needed
cd ../enricher
python enrich_ais_basket_openalex.py

# Generate fresh analysis
cd ../analysis
python analyze_ais_basket_coverage.py
python analyze_enrichment_results.py
```

## 📊 **Using Results for Research**

These output files enable multiple research approaches:

### **Bibliometric Analysis**
- Use coverage analysis for journal comparison studies
- Track temporal trends in publication patterns
- Analyze field evolution over 49 years

### **Content Analysis**
- Leverage 99.9% keyword coverage for topic modeling
- Use enriched abstracts for semantic analysis
- Perform cross-journal content comparison

### **Network Analysis**
- Utilize 57% reference coverage for citation networks
- Map knowledge flow between journals
- Identify influential papers and authors

### **Quality Assessment**
- Document data limitations using coverage reports
- Report enrichment improvements in methodology
- Validate findings against processing logs

---

**Note**: All timestamps in filenames use format YYYYMMDD_HHMMSS for chronological sorting.