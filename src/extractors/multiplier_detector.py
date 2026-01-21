import re
from typing import Tuple

class MultiplierDetector:
    SCALE_WORDS = {
        'thousand': 1_000, 'thousands': 1_000,
        'million': 1_000_000, 'millions': 1_000_000,
        'billion': 1_000_000_000, 'billions': 1_000_000_000,
        'trillion': 1_000_000_000_000, 'trillions': 1_000_000_000_000,
    }
    SUFFIX_MAP = {'K': 1_000, 'M': 1_000_000, 'B': 1_000_000_000, 'T': 1_000_000_000_000, 'MM': 1_000_000}

    @classmethod
    def detect_multiplier(cls, text: str, extended_context: str = "") -> Tuple[float, str]:
        search_text = (text + " " + extended_context).lower()
        # natural lang multiplier
        for word, mult in cls.SCALE_WORDS.items():
            pattern = rf'\b(?:in\s+)?(?:\()?{word}\)?'
            if re.search(pattern, search_text):
                return mult, word
            
        # numerical matterns
        if re.search(r"\b\d*000[\'']?s?\b", search_text):
            return 1_000, "000s"
        
        # suffix extrction
        for suffix, mult in cls.SUFFIX_MAP.items():
            if re.search(rf'\${suffix}\b', search_text, re.I):
                return mult, f"${suffix}"
            
        return 1.0, ""
