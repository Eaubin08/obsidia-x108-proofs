"""
Regression tests for Obsidure MathMemory context-pack fallback.

These tests intentionally avoid any write to proofs/, kernel, or canonical memory.
"""
from periphery.agents import agent_obsidure as ao


class _ProviderWithoutResearch:
    def list_ids(self):
        return ["P36"]

    def explain_boundary(self):
        return {
            "readonly": True,
            "kernel_mutation": False,
            "emits_act": False,
            "memory_write": False,
        }

    def get_pepite(self, pepite_id):
        if pepite_id != "P36":
            return "MISSING_CONTEXT"
        return {
            "id": "P36",
            "status": "CANONICAL_CANDIDATE",
            "can_be_used_by_obsidure": True,
            "lean_signature_candidate": "example",
            "missing_dependencies": [],
        }

    def get_status(self, pepite_id):
        return "CANONICAL_CANDIDATE"

    def can_use_for_proof(self, pepite_id):
        return False

    def get_missing_dependencies(self, pepite_id):
        return []


class _ProviderWithResearch(_ProviderWithoutResearch):
    def research_context(self, objective):
        return {
            "availability": "AVAILABLE",
            "source_evidence": [{"objective": objective}],
            "source_errors": [],
        }


def test_math_context_pack_falls_back_when_research_hook_is_absent(monkeypatch):
    provider = _ProviderWithoutResearch()
    monkeypatch.setattr(ao, "_MATH_PROVIDER_OK", True)
    monkeypatch.setattr(ao, "_get_math_provider", lambda: provider)

    pack = ao._build_math_memory_context_pack("P36")

    assert pack["status"] == "AVAILABLE"
    assert pack["selected_count"] == 1
    assert pack["selected_items"][0]["id"] == "P36"
    assert pack["boundary"]["readonly"] is True
    assert pack["boundary"]["kernel_mutation"] is False
    assert pack["boundary"]["emits_act"] is False
    assert pack["boundary"]["memory_write"] is False


def test_math_context_pack_uses_optional_research_hook_when_present(monkeypatch):
    provider = _ProviderWithResearch()
    monkeypatch.setattr(ao, "_MATH_PROVIDER_OK", True)
    monkeypatch.setattr(ao, "_get_math_provider", lambda: provider)

    pack = ao._build_math_memory_context_pack("cherche contexte")

    assert pack["source"] == "OBSIDURE_RESEARCH_ROOT"
    assert pack["status"] == "AVAILABLE"
    assert pack["selected_count"] == 1
    assert pack["boundary"]["readonly"] is True
    assert pack["boundary"]["kernel_mutation"] is False
    assert pack["boundary"]["emits_act"] is False
    assert pack["boundary"]["memory_write"] is False
