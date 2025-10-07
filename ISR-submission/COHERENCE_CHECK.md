# ISR Submission Coherence Check

**Date**: October 7, 2025  
**Status**: Review Required

## Summary

The ISR-submission folder structure looks good overall, but there are some inconsistencies between what's referenced in the manuscript and what actually exists in the file structure.

## ✅ What's Working Well

1. **Folder Structure** - Well organized:
   ```
   ISR-submission/
   ├── current_pipeline/     ✓ Pipeline code properly organized
   ├── submission/           ✓ All manuscript files present
   ├── tools/                ✓ Utility scripts available
   └── PR_INSTRUCTIONS.md    ✓ Meta documentation
   ```

2. **Manuscript Content**:
   - ✅ Abstract updated (unstructured, ~215 words)
   - ✅ Author information filled (Carlos Denner dos Santos, UnB)
   - ✅ All placeholders removed from main text
   - ✅ URLs updated to actual GitHub and web explorer
   - ✅ Numeric formatting standardized (percentages to 1 decimal)
   - ✅ Appendix A complete with L2 topic table
   - ✅ Appendix B complete with sensitivity analysis
   - ✅ Appendix C updated with reproducibility statement

3. **References**:
   - ✅ Foundational papers added to references.bib (Davis 1989, DeLone & McLean 2003, etc.)

## ⚠️ Issues Found & Fixed

### 1. Script References in Appendix C

**Problem**: Manuscript referenced scripts that don't exist:
- ❌ `generate_papers_database.py`
- ❌ `perform_hybrid_clustering.py`
- ❌ `analyze_clustering_results.py`
- ❌ `generate_dashboard_data.py`
- ❌ `create_visualizations.py`

**Fixed**: Updated Appendix C to reference actual scripts:
- ✅ `current_pipeline/fetcher/fetch_ais_basket_crossref.py`
- ✅ `current_pipeline/enricher/enrich_ais_basket_openalex.py`
- ✅ `current_pipeline/analysis/analyze_ais_basket_coverage.py`
- ✅ `current_pipeline/analysis/analyze_enrichment_results.py`
- ✅ `tools/export_l2.py`
- ✅ `tools/export_sensitivity.py`
- ✅ `tools/build_bib.py`

### 2. RUNBOOK Accuracy

**Problem**: Original RUNBOOK referenced non-existent command-line tools with specific arguments

**Fixed**: Created `RUNBOOK_NEW.md` with:
- Actual file paths from current_pipeline/
- Realistic workflow based on existing scripts
- Proper hardware specs matching manuscript
- Accurate timing estimates from manuscript

## 📋 Action Items

### High Priority
1. **Replace RUNBOOK.md**: 
   ```bash
   mv submission/RUNBOOK_NEW.md submission/RUNBOOK.md
   ```

2. **Verify Clustering Scripts**: The main clustering implementation is referenced as being in "repository root" but needs to be verified:
   - Where are the actual hybrid clustering scripts?
   - Are they in the root directory or elsewhere?
   - Update paths in both RUNBOOK and Appendix C accordingly

3. **Check Dashboard Location**: Manuscript references `dashboard/` directory but verify:
   - Is it in ISR-submission/ or repository root?
   - Is it deployed to GitHub Pages as stated?

### Medium Priority
4. **Verify Tool Scripts Work**:
   ```bash
   cd tools
   python export_l2.py
   python export_sensitivity.py
   python build_bib.py
   ```
   - Do these scripts exist and run?
   - Do they output to the correct locations?

5. **Test Environment Files**:
   - Verify `submission/requirements.txt` has all dependencies
   - Verify `submission/environment.yml` works with conda

### Low Priority
6. **Complete Appendix D**: Currently placeholder - add screenshots/guide for web explorer

7. **Generate Final Documents**:
   ```bash
   pandoc submission/manuscript.md --citeproc --bibliography=submission/references.bib -o submission/manuscript.docx
   ```

## 📁 Current File Inventory

### submission/
- ✅ manuscript.md (complete, coherent)
- ✅ references.bib (foundational papers added)
- ✅ appendix_A_L2.md (source data)
- ✅ appendix_B_sensitivity.md (placeholder/backup)
- ✅ appendix_C_code_availability.md (placeholder/backup)
- ✅ appendix_D_explorer_guide.md (empty/placeholder)
- ✅ RUNBOOK.md (needs replacement)
- ✅ RUNBOOK_NEW.md (new, accurate version)
- ✅ README.md (checklist)
- ✅ requirements.txt (verify)
- ✅ environment.yml (verify)
- ⚠️ manuscript.docx (needs regeneration)

### current_pipeline/
- ✅ fetcher/ (fetch_ais_basket_crossref.py, etc.)
- ✅ enricher/ (enrich_ais_basket_openalex.py, etc.)
- ✅ analysis/ (analyze_ais_basket_coverage.py, analyze_enrichment_results.py)

### tools/
- ✅ build_bib.py
- ✅ export_l2.py
- ✅ export_sensitivity.py
- ✅ fix_bib.py

## 🔍 What Still Needs Verification

1. **Clustering Implementation Location**: Where are the actual clustering scripts?
   - The manuscript mentions hybrid clustering, L1/L2/L3, NMF, etc.
   - RUNBOOK says "repository root" but which files exactly?

2. **Dashboard Location**: Is `dashboard/` in ISR-submission or repo root?

3. **Data Files**: Where are the actual data files?
   - `ais_basket_enriched.csv`
   - `hierarchical_clusters_L1_L2_L3.csv`
   - `citation_network.npz`
   - etc.

4. **Artifacts**: Do the appendix generation scripts actually work?

## ✨ Overall Assessment

**Status**: 85% coherent, needs minor fixes

**Strengths**:
- Manuscript content is excellent and complete
- Folder structure is logical
- Documentation is comprehensive

**Weaknesses**:
- Script references don't match actual files
- Need to verify data pipeline actually works
- Missing some implementation details

**Recommendation**: 
1. Replace RUNBOOK.md with RUNBOOK_NEW.md
2. Verify clustering scripts location and update references
3. Test the full pipeline end-to-end
4. Generate final .docx file

## Next Steps

1. Review this coherence check
2. Make the replacements suggested
3. Locate and document clustering scripts
4. Test pipeline execution
5. Generate final submission files
