from scripts.kernel.kx108_recursive_meta_validation_receipt_v1 import (
    KX108RecursiveMetaValidationReceiptBuilder,
)


def validation():
    return {
        "validation_status": "VALIDATED",
        "validation_authority": False,
        "decision_authority": False,
        "kernel_mutation": False,
    }


def test_receipt_creation():
    receipt = KX108RecursiveMetaValidationReceiptBuilder().create(
        validation()
    )
    assert (
        receipt.receipt_id
        == "kx108-recursive-meta-validation-receipt-v1"
    )


def test_validation_status():
    receipt = KX108RecursiveMetaValidationReceiptBuilder().create(
        validation()
    )
    assert receipt.validation_status == "VALIDATED"


def test_provenance():
    receipt = KX108RecursiveMetaValidationReceiptBuilder().create(
        validation()
    )
    assert receipt.provenance == "recursive-meta-validation"


def test_authority_isolation():
    receipt = KX108RecursiveMetaValidationReceiptBuilder().create(
        validation()
    )
    assert receipt.validation_authority is False
    assert receipt.decision_authority is False


def test_kernel_integrity():
    status = KX108RecursiveMetaValidationReceiptBuilder().status()
    assert status["memory_write"] is False
    assert status["kernel_mutation"] is False
