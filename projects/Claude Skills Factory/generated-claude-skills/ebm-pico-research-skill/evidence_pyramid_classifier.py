#!/usr/bin/env python3
"""
Evidence Pyramid Classifier for EBM PICO Research Skill

This script classifies articles into evidence pyramid levels and sorts
them by quality.

Usage:
    python evidence_pyramid_classifier.py --articles articles.json
"""

import argparse
import json
from typing import Dict, List, Any, Optional


class EvidencePyramidClassifier:
    """Classify research articles by evidence level."""

    # Evidence pyramid levels (highest to lowest)
    EVIDENCE_LEVELS = {
        1: "Systematic Review & Meta-Analysis",
        2: "Randomized Controlled Trial",
        3: "Cohort Study",
        4: "Case-Control Study",
        5: "Case Series / Case Report",
        6: "Animal Research / In Vitro",
    }

    # Publication types for each level
    PUBLICATION_TYPE_MAP = {
        1: [
            "meta-analysis",
            "systematic review",
            "research support, u.s. gov't",
        ],
        2: [
            "randomized controlled trial",
            "clinical trial",
            "clinical trial, phase i",
            "clinical trial, phase ii",
            "clinical trial, phase iii",
            "clinical trial, phase iv",
            "controlled clinical trial",
            "pragmatic clinical trial",
        ],
        3: [
            "cohort study",
            "follow-up study",
            "longitudinal studies",
            "observational study",
            "prospective study",
        ],
        4: [
            "case-control studies",
            "retrospective studies",
            "case-control study",
        ],
        5: [
            "case reports",
            "case series",
        ],
        6: [
            "animal experiment",
            "in vitro",
            "animals",
            "animal model",
        ],
    }

    def __init__(self):
        """Initialize the classifier."""
        pass

    def classify_article(self, article: Dict[str, Any]) -> Dict[str, Any]:
        """
        Classify a single article by evidence level.

        Args:
            article: Article dictionary with PubMed metadata

        Returns:
            Article with added evidence level information
        """
        # Get publication types
        pub_types = article.get('pubmedPublicationTypes', [])
        if isinstance(pub_types, str):
            pub_types = [pub_types]

        # Classify by publication type
        evidence_level = self._classify_by_publication_type(pub_types)

        # If no publication type, try to classify by title/abstract
        if evidence_level is None:
            title = article.get('title', '')
            abstract = article.get('abstract', '')
            evidence_level = self._classify_by_text(title, abstract)

        # Default to lowest level if still unknown
        if evidence_level is None:
            evidence_level = 6  # Animal/In Vitro is default unknown

        # Add classification to article
        article['evidence_level'] = evidence_level
        article['evidence_level_name'] = self.EVIDENCE_LEVELS[evidence_level]

        return article

    def classify_articles(self, articles: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Classify multiple articles and sort by evidence level.

        Args:
            articles: List of article dictionaries

        Returns:
            Sorted list of articles with evidence levels
        """
        classified = []

        for article in articles:
            classified_article = self.classify_article(article)
            classified.append(classified_article)

        # Sort by evidence level (ascending - lower number = higher quality)
        sorted_articles = sorted(
            classified,
            key=lambda x: x.get('evidence_level', 6)
        )

        return sorted_articles

    def _classify_by_publication_type(self, pub_types: List[str]) -> Optional[int]:
        """Classify article by publication type."""
        # Normalize publication types to lowercase
        pub_types_lower = [pt.lower() for pt in pub_types]

        # Check each level (highest to lowest)
        for level, type_list in self.PUBLICATION_TYPE_MAP.items():
            for type_name in type_list:
                if any(type_name in pt for pt in pub_types_lower):
                    return level

        return None

    def _classify_by_text(self, title: str, abstract: str) -> Optional[int]:
        """Classify article by title and abstract text."""
        text = f"{title} {abstract}".lower()

        # Level 1: Meta-analysis / Systematic review
        if any(kw in text for kw in [
            'meta-analysis', 'meta analysis', 'systematic review',
            'systematic literature review', 'pooled analysis'
        ]):
            return 1

        # Level 2: Randomized controlled trial
        if any(kw in text for kw in [
            'randomized', 'randomised', 'randomized controlled trial',
            'rct', 'double-blind', 'double blind', 'single-blind',
            'single blind', 'placebo-controlled'
        ]):
            return 2

        # Level 3: Cohort study
        if any(kw in text for kw in [
            'cohort', 'prospective study', 'prospective follow-up',
            'longitudinal', 'observational cohort'
        ]):
            return 3

        # Level 4: Case-control
        if any(kw in text for kw in [
            'case-control', 'case control', 'retrospective cohort'
        ]):
            return 4

        # Level 5: Case report/series
        if any(kw in text for kw in [
            'case report', 'case series', 'single case'
        ]):
            return 5

        # Level 6: Animal/In vitro
        if any(kw in text for kw in [
            'animal', 'mouse', 'rat', 'in vitro', 'cell line',
            'experimental model', 'animal model'
        ]):
            return 6

        # Check for "clinical trial" (without "randomized")
        if 'clinical trial' in text:
            return 2

        # Default unknown
        return None

    def filter_by_level(
        self,
        articles: List[Dict[str, Any]],
        min_level: int = 1,
        max_level: int = 2
    ) -> List[Dict[str, Any]]:
        """
        Filter articles by evidence level range.

        Args:
            articles: List of classified articles
            min_level: Minimum evidence level (highest quality = 1)
            max_level: Maximum evidence level

        Returns:
            Filtered list of articles
        """
        filtered = [
            article for article in articles
            if min_level <= article.get('evidence_level', 6) <= max_level
        ]
        return filtered

    def get_top_evidence(
        self,
        articles: List[Dict[str, Any]],
        max_articles: int = 20
    ) -> List[Dict[str, Any]]:
        """
        Get top evidence articles (meta-analyses and RCTs).

        Args:
            articles: List of classified articles
            max_articles: Maximum number of articles to return

        Returns:
            Top quality articles
        """
        # Get levels 1 and 2
        top = self.filter_by_level(articles, min_level=1, max_level=2)

        # Limit number of results
        return top[:max_articles]

    def format_summary(self, articles: List[Dict[str, Any]]) -> str:
        """Format a summary of evidence levels in the article list."""
        lines = []
        lines.append("=" * 60)
        lines.append("EVIDENCE PYRAMID SUMMARY")
        lines.append("=" * 60)
        lines.append("")

        # Count articles by level
        level_counts = {}
        for article in articles:
            level = article.get('evidence_level', 6)
            level_counts[level] = level_counts.get(level, 0) + 1

        # Format summary
        for level in sorted(level_counts.keys()):
            count = level_counts[level]
            level_name = self.EVIDENCE_LEVELS[level]
            lines.append(f"Level {level} - {level_name}: {count} articles")

        lines.append("")
        lines.append(f"Total articles: {len(articles)}")
        lines.append("")

        # Show breakdown by level
        lines.append("=" * 60)
        lines.append("TOP EVIDENCE (Levels 1-2)")
        lines.append("=" * 60)
        lines.append("")

        top_articles = self.get_top_evidence(articles, max_articles=10)
        if top_articles:
            for i, article in enumerate(top_articles[:10], 1):
                level = article.get('evidence_level', 6)
                level_name = self.EVIDENCE_LEVELS[level]
                title = article.get('title', 'Unknown title')
                first_author = article.get('firstAuthor', 'Unknown')

                lines.append(f"{i}. [{level_name}]")
                lines.append(f"   {first_author} et al.")
                lines.append(f"   {title[:80]}{'...' if len(title) > 80 else ''}")
                lines.append("")
        else:
            lines.append("No high-level evidence (meta-analyses or RCTs) found.")
            lines.append("")

        return '\n'.join(lines)

    def format_evidence_table(
        self,
        articles: List[Dict[str, Any]],
        show_abstracts: bool = False
    ) -> str:
        """Format articles as an evidence table."""
        lines = []
        lines.append("| Level | Evidence Type | Authors | Year | Title |")
        lines.append("|-------|---------------|---------|------|-------|")

        for article in articles:
            level = article.get('evidence_level', 6)
            level_name = self.EVIDENCE_LEVELS[level]
            first_author = article.get('firstAuthor', 'Unknown')
            year = article.get('pubYear', 'Unknown')
            title = article.get('title', 'Unknown title')

            # Truncate title for table
            if len(title) > 60:
                title = title[:57] + '...'

            lines.append(f"| {level} | {level_name} | {first_author} | {year} | {title} |")

            # Add abstract if requested
            if show_abstracts and article.get('abstract'):
                abstract = article['abstract']
                if len(abstract) > 200:
                    abstract = abstract[:197] + '...'
                lines.append(f"| | | | | *Abstract*: {abstract} |")

        return '\n'.join(lines)


def main():
    """Command-line interface for evidence classifier."""
    parser = argparse.ArgumentParser(
        description='Classify articles by evidence level'
    )
    parser.add_argument(
        '--articles',
        type=str,
        required=True,
        help='JSON file with PubMed articles'
    )
    parser.add_argument(
        '--output',
        type=str,
        required=True,
        help='Output file for classified articles'
    )
    parser.add_argument(
        '--filter-level',
        type=str,
        help='Filter to evidence level (e.g., "1-2" for meta-analyses and RCTs only)'
    )
    parser.add_argument(
        '--max',
        type=int,
        default=100,
        help='Maximum number of articles to output (default: 100)'
    )
    parser.add_argument(
        '--summary',
        action='store_true',
        help='Print evidence summary to stdout'
    )
    parser.add_argument(
        '--table',
        action='store_true',
        help='Print evidence table to stdout'
    )

    args = parser.parse_args()

    # Load articles
    with open(args.articles, 'r') as f:
        articles = json.load(f)

    # Classify
    classifier = EvidencePyramidClassifier()
    classified = classifier.classify_articles(articles)

    # Filter if requested
    if args.filter_level:
        try:
            min_level, max_level = map(int, args.filter_level.split('-'))
            classified = classifier.filter_by_level(
                classified,
                min_level=min_level,
                max_level=max_level
            )
        except ValueError:
            parser.error("--filter-level must be in format 'min-max' (e.g., '1-2')")

    # Limit results
    classified = classified[:args.max]

    # Save results
    with open(args.output, 'w') as f:
        json.dump(classified, f, indent=2)

    print(f"Saved {len(classified)} classified articles to {args.output}")

    # Print summary if requested
    if args.summary:
        print()
        print(classifier.format_summary(classified))

    # Print table if requested
    if args.table:
        print()
        print(classifier.format_evidence_table(classified))


if __name__ == '__main__':
    main()
