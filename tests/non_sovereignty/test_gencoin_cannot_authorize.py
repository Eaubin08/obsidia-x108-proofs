from periphery.gencoin_distribution import compute_distribution


def test_gencoin_cannot_authorize():
    distribution = compute_distribution(
        "nsov_gencoin",
        200.0,
    )

    assert distribution.mint_allowed is False
    assert (
        not hasattr(distribution, "authorize")
        or not callable(getattr(distribution, "authorize", None))
    )
