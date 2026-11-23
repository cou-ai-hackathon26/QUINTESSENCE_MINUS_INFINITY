"""Reject unsupported explicit monetary claims; not a general entailment oracle."""
import re
from decimal import Decimal
from app.groq_provider import InferenceUnavailable

_DIGITS = str.maketrans('০১২৩৪৫৬৭৮৯', '0123456789')
_NUMBER = r'(-?\d[\d,]*(?:\.\d{1,2})?)'
_MONEY = re.compile(r'(?:৳|\bBDT\b|\bTk\.?|\bTaka\b)\s*' + _NUMBER + r'|' + _NUMBER + r'\s*(?:Taka\b|টাকা|BDT\b)', re.I)


def monetary_values(context):
    values = set()
    def walk(value, key=''):
        if isinstance(value, dict):
            for k, v in value.items(): walk(v, k)
        elif isinstance(value, list):
            for v in value: walk(v, key)
        elif isinstance(value, int) and not isinstance(value, bool) and (key.endswith('_paisa') or key == 'expected_payables'):
            values.add(value)
    walk(context)
    # Retrieved originals may establish document amounts absent from the ledger.
    originals = list(context.get('retrieved_sources', context.get('sources', [])))
    originals.append({'text': context.get('question', '')})
    for source in originals:
        for match in _MONEY.finditer(source.get('text', '').translate(_DIGITS)):
            values.add(int(Decimal((match.group(1) or match.group(2)).replace(',', '')) * 100))
    return values


def validate_money_mentions(text, context):
    allowed = monetary_values(context)
    for match in _MONEY.finditer(text.translate(_DIGITS)):
        number = (match.group(1) or match.group(2)).replace(',', '')
        if int(Decimal(number) * 100) not in allowed:
            raise InferenceUnavailable('unsupported_financial_claim', 422)
