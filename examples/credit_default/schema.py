import pandas as pd
import pandera.pandas as pa

MINIMUM_ROW_COUNT = 30_000
MINIMUM_TARGET_PREVALENCE = 0.10
MAXIMUM_TARGET_PREVALENCE = 0.40

PAYMENT_STATUS_COLUMNS = (
    "pay_0",
    "pay_2",
    "pay_3",
    "pay_4",
    "pay_5",
    "pay_6",
)

BILL_AMOUNT_COLUMNS = (
    "bill_amt1",
    "bill_amt2",
    "bill_amt3",
    "bill_amt4",
    "bill_amt5",
    "bill_amt6",
)

PAYMENT_AMOUNT_COLUMNS = (
    "pay_amt1",
    "pay_amt2",
    "pay_amt3",
    "pay_amt4",
    "pay_amt5",
    "pay_amt6",
)


def has_minimum_row_count(frame: pd.DataFrame) -> bool:
    return len(frame) >= MINIMUM_ROW_COUNT


def has_expected_target_prevalence(
    frame: pd.DataFrame,
) -> bool:
    prevalence = frame["default_payment_next_month"].mean()

    return MINIMUM_TARGET_PREVALENCE <= prevalence <= MAXIMUM_TARGET_PREVALENCE


columns = {
    "id": pa.Column(
        pa.Int64,
        checks=pa.Check.ge(1),
        nullable=False,
        unique=True,
    ),
    "limit_bal": pa.Column(
        pa.Int64,
        checks=pa.Check.ge(0),
        nullable=False,
    ),
    "sex": pa.Column(
        pa.Int64,
        checks=pa.Check.isin([1, 2]),
        nullable=False,
    ),
    "education": pa.Column(
        pa.Int64,
        checks=pa.Check.isin([0, 1, 2, 3, 4, 5, 6]),
        nullable=False,
    ),
    "marriage": pa.Column(
        pa.Int64,
        checks=pa.Check.isin([0, 1, 2, 3]),
        nullable=False,
    ),
    "age": pa.Column(
        pa.Int64,
        checks=pa.Check.gt(0),
        nullable=False,
    ),
}

columns.update(
    {
        column: pa.Column(
            pa.Int64,
            checks=[
                pa.Check.ge(-2),
                pa.Check.le(9),
            ],
            nullable=False,
        )
        for column in PAYMENT_STATUS_COLUMNS
    }
)

columns.update(
    {
        column: pa.Column(
            pa.Int64,
            nullable=False,
        )
        for column in BILL_AMOUNT_COLUMNS
    }
)

columns.update(
    {
        column: pa.Column(
            pa.Int64,
            checks=pa.Check.ge(0),
            nullable=False,
        )
        for column in PAYMENT_AMOUNT_COLUMNS
    }
)

columns["default_payment_next_month"] = pa.Column(
    pa.Int64,
    checks=pa.Check.isin([0, 1]),
    nullable=False,
)

CreditDefaultFrame = pa.DataFrameSchema(
    columns=columns,
    checks=[
        pa.Check(
            has_minimum_row_count,
            name="minimum_row_count",
            error="Dataset must contain at least 30000 rows",
        ),
        pa.Check(
            has_expected_target_prevalence,
            name="target_prevalence",
            error="Target prevalence must be between 0.10 and 0.40",
        ),
    ],
    strict=True,
    ordered=True,
    coerce=False,
    unique_column_names=True,
    name="CreditDefaultFrame",
)
