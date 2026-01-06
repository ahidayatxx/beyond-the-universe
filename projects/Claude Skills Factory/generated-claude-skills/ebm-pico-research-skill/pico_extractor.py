#!/usr/bin/env python3
"""
PICO Extractor for EBM PICO Research Skill

This script extracts PICO (Population, Intervention, Comparison, Outcome)
elements from clinical questions or parsed clinical notes.

Usage:
    python pico_extractor.py --question "clinical question"
    python pico_extractor.py --context context.json
"""

import argparse
import json
import re
from typing import Dict, List, Optional, Any


class PICOExtractor:
    """Extract PICO elements from clinical text."""

    def __init__(self):
        # Keywords that indicate PICO components
        self.population_keywords = [
            'patient', 'patients', 'population', 'adult', 'child', 'elderly',
            'pediatric', 'geriatric', 'with', 'diagnosed with', 'suffering from',
            'presenting with', 'admitted with', 'history of'
        ]

        self.intervention_keywords = [
            'treatment', 'therapy', 'drug', 'medication', 'surgery', 'procedure',
            'intervention', 'management', 'use of', 'versus', 'vs', 'compared to',
            'compared with', 'role of', 'effect of', 'impact of', 'efficacy'
        ]

        self.comparison_keywords = [
            'versus', 'vs', 'compared to', 'compared with', 'against', 'alternative',
            'placebo', 'standard care', 'usual care', 'no treatment', 'watchful waiting'
        ]

        self.outcome_keywords = [
            'outcome', 'outcomes', 'reduce', 'prevent', 'improve', 'decrease',
            'increase', 'mortality', 'morbidity', 'adverse effect', 'side effect',
            'complication', 'survival', 'recovery', 'response rate', 'efficacy',
            'effectiveness', 'safety', 'tolerability'
        ]

        # Common medical question patterns
        self.question_patterns = {
            'therapy': [
                r'is\s+(\w+)\s+(better|more effective|superior)\s+than\s+(\w+)',
                r'does\s+(\w+)\s+(improve|reduce|prevent)',
                r'effect\s+of\s+(\w+)\s+on\s+(\w+)',
            ],
            'diagnosis': [
                r'is\s+(\w+)\s+(more accurate|better|superior)\s+than\s+(\w+)\s+for',
                r'accuracy\s+of\s+(\w+)',
            ],
            'prognosis': [
                r'risk\s+of\s+(\w+)',
                r'predict[s]?\s+(\w+)',
                r'prognos[ic|is]\s+factor[s]?\s+for\s+(\w+)',
            ],
            'harm': [
                r'does\s+(\w+)\s+(cause|increase|risk)',
                r'associated\s+with\s+(increased|risk)',
            ],
        }

    def extract_from_question(self, question: str) -> Dict[str, Any]:
        """
        Extract PICO from a direct clinical question.

        Args:
            question: Clinical question text

        Returns:
            Dictionary with P-I-C-O components
        """
        pico = {
            'P': None,
            'I': None,
            'C': None,
            'O': None,
            'question_type': self._classify_question_type(question),
            'original_question': question.strip(),
        }

        # Extract using pattern matching
        pico['P'] = self._extract_population(question)
        pico['I'] = self._extract_intervention(question)
        pico['C'] = self._extract_comparison(question)
        pico['O'] = self._extract_outcome(question)

        # Validate and enhance
        pico = self._validate_pico(pico)

        return pico

    def extract_from_context(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Construct PICO from parsed clinical note context.

        Args:
            context: Parsed clinical context from clinical_note_parser

        Returns:
            Dictionary with P-I-C-O components
        """
        # Construct Population
        population = self._construct_population_from_context(context)

        # Identify clinical decision point for Intervention
        intervention = self._identify_intervention_from_context(context)

        # Suggest Comparison based on context
        comparison = self._suggest_comparison_from_context(context, intervention)

        # Identify relevant Outcomes
        outcomes = self._identify_outcomes_from_context(context, intervention)

        pico = {
            'P': population,
            'I': intervention,
            'C': comparison,
            'O': outcomes,
            'question_type': 'therapy',  # Most clinical notes involve therapy questions
            'source': 'clinical_note',
            'original_context': context,
        }

        pico = self._validate_pico(pico)

        return pico

    def _classify_question_type(self, question: str) -> str:
        """Classify the type of clinical question."""
        question_lower = question.lower()

        # Check for therapy keywords
        if any(kw in question_lower for kw in ['treatment', 'therapy', 'manage', 'effective']):
            return 'therapy'

        # Check for diagnosis keywords
        if any(kw in question_lower for kw in ['diagnos', 'detect', 'screen', 'accuracy']):
            return 'diagnosis'

        # Check for prognosis keywords
        if any(kw in question_lower for kw in ['prognos', 'risk', 'predict', 'course', 'outcome']):
            return 'prognosis'

        # Check for harm/etiology keywords
        if any(kw in question_lower for kw in ['cause', 'harm', 'adverse', 'risk factor', 'associate']):
            return 'harm'

        return 'therapy'  # Default

    def _extract_population(self, text: str) -> str:
        """Extract population from text."""
        # Look for patterns like "In [population], ..."
        match = re.search(r'(?:in|for|among)\s+([^,]+?)(?:,|\swith\s|\swho\s|\sundergoing)', text, re.IGNORECASE)
        if match:
            return match.group(1).strip()

        # Look for age or condition descriptions at the beginning
        sentences = text.split('.')
        first_sentence = sentences[0] if sentences else text

        # Common patterns
        if ' with ' in first_sentence.lower():
            parts = first_sentence.lower().split(' with ')
            if len(parts) > 1:
                # Get the condition
                condition = parts[1].split(',')[0].strip()
                # Get the population if present
                pop = parts[0].strip()
                return f"{pop} with {condition}"

        return None

    def _extract_intervention(self, text: str) -> str:
        """Extract intervention from text."""
        # Look for "does X" or "effect of X" patterns
        patterns = [
            r'does\s+([^,\s]+(?:\s+[^,\s]+)?)\s+(?:improve|reduce|treat|prevent|help)',
            r'effect\s+of\s+([^,\s]+(?:\s+[^,\s]+)?)\s+(?:on|for)',
            r'(?:is|are)\s+([^,\s]+(?:\s+[^,\s]+)?)\s+(?:effective|better)',
        ]

        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1).strip()

        return None

    def _extract_comparison(self, text: str) -> str:
        """Extract comparison from text."""
        # Look for comparison indicators
        patterns = [
            r'(?:versus|vs\.?|compared\s+(?:to|with)|against)\s+([^,\s]+(?:\s+[^,\s]+)?)',
            r'(?:than|instead\s+of)\s+([^,\s]+(?:\s+[^,\s]+)?)',
        ]

        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1).strip()

        return None

    def _extract_outcome(self, text: str) -> str:
        """Extract outcome from text."""
        # Look for outcome keywords
        patterns = [
            r'(?:reduce|prevent|improve|decrease|lower)\s+([^,\.]+)',
            r'(?:for|to\s+treat|to\s+prevent)\s+([^,\.]+)',
            r'outcome[s]?\s+(?:of|include[s]?:?)\s+([^,\.]+)',
        ]

        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1).strip()

        return None

    def _construct_population_from_context(self, context: Dict[str, Any]) -> str:
        """Construct population description from clinical context."""
        parts = []

        demo = context.get('demographics', {})

        # Age group
        if demo.get('age_group'):
            parts.append(demo['age_group'])

        # Sex (if relevant to condition)
        if demo.get('sex') and context.get('primary_condition', {}).get('diagnosis'):
            condition = context['primary_condition']['diagnosis'].lower()
            # Only include sex for sex-specific conditions or when relevant
            if any(term in condition for term in ['prostate', 'ovarian', 'breast', 'uterine', 'testicular', 'pregnancy']):
                parts.append(demo['sex'])

        # Primary condition
        if context.get('primary_condition', {}).get('diagnosis'):
            parts.append(f"with {context['primary_condition']['diagnosis']}")

        # Comorbidities (limit to most relevant)
        comorbidities = context.get('comorbidities', [])
        if comorbidities:
            # Include up to 2 most relevant comorbidities
            relevant = comorbidities[:2]
            parts.append(f"and {' '.join(relevant)}")

        return ' '.join(parts) if parts else "Adults"

    def _identify_intervention_from_context(self, context: Dict[str, Any]) -> str:
        """Identify intervention from clinical context."""
        # Check treatment decisions
        decisions = context.get('treatment_decisions', [])
        if decisions:
            return decisions[0]

        # Check primary condition for common interventions
        primary = context.get('primary_condition', {}).get('diagnosis', '').lower()

        # Common condition-intervention mappings
        intervention_map = {
            'pneumonia': 'antibiotic therapy',
            'stroke': 'thrombolysis or anticoagulation',
            'diabetes': 'glycemic control',
            'hypertension': 'antihypertensive therapy',
            'depression': 'antidepressant therapy or psychotherapy',
            'heart failure': 'ACE inhibitors or beta-blockers',
        }

        for condition, intervention in intervention_map.items():
            if condition in primary:
                return intervention

        # Check contraindications to refine intervention
        contraindications = context.get('contraindications', [])
        if contraindications:
            return f"appropriate treatment (avoiding {contraindications[0]})"

        return "treatment"

    def _suggest_comparison_from_context(self, context: Dict[str, Any], intervention: str) -> Optional[str]:
        """Suggest appropriate comparison based on context."""
        if not intervention:
            return None

        # Common comparisons by condition type
        condition_type = context.get('primary_condition', {}).get('condition_type', '')

        if condition_type == 'Acute':
            return "standard care or placebo"

        elif condition_type == 'Chronic':
            return "usual care or alternative management"

        # Check for specific interventions that have standard comparators
        intervention_lower = intervention.lower()

        if 'antibiotic' in intervention_lower:
            return "alternative antibiotic regimen"

        if 'surgery' in intervention_lower or 'surgical' in intervention_lower:
            return "conservative management"

        if 'drug' in intervention_lower or 'medication' in intervention_lower:
            return "placebo or standard therapy"

        return "standard care or placebo"

    def _identify_outcomes_from_context(self, context: Dict[str, Any], intervention: str) -> List[str]:
        """Identify relevant outcomes based on context and intervention."""
        outcomes = []

        # Condition-specific outcomes
        primary = context.get('primary_condition', {}).get('diagnosis', '').lower()

        # Mortality is almost always relevant
        outcomes.append("mortality")

        # Condition-specific outcomes
        outcome_map = {
            'pneumonia': ['clinical response', 'hospital length of stay'],
            'stroke': ['functional independence', 'recurrent stroke', 'intracranial hemorrhage'],
            'diabetes': ['HbA1c reduction', 'hypoglycemic events'],
            'hypertension': ['blood pressure control', 'cardiovascular events'],
            'depression': ['symptom remission', 'quality of life'],
            'heart failure': ['hospitalization', 'quality of life', 'functional status'],
        }

        for condition, condition_outcomes in outcome_map.items():
            if condition in primary:
                outcomes.extend(condition_outcomes)
                break

        # Add adverse effects
        outcomes.append("adverse effects")

        # Check severity for additional outcomes
        severity = context.get('clinical_context', {}).get('severity', '')
        if severity == 'Critical':
            outcomes.append("ICU length of stay")

        return outcomes

    def _validate_pico(self, pico: Dict[str, Any]) -> Dict[str, Any]:
        """Validate and enhance PICO components."""
        # Ensure Population is not None
        if not pico['P']:
            pico['P'] = "Patients"

        # Intervention is required
        if not pico['I']:
            pico['I'] = "treatment"

        # Comparison is optional, set to None if not found
        if not pico.get('C'):
            pico['C'] = None

        # Outcome is required
        if not pico['O']:
            pico['O'] = "clinical outcome"

        # Add warnings for incomplete PICO
        warnings = []
        if not pico['P'] or pico['P'] == "Patients":
            warnings.append("Population not clearly specified")

        if not pico['I'] or pico['I'] == "treatment":
            warnings.append("Intervention not clearly specified")

        if not pico['C'] and pico.get('question_type') == 'therapy':
            warnings.append("Comparison not specified - consider standard care or placebo")

        if not pico['O'] or pico['O'] == "clinical outcome":
            warnings.append("Outcome not clearly specified")

        if warnings:
            pico['warnings'] = warnings

        return pico

    def format_pico(self, pico: Dict[str, Any]) -> str:
        """Format PICO as a readable string."""
        lines = []
        lines.append("=" * 60)
        lines.append("PICO ANALYSIS")
        lines.append("=" * 60)
        lines.append("")

        if pico.get('original_question'):
            lines.append(f"Original Question: {pico['original_question']}")
            lines.append("")

        if pico.get('question_type'):
            lines.append(f"Question Type: {pico['question_type'].title()}")
            lines.append("")

        lines.append("P (Population):")
        lines.append(f"  {pico['P'] or 'Not specified'}")
        lines.append("")

        lines.append("I (Intervention):")
        lines.append(f"  {pico['I'] or 'Not specified'}")
        lines.append("")

        lines.append("C (Comparison):")
        lines.append(f"  {pico['C'] or 'Not applicable'}")
        lines.append("")

        lines.append("O (Outcome):")
        if isinstance(pico['O'], list):
            for outcome in pico['O']:
                lines.append(f"  - {outcome}")
        else:
            lines.append(f"  {pico['O'] or 'Not specified'}")

        lines.append("")

        if pico.get('warnings'):
            lines.append("=" * 60)
            lines.append("WARNINGS:")
            for warning in pico['warnings']:
                lines.append(f"  ⚠️  {warning}")

        return '\n'.join(lines)

    def format_search_query(self, pico: Dict[str, Any]) -> str:
        """Format PICO as a PubMed search query."""
        parts = []

        # Population
        if pico['P']:
            # Clean up the population string
            pop = str(pico['P'])
            # Remove common words
            pop = re.sub(r'\b(with|and|or|the|a|an)\b', '', pop)
            parts.append(f'"{pop.strip()}"')

        # Intervention
        if pico['I']:
            intervention = str(pico['I'])
            intervention = re.sub(r'\b(and|or|for|to)\b', '', intervention)
            parts.append(f'"{intervention.strip()}"')

        # Comparison (if present)
        if pico['C']:
            comparison = str(pico['C'])
            comparison = re.sub(r'\b(and|or|for|to)\b', '', comparison)
            parts.append(f'"{comparison.strip()}"')

        # Combine with AND for PubMed
        if parts:
            return ' AND '.join(parts)

        return ""


def main():
    """Command-line interface for PICO extractor."""
    parser = argparse.ArgumentParser(
        description='Extract PICO elements from clinical text'
    )
    parser.add_argument(
        '--question',
        type=str,
        help='Clinical question text'
    )
    parser.add_argument(
        '--context',
        type=str,
        help='JSON file with clinical context from clinical_note_parser'
    )
    parser.add_argument(
        '--output',
        type=str,
        choices=['json', 'formatted', 'query'],
        default='formatted',
        help='Output format'
    )

    args = parser.parse_args()

    extractor = PICOExtractor()

    # Get PICO based on input type
    if args.question:
        pico = extractor.extract_from_question(args.question)
    elif args.context:
        with open(args.context, 'r') as f:
            context = json.load(f)
        pico = extractor.extract_from_context(context)
    else:
        parser.error("Either --question or --context must be provided")

    # Output results
    if args.output == 'json':
        print(json.dumps(pico, indent=2))
    elif args.output == 'query':
        print(extractor.format_search_query(pico))
    else:
        print(extractor.format_pico(pico))


if __name__ == '__main__':
    main()
