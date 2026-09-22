from scripts.kernel.kx108_recursive_state_receipt_v1 import (
    KX108RecursiveStateReceiptBuilder,
)


def recursive_state():

    return {

        "canonical_recursive_state":
            {

                "meta_states":

                    [

                        {
                            "domain": "SYSTEM",
                            "state": "validated",
                        },

                        {
                            "domain": "ENVIRONMENT",
                            "state": "validated",
                        },

                        {
                            "domain": "OPERATIONAL",
                            "state": "validated",
                        },

                    ]

            }
    }


def test_receipt_creation():

    receipt = (
        KX108RecursiveStateReceiptBuilder()
        .create(
            recursive_state()
        )
    )

    assert (
        receipt.receipt_id
        ==
        "kx108-recursive-state-receipt-v1"
    )


def test_state_count():

    receipt = (
        KX108RecursiveStateReceiptBuilder()
        .create(
            recursive_state()
        )
    )

    assert (
        receipt.state_count
        ==
        3
    )


def test_recursive_depth():

    receipt = (
        KX108RecursiveStateReceiptBuilder()
        .create(
            recursive_state()
        )
    )

    assert (
        receipt.recursive_depth
        ==
        1
    )


def test_recursive_authority_disabled():

    receipt = (
        KX108RecursiveStateReceiptBuilder()
        .create(
            recursive_state()
        )
    )

    assert (
        receipt.recursive_authority
        is False
    )


def test_kernel_integrity():

    status = (
        KX108RecursiveStateReceiptBuilder()
        .status()
    )

    assert (
        status["memory_write"]
        is False
    )

    assert (
        status["kernel_mutation"]
        is False
    )
