# Test Matrix

This document lists tests to validate the safety boundaries of the legacy modules against the modern kernel.

| Test ID | Objective | Components Covered | Precondition | Input | Expected Output | Invariant Verified |
| --- | --- | --- | --- | --- | --- | --- |
| test_no_direct_ACT | Ensure no component can emit ACT | All components | None | Simulate output | Must not include ACT | no_direct_ACT |
| test_agent_cannot_decide | Ensure agents cannot decide irreversible actions | C041–C100 | Trigger agent tasks | Agent output | Only advisory outputs | no_agent_decision |
| test_portal_cannot_authorize | Ensure portals cannot authorize actions | C124–C143 | Trigger portal activation | Portal output | Only unlock signals | portal_non_authorization |
| test_memory_readonly | Ensure memory modules do not decide or mutate kernel | C231–C250 | Retrieve memory | Memory output | No mutation or decision | memory_readonly |
| test_output_candidate_requires_kx108 | Ensure world action requires kernel approval | C416–C433 | Propose action | Candidate packet | Contains requires_kx108 flag | action_candidate_requires_KX108 |
| test_effect_receipt_only_after_ACT | Ensure effect receipts are only created post-approval | C441–C458 | Simulate effect receipt | Receipt creation | Only after ACT | effect_receipt_only_after_ACT |
| test_debug_feedback_not_authority | Ensure debug feedback doesn't override kernel | C333–C345 | Use debug UI | Feedback signals | Suggestions only, no overrides | debug_feedback_not_authority |
| test_no_kernel_mutation_from_legacy | Ensure no legacy component can mutate the kernel | All legacy components | Attempt kernel state change | Should fail or be blocked | no_kernel_mutation_from_legacy |
| test_world_action_requires_kx108 | Verify world actions cannot bypass KX108 | C416–C433 | Attempt world action | Error or hold | KX108_ONLY requirement |
| test_quarantine_public_modules_disabled | Ensure quarantined modules remain inactive | Quarantine registry | Attempt to activate | Failure or safe message | quarantine_enforced |
