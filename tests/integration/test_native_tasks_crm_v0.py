import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
SCRIPTS = ROOT / "scripts"
for candidate in (ROOT, SCRIPTS):
    if str(candidate) not in sys.path:
        sys.path.insert(0, str(candidate))

from obsidia_world_action_pre_execution_v0 import (  # noqa: E402
    run_world_action_pre_execution_v0,
)
from periphery.native_ops.common_v0 import (  # noqa: E402
    ABSENT_STATE_HASH,
    NativeEntityStoreV0,
    canonical_hash,
)
from periphery.native_ops.crm_native_v0 import (  # noqa: E402
    DOMAIN_ID as CRM_DOMAIN,
    KIND_FOLLOWUP,
    KIND_INTERACTION,
    KIND_RECORD,
    KIND_RELATIONSHIP,
    apply_crm_mutation_v0,
    build_crm_mutation_v0,
    crm_timeline_v0,
)
from periphery.native_ops.tasks_native_v0 import (  # noqa: E402
    DOMAIN_ID as TASK_DOMAIN,
    ENTITY_KIND as TASK_KIND,
    STATUS_DONE,
    STATUS_IN_PROGRESS,
    apply_task_mutation_v0,
    build_task_mutation_v0,
)
from periphery.native_ops.world_action_bridge_v0 import (  # noqa: E402
    build_native_human_approval_v0,
    build_native_world_action_request_v0,
)


T0 = "2026-10-07T10:00:00+00:00"
T1 = "2026-10-07T10:01:00+00:00"
T2 = "2026-10-07T10:02:00+00:00"
T3 = "2026-10-07T10:03:00+00:00"
T4 = "2026-10-07T10:04:00+00:00"
T5 = "2026-10-07T10:05:00+00:00"


def governed_apply_task(
    tmp_path,
    store,
    mutation,
    *,
    unknowns=(),
    contradictions=(),
):
    request = build_native_world_action_request_v0(mutation)
    approval = build_native_human_approval_v0(
        request,
        approval_id=f"approval:{mutation.mutation_id}",
        approved_by="HUMAN:TEST_OPERATOR",
        approval_reference=f"review:{mutation.mutation_id}",
    )
    root = tmp_path / "governance" / mutation.mutation_id
    pre = run_world_action_pre_execution_v0(
        request=request,
        human_approval=approval,
        evidence_refs=[f"fixture:{mutation.mutation_id}"],
        unknowns=list(unknowns),
        contradictions=list(contradictions),
        context_store_dir=root / "contexts",
        decision_store_dir=root / "decisions",
    )
    if pre.x108_gate != "ALLOW":
        return request, pre, None
    receipt = apply_task_mutation_v0(
        store=store,
        mutation=mutation,
        request=request,
        decision_record_id=pre.decision_record_id,
        decision_store_dir=root / "decisions",
        context_store_dir=root / "contexts",
    )
    return request, pre, receipt


def governed_apply_crm(
    tmp_path,
    store,
    mutation,
    *,
    unknowns=(),
    contradictions=(),
):
    request = build_native_world_action_request_v0(mutation)
    approval = build_native_human_approval_v0(
        request,
        approval_id=f"approval:{mutation.mutation_id}",
        approved_by="HUMAN:TEST_OPERATOR",
        approval_reference=f"review:{mutation.mutation_id}",
    )
    root = tmp_path / "governance" / mutation.mutation_id
    pre = run_world_action_pre_execution_v0(
        request=request,
        human_approval=approval,
        evidence_refs=[f"fixture:{mutation.mutation_id}"],
        unknowns=list(unknowns),
        contradictions=list(contradictions),
        context_store_dir=root / "contexts",
        decision_store_dir=root / "decisions",
    )
    if pre.x108_gate != "ALLOW":
        return request, pre, None
    receipt = apply_crm_mutation_v0(
        store=store,
        mutation=mutation,
        request=request,
        decision_record_id=pre.decision_record_id,
        decision_store_dir=root / "decisions",
        context_store_dir=root / "contexts",
    )
    return request, pre, receipt


