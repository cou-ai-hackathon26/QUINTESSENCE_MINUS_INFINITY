"""
Hybrid Merchant Memory Retrieval Engine.
Combines exact entity filters, keyword lexical ranking, dense vector similarity, and Reciprocal Rank Fusion (RRF).
Enforces strict tenant scoping, revocation filtering, and exact-ID priority.
"""
from __future__ import annotations
import json
import math
import re
from typing import Any, Dict, List, Optional, Tuple
from sqlalchemy.orm import Session

from app.ingestion.adapters import normalize_bengali_digits
from app.persistence.models import DocumentChunkModel

# Reviewed MSME product and merchant aliases for semantic normalization
REVIEWED_ALIASES: Dict[str, str] = {
    "haque": "মেসার্স হক ট্রেডার্স",
    "haque traders": "মেসার্স হক ট্রেডার্স",
    "karim": "করিম ভাই",
    "rahim": "রহিম স্টোর",
    "madina": "আল মদিনা স্টোর",
    "soyabean tel": "সয়াবিন তেল",
    "soyabean oil": "সয়াবিন তেল",
    "dim": "মুরগির ডিম",
    "egg": "মুরগির ডিম",
    "chini": "সাদা চিনি",
    "sugar": "সাদা চিনি",
    "chal": "মিনিকেট চাল",
    "rice": "মিনিকেট চাল",
}

RRF_K = 60


def normalize_search_query(query: str) -> str:
    """Normalizes Bengali digits and reviewed Banglish/English product aliases."""
    normalized = normalize_bengali_digits(query.lower().strip())
    for alias, replacement in REVIEWED_ALIASES.items():
        if alias in normalized:
            normalized = normalized.replace(alias, replacement)
    return normalized


def compute_cosine_similarity(vec1: List[float], vec2: List[float]) -> float:
    """Computes cosine similarity between two float vectors."""
    if not vec1 or not vec2 or len(vec1) != len(vec2):
        return 0.0
    dot = sum(a * b for a, b in zip(vec1, vec2))
    norm1 = math.sqrt(sum(a * a for a in vec1))
    norm2 = math.sqrt(sum(b * b for b in vec2))
    if norm1 == 0 or norm2 == 0:
        return 0.0
    return dot / (norm1 * norm2)


def generate_lexical_embedding_double(text: str, dim: int = 16) -> List[float]:
    """
    Deterministic test double embedding generator based on token hashing.
    Used for local testing where remote Google text-embedding-004 is unconfigured.
    """
    vec = [0.0] * dim
    words = re.findall(r"\w+", text.lower())
    for w in words:
        h = hash(w) % dim
        vec[h] += 1.0
    norm = math.sqrt(sum(v * v for v in vec))
    if norm > 0:
        vec = [v / norm for v in vec]
    return vec


class RetrievalResult:
    def __init__(
        self,
        chunk_id: str,
        document_id: Optional[str],
        content: str,
        source_type: str,
        rrf_score: float,
        keyword_rank: int,
        dense_rank: int,
        metadata: Dict[str, Any],
        exact_id_match: bool = False,
    ):
        self.chunk_id = chunk_id
        self.document_id = document_id
        self.content = content
        self.source_type = source_type
        self.rrf_score = rrf_score
        self.keyword_rank = keyword_rank
        self.dense_rank = dense_rank
        self.metadata = metadata
        self.exact_id_match = exact_id_match

    def to_dict(self) -> Dict[str, Any]:
        return {
            "chunk_id": self.chunk_id,
            "document_id": self.document_id,
            "content": self.content,
            "source_type": self.source_type,
            "rrf_score": round(self.rrf_score, 4),
            "keyword_rank": self.keyword_rank,
            "dense_rank": self.dense_rank,
            "metadata": self.metadata,
            "exact_id_match": self.exact_id_match,
        }


class EvidencePack:
    def __init__(
        self,
        query: str,
        results: List[RetrievalResult],
        is_sufficient: bool,
        has_conflicts: bool = False,
        missing_reasons: Optional[List[str]] = None,
    ):
        self.query = query
        self.results = results
        self.is_sufficient = is_sufficient
        self.has_conflicts = has_conflicts
        self.missing_reasons = missing_reasons or []

    def to_dict(self) -> Dict[str, Any]:
        return {
            "query": self.query,
            "results_count": len(self.results),
            "is_sufficient": self.is_sufficient,
            "has_conflicts": self.has_conflicts,
            "missing_reasons": self.missing_reasons,
            "top_citations": [r.to_dict() for r in self.results[:5]],
        }


