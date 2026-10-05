"""Predeclared uncertainty diagnostics; ranking improvement is not an outcome."""

import numpy as np
from scipy.stats import nbinom


def verify_freeze(expected, actual):
    if expected != actual:
        raise ValueError("freeze mismatch: create a new release, do not overwrite holdout evidence")


def uncertainty(train_counts, test_counts, exposure=3):
    n = np.asarray(train_counts, dtype=float)
    y = np.asarray(test_counts, dtype=float)
    if len(n) != len(y) or len(n) == 0 or (n < 0).any() or (y < 0).any():
        raise ValueError("invalid count arrays")
    mean = float(n.mean())
    var = float(n.var())
    if mean == 0:
        return {
            "verdict": "rejected",
            "reason": "No training events; prior not estimable",
            "rank_change_possible": False,
        }
    alpha = mean**2 / max(var - mean, 1e-6)
    beta = alpha / (mean / exposure)
    shape = alpha + n
    rate = beta + exposure
    lo = nbinom.ppf(0.05, shape, rate / (rate + 1))
    hi = nbinom.ppf(0.95, shape, rate / (rate + 1))
    covered = (y >= lo) & (y <= hi)
    active = n > 0
    zero_rate = float((n == 0).mean())
    predicted_zero = float(np.mean(nbinom.pmf(0, shape, rate / (rate + 1))))
    active_coverage = float(covered[active].mean()) if active.any() else None
    # Conservative interpretation: pooling almost entirely empty land masks road-site calibration.
    rejected = zero_rate > 0.8 or active_coverage is None or active_coverage < 0.8
    sensitivities = []
    for factor in [0.5, 1, 2]:
        sh = alpha * factor + n
        rt = beta * factor + exposure
        lower = nbinom.ppf(0.05, sh, rt / (rt + 1))
        upper = nbinom.ppf(0.95, sh, rt / (rt + 1))
        sensitivities.append(
            {
                "prior_strength": factor,
                "coverage90": float(((y >= lower) & (y <= upper)).mean()),
                "mean_width90": float((upper - lower).mean()),
            }
        )
    return {
        "alpha": alpha,
        "beta": beta,
        "exposure_years": exposure,
        "posterior_means": (shape / rate).tolist(),
        "coverage90": float(covered.mean()),
        "active_cell_coverage90": active_coverage,
        "mean_width90": float((hi - lo).mean()),
        "training_dispersion": var / mean,
        "training_zero_fraction": zero_rate,
        "test_zero_fraction": float((y == 0).mean()),
        "predicted_test_zero_fraction": predicted_zero,
        "prior_sensitivity": sensitivities,
        "rank_change_possible": False,
        "verdict": "rejected" if rejected else "provisional",
        "reason": "Structural zero cells dominate municipal land; broad coverage does not validate road-site uncertainty."
        if rejected
        else "Descriptive uncertainty only; stationarity and empirical-Bayes fixed-hyperparameter assumptions remain.",
        "interval_note": "Discrete 90% central predictive intervals; condition on estimated prior hyperparameters.",
    }
