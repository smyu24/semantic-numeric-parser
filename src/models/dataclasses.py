from dataclasses import dataclass, asdict
from typing import List, Optional, Dict
import pandas as pd

@dataclass
class NumberCandidate:
    raw_value: float
    adjusted_value: float
    text: str
    context: str
    page: int
    position: dict
    multiplier: float = 1.0
    multiplier_source: str = ""
    confidence: float = 1.0
    element_type: str = ""
    table_context: str = ""
    
    def to_dict(self):
        return asdict(self)

@dataclass
class UnitContext:
    unit: str
    multiplier: float
    source: str

@dataclass
class AuditRow:
    table: int
    page: Optional[int]
    row: int
    column: str
    raw_text: str
    raw_value: Optional[float]
    adjusted_value: Optional[float]
    unit: Optional[str]
    multiplier: Optional[float]
    source: Optional[str]

@dataclass
class TableInfo:
    table_number: int
    page: Optional[int]
    caption: Optional[str]
    table_unit: str
    table_multiplier: float
    table_multiplier_source: str
    column_overrides: Dict[int, dict]
    original_df: pd.DataFrame
    normalized_df: pd.DataFrame
    audit_df: pd.DataFrame
    shape: tuple
    is_empty: bool