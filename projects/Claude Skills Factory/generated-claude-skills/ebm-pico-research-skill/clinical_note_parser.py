#!/usr/bin/env python3
"""
Clinical Note Parser for EBM PICO Research Skill

This script parses clinical note summaries and extracts structured patient context
for evidence-based medicine searches.

Usage:
    python clinical_note_parser.py --note "clinical note text"
    python clinical_note_parser.py --file clinical_note.txt
"""

import argparse
import json
import re
from typing import Dict, List, Optional, Any


class ClinicalNoteParser:
    """Parse clinical notes to extract patient context and PICO elements."""

    def __init__(self):
        # Common patterns for clinical information extraction
        self.age_pattern = re.compile(
            r'(\d+)[- ]?(year[s]?-old|yo|y\.o\.|years old)',
            re.IGNORECASE
        )
        self.sex_pattern = re.compile(
            r'\b(male|female|man|woman|boy|girl)\b',
            re.IGNORECASE
        )

        # Common medical abbreviations and their expansions
        self.abbreviations = {
            'htn': 'hypertension',
            'dm': 'diabetes mellitus',
            'dm2': 'type 2 diabetes',
            'dm1': 'type 1 diabetes',
            't2dm': 'type 2 diabetes',
            't1dm': 'type 1 diabetes',
            'chf': 'congestive heart failure',
            'cad': 'coronary artery disease',
            'copd': 'chronic obstructive pulmonary disease',
            'ckd': 'chronic kidney disease',
            'esrd': 'end-stage renal disease',
            'af': 'atrial fibrillation',
            'afb': 'atrial fibrillation',
            'mi': 'myocardial infarction',
            'dvt': 'deep vein thrombosis',
            'pe': 'pulmonary embolism',
            'vte': 'venous thromboembolism',
            'tia': 'transient ischemic attack',
            'cva': 'cerebrovascular accident',
            'tbi': 'traumatic brain injury',
            'uti': 'urinary tract infection',
            'uri': 'upper respiratory infection',
            'lri': 'lower respiratory infection',
            'pna': 'pneumonia',
            'uuo': 'uncertain diagnosis',
            'r/o': 'rule out',
            'sob': 'shortness of breath',
            'cp': 'chest pain',
            'abd': 'abdominal',
            'fx': 'fracture',
            'sx': 'symptom',
            'dx': 'diagnosis',
            'hx': 'history',
            'tx': 'treatment',
            'px': 'prognosis',
            'f/u': 'follow-up',
            'n/v': 'nausea/vomiting',
            'c/o': 'complains of',
            'b/l': 'bilateral',
            'l': 'left',
            'r': 'right',
        }

    def parse(self, clinical_note: str) -> Dict[str, Any]:
        """
        Parse clinical note and extract structured patient context.

        Args:
            clinical_note: Raw clinical note text

        Returns:
            Dictionary containing structured patient context
        """
        # Expand abbreviations
        expanded_note = self._expand_abbreviations(clinical_note)

        # Extract components
        context = {
            'original_note': clinical_note.strip(),
            'demographics': self._extract_demographics(expanded_note),
            'primary_condition': self._extract_primary_condition(expanded_note),
            'comorbidities': self._extract_comorbidities(expanded_note),
            'clinical_context': self._extract_clinical_context(expanded_note),
            'treatment_decisions': self._identify_treatment_decisions(expanded_note),
            'contraindications': self._extract_contraindications(expanded_note),
            'patient_specific_factors': self._extract_patient_factors(expanded_note),
        }

        return context

    def _expand_abbreviations(self, text: str) -> str:
        """Expand common medical abbreviations."""
        words = text.split()
        expanded = []

        for word in words:
            # Remove punctuation for matching
            clean_word = word.lower().strip('.,;:!?')
            if clean_word in self.abbreviations:
                expanded.append(self.abbreviations[clean_word])
            else:
                expanded.append(word)

        return ' '.join(expanded)

    def _extract_demographics(self, text: str) -> Dict[str, Optional[str]]:
        """Extract patient demographics."""
        age = None
        sex = None

        # Extract age
        age_match = self.age_pattern.search(text)
        if age_match:
            age = int(age_match.group(1))

        # Extract sex
        sex_match = self.sex_pattern.search(text)
        if sex_match:
            sex_lower = sex_match.group(1).lower()
            if sex_lower in ['male', 'man', 'boy']:
                sex = 'Male'
            elif sex_lower in ['female', 'woman', 'girl']:
                sex = 'Female'

        # Identify age group
        age_group = None
        if age:
            if age < 1:
                age_group = 'Neonate'
            elif age < 12:
                age_group = 'Child'
            elif age < 18:
                age_group = 'Adolescent'
            elif age < 40:
                age_group = 'Young Adult'
            elif age < 65:
                age_group = 'Middle-aged Adult'
            else:
                age_group = 'Elderly'

        return {
            'age': age,
            'sex': sex,
            'age_group': age_group,
        }

    def _extract_primary_condition(self, text: str) -> Dict[str, str]:
        """Extract primary diagnosis/condition."""
        text_lower = text.lower()

        # Look for diagnosis patterns
        diagnosis_keywords = [
            'diagnosis', 'admitted with', 'presenting with',
            'primary diagnosis', 'principal diagnosis',
            'reason for admission', 'chief complaint'
        ]

        primary_diagnosis = None
        for keyword in diagnosis_keywords:
            pattern = rf'{keyword}[:\s]+([^.]+\.?)'
            match = re.search(pattern, text_lower)
            if match:
                primary_diagnosis = match.group(1).strip()
                break

        # If no explicit diagnosis found, look for first sentence
        # (often contains the presenting problem)
        if not primary_diagnosis:
            sentences = re.split(r'[.!?]+', text)
            if sentences:
                primary_diagnosis = sentences[0].strip()

        # Classify condition type
        condition_type = self._classify_condition_type(text)

        return {
            'diagnosis': primary_diagnosis,
            'condition_type': condition_type,
        }

    def _classify_condition_type(self, text: str) -> str:
        """Classify the type of condition (acute, chronic, etc.)."""
        text_lower = text.lower()

        acute_indicators = [
            'acute', 'emergency', 'urgent', 'sudden',
            'admitted', 'presented to er', 'presented to ed'
        ]

        chronic_indicators = [
            'chronic', 'history of', 'long-standing',
            'follow-up', 'routine', 'outpatient'
        ]

        acute_score = sum(1 for ind in acute_indicators if ind in text_lower)
        chronic_score = sum(1 for ind in chronic_indicators if ind in text_lower)

        if acute_score > chronic_score:
            return 'Acute'
        elif chronic_score > acute_score:
            return 'Chronic'
        elif acute_score == chronic_score and acute_score > 0:
            return 'Acute-on-chronic'
        else:
            return 'Unknown'

    def _extract_comorbidities(self, text: str) -> List[str]:
        """Extract comorbidities from clinical note."""
        text_lower = text.lower()

        comorbidities = []

        # Common comorbidity patterns
        comorbidity_patterns = [
            r'history of ([^.]+?)(?:,|\.)',
            r'with ([^.]+?)(?:,|\.)',
            r'past medical history[:\s]+([^.]+)',
            r'pmh[:\s]+([^.]+)',
            r'comorbidities[:\s]+([^.]+)',
        ]

        for pattern in comorbidity_patterns:
            matches = re.findall(pattern, text_lower)
            for match in matches:
                # Split on common separators
                items = re.split(r'[,;]|\sand\s', match)
                comorbidities.extend([item.strip() for item in items if item.strip()])

        # Filter out non-medical terms
        medical_terms = []
        non_medical = ['unremarkable', 'none', 'denies', 'negative']

        for comorb in comorbidities:
            if comorb and not any(nm in comorb for nm in non_medical):
                medical_terms.append(comorb)

        return list(set(medical_terms))  # Remove duplicates

    def _extract_clinical_context(self, text: str) -> Dict[str, str]:
        """Extract clinical context (setting, severity, etc.)."""
        text_lower = text.lower()

        # Clinical setting
        setting = 'Unknown'
        if any(ind in text_lower for ind in ['admitted', 'inpatient', 'hospitalized']):
            setting = 'Inpatient'
        elif any(ind in text_lower for ind in ['outpatient', 'clinic', 'office']):
            setting = 'Outpatient'
        elif any(ind in text_lower for ind in ['icu', 'intensive care']):
            setting = 'ICU'
        elif any(ind in text_lower for ind in ['ed', 'er', 'emergency']):
            setting = 'Emergency Department'

        # Severity indicators
        severity_keywords = {
            'Critical': ['critical', 'severe', 'unstable', 'life-threatening'],
            'Moderate': ['moderate', 'stable'],
            'Mild': ['mild', 'minor'],
        }

        severity = 'Unknown'
        for sev_level, keywords in severity_keywords.items():
            if any(kw in text_lower for kw in keywords):
                severity = sev_level
                break

        # Duration indicators
        duration = None
        duration_patterns = [
            r'(\d+)\s*(day[s]?|week[s]?|month[s]?|year[s]?)\s+(history|ago)',
            r'(\d+)\s*(day|week|month|year)-old',
        ]

        for pattern in duration_patterns:
            match = re.search(pattern, text_lower)
            if match:
                duration = match.group(0)
                break

        return {
            'setting': setting,
            'severity': severity,
            'duration': duration,
        }

    def _identify_treatment_decisions(self, text: str) -> List[str]:
        """Identify treatment decisions or questions."""
        text_lower = text.lower()

        decisions = []

        # Look for decision keywords
        decision_patterns = [
            r'plan[:\s]+([^.]+)',
            r'decision[:\s]+([^.]+)',
            r'question[:\s]+([^.]+)',
            r'considering ([^.]+)',
            r'need to decide ([^.]+)',
        ]

        for pattern in decision_patterns:
            matches = re.findall(pattern, text_lower)
            decisions.extend([m.strip() for m in matches])

        return list(set(decisions))  # Remove duplicates

    def _extract_contraindications(self, text: str) -> List[str]:
        """Extract contraindications or special considerations."""
        text_lower = text.lower()

        contraindications = []

        # Look for allergy patterns
        allergy_patterns = [
            r'allergy[:\s]+([^.]+)',
            r'allergic to ([^.]+)',
            r'contraindicated ([^.]+)',
            r'contraindication[:\s]+([^.]+)',
        ]

        for pattern in allergy_patterns:
            matches = re.findall(pattern, text_lower)
            contraindications.extend([m.strip() for m in matches])

        return list(set(contraindications))

    def _extract_patient_factors(self, text: str) -> List[str]:
        """Extract other patient-specific factors."""
        factors = []

        text_lower = text.lower()

        # Special population indicators
        special_populations = {
            'Pregnant': r'pregnant|pregnancy|prenatal|gestating',
            'Postpartum': r'postpartum|post[- ]partum',
            'Breastfeeding': r'breastfeeding|breast[- ]feeding|lactating',
            'Immunocompromised': r'immunocompromised|immunosuppressed|on chemotherapy|hiv|aids|transplant',
            'Frail': r'frail|frailty',
            'Obese': r'obese|bmi >|obesity',
        }

        for factor, pattern in special_populations.items():
            if re.search(pattern, text_lower):
                factors.append(factor)

        return factors

    def format_pico_context(self, context: Dict[str, Any]) -> str:
        """
        Format the parsed context as a structured summary for PICO extraction.

        Args:
            context: Parsed clinical context

        Returns:
            Formatted string for PICO construction
        """
        parts = []

        # Demographics
        demo = context['demographics']
        demo_parts = []
        if demo['age_group']:
            demo_parts.append(demo['age_group'])
        if demo['sex']:
            demo_parts.append(demo['sex'])
        if demo_parts:
            parts.append(f"Patient: {', '.join(demo_parts)}")

        # Primary condition
        if context['primary_condition']['diagnosis']:
            parts.append(f"Primary Condition: {context['primary_condition']['diagnosis']}")

        # Comorbidities
        if context['comorbidities']:
            parts.append(f"Comorbidities: {', '.join(context['comorbidities'][:5])}")  # Limit to 5

        # Clinical context
        ctx = context['clinical_context']
        if ctx['setting'] != 'Unknown':
            parts.append(f"Setting: {ctx['setting']}")
        if ctx['severity'] != 'Unknown':
            parts.append(f"Severity: {ctx['severity']}")

        # Treatment decisions
        if context['treatment_decisions']:
            parts.append(f"Clinical Question: {context['treatment_decisions'][0]}")

        # Contraindications
        if context['contraindications']:
            parts.append(f"Contraindications: {', '.join(context['contraindications'])}")

        # Special factors
        if context['patient_specific_factors']:
            parts.append(f"Special Considerations: {', '.join(context['patient_specific_factors'])}")

        return '\n'.join(parts)


