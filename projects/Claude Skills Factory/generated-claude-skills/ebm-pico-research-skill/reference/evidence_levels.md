# Evidence Pyramid Levels

## Level 1: Systematic Reviews & Meta-Analyses (Highest Quality)

**Definition:**
- **Systematic Review**: Comprehensive survey of primary studies that summarizes and synthesizes evidence using explicit, pre-specified methods
- **Meta-Analysis**: Statistical synthesis of results from multiple studies to produce a single summary estimate

**PubMed Publication Types:**
- `meta-analysis`
- `systematic review`
- `research support, u.s. gov't` + review

**Key Features:**
- Addresses a focused clinical question
- Uses explicit methods to search, appraise, and synthesize literature
- Includes comprehensive literature search
- Assesses quality of included studies
- Reduces bias through systematic approach

## Level 2: Randomized Controlled Trials (RCTs)

**Definition:**
- Experimental study where participants are randomly assigned to intervention or control groups

**PubMed Publication Types:**
- `clinical trial`
- `clinical trial, phase i`
- `clinical trial, phase ii`
- `clinical trial, phase iii`
- `clinical trial, phase iv`
- `randomized controlled trial`
- `controlled clinical trial`

**Key Features:**
- Random allocation minimizes selection bias
- Blinding (single/double) reduces performance and detection bias
- Prospective design
- Considered gold standard for intervention studies

## Level 3: Cohort Studies

**Definition:**
- Observational study following two or more groups over time to compare outcomes

**PubMed Publication Types:**
- `cohort study`
- `follow-up study`
- `longitudinal studies`
- `observational study`

**Key Features:**
- Prospective or retrospective design
- Participants classified by exposure status
- Incidence can be calculated
- Can study multiple outcomes
- Subject to confounding but less than case-control

## Level 4: Case-Control Studies

**Definition:**
- Observational study comparing people with outcome (cases) to those without (controls)

**PubMed Publication Types:**
- `case-control studies`
- `retrospective studies`

**Key Features:**
- Retrospective design
- Efficient for rare outcomes
- Prone to recall and selection bias
- Cannot calculate incidence
- Subject to confounding

## Level 5: Case Series & Case Reports

**Definition:**
- Descriptive studies reporting on individual patients or series

**PubMed Publication Types:**
- `case reports`
- `case series`

**Key Features:**
- No control group
- Descriptive only
- Useful for rare conditions or new interventions
- Cannot establish causality
- Highest risk of bias

## Level 6: Animal Research & In Vitro Studies (Lowest for Clinical Evidence)

**Definition:**
- Preclinical studies in animals or laboratory settings

**PubMed Publication Types:**
- `animal experiment`
- `in vitro`
- `animals`

**Key Features:**
- Not directly applicable to humans
- Useful for mechanism exploration
- Requires human trials for clinical application

---

## Evidence Classification Rules for PubMed Results

1. **Primary Sorting**: Use `pubmedPublicationTypes` field
2. **Priority Hierarchy**:
   - If contains `meta-analysis` OR `systematic review` → Level 1
   - If contains `randomized controlled trial` OR `clinical trial` → Level 2
   - If contains `cohort study` → Level 3
   - If contains `case-control studies` → Level 4
   - If contains `case reports` → Level 5
   - If contains `animal experiment` OR `in vitro` → Level 6
3. **Default**: If publication type unclear, classify by study design description in abstract

## Special Considerations

### Practice Guidelines
- Clinical practice guidelines are often Level 1a (based on systematic reviews)
- Check if guideline references systematic reviews or expert consensus

### Narrative Reviews
- Not systematic reviews
- Generally classified as Level 5 (expert opinion)
- Authors select articles subjectively

### Cross-Sectional Studies
- Observational studies at single time point
- Generally classified between Level 3 and 4
- Useful for prevalence, not causation
