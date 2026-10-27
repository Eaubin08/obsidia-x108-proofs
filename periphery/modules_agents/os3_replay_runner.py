from __future__ import annotations

import hashlib
import json
from typing import Any

from .os3_ticket import sha256_obj, _obj_dict, build_os3_ticket
from .os3_replay_manifest import OS3ReplayManifest, build_replay_manifest


def _replay_compute_hashes(action_candidate: Any, packet: Any, envelope: Any) -> tuple[str, str, str, str]:
    ih = sha256_obj(_obj_dict(action_candidate))
    oh = sha256_obj(_obj_dict(envelope))
    th = sha256_obj({"input_hash": ih, "output_hash": oh, "packet": _obj_dict(packet)})
    mr = sha256_obj([ih, oh, th])
    return ih, oh, th, mr


def run_replay(ticket: Any, action_candidate: Any, packet: Any, envelope: Any) -> OS3ReplayManifest:
    manifest = build_replay_manifest(ticket)

    ih, oh, th, mr = _replay_compute_hashes(action_candidate, packet, envelope)
    replay_hash = sha256_obj({"ih": ih, "oh": oh, "th": th, "mr": mr})
    original_hash = sha256_obj({
        "ih": ticket.input_hash,
        "oh": ticket.output_hash,
        "th": ticket.trace_hash,
        "mr": ticket.merkle_root,
    })

    manifest.replay_hash = replay_hash

    if replay_hash == original_hash:
        manifest.replay_status = "PASS"
        manifest.replay_compare_result = "MATCH"
    else:
        manifest.replay_status = "FAIL"
        manifest.replay_compare_result = "MISMATCH"
        manifest.notes.append(f"replay_hash={replay_hash[:16]}… original={original_hash[:16]}…")

    return manifest


def replay_compare(original_hash: str, replay_hash: str) -> str:
    return "MATCH" if original_hash == replay_hash else "MISMATCH"
