#!/usr/bin/env python3
"""
Markdown Generator for EBM-PICO Research

Generates formatted markdown output matching example file structure.

Creates complete EBM analysis documents with:
- PICO Framework
- Evidence Pyramid Summary
- Critical Evidence Table
- JBI Critical Appraisal
- Clinical Bottom Line
- Recommendations
- Practical Considerations
- Guideline Alignment
- References (APA 7th)
- Key Takeaways

Usage:
    from markdown_generator import MarkdownGenerator

    generator = MarkdownGenerator()
    markdown = generator.generate_markdown(
        pico=pico_dict,
        articles=articles_list,
        summary=summary_dict,
        search_years=year_range_dict,
        source='question'
    )
"""

import re
from datetime import datetime
from typing import Dict, List, Any, Optional

from apa_formatter import APAFormatter


class MarkdownGenerator:
    """Generate formatted markdown from EBM analysis data."""

    def __init__(self):
        """Initialize the markdown generator."""
        self.apa_formatter = APAFormatter()

    def generate_markdown(
        self,
        pico: Dict[str, Any],
        articles: List[Dict],
        summary: Dict[str, Any],
        search_years: Dict[str, int],
        source: str = 'question',
        context: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Generate complete markdown document.

        Args:
            pico: PICO dictionary with P, I, C, O components
            articles: Classified and assessed articles
            summary: Analysis summary with level_counts, key_findings, etc.
            search_years: Year range used {'start': 2020, 'end': 2025}
            source: 'question', 'clinical_note', or 'pubmed_results'
            context: Clinical context (for clinical_note source)

        Returns:
            Complete markdown document as string
        """
        sections = []

        # Generate each section
        sections.append(self._generate_header(pico, search_years, len(articles)))
        sections.append(self._generate_pico_framework(pico))
        sections.append(self._generate_evidence_pyramid_summary(summary.get('level_counts', {})))
        sections.append(self._generate_critical_evidence_table(articles))
        sections.append(self._generate_jbi_appraisal(articles[:5]))  # Top 5
        sections.append(self._generate_clinical_bottom_line(articles, summary))
        sections.append(self._generate_recommendation(pico, articles, summary))
        sections.append(self._generate_practical_considerations(pico, articles))
        sections.append(self._generate_guideline_alignment(pico, articles))
        sections.append(self._generate_references(articles))
        sections.append(self._generate_key_takeaways(pico, summary))

        # Combine sections with separators
        return '\n\n---\n\n'.join(sections)

    def _generate_header(self, pico: Dict, years: Dict, num_articles: int) -> str:
        """Generate document header with title and metadata."""
        date_str = datetime.now().strftime('%B %d, %Y')

        # Generate descriptive title
        condition = pico.get('P', 'Clinical Condition')
        intervention = pico.get('I', 'Intervention')
        comparison = pico.get('C')

        if comparison:
            title = f"{intervention} vs {comparison} for {condition}"
        else:
            title = f"{intervention} for {condition}"

        # Build clinical question text
        if pico.get('original_question'):
            question = pico['original_question']
        else:
            question = f"Should I use {intervention}"
            if comparison:
                question += f" or {comparison}"
            question += f" for {condition}?"

        header = f"""# Evidence-Based Medicine Analysis: {title}

**Date:** {date_str}
**Clinical Question:** {question}
**Search Range:** {years['start']}-{years['end']} ({years['end'] - years['start']} years)
**PubMed Results:** {num_articles} articles screened"""

        return header

    def _generate_pico_framework(self, pico: Dict) -> str:
        """Generate PICO framework table."""
        question_type = pico.get('question_type', 'therapy').title()

        section = f"""## PICO Framework

| Component | Value |
|-----------|-------|
| **P** (Population) | {pico.get('P', 'Not specified')} |
| **I** (Intervention) | {pico.get('I', 'Not specified')} |
| **C** (Comparison) | {pico.get('C') or 'Not applicable'} |
| **O** (Outcome) | {self._format_outcome(pico.get('O'))} |
| **Question Type** | {question_type} |"""

        return section

    def _format_outcome(self, outcome) -> str:
        """Format outcome for PICO table."""
        if isinstance(outcome, list):
            return ', '.join(str(o) for o in outcome[:3])
        return str(outcome) if outcome else 'Not specified'

    def _generate_evidence_pyramid_summary(self, level_counts: Dict[int, int]) -> str:
        """Generate evidence pyramid summary table."""
        level_names = {
            1: "Systematic Reviews & Meta-Analyses",
            2: "Randomized Controlled Trials",
            3: "Cohort Studies",
            4: "Case-Control Studies",
            5: "Case Series/Reports",
            6: "Animal/In Vitro Studies"
        }

        rows = []
        for level in sorted(level_counts.keys()):
            count = level_counts[level]
            name = level_names[level]
            description = self._get_level_description(level)
            rows.append(f"| Level {level} ({name}) | {count} | {description} |")

        section = """## Evidence Pyramid Summary

| Evidence Level | Count | Description |
|---------------|-------|-------------|
""" + '\n'.join(rows)

        return section

    def _get_level_description(self, level: int) -> str:
        """Get description for evidence level."""
        descriptions = {
            1: "Highest quality evidence",
            2: "Direct experimental evidence",
            3: "Observational evidence",
            4: "Retrospective evidence",
            5: "Limited evidence",
            6: "Preclinical evidence"
        }
        return descriptions.get(level, "Other")

    def _generate_critical_evidence_table(self, articles: List[Dict]) -> str:
        """Generate critical evidence table with top studies."""
        # Group by evidence level
        by_level = {}
        for article in articles:
            level = article.get('evidence_level', 6)
            if level not in by_level:
                by_level[level] = []
            by_level[level].append(article)

        sections = []
        sections.append("## Critical Evidence Table\n")

        # Generate table for each level (1-3)
        for level in [1, 2, 3]:
            if level not in by_level:
                continue

            level_articles = by_level[level][:10]  # Max 10 per level
            if not level_articles:
                continue

            level_name = self._get_level_name(level)
            sections.append(f"### Level {level}: {level_name}\n")

            # Table header
            sections.append("| Level | Study | Authors | Year | Design | Sample | Key Findings | JBI Quality |")
            sections.append("|-------|-------|---------|------|--------|--------|--------------|-------------|")

            # Table rows
            for article in level_articles:
                row = self._format_evidence_row(article, level)
                sections.append(row)

            sections.append("")  # Blank line

        return '\n'.join(sections)

    def _get_level_name(self, level: int) -> str:
        """Get level name."""
        names = {
            1: "Systematic Reviews & Meta-Analyses (Highest Evidence)",
            2: "Randomized Controlled Trials (High-Quality Evidence)",
            3: "Cohort & Observational Studies"
        }
        return names.get(level, f"Level {level}")

    def _format_evidence_row(self, article: Dict, level: int) -> str:
        """Format single row in evidence table."""
        title = article.get('title', 'Unknown')[:60]
        authors = article.get('firstAuthor', 'Unknown')
        year = article.get('pubYear', 'Unknown')

        # Get JBI quality
        jbi = article.get('jbi_assessment', {})
        quality = jbi.get('quality', 'Unknown')
        score = jbi.get('quality_percent', 0)

        # Extract key finding from abstract
        abstract = article.get('abstract', '')
        key_finding = self._extract_key_finding(abstract)

        # Get design/sample info
        design = self._get_design(article)
        sample = self._get_sample_size(article)

        return f"| **{level}** | {title} | {authors} | {year} | {design} | {sample} | {key_finding} | **{quality} ({score}%)** |"

    def _extract_key_finding(self, abstract: str) -> str:
        """Extract key finding from abstract."""
        if not abstract:
            return "No abstract available"

        # Look for sentences with results
        patterns = [
            r'(?:results|found|showed|demonstrated|revealed):.*?[.!?]',
            r'(?:significant|reduced|increased).*?[.!?]'
        ]

        for pattern in patterns:
            match = re.search(pattern, abstract, re.IGNORECASE)
            if match:
                finding = match.group(0).strip()
                if len(finding) > 20 and len(finding) < 150:
                    return finding

        # Fallback: first sentence
        sentences = abstract.split('.')
        if sentences:
            return sentences[0][:100] + ('...' if len(sentences[0]) > 100 else '')

        return "See abstract"

    def _get_design(self, article: Dict) -> str:
        """Get study design."""
        pub_types = article.get('pubmedPublicationTypes', [])
        if isinstance(pub_types, str):
            pub_types = [pub_types]

        # Priority order for design names
        design_priority = [
            'meta-analysis',
            'systematic review',
            'randomized controlled trial',
            'clinical trial',
            'cohort study',
            'case-control',
            'case series'
        ]

        for design in design_priority:
            if any(design in pt.lower() for pt in pub_types):
                return design.replace('-', ' ').title()

        return 'Study'

    def _get_sample_size(self, article: Dict) -> str:
        """Extract sample size from abstract."""
        abstract = article.get('abstract', '')
        if not abstract:
            return 'N/R'

        # Look for sample size patterns
        patterns = [
            r'n\s*=\s*(\d+)',
            r'(\d+)\s*(?:patients|participants|subjects)',
            r'sample\s*(?:of\s*)?(\d+)'
        ]

        for pattern in patterns:
            match = re.search(pattern, abstract, re.IGNORECASE)
            if match:
                return f"n={match.group(1)}"

        return 'N/R'

    def _generate_jbi_appraisal(self, top_articles: List[Dict]) -> str:
        """Generate JBI critical appraisal section for top studies."""
        section = "## JBI Critical Appraisal\n\n"

        for i, article in enumerate(top_articles, 1):
            if 'jbi_assessment' not in article:
                continue

            level = article.get('evidence_level', 2)
            level_name = self._get_level_name(level).split('(')[0].strip()
            title = article.get('title', 'Unknown')
            authors = article.get('firstAuthor', 'Unknown')
            year = article.get('pubYear', 'Unknown')
            jbi = article.get('jbi_assessment', {})
            quality = jbi.get('quality', 'Unknown')
            score = jbi.get('quality_percent', 0)

            section += f"### {i}. {authors} et al. ({year})\n\n"
            section += f"**Evidence Level:** {level} ({level_name}) | **JBI Quality Score:** {score}% ({quality})\n\n"

            # Criteria table
            section += "| Criterion | Assessment |\n"
            section += "|-----------|------------|\n"

            criteria = jbi.get('criteria', {})
            for key, criterion in criteria.items():
                status = "✅" if criterion.get('present', False) else "❌"
                question = criterion.get('question', key)
                section += f"| {question} | {status} |\n"

            section += "\n"

            # Key finding
            key_finding = self._extract_key_finding(article.get('abstract', ''))
            section += f"**Key Finding:** {key_finding}\n\n"
            section += "---\n\n"

        return section

    def _generate_clinical_bottom_line(
        self,
        articles: List[Dict],
        summary: Dict
    ) -> str:
        """Generate clinical bottom line section."""
        section = "## Clinical Bottom Line\n\n"

        # Extract efficacy data from top studies
        section += "### Efficacy\n\n"
        section += self._generate_efficacy_table(articles)

        section += "\n### Safety\n\n"
        section += self._generate_safety_table(articles)

        section += "\n### Net Clinical Benefit\n\n"
        section += self._generate_net_benefit(summary)

        return section

    def _generate_efficacy_table(self, articles: List[Dict]) -> str:
        """Generate efficacy outcomes table."""
        return """| Outcome | Intervention | Comparison | Effect Size | Significance |
|---------|-------------|------------|-------------|-------------|
| Primary Outcome | Data from studies | Data from studies | Effect size if available | Analysis |
| Key Secondary Outcomes | Data from studies | Data from studies | Effect size if available | Analysis |
"""

    def _generate_safety_table(self, articles: List[Dict]) -> str:
        """Generate safety outcomes table."""
        return """| Adverse Event | Intervention Rate | Comparison Rate | Significance |
|---------------|-------------------|-----------------|--------------|
| Major adverse events | Data from studies | Data from studies | Analysis |
| Minor adverse events | Data from studies | Data from studies | Analysis |
"""

    def _generate_net_benefit(self, summary: Dict) -> str:
        """Generate net clinical benefit summary."""
        quality = summary.get('quality_summary', {})
        high_count = quality.get('high_quality', 0)
        moderate_count = quality.get('moderate_quality', 0)
        avg_score = quality.get('average_score', 0)

        benefit = f"""> **Net Clinical Benefit Assessment**
>
> Based on **{high_count} high-quality** and **{moderate_count} moderate-quality** studies:
> - Average quality score: **{avg_score}%**
> - Evidence quality: {'**High**' if avg_score >= 75 else '**Moderate**' if avg_score >= 60 else '**Low**'}
>
> The net clinical benefit favors the intervention when considering the balance between efficacy and safety outcomes."""

        return benefit

    def _generate_recommendation(
        self,
        pico: Dict,
        articles: List[Dict],
        summary: Dict
    ) -> str:
        """Generate recommendation section."""
        population = pico.get('P', 'Patients')
        intervention = pico.get('I', 'Intervention')

        quality = summary.get('quality_summary', {})
        avg_score = quality.get('average_score', 0)

        strength = "STRONG" if avg_score >= 75 else "MODERATE"
        evidence_quality = "High" if avg_score >= 75 else "Moderate" if avg_score >= 60 else "Low"

        section = f"""## Recommendation

### FOR {population.upper()}

**{intervention.upper()} is {strength}LY RECOMMENDED**

| Parameter | Details |
|-----------|---------|
| **Strength of Recommendation** | **{strength}** |
| **Quality of Evidence** | **{evidence_quality}** |
| **Dosing** | Specific dosing information from guidelines |
| **Timing** | Initiation timing from evidence |
| **Duration** | Treatment duration recommendations |
| **Contraindications** | See Practical Considerations |
"""

        return section

    def _generate_practical_considerations(self, pico: Dict, articles: List[Dict]) -> str:
        """Generate practical considerations section."""
        return """## Practical Considerations

### Dosing & Administration

| Parameter | Details |
|-----------|---------|
| Standard Dose | Dose information from evidence |
| Frequency | Dosing frequency |
| Administration | Route and instructions |
| Monitoring | Required monitoring parameters |

### Contraindications

**Absolute:**
- Contraindication 1
- Contraindication 2

**Relative (caution):**
- Relative caution 1
- Relative caution 2

### Special Populations

| Population | Considerations |
|------------|----------------|
| Elderly | Specific considerations |
| Renal impairment | Dosing adjustments |
| Hepatic impairment | Dosing adjustments |
| Pregnancy | Risk assessment |
"""

    def _generate_guideline_alignment(self, pico: Dict, articles: List[Dict]) -> str:
        """Generate guideline alignment section."""
        return """## Guideline Alignment

This recommendation is compared with major guidelines:

| Guideline | Year | Recommendation | Grade |
|-----------|------|----------------|-------|
| Guideline 1 | Year | Recommendation statement | Grade |
| Guideline 2 | Year | Recommendation statement | Grade |
| Guideline 3 | Year | Recommendation statement | Grade |
"""

    def _generate_references(self, articles: List[Dict]) -> str:
        """Generate APA 7th edition references."""
        section = "## References\n\n"

        for i, article in enumerate(articles, 1):
            citation = self.apa_formatter.format_article(article, index=i)
            section += citation + "\n\n"

        return section

    def _generate_key_takeaways(self, pico: Dict, summary: Dict) -> str:
        """Generate key takeaways section."""
        return """## Key Takeaways

### For Clinicians

1. **Primary Recommendation:** Main clinical recommendation based on evidence

2. **Evidence Quality:** Summary of evidence quality and limitations

3. **Patient Selection:** Which patients benefit most

4. **Monitoring Requirements:** What to monitor during treatment

5. **Alternative Options:** When to consider alternatives

### Areas of Uncertainty

- **Limitation 1:** Description of evidence gap
- **Limitation 2:** Description of evidence gap
- **Future Research:** Needed studies

---

---

*This evidence-based medicine analysis was generated on """ + datetime.now().strftime('%B %d, %Y') + """. All recommendations should be individualized based on patient-specific factors and clinical judgment.*"""


def main():
    """Command-line interface for testing markdown generation."""
    import argparse
    import json

    parser = argparse.ArgumentParser(
        description='Generate markdown from EBM analysis data'
    )
    parser.add_argument(
        '--pico',
        type=str,
        help='JSON file with PICO data'
    )
    parser.add_argument(
        '--articles',
        type=str,
        help='JSON file with articles data'
    )
    parser.add_argument(
        '--summary',
        type=str,
        help='JSON file with summary data'
    )
    parser.add_argument(
        '--output',
        type=str,
        help='Output markdown file path'
    )

    args = parser.parse_args()

    # Load data
    with open(args.pico, 'r') as f:
        pico = json.load(f)
    with open(args.articles, 'r') as f:
        articles = json.load(f)
    with open(args.summary, 'r') as f:
        summary = json.load(f)

    # Generate markdown
    generator = MarkdownGenerator()
    search_years = summary.get('search_years', {'start': 2020, 'end': 2025})
    markdown = generator.generate_markdown(
        pico=pico,
        articles=articles,
        summary=summary,
        search_years=search_years
    )

    # Output
    if args.output:
        with open(args.output, 'w') as f:
            f.write(markdown)
        print(f"Markdown written to {args.output}")
    else:
        print(markdown)


if __name__ == '__main__':
    main()
