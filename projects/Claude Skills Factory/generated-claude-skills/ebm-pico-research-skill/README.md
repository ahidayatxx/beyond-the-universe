# EBM PICO Research Skill

A Claude Code skill that automates evidence-based medicine (EBM) research using the PICO framework, PubMed search, and Joanna Briggs Institute (JBI) critical appraisal.

## Overview

This skill converts clinical situations or patient notes into structured PICO format, searches PubMed with intelligent year-range selection, filters results by evidence pyramid level, and performs critical appraisal using JBI criteria.

## Features

- **Dual Input Modes**: Accepts both direct clinical questions and clinical note summaries
- **Intelligent Search Year Selection**: Automatically determines appropriate search range based on medical specialty (3-15 years)
- **Evidence Pyramid Classification**: Sorts articles from Level 1 (Systematic Reviews/Meta-Analyses) to Level 6 (Animal Research)
- **JBI Critical Appraisal**: Performs quality assessment with scores (0-100%) and ratings (High/Moderate/Low)
- **Markdown Output**: Generates comprehensive EBM analysis with evidence tables, clinical recommendations, and APA 7th edition references

## Installation

### As a Claude Code Skill

1. Copy the skill directory to your Claude skills folder:
   ```bash
   cp -r ebm-pico-research-skill ~/.claude/skills/ebm-pico-research
   ```

2. Restart Claude Code or reload skills

### As a Python Module

```bash
pip install -r requirements.txt  # if requirements.txt exists
```

## Usage

### Clinical Question Example

```
Use ebm-pico-research skill: Should I use LMWH or UFH for VTE prophylaxis in stroke patients?
```

### Clinical Note Example

```
Use ebm-pico-research skill for this case:
72-year-old female, admitted with community-acquired pneumonia. CURB-65 score 3.
Comorbidities: COPD, HFpEF, CKD stage 3. Allergies: Penicillin (rash).
Decision: Antibiotic selection.
```

## Components

### Python Scripts

- **`clinical_note_parser.py`** - Parses clinical notes and extracts patient demographics, conditions, comorbidities
- **`pico_extractor.py`** - Extracts P-I-C-O elements from clinical questions or patient context
- **`evidence_pyramid_classifier.py`** - Classifies PubMed articles by evidence level (1-6)
- **`jbi_checklist.py`** - Performs JBI critical appraisal with quality scoring

### Reference Materials

- **`reference/evidence_levels.md`** - Evidence pyramid reference guide
- **`reference/jbi_criteria.md`** - JBI critical appraisal checklists
- **`reference/pico_guidelines.md`** - PICO framework guidelines
- **`reference/medical_specialties.yaml`** - Search year range rules by specialty

## Evidence Pyramid Levels

| Level | Type | Description |
|-------|------|-------------|
| 1 | Systematic Reviews & Meta-Analyses | Highest quality evidence |
| 2 | Randomized Controlled Trials | Experimental studies |
| 3 | Cohort Studies | Observational, prospective/retrospective |
| 4 | Case-Control Studies | Observational, retrospective |
| 5 | Case Series/Reports | Descriptive studies |
| 6 | Animal Research/In Vitro | Preclinical studies |

## MCP Tool Dependencies

This skill requires the following MCP tools:
- `mcp__MCP_DOCKER__search_pubmed` - Primary PubMed search
- `mcp__MCP_DOCKER__read_pubmed_paper` - Full text access
- `mcp__sequential-thinking__sequentialthinking` - Complex PICO analysis

## Python Version

Requires Python 3.7+

## License

This skill is part of the Claude Skills Factory collection.

## Version

**Version**: 1.1.0
**Last Updated**: January 2025

## Author

Claude Code Skills Factory

## Changelog

### v1.1.0 (January 2025)
- Added markdown file output functionality
- Enhanced JBI assessment capabilities

### v1.0.0
- Initial release
