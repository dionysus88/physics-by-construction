import numpy as np
import pytest

from pbc.abm.acceptance import FALSE_FAILURE, agreement, t_factor


def test_the_t_factor_is_the_two_sided_quantile_of_student_t():
    # Tabulated two-sided quantiles at 0.001: 4.437 for 11 degrees of
    # freedom, 6.869 for 5, and the Gaussian 3.291 for many.
    assert t_factor(12) == pytest.approx(4.437, abs=1e-3)
    assert t_factor(6) == pytest.approx(6.869, abs=1e-3)
    assert t_factor(10**6) == pytest.approx(3.291, abs=1e-3)
    assert t_factor(12, alpha=0.05) == pytest.approx(2.201, abs=1e-3)
    assert FALSE_FAILURE == 0.001


def test_agreement_is_within_the_allowance_plus_t_standard_errors():
    values = np.array([1.0, 2.0, 3.0, 4.0])
    error = np.std(values, ddof=1) / 2.0

    result = agreement(values, 1.0, allowance=0.5)

    assert result.mean == 2.5
    assert result.error == pytest.approx(error)
    assert result.difference == pytest.approx(1.5)
    assert result.tolerance == pytest.approx(0.5 + t_factor(4) * error)
    assert result.agrees
    # Far from the theory, and with no allowance, the same runs disagree.
    assert not agreement(values, 2.5 + 1.01 * t_factor(4) * error).agrees
    assert not agreement(values, 2.5 - 1.01 * t_factor(4) * error).agrees


def test_agreement_refuses_what_has_no_standard_error_or_a_negative_allowance():
    with pytest.raises(ValueError, match="at least two runs"):
        agreement([1.0], 1.0)
    with pytest.raises(ValueError, match="must not be negative"):
        agreement([1.0, 2.0], 1.0, allowance=-0.1)
    with pytest.raises(ValueError, match="alpha"):
        t_factor(5, alpha=1.5)
