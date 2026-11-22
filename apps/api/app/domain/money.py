"""
Exact Money & Currency Domain Primitive.
Financial Invariant: Money is represented as an integer number of paisa (1 BDT = 100 paisa).
Floating-point values are strictly prohibited for balances and calculations.
"""
from __future__ import annotations
from decimal import Decimal
from typing import Any, Union


class Money:
    __slots__ = ("_paisa", "_currency")

    def __init__(self, paisa: int, currency: str = "BDT") -> None:
        if not isinstance(paisa, int) or isinstance(paisa, bool):
            raise TypeError(f"Money amount must be an integer paisa count, got {type(paisa).__name__}: {paisa}")
        if not isinstance(currency, str) or currency.upper() != "BDT":
            raise ValueError(f"Only BDT currency is supported, got: {currency}")
        self._paisa: int = paisa
        self._currency: str = "BDT"

    @property
    def paisa(self) -> int:
        return self._paisa

    @property
    def currency(self) -> str:
        return self._currency

    @classmethod
    def from_bdt_decimal(cls, bdt: Union[Decimal, str, int]) -> Money:
        """Converts exact decimal BDT to integer paisa (e.g. Decimal('25.50') -> 2550 paisa)."""
        dec = Decimal(str(bdt))
        paisa = int((dec * 100).to_integral_value())
        return cls(paisa)

    def to_bdt_decimal(self) -> Decimal:
        """Converts integer paisa to Decimal BDT."""
        return Decimal(self._paisa) / Decimal(100)

    def is_zero(self) -> bool:
        return self._paisa == 0

    def is_positive(self) -> bool:
        return self._paisa > 0

    def is_negative(self) -> bool:
        return self._paisa < 0

    def __add__(self, other: Any) -> Money:
        if not isinstance(other, Money):
            raise TypeError(f"Cannot add Money and {type(other).__name__}")
        return Money(self._paisa + other._paisa)

    def __sub__(self, other: Any) -> Money:
        if not isinstance(other, Money):
            raise TypeError(f"Cannot subtract {type(other).__name__} from Money")
        return Money(self._paisa - other._paisa)

    def __mul__(self, other: Any) -> Money:
        if not isinstance(other, int) or isinstance(other, bool):
            raise TypeError(f"Money can only be multiplied by an integer, got {type(other).__name__}")
        return Money(self._paisa * other)

    def __neg__(self) -> Money:
        return Money(-self._paisa)

    def __abs__(self) -> Money:
        return Money(abs(self._paisa))

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, Money):
            return False
        return self._paisa == other._paisa and self._currency == other._currency

    def __lt__(self, other: Any) -> bool:
        if not isinstance(other, Money):
            raise TypeError(f"Cannot compare Money with {type(other).__name__}")
        return self._paisa < other._paisa

    def __le__(self, other: Any) -> bool:
        if not isinstance(other, Money):
            raise TypeError(f"Cannot compare Money with {type(other).__name__}")
        return self._paisa <= other._paisa

    def __gt__(self, other: Any) -> bool:
        if not isinstance(other, Money):
            raise TypeError(f"Cannot compare Money with {type(other).__name__}")
        return self._paisa > other._paisa

    def __ge__(self, other: Any) -> bool:
        if not isinstance(other, Money):
            raise TypeError(f"Cannot compare Money with {type(other).__name__}")
        return self._paisa >= other._paisa

    def __repr__(self) -> str:
        return f"Money({self._paisa} paisa, {self._currency})"

    def format_bdt(self) -> str:
        bdt = self.to_bdt_decimal()
        return f"BDT {bdt:,.2f}"

    def format_bangla(self) -> str:
        bdt = self.to_bdt_decimal()
        eng_str = f"৳ {bdt:,.2f}"
        bangla_digits = {"0": "০", "1": "১", "2": "২", "3": "৩", "4": "৪", "5": "৫", "6": "৬", "7": "৭", "8": "৮", "9": "৯"}
        return "".join(bangla_digits.get(ch, ch) for ch in eng_str)