def create_task(tmp_path, store, task_id, title, occurred_at=T0):
    mutation = build_task_mutation_v0(
        mutation_id=f"create:{task_id}",
        task_id=task_id,
        operation="CREATE_TASK",
        payload={
            "occurred_at": occurred_at,
            "title": title,
            "description": "",
            "priority": "NORMAL",
            "assignee_ref": None,
            "due_at": None,
            "dependency_ids": [],
            "tags": [],
        },
        expected_prestate_hash=ABSENT_STATE_HASH,
        source_refs=(f"fixture:{task_id}",),
        requested_by="HUMAN:TEST_OPERATOR",
    )
    _, pre, receipt = governed_apply_task(tmp_path, store, mutation)
    assert pre.x108_gate == "ALLOW"
    assert receipt is not None
    return receipt


def create_crm_record(
    tmp_path,
    store,
    record_id,
    record_type,
    label,
    status,
    occurred_at=T0,
):
    mutation = build_crm_mutation_v0(
        mutation_id=f"create-record:{record_id}",
        entity_kind=KIND_RECORD,
        entity_id=record_id,
        operation="CREATE_RECORD",
        payload={
            "occurred_at": occurred_at,
            "record_type": record_type,
            "display_label": label,
            "lifecycle_status": status,
            "owner_ref": "owner:test",
            "fields": {},
            "tags": [],
        },
        expected_prestate_hash=ABSENT_STATE_HASH,
        source_refs=(f"fixture:{record_id}",),
        requested_by="HUMAN:TEST_OPERATOR",
    )
    _, pre, receipt = governed_apply_crm(tmp_path, store, mutation)
    assert pre.x108_gate == "ALLOW"
    assert receipt is not None
    return receipt


def test_task_create_assign_progress_done_and_replay(tmp_path):
    store = NativeEntityStoreV0(tmp_path / "native")
    create_task(tmp_path, store, "task-1", "Prepare dossier")

    assign = build_task_mutation_v0(
        mutation_id="assign:task-1",
        task_id="task-1",
        operation="ASSIGN_TASK",
        payload={"occurred_at": T1, "assignee_ref": "person:operator"},
        expected_prestate_hash=store.state_hash(
            TASK_DOMAIN, TASK_KIND, "task-1"
        ),
        source_refs=("fixture:assign",),
        requested_by="HUMAN:TEST_OPERATOR",
    )
    _, pre, receipt = governed_apply_task(tmp_path, store, assign)
    assert pre.x108_gate == "ALLOW"
    assert receipt.after_state["assignee_ref"] == "person:operator"

    progress = build_task_mutation_v0(
        mutation_id="progress:task-1",
        task_id="task-1",
        operation="SET_STATUS",
        payload={"occurred_at": T2, "status": STATUS_IN_PROGRESS},
        expected_prestate_hash=store.state_hash(
            TASK_DOMAIN, TASK_KIND, "task-1"
        ),
        source_refs=("fixture:progress",),
        requested_by="HUMAN:TEST_OPERATOR",
    )
    governed_apply_task(tmp_path, store, progress)

    done = build_task_mutation_v0(
        mutation_id="done:task-1",
        task_id="task-1",
        operation="SET_STATUS",
        payload={"occurred_at": T3, "status": STATUS_DONE},
        expected_prestate_hash=store.state_hash(
            TASK_DOMAIN, TASK_KIND, "task-1"
        ),
        source_refs=("fixture:done",),
        requested_by="HUMAN:TEST_OPERATOR",
    )
    _, _, done_receipt = governed_apply_task(tmp_path, store, done)
    assert done_receipt.after_state["status"] == STATUS_DONE

    replayed, replay_hash = store.replay(
        TASK_DOMAIN, TASK_KIND, "task-1"
    )
    assert replayed == store.load_state(TASK_DOMAIN, TASK_KIND, "task-1")
    assert replay_hash == store.state_hash(
        TASK_DOMAIN, TASK_KIND, "task-1"
    )
    assert len(store.receipts(TASK_DOMAIN, TASK_KIND, "task-1")) == 4


