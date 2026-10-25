import json
from pathlib import Path

import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    average_precision_score,
    brier_score_loss,
    roc_auc_score,
)
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

CATEGORICAL_FEATURES: tuple[str, ...] = (
    "sex",
    "education",
    "marriage",
    "pay_0",
    "pay_2",
    "pay_3",
    "pay_4",
    "pay_5",
    "pay_6",
)

NUMERIC_FEATURES: tuple[str, ...] = (
    "limit_bal",
    "age",
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
)

DEFAULT_SEED = 42
ID_COLUMN = "id"
TARGET_COLUMN = "default_payment_next_month"
SPLIT_COLUMN = "split"

MODEL_FEATURES = CATEGORICAL_FEATURES + NUMERIC_FEATURES

DATASET_PATH = Path("data/processed/credit-default/v1/data.parquet")
ASSIGNMENTS_PATH = Path("data/processed/credit-default/v1/split_assignments.parquet")
BASELINE_EVIDENCE_PATH = Path("examples/credit_default/evidence/baseline_metrics.json")

SPLIT_NAMES = ("train", "validation", "test")


def build_baseline_pipeline(seed: int = DEFAULT_SEED) -> Pipeline:
    preprocessor = ColumnTransformer(
        transformers=[
            (
                "categorical",
                OneHotEncoder(handle_unknown="ignore"),
                CATEGORICAL_FEATURES,
            ),
            (
                "numeric",
                StandardScaler(),
                NUMERIC_FEATURES,
            ),
        ],
        remainder="drop",
    )

    classifier = LogisticRegression(
        max_iter=1000,
        random_state=seed,
    )
    return Pipeline(steps=[("preprocessor", preprocessor), ("classifier", classifier)])


def prepare_split_data(
    dataset: pd.DataFrame, assignments: pd.DataFrame, *, split_name: str
) -> tuple[pd.DataFrame, pd.Series]:
    merged_frame = assignments.merge(dataset, on=ID_COLUMN, validate="one_to_one")

    split_frame = merged_frame.loc[merged_frame[SPLIT_COLUMN] == split_name]

    if split_frame.empty:
        raise ValueError(f"Split contains no rows: {split_name}")

    features = split_frame.loc[:, list(MODEL_FEATURES)].copy()
    target = split_frame[TARGET_COLUMN].copy()

    return features, target


def compute_binary_classification_metrics(
    target: pd.Series,
    positive_probabilities: pd.Series,
) -> dict[str, float]:
    return {
        "roc_auc": float(roc_auc_score(target, positive_probabilities)),
        "average_precision": float(
            average_precision_score(target, positive_probabilities)
        ),
        "brier_score": float(brier_score_loss(target, positive_probabilities)),
    }


def train_and_evaluate_baseline(
    dataset: pd.DataFrame,
    assignments: pd.DataFrame,
    seed: int = DEFAULT_SEED,
) -> tuple[Pipeline, dict[str, object]]:
    train_features, train_target = prepare_split_data(
        dataset, assignments, split_name="train"
    )

    pipeline = build_baseline_pipeline(seed=seed)
    pipeline.fit(train_features, train_target)

    split_evidence: dict[str, dict[str, float | int]] = {}

    for split_name in SPLIT_NAMES:
        features, target = prepare_split_data(
            dataset, assignments, split_name=split_name
        )

        positive_probabilities = pd.Series(
            pipeline.predict_proba(features)[:, 1], index=target.index
        )

        split_evidence[split_name] = {
            "rows": len(target),
            **compute_binary_classification_metrics(
                target,
                positive_probabilities,
            ),
        }

    evidence: dict[str, object] = {
        "algorithm": "logistic_regression",
        "seed": seed,
        "feature_count": len(MODEL_FEATURES),
        "features": list(MODEL_FEATURES),
        "splits": split_evidence,
    }

    return pipeline, evidence


def main() -> None:
    dataset = pd.read_parquet(DATASET_PATH)
    assignments = pd.read_parquet(ASSIGNMENTS_PATH)

    _, evidence = train_and_evaluate_baseline(
        dataset,
        assignments,
        seed=DEFAULT_SEED,
    )

    BASELINE_EVIDENCE_PATH.parent.mkdir(parents=True, exist_ok=True)
    BASELINE_EVIDENCE_PATH.write_text(
        json.dumps(evidence, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )

    print(json.dumps(evidence, indent=2, sort_keys=True))
    print(f"evidence_path={BASELINE_EVIDENCE_PATH}")


if __name__ == "__main__":
    main()
