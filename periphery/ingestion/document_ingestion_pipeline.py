from __future__ import annotations

import hashlib
from dataclasses import dataclass
from typing import Any


@dataclass
class IngestedDocument:
    doc_id: str
    source_class: str
    content_hash: str
    status: str
    ingested: bool = False
    reason: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "doc_id": self.doc_id,
            "source_class": self.source_class,
            "content_hash": self.content_hash,
            "status": self.status,
            "ingested": self.ingested,
            "reason": self.reason,
        }


def ingest_document(doc_id: str, content: str, source_class: str) -> IngestedDocument:
    if not content:
        return IngestedDocument(
            doc_id=doc_id,
            source_class=source_class,
            content_hash="",
            status="REJECTED",
            reason="EMPTY_CONTENT",
        )

    content_hash = hashlib.sha256(content.encode("utf-8")).hexdigest()

    if source_class == "UNTRUSTED":
        return IngestedDocument(
            doc_id=doc_id,
            source_class=source_class,
            content_hash=content_hash,
            status="QUARANTINED",
            reason="UNTRUSTED_SOURCE",
        )

    return IngestedDocument(
        doc_id=doc_id,
        source_class=source_class,
        content_hash=content_hash,
        status="INGESTED",
        ingested=True,
        reason="HASH_VERIFIED",
    )
