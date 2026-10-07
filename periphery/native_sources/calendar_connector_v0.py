"""CALENDAR_NATIVE_CONNECTOR_V0 — provider-neutral READONLY calendar adapter."""
from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .common_v0 import SOURCE_CALENDAR
from .connector_common_v0 import (
    NativeConnectorReadReceiptV0,
    build_native_connector_read_receipt_v0,
)
from .source_runtime_v0 import NativeSourceRuntimeV0


@dataclass(frozen=True)
class NativeCalendarMaterialV0:
    provider_item_id: str
    title: str
    description: str
    start_time: str
    end_time: str
    timezone: str
    attendee_count: int
    location: str | None

    def ephemeral_dict(self) -> dict[str, Any]:
        return {
            "provider_item_id": self.provider_item_id,
            "title": self.title,
            "description": self.description,
            "start_time": self.start_time,
            "end_time": self.end_time,
            "timezone": self.timezone,
            "attendee_count": self.attendee_count,
            "location": self.location,
        }


class LocalCalendarFixtureProviderV0:
    provider_id = "LOCAL_CALENDAR_FIXTURE"
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

    def fetch(self, item_id: str) -> NativeCalendarMaterialV0:
        matches = []
        for path in sorted(self.root.glob("*.json")):
            data = json.loads(path.read_text(encoding="utf-8"))
            if str(data["id"]) == item_id:
                matches.append(data)
        if len(matches) != 1:
            raise ValueError("CALENDAR_NATIVE_PROVIDER_ITEM_NOT_UNIQUE")
        data = matches[0]
        required = {
            "id", "title", "description", "start_time", "end_time",
            "timezone", "attendee_count", "location",
        }
        if set(data) != required:
            raise ValueError("CALENDAR_NATIVE_PROVIDER_ITEM_SHAPE_INVALID")
        if int(data["attendee_count"]) < 0:
            raise ValueError("CALENDAR_NATIVE_ATTENDEE_COUNT_INVALID")
        from .common_v0 import require_time
        require_time(str(data["start_time"]))
        require_time(str(data["end_time"]))
        if str(data["end_time"]) <= str(data["start_time"]):
            # ISO-8601 values in fixtures use the same offset/timezone.
            raise ValueError("CALENDAR_NATIVE_TIME_RANGE_INVALID")
        return NativeCalendarMaterialV0(
            provider_item_id=str(data["id"]),
            title=str(data["title"]),
            description=str(data["description"]),
            start_time=str(data["start_time"]),
            end_time=str(data["end_time"]),
            timezone=str(data["timezone"]),
            attendee_count=int(data["attendee_count"]),
            location=None if data["location"] is None else str(data["location"]),
        )


class CalendarNativeConnectorV0:
    connector_kind = "CALENDAR_NATIVE_CONNECTOR_V0"

    def __init__(
        self,
        *,
        runtime: NativeSourceRuntimeV0,
        source_id: str,
        provider: LocalCalendarFixtureProviderV0,
    ):
        self.runtime = runtime
        self.source_id = source_id
        self.provider = provider

    def _registration(self):
        registration = self.runtime.registry.load(self.source_id)
        if registration is None:
            raise ValueError("CALENDAR_NATIVE_SOURCE_NOT_REGISTERED")
        if registration.source_kind != SOURCE_CALENDAR:
            raise ValueError("CALENDAR_NATIVE_SOURCE_KIND_MISMATCH")
        if not self.runtime.registry.is_active(self.source_id):
            raise ValueError("CALENDAR_NATIVE_SOURCE_INACTIVE")
        if "READ_EVENT" not in registration.capabilities:
            raise ValueError("CALENDAR_NATIVE_READ_SCOPE_REQUIRED")
        if self.provider.readonly is not True:
            raise ValueError("CALENDAR_NATIVE_PROVIDER_READONLY_REQUIRED")
        return registration

    def list_item_ids(self) -> list[str]:
        registration = self._registration()
        if "LIST" not in registration.capabilities and "SEARCH" not in registration.capabilities:
            raise ValueError("CALENDAR_NATIVE_LIST_OR_SEARCH_SCOPE_REQUIRED")
        return self.provider.list_item_ids()

    def read(
        self,
        item_id: str,
    ) -> tuple[NativeCalendarMaterialV0, Any, Any, NativeConnectorReadReceiptV0]:
        registration = self._registration()
        material = self.provider.fetch(item_id)
        import hashlib
        content = json.dumps(
            {
                "title": material.title,
                "description": material.description,
                "start_time": material.start_time,
                "end_time": material.end_time,
                "timezone": material.timezone,
                "attendee_count": material.attendee_count,
                "location": material.location,
            },
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
        )
        metadata = {
            "material_schema": "OBSIDIA_NATIVE_CALENDAR_MATERIAL_V0",
            "title_sha256": hashlib.sha256(
                material.title.encode("utf-8")
            ).hexdigest(),
            "start_time": material.start_time,
            "end_time": material.end_time,
            "timezone": material.timezone,
            "attendee_count": material.attendee_count,
            "location_sha256": (
                None
                if material.location is None
                else hashlib.sha256(material.location.encode("utf-8")).hexdigest()
            ),
        }
        observation, packet = self.runtime.observe(
            source_id=self.source_id,
            provider_item_id=material.provider_item_id,
            content=content,
            metadata=metadata,
            observed_at=material.start_time,
        )
        receipt = build_native_connector_read_receipt_v0(
            connector_kind=self.connector_kind,
            read_operation="READ_EVENT",
            observation=observation,
            packet=packet,
            network_call_performed=self.provider.network_capable,
        )
        if receipt.provider != registration.provider:
            raise ValueError("CALENDAR_NATIVE_PROVIDER_BINDING_MISMATCH")
        return material, observation, packet, receipt
