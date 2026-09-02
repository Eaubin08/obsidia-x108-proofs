from scripts.kernel.kx108_proof_verification_receipt_v1 import (
    KX108VerificationReceiptBuilder,
)


def test_receipt():

    receipt = (
        KX108VerificationReceiptBuilder()
        .create(
            {
                "verification_status":
                    "VERIFIED",

                "checks":
                    {
                        "a":True
                    }
            }
        )
    )

    assert (
        receipt.verification_id
        ==
        "kx108-proof-verification-v1"
    )


def test_status():

    receipt = (
        KX108VerificationReceiptBuilder()
        .create(
            {
                "verification_status":
                    "VERIFIED",

                "checks":
                    {
                        "a":True
                    }
            }
        )
    )

    assert (
        receipt.verification_status
        ==
        "VERIFIED"
    )


def test_count():

    receipt = (
        KX108VerificationReceiptBuilder()
        .create(
            {
                "verification_status":
                    "VERIFIED",

                "checks":
                    {
                        "a":True
                    }
            }
        )
    )

    assert (
        receipt.checks_count
        ==
        1
    )


def test_authority():

    receipt = (
        KX108VerificationReceiptBuilder()
        .create({})
    )

    assert receipt.authority is False


def test_kernel():

    assert (
        KX108VerificationReceiptBuilder()
        .status()["kernel_mutation"]
        is False
    )
