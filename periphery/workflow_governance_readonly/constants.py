"""Global constants for OBSIDIA_WORKFLOW_GOVERNANCE_PRIMITIVE_V5.

The constants intentionally centralize every boundary bit. Agents, skills,
adapters, primitives, operators, routines, scripts and reports must import from
here instead of duplicating authority strings.
"""

DECISION_AUTHORITY = "KX108_ONLY"
MODULE_FAMILY = "OBSIDIA_WORKFLOW_GOVERNANCE_PRIMITIVE_V5"
MODE = "READONLY_WORKFLOW_GOVERNANCE"
PROOF_STATUS = "SMOKE_AND_CONTRACT_ONLY_NOT_LEAN_PROVEN"
FREEZE_STATUS = "V5_REPO_AWARE_CONTENT_FILLED_AUDITED_LOCAL_FREEZE"

READONLY_FLAGS = {
    "readonly": True,
    "advisory_only": True,
    "context_signal_only": True,
    "allowed_to_decide": False,
    "emits_act": False,
    "emits_verdict": False,
    "kernel_mutation": False,
    "x108_mutation": False,
    "workflow_decision": False,
    "memory_decision": False,
    "graphiti_decision": False,
    "brody_decision": False,
    "modules_execution": False,
    "gates_execution": False,
    "gates_decision": False,
}

# Runtime payloads must not contain these exact field names at any level.
# Documentation may discuss them, but generated runtime payloads must keep the
# boundary explicit without requesting execution.
FORBIDDEN_OUTPUT_FIELDS = {
    "decision",
    "verdict",
    "action",
    "act",
    "kernel_patch",
    "x108_patch",
    "mutation",
    "execution_request",
    "approval",
    "authorization",
}

# Token scan is used only in strict runtime mode. Descriptive documentation may
# mention these words, while generated envelopes should not use them as commands.
FORBIDDEN_DECISION_TOKENS = {
    "ALLOW",
    "HOLD",
    "BLOCK",
    "ACT",
    "DECIDE",
    "VERDICT",
    "AUTHORIZE",
    "EXECUTE",
    "APPROVE",
    "REJECT",
}

ALLOWED_SIGNAL_FAMILIES = {
    "workflow_structure_signal",
    "sop_extraction_signal",
    "risk_signal",
    "compliance_signal",
    "evidence_signal",
    "contradiction_signal",
    "replay_signal",
    "ir_reduction_candidate",
    "context_packet",
    "x108_readonly_ingress_envelope",
    "trace_pointer",
    "proof_pointer",
    "boundary_warning",
    "unknown_refusal",
}

AGENT_IDS = [
    "AGENT_01_SOP_EXTRACTOR_READONLY",
    "AGENT_02_RISK_ANALYZER_READONLY",
    "AGENT_03_COMPLIANCE_MAPPER_READONLY",
    "AGENT_04_EVIDENCE_BUILDER_READONLY",
    "AGENT_05_CONTRADICTION_REPLAYER_READONLY",
    "AGENT_06_READONLY_AGGREGATOR",
]

SKILL_IDS = [
    "SKILL_EXTRACT_SOP_READONLY",
    "SKILL_MAP_WORKFLOW_GRAPH_READONLY",
    "SKILL_DETECT_CRITICAL_ACTIONS_READONLY",
    "SKILL_BUILD_OBSIDIA_IR_READONLY",
    "SKILL_EXPORT_CONTEXT_PACKET_READONLY",
    "SKILL_REPLAY_AUDIT_TRACE_READONLY",
    "SKILL_X108_INGRESS_ENVELOPE_READONLY",
    "SKILL_AUDIT_REPO_READONLY",
    "SKILL_GENERATE_REPORT_READONLY",
    "SKILL_BUILD_WORKBENCH_VIEW_READONLY",
]

CRITICAL_ACTION_KEYWORDS = {
    "financial_transfer": [
        "payment", "payer", "virement", "transfer", "wire", "bank", "banque",
        "refund", "remboursement", "invoice", "facture", "iban", "swift",
    ],
    "contract_commitment": [
        "contract", "contrat", "signature", "signer", "sign", "engagement",
        "legal", "juridique", "nda", "terms", "conditions",
    ],
    "production_change": [
        "deploy", "déployer", "production", "release", "publish", "publier",
        "migration", "database", "schema", "rollback", "hotfix",
    ],
    "destructive_operation": [
        "delete", "supprimer", "destroy", "purge", "wipe", "remove", "erase",
        "revoke", "révoquer", "disable", "désactiver",
    ],
    "external_send": [
        "send", "envoyer", "email", "mail", "publish", "post", "client", "customer",
        "public", "external", "externe",
    ],
    "access_security": [
        "credentials", "identifiants", "password", "secret", "token", "api key",
        "access", "accès", "permission", "admin", "root", "ssh",
    ],
    "regulated_data": [
        "rgpd", "gdpr", "personal data", "données personnelles", "privacy",
        "sensitive", "confidential", "pii", "health", "medical",
    ],
}

