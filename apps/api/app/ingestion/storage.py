"""
Tenant-Isolated Storage Engine.
Manages private file storage, SHA-256 calculation, and size limits.
"""
import hashlib
import os
import re
from typing import Tuple
from fastapi import HTTPException, status

MAX_FILE_SIZE_BYTES = 10 * 1024 * 1024  # 10 MB limit


class EvidenceStorage:
    def __init__(self, base_dir: str = "apps/api/data/evidence") -> None:
        self.base_dir = os.path.abspath(base_dir)
        os.makedirs(self.base_dir, exist_ok=True)

    def _sanitize_filename(self, filename: str) -> str:
        # Strip path traversal characters
        cleaned = os.path.basename(filename)
        cleaned = re.sub(r"[^a-zA-Z0-9_.-]", "_", cleaned)
        return cleaned or "document.bin"

    def store_file(
        self, tenant_id: str, original_filename: str, content: bytes, mime_type: str
    ) -> Tuple[str, str, int, str]:
        """
        Validates size, calculates SHA-256, and stores in private tenant folder.
        Returns: (content_sha256, storage_path, file_size_bytes, source_type)
        """
        file_size = len(content)
        if file_size > MAX_FILE_SIZE_BYTES:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail=f"File exceeds maximum allowed size of {MAX_FILE_SIZE_BYTES // (1024*1024)}MB.",
            )

        sha256_hash = hashlib.sha256(content).hexdigest()
        sanitized_name = self._sanitize_filename(original_filename)

        # Detect source type
        mime_lower = mime_type.lower()
        if "pdf" in mime_lower or sanitized_name.endswith(".pdf"):
            source_type = "pdf"
        elif "image" in mime_lower or any(sanitized_name.endswith(ext) for ext in [".jpg", ".jpeg", ".png", ".webp"]):
            source_type = "image"
        elif "audio" in mime_lower or any(sanitized_name.endswith(ext) for ext in [".mp3", ".wav", ".m4a", ".ogg"]):
            source_type = "audio"
        else:
            source_type = "text"

        tenant_folder = os.path.join(self.base_dir, tenant_id)
        os.makedirs(tenant_folder, exist_ok=True)

        storage_filename = f"{sha256_hash[:16]}_{sanitized_name}"
        storage_path = os.path.join(tenant_folder, storage_filename)

        with open(storage_path, "wb") as f:
            f.write(content)

        return sha256_hash, storage_path, file_size, source_type


storage = EvidenceStorage()