class HybridRetriever:
    """Executes tenant-isolated hybrid retrieval using exact filters, lexical ranking, and vector similarity."""

    def __init__(self, db: Session):
        self.db = db

    def search(
        self,
        tenant_id: str,
        query: str,
        target_invoice_ref: Optional[str] = None,
        source_type_filter: Optional[str] = None,
        top_k: int = 5,
        query_embedding: Optional[List[float]] = None,
    ) -> EvidencePack:
        # Pre-process query
        norm_query = normalize_search_query(query)
        target_ref_norm = normalize_bengali_digits(target_invoice_ref) if target_invoice_ref else None

        # 1. Tenant and revocation isolation filter
        q = (
            self.db.query(DocumentChunkModel)
            .filter(
                DocumentChunkModel.tenant_id == tenant_id,
                DocumentChunkModel.is_revoked == False,
            )
        )
        if source_type_filter:
            q = q.filter(DocumentChunkModel.source_type == source_type_filter)

        candidates = q.all()
        if not candidates:
            return EvidencePack(query=query, results=[], is_sufficient=False, missing_reasons=["No active chunks found for tenant."])

        # Generate query vector if not passed
        effective_query_vec = query_embedding or generate_lexical_embedding_double(norm_query)

        # 2. Score keyword matches
        keyword_scores: List[Tuple[DocumentChunkModel, float, bool]] = []
        for c in candidates:
            score = 0.0
            exact_match = False
            meta = json.loads(c.metadata_json) if c.metadata_json else {}

            # Exact invoice identity match boost
            c_invoice = str(meta.get("invoice_ref", ""))
            if target_ref_norm and c_invoice and normalize_bengali_digits(c_invoice) == target_ref_norm:
                exact_match = True
                score += 10.0
            elif target_ref_norm and target_ref_norm in c.normalized_content:
                exact_match = True
                score += 5.0

            # Lexical token matching
            q_tokens = re.findall(r"\w+", norm_query)
            for t in q_tokens:
                if t in c.normalized_content:
                    score += 1.0

            keyword_scores.append((c, score, exact_match))

        # Sort keyword rank (1-indexed)
        keyword_sorted = sorted(keyword_scores, key=lambda x: x[1], reverse=True)
        keyword_rank_map = {item[0].id: (idx + 1, item[2]) for idx, item in enumerate(keyword_sorted)}

        # 3. Score dense vector similarities
        dense_scores: List[Tuple[DocumentChunkModel, float]] = []
        for c in candidates:
            vec = json.loads(c.embedding_json) if c.embedding_json else generate_lexical_embedding_double(c.normalized_content)
            sim = compute_cosine_similarity(effective_query_vec, vec)
            dense_scores.append((c, sim))

        dense_sorted = sorted(dense_scores, key=lambda x: x[1], reverse=True)
        dense_rank_map = {item[0].id: idx + 1 for idx, item in enumerate(dense_sorted)}

        # 4. Reciprocal Rank Fusion (RRF)
        scored_results: List[RetrievalResult] = []
        for c in candidates:
            k_rank, is_exact = keyword_rank_map[c.id]
            d_rank = dense_rank_map[c.id]

            # Standard RRF formula
            rrf = (1.0 / (RRF_K + k_rank)) + (1.0 / (RRF_K + d_rank))
            # Exact invoice ID priority invariant: exact matches must outrank purely semantic look-alikes
            if is_exact:
                rrf += 1.0

            meta = json.loads(c.metadata_json) if c.metadata_json else {}
            scored_results.append(
                RetrievalResult(
                    chunk_id=c.id,
                    document_id=c.document_id,
                    content=c.content,
                    source_type=c.source_type,
                    rrf_score=rrf,
                    keyword_rank=k_rank,
                    dense_rank=d_rank,
                    metadata=meta,
                    exact_id_match=is_exact,
                )
            )

        scored_results.sort(key=lambda r: r.rrf_score, reverse=True)
        top_results = scored_results[:top_k]

        is_sufficient = len(top_results) > 0 and (top_results[0].exact_id_match or top_results[0].rrf_score > 0.02)
        has_conflicts = False

        # Detect conflicting terms (e.g. conflicting payment terms for same invoice)
        invoice_terms = set()
        for r in top_results:
            if "terms" in r.metadata:
                invoice_terms.add(r.metadata["terms"])
        if len(invoice_terms) > 1:
            has_conflicts = True

        return EvidencePack(
            query=query,
            results=top_results,
            is_sufficient=is_sufficient,
            has_conflicts=has_conflicts,
        )
