import numpy as np
import pandas as pd
import pytest

from review_execution import money_result


def test_money_result_includes_initial_capital_in_drawdown():
    result = money_result(pd.Series([-0.10, 0.02, 0.01]), 1000.0)
    assert result["initial_investment"] == 1000.0
    assert result["ending_value"] == pytest.approx(927.18)
    assert result["profit"] == pytest.approx(-72.82)
    assert result["max_drawdown"] == pytest.approx(-0.10)
    assert result["trades"] == 3


def test_money_result_empty_series_preserves_capital():
    result = money_result(pd.Series(dtype=float), 1000.0)
    assert result["ending_value"] == 1000.0
    assert result["profit"] == 0.0
    assert result["max_drawdown"] == 0.0
    assert result["trades"] == 0


@pytest.mark.parametrize("value", [np.nan, np.inf, -np.inf, -1.0, -1.01])
def test_money_result_rejects_invalid_or_insolvent_returns(value):
    with pytest.raises(ValueError):
        money_result(pd.Series([value]), 1000.0)
