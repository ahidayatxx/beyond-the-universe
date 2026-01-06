---
name: ebm-pico-research
description: Clinical evidence research using PICO framework with PubMed search and JBI credibility assessment
tags: [evidence-based-medicine, research, clinical, PubMed, PICO, systematic-review]
---

# Evidence-Based Medicine PICO Research Skill

## Overview

This skill automates evidence-based medicine research by converting clinical situations or patient notes into structured PICO format, searching PubMed with intelligent year-range selection, filtering results by evidence pyramid level, and performing Joanna Briggs Institute (JBI) critical appraisal.

## When to Use This Skill

Use this skill when you need to:
- Find evidence for clinical decisions
- Conduct literature reviews for clinical questions
- Answer specific clinical questions with best available evidence
- Research treatment options for a patient
- Create or update clinical guidelines
- Support evidence-based practice
- Assess study credibility using JBI criteria

## How This Skill Works

### Input Modes

The skill accepts two types of input:

**1. Direct Clinical Question**
> "Should I use LMWH or UFH for VTE prophylaxis in stroke patients?"

**2. Clinical Note Summary**
> "65-year-old male, admitted with acute ischemic stroke, right MCA territory. NIHSS 12. History of hypertension, type 2 diabetes, atrial fibrillation. On warfarin but INR subtherapeutic. Not a thrombolysis candidate. Plan for VTE prophylaxis."

### Workflow

1. **PICO Extraction**
   - For clinical questions: Parse and extract P-I-C-O elements
   - For clinical notes: Parse patient context and construct PICO automatically

2. **Search Year Determination**
   - Automatically determines appropriate search range based on:
     - Medical specialty (3-15 years)
     - Rapidly evolving fields (oncology, infectious diseases): 3-5 years
     - Established treatments (cardiology, internal medicine): 5-10 years
     - Rare conditions: up to 15 years

3. **PubMed Search**
   - Constructs MeSH-aware queries from PICO elements
   - Uses `mcp__MCP_DOCKER__search_pubmed` tool
   - Filters by publication date range

4. **Evidence Pyramid Classification**
   - Classifies articles into levels:
     - Level 1: Systematic Reviews & Meta-Analyses (highest)
     - Level 2: Randomized Controlled Trials
     - Level 3: Cohort Studies
     - Level 4: Case-Control Studies
     - Level 5: Case Series/Case Reports
     - Level 6: Animal Research/In Vitro (lowest)

5. **JBI Credibility Assessment**
   - Performs critical appraisal using Joanna Briggs Institute checklists
   - Checklists vary by study design (RCT, systematic review, cohort, etc.)
   - Assesses: randomization, blinding, follow-up, confounding, statistical analysis
   - Provides quality score (0-100) and rating (High/Moderate/Low)

6. **Output Generation**
   - **Markdown file output** - Creates formatted markdown file with:
     - PICO framework analysis
     - Evidence pyramid classification
     - Critical evidence table
     - JBI credibility assessments
     - Clinical bottom line
     - Practical recommendations
     - Guideline alignment
     - Full APA 7th edition references

   - **File naming convention**: `{condition}-{intervention}-vs-{comparison}-ebm-analysis-{YYYYMMDD}.md`
   - **Console output** - Displays progress and confirmation during analysis

### Orchestrator Workflow (v1.3.0)

The skill uses a main orchestrator script (`ebm_analyzer.py`) that integrates all components:

**Pass 1: PICO Extraction & PubMed Search Request**
```
User provides clinical question or note
    ↓
Orchestrator extracts PICO elements
    ↓
Specialty classifier determines search year range (3-15 years)
    ↓
Orchestrator outputs PUBMED_SEARCH_REQUEST JSON
    ↓
Claude Code captures JSON and invokes MCP PubMed tool
```

**Pass 2: Evidence Processing & Markdown Generation**
```
Claude Code passes PubMed results to orchestrator
    ↓
Evidence pyramid classifier sorts articles by level (1-6)
    ↓
JBI checklist performs critical appraisal with quality scores
    ↓
Markdown generator formats complete EBM analysis document
    ↓
APA formatter generates references in 7th edition style
    ↓
File written to disk with descriptive name
```

### Command-Line Usage

You can also run the orchestrator directly from command line:

```bash
# From clinical question
python scripts/ebm_analyzer.py --question "LMWH vs UFH for VTE prophylaxis in stroke"

# From clinical note
python scripts/ebm_analyzer.py --note "65M, acute ischemic stroke..."

# With pre-fetched PubMed results
python scripts/ebm_analyzer.py \
    --pubmed-results results.json \
    --pico pico.json \
    --search-years '{"start": 2020, "end": 2025}'
```

## Using the Skill

### Example 1: Direct Clinical Question

**User Input:**
```
I need to decide whether to use LMWH or UFH for VTE prophylaxis in stroke patients
```

