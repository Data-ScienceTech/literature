# Sample Expansion Analysis: Journals & Time Period

**Analysis Date:** October 3, 2025  
**Current Sample:** 3,093 papers from 4 journals (2016-2025)

---

## Current Sample Overview

### Journals (4 journals)
1. **Information Systems Research (ISR)** - 922 papers (29.8%)
2. **Organization Science (ORSC)** - 918 papers (29.7%)
3. **MIS Quarterly (MISQ)** - 707 papers (22.9%)
4. **Academy of Management Review (AMR)** - 546 papers (17.7%)

### Time Period
- **Current:** 2016-2025 (10 years)
- **Coverage:** 100% DOI coverage, 75% abstract coverage
- **Papers per year:** Ranges from 233 (2017) to 428 (2025)
- **Average:** ~309 papers/year

---

## Expansion Option 1: Add More Journals (Same Time Period)

### 1.1 Adding Top-Tier Management Journals

**Strong Candidates (Same Quality Tier):**

| Journal | Abbreviation | Why Include | Est. Papers/Year |
|---------|-------------|-------------|------------------|
| Academy of Management Journal | AMJ | Empirical complement to AMR | 80-100 |
| Strategic Management Journal | SMJ | Strategy/competitive advantage | 100-120 |
| Administrative Science Quarterly | ASQ | Theory & organizational research | 40-50 |
| Journal of Management | JoM | Broad management research | 80-100 |
| Management Science | MS | Quantitative/analytical methods | 150-200 |

**Expected Addition:** ~450-570 papers/year × 10 years = **4,500-5,700 papers**

### 1.2 Adding IS/Technology Journals

| Journal | Abbreviation | Why Include | Est. Papers/Year |
|---------|-------------|-------------|------------------|
| Journal of Management Information Systems | JMIS | Complement to MISQ/ISR | 40-50 |
| European Journal of Information Systems | EJIS | European IS perspective | 50-60 |
| Journal of the Association for Information Systems | JAIS | Broad IS coverage | 30-40 |
| Journal of Strategic Information Systems | JSIS | Strategic IS issues | 30-40 |

**Expected Addition:** ~150-190 papers/year × 10 years = **1,500-1,900 papers**

### 1.3 Adding Specialized/Entrepreneurship Journals

| Journal | Abbreviation | Why Include | Est. Papers/Year |
|---------|-------------|-------------|------------------|
| Entrepreneurship Theory and Practice | ETP | Entrepreneurship focus | 60-80 |
| Journal of Business Venturing | JBV | Entrepreneurship/innovation | 80-100 |
| Research Policy | RP | Innovation/technology policy | 200-250 |

**Expected Addition:** ~340-430 papers/year × 10 years = **3,400-4,300 papers**

### Total with Expanded Journals (Conservative Scenario)
- **Current:** 3,093 papers
- **+5 Management journals:** ~5,000 papers
- **+4 IS journals:** ~1,700 papers
- **+3 Entrepreneurship/Innovation:** ~3,800 papers
- **TOTAL:** ~**13,600 papers** (4.4x increase)

---

## Expansion Option 2: Extend Time Period (Same Journals)

### 2.1 Backward Extension

**Option A: Add 5 years backward (2011-2015)**
- Estimated papers: ~1,500-1,800 papers
- **Total sample:** ~4,600-4,900 papers (1.5x increase)
- **Pros:** 
  - Captures earlier foundational work
  - 15-year window provides better temporal analysis
  - Shows evolution of research streams
- **Cons:**
  - Older papers may have lower abstract availability
  - Publication patterns may differ (fewer online-first)

**Option B: Add 10 years backward (2006-2015)**
- Estimated papers: ~3,000-3,600 papers
- **Total sample:** ~6,100-6,700 papers (2x increase)
- **Pros:**
  - 20-year window ideal for longitudinal analysis
  - Captures pre-2008 financial crisis research
  - Better for RPYS and historical analysis
- **Cons:**
  - Metadata quality may decline significantly
  - Abstract availability likely <50%
  - DOI coverage may be incomplete

**Option C: Extend to all available (1990-2025)**
- Estimated papers: ~8,000-12,000 papers
- **Total sample:** ~11,000-15,000 papers (3.5-5x increase)
- **Pros:**
  - Complete historical coverage
  - Ideal for comprehensive field mapping
  - Maximum RPYS insight
- **Cons:**
  - Very low abstract/metadata availability pre-2000
  - Significant data quality challenges
  - May require manual curation

### 2.2 Forward Extension
- **Current:** Through 2025
- **Not applicable** - already at current date