def test_task_dependency_must_exist_and_can_be_added(tmp_path):
    store = NativeEntityStoreV0(tmp_path / "native")
    create_task(tmp_path, store, "dep-1", "Dependency")
    create_task(tmp_path, store, "task-2", "Main task", occurred_at=T1)

    mutation = build_task_mutation_v0(
        mutation_id="dependency:task-2",
        task_id="task-2",
        operation="ADD_DEPENDENCY",
        payload={"occurred_at": T2, "dependency_id": "dep-1"},
        expected_prestate_hash=store.state_hash(
            TASK_DOMAIN, TASK_KIND, "task-2"
        ),
        source_refs=("fixture:dependency",),
        requested_by="HUMAN:TEST_OPERATOR",
    )
    _, _, receipt = governed_apply_task(tmp_path, store, mutation)
    assert receipt.after_state["dependency_ids"] == ["dep-1"]

    bad = build_task_mutation_v0(
        mutation_id="dependency:missing",
        task_id="task-2",
        operation="ADD_DEPENDENCY",
        payload={"occurred_at": T3, "dependency_id": "missing"},
        expected_prestate_hash=store.state_hash(
            TASK_DOMAIN, TASK_KIND, "task-2"
        ),
        source_refs=("fixture:dependency-missing",),
        requested_by="HUMAN:TEST_OPERATOR",
    )
    request = build_native_world_action_request_v0(bad)
    approval = build_native_human_approval_v0(
        request,
        approval_id="approval:missing",
        approved_by="HUMAN:TEST_OPERATOR",
        approval_reference="review:missing",
    )
    root = tmp_path / "governance" / "missing"
    pre = run_world_action_pre_execution_v0(
        request=request,
        human_approval=approval,
        evidence_refs=["fixture:missing"],
        context_store_dir=root / "contexts",
        decision_store_dir=root / "decisions",
    )
    assert pre.x108_gate == "ALLOW"
    with pytest.raises(ValueError, match="TASK_DEPENDENCY_NOT_FOUND"):
        apply_task_mutation_v0(
            store=store,
            mutation=bad,
            request=request,
            decision_record_id=pre.decision_record_id,
            decision_store_dir=root / "decisions",
            context_store_dir=root / "contexts",
        )


def test_task_terminal_state_is_immutable(tmp_path):
    store = NativeEntityStoreV0(tmp_path / "native")
    create_task(tmp_path, store, "task-terminal", "Terminal")
    progress = build_task_mutation_v0(
        mutation_id="terminal-progress",
        task_id="task-terminal",
        operation="SET_STATUS",
        payload={"occurred_at": T1, "status": STATUS_IN_PROGRESS},
        expected_prestate_hash=store.state_hash(
            TASK_DOMAIN, TASK_KIND, "task-terminal"
        ),
        source_refs=("fixture:terminal-progress",),
        requested_by="HUMAN:TEST_OPERATOR",
    )
    governed_apply_task(tmp_path, store, progress)
    done = build_task_mutation_v0(
        mutation_id="terminal-done",
        task_id="task-terminal",
        operation="SET_STATUS",
        payload={"occurred_at": T2, "status": STATUS_DONE},
        expected_prestate_hash=store.state_hash(
            TASK_DOMAIN, TASK_KIND, "task-terminal"
        ),
        source_refs=("fixture:terminal-done",),
        requested_by="HUMAN:TEST_OPERATOR",
    )
    governed_apply_task(tmp_path, store, done)

    mutate = build_task_mutation_v0(
        mutation_id="terminal-mutate",
        task_id="task-terminal",
        operation="ASSIGN_TASK",
        payload={"occurred_at": T3, "assignee_ref": "other"},
        expected_prestate_hash=store.state_hash(
            TASK_DOMAIN, TASK_KIND, "task-terminal"
        ),
        source_refs=("fixture:terminal-mutate",),
        requested_by="HUMAN:TEST_OPERATOR",
    )
    request = build_native_world_action_request_v0(mutate)
    approval = build_native_human_approval_v0(
        request,
        approval_id="approval:terminal",
        approved_by="HUMAN:TEST_OPERATOR",
        approval_reference="review:terminal",
    )
    root = tmp_path / "governance" / "terminal"
    pre = run_world_action_pre_execution_v0(
        request=request,
        human_approval=approval,
        evidence_refs=["fixture:terminal"],
        context_store_dir=root / "contexts",
        decision_store_dir=root / "decisions",
    )
    with pytest.raises(ValueError, match="TASK_TERMINAL_STATE_IMMUTABLE"):
        apply_task_mutation_v0(
            store=store,
            mutation=mutate,
            request=request,
            decision_record_id=pre.decision_record_id,
            decision_store_dir=root / "decisions",
            context_store_dir=root / "contexts",
        )


