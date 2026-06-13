import re

CRISIS_KEYWORDS = [
    r"\bsuicide\b",
    r"\bself-harm\b",
    r"\bkill myself\b",
    r"\bend my life\b",
    r"\bwant to die\b",
    r"\bcutting myself\b",
    r"\bhopeless\b",
    r"\bdone with life\b",
]

WARNING_KEYWORDS = [
    r"\bextreme stress\b",
    r"\bpanic attack\b",
    r"\bcant cope\b",
    r"\bcan't cope\b",
    r"\bburnout\b",
    r"\bdepressed\b",
    r"\bfeeling down\b",
    r"\banxious\b",
]


class SafetyEngine:
    @staticmethod
    def analyze_safety(text: str) -> dict:
        """
        Analyze text for safety violations, crisis markers, or self-harm risks.
        Returns a dict:
        {
            'safety_level': 'SAFE' | 'WARNING' | 'CRITICAL',
            'detected_terms': list of matched keywords
        }
        """
        if not text:
            return {"safety_level": "SAFE", "detected_terms": []}

        text_lower = text.lower()
        detected_critical = []
        detected_warning = []

        # Check critical self-harm/suicide terms
        for pattern in CRISIS_KEYWORDS:
            if re.search(pattern, text_lower):
                detected_critical.append(pattern.replace(r"\b", ""))

        if detected_critical:
            return {
                "safety_level": "CRITICAL",
                "detected_terms": detected_critical,
            }

        # Check warning/high stress terms
        for pattern in WARNING_KEYWORDS:
            if re.search(pattern, text_lower):
                detected_warning.append(pattern.replace(r"\b", ""))

        if detected_warning:
            return {
                "safety_level": "WARNING",
                "detected_terms": detected_warning,
            }

        return {"safety_level": "SAFE", "detected_terms": []}
