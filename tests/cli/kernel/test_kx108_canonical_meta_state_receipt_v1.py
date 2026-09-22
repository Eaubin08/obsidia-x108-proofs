from scripts.kernel.kx108_canonical_meta_state_receipt_v1 import (
    KX108CanonicalMetaStateReceiptBuilder,
)


def meta_state():

    return {

        "aggregate_count":
            3,

        "canonical_meta_state":
            {

                "aggregates":
                    [

                        {
                            "group": "NAVIGATION",
                            "state": "validated",
                        },

                        {
                            "group": "PERCEPTION",
                            "state": "validated",
                        },

                        {
                            "group": "PHYSICAL",
                            "state": "validated",
                        },

                    ]
            }
    }


def test_receipt_creation():

    receipt = (
        KX108CanonicalMetaStateReceiptBuilder()
        .create(
            meta_state()
        )
    )

    assert (
        receipt.receipt_id
        ==
        "kx108-canonical-meta-state-receipt-v1"
    )


def test_aggregate_count():

    receipt = (
        KX108CanonicalMetaStateReceiptBuilder()
        .create(
            meta_state()
        )
    )

    assert (
        receipt.aggregate_count
        ==
        3
    )


def test_aggregate_preservation():

    receipt = (
        KX108CanonicalMetaStateReceiptBuilder()
        .create(
            meta_state()
        )
    )

    assert (
        len(receipt.aggregates)
        ==
        3
    )


def test_no_decision_authority():

    receipt = (
        KX108CanonicalMetaStateReceiptBuilder()
        .create(
            meta_state()
        )
    )

    assert (
        receipt.decision_authority
        is False
    )


def test_kernel_integrity():

    status = (
        KX108CanonicalMetaStateReceiptBuilder()
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