**Skill Output:**
```
PICO ANALYSIS
=============
P (Population): Stroke patients
I (Intervention): LMWH (Low Molecular Weight Heparin)
C (Comparison): UFH (Unfractionated Heparin)
O (Outcome): VTE prophylaxis effectiveness, bleeding risk

Searching PubMed (5 years for neurology)...

TOP EVIDENCE (Levels 1-2)
=========================
3 meta-analyses, 7 RCTs found

EVIDENCE TABLE
--------------
| Level | Quality | Study | Authors | Year | Key Findings |
|-------|---------|-------|---------|------|--------------|
| 1 | High (85%) | Meta-analysis of VTE prophylaxis in stroke | Smith et al. | 2022 | LMWH reduces DVT vs placebo (RR 0.65), no difference in ICH |
| 2 | High (88%) | RCT: LMWH vs UFH for stroke | Jones et al. | 2020 | No significant difference in efficacy, similar bleeding rates |

ANALYSIS
========
Based on 1 meta-analysis and 7 RCTs (total n=2,450), LMWH and UFH have
comparable efficacy for VTE prophylaxis in acute ischemic stroke patients.
No significant difference in DTE prevention (RR 1.02, 95% CI 0.94-1.11)
or intracranial hemorrhage (RR 0.98, 95% CI 0.85-1.13).

Recommendation: Either LMWH or UFH is acceptable. Consider LMWH for
once-daily dosing convenience.
```

### Example 2: Clinical Note Summary

**User Input:**
```
72-year-old female, admitted with community-acquired pneumonia. CURB-65 score 3.
Comorbidities: COPD, HFpEF, CKD stage 3. Allergies: Penicillin (rash).
Decision: Antibiotic selection.
```

**Skill Output:**
```
PATIENT CONTEXT ANALYSIS
========================
Patient: Elderly female
Primary Condition: Community-acquired pneumonia (CURB-65 3, moderate-severe)
Comorbidities: COPD, HFpEF, CKD stage 3
Contraindications: Penicillin allergy

PICO CONSTRUCTED
================
P: Elderly patients with moderate-severe CAP and comorbidities
I: Respiratory fluoroquinolone (levofloxacin)
C: Combination therapy (macrolide + cephalosporin)
O: Treatment failure, mortality, adverse effects

Searching PubMed (5 years for infectious diseases)...

TOP EVIDENCE (Levels 1-2)
=========================
[Analysis with CAP-specific guidelines and studies]
```

## Skill Components

The skill consists of the following files:

### Python Scripts

**Core Components:**

1. **`ebm_analyzer.py`** (Main Orchestrator)
   - Integrates all components into complete EBM analysis workflow
   - Manages two-pass PubMed search integration
   - Generates markdown files with descriptive naming
   - Accepts questions, clinical notes, or pre-fetched results

2. **`markdown_generator.py`** (Template Engine)
   - Generates formatted markdown matching example structure
   - Creates all sections: PICO, evidence tables, JBI assessments
   - Formats clinical bottom line and recommendations
   - Generates key takeaways summary

3. **`specialty_classifier.py`** (Year Range Logic)
   - Loads medical_specialties.yaml configuration
   - Detects medical specialty from PICO text
   - Returns appropriate search year range (3-15 years)
   - Handles special situations (pediatric, pregnancy, rare diseases)

4. **`apa_formatter.py`** (Citation Formatter)
   - Formats citations in APA 7th edition style
   - Handles up to 20 authors, missing data, edge cases
   - Generates reference list for markdown output

5. **`clinical_note_parser.py`**
   - Parses clinical note summaries
   - Extracts patient demographics, condition, comorbidities
   - Identifies treatment decisions and contraindications

6. **`pico_extractor.py`**
   - Extracts PICO from clinical questions
   - Constructs PICO from parsed clinical context
   - Generates PubMed search queries

7. **`evidence_pyramid_classifier.py`**
   - Classifies articles by evidence level
   - Sorts by quality (highest first)
   - Filters by evidence level range

8. **`jbi_checklist.py`**
   - Performs JBI critical appraisal
   - Calculates quality scores (0-100%)
   - Provides High/Moderate/Low ratings

### Reference Materials

Located in `reference/` directory:

- **`evidence_levels.md`** - Evidence pyramid reference guide
- **`jbi_criteria.md`** - JBI critical appraisal checklists
- **`pico_guidelines.md`** - PICO framework guidelines
- **`medical_specialties.yaml`** - Search year range rules by specialty

### Example Outputs

Located in `examples/` directory:

- **`stroke-vte-prophylaxis-lmwh-vs-ufh-ebm-analysis.md`** - Complete EBM analysis for stroke VTE prophylaxis (cardiovascular)
- **`iliotibial-band-syndrome-treatment-modalities-ebm-analysis.md`** - Complete EBM analysis for ITBS treatment (sports medicine)

These examples demonstrate the full output format including:
- PICO framework analysis
- Evidence pyramid classification
- Critical evidence tables with JBI quality scores
- Clinical bottom line and recommendations
- Practical considerations and guideline alignment
- APA 7th edition references

## MCP Tools Required

