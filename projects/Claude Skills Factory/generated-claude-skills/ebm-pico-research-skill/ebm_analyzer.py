#!/usr/bin/env python3
"""
EBM PICO Research Orchestrator

Main orchestrator that integrates all EBM-PICO components:
- Accepts clinical notes or direct questions
- Orchestrates PubMed search via MCP
- Classifies evidence by pyramid level
- Performs JBI critical appraisal
- Generates formatted markdown output

Usage:
    python ebm_analyzer.py --question "clinical question"
    python ebm_analyzer.py --note "clinical note text"
    python ebm_analyzer.py --pubmed-results results.json --pico pico.json
"""

import argparse
import json
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional

# Import existing components
sys.path.append(str(Path(__file__).parent))
from clinical_note_parser import ClinicalNoteParser
from pico_extractor import PICOExtractor
from evidence_pyramid_classifier import EvidencePyramidClassifier
from jbi_checklist import JBIChecklist

# Import new components
from markdown_generator import MarkdownGenerator
from apa_formatter import APAFormatter
from specialty_classifier import SpecialtyClassifier


class EBMAnalyzer:
    """Main orchestrator for EBM-PICO research workflow."""

    def __init__(self, output_dir: str = None):
        """
        Initialize the EBM analyzer.

        Args:
            output_dir: Directory for markdown output (default: current directory)
        """
        self.output_dir = Path(output_dir) if output_dir else Path.cwd()

        # Initialize components
        self.note_parser = ClinicalNoteParser()
        self.pico_extractor = PICOExtractor()
        self.evidence_classifier = EvidencePyramidClassifier()
        self.jbi_checklist = JBIChecklist()
        self.specialty_classifier = SpecialtyClassifier()
        self.markdown_generator = MarkdownGenerator()
        self.apa_formatter = APAFormatter()

    def analyze_from_question(
        self,
        question: str,
        pubmed_results: Optional[List[Dict]] = None
    ) -> str:
        """
        Analyze evidence for a direct clinical question.

        Args:
            question: Clinical question text
            pubmed_results: Optional pre-fetched PubMed results from MCP tool

        Returns:
            Path to generated markdown file, or "PENDING_PUBMED_SEARCH"
        """
        # Step 1: Extract PICO from question
        pico = self.pico_extractor.extract_from_question(question)

        # Step 2: Determine search year range
        search_years = self.specialty_classifier.determine_search_range(
            pico.get('P', ''),
            pico.get('I', ''),
            pico.get('original_question', '')
        )

        # Step 3: Process PubMed results
        if not pubmed_results:
            return self._request_pubmed_search(pico, search_years)

        # Step 4: Classify evidence
        classified_articles = self._classify_articles(pubmed_results)

        # Step 5: Perform JBI assessment
        assessed_articles = self._assess_articles(classified_articles)

        # Step 6: Generate analysis summary
        analysis_summary = self._generate_summary(pico, assessed_articles, search_years)

        # Step 7: Generate markdown
        markdown_content = self.markdown_generator.generate_markdown(
            pico=pico,
            articles=assessed_articles,
            summary=analysis_summary,
            search_years=search_years,
            source='question'
        )

        # Step 8: Write to file
        output_path = self._generate_filename(pico, 'question')
        self._write_markdown(output_path, markdown_content)

        return str(output_path)

    def analyze_from_note(
        self,
        clinical_note: str,
        pubmed_results: Optional[List[Dict]] = None
    ) -> str:
        """
        Analyze evidence from a clinical note.

        Args:
            clinical_note: Clinical note text
            pubmed_results: Optional pre-fetched PubMed results from MCP tool

        Returns:
            Path to generated markdown file, or "PENDING_PUBMED_SEARCH"
        """
        # Step 1: Parse clinical note
        context = self.note_parser.parse(clinical_note)

        # Step 2: Extract PICO from context
        pico = self.pico_extractor.extract_from_context(context)

        # Step 3: Determine search year range
        condition = context.get('primary_condition', {}).get('diagnosis', '')
        search_years = self.specialty_classifier.determine_search_range(
            pico.get('P', ''),
            pico.get('I', ''),
            condition
        )

        # Step 4: Process PubMed results
        if not pubmed_results:
            return self._request_pubmed_search(pico, search_years, context)

        # Step 5-8: Same as question workflow
        classified_articles = self._classify_articles(pubmed_results)
        assessed_articles = self._assess_articles(classified_articles)
        analysis_summary = self._generate_summary(pico, assessed_articles, search_years)
        markdown_content = self.markdown_generator.generate_markdown(
            pico=pico,
            articles=assessed_articles,
            summary=analysis_summary,
            search_years=search_years,
            source='clinical_note',
            context=context
        )
        output_path = self._generate_filename(pico, 'clinical_note')
        self._write_markdown(output_path, markdown_content)

        return str(output_path)

    def analyze_from_pubmed_results(
        self,
        pubmed_results: List[Dict],
        pico: Dict[str, Any],
        search_years: Dict[str, int]
    ) -> str:
        """
        Process pre-fetched PubMed results with provided PICO.

        Args:
            pubmed_results: PubMed search results from MCP tool
            pico: Pre-extracted PICO dictionary
            search_years: Search year range dict with 'start' and 'end'

        Returns:
            Path to generated markdown file
        """
        # Classify and assess
        classified_articles = self._classify_articles(pubmed_results)
        assessed_articles = self._assess_articles(classified_articles)

        # Generate summary and markdown
        analysis_summary = self._generate_summary(pico, assessed_articles, search_years)
        markdown_content = self.markdown_generator.generate_markdown(
            pico=pico,
            articles=assessed_articles,
            summary=analysis_summary,
            search_years=search_years,
            source='pubmed_results'
        )

        # Write to file
        output_path = self._generate_filename(pico, 'pubmed')
        self._write_markdown(output_path, markdown_content)

        return str(output_path)

    def _request_pubmed_search(
        self,
        pico: Dict,
        search_years: Dict,
        context: Optional[Dict] = None
    ) -> str:
        """
        Generate structured request for PubMed search via MCP tool.

        Prints JSON structure for Claude Code to capture and execute.

        Returns:
            "PENDING_PUBMED_SEARCH" indicator
        """
        search_query = self.pico_extractor.format_search_query(pico)

        request = {
            'action': 'search_pubmed',
            'query': search_query,
            'year_range': search_years,
            'pico': pico,
            'max_results': 100
        }

        # Print to stdout for Claude Code to capture
        print("PUBMED_SEARCH_REQUEST:")
        print(json.dumps(request, indent=2))

        return "PENDING_PUBMED_SEARCH"

    def _classify_articles(self, articles: List[Dict]) -> List[Dict]:
        """
        Classify articles by evidence pyramid level.

        Args:
            articles: List of PubMed article dictionaries

        Returns:
            Articles with evidence_level field added
        """
        classified = []
        for article in articles:
            classified_article = self.evidence_classifier.classify_article(article)
            classified.append(classified_article)
        return classified

    def _assess_articles(self, articles: List[Dict]) -> List[Dict]:
        """
        Perform JBI critical appraisal on articles.

        Args:
            articles: Classified articles

        Returns:
            Articles with jbi_assessment field added
        """
        assessed = []
        for article in articles:
            assessed_article = self.jbi_checklist.assess_article(article)
            assessed.append(assessed_article)
        return assessed

    def _generate_summary(
        self,
        pico: Dict,
        articles: List[Dict],
        search_years: Dict
    ) -> Dict[str, Any]:
        """
        Generate analysis summary from processed articles.

        Args:
            pico: PICO dictionary
            articles: Classified and assessed articles
            search_years: Year range dictionary

        Returns:
            Summary dictionary with level_counts, top_studies, key_findings, etc.
        """
        # Count by evidence level
        level_counts = {}
        for article in articles:
            level = article.get('evidence_level', 6)
            level_counts[level] = level_counts.get(level, 0) + 1

        # Extract top studies (by evidence level and quality)
        top_studies = self._get_top_evidence(articles, max_articles=10)

        # Extract key findings
        key_findings = self._extract_key_findings(top_studies)

        # Calculate aggregate quality metrics
        quality_summary = self._calculate_quality_summary(articles)

        return {
            'total_articles': len(articles),
            'level_counts': level_counts,
            'top_studies': top_studies,
            'key_findings': key_findings,
            'quality_summary': quality_summary,
            'search_years': search_years
        }

    def _get_top_evidence(
        self,
        articles: List[Dict],
        max_articles: int = 10
    ) -> List[Dict]:
        """
        Get top evidence articles prioritized by level and quality.

        Args:
            articles: Classified and assessed articles
            max_articles: Maximum number of articles to return

        Returns:
            Top articles sorted by evidence level and JBI quality
        """
        # Sort by evidence level (ascending) then by quality score (descending)
        sorted_articles = sorted(
            articles,
            key=lambda a: (
                a.get('evidence_level', 6),
                -a.get('jbi_assessment', {}).get('quality_percent', 0)
            )
        )

        return sorted_articles[:max_articles]

    def _extract_key_findings(self, articles: List[Dict]) -> List[str]:
        """
        Extract key findings from article abstracts.

        Args:
            articles: List of articles

        Returns:
            List of formatted key findings
        """
        findings = []

        for article in articles[:10]:  # Top 10 studies
            abstract = article.get('abstract', '')
            title = article.get('title', '')
            authors = article.get('firstAuthor', 'Unknown')
            year = article.get('pubYear', 'Unknown')

            # Extract sentences with statistical findings
            patterns = [
                r'(?:significant|reduced|increased|improved|efficacy|effective).*?[.!?](?:\s|$)',
                r'(?:RR|OR|HR|CI|p-value|p < |p=).*?[.!?](?:\s|$)'
            ]

            for pattern in patterns:
                matches = re.finditer(pattern, abstract, re.IGNORECASE)
                for match in matches:
                    finding = match.group(0).strip()
                    if len(finding) > 20 and len(finding) < 200:
                        findings.append(f"**{authors} et al. ({year})**: {finding}")

        return findings[:20]  # Max 20 findings

    def _calculate_quality_summary(self, articles: List[Dict]) -> Dict:
        """
        Calculate aggregate quality metrics.

        Args:
            articles: Assessed articles

        Returns:
            Dictionary with quality metrics
        """
        high_count = sum(
            1 for a in articles
            if a.get('jbi_assessment', {}).get('quality') == 'High'
        )
        moderate_count = sum(
            1 for a in articles
            if a.get('jbi_assessment', {}).get('quality') == 'Moderate'
        )
        low_count = sum(
            1 for a in articles
            if a.get('jbi_assessment', {}).get('quality') == 'Low'
        )

        avg_score = sum(
            a.get('jbi_assessment', {}).get('quality_percent', 0)
            for a in articles
        ) / max(len(articles), 1)

        return {
            'high_quality': high_count,
            'moderate_quality': moderate_count,
            'low_quality': low_count,
            'average_score': round(avg_score, 1)
        }

    def _generate_filename(self, pico: Dict, source: str) -> Path:
        """
        Generate descriptive filename for markdown output.

        Format: {condition}-{intervention}-vs-{comparison}-ebm-analysis-{date}.md

        Args:
            pico: PICO dictionary
            source: Source type ('question', 'clinical_note', 'pubmed')

        Returns:
            Path object for output file
        """
        # Extract key terms
        condition = self._sanitize_filename(pico.get('P', 'unknown'))
        intervention = self._sanitize_filename(pico.get('I', 'treatment'))
        comparison = self._sanitize_filename(pico.get('C', '')) if pico.get('C') else ''

        # Build filename
        if comparison:
            base_name = f"{condition}-{intervention}-vs-{comparison}"
        else:
            base_name = f"{condition}-{intervention}"

        # Add date and suffix
        date_str = datetime.now().strftime('%Y%m%d')
        filename = f"{base_name}-ebm-analysis-{date_str}.md"

        return self.output_dir / filename

    def _sanitize_filename(self, text: str) -> str:
        """
        Clean text for safe filename.

        Args:
            text: Raw text string

        Returns:
            Sanitized filename-safe string
        """
        # Remove special chars, replace spaces with hyphens
        cleaned = re.sub(r'[^\w\s-]', '', text.lower())
        cleaned = re.sub(r'[\s_]+', '-', cleaned)
        return cleaned[:50]  # Limit length

    def _write_markdown(self, path: Path, content: str):
        """
        Write markdown content to file.

        Args:
            path: Output file path
            content: Markdown content
        """
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"\n✅ Markdown file generated: {path}")


