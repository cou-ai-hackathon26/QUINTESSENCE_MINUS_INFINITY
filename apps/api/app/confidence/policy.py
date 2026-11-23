"""
Evidence Support Confidence Policy (version: evidence-support-v1).
Deterministic derivation of evidence support index, critical caps, and action readiness.
Never computes or claims a calibrated correctness probability.
"""
from __future__ import annotations
import math
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

POLICY_VERSION = "evidence-support-v1"
POLICY_KIND = "evidence_support_index"
CRITICAL_WEIGHT = 3
ORDINARY_WEIGHT = 1
CRITICAL_CAP = 59
STRONG_MIN = 85
REVIEW_MIN = 60


class ClaimInput(BaseModel):
    key: str
    critical: bool = False
    state: str = Field(..., pattern="^(supported|unknown|conflicted|unsupported)$")
    weight: Optional[int] = None
    source_locator: Optional[str] = None
    reasons: List[str] = Field(default_factory=list)


class ConfidenceResult(BaseModel):
    policy_version: str = POLICY_VERSION
    kind: str = POLICY_KIND
    base_score: Optional[int] = None
    score: Optional[int] = None
    band: str  # "strong", "review", "limited", "unavailable"
    readiness: str  # "ready_for_review", "needs_review", "needs_clarification", "blocked", "unavailable"
    can_execute_without_approval: bool = False
    has_critical_blocker: bool = False
    critical_blockers: List[str] = Field(default_factory=list)
    unavailable_reason: Optional[str] = None
    blocking_validation_failure: bool = False
    model_self_confidence: Optional[float] = None
    calibrated_probability: Optional[float] = None  # Explicitly null per Section D


def evaluate_confidence(
    claims: List[Dict[str, Any]],
    unavailable_reason: Optional[str] = None,
    blocking_validation_failure: bool = False,
    model_self_confidence: Optional[float] = None,
) -> ConfidenceResult:
    """
    Computes deterministic evidence-support-v1 index.
    Formula: base = floor(100 * sum(weights of supported) / sum(weights of required) + 0.5)
    If critical claim is not supported, cap score at 59 and route to needs_clarification.
    """
    if unavailable_reason:
        return ConfidenceResult(
            base_score=None,
            score=None,
            band="unavailable",
            readiness="unavailable",
            can_execute_without_approval=False,
            unavailable_reason=unavailable_reason,
            blocking_validation_failure=blocking_validation_failure,
            model_self_confidence=model_self_confidence,
        )

    if blocking_validation_failure:
        return ConfidenceResult(
            base_score=None,
            score=None,
            band="unavailable",
            readiness="blocked",
            can_execute_without_approval=False,
            blocking_validation_failure=True,
            model_self_confidence=model_self_confidence,
        )

    if not claims:
        return ConfidenceResult(
            base_score=None,
            score=None,
            band="unavailable",
            readiness="unavailable",
            can_execute_without_approval=False,
            model_self_confidence=model_self_confidence,
        )

    total_weight = 0
    supported_weight = 0
    critical_blockers = []

    for c in claims:
        is_crit = bool(c.get("critical", False))
        weight = c.get("weight") or (CRITICAL_WEIGHT if is_crit else ORDINARY_WEIGHT)
        state = c.get("state", "unknown")

        total_weight += weight
        if state == "supported":
            supported_weight += weight
        elif is_crit:
            critical_blockers.append(c.get("key", "critical_claim"))

    if total_weight == 0:
        base_score = 0
    else:
        base_score = math.floor(100.0 * supported_weight / total_weight + 0.5)

    has_crit_blocker = len(critical_blockers) > 0

    if has_crit_blocker:
        score = min(base_score, CRITICAL_CAP)
        band = "review" if score >= REVIEW_MIN else "limited"
        readiness = "needs_clarification"
    else:
        score = base_score
        if score >= STRONG_MIN:
            band = "strong"
            readiness = "ready_for_review"
        elif score >= REVIEW_MIN:
            band = "review"
            readiness = "needs_review"
        else:
            band = "limited"
            readiness = "needs_clarification"

    return ConfidenceResult(
        base_score=base_score,
        score=score,
        band=band,
        readiness=readiness,
        can_execute_without_approval=False,
        has_critical_blocker=has_crit_blocker,
        critical_blockers=critical_blockers,
        unavailable_reason=None,
        blocking_validation_failure=False,
        model_self_confidence=model_self_confidence,
    )