def test_task_prestate_drift_blocks_even_after_kx108_allow(tmp_path):
    store = NativeEntityStoreV0(tmp_path / "native")
    create_task(tmp_path, store, "task-drift", "Drift")
    stale_hash = store.state_hash(TASK_DOMAIN, TASK_KIND, "task-drift")
    mutation = build_task_mutation_v0(
        mutation_id="drift-original",
        task_id="task-drift",
        operation="ASSIGN_TASK",
        payload={"occurred_at": T2, "assignee_ref": "person:a"},
        expected_prestate_hash=stale_hash,
        source_refs=("fixture:drift",),
        requested_by="HUMAN:TEST_OPERATOR",
    )
    request = build_native_world_action_request_v0(mutation)
    approval = build_native_human_approval_v0(
        request,
        approval_id="approval:drift",
        approved_by="HUMAN:TEST_OPERATOR",
        approval_reference="review:drift",
    )
    root = tmp_path / "governance" / "drift-original"
    pre = run_world_action_pre_execution_v0(
        request=request,
        human_approval=approval,
        evidence_refs=["fixture:drift"],
        context_store_dir=root / "contexts",
        decision_store_dir=root / "decisions",
    )
    assert pre.x108_gate == "ALLOW"

    competing = build_task_mutation_v0(
        mutation_id="drift-competing",
        task_id="task-drift",
        operation="ADD_TAG",
        payload={"occurred_at": T1, "tag": "changed"},
        expected_prestate_hash=stale_hash,
        source_refs=("fixture:competing",),
        requested_by="HUMAN:TEST_OPERATOR",
    )
    governed_apply_task(tmp_path, store, competing)

    with pytest.raises(ValueError, match="TASK_PRESTATE_CHANGED"):
        apply_task_mutation_v0(
            store=store,
            mutation=mutation,
            request=request,
            decision_record_id=pre.decision_record_id,
            decision_store_dir=root / "decisions",
            context_store_dir=root / "contexts",
        )


def test_kx108_hold_or_block_never_reaches_native_task_apply(tmp_path):
    store = NativeEntityStoreV0(tmp_path / "native")
    mutation = build_task_mutation_v0(
        mutation_id="hold-task",
        task_id="hold-task",
        operation="CREATE_TASK",
        payload={
            "occurred_at": T0,
            "title": "Hold",
            "description": "",
            "priority": "NORMAL",
            "assignee_ref": None,
            "due_at": None,
            "dependency_ids": [],
            "tags": [],
        },
        expected_prestate_hash=ABSENT_STATE_HASH,
        source_refs=("fixture:hold",),
        requested_by="HUMAN:TEST_OPERATOR",
    )
    _, hold, receipt = governed_apply_task(
        tmp_path,
        store,
        mutation,
        unknowns=("OWNER_UNKNOWN", "SCOPE_UNKNOWN"),
    )
    assert hold.x108_gate == "HOLD"
    assert receipt is None
    assert store.load_state(TASK_DOMAIN, TASK_KIND, "hold-task") is None

    block_mutation = build_task_mutation_v0(
        mutation_id="block-task",
        task_id="block-task",
        operation="CREATE_TASK",
        payload={
            "occurred_at": T0,
            "title": "Block",
            "description": "",
            "priority": "NORMAL",
            "assignee_ref": None,
            "due_at": None,
            "dependency_ids": [],
            "tags": [],
        },
        expected_prestate_hash=ABSENT_STATE_HASH,
        source_refs=("fixture:block",),
        requested_by="HUMAN:TEST_OPERATOR",
    )
    _, block, receipt = governed_apply_task(
        tmp_path,
        store,
        block_mutation,
        contradictions=("AUTHORITY_CONFLICT", "TARGET_CONFLICT"),
    )
    assert block.x108_gate == "BLOCK"
    assert receipt is None


