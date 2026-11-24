"""Deterministic supplier-payment allocation. Models may propose facts, never amounts."""
from dataclasses import dataclass
from typing import Iterable, Optional


@dataclass(frozen=True)
class OpenInvoice:
    obligation_id: str
    remaining_paisa: int
    due_sort: str
    invoice_ref: str
    version: int


@dataclass(frozen=True)
class ProposedAllocation:
    obligation_id: str
    amount_paisa: int
    obligation_version: int


@dataclass(frozen=True)
class SplitProposal:
    lines: list[ProposedAllocation]
    allocated_paisa: int
    unallocated_paisa: int


def propose_oldest_due_first(amount_paisa: int, invoices: Iterable[OpenInvoice]) -> SplitProposal:
    if type(amount_paisa) is not int or amount_paisa <= 0:
        raise ValueError("Payment amount must be a positive integer-paisa value.")
    remaining = amount_paisa
    lines: list[ProposedAllocation] = []
    ordered = sorted(invoices, key=lambda row: (row.due_sort, row.invoice_ref.casefold(), row.obligation_id))
    for invoice in ordered:
        if invoice.remaining_paisa <= 0 or remaining <= 0:
            continue
        applied = min(remaining, invoice.remaining_paisa)
        lines.append(ProposedAllocation(invoice.obligation_id, applied, invoice.version))
        remaining -= applied
    return SplitProposal(lines, amount_paisa - remaining, remaining)


def validate_manual_split(
    amount_paisa: int,
    invoices: dict[str, OpenInvoice],
    requested: Iterable[tuple[str, int]],
) -> SplitProposal:
    if type(amount_paisa) is not int or amount_paisa <= 0:
        raise ValueError("Payment amount must be a positive integer-paisa value.")
    seen: set[str] = set()
    lines: list[ProposedAllocation] = []
    total = 0
    for obligation_id, value in requested:
        if obligation_id in seen:
            raise ValueError("Each invoice may appear only once.")
        seen.add(obligation_id)
        if type(value) is not int or value <= 0:
            raise ValueError("Every allocation must be a positive integer-paisa value.")
        invoice = invoices.get(obligation_id)
        if not invoice:
            raise ValueError("An invoice is unavailable for this supplier.")
        if value > invoice.remaining_paisa:
            raise ValueError(f"Allocation exceeds the remaining balance of {invoice.invoice_ref}.")
        total += value
        if total > amount_paisa:
            raise ValueError("Allocations exceed the payment amount.")
        lines.append(ProposedAllocation(obligation_id, value, invoice.version))
    if total != amount_paisa:
        raise ValueError("Allocate the full payment before recording it.")
    return SplitProposal(lines, total, 0)
