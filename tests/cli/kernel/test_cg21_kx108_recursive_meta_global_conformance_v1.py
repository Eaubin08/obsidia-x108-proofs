from scripts.kernel.kx108_recursive_meta_validation_boundary_v1 import (
    KX108RecursiveMetaValidationBoundary,
)
from scripts.kernel.kx108_recursive_meta_validation_receipt_v1 import (
    KX108RecursiveMetaValidationReceiptBuilder,
)
from scripts.kernel.kx108_recursive_meta_validation_audit_v1 import (
    KX108RecursiveMetaValidationAudit,
)


def valid_governance():
    return {
        "governance_status": "COMPLETED",
        "governance_authority": False,
        "decision_authority": False,
    }


def pipeline():
    validation = (
        KX108RecursiveMetaValidationBoundary()
        .validate(valid_governance())
    )

    receipt = (
        KX108RecursiveMetaValidationReceiptBuilder()
        .create(validation)
    )

    audit = (
        KX108RecursiveMetaValidationAudit()
        .audit(receipt.to_dict())
    )

    return validation, receipt, audit


def test_complete_pipeline():
    _, _, audit = pipeline()
    assert audit["audit_status"] == "PASSED"


def test_validation_binding():
    validation, _, _ = pipeline()
    assert validation["validation_status"] == "VALIDATED"


def test_receipt_binding():
    _, receipt, _ = pipeline()
    assert receipt.validation_status == "VALIDATED"


def test_authority_isolation():
    validation, receipt, _ = pipeline()
    assert validation["decision_authority"] is False
    assert receipt.decision_authority is False


def test_kernel_protection():
    boundary = KX108RecursiveMetaValidationBoundary().status()
    receipt = KX108RecursiveMetaValidationReceiptBuilder().status()
    audit = KX108RecursiveMetaValidationAudit().status()

    assert boundary["kernel_mutation"] is False
    assert receipt["kernel_mutation"] is False
    assert audit["kernel_mutation"] is False