def test_crm_records_relationship_interaction_followup_and_timeline(tmp_path):
    store = NativeEntityStoreV0(tmp_path / "native")
    create_task(tmp_path, store, "task-followup", "Call back", T0)
    create_crm_record(
        tmp_path, store, "org-1", "ORGANIZATION", "Acme Fixture", "ACTIVE", T0
    )
    create_crm_record(
        tmp_path, store, "person-1", "PERSON", "Person Fixture", "ACTIVE", T1
    )

    relationship = build_crm_mutation_v0(
        mutation_id="rel-1-create",
        entity_kind=KIND_RELATIONSHIP,
        entity_id="rel-1",
        operation="CREATE_RELATIONSHIP",
        payload={
            "occurred_at": T2,
            "from_record_id": "person-1",
            "to_record_id": "org-1",
            "relation_type": "MEMBER_OF",
        },
        expected_prestate_hash=ABSENT_STATE_HASH,
        source_refs=("fixture:relationship",),
        requested_by="HUMAN:TEST_OPERATOR",
    )
    governed_apply_crm(tmp_path, store, relationship)

    interaction = build_crm_mutation_v0(
        mutation_id="interaction-1-create",
        entity_kind=KIND_INTERACTION,
        entity_id="interaction-1",
        operation="APPEND_INTERACTION",
        payload={
            "occurred_at": T3,
            "record_id": "person-1",
            "interaction_type": "NOTE",
            "summary": "Fixture contact reviewed.",
            "evidence_refs": ["fixture:contact-note"],
        },
        expected_prestate_hash=ABSENT_STATE_HASH,
        source_refs=("fixture:interaction",),
        requested_by="HUMAN:TEST_OPERATOR",
    )
    governed_apply_crm(tmp_path, store, interaction)

    followup = build_crm_mutation_v0(
        mutation_id="followup-1-create",
        entity_kind=KIND_FOLLOWUP,
        entity_id="followup-1",
        operation="CREATE_FOLLOWUP",
        payload={
            "occurred_at": T4,
            "record_id": "person-1",
            "task_ref": "task-followup",
            "due_at": "2026-10-08T10:00:00+00:00",
        },
        expected_prestate_hash=ABSENT_STATE_HASH,
        source_refs=("fixture:followup",),
        requested_by="HUMAN:TEST_OPERATOR",
    )
    governed_apply_crm(tmp_path, store, followup)

    timeline = crm_timeline_v0(store, "person-1")
    kinds = [row["kind"] for row in timeline]
    assert "RECORD_MUTATION" in kinds
    assert "RELATIONSHIP" in kinds
    assert "INTERACTION" in kinds
    assert "FOLLOWUP" in kinds

    followup_state = store.load_state(
        CRM_DOMAIN, KIND_FOLLOWUP, "followup-1"
    )
    assert followup_state["task_ref"] == "task-followup"
    assert followup_state["status"] == "OPEN"


def test_crm_followup_close_and_replay(tmp_path):
    store = NativeEntityStoreV0(tmp_path / "native")
    create_crm_record(
        tmp_path, store, "case-1", "CASE", "Case Fixture", "OPEN", T0
    )
    create_task(tmp_path, store, "case-task", "Resolve case", T0)
    create = build_crm_mutation_v0(
        mutation_id="case-followup-create",
        entity_kind=KIND_FOLLOWUP,
        entity_id="case-followup",
        operation="CREATE_FOLLOWUP",
        payload={
            "occurred_at": T1,
            "record_id": "case-1",
            "task_ref": "case-task",
            "due_at": "2026-10-08T12:00:00+00:00",
        },
        expected_prestate_hash=ABSENT_STATE_HASH,
        source_refs=("fixture:case-followup",),
        requested_by="HUMAN:TEST_OPERATOR",
    )
    governed_apply_crm(tmp_path, store, create)

    close = build_crm_mutation_v0(
        mutation_id="case-followup-close",
        entity_kind=KIND_FOLLOWUP,
        entity_id="case-followup",
        operation="CLOSE_FOLLOWUP",
        payload={"occurred_at": T2},
        expected_prestate_hash=store.state_hash(
            CRM_DOMAIN, KIND_FOLLOWUP, "case-followup"
        ),
        source_refs=("fixture:case-followup-close",),
        requested_by="HUMAN:TEST_OPERATOR",
    )
    _, _, receipt = governed_apply_crm(tmp_path, store, close)
    assert receipt.after_state["status"] == "DONE"

    replay, replay_hash = store.replay(
        CRM_DOMAIN, KIND_FOLLOWUP, "case-followup"
    )
    assert replay["status"] == "DONE"
    assert replay_hash == store.state_hash(
        CRM_DOMAIN, KIND_FOLLOWUP, "case-followup"
    )