def main():
    """Command-line interface for clinical note parser."""
    parser = argparse.ArgumentParser(
        description='Parse clinical notes and extract patient context'
    )
    parser.add_argument(
        '--note',
        type=str,
        help='Clinical note text as string'
    )
    parser.add_argument(
        '--file',
        type=str,
        help='File containing clinical note'
    )
    parser.add_argument(
        '--output',
        type=str,
        choices=['json', 'formatted'],
        default='formatted',
        help='Output format'
    )

    args = parser.parse_args()

    # Get clinical note text
    if args.file:
        with open(args.file, 'r') as f:
            clinical_note = f.read()
    elif args.note:
        clinical_note = args.note
    else:
        parser.error("Either --note or --file must be provided")

    # Parse the note
    parser_obj = ClinicalNoteParser()
    context = parser_obj.parse(clinical_note)

    # Output results
    if args.output == 'json':
        print(json.dumps(context, indent=2))
    else:
        print("=" * 60)
        print("CLINICAL NOTE ANALYSIS")
        print("=" * 60)
        print()
        print(parser_obj.format_pico_context(context))
        print()
        print("=" * 60)
        print("STRUCTURED DATA FOR PICO CONSTRUCTION")
        print("=" * 60)
        print(json.dumps(context, indent=2))


if __name__ == '__main__':
    main()
