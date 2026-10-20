import numpy as np
import pandas as pd
import pandera.pandas as pa
import pytest

from examples.credit_default.schema import (
    BILL_AMOUNT_COLUMNS,
    PAYMENT_AMOUNT_COLUMNS,
    PAYMENT_STATUS_COLUMNS,
    CreditDefaultFrame,
)

ROW_COUNT = 30_000


@pytest.fixture(scope="module")
def valid_credit_default_frame() -> pd.DataFrame:
    data = {
        "id": np.arange(1, ROW_COUNT + 1, dtype=np.int64),
        "limit_bal": np.full(ROW_COUNT, 20_000, dtype=np.int64),
        "sex": np.full(ROW_COUNT, 2, dtype=np.int64),
        "education": np.full(ROW_COUNT, 2, dtype=np.int64),
        "marriage": np.full(ROW_COUNT, 1, dtype=np.int64),
        "age": np.full(ROW_COUNT, 30, dtype=np.int64),
    }

    data.update(
        {
            column: np.zeros(ROW_COUNT, dtype=np.int64)
            for column in PAYMENT_STATUS_COLUMNS
        }
    )

    data.update(
        {column: np.zeros(ROW_COUNT, dtype=np.int64) for column in BILL_AMOUNT_COLUMNS}
    )

    data.update(
        {
            column: np.zeros(ROW_COUNT, dtype=np.int64)
            for column in PAYMENT_AMOUNT_COLUMNS
        }
    )

    data["default_payment_next_month"] = (np.arange(ROW_COUNT) % 5 == 0).astype(
        np.int64
    )

    return pd.DataFrame(data)


def test_valid_credit_default_frame_passes(
    valid_credit_default_frame: pd.DataFrame,
) -> None:
    validated_frame = CreditDefaultFrame.validate(
        valid_credit_default_frame,
        lazy=True,
    )

    assert validated_frame.shape == (30_000, 25)


def test_negative_limit_balance_produces_validation_report(
    valid_credit_default_frame: pd.DataFrame,
) -> None:
    broken_frame = valid_credit_default_frame.copy()
    broken_frame.loc[0, "limit_bal"] = -1

    with pytest.raises(pa.errors.SchemaErrors) as exc_info:
        CreditDefaultFrame.validate(
            broken_frame,
            lazy=True,
        )

    failure_cases = exc_info.value.failure_cases

    print(failure_cases.to_string(index=False))

    assert "limit_bal" in failure_cases["column"].tolist()
    assert -1 in failure_cases["failure_case"].tolist()
