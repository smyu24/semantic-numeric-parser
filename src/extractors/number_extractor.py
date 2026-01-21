import re
from typing import List, Tuple, Optional

class NumberExtractor:
    NUMBER_PATTERN = re.compile(
        r'''
        (?:[\$€£¥]?\s*)?            # currency
        [\(]?                       # open parenthesis
        (\d{1,3}(?:,\d{3})*(?:\.\d+)?|\d+(?:\.\d+)?)  # nums
        [\)]?                       # close parenthesis
        (?:                         # unit suffix
            (?<=\d)                 
            (K|M|B|T|MM)            
            \b                      
        )?
        ''',
        re.VERBOSE | re.IGNORECASE
    )

    @classmethod
    def extract_numbers(cls, text: str) -> List[Tuple[float, str, int, int, bool]]:
        results = []
        for match in cls.NUMBER_PATTERN.finditer(text):
            matched_text = match.group(0)
            start, end = match.span()
            suffix = match.group(2)
            has_suffix = False
            if suffix and suffix.upper() in {"K", "M", "B", "T", "MM"} and suffix.isupper():
                has_suffix = True
            try:
                value = cls.parse_number(matched_text)
                if value is not None:
                    results.append((value, matched_text, start, end, has_suffix))
            except ValueError:
                continue
        return results

    @classmethod
    def parse_number(cls, text: str) -> Optional[float]:
        text = text.strip()
        is_negative = text.startswith('(') and text.endswith(')')

        # get currency and/or parentheses
        clean = re.sub(r'[\$€£¥,\(\)]', '', text)
        clean = re.sub(r'\s+[kmbt]\b', '', clean, flags=re.I)
        
        multiplier = 1.0
        clean_upper = clean.upper()
        if clean_upper.endswith('MM'):
            multiplier = 1_000_000
            clean = clean[:-2]
        elif clean_upper.endswith('M'):
            multiplier = 1_000_000
            clean = clean[:-1]
        elif clean_upper.endswith('B'):
            multiplier = 1_000_000_000
            clean = clean[:-1]
        elif clean_upper.endswith('K'):
            multiplier = 1_000
            clean = clean[:-1]
        elif clean_upper.endswith('T'):
            multiplier = 1_000_000_000_000
            clean = clean[:-1]
        try:
            value = float(clean.strip()) * multiplier
            return -value if is_negative else value
        except ValueError:
            return None