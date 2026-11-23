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
from app.retrieval import semantic

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
    for alias, replacement in sorted(REVIEWED_ALIASES.items(),key=lambda item:-len(item[0])):
        normalized=re.sub(r'(?<!\w)'+re.escape(alias)+r'(?!\w)',replacement,normalized)
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
            "results": [r.to_dict() for r in self.results],
            "retrieval_mode": getattr(self,"retrieval_mode","keyword_only"),
            "semantic": semantic.status(),
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

        # Real local inference only. Existing hash vectors have no matching model identity and are ignored.
        vectors,identity=semantic.encode([query],query=True)
        effective_query_vec=vectors[0] if vectors else None
        missing=[c for c in candidates if not c.embedding_json or json.loads(c.metadata_json or '{}').get('embedding_model')!=identity]
        if identity and missing:
            generated,generated_identity=semantic.encode([c.content for c in missing[:64]])
            if generated:
                for chunk,vector in zip(missing[:64],generated):
                    meta=json.loads(chunk.metadata_json or '{}');meta.update({'embedding_model':generated_identity,'embedding_dimension':len(vector),'embedding_status':'generated'})
                    chunk.embedding_json=json.dumps(vector);chunk.metadata_json=json.dumps(meta)
                self.db.flush()

        # Unicode whitespace tokens preserve Bengali combining marks. BM25 uses actual corpus counts.
        def tokens(text):return re.findall(r'[^\s,;:.!?()\[\]"।]+',text.lower())
        query_tokens=[t for t in tokens(norm_query) if t not in {'the','a','an','is','my','what','were','are','of','for','and','to','how','do','i'}]
        corpus={c.id:tokens(c.normalized_content or normalize_search_query(c.content)) for c in candidates}
        mean_length=sum(map(len,corpus.values()))/max(1,len(candidates))
        keyword_scores=[];exact_matches={}
        for c in candidates:
            meta=json.loads(c.metadata_json or '{}');ref=normalize_bengali_digits(str(meta.get('invoice_ref',''))).lower()
            exact=bool(target_ref_norm and ref==target_ref_norm.lower())
            if target_ref_norm and target_ref_norm.lower() in (c.normalized_content or '').lower():exact=True
            exact_matches[c.id]=exact
            words=corpus[c.id];score=0.0
            for token in set(query_tokens):
                frequency=words.count(token)
                if not frequency:continue
                documents=sum(token in values for values in corpus.values())
                idf=math.log(1+(len(candidates)-documents+0.5)/(documents+0.5))
                score+=idf*(frequency*2.2)/(frequency+1.2*(0.25+0.75*len(words)/max(1,mean_length)))
            if score>0 or exact:keyword_scores.append((c,score))
        keyword_scores.sort(key=lambda row:row[1],reverse=True)
        keyword_rank={row[0].id:index+1 for index,row in enumerate(keyword_scores)}
        dense_scores=[]
        for c in candidates:
            meta=json.loads(c.metadata_json or '{}')
            if not effective_query_vec or meta.get('embedding_model')!=identity or not c.embedding_json:continue
            similarity=compute_cosine_similarity(effective_query_vec,json.loads(c.embedding_json))
            if similarity>=0.78:dense_scores.append((c,similarity))
        dense_scores.sort(key=lambda row:row[1],reverse=True)
        dense_rank={row[0].id:index+1 for index,row in enumerate(dense_scores)}
        scored=[]
        for c in candidates:
            kr=keyword_rank.get(c.id,0);dr=dense_rank.get(c.id,0);exact=exact_matches[c.id]
            if not kr and not dr and not exact:continue
            score=(1/(RRF_K+kr) if kr else 0)+(1/(RRF_K+dr) if dr else 0)+(1 if exact else 0)
            scored.append(RetrievalResult(c.id,c.document_id,c.content,c.source_type,score,kr,dr,json.loads(c.metadata_json or '{}'),exact))
        scored.sort(key=lambda row:row.rrf_score,reverse=True)
        top=scored[:top_k]
        terms={str(r.metadata.get('terms')) for r in top if 'terms' in r.metadata}
        conflicts=len(terms)>1
        pack=EvidencePack(query,top,bool(top) and not conflicts,conflicts,[] if top else ['No matching active evidence.'])
        pack.retrieval_mode='hybrid_bm25_dense_rrf' if effective_query_vec else 'keyword_only'
        return pack
