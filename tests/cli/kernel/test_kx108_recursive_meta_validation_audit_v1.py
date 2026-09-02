from scripts.kernel.kx108_recursive_meta_validation_audit_v1 import (
    KX108RecursiveMetaValidationAudit,
)


def receipt():
    return {
        "receipt_id":
            "kx108-recursive-meta-validation-receipt-v1",
        "validation_status": "VALIDATED",
        "provenance": "recursive-meta-validation",
        "validation_authority": False,
        "decision_authority": False,
        "kernel_mutation": False,
    }


def test_audit_passes():
    result = KX108RecursiveMetaValidationAudit().audit(receipt())
    assert result["audit_status"] == "PASSED"


def test_bad_receipt_fails():
    data = receipt()
    data["receipt_id"] = "invalid"
    result = KX108RecursiveMetaValidationAudit().audit(data)
    assert result["audit_status"] == "FAILED"


def test_provenance_validation():
    result = KX108RecursiveMetaValidationAudit().audit(receipt())
    assert result["checks"]["provenance_valid"] is True


def test_authority_validation():
    result = KX108RecursiveMetaValidationAudit().audit(receipt())
    assert result["checks"]["validation_authority_disabled"] is True
    assert result["checks"]["decision_authority_disabled"] is True


def test_kernel_integrity():
    status = KX108RecursiveMetaValidationAudit().status()
    assert status["memory_write"] is False
    assert status["kernel_mutation"] is False