def main():
    """Command-line interface for EBM analyzer."""
    parser = argparse.ArgumentParser(
        description='EBM-PICO Research Orchestrator'
    )
    parser.add_argument(
        '--question',
        type=str,
        help='Direct clinical question'
    )
    parser.add_argument(
        '--note',
        type=str,
        help='Clinical note text'
    )
    parser.add_argument(
        '--pubmed-results',
        type=str,
        help='JSON file with PubMed results from MCP tool'
    )
    parser.add_argument(
        '--pico',
        type=str,
        help='JSON file with pre-extracted PICO'
    )
    parser.add_argument(
        '--search-years',
        type=str,
        help='Search year range as JSON: {"start": 2020, "end": 2025}'
    )
    parser.add_argument(
        '--output-dir',
        type=str,
        default='.',
        help='Output directory for markdown files'
    )

    args = parser.parse_args()

    analyzer = EBMAnalyzer(output_dir=args.output_dir)

    # Route to appropriate workflow
    if args.question:
        result = analyzer.analyze_from_question(args.question)
    elif args.note:
        result = analyzer.analyze_from_note(args.note)
    elif args.pubmed_results and args.pico:
        with open(args.pubmed_results) as f:
            articles = json.load(f)
        with open(args.pico) as f:
            pico = json.load(f)
        years = json.loads(args.search_years) if args.search_years else {'start': 2018, 'end': 2025}
        result = analyzer.analyze_from_pubmed_results(articles, pico, years)
    else:
        parser.error("Must provide --question, --note, or --pubmed-results with --pico")

    print(f"\nAnalysis complete: {result}")


if __name__ == '__main__':
    main()