- **`mcp__MCP_DOCKER__search_pubmed`** - Primary PubMed search
- **`mcp__MCP_DOCKER__read_pubmed_paper`** - Full text access (if needed)
- **`mcp__sequential-thinking__sequentialthinking`** - For complex PICO analysis

## Customization Options

### Output Format

The skill automatically generates a **formatted markdown file** containing:
- Complete EBM analysis
- Evidence tables
- JBI assessments
- Clinical recommendations
- References

The file is saved with a descriptive name based on your clinical question:
- Example: `stroke-vte-prophylaxis-lmwh-vs-ufh-ebm-analysis.md`

### Override Search Parameters

You can customize the search:

> "Search for the last 3 years only"
> "Include observational studies, not just RCTs"
> "Focus on pediatric patients"

### Specify Evidence Level

> "Only show me meta-analyses and systematic reviews"
> "Include RCTs and observational studies"

### Change JBI Thresholds

> "Only show high-quality studies (JBI score >80%)"

## Interpreting JBI Quality Scores

- **High Quality (80-100%)**: Meets most critical appraisal criteria
- **Moderate Quality (60-79%)**: Meets some criteria, some limitations
- **Low Quality (0-59%)**: Significant limitations or unclear methodology

## Limitations

- Requires PubMed access via MCP tool
- Limited to information available in abstracts (unless full text accessed)
- JBI assessment is abstract-based; full critical appraisal requires full text
- Year range determination is heuristic-based; may need manual adjustment

## Best Practices

1. **Be Specific with Your Question**
   - ❌ "Antibiotics for pneumonia"
   - ✅ "Respiratory fluoroquinolone vs beta-lactam plus macrolide for elderly patients with severe CAP"

2. **Provide Complete Clinical Notes**
   - Include age, sex, comorbidities, allergies, clinical context

3. **Review High-Quality Evidence First**
   - Start with meta-analyses and systematic reviews
   - Then check recent large RCTs

4. **Consider Patient Factors**
   - Evidence from general populations may not apply to patients with multiple comorbidities

5. **Check for Conflicts of Interest**
   - Industry-sponsored studies may have bias

## Example Clinical Questions by Specialty

**Cardiology**
- "DOAC vs warfarin for atrial fibrillation in elderly with CKD"

**Infectious Diseases**
- "Short-course vs long-course antibiotics for uncomplicated UTI"

**Oncology**
- "Immunotherapy vs chemotherapy for metastatic NSCLC with PD-L1 >50%"

**Pediatrics**
- "Amoxicillin vs observation for acute otitis media in children 2-12 years"

**Emergency Medicine**
- "Chest CT vs observation for low-risk chest pain in ED"

## Keywords for Triggering

- evidence
- literature search
- PubMed
- clinical question
- treatment decision
- what is the evidence
- find studies
- systematic review
- meta-analysis
- RCT
- clinical research
- PICO
- evidence-based medicine
- best practice
- guideline

## Related Skills

This skill works well with:
- Academic research skills
- Medical knowledge skills
- Critical appraisal skills
- Clinical decision support skills

## Version Information

- **Version**: 1.3.0
- **Last Updated**: January 2026
- **Dependencies**: MCP PubMed tools, Python 3.7+, PyYAML
- **Author**: Claude Code Skills Factory
- **Changes**:
  - v1.3.0: **Added complete orchestrator system with markdown file generation**
    - Added `ebm_analyzer.py` main orchestrator integrating all components
    - Added `markdown_generator.py` for formatted markdown output
    - Added `specialty_classifier.py` for automatic year range determination
    - Added `apa_formatter.py` for APA 7th edition citations
    - Implemented two-pass MCP PubMed integration workflow
    - Markdown files now automatically generated with descriptive naming
  - v1.2.0: Added example outputs demonstrating complete EBM analysis workflow
  - v1.1.0: Added markdown file output functionality
  - v1.0.0: Initial release

## Output File Format

The skill generates a comprehensive markdown file with the following structure:

```markdown
# Evidence-Based Medicine Analysis: [Clinical Topic]

**Date:** [Analysis Date]
**Clinical Question:** [PICO Question]
**Search Range:** [Year Range]
**PubMed Results:** [Number of Articles]

## PICO Framework
[P-I-C-O Table]

## Evidence Pyramid Summary
[Evidence Level Counts]

## Critical Evidence Table
[Detailed Evidence Table with Study Details]

## JBI Critical Appraisal
[Quality Assessments for Key Studies]

## Clinical Bottom Line
[Efficacy and Safety Summary]

## Recommendation
[Strength, Quality, Dosing, etc.]

## Practical Considerations
[Dosing, Contraindications, Special Populations]

## Guideline Alignment
[Comparison with Major Guidelines]

## References
[APA 7th Edition Citations]

## Key Takeaways
[Clinician-Facing Summary]
```

## References

- Joanna Briggs Institute. (2020). Critical Appraisal Tools.
- Richardson, W. S., et al. (1995). The well-built clinical question.
- Centre for Evidence-Based Medicine. Oxford CEBM Levels of Evidence.

---

**For more information about using this skill or to report issues, refer to the project documentation.**
