#!/usr/bin/env python3
"""
JBI Credibility Checklist for EBM PICO Research Skill

This script performs Joanna Briggs Institute critical appraisal
of research articles.

Usage:
    python jbi_checklist.py --article article.json
    python jbi_checklist.py --articles articles.json
"""

import argparse
import json
import re
from typing import Dict, List, Any, Optional


class JBIChecklist:
    """Perform JBI critical appraisal of research articles."""

    # Quality thresholds
    QUALITY_THRESHOLDS = {
        'high': 80,
        'moderate': 60,
        'low': 0,
    }

    def __init__(self):
        """Initialize the JBI checklist."""
        pass

    def assess_article(self, article: Dict[str, Any]) -> Dict[str, Any]:
        """
        Perform JBI credibility assessment on a single article.

        Args:
            article: Article dictionary with PubMed metadata

        Returns:
            Article with added JBI assessment
        """
        # Get evidence level to determine appropriate checklist
        evidence_level = article.get('evidence_level', 2)

        # Select appropriate checklist based on study design
        if evidence_level == 1:
            # Systematic review or meta-analysis
            assessment = self._assess_systematic_review(article)
        elif evidence_level == 2:
            # RCT
            assessment = self._assess_rct(article)
        elif evidence_level == 3:
            # Cohort study
            assessment = self._assess_cohort(article)
        elif evidence_level == 4:
            # Case-control study
            assessment = self._assess_case_control(article)
        else:
            # Other/unknown - use simplified assessment
            assessment = self._assess_generic(article)

        # Add overall quality rating
        score = assessment.get('total_score', 0)
        assessment['quality'] = self._get_quality_rating(score)
        assessment['quality_percent'] = score

        # Add to article
        article['jbi_assessment'] = assessment

        return article

    def assess_articles(self, articles: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Perform JBI assessment on multiple articles.

        Args:
            articles: List of article dictionaries

        Returns:
            Articles with JBI assessments
        """
        assessed = []

        for article in articles:
            assessed_article = self.assess_article(article)
            assessed.append(assessed_article)

        return assessed

    def _assess_rct(self, article: Dict[str, Any]) -> Dict[str, Any]:
        """Assess an RCT using JBI checklist."""
        text = self._get_article_text(article)

        criteria = {
            'randomization': {
                'question': 'Was randomization used?',
                'points': 10,
                'present': self._check_keyword(text, [
                    'random', 'randomized', 'randomised', 'randomly assigned',
                    'random allocation'
                ]),
            },
            'allocation_concealment': {
                'question': 'Was allocation concealed?',
                'points': 10,
                'present': self._check_keyword(text, [
                    'allocation concealed', 'concealed allocation',
                    'central randomization', 'sealed opaque envelope'
                ]),
            },
            'blinding_participants': {
                'question': 'Were participants blinded?',
                'points': 5,
                'present': self._check_keyword(text, [
                    'participant blinded', 'patient blinded', 'double-blind',
                    'single-blind'
                ]),
            },
            'blinding_personnel': {
                'question': 'Were personnel blinded?',
                'points': 5,
                'present': self._check_keyword(text, [
                    'investigator blinded', 'personnel blinded',
                    'double-blind', 'assessor blinded'
                ]),
            },
            'blinding_outcome': {
                'question': 'Were outcome assessors blinded?',
                'points': 5,
                'present': self._check_keyword(text, [
                    'outcome assessor blinded', 'blinded outcome assessment',
                    'double-blind'
                ]),
            },
            'follow_up_complete': {
                'question': 'Was follow-up complete (>80%)?',
                'points': 15,
                'present': self._check_follow_up(text),
            },
            'intention_to_treat': {
                'question': 'Was intention-to-treat analysis used?',
                'points': 15,
                'present': self._check_keyword(text, [
                    'intention to treat', 'intention-to-treat', 'itt analysis',
                    'analyzed as randomized'
                ]),
            },
            'baseline_similarity': {
                'question': 'Were groups similar at baseline?',
                'points': 10,
                'present': self._check_keyword(text, [
                    'baseline characteristics', 'similar at baseline',
                    'no significant difference at baseline', 'balanced'
                ]),
            },
            'equal_treatment': {
                'question': 'Were groups treated equally?',
                'points': 10,
                'present': self._check_keyword(text, [
                    'co-intervention', 'equal treatment', 'except for intervention'
                ]),
            },
            'reliable_measures': {
                'question': 'Were outcomes measured reliably?',
                'points': 10,
                'present': self._check_keyword(text, [
                    'validated', 'reliable measure', 'standardized measure'
                ]),
            },
            'appropriate_analysis': {
                'question': 'Was appropriate statistical analysis used?',
                'points': 5,
                'present': self._check_statistical_analysis(text),
            },
            'conflicts_declared': {
                'question': 'Were conflicts of interest declared?',
                'points': 10,
                'present': self._check_conflicts(article),
            },
        }

        return self._calculate_score(criteria)

    def _assess_systematic_review(self, article: Dict[str, Any]) -> Dict[str, Any]:
        """Assess a systematic review using JBI checklist."""
        text = self._get_article_text(article)

        criteria = {
            'question_defined': {
                'question': 'Was the review question clearly defined?',
                'points': 10,
                'present': self._check_keyword(text, [
                    'objective', 'research question', 'aim of this review',
                    'purpose of this review'
                ]),
            },
            'inclusion_criteria': {
                'question': 'Were appropriate inclusion criteria defined?',
                'points': 10,
                'present': self._check_keyword(text, [
                    'inclusion criteria', 'eligibility criteria',
                    'inclusion and exclusion'
                ]),
            },
            'search_strategy': {
                'question': 'Was the search strategy comprehensive?',
                'points': 20,
                'present': self._check_keyword(text, [
                    'comprehensive search', 'multiple databases',
                    'medline', 'pubmed', 'embase', 'cochrane',
                    'systematic search'
                ]),
            },
            'study_selection': {
                'question': 'Were studies selected independently?',
                'points': 10,
                'present': self._check_keyword(text, [
                    'independent selection', 'two reviewers',
                    'two independent reviewers'
                ]),
            },
            'quality_assessment': {
                'question': 'Was study quality assessed?',
                'points': 15,
                'present': self._check_keyword(text, [
                    'quality assessment', 'risk of bias', 'critical appraisal',
                    'methodological quality'
                ]),
            },
            'data_extraction': {
                'question': 'Was data extracted independently?',
                'points': 10,
                'present': self._check_keyword(text, [
                    'independent extraction', 'two reviewers',
                    'data extraction'
                ]),
            },
            'synthesis_methods': {
                'question': 'Were appropriate synthesis methods used?',
                'points': 15,
                'present': self._check_keyword(text, [
                    'meta-analysis', 'pooled', 'heterogeneity',
                    'publication bias', 'sensitivity analysis'
                ]),
            },
            'conflicts_declared': {
                'question': 'Were conflicts of interest declared?',
                'points': 10,
                'present': self._check_conflicts(article),
            },
        }

        return self._calculate_score(criteria)

    def _assess_cohort(self, article: Dict[str, Any]) -> Dict[str, Any]:
        """Assess a cohort study using JBI checklist."""
        text = self._get_article_text(article)

        criteria = {
            'representative': {
                'question': 'Was the sample representative?',
                'points': 10,
                'present': self._check_keyword(text, [
                    'representative', 'consecutive', 'population-based'
                ]),
            },
            'groups_defined': {
                'question': 'Were exposure groups clearly defined?',
                'points': 15,
                'present': self._check_keyword(text, [
                    'exposure group', 'exposed group', 'unexposed',
                    'comparison group'
                ]),
            },
            'confounding_identified': {
                'question': 'Were confounding factors identified?',
                'points': 10,
                'present': self._check_keyword(text, [
                    'confound', 'confounding', 'potential confounder'
                ]),
            },
            'confounding_controlled': {
                'question': 'Were strategies to deal with confounding used?',
                'points': 10,
                'present': self._check_keyword(text, [
                    'adjusted', 'multivariate', 'regression', 'propensity score',
                    'matched', 'stratified'
                ]),
            },
            'outcomes_objective': {
                'question': 'Were outcomes measured objectively?',
                'points': 20,
                'present': self._check_keyword(text, [
                    'objective outcome', 'standardized', 'validated'
                ]),
            },
            'follow_up_adequate': {
                'question': 'Was follow-up adequate?',
                'points': 15,
                'present': self._check_follow_up(text),
            },
            'appropriate_analysis': {
                'question': 'Was appropriate statistical analysis used?',
                'points': 15,
                'present': self._check_statistical_analysis(text),
            },
            'conflicts_declared': {
                'question': 'Were conflicts of interest declared?',
                'points': 5,
                'present': self._check_conflicts(article),
            },
        }

        return self._calculate_score(criteria)

    def _assess_case_control(self, article: Dict[str, Any]) -> Dict[str, Any]:
        """Assess a case-control study using JBI checklist."""
        text = self._get_article_text(article)

        criteria = {
            'cases_defined': {
                'question': 'Were cases clearly defined?',
                'points': 15,
                'present': self._check_keyword(text, [
                    'case definition', 'cases defined', 'inclusion criteria'
                ]),
            },
            'cases_representative': {
                'question': 'Were cases representative?',
                'points': 10,
                'present': self._check_keyword(text, [
                    'consecutive', 'all cases', 'population-based'
                ]),
            },
            'controls_appropriate': {
                'question': 'Were controls appropriately selected?',
                'points': 20,
                'present': self._check_keyword(text, [
                    'matched', 'control group', 'comparison group',
                    'same population'
                ]),
            },
            'exposure_objective': {
                'question': 'Was exposure assessed objectively?',
                'points': 20,
                'present': self._check_keyword(text, [
                    'standardized', 'validated', 'blinded assessment'
                ]),
            },
            'confounding_controlled': {
                'question': 'Were confounding factors controlled?',
                'points': 15,
                'present': self._check_keyword(text, [
                    'adjusted', 'multivariate', 'regression',
                    'matched', 'stratified'
                ]),
            },
            'appropriate_analysis': {
                'question': 'Was appropriate statistical analysis used?',
                'points': 10,
                'present': self._check_statistical_analysis(text),
            },
            'conflicts_declared': {
                'question': 'Were conflicts of interest declared?',
                'points': 10,
                'present': self._check_conflicts(article),
            },
        }

        return self._calculate_score(criteria)

    def _assess_generic(self, article: Dict[str, Any]) -> Dict[str, Any]:
        """Generic assessment for unclear study designs."""
        text = self._get_article_text(article)

        criteria = {
            'design_appropriate': {
                'question': 'Was study design appropriate for the question?',
                'points': 15,
                'present': self._check_keyword(text, [
                    'study', 'design', 'method'
                ]),
            },
            'sample_adequate': {
                'question': 'Was the sample adequate?',
                'points': 15,
                'present': self._check_sample_size(text),
            },
            'objective_measures': {
                'question': 'Were measures objective?',
                'points': 20,
                'present': self._check_keyword(text, [
                    'objective', 'validated', 'standardized', 'reliable'
                ]),
            },
            'confounding_addressed': {
                'question': 'Was confounding addressed?',
                'points': 20,
                'present': self._check_keyword(text, [
                    'confound', 'adjusted', 'controlled'
                ]),
            },
            'follow_up_adequate': {
                'question': 'Was follow-up adequate?',
                'points': 15,
                'present': self._check_follow_up(text),
            },
            'appropriate_analysis': {
                'question': 'Was appropriate analysis used?',
                'points': 15,
                'present': self._check_statistical_analysis(text),
            },
        }

        return self._calculate_score(criteria)

    def _calculate_score(self, criteria: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate total score from criteria assessment."""
        total_possible = sum(c['points'] for c in criteria.values())
        total_earned = sum(
            c['points'] for c in criteria.values()
            if c['present']
        )

        # Calculate percentage
        if total_possible > 0:
            percentage = (total_earned / total_possible) * 100
        else:
            percentage = 0

        return {
            'criteria': criteria,
            'total_score': int(percentage),
            'criteria_met': sum(1 for c in criteria.values() if c['present']),
            'criteria_total': len(criteria),
        }

    def _get_article_text(self, article: Dict[str, Any]) -> str:
        """Get combined text from title and abstract."""
        title = article.get('title', '')
        abstract = article.get('abstract', '')
        return f"{title} {abstract}".lower()

    def _check_keyword(self, text: str, keywords: List[str]) -> bool:
        """Check if any keyword is present in text."""
        return any(kw in text for kw in [k.lower() for k in keywords])

    def _check_follow_up(self, text: str) -> bool:
        """Check for adequate follow-up indicators."""
        # Look for loss to follow-up <20%
        loss_pattern = re.search(r'loss to follow[- ]up[:\s]+(\d+)', text)
        if loss_pattern:
            loss_percent = int(loss_pattern.group(1))
            if loss_percent < 20:
                return True

        # Look for complete follow-up keywords
        if any(kw in text for kw in ['complete follow-up', 'followed up', 'no loss to follow']):
            return True

        return False

    def _check_sample_size(self, text: str) -> bool:
        """Check if sample size is adequate."""
        # Look for sample size indicators
        pattern = re.search(r'(\d+)\s*(participants|patients|subjects)', text)
        if pattern:
            n = int(pattern.group(1))
            return n > 50  # Consider >50 as adequate
        return False

    def _check_statistical_analysis(self, text: str) -> bool:
        """Check for appropriate statistical analysis."""
        # Look for statistical tests
        statistical_terms = [
            'p value', 'p-value', 'statistically significant',
            'confidence interval', 'odds ratio', 'relative risk',
            'hazard ratio', 'regression', 'anova', 't-test'
        ]
        return any(kw in text for kw in statistical_terms)

    def _check_conflicts(self, article: Dict[str, Any]) -> bool:
        """Check if conflicts of interest were declared."""
        # This is often in the full text, but we can check the abstract
        text = self._get_article_text(article)
        return self._check_keyword(text, ['conflict of interest', 'no conflict', 'disclosures'])

    def _get_quality_rating(self, score: int) -> str:
        """Get quality rating based on score."""
        if score >= self.QUALITY_THRESHOLDS['high']:
            return 'High'
        elif score >= self.QUALITY_THRESHOLDS['moderate']:
            return 'Moderate'
        else:
            return 'Low'

    def format_assessment(self, article: Dict[str, Any]) -> str:
        """Format JBI assessment for display."""
        if 'jbi_assessment' not in article:
            return "No JBI assessment available."

        assessment = article['jbi_assessment']
        lines = []

        lines.append(f"Quality Rating: {assessment.get('quality', 'Unknown')}")
        lines.append(f"Quality Score: {assessment.get('quality_percent', 0)}%")
        lines.append(f"Criteria Met: {assessment.get('criteria_met', 0)}/{assessment.get('criteria_total', 0)}")
        lines.append("")
        lines.append("Criteria Assessment:")

        criteria = assessment.get('criteria', {})
        for key, criterion in criteria.items():
            status = "✓" if criterion['present'] else "✗"
            lines.append(f"  {status} {criterion['question']} ({criterion['points']} pts)")

        return '\n'.join(lines)

    def format_summary_table(self, articles: List[Dict[str, Any]]) -> str:
        """Format JBI assessments as a summary table."""
        lines = []
        lines.append("| Quality | Score | Study | Authors | Year |")
        lines.append("|---------|-------|-------|---------|------|")

        for article in articles:
            if 'jbi_assessment' not in article:
                continue

            assessment = article['jbi_assessment']
            quality = assessment.get('quality', 'Unknown')
            score = assessment.get('quality_percent', 0)
            title = article.get('title', 'Unknown')
            first_author = article.get('firstAuthor', 'Unknown')
            year = article.get('pubYear', 'Unknown')

            # Truncate title
            if len(title) > 40:
                title = title[:37] + '...'

            lines.append(f"| {quality} | {score}% | {title} | {first_author} | {year} |")

        return '\n'.join(lines)


def main():
    """Command-line interface for JBI checklist."""
    parser = argparse.ArgumentParser(
        description='Perform JBI critical appraisal'
    )
    parser.add_argument(
        '--article',
        type=str,
        help='JSON file with single article'
    )
    parser.add_argument(
        '--articles',
        type=str,
        help='JSON file with multiple articles'
    )
    parser.add_argument(
        '--output',
        type=str,
        help='Output file for assessed articles'
    )
    parser.add_argument(
        '--summary',
        action='store_true',
        help='Print summary table to stdout'
    )

    args = parser.parse_args()

    # Load articles
    if args.article:
        with open(args.article, 'r') as f:
            articles = [json.load(f)]
    elif args.articles:
        with open(args.articles, 'r') as f:
            articles = json.load(f)
    else:
        parser.error("Either --article or --articles must be provided")

    # Assess articles
    checklist = JBIChecklist()
    assessed = checklist.assess_articles(articles)

    # Save if output specified
    if args.output:
        with open(args.output, 'w') as f:
            json.dump(assessed, f, indent=2)
        print(f"Saved {len(assessed)} assessed articles to {args.output}")

    # Print summary if requested
    if args.summary:
        print()
        print(checklist.format_summary_table(assessed))


if __name__ == '__main__':
    main()
