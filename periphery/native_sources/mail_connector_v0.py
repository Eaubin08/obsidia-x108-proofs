"""MAIL_NATIVE_CONNECTOR_V0 — provider-neutral READONLY mail adapter.

V0 ships with a deterministic local JSON provider used for proof/sandbox.
A future Gmail/IMAP/M365 adapter must implement the same list/fetch contract.
"""
from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping, Optional

from .common_v0 import SOURCE_MAILBOX
from .connector_common_v0 import (
    NativeConnectorReadReceiptV0,
    build_native_connector_read_receipt_v0,
)
from .source_runtime_v0 import NativeSourceRuntimeV0


@dataclass(frozen=True)
class NativeMailMaterialV0:
    provider_item_id: str
    sender: str
    recipients: tuple[str, ...]
    subject: str
    body: str
    received_at: str
    attachment_count: int

    def ephemeral_dict(self) -> dict[str, Any]:
        return {
            "provider_item_id": self.provider_item_id,
            "sender": self.sender,
            "recipients": list(self.recipients),
            "subject": self.subject,
            "body": self.body,
            "received_at": self.received_at,
            "attachment_count": self.attachment_count,
        }


class LocalMailFixtureProviderV0:
    """READONLY JSON mailbox fixture provider.

    Each *.json file must contain:
    id, sender, recipients, subject, body, received_at, attachment_count.
    """

    provider_id = "LOCAL_MAIL_FIXTURE"
    network_capable = False
    readonly = True

    def __init__(self, root: Path):
        self.root = root

    def list_item_ids(self) -> list[str]:
        if not self.root.exists():
            return []
        ids = []
        for path in sorted(self.root.glob("*.json")):
            data = json.loads(path.read_text(encoding="utf-8"))
            ids.append(str(data["id"]))
        return ids

    def fetch(self, item_id: str) -> NativeMailMaterialV0:
        matches = []
        for path in sorted(self.root.glob("*.json")):
            data = json.loads(path.read_text(encoding="utf-8"))
            if str(data["id"]) == item_id:
                matches.append(data)
        if len(matches) != 1:
            raise ValueError("MAIL_NATIVE_PROVIDER_ITEM_NOT_UNIQUE")
        data = matches[0]
        required = {
            "id", "sender", "recipients", "subject", "body",
            "received_at", "attachment_count",
        }
        if set(data) != required:
            raise ValueError("MAIL_NATIVE_PROVIDER_ITEM_SHAPE_INVALID")
        if not isinstance(data["recipients"], list):
            raise ValueError("MAIL_NATIVE_RECIPIENTS_INVALID")
        if int(data["attachment_count"]) < 0:
            raise ValueError("MAIL_NATIVE_ATTACHMENT_COUNT_INVALID")
        return NativeMailMaterialV0(
            provider_item_id=str(data["id"]),
            sender=str(data["sender"]),
            recipients=tuple(str(x) for x in data["recipients"]),
            subject=str(data["subject"]),
            body=str(data["body"]),
            received_at=str(data["received_at"]),
            attachment_count=int(data["attachment_count"]),
        )


class MailNativeConnectorV0:
    connector_kind = "MAIL_NATIVE_CONNECTOR_V0"

    def __init__(
        self,
        *,
        runtime: NativeSourceRuntimeV0,
        source_id: str,
        provider: LocalMailFixtureProviderV0,
    ):
        self.runtime = runtime
        self.source_id = source_id
        self.provider = provider

    def _registration(self):
        registration = self.runtime.registry.load(self.source_id)
        if registration is None:
            raise ValueError("MAIL_NATIVE_SOURCE_NOT_REGISTERED")
        if registration.source_kind != SOURCE_MAILBOX:
            raise ValueError("MAIL_NATIVE_SOURCE_KIND_MISMATCH")
        if not self.runtime.registry.is_active(self.source_id):
            raise ValueError("MAIL_NATIVE_SOURCE_INACTIVE")
        if "READ_MESSAGE" not in registration.capabilities:
            raise ValueError("MAIL_NATIVE_READ_MESSAGE_SCOPE_REQUIRED")
        if self.provider.readonly is not True:
            raise ValueError("MAIL_NATIVE_PROVIDER_READONLY_REQUIRED")
        return registration

    def list_item_ids(self) -> list[str]:
        registration = self._registration()
        if "LIST" not in registration.capabilities and "SEARCH" not in registration.capabilities:
            raise ValueError("MAIL_NATIVE_LIST_OR_SEARCH_SCOPE_REQUIRED")
        return self.provider.list_item_ids()

    def read(
        self,
        item_id: str,
    ) -> tuple[NativeMailMaterialV0, Any, Any, NativeConnectorReadReceiptV0]:
        registration = self._registration()
        material = self.provider.fetch(item_id)
        metadata = {
            "material_schema": "OBSIDIA_NATIVE_MAIL_MATERIAL_V0",
            "sender_sha256": __import__("hashlib").sha256(
                material.sender.encode("utf-8")
            ).hexdigest(),
            "recipient_count": len(material.recipients),
            "recipients_sha256": __import__("hashlib").sha256(
                json.dumps(
                    sorted(material.recipients),
                    ensure_ascii=False,
                    separators=(",", ":"),
                ).encode("utf-8")
            ).hexdigest(),
            "subject_sha256": __import__("hashlib").sha256(
                material.subject.encode("utf-8")
            ).hexdigest(),
            "received_at": material.received_at,
            "attachment_count": material.attachment_count,
        }
        observation, packet = self.runtime.observe(
            source_id=self.source_id,
            provider_item_id=material.provider_item_id,
            content=material.body,
            metadata=metadata,
            observed_at=material.received_at,
        )
        receipt = build_native_connector_read_receipt_v0(
            connector_kind=self.connector_kind,
            read_operation="READ_MESSAGE",
            observation=observation,
            packet=packet,
            network_call_performed=self.provider.network_capable,
        )
        if receipt.provider != registration.provider:
            raise ValueError("MAIL_NATIVE_PROVIDER_BINDING_MISMATCH")
        return material, observation, packet, receipt
