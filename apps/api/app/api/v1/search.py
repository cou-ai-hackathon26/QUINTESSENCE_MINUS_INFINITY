"""
Hybrid Search and Document Chunk Indexing Router.
Provides tenant-isolated hybrid retrieval and evidence pack compilation.
"""
import json
from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.core.auth import get_current_user
from app.core.database import get_db
from app.ingestion.adapters import normalize_bengali_digits
from app.persistence.models import DocumentChunkModel, UserModel
from app.retrieval.engine import (
    HybridRetriever,
    generate_lexical_embedding_double,
    normalize_search_query,
)

search_router = APIRouter(prefix="/api/v1/search", tags=["Search"])


class SearchRequestDTO(BaseModel):
    query: str = Field(..., min_length=1)
    target_invoice_ref: Optional[str] = None
    source_type_filter: Optional[str] = None
    top_k: int = Field(5, ge=1, le=20)


class IndexChunkDTO(BaseModel):
    document_id: Optional[str] = None
    source_type: str = Field(..., pattern="^(invoice|bill|offer|note|audio_transcript|return_terms)$")
    content: str = Field(..., min_length=1)
    metadata: Optional[Dict[str, Any]] = None
    embedding: Optional[List[float]] = None


@search_router.post("")
def hybrid_search(
    req: SearchRequestDTO,
    current_user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Executes tenant-isolated hybrid search combining keyword and vector scoring via RRF."""
    retriever = HybridRetriever(db)
    pack = retriever.search(
        tenant_id=current_user.tenant_id,
        query=req.query,
        target_invoice_ref=req.target_invoice_ref,
        source_type_filter=req.source_type_filter,
        top_k=req.top_k,
    )
    return pack.to_dict()


@search_router.post("/index", status_code=status.HTTP_201_CREATED)
def index_chunk(
    req: IndexChunkDTO,
    current_user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Indexes a document chunk with normalized content and embeddings."""
    norm_content = normalize_search_query(req.content)
    embedding = req.embedding or generate_lexical_embedding_double(norm_content)

    chunk = DocumentChunkModel(
        tenant_id=current_user.tenant_id,
        document_id=req.document_id,
        source_type=req.source_type,
        content=req.content,
        normalized_content=norm_content,
        metadata_json=json.dumps(req.metadata) if req.metadata else None,
        embedding_json=json.dumps(embedding),
    )
    db.add(chunk)
    db.commit()
    db.refresh(chunk)
    return {"status": "indexed", "chunk_id": chunk.id}


@search_router.post("/chunks/{chunk_id}/revoke")
def revoke_chunk(
    chunk_id: str,
    current_user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Revokes a document chunk so it is immediately excluded from future retrieval."""
    chunk = (
        db.query(DocumentChunkModel)
        .filter(DocumentChunkModel.id == chunk_id, DocumentChunkModel.tenant_id == current_user.tenant_id)
        .first()
    )
    if not chunk:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Chunk not found.")

    chunk.is_revoked = True
    db.commit()
    return {"status": "revoked", "chunk_id": chunk.id}