def test_crm_secret_fields_are_rejected_before_kx108():
    with pytest.raises(ValueError, match="CRM_SECRET_FIELD_FORBIDDEN"):
        build_crm_mutation_v0(
            mutation_id="secret-record",
            entity_kind=KIND_RECORD,
            entity_id="record-secret",
            operation="CREATE_RECORD",
            payload={
                "occurred_at": T0,
                "record_type": "PERSON",
                "display_label": "Secret Fixture",
                "lifecycle_status": "ACTIVE",
                "owner_ref": "owner:test",
                "fields": {"api_token": "forbidden"},
                "tags": [],
            },
            expected_prestate_hash=ABSENT_STATE_HASH,
            source_refs=("fixture:secret",),
            requested_by="HUMAN:TEST_OPERATOR",
        )


def test_crm_relationship_to_missing_record_fails_after_governance(tmp_path):
    store = NativeEntityStoreV0(tmp_path / "native")
    create_crm_record(
        tmp_path, store, "person-only", "PERSON", "Person Only", "ACTIVE", T0
    )
    mutation = build_crm_mutation_v0(
        mutation_id="missing-rel",
        entity_kind=KIND_RELATIONSHIP,
        entity_id="missing-rel",
        operation="CREATE_RELATIONSHIP",
        payload={
            "occurred_at": T1,
            "from_record_id": "person-only",
            "to_record_id": "missing-org",
            "relation_type": "MEMBER_OF",
        },
        expected_prestate_hash=ABSENT_STATE_HASH,
        source_refs=("fixture:missing-rel",),
        requested_by="HUMAN:TEST_OPERATOR",
    )
    request = build_native_world_action_request_v0(mutation)
    approval = build_native_human_approval_v0(
        request,
        approval_id="approval:missing-rel",
        approved_by="HUMAN:TEST_OPERATOR",
        approval_reference="review:missing-rel",
    )
    root = tmp_path / "governance" / "missing-rel"
    pre = run_world_action_pre_execution_v0(
        request=request,
        human_approval=approval,
        evidence_refs=["fixture:missing-rel"],
        context_store_dir=root / "contexts",
        decision_store_dir=root / "decisions",
    )
    assert pre.x108_gate == "ALLOW"
    with pytest.raises(
        ValueError, match="CRM_RELATIONSHIP_TO_RECORD_NOT_FOUND"
    ):
        apply_crm_mutation_v0(
            store=store,
            mutation=mutation,
            request=request,
            decision_record_id=pre.decision_record_id,
            decision_store_dir=root / "decisions",
            context_store_dir=root / "contexts",
        )


def test_native_bridge_uses_internal_connectors_and_world_action_pre(tmp_path):
    store = NativeEntityStoreV0(tmp_path / "native")
    task = build_task_mutation_v0(
        mutation_id="bridge-task",
        task_id="bridge-task",
        operation="CREATE_TASK",
        payload={
            "occurred_at": T0,
            "title": "Bridge",
            "description": "",
            "priority": "NORMAL",
            "assignee_ref": None,
            "due_at": None,
            "dependency_ids": [],
            "tags": [],
        },
        expected_prestate_hash=ABSENT_STATE_HASH,
        source_refs=("fixture:bridge",),
        requested_by="HUMAN:TEST_OPERATOR",
    )
    request, pre, receipt = governed_apply_task(tmp_path, store, task)
    assert request["connector_id"] == "OBSIDIA_NATIVE_TASKS"
    assert request["effect_class"] == "INTERNAL_BOUNDED"
    assert request["surface_id"] == "TASKS"
    assert pre.decision_phase == "WORLD_ACTION_PRE_EXECUTION"
    assert pre.x108_gate == "ALLOW"
    assert receipt.world_action_request_hash == request["request_hash"]

    crm = build_crm_mutation_v0(
        mutation_id="bridge-crm",
        entity_kind=KIND_RECORD,
        entity_id="bridge-crm",
        operation="CREATE_RECORD",
        payload={
            "occurred_at": T1,
            "record_type": "ORGANIZATION",
            "display_label": "Bridge CRM",
            "lifecycle_status": "ACTIVE",
            "owner_ref": None,
            "fields": {},
            "tags": [],
        },
        expected_prestate_hash=ABSENT_STATE_HASH,
        source_refs=("fixture:bridge-crm",),
        requested_by="HUMAN:TEST_OPERATOR",
    )
    request, pre, receipt = governed_apply_crm(tmp_path, store, crm)
    assert request["connector_id"] == "OBSIDIA_NATIVE_CRM"
    assert request["surface_id"] == "CRM"
    assert pre.x108_gate == "ALLOW"
    assert receipt.world_action_request_hash == request["request_hash"]
