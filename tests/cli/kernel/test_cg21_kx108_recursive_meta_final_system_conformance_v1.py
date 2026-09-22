from scripts.kernel.kx108_recursive_meta_validation_boundary_v1 import (
    KX108RecursiveMetaValidationBoundary,
)
from scripts.kernel.kx108_recursive_meta_validation_receipt_v1 import (
    KX108RecursiveMetaValidationReceiptBuilder,
)
from scripts.kernel.kx108_recursive_meta_validation_audit_v1 import (
    KX108RecursiveMetaValidationAudit,
)


def test_cg21_final_system_conformance():

    governance = {
        "governance_status": "COMPLETED",
        "governance_authority": False,
        "decision_authority": False,
    }

    validation = (
        KX108RecursiveMetaValidationBoundary()
        .validate(governance)
    )

    receipt = (
        KX108RecursiveMetaValidationReceiptBuilder()
        .create(validation)
    )

    audit = (
        KX108RecursiveMetaValidationAudit()
        .audit(receipt.to_dict())
    )

    assert validation["validation_status"] == "VALIDATED"
    assert audit["audit_status"] == "PASSED"


def test_fail_closed_missing_input():
    result = KX108RecursiveMetaValidationBoundary().validate({})
    assert result["validation_status"] == "REJECTED"


def test_receipt_provenance():
    receipt = (
        KX108RecursiveMetaValidationReceiptBuilder()
        .create({"validation_status": "VALIDATED"})
    )
    assert receipt.provenance == "recursive-meta-validation"


def test_authority_final_integrity():
    result = (
        KX108RecursiveMetaValidationBoundary()
        .validate({
            "governance_status": "COMPLETED",
            "governance_authority": False,
            "decision_authority": False,
        })
    )

    assert result["validation_authority"] is False
    assert result["decision_authority"] is False


def test_kernel_final_integrity():
    assert (
        KX108RecursiveMetaValidationBoundary()
        .status()["kernel_mutation"]
        is False
    )
    assert (
        KX108RecursiveMetaValidationReceiptBuilder()
        .status()["kernel_mutation"]
        is False
    )
    assert (
        KX108RecursiveMetaValidationAudit()
        .status()["kernel_mutation"]
        is False
    )
