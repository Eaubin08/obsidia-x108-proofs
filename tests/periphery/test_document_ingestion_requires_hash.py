import pytest
from periphery.ingestion.document_ingestion_pipeline import ingest_document
from periphery.ingestion.hash_ingestion import hash_content, verify_hash


def test_ingestion_produces_hash():
    doc = ingest_document("doc1", "Some content here.", "TRUSTED")
    assert doc.content_hash != ""
    assert len(doc.content_hash) == 64


def test_empty_content_rejected():
    doc = ingest_document("doc2", "", "TRUSTED")
    assert doc.status == "REJECTED"
    assert not doc.ingested


def test_untrusted_source_quarantined():
    doc = ingest_document("doc3", "Some content", "UNTRUSTED")
    assert doc.status == "QUARANTINED"
    assert not doc.ingested


def test_hash_verify():
    content = "Hello world"
    h = hash_content(content)
    assert verify_hash(content, h) is True
    assert verify_hash(content, "wrong_hash") is False
