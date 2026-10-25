import pandas as pd
import pytest
from sklearn.compose import ColumnTransformer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

from examples.credit_default.train import (
    CATEGORICAL_FEATURES,
    NUMERIC_FEATURES,
    build_baseline_pipeline,
    compute_binary_classification_metrics,
    prepare_split_data,
)

EXPECTED_FEATURES = {
    "limit_bal",
    "sex",
    "education",
    "marriage",
    "age",
    "pay_0",
    "pay_2",
    "pay_3",
    "pay_4",
    "pay_5",
    "pay_6",
    "bill_amt1",
    "bill_amt2",
    "bill_amt3",
    "bill_amt4",
    "bill_amt5",
    "bill_amt6",
    "pay_amt1",
    "pay_amt2",
    "pay_amt3",
    "pay_amt4",
    "pay_amt5",
    "pay_amt6",
}


def test_feature_contract_excludes_id_and_target() -> None:
    feature_columns = CATEGORICAL_FEATURES + NUMERIC_FEATURES

    assert len(feature_columns) == 23
    assert len(feature_columns) == len(set(feature_columns))

    assert "id" not in feature_columns
    assert "default_payment_next_month" not in feature_columns

    assert set(feature_columns) == EXPECTED_FEATURES


def test_baseline_pipeline_has_expected_components() -> None:
    pipeline = build_baseline_pipeline(seed=42)

    assert isinstance(pipeline, Pipeline)
    assert list(pipeline.named_steps) == [
        "preprocessor",
        "classifier",
    ]

    preprocessor = pipeline.named_steps["preprocessor"]
    classifier = pipeline.named_steps["classifier"]

    assert isinstance(preprocessor, ColumnTransformer)
    assert isinstance(classifier, LogisticRegression)

    configured_transformers = {
        name: (transformer, tuple(columns))
        for name, transformer, columns in preprocessor.transformers
    }

    categorical_transformer, categorical_columns = configured_transformers[
        "categorical"
    ]
    numeric_transformer, numeric_columns = configured_transformers["numeric"]

    assert isinstance(categorical_transformer, OneHotEncoder)
    assert isinstance(numeric_transformer, StandardScaler)

    assert categorical_columns == CATEGORICAL_FEATURES
    assert numeric_columns == NUMERIC_FEATURES


def test_baseline_pipeline_fits_and_predicts_probabilities() -> None:
    feature_values: dict[str, list[int | float]] = {
        feature: [0, 1, 0, 1, 0, 1] for feature in CATEGORICAL_FEATURES
    }
    feature_values.update(
        {feature: [10.0, 20.0, 30.0, 40.0, 50.0, 60.0] for feature in NUMERIC_FEATURES}
    )
    training_features = pd.DataFrame(feature_values)
    training_target = pd.Series([0, 1, 0, 1, 0, 1])

    pipeline = build_baseline_pipeline(seed=42)
    pipeline.fit(training_features, training_target)

    validation_features = training_features.iloc[[0]].copy()
    validation_features.loc[:, "education"] = 99

    probabilities = pipeline.predict_proba(validation_features)

    assert probabilities.shape == (1, 2)
    assert probabilities[0].sum() == pytest.approx(1.0)
    assert all(0.0 <= probability <= 1.0 for probability in probabilities[0])


def test_prepare_split_data_selects_only_requested_split() -> None:
    dataset = pd.DataFrame(
        {
            "id": [101, 102, 103],
            "default_payment_next_month": [0, 1, 0],
        }
    )

    for feature in CATEGORICAL_FEATURES:
        dataset[feature] = [0, 1, 2]

    for feature in NUMERIC_FEATURES:
        dataset[feature] = [100.0, 200.0, 300.0]

    assignments = pd.DataFrame(
        {
            "id": [103, 101, 102],
            "split": ["test", "train", "validation"],
        }
    )

    features, target = prepare_split_data(
        dataset,
        assignments,
        split_name="train",
    )

    expected_feature_columns = list(CATEGORICAL_FEATURES + NUMERIC_FEATURES)

    assert features.columns.tolist() == expected_feature_columns
    assert features["limit_bal"].tolist() == [100.0]
    assert target.tolist() == [0]


def test_compute_binary_classification_metrics() -> None:
    target = pd.Series([0, 0, 1, 1])
    positive_probabilities = pd.Series([0.1, 0.4, 0.35, 0.8])

    metrics = compute_binary_classification_metrics(
        target,
        positive_probabilities,
    )

    assert metrics == pytest.approx(
        {
            "roc_auc": 0.75,
            "average_precision": 0.8333333333333333,
            "brier_score": 0.158125,
        }
    )