CRITICALITY_ORDER = {"low": 0, "medium": 1, "high": 2, "critical": 3}

EVIDENCE_REQUIREMENTS_BY_CRITICALITY = {
    "low": ["source_step_reference", "operator_trace_note"],
    "medium": ["source_step_reference", "operator_trace_note", "input_snapshot"],
    "high": [
        "source_step_reference",
        "operator_trace_note",
        "input_snapshot",
        "risk_reason",
        "second_review_note",
        "x108_gate_required",
    ],
    "critical": [
        "source_step_reference",
        "operator_trace_note",
        "input_snapshot",
        "risk_reason",
        "second_review_note",
        "x108_gate_required",
        "irreversibility_rationale",
        "rollback_or_compensation_plan",
        "signed_replay_trace",
    ],
}

CONTROL_FAMILY_HINTS = {
    "rgpd": "privacy_data_protection",
    "gdpr": "privacy_data_protection",
    "personal data": "privacy_data_protection",
    "données personnelles": "privacy_data_protection",
    "pii": "privacy_data_protection",
    "contract": "contractual_obligation",
    "contrat": "contractual_obligation",
    "signature": "contractual_obligation",
    "bank": "financial_control",
    "banque": "financial_control",
    "payment": "financial_control",
    "virement": "financial_control",
    "invoice": "financial_control",
    "facture": "financial_control",
    "credentials": "access_security",
    "identifiants": "access_security",
    "password": "access_security",
    "secret": "access_security",
    "access": "access_security",
    "accès": "access_security",
    "production": "change_management",
    "deploy": "change_management",
    "déployer": "change_management",
    "database": "change_management",
    "client": "external_communication",
    "customer": "external_communication",
    "email": "external_communication",
    "send": "external_communication",
}

SKILL_ROLE_MATRIX = {
    "SKILL_EXTRACT_SOP_READONLY": {
        "role": "Extract ordered procedural steps from raw SOP material.",
        "input": "sop_text + optional title",
        "output": "sop_extraction_signal",
        "runtime_effect": False,
    },
    "SKILL_MAP_WORKFLOW_GRAPH_READONLY": {
        "role": "Build a graph candidate: nodes, edges, conditions, tools, evidence pointers.",
        "input": "agent extraction/risk/compliance/evidence payloads",
        "output": "WorkflowGraph",
        "runtime_effect": False,
    },
    "SKILL_DETECT_CRITICAL_ACTIONS_READONLY": {
        "role": "Identify critical action candidates and X108 review requirements.",
        "input": "WorkflowGraph",
        "output": "candidate-only critical action list",
        "runtime_effect": False,
    },
    "SKILL_BUILD_OBSIDIA_IR_READONLY": {
        "role": "Reduce the workflow graph into an Obsidia IR candidate.",
        "input": "WorkflowGraph + readonly aggregation signal",
        "output": "ObsidiaIR",
        "runtime_effect": False,
    },
    "SKILL_EXPORT_CONTEXT_PACKET_READONLY": {
        "role": "Pack graph, IR, signals, evidence requirements and trace chain.",
        "input": "WorkflowGraph + ObsidiaIR + AgentSignals",
        "output": "ContextPacket",
        "runtime_effect": False,
    },
    "SKILL_REPLAY_AUDIT_TRACE_READONLY": {
        "role": "Build structural replay checks and invariant coverage.",
        "input": "ContextPacket",
        "output": "replay audit report",
        "runtime_effect": False,
    },
    "SKILL_X108_INGRESS_ENVELOPE_READONLY": {
        "role": "Wrap the packet for X108 readonly ingress, without runtime binding.",
        "input": "ContextPacket",
        "output": "X108ReadonlyIngressEnvelope",
        "runtime_effect": False,
    },
    "SKILL_AUDIT_REPO_READONLY": {
        "role": "Scan text/file inventories for boundary markers and missing invariants.",
        "input": "text lines or path inventory",
        "output": "readonly audit summary",
        "runtime_effect": False,
    },
    "SKILL_GENERATE_REPORT_READONLY": {
        "role": "Generate a human-readable governance report for handoff.",
        "input": "swarm result",
        "output": "markdown report",
        "runtime_effect": False,
    },
    "SKILL_BUILD_WORKBENCH_VIEW_READONLY": {
        "role": "Build a static Workbench view model for ObsidiaShell/UI inspection.",
        "input": "swarm result",
        "output": "readonly UI state",
        "runtime_effect": False,
    },
}