---

## Expansion Option 3: Combined Expansion

### Scenario A: Moderate Expansion
- **Journals:** Add 5 core management journals (AMJ, SMJ, ASQ, JoM, MS)
- **Time:** Extend backward to 2011 (15-year window)
- **Estimated total:** ~7,000-8,500 papers (2.3-2.7x increase)

### Scenario B: Aggressive Expansion
- **Journals:** Add 12 journals (management + IS + entrepreneurship)
- **Time:** Extend backward to 2006 (20-year window)
- **Estimated total:** ~18,000-22,000 papers (5.8-7.1x increase)

### Scenario C: Comprehensive Field Mapping
- **Journals:** Add 15-20 top journals across all domains
- **Time:** Extend backward to 2000 (25-year window)
- **Estimated total:** ~30,000-40,000 papers (9.7-12.9x increase)

---

## Technical Feasibility Assessment

### Computational Requirements

| Sample Size | Embeddings | Clustering | Citation Network | Total Time | Memory |
|-------------|-----------|-----------|------------------|------------|--------|
| 3,093 (current) | 15-20 min | 5-10 min | 30-60 min | ~2 hours | 8 GB |
| ~7,500 (moderate) | 40-50 min | 15-25 min | 2-3 hours | ~4-5 hours | 16 GB |
| ~15,000 (aggressive) | 80-100 min | 30-45 min | 5-8 hours | ~10-12 hours | 32 GB |
| ~35,000 (comprehensive) | 3-4 hours | 1-2 hours | 15-20 hours | ~24-30 hours | 64 GB |

### Data Acquisition Challenges

#### For Additional Journals:
1. **Access Requirements:**
   - Institutional subscriptions needed for most journals
   - Some journals may have export restrictions
   - BibTeX export quality varies by publisher

2. **Data Quality:**
   - Abstract availability varies (60-90% for recent papers)
   - DOI coverage excellent for post-2010 (>95%)
   - Pre-2010 may require manual DOI lookup

3. **Export Methods:**
   - **Web of Science:** Bulk export (up to 500 at a time)
   - **Scopus:** Similar bulk export capabilities
   - **Publisher sites:** Variable export quality
   - **Google Scholar:** No bulk export (would need scraping)

#### For Extended Time Period:
1. **Pre-2010 Challenges:**
   - Lower digitization rates
   - Missing abstracts (may be <50% pre-2005)
   - Inconsistent DOI assignment
   - May require OCR for older content

2. **Database Coverage:**
   - Web of Science has best historical coverage
   - Scopus coverage declines pre-2000
   - Publisher archives vary significantly

---

## Recommended Approach

### Phase 1: Moderate Strategic Expansion (Recommended)
**Add 5 key journals + extend to 2011**

**Journals to add:**
1. Academy of Management Journal (AMJ) - empirical counterpart
2. Strategic Management Journal (SMJ) - strategy focus
3. Administrative Science Quarterly (ASQ) - theory depth
4. Management Science (MS) - quantitative rigor
5. Journal of Business Venturing (JBV) - entrepreneurship

**Why these 5?**
- Complement existing journals perfectly
- Strong citation linkages with current sample
- Excellent metadata availability
- Manageable size increase (~4,500 papers total)

**Time extension: 2011-2025 (15 years)**
- Captures post-financial crisis evolution
- Good metadata availability
- Maintains manageable scope

**Expected final sample:** ~7,500-8,500 papers

### Phase 2: Gradual Further Expansion (If Successful)
After validating Phase 1 results:
1. Add 3-4 IS journals (JMIS, EJIS, JAIS)
2. Consider extending back to 2006
3. Evaluate stream quality and coverage

---

## Data Collection Strategy

### Option 1: Web of Science (Recommended)
**Pros:**
- Comprehensive coverage of all target journals
- Excellent metadata quality
- Reliable BibTeX export
- Good abstract coverage
- Institutional access likely available

**Process:**
1. Advanced search by journal + year range
2. Export in BibTeX format (500 records/batch)
3. Merge files programmatically
4. Validate DOI coverage

**Estimated time:** 2-4 hours for 5 journals × 15 years

### Option 2: Scopus
**Pros:**
- Similar coverage to Web of Science
- Good export functionality
- Clean metadata

**Cons:**
- May have slight gaps pre-2000
- Export limits similar to WoS

### Option 3: Publisher Direct Access
**Pros:**
- Most complete article metadata
- Best abstract coverage

**Cons:**
- Would need separate exports from:
  - Sage (AMJ, ASQ, SMJ)
  - INFORMS (MS)
  - Elsevier (JBV)
