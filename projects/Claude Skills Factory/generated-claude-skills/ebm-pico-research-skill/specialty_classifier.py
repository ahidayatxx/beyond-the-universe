#!/usr/bin/env python3
"""
Medical Specialty Classifier for Search Year Ranges

Determines appropriate search year ranges based on medical specialty
and clinical topic characteristics.

Usage:
    from specialty_classifier import SpecialtyClassifier

    classifier = SpecialtyClassifier()
    year_range = classifier.determine_search_range(
        population="elderly patients",
        intervention="SGLT2 inhibitors",
        condition="type 2 diabetes"
    )
    # Returns: {'start': 2018, 'end': 2025}
"""

import yaml
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional


class SpecialtyClassifier:
    """Classify medical specialty and determine search year ranges."""

    def __init__(self):
        """Initialize the classifier."""
        self.config_path = Path(__file__).parent.parent / 'reference' / 'medical_specialties.yaml'
        self.config = self._load_config()
        self.current_year = datetime.now().year

    def _load_config(self) -> Dict:
        """
        Load medical specialties configuration.

        Returns:
            Dictionary with specialty configurations
        """
        with open(self.config_path, 'r') as f:
            return yaml.safe_load(f)

    def determine_search_range(
        self,
        population: str,
        intervention: str,
        condition: str = ''
    ) -> Dict[str, int]:
        """
        Determine appropriate search year range based on specialty.

        Args:
            population: Population description (e.g., "stroke patients")
            intervention: Intervention description (e.g., "LMWH vs UFH")
            condition: Primary condition (optional, e.g., "VTE prophylaxis")

        Returns:
            Dictionary with 'start' and 'end' years
        """
        # Combine text for analysis
        text = f"{population} {intervention} {condition}".lower()

        # Check special situations first (highest priority)
        special_years = self._check_special_situations(text)
        if special_years:
            return {
                'start': self.current_year - special_years,
                'end': self.current_year
            }

        # Check specialty keywords
        specialty_years = self._check_specialty_keywords(text)
        if specialty_years:
            return {
                'start': self.current_year - specialty_years,
                'end': self.current_year
            }

        # Default to 7 years
        return {
            'start': self.current_year - 7,
            'end': self.current_year
        }

    def _check_special_situations(self, text: str) -> Optional[int]:
        """
        Check for special situation keywords that override specialty classification.

        Special situations include:
        - Pediatric: 10 years (fewer studies)
        - Geriatric: 10 years (evidence accumulates slowly)
        - Pregnancy: 15 years (safety data requires longer timeframe)
        - Rare diseases: 15 years (limited evidence)
        - COVID-19/Pandemic: 3 years (very recent evidence only)

        Args:
            text: Combined PICO text in lowercase

        Returns:
            Number of years for search range, or None if no match
        """
        special = self.config.get('special_situations', {})

        for situation, config in special.items():
            keywords = config.get('keywords', [])
            if any(kw in text for kw in keywords):
                return config.get('years', 7)

        return None

    def _check_specialty_keywords(self, text: str) -> Optional[int]:
        """
        Check specialty keywords to determine year range.

        Categories:
        - Rapidly evolving (oncology, infectious diseases): 3-5 years
        - Moderately evolving (cardiology, neurology): 5-7 years
        - Established treatments (internal medicine): 7-10 years
        - Surgical/procedural: 5-10 years
        - Emergency/acute care: 3-5 years
        - Mental health: 7-10 years
        - Diagnostic/imaging: 3-5 years
        - Rehabilitation: 5-7 years
        - Palliative care: 5-7 years

        Args:
            text: Combined PICO text in lowercase

        Returns:
            Number of years for search range, or None if no match
        """
        categories = [
            'rapidly_evolving',
            'moderately_evolving',
            'established_treatments',
            'surgical',
            'emergency',
            'mental_health',
            'diagnostic',
            'rehab',
            'palliative'
        ]

        for category in categories:
            config = self.config.get(category, {})
            keywords = config.get('keywords', [])
            if any(kw in text for kw in keywords):
                return config.get('default_years', 7)

        return None


def main():
    """Command-line interface for testing specialty classification."""
    import argparse
    import json

    parser = argparse.ArgumentParser(
        description='Determine search year range for medical literature search'
    )
    parser.add_argument(
        '--population',
        type=str,
        help='Population description'
    )
    parser.add_argument(
        '--intervention',
        type=str,
        help='Intervention description'
    )
    parser.add_argument(
        '--condition',
        type=str,
        default='',
        help='Primary condition (optional)'
    )

    args = parser.parse_args()

    if not args.population or not args.intervention:
        parser.error("Both --population and --intervention are required")

    classifier = SpecialtyClassifier()
    year_range = classifier.determine_search_range(
        population=args.population,
        intervention=args.intervention,
        condition=args.condition
    )

    print(json.dumps(year_range, indent=2))


if __name__ == '__main__':
    main()
