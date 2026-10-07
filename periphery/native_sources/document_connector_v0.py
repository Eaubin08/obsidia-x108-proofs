"""DOCUMENT_NATIVE_CONNECTOR_V0 — READONLY filesystem document adapter."""
from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .common_v0 import SOURCE_DOCUMENT_REPOSITORY
from .connector_common_v0 import (
    NativeConnectorReadReceiptV0,
    build_native_connector_read_receipt_v0,
)
from .source_runtime_v0 import NativeSourceRuntimeV0


@dataclass(frozen=True)
class NativeDocumentMaterialV0:
    provider_item_id: str
    relative_path: str
    content: str
    byte_size: int
    extension: str

    def ephemeral_dict(self) -> dict[str, Any]:
        return {
            "provider_item_id": self.provider_item_id,
            "relative_path": self.relative_path,
            "content": self.content,
            "byte_size": self.byte_size,
            "extension": self.extension,
        }


class LocalDocumentRepositoryProviderV0:
    provider_id = "LOCAL_DOCUMENT_REPOSITORY"
    network_capable = False
    readonly = True
    allowed_extensions = {".txt", ".md", ".json", ".csv"}

    def __init__(self, root: Path):
        self.root = root.resolve()

    def _safe_path(self, relative_path: str) -> Path:
        candidate = (self.root / relative_path).resolve()
        try:
            candidate.relative_to(self.root)
        except ValueError as exc:
            raise ValueError("DOCUMENT_NATIVE_PATH_ESCAPE_FORBIDDEN") from exc
        return candidate

    def list_item_ids(self) -> list[str]:
        if not self.root.exists():
            return []
        out = []
        for path in sorted(p for p in self.root.rglob("*") if p.is_file()):
            if path.suffix.lower() in self.allowed_extensions:
                out.append(path.relative_to(self.root).as_posix())
        return out

    def fetch(self, item_id: str) -> NativeDocumentMaterialV0:
        path = self._safe_path(item_id)
        if not path.is_file():
            raise ValueError("DOCUMENT_NATIVE_ITEM_NOT_FOUND")
        if path.suffix.lower() not in self.allowed_extensions:
            raise ValueError("DOCUMENT_NATIVE_EXTENSION_UNSUPPORTED")
        raw = path.read_bytes()
        try:
            content = raw.decode("utf-8")
        except UnicodeDecodeError as exc:
            raise ValueError("DOCUMENT_NATIVE_UTF8_REQUIRED_V0") from exc
        return NativeDocumentMaterialV0(
            provider_item_id=item_id,
            relative_path=item_id,
            content=content,
            byte_size=len(raw),
            extension=path.suffix.lower(),
        )


class DocumentNativeConnectorV0:
    connector_kind = "DOCUMENT_NATIVE_CONNECTOR_V0"

    def __init__(
        self,
        *,
        runtime: NativeSourceRuntimeV0,
        source_id: str,
        provider: LocalDocumentRepositoryProviderV0,
    ):
        self.runtime = runtime
        self.source_id = source_id
        self.provider = provider

    def _registration(self):
        registration = self.runtime.registry.load(self.source_id)
        if registration is None:
            raise ValueError("DOCUMENT_NATIVE_SOURCE_NOT_REGISTERED")
        if registration.source_kind != SOURCE_DOCUMENT_REPOSITORY:
            raise ValueError("DOCUMENT_NATIVE_SOURCE_KIND_MISMATCH")
        if not self.runtime.registry.is_active(self.source_id):
            raise ValueError("DOCUMENT_NATIVE_SOURCE_INACTIVE")
        if "READ_DOCUMENT" not in registration.capabilities:
            raise ValueError("DOCUMENT_NATIVE_READ_SCOPE_REQUIRED")
        if self.provider.readonly is not True:
            raise ValueError("DOCUMENT_NATIVE_PROVIDER_READONLY_REQUIRED")
        return registration

    def list_item_ids(self) -> list[str]:
        registration = self._registration()
        if "LIST" not in registration.capabilities and "SEARCH" not in registration.capabilities:
            raise ValueError("DOCUMENT_NATIVE_LIST_OR_SEARCH_SCOPE_REQUIRED")
        return self.provider.list_item_ids()

    def read(
        self,
        item_id: str,
        *,
        observed_at: str,
    ) -> tuple[NativeDocumentMaterialV0, Any, Any, NativeConnectorReadReceiptV0]:
        registration = self._registration()
        material = self.provider.fetch(item_id)
        import hashlib
        metadata = {
            "material_schema": "OBSIDIA_NATIVE_DOCUMENT_MATERIAL_V0",
            "relative_path_sha256": hashlib.sha256(
                material.relative_path.encode("utf-8")
            ).hexdigest(),
            "byte_size": material.byte_size,
            "extension": material.extension,
        }
        observation, packet = self.runtime.observe(
            source_id=self.source_id,
            provider_item_id=material.provider_item_id,
            content=material.content,
            metadata=metadata,
            observed_at=observed_at,
        )
        receipt = build_native_connector_read_receipt_v0(
            connector_kind=self.connector_kind,
            read_operation="READ_DOCUMENT",
            observation=observation,
            packet=packet,
            network_call_performed=self.provider.network_capable,
        )
        if receipt.provider != registration.provider:
            raise ValueError("DOCUMENT_NATIVE_PROVIDER_BINDING_MISMATCH")
        return material, observation, packet, receipt
