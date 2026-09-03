from scripts.kernel.kx108_proof_contradiction_resolution_receipt_v1 import (
    KX108ContradictionResolutionReceiptBuilder,
)


def test_receipt():

    receipt = (
        KX108ContradictionResolutionReceiptBuilder()
        .create(
            {
            "resolution_status":
                "RESOLVED",

            "contradiction_type":
                "INVARIANT_CONFLICT",

            "propagation_blocked":
                True,
            }
        )
    )

    assert (
        receipt.resolution_status
        ==
        "RESOLVED"
    )


def test_id():

    receipt = (
        KX108ContradictionResolutionReceiptBuilder()
        .create({})
    )

    assert (
        receipt.resolution_id
        ==
        "kx108-proof-contradiction-resolution-v1"
    )


def test_block():

    receipt = (
        KX108ContradictionResolutionReceiptBuilder()
        .create({})
    )

    assert (
        receipt.propagation_blocked
        is False
    )


def test_authority():

    receipt = (
        KX108ContradictionResolutionReceiptBuilder()
        .create({})
    )

    assert receipt.authority is False


def test_kernel():

    builder = KX108ContradictionResolutionReceiptBuilder()

    assert builder.memory_write is False
    assert builder.kernel_mutation is False