- Time-consuming
- Inconsistent export formats

### Option 4: Hybrid Approach
1. Use Web of Science for bulk collection
2. Fill gaps from publisher sites
3. Validate against Scopus
4. Use OpenAlex API to fill missing DOIs/metadata

---

## Cost-Benefit Analysis

### Current Sample (3,093 papers, 4 journals, 2016-2025)
- **Pros:** 
  - Manageable size
  - Excellent data quality
  - Fast processing
  - Already complete
- **Cons:**
  - Limited journal diversity
  - No strategy/entrepreneurship focus
  - Short time window for longitudinal analysis
  - May miss important research streams

### Moderate Expansion (7,500 papers, 9 journals, 2011-2025)
- **Pros:**
  - Much broader field coverage
  - Adds strategy, entrepreneurship, quantitative perspectives
  - 15-year window enables better temporal analysis
  - Still computationally manageable
  - Captures financial crisis aftermath
- **Cons:**
  - 2-3x longer processing time
  - Requires data collection effort (4-6 hours)
  - Higher computational requirements (16GB RAM)

### Aggressive Expansion (18,000 papers, 15+ journals, 2006-2025)
- **Pros:**
  - Comprehensive field mapping
  - 20-year perspective
  - Maximum research stream diversity
- **Cons:**
  - Significant data collection effort (8-12 hours)
  - Long processing time (10-12 hours)
  - Requires 32GB+ RAM
  - Metadata quality concerns pre-2010
  - May be unwieldy for analysis

---

## Quality Considerations

### What Makes a Good Sample Size?

**Too Small (<2,000 papers):**
- May miss important streams
- Limited clustering resolution
- Weak citation networks
- Statistical power concerns

**Optimal (5,000-15,000 papers):**
- Good stream discovery
- Rich citation networks
- Diverse perspectives
- Manageable analysis
- **Sweet spot for most research questions**

**Too Large (>25,000 papers):**
- Computational challenges
- Overwhelming detail
- Difficult to validate
- May blur important distinctions
- Diminishing returns

**Current sample (3,093) is on the smaller side but workable**
- Good starting point
- Could benefit from strategic expansion

---

## Recommendations Summary

### Immediate Next Steps (if you want to expand):

1. **Recommended Expansion: "Strategic 9-Journal, 15-Year Sample"**
   - Add: AMJ, SMJ, ASQ, MS, JBV (5 journals)
   - Time: 2011-2025 (15 years)
   - Expected size: ~7,500-8,500 papers
   - Effort: 4-6 hours data collection
   - Processing: 4-5 hours
   - Memory: 16GB RAM

2. **Data Collection Method:**
   - Use Web of Science (institutional access)
   - Export BibTeX in batches
   - Use provided Python scripts to merge and validate
   - Verify DOI coverage

3. **Quality Checks:**
   - Aim for >90% DOI coverage
   - Target >70% abstract coverage
   - Validate year ranges
   - Remove duplicates

4. **Alternative: Stay with Current Sample**
   - If time/resources are limited
   - If 4 journals provide sufficient coverage for your research question
   - Focus on deeper analysis rather than broader coverage

### Questions to Guide Your Decision:

1. **What's your research question?**
   - Field mapping → broader is better (expand journals)
   - Temporal evolution → longer is better (extend years)
   - Specific stream deep-dive → current may be sufficient

2. **What resources do you have?**
   - Computational: Can you access 16-32GB RAM?
   - Data access: Do you have Web of Science/Scopus access?
   - Time: Can you invest 4-6 hours in data collection?

3. **What's your timeline?**
   - If urgent: stick with current sample
   - If flexible: strategic expansion recommended
   - If long-term project: consider comprehensive expansion

---

## Conclusion

**Expansion is definitely feasible and recommended**, especially adding 5 strategic journals (AMJ, SMJ, ASQ, MS, JBV) and extending the time window to 2011-2025. This would create a ~7,500-8,500 paper corpus that:

- Covers the major management, strategy, IS, and entrepreneurship literatures
- Provides 15 years of temporal data for trend analysis
- Maintains manageable computational requirements
- Significantly improves research stream discovery
- Enhances citation network analysis

**Feasibility: ★★★★☆ (4/5 stars)**
- Technically straightforward
- Data access likely available via institutional subscriptions
- Computationally manageable with modern hardware
- Reasonable time investment

**Impact: ★★★★★ (5/5 stars)**
- Substantially improves coverage and insights
- Enables cross-disciplinary stream discovery
- Better temporal analysis
- More robust citation networks
- Higher publication potential
