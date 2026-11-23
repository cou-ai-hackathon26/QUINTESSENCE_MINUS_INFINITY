"""Exact import values and safe spreadsheet text; no inferred accounting."""
import re
from decimal import Decimal

_DIGITS = str.maketrans('০১২৩৪৫৬৭৮৯', '0123456789')


def csv_paisa(value: str) -> int:
    text = str(value).strip().translate(_DIGITS)
    if not re.fullmatch(r'(?:\d+|\d{1,3}(?:,\d{3})+)(?:\.\d{1,2})?', text):
        raise ValueError('Use a non-negative BDT amount with at most two decimal places.')
    amount = int(Decimal(text.replace(',', '')) * 100)
    if amount > 99_999_999_999:
        raise ValueError('Amount exceeds the supported limit.')
    return amount


def csv_count(value: str, label: str, maximum: int = 1_000_000_000) -> int:
    text = str(value).strip().translate(_DIGITS)
    if not re.fullmatch(r'\d{1,10}', text) or int(text) > maximum:
        raise ValueError(f'{label} must be a non-negative whole number within {maximum}.')
    return int(text)


def spreadsheet_text(value: str) -> str:
    text = str(value or '')
    if text.lstrip().startswith(('=', '+', '-', '@')) or text.startswith(('\t', '\r', '\n')):
        return "'" + text
    return text
