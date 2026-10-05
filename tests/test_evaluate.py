import numpy as np
import pytest

from transport.evaluate import uncertainty, verify_freeze


def test_common_prior_preserves_order_and_intervals_contain_finite_nonnegative_counts():
    r = uncertainty(np.array([0, 1, 3, 9]), np.array([0, 0, 2, 3]))
    assert r["posterior_means"] == sorted(r["posterior_means"])
    assert 0 <= r["coverage90"] <= 1 and r["mean_width90"] >= 0
    assert r["rank_change_possible"] is False


def test_zero_population_returns_explicit_rejection():
    assert uncertainty(np.zeros(4), np.zeros(4))["verdict"] == "rejected"


def test_changed_input_invalidates_holdout_freeze():
    with pytest.raises(ValueError, match="freeze"):
        verify_freeze({"snapshot_id": "a"}, {"snapshot_id": "b"})
    verify_freeze({"snapshot_id": "a"}, {"snapshot_id": "a"})
